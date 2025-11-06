# YouTube Data API Setup Guide

This guide will help you set up YouTube Data API credentials to automatically sync your subscribed channels.

## Step-by-Step Instructions

### 1. Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Sign in with your Google account
3. Click on the project dropdown at the top
4. Click "New Project"
5. Enter a project name (e.g., "YouTube Notifier")
6. Click "Create"

### 2. Enable YouTube Data API v3

1. In the Google Cloud Console, go to **"APIs & Services"** > **"Library"**
2. Search for **"YouTube Data API v3"**
3. Click on it
4. Click the **"Enable"** button
5. Wait for it to enable (may take a few seconds)

### 3. Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** > **"Credentials"**
2. Click **"Create Credentials"** at the top
3. Select **"OAuth client ID"**
4. If prompted, configure the OAuth consent screen:
   - Choose **"External"** (unless you have a Google Workspace account)
   - Fill in the required information:
     - App name: "YouTube Notifier" (or any name)
     - User support email: Your email
     - Developer contact: Your email
   - Click **"Save and Continue"**
   - On the Scopes page, click **"Save and Continue"** (no need to add scopes here)
   - On the Test users page, click **"Save and Continue"** (you can add yourself later if needed)
   - Review and click **"Back to Dashboard"**

5. Now create the OAuth client:
   - Application type: Select **"Desktop app"**
   - Name: "YouTube Notifier" (or any name)
   - Click **"Create"**

6. Download the credentials:
   - A dialog will appear with your client ID and secret
   - Click the **download icon** (⬇️) to download the JSON file
   - Save it as `credentials.json` in your project directory

### 4. Use the Credentials

1. Place `credentials.json` in the same directory as `setup.py`
2. Run `python setup.py`
3. Type `sync` to sync your subscribed channels
4. A browser window will open asking you to sign in
5. Sign in with your YouTube account
6. Grant permissions to read your subscriptions
7. The script will automatically fetch all your subscribed channels!

## Troubleshooting

### "credentials.json not found"
- Make sure you downloaded the JSON file from Google Cloud Console
- Make sure it's named exactly `credentials.json`
- Make sure it's in the same directory as `setup.py`

### "Access denied" or "403 Forbidden"
- Make sure YouTube Data API v3 is enabled in your project
- Make sure you're using the correct credentials file
- Try creating new credentials if the issue persists

### "Invalid client" error
- Make sure you selected "Desktop app" as the application type
- Make sure you downloaded the credentials after creating them
- Try creating new credentials

### Browser doesn't open for authentication
- Make sure you have a default browser set
- Try running the script from a terminal/command prompt
- Check that port 8080 (or the port shown) is not blocked

## Security Notes

- **Never share your `credentials.json` file** - it contains sensitive information
- The `token.pickle` file stores your authentication token - keep it secure
- Both files are already in `.gitignore` to prevent accidental commits
- You can revoke access at any time in [Google Account Settings](https://myaccount.google.com/permissions)

## Revoking Access

If you want to revoke access:
1. Go to [Google Account Settings](https://myaccount.google.com/permissions)
2. Find "YouTube Notifier" (or your app name)
3. Click "Remove Access"

