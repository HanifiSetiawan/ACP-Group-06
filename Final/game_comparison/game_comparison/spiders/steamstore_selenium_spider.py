import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class SteamStoreSeleniumSpider(scrapy.Spider):
    name = "steamstore_selenium"
    allowed_domains = ["store.steampowered.com"]
    start_urls = [
        "https://store.steampowered.com/search/?filter=topsellers"
    ]

    def start_requests(self):
        options = Options()
        # options.add_argument("--headless")
        options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        driver = webdriver.Chrome(options=options)
        driver.get(self.start_urls[0])

        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "a.search_result_row"))
        )

        last_count = 0
        for _ in range(5):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            games = driver.find_elements(By.CSS_SELECTOR, "a.search_result_row")
            if len(games) > last_count:
                last_count = len(games)
            else:
                break

        html = driver.page_source
        with open("steam_debug.html", "w", encoding="utf-8") as f:
            f.write(html)
        driver.quit()
        yield scrapy.http.HtmlResponse(url=self.start_urls[0], body=html, encoding='utf-8')

    def parse(self, response):
        count = 0
        for row in response.css('a.search_result_row'):
            name = row.css('span.title::text').get()
            # Try to get discount info
            discount = row.css('div.discount_pct::text').get()
            original_price = row.css('div.discount_original_price::text').get()
            final_price = row.css('div.discount_final_price::text').get()
            # If not discounted, get price from search_price
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
                }
        count += 1
        # Removed 'break' as it is not valid outside a loop


       