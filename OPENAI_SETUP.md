# OpenAI API Setup Guide

The system now uses OpenAI's GPT-4o-mini model instead of Anthropic's Claude. GPT-4o-mini is very cost-effective and works great for extracting clinical pearls.

## Cost Comparison

**OpenAI GPT-4o-mini:**
- Input: $0.15 per 1M tokens
- Output: $0.60 per 1M tokens
- **Estimated cost per procedure: ~$0.001-0.002**
- **Monthly cost (5 procedures daily): ~$0.15-0.30**

This is similar to Claude Haiku pricing and very affordable.

---

## Step 1: Get Your OpenAI API Key

1. Go to https://platform.openai.com/
2. Sign up or log in to your account
3. Click on your profile picture (top right)
4. Select **"API keys"** or go directly to https://platform.openai.com/api-keys
5. Click **"Create new secret key"**
6. Give it a name like "Surgical Scout"
7. Copy the key (starts with `sk-proj-` or `sk-`)
   - **Important:** You can only see this key once! Save it now.

---

## Step 2: Add Credits to Your Account

OpenAI requires prepaid credits:

1. Go to https://platform.openai.com/settings/organization/billing
2. Click **"Add payment method"**
3. Add a credit card
4. Click **"Add to credit balance"**
5. Add at least **$5** (this will last months for this application)

**Note:** OpenAI has usage limits for new accounts. If you just created your account, you may need to wait or add more credits.

---

## Step 3: Update Your .env File

Open `/Users/coleholan/Desktop/surgical-scout/.env` and replace the placeholder with your actual key:

```bash
OPENAI_API_KEY=sk-proj-your-actual-key-here
PUBMED_EMAIL=holan.cole@mayo.edu
SENDER_EMAIL=caholan17@gmail.com
SENDER_PASSWORD=lsoy wxjw ksmk kenc
RECIPIENT_EMAIL=holan.cole@mayo.edu
```

---

## Step 4: Install New Dependencies

The system now uses the OpenAI Python library instead of Anthropic:

```bash
cd /Users/coleholan/Desktop/surgical-scout
source venv/bin/activate
pip install openai
```

Or just run the system (it will auto-install):
```bash
./run.sh
```

---

## Step 5: Test It

Run the system:
```bash
cd /Users/coleholan/Desktop/surgical-scout
./run.sh
```

You should see:
```
[1/3] Scouting: Breast Reduction...
    └─ Searching PubMed...
    └─ Found 5 articles
    └─ Extracting clinical pearls with OpenAI...
    └─ ✓ Complete
```

---

## Troubleshooting

### "Rate limit exceeded"
- You've hit OpenAI's rate limit (common for new accounts)
- Wait a few minutes and try again
- Add more credits to your account

### "Insufficient credits"
- Add more credits at https://platform.openai.com/settings/organization/billing
- Minimum recommended: $5

### "Invalid API key"
- Check that you copied the entire key
- Make sure there are no spaces at the beginning or end
- Verify the key starts with `sk-proj-` or `sk-`

### "Model not found" or "Model access denied"
- Your account may not have access to GPT-4o-mini yet
- The system will automatically fall back to gpt-3.5-turbo if needed
- Contact OpenAI support if the issue persists

---

## Model Options

The default model is **gpt-4o-mini** (fast, cheap, good quality).

If you want to use a different model, edit `engine.py` line ~239:

```python
# Current (default):
model="gpt-4o-mini",

# Alternatives:
model="gpt-4o",           # More powerful, ~10x more expensive
model="gpt-3.5-turbo",    # Cheaper, slightly lower quality
```

---

## Why OpenAI Instead of Claude?

- **More accessible:** Easier to get API access
- **Similar cost:** Both ~$0.001-0.002 per procedure
- **Great quality:** GPT-4o-mini is excellent for this task
- **Reliable:** Stable API with good uptime

---

## Need Help?

Check the log file for detailed error messages:
```bash
cat /Users/coleholan/Desktop/surgical-scout/surgical_scout.log
```

---

**Once you have your OpenAI API key, you're ready to run Surgical Scout!**
