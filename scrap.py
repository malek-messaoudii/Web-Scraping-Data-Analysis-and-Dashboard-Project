from playwright.sync_api import sync_playwright
import time
import csv


url = "https://barbechli.tn/search;subcategory=laptops;subcategories=laptops"

# Prepare CSV file for saving
def save_to_csv(products, filename="scraped_data.csv"):
    """ Saves scraped product data to a CSV file. """
    if not products:
        print("No products to save.")
        return

    keys = products[0].keys()
    with open(filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=keys)
        writer.writeheader()
        writer.writerows(products)

    print(f"Data saved to {filename}")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Set to True when done debugging
    page = browser.new_page()
    page.goto(url, timeout=60000)  # Load page with 60s timeout

    # Ensure JavaScript content is fully loaded
    page.wait_for_load_state("networkidle")

    # Scroll down multiple times to load all products
    for _ in range(5):  # Adjust if necessary
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        time.sleep(2)  # Allow time for content to load

    # Wait for product elements to appear
    product_selector = "product-thumbnail"
    page.wait_for_selector(product_selector, timeout=15000)

    # Extract product details
    products = page.query_selector_all(product_selector)
    product_data = []
    
    for idx, product in enumerate(products):
        try:
            name = product.query_selector(".ba-item-title").inner_text().strip()
            price = product.query_selector(".price-container.current").inner_text().strip()
            link = product.query_selector(".card.ba-container").get_attribute("href")

            # Print product details
            print(f"Product {idx+1}:")
            print(f"  Name: {name}")
            print(f"  Price: {price}")
            print(f"  Link: https://barbechli.tn/{link}\n")  # Append base URL

            # Add product details to the list
            product_data.append({
                "name": name,
                "price": price,
                "link": f"https://barbechli.tn/{link}"
            })
        except Exception as e:
            print(f"Product {idx+1}: Could not extract some details. Error: {e}")

    # Save all products to CSV
    save_to_csv(product_data)

    browser.close()
