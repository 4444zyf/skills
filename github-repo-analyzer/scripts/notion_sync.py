#!/usr/bin/env python3
"""
Notion 同步工具 - 将 Markdown 文件上传到 Notion
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Optional

# Notion API 配置
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"


def get_notion_api_key() -> Optional[str]:
    """从配置文件读取 Notion API Key"""
    config_path = Path.home() / ".config" / "notion" / "api_key"
    if config_path.exists():
        return config_path.read_text().strip()
    return None


def parse_markdown_blocks(content: str, max_length: int = 2000) -> list:
    """将 Markdown 内容分块"""
    blocks = []
    lines = content.split('\n')
    current_block = []
    current_length = 0

    for line in lines:
        line_length = len(line) + 1  # +1 for newline

        if current_length + line_length > max_length and current_block:
            blocks.append('\n'.join(current_block))
            current_block = []
            current_length = 0

        current_block.append(line)
        current_length += line_length

    if current_block:
        blocks.append('\n'.join(current_block))

    return blocks


def markdown_to_notion_blocks(content: str) -> list:
    """将 Markdown 转换为 Notion block 格式"""
    blocks = []
    lines = content.split('\n')

    for line in lines:
        # 标题转换
        if line.startswith('# '):
            blocks.append({
                "object": "block",
                "type": "heading_1",
                "heading_1": {
                    "rich_text": [{"type": "text", "text": {"content": line[2:]}}]
                }
            })
        elif line.startswith('## '):
            blocks.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": line[3:]}}]
                }
            })
        elif line.startswith('### '):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[4:]}}]
                }
            })
        # 代码块
        elif line.startswith('```'):
            # 简化处理：作为普通文本
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                }
            })
        # 列表项
        elif line.strip().startswith('- ') or line.strip().startswith('* '):
            blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": line.strip()[2:]}}]
                }
            })
        # 数字列表
        elif re.match(r'^\s*\d+\.', line):
            text = re.sub(r'^\s*\d+\.\s*', '', line)
            blocks.append({
                "object": "block",
                "type": "numbered_list_item",
                "numbered_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": text}}]
                }
            })
        # 空行
        elif not line.strip():
            continue
        # 普通段落
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                }
            })

    return blocks


def create_notion_page(api_key: str, parent_page_id: str, title: str, content: str) -> dict:
    """在 Notion 创建页面"""
    import urllib.request
    import urllib.error

    url = f"{NOTION_API_BASE}/pages"

    blocks = markdown_to_notion_blocks(content)
    # Notion 限制：每次最多 100 个 blocks
    blocks = blocks[:100]

    data = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
            }
        },
        "children": blocks
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"Notion API error: {error_body}")


def create_database_item(api_key: str, database_id: str, title: str, content: str) -> dict:
    """在 Notion 数据库创建条目"""
    import urllib.request
    import urllib.error

    url = f"{NOTION_API_BASE}/pages"

    # 截取内容摘要
    summary = content[:2000] if len(content) > 2000 else content

    data = {
        "parent": {"database_id": database_id},
        "properties": {
            "Name": {
                "title": [{"type": "text", "text": {"content": title}}]
            },
            "Summary": {
                "rich_text": [{"type": "text", "text": {"content": summary}}]
            }
        }
    }

    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"Notion API error: {error_body}")


def sync_reports_to_notion(reports_dir: str, parent_page_id: Optional[str] = None) -> dict:
    """
    同步报告目录到 Notion

    Args:
        reports_dir: 报告目录路径
        parent_page_id: Notion 父页面 ID（可选）

    Returns:
        同步结果统计
    """
    api_key = get_notion_api_key()
    if not api_key:
        return {
            "success": False,
            "error": "Notion API key not found in ~/.config/notion/api_key"
        }

    reports_path = Path(reports_dir)
    if not reports_path.exists():
        return {
            "success": False,
            "error": f"Reports directory not found: {reports_dir}"
        }

    results = {
        "success": True,
        "synced_files": [],
        "errors": [],
        "pages_created": []
    }

    # 获取所有 markdown 文件
    md_files = sorted(reports_path.glob("*.md"))

    if not md_files:
        return {
            "success": False,
            "error": "No markdown files found in reports directory"
        }

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding='utf-8')
            title = md_file.stem  # 文件名（不含扩展名）

            # 如果提供了父页面 ID，创建为子页面
            if parent_page_id:
                page = create_notion_page(api_key, parent_page_id, title, content)
                results["pages_created"].append({
                    "file": str(md_file),
                    "notion_page_id": page.get("id"),
                    "url": page.get("url")
                })

            results["synced_files"].append(str(md_file))

        except Exception as e:
            results["errors"].append({
                "file": str(md_file),
                "error": str(e)
            })

    return results


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: notion_sync.py <reports_directory> [parent_page_id]")
        sys.exit(1)

    reports_dir = sys.argv[1]
    parent_page_id = sys.argv[2] if len(sys.argv) > 2 else None

    result = sync_reports_to_notion(reports_dir, parent_page_id)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
