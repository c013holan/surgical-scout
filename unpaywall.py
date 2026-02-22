"""
Unpaywall API Integration
Access legal open access versions of articles
"""

import logging
import requests
from typing import Optional, Dict
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UnpaywallClient:
    """Access open access articles via Unpaywall API"""

    BASE_URL = "https://api.unpaywall.org/v2"

    def __init__(self, email: str):
        """
        Initialize Unpaywall client

        Args:
            email: Your email (required by Unpaywall API)
        """
        self.email = email
        logger.info(f"Initialized Unpaywall client with email: {email}")

    def get_oa_pdf(self, doi: str) -> Optional[str]:
        """
        Get open access PDF URL for a DOI

        Args:
            doi: Article DOI

        Returns:
            PDF URL if open access version exists, None otherwise
        """
        try:
            if not doi:
                return None

            logger.debug(f"Checking Unpaywall for DOI: {doi}")

            # Query Unpaywall API
            url = f"{self.BASE_URL}/{doi}"
            params = {"email": self.email}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                # Check if open access
                if data.get("is_oa"):
                    best_location = data.get("best_oa_location")

                    if best_location:
                        pdf_url = best_location.get("url_for_pdf")

                        if pdf_url:
                            logger.info(f"✓ Found OA PDF via Unpaywall: {doi}")
                            return pdf_url
                        else:
                            logger.debug(f"OA article found but no PDF URL: {doi}")
                else:
                    logger.debug(f"Not open access: {doi}")

            elif response.status_code == 404:
                logger.debug(f"DOI not found in Unpaywall: {doi}")
            else:
                logger.warning(f"Unpaywall API error {response.status_code}: {doi}")

            return None

        except Exception as e:
            logger.error(f"Error querying Unpaywall for {doi}: {e}")
            return None

    def get_article_info(self, doi: str) -> Optional[Dict]:
        """
        Get full article information from Unpaywall

        Args:
            doi: Article DOI

        Returns:
            Dictionary with OA info if available, None otherwise
        """
        try:
            if not doi:
                return None

            url = f"{self.BASE_URL}/{doi}"
            params = {"email": self.email}

            response = requests.get(url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()

                if data.get("is_oa"):
                    best_location = data.get("best_oa_location")

                    return {
                        "is_oa": True,
                        "pdf_url": best_location.get("url_for_pdf") if best_location else None,
                        "url": best_location.get("url") if best_location else None,
                        "version": best_location.get("version") if best_location else None,
                        "license": best_location.get("license") if best_location else None,
                    }

            return None

        except Exception as e:
            logger.error(f"Error getting article info for {doi}: {e}")
            return None


def get_oa_pdf_url(doi: str, email: str) -> Optional[str]:
    """
    Convenience function to get OA PDF URL

    Args:
        doi: Article DOI
        email: Your email

    Returns:
        PDF URL if available, None otherwise
    """
    client = UnpaywallClient(email)
    return client.get_oa_pdf(doi)


if __name__ == "__main__":
    # Test the client
    from dotenv import load_dotenv
    import os

    load_dotenv(override=True)

    print("Testing Unpaywall API...\n")

    email = os.getenv("PUBMED_EMAIL")
    if not email:
        print("✗ PUBMED_EMAIL not set in .env")
        exit(1)

    # Test with a known OA article
    test_doi = "10.1371/journal.pone.0308208"  # Recent PLoS ONE article (always OA)

    print(f"Testing with DOI: {test_doi}\n")

    client = UnpaywallClient(email)

    # Get PDF URL
    pdf_url = client.get_oa_pdf(test_doi)
    if pdf_url:
        print(f"✓ Found OA PDF: {pdf_url}")
    else:
        print("✗ No OA PDF found")

    # Get full info
    info = client.get_article_info(test_doi)
    if info:
        print(f"\n✓ Article info:")
        for key, value in info.items():
            print(f"  - {key}: {value}")
    else:
        print("\n✗ No OA info available")
