# ytqa.py
## a q&a bot for youtube videos

ytqa.py is a q&a bot for youtube videos. It breaks the transcript into groups of utterances, generates embeddings, and stores that in a file. It then uses the embeddings to find relevant utterances for adding to a prompt, and uses the prompt to generate an answer. It uses [text-davinci-003 from openai](https://openai.com/api/) to generate the answer, [text-embedding-ada-002](https://openai.com/api/) to generate the embeddings, and [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/) to extract the transcript.

Note that the first time you use this script for a video, it will download the transcript and generate the embeddings. This will take a while (can be 10 minutes plus for many hours of video). Subsequent runs will be much faster.

The script generates a lot of embeddings, but these are very cheap compared to text completion. 

You will require an api key for Open API. Sign up for one [here](https://openai.com/api/). Note that this will cost money, use it at your own risk.

### Usage

First install python (I used v3.10). Then set up a virtual environment and install the requirements using the setupvenv script:

Windows:
```
.\setupvenv.ps1
```

Linux / Mac:
```
. ./setupvenv.sh
```

Next, copy the file 'setcreds template.py' to 'setcreds.py' and fill in your OpenAI API key.

Now you can begin a q&a session on a youtube video by running:

``` 
python ytqa.py <youtube video url> [--prompt_header <promptheader_filename>] [--diagnostics] [--embeddings-db <embeddings_db_filename>]

```

```
--diagnostics: outputs verbose information

--embeddings-db: specifies the filename to use for the embeddings database. If not specified, the default is ./working/yt_embeddings_db_{video_id}.json

--prompt_header: if specified, indicates a text file to insert into prompts. This can be used to provide context for the question.

``` 

### Example: Q&A about "How close is nuclear fusion power?" by Sabine Hossenfelder

NOTE: Before running this script, try running ytsummary.py to get a summary of the video. This will give you a better idea of what the video is about, and will help you formulate better questions.

```
python ytqa.py https://www.youtube.com/watch?v=LJ4W1g-6JiY
```

First time, you'll get lots of lines like this, as the embeddings are generated:

```
Creating new utterance: {'start': 419.68, 'duration': 41.281, 'text': 'in our view the correct scientific criterion must dominate the program from the earliest stages the danger of not doing this could be that the entire program is dedicated to pursuing performance parameters which are simply not relevant to the eventual goal the result of doing this could in the'}
Processing utterance 174
Creating new utterance: {'start': 421.599, 'duration': 4.88, 'text': 'criterion must dominate the program from'}
Creating new utterance: {'start': 421.599, 'duration': 14.161, 'text': 'criterion must dominate the program from the earliest stages the danger of not doing this could be'}
Creating new utterance: {'start': 421.599, 'duration': 24.0, 'text': 'criterion must dominate the program from the earliest stages the danger of not doing this could be that the entire program is dedicated to pursuing performance parameters which'}
Creating new utterance: {'start': 421.599, 'duration': 31.521, 'text': 'criterion must dominate the program from the earliest stages the danger of not doing this could be that the entire program is dedicated to pursuing performance parameters which are simply not relevant to the eventual goal'}
Creating new utterance: {'start': 421.599, 'duration': 41.6, 'text': 'criterion must dominate the program from the earliest stages the danger of not doing this could be that the entire program is dedicated to pursuing performance parameters which are simply not relevant to the eventual goal the result of doing this could in the very worst scenario be the enormous'}
```

Then you'll get a prompt:
```
Hi, I'm a bot. Ask me a question about the video, and I'll try to find the answer for you.

> What are the methods of nuclear fusion listed in the video?

The video mentions two methods of nuclear fusion: heating the fuel in strong magnetic fields until it becomes a plasma, and using lasers to pump the plasma. The video notes that the currently most widely used technology for nuclear fusion is heating the fuel in strong magnetic fields until it becomes a plasma, while the National Ignition Facility in the United States reported they'd managed to get out 70 percent of the energy they put in by pumping the plasma with lasers. The video also mentions the European Taurus Jet, which set the previous record of 0.67 for energy gain in 1997.

> Does it mention tokomaks?

No, the video does not mention tokomaks. The video mentions two methods of nuclear fusion: heating the fuel in strong magnetic fields until it becomes a plasma, and using lasers to pump the plasma.> Which one is better?Here's what I found:The video does not make a definitive statement about which one is better. It notes that the most widely used technology for nuclear fusion is heating the fuel in strong magnetic fields until it becomes a plasma, while the National Ignition Facility in the United States reported they'd managed to get out 70 percent of the energy they put in by pumping the plasma with lasers. Ultimately, the choice of which method to use depends on the specific application and the resources available.

> stop
```
