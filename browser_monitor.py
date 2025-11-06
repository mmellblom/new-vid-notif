"""
Browser Monitor
Detects when YouTube is opened in a browser and triggers video checking.
"""

import psutil
import time
import subprocess
import sys
from typing import List, Set
from youtube_notifier import YouTubeNotifier


class BrowserMonitor:
    def __init__(self, notifier: YouTubeNotifier):
        """Initialize browser monitor."""
        self.notifier = notifier
        self.browser_processes = [
            'chrome.exe', 'firefox.exe', 'msedge.exe', 
            'opera.exe', 'brave.exe', 'vivaldi.exe'
        ]
        self.youtube_domains = [
            'youtube.com', 'www.youtube.com', 'm.youtube.com'
        ]
        self.checked_processes: Set[int] = set()
        self.last_check_time = {}
        
    def _is_youtube_open(self) -> bool:
        """Check if YouTube is open in any browser."""
        try:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    proc_name = proc.info['name'].lower()
                    
                    # Check if it's a browser process
                    if any(browser in proc_name for browser in self.browser_processes):
                        pid = proc.info['pid']
                        
                        # Check connections for YouTube domains
                        connections = proc.info.get('connections', [])
                        for conn in connections:
                            if hasattr(conn, 'remote_address') and conn.remote_address:
                                remote_addr = str(conn.remote_address)
                                # Check if any YouTube domain is in the connection
                                # Note: This is a simplified check
                                if any(domain in remote_addr for domain in self.youtube_domains):
                                    return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Error checking processes: {e}")
        
        return False
    
    def _check_browser_tabs_simple(self) -> bool:
        """
        Simple check: Look for browser processes and assume YouTube might be open.
        This is a fallback method since detailed tab checking requires browser extensions.
        """
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if any(browser in proc_name for browser in self.browser_processes):
                        # Browser is running, could have YouTube open
                        return True
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Error in simple browser check: {e}")
        
        return False
    
    def monitor(self, check_interval: int = 5):
        """
        Monitor for YouTube being opened and check for new videos.
        
        Args:
            check_interval: Seconds between checks for YouTube being open
        """
        print("Browser Monitor Started")
        print("Monitoring for YouTube to be opened...")
        print("Press Ctrl+C to stop\n")
        
        last_checked = 0
        min_check_interval = 60  # Minimum seconds between video checks
        
        try:
            while True:
                # Check if YouTube might be open (simplified check)
                browser_open = self._check_browser_tabs_simple()
                
                if browser_open:
                    current_time = time.time()
                    # Only check videos if enough time has passed
                    if current_time - last_checked >= min_check_interval:
                        print(f"\n[{time.strftime('%H:%M:%S')}] Browser detected - Checking for new videos...")
                        self.notifier.check_channels()
                        last_checked = current_time
                
                time.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n\nMonitor stopped by user.")
        except Exception as e:
            print(f"Error in monitor: {e}")


def main():
    """Main function for browser monitoring."""
    notifier = YouTubeNotifier()
    monitor = BrowserMonitor(notifier)
    
    # Start monitoring
    monitor.monitor(check_interval=5)


if __name__ == "__main__":
    main()

