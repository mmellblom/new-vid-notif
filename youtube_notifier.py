"""
YouTube New Video Notifier
Monitors subscribed channels and sends notifications when new videos are posted.
"""

import json
import sqlite3
import time
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

import yt_dlp
from plyer import notification

try:
    from youtube_api import YouTubeAPI
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False


class YouTubeNotifier:
    def __init__(self, config_path: str = "config.json", db_path: str = "videos.db"):
        """Initialize the YouTube Notifier."""
        self.config_path = config_path
        self.db_path = db_path
        self.config = self._load_config()
        self._init_database()
        
    def _load_config(self) -> dict:
        """Load configuration from JSON file."""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as f:
                return json.load(f)
        return {"channels": [], "check_interval_seconds": 60, "notification_enabled": True}
    
    def _save_config(self):
        """Save configuration to JSON file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def _init_database(self):
        """Initialize SQLite database for tracking videos."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                channel_id TEXT,
                channel_name TEXT,
                title TEXT,
                url TEXT,
                published_at TEXT,
                first_seen_at TEXT
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_channel(self, channel_url: str) -> bool:
        """
        Add a channel to monitor.
        
        Args:
            channel_url: YouTube channel URL or handle (e.g., @channelname or full URL)
            
        Returns:
            True if channel was added successfully, False otherwise
        """
        try:
            # Extract channel info
            channel_info = self._get_channel_info(channel_url)
            if not channel_info:
                return False
            
            # Check if channel already exists
            channel_id = channel_info.get('channel_id')
            if any(ch.get('channel_id') == channel_id for ch in self.config['channels']):
                print(f"Channel {channel_info.get('channel_name')} is already being monitored.")
                return False
            
            # Add to config
            self.config['channels'].append({
                'channel_id': channel_id,
                'channel_name': channel_info.get('channel_name'),
                'channel_url': channel_info.get('channel_url'),
                'added_at': datetime.now().isoformat()
            })
            self._save_config()
            print(f"Added channel: {channel_info.get('channel_name')}")
            return True
        except Exception as e:
            print(f"Error adding channel: {e}")
            return False
    
    def _get_channel_info(self, channel_url: str) -> Optional[Dict]:
        """Get channel information from URL."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                if 'channel_id' in info:
                    return {
                        'channel_id': info['channel_id'],
                        'channel_name': info.get('channel', info.get('uploader', 'Unknown')),
                        'channel_url': info.get('channel_url', channel_url)
                    }
                elif 'entries' and len(info.get('entries', [])) > 0:
                    # For channel pages
                    entry = info['entries'][0]
                    return {
                        'channel_id': entry.get('channel_id', ''),
                        'channel_name': entry.get('channel', entry.get('uploader', 'Unknown')),
                        'channel_url': entry.get('channel_url', channel_url)
                    }
        except Exception as e:
            print(f"Error getting channel info: {e}")
        return None
    
    def _get_latest_videos(self, channel_url: str, max_results: int = 5) -> List[Dict]:
        """Get latest videos from a channel."""
        try:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(channel_url, download=False)
                
                videos = []
                entries = info.get('entries', [])
                
                for entry in entries[:max_results]:
                    if entry:
                        video_id = entry.get('id', '')
                        if video_id:
                            videos.append({
                                'video_id': video_id,
                                'channel_id': entry.get('channel_id', ''),
                                'channel_name': entry.get('channel', entry.get('uploader', 'Unknown')),
                                'title': entry.get('title', 'Unknown Title'),
                                'url': f"https://www.youtube.com/watch?v={video_id}",
                                'published_at': entry.get('upload_date', ''),
                            })
                return videos
        except Exception as e:
            print(f"Error getting videos from {channel_url}: {e}")
        return []
    
    def _is_video_new(self, video_id: str) -> bool:
        """Check if a video is new (not in database)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT video_id FROM videos WHERE video_id = ?', (video_id,))
        exists = cursor.fetchone() is not None
        conn.close()
        return not exists
    
    def _save_video(self, video: Dict):
        """Save video to database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO videos 
            (video_id, channel_id, channel_name, title, url, published_at, first_seen_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            video['video_id'],
            video.get('channel_id', ''),
            video.get('channel_name', ''),
            video.get('title', ''),
            video.get('url', ''),
            video.get('published_at', ''),
            datetime.now().isoformat()
        ))
        conn.commit()
        conn.close()
    
    def _send_notification(self, video: Dict):
        """Send Windows notification for new video."""
        if not self.config.get('notification_enabled', True):
            return
        
        try:
            notification.notify(
                title=f"New Video: {video.get('channel_name', 'Unknown Channel')}",
                message=video.get('title', 'New video posted!'),
                app_name="YouTube Notifier",
                timeout=10
            )
        except Exception as e:
            print(f"Error sending notification: {e}")
    
    def check_channels(self):
        """Check all monitored channels for new videos."""
        if not self.config.get('channels'):
            print("No channels configured. Add channels using add_channel() method.")
            return
        
        print(f"Checking {len(self.config['channels'])} channels...")
        new_videos_count = 0
        
        for channel in self.config['channels']:
            channel_url = channel.get('channel_url', '')
            channel_name = channel.get('channel_name', 'Unknown')
            
            print(f"Checking {channel_name}...")
            videos = self._get_latest_videos(channel_url, max_results=5)
            
            for video in videos:
                if self._is_video_new(video['video_id']):
                    print(f"  NEW: {video['title']}")
                    self._save_video(video)
                    self._send_notification(video)
                    new_videos_count += 1
        
        if new_videos_count == 0:
            print("No new videos found.")
        else:
            print(f"Found {new_videos_count} new video(s)!")
    
    def list_channels(self):
        """List all monitored channels."""
        if not self.config.get('channels'):
            print("No channels configured.")
            return
        
        print("\nMonitored Channels:")
        for i, channel in enumerate(self.config['channels'], 1):
            print(f"{i}. {channel.get('channel_name')} ({channel.get('channel_id')})")
    
    def remove_channel(self, channel_name: str) -> bool:
        """Remove a channel from monitoring."""
        original_count = len(self.config['channels'])
        self.config['channels'] = [
            ch for ch in self.config['channels'] 
            if ch.get('channel_name', '').lower() != channel_name.lower()
        ]
        
        if len(self.config['channels']) < original_count:
            self._save_config()
            print(f"Removed channel: {channel_name}")
            return True
        else:
            print(f"Channel not found: {channel_name}")
            return False
    
    def sync_from_youtube_account(self, replace_existing: bool = False) -> int:
        """
        Automatically fetch and add all channels from your YouTube subscribed list.
        
        Args:
            replace_existing: If True, replace existing channels. If False, merge with existing.
            
        Returns:
            Number of channels added
        """
        if not API_AVAILABLE:
            print("YouTube Data API not available. Install required packages:")
            print("pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return 0
        
        print("Authenticating with YouTube...")
        api = YouTubeAPI()
        
        if not api.authenticate():
            print("Failed to authenticate with YouTube. Please check your credentials.")
            return 0
        
        print("Fetching your subscribed channels...")
        subscribed_channels = api.get_subscribed_channels(max_results=200)
        
        if not subscribed_channels:
            print("No subscribed channels found or error fetching channels.")
            return 0
        
        print(f"Found {len(subscribed_channels)} subscribed channels.")
        
        if replace_existing:
            self.config['channels'] = []
            print("Replacing existing channels...")
        else:
            print("Merging with existing channels...")
        
        added_count = 0
        skipped_count = 0
        
        for channel in subscribed_channels:
            channel_id = channel.get('channel_id')
            
            # Check if channel already exists
            if any(ch.get('channel_id') == channel_id for ch in self.config['channels']):
                skipped_count += 1
                continue
            
            self.config['channels'].append({
                'channel_id': channel_id,
                'channel_name': channel.get('channel_name', 'Unknown'),
                'channel_url': channel.get('channel_url', ''),
                'added_at': datetime.now().isoformat(),
                'synced_from_account': True
            })
            added_count += 1
        
        self._save_config()
        
        print(f"\nSync complete!")
        print(f"  Added: {added_count} channels")
        if skipped_count > 0:
            print(f"  Skipped: {skipped_count} channels (already in list)")
        print(f"  Total monitored: {len(self.config['channels'])} channels")
        
        return added_count


def main():
    """Main function for command-line usage."""
    notifier = YouTubeNotifier()
    
    print("YouTube New Video Notifier")
    print("=" * 40)
    
    # Check channels
    notifier.check_channels()


if __name__ == "__main__":
    main()

