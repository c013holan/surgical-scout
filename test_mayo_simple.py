from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time

print("Testing Mayo ADFS login...")

options = Options()
driver = webdriver.Chrome(options=options)

try:
    # Navigate to ADFS
    print("1. Navigating to ADFS...")
    driver.get("https://login.mayo.edu/adfs/ls/")
    time.sleep(2)
    
    print(f"2. Current URL: {driver.current_url}")
    print(f"3. Page title: {driver.title}")
    
    # Find username field
    print("4. Looking for username field...")
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "userNameInput"))
    )
    print("   ✓ Found username field")
    
    # Enter credentials
    print("5. Entering credentials...")
    username_field.send_keys("holan.cole@mayo.edu")
    
    password_field = driver.find_element(By.ID, "passwordInput")
    password_field.send_keys("Qa1w23se^")
    
    print("6. Submitting form...")
    submit_button = driver.find_element(By.ID, "submitButton")
    submit_button.click()
    
    # Wait for response
    time.sleep(5)
    
    print(f"7. After submit URL: {driver.current_url}")
    print(f"8. Page title: {driver.title}")
    
    # Check for errors
    try:
        error = driver.find_element(By.ID, "errorText")
        print(f"   ✗ Error found: {error.text}")
    except:
        print("   ✓ No error message found")
    
    # Get cookies
    cookies = driver.get_cookies()
    print(f"9. Got {len(cookies)} cookies")
    
    print("\n✓ Test complete - press Ctrl+C to close browser")
    time.sleep(10)
    
except Exception as e:
    print(f"\n✗ Error: {e}")
finally:
    driver.quit()
    print("Browser closed")
