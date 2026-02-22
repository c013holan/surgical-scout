#!/usr/bin/env python3
"""
Quick test to verify AI case parsing works with correct model
"""

import os
import sys
import ssl
import certifi
from dotenv import load_dotenv

# Fix SSL
os.environ["SSL_CERT_FILE"] = certifi.where()
ssl._create_default_https_context = ssl._create_unverified_context

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_parser import AICaseParser

load_dotenv()

print("=" * 80)
print("QUICK TEST: AI Case Parsing")
print("=" * 80)

# Test case
case = "58F, DIEP flap, prior radiation, delayed reconstruction"
print(f"\nInput: {case}\n")

try:
    parser = AICaseParser()
    extraction = parser.parse_case(case)
    
    print("✅ SUCCESS!\n")
    print(f"Procedure: {extraction.procedure}")
    print(f"Patient Factors: {', '.join(extraction.patient_factors)}")
    print(f"Timing: {extraction.timing}")
    print(f"\nSearch Terms ({len(extraction.search_terms)}):")
    for i, term in enumerate(extraction.search_terms, 1):
        print(f"  {i}. {term}")
    
    print("\n" + "=" * 80)
    print("✅ AI case parsing is working correctly!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
