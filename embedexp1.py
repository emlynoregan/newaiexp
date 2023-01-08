'''
In this experimental script, we read a transcript of a conversation (ie: a list of utterances), then try to convert it to the best 
list of ([utterance], startindex, embedding) triples. The list of utterances in a triple should be contextually similar.

triples = []
For each index, utterance:
    for length from 0 to 9:
        Construct a list of utterances from index - length to index.
        Create a triple ([utterances], index-length, embedding) called t.
        Check if t should be added to triples:
            for each triple in triples where triple is entirely contained in t:
                if t's embedding is too close to triple's embedding, throw away t.
            add t to triples if it is not thrown away.
            for each triple in triples where t is entirely contained in triple:
                if t's embedding is too close to triple's embedding, throw away triple.
            remove triples that are thrown away.
        
'''

import json
import argparse

import openai
import setcreds

def calculate_embedding(utterances):

    utterances_text_combined = " ".join([utterance["text"] for utterance in utterances])

    # Use the OpenAI API to calculate the embedding for the given text
    response = openai.Embedding.create(
        engine="text-embedding-ada-002",
        input=utterances_text_combined
    )

    # Extract the embedding from the API response
    embedding = response["data"][0]["embedding"]

    # # Print the embedding
    # print(embedding)    

    return embedding

def calculate_similarity(embedding1, embedding2):
    # calculate the cosine similarity between the two embeddings
    # https://en.wikipedia.org/wiki/Cosine_similarity
    # note that we can assume magnitudes are 1 because we are using normalized embeddings

    similarity = sum([a*b for a,b in zip(embedding1, embedding2)])

    return similarity

# def calculate_magnitude(embedding):
#     # calculate the magnitude of the embedding
#     magnitude = sum([a*a for a in embedding]) ** 0.5

#     return magnitude

C_MAX_UTTERANCES_IN_A_CLUMP = 10
C_MIN_UTTERANCES_IN_A_CLUMP = 1
C_MAX_SIMILARITY = 0.9

