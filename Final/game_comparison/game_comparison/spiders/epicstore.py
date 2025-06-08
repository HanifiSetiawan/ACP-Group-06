import scrapy

def get_discount(original_price, final_price):
    if original_price and final_price:
        try:
            original_price_value = float(original_price.strip('$'))
            final_price_value = float(final_price.strip('$'))
            discount = int((original_price_value - final_price_value) / original_price_value * 100)
            return f"{discount}%"
        except ValueError:
            return None
    return None

class EpicstoreSpider(scrapy.Spider):
    name = "epicstore"
    allowed_domains = ["egdata.app"]
    start_urls = ["https://egdata.app/collections/top-sellers"]

    def parse(self, response):
        # Extract game information here
        games = response.css("div.flex.flex-col.gap-2.w-full")
        for game in games.css("a"):
            name = game.css("h3.text-xl.font-light.truncate::text").get()
            link = game.css("::attr(href)").get()
            original_price = game.css("span.text-lg.font-medium.text-muted-foreground.line-through::text").get()
            final_price = game.css("span.text-lg.font-semibold.text-badge::text").get()
            image_url = game.css("div.h-full.w-24.flex-shrink-0.flex.flex-col.justify-center.items-center img::attr(src)").get()
            if not image_url:
                image_url = game.css("div.h-full.w-24.flex-shrink-0.flex.flex-col.justify-center.items-center img::attr(data-src)").get()
            if not final_price:
                final_price = game.css("span.text-lg.font-semibold::text").get()
            yield {
                "name": name.strip() if name else None,
                "link": response.urljoin(link) if link else None,
                "discount": get_discount(original_price, final_price),
                "original_price": original_price.strip() if original_price else None,
                "final_price": final_price.strip() if final_price else None,
                "image_url": image_url.strip() if image_url else None
            }
