import gspread
from oauth2client.service_account import ServiceAccountCredentials
import logging
from typing import List, Dict, Optional
from .models import SynthesisReport, VerdictStatus

# Configure logging
logger = logging.getLogger(__name__)

class SheetManager:
    """
    Manages interactions with the Aesthetic Intel Google Sheet.
    """
    
    SCOPE = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
    
    # Sheet ID from the user's URL
    SHEET_ID = "1I-RqLu07DHx1wzXLFUsN9Fl6UIs7tdgFQro7Vah9hYA"
    
    def __init__(self, key_file: str = "service_account.json"):
        try:
            logger.info(f"Attempting to connect with key file: {key_file}")
            creds = ServiceAccountCredentials.from_json_keyfile_name(key_file, self.SCOPE)
            self.client = gspread.authorize(creds)
            logger.info(f"Authorized. Opening sheet with ID: {self.SHEET_ID}")
            self.sheet = self.client.open_by_key(self.SHEET_ID).sheet1  # Assuming first sheet
            logger.info("Successfully connected to Google Sheet")
        except Exception as e:
            logger.error(f"Failed to connect to Google Sheet: {repr(e)}")
            raise e

    def get_procedures(self) -> List[Dict[str, int]]:
        """
        Reads all procedures from Column A.
        Returns a list of dicts with 'name' and 'row_index'.
        Row index is 1-based.
        """
        try:
            # Get all values in Column A (Procedure)
            procedures = self.sheet.col_values(1)
            
            # Skip header (Row 1)
            result = []
            for idx, proc in enumerate(procedures[1:], start=2):
                if proc.strip():
                    result.append({"name": proc.strip(), "row": idx})
            
            return result
        except Exception as e:
            logger.error(f"Error reading procedures: {e}")
            return []

    def update_procedure(self, row_idx: int, report: SynthesisReport):
        """
        Updates the specific row with synthesis data.
        
        Mapping based on User's Sheet:
        - Col E (5): "2026 Technique" -> Market Verdict
        - Col J (10): "Article Links" -> Top Articles
        """
        try:
            # 1. Format "2026 Technique" (Verdict)
            verdict_text = "No verdict available."
            if report.verdicts:
                v = report.verdicts[0]
                icon = "✅" if v.verdict == VerdictStatus.IN else "⚠️" if v.verdict == VerdictStatus.EVOLVING else "❌"
                verdict_text = f"{icon} {v.verdict.value.upper()}: {v.reasoning}"

            # 2. Format "Article Links"
            links_text = ""
            for art in report.articles[:3]:
                links_text += f"• {art.title} ({art.journal})\n  {art.url}\n\n"

            # 3. Update Cells
            # gspread uses (row, col) 1-based indexing
            self.sheet.update_cell(row_idx, 5, verdict_text) # Col E
            self.sheet.update_cell(row_idx, 10, links_text.strip()) # Col J
            
            logger.info(f"Updated row {row_idx} for {report.verdicts[0].topic if report.verdicts else 'Unknown'}")

        except Exception as e:
            logger.error(f"Error updating row {row_idx}: {e}")
            raise e
