import os

# Read .env file directly
with open('.env', 'r') as f:
    for i, line in enumerate(f, 1):
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            key, value = line.split('=', 1)
            print(f"Line {i}: key='{key}', value_len={len(value)}")
            if 'ANTHROPIC' in key:
                print(f"  -> ANTHROPIC key found: {value[:30]}...")

# Now try dotenv
from dotenv import load_dotenv
load_dotenv('.env')

key = os.getenv('ANTHROPIC_API_KEY')
print(f"\nAfter dotenv: {key[:20] if key else 'NOT FOUND'}")

# Try all matching keys
anthropic_keys = {k: v for k, v in os.environ.items() if 'ANTHROPIC' in k.upper()}
print(f"All ANTHROPIC vars: {list(anthropic_keys.keys())}")
