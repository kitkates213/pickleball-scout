import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# Try to import manager for local use
try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_MANAGER = True
except ImportError:
    HAS_MANAGER = False

def run_scout():
    print("Starting Scout Robot (User-Link Mode)...")
    
    # 1. Setup Headless Options
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # 2. Driver Selection
    cloud_driver_path = "/usr/bin/chromedriver"
    if os.path.exists(cloud_driver_path):
        service = Service(cloud_driver_path)
    elif HAS_MANAGER:
        service = Service(ChromeDriverManager().install())
    else:
        return []

    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        
        # 3. Go to YOUR specific stable URL
        url = "https://pickleballtournaments.com/search?show_all=true&zoom_level=7&current_page=1&tournament_filter=local"
        driver.get(url)
        
        # 4. Wait for results to populate (10 seconds)
        time.sleep(10) 

        # 5. Scrape Links
        found_tourneys = []
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in all_links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                # Broad Filter: Look for 'tournament' or 'event' in the URL
                if href and ("tournament" in href or "event" in href):
                    # Ignore tiny links or login links
                    if len(text) > 4 and "Log In" not in text:
                        if not any(t['link'] == href for t in found_tourneys):
                            found_tourneys.append({
                                "name": text.split('\n')[0],
                                "link": href,
                                "location": "Local",
                                "date": "Upcoming"
                            })
            except:
                continue
        
        return found_tourneys

    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    results = run_scout()
    print(f"Found {len(results)} items.")