import scrapy


class SteamWebSpider(scrapy.Spider):
    name = "steam_web"
    allowed_domains = ["gg.deals"]
    start_urls = ["https://gg.deals/deals/steam-deals/"]

    def parse(self, response):
        pass
