import scrapy

class ExtensionDetailSpider(scrapy.Spider):
    name = "extension_detail"
    
    def start_requests(self):
        urls = [
            "https://chromewebstore.google.com/detail/meeting-assistant-chatgpt/kdkohcmkkplmkknlelglhfhjkegkiljd",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        yield {
            "url": response.url,
            "html": response.text
        }
        # # Extract title
        # title = response.css('title::text').get().strip()
        
        # # Extract description
        # description = response.css('meta[name="description"]::attr(content)').get().strip()
        
        # # Extract user number and star rating
        # stats = response.css('.eTD1t')
        # star_rating = stats.css('.GlMWqe::text').get().strip().split()[0]
        # user_number = stats.css('.Xm7sWb::text').get().strip()
        
        # # Extract images
        # images = response.css('.e1f09::attr(src)').getall()[:5]  # Limit to first 5 images
        
        # yield {
        #     'title': title,
        #     'description': description,
        #     'user_number': user_number,
        #     'star_rating': star_rating,
        #     'images': images,
        # }