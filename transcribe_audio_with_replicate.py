import requests
import time
from setcreds import replicate_api_key
import sys
import json
import urllib.parse
import argparse
import os
from replicate import Client

def transcribe_audio(audio_url):
  client = Client(replicate_api_key)
  model = client.models.get("openai/whisper")
  version = model.versions.get("30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed")
  output = version.predict(audio=audio_url)

  return output

def parse_transcription(transcription):
  # break the transcription into a list of utterances.
  # each utterance is a dictionary with the
  # speaker, start_time, and text

  transcript_lines = transcription.splitlines()
  print (len(transcript_lines))
  if len(transcript_lines) < 10:
    print(f"transcript lines: {transcript_lines}")

  heading_and_text_line_pairs = []
  for i in range(0, len(transcript_lines), 3):
      
      heading_and_text_line_pairs.append((transcript_lines[i], transcript_lines[i+1]))

  print (heading_and_text_line_pairs)

  utterances = []

  for heading_line, text_line in heading_and_text_line_pairs:
      heading_line = heading_line.strip()
      start_part, speaker_part = heading_line.split("] ")
      start_time = start_part[1:]
      speaker = speaker_part[:-1]
      text = text_line.strip()

      utterance = {
          "speaker": speaker,
          "start_time": start_time,
          "text": text
      }
      utterances.append(utterance)

  return utterances

def main():
    # usage: python3 transcribe_audio.py audiourl [<OUTPUT-FILE>]
    # default OUTPUT-FILE is "./working/transcription_using_<ENGINE>_for_<YOUR-FILE-PATH>.json"

    # first get all the command line arguments
    parser = argparse.ArgumentParser(description="Transcribe audio using OpenAI's Whisper model.")

    parser.add_argument("audiourl", help="The url of the audio file to transcribe.")
    parser.add_argument("output_file", nargs="?", help="The path to the output file. If not specified, the default is ./working/transcription_using_replicate_for_<YOUR-FILE-PATH>.json")

    args = parser.parse_args()

    # get the audio file path from the command line arguments
    audio_url = args.audiourl

    print (f"Transcribing {audio_url} using whisper...")

    # remove path and extension from filename
    # do this in an os-agnostic way (eg: on Windows, the path separator is \, not /)

    # get a version of the audio url that is safe to use as a filename
    audio_url_safe = urllib.parse.quote(audio_url, safe="")

    cleaned_filename = os.path.splitext(os.path.basename(audio_url_safe))[0]

    default_output_file_path_elems = ["working", f"transcription_using_replicate_for_{cleaned_filename}.json"]

    default_output_file = os.path.join(*default_output_file_path_elems)

    output_file = args.output_file or default_output_file

    # with open(filename, "rb") as f:
    #   audio_bytes = f.read()

    result = transcribe_audio(audio_url)

    print (result)

    return

    if result is None:
      print("Error: no result")
      return

    if result['status'] != "COMPLETED":
      print(f"Error: {json.dumps(result, indent=2)}")
      return

    try:
      # the transcription is in result['result']['input_text']
      transcription = result['result']['input_text']

      utterances = parse_transcription(transcription)

      print(f"Writing {len(utterances)} utterances to {output_file}...")

      # write the utterances to a file
      with open(output_file, "w") as f:
        json.dump(utterances, f, indent=2)

      print("Done.")
    except Exception as e:
      import traceback

      full_error = traceback.format_exc()

      print(f"Error: {full_error}")

      print(f"Raw result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main()
