"""
Surgical Scout Engine - PubMed search and AI-powered extraction
"""

import os
import logging
import ssl
import base64
import io
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from Bio import Entrez
import anthropic
import google.generativeai as genai
from PIL import Image
from pmc_fetcher import PMCFetcher
from unpaywall import UnpaywallClient
import browser_session

# Handle SSL certificate issues on corporate networks
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PubMedSearcher:
    """Handle PubMed searches using Biopython"""

    TARGET_JOURNALS = [
        "Plastic and Reconstructive Surgery",
        "Aesthetic Surgery Journal",
        "Journal of Plastic, Reconstructive & Aesthetic Surgery"
    ]

    def __init__(self, email: str):
        """
        Initialize PubMed searcher

        Args:
            email: Email for NCBI Entrez API (required by NCBI)
        """
        Entrez.email = email
        self.email = email
        logger.info(f"Initialized PubMed searcher with email: {email}")

    def search_pubmed(self, procedure_name: str, max_results: int = 5) -> List[Dict]:
        """
        Search PubMed for recent articles about a procedure

        Args:
            procedure_name: Surgical procedure to search for
            max_results: Maximum number of results to return

        Returns:
            List of dictionaries containing article information
        """
        try:
            # Calculate date range (last 24 months)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=730)  # ~24 months

            # Format dates for PubMed (YYYY/MM/DD)
            date_filter = f"{start_date.strftime('%Y/%m/%d')}:{end_date.strftime('%Y/%m/%d')}[DP]"

            # Build journal filter
            journal_filter = " OR ".join([f'"{journal}"[Journal]' for journal in self.TARGET_JOURNALS])

            # Construct search query
            search_query = f'({procedure_name}) AND ({journal_filter}) AND ({date_filter})'

            logger.info(f"Searching PubMed for: {procedure_name}")
            logger.debug(f"Query: {search_query}")

            # Search PubMed
            handle = Entrez.esearch(
                db="pubmed",
                term=search_query,
                retmax=max_results,
                sort="relevance"
            )
            search_results = Entrez.read(handle)
            handle.close()

            id_list = search_results.get("IdList", [])

            if not id_list:
                logger.warning(f"No results found for: {procedure_name}")
                return []

            logger.info(f"Found {len(id_list)} articles for {procedure_name}")

            # Fetch article details
            handle = Entrez.efetch(
                db="pubmed",
                id=id_list,
                rettype="abstract",
                retmode="xml"
            )
            records = Entrez.read(handle)
            handle.close()

            # Parse results
            articles = []
            for article in records.get("PubmedArticle", []):
                try:
                    medline_citation = article["MedlineCitation"]
                    article_data = medline_citation["Article"]

                    # Extract title
                    title = article_data.get("ArticleTitle", "No title available")

                    # Extract authors
                    authors = []
                    author_list = article_data.get("AuthorList", [])
                    for author in author_list[:3]:  # First 3 authors
                        last_name = author.get("LastName", "")
                        initials = author.get("Initials", "")
                        if last_name:
                            authors.append(f"{last_name} {initials}".strip())

                    author_str = ", ".join(authors)
                    if len(author_list) > 3:
                        author_str += " et al."
                    if not author_str:
                        author_str = "Authors not available"

                    # Extract journal
                    journal = article_data.get("Journal", {})
                    journal_title = journal.get("Title", "Unknown Journal")

                    # Extract publication date
                    pub_date = journal.get("JournalIssue", {}).get("PubDate", {})
                    year = pub_date.get("Year", "")
                    month = pub_date.get("Month", "")
                    date_str = f"{month} {year}".strip() if month and year else year
                    if not date_str:
                        date_str = "Date not available"

                    # Extract abstract
                    abstract_texts = article_data.get("Abstract", {}).get("AbstractText", [])
                    if isinstance(abstract_texts, list):
                        abstract = " ".join([str(text) for text in abstract_texts])
                    else:
                        abstract = str(abstract_texts) if abstract_texts else "No abstract available"

                    # Extract PMID
                    pmid = str(medline_citation.get("PMID", ""))

                    # Extract DOI
                    doi = None
                    article_ids = article.get("PubmedData", {}).get("ArticleIdList", [])
                    for article_id in article_ids:
                        if article_id.attributes.get("IdType") == "doi":
                            doi = str(article_id)
                            break

                    articles.append({
                        "title": title,
                        "authors": author_str,
                        "journal": journal_title,
                        "date": date_str,
                        "abstract": abstract,
                        "pmid": pmid,
                        "doi": doi
                    })

                except Exception as e:
                    logger.error(f"Error parsing article: {e}")
                    continue

            logger.info(f"Successfully parsed {len(articles)} articles")
            return articles

        except Exception as e:
            logger.error(f"Error searching PubMed for {procedure_name}: {e}")
            return []


class ClinicalPearlExtractor:
    """Extract clinical pearls using Claude"""

    def __init__(self, api_key: str):
        """
        Initialize Claude client

        Args:
            api_key: Anthropic API key
        """
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info("Initialized Claude client")

    def extract_pearls(self, abstracts: List[Dict], procedure_name: str) -> str:
        """
        Extract clinical pearls from abstracts using Claude

        Args:
            abstracts: List of article dictionaries
            procedure_name: Name of the surgical procedure

        Returns:
            HTML-formatted string with clinical pearls
        """
        if not abstracts:
            return "<p>No articles found in recent literature.</p>"

        try:
            # Format abstracts for Claude
            abstracts_text = ""
            for i, article in enumerate(abstracts, 1):
                abstracts_text += f"\n\n--- ARTICLE {i} ---\n"
                abstracts_text += f"Title: {article['title']}\n"
                abstracts_text += f"Authors: {article['authors']}\n"
                abstracts_text += f"Journal: {article['journal']}, {article['date']}\n"
                abstracts_text += f"PMID: {article['pmid']}\n"
                abstracts_text += f"Abstract: {article['abstract']}\n"

            # Create prompt
            prompt = f"""You are an expert plastic surgeon reviewing recent literature on {procedure_name}.

For each abstract below, identify if it contains:
- A NEW surgical technique or technical modification
- A NEW product, device, or material
- Important safety data or complication prevention strategies

If YES, extract a 2-3 sentence clinical pearl focusing on what's NEW and ACTIONABLE for a plastic surgery resident.
If NO (generic review, basic science with no clinical application, or no new insights), skip it.

Format each relevant finding as HTML:
<h3>{{Article Title}}</h3>
<p><strong>Authors:</strong> {{First author et al.}}<br>
<strong>Journal:</strong> {{Journal}}, {{Date}}<br>
<strong>Pearl:</strong> {{Your 2-3 sentence summary}}</p>
<p><a href='https://pubmed.ncbi.nlm.nih.gov/{{PMID}}'>View on PubMed</a></p>
<hr>

If no abstracts contain actionable updates, return only:
<p>No significant technique or product updates found in recent literature.</p>

Here are the abstracts to review:
{abstracts_text}"""

            logger.info(f"Sending {len(abstracts)} abstracts to Claude for {procedure_name}")

            # Call Claude
            message = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text
            logger.info(f"Successfully extracted pearls for {procedure_name}")

            return response_text

        except Exception as e:
            logger.error(f"Error extracting pearls for {procedure_name}: {e}")
            return f"<p>Error processing literature for {procedure_name}: {str(e)}</p>"


def search_pubmed(procedure_name: str) -> List[Dict]:
    """
    Convenience function to search PubMed

    Args:
        procedure_name: Surgical procedure to search for

    Returns:
        List of article dictionaries
    """
    email = os.getenv("PUBMED_EMAIL")
    if not email:
        raise ValueError("PUBMED_EMAIL not set in environment variables")

    searcher = PubMedSearcher(email)
    return searcher.search_pubmed(procedure_name)


