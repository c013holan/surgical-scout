import os
import ssl
import certifi
import logging
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict

# Configure logging
logger = logging.getLogger(__name__)

# MAC OS SSL FIX for Biopython which uses urllib
os.environ["SSL_CERT_FILE"] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

from .models import SynthesisReport
from .services import PubMedIntelligenceService
from .sheets import SheetManager
from .utils import generate_markdown
from .pubmed import PubMedSearcher
from .ai_parser import AICaseParser, AISummarizer
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="The Aesthetic Intel Architect", version="1.0.0")

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response models for smart search
class SmartSearchRequest(BaseModel):
    case_description: str


class SmartSearchResponse(BaseModel):
    ai_extraction: Dict
    articles: List[Dict]
    ai_summary: str
    detailed_findings: List[Dict]  # Article-by-article actionable insights

# Initialize service
service = PubMedIntelligenceService()

@app.get("/")
def read_root():
    return {"message": "Aesthetic Intel Architect is running."}

@app.get("/generate-report", response_model=SynthesisReport)
def generate_report(query: str = Query(..., description="Topic to search for, e.g., 'Nanofat'"), 
                    months_back: int = 18):
    """
    Generates a structured report on the given topic using PubMed + Gemini.
    """
    try:
        report = service.generate_report(query, months_back)
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/generate-report/markdown", response_class=PlainTextResponse)
def generate_report_markdown(query: str = Query(..., description="Topic to search for"), months_back: int = 18):
    """
    Generates the report and returns it as a formatted Markdown string.
    """
    try:
        report = service.generate_report(query, months_back)
        return generate_markdown(report)
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/sync-sheet")
def sync_sheet(limit: int = 5):
    """
    Reads procedures from the Google Sheet, generates reports, and updates the sheet.
    Limit controls how many procedures to process to avoid timeouts.
    """
    try:
        # Initialize Sheet Manager
        sheet_manager = SheetManager()
        procedures = sheet_manager.get_procedures()
        
        results = []
        for item in procedures[:limit]:
            proc_name = item["name"]
            row_idx = item["row"]
            
            # Generate Report
            try:
                report = service.generate_report(proc_name)
                
                # Update Sheet
                sheet_manager.update_procedure(row_idx, report)
                results.append(f"Updated {proc_name}")
                
            except Exception as e:
                results.append(f"Failed {proc_name}: {e}")
                
        return {"status": "completed", "results": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/smart-search", response_model=SmartSearchResponse)
def smart_search(request: SmartSearchRequest):
    """
    AI-Powered Smart Search:
    1. Parse case description with AI to extract structured data
    2. Generate optimized PubMed search terms
    3. Search PubMed using AI-generated terms
    4. Generate clinical summary from results
    
    This is the main endpoint for the enhanced Surgical Scout UI.
    """
    try:
        case_description = request.case_description.strip()
        
        if not case_description:
            raise HTTPException(status_code=400, detail="Case description cannot be empty")
        
        # Step 1: AI Case Parsing
        logger.info(f"Step 1: Parsing case with AI - {case_description[:50]}...")
        parser = AICaseParser()
        extraction = parser.parse_case(case_description)
        
        # Step 2: Search PubMed with AI-generated terms
        logger.info(f"Step 2: Searching PubMed with {len(extraction.search_terms)} AI-generated terms")
        pubmed = PubMedSearcher(email=os.getenv("PUBMED_EMAIL"))
        
        # Combine all search terms with OR to get comprehensive results
        combined_query = " OR ".join([f'({term})' for term in extraction.search_terms])
        articles = pubmed.search(combined_query, months_back=24, max_results=10)
        
        logger.info(f"Found {len(articles)} articles from PubMed")
        
        # Step 3: Generate AI Clinical Summary and Detailed Findings
        logger.info("Step 3: Generating AI clinical summary and detailed findings")
        summarizer = AISummarizer()
        ai_summary = summarizer.generate_summary(articles, extraction.procedure)
        detailed_findings = summarizer.generate_detailed_findings(articles, extraction.procedure)
        
        logger.info(f"Generated summary and {len(detailed_findings)} detailed article insights")
        
        # Return structured response
        return SmartSearchResponse(
            ai_extraction=extraction.dict(),
            articles=articles,
            ai_summary=ai_summary,
            detailed_findings=detailed_findings
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in smart search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Smart search failed: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

