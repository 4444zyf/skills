---
name: email-sender
description: Send emails with folder attachments via SMTP. Use this skill when the user wants to send files or folders via email, share directories as compressed attachments, or email backup archives. Automatically triggers when users mention sending emails with attachments, emailing folders, or compressing and sending files.
---

# Email Sender Skill

Send emails with folder attachments via SMTP. This skill helps you compress directories and send them as email attachments.

## Prerequisites

- Python 3.7+
- SMTP server credentials (Gmail, QQ邮箱, 163邮箱, etc.)

## Configuration

The skill stores configuration in `~/.config/email-sender/config.json`. On first run, you will be prompted to enter:

- SMTP server address (e.g., smtp.gmail.com, smtp.qq.com)
- SMTP port (e.g., 587 for TLS, 465 for SSL)
- Sender email address
- Email password or app-specific password
- Use TLS (recommended for port 587)

### Common SMTP Settings

| Provider | Server | Port | TLS |
|----------|--------|------|-----|
| Gmail | smtp.gmail.com | 587 | Yes |
| QQ邮箱 | smtp.qq.com | 587 | Yes |
| 163邮箱 | smtp.163.com | 25/587 | Yes |
| Outlook | smtp.office365.com | 587 | Yes |

**Note:** For Gmail, use an "App Password" instead of your regular password.

## Usage

### Send a Folder as Email Attachment

```
邮件发送 /path/to/folder 到 recipient@example.com
```

### With Custom Subject

```
邮件发送 /path/to/folder 到 recipient@example.com --subject "备份文件"
```

### With Custom Body

```
邮件发送 /path/to/folder 到 recipient@example.com --subject "备份" --body "请查收附件"
```

## Workflow

1. **Check Configuration**: Verify SMTP config exists, prompt if missing
2. **Validate Folder**: Ensure source folder exists and is readable
3. **Compress**: Create ZIP archive of the folder
4. **Send Email**: Send via SMTP with the compressed attachment
5. **Cleanup**: Remove temporary ZIP file after sending (optional)

## Technical Details

The skill uses bundled Python scripts:
- `scripts/config_manager.py` - Handle configuration storage
- `scripts/send_email.py` - SMTP sending and folder compression

Configuration is stored securely in `~/.config/email-sender/config.json` with user-only permissions (0600).

## Examples

**Basic folder send:**
```
邮件发送 ./my-project 到 boss@company.com
```

**Send with subject:**
```
邮件发送 ./reports 到 team@company.com --subject "月度报告"
```

**Send multiple folders:**
```
邮件发送 ./folder1 ./folder2 到 admin@company.com --subject "项目文件"
```

## Error Handling

- Missing folder: Error with clear message
- Missing config: Interactive prompt to set up
- Authentication failure: Detailed error with troubleshooting hints
- File too large: Warning about attachment size limits
