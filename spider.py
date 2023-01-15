import argparse
import scrapy
from scrapy.crawler import CrawlerProcess

import bs4

class MySpider(scrapy.Spider):
    name = 'myspider'
    start_urls = None
    match_text = None
    levels = None
    found_urls = []

    def __init__(self, start_url, match_text, levels, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url]
        self.match_text = match_text
        self.levels = levels

    def start_requests(self):
        if self.levels > 0:
            for url in self.start_urls:
                def construct_callback(level):
                    def callback(response):
                        return self.parse(response, level)
                    return callback
                yield scrapy.Request(url, callback=construct_callback(self.levels-1))

    def add_url(self, url):
        if url not in self.found_urls:
            self.found_urls.append(url)

    def parse(self, response, level):
        if level <= 0:
            return

        #1: use bs4 to get all links
        soup = bs4.BeautifulSoup(response.body, 'html.parser')

        just_found_urls = []

        for link in soup.find_all('a'):
            url = link.get('href')

            if not url:
                continue

            scheme = url.split(':')[0] if ':' in url else None

            is_relative = scheme is None

            if scheme in ['http', 'https']:
                pass
            elif is_relative:
                url = response.urljoin(url)
            else:
                continue

            link_text = link.text

            if url and not url in self.found_urls and self.match_text.lower() in link_text.lower():
                self.add_url(url)
                just_found_urls.append(url)

        #2: use scrapy to visit all links
        for url in just_found_urls:
            print (f'visiting {url}')
            def construct_callback(level):
                def callback(response):
                    return self.parse(response, level)
                return callback
            yield scrapy.Request(url, callback=construct_callback(level-1))

def main():
    # usage: python spider.py <url> <match_text> [--levels <levels>]
    # spider visits all pages in the domain of the given url, and outputs a list of all urls found,
    # where the text of the link contains the given match_text
    # levels is optional, and specifies how many levels deep to spider. Default is 2.

    # parse command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument('url', help='url to start spidering from')
    parser.add_argument('match_text', help='text to match in links')
    parser.add_argument('--levels', help='how many levels deep to spider', default=2, type=int)

    args = parser.parse_args()

    url = args.url
    match_text = args.match_text
    levels = args.levels

    # start spider
    process = CrawlerProcess()
    process.crawl(MySpider, url, match_text, levels)

    process.start()

    # output urls
    for url in MySpider.found_urls:
        print(url)
    
if __name__ == '__main__':
    main()
