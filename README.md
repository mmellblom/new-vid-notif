# YouTube New Video Notifier

A Python script that monitors your subscribed YouTube channels and sends Windows notifications when new videos are posted. The script can detect when YouTube is opened in your browser and automatically check for new videos.

## Features

- 🎥 Monitor multiple YouTube channels
- 🔔 Windows desktop notifications for new videos
- 🌐 Browser detection - automatically checks when YouTube is opened
- 💾 SQLite database to track watched videos (no duplicate notifications)
- ⚙️ Easy channel management via command-line interface
- 🔄 Configurable check intervals

## Requirements

- Python 3.7 or higher
- Windows 10/11 (for notifications)
- Internet connection

## Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Setup

### Option A: Automatically Sync from Your YouTube Account (Recommended)

**This automatically fetches all channels you're subscribed to on YouTube!**

> **Note:** You don't need to manually add channels if you use the `sync` command. It will automatically fetch all channels from your YouTube subscribed list!

1. **Set up YouTube Data API credentials:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project (or select an existing one)
   - Enable the **YouTube Data API v3**:
     - Go to "APIs & Services" > "Library"
     - Search for "YouTube Data API v3"
     - Click "Enable"
   - Create OAuth 2.0 credentials:
     - Go to "APIs & Services" > "Credentials"
     - Click "Create Credentials" > "OAuth client ID"
     - Choose "Desktop app" as the application type
     - Name it (e.g., "YouTube Notifier")
     - Click "Create"
   - Download the credentials:
     - Click the download icon next to your OAuth client
     - Save the JSON file as `credentials.json` in the project directory

2. **Sync your subscribed channels:**
   ```bash
   python setup.py
   ```
   Then type: `sync`
   - This will open a browser for authentication
   - Sign in with your YouTube account
   - Grant permissions to read your subscriptions
   - All your subscribed channels will be automatically added!

### Option B: Manually Add Channels

If you prefer to manually add channels or don't want to set up API credentials:

1. **Run the setup script:**
   ```bash
   python setup.py
   ```

2. **Use the interactive commands:**
   - `add <channel_url>` - Add a channel to monitor
     - Examples:
       - `add https://www.youtube.com/@channelname`
       - `add https://www.youtube.com/c/channelname`
       - `add https://www.youtube.com/channel/UCxxxxxxxxxxxxx`
   - `sync` - Sync channels from your YouTube account (requires API setup)
   - `list` - List all monitored channels
   - `remove <channel_name>` - Remove a channel
   - `check` - Manually check for new videos
   - `quit` - Exit setup

### Configure Settings

Edit `config.json` to customize settings:

```json
{
  "channels": [...],
  "check_interval_seconds": 60,
  "notification_enabled": true
}
```

- `check_interval_seconds`: Minimum time between video checks (in seconds)
- `notification_enabled`: Enable/disable notifications

## Usage

### Option 1: Browser Monitor (Recommended)

Automatically checks for new videos when YouTube is detected in your browser:

```bash
python browser_monitor.py
```

This will:
- Monitor for browser processes
- Detect when YouTube might be open
- Automatically check for new videos
- Send notifications for new content

**Note:** The browser detection uses a simplified method. For more accurate detection, you may want to use a browser extension or scheduled checks.

### Option 2: Manual Check

Check for new videos manually:

```bash
python youtube_notifier.py
```

### Option 3: Scheduled Checks

You can set up a scheduled task in Windows Task Scheduler to run `youtube_notifier.py` at regular intervals.

## How It Works

1. **Channel Monitoring**: The script uses `yt-dlp` to fetch the latest videos from each monitored channel.

2. **Video Tracking**: A SQLite database (`videos.db`) stores all videos that have been seen, preventing duplicate notifications.

3. **Notifications**: When a new video is detected, a Windows notification is sent using the `plyer` library.

4. **Browser Detection**: The browser monitor checks for running browser processes and assumes YouTube might be open (simplified detection).

## Project Structure

```
new-vid-notif/
├── youtube_notifier.py    # Main notification logic
├── browser_monitor.py     # Browser detection and monitoring
├── setup.py               # Interactive channel setup
├── config.json            # Configuration file
├── videos.db              # SQLite database (created automatically)
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Troubleshooting

### Notifications Not Working

- Ensure you're on Windows 10/11
- Check that notifications are enabled in Windows settings
- Verify `notification_enabled` is `true` in `config.json`

### Channel Not Found

- Make sure the channel URL is correct
- Try using the full channel URL (e.g., `https://www.youtube.com/@channelname`)
- Some channels may require different URL formats

### Browser Detection Not Working

The current browser detection is simplified. For more accurate detection:
- Consider using a browser extension
- Use scheduled checks instead
- Manually run the check script

## Future Enhancements

Potential improvements:
- More accurate browser tab detection
- Browser extension for better integration
- YouTube Data API integration (requires API key)
- Custom notification sounds
- Filter by video duration or category
- Email notifications
- Multiple notification methods

## License

This project is open source and available for personal use.

## Contributing

Feel free to submit issues or pull requests if you'd like to improve this project!
