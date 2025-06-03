import scrapy
from scrapy_selenium import SeleniumRequest

class SteamStoreSeleniumSpider(scrapy.Spider):
    name = "steamstore_selenium"
    allowed_domains = ["store.steampowered.com"]
    start_urls = [
        "https://store.steampowered.com/search/?filter=topsellers"
    ]

    def start_requests(self):
        yield SeleniumRequest(
            url=self.start_urls[0],
            wait_time=5,
            callback=self.parse,
            script="""
                let scrolls = 15;
                function scrollDown(i) {
                    if (i < scrolls) {
                        window.scrollTo(0, document.body.scrollHeight);
                        setTimeout(() => scrollDown(i+1), 1500);
                    }
                }
                scrollDown(0);
            """
    )

    def parse(self, response):
        for row in response.css('a.search_result_row'):
            name = row.css('span.title::text').get()
            discount = row.css('div.discount_pct::text').get()
            original_price = row.css('div.discount_original_price::text').get()
            final_price = row.css('div.discount_final_price::text').get()
            if not final_price:
                final_price = row.css('div.search_price::text').get()
                if final_price:
                    final_price = final_price.strip()
            if name and final_price:
                yield {
                    "name": name.strip(),
                    "discount": discount.strip() if discount else None,
                    "original_price": original_price.strip() if original_price else None,
                    "final_price": final_price.strip(),
                }