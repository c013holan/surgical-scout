import os
import logging
import json
import google.generativeai as genai
from typing import List, Dict, Any
from .models import SynthesisReport
from .pubmed import PubMedSearcher

# Configure logging
logger = logging.getLogger(__name__)

class PubMedIntelligenceService:
    def __init__(self):
        # Initialize PubMed Searcher
        self.pubmed = PubMedSearcher(email=os.getenv("PUBMED_EMAIL"))
        
        # Initialize Gemini
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')

    def generate_report(self, query: str, months_back: int = 18) -> SynthesisReport:
        """
        Orchestrates the pipeline: PubMed Search -> Gemini Synthesis -> Structured Report
        """
        # 1. Fetch Data
        articles = self.pubmed.search(query, months_back=months_back)
        
        if not articles:
            # Return empty report or handle gracefully
            return self._create_empty_report(query)

        # 2. Synthesize with Gemini
        synthesis_json = self._synthesize_with_llm(query, articles)
        
        # 3. Parse and Validate
        try:
            return SynthesisReport(**synthesis_json)
        except Exception as e:
            logger.error(f"Failed to parse LLM output: {e}")
            # Fallback or re-raise
            raise e

    def _synthesize_with_llm(self, query: str, articles: List[Dict]) -> Dict[str, Any]:
        """
        Sends abstracts to Gemini and requests a structured JSON response.
        """
        
        # Prepare context
        articles_context = ""
        for i, art in enumerate(articles, 1):
            articles_context += f"\n--- Article {i} ---\n"
            articles_context += f"Title: {art['title']}\n"
            articles_context += f"Authors: {art.get('authors', 'Unknown')}\n"
            articles_context += f"Journal: {art['journal']} ({art['date']})\n"
            articles_context += f"Abstract: {art['abstract']}\n"
            articles_context += f"URL: {art['url']}\n"

        prompt = f"""
        You are "The Aesthetic Intel Architect" - a surgical intelligence system for a Plastic Surgery Resident.
        
        Your Mission: Extract OR-READY INTEL from recent literature on "{query}".
        
        Input Data:
        {articles_context}
        
        Critical Instructions:
        You are NOT writing a literature review. You are providing ACTIONABLE INTELLIGENCE for tomorrow's OR.
        
        Focus on extracting:
        1. **NEW SURGICAL TECHNIQUES**: Novel incision patterns, procedural modifications, surgical approaches
           - Example: "L-shaped vs J-shaped breast reduction", "Dual-plane pocket dissection"
        
        2. **SPECIFIC PROTOCOLS**: Exact steps, settings, sequences that can be replicated
           - Example: "30-pass emulsification through 2.4→1.2mm connectors", "VASER at 60% power, 36kHz"
        
        3. **DEVICES & PRODUCTS**: Brand names, specific implants, mesh types, instruments
           - Example: "Allergan Inspira SRX 350cc", "TiLOOP Bra mesh", "Tulip GEMS connectors"
        
        4. **NOVEL APPLICATIONS**: New uses for existing techniques
           - Example: "Nanofat for skin quality (not volume)", "Mesh for lower pole support in revision"
        
        5. **OPTIMIZATION STRATEGIES**: How to get better outcomes with current techniques
           - Example: "Add PRP 10% v/v to improve retention", "Pre-op 3D imaging reduces revision rate"
        
        For each article card, the "how" field MUST include:
        - Exact technique/protocol (step-by-step if available)
        - Specific devices/products/settings
        - Patient selection criteria or contraindications
        
        The "stats" field MUST include:
        - Quantitative outcomes (retention %, complication rates, p-values)
        - Comparison to standard technique if available
        
        Output Format:
        Return ONLY valid JSON matching this schema:
        {{
            "header": "{query} Update - [Current Date]",
            "articles": [
                {{
                    "title": "Title of paper",
                    "authors": "First author et al.",
                    "journal": "Journal Name",
                    "date": "Pub Date",
                    "why": "What clinical problem does this solve? What's the innovation?",
                    "how": "SPECIFIC technique/protocol/device. Include: exact steps, settings, product names, contraindications.",
                    "stats": "Quantitative outcomes: retention %, complication %, p-values, comparison to standard.",
                    "url": "Link to paper"
                }}
            ],
            "verdicts": [
                {{
                    "topic": "{query}",
                    "verdict": "In" | "Out" | "Evolving",
                    "reasoning": "Is this ready for the OR? What's the evidence level?"
                }}
            ]
        }}
        
        CRITICAL: Return ONLY the JSON. No markdown, no backticks, no explanations.
        """
        
        response = self.model.generate_content(prompt)
        text_response = response.text.strip()
        
        # Clean up if the model adds backticks
        if text_response.startswith("```json"):
            text_response = text_response[7:-3]
        elif text_response.startswith("```"):
            text_response = text_response[3:-3]
            
        return json.loads(text_response)

    def _create_empty_report(self, query: str) -> SynthesisReport:
        from .models import MarketVerdict, VerdictStatus
        return SynthesisReport(
            header=f"{query} Update - No Recent Data",
            articles=[],
            verdicts=[
                MarketVerdict(
                    topic=query,
                    verdict=VerdictStatus.EVOLVING,
                    reasoning="No recent publications found in target journals."
                )
            ]
        )
