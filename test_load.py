import os
from dotenv import load_dotenv

# Load from specific file
result = load_dotenv('.env')
print(f"load_dotenv returned: {result}")

key = os.getenv('ANTHROPIC_API_KEY')
if key:
    print(f"✓ Key loaded: {key[:20]}...{key[-10:]}")
else:
    print("✗ Key not found")
    
email = os.getenv('PUBMED_EMAIL')
print(f"PubMed email: {email}")
