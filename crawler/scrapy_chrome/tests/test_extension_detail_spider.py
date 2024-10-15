import unittest
from scrapy.http import HtmlResponse, Request
from scrapy.utils.test import get_crawler
from scrapy.contracts import ContractsManager
from scrapy.contracts.default import ReturnsContract
from scrapy_chrome.spiders.extension_detail_spider import ExtensionDetailSpider

class TestExtensionDetailSpider(unittest.TestCase):
    def setUp(self):
        self.spider = ExtensionDetailSpider()
        self.crawler = get_crawler(ExtensionDetailSpider)
        self.contract_manager = ContractsManager(load_contracts=True)

    def test_parse_method(self):
        # Create a mock response
        url = "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd"
        request = Request(url=url)
        response = HtmlResponse(url=url, request=request, body=b'<html><body>Test HTML</body></html>')

        # Call the parse method
        results = list(self.spider.parse(response))

        # Assert that we get one item
        self.assertEqual(len(results), 1)

        # Check the structure of the returned item
        item = results[0]
        self.assertIn('url', item)
        self.assertIn('html', item)

        # Check the values
        self.assertEqual(item['url'], url)
        self.assertEqual(item['html'], '<html><body>Test HTML</body></html>')

    def test_start_requests(self):
        # Get the requests from start_requests
        requests = list(self.spider.start_requests())

        # Assert that we get one request
        self.assertEqual(len(requests), 1)

        # Check the URL of the request
        self.assertEqual(requests[0].url, "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd")

if __name__ == '__main__':
    unittest.main()
