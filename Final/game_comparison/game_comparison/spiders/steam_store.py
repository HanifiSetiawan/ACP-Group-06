import scrapy


class SteamStoreSpider(scrapy.Spider):
    name = "steam_store"
    allowed_domains = ["steampricehistory.com"]
    start_urls = [f"https://steampricehistory.com/popular?page={i}" for i in range(1, 11)]

    custom_settings = {
    'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'ROBOTSTXT_OBEY': False,
    }

    def parse(self, response):
        for row in response.css('table.app-table tbody tr'):
            # skip header row (it has <th> not <td>)
            if row.css('th'):
                continue
            name = row.css('a.app-link::text').get()
            price = row.css('td:nth-child(3)::text').get()
            # image is in the first <td> as <img>, but not all rows have it
            image_url = row.css('td:nth-child(1) img::attr(src)').get()
            if name and price:
                yield {
                    'name': name.strip(),
                    'price': price.strip(),
                    'image_url': image_url.strip() if image_url else None
                }