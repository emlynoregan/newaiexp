import requests
import time
from setcreds import oneai_api_key
import sys
import json
import urllib.parse
import argparse
import os

def transcribe_audio(audio_bytes, engine):
  pipeline_dict = {
      "input_type": "auto-detect",
      "steps": [
          {
              "skill": "transcribe",
              "params": {
                  "timestamp_per_word": False,
                  "engine": engine
              }
          }
      ], 
      # "content_type": "audio/mp3"
  }

  pipeline_urlencode = urllib.parse.quote(json.dumps(pipeline_dict))

  url = f"https://api.oneai.com/api/v0/pipeline/async/file?pipeline={pipeline_urlencode}"

  headers = {
    "api-key": oneai_api_key, 
    "content-type": "application/json"
  }

  print(f"Sending request to {url}...")
  r = requests.post(url, audio_bytes, headers=headers)

  if r.status_code < 200 or r.status_code >= 300:
      print(f"Error ({r.status_code}): {r.text}")
      sys.exit(1)

  data = r.json()

  get_url = f"https://api.oneai.com/api/v0/pipeline/async/tasks/{data['task_id']}"
  start_time = time.time()
  result = None
  while (True):
    r = requests.get(get_url, headers=headers)
    response = r.json()
      
    if response['status'] != "RUNNING":
      result = response
      break

    duration = time.time() - start_time
    duration_h_m_s_display = time.strftime("%H:%M:%S", time.gmtime(duration))

    print(f"waiting for task to complete (duration:{duration_h_m_s_display})... {json.dumps(response, indent=2)}")
      
    time.sleep(5)

  return result

def parse_transcription(transcription):
  # break the transcription into a list of utterances.
  # each utterance is a dictionary with the
  # speaker, start_time, and text

  transcript_lines = transcription.splitlines()

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
    # usage: python3 transcribe_audio.py <YOUR-FILE-PATH> [<ENGINE>] [<OUTPUT-FILE>]
    # default ENGINE is "default"
    # default OUTPUT-FILE is "./working/transcription_using_<ENGINE>_for_<YOUR-FILE-PATH>.json"

    # first get all the command line arguments
    parser = argparse.ArgumentParser(description='Transcribe an audio file (or audio in a video file).')

    parser.add_argument('filename', type=str, help='the path to the audio or video file')
    parser.add_argument('--engine', type=str, default="default", help='the engine to use for transcription')
    parser.add_argument('--output_file', type=str, default=None, help='the path to the output file')

    args = parser.parse_args()

    filename = args.filename
    engine = args.engine

    print (f"Transcribing {filename} using engine {engine}...")

    # remove path and extension from filename
    # do this in an os-agnostic way (eg: on Windows, the path separator is \, not /)
    cleaned_filename = os.path.splitext(os.path.basename(filename))[0]

    default_output_file_path_elems = ["working", f"transcription_using_{engine}_for_{cleaned_filename}.json"]

    default_output_file = os.path.join(*default_output_file_path_elems)

    output_file = args.output_file or default_output_file

    with open(filename, "rb") as f:
      audio_bytes = f.read()

    result = transcribe_audio(audio_bytes, engine)

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
      print(f"Error: {e}")

      print(f"Raw result: {json.dumps(result, indent=2)}")

if __name__ == "__main__":
    main()
