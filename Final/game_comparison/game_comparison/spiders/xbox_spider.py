import scrapy

class XboxDealsSpider(scrapy.Spider):
    name = "xbox_deals"
    allowed_domains = ["xbdeals.net"]
    start_urls = ["https://xbdeals.net/us-store/collection/most_wanted/1"]

    def parse(self, response):
        for card in response.css('div.game-collection-item'):
            link = card.css('a.game-collection-item-link::attr(href)').get()
            name = card.css('span.game-collection-item-details-title::text').get()
            discount = card.css('div.game-collection-item-discounts span.game-collection-item-discount-bonus::text').get()
            original_price = card.css('span.game-collection-item-price.strikethrough::text').get()
            final_price = card.css('span[itemprop="price"]::attr(content)').get()
            image_url = card.css('div.game-collection-item-image-placeholder img::attr(src)').get()
            if not image_url:
                image_url = card.css('div.game-collection-item-image-placeholder img::attr(data-src)').get()
            if not final_price:
                # fallback: sometimes price is visible
                final_price = card.css('span.game-collection-item-price::text').get()
            yield {
                "name": name.strip() if name else None,
                "discount": discount.strip() if discount else None,
                "original_price": original_price.strip() if original_price else None,
                "final_price": final_price.strip() if final_price else None,
                "url": response.urljoin(link) if link else None,
                "image_url": image_url.strip() if image_url else None
            }

        # Pagination: follow next page if exists
        next_page = response.css('ul.pagination li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)