import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# We try to import webdriver_manager for local laptop use
# If it fails (on some servers), we just skip it
try:
    from webdriver_manager.chrome import ChromeDriverManager
    HAS_MANAGER = True
except ImportError:
    HAS_MANAGER = False

def run_scout():
    print("Starting Scout Robot (Hybrid Mode)...")
    
    # 1. Setup Headless Options (Required for Cloud)
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    # 2. INTELLIGENT DRIVER SELECTION
    # Check if we are on the Cloud Server (Linux) where the driver is pre-installed
    cloud_driver_path = "/usr/bin/chromedriver"
    
    if os.path.exists(cloud_driver_path):
        print(f"Cloud Environment Detected. Using system driver: {cloud_driver_path}")
        service = Service(cloud_driver_path)
    elif HAS_MANAGER:
        print("Local Environment Detected. Downloading matching driver...")
        service = Service(ChromeDriverManager().install())
    else:
        print("Critical Error: No driver found and manager not available.")
        return []

    try:
        driver = webdriver.Chrome(service=service, options=options)
    except Exception as e:
        print(f"Driver Crash: {e}")
        return []

    found_tourneys = []

    try:
        # 3. Go DIRECTLY to your filtered search URL
        url = "https://pickleballtournaments.com/search?show_all=true&zoom_level=7&current_page=1&tournament_filter=local"
        print(f"Navigating to: {url}")
        driver.get(url)
        
        # 4. Wait for results (8 seconds)
        time.sleep(8) 

        # 5. Scan for Links
        print("Scanning page...")
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in all_links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                # Filter for valid tournament details
                if href and "tournament/detail" in href:
                    if len(text) > 3:
                        if not any(t['link'] == href for t in found_tourneys):
                            name = text.split('\n')[0]
                            found_tourneys.append({
                                "name": name,
                                "link": href,
                                "date": "Check Link", 
                                "location": "Local Search"
                            })
            except:
                continue

        print(f"Success: Found {len(found_tourneys)} tournaments.")
        return found_tourneys

    except Exception as e:
        print(f"Scout Logic Error: {e}")
        return []
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    results = run_scout()
    for r in results:
        print(f"- {r['name']}")