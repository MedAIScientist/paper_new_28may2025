#!/usr/bin/env python3
"""
Batch PDF Converter for RAG Implementation
User-friendly script to convert all scraped JSON data to PDF files
"""

import os
import sys
from pathlib import Path
from json_to_pdf_converter import JSONToPDFConverter

def print_banner():
    """Print a nice banner for the script"""
    print("=" * 60)
    print("  JSON to PDF Batch Converter for RAG Implementation")
    print("=" * 60)
    print()

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import reportlab
        return True
    except ImportError:
        print("❌ Missing dependency: ReportLab")
        print("Please install it using: pip install reportlab")
        return False

def find_json_files():
    """Find all JSON files in the current directory"""
    json_files = list(Path('.').glob('*.json'))
    return json_files

def main():
    """Main function for batch conversion"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Find JSON files
    json_files = find_json_files()
    
    if not json_files:
        print("❌ No JSON files found in the current directory.")
        print("Please make sure you have JSON files from web scraping.")
        return
    
    print(f"📁 Found {len(json_files)} JSON file(s):")
    for i, file in enumerate(json_files, 1):
        print(f"   {i}. {file.name}")
    
    print()
    
    # Ask user which file to convert
    if len(json_files) == 1:
        selected_file = json_files[0]
        print(f"🎯 Using: {selected_file.name}")
        selected_files = [selected_file]
    else:
        while True:
            try:
                choice = input(f"Select file to convert (1-{len(json_files)}) or 'all' for all files: ").strip().lower()
                
                if choice == 'all':
                    selected_files = json_files
                    break
                else:
                    choice_num = int(choice)
                    if 1 <= choice_num <= len(json_files):
                        selected_files = [json_files[choice_num - 1]]
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(json_files)}")
            except ValueError:
                print("Please enter a valid number or 'all'")
    
    # Use standard output directory
    output_dir = "converted_pdfs"
    
    # Ask for output directory (optional)
    custom_dir = input(f"\n📂 Output directory (default: {output_dir}): ").strip()
    if custom_dir:
        output_dir = custom_dir
    
    print(f"\n🚀 Starting conversion...")
    print(f"   Format: Clean (relevant content only)")
    print(f"   Output directory: {output_dir}")
    print()
    
    # Process files
    total_successful = 0
    total_failed = 0
    
    for json_file in selected_files:
        print(f"📖 Processing: {json_file.name}")
        print("-" * 40)
        
        # Create converter for this file
        converter = JSONToPDFConverter(str(json_file), output_dir)
        successful, failed = converter.convert_all_articles()
        
        total_successful += successful
        total_failed += failed
        
        print()
    
    # Final summary
    print("=" * 60)
    print("📊 FINAL SUMMARY")
    print("=" * 60)
    print(f"✅ Total successful conversions: {total_successful}")
    print(f"❌ Total failed conversions: {total_failed}")
    print(f"📁 Output directory: {os.path.abspath(output_dir)}")
    
    if total_successful > 0:
        print(f"\n🎉 Success! {total_successful} PDF files are ready for your RAG implementation!")
        print(f"📍 Location: {os.path.abspath(output_dir)}")
        print(f"📋 Format: Clean (relevant content only)")
        
        # Show some example filenames
        output_path = Path(output_dir)
        if output_path.exists():
            pdf_files = list(output_path.glob('*.pdf'))[:3]  # Show first 3 files
            if pdf_files:
                print(f"\n📄 Sample files created:")
                for pdf_file in pdf_files:
                    print(f"   • {pdf_file.name}")
                if len(list(output_path.glob('*.pdf'))) > 3:
                    print(f"   ... and {len(list(output_path.glob('*.pdf'))) - 3} more files")
    else:
        print("\n❌ No files were successfully converted.")
        print("Please check the error messages above for troubleshooting.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main() 