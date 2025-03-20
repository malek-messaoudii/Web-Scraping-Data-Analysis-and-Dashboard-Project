from playwright.sync_api import sync_playwright
import time
import unicodedata
import re
from storage import save_to_csv_single
from config import URL, CSV_FILENAME
from database import store_product_in_db  # Import the function to store data in DB


def scrape():
    """Scrapes laptop data from the website."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        page.goto(URL, timeout=120000)
        page.wait_for_load_state("networkidle")

        # Scroll to load all products
        for _ in range(7):
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(2)

        # Get product links
        product_selector = "product-card > a"
        page.wait_for_selector(product_selector, timeout=60000)
        product_links = [
            f"https://barbechli.tn/{el.get_attribute('href')}"
            for el in page.query_selector_all(product_selector) if el.get_attribute("href")
        ]

        print(f"Found {len(product_links)} products.")

        # Extract product details
        for idx, link in enumerate(product_links):
            try:
                product_page = context.new_page()
                product_page.goto(link, timeout=60000)
                product_page.wait_for_load_state("networkidle")

                name_element = product_page.query_selector(".ba-item-title")
                name = name_element.inner_text().strip() if name_element else "N/A"

                # Skip unwanted products
                if unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('ascii').lower().startswith("ecran"):
                    print(f"Skipping {idx+1}: {name}")
                    continue

                # Price extraction with additional debugging
                price_element = product_page.query_selector(".price-container .current span:first-child")
                raw_price = price_element.inner_text() if price_element else "N/A"
                # print(f"Raw price: {raw_price}")  # Debugging line
                price = re.sub(r"[^\d.,]", "", raw_price).strip() if raw_price != "N/A" else "N/A"
                # print(f"Formatted price: {price}")  # Debugging line

                img_element = product_page.query_selector("img.item-list-source-logo")
                img_url = img_element.get_attribute("src") if img_element else "N/A"

                # Extract shop name from image URL
                shopName = "N/A"
                if img_url and "logo-" in img_url:
                    match = re.search(r"logo-(.*?)\.jpg", img_url)
                    shopName = match.group(1) if match else "N/A"

                details_element = product_page.query_selector("div.row.product-body-text")
                details = details_element.inner_text().strip() if details_element else "N/A"

                # Extract company link (from 'Acheter' button)
                company_link_element = product_page.query_selector(".item-list-source-external-container a")
                company_link = company_link_element.get_attribute("href") if company_link_element else "N/A"

                product = {"name": name, "price": price, "link": link, "shop": shopName, "details": details,"companyLink": company_link}
                # Store directly in the PostgreSQL database
                store_product_in_db(product)
                # save_to_csv_single(product,idx, CSV_FILENAME)

                product_page.close()
            except Exception as e:
                print(f"Product {idx+1}: Error - {e}")

        browser.close()