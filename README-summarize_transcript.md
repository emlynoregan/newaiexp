# summarize_transcript.py
## summarizes a video transcript file

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

Now you can transcribe a video by running:

Usage:
---
```
python3 summarize_transcript.py <transcription_filename> [--outfile <output_filename>] [--prompt_header <promptheader_filename>] [--chunk_len_mins <int>] [--diagnostics]
```
transcript_filename: the filename of the transcript to summarize. This should be a json file, as produced by transcribe_video.py

prompt_header: a file containing extra instructions for text-davinci-003, inserted into summarization prompts. This is optional. You could include text like "Speaker 1 is Fred Bloggs" or "Do not include information about ads in the summary". The file can be multiple lines, not too long, and do include a few newlines at the end.

chunk_len_mins: the length of each chunk of text to summarize. The default is 10 minutes. Larger chunk lengths result in less summaries, but you may lose detail. Smaller chunk lengths result in more summaries, but mean you'll have more to read, and the overall summary's prompt may be too long and fail.

diagnostics: if this is set, the script will print out the prompts it is using, and the summaries it gets back. This is useful for debugging.

Results:
---

transcription.json is a file containing the transcript of the mp3 from [here](https://www.thisamericanlife.org/757/the-ghost-in-the-machine).

promptheader_tal.txt is a file containing the following:
```
Speaker 1 is Ira Glass.
Speaker 2 is also Ira Glass.
Speaker 3 is Michelle Dawson Haber.
```

This is the command:
```
python3 summarize_transcript.py ./transcription.json --prompt_header ./promptheader_tal.txt
```

This is the output:
```
Found 7 chunks

Summary of section beginning at 0:00:00
-----
In this section of the transcript, Ira Glass talks about the importance of recording and preserving sound, and how it can be used to capture memories and moments that would otherwise be lost. He shares the story of Michelle Dawson Haber, who never knew her father, but was able to hear his voice for the first time when her sister found 25 recordings of him singing opera. He then talks about Thomas Edison, who invented the phonograph machine, and how the RCA logo was based on a painting of a dog listening to a recording of its dead master's voice. Finally, Ira visits Edison's lab in New Jersey, where he sees the first phonograph machine and reflects on the importance of recording sound.

Summary of section beginning at 0:10:00
-----
In this section, Ira Glass and Michelle Dawson Haber discuss the technology of GPT-3, an artificial intelligence program that can write remarkably like a human. They talk about how Wahid Ivar used the program to try and write about her sister's death, which she had never been able to do before. She fed the program very little to work with at first, but with each subsequent draft, she fed it more and more. The AI responded with stories that were sometimes nuanced and sometimes a total mess. The AI was able to pick up on the sentiment of loss, but it was unable to fully articulate the emotions of grief.

Summary of section beginning at 0:20:00
-----
In this section of the transcript, Michelle Dawson Haber and Ira Glass discuss how GPT-3, an AI, has been used to explore grief. Michelle has been using GPT-3 to write about her sister who passed away, and Ira has been observing the process. They discuss how GPT-3 can evoke specific feelings and memories, and how it can become stuck in repetitive loops. They also talk about how GPT-3 can pull from the collective experience of people writing about grief, and how it can synthesize it into a reflection of our own grief, even though it does not understand it.

Summary of section beginning at 0:30:00
-----
In this section of the transcript, Ira Glass and Michelle Dawson Haber discuss the story of Gene, a woman who is claustrophobic and whose father was part of the team that built the first full body MRI in 1980. Gene visits the machine in Aberdeen, Scotland, where her sister lives, to commune with her father who has since passed away. She describes the machine as looking "janky" and having her father's handwriting and math on various pieces.

Summary of section beginning at 0:40:00
-----
In this section of the transcript, Ira Glass and Michelle Dawson Haber discuss the story of Jonah Furman and his father Boris. Boris has been calculating the family's average location for the past ten years, by asking his children and their spouses for their sleep locations and then finding the average coordinates of those locations. He then puts those coordinates into MapQuest to find the family's average location, which changes depending on where everyone is.

Summary of section beginning at 0:50:00
-----
In this section of the transcript, speaker 3 (Michelle Dawson Haber) interviews members of the family of Boris, who has been sending emails to his family with the Family Average Location (FAL) for the past eight years. The family members discuss why Boris does this, and it is revealed that Boris' parents escaped the Holocaust and his family was torn apart. They explain that the FAL is a way for Boris to keep track of his family and to keep them connected, even though they are now living in different places. They also discuss how the FAL is a way for Boris to repair the tragedy of his family's past, and how it is a way for him to show his love for his family.

Summary of section beginning at 1:00:00
-----
In this section of the transcript, Ira Glass and Michelle Dawson Haber discuss Alex Edelman's story of how his Orthodox Jewish parents celebrated Christmas with him and his brother AJ. AJ was so excited that he stood on the couch and exclaimed "Santa came!" Ira Glass then announces that this story will be featured on the podcast of This American Life the following week.

Overall summary
-----
This transcript covers a variety of stories about the power of sound and technology to capture memories and moments that would otherwise be lost. It discusses the use of GPT-3, an artificial intelligence program, to explore grief, as well as the story of Gene, who visited the first full body MRI machine in Aberdeen, Scotland to commune with her father. It also covers the story of Jonah Furman and his father Boris, who has been sending emails to his family with the Family Average Location for the past eight years, and Alex Edelman's story of how his Orthodox Jewish parents celebrated Christmas with him and his brother AJ.