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
        print("🚀 Launching Headless Browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # 1. Navigate
        print("🌍 Going to NMC website...")
        # Increased timeout to 60s for slow connections
        await page.goto("https://www.nmc.org.in/information-desk/college-and-course-search/", timeout=60000)
        
        # 2. THE CRITICAL FIX: Wait for the dropdown to actually exist
        print("⏳ Waiting for search form...")
        await page.wait_for_selector('select#courseName', state="visible", timeout=60000)

        # 3. Now it is safe to select
        print("✅ Selecting 'All PG Courses'...")
        await page.select_option('select#courseName', label="All PG Courses")
        
        # 4. Click View Results
        await page.click('input[value="View Results"]')
        
        # 5. Wait for the TABLE to appear (Wait for results)
        print("⏳ Waiting for results table...")
        await page.wait_for_selector('table#course_table tbody tr', timeout=60000)

        # 6. Optimize View to 500 entries
        print("⚡ Optimizing view to 500 entries...")
        await page.select_option('select[name="course_table_length"]', "500")
        await asyncio.sleep(5) # Give it time to reload the big table

        page_num = 1
        while True:
            print(f"📄 Scraping Page {page_num}...")
            # Re-query the rows every loop to avoid 'stale element' errors
            rows = await page.query_selector_all('table#course_table tbody tr')
            
            for row in rows:
                cols = await row.query_selector_all('td')
                if len(cols) >= 6:
                    course = await cols[1].inner_text()
                    state = await cols[3].inner_text()
                    college = await cols[4].inner_text()
                    mgmt = await cols[5].inner_text()

                    # Upsert College
                    try:
                        res = supabase.table("colleges").upsert({
                            "name": college.strip(),
                            "state": state.strip(),
                            "management_type": mgmt.strip()
                        }, on_conflict="name,state").execute()
                        
                        # Upsert Department
                        if res.data:
                            c_id = res.data[0]['id']
                            supabase.table("departments").upsert({
                                "college_id": c_id,
                                "dept_name": course.strip()
                            }, on_conflict="college_id,dept_name").execute()
                    except Exception as e:
                        print(f"⚠️ Error syncing {college}: {e}")

            # Pagination Logic
            next_btn = page.locator('a#course_table_next:not(.disabled)')
            if await next_btn.count() > 0:
                await next_btn.click()
                await asyncio.sleep(3) # Wait for next page load
                page_num += 1
            else:
                print("🏁 Scrape Complete!")
                break

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
