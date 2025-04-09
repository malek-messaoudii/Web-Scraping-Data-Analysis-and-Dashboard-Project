from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# ====================== Configuration ======================
app = FastAPI(
    title="Scrapping annonces API")

# ====================== Database Configuration ======================
DB_CONFIG = {
    "dbname": "Barbechli",
    "user": "postgres",
    "password": "7y4bH5Cs",
    "host": "localhost",
    "port": "5432"
}

# ====================== Models ======================
class ProductBase(BaseModel):
    company_path: str
    description: str
    price: float

class ProductCreate(ProductBase):
    price_2: Optional[float] = None
    currency: Optional[str] = None
    discount_percentage: Optional[float] = None
    company: Optional[str] = None
    type: Optional[str] = None
    model: Optional[str] = None
    processor_brand: Optional[str] = None
    processor: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    gpu: Optional[str] = None
    screen: Optional[str] = None
    color: Optional[str] = None
    os: Optional[str] = None

class Product(ProductCreate):
    id: str

# ====================== Database Utilities ======================
def get_db_connection():
    """Establish and return a database connection with RealDictCursor"""
    return psycopg2.connect(
        cursor_factory=RealDictCursor,
        **DB_CONFIG
    )

# ====================== CRUD Operations ======================
@app.get("/products", response_model=List[Product], summary="Get all products")
def get_all_products():
    """
    Retrieve a list of all products from the database.
    
    Returns:
        List[Product]: A list of product objects
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM products;")
            return cursor.fetchall()
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}"
        )
    finally:
        if conn:
            conn.close()

@app.post(
    "/products",
    response_model=Product,
    status_code=201,
    summary="Create a new product",
    response_description="The created product"
)
def create_product(product: ProductCreate):
    """
    Create a new product in the database.
    
    Args:
        product (ProductCreate): Product data to be created
        
    Returns:
        Product: The newly created product with its ID
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Generate a new UUID for the product
            cursor.execute("SELECT gen_random_uuid() as id;")
            product_id = cursor.fetchone()['id']
            
            insert_query = """
                INSERT INTO products (
                    id, company_path, description, price, price_2, currency,
                    discount_percentage, company, type, model, processor_brand,
                    processor, ram, storage, gpu, screen, color, os
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING *;
            """
            
            cursor.execute(insert_query, (
                product_id,
                product.company_path,
                product.description,
                product.price,
                product.price_2,
                product.currency,
                product.discount_percentage,
                product.company,
                product.type,
                product.model,
                product.processor_brand,
                product.processor,
                product.ram,
                product.storage,
                product.gpu,
                product.screen,
                product.color,
                product.os
            ))
            
            new_product = cursor.fetchone()
            conn.commit()
            return new_product
            
    except Exception as e:
        conn.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create product: {str(e)}"
        )
    finally:
        if conn:
            conn.close()

# ====================== Main Execution ======================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)