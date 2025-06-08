import scrapy
from scrapy_playwright.page import PageMethod

def get_discount(original_price, final_price):
    try:
        original = float(original_price.strip('$'))
        final = float(final_price.strip('$'))
        return f"{int((original - final) / original * 100)}%"
    except:
        return None

class EpicPlaywrightSpider(scrapy.Spider):
    name = "epic_playwright"
    allowed_domains = ["store.epicgames.com"]
    start_urls = ["https://store.epicgames.com/en-US/collection/top-sellers"]

    def start_requests(self):
        yield scrapy.Request(
            self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,  # Keep the page open for debugging
                "playwright_page_methods": [
                    PageMethod("wait_for_selector", "button", {"timeout": 20000}),
                    # Give user 30 seconds to manually click cookie consent
                    PageMethod("evaluate", """
                        await new Promise(r => setTimeout(r, 30000));
                    """),
                    PageMethod("wait_for_selector", "div.border.bg-card.shadow.w-full.h-16.flex.flex-row.items-center.rounded-xl.overflow-hidden.px-5", {"timeout": 20000}),
                ]
            },
            callback=self.parse
        )

    def parse(self, response):
        # Save the HTML for debugging if needed
        with open('epic_debug.html', 'w', encoding='utf-8') as f:
            f.write(response.text)

        for game in response.css("div.border.bg-card.shadow.w-full.h-16.flex.flex-row.items-center.rounded-xl.overflow-hidden.px-5"):
            # Get the name
            name = game.css("h3.text-xl.font-light.truncate::text").get()
            # Get the image
            image_url = game.css('picture img::attr(src)').get()
            if not image_url:
                image_url = game.css('picture img::attr(data-src)').get()
            # Get the link
            link = game.css('a::attr(href)').get()
            # Get the prices
            original_price = game.css("span.text-lg.font-medium.text-muted-foreground.line-through::text").get()
            final_price = game.css("span.text-lg.font-semibold.text-badge::text").get() or \
                          game.css("span.text-lg.font-semibold::text").get()
            # Calculate discount
            discount = get_discount(original_price, final_price)
            yield {
                "name": name.strip() if name else None,
                "image_url": image_url.strip() if image_url else None,
                "link": response.urljoin(link) if link else None,
                "original_price": original_price.strip() if original_price else None,
                "final_price": final_price.strip() if final_price else None,
                "discount": discount
            }



            