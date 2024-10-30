import pytest
from scrapy_chrome.spiders.utils import extract_image_url, extract_number_from_str

def test_extract_image_url():
    # Test basic URL splitting
    test_url = "https://example.com/image.jpg=s400"
    assert extract_image_url(test_url) == "https://example.com/image.jpg"

    # Test URL without parameters
    test_url = "https://example.com/image.jpg"
    assert extract_image_url(test_url) == "https://example.com/image.jpg"

def test_extract_number_from_str():
    test_url = "https://example.com"
    
    assert extract_number_from_str("1 rating", test_url) == 1

    # Test basic number
    assert extract_number_from_str("169 ratings", test_url) == 169
    
    # Test number with comma
    assert extract_number_from_str("1,234 ratings", test_url) == 1234
    
    # Test K suffix
    assert extract_number_from_str("43.1K ratings", test_url) == 43100
    assert extract_number_from_str("5K ratings", test_url) == 5000
    
    # Test M suffix
    assert extract_number_from_str("1.5M ratings", test_url) == 1500000
    assert extract_number_from_str("2M ratings", test_url) == 2000000
    
    # Test B suffix
    assert extract_number_from_str("1.2B ratings", test_url) == 1200000000
    
    # Test edge cases
    assert extract_number_from_str("", test_url) is None
    assert extract_number_from_str(None, test_url) is None
    assert extract_number_from_str("invalid ratings", test_url) is None
    assert extract_number_from_str("abc123 ratings", test_url) is None

# def test_extract_number_from_str_with_caplog(caplog):
#     test_url = "https://example.com"
    
#     # Test logging for empty string
#     extract_number_from_str("", test_url)
#     assert "No user_count/rate_count found" in caplog.text
#     caplog.clear()
    
#     # Test logging for invalid number
#     extract_number_from_str("invalid ratings", test_url)
#     assert "Failed to parse number" in caplog.text
#     caplog.clear()
    
#     # Test logging for invalid number with suffix
#     extract_number_from_str("abc.1K ratings", test_url)
#     assert "Failed to parse number with suffix" in caplog.text 