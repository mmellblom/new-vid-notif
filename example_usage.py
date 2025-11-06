"""
Example usage of the YouTube Notifier
This demonstrates how to use the notifier programmatically.
"""

from youtube_notifier import YouTubeNotifier


def example_basic_usage():
    """Basic example of using the notifier."""
    # Initialize the notifier
    notifier = YouTubeNotifier()
    
    # Add a channel to monitor
    print("Adding a channel...")
    notifier.add_channel("https://www.youtube.com/@mkbhd")  # Example channel
    
    # List all monitored channels
    print("\nListing channels...")
    notifier.list_channels()
    
    # Check for new videos
    print("\nChecking for new videos...")
    notifier.check_channels()


def example_programmatic_setup():
    """Example of setting up channels programmatically."""
    notifier = YouTubeNotifier()
    
    # Add multiple channels
    channels = [
        "https://www.youtube.com/@mkbhd",
        "https://www.youtube.com/@LinusTechTips",
        # Add more channel URLs here
    ]
    
    for channel_url in channels:
        print(f"Adding channel: {channel_url}")
        notifier.add_channel(channel_url)
    
    # Check for new videos
    notifier.check_channels()


if __name__ == "__main__":
    print("YouTube Notifier - Example Usage")
    print("=" * 40)
    
    # Run basic example
    example_basic_usage()
    
    # Uncomment to run programmatic setup example
    # example_programmatic_setup()

