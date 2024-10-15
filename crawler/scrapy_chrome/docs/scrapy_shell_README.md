# Scrapy Chrome Extension Crawler

This project uses Scrapy to crawl and extract data from the Chrome Web Store.

## Using Scrapy Shell

Scrapy shell is an interactive shell that allows you to test your selectors and explore the response of a web page without running the entire spider. It's a great tool for debugging and development.

### Starting the Scrapy Shell

1. Open a terminal and navigate to the project directory.
2. Run the following command:

   ```
   https_proxy=$var_http_proxy https_proxy=$var_http_proxy scrapy shell "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd"
   ```

   This will fetch the page and open an interactive Python shell.

### Basic Usage

Once in the Scrapy shell, you have access to several objects:

- `response`: The response object for the fetched page.
- `request`: The request object used to fetch the page.
- `spider`: A default spider object.

### Common Commands

1. Inspect the response:
   ```python
   response.url
   response.status
   response.headers
   ```

2. Use CSS selectors:
   ```python
   response.css('title::text').get()
   response.css('meta[name="description"]::attr(content)').get()
   ```

3. Use XPath selectors:
   ```python
   response.xpath('//h1/text()').get()
   ```

4. Combine selectors:
   ```python
   response.css('div.product-info').xpath('./h1/text()').get()
   ```

5. Extract all matching elements:
   ```python
   response.css('img::attr(src)').getall()
   ```

### Tips

- Use `view(response)` to open the response in your web browser.
- Use `shelp()` to see all available objects and methods in the shell.
- Use `fetch(url)` to fetch a new URL without leaving the shell.

### Exiting the Shell

To exit the Scrapy shell, simply type `exit()` or press Ctrl+D.

## Running the Spider

To run the extension detail spider:
