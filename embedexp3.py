import json
import argparse
import openai
from openai.embeddings_utils import get_embedding, cosine_similarity
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

    similarity = sum([a*b for a,b in zip(embedding1, embedding2)])

    # magnitude1 = sum([a*a for a in embedding1]) ** 0.5

    # magnitude2 = sum([a*a for a in embedding2]) ** 0.5

    # similarity = similarity / (magnitude1 * magnitude2)

    return similarity

def main():
    # utterances = [
    #     {
    #         "text": "A centaur is a horse"
    #     },
    #     {
    #         "text": "A centaur is a horse with a human torso"
    #     },
    #     {
    #         "text": "His name is John"
    #     },
    #     {
    #         "text": "What is your favourite fruit?"
    #     },
    #     {
    #         "text": "I like apples"
    #     },
    # ]

    # utterances = [
    #     {
    #         "text": "This is a",
    #     },
    #     {  
    #         "text": "sentence about",
    #     },
    #     {
    #         "text": "hats in the",
    #     },
    #     {
    #         "text": "rain.",
    #     },
    #     {
    #         "text": "This is a sentence about hats in the rain."
    #     }
    # ]

    utterances = [
        {
            "text": "How did we go from\nhats being a crucial part"
        },
        {
            "text": "of our fashion, culture and\neconomy to almost non-existent"
        },
        {
            "text": "in less than 50 years?"
        },
        {
            "text": "(ambient music)"
        },
        {
            "text": "Well, hat wearing is\nnow viewed as something"
        },
        {
            "text": "for special events or the eccentric"
        },
        {
            "text": "or just the Royal Family."
        },
        {
            "text": "What the hell happened?"
        },
        {
            "text": "This is kind of nuts when\nyou really think about it."
        },
        {
            "text": "It's so drastic, it's so intense."
        },
        {
            "text": "What the hell happened?"
        },
    ]

    utterances = [
        {
            "text": f"{utterances[index]['text']} {utterances[index+1]['text']} {utterances[index+2]['text']}"
        } for index, utterance in enumerate(utterances[:-2]) 
    ]

    utterances += [
        {
            "text": "Queen Elizabeth"
        },
        {
            "text": "The Royal Family"
        },
    ]

    # Add embeddings to the utterances
    for utterance in utterances:
        # utterance["embedding"] = calculate_embedding([utterance])
        utterance["embedding"] = get_embedding(utterance["text"])


    # Add a list of all other utterances to each utterance
    for utterance in utterances:
        utterance["other_utterances"] = [{
                "text": other_utterance["text"],
                "embedding": other_utterance["embedding"]
            } for other_utterance in utterances if other_utterance["text"] != utterance["text"]]

    # Calculate the similarities between each utterance and all other utterances
    for utterance in utterances:
        for other_utterance in utterance["other_utterances"]:
            other_utterance["my_similarity"] = calculate_similarity(utterance["embedding"], other_utterance["embedding"])
            other_utterance["oai_similarity"] = cosine_similarity(utterance["embedding"], other_utterance["embedding"])

    # remove the embeddings from the utterances
    for utterance in utterances:
        del utterance["embedding"]
        for other_utterance in utterance["other_utterances"]:
            del other_utterance["embedding"]

    # Print it
    print(json.dumps(utterances, indent=4))



    
    

if __name__ == '__main__':
    main()