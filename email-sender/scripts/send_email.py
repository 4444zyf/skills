#!/usr/bin/env python3
"""
Email sender with folder attachment support.
Compresses folders to ZIP and sends via SMTP.
"""

import argparse
import os
import smtplib
import sys
import zipfile
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import List, Optional

import config_manager


def compress_folder(folder_path: str, output_path: Optional[str] = None) -> str:
    """
    Compress a folder to ZIP format.

    Args:
        folder_path: Path to the folder to compress
        output_path: Optional output path for the ZIP file

    Returns:
        Path to the created ZIP file
    """
    source = Path(folder_path).resolve()

    if not source.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    if not source.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {folder_path}")

    # Determine output path
    if output_path is None:
        zip_path = source.parent / f"{source.name}.zip"
    else:
        zip_path = Path(output_path)

    # Ensure .zip extension
    if not zip_path.suffix == '.zip':
        zip_path = zip_path.with_suffix('.zip')

    # Create ZIP archive
    print(f"Compressing folder: {source}")
    print(f"Output: {zip_path}")

    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(source):
            root_path = Path(root)

            # Skip hidden directories (starting with .)
            dirs[:] = [d for d in dirs if not d.startswith('.')]

            for file in files:
                # Skip hidden files
                if file.startswith('.'):
                    continue

                file_path = root_path / file
                arcname = file_path.relative_to(source.parent)

                try:
                    zf.write(file_path, arcname)
                except (OSError, PermissionError) as e:
                    print(f"Warning: Could not add file {file_path}: {e}")

    # Get size
    size_bytes = zip_path.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    print(f"Archive size: {size_mb:.2f} MB")

    return str(zip_path)


def create_email_message(
    sender: str,
    recipient: str,
    subject: str,
    body: str,
    attachment_paths: List[str]
) -> MIMEMultipart:
    """
    Create a multipart email message with attachments.

    Args:
        sender: Sender email address
        recipient: Recipient email address
        subject: Email subject
        body: Email body text
        attachment_paths: List of file paths to attach

    Returns:
        MIMEMultipart message
    """
    msg = MIMEMultipart()
    msg['From'] = sender
    msg['To'] = recipient
    msg['Subject'] = subject

    # Attach body
    msg.attach(MIMEText(body, 'plain', 'utf-8'))

    # Attach files
    for attachment_path in attachment_paths:
        path = Path(attachment_path)

        if not path.exists():
            print(f"Warning: Attachment not found: {attachment_path}")
            continue

        with open(path, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())

        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{path.name}"'
        )
        msg.attach(part)
        print(f"Attached: {path.name}")

    return msg


def send_email(
    config: dict,
    recipient: str,
    subject: str,
    body: str,
    attachment_paths: List[str]
) -> bool:
    """
    Send an email with attachments via SMTP.

    Args:
        config: SMTP configuration dictionary
        recipient: Recipient email address
        subject: Email subject
        body: Email body text
        attachment_paths: List of file paths to attach

    Returns:
        True if successful, False otherwise
    """
    sender = config['email']

    # Create message
    msg = create_email_message(sender, recipient, subject, body, attachment_paths)

    # Connect to SMTP server and send
    try:
        print(f"Connecting to {config['smtp_server']}:{config['smtp_port']}...")

        if config.get('use_tls', True):
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
        else:
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])

        print("Logging in...")
        server.login(config['email'], config['password'])

        print(f"Sending email to {recipient}...")
        server.send_message(msg)
        server.quit()

        print("Email sent successfully!")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {e}")
        print("Troubleshooting:")
        print("  - Double-check your email and password")
        print("  - For Gmail, use an App Password instead of your regular password")
        print("  - Check if your email provider requires special settings")
        return False

    except smtplib.SMTPException as e:
        print(f"SMTP error: {e}")
        return False

    except Exception as e:
        print(f"Error sending email: {e}")
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Send folders via email with ZIP compression'
    )
    parser.add_argument(
        'folders',
        nargs='+',
        help='Folder(s) to compress and send'
    )
    parser.add_argument(
        '--to', '-t',
        required=True,
        help='Recipient email address'
    )
    parser.add_argument(
        '--subject', '-s',
        default='Folder Attachment',
        help='Email subject'
    )
    parser.add_argument(
        '--body', '-b',
        default='Please find the attached folder(s).',
        help='Email body text'
    )
    parser.add_argument(
        '--keep-zip', '-k',
        action='store_true',
        help='Keep the ZIP file after sending (default: delete)'
    )
    parser.add_argument(
        '--output', '-o',
        help='Output path for ZIP file'
    )

    args = parser.parse_args()

    # Load or create configuration
    try:
        config = config_manager.get_config()
    except KeyboardInterrupt:
        print("\nSetup cancelled.")
        return 1
    except Exception as e:
        print(f"Configuration error: {e}")
        return 1

    # Validate folders
    for folder in args.folders:
        if not os.path.exists(folder):
            print(f"Error: Folder not found: {folder}")
            return 1
        if not os.path.isdir(folder):
            print(f"Error: Not a directory: {folder}")
            return 1

    # Compress folders
    zip_paths = []
    try:
        if len(args.folders) == 1 and args.output:
            # Single folder with custom output
            zip_path = compress_folder(args.folders[0], args.output)
            zip_paths.append(zip_path)
        elif len(args.folders) == 1:
            # Single folder, default output
            zip_path = compress_folder(args.folders[0])
            zip_paths.append(zip_path)
        else:
            # Multiple folders
            for folder in args.folders:
                zip_path = compress_folder(folder)
                zip_paths.append(zip_path)
    except Exception as e:
        print(f"Error compressing folder: {e}")
        return 1

    # Send email
    success = send_email(
        config,
        args.to,
        args.subject,
        args.body,
        zip_paths
    )

    # Cleanup
    if not args.keep_zip:
        for zip_path in zip_paths:
            try:
                os.remove(zip_path)
                print(f"Cleaned up: {zip_path}")
            except OSError as e:
                print(f"Warning: Could not delete {zip_path}: {e}")
    else:
        print(f"ZIP files kept at:")
        for zip_path in zip_paths:
            print(f"  {zip_path}")

    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
