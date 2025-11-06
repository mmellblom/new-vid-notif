"""
YouTube Data API Integration
Handles authentication and fetching subscribed channels from YouTube account.
"""

import os
import json
import pickle
from typing import List, Dict, Optional

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    API_AVAILABLE = True
except ImportError:
    API_AVAILABLE = False
    print("Warning: Google API libraries not installed. Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")


# YouTube Data API v3 scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']


class YouTubeAPI:
    """Handles YouTube Data API authentication and operations."""
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        """
        Initialize YouTube API client.
        
        Args:
            credentials_file: Path to OAuth2 credentials JSON file
            token_file: Path to store authentication token
        """
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.credentials = None
        
    def authenticate(self) -> bool:
        """
        Authenticate with YouTube Data API.
        
        Returns:
            True if authentication successful, False otherwise
        """
        if not API_AVAILABLE:
            print("YouTube Data API libraries not available.")
            return False
        
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            except Exception as e:
                print(f"Error loading token: {e}")
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing token: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    print(f"\nError: {self.credentials_file} not found!")
                    print("\nTo use automatic subscription fetching, you need to:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Create a new project (or select existing)")
                    print("3. Enable YouTube Data API v3")
                    print("4. Create OAuth 2.0 credentials (Desktop app)")
                    print("5. Download credentials and save as 'credentials.json'")
                    print("\nSee README.md for detailed instructions.")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during authentication: {e}")
                    return False
            
            # Save credentials for next run
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            except Exception as e:
                print(f"Error saving token: {e}")
        
        self.credentials = creds
        
        try:
            self.service = build('youtube', 'v3', credentials=creds)
            return True
        except Exception as e:
            print(f"Error building YouTube service: {e}")
            return False
    
    def get_subscribed_channels(self, max_results: int = 50) -> List[Dict]:
        """
        Get list of channels the authenticated user is subscribed to.
        
        Args:
            max_results: Maximum number of channels to retrieve
            
        Returns:
            List of channel dictionaries with channel_id, channel_name, and channel_url
        """
        if not self.service:
            if not self.authenticate():
                return []
        
        try:
            channels = []
            next_page_token = None
            
            while len(channels) < max_results:
                # Get subscriptions
                request = self.service.subscriptions().list(
                    part='snippet,contentDetails',
                    mine=True,
                    maxResults=min(50, max_results - len(channels)),
                    pageToken=next_page_token
                )
                response = request.execute()
                
                for item in response.get('items', []):
                    snippet = item.get('snippet', {})
                    resource_id = snippet.get('resourceId', {})
                    channel_id = resource_id.get('channelId', '')
                    channel_title = snippet.get('title', 'Unknown Channel')
                    
                    if channel_id:
                        channels.append({
                            'channel_id': channel_id,
                            'channel_name': channel_title,
                            'channel_url': f"https://www.youtube.com/channel/{channel_id}",
                            'added_at': snippet.get('publishedAt', '')
                        })
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
            
            return channels
            
        except HttpError as e:
            print(f"Error fetching subscribed channels: {e}")
            if e.resp.status == 403:
                print("Access denied. Make sure you've enabled YouTube Data API v3 and have the correct credentials.")
            return []
        except Exception as e:
            print(f"Error getting subscribed channels: {e}")
            return []
    
    def get_channel_info(self, channel_id: str) -> Optional[Dict]:
        """
        Get detailed information about a channel.
        
        Args:
            channel_id: YouTube channel ID
            
        Returns:
            Channel information dictionary or None
        """
        if not self.service:
            if not self.authenticate():
                return None
        
        try:
            request = self.service.channels().list(
                part='snippet,contentDetails',
                id=channel_id
            )
            response = request.execute()
            
            if response.get('items'):
                item = response['items'][0]
                snippet = item.get('snippet', {})
                return {
                    'channel_id': channel_id,
                    'channel_name': snippet.get('title', 'Unknown'),
                    'channel_url': f"https://www.youtube.com/channel/{channel_id}",
                    'description': snippet.get('description', ''),
                    'subscriber_count': item.get('statistics', {}).get('subscriberCount', '0')
                }
        except Exception as e:
            print(f"Error getting channel info: {e}")
        
        return None

