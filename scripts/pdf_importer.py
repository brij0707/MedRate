import os
import pdfplumber
from supabase import create_client, Client

# Initialize Supabase
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(URL, KEY)

def import_pdf_data():
    pdf_path = "data/nmc_data.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ Error: File not found at {pdf_path}")
        return

    print("📖 Opening PDF...")
    
    count_colleges = 0
    count_depts = 0

    with pdfplumber.open(pdf_path) as pdf:
        # Loop through every page in the PDF
        for i, page in enumerate(pdf.pages):
            print(f"📄 Processing Page {i+1}...")
            
            # Extract the table from the page
            table = page.extract_table()
            
            if not table:
                continue

            for row in table:
                # Filter out empty rows or headers
                # Based on your image: Col 0=State, Col 1=College, Col 2=Course
                if len(row) > 2 and row[0] != "STATE" and row[0] is not None:
                    
                    state_val = row[0]
                    college_val = row[1]
                    course_val = row[2] # This is the Department

                    # Skip if data is empty (sometimes happens with bad formatting)
                    if not college_val or not course_val:
                        continue

                    try:
                        # 1. Upsert College
                        # Since PDF doesn't have "Type", we default to "Unknown" for now
                        college_res = supabase.table("colleges").upsert({
                            "name": college_val.strip(),
                            "state": state_val.strip(),
                            "management_type": "Unknown" 
                        }, on_conflict="name,state").execute()
                        
                        if college_res.data:
                            # 2. Upsert Department
                            c_id = college_res.data[0]['id']
                            supabase.table("departments").upsert({
                                "college_id": c_id,
                                "dept_name": course_val.strip()
                            }, on_conflict="college_id,dept_name").execute()
                            
                            count_depts += 1

                    except Exception as e:
                        print(f"⚠️ Error on row: {row} -> {e}")

    print(f"✅ DONE! Imported {count_depts} departments from PDF.")

if __name__ == "__main__":
    import_pdf_data()
