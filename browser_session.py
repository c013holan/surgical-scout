"""
Browser Session Manager
Reuses existing Chrome profile with Mayo institutional access
"""

import os
import logging
import time
from typing import Optional
from pathlib import Path
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BrowserSession:
    """Manage browser session with existing Chrome profile"""

    def __init__(self, use_existing_profile: bool = True):
        """
        Initialize browser session

        Args:
            use_existing_profile: If True, uses existing Chrome profile with saved logins
        """
        self.driver = None
        self.use_existing_profile = use_existing_profile
        self.session = None
        logger.info("Initialized BrowserSession manager")

    def start_browser(self) -> webdriver.Chrome:
        """
        Start Chrome browser with existing profile

        Returns:
            Chrome webdriver instance
        """
        try:
            chrome_options = Options()

            if self.use_existing_profile:
                # Use existing Chrome Default profile where user is already logged in
                user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome")
                chrome_options.add_argument(f"user-data-dir={user_data_dir}")
                chrome_options.add_argument("profile-directory=Default")
                logger.info("Using Chrome Default profile with saved Mayo login")
            else:
                # Use temporary profile
                logger.info("Using temporary Chrome profile")

            # Standard options
            chrome_options.add_argument("--headless=new")  # New headless mode
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1200,800")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36"
            )

            # Suppress logging
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            chrome_options.add_experimental_option('useAutomationExtension', False)

            self.driver = webdriver.Chrome(options=chrome_options)
            logger.info("Chrome browser started")
            return self.driver

        except Exception as e:
            logger.error(f"Error starting browser: {e}")
            raise

    def get_cookies_as_session(self) -> requests.Session:
        """
        Extract cookies from browser and create requests session

        Returns:
            Requests session with browser cookies
        """
        try:
            if not self.driver:
                raise ValueError("Browser not started")

            session = requests.Session()

            # Extract all cookies from browser
            cookies = self.driver.get_cookies()

            for cookie in cookies:
                session.cookies.set(
                    cookie['name'],
                    cookie['value'],
                    domain=cookie.get('domain'),
                    path=cookie.get('path', '/')
                )

            # Set headers to match browser
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            })

            logger.info(f"Created session with {len(cookies)} cookies")
            self.session = session
            return session

        except Exception as e:
            logger.error(f"Error creating session from cookies: {e}")
            raise

    def navigate_to_article(self, doi: str) -> Optional[str]:
        """
        Navigate to article via DOI and find PDF URL

        Args:
            doi: Article DOI

        Returns:
            PDF URL if found, None otherwise
        """
        try:
            if not self.driver:
                self.start_browser()

            # Navigate via DOI resolver
            doi_url = f"https://doi.org/{doi}"
            logger.info(f"Navigating to: {doi_url}")
            self.driver.get(doi_url)

            # Wait for page to load
            time.sleep(3)

            # Get current URL after redirects
            current_url = self.driver.current_url
            logger.debug(f"Current URL: {current_url}")

            # Look for PDF link
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Strategy 1: Look for PDF links
            pdf_links = soup.find_all('a', href=lambda x: x and ('.pdf' in x.lower() or '/pdf' in x.lower()))

            for link in pdf_links:
                href = link.get('href', '')
                if href:
                    # Make absolute URL
                    pdf_url = urljoin(current_url, href)
                    if '.pdf' in pdf_url.lower() or '/pdf' in pdf_url.lower():
                        logger.info(f"Found PDF link: {pdf_url}")
                        return pdf_url

            # Strategy 2: Look for "Download PDF" or "View PDF" buttons/links
            pdf_buttons = soup.find_all(['a', 'button'], text=lambda x: x and 'pdf' in x.lower())

            for button in pdf_buttons:
                href = button.get('href') or button.get('data-href') or button.get('data-url')
                if href:
                    pdf_url = urljoin(current_url, href)
                    logger.info(f"Found PDF button: {pdf_url}")
                    return pdf_url

            logger.warning(f"No PDF link found for DOI: {doi}")
            return None

        except Exception as e:
            logger.error(f"Error navigating to article: {e}")
            return None

    def close(self):
        """Close browser"""
        if self.driver:
            try:
                self.driver.quit()
                logger.info("Browser closed")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")


def get_authenticated_session() -> requests.Session:
    """
    Get authenticated session using browser cookies

    Returns:
        Requests session with authentication cookies
    """
    browser = BrowserSession(use_existing_profile=True)

    try:
        # Start browser with existing profile
        browser.start_browser()

        # Wait a moment for profile to load
        time.sleep(2)

        # Extract cookies as session
        session = browser.get_cookies_as_session()

        return session

    finally:
        browser.close()


def get_pdf_via_browser(doi: str) -> Optional[str]:
    """
    Get PDF URL by navigating via browser

    Args:
        doi: Article DOI

    Returns:
        PDF URL if found, None otherwise
    """
    browser = BrowserSession(use_existing_profile=True)

    try:
        browser.start_browser()
        pdf_url = browser.navigate_to_article(doi)
        return pdf_url

    finally:
        browser.close()


if __name__ == "__main__":
    # Test the browser session
    from dotenv import load_dotenv

    load_dotenv(override=True)

    print("Testing Browser Session...\n")

    # Test with a sample DOI
    test_doi = "10.1097/PRS.0000000000010023"  # Recent PRS article

    print(f"Testing with DOI: {test_doi}\n")

    try:
        print("Starting browser with existing profile...")
        pdf_url = get_pdf_via_browser(test_doi)

        if pdf_url:
            print(f"✓ Found PDF URL: {pdf_url}")
        else:
            print("✗ No PDF URL found")

    except Exception as e:
        print(f"✗ Error: {e}")
