"""
Setup script for adding channels to monitor.
"""

import sys
from youtube_notifier import YouTubeNotifier


def main():
    """Interactive setup for adding channels."""
    notifier = YouTubeNotifier()
    
    print("YouTube Notifier - Channel Setup")
    print("=" * 40)
    print("\nCommands:")
    print("  add <channel_url>  - Add a channel to monitor")
    print("  list               - List all monitored channels")
    print("  remove <name>      - Remove a channel")
    print("  check              - Check for new videos now")
    print("  quit               - Exit setup\n")
    
    while True:
        try:
            command = input("> ").strip().split()
            
            if not command:
                continue
            
            cmd = command[0].lower()
            
            if cmd == 'quit' or cmd == 'exit':
                print("Goodbye!")
                break
            elif cmd == 'add' and len(command) > 1:
                channel_url = ' '.join(command[1:])
                notifier.add_channel(channel_url)
            elif cmd == 'list':
                notifier.list_channels()
            elif cmd == 'remove' and len(command) > 1:
                channel_name = ' '.join(command[1:])
                notifier.remove_channel(channel_name)
            elif cmd == 'check':
                notifier.check_channels()
            elif cmd == 'help':
                print("\nCommands:")
                print("  add <channel_url>  - Add a channel to monitor")
                print("  list               - List all monitored channels")
                print("  remove <name>      - Remove a channel")
                print("  check              - Check for new videos now")
                print("  quit               - Exit setup\n")
            else:
                print("Unknown command. Type 'help' for available commands.")
                
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()

