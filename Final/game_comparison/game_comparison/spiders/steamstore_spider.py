import scrapy

class SteamStoreSpider(scrapy.Spider):
    name = "steamstore"
    allowed_domains = ["store.steampowered.com"]
    start_urls = [
        "https://store.steampowered.com/search/?filter=topsellers"
    ]

    def parse(self, response):
        for row in response.css('a.search_result_row'):
            name = row.css('span.title::text').get()
            discount = row.css('div.discount_pct::text').get()
            original_price = row.css('div.discount_original_price::text').get()
            final_price = row.css('div.discount_final_price::text').get()

            if name and final_price:
                yield {
                    "name": name.strip(),
                    "discount": discount.strip() if discount else None,
                    "original_price": original_price.strip() if original_price else None,
                    "final_price": final_price.strip(),
                }