from fastapi import FastAPI, HTTPException
import logging
from scraper import scrape
from database import get_all_products 
from fastapi.middleware.cors import CORSMiddleware

# Initialize FastAPI app
app = FastAPI()

# Allow Dash frontend (e.g. on port 8050) to call FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # you can restrict it to localhost:8050 if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
