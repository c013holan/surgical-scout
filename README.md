# 🔍 Surgical Scout

An automated literature digest system that searches PubMed for recent articles about your upcoming surgical cases and emails you AI-extracted clinical pearls.

## Features

- 📚 **Automated PubMed Search**: Searches top plastic surgery journals for recent articles
- 🤖 **AI-Powered Extraction**: Uses Claude AI to identify actionable clinical pearls
- 📧 **Email Digests**: Sends formatted HTML summaries to your inbox
- ⚡ **Easy Setup**: Simple configuration and ready-to-use scripts
- 🔄 **Schedulable**: Set it and forget it with cron/Task Scheduler

## System Requirements

- Python 3.10 or higher
- Internet connection
- Gmail account (or other SMTP-compatible email)
- Anthropic API key (for Claude AI)

## Quick Start

### 1. Get Your API Keys

**Anthropic API Key:**
1. Go to https://console.anthropic.com/
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key and copy it

**Gmail Setup:**
- Follow the detailed instructions in `setup_gmail.md`
- You'll need to create a Gmail App Password (not your regular password)

### 2. Configure the System

Edit the `.env` file with your credentials:

```bash
# Anthropic API Configuration
ANTHROPIC_API_KEY=your_actual_api_key_here

# PubMed Configuration
PUBMED_EMAIL=your_email@example.com

# Email Configuration
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_gmail_app_password_here
RECIPIENT_EMAIL=your_email@gmail.com
```

### 3. Add Your Cases

Edit `cases.txt` with your upcoming procedures (one per line):

```
Breast Reduction
Rhinoplasty
DIEP Flap
Facelift
Abdominoplasty
```

Lines starting with `#` are comments and will be ignored.

### 4. Run It

**On macOS/Linux:**
```bash
chmod +x run.sh
./run.sh
```

**On Windows:**
```bash
python scout.py
```

## How It Works

1. **Reads Your Cases**: Loads procedures from `cases.txt`
2. **Searches PubMed**: For each procedure, searches these journals:
   - Plastic and Reconstructive Surgery
   - Aesthetic Surgery Journal
   - Journal of Plastic, Reconstructive & Aesthetic Surgery
3. **Filters by Date**: Only articles from the last 24 months
4. **Extracts Pearls**: Claude AI identifies:
   - New surgical techniques
   - New products/devices
   - Safety data and complication prevention
5. **Emails Summary**: Sends a formatted digest to your inbox

## Scheduling Daily Runs

### macOS/Linux (using cron)

1. Open your crontab:
   ```bash
   crontab -e
   ```

2. Add this line to run daily at 6 AM:
   ```
   0 6 * * * cd /Users/coleholan/Desktop/surgical-scout && ./run.sh >> surgical_scout_cron.log 2>&1
   ```

3. Save and exit

To check your scheduled jobs:
```bash
crontab -l
```

### Windows (using Task Scheduler)

1. Open Task Scheduler
2. Click "Create Basic Task"
3. Name it "Surgical Scout Daily Digest"
4. Set trigger to "Daily" at your preferred time
5. Action: "Start a program"
6. Program/script: `python`
7. Arguments: `scout.py`
8. Start in: `C:\Users\YourName\Desktop\surgical-scout`
9. Finish and test the task

## File Structure

```
surgical-scout/
├── README.md              # This file
├── setup_gmail.md         # Gmail setup instructions
├── requirements.txt       # Python dependencies
├── .env                   # Configuration (API keys, email)
├── cases.txt             # Your surgical cases
├── scout.py              # Main script
├── engine.py             # PubMed search & Claude extraction
├── email_sender.py       # Email functionality
├── run.sh                # Convenience run script
└── surgical_scout.log    # Log file (created on first run)
```

## Customization

### Change Search Journals

Edit `engine.py` and modify the `TARGET_JOURNALS` list:

```python
TARGET_JOURNALS = [
    "Plastic and Reconstructive Surgery",
    "Aesthetic Surgery Journal",
    "Your Favorite Journal Here"
]
```

### Change Date Range

Edit `engine.py` and modify the `search_pubmed` method:

```python
# Change from 24 months to 12 months
start_date = end_date - timedelta(days=365)
```

### Adjust Number of Articles

Edit `engine.py` and change the default `max_results`:

```python
def search_pubmed(self, procedure_name: str, max_results: int = 10):
```

### Use a Different AI Model

Edit `engine.py` and change the model in `extract_pearls`:

```python
# Use a more powerful model
model="claude-3-5-sonnet-20241022",
```

**Note**: Sonnet models cost more but provide better analysis.

## Troubleshooting

### No Email Received

1. Check spam/junk folder
2. Verify `.env` configuration is correct
3. Run the test: `python email_sender.py`
4. Check `surgical_scout.log` for errors

### Authentication Errors

- Make sure you're using a Gmail **App Password**, not your regular password
- Verify 2FA is enabled on your Gmail account
- See `setup_gmail.md` for detailed instructions

### No Articles Found

- Check that procedure names in `cases.txt` are spelled correctly
- Try broader terms (e.g., "Breast Surgery" instead of "Wise Pattern Reduction")
- Check `surgical_scout.log` to see the actual search query

### API Key Errors

- Verify your Anthropic API key is correct in `.env`
- Check you have credits at https://console.anthropic.com/
- Ensure there are no extra spaces in the `.env` file

### Python Not Found

Install Python 3.10+:
- **macOS**: `brew install python@3.10`
- **Windows**: Download from https://www.python.org/
- **Linux**: `sudo apt install python3.10`

## Cost Estimates

- **PubMed API**: Free
- **Claude AI (Haiku)**: ~$0.001 per procedure (extremely cheap)
- **Email**: Free with Gmail

**Example**: 5 procedures per day = ~$0.15/month

## Privacy & Data

- Your cases list stays on your computer
- PubMed searches are logged by NCBI (standard practice)
- Article abstracts are sent to Claude API for analysis
- No data is stored by Surgical Scout beyond the log file

## Tips for Best Results

1. **Use specific procedure names**: "Rhinoplasty" is better than "Nose surgery"
2. **Check cases.txt regularly**: Keep it updated with your actual schedule
3. **Read the full articles**: The digest is a starting point, not a replacement
4. **Adjust the prompt**: Edit `engine.py` to focus on what matters to you
5. **Schedule wisely**: Run it the night before your cases, not months in advance

## Support & Contributions

This is a personal tool designed for educational and research purposes.

**Found a bug?** Check the log file first:
```bash
cat surgical_scout.log
```

**Want to add a feature?** The code is well-commented and modular:
- `engine.py` - Search and extraction logic
- `email_sender.py` - Email functionality
- `scout.py` - Main workflow orchestration

## Legal & Ethical Notes

- This tool is for **personal educational use**
- Always verify clinical information before applying to patient care
- PubMed usage complies with NCBI guidelines
- Claude AI usage complies with Anthropic's terms of service
- Email automation complies with Gmail's terms of service

## License

MIT License - Free to use, modify, and distribute.

## Changelog

**Version 1.0** (Initial Release)
- PubMed search across 3 major plastic surgery journals
- Claude AI extraction of clinical pearls
- HTML email digest
- Automated scheduling support
- Comprehensive error handling and logging

---

**Built with ❤️ for surgical residents and attending surgeons who want to stay current without drowning in literature.**
