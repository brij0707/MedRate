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
        print("🚀 Launching Browser in Desktop Mode...")
        browser = await p.chromium.launch(headless=True)
        
        # FIX 1: Set a large Viewport (1920x1080) so filters aren't hidden
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await context.new_page()
        
        print("🌍 Going to NMC website...")
        # Increased timeout to 90s just to be safe
        await page.goto("https://www.nmc.org.in/information-desk/college-and-course-search/", timeout=90000)
        
        # FIX 2: Wait for the Dropdown with a specific state check
        print("⏳ Waiting for Course Dropdown...")
        course_dropdown = page.locator('select#courseName')
        await course_dropdown.wait_for(state="attached", timeout=60000)
        
        print("✅ Selecting 'All PG Courses'...")
        # Sometimes you need to force scroll to it
        await course_dropdown.scroll_into_view_if_needed()
        await page.select_option('select#courseName', label="All PG Courses")
        
        print("👆 Clicking View Results...")
        await page.click('input[value="View Results"]')
        
        print("⏳ Waiting for Data Table...")
        await page.wait_for_selector('table#course_table tbody tr', timeout=60000)

        # Optimize view to 500 entries
        print("⚡ Optimizing view to 500 entries...")
        await page.select_option('select[name="course_table_length"]', "500")
        await asyncio.sleep(5) 

        page_num = 1
        while True:
            print(f"📄 Scraping Page {page_num}...")
            rows = await page.query_selector_all('table#course_table tbody tr')
            
            for row in rows:
                cols = await row.query_selector_all('td')
                if len(cols) >= 6:
                    course = await cols[1].inner_text()
                    state = await cols[3].inner_text()
                    college = await cols[4].inner_text()
                    mgmt = await cols[5].inner_text()

                    try:
                        # 1. Upsert College
                        res = supabase.table("colleges").upsert({
                            "name": college.strip(),
                            "state": state.strip(),
                            "management_type": mgmt.strip()
                        }, on_conflict="name,state").execute()
                        
                        # 2. Upsert Department
                        if res.data:
                            c_id = res.data[0]['id']
                            supabase.table("departments").upsert({
                                "college_id": c_id,
                                "dept_name": course.strip()
                            }, on_conflict="college_id,dept_name").execute()
                    except Exception as e:
                        print(f"⚠️ Error: {e}")

            # Pagination
            next_btn = page.locator('a#course_table_next:not(.disabled)')
            if await next_btn.count() > 0:
                await next_btn.click()
                await asyncio.sleep(3)
                page_num += 1
            else:
                print("🏁 All pages scraped!")
                break

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
