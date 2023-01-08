# this module contains helper functions
import openai
diagnostics = False

def set_diagnostics(value):
    global diagnostics
    diagnostics = value

def get_diagnostics():
    global diagnostics
    return diagnostics

def get_chunks_from_transcript(transcript, chunk_length_mins=10.0):
    # this function converts a transcript of a video
    # into an array of chunks
    # where each chunk is an array of lines

    # An example of a transcript:
    # [
    #     {
    #         'speaker': 'speaker1',
    #         'text': 'Hey there',
    #         'start': 7.58,
    #         'duration': 6.13
    #     },
    #     {
    #         'speaker': 'speaker1',
    #         'text': 'how are you',
    #         'start': 14.08,
    #         'duration': 7.58
    #     },
    #     # ...
    # ]
    # 
    # The duration is optional.
    # The speaker is optional.
    # The start could also be a string like this: "00:00:24.410"
    # start might also be called start_time

    def add_new_chunk(chunks, new_chunk):
        if len(new_chunk) > 0:
            # get the previous chunk
            previous_chunk = None
            if len(chunks) > 0:
                previous_chunk = chunks[-1]

            # Add up to 3 lines from the previous chunk to the new chunk
            if previous_chunk is not None:
                # get the last 3 lines from the previous chunk
                last_lines = previous_chunk[-3:]
                # add them to the new chunk
                new_chunk = last_lines + new_chunk

            # Add up to 3 lines from the new chunk to the previous chunk
            if previous_chunk is not None:
                # get the first 3 lines from the new chunk
                first_lines = new_chunk[:3]
                # add them to the previous chunk
                previous_chunk = previous_chunk + first_lines

            # add the new chunk to the list of chunks
            chunks.append(new_chunk)

        return chunks

    chunks = []

    start_timestamp = 0.0
    current_timestamp_mins = 0.0

    current_chunk = []

    for entry in transcript:
        start = entry.get('start') or entry.get('start_time')

        # if the start is a string, convert it to a float
        if isinstance(start, str):
            # parse the string into a duration
            # the string is in the format "00:00:24.410"
            # where the first two numbers are the hours
            # the next two numbers are the minutes
            # the next two numbers are the seconds
            # the last three numbers are the milliseconds

            # split the string into hours, minutes, seconds, and milliseconds
            hours, minutes, seconds_and_milliseconds = start.split(":")
            seconds, milliseconds = seconds_and_milliseconds.split(".")
            # convert the strings to numbers
            hours = int(hours)
            minutes = int(minutes)
            seconds = int(seconds)
            milliseconds = int(milliseconds)
            # convert the duration to seconds
            start = hours * 3600 + minutes * 60 + seconds + milliseconds / 1000.0

        try:
            current_timestamp_mins = start / 60.0
        except:
            pass # just use the previous timestamp

        # if the current timestamp is more than chunk_length_mins minutes after the start timestamp
        # then we have a chunk
        if current_timestamp_mins - start_timestamp > chunk_length_mins:
            # add the current chunk to the list of chunks
            chunks = add_new_chunk(chunks, current_chunk)
            # reset the start timestamp
            start_timestamp = current_timestamp_mins
            # reset the current chunk
            current_chunk = []

        # if we have a speaker, then the line should be <speaker>: <text>
        # otherwise, it's just <text>
        if 'speaker' in entry:
            line = f"{entry['speaker']}: {entry['text']}"
        else:
            line = entry['text']

        # add the line to the current chunk
        current_chunk.append(line)

    # add the last chunk
    if len(current_chunk) > 0:
        chunks.append(current_chunk)

    print(f"Found {len(chunks)} chunks")

    return chunks

def summarize_chunk(index, chunk, prompt_header):
    chunk_str = "\n".join(chunk)
    prompt = f"""The following is a section of the transcript of a youtube video. It is section #{index+1}:

{chunk_str}

{prompt_header}Summarize this section of the transcript."""

    if diagnostics:
        # print each line of the prompt with a leading # so we can see it in the output
        for line in prompt.split('\n'):
            print(f"# {line}")

    completion = openai.Completion.create(
        engine="text-davinci-003", 
        max_tokens=500, 
        temperature=0.2,
        prompt=prompt,
        frequency_penalty=0
    )

    msg = completion.choices[0].text

    if diagnostics:
        print(f"# Response: {msg}")

    return msg

def summarize_the_summaries(summaries, prompt_header):

    summaries_str = ""
    for index, summary in enumerate(summaries):
        summaries_str += f"Summary of chunk {index+1}:\n{summary}\n\n"

    prompt = f"""The following are summaries of a youtube video in 10 minute chunks:"

{summaries_str}

{prompt_header}Summarize the summaries."""

    if diagnostics:
        # print each line of the prompt with a leading # so we can see it in the output
        for line in prompt.split('\n'):
            print(f"# {line}")

    completion = openai.Completion.create(
        engine="text-davinci-003", 
        max_tokens=500, 
        temperature=0.2,
        prompt=prompt,
        frequency_penalty=0
    )

    msg = completion.choices[0].text

    if diagnostics:
        print(f"# Response: {msg}")

    return msg

def people_and_entities_mentioned_in_chunk(index, chunk, prompt_header):
    # this function will return a list of people who appear to be speaking in the chunk,
    # and a list of people mentioned in the chunk, but not speaking.

    # first get the people speaking:
    chunk_str = "\n".join(chunk)
    prompt = f"""The following is a section of the transcript of a youtube video. It is section #{index+1}:

{chunk_str}

{prompt_header}Who is mentioned in this section of the transcript? Include people, companies or organizations, and other non-human entities."""

    if diagnostics:
        # print each line of the prompt with a leading # so we can see it in the output
        for line in prompt.split('\n'):
            print(f"# {line}")

    completion = openai.Completion.create(
        engine="text-davinci-003", 
        max_tokens=500, 
        temperature=0.2,
        prompt=prompt,
        frequency_penalty=0
    )

    mentioned = completion.choices[0].text

    if diagnostics:
        print(f"# Response: {mentioned}")

    # now we have the people speaking and the people mentioned
    # we can return them
    return mentioned
    
