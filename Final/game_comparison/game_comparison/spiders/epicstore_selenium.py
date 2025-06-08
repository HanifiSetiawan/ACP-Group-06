from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from parsel import Selector
import time

def get_discount(original_price, final_price):
    try:
        original = float(original_price.strip('$'))
        final = float(final_price.strip('$'))
        return f"{int((original - final) / original * 100)}%"
    except:
        return None

options = Options()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

try:
    driver.get("https://egdata.app/collections/top-sellers")

    # Keep clicking "Show more" until it's gone or max clicks
    for _ in range(20):
        try:
            button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Load more')]"))
            )
            button.click()
            time.sleep(1)  # Let new content load
        except:
            break  # No more "Show more" button

    # Get full page source and parse it
    sel = Selector(text=driver.page_source)

    games = sel.css("div.flex.flex-col.gap-2.w-full > a")
    for game in games:
        name = game.css("h3.text-xl.font-light.truncate::text").get()
        link = game.css("::attr(href)").get()
        original_price = game.css("span.text-lg.font-medium.text-muted-foreground.line-through::text").get()
        final_price = game.css("span.text-lg.font-semibold.text-badge::text").get() or \
                      game.css("span.text-lg.font-semibold::text").get()

        print({
            "name": name.strip() if name else None,
            "link": "https://egdata.app" + link if link else None,
            "discount": get_discount(original_price, final_price),
            "original_price": original_price.strip() if original_price else None,
            "final_price": final_price.strip() if final_price else None
        })

finally:
    driver.quit()
