#!/usr/bin/env python3
"""
JSON to PDF Converter for RAG Implementation
Converts scraped article data from JSON format to PDFs with copyable text
"""

import json
import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from urllib.parse import urlparse
import re

class JSONToPDFConverter:
    """Converts JSON scraped data to PDF files with copyable text"""
    
    def __init__(self, json_file_path, output_directory="converted_pdfs"):
        """
        Initialize the converter
        
        Args:
            json_file_path (str): Path to the JSON file containing scraped data
            output_directory (str): Directory to save the generated PDF files
        """
        self.json_file_path = json_file_path
        self.output_directory = output_directory
        self.create_output_directory()
        self.setup_styles()
    
    def create_output_directory(self):
        """Create output directory if it doesn't exist"""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
            print(f"Created output directory: {self.output_directory}")
    
    def setup_styles(self):
        """Setup PDF styles for different text elements"""
        self.styles = getSampleStyleSheet()
        
        # Title style
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Title'],
            fontSize=16,
            spaceAfter=20,
            alignment=TA_CENTER,
            textColor='black'
        )
        
        # Author/URL style
        self.meta_style = ParagraphStyle(
            'MetaInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=10,
            alignment=TA_CENTER,
            textColor='blue'
        )
        
        # Abstract/Summary style
        self.abstract_style = ParagraphStyle(
            'Abstract',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=15,
            alignment=TA_JUSTIFY,
            leftIndent=20,
            rightIndent=20,
            textColor='black'
        )
        
        # Body text style
        self.body_style = ParagraphStyle(
            'BodyText',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceAfter=12,
            alignment=TA_JUSTIFY,
            textColor='black',
            leading=14
        )
        
        # Section header style
        self.section_style = ParagraphStyle(
            'SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            spaceAfter=10,
            spaceBefore=15,
            textColor='black'
        )
    
    def clean_text(self, text):
        """
        Clean and prepare text for PDF generation
        
        Args:
            text (str): Raw text to clean
            
        Returns:
            str: Cleaned text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Handle common HTML entities that might remain
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&quot;', '"')
        text = text.replace('&#39;', "'")
        
        # Remove any remaining HTML-like tags
        text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    def extract_domain_from_url(self, url):
        """Extract domain name from URL for filename"""
        try:
            domain = urlparse(url).netloc
            # Remove www. if present
            domain = re.sub(r'^www\.', '', domain)
            # Replace dots with underscores for filename
            domain = domain.replace('.', '_')
            return domain
        except:
            return "unknown_source"
    
    def create_filename(self, article_data, index):
        """
        Create a meaningful filename for the PDF
        
        Args:
            article_data (dict): Article data
            index (int): Index of the article
            
        Returns:
            str: Generated filename
        """
        # Extract domain
        domain = self.extract_domain_from_url(article_data.get('url', ''))
        
        # Clean title for filename
        title = article_data.get('title', f'article_{index}')
        title = re.sub(r'[^\w\s-]', '', title)  # Remove special characters
        title = re.sub(r'\s+', '_', title)  # Replace spaces with underscores
        title = title[:50]  # Limit length
        
        # Create filename
        filename = f"{index:03d}_{domain}_{title}.pdf"
        return filename
    
    def extract_abstract_from_content(self, content):
        """
        Try to extract abstract/summary from content
        
        Args:
            content (dict): Content dictionary
            
        Returns:
            str: Extracted abstract or first paragraph
        """
        full_text = content.get('full_text', '')
        paragraphs = content.get('paragraphs', [])
        
        # Look for abstract in full text
        abstract_match = re.search(r'(?i)abstract[:\s]+(.*?)(?=\n\n|\. [A-Z]|$)', full_text)
        if abstract_match:
            return self.clean_text(abstract_match.group(1))
        
        # Look for background/objective
        background_match = re.search(r'(?i)(?:background|objective)[:\s]+(.*?)(?=\n\n|\. [A-Z]|$)', full_text)
        if background_match:
            return self.clean_text(background_match.group(1))
        
        # Use first substantial paragraph
        for para in paragraphs:
            clean_para = self.clean_text(para)
            if len(clean_para) > 100 and not clean_para.lower().startswith('the .gov means'):
                return clean_para
        
        return ""
    
    def convert_article_to_pdf(self, article_data, filename):
        """
        Convert a single article to PDF
        
        Args:
            article_data (dict): Article data from JSON
            filename (str): Output filename
        """
        output_path = os.path.join(self.output_directory, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        content = []
        
        # Title
        title = self.clean_text(article_data.get('title', 'No Title'))
        content.append(Paragraph(title, self.title_style))
        content.append(Spacer(1, 12))
        
        # URL and metadata
        url = article_data.get('url', '')
        domain = article_data.get('domain', '')
        date_scraped = article_data.get('date_scraped', '')
        
        if url:
            content.append(Paragraph(f"Source: {url}", self.meta_style))
        if domain:
            content.append(Paragraph(f"Domain: {domain}", self.meta_style))
        if date_scraped:
            content.append(Paragraph(f"Scraped: {date_scraped}", self.meta_style))
        
        content.append(Spacer(1, 20))
        
        # Get article content
        article_content = article_data.get('content', {})
        
        # Add Abstract section if available
        abstract = article_content.get('abstract', '')
        if abstract:
            content.append(Paragraph("ABSTRACT", self.section_style))
            content.append(Paragraph(self.clean_text(abstract), self.abstract_style))
            content.append(Spacer(1, 15))
        
        # Add Conflict of Interest section if available
        conflict_of_interest = article_content.get('conflict_of_interest', '')
        if conflict_of_interest:
            content.append(Paragraph("CONFLICT OF INTEREST", self.section_style))
            content.append(Paragraph(self.clean_text(conflict_of_interest), self.body_style))
            content.append(Spacer(1, 15))
        
        # Use paragraphs if available, otherwise use full text
        paragraphs = article_content.get('paragraphs', [])
        full_text = article_content.get('full_text', '')
        
        if paragraphs:
            # Filter out very short or repetitive paragraphs but keep relevant content
            filtered_paragraphs = []
            seen_paragraphs = set()
            
            for para in paragraphs:
                clean_para = self.clean_text(para)
                # Less aggressive filtering - keep important content
                if (len(clean_para) > 50 and 
                    clean_para not in seen_paragraphs and
                    not clean_para.lower().startswith('the .gov means') and
                    not clean_para.lower().startswith('the pubmed wordmark') and
                    'clipboard' not in clean_para.lower() and
                    'citation' not in clean_para.lower() and
                    'bibliography' not in clean_para.lower()):
                    filtered_paragraphs.append(clean_para)
                    seen_paragraphs.add(clean_para)
            
            # Add paragraphs to content
            for para in filtered_paragraphs:
                content.append(Paragraph(para, self.body_style))
                content.append(Spacer(1, 12))
        
        elif full_text:
            # Split full text into reasonable chunks, keeping important sections
            clean_text = self.clean_text(full_text)
            
            # Split by sentences or double spaces
            chunks = re.split(r'(?<=[.!?])\s+|\n\n+', clean_text)
            
            current_paragraph = ""
            for chunk in chunks:
                # Skip very short chunks or metadata
                if len(chunk.strip()) < 30:
                    continue
                    
                if len(current_paragraph + chunk) < 500:
                    current_paragraph += chunk + " "
                else:
                    if current_paragraph.strip():
                        content.append(Paragraph(current_paragraph.strip(), self.body_style))
                        content.append(Spacer(1, 12))
                    current_paragraph = chunk + " "
            
            # Add the last paragraph
            if current_paragraph.strip():
                content.append(Paragraph(current_paragraph.strip(), self.body_style))
        
        # Add footer
        content.append(Spacer(1, 30))
        content.append(Paragraph("---", self.meta_style))
        content.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.meta_style))
        
        # Build PDF
        try:
            doc.build(content)
            print(f"✓ Created: {filename}")
            return True
        except Exception as e:
            print(f"✗ Error creating {filename}: {str(e)}")
            return False
    
    def convert_all_articles(self):
        """Convert all articles from JSON to PDF files"""
        try:
            # Load JSON data
            with open(self.json_file_path, 'r', encoding='utf-8') as file:
                articles = json.load(file)
            
            print(f"Found {len(articles)} articles to convert")
            
            successful_conversions = 0
            failed_conversions = 0
            
            # Convert each article
            for index, article in enumerate(articles, 1):
                filename = self.create_filename(article, index)
                
                if self.convert_article_to_pdf(article, filename):
                    successful_conversions += 1
                else:
                    failed_conversions += 1
            
            # Print summary
            print(f"\n=== Conversion Summary ===")
            print(f"Total articles: {len(articles)}")
            print(f"Successfully converted: {successful_conversions}")
            print(f"Failed conversions: {failed_conversions}")
            print(f"Output directory: {os.path.abspath(self.output_directory)}")
            
            return successful_conversions, failed_conversions
            
        except FileNotFoundError:
            print(f"Error: JSON file not found: {self.json_file_path}")
            return 0, 0
        except json.JSONDecodeError:
            print(f"Error: Invalid JSON format in file: {self.json_file_path}")
            return 0, 0
        except Exception as e:
            print(f"Error: {str(e)}")
            return 0, 0

def main():
    """Main function to run the converter"""
    print("JSON to PDF Converter for RAG Implementation")
    print("=" * 50)
    
    # Configuration
    json_file = "results.json"
    output_dir = "converted_pdfs"
    
    # Check if JSON file exists
    if not os.path.exists(json_file):
        print(f"Error: JSON file '{json_file}' not found in current directory.")
        print("Please make sure the results.json file is in the same directory as this script.")
        return
    
    # Create converter and run conversion
    converter = JSONToPDFConverter(json_file, output_dir)
    successful, failed = converter.convert_all_articles()
    
    if successful > 0:
        print(f"\n✓ Successfully converted {successful} articles to PDF format!")
        print(f"📁 PDFs saved in: {os.path.abspath(output_dir)}")
        print("\nThese PDFs are now ready for use in your RAG implementation.")
    else:
        print("\n✗ No articles were successfully converted.")

if __name__ == "__main__":
    main() 