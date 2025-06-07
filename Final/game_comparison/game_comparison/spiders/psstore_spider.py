import scrapy

class PSStoreSpider(scrapy.Spider):
    name = "psstore"
    allowed_domains = ["psdeals.net"]
    start_urls = [
        "https://psdeals.net/us-store/collection/most_wanted/1"
    ]

    # def start_requests(self):
    #     for url in self.start_urls:
    #         yield scrapy.Request(
    #             url=url,
    #             callback=self.parse,
    #             # headers={
    #             #     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    #             # }
    #         )

    def parse(self, response):
        # Extract game information here
        for game in response.css("div.game-collection-item.col-md-2.col-sm-4.col-xs-6"):
            name = game.css("span.game-collection-item-details-title::text").get()
            link = game.css("a.game-collection-item-link::attr(href)").get()
            discount = game.css("span.game-collection-item-discount::text").get()
            original_price = game.css("span.game-collection-item-price strikethrough::text").get()
            final_price = game.css("span.game-collection-item-price-discount::text").get()
            image_url = game.css('div.game-collection-item-image-placeholder img::attr(src)').get()
            if not image_url:
                image_url = game.css('div.game-collection-item-image-placeholder img::attr(data-src)').get()
            if not final_price:
                final_price = game.css("span.game-collection-item-price ::text").get()
            yield {
                "name": name.strip(),
                "link": link.strip(),
                "discount": discount.strip() if discount else None,
                "original_price": original_price.strip() if original_price else None,
                "final_price": final_price.strip(),
                "image_url": image_url.strip() if image_url else None,
            }
        
        #pagination: follow next page if exists
        next_page = response.css("ul.pagination li.next a::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)