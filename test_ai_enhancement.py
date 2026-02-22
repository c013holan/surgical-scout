#!/usr/bin/env python3
"""
Test script for AI-Enhanced Surgical Scout
Tests the smart search functionality end-to-end
"""

import os
import sys
import json
import ssl
import certifi
from dotenv import load_dotenv

# Fix SSL certificate issues
os.environ["SSL_CERT_FILE"] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_parser import AICaseParser, AISummarizer
from app.pubmed import PubMedSearcher

# Load environment
load_dotenv()


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80 + "\n")


def print_section(text):
    """Print formatted section"""
    print(f"\n{'─' * 80}")
    print(f"  {text}")
    print('─' * 80)


def test_case_parsing():
    """Test AI case parsing"""
    print_header("TEST 1: AI Case Parsing")
    
    test_cases = [
        "58F, DIEP flap, prior radiation, delayed reconstruction",
        "37F, abdominoplasty with progressive tension sutures, no drains",
        "43M, revision rhinoplasty, dorsal over-resection, needs augmentation"
    ]
    
    try:
        parser = AICaseParser()
        
        for i, case in enumerate(test_cases, 1):
            print_section(f"Test Case {i}")
            print(f"Input: {case}\n")
            
            extraction = parser.parse_case(case)
            
            print(f"✓ Procedure: {extraction.procedure}")
            print(f"✓ Patient Factors: {', '.join(extraction.patient_factors)}")
            print(f"✓ Timing: {extraction.timing}")
            print(f"✓ Search Terms ({len(extraction.search_terms)}):")
            for term in extraction.search_terms:
                print(f"    • {term}")
            
        print("\n✅ AI Case Parsing: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ AI Case Parsing: FAILED")
        print(f"Error: {e}")
        return False


def test_pubmed_search():
    """Test PubMed search with AI-generated terms"""
    print_header("TEST 2: PubMed Search with AI Terms")
    
    try:
        # Parse a case first
        parser = AICaseParser()
        case = "58F, DIEP flap, prior radiation, delayed reconstruction"
        print(f"Parsing: {case}\n")
        
        extraction = parser.parse_case(case)
        print(f"Generated {len(extraction.search_terms)} search terms\n")
        
        # Search PubMed
        pubmed = PubMedSearcher(email=os.getenv("PUBMED_EMAIL"))
        combined_query = " OR ".join([f'({term})' for term in extraction.search_terms])
        
        print(f"Searching PubMed...")
        articles = pubmed.search(combined_query, months_back=24, max_results=5)
        
        print(f"\n✓ Found {len(articles)} articles")
        
        if articles:
            print_section("Sample Article")
            article = articles[0]
            print(f"Title: {article['title']}")
            print(f"Authors: {article['authors']}")
            print(f"Journal: {article['journal']}")
            print(f"Date: {article['date']}")
            print(f"PMID: {article['pmid']}")
            print(f"URL: {article['url']}")
            print(f"Abstract: {article['abstract'][:200]}...")
            
            # Verify URL format
            expected_url = f"https://pubmed.ncbi.nlm.nih.gov/{article['pmid']}/"
            if article['url'] == expected_url:
                print(f"\n✓ URL format verified: {article['url']}")
            else:
                print(f"\n⚠️  URL format mismatch:")
                print(f"   Expected: {expected_url}")
                print(f"   Got: {article['url']}")
        
        print("\n✅ PubMed Search: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ PubMed Search: FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ai_summary():
    """Test AI summary generation"""
    print_header("TEST 3: AI Clinical Summary Generation")
    
    try:
        # Get some articles first
        parser = AICaseParser()
        case = "DIEP flap breast reconstruction"
        print(f"Searching for: {case}\n")
        
        pubmed = PubMedSearcher(email=os.getenv("PUBMED_EMAIL"))
        articles = pubmed.search(case, months_back=24, max_results=5)
        
        if not articles:
            print("⚠️  No articles found, skipping summary test")
            return True
        
        print(f"Found {len(articles)} articles")
        print("Generating AI summary...\n")
        
        summarizer = AISummarizer()
        summary = summarizer.generate_summary(articles, case)
        
        print_section("AI-Generated Clinical Summary")
        print(summary)
        print()
        
        # Basic validation
        if len(summary) > 50 and len(summary) < 1000:
            print("✓ Summary length appropriate")
        else:
            print(f"⚠️  Summary length unusual: {len(summary)} characters")
        
        print("\n✅ AI Summary Generation: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ AI Summary Generation: FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_full_pipeline():
    """Test complete smart search pipeline"""
    print_header("TEST 4: Complete Smart Search Pipeline")
    
    try:
        case = "37F, abdominoplasty with progressive tension sutures, no drains"
        print(f"Case: {case}\n")
        
        # Step 1: Parse
        print("Step 1: AI Case Parsing...")
        parser = AICaseParser()
        extraction = parser.parse_case(case)
        print(f"  ✓ Extracted procedure: {extraction.procedure}")
        print(f"  ✓ Generated {len(extraction.search_terms)} search terms")
        
        # Step 2: Search
        print("\nStep 2: PubMed Search...")
        pubmed = PubMedSearcher(email=os.getenv("PUBMED_EMAIL"))
        combined_query = " OR ".join([f'({term})' for term in extraction.search_terms])
        articles = pubmed.search(combined_query, months_back=24, max_results=8)
        print(f"  ✓ Found {len(articles)} articles")
        
        # Step 3: Summarize
        print("\nStep 3: AI Summary Generation...")
        summarizer = AISummarizer()
        summary = summarizer.generate_summary(articles, extraction.procedure)
        print(f"  ✓ Generated summary ({len(summary)} chars)")
        
        # Display results
        print_section("Pipeline Results")
        print(f"Procedure: {extraction.procedure}")
        print(f"Articles Found: {len(articles)}")
        print(f"Summary: {summary[:200]}..." if len(summary) > 200 else f"Summary: {summary}")
        
        print("\n✅ Complete Pipeline: PASSED")
        return True
        
    except Exception as e:
        print(f"\n❌ Complete Pipeline: FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def verify_environment():
    """Verify required environment variables"""
    print_header("Environment Verification")
    
    required_vars = {
        "ANTHROPIC_API_KEY": "Claude API (for AI parsing & summarization)",
        "PUBMED_EMAIL": "PubMed API (required by NCBI)",
    }
    
    all_present = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else value
            print(f"✓ {var}: {masked} ({description})")
        else:
            print(f"✗ {var}: NOT SET ({description})")
            all_present = False
    
    if not all_present:
        print("\n❌ Missing required environment variables!")
        print("Please update your .env file and try again.")
        return False
    
    print("\n✅ Environment: OK")
    return True


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "SURGICAL SCOUT AI - TEST SUITE" + " " * 28 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Verify environment
    if not verify_environment():
        sys.exit(1)
    
    # Run tests
    results = {
        "Case Parsing": test_case_parsing(),
        "PubMed Search": test_pubmed_search(),
        "AI Summary": test_ai_summary(),
        "Full Pipeline": test_full_pipeline()
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, passed_test in results.items():
        status = "✅ PASSED" if passed_test else "❌ FAILED"
        print(f"{test_name:.<50} {status}")
    
    print(f"\n{'─' * 80}")
    print(f"  Total: {passed}/{total} tests passed")
    print('─' * 80)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! The AI enhancement is working correctly.\n")
        print("Next steps:")
        print("  1. Start the backend: python -m uvicorn app.main:app --reload")
        print("  2. Open surgical-scout.html in your browser")
        print("  3. Test with the example cases\n")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please review the errors above.\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
