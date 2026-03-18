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


def make_notion_api_request(api_key: str, endpoint: str, method: str = "GET",
                            data: Optional[Dict] = None) -> Dict[str, Any]:
    """发送 Notion API 请求"""
    import urllib.request
    import urllib.error

    url = f"{NOTION_API_BASE}{endpoint}"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Notion-Version": NOTION_VERSION
    }

    req_data = json.dumps(data).encode('utf-8') if data else None

    req = urllib.request.Request(
        url,
        data=req_data,
        headers=headers,
        method=method
    )

    try:
        with urllib.request.urlopen(req) as response:
            return json.loads(response.read().decode('utf-8'))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode('utf-8')
        raise Exception(f"Notion API error: {error_body}")


def search_notion_pages(api_key: str, query: str = "", page_size: int = 100) -> Dict[str, Any]:
    """
    搜索 Notion 页面

    Args:
        api_key: Notion API Key
        query: 搜索关键词（可选）
        page_size: 返回结果数量（最大 100）

    Returns:
        搜索结果，包含页面列表
    """
    data = {
        "query": query,
        "filter": {
            "value": "page",
            "property": "object"
        },
        "page_size": min(page_size, 100)
    }

    return make_notion_api_request(api_key, "/search", method="POST", data=data)


def get_page_info(api_key: str, page_id: str) -> Dict[str, Any]:
    """
    获取特定页面的详细信息

    Args:
        api_key: Notion API Key
        page_id: 页面 ID

    Returns:
        页面详细信息
    """
    return make_notion_api_request(api_key, f"/pages/{page_id}", method="GET")


def list_available_pages(api_key: str, query: str = "") -> Dict[str, Any]:
    """
    列出所有可用的父页面（可作为上传目标的页面）

    Args:
        api_key: Notion API Key
        query: 可选的搜索关键词

    Returns:
        包含页面列表的结果字典
    """
    results = {
        "success": True,
        "pages": [],
        "total": 0,
        "error": None
    }

    try:
        response = search_notion_pages(api_key, query)
        pages = response.get("results", [])

        for page in pages:
            page_info = {
                "id": page.get("id"),
                "title": "",
                "url": page.get("url"),
                "created_time": page.get("created_time"),
                "last_edited_time": page.get("last_edited_time"),
                "archived": page.get("archived", False)
            }

            # 提取页面标题
            properties = page.get("properties", {})
            if "title" in properties:
                title_data = properties["title"]
                if "title" in title_data:
                    title_parts = [t.get("text", {}).get("content", "")
                                   for t in title_data["title"]]
                    page_info["title"] = "".join(title_parts)

            results["pages"].append(page_info)

        results["total"] = len(results["pages"])

    except Exception as e:
        results["success"] = False
        results["error"] = str(e)

    return results


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
    if len(sys.argv) < 2:
        print("Usage: notion_sync.py <command> [options]")
        print("\nCommands:")
        print("  upload <path> <parent_page_id> [title]  上传 Markdown 到 Notion")
        print("  list [query]                            列出可用的父页面")
        print("  info <page_id>                          获取页面详细信息")
        print("\nExamples:")
        print("  # 列出所有可用页面")
        print("  python3 notion_sync.py list")
        print("\n  # 搜索特定页面")
        print("  python3 notion_sync.py list \"My Project\"")
        print("\n  # 获取页面详细信息")
        print("  python3 notion_sync.py info 12345678-1234-1234-1234-123456789abc")
        print("\n  # 上传单个文件")
        print("  python3 notion_sync.py upload report.md 12345678-1234-1234-1234-123456789abc")
        print("\n  # 上传单个文件并指定标题")
        print("  python3 notion_sync.py upload report.md 12345678-... 'My Report'")
        print("\n  # 上传整个目录（会创建目录父页面，子内容作为子页面）")
        print("  python3 notion_sync.py upload ./reports/ 12345678-... 'Analysis Reports'")
        sys.exit(1)

    command = sys.argv[1]

    # 处理 list 命令
    if command == "list":
        api_key = get_notion_api_key()
        if not api_key:
            print(json.dumps({
                "success": False,
                "error": "Notion API key not found in ~/.config/notion/api_key"
            }, indent=2, ensure_ascii=False))
            sys.exit(1)

        query = sys.argv[2] if len(sys.argv) > 2 else ""
        result = list_available_pages(api_key, query)

        # 格式化输出
        if result["success"]:
            print(f"\n找到 {result['total']} 个页面:\n")
            print(f"{'序号':<6}{'页面标题':<40}{'页面 ID':<40}{'URL':<30}")
            print("-" * 120)
            for idx, page in enumerate(result["pages"], 1):
                title = page["title"][:38] if page["title"] else "(无标题)"
                page_id = page["id"]
                url = page["url"][:28] if page["url"] else ""
                print(f"{idx:<6}{title:<40}{page_id:<40}{url:<30}")
            print("\n提示: 使用页面 ID 作为 parent_page_id 进行上传")
        else:
            print(f"错误: {result['error']}")
            sys.exit(1)

        sys.exit(0)

    # 处理 info 命令
    if command == "info":
        if len(sys.argv) < 3:
            print("Usage: notion_sync.py info <page_id>")
            print("\nExample:")
            print("  python3 notion_sync.py info 12345678-1234-1234-1234-123456789abc")
            sys.exit(1)

        api_key = get_notion_api_key()
        if not api_key:
            print(json.dumps({
                "success": False,
                "error": "Notion API key not found in ~/.config/notion/api_key"
            }, indent=2, ensure_ascii=False))
            sys.exit(1)

        page_id = sys.argv[2]
        try:
            page_info = get_page_info(api_key, page_id)
            print(json.dumps(page_info, indent=2, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({
                "success": False,
                "error": str(e)
            }, indent=2, ensure_ascii=False))
            sys.exit(1)

        sys.exit(0)

    # 处理 upload 命令
    if command == "upload":
        if len(sys.argv) < 4:
            print("Usage: notion_sync.py upload <path> <parent_page_id> [title]")
            print("\nExample:")
            print("  python3 notion_sync.py upload report.md 12345678-1234-1234-1234-123456789abc")
            sys.exit(1)

        path = sys.argv[2]
        parent_page_id = sys.argv[3]
        title = sys.argv[4] if len(sys.argv) > 4 else None

        result = sync_markdown_to_notion(path, parent_page_id, title)

        print(json.dumps(result, indent=2, ensure_ascii=False))

        sys.exit(0 if result["success"] else 1)

    # 向后兼容：如果没有指定命令，默认使用 upload（旧版本用法）
    # 检测旧格式：第二个参数看起来像 page_id (UUID 格式 或包含特定字符)
    if len(sys.argv) >= 3:
        potential_page_id = sys.argv[2]
        # UUID 格式检测: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        # 或者简化的检测：长度较长且包含 - 符号
        if (len(potential_page_id) >= 20 and '-' in potential_page_id) or \
           potential_page_id.startswith(("1234", "abcd", "http")):
            # 旧格式: notion_sync.py <path> <parent_page_id> [title]
            path = sys.argv[1]
            parent_page_id = sys.argv[2]
            title = sys.argv[3] if len(sys.argv) > 3 else None

            result = sync_markdown_to_notion(path, parent_page_id, title)

            print(json.dumps(result, indent=2, ensure_ascii=False))

            sys.exit(0 if result["success"] else 1)

    # 未知命令
    print(f"未知命令: {command}")
    print("可用命令: upload, list, info")
    sys.exit(1)


if __name__ == "__main__":
    main()
