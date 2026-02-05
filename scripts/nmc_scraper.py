import os
import asyncio
from playwright.async_api import async_playwright
from supabase import create_client, Client
from geopy.geocoders import Nominatim
import pandas as pd

# Load GitHub Secrets
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase: Client = create_client(url, key)

async def scrape_nmc():
    async with async_playwright() as p:
        # 1. Open Browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_row()
        
        # 2. Go to NMC Search
        print("Navigating to NMC...")
        await page.goto("https://www.nmc.org.in/information-desk/college-and-course-search/")
        
        # 3. Apply Filters (Strategy: Select PG)
        await page.click('input[value="PG"]') # Select PG Radio button
        # Yahan hum baki clicks aur search logic add karenge
        
        # 4. Extract Data (Example Logic)
        # Hum table rows ko loop karenge aur data extract karenge
        
        await browser.close()

def get_coordinates(college_name, state):
    geolocator = Nominatim(user_agent="medRate_scraper")
    location = geolocator.geocode(f"{college_name}, {state}, India")
    if location:
        return f"POINT({location.longitude} {location.latitude})"
    return None

if __name__ == "__main__":
    asyncio.run(scrape_nmc())

