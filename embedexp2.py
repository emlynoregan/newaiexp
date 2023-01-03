import json
import argparse

def calculate_similarity(embedding1, embedding2):
    # calculate the cosine similarity between the two embeddings
    # https://en.wikipedia.org/wiki/Cosine_similarity

    similarity = sum([a*b for a,b in zip(embedding1, embedding2)])

    magnitude1 = sum([a*a for a in embedding1]) ** 0.5

    magnitude2 = sum([a*a for a in embedding2]) ** 0.5

    similarity = similarity / (magnitude1 * magnitude2)

    return similarity

def main():
    # usage: python3 embedexp2.py <all clumps file> [<output file>]

    # first get all the command line arguments
    parser = argparse.ArgumentParser(description='analyse the transcript')

    parser.add_argument('all_clumps_file', help='the clumps file to read')
    parser.add_argument('output_file', nargs='?', help='the output file to write')

    args = parser.parse_args()

    all_clumps_file = args.all_clumps_file
    output_file = args.output_file or '.\\working\\output.json'

    # Read the clumps file as a json object
    with open(all_clumps_file, 'r') as f:
        all_clumps = json.load(f)

    # all clumps is a dictionary of clumps.
    # a clump is a dictionary with the following keys:
    # {
    #     "key": "0:1",
    #     "start": 0,
    #     "length": 1,
    #     "utterances": [
    #         {
    #             "text": "- How did we go from\nhats being a crucial part",
    #             "start": 0.12,
    #             "duration": 2.19
    #         }
    #     ],
    #     "embedding": <list of floats>
    # }

    # Throw away all clumps with length greater than 1
    all_clumps = [clump for clump in all_clumps.values() if clump['length'] == 1]

    # For each remaining clump, calculate the semantic similarity between the clump and the next clump
    # and add it to the clump as a new key called "similarity"

    clump_pairs = zip(all_clumps[:-1], all_clumps[1:])

    all_clumps = [{
        **clump,
        'similarity': calculate_similarity(clump.get("embedding"), next_clump.get("embedding"))
    } for clump, next_clump in clump_pairs]

    # remove the embeddings from the clumps
    all_clumps = [{
        **clump,
        'embedding': None
    } for clump in all_clumps]

    # Write the clumps to the output file
    with open(output_file, 'w') as f:
        json.dump(all_clumps, f, indent=2)

    
    

if __name__ == '__main__':
    main()