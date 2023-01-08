# In this program we will read the transcript of a youtube video and summarize it

import setcreds
from youtube_transcript_api import YouTubeTranscriptApi
from utils import get_chunks_from_transcript, summarize_audio_transcript_chunks, set_diagnostics
import argparse
import os
import json

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

def main():
    # usage: python3 ytsummary.py <YOUR-FILE-PATH>  [--outfile <output_filename>] [--prompt_header <promptheader_filename>] [--chunk_len_mins <int>] [--diagnostics] [--mentions] [--save_transcript <transcript_filename>]

    # first get all the command line arguments
    parser = argparse.ArgumentParser(description='Summarize a youtube video.')

    parser.add_argument('video_id_or_url', type=str, help='The video id or url of the video to summarize')
    parser.add_argument('--outfile', type=str, help='The name of the file to write the summary to')
    parser.add_argument('--prompt_header', type=str, help='The name of the file to write the prompt header to')
    parser.add_argument('--chunk_len_mins', type=int, help='The length of the chunks to summarize in minutes')
    parser.add_argument('--diagnostics', action='store_true', help='Print out the prompts and responses')
    parser.add_argument('--mentions', action='store_true', help='Include people and entities mentioned in the video')
    parser.add_argument('--save_transcript', type=str, help='The name of the file to write the transcript to')

    args = parser.parse_args()

    video_id_or_url = args.video_id_or_url
    video_id = get_video_id_from_video_id_or_url(video_id_or_url)
    outfile_name = args.outfile
    transcript_outfile_name = args.save_transcript

    if not outfile_name:
        default_output_file_path_elems = ["working", f"yt_transcript_{video_id}.txt"]

        outfile_name = os.path.join(*default_output_file_path_elems)

    # create any intermediate directories if they don't exist, in an OS independent way            
    os.makedirs(os.path.dirname(outfile_name), exist_ok=True)

    prompt_header = None
    prompt_header_file = args.prompt_header
    if prompt_header_file:
        with open(prompt_header_file, "r") as f:
            prompt_header = f.read()

    chunk_len_mins = args.chunk_len_mins if args.chunk_len_mins else 10

    set_diagnostics(args.diagnostics)

    include_mentions = args.mentions

    transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=("en", "en-US", "en-GB"))

    if transcript_outfile_name:
        # write the transcript as json to a file
        with open(transcript_outfile_name, "w") as f:
            json.dump(transcript, f)

    chunks = get_chunks_from_transcript(transcript, chunk_len_mins)

    result = summarize_audio_transcript_chunks(chunks, prompt_header, include_mentions, chunk_len_mins)

    with open(outfile_name, "w") as f:
        f.write(result)

if __name__ == "__main__":
    main()
