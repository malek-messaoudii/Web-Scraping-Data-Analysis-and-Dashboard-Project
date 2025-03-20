import psycopg2
from config import DB_CONFIG
from extractor import extract_characteristics, extract_price,process_single_product  # Function to process details

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
            print(f"Product already exists in DB: {product['name']}")
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

        print(f"Stored in DB: {product['name']}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database Error: {e}")
