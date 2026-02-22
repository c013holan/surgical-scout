"""
AI Case Parser - Extracts structured clinical data from natural language case descriptions
Uses Claude API to intelligently parse surgical cases and generate optimized PubMed search terms
"""

import os
import logging
from typing import Dict, List
import anthropic
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class CaseExtraction(BaseModel):
    """Structured clinical data extracted from case description"""
    procedure: str
    patient_factors: List[str]
    timing: str
    search_terms: List[str]


class AICaseParser:
    """Parse natural language surgical case descriptions using Claude"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info("Initialized AI Case Parser with Claude API")
    
    def parse_case(self, case_description: str) -> CaseExtraction:
        """
        Parse natural language case description and extract structured clinical data
        
        Args:
            case_description: Natural language description of surgical case
            
        Returns:
            CaseExtraction object with structured data and optimized search terms
            
        Example:
            Input: "58F, DIEP flap, prior radiation, delayed reconstruction"
            Output: {
                "procedure": "DIEP flap breast reconstruction",
                "patient_factors": ["female", "58 years", "prior radiation therapy"],
                "timing": "delayed reconstruction",
                "search_terms": [
                    "DIEP flap radiation complications",
                    "delayed breast reconstruction postmastectomy radiation",
                    ...
                ]
            }
        """
        prompt = f"""You are an expert plastic surgeon and medical literature researcher. 

Analyze this surgical case description and extract structured clinical data:

CASE: {case_description}

Your task:
1. Identify the PRIMARY PROCEDURE/SURGERY TYPE
2. Extract PATIENT DEMOGRAPHICS and KEY FACTORS (age, sex, comorbidities, prior surgeries, anatomical variations)
3. Identify TIMING INDICATORS (immediate, delayed, revision, etc.)
4. Generate 4-6 OPTIMIZED PUBMED SEARCH TERMS that will find the most clinically relevant literature

For search terms:
- Combine procedure with key modifiers (e.g., "DIEP flap radiation complications")
- Include common medical synonyms (e.g., "autologous breast reconstruction")
- Focus on complications, outcomes, and technical considerations
- Use MeSH-like terminology that PubMed will recognize

Return ONLY valid JSON matching this exact structure:
{{
    "procedure": "Full procedural name",
    "patient_factors": ["factor 1", "factor 2", "factor 3"],
    "timing": "timing descriptor or 'not specified'",
    "search_terms": [
        "search term 1",
        "search term 2",
        "search term 3",
        "search term 4"
    ]
}}

CRITICAL: Return ONLY the JSON object. No markdown, no backticks, no explanations."""

        try:
            logger.info(f"Parsing case description: {case_description[:100]}...")
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                temperature=0.3,  # Lower temperature for more consistent extraction
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            response_text = response.content[0].text.strip()
            
            # Clean up response if needed
            if response_text.startswith("```json"):
                response_text = response_text[7:-3]
            elif response_text.startswith("```"):
                response_text = response_text[3:-3]
            
            # Parse into Pydantic model for validation
            import json
            data = json.loads(response_text)
            extraction = CaseExtraction(**data)
            
            logger.info(f"Successfully parsed case - Procedure: {extraction.procedure}")
            logger.info(f"Generated {len(extraction.search_terms)} search terms")
            
            return extraction
            
        except Exception as e:
            logger.error(f"Error parsing case description: {e}")
            # Return a fallback extraction
            return CaseExtraction(
                procedure=case_description,
                patient_factors=["Unable to extract specific factors"],
                timing="not specified",
                search_terms=[case_description]
            )


class AISummarizer:
    """Generate clinical summaries from PubMed abstracts using Claude"""
    
    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        
        self.client = anthropic.Anthropic(api_key=api_key)
        logger.info("Initialized AI Summarizer with Claude API")
    
    def generate_summary(self, articles: List[Dict], procedure: str) -> str:
        """
        Generate a 2-3 sentence clinical summary from PubMed abstracts
        
        Args:
            articles: List of article dictionaries with title, authors, abstract, etc.
            procedure: The surgical procedure being researched
            
        Returns:
            2-3 sentence clinical summary highlighting key findings
        """
        if not articles:
            return "No recent literature found for this procedure."
        
        # Format articles for Claude
        articles_text = ""
        for i, article in enumerate(articles[:10], 1):  # Limit to 10 articles
            articles_text += f"\n--- Article {i} ---\n"
            articles_text += f"Title: {article.get('title', 'N/A')}\n"
            articles_text += f"Authors: {article.get('authors', 'N/A')}\n"
            articles_text += f"Journal: {article.get('journal', 'N/A')}\n"
            articles_text += f"Date: {article.get('date', 'N/A')}\n"
            articles_text += f"Abstract: {article.get('abstract', 'N/A')}\n"
        
        prompt = f"""You are an expert plastic surgeon reviewing recent literature on {procedure}.

Analyze the abstracts below and create a 2-3 sentence CLINICAL SUMMARY that:
1. Highlights key complication rates or outcome data (with specific percentages/numbers)
2. Mentions important technical considerations or best practices
3. Notes any emerging trends or recent findings

Focus on ACTIONABLE information a surgeon would want to know before performing this procedure.

Be specific with numbers/percentages when available. Write in a clear, professional tone.

Return ONLY the 2-3 sentence summary. No preamble, no markdown, no section headers.

Articles to analyze:
{articles_text}"""

        try:
            logger.info(f"Generating clinical summary from {len(articles)} articles")
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=512,
                temperature=0.5,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            summary = response.content[0].text.strip()
            
            logger.info(f"Successfully generated summary: {summary[:100]}...")
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Unable to generate AI summary. Found {len(articles)} relevant articles on {procedure}."
    
    def generate_detailed_findings(self, articles: List[Dict], procedure: str) -> List[Dict]:
        """
        Generate one-line actionable takeaway for each article
        
        Args:
            articles: List of article dictionaries
            procedure: The surgical procedure being researched
            
        Returns:
            List of dictionaries with article info and one-sentence takeaway
        """
        if not articles:
            return []
        
        findings = []
        
        # Process articles to extract one key takeaway per article
        for article in articles[:8]:  # Limit to 8 most relevant articles
            try:
                prompt = f"""You are an expert plastic surgeon analyzing a research article on {procedure}.

Review this abstract and extract ONE KEY ACTIONABLE TAKEAWAY in a single sentence.

Article Title: {article.get('title', 'N/A')}
Authors: {article.get('authors', 'N/A')}
Abstract: {article.get('abstract', 'N/A')}

Write ONE sentence (max 150 characters) that captures the most important clinical finding or technique from this study. Focus on:
- Specific outcome data with numbers/percentages
- Novel techniques or technical modifications
- Key complications or prevention strategies
- Important patient selection criteria

If the abstract doesn't contain actionable clinical information, return: "SKIP"

Return ONLY the single sentence. No preamble, no explanation."""

                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=150,
                    temperature=0.3,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                
                takeaway = response.content[0].text.strip()
                
                # Skip if no actionable findings
                if "SKIP" not in takeaway:
                    findings.append({
                        "title": article.get('title', 'Unknown Title'),
                        "authors": article.get('authors', 'Unknown Authors'),
                        "journal": article.get('journal', 'Unknown Journal'),
                        "date": article.get('date', 'N/A'),
                        "url": article.get('url', ''),
                        "pmid": article.get('pmid', ''),
                        "takeaway": takeaway
                    })
                
            except Exception as e:
                logger.error(f"Error processing article {article.get('title', 'Unknown')[:50]}: {e}")
                continue
        
        logger.info(f"Generated {len(findings)} one-line takeaways")
        return findings
