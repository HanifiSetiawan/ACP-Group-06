import scrapy
from scrapy_playwright.page import PageMethod

class SteamPlaywrightSpider(scrapy.Spider):
    name = "steam_playwright"
    allowed_domains = ["store.steampowered.com"]
    start_urls = ["https://store.steampowered.com/search/?filter=topsellers"]

    def start_requests(self):
        url = "https://store.steampowered.com/search/?filter=topsellers"
        yield scrapy.Request(
            url,
            meta={
                "playwright": True,
                "playwright_page_methods": [
                    PageMethod("evaluate", """
                        let scrolls = 9;
                        async function scrollDown(i) {
                            if (i < scrolls) {
                                window.scrollTo(0, document.body.scrollHeight);
                                await new Promise(r => setTimeout(r, 1500));
                                await scrollDown(i+1);
                            }
                        }
                        scrollDown(0);
                    """)
                ]
            }
        )

    def parse(self, response):
        for row in response.css('a.search_result_row'):
            name = row.css('span.title::text').get()
            discount = row.css('div.discount_pct::text').get()
            original_price = row.css('div.discount_original_price::text').get()
            final_price = row.css('div.discount_final_price::text').get()
            image_url = row.css('div.search_capsule img::attr(src)').get()
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
                    'image_url': image_url.strip() if image_url else None
                }