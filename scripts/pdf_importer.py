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
    count_depts = 0

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            print(f"Processing Page {i+1}...")
            table = page.extract_table()
            
            if not table: continue

            for row in table:
                # Ensure row has at least 3 columns (State, College, Course)
                if not row or len(row) < 3: continue
                
                # Map columns based on your PDF
                state_val = row[0]
                college_val = row[1]
                course_val = row[2]

                # Skip header row ('STATE') or empty data
                if state_val == "STATE" or not college_val:
                    continue

                try:
                    # 1. Upsert College (State + College Name)
                    # We default 'management_type' to 'Unknown' since it's not in this PDF
                    c_res = supabase.table("colleges").upsert({
                        "name": college_val.strip(),
                        "state": state_val.strip(),
                        "management_type": "Unknown" 
                    }, on_conflict="name,state").execute()
                    
                    # 2. Upsert Department (Course Name) linked to the College
                    if c_res.data:
                        c_id = c_res.data[0]['id']
                        supabase.table("departments").upsert({
                            "college_id": c_id,
                            "dept_name": course_val.strip()
                        }, on_conflict="college_id,dept_name").execute()
                        count_depts += 1

                except Exception as e:
                    print(f"⚠️ Row Error: {e}")

    print(f"✅ SUCCESS! Imported {count_depts} courses.")

if __name__ == "__main__":
    import_pdf_data()
