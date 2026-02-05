import os
import asyncio
from playwright.async_api import async_playwright
from supabase import create_client, Client

# Initialize Supabase
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(URL, KEY)

async def run_scraper():
    async with async_playwright() as p:
        print("🚀 Launching Browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Navigate and Select Filters
        print("🌍 Going to NMC website...")
        await page.goto("https://www.nmc.org.in/information-desk/college-and-course-search/", wait_until="networkidle")
        
        # Select 'All PG Courses'
        await page.select_option('select#courseName', label="All PG Courses")
        # Click View Results
        await page.click('input[value="View Results"]')
        await page.wait_for_selector('table#course_table tbody tr', timeout=60000)

        # 2. Optimization: Show 500 entries to reduce page clicks
        print("⚡ Optimizing view to 500 entries...")
        await page.select_option('select[name="course_table_length"]', "500")
        await asyncio.sleep(4) # Allow time for table reload

        page_num = 1
        while True:
            print(f"📄 Scraping Page {page_num}...")
            rows = await page.query_selector_all('table#course_table tbody tr')
            
            for row in rows:
                cols = await row.query_selector_all('td')
                if len(cols) >= 6:
                    # Extract Data
                    course_name = await cols[1].inner_text()
                    state_name = await cols[3].inner_text()
                    college_name = await cols[4].inner_text()
                    mgmt_type = await cols[5].inner_text()

                    # A. Save College (Ignore duplicates)
                    # We use .execute() to get the ID back immediately
                    try:
                        college_res = supabase.table("colleges").upsert({
                            "name": college_name.strip(),
                            "state": state_name.strip(),
                            "management_type": mgmt_type.strip()
                        }, on_conflict="name,state").execute()
                        
                        # B. Save Department linked to that College
                        if college_res.data:
                            c_id = college_res.data[0]['id']
                            supabase.table("departments").upsert({
                                "college_id": c_id,
                                "dept_name": course_name.strip()
                            }, on_conflict="college_id,dept_name").execute()
                    except Exception as e:
                        print(f"⚠️ Error on {college_name}: {e}")

            # 3. Handle 'Next' Button
            next_btn = page.locator('a#course_table_next:not(.disabled)')
            if await next_btn.count() > 0:
                await next_btn.click()
                await asyncio.sleep(3) # Wait for next 500 rows to load
                page_num += 1
            else:
                print("🏁 All pages scraped!")
                break

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
