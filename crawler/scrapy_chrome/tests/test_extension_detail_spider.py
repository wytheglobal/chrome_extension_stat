import pytest
from scrapy.http import HtmlResponse, Request
from scrapy.utils.test import get_crawler
from scrapy_chrome.spiders.extension_detail_spider import ExtensionDetailSpider
from urllib.request import urlopen

@pytest.fixture
def spider():
    return ExtensionDetailSpider()

@pytest.fixture
def crawler():
    return get_crawler(ExtensionDetailSpider)

def test_parse_method(spider):
    # Create a mock response with more realistic HTML content
    url = "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd"
    with urlopen(url) as response:
        html_content = response.read()

    request = Request(url=url)
    response = HtmlResponse(url=url, request=request, body=html_content)

    # Call the parse method
    parsed_data = next(spider.parse(response))
    print(parsed_data)

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


    # Uncomment these tests when the spider is updated to extract more information
    # assert 'title' in item
    # assert 'description' in item
    # assert 'user_number' in item
    # assert 'star_rating' in item
    # assert 'images' in item

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