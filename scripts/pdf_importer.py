import os
import pdfplumber
from supabase import create_client, Client

# 1. Setup Supabase
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(URL, KEY)

def import_pdf_data():
    pdf_path = "data/nmc_data.pdf"
    
    # Validation
    if not os.path.exists(pdf_path):
        print(f"❌ Error: {pdf_path} does not exist. Please upload it.")
        return

    print("📖 Parsing PDF... This may take a few minutes.")
    count_depts = 0

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        print(f"📄 Found {total_pages} pages.")

        for i, page in enumerate(pdf.pages):
            table = page.extract_table()
            
            if not table: continue

            for row in table:
                # Validation: Row must have at least 3 columns [State, College, Course]
                if not row or len(row) < 3: continue
                
                # MAP COLUMNS based on your PDF screenshot
                state_val = row[0]
                college_val = row[1]
                course_val = row[2]

                # Skip Headers and Empty Rows
                if state_val == "STATE" or not college_val or not course_val:
                    continue

                try:
                    # Step 1: Upsert College
                    # We default 'management_type' to 'Unknown' as it's missing in this PDF
                    c_data = {
                        "name": college_val.strip(),
                        "state": state_val.strip(),
                        "management_type": "Unknown" 
                    }
                    
                    # Execute & Return Data to get the ID
                    c_res = supabase.table("colleges").upsert(
                        c_data, on_conflict="name,state"
                    ).execute()
                    
                    # Step 2: Upsert Department (Linked to College ID)
                    if c_res.data:
                        c_id = c_res.data[0]['id']
                        
                        supabase.table("departments").upsert({
                            "college_id": c_id,
                            "dept_name": course_val.strip()
                        }, on_conflict="college_id,dept_name").execute()
                        
                        count_depts += 1

                except Exception as e:
                    print(f"⚠️ Error on Page {i+1}: {e}")

            # Log progress every 10 pages
            if (i + 1) % 10 == 0:
                print(f"   Processed {i + 1}/{total_pages} pages...")

    print(f"✅ SUCCESS! Imported {count_depts} departments.")

if __name__ == "__main__":
    import_pdf_data()
