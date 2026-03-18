# Notion 同步脚本技术细节

本文档详细介绍 `scripts/notion_sync.py` 的实现细节，供需要深入了解或扩展功能的开发者参考。

## 脚本架构

```
scripts/notion_sync.py
├── 配置常量 (NOTION_API_BASE, NOTION_VERSION, MAX_BLOCKS_PER_REQUEST)
├── get_notion_api_key()           # 读取 API Key
├── make_notion_api_request()      # 通用 API 请求
├── search_notion_pages()          # 搜索页面
├── get_page_info()                # 获取页面详情
├── list_available_pages()         # 列出可用页面
├── markdown_to_notion_blocks()    # Markdown 解析器
├── create_notion_page()           # 创建空页面
├── append_blocks_to_page()        # 追加 blocks
├── upload_markdown_to_page()      # 上传单个文件（含分块逻辑）
├── process_directory()            # 递归处理目录
├── sync_markdown_to_notion()      # 主入口函数
└── main()                         # 命令行入口
```

## 核心函数说明

### `make_notion_api_request(api_key: str, endpoint: str, method: str = "GET", data: Optional[Dict] = None) -> Dict`

通用 Notion API 请求封装函数，处理所有 API 调用的通用逻辑。

**参数**:
- `api_key`: Notion API Key
- `endpoint`: API 端点路径（如 `/pages/xxx`）
- `method`: HTTP 方法（GET/POST/PATCH）
- `data`: 请求体数据（可选，用于 POST/PATCH）

**返回**: API 响应的 JSON 数据

**示例**:
```python
# GET 请求
page_info = make_notion_api_request(api_key, "/pages/xxx", method="GET")

# POST 请求
search_data = {"query": "My Project", "filter": {"value": "page", "property": "object"}}
results = make_notion_api_request(api_key, "/search", method="POST", data=search_data)
```

### `search_notion_pages(api_key: str, query: str = "", page_size: int = 100) -> Dict`

搜索 Notion 中可作为上传目标的页面。

**参数**:
- `api_key`: Notion API Key
- `query`: 搜索关键词（可选）
- `page_size`: 返回结果数量（最大 100）

**示例**:
```python
# 列出所有页面
results = search_notion_pages(api_key)

# 搜索特定页面
results = search_notion_pages(api_key, query="Reports")
```

### `get_page_info(api_key: str, page_id: str) -> Dict`

获取特定页面的详细信息。

**参数**:
- `api_key`: Notion API Key
- `page_id`: 页面 ID

**返回**: 页面详细信息，包括标题、属性、URL 等

### `list_available_pages(api_key: str, query: str = "") -> Dict`

列出所有可用的父页面，返回格式化的结果。

**返回示例**:
```python
{
    "success": True,
    "pages": [
        {
            "id": "12345678-...",
            "title": "My Project",
            "url": "https://notion.so/...",
            "created_time": "2024-03-14T12:30:00.000Z",
            "last_edited_time": "2024-03-14T12:30:00.000Z",
            "archived": False
        }
    ],
    "total": 1
}
```

### `markdown_to_notion_blocks(content: str) -> List[Dict]`

将 Markdown 文本转换为 Notion Block 对象列表。

**状态机设计**：使用状态机处理代码块，确保多行代码块被正确识别。

```python
# 代码块处理逻辑
if line.startswith('```'):
    if not in_code_block:
        in_code_block = True  # 开始代码块
        code_language = extract_language(line)
    else:
        in_code_block = False  # 结束代码块
        blocks.append(create_code_block(...))
```

### `upload_markdown_to_page(api_key, parent_page_id, title, content)`

支持大文件分块上传：

```python
# 1. 创建空页面
page = create_notion_page(api_key, parent_page_id, title)
page_id = page.get("id")

# 2. 转换 Markdown
blocks = markdown_to_notion_blocks(content)

# 3. 分块上传
for i in range(0, len(blocks), MAX_BLOCKS_PER_REQUEST):
    chunk = blocks[i:i + MAX_BLOCKS_PER_REQUEST]
    append_blocks_to_page(api_key, page_id, chunk)
```

### `process_directory(api_key, dir_path, parent_page_id, results, custom_title)`

递归处理目录的核心逻辑：

1. 为当前目录创建父页面
2. 遍历目录下所有条目
3. 对于 Markdown 文件：创建子页面并上传内容
4. 对于子目录：递归调用 `process_directory()`
5. 跳过隐藏文件/目录（以 `.` 开头）

## 扩展开发

如需添加新的 Markdown 格式支持，修改 `markdown_to_notion_blocks()`：

```python
# 示例：添加表格支持
elif is_table_line(line):
    table_block = parse_table(lines[i:])
    blocks.append(table_block)
    i += table_block['table']['table_width']
```

## 依赖要求

- Python 3.7+
- 标准库：`os`, `sys`, `json`, `re`, `pathlib`, `typing`, `urllib`
- 无需第三方依赖

## API 配置参考

- **API 版本**: `2022-06-28`
- **认证方式**: Bearer Token
- **配置文件**: `~/.config/notion/api_key`
- **Base URL**: `https://api.notion.com/v1`

## 错误码说明

| 错误场景 | 返回值 |
|---------|--------|
| API Key 不存在 | `{"success": false, "error": "Notion API key not found..."}` |
| 路径不存在 | `{"success": false, "error": "Path not found: ..."}` |
| 文件格式错误 | `{"success": false, "error": "File is not a markdown file..."}` |
| API 调用失败 | 错误信息记录到 `errors` 数组 |
