"""
run.py
-------

This script is used to launch the scraper. It loads configuration from environment variables,
initializes a Scraper object, and invokes the scraping process.

Environment Variables:
PROXY       - Proxy address to use for scraping
INPUT_URL   - URL of the page to scrape
OUTPUT_FILE - File path where the scraping results will be written to

Modules:
os          - Module for interacting with the operating system
dotenv      - Module for loading environment variables from a .env file
scraper     - Module with the Scraper class definition
"""

import os
from dotenv import load_dotenv
from scraper import Scraper

env_vars = ['PROXY', 'INPUT_URL', 'OUTPUT_FILE']

def main():
    """
    Main function that loads configuration, initializes a Scraper object, 
    and invokes the scraping process.
    """
    load_dotenv()
    config = {var: os.getenv(var) for var in env_vars}

    if None in config.values():
        missing_vars = [var for var, value in config.items() if value is None]
        print(f"Missing environment variables: {', '.join(missing_vars)}")
        return

    scraper = Scraper(
        input_url=config['INPUT_URL'], 
        output_file=config['OUTPUT_FILE'],  
        #proxy_url=config['PROXY']
    )
    scraper.scrape()  

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An error occurred: {e}")
