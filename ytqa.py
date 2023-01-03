# In this program we will read the transcript of a youtube video and summarize it, then allow the user to ask questions about the video.

import setcreds
from youtube_transcript_api import YouTubeTranscriptApi
from utils import get_chunks_from_transcript, summarize_audio_transcript_chunks, set_diagnostics, diagnostics
import argparse
import os
import json
from openai.embeddings_utils import get_embedding, cosine_similarity
import openai
import threading
import queue

def get_video_id_from_video_id_or_url(video_id_or_url):
    # a youtube video id is 11 characters long
    # if the video id is longer than that, then it's a url
    if len(video_id_or_url) > 11:
        # it's a url
        # the video id is the last 11 characters
        return video_id_or_url[-11:]
    else:
        # it's a video id
        return video_id_or_url

C_MAX_SIMULTANEOUS_EMBEDDINGS = 20

def create_embeddings_db(transcript):
    # a transcript is a list of dictionaries, each dictionary has the following keys:
    #   "start": float
    #   "duration": float
    #   "text": string


    # we're going to break the transcript into all odd-numbered sequential sets of utterances, max length 9.
    # we'll concatenate the text from each utterance in a set, and make a new utterance with that text.

    new_utterances = []
    new_embeddings_unprocessed = []

    print (f"Creating embeddings db. Number of utterances: {len(transcript)}")
    for index, utterance in enumerate(transcript):
        print (f"Processing utterance {index}")
        for i in [0, 2, 4, 6, 8]:
            if index + i < len(transcript):
                new_text = " ".join([transcript[index + j]["text"] for j in range(i+1)])

                if new_text.strip() == "":
                    print (f"Skipping utterance {index + i} because it's empty")
                    continue

                new_utterance = {
                    "start": utterance["start"],
                    "duration": sum([transcript[index + j]["duration"] for j in range(i+1)]),
                    "text": new_text
                }
                print (f"Creating new utterance: {new_utterance}")
                # new_utterance["embedding"] = get_embedding(new_text, "text-embedding-ada-002")
                new_embeddings_unprocessed.append(new_utterance)

        if len(new_embeddings_unprocessed) > C_MAX_SIMULTANEOUS_EMBEDDINGS:
            print(f"Getting embeddings for {len(new_embeddings_unprocessed)} new utterances")
            embeddings = get_embeddings_for_list([new_utterance["text"] for new_utterance in new_embeddings_unprocessed])
            print (f"Got {len(embeddings)} new embeddings")

            for i, new_utterance in enumerate(new_embeddings_unprocessed):
                new_utterance["embedding"] = embeddings[i]
                new_utterances.append(new_utterance)
            
            new_embeddings_unprocessed = []

    if len(new_embeddings_unprocessed):
        print(f"Getting embeddings for {len(new_embeddings_unprocessed)} new utterances")
        embeddings += get_embeddings_for_list([new_utterance["text"] for new_utterance in new_embeddings_unprocessed])
        print (f"Got {len(embeddings)} new embeddings")

        for i, new_utterance in enumerate(new_embeddings_unprocessed):
            new_utterance["embedding"] = embeddings[i]
            new_utterances.append(new_utterance)
        
        new_embeddings_unprocessed = []

    return new_utterances

def utterances_overlap(utterance1, utterance2):
    # check if the two utterances overlap in time
    # if the two start times both come before the two end times, then they overlap

    return utterance1["start"] < utterance2["start"] + utterance2["duration"] and utterance2["start"] < utterance1["start"] + utterance1["duration"]

def get_top_n_similar_utterances(input_str, embeddings_db, n):
    # calculate the embedding for the input string
    input_embedding = get_embedding(input_str, "text-embedding-ada-002")
    utterances = [*embeddings_db]

    # calculate the similarity between the input embedding and each utterance embedding in the embeddings db
    for utterance in utterances:
        similarity = cosine_similarity(input_embedding, utterance["embedding"])
        utterance["similarity"] = similarity

    # sort the utterances in descending order
    utterances.sort(key=lambda x: x["similarity"], reverse=True)

    # We want to return the top n, but we don't want to include overlapping utterances.
    result = []
    for utterance in utterances:
        if not any([utterances_overlap(utterance, result_utterance) for result_utterance in result]):
            result.append(utterance)

        if len(result) == n:
            break

    return result

def get_embeddings_for_list(input_list):
    def get_one_embedding(ix, input, q):
        response = get_embedding(input, "text-embedding-ada-002")
        q.put((ix, response))

    threads = []
    
    q = queue.Queue()

    for ix, input in enumerate(input_list):
        t = threading.Thread(target=get_one_embedding, args=(ix, input, q))
        threads.append(t)
        t.start()

    # Wait for all threads to complete
    for t in threads:
        t.join()

    # Get all the results from the queue
    results = []
    while not q.empty():
        results.append(q.get())

    print (f"Got {len(results)} results from the queue")

    # Sort the results by the index
    results.sort(key=lambda x: x[0])

    # Now just return the embeddings in the correct order
    return [result[1] for result in results]


def answer_the_question(user_input, top_n_similar_utterances, chat_utterances, prompt_header):
    # Create a string version of the top n similar utterances

    top_n_similar_utterances_str = "\n".join([
        f"{i + 1}. {top_n_similar_utterance['text']}" for i, top_n_similar_utterance in enumerate(top_n_similar_utterances)
    ])

    most_recent_chat_utterances = chat_utterances[-20:]

    # Create a string version of the most recent chat utterances

    most_recent_chat_utterances_str = "\n".join([
        f"{most_recent_chat_utterance['speaker']}. {most_recent_chat_utterance['text']}" for i, most_recent_chat_utterance in enumerate(most_recent_chat_utterances)
    ])

    # Create the prompt

    prompt = f"""
The transcript of a video includes the following sections that might be relevant to the question:

{top_n_similar_utterances_str}

The user and the AI are having a conversation about the video. Here's the most recent transcript of the conversation:

{most_recent_chat_utterances_str}

{prompt_header}Using the information above, answer the following question. Try to stick to information in the video transcript, 
and include quotes where that's helpful (but not too many):
{user_input}
"""

    # Ask OpenAI to answer the question
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=1000,
        temperature=0.5,
    )    

    return completion.choices[0].text

def rewrite_user_input_for_semantic_search(chat_utterances):
    # we'll ask openai to rewrite the user input to make it more useful in a semantic search

    most_recent_chat_utterances = chat_utterances[-20:]

    # Create a string version of the most recent chat utterances

    most_recent_chat_utterances_str = "\n".join([
        f"{most_recent_chat_utterance['speaker']}. {most_recent_chat_utterance['text']}" for i, most_recent_chat_utterance in enumerate(most_recent_chat_utterances)
    ])

    # Create the prompt

    prompt = f"""
The user and the AI are having a conversation about the video. Here's the most recent transcript of the conversation:

{most_recent_chat_utterances_str}

Rewrite the final user response, using the rest of the chat as context, producing a sentence that would be more useful for
creating an embedding for semantic search:
"""

    # Ask OpenAI to rewrite the user input
    completion = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt,
        max_tokens=200,
        temperature=0.5,
    )

    return completion.choices[0].text

