import scrapy

def get_discount(original_price, final_price):
    try:
        original = float(original_price.strip('$'))
        final = float(final_price.strip('$'))
        return f"{int((original - final) / original * 100)}%"
    except:
        return None

class EpicStoreSpider(scrapy.Spider):
    name = "epic_store"
    allowed_domains = ["store.epicgames.com"]
    start_urls = ["https://store.epicgames.com/en-US/collection/top-sellers"]

    def parse(self, response):
        # Always save the HTML for debugging
        with open('epic_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        self.logger.info(f"Response status: {response.status}")
        self.logger.info(f"Response length: {len(response.text)}")
        self.logger.info(f"First 500 chars: {response.text[:500]}")

        if not response.text or len(response.text) < 1000:
            yield {"error": "Empty or very short response", "status": response.status}
            return

        found = False
        for game in response.css('div[data-component="DiscoverOfferCard"]'):
            found = True
            # Get the name
            name = game.css('div.css-rgqwpc::text').get()
            # Get the image
            image_url = game.css('img[data-testid="picture-image"]::attr(src)').get()
            # Get the link
            link = game.css('a::attr(href)').get()
            # Get the prices
            original_price = game.css('span.css-4jky3p::text').get()
            final_price = game.css('span.css-12s1vua::text').get()
            # Get the discount
            discount = game.css('span.eds_1xxntt819::text').get()
            yield {
                "name": name.strip() if name else None,
                "image_url": image_url.strip() if image_url else None,
                "link": response.urljoin(link) if link else None,
                "original_price": original_price.strip() if original_price else None,
                "final_price": final_price.strip() if final_price else None,
                "discount": discount.strip() if discount else None
            }
        if not found:
            yield {"error": "No game cards found with selector", "status": response.status}