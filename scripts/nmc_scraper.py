import os
import asyncio
from playwright.async_api import async_playwright
from supabase import create_client, Client
from geopy.geocoders import Nominatim
import time

# 1. Initialize Supabase with your Secret Names
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(URL, KEY)

# 2. GPS Helper Function
def get_coordinates(name, state):
    try:
        geolocator = Nominatim(user_agent="medRate_scraper_v1")
        # Adding 'India' to ensure accuracy
        location = geolocator.geocode(f"{name}, {state}, India")
        if location:
            # Format required for PostGIS/Supabase Geography type
            return f"POINT({location.longitude} {location.latitude})"
    except Exception as e:
        print(f"⚠️ Geocoding failed for {name}: {e}")
    return None

async def run_scraper():
    async with async_playwright() as p:
        print("🚀 Launching Headless Browser...")
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Navigate to NMC Portal
        await page.goto("https://www.nmc.org.in/information-desk/college-and-course-search/")
        
        # Select 'PG' and Search
        await page.click('input[value="PG"]')
        await page.click('#gosearch')
        await page.wait_for_selector('table#course_table tr')

        # Get all rows (skipping header)
        rows = await page.query_selector_all('table#course_table tr')
        print(f"📊 Found {len(rows) - 1} colleges. Starting Upsert...")

        for row in rows[1:10]:  # Testing with first 10 for safety
            cols = await row.query_selector_all('td')
            if len(cols) > 3:
                name = await cols[1].inner_text()
                state = await cols[2].inner_text()
                mgt = await cols[3].inner_text()
                
                coords = get_coordinates(name, state)
                
                # 'Upsert' logic: Match by name and state
                data = {
                    "name": name.strip(),
                    "state": state.strip(),
                    "management_type": mgt.strip(),
                    "coordinates": coords
                }
                
                try:
                    # Using 'on_conflict' to avoid duplicates
                    supabase.table("colleges").upsert(data, on_conflict="name,state").execute()
                    print(f"✅ Synced: {name}")
                except Exception as e:
                    print(f"❌ Error syncing {name}: {e}")
                
                # Respectful delay for the Geocoder API
                time.sleep(1)

        await browser.close()
        print("🏁 Scrape Complete.")

if __name__ == "__main__":
    asyncio.run(run_scraper())
