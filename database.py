import psycopg2
from config import DB_CONFIG
from extractor import extract_characteristics,process_single_product  # Function to process details
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_duplicate(company_link):
    """Check if a product with the same companyLink already exists in the database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = "SELECT id FROM products WHERE company_path = %s"
        cursor.execute(query, (company_link,))
        result = cursor.fetchone()  # Fetch one result
        
        cursor.close()
        conn.close()

        # If result is None, no duplicate exists
        return result is not None

    except Exception as e:
        print(f"Database Error (checking duplicate): {e}")
        return False

def store_product_in_db(product):
    """Store a product entry in the PostgreSQL database if it's not a duplicate."""
    try:
        # Check if the product already exists based on the companyLink
        if check_duplicate(product["companyLink"]):
            logger.info(f"Product already exists in DB: {product['name']}")
            return  # Skip saving this product

        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Extract characteristics from details
        characteristics = process_single_product(product["details"])

        query = """
        INSERT INTO products (
            id, company_path, description, price, price_2, currency, discount_percentage, company, type, model,
            processor_brand, processor, ram, gpu, screen, color, os, storage
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        
        values = (
            product["link"],
            product["companyLink"],
            product["details"],
            product["price"],  # Extract numeric price
            None,  # price_2 (Optional, can be added later)
            "DT",  # Assume currency is TND
            None,  # discount_percentage (Optional)
            product["shop"],
            characteristics.get("type", "N/A"),
            characteristics.get("model", "N/A"),
            characteristics.get("processor brand", "N/A"),
            characteristics.get("processor", "N/A"),
            characteristics.get("ram", "N/A"),
            characteristics.get("gpu", "N/A"),
            characteristics.get("screen", "N/A"),
            characteristics.get("color", "N/A"),
            characteristics.get("os", "N/A"),
            characteristics.get("storage", "N/A")
        )

        cursor.execute(query, values)
        conn.commit()

        logger.info(f"Stored in DB: {product['name']}")

        cursor.close()
        conn.close()
    except Exception as e:
        logger.error(f"Database Error: {e}")

# Add this to database.py

def get_all_products():
    """Fetch all products from the database."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        query = """
        SELECT 
            id, company_path, description, price, company, type, model, 
            processor_brand, processor, ram, gpu, screen, color, os, storage
        FROM products
        """
        cursor.execute(query)
        products = cursor.fetchall()

        # Convert tuples to dictionaries for JSON serialization
        product_list = []
        for product in products:
            product_dict = {
                "id": product[0],
                "company_link": product[1],
                "description": product[2],
                "price": product[3],
                "shop": product[4],
                "type": product[5],
                "model": product[6],
                "processor_brand": product[7],
                "processor": product[8],
                "ram": product[9],
                "gpu": product[10],
                "screen": product[11],
                "color": product[12],
                "os": product[13],
                "storage": product[14]
            }
            product_list.append(product_dict)

        cursor.close()
        conn.close()
        return product_list

    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise