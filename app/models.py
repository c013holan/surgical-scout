from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field

class VerdictStatus(str, Enum):
    IN = "In"
    OUT = "Out"
    EVOLVING = "Evolving"

class ArticleCard(BaseModel):
    title: str = Field(..., description="Title of the paper")
    authors: str = Field(..., description="Authors of the paper")
    journal: str = Field(..., description="Journal name (e.g., PRS, ASJ)")
    date: str = Field(..., description="Publication date")
    why: str = Field(..., description="Problem/Gap addressed")
    how: str = Field(..., description="Granular technique/device details")
    stats: str = Field(..., description="Key findings/stats (e.g., p-values, scores)")
    url: Optional[str] = Field(None, description="Link to the paper")

class MarketVerdict(BaseModel):
    topic: str = Field(..., description="The specific technique or product")
    verdict: VerdictStatus = Field(..., description="Is it In, Out, or Evolving?")
    reasoning: Optional[str] = Field(None, description="Short justification for the verdict")

class SynthesisReport(BaseModel):
    header: str = Field(..., description="Topic Name + Date of Report")
    articles: List[ArticleCard] = Field(..., description="Top 2-3 relevant papers")
    verdicts: List[MarketVerdict] = Field(..., description="Resident's Verdict table rows")
