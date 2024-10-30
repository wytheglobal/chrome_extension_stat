import scrapy
import re
from scrapy_chrome.items import ExtensionItem
import os
import json
import logging
from datetime import datetime
from scrapy_chrome.config.extension_list import load_chrome_extension_list, save_chrome_extension_list, check_duplicate_urls
from scrapy_chrome.spiders.utils import extract_image_url, extract_number_from_str

urls = load_chrome_extension_list()


class ExtensionDetailSpider(scrapy.Spider):
    name = "extension_detail"
    
    def start_requests(self):

        # Save URLs to a local JSON file
        # save_chrome_extension_list(urls)

        # urls = [
        #     "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd",
        # ]

        print("Start scraping: total urls: ", len(urls))
        
        for id in urls:
            config = urls[id]
            yield scrapy.Request(url=config['url'], callback=self.parse)

    def parse(self, response):
        print("start parsing: ", response.url)
        extension_id = response.url.split('/')[-1]
        user_count_str = response.css('.F9iKBc::text').get()
        rate_count_str = response.css('.xJEoWe::text').get()
        rate_str = response.css('.Vq0ZA::text').get()
        rate = float(rate_str) if rate_str else None

        # Convert version_updated date string to datetime object
        version_updated_str = response.css('.uBIrad div:nth-child(2)::text').get()
        try:
            version_updated_date = datetime.strptime(version_updated_str, '%B %d, %Y').isoformat() if version_updated_str else None
        except ValueError:
            version_updated_date = None
            logging.warning(f"Failed to parse version_updated date: {version_updated_str} for {response.url}")

        item = {
            'item_id': extension_id,
            'url': response.url,
            'logo': extract_image_url(response.css('.rBxtY::attr(src)').get()),
            'user_count': extract_number_from_str(user_count_str, response.url),
            'name': response.css('h1::text').get().strip(),
            'desc_summary': response.css('.JJ3H1e p:nth-child(1)::text').get(),
            'description': response.css('.JJ3H1e p:nth-child(2)::text').get(),
            'rate': rate,
            'rate_count': extract_number_from_str(rate_count_str, response.url),
            'category': urls[extension_id]['category'],
            'version': response.css('.N3EXSc::text').get(),
            'version_size': response.css('.ZSMSLb div:nth-child(2)::text').get(),
            'version_updated': version_updated_date
        }
        yield item

