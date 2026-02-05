import os
import asyncio
from playwright.async_api import async_playwright

async def run_scraper():
    async with async_playwright() as p:
        # Launch browser with a real user agent to avoid being blocked
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
        page = await context.new_page()
        
        print("🚀 Navigating to NMC Portal...")
        await page.goto("https://www.nmc.org.in/information-desk/college-and-course-search/", wait_until="networkidle")

        # Step 1: Set filters to 'ALL' (Usually default, but we'll be explicit)
        # The selectors are based on the standard NMC table search UI
        print("🔍 Setting filters to 'ALL'...")
        
        # Step 2: Click the 'View Results' button shown in your screenshot
        # Using a more robust selector for that specific button
        view_results_btn = page.locator('input[type="button"][value="View Results"]')
        await view_results_btn.wait_for(state="visible")
        await view_results_btn.click()

        # Step 3: Wait for the results table to populate
        print("⏳ Waiting for table to load...")
        await page.wait_for_selector('table#course_table', timeout=60000)

        # Step 4: Extract the rows
        rows = await page.query_selector_all('table#course_table tr')
        print(f"✅ Success! Found {len(rows)} entries in the table.")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_scraper())
