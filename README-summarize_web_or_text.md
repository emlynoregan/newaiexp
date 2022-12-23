# summarize_web_or_text.py
## summarizes a web page or text file

You will require an api key for Open API. Sign up for one [here](https://openai.com/api/). Note that this will cost money, use it at your own risk.

Also, if you add a key for ScrapingRobot (https://scrapingrobot.com), then it will be used to scrape the web page instead of just using a GET. You can
turn this behaviour off with --noscrape

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

Next, copy the file 'setcreds template.py' to 'setcreds.py' and fill in your OpenAI API key, and optionally your ScrapingRobot API key.

Now you can summarize a web page or text file by running:

Usage:
---
```
    python3 summarize_web_or_text.py <url_or_file> [--outfile <output_filename>] [--prompt_header <promptheader_filename>] [--chunk_size_chars <int>] [--noscrape] [--diagnostics] 
```

url_or_file: the url of the web page to summarize, or the filename of the text file to summarize.

outfile: the filename to write the summary to. If not specified, the summary will be printed to a default filename.

prompt_header: a file containing extra instructions for text-davinci-003, inserted into summarization prompts. This is optional. You could include text like "Skip all the ads" or "Do not include information about ads in the summary". The file can be multiple lines, not too long, and do include a few newlines at the end.

chunk_size_chars: the size of each chunk of text to summarize. The default is 5000 characters. Larger chunk sizes result in less summaries, but you may lose detail. Smaller chunk sizes result in more summaries, but mean you'll have more to read, and the overall summary's prompt may be too long and fail.

noscrape: if this is set, the script will not use ScrapingRobot to scrape the web page. This is useful if you don't have a key, or if you don't want to use it.

diagnostics: if this is set, the script will print out the prompts it is using, and the summaries it gets back. This is useful for debugging.

Results:
---
This is the command:
```
python .\summarize_web_or_text.py https://en.wikipedia.org/wiki/Natural-language_understanding
```

This is the output:
```
len(raw_text): 21912
# Chunks:  5

Summary of chunk 1:
-----
Natural-language understanding (NLU) is a subtopic of natural-language processing in artificial intelligence that deals with machine reading comprehension. This section of the text document discusses the importance of donations to Wikipedia and encourages readers to donate, providing them with various payment methods. It also explains the benefits of making a recurring donation and provides information about the Wikimedia Foundation, a nonprofit, tax-exempt organization.

Summary of chunk 2:
-----
This section discusses the history of natural-language understanding, a field of artificial intelligence that deals with machine reading comprehension. It begins with the 1964 program STUDENT, written by Daniel Bobrow for his PhD dissertation, and the 1965 program ELIZA, written by Joseph Weizenbaum. It then covers Roger Schank's conceptual dependency theory from 1969, William A. Woods' augmented transition network from 1970, and Terry Winograd's SHRDLU from 1971. It also mentions the natural language processing group at SRI International in the 1970s and 1980s, and the IBM Watson from the third millennium. The scope and context of natural-language understanding is discussed, with examples of applications ranging from simple commands issued to robots to the full comprehension of newspaper articles.

Summary of chunk 3:
-----
This section discusses the development of natural language processing (NLP) systems, which are used to process and understand natural language. It outlines the components and architecture of such systems, which include a lexicon, parser, grammar rules, and semantic theory. It also discusses the challenges of context management and the trade-offs between different semantic theories. Finally, it mentions some related topics, such as computational semantics, discourse representation theory, and information extraction.

Summary of chunk 4:
-----
This section provides a brief history of Artificial Intelligence (AI), including a discussion of various milestones in the development of AI, such as Daniel Bobrow's PhD thesis, Machines Who Think by Pamela McCorduck, and Roger Schank's 1969 conceptual dependency parser. It also covers topics such as natural language processing, text processing, text analysis, and semantic role labeling. Additionally, the section mentions various language resources, datasets, and corpora that are used in AI research.

Summary of chunk 5:
-----
This section of the text document provides an overview of various natural language processing technologies, such as Google Ngram Viewer, WordNet, Automatic Identification and Data Capture, Speech Recognition, Speech Segmentation, Speech Synthesis, Natural Language Generation, Optical Character Recognition, Topic Model, Document Classification, Latent Dirichlet Allocation, Pachinko Allocation, Computer-Assisted Reviewing, Automated Essay Scoring, Concordancer, Grammar Checker, Predictive Text, Spell Checker, Syntax Guessing, Natural Language User Interface, Chatbot, Interactive Fiction, Question Answering, Virtual Assistant, Voice User Interface, and Natural Language Toolkit spaCy. It also provides information about the Creative Commons Attribution-ShareAlike License 3.0 and the Terms of Use and Privacy Policy.

Overall summary
-----
This text document covers the topics of natural-language understanding, natural-language processing, artificial intelligence, and various natural language processing technologies. It discusses the importance of donations to Wikipedia, the history of NLU, the components and architecture of NLP systems, the development of AI, and the Creative Commons Attribution-ShareAlike License 3.0 and the Terms of Use and Privacy Policy.
```