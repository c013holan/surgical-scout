# Surgical Scout AI Enhancement

## 🎯 Overview

Surgical Scout now includes an **intelligent AI preprocessing layer** that makes PubMed searches significantly smarter and more clinically relevant.

## ✨ New Features

### 1. **AI Case Parser**
- Uses **Claude API** to parse natural language case descriptions
- Extracts structured clinical data:
  - Primary procedure/surgery type
  - Patient demographics (age, sex, comorbidities)
  - Key modifiers (complications, prior surgeries, anatomy variations)
  - Timing indicators (immediate, delayed, revision)
- Generates optimized PubMed search terms

### 2. **AI Reasoning Display**
- Shows extracted key concepts in the UI
- Displays AI-generated search queries
- Proves AI is adding value beyond keyword matching

### 3. **Enhanced PubMed Queries**
- Uses AI-generated search terms for better results
- Queries real NCBI E-utilities API (esearch + efetch)
- Returns real, verified PubMed links: `https://pubmed.ncbi.nlm.nih.gov/[PMID]/`

### 4. **AI Clinical Summary**
- Feeds 5-10 abstracts to Claude
- Generates 2-3 sentence clinical summary
- Highlights:
  - Complication rates and outcomes (with specific percentages)
  - Technical considerations and best practices
  - Emerging trends

## 🚀 Quick Start

### Installation

```bash
cd /Users/coleholan/Desktop/surgical-scout

# Install dependencies (if not already done)
pip install -r requirements.txt
```

### Running the Application

```bash
# Start the FastAPI backend
python -m uvicorn app.main:app --reload --port 8000
```

Then open `surgical-scout.html` in your browser (or serve it with a local web server).

## 🧪 Testing Cases

Use these cases to verify the AI enhancement:

1. **DIEP + Radiation**: "58F, DIEP flap, prior radiation, delayed reconstruction"
2. **Abdominoplasty**: "37F, abdominoplasty with progressive tension sutures, no drains"
3. **Revision Rhinoplasty**: "43M, revision rhinoplasty, dorsal over-resection, needs augmentation"

## 📋 Example Flow

### Input
```
58F, DIEP flap, prior radiation, delayed reconstruction
```

### AI Extraction
```json
{
  "procedure": "DIEP flap breast reconstruction",
  "patient_factors": [
    "female",
    "58 years",
    "prior radiation therapy"
  ],
  "timing": "delayed reconstruction",
  "search_terms": [
    "DIEP flap radiation complications",
    "delayed breast reconstruction postmastectomy radiation",
    "free flap radiated tissue",
    "microsurgery irradiated recipient vessels"
  ]
}
```

### AI Summary Example
```
Delayed DIEP reconstruction after radiation has complication rates of 15-25% 
vs 8-12% in non-radiated tissue. Recent studies suggest preoperative CTA imaging 
improves surgical planning. Longer pedicle dissection may be needed to reach 
beyond fibrotic zones.
```

## 🔧 Technical Architecture

### Backend (FastAPI)
- **Endpoint**: `POST /smart-search`
- **Request**: `{ "case_description": "..." }`
- **Response**: 
  ```json
  {
    "ai_extraction": { ... },
    "articles": [ ... ],
    "ai_summary": "..."
  }
  ```

### AI Services
- **`AICaseParser`**: Parses case descriptions using Claude 3.5 Sonnet
- **`AISummarizer`**: Generates clinical summaries using Claude 3.5 Sonnet
- **`PubMedSearcher`**: Queries NCBI E-utilities API

### Frontend
- Modern HTML5 + CSS3 + Vanilla JavaScript
- Dark theme with vibrant gradients
- Responsive design
- Smooth animations

## 🔑 Environment Variables

Required in `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-...
PUBMED_EMAIL=your-email@example.com
GOOGLE_API_KEY=AIza...  # For existing features
```

## 🎨 UI Features

- **Premium Design**: Dark theme with gradient accents
- **AI Reasoning Panel**: Shows extracted concepts and search terms
- **Clinical Summary**: Highlighted AI-generated insights
- **PubMed Results**: Clean article cards with real links
- **Example Cases**: Quick-load buttons for testing
- **Responsive**: Works on desktop, tablet, and mobile

## 📊 Smart Search vs. Dumb Search

### Dumb Keyword Search
```
Query: "DIEP flap prior radiation"
→ Limited results, may miss important terms
```

### Smart AI Search
```
Query: AI generates 4-6 optimized terms:
  - "DIEP flap radiation complications"
  - "delayed breast reconstruction postmastectomy radiation"
  - "free flap radiated tissue"
  - "microsurgery irradiated recipient vessels"
→ Comprehensive results with clinical relevance
```

## 🔍 API Endpoints

### `POST /smart-search`
Main endpoint for AI-powered search.

**Request:**
```json
{
  "case_description": "58F, DIEP flap, prior radiation, delayed reconstruction"
}
```

**Response:**
```json
{
  "ai_extraction": {
    "procedure": "DIEP flap breast reconstruction",
    "patient_factors": ["female", "58 years", "prior radiation therapy"],
    "timing": "delayed reconstruction",
    "search_terms": ["...", "..."]
  },
  "articles": [
    {
      "title": "Article title",
      "authors": "Smith J et al.",
      "journal": "Plastic and Reconstructive Surgery",
      "date": "Dec 2024",
      "abstract": "...",
      "pmid": "12345678",
      "url": "https://pubmed.ncbi.nlm.nih.gov/12345678/"
    }
  ],
  "ai_summary": "Clinical summary text..."
}
```

### `GET /generate-report`
Original endpoint for generating reports.

### `POST /sync-sheet`
Syncs with Google Sheets (existing feature).

## 🐛 Troubleshooting

### CORS Errors
If you see CORS errors in the browser console, make sure the backend is running and CORS is enabled (already configured).

### No Results
- Check that PubMed search terms are medically relevant
- Try broader time windows (months_back parameter)
- Verify PUBMED_EMAIL is set correctly

### API Key Errors
- Verify ANTHROPIC_API_KEY is valid and has credits
- Check .env file is in the correct directory

## 📝 Files Modified/Created

### New Files
- `surgical-scout.html` - Modern web interface
- `app/ai_parser.py` - AI case parser and summarizer

### Modified Files
- `app/main.py` - Added `/smart-search` endpoint and CORS

### Unchanged Files (Still Work)
- `scout.py` - Original command-line interface
- `engine.py` - PubMed search and extraction
- All other existing functionality

## 🎯 Success Criteria

✅ AI parsing visible in UI  
✅ Real PubMed results (links verified)  
✅ Clinical summary generated by AI  
✅ Clear demonstration of "smart search" vs "dumb keyword search"  
✅ Error handling for API failures  
✅ Clean, professional UI  

## 🚀 Next Steps

1. Open `surgical-scout.html` in a browser
2. Start the backend: `python -m uvicorn app.main:app --reload`
3. Try the example cases
4. Verify AI extraction and summaries make sense
5. Check that PubMed links work

## 📚 References

- [NCBI E-utilities API](https://www.ncbi.nlm.nih.gov/books/NBK25501/)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
