#!/usr/bin/env python3
"""
Script to extract links from a PDF file and save them to a CSV file.
"""

import os
import csv
import re
import argparse
import fitz  # PyMuPDF

def extract_links_from_pdf(pdf_path):
    """Extracts all links from a PDF file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"The PDF file '{pdf_path}' does not exist.")
    
    links = []
    try:
        # Open the PDF document
        pdf_document = fitz.open(pdf_path)
        
        # Go through each page
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            
            # Extract hypertext links from the page
            page_links = page.get_links()
            for link in page_links:
                if "uri" in link:
                    links.append({
                        "url": link["uri"],
                        "page": page_num + 1,
                        "type": "hyperlink"
                    })
            
            # Extract text from the page to find URLs
            text = page.get_text()
            
            # Search for URLs in the text
            # Pattern to detect URLs with or without @ as prefix
            url_patterns = [
                r'@?(https?://[^\s]+)',  # URLs starting with http:// or https://
                r'@?(www\.[^\s]+)'       # URLs starting with www.
            ]
            
            for pattern in url_patterns:
                for match in re.finditer(pattern, text):
                    url = match.group(1)
                    # Clean the URL (remove punctuation characters at the end)
                    url = url.rstrip('.,;:"\')]}')
                    
                    # Check if it's not already a hypertext link
                    if not any(link['url'] == url for link in links):
                        links.append({
                            "url": url,
                            "page": page_num + 1,
                            "type": "text"
                        })
                    
        pdf_document.close()
        return links
    
    except Exception as e:
        print(f"Error while extracting links: {e}")
        return []

def save_links_to_csv(links, csv_path):
    """Saves the extracted links to a CSV file."""
    try:
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['url', 'page', 'type']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for link in links:
                writer.writerow(link)
                
        print(f"{len(links)} links have been saved to {csv_path}")
        return True
    
    except Exception as e:
        print(f"Error while saving links to CSV: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Link extractor from PDF")
    parser.add_argument("pdf_path", help="Path to the PDF file")
    parser.add_argument("--output", "-o", default="links.csv", 
                        help="Output path for the CSV file (default: links.csv)")
    
    args = parser.parse_args()
    
    # Extract links
    links = extract_links_from_pdf(args.pdf_path)
    
    if links:
        # Save links to a CSV
        save_links_to_csv(links, args.output)
        print(f"Done. {len(links)} links extracted.")
    else:
        print("No links were found in the PDF.")

if __name__ == "__main__":
    main() 


    