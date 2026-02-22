"""
PubMed Central (PMC) Fetcher
Access free full-text articles from PMC
"""

import logging
import requests
from typing import Optional, Tuple
from Bio import Entrez
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PMCFetcher:
    """Fetch full-text articles from PubMed Central"""

    PMC_PDF_BASE = "https://www.ncbi.nlm.nih.gov/pmc/articles"

    def __init__(self, email: str):
        """
        Initialize PMC fetcher

        Args:
            email: Your email (required by NCBI)
        """
        self.email = email
        Entrez.email = email
        logger.info(f"Initialized PMC fetcher with email: {email}")

    def get_pmc_id(self, pmid: str) -> Optional[str]:
        """
        Get PMC ID from PubMed ID

        Args:
            pmid: PubMed ID

        Returns:
            PMC ID if available, None otherwise
        """
        try:
            logger.debug(f"Checking for PMC ID for PMID: {pmid}")

            # Use Entrez to convert PMID to PMC ID
            handle = Entrez.elink(dbfrom="pubmed", db="pmc", id=pmid)
            result = Entrez.read(handle)
            handle.close()

            # Check if PMC link exists
            if result and result[0]["LinkSetDb"]:
                pmc_ids = result[0]["LinkSetDb"][0]["Link"]
                if pmc_ids:
                    pmc_id = pmc_ids[0]["Id"]
                    logger.info(f"✓ Found PMC ID: PMC{pmc_id} for PMID {pmid}")
                    return pmc_id

            logger.debug(f"No PMC version for PMID {pmid}")
            return None

        except Exception as e:
            logger.error(f"Error getting PMC ID for {pmid}: {e}")
            return None

    def get_pmc_pdf_url(self, pmc_id: str) -> Optional[str]:
        """
        Get PDF URL for PMC article

        Args:
            pmc_id: PMC ID (without 'PMC' prefix)

        Returns:
            PDF URL if available, None otherwise
        """
        try:
            # PMC PDF URLs follow pattern: /pmc/articles/PMCXXXXXXX/pdf/
            pdf_url = f"{self.PMC_PDF_BASE}/PMC{pmc_id}/pdf/"

            logger.debug(f"PMC PDF URL: {pdf_url}")

            # Verify PDF exists by checking headers
            response = requests.head(pdf_url, timeout=10, allow_redirects=True)

            if response.status_code == 200:
                logger.info(f"✓ PMC PDF available: PMC{pmc_id}")
                return pdf_url
            else:
                logger.debug(f"PMC PDF not available (status {response.status_code}): PMC{pmc_id}")
                return None

        except Exception as e:
            logger.error(f"Error checking PMC PDF for PMC{pmc_id}: {e}")
            return None

    def get_full_text_url(self, pmid: str) -> Optional[Tuple[str, str]]:
        """
        Get full-text PDF URL from PMC if available

        Args:
            pmid: PubMed ID

        Returns:
            Tuple of (pdf_url, source) if available, None otherwise
        """
        try:
            # Get PMC ID
            pmc_id = self.get_pmc_id(pmid)

            if not pmc_id:
                return None

            # Get PDF URL
            pdf_url = self.get_pmc_pdf_url(pmc_id)

            if pdf_url:
                return (pdf_url, "PMC")

            return None

        except Exception as e:
            logger.error(f"Error getting PMC full text for {pmid}: {e}")
            return None


def get_pmc_pdf(pmid: str, email: str) -> Optional[Tuple[str, str]]:
    """
    Convenience function to get PMC PDF URL

    Args:
        pmid: PubMed ID
        email: Your email

    Returns:
        Tuple of (pdf_url, source) if available, None otherwise
    """
    fetcher = PMCFetcher(email)
    return fetcher.get_full_text_url(pmid)


if __name__ == "__main__":
    # Test the fetcher
    from dotenv import load_dotenv
    import os

    load_dotenv(override=True)

    print("Testing PMC Fetcher...\n")

    email = os.getenv("PUBMED_EMAIL")
    if not email:
        print("✗ PUBMED_EMAIL not set in .env")
        exit(1)

    # Test with a known PMC article
    test_pmid = "38000000"  # Replace with actual PMID that has PMC version

    print(f"Testing with PMID: {test_pmid}\n")

    fetcher = PMCFetcher(email)

    # Get PMC ID
    pmc_id = fetcher.get_pmc_id(test_pmid)
    if pmc_id:
        print(f"✓ Found PMC ID: PMC{pmc_id}")

        # Get PDF URL
        pdf_url = fetcher.get_pmc_pdf_url(pmc_id)
        if pdf_url:
            print(f"✓ PMC PDF available: {pdf_url}")
        else:
            print("✗ PMC PDF not available")
    else:
        print("✗ No PMC version for this article")

    # Test convenience function
    print("\nTesting convenience function:")
    result = get_pmc_pdf(test_pmid, email)
    if result:
        pdf_url, source = result
        print(f"✓ Full text available from {source}: {pdf_url}")
    else:
        print("✗ No full text available")