def extract_pearls(abstracts: List[Dict], procedure_name: str) -> str:
    """
    Convenience function to extract clinical pearls

    Args:
        abstracts: List of article dictionaries
        procedure_name: Name of the surgical procedure

    Returns:
        HTML-formatted string with clinical pearls
    """
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set in environment variables")

    extractor = ClinicalPearlExtractor(api_key)
    return extractor.extract_pearls(abstracts, procedure_name)


def try_get_full_text(article: Dict, email: str, use_browser: bool = False) -> Optional[Tuple[str, str]]:
    """
    Try to get full-text PDF URL from multiple sources

    Args:
        article: Article dictionary with pmid and doi
        email: Email for API requests
        use_browser: If True, try browser session as fallback

    Returns:
        Tuple of (pdf_url, source) if found, None otherwise
        source can be 'PMC', 'Unpaywall', or 'Browser'
    """
    try:
        pmid = article.get('pmid')
        doi = article.get('doi')

        logger.info(f"Trying to get full text for PMID {pmid}")

        # Try PMC first (free, no auth needed, fastest)
        if pmid:
            logger.debug(f"Checking PMC for PMID {pmid}")
            pmc_fetcher = PMCFetcher(email)
            result = pmc_fetcher.get_full_text_url(pmid)

            if result:
                pdf_url, source = result
                logger.info(f"✓ Found full text via {source}")
                return (pdf_url, source)

        # Try Unpaywall (open access versions, fast)
        if doi:
            logger.debug(f"Checking Unpaywall for DOI {doi}")
            unpaywall_client = UnpaywallClient(email)
            pdf_url = unpaywall_client.get_oa_pdf(doi)

            if pdf_url:
                logger.info(f"✓ Found full text via Unpaywall")
                return (pdf_url, "Unpaywall")

        # Try browser session with Mayo access (slower but higher success rate)
        if use_browser and doi:
            logger.debug(f"Trying browser session for DOI {doi}")
            try:
                pdf_url = browser_session.get_pdf_via_browser(doi)

                if pdf_url:
                    logger.info(f"✓ Found full text via Browser session")
                    return (pdf_url, "Browser")
            except Exception as e:
                logger.warning(f"Browser session failed: {e}")

        logger.info(f"No full text available for PMID {pmid}")
        return None

    except Exception as e:
        logger.error(f"Error getting full text: {e}")
        return None


class FullTextAnalyzer:
    """Analyze full-text PDFs with figures using Google Gemini"""

    def __init__(self, api_key: str):
        """
        Initialize Gemini client

        Args:
            api_key: Google API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
        logger.info("Initialized Gemini Flash client for full-text analysis")

    def analyze_full_article(self, pdf_content: Dict, procedure_name: str) -> str:
        """
        Analyze full article with figures using Gemini

        Args:
            pdf_content: Dictionary with 'text' and 'figures' from pdf_processor
            procedure_name: Name of the surgical procedure

        Returns:
            HTML-formatted analysis with clinical pearls
        """
        try:
            full_text = pdf_content.get('text', '')
            figures = pdf_content.get('figures', [])

            if not full_text:
                logger.warning(f"No text content for {procedure_name}")
                return "<p>Unable to extract text from PDF.</p>"

            # Truncate text if too long (Gemini has limits)
            max_chars = 30000
            if len(full_text) > max_chars:
                logger.info(f"Truncating text from {len(full_text)} to {max_chars} chars")
                full_text = full_text[:max_chars] + "\n\n[Content truncated]"

            logger.info(f"Analyzing full article for {procedure_name} ({len(full_text)} chars, {len(figures)} figures)")

            # Create prompt
            prompt = f"""You are an expert plastic surgeon analyzing a full research article on {procedure_name}.

Analyze this complete article and provide:

1. **Clinical Pearl Summary** (2-3 sentences of the MOST actionable insight for a plastic surgery resident)

2. **Surgical Technique Guide** (if a new technique is described, provide step-by-step instructions)

