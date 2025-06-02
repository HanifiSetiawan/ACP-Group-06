import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

class XboxSpider(scrapy.Spider):
    name = "xbox"
    allowed_domains = ["xbox.com"]
    start_urls = [
        "https://www.xbox.com/en-US/games/browse"
    ]

    def start_requests(self):
        options = Options()
        # options.add_argument("--headless")  # Uncomment to run headless
        driver = webdriver.Chrome(options=options)
        driver.get(self.start_urls[0])
        time.sleep(5)  # Wait for JS to load content

        # Optionally, click "Load more" a few times:
        for _ in range(3):
            try:
                load_more = driver.find_element(By.CSS_SELECTOR, 'button[data-automation-id="loadMoreButton"]')
                load_more.click()
                time.sleep(3)
            except Exception:
                break

        html = driver.page_source

        with open("xbox_debug.html", "w", encoding="utf-8") as f:
            f.write(html)

        driver.quit()
        yield scrapy.http.HtmlResponse(url=self.start_urls[0], body=html, encoding='utf-8')

    def parse(self, response):
        for card in response.css('div.ProductCard-module__cardWrapper___6Ls86'):
            a = card.css('a[aria-label][href*="/games/store/"]')
            name = a.css('span.ProductCard-module__title___nHGIp::text').get()
            original_price = card.css('span.Price-module__originalPrice___XNCxs::text').get()
            final_price = card.css('span.Price-module__boldText___1i2Li::text').get()
            discount = card.css('div.ProductCard-module__discountTag___OjGFy::text').get()
            url = a.attrib.get('href')
            if name and final_price:
                yield {
                    "name": name.strip(),
                    "discount": discount.strip() if discount else None,
                    "original_price": original_price.strip() if original_price else None,
                    "final_price": final_price.strip(),
                    "url": response.urljoin(url) if url else None,
                }