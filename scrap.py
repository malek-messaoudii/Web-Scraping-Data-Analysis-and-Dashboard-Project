from playwright.sync_api import sync_playwright
import time
import csv
import re
import unicodedata

url = "https://barbechli.tn/search;subcategory=laptops;subcategories=laptops"

# Prepare CSV file (open in append mode to avoid losing progress)
def save_to_csv_single(product, filename="scraped_data.csv"):
    """ Saves a single product's data to a CSV file immediately. """
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "link", "shop", "details"])
        if file.tell() == 0:  # If file is empty, write headers
            writer.writeheader()
        writer.writerow(product)

    print(f"Saved: {product['name']} - {product['price']}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url, timeout=120000)

    page.wait_for_load_state("networkidle")

    # Scroll down multiple times to load all products
    for _ in range(7):
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)

    product_selector = "product-card > a"
    page.wait_for_selector(product_selector, timeout=60000)

    product_links = [
        element.get_attribute("href") for element in page.query_selector_all(product_selector)
    ]
    product_links = [f"https://barbechli.tn/{link}" for link in product_links if link]

    print(f"Found {len(product_links)} products.")

    # Scrape each product page
    for idx, link in enumerate(product_links):
        try:
            product_page = context.new_page()
            for attempt in range(3):
                try:
                    product_page.goto(link, timeout=60000)
                    product_page.wait_for_load_state("networkidle")
                    break
                except Exception:
                    if attempt == 2:
                        raise

            # Extract product details
            name_element = product_page.query_selector(".ba-item-title")
            name = name_element.inner_text().strip() if name_element else "N/A"

            # Inline normalization of the name
            first_word = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('ascii').lower().split()[0] if name != "N/A" else ""

            if first_word == "ecran":  # Compare to normalized "ecran"
                print(f"Product {idx+1}: Skipped due to name starting with 'Ecran' (or variation)")
                continue
            
            price_element = product_page.query_selector(".price-container .current")
            price = price_element.inner_text().strip() if price_element else "N/A"

            img_element = product_page.query_selector("img.item-list-source-logo")
            img_url = img_element.get_attribute("src") if img_element else "N/A"

            shopName = "N/A"
            if img_url and img_url != "N/A":
                match = re.search(r"logo-(.*?)\.jpg", img_url)
                shopName = match.group(1) if match else "N/A"

            details_element = product_page.query_selector("div.row.product-body-text")
            details = details_element.inner_text().strip() if details_element else "N/A"

            print(f"Product {idx+1}: {name} - {price} - {shopName}")

            product = {
                "name": name,
                "price": price,
                "link": link,
                "shop": shopName,
                "details": details
            }

            # Save immediately
            save_to_csv_single(product)

            product_page.close()

        except Exception as e:
            print(f"Product {idx+1}: Could not extract details. Error: {e}")

    browser.close()
