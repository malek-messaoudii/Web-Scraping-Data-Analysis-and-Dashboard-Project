import csv
import pandas as pd

def save_to_csv_single(product, idx, filename):
    """Append a product entry to a CSV file."""
    with open(filename, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["name", "price", "link", "shop", "details","companyLink"])
        if file.tell() == 0:  # Write headers if file is empty
            writer.writeheader()
        writer.writerow(product)
    print(f"Saved {idx+1}: {product['name']} - {product['price']}")

def clean_csv(filename):
    """Remove duplicate rows from CSV."""
    df = pd.read_csv(filename)
    df_cleaned = df.drop_duplicates()
    df_cleaned.to_csv(filename, index=False)
    print(f"Cleaned dataset saved as {filename}")
