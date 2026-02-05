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
        browser = await p.chromium.launch(headless=True)
        # Use a real user-agent to stay undetected
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
        page = await context.new_page()
        
        print("🚀 Navigating to NMC Portal...")
        await page.goto("https://www.nmc.org.in/information-desk/college-and-course-search/", wait_until="networkidle")

        # 1. Select 'All PG Courses'
        # We target the ID courseName from the dropdown
        await page.select_option('select#courseName', label="All PG Courses")
        
        # 2. Click 'View Results'
        await page.click('input[value="View Results"]')
        await page.wait_for_selector('table#course_table tbody tr', timeout=60000)

        # 3. Optimize: Set 'Show 500 entries' to reduce page turns
        await page.select_option('select[name="course_table_length"]', "500")
        await asyncio.sleep(3) # Wait for table to reload with 500 rows

        page_num = 1
        while True:
            print(f"📄 Scraping Page {page_num}...")
            rows = await page.query_selector_all('table#course_table tbody tr')
            
            batch_data = []
            for row in rows:
                cols = await row.query_selector_all('td')
                if len(cols) >= 6:
                    # Column 5 contains 'Name and Address of Medical College'
                    name_raw = await cols[4].inner_text()
                    # Column 4 contains 'Select a State'
                    state_raw = await cols[3].inner_text()
                    
                    batch_data.append({
                        "name": name_raw.strip(),
                        "state": state_raw.strip()
                    })

            # 4. Upsert to Supabase
            if batch_data:
                supabase.table("colleges").upsert(batch_data, on_conflict="name,state").execute()
            
            # 5. Handle Pagination
            # Check if the 'Next' button exists and is not disabled
            next_btn = page.locator('a#course_table_next:not(.disabled)')
            if await next_btn.count() > 0:
                await next_btn.click()
                await asyncio.sleep(2) # Wait for page load
                page_num += 1
            else:
                print("🏁 Finished! All pages processed.")
                break

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
