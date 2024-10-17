import scrapy
import re
from scrapy_chrome.items import ExtensionItem
import os
import json
import logging
from datetime import datetime
from scrapy_chrome.config.extension_list import load_chrome_extension_list, save_chrome_extension_list, check_duplicate_urls

class ExtensionDetailSpider(scrapy.Spider):
    name = "extension_detail"
    
    def start_requests(self):

        urls = load_chrome_extension_list()
        check_duplicate_urls(urls)
        # Save URLs to a local JSON file
        save_chrome_extension_list(urls)

        # urls = [
        #     "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd",
        # ]

        print("Start scraping: total urls: ", len(urls))
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        user_count_str = response.css('.F9iKBc::text').get()
        rate_count_str = response.css('.xJEoWe::text').get()
        rate_str = response.css('.Vq0ZA::text').get()
        rate = float(rate_str) if rate_str else None

        item = {
            'extension_id': response.url.split('/')[-1],
            'url': response.url,
            'user_count': extract_number_from_str(user_count_str, response.url),
            'name': response.css('h1::text').get().strip(),
            'desc_summary': response.css('.JJ3H1e p:nth-child(1)::text').get(),
            'description': response.css('.JJ3H1e p:nth-child(2)::text').get(),
            'rate': rate,
            'rate_count': extract_number_from_str(rate_count_str, response.url),
        }
        yield item

def extract_number_from_str(str, url):
    if str:
        match = re.search(r'(\d+(?:,\d+)*)', str)
        if match:
            user_count = int(match.group(1).replace(',', ''))
        else:
            logging.warning("No user_count/rate_count found: %s", url)
            user_count = None
    else:
        logging.warning("No user_count/rate_count found: %s", url)
        user_count = None
    return user_count