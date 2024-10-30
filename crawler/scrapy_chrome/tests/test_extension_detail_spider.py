import pytest
from scrapy.http import HtmlResponse, Request
from scrapy.utils.test import get_crawler
from scrapy_chrome.spiders.extension_detail_spider import ExtensionDetailSpider
from urllib import request as urlrequest
import json


@pytest.fixture
def spider():
    return ExtensionDetailSpider()

@pytest.fixture
def crawler():
    return get_crawler(ExtensionDetailSpider)


def send_request(url):
    proxy_handler = urlrequest.ProxyHandler({
        'http': 'http://127.0.0.1:7890',
        'https': 'http://127.0.0.1:7890',
    })
    opener = urlrequest.build_opener(proxy_handler)
    return opener.open(url)

def get_parsed_response(spider, url):
    resp = send_request(url)
    html_content = resp.read()
    response = HtmlResponse(url=url, body=html_content)
    return next(spider.parse(response))


def test_parse_method(spider):



    # Create a mock response with more realistic HTML content
    url = "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd"

    # resp = send_request(url)
    # html_content = resp.read()


    # response = HtmlResponse(url=url, body=html_content)

    # Call the parse method
    parsed_data = get_parsed_response(spider, url)
    print(json.dumps(parsed_data, indent=4))

    # Assert that we get one item
    # Assert that we get one item
    assert isinstance(parsed_data, dict)
    
    # Assert that user_count is present and is a number
    assert 'user_count' in parsed_data
    
    # user_count is a string like "10,000+"
    assert isinstance(parsed_data['user_count'], (int, float))    
    assert parsed_data['url'] == 'https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd'
    assert parsed_data['name'] == 'Meeting Assistant & ChatGPT summary, by Noty.ai'

    assert parsed_data['desc_summary'] != ''

    assert parsed_data['description'] != ''
    assert parsed_data['logo'] == 'https://lh3.googleusercontent.com/R_Kdyo_CGzUCzg74WpVDCKkF1E0lQCLaTT0q9LITFpCGHuU5FVqsDSD7rauyD3CjkbYtcZp3cMKoddhqY08AjRczqw'
    assert parsed_data['category'] == 'communication'



def test_parse_method_2(spider):
    url = "https://chromewebstore.google.com/detail/take-webpage-screenshots/mcbpblocgmgfnpjjppndjkmgjaogfceg"
    parsed_data = get_parsed_response(spider, url)
    assert isinstance(parsed_data['rate_count'], (int))    
    assert parsed_data['category'] == 'tools'


def test_item_not_available(spider):
    url = "https://chromewebstore.google.com/detail/linkedin-demetricator/edcbdhndiniiafhoaoljbmhbmchadhmg"
    parsed_data = get_parsed_response(spider, url)
    # assert parsed_data['name'] == "This item is not available"
    print(json.dumps(parsed_data, indent=4))


    # assert item['title'] == "Meeting Assistant - ChatGPT"
    # assert item['description'] == "AI-powered meeting assistant for better productivity"
    # assert item['user_number'] == "10,000+ users"
    # assert item['star_rating'] == "4.8"
    # assert len(item['images']) == 5
    # assert item['images'][0] == "image1.jpg"

# def test_start_requests(spider):
#     # Get the requests from start_requests
#     requests = list(spider.start_requests())

#     # Assert that we get one request
#     assert len(requests) == 1

#     # Check the URL of the request
#     assert requests[0].url == "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd"

#     print(requests)