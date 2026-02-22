"""
PDF Downloader for Journal Articles
Downloads full-text PDFs using authenticated Mayo session
"""

import os
import logging
import time
import random
from pathlib import Path
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, quote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PDFDownloader:
    """Handle downloading journal article PDFs"""

    PDF_DIR = "pdfs"
    DOWNLOAD_TIMEOUT = 30
    RETRY_ATTEMPTS = 2
    DELAY_RANGE = (2, 5)  # Random delay between downloads (seconds)

    # Publisher-specific PDF URL patterns
    PUBLISHER_PATTERNS = {
        "lww.com": "/pdfs/",  # Lippincott Williams & Wilkins
        "wiley.com": "/doi/pdf",
        "sciencedirect.com": "/science/article/pii/",
        "springer.com": "/content/pdf/",
        "journals.sagepub.com": "/doi/pdf/",
    }

    def __init__(self, session: Optional[requests.Session] = None, save_dir: str = PDF_DIR):
        """
        Initialize PDF downloader

        Args:
            session: Optional authenticated requests session (for browser-based downloads)
            save_dir: Directory to save PDFs
        """
        if session:
            self.session = session
            logger.info("Using provided authenticated session")
        else:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/pdf,*/*',
            })
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(exist_ok=True)
        logger.info(f"Initialized PDF downloader, saving to {self.save_dir}")

    def download_from_url(self, pdf_url: str, pmid: str, procedure: str) -> Optional[Path]:
        """
        Download PDF from a direct URL

        Args:
            pdf_url: Direct URL to PDF
            pmid: PubMed ID
            procedure: Procedure name (for filename)

        Returns:
            Path to downloaded PDF if successful, None otherwise
        """
        return self.download_pdf(pdf_url, pmid, procedure)

    def download_pdf(self, pdf_url: str, pmid: str, procedure: str) -> Optional[Path]:
        """
        Download PDF from URL

        Args:
            pdf_url: URL of PDF
            pmid: PubMed ID
            procedure: Procedure name (for filename)

        Returns:
            Path to downloaded PDF if successful, None otherwise
        """
        try:
            # Clean procedure name for filename
            clean_procedure = "".join(c for c in procedure if c.isalnum() or c in (' ', '-', '_')).strip()
            clean_procedure = clean_procedure.replace(' ', '_')

            filename = f"{pmid}_{clean_procedure}.pdf"
            filepath = self.save_dir / filename

            # Skip if already downloaded
            if filepath.exists():
                logger.info(f"PDF already exists: {filename}")
                return filepath

            logger.info(f"Downloading PDF: {filename}")

            # Add random delay to be respectful
            delay = random.uniform(*self.DELAY_RANGE)
            time.sleep(delay)

            # Download with retries
            for attempt in range(1, self.RETRY_ATTEMPTS + 1):
                try:
                    response = self.session.get(
                        pdf_url,
                        timeout=self.DOWNLOAD_TIMEOUT,
                        stream=True
                    )

                    if response.status_code == 200:
                        # Check if it's actually a PDF
                        content_type = response.headers.get('Content-Type', '')
                        if 'pdf' not in content_type.lower():
                            logger.warning(f"Response is not a PDF: {content_type}")
                            # Try anyway - some servers don't set correct content type
                            pass

                        # Save PDF
                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        # Verify file was written
                        if filepath.exists() and filepath.stat().st_size > 1000:
                            logger.info(f"✓ Downloaded: {filename} ({filepath.stat().st_size} bytes)")
                            return filepath
                        else:
                            logger.warning(f"Downloaded file too small or missing: {filename}")
                            return None

                    else:
                        logger.warning(f"Download failed (attempt {attempt}): HTTP {response.status_code}")

                except requests.Timeout:
                    logger.warning(f"Download timeout (attempt {attempt})")

                except Exception as e:
                    logger.error(f"Download error (attempt {attempt}): {e}")

                # Wait before retry
                if attempt < self.RETRY_ATTEMPTS:
                    time.sleep(2)

            logger.error(f"Failed to download after {self.RETRY_ATTEMPTS} attempts: {pdf_url}")
            return None

        except Exception as e:
            logger.error(f"Error in download_pdf: {e}")
            return None

def download_pdf_from_url(pdf_url: str, pmid: str, procedure: str) -> Optional[Path]:
    """
    Convenience function to download PDF from URL

    Args:
        pdf_url: Direct URL to PDF
        pmid: PubMed ID
        procedure: Procedure name

    Returns:
        Path to downloaded PDF if successful, None otherwise
    """
    downloader = PDFDownloader()
    return downloader.download_from_url(pdf_url, pmid, procedure)


if __name__ == "__main__":
    # Test the downloader
    from dotenv import load_dotenv

    load_dotenv(override=True)

    print("Testing PDF Downloader...\n")

    try:
        # Test with a sample PMC PDF URL
        test_url = "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC10000000/pdf/"
        test_pmid = "38000000"

        print(f"Testing download from URL: {test_url}")
        downloader = PDFDownloader()
        pdf_path = downloader.download_from_url(test_url, test_pmid, "TestProcedure")

        if pdf_path:
            print(f"✓ Downloaded to: {pdf_path}")
        else:
            print("✗ Download failed (expected if URL doesn't exist)")

    except Exception as e:
        print(f"✗ Error: {e}")
