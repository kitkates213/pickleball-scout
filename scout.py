import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

def run_scout():
    print("Starting Scout Robot...")
    
    # 1. Setup Headless Chrome (Invisible)
    options = Options()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # This 'user-agent' trick makes the website think we are a real laptop, not a robot
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        # 2. Go DIRECTLY to your filtered search URL
        # This URL already includes: local filter, zoom level, and showing all pages
        url = "https://pickleballtournaments.com/search?zoom_level=7&current_page=1&show_all=true&tournament_filter=local"
        driver.get(url)
        
        # 3. Wait for the data to load
        print("Landing on page... waiting for list to populate...")
        time.sleep(8) # Generous wait time for the map/list to load

        # 4. Scrape the "Cards"
        # On this specific site, tournament cards often sit in a div called 'tournament-card' or similar.
        # We will cast a wide net to find links.
        
        found_tourneys = []
        
        # Strategy: Find all links that look like tournament details
        # The site usually lists tournaments in <div> elements with specific classes.
        # We'll look for the main container.
        
        # Attempt to find the main list items
        # Note: Class names here are based on common structures for this platform.
        items = driver.find_elements(By.CSS_SELECTOR, "div.search-result-item, div.tournament-card, .event-item")
        
        if not items:
            # Fallback: Find all links with "tournament" in the URL
            print("Standard containers not found, switching to Link Scan Mode...")
            links = driver.find_elements(By.TAG_NAME, "a")
            for link in links:
                href = link.get_attribute("href")
                text = link.text
                if href and "tournament" in href and len(text) > 5:
                     # Only add if it's not a duplicate
                    if not any(d['link'] == href for d in found_tourneys):
                        found_tourneys.append({
                            "name": text.split("\n")[0], # Take first line as title
                            "date": "Check Link",
                            "location": "Near 22030",
                            "link": href
                        })
        else:
            # If we found nice containers, parse them neatly
            for item in items:
                text_content = item.text.split("\n")
                name = text_content[0]
                
                # Try to find the link inside this container
                try:
                    link_elem = item.find_element(By.TAG_NAME, "a")
                    link = link_elem.get_attribute("href")
                except:
                    link = url

                found_tourneys.append({
                    "name": name,
                    "date": "Upcoming", # Date is hard to parse reliably without specific tags
                    "location": "Local",
                    "link": link
                })

        return found_tourneys

    except Exception as e:
        print(f"Scout Error: {e}")
        return []
    
    finally:
        driver.quit()

if __name__ == "__main__":
    # Test run
    results = run_scout()
    print(f"Found {len(results)} tournaments.")
    for r in results:
        print(r)