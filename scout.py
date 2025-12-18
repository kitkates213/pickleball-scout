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
    print("Starting Scout Robot (Diagnostic Mode)...")
    
    # 1. Setup Headless Options
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    # New Trick: specific headers to look more human
    options.add_argument("--accept-lang=en-US,en;q=0.9")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36")

    # 2. Driver Selection (Cloud vs Local)
    cloud_driver_path = "/usr/bin/chromedriver"
    if os.path.exists(cloud_driver_path):
        service = Service(cloud_driver_path)
    elif HAS_MANAGER:
        service = Service(ChromeDriverManager().install())
    else:
        return [{"name": "Error: Driver not found", "link": "#"}]

    driver = None
    try:
        driver = webdriver.Chrome(service=service, options=options)
        
        # 3. Target URL
        url = "https://pickleballtournaments.com/search?show_all=true&zoom_level=7&current_page=1&tournament_filter=local"
        driver.get(url)
        
        # 4. Scroll to trigger content loading
        time.sleep(3)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(5) 

        # 5. DIAGNOSTIC: Check what page we are actually on
        page_title = driver.title
        print(f"Robot sees page title: {page_title}")

        # 6. Scrape Links
        found_tourneys = []
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in all_links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                # Loose filter: Just look for 'tournament' or 'event' keyword
                if href and ("tournament" in href or "event" in href):
                    if len(text) > 3:
                        if not any(t['link'] == href for t in found_tourneys):
                            found_tourneys.append({
                                "name": text.split('\n')[0],
                                "link": href,
                                "location": "Scouted Result",
                                "date": "See Link"
                            })
            except:
                continue
        
        # 7. RESULTS LOGIC
        if len(found_tourneys) > 0:
            return found_tourneys
        else:
            # If empty, return the DIAGNOSTIC info so we know why!
            return [{
                "name": f"⚠️ Robot Blocked. Page Title: '{page_title}'", 
                "link": url,
                "location": "Debug Info",
                "date": "Error"
            }]

    except Exception as e:
        return [{"name": f"Error: {str(e)}", "link": "#"}]
    
    finally:
        if driver:
            driver.quit()

if __name__ == "__main__":
    print(run_scout())