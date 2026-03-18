#!/usr/bin/env python3
"""
Configuration manager for email-sender skill.
Handles reading, writing, and interactive setup of SMTP configuration.
"""

import json
import os
import stat
from pathlib import Path


CONFIG_DIR = Path.home() / ".config" / "email-sender"
CONFIG_FILE = CONFIG_DIR / "config.json"


def ensure_config_dir():
    """Ensure configuration directory exists with proper permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    # Set directory permissions to user-only
    os.chmod(CONFIG_DIR, stat.S_IRWXU)


def config_exists():
    """Check if configuration file exists."""
    return CONFIG_FILE.exists()


def load_config():
    """Load configuration from file."""
    if not config_exists():
        return None
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config):
    """Save configuration to file with secure permissions."""
    ensure_config_dir()
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    # Set file permissions to user-read/write only
    os.chmod(CONFIG_FILE, stat.S_IRUSR | stat.S_IWUSR)


def interactive_setup():
    """Interactive configuration setup."""
    print("=" * 50)
    print("Email Sender - Initial Setup")
    print("=" * 50)
    print()
    print("Please enter your SMTP server information:")
    print()

    config = {}

    # SMTP Server
    print("Common SMTP servers:")
    print("  - Gmail: smtp.gmail.com")
    print("  - QQ邮箱: smtp.qq.com")
    print("  - 163邮箱: smtp.163.com")
    print("  - Outlook: smtp.office365.com")
    print()
    config['smtp_server'] = input("SMTP Server: ").strip()

    # SMTP Port
    print()
    print("Common ports:")
    print("  - 587 (TLS, recommended)")
    print("  - 465 (SSL)")
    print("  - 25 (unencrypted, not recommended)")
    print()
    port_str = input("SMTP Port [587]: ").strip()
    config['smtp_port'] = int(port_str) if port_str else 587

    # Use TLS
    print()
    use_tls = input("Use TLS? (yes/no) [yes]: ").strip().lower()
    config['use_tls'] = use_tls in ('', 'yes', 'y', 'true', '1')

    # Email address
    print()
    config['email'] = input("Your email address: ").strip()

    # Password
    print()
    print("Note: For Gmail, use an 'App Password' instead of your regular password.")
    print("      You can generate one at: https://myaccount.google.com/apppasswords")
    print()
    import getpass
    config['password'] = getpass.getpass("Email password: ")

    # Validate required fields
    if not config['smtp_server'] or not config['email'] or not config['password']:
        raise ValueError("SMTP server, email, and password are required.")

    # Save configuration
    save_config(config)

    print()
    print("=" * 50)
    print("Configuration saved successfully!")
    print(f"Config file: {CONFIG_FILE}")
    print("=" * 50)

    return config


def get_config():
    """Get configuration, running interactive setup if needed."""
    config = load_config()
    if config is None:
        config = interactive_setup()
    return config


def show_config():
    """Display current configuration (without password)."""
    config = load_config()
    if config is None:
        print("No configuration found. Run setup first.")
        return

    print("Current configuration:")
    print(f"  SMTP Server: {config.get('smtp_server', 'N/A')}")
    print(f"  SMTP Port: {config.get('smtp_port', 'N/A')}")
    print(f"  Use TLS: {config.get('use_tls', True)}")
    print(f"  Email: {config.get('email', 'N/A')}")
    print(f"  Password: {'*' * 8}")


def main():
    """Main entry point for CLI usage."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: config_manager.py <command>")
        print("Commands:")
        print("  setup    - Run interactive configuration setup")
        print("  show     - Show current configuration")
        print("  get      - Get configuration (runs setup if needed)")
        return

    command = sys.argv[1].lower()

    if command == 'setup':
        interactive_setup()
    elif command == 'show':
        show_config()
    elif command == 'get':
        config = get_config()
        print(json.dumps(config, indent=2))
    else:
        print(f"Unknown command: {command}")


if __name__ == '__main__':
    main()
