# ytsummary.py
## a summariser for youtube videos

ytsummary.py is a summariser for youtube videos. It uses the youtube API to get the video's transcript and then uses OpenAI's text-davinci-003 model to summarise the transcript.

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

Now you can summarize a youtube video by running:

``` 
python ytsummary.py <youtube video url> --diagnostics --mentions

```

```
--diagnostics: outputs verbose information about the summarisation process

--mentions: outputs people and things mentioned in the video
```

### Example: Transcribing "How close is nuclear fusion power?" by Sabine Hossenfelder

```
python ytsummary.py https://www.youtube.com/watch?v=LJ4W1g-6JiY
```

```
Found 2 chunks

Summary of chunk 1: 
In this section, the speaker discusses the potential 
benefits of nuclear fusion research and development, 
and how it has been incorrectly communicated to the 
public and policy makers. They then discuss the 
sponsor of the video, Magellan TV, and the 
documentary "The Story of Energy". The speaker then 
explains the concept of energy gain (Q) and how it 
relates to nuclear fusion, and how the energy gain 
that is normally quoted (Q Plasma) is not the same as 
the energy gain of the entire reactor (Q Total). They 
then discuss the current popular methods of nuclear 
fusion, and how the confusion of the energy gain has 
been around since 1988. Finally, they explain how the 
Q Total of current experiments is much lower than the 
Q Plasma, and is likely well below 0.1.

Summary of chunk 2: 
This section of the transcript discusses the confusion 
between the terms "energy" and "power" when 
discussing nuclear fusion. It also highlights the 
importance of understanding the total energy gain 
when investing in research projects, and encourages 
people to call out any popular science articles or 
interviews that do not clearly spell out the total 
energy gain.

Summary of summaries: 
This video discusses the potential benefits of nuclear 
fusion research and development, and how the concept 
of energy gain (Q) relates to nuclear fusion. It 
explains how the energy gain that is normally quoted 
(Q Plasma) is not the same as the energy gain of the 
entire reactor (Q Total). It also highlights the 
confusion between the terms "energy" and "power" 
when discussing nuclear fusion, and encourages people 
to call out any popular science articles or 
interviews that do not clearly spell out the total 
energy gain.
```
