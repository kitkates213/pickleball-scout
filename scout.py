import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Try to import manager for local use
try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_MANAGER = True
except ImportError:
    HAS_MANAGER = False

def run_scout():
    print("Starting Scout Robot (Explicit Search Mode)...")
    
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
        
        # 3. Go to PickleballBrackets (The 'Clean' Database)
        url = "https://pickleballbrackets.com/pts.aspx"
        print(f"Navigating to: {url}")
        driver.get(url)
        time.sleep(5) 

        # 4. EXPLICIT SEARCH (Bypass GPS)
        # We find the search box and type "Virginia"
        try:
            search_box = driver.find_element(By.ID, "txtSearch")
            search_box.clear()
            search_box.send_keys("Virginia")
            search_box.send_keys(Keys.RETURN)
            print("Typed 'Virginia' and hit Enter...")
            time.sleep(5) # Wait for table to reload
        except Exception as e:
            print(f"Search Box Error: {e}")

        # 5. Scrape Real Results
        print("Scanning results...")
        found_tourneys = []
        
        # We look for the specific tournament cards
        # usually class 'br-tournament-card' or links with 'ptd.aspx'
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in all_links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                # STRICT FILTER: 
                # 1. Must have 'ptd.aspx' (Tournament Detail) in the link
                # 2. Must NOT be 'Log In' or 'Sign Up'
                if href and "ptd.aspx" in href:
                    if len(text) > 5 and "Log In" not in text:
                        
                        # Deduplicate
                        if not any(t['link'] == href for t in found_tourneys):
                            # Clean the name (usually line 1)
                            clean_name = text.split('\n')[0]
                            
                            # Optional: Filter for nearby cities if text allows
                            # or just return all VA tournaments
                            found_tourneys.append({
                                "name": clean_name,
                                "link": href,
                                "location": "Virginia",
                                "date": "See Details"
                            })
            except:
                continue

        print(f"Success: Found {len(found_tourneys)} tournaments.")
        return found_tourneys

    except Exception as e:
        print(f"Error: {e}")
        return []
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    results = run_scout()
    for r in results:
        print(f"- {r['name']}")