# In this program we will read a webpage and summarize it
# Where the page is longer than 10 minutes, we will split it into 10 minute chunks

# I'm using scrapingrobot to get the text of the webpage
# website: https://scrapingrobot.com
# Affiliate link: https://billing.scrapingrobot.com/aff.php?aff=2


from setcreds import scraping_api_key
import openai
import sys
import requests
from bs4 import BeautifulSoup
import json
from utils import summarize_text_chunks, set_diagnostics
import argparse
import os

diagnostics = 0
include_mentions = 0

def get_webpage_via_scraping(scraping_api_key, url):
    # this function will get the text of a webpage
    # and return it as a string

    '''
Basic Usage
This page will tell you about Scraping Robot's basic functionality

The Scraping Robot API exposes a single API endpoint. Simply send an http-request to https://api.scrapingrobot.com with your API key, passed as a query-parameter, and get the needed data.

All task-parameters are passed in a POST-body as a JSON-object.

POST Sample Code
https://api.scrapingrobot.com?token=<YOUR_SR_TOKEN>

Sample Code

{
    "url": "https://www.scrapingrobot.com/",
    "module": "HtmlChromeScraper"
}
    '''

    # the url of the scrapingrobot api
    api_url = f"https://api.scrapingrobot.com?token={scraping_api_key}"

    # the parameters for the api call
    params = {
        "url": url,
        "module": "HtmlChromeScraper"
    }

    # make the api call
    response = requests.post(api_url, json=params)

    # check the response
    if response.status_code != 200:
        print(f"Error: {response.status_code} {response.reason}")
        raise Exception(f"Error getting webpage text: {response.status_code} {response.reason}")
    else:
        # result is json
        result = response.json()
        
        if result.get("status") != "SUCCESS":
            print(f"Error: {result.status} {result.message}")
            raise Exception(f"Error getting webpage text: {result.status} {result.message}")
        else:
            return result.get('result')





        # print("Got webpage text. Length:", len(response.text), " characters")
        # print("First 100 characters:", response.text[:100])
        # return response.text

def get_webpage(url):
    # this function uses the requests library to get the text of a webpage

    # make the request
    response = requests.get(url)

    # check the response
    if response.status_code < 200 or response.status_code >= 300:
        print(f"Error: {response.status_code} {response.reason}")
        raise Exception(f"Error getting webpage text: {response.status_code} {response.reason}")
    else:
        # print("Got webpage text. Length:", len(response.text), " characters")
        # print("First 100 characters:", response.text[:100])
        return response.text

def get_text_from_html(html_string):
    # use beautifulsoup to extract all the text from inside the html tags

    # create a soup object from the html
    soup = BeautifulSoup(html_string, 'html.parser')

    # traverse all the tags, and get the text from each one
    text = soup.get_text()

    # remove any extra whitespace
    text = ' '.join(text.split())

    return text

def calc_is_url(url_or_file):
    # return true if the string is a url, false otherwise
    return url_or_file.startswith("http")

def calc_is_html(text):
    # return true if the string is html, false otherwise
    return text.startswith("<!DOCTYPE html>") or text.startswith("<html")

def main():
    # usage: python3 summarize_web_or_text.py <url_or_file> [--outfile <output_filename>] [--prompt_header <promptheader_filename>] [--chunk_size_chars <int>] [--noscrape] [--diagnostics] 

    # first get all the command line arguments
    parser = argparse.ArgumentParser(description='Summarize a web page or a text file.')

    parser.add_argument('url_or_file', type=str, help='The url or file to summarize')
    parser.add_argument('--outfile', type=str, help='The output file to write the summary to')
    parser.add_argument('--prompt_header', type=str, help='The file containing the prompt header')
    parser.add_argument('--chunk_size_chars', type=int, help='The number of characters to use for each chunk, default is 5000')
    parser.add_argument('--noscrape', action='store_true', help='Do not scrape the webpage, just do a GET')
    parser.add_argument('--diagnostics', action='store_true', help='Print diagnostic information')

    args = parser.parse_args()

    url_or_file = args.url_or_file
    outfile = args.outfile
    prompt_header = args.prompt_header
    chunk_size_chars = args.chunk_size_chars or 5000
    noscrape = args.noscrape or not scraping_api_key
    set_diagnostics(args.diagnostics)

    is_url = calc_is_url(url_or_file)

    if not outfile:
        if is_url:
            # clean up the url to add to the output file name
            cleaned_url = url_or_file.replace("http://", "").replace("https://", "").replace("/", "_")
            default_output_file_path_elems = ["working", f"summary_of_{cleaned_url}.txt"]
        else:
            cleaned_filename = os.path.splitext(os.path.basename(url_or_file))[0]
            default_output_file_path_elems = ["working", f"summary_of_{cleaned_filename}.txt"]

        outfile = os.path.join(*default_output_file_path_elems)

    if is_url:
        if noscrape:
            raw_webpage = get_webpage(url_or_file)
        else:
            raw_webpage = get_webpage_via_scraping(scraping_api_key, url_or_file)
        raw_text = get_text_from_html(raw_webpage)
    else:
        # read the file as text, be resilient to unicode errors
        with open(url_or_file, 'r', encoding='utf-8', errors='ignore') as f:
            raw_text = f.read()

        if calc_is_html(raw_text):
            raw_text = get_text_from_html(raw_text)

    print (f"len(raw_text): {len(raw_text)}")

    # Now let's break it into chunks
    # just need to break the string into an array of strings that are chunk_size_chars characters or less
    # don't worry about line or word boundaries
    # have a 100 character overlap between chunks

    chunks = [raw_text[i:i+chunk_size_chars+100] for i in range(0, len(raw_text), chunk_size_chars)]

    # strip all chunks, and remove any that are empty
    chunks = [chunk.strip() for chunk in chunks if len(chunk.strip()) > 0]

    print ("# Chunks: ", len(chunks))

    # for chunk in chunks:
    #     print (f"# Chunk (len={len(chunk)}): {chunk[:100]}")

    result = summarize_text_chunks(chunks, prompt_header)

    with open(outfile, "w") as f:
        f.write(result)

if __name__ == "__main__":
    main()
