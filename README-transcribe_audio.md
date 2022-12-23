# transcribe_audio.py
## transcribes a audio on your local filesystem by sending it to https://oneai.com

You will require an api key for One API. Sign up for one [here](https://oneai.com/). Note that this will cost money, use it at your own risk.

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

Next, copy the file 'setcreds template.py' to 'setcreds.py' and fill in your OneAI API key.

Now you can transcribe an audio or video file by running:

```
python transcribe_audio.py <audio or video file> ["default"|"whisper"] [<outfile name>]
```

"default" is the default engine, "whisper" is openai's whisper engine.

Results:

This call can run for a while! As a very rough guide, a 40 minute video could take 10 minutes to transcribe.
It will output progress like so:

```
waiting for task to complete (duration:00:07:18)... {
  "task_id": "60f6581c-1596-4ce4-914c-65ebca1e0435",
  "status": "RUNNING",
  "creation_time": "2022-12-23T01:27:09.213000"
}
waiting for task to complete (duration:00:07:24)... {
  "task_id": "60f6581c-1596-4ce4-914c-65ebca1e0435",
  "status": "RUNNING",
  "creation_time": "2022-12-23T01:27:09.213000"
}
waiting for task to complete (duration:00:07:29)... {
  "task_id": "60f6581c-1596-4ce4-914c-65ebca1e0435",
  "status": "RUNNING",
  "creation_time": "2022-12-23T01:27:09.213000"
}
...
```

When it finishes, it will parse the transcription, and write the results to a file called 
```
    ./working/transcription_using_{engine}_for_{filename}.json
```
or the outfile name you provided.