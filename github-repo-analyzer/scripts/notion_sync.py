#!/usr/bin/env python3
"""
Notion 同步工具 - 将 Markdown 文件上传到 Notion
支持分块上传，处理大文件（超过 100 个 blocks）
支持递归目录上传，自动创建层级结构

目录结构示例:
    reports/
    ├── 01-架构.md
    ├── 02-代码质量.md
    └── 详细分析/
        └── 子报告.md

上传后在 Notion 中的结构:
    reports (父页面)
    ├── 01-架构 (子页面)
    ├── 02-代码质量 (子页面)
    └── 详细分析 (子页面，也是父页面)
        └── 子报告 (子子页面)
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Optional, List, Dict, Any, Union

# Notion API 配置
NOTION_API_BASE = "https://api.notion.com/v1"
NOTION_VERSION = "2022-06-28"
MAX_BLOCKS_PER_REQUEST = 100  # Notion API 限制


def get_notion_api_key() -> Optional[str]:
    """从配置文件读取 Notion API Key"""
    config_path = Path.home() / ".config" / "notion" / "api_key"
    if config_path.exists():
        return config_path.read_text().strip()
    return None


def markdown_to_notion_blocks(content: str) -> List[Dict[str, Any]]:
    """将 Markdown 转换为 Notion block 格式，支持多行代码块"""
    blocks = []
    lines = content.split('\n')
    i = 0
    in_code_block = False
    code_block_lines = []
    code_language = ""

    while i < len(lines):
        line = lines[i]

        # 代码块处理
        if line.startswith('```'):
            if not in_code_block:
                # 开始代码块
                in_code_block = True
                code_block_lines = []
                # 提取语言标识
                lang_match = re.match(r'^```(\w+)?', line)
                code_language = lang_match.group(1) if lang_match and lang_match.group(1) else "plain text"
            else:
                # 结束代码块
                in_code_block = False
                code_content = '\n'.join(code_block_lines)
                blocks.append({
                    "object": "block",
                    "type": "code",
                    "code": {
                        "rich_text": [{"type": "text", "text": {"content": code_content}}],
                        "language": code_language if code_language else "plain text"
                    }
                })
            i += 1
            continue

        if in_code_block:
            code_block_lines.append(line)
            i += 1
            continue

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
        elif line.startswith('#### '):
            blocks.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": line[5:]}}]
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
        # 引用块
        elif line.strip().startswith('> '):
            blocks.append({
                "object": "block",
                "type": "quote",
                "quote": {
                    "rich_text": [{"type": "text", "text": {"content": line.strip()[2:]}}]
                }
            })
        # 分隔线
        elif line.strip() == '---' or line.strip() == '***':
            blocks.append({
                "object": "block",
                "type": "divider",
                "divider": {}
            })
        # 空行
        elif not line.strip():
            pass
        # 普通段落
        else:
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [{"type": "text", "text": {"content": line}}]
                }
            })

        i += 1

    # 处理未闭合的代码块
    if in_code_block and code_block_lines:
        code_content = '\n'.join(code_block_lines)
        blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": code_content}}],
                "language": code_language if code_language else "plain text"
            }
        })

    return blocks


def create_notion_page(api_key: str, parent_page_id: str, title: str) -> Dict[str, Any]:
    """在 Notion 创建空页面（不包含内容）"""
    import urllib.request
    import urllib.error

    url = f"{NOTION_API_BASE}/pages"

    data = {
        "parent": {"page_id": parent_page_id},
        "properties": {
            "title": {
                "title": [{"type": "text", "text": {"content": title}}]
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


def append_blocks_to_page(api_key: str, page_id: str, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """向 Notion 页面追加 blocks"""
    import urllib.request
    import urllib.error

    url = f"{NOTION_API_BASE}/blocks/{page_id}/children"

    data = {
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
        method="PATCH"
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"Notion API error: {error_body}")


def upload_markdown_to_page(api_key: str, parent_page_id: str, title: str, content: str) -> Dict[str, Any]:
    """
    上传 Markdown 内容到 Notion 页面，支持分块上传

    Args:
        api_key: Notion API Key
        parent_page_id: 父页面 ID
        title: 页面标题
        content: Markdown 内容

    Returns:
        创建的页面信息
    """
    # 1. 创建空页面
    page = create_notion_page(api_key, parent_page_id, title)
    page_id = page.get("id")

    # 2. 转换 Markdown 为 blocks
    blocks = markdown_to_notion_blocks(content)

    # 3. 分块上传（每次最多 100 个 blocks）
    total_blocks = len(blocks)
    for i in range(0, total_blocks, MAX_BLOCKS_PER_REQUEST):
        chunk = blocks[i:i + MAX_BLOCKS_PER_REQUEST]
        append_blocks_to_page(api_key, page_id, chunk)

    return page


def process_directory(
    api_key: str,
    dir_path: Path,
    parent_page_id: str,
    results: Dict[str, Any],
    custom_title: Optional[str] = None
) -> Optional[str]:
    """
    递归处理目录，创建父页面并上传子内容

    Args:
        api_key: Notion API Key
        dir_path: 目录路径
        parent_page_id: 父页面 ID
        results: 结果统计字典
        custom_title: 自定义父页面标题

    Returns:
        创建的父页面 ID，失败返回 None
    """
    # 创建目录父页面
    dir_title = custom_title if custom_title else dir_path.name

    try:
        dir_page = create_notion_page(api_key, parent_page_id, dir_title)
        dir_page_id = dir_page.get("id")

        results["pages_created"].append({
            "type": "directory",
            "path": str(dir_path),
            "notion_page_id": dir_page_id,
            "url": dir_page.get("url")
        })
    except Exception as e:
        results["errors"].append({
            "path": str(dir_path),
            "error": f"Failed to create directory page: {str(e)}"
        })
        return None

    # 处理目录下的所有条目
    try:
        entries = sorted(dir_path.iterdir())
    except Exception as e:
        results["errors"].append({
            "path": str(dir_path),
            "error": f"Failed to read directory: {str(e)}"
        })
        return dir_page_id

    for entry in entries:
        # 跳过隐藏文件/目录
        if entry.name.startswith('.'):
            continue

        if entry.is_file() and entry.suffix.lower() == '.md':
            # 处理 Markdown 文件
            try:
                content = entry.read_text(encoding='utf-8')
                page_title = entry.stem

                page = upload_markdown_to_page(api_key, dir_page_id, page_title, content)
                results["pages_created"].append({
                    "type": "file",
                    "file": str(entry),
                    "notion_page_id": page.get("id"),
                    "url": page.get("url"),
                    "parent_directory": dir_title
                })
                results["synced_files"].append(str(entry))

            except Exception as e:
                results["errors"].append({
                    "file": str(entry),
                    "error": str(e)
                })

        elif entry.is_dir():
            # 递归处理子目录
            process_directory(api_key, entry, dir_page_id, results)

    return dir_page_id


def sync_markdown_to_notion(
    path: Union[str, Path],
    parent_page_id: Optional[str] = None,
    title: Optional[str] = None
) -> Dict[str, Any]:
    """
    同步 Markdown 文件或目录到 Notion

    Args:
        path: Markdown 文件路径或目录路径
        parent_page_id: Notion 父页面 ID（可选）
        title: 自定义页面标题（对目录为父页面标题，对单文件为页面标题，可选）

    Returns:
        同步结果统计
    """
    api_key = get_notion_api_key()
    if not api_key:
        return {
            "success": False,
            "error": "Notion API key not found in ~/.config/notion/api_key"
        }

    target_path = Path(path)
    if not target_path.exists():
        return {
            "success": False,
            "error": f"Path not found: {path}"
        }

    results = {
        "success": True,
        "synced_files": [],
        "errors": [],
        "pages_created": [],
        "directory_structure": []
    }

    # 处理单文件
    if target_path.is_file():
        if target_path.suffix.lower() != '.md':
            return {
                "success": False,
                "error": f"File is not a markdown file: {path}"
            }

        try:
            content = target_path.read_text(encoding='utf-8')
            page_title = title if title else target_path.stem

            if parent_page_id:
                page = upload_markdown_to_page(api_key, parent_page_id, page_title, content)
                results["pages_created"].append({
                    "type": "file",
                    "file": str(target_path),
                    "notion_page_id": page.get("id"),
                    "url": page.get("url")
                })

            results["synced_files"].append(str(target_path))

        except Exception as e:
            results["errors"].append({
                "file": str(target_path),
                "error": str(e)
            })

    # 处理目录（递归）
    elif target_path.is_dir():
        if not parent_page_id:
            return {
                "success": False,
                "error": "parent_page_id is required for directory upload"
            }

        process_directory(api_key, target_path, parent_page_id, results, title)

    # 更新成功状态
    if results["errors"] and not results["pages_created"]:
        results["success"] = False

    return results


def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("Usage: notion_sync.py <markdown_file_or_directory> <parent_page_id> [title]")
        print("\nExamples:")
        print("  # 上传单个文件")
        print("  python3 notion_sync.py report.md 12345678-1234-1234-1234-123456789abc")
        print("\n  # 上传单个文件并指定标题")
        print("  python3 notion_sync.py report.md 12345678-1234-1234-1234-123456789abc 'My Report'")
        print("\n  # 上传整个目录（会创建目录父页面，子内容作为子页面）")
        print("  python3 notion_sync.py ./reports/ 12345678-1234-1234-1234-123456789abc 'Analysis Reports'")
        print("\n目录上传说明:")
        print("  - 目录上传会递归处理所有子目录")
        print("  - 每个目录会创建一个父页面")
        print("  - Markdown 文件作为对应目录的子页面")
        print("  - 支持嵌套目录结构")
        sys.exit(1)

    path = sys.argv[1]
    parent_page_id = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else None

    result = sync_markdown_to_notion(path, parent_page_id, title)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
