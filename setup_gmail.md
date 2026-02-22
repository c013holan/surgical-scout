# Gmail Setup Guide for Surgical Scout

This guide will help you set up Gmail to work with Surgical Scout's email functionality.

## Important Note

Gmail no longer allows apps to sign in using your regular password. You must use an **App Password** instead.

## Prerequisites

- A Gmail account
- Two-factor authentication (2FA) enabled on your Google account

---

## Step 1: Enable Two-Factor Authentication

If you don't already have 2FA enabled:

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google," click on **2-Step Verification**
4. Follow the prompts to set up 2FA using your phone

---

## Step 2: Create a Gmail App Password

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google," click on **2-Step Verification**
4. Scroll down and click on **App passwords** (at the bottom)
   - If you don't see this option, make sure 2FA is fully enabled
5. You may need to sign in again
6. In the "Select app" dropdown, choose **Mail**
7. In the "Select device" dropdown, choose **Other (Custom name)**
8. Type "Surgical Scout" as the name
9. Click **Generate**
10. Google will display a 16-character password (with spaces)
11. **Copy this password** - you'll need it for the next step

---

## Step 3: Update Your .env File

1. Open the `.env` file in the surgical-scout folder
2. Update these three fields:

```bash
# Your Gmail address (the one you just created the App Password for)
SENDER_EMAIL=your.email@gmail.com

# The 16-character App Password (you can include or remove spaces)
SENDER_PASSWORD=abcd efgh ijkl mnop

# Where you want to receive the digest (usually the same as SENDER_EMAIL)
RECIPIENT_EMAIL=your.email@gmail.com
```

3. Save the file

---

## Step 4: Test the Email System

Run this test command from the surgical-scout directory:

```bash
python email_sender.py
```

You should receive a test email within a few seconds.

---

## Troubleshooting

### "Authentication failed" error

- Double-check that you copied the App Password correctly
- Make sure there are no extra spaces at the beginning or end
- Verify that 2FA is enabled on your Google account
- Try generating a new App Password

### "Connection refused" error

- Check your internet connection
- Verify that your firewall isn't blocking port 587
- Make sure you're not on a corporate network that blocks SMTP

### Email not arriving

- Check your spam/junk folder
- Verify the RECIPIENT_EMAIL is correct in your .env file
- Look at the console output for any error messages
- Check the `surgical_scout.log` file for detailed error information

### "App passwords" option not visible

- Ensure 2FA is fully enabled and working
- Wait a few minutes after enabling 2FA
- Try signing out and back into your Google account
- Some organizational/school Google accounts may have this disabled by administrators

---

## Security Best Practices

1. **Never share your App Password** - treat it like a regular password
2. **Don't commit .env to version control** - it's already in .gitignore
3. **Revoke unused App Passwords** - if you stop using Surgical Scout, revoke the App Password at https://myaccount.google.com/apppasswords
4. **Use a dedicated email** - consider creating a separate Gmail account just for automated systems

---

## Alternative: Using a Different Email Provider

If you prefer not to use Gmail, you can modify `email_sender.py` to use a different SMTP server:

- **Outlook/Hotmail**: smtp-mail.outlook.com:587
- **Yahoo**: smtp.mail.yahoo.com:587
- **Custom SMTP**: Check with your email provider for settings

Update the `SMTP_SERVER` and `SMTP_PORT` constants in `email_sender.py`.

---

## Need Help?

If you continue having issues:

1. Check the `surgical_scout.log` file for detailed error messages
2. Run with verbose logging: `python scout.py --debug`
3. Test the email sender independently: `python email_sender.py`
