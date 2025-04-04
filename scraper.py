from playwright.async_api import async_playwright  
import unicodedata
import re
import asyncio
from storage import save_to_csv_single
from config import URL, CSV_FILENAME
from database import store_product_in_db  
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def scrape():
    """Scrapes laptop data from the website asynchronously, handling pagination."""
    async with async_playwright() as p:
        try:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            await page.goto(URL, timeout=120000)
            await page.wait_for_load_state("networkidle")

            page_number = 1
            max_pages = 96  # From your HTML; adjust if needed

            while page_number <= max_pages:
                logger.info(f"Scraping page {page_number}...")

                # Scroll to load all products
                for _ in range(7):
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(2)

                # Get product links
                product_selector = "product-card > a"
                try:
                    await page.wait_for_selector(product_selector, timeout=60000)
                    product_links = [
                        f"https://barbechli.tn/{await el.get_attribute('href')}"
                        for el in await page.query_selector_all(product_selector) 
                        if await el.get_attribute("href")
                    ]
                    logger.info(f"Found {len(product_links)} products on page {page_number}")
                except Exception as e:
                    logger.warning(f"Failed to find products on page {page_number}: {e}")
                    break

                # Stop if no products are found
                if len(product_links) == 0:
                    logger.info("No products found on this page. Stopping.")
                    break

                # Extract product details for this page
                for idx, link in enumerate(product_links):
                    try:
                        product_page = await context.new_page()
                        await product_page.goto(link, timeout=60000)
                        await product_page.wait_for_load_state("networkidle")

                        name_element = await product_page.query_selector(".ba-item-title")
                        name = await name_element.inner_text() if name_element else "N/A"

                        if unicodedata.normalize('NFD', name).encode('ascii', 'ignore').decode('ascii').lower().startswith("ecran"):
                            logger.info(f"Skipping {idx+1} on page {page_number}: {name}")
                            await product_page.close()
                            continue

                        price_element = await product_page.query_selector(".price-container .current span:first-child")
                        raw_price = await price_element.inner_text() if price_element else "N/A"
                        price = re.sub(r"[^\d.,]", "", raw_price).strip() if raw_price != "N/A" else "N/A"

                        img_element = await product_page.query_selector("img.item-list-source-logo")
                        img_url = await img_element.get_attribute("src") if img_element else "N/A"

                        shopName = "N/A"
                        if img_url and "logo-" in img_url:
                            match = re.search(r"logo-(.*?)\.jpg", img_url)
                            shopName = match.group(1) if match else "N/A"

                        details_element = await product_page.query_selector("div.row.product-body-text")
                        details = await details_element.inner_text() if details_element else "N/A"

                        company_link_element = await product_page.query_selector(".item-list-source-external-container a")
                        company_link = await company_link_element.get_attribute("href") if company_link_element else "N/A"

                        product = {
                            "name": name, 
                            "price": price, 
                            "link": link, 
                            "shop": shopName, 
                            "details": details, 
                            "companyLink": company_link
                        }

                        store_product_in_db(product)
                        logger.info(f"Scraped and stored product {idx+1} on page {page_number}: {name}")
                        await product_page.close()
                    except Exception as e:
                        logger.error(f"Error scraping product {idx+1} on page {page_number} at {link}: {e}")

                # Navigate to the next page via URL
                next_page_num = page_number + 1
                if ";pagenumber=" in URL:
                    next_url = re.sub(r";pagenumber=\d+", f";pagenumber={next_page_num}", URL)
                else:
                    next_url = f"{URL};pagenumber={next_page_num}"
                
                logger.info(f"Navigating to: {next_url}")
                try:
                    await page.goto(next_url, timeout=60000)
                    await page.wait_for_load_state("networkidle", timeout=60000)
                    await asyncio.sleep(3)  # Ensure page fully loads
                    page_number += 1
                except Exception as e:
                    logger.warning(f"Navigation to page {next_page_num} failed: {e}. Stopping.")
                    break

            await browser.close()
        except Exception as e:
            logger.error(f"Error during scraping process: {e}")
