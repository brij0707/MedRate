import pdfplumber
import os

def debug_pdf():
    pdf_path = "data/nmc_data.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found at {pdf_path}")
        return

    print("🔍 DIAGNOSTIC MODE: Analyzing Page 1...")

    with pdfplumber.open(pdf_path) as pdf:
        # Check if pages exist
        if not pdf.pages:
            print("❌ Error: PDF has 0 pages.")
            return

        page = pdf.pages[0]
        
        # Try extracting table with default settings
        table = page.extract_table()

        if not table:
            print("⚠️ No table found on Page 1. Trying text extraction...")
            text = page.extract_text()
            print("--- RAW TEXT START ---")
            print(text[:500])  # Print first 500 chars
            print("--- RAW TEXT END ---")
            return

        print(f"✅ Table found! Rows detected: {len(table)}")
        print("--- PRINTING FIRST 5 ROWS ---")
        
        for i, row in enumerate(table[:5]):
            print(f"Row {i}: {row}")
            
    print("--- END DIAGNOSTIC ---")

if __name__ == "__main__":
    debug_pdf()
