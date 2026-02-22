# Quick Start Guide

Get Surgical Scout running in 5 minutes!

## Step 1: Get Your OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Give it a name like "Surgical Scout"
5. Copy the key (starts with `sk-proj-` or `sk-`)
6. Add credits: https://platform.openai.com/settings/organization/billing (minimum $5)

See `OPENAI_SETUP.md` for detailed instructions.

## Step 2: Set Up Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable "2-Step Verification" if not already enabled
3. Go back to Security → 2-Step Verification
4. Scroll to bottom and click "App passwords"
5. Select app: **Mail**, device: **Other (Custom name)**
6. Enter "Surgical Scout" and click Generate
7. Copy the 16-character password

See `setup_gmail.md` for detailed instructions.

## Step 3: Configure .env File

Open `.env` and fill in your credentials:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
PUBMED_EMAIL=your.email@gmail.com
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=abcd efgh ijkl mnop
RECIPIENT_EMAIL=your.email@gmail.com
```

## Step 4: Edit cases.txt

Add your upcoming procedures (one per line):

```
Breast Reduction
Rhinoplasty
DIEP Flap
```

## Step 5: Run It!

```bash
./run.sh
```

That's it! Check your email for the digest.

## Test Individual Components

**Test PubMed search:**
```bash
python engine.py
```

**Test email sender:**
```bash
python email_sender.py
```

## Common Issues

**"python3: command not found"**
- Install Python 3.10+: https://www.python.org/

**"Authentication failed"**
- Make sure you're using Gmail App Password, not regular password
- Check `setup_gmail.md` for help

**"No module named 'Bio'"**
- Run: `./run.sh` (it installs dependencies automatically)

**"No articles found"**
- Check spelling in cases.txt
- Try broader terms (e.g., "Rhinoplasty" not "Open Septorhinoplasty")

## What Happens When You Run It?

1. Creates virtual environment (first run only)
2. Installs dependencies (first run only)
3. Searches PubMed for each procedure
4. Sends abstracts to Claude AI
5. Extracts clinical pearls
6. Emails you a formatted digest

## Cost

- PubMed: FREE
- Claude Haiku: ~$0.001 per procedure
- Gmail: FREE

**Example:** 5 procedures = $0.005 per run (~$0.15/month daily)

## Next Steps

- Read `README.md` for full documentation
- Set up daily automation (see README.md → "Scheduling Daily Runs")
- Customize search parameters (see README.md → "Customization")

## Need Help?

Check the log file:
```bash
cat surgical_scout.log
```

---

**Ready to stay current with surgical literature? Run `./run.sh` now!**