def summarize_mentions(mentioneds, prompt_header):
    mentioneds_str = ""
    for index, mentioned in enumerate(mentioneds):
        mentioneds_str += f"People mentioned in chunk {index+1}:\n{mentioned}\n\n"

    prompt = f"""The following are the people and other entities mentioned in a youtube video in 10 minute chunks:"

{mentioneds_str}

{prompt_header}Summarize the people and entitites mentioned."""

    if diagnostics:
        # print each line of the prompt with a leading # so we can see it in the output
        for line in prompt.split('\n'):
            print(f"# {line}")

    completion = openai.Completion.create(
        engine="text-davinci-003", 
        max_tokens=500, 
        temperature=0.2,
        prompt=prompt,
        frequency_penalty=0
    )

    msg = completion.choices[0].text

    if diagnostics:
        print(f"# Response: {msg}")

    return msg

def summarize_audio_transcript_chunks(chunks, prompt_header, include_mentions, chunk_len_mins):
    result = ""

    if len(chunks) == 0:
        output = "No chunks found"
        print(output)
        result += output
    elif len(chunks) == 1:
        summary = summarize_chunk(0, chunks[0], prompt_header)
        output = f"Summary: {summary}"
        print(output)
        result += output

        if include_mentions:
            mentioned = people_and_entities_mentioned_in_chunk(0, chunks[0], prompt_header)
            output = f"\nPeople mentioned: {mentioned}"
            print(output)
            result += output
    else:
        # Now we have the chunks, we can summarize each one
        summaries = []
        mentioneds = []
        for index, chunk in enumerate(chunks):
            summary = summarize_chunk(index, chunk, prompt_header)
            summaries.append(summary)

            chunk_start_time_mins = index * chunk_len_mins

            display_chunk_start_time_h_m_s = f"{chunk_start_time_mins // 60}:{chunk_start_time_mins % 60:02d}:00"

            output = f"\nSummary of section beginning at {display_chunk_start_time_h_m_s}\n-----\n{summary.strip()}"

            if include_mentions:
                mentioned = people_and_entities_mentioned_in_chunk(index, chunk)
                mentioneds.append(mentioned)
                output += f"\n\nPeople mentioned:\n-----\n{mentioned.strip()}"

            print(output)
            result += output

        # Now we have the summaries, we can summarize the summaries
        summary_of_summaries = summarize_the_summaries(summaries, prompt_header)

        output = f"\nOverall summary\n-----\n{summary_of_summaries.strip()}"

        if include_mentions:
            # Now we have the people speaking and mentioned, we can summarize them
            # summary_of_people = summarize_the_people(speakings, mentioneds)
            summary_of_people = summarize_mentions(mentioneds, prompt_header)

            output += f"\n\nSummary of people:\n-----\n{summary_of_people.strip()}"
        
        print(output)
        result += output

    return result

def summarize_single_text_chunk(index, chunk, prompt_header):
    prompt = f"""The following is a section of a text document. It is section #{index+1}:

{chunk}

{prompt_header}Summarize this section."""

    if diagnostics:
        # print each line of the prompt with a leading # so we can see it in the output
        for line in prompt.split('\n'):
            print(f"# {line}")

    completion = openai.Completion.create(
        engine="text-davinci-003", 
        max_tokens=500, 
        temperature=0.2,
        prompt=prompt,
        frequency_penalty=0
    )

    msg = completion.choices[0].text

    if diagnostics:
        print(f"# Response: {msg}")

    return msg

def summarize_the_text_summaries(summaries, prompt_header):
    summaries_str = ""
    for index, summary in enumerate(summaries):
        summaries_str += f"Summary of section {index+1}:\n{summary}\n\n"

    prompt = f"""A text document, possibly from a web page, is broken into sections. Each section is summarized. The summaries are:"

{summaries_str}

{prompt_header}Summarize the summaries."""

    if diagnostics:
        # print each line of the prompt with a leading # so we can see it in the output
        for line in prompt.split('\n'):
            print(f"# {line}")

    completion = openai.Completion.create(
        engine="text-davinci-003", 
        max_tokens=500, 
        temperature=0.2,
        prompt=prompt,
        frequency_penalty=0
    )

    msg = completion.choices[0].text

    if diagnostics:
        print(f"# Response: {msg}")

    return msg

def summarize_text_chunks(chunks, prompt_header):
    result = ""

    if len(chunks) == 0:
        output = "No chunks found"
        print(output)
        result += output
    elif len(chunks) == 1:
        summary = summarize_single_text_chunk(0, chunks[0], prompt_header)
        output = f"Summary: {summary}"
        print(output)
        result += output
    else:
        # Now we have the chunks, we can summarize each one
        summaries = []
        for index, chunk in enumerate(chunks):
            summary = summarize_single_text_chunk(index, chunk, prompt_header)
            summaries.append(summary)
            output = f"\nSummary of chunk {index+1}:\n-----\n{summary.strip()}"
            print(output)
            result += f"{output}\n"

        # Now we have the summaries, we can summarize the summaries
        summary_of_summaries = summarize_the_text_summaries(summaries, prompt_header)

        output = f"\nOverall summary\n-----\n{summary_of_summaries.strip()}"
        print(output)
        result += output
    
    return result