def main():
    # usage: python3 embedexp1.py [<transcript file>]
    # note that if you don't specify a transcript file, it will read the clumps from the file ./working/full_clumps.json

    # first get all the command line arguments
    parser = argparse.ArgumentParser(description='group together similar utterances in a transcript')

    parser.add_argument('transcript_file', nargs='?', help='the transcript file to read')

    args = parser.parse_args()

    transcript_file = args.transcript_file

    if transcript_file:

        # Read the transcript as json
        with open(transcript_file, 'r') as f:
            transcript = json.load(f)

        transcript = transcript[:50] # for testing

        print ("transcript:", transcript)

        # A transcript is a list of utterances.
        # A clump of utterances is a continguous list of utterances from the transcript.
        # A clump contains a maximum of C_MAX_UTTERANCES_IN_A_CLUMP utterances.

        clumps = {}

        # add the clumps to the clumps dictionary, where the key is start:length and the value is the clump
        for start, utterance in enumerate(transcript):
            # max length is the shorter of C_MAX_UTTERANCES_IN_A_CLUMP and the length of the transcript from start to the end
            max_length = min(C_MAX_UTTERANCES_IN_A_CLUMP, len(transcript) - start)

            # iterate through lengths, starting at C_MIN_UTTERANCES_IN_A_CLUMP and ending at max_length
            for length in range(C_MIN_UTTERANCES_IN_A_CLUMP, max_length+1):
                # construct the clump
                utterances = transcript[start:start+length]
                # add the clump to the clumps dictionary
                clump_key = f"{start}:{length}"
                clumps[clump_key] = {
                    "key": clump_key,
                    "start": start,
                    "length": length,
                    "utterances": utterances,
                    "embedding": calculate_embedding(utterances)
                }
                print (f"clump: {clump_key}")

        print ("clumps:", json.dumps([{
            "key": clump["key"],
            "start": clump["start"],
            "length": clump["length"],
            "utterances": clump["utterances"]
        } for clump in clumps.values()], indent=4))

        # write this to a file
        with open("./working/full_clumps.json", "w") as f:
            json.dump(clumps, f, indent=4)
    else:
        # read the clumps from the file
        with open("./working/full_clumps.json", "r") as f:
            clumps = json.load(f)
    
    clumps_to_be_discarded = {}

    # we need a list of clumps, sorted by length, longest first
    clumps_sorted_by_length = sorted(clumps.values(), key=lambda clump: clump["length"], reverse=True)

    for clump in clumps_sorted_by_length:
        clump_key = clump["key"]

        # if the clump is already in the list of clumps to be discarded, we don't need to check it
        if clump_key in clumps_to_be_discarded:
            continue

        start = clump["start"]
        length = clump["length"]

        if length == C_MIN_UTTERANCES_IN_A_CLUMP:
            continue # we don't need to check the smallest clumps

        end = start + length

        keep_this_clump = True

        # we need to find all clumps that are entirely contained in this clump,
        # and are not the same clump. If the similarity is too high, we discard the current clump
        for contained_start in range(start, end-1):
            for contained_end in range(contained_start+1, end):
                contained_length = contained_end - contained_start
                # construct the key for the contained clump
                contained_clump_key = f"{contained_start}:{contained_length}"
                # if the contained clump is the same as the current clump, we don't need to check it
                if contained_clump_key == clump_key:
                    continue
                # get the contained clump
                contained_clump = clumps.get(contained_clump_key)
                # if the contained clump is not in the clumps dictionary, we don't need to check it
                if contained_clump is None:
                    continue

                # calculate the similarity between the clumps
                similarity = calculate_similarity(clump["embedding"], contained_clump["embedding"])
                # if the similarity is too high, we discard the current clump
                if similarity > 0.9:
                    print (f"similarity ({similarity}) is too high between clumps {clump_key} and {contained_clump_key}, discarding {clump_key}")
                    clumps_to_be_discarded[clump_key] = clump
                    keep_this_clump = False
                    break
            if not keep_this_clump:
                break

    print ("keys of clumps to be discarded, pass 1:", clumps_to_be_discarded.keys())

    # remove the clumps to be discarded from the clumps dictionary
    for clump_key in clumps_to_be_discarded.keys():
        del clumps[clump_key]
    
    # clear the list of clumps to be discarded
    clumps_to_be_discarded = {}

    # next, let's visit the clumps in the order of their start position (then length, longest first),
    # and if the similarity between the current clump and the next clump is too high,
    # we discard the next clump

    # we need a list of clumps, sorted by start, earliest first, then length, longest first
    clumps_sorted_by_start = sorted(clumps.values(), key=lambda clump: (clump["start"], clump["length"]), reverse=True)

    current_index = 0
    while current_index < len(clumps_sorted_by_start):
        clump = clumps_sorted_by_start[current_index]

        def clumps_overlap(clump1, clump2):
            return clump1["start"] < clump2["start"] + clump2["length"] and clump2["start"] < clump1["start"] + clump1["length"]

        # remove successive clumps that overlap with and are too similar to the current clump
        next_index = current_index + 1
        while next_index < len(clumps_sorted_by_start):
            next_clump = clumps_sorted_by_start[next_index]
            if clumps_overlap(clump, next_clump):
                similarity = calculate_similarity(clump["embedding"], next_clump["embedding"])
                if similarity > 0.9:
                    print (f"similarity ({similarity}) is too high between clumps {clump['key']} and {next_clump['key']}, discarding {next_clump['key']}")
                    clumps_to_be_discarded[next_clump["key"]] = next_clump
                    next_index += 1
                else:
                    break
            else:
                break
        
        current_index = next_index

    print ("keys of clumps to be discarded, pass 2:", clumps_to_be_discarded.keys())

    # remove the clumps to be discarded from the clumps dictionary
    for clump_key in clumps_to_be_discarded.keys():
        del clumps[clump_key]

    print ("clumps after discarding:", json.dumps([{
        "key": clump["key"],
        "start": clump["start"],
        "length": clump["length"],
        "utterances": clump["utterances"]
    } for clump in clumps.values()], indent=4))

    # now we need to write the clumps to a file
    with open('.\\working\\clumps.json', 'w') as f:
        json.dump(clumps, f, indent=4)

    print ("Done")





if __name__ == '__main__':
    main()