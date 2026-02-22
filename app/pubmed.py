import os
import re
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from Bio import Entrez

# Configure logging
logger = logging.getLogger(__name__)

class PubMedSearcher:
    """
    Handle PubMed searches using Biopython.
    Adapted for Aesthetic Surgery and related journals.
    """

    TARGET_JOURNALS = [
        "Plastic and Reconstructive Surgery",
        "Aesthetic Surgery Journal",
        "Journal of Plastic, Reconstructive & Aesthetic Surgery",
        "Annals of Plastic Surgery",
        "Dermatologic Surgery",
        "JAMA Facial Plastic Surgery",
        "Facial Plastic Surgery & Aesthetic Medicine",
        "Clinics in Plastic Surgery",
        "Aesthetic Plastic Surgery",
    ]

    def __init__(self, email: str):
        Entrez.email = email
        self.email = email

    def search(self, query: str, months_back: int = 18, max_results: int = 5) -> List[Dict]:
        """
        Search PubMed for recent articles about a procedure.
        Uses a two-pass strategy: first with journal filter, then broadened if no results.
        """
        try:
            # Clean the query: "Botox (glabella, forehead)" -> "Botox" with sub-terms
            clean_query = self._clean_query(query)
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=months_back * 30)
            date_filter = f"{start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[DP]"

            # Build journal filter
            journal_filter = " OR ".join([f'"{journal}"[Journal]' for journal in self.TARGET_JOURNALS])

            # Pass 1: Search with journal filter
            search_query = f'({clean_query}) AND ({journal_filter}) AND ({date_filter})'
            logger.info(f"Searching PubMed (pass 1, with journals): {clean_query}")
            id_list = self._search_pubmed(search_query, max_results)

            # Pass 2: If no results, broaden to any journal but add aesthetic/plastic surgery context
            if not id_list:
                broad_query = f'({clean_query}) AND (plastic surgery OR aesthetic OR cosmetic) AND ({date_filter})'
                logger.info(f"Searching PubMed (pass 2, broadened): {clean_query}")
                id_list = self._search_pubmed(broad_query, max_results)

            if not id_list:
                logger.warning(f"No results found for: {query}")
                return []

            return self._fetch_articles(id_list)

        except Exception as e:
            logger.error(f"Error searching PubMed: {e}", exc_info=True)
            return []

    def _clean_query(self, raw_query: str) -> str:
        """
        Clean procedure names from the Google Sheet for PubMed search.
        Examples:
            "Botox (glabella, forehead, crow's feet)" -> "botulinum toxin glabella forehead"
            "Filler (lips, NLF, tear trough)" -> "dermal filler lips nasolabial fold tear trough"
            "Rhinoplasty (primary open)" -> "rhinoplasty primary open"
        """
        # Extract base term and parenthetical
        match = re.match(r'^([^(]+?)(?:\s*\((.+?)\))?\s*$', raw_query)
        if match:
            base = match.group(1).strip()
            sub_terms = match.group(2)
            
            # Expand common abbreviations
            expansions = {
                "NLF": "nasolabial fold",
                "Botox": "botulinum toxin",
                "Filler": "dermal filler",
            }
            base = expansions.get(base, base)
            
            if sub_terms:
                # Split sub-terms and join with OR for broader results
                parts = [t.strip() for t in sub_terms.split(",") if t.strip()]
                # Expand abbreviations in sub-terms too
                parts = [expansions.get(p, p) for p in parts]
                return f'{base} AND ({" OR ".join(parts)})'
            return base
        return raw_query

    def _search_pubmed(self, query: str, max_results: int) -> List[str]:
        """Execute a PubMed search and return list of PMIDs."""
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="relevance"
        )
        search_results = Entrez.read(handle)
        handle.close()
        return search_results.get("IdList", [])

    def _fetch_articles(self, id_list: List[str]) -> List[Dict]:
        """Fetch article details from a list of PMIDs."""
        handle = Entrez.efetch(
            db="pubmed",
            id=id_list,
            rettype="abstract",
            retmode="xml"
        )
        records = Entrez.read(handle)
        handle.close()

        articles = []
        for article in records.get("PubmedArticle", []):
            try:
                medline_citation = article["MedlineCitation"]
                article_data = medline_citation["Article"]

                title = article_data.get("ArticleTitle", "No title")

                # Authors
                authors_list = article_data.get("AuthorList", [])
                authors_str = "Unknown"
                if authors_list:
                    first_author = authors_list[0]
                    last_name = first_author.get("LastName", "")
                    initials = first_author.get("Initials", "")
                    authors_str = f"{last_name} {initials} et al."

                # Journal
                journal_data = article_data.get("Journal", {})
                journal_title = journal_data.get("Title", "Unknown Journal")

                # Date
                pub_date = journal_data.get("JournalIssue", {}).get("PubDate", {})
                date_str = f"{pub_date.get('Month', '')} {pub_date.get('Year', '')}".strip()

                # Abstract
                abstract_list = article_data.get("Abstract", {}).get("AbstractText", [])
                abstract = " ".join([str(x) for x in abstract_list]) if abstract_list else "No abstract available"

                # PMID
                pmid = str(medline_citation.get("PMID", ""))

                articles.append({
                    "title": title,
                    "authors": authors_str,
                    "journal": journal_title,
                    "date": date_str,
                    "abstract": abstract,
                    "pmid": pmid,
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
                })

            except Exception as e:
                logger.error(f"Error parsing article: {e}", exc_info=True)
                continue

        return articles