def main():
    # usage: python3 ytsummary.py <YOUR-FILE-PATH>  [--outfile <output_filename>] [--prompt_header <promptheader_filename>] [--chunk_len_mins <int>] [--diagnostics] [--mentions] [--save_transcript <transcript_filename>] [--embeddings-db <embeddings_db_filename>]

    # first get all the command line arguments
    parser = argparse.ArgumentParser(description='Summarize a youtube video.')

    parser.add_argument('video_id_or_url', type=str, help='The video id or url of the video to summarize')
    parser.add_argument('--outfile', type=str, help='The name of the file to write the summary to')
    parser.add_argument('--prompt_header', type=str, help='The name of the file to write the prompt header to')
    parser.add_argument('--chunk_len_mins', type=int, help='The length of the chunks to summarize in minutes')
    parser.add_argument('--diagnostics', action='store_true', help='Print out the prompts and responses')
    parser.add_argument('--mentions', action='store_true', help='Include people and entities mentioned in the video')
    parser.add_argument('--save_transcript', type=str, help='The name of the file to write the transcript to')
    parser.add_argument('--embeddings-db', type=str, help='The name of the file to write the embeddings db to')

    args = parser.parse_args()

    video_id_or_url = args.video_id_or_url
    video_id = get_video_id_from_video_id_or_url(video_id_or_url)
    outfile_name = args.outfile
    transcript_outfile_name = args.save_transcript
  
    embeddings_db_name = args.embeddings_db

    if not outfile_name:
        default_output_file_path_elems = ["working", f"yt_transcript_{video_id}.txt"]

        outfile_name = os.path.join(*default_output_file_path_elems)

    if not embeddings_db_name:
        default_embeddings_db_file_path_elems = ["working", f"yt_embeddings_db_{video_id}.json"]

        embeddings_db_name = os.path.join(*default_embeddings_db_file_path_elems)

    # create any intermediate directories if they don't exist, in an OS independent way            
    os.makedirs(os.path.dirname(outfile_name), exist_ok=True)

    prompt_header = None
    prompt_header_file = args.prompt_header
    if prompt_header_file:
        with open(prompt_header_file, "r") as f:
            prompt_header = f.read()

    set_diagnostics(args.diagnostics)

    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['en', 'en-US', 'en-GB'])

    if transcript_outfile_name:
        # write the transcript as json to a file
        with open(transcript_outfile_name, "w") as f:
            json.dump(transcript, f)

    # next we'll break the video into pieces, generate embeddings for each piece, and store those in dictionary

    # first try to load the embeddings db
    embeddings_db = {}
    if os.path.exists(embeddings_db_name):
        with open(embeddings_db_name, "r") as f:
            embeddings_db = json.load(f)
    else:
        embeddings_db = create_embeddings_db(transcript)
        # write the embeddings db to a file
        with open(embeddings_db_name, "w") as f:
            json.dump(embeddings_db, f, indent=2)
    
    # ok now start a conversation with the user.
    # They will ask questions, and we'll find similar utterances in the video and return them.
    # We'll keep going until the user says "stop"

    print ("Hi, I'm a bot. Ask me a question about the video, and I'll try to find the answer for you.")

    chat_utterances = []

    while True:
        user_input = input("> ")

        if user_input == "stop":
            break

        if user_input.strip() == "":
            continue

        # add the user's utterance to the chat utterances
        chat_utterances.append({
            "text": user_input,
            "speaker": "user",
        })

        # get a sentence that sums up the user's request in context, and is useful for semantic comparison
        user_input_for_embedding = rewrite_user_input_for_semantic_search(chat_utterances)

        if args.diagnostics:
            print (f"***User input for embedding: {user_input_for_embedding}")

        # find the top 5 most similar utterances
        top_n_similar_utterances = get_top_n_similar_utterances(user_input_for_embedding, embeddings_db, 30)

        # ask openai to generate a response
        response = answer_the_question(user_input, top_n_similar_utterances, chat_utterances, prompt_header=prompt_header)

        # add the bot's response to the chat utterances
        chat_utterances.append({
            "text": response,
            "speaker": "bot",
        })

        # for index, utterance in enumerate(top_n_similar_utterances):
        #     print(f"{index + 1}. {utterance['text']}")

        print(f"Here's what I found: {response}")

    print("Ok, bye!")        
    

if __name__ == "__main__":
    main()