3. **Key Figures Analysis** (describe what important figures show and why they matter clinically)

4. **Novel Findings** (what's NEW compared to standard practice - be specific)

5. **Safety Considerations** (complications, contraindications, patient selection)

Format your response as clean HTML suitable for email:
- Use <h3> for section headers
- Use <p> for paragraphs
- Use <strong> for emphasis
- Use <ul> and <li> for lists
- Use <hr> to separate major sections

Focus on ACTIONABLE information that would help a resident perform this procedure better.

Here is the full article text:

{full_text}
"""

            # Prepare content parts for Gemini
            content_parts = [prompt]

            # Add figures (convert base64 to PIL Images)
            added_figures = 0
            for i, fig in enumerate(figures[:8]):  # Limit to 8 figures for token efficiency
                try:
                    img_bytes = base64.b64decode(fig['data'])
                    pil_image = Image.open(io.BytesIO(img_bytes))

                    # Add figure with caption
                    content_parts.append(f"\n\nFigure {i+1}")
                    if fig.get('caption'):
                        content_parts.append(f"Caption: {fig['caption']}")
                    content_parts.append(pil_image)
                    added_figures += 1

                except Exception as e:
                    logger.warning(f"Could not add figure {i+1}: {e}")
                    continue

            logger.info(f"Sending to Gemini: {len(full_text)} chars + {added_figures} figures")

            # Call Gemini
            response = self.model.generate_content(content_parts)

            logger.info(f"Successfully analyzed full article for {procedure_name}")
            return response.text

        except Exception as e:
            logger.error(f"Error analyzing full article for {procedure_name}: {e}")
            return f"<p>Error processing full article: {str(e)}</p>"

    def analyze_multiple_articles(self, pdf_contents: List[Dict], procedure_name: str) -> str:
        """
        Analyze multiple full articles for a procedure

        Args:
            pdf_contents: List of PDF content dictionaries
            procedure_name: Name of the surgical procedure

        Returns:
            HTML-formatted combined analysis
        """
        if not pdf_contents:
            return "<p>No full-text articles available.</p>"

        results = []

        for i, pdf_content in enumerate(pdf_contents, 1):
            logger.info(f"Analyzing article {i}/{len(pdf_contents)} for {procedure_name}")

            # Get metadata if available
            metadata = pdf_content.get('metadata', {})
            title = metadata.get('title', f'Article {i}')

            analysis = self.analyze_full_article(pdf_content, procedure_name)

            # Wrap in article section
            article_html = f"""
            <div class="article-analysis">
                <h3>Article {i}: {title}</h3>
                {analysis}
            </div>
            <hr>
            """

            results.append(article_html)

        return "\n".join(results)


def analyze_full_text_articles(pdf_contents: List[Dict], procedure_name: str) -> str:
    """
    Convenience function to analyze full-text articles

    Args:
        pdf_contents: List of PDF content dictionaries
        procedure_name: Name of the surgical procedure

    Returns:
        HTML-formatted analysis
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_API_KEY not set, cannot perform full-text analysis")
        return "<p>Google API key not configured for full-text analysis.</p>"

    analyzer = FullTextAnalyzer(api_key)
    return analyzer.analyze_multiple_articles(pdf_contents, procedure_name)


if __name__ == "__main__":
    # Test the engine
    from dotenv import load_dotenv
    load_dotenv(override=True)

    print("Testing Surgical Scout Engine...\n")

    test_procedure = "Rhinoplasty"
    print(f"Searching for: {test_procedure}")

    articles = search_pubmed(test_procedure)
    print(f"\nFound {len(articles)} articles")

    if articles:
        print("\nFirst article:")
        print(f"  Title: {articles[0]['title']}")
        print(f"  Authors: {articles[0]['authors']}")
        print(f"  Journal: {articles[0]['journal']}")

        print("\nExtracting clinical pearls...")
        pearls = extract_pearls(articles, test_procedure)
        print("\nPearls extracted successfully!")
        print(f"Length: {len(pearls)} characters")
