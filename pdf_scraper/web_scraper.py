#!/usr/bin/env python3
"""
Script to visit links extracted from PDF and retrieve content from web pages.
"""

import os
import csv
import json
import argparse
import asyncio
from datetime import datetime
from urllib.parse import urlparse
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

class WebScraper:
    def __init__(self, headless=False, timeout=60000):
        self.headless = headless
        self.timeout = timeout
        self.browser = None
        self.context = None
        
    async def init(self):
        """Initialize the Playwright browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(headless=self.headless)
        self.context = await self.browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        
    async def close(self):
        """Close the browser"""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
    
    async def visit_url(self, url):
        """Visit a URL and extract specific content sections"""
        try:
            # Create a new page
            page = await self.context.new_page()
            
            # Navigate to the URL with timeout
            await page.goto(url, wait_until="domcontentloaded", timeout=self.timeout)
            
            # Wait for the page to load
            await page.wait_for_load_state("networkidle", timeout=self.timeout)
            
            # Extract HTML content
            html_content = await page.content()
            
            # Extract page title
            title = await page.title()
            
            # Parse HTML content with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Close the page
            await page.close()
            
            # Extract specific sections
            abstract_content = None
            conflict_content = None
            
            # Extract abstract section
            abstract_div = soup.find('div', {'class': 'abstract', 'id': 'abstract'})
            if abstract_div:
                abstract_content = abstract_div.get_text(separator=" ", strip=True)
            
            # Extract conflict of interest section
            conflict_div = soup.find('div', {'class': 'conflict-of-interest', 'id': 'conflict-of-interest'})
            if conflict_div:
                conflict_content = conflict_div.get_text(separator=" ", strip=True)
            
            # Create results dictionary
            result = {
                "url": url,
                "title": title,
                "domain": urlparse(url).netloc,
                "date_scraped": datetime.now().isoformat(),
                "content": {
                    "abstract": abstract_content,
                    "conflict_of_interest": conflict_content
                },
                "sections_found": {
                    "abstract": abstract_content is not None,
                    "conflict_of_interest": conflict_content is not None
                }
            }
            
            return result
            
        except Exception as e:
            print(f"Error while visiting {url}: {e}")
            return {
                "url": url,
                "error": str(e),
                "date_scraped": datetime.now().isoformat()
            }

async def process_urls(csv_path, output_json, max_urls=None, headless=False):
    """Process URLs from the CSV file and save results to a JSON file"""
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"The CSV file '{csv_path}' does not exist.")
    
    # Read URLs from CSV file
    urls = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if 'url' in row:
                urls.append(row['url'])
    
    # Limit the number of URLs to process if specified
    if max_urls and max_urls > 0:
        urls = urls[:max_urls]
    
    print(f"Processing {len(urls)} URLs...")
    
    # Initialize the scraper
    scraper = WebScraper(headless=headless)
    await scraper.init()
    
    # Process each URL
    results = []
    for i, url in enumerate(urls):
        print(f"[{i+1}/{len(urls)}] Processing {url}")
        result = await scraper.visit_url(url)
        results.append(result)
    
    # Close the scraper
    await scraper.close()
    
    # Save results to a JSON file
    with open(output_json, 'w', encoding='utf-8') as jsonfile:
        json.dump(results, jsonfile, ensure_ascii=False, indent=2)
    
    print(f"Done. {len(results)} results saved to {output_json}")

def main():
    parser = argparse.ArgumentParser(description="Web Scraper for links extracted from PDF")
    parser.add_argument("csv_path", help="Path to the CSV file containing links")
    parser.add_argument("--output", "-o", default="results.json", 
                        help="Output path for the JSON file (default: results.json)")
    parser.add_argument("--max-urls", "-m", type=int, default=None,
                        help="Maximum number of URLs to process (default: all)")
    parser.add_argument("--visible", "-v", action="store_true",
                        help="Display the browser during scraping")
    
    args = parser.parse_args()
    
    # Execute the scraper
    asyncio.run(process_urls(
        args.csv_path, 
        args.output, 
        max_urls=args.max_urls,
        headless=not args.visible
    ))

if __name__ == "__main__":
    main() 