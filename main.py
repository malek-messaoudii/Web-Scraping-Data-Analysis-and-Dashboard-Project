from scraper import scrape
from storage import clean_csv
from extractor import process_extracted_data
from config import CSV_FILENAME

if __name__ == "__main__":
    print("Starting scraping process...")
    scrape()
    
    # print("Cleaning CSV data...")
    # clean_csv(CSV_FILENAME)
    
    # print("Extracting characteristics...")
    # process_extracted_data(CSV_FILENAME)

    print("Scraping and processing completed.")
