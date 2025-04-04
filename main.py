from fastapi import FastAPI, HTTPException
import logging
from scraper import scrape
from database import get_all_products 


# Initialize FastAPI app
app = FastAPI()

# Set up logging to capture more details
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/scrape")
async def scrape_product():
    try:
        logger.info("Starting scraping process...")
        
        # Call your scraping function here
        await scrape()  # Assuming `scrape()` is the function responsible for scraping
        
        logger.info("Scraping completed successfully.")
        return {"message": "Scraping process completed."}
    
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise HTTPException(status_code=500, detail=str(e))  # Return a detailed error message


@app.get("/products")
def get_products():
    try:
        products = get_all_products()  # Fetch products from DB
        return {"products": products}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
