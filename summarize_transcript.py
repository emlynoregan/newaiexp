# In this program we will read a transcript from file, and summarize it

import setcreds
import json
import argparse
import os
from utils import transcribe_video_transcript_chunks, get_chunks_from_transcript

diagnostics = 0
include_mentions = 0

def main():
    # usage: python3 summarize_transcript.py <transcription_filename> [--outfile <output_filename>] [--prompt_header <promptheader_filename>] [--chunk_len_mins <int>] [--diagnostics] 

    # first get all the command line arguments
    parser = argparse.ArgumentParser(description='Summarize a youtube video transcript')

    parser.add_argument('transcription_filename', type=str, help='the filename of the transcript to summarize')
    parser.add_argument('--outfile', type=str, help='the filename to write the summary to')
    parser.add_argument('--prompt_header', type=str, help='the filename of a file containing a header to add to the prompt')
    parser.add_argument('--chunk_len_mins', type=int, default=10, help='the length of the chunks to summarize')
    parser.add_argument('--diagnostics', action='store_true', help='print out diagnostic information')

    args = parser.parse_args()

    transcription_filename = args.transcription_filename
    output_file = args.outfile
    prompt_header_filename = args.prompt_header
    chunk_len_mins = args.chunk_len_mins
    global diagnostics
    diagnostics = args.diagnostics

    if not output_file:
        cleaned_filename = os.path.splitext(os.path.basename(transcription_filename))[0]

        default_output_file_path_elems = ["working", f"summary_of_{cleaned_filename}.txt"]

        output_file = os.path.join(*default_output_file_path_elems)

    # create any intermediate directories if they don't exist, in an OS independent way            
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with (open(transcription_filename, "r")) as f:
        transcript = json.load(f)

    # read the prompt header file
    prompt_header = None
    if prompt_header_filename:
        with (open(prompt_header_filename, "r")) as f:
            prompt_header = f.read()

    # chunks = get_chunks(transcript_file_name)
    chunks = get_chunks_from_transcript(transcript, chunk_len_mins)

    result = transcribe_video_transcript_chunks(chunks, prompt_header, include_mentions, chunk_len_mins)

    with open(output_file, "w") as f:
        f.write(result)

if __name__ == "__main__":
    main()
