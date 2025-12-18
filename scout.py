import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def run_scout():
    print("Starting Scout Robot (Direct Link Mode)...")
    
    # 1. Setup Invisible Chrome
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    found_tourneys = []

    try:
        # 2. Go DIRECTLY to your specific local search URL
        url = "https://pickleballtournaments.com/search?show_all=true&zoom_level=7&current_page=1&tournament_filter=local"
        print(f"Navigating to filtered search...")
        driver.get(url)
        
        # 3. Wait for the results to populate
        # We wait 8 seconds to ensure the 'skeleton' loading finishes and real text appears
        time.sleep(8) 

        # 4. Scrape the Links
        print("Scanning page for tournament links...")
        
        # We look for all links (<a> tags) on the page
        all_links = driver.find_elements(By.TAG_NAME, "a")
        
        for link in all_links:
            try:
                href = link.get_attribute("href")
                text = link.text.strip()
                
                # FILTER: valid tournaments usually have "tournament/detail" in the URL
                if href and "tournament/detail" in href:
                    # Filter out tiny links (icons) to keep the list clean
                    if len(text) > 3:
                        # Deduplicate: Don't add the same tournament twice
                        if not any(t['link'] == href for t in found_tourneys):
                            
                            # Clean up the name (take the first line of text)
                            name = text.split('\n')[0]
                            
                            found_tourneys.append({
                                "name": name,
                                "link": href,
                                "date": "Check Link", # Date is hard to auto-read, user can click link
                                "location": "Local Search"
                            })
            except:
                continue

        print(f"Scout Success: Found {len(found_tourneys)} tournaments.")
        return found_tourneys

    except Exception as e:
        print(f"Scout Error: {e}")
        return []
    
    finally:
        driver.quit()

if __name__ == "__main__":
    results = run_scout()
    for r in results:
        print(f"- {r['name']}")