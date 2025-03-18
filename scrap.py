from playwright.sync_api import sync_playwright
import time
import csv
import re
import unicodedata
import pandas as pd

url = "https://barbechli.tn/search;subcategory=laptops;subcategories=laptops"
csv_filename = "scraped_data.csv"

# Prepare CSV file
def save_to_csv_single(product, filename=csv_filename):
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "link", "shop", "details"])
        if file.tell() == 0:
            writer.writeheader()
        writer.writerow(product)
    print(f"Saved: {product['name']} - {product['price']}")

# Scraping process
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto(url, timeout=120000)
    page.wait_for_load_state("networkidle")

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

            name_element = product_page.query_selector(".ba-item-title")
            name = name_element.inner_text().strip() if name_element else "N/A"

            first_word = unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('ascii').lower().split()[0] if name != "N/A" else ""
            if first_word == "ecran":
                print(f"Product {idx+1}: Skipped due to name starting with 'Ecran'")
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

            save_to_csv_single(product)
            product_page.close()

        except Exception as e:
            print(f"Product {idx+1}: Could not extract details. Error: {e}")

    browser.close()

# --- Data Cleaning and Transformation ---
df = pd.read_csv(csv_filename)
df_cleaned = df.drop_duplicates()
df_cleaned.to_csv(csv_filename, index=False)
print(f"Cleaned dataset saved as {csv_filename}")

# --- Feature Extraction ---
def extract_characteristics(text):
    characteristics = {
        'Model': None, 'Processor Brand': None, 'Processor': None,
        'RAM': None, 'Storage': None, 'GPU': None, 'Screen': None, 'Color': None, 'OS': None
    }
    
    if pd.isna(text):
        return characteristics


    processor_match = re.search(r'(Intel|AMD|Apple|Celeron|Ryzen|M\d+|Ultra \d+)', text, re.IGNORECASE)
    if processor_match:
        characteristics['Processor Brand'] = processor_match.group(1)

    ram_match = re.search(r'(\d+\s*Go)', text, re.IGNORECASE)
    if ram_match:
        characteristics['RAM'] = ram_match.group(1)

    storage_match = re.search(r'(\d+\s*Go\s*SSD|\d+\s*TB\s*SSD|\d+\s*Go|\d+\s*TB)', text, re.IGNORECASE)
    if storage_match:
        characteristics['Storage'] = storage_match.group(1)

    gpu_match = re.search(r'(RTX\s*\d+|GTX\s*\d+)', text, re.IGNORECASE)
    if gpu_match:
        characteristics['GPU'] = gpu_match.group(1)

    screen_match = re.search(r'(\d+["”]|\d+\s*cm|\d+\s*inch)', text, re.IGNORECASE)
    if screen_match:
        characteristics['Screen'] = screen_match.group(1)

    color_match = re.search(r'(Gris|Silver|Bleu|Noir|Gold|Rose|Rouge|Vert)', text, re.IGNORECASE)
    if color_match:
        characteristics['Color'] = color_match.group(1)

    return characteristics

df_characteristics = df_cleaned.copy()
characteristics_df = df_characteristics['details'].apply(extract_characteristics).apply(pd.Series)

df_final = pd.concat([df_characteristics, characteristics_df], axis=1)
df_final.to_csv(csv_filename, index=False)
print("Processed data saved as scraped_data.csv")
