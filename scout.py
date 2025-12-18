import time
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def run_scout():
    print("Starting the Scout Robot (Cloud Mode)...")
    
    options = Options()
    options.add_argument("--headless")  # Run without a window (Required for Cloud)
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    try:
        # distinct logic for trying to find the browser on the cloud
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
        # 1. Go to PickleballBrackets
        url = "https://pickleballbrackets.com/pts.aspx" 
        driver.get(url)
        time.sleep(3) # Wait for load

        # 2. Search for Virginia
        # Note: On the cloud, sometimes the screen size is small, so we force a size
        driver.set_window_size(1920, 1080)
        
        # Find search box (using the ID from before)
        # Note: If these IDs change, the script breaks.
        try:
            search_box = driver.find_element("id", "txtSearch") 
            search_box.send_keys("Virginia")
            
            search_btn = driver.find_element("id", "btnSearch")
            search_btn.click()
            time.sleep(3)
        except:
            print("Could not find search bar - site layout might have changed.")
            return []

        # 3. Scrape results
        tournaments = driver.find_elements("class name", "br-tournament-card")
        found_tourneys = []

        for t in tournaments:
            text = t.text
            if "Fairfax" in text or "Alexandria" in text or "Arlington" in text:
                link_element = t.find_element("tag name", "a")
                link = link_element.get_attribute("href")
                name = text.split('\n')[0]
                found_tourneys.append({"name": name, "link": link})
                
        return found_tourneys

    except Exception as e:
        print(f"Scout Error: {e}")
        return []
    
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    print(run_scout())