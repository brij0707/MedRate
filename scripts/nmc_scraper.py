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
        context = await browser.new_context(user_agent="Mozilla/5.0")
        page = await context.new_page()
        
        print("🚀 Navigating to NMC...")
        await page.goto("https://www.nmc.org.in/information-desk/college-and-course-search/", wait_until="networkidle")

        # 1. Select 'All PG Courses' from dropdown
        await page.select_option('select#courseName', label="All PG Courses")
        
        # 2. Click 'View Results'
        await page.click('input[value="View Results"]')
        await page.wait_for_selector('table#course_table tr', timeout=60000)

        # 3. Set 'Show 500 entries' to speed up
        await page.select_option('select[name="course_table_length"]', "500")
        await asyncio.sleep(2) # Give it a second to reload the 500 rows

        has_next = True
        page_num = 1

        while has_next:
            print(f"📄 Scraping Page {page_num}...")
            rows = await page.query_selector_all('table#course_table tbody tr')
            
            college_data = []
            for row in rows:
                cols = await row.query_selector_all('td')
                if len(cols) > 5:
                    name = await cols[4].inner_text() # 'Name and Address' column
                    state = await cols[3].inner_text() # 'Select a State' column
                    college_data.append({
                        "name": name.strip(),
                        "state": state.strip()
                    })

            # Batch Upsert to Supabase
            if college_data:
                supabase.table("colleges").upsert(college_data, on_conflict="name,state").execute()
            
            # 4. Check for 'Next' button
            next_btn = page.locator('a#course_table_next:not(.disabled)')
            if await next_btn.count() > 0:
                await next_btn.click()
                await asyncio.sleep(2) # Wait for table refresh
                page_num += 1
            else:
                has_next = False
                print("🏁 All pages scraped successfully.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
