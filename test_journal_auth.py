"""
Test accessing a journal article through Mayo
"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

# Test with a real article
TEST_ARTICLE_DOI = "10.1097/PRS.0000000000010717"  # Example from Plastic & Reconstructive Surgery

print("Testing journal access through Mayo...")

options = Options()
driver = webdriver.Chrome(options=options)

try:
    # Go directly to journal article
    article_url = f"https://doi.org/{TEST_ARTICLE_DOI}"
    print(f"1. Navigating to article: {article_url}")
    driver.get(article_url)
    time.sleep(3)
    
    print(f"2. Current URL: {driver.current_url}")
    print(f"3. Page title: {driver.title}")
    
    # Check if we're at Mayo login
    if "mayo.edu" in driver.current_url or "login" in driver.current_url.lower():
        print("4. Detected Mayo login page - entering credentials...")
        
        # Wait for username field
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "userNameInput"))
        )
        username_field.send_keys("holan.cole@mayo.edu")
        
        password_field = driver.find_element(By.ID, "passwordInput")
        password_field.send_keys("Qa1w23se^")
        
        submit_button = driver.find_element(By.ID, "submitButton")
        submit_button.click()
        
        print("5. Credentials submitted, waiting for redirect...")
        time.sleep(5)
        
        print(f"6. After auth URL: {driver.current_url}")
        print(f"7. Page title: {driver.title}")
        
        # Check if we're at the article
        if "doi.org" not in driver.current_url and "mayo.edu" not in driver.current_url:
            print("✓ Successfully reached article!")
            
            # Get cookies from the journal domain
            cookies = driver.get_cookies()
            print(f"8. Got {len(cookies)} cookies from: {driver.current_url}")
            
            # Try to find PDF link
            try:
                pdf_links = driver.find_elements(By.PARTIAL_LINK_TEXT, "PDF")
                print(f"9. Found {len(pdf_links)} PDF links")
                if pdf_links:
                    print(f"   PDF link: {pdf_links[0].get_attribute('href')}")
            except:
                pass
        else:
            print("✗ Still at login/redirect page")
    else:
        print("4. No login required - checking article access...")
        time.sleep(2)
        print(f"   Final URL: {driver.current_url}")
    
    print("\nTest complete - keeping browser open for 10 seconds...")
    time.sleep(10)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    driver.quit()
    print("Browser closed")
