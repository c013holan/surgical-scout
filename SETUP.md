# Surgical Scout - Setup Guide

## One-Time Setup: Mayo Library Access

To enable full-text access (60-80% coverage), you need to log into Mayo's library portal once in Chrome:

### Steps:

1. **Open Chrome** (the default browser on your Mac)

2. **Visit any journal article** that requires Mayo access, for example:
   - https://journals.lww.com/plasreconsurg/ (Plastic and Reconstructive Surgery)
   - Or search for any PRS article on PubMed and click "Full text"

3. **Log in with your Mayo credentials** when prompted
   - Use your Mayo username: holan.cole@mayo.edu
   - Use your Mayo password

4. **Verify you can access the full article**
   - You should see the full article text and PDF download button
   - If you see "Access Denied", you may need to be on Mayo VPN

5. **Keep Chrome as your default browser**
   - The system will reuse your saved login session automatically
   - No need to close Chrome - keep it open normally

### How It Works

The system uses a **3-tier fallback strategy** for maximum coverage:

1. **PMC (PubMed Central)** - Free full-text articles (~30% coverage)
   - No login needed
   - Completely automated

2. **Unpaywall** - Open access versions (~10-20% additional coverage)
   - No login needed
   - Finds legal OA versions from repositories

3. **Browser Session** - Mayo institutional access (~30-40% additional coverage)
   - Uses your Chrome login automatically
   - No ADFS automation - just reuses your existing session
   - Works as long as you stay logged into Mayo in Chrome

**Total Expected Coverage: 60-80% full-text access**

### Session Management

- **Session duration**: Your Mayo login typically lasts 24 hours
- **Re-authentication**: Just log back into Mayo in Chrome when it expires
- **No manual steps during runs**: Once you're logged in, the system handles everything automatically

### Troubleshooting

**If browser session fails:**
- The system will gracefully fall back to free sources only
- You'll see a warning: "Browser session unavailable"
- Articles will still be analyzed using abstracts

**If you see Chrome profile warnings:**
- Close all Chrome windows before running
- Or run with Chrome open (the system handles both cases)

**If Mayo login expires:**
- Just log back into any Mayo journal in Chrome
- Run the script again

### Privacy & Security

- The system only reads cookies from your Chrome profile
- No passwords are stored or transmitted
- Your Mayo credentials remain secure in Chrome's keychain
- The system never modifies your browsing history or settings

## Running the System

Once setup is complete:

```bash
cd /Users/coleholan/Desktop/surgical-scout
python3 scout.py
```

The system will:
1. Try PMC (fast, free)
2. Try Unpaywall (fast, free)
3. Try Browser session with Mayo access (slower but high success)
4. Fall back to abstracts if no full text available

## What You'll Get

### Full-Text Articles (via Gemini Flash)
- Complete article text analysis
- Figures and diagrams included
- Step-by-step surgical technique guides
- Novel findings vs standard practice
- Safety considerations and contraindications

### Abstract-Only Articles (via Claude Haiku)
- Clinical pearls from abstracts
- New techniques and products
- Safety data

## Cost

- **Full-text articles**: ~3-4¢ per article (Gemini Flash)
- **Abstract-only**: ~0.1¢ per article (Claude Haiku)
- **Typical daily run**: $0.05-0.15
- **Monthly cost**: ~$1.50-4.50

Much cheaper than the original Claude Sonnet approach!

## Tips for Best Results

1. **Keep Chrome logged into Mayo** for maximum coverage
2. **Run daily** to stay current with new literature
3. **Add/remove procedures** in cases.txt as your schedule changes
4. **Check your email** for the digest each morning

## Support

If you encounter issues:
1. Check surgical_scout.log for detailed error messages
2. Verify your Mayo login is active in Chrome
3. Ensure all environment variables are set in .env
4. Try running with just free sources to isolate browser issues
