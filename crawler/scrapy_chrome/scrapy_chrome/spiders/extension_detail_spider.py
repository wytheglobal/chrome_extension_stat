import scrapy
import re
from scrapy_chrome.items import ExtensionItem
import os
import json
import logging
from datetime import datetime
from scrapy_chrome.config.extension_list import load_chrome_extension_list, save_chrome_extension_list

class ExtensionDetailSpider(scrapy.Spider):
    name = "extension_detail"
    
    def start_requests(self):

        urls = load_chrome_extension_list()
        # Save URLs to a local JSON file
        save_chrome_extension_list(urls)

        unique_urls = set(urls)
        print(f"Total URLs: {len(urls)}")
        print(f"Unique URLs: {len(unique_urls)}")
        print(f"Duplicate URLs: {len(urls) - len(unique_urls)}")
        if len(urls) != len(unique_urls):
            print("Duplicates found!")
            for url in unique_urls:
                if urls.count(url) > 1:
                    print(f"Duplicate URL: {url}")
        else:
            print("No duplicates found.")
        exit(1)

        config_file_path = os.path.join(os.path.dirname(__file__), '../../../', 'extension_list/data/2024-10-15/productivity_communication_15-26-14.json')
        with open(config_file_path, 'r') as file:
            config_data = json.load(file)
        
        urls = [f"https://chromewebstore.google.com{item['detailUrl']}" for item in config_data['items']]
        # urls = [
        #     "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd",
        # ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        user_count_str = response.css('.F9iKBc::text').get()

        item = {
            'extension_id': response.url.split('/')[-1],
            'url': response.url,
            'user_count': extract_user_count(user_count_str),
            'name': response.css('h1::text').get().strip(),
            'desc_summary': response.css('.JJ3H1e p:nth-child(1)::text').get(),
            'description': response.css('.JJ3H1e p:nth-child(2)::text').get(),
        }
        yield item

def extract_user_count(user_count_str):
    if user_count_str:
        match = re.search(r'(\d+(?:,\d+)*)', user_count_str)
        if match:
            user_count = int(match.group(1).replace(',', ''))
        else:
            logging.warning("[user_count] No user count found: %s", response.url)
            user_count = None
    else:
        logging.warning("[user_count] No user count found: %s", response.url)
        user_count = None