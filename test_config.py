#!/usr/bin/env python3
"""Quick configuration test"""
import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 Testing Configuration...\n")

required = {
    "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
    "PUBMED_EMAIL": os.getenv("PUBMED_EMAIL"),
    "SENDER_EMAIL": os.getenv("SENDER_EMAIL"),
    "SENDER_PASSWORD": os.getenv("SENDER_PASSWORD"),
    "RECIPIENT_EMAIL": os.getenv("RECIPIENT_EMAIL")
}

all_good = True
for key, value in required.items():
    if value and "your_" not in value and "example.com" not in value:
        print(f"✓ {key}: Configured")
    else:
        print(f"✗ {key}: Missing or invalid")
        all_good = False

if all_good:
    print("\n✅ All configuration looks good!")
    print("\nYou're ready to run: ./run.sh")
else:
    print("\n❌ Some configuration is missing")
