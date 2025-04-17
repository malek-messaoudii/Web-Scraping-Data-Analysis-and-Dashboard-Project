# Web Scraping, Data Analysis and Dashboard Project

## Project Overview

This project involves scraping computer listings from Barbéchlì (early 2025), storing the data in PostgreSQL, creating REST APIs to access the data, and building interactive dashboards for data visualization.

## Branches

Malek: Contains the dashboard implementation using Dash, Plotly, and Pandas

MalekRestApis: Contains REST API implementations (GET/POST) and data updating logic (Data scrapped from Instant Data Scraper)

Ahmed: Complete pipeline integration 

## Technologies Used

Web Scraping: Playwright (Python), Google Instant Data Scraper

Database: PostgreSQL

Backend: Python REST APIs (FastAPI)

Visualization: Dash, Plotly, Pandas, Kibana

Version Control: Git

## Installation

1. Clone the repository :
   
   git clone https://github.com/malek-messaoudii/Web-Scraping-Data-Analysis-and-Dashboard-Project.git
   
   cd Web-Scraping-Data-Analysis-and-Dashboard-Project
   
2. Install dependencies :
   
   pip install -r requirements.txt
   
## Usage

1. Start the API server :
   
   python -m uvicorn main:app --reload
   
2. Launch the dashboard :
   
   cd dashboard
   
   python app.py

## API Endpoints

GET /products: Retrieve all scraped computer data

POST /scrape: Initiate a new scraping session



## Dashboard Features

Interactive price distribution charts

Brand comparison visualizations

Time-series analysis of price trends

Filtering capabilities

## Team

Malek

Ahmed
