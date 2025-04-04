import re
import pandas as pd

# Precompiled regex patterns
PATTERNS = {
    'Type': re.compile(r'(PC Portable|Écran Gaming|Portable|Moniteur|Laptop|Notebook|MacBook)', re.IGNORECASE),
    'Model': re.compile(r'\b(HP|Dell|Lenovo|Asus|Acer|MSI|Apple)\s*[-\w\s]+', re.IGNORECASE),  # Extract model name
    'Processor Brand': re.compile(r'\b(Intel|AMD|Apple)\b', re.IGNORECASE),  # Extract processor brand
    'Processor': re.compile(r'\b(Intel|AMD|Apple)\s+(Core\s(Ultra\s)?\w+|\w+|Ryzen\s\d+\s?\d*[A-Za-z]*|M\d+|Celeron|Pentium)(?:\s[-\w]+)?\b', re.IGNORECASE),
    'RAM': re.compile(r'(\d+\s*Go)(?=\s*(?:RAM|))', re.IGNORECASE),  # Avoids storage confusion and removes "RAM"  # Avoids storage confusion
    'Storage': re.compile(r'(\d+\s*(Go|GB|TB)\s*(SSD|HDD|NVMe|PCIe|M\.2|eMMC))', re.IGNORECASE),  # Extract storage
    'GPU': re.compile(r'(RTX\s*\d+\s*\w*|GTX\s*\d+\s*\w*|Intel Iris Xᵉ|Intel UHD Graphics|Radeon\s*\w+|NVIDIA GeForce MX\d+)\s*(\d+\s*Go)?', re.IGNORECASE),
    'Screen': re.compile(r'(\d{2}(\.\d+)?\s*(\"|inch|cm|Full HD|FHD|QHD|4K))', re.IGNORECASE),
    'Color': re.compile(r'(Gris|Silver|Bleu|Noir|Gold|Rose|Rouge|Vert)', re.IGNORECASE),
    'OS': re.compile(r'(Windows\s*\d+\s*(Pro|Home|Enterprise)?)|macOS|Linux|Ubuntu|FreeDOS|ChromeOS', re.IGNORECASE)
}

def extract_characteristics(text):
    """Extract structured product characteristics from text."""
    characteristics = {key.lower(): None for key in PATTERNS}  # Use lowercase keys

    if not isinstance(text, str) or not text.strip():
        return characteristics  # Return empty values if text is None or empty

    for key, pattern in PATTERNS.items():
        match = pattern.search(text)
        if match:
            characteristics[key.lower()] = match.group(0).strip()
        else:
            print(f"Pattern not matched for {key}: {text}")  # Debugging line

    # Default to "PC Portable" if Type is missing
    if not characteristics['type']:
        characteristics['type'] = "PC Portable"

    return characteristics

def process_single_product(product_details):
    """Extract characteristics for a single product and return the processed data."""
    # Extract characteristics using the extractor function
    product_characteristics = extract_characteristics(product_details)
    
    # Optionally, convert it into a pandas DataFrame if you plan to save it
    # processed_df = pd.DataFrame([product_characteristics])

    # # Save the processed data to a CSV (if needed)
    # processed_df.to_csv('processed_product_data.csv', mode='a', header=False, index=False)  # Append to existing CSV if needed
    # print("Processed single product data saved.")
    
    return product_characteristics  # Optionally, return the processed data

def process_extracted_data(filename):
    """Reads a CSV file, extracts product characteristics, and saves the cleaned data."""
    df = pd.read_csv(filename).fillna('')  # Avoid NaN issues
    characteristics_df = df['details'].apply(extract_characteristics).apply(pd.Series)
    df_final = pd.concat([df, characteristics_df], axis=1)
    
    df_final.to_csv(filename, index=False)
    print(f"Processed data saved as {filename}")
