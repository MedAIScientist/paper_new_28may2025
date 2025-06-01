#!/usr/bin/env python3
"""
Main script that combines link extraction and web scraping.
"""

import os
import argparse
import asyncio
from pdf_link_extractor import extract_links_from_pdf, save_links_to_csv
from web_scraper import process_urls

async def main_async():
    parser = argparse.ArgumentParser(description="PDF Link Extractor and Web Scraper")
    
    # PDF arguments
    parser.add_argument("pdf_path", help="Path to the PDF file containing links")
    
    # CSV output arguments
    parser.add_argument("--csv", default="links.csv", 
                        help="Output path for the CSV file (default: links.csv)")
    
    # JSON output arguments
    parser.add_argument("--json", default="results.json",
                        help="Output path for the JSON file (default: results.json)")
    
    # Additional options
    parser.add_argument("--max-urls", "-m", type=int, default=None,
                        help="Maximum number of URLs to process (default: all)")
    parser.add_argument("--visible", "-v", action="store_true",
                        help="Display the browser during scraping")
    parser.add_argument("--skip-extraction", "-s", action="store_true",
                        help="Skip the link extraction step (use an existing CSV file)")
    
    args = parser.parse_args()
    
    # Step 1: Extract links from PDF
    if not args.skip_extraction:
        print(f"Step 1: Extracting links from {args.pdf_path}")
        links = extract_links_from_pdf(args.pdf_path)
        
        if not links:
            print("No links were found in the PDF. Program stopped.")
            return
        
        save_links_to_csv(links, args.csv)
    else:
        if not os.path.exists(args.csv):
            print(f"The CSV file {args.csv} does not exist. Cannot skip the extraction step.")
            return
        print(f"Step 1: Extraction step skipped, using file {args.csv}")
    
    # Step 2: Web scraping of links
    print(f"Step 2: Web scraping of links from {args.csv}")
    await process_urls(
        args.csv,
        args.json,
        max_urls=args.max_urls,
        headless=not args.visible
    )
    
    print(f"\nProcessing completed!")
    print(f"Links extracted to: {args.csv}")
    print(f"Content retrieved to: {args.json}")

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 