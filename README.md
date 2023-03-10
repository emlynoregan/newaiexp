# newaiexp
A general repo for short, cli based experiments with new AI tools, particularly from OpenAI

## ytsummary.py
A tool for summarizing youtube videos. It uses the [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/) package to download the video and extract the transcript, then uses [text-davinci-003 from openai](https://openai.com/api/) to summarize the transcript.

[More info](README-ytsummary.md)

## ytqa.py
A tool for asking questions about youtube videos. It breaks the transcript into groups of utterances, generates embeddings, and 
stores that in a file. It then uses the embeddings to find relevant utterances for adding to a prompt, and uses the prompt to generate an answer. It uses [text-davinci-003 from openai](https://openai.com/api/) to generate the answer, [text-embedding-ada-002](https://openai.com/api/) to generate the embeddings, and [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/) to download the video and extract the transcript.

[More info](README-ytqa.md)

## transcribe_audio.py
This script transcribes an audio file, or a video, on your local filesystem by sending it to https://oneai.com. You can choose the engine to use for transcription; either their own default engine "default", or openai's "whisper".

[More info](README-transcribe_audio.md)

## summarize_transcript.py
This script summarizes a transcript file using openai's text-davinci-003 engine, similarly to ytsummary.py.
The transcript file must be in the format output from transcribe_audio.py.

[More info](README-summarize_transcript.md)

## summarize_web_or_text.py
This script summarizes a web page or a text file using openai's text-davinci-003 engine. It has optional support for ScrapingRobot, which can be used to scrape the web page before summarizing it.

[More info](README-summarize_web_or_text.md)

## ddgsearch.py
This script searches duckduckgo, then scrapes each result page for text, and returns a list of results including url, title, and text, and useful_text.

[More info](README-ddgsearch.md)
