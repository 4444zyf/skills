---
name: github-repo-analyzer
description: |
  分析 GitHub 开源仓库的源代码，生成结构化的分析报告。
  支持生成项目架构概览、代码质量分析、核心模块说明等报告，
  并可选同步到 Notion。
---

# GitHub 仓库分析器

分析 GitHub 开源仓库，生成结构化的 Markdown 分析报告，支持同步到 Notion。

## 工作流程

### 第一步：获取仓库地址

按需询问用户提供 GitHub 仓库地址。格式示例：
- `https://github.com/user/repo`
- `github.com/user/repo`
- `user/repo`

### 第二步：Clone 仓库

1. 在现有目录下创建分析工作目录（使用时间戳命名，如 `analysis-20240314-123045`）
2. 在该目录下创建 `repo/` 子目录用于存放 clone 的代码
3. 执行 `git clone` 命令将仓库 clone 到 `repo/` 目录
4. 验证 clone 成功（检查目录非空）

### 第三步：获取分析要求

询问用户具体的分析要求，例如：
- "分析整体架构和模块关系"
- "检查代码质量和潜在问题"
- "生成 API 接口文档"
- "分析安全漏洞"
- "评估测试覆盖率"
- 或用户的自定义需求

### 第四步：分析仓库

根据用户要求，调用以下工具之一进行深度分析：
- 最优先：`Open Code` - 如果用户已配置
- 次优先：`Claude Code` - 如果用户已配置
- 最后：`Codex` - 如果用户已配置

分析策略：
1. 首先探索仓库结构（README、目录结构、主要配置文件）
2. 识别核心模块和入口文件
3. 针对用户要求，深度分析相关代码
4. 记录关键发现、模式、问题

### 第五步：生成分析报告

在工作目录（与 `repo/` 同级）创建以下 Markdown 文档：

```
analysis-20240314-123045/
├── repo/                    # clone 的仓库代码
├── reports/                 # 分析报告目录
│   ├── 01-主题1.md
│   ├── 02-主题2.md
│   ├── 03-主题3.md
│   └── 04-其他用户要求的主题.md
└── notion-sync.log         # Notion 同步日志（如果启用notion同步脚本）
```

#### 报告内容规范

**01-项目架构概览.md**
- 项目基本信息（名称、描述、技术栈）
- 目录结构说明
- 架构模式（MVC、微服务、分层架构等）
- 关键组件及其关系
- 依赖关系图（用文字描述）

**02-代码质量分析.md**
- 代码规范遵循情况
- 潜在 bug 或问题
- 复杂度分析
- 测试覆盖情况（如有）
- 改进建议

**03-核心模块说明.md**
- 主要模块/包的功能说明
- 关键类/函数的用途
- 数据流分析
- 重要算法或业务逻辑说明

### 第六步：Notion 同步（可选）

检查 `~/.config/notion/api_key` 是否存在：
- 如果存在，询问用户是否同步到 Notion
- 如果用户同意，使用 `scripts/notion_sync.py` 脚本进行同步
- 支持单文件、目录、递归目录上传
- 记录同步日志到 `notion-sync.log`

#### Notion 同步脚本使用说明

**脚本位置**: `scripts/notion_sync.py`

**功能特性**:
- ✅ 单文件 Markdown 上传
- ✅ 目录批量上传（自动创建父页面）
- ✅ 递归目录上传（保持层级结构）
- ✅ 分块上传（支持超过 100 个 blocks 的大文件）
- ✅ 完整的 Markdown 格式支持（代码块、标题、列表、引用等）

**使用方法**:

```bash
# 基本语法
python3 scripts/notion_sync.py <path> <parent_page_id> [title]

# 1. 上传单个文件
python3 scripts/notion_sync.py reports/01-架构.md 12345678-1234-1234-1234-123456789abc

# 2. 上传单个文件并指定标题
python3 scripts/notion_sync.py reports/01-架构.md 12345678-... "项目架构说明"

# 3. 上传整个目录（会创建目录父页面，子内容作为子页面）
python3 scripts/notion_sync.py reports/ 12345678-... "仓库分析报告"

# 4. 目录上传时指定父页面标题
python3 scripts/notion_sync.py reports/ 12345678-... "My Analysis Reports"
```

**参数说明**:
- `path`: Markdown 文件路径或目录路径（必需）
- `parent_page_id`: Notion 父页面 ID（必需）
- `title`: 自定义标题（可选）
  - 单文件：作为页面标题
  - 目录：作为目录父页面标题，默认使用目录名

**Notion 页面结构（目录上传）**:

当上传目录时，脚本会创建层级结构：

```
reports/                          # 本地目录
├── 01-架构.md
├── 02-代码质量.md
├── 03-核心模块.md
└── 详细分析/                     # 子目录
    ├── 数据库设计.md
    └── API设计.md

Notion 结构:
reports (父页面)
├── 01-架构 (子页面)
├── 02-代码质量 (子页面)
├── 03-核心模块 (子页面)
└── 详细分析 (子页面，也是父页)
    ├── 数据库设计 (子子页面)
    └── API设计 (子子页面)
```

**支持的 Markdown 格式**:
- 标题：`#`、`##`、`###`、`####`
- 代码块：```language ... ```（自动识别语言）
- 无序列表：`- ` 或 `* `
- 有序列表：`1.`、`2.`
- 引用块：`> `
- 分隔线：`---` 或 `***`
- 普通段落

**分块上传机制**:
Notion API 限制每次最多 100 个 blocks。对于大文件，脚本会自动：
1. 创建空页面
2. 分批次追加 blocks（每次最多 100 个）
3. 支持无限大小的 Markdown 文件

**API 配置**:
- API 版本: `2022-06-28`
- 认证方式: Bearer Token
- 配置文件: `~/.config/notion/api_key`

**错误处理**:
- API Key 不存在：返回 `{"success": false, "error": "..."}`
- 路径不存在：返回错误信息
- 单文件非 .md 格式：返回错误
- API 调用失败：记录到 `errors` 数组，继续处理其他文件

**输出格式**:
脚本返回 JSON 格式的结果：

```json
{
  "success": true,
  "synced_files": ["/path/to/file1.md", "/path/to/file2.md"],
  "errors": [],
  "pages_created": [
    {
      "type": "directory",
      "path": "/path/to/reports",
      "notion_page_id": "xxx",
      "url": "https://notion.so/xxx"
    },
    {
      "type": "file",
      "file": "/path/to/file1.md",
      "notion_page_id": "xxx",
      "url": "https://notion.so/xxx",
      "parent_directory": "reports"
    }
  ]
}
```

### 第七步：清理（可选）

询问用户是否删除 clone 的仓库：
- 如果用户选择删除，删除 `repo/` 目录但保留 `reports/`
- 如果用户选择保留，告知完整路径

## 重要提示

1. **报告存放位置**：分析报告必须放在与 `repo/` 同级的 `reports/` 目录，不要放在仓库内部
2. **仓库路径**：始终使用 `/github-analysis/analysis-<timestamp>/` 结构
3. **错误处理**：
   - Clone 失败时（网络问题、仓库不存在、权限问题），提示用户并退出
   - 分析工具不可用时，询问用户是否采用当前会话的工具进行分析
   - Notion 同步失败时，记录错误但不中断流程
4. **大仓库处理**：如果仓库文件数超过 10000，提示用户分析可能需要较长时间
5. **敏感信息**：分析报告中如发现 API 密钥、密码等敏感信息，提醒用户注意

## 输出示例

分析完成后，向用户汇报：

```
✅ 仓库分析完成！

📁 分析报告位置：/github-analysis/analysis-20240314-123045/reports/

📄 生成文件：
   - 01-项目架构概览.md
   - 02-代码质量分析.md
   - 03-核心模块说明.md

📊 分析摘要：
   - 技术栈：Python/FastAPI + React
   - 代码文件：127 个
   - 主要问题：发现 3 处潜在问题，详见代码质量分析报告

🔄 Notion 同步：已同步到 https://notion.so/xxx（如适用）

❓ 是否删除 clone 的仓库？(y/n)
```

## Notion 同步脚本技术细节

### 脚本架构

```
scripts/notion_sync.py
├── 配置常量 (NOTION_API_BASE, NOTION_VERSION, MAX_BLOCKS_PER_REQUEST)
├── get_notion_api_key()           # 读取 API Key
├── markdown_to_notion_blocks()    # Markdown 解析器
├── create_notion_page()           # 创建空页面
├── append_blocks_to_page()        # 追加 blocks
├── upload_markdown_to_page()      # 上传单个文件（含分块逻辑）
├── process_directory()            # 递归处理目录
└── sync_markdown_to_notion()      # 主入口函数
```

### 核心函数说明

#### `markdown_to_notion_blocks(content: str) -> List[Dict]`

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

#### `upload_markdown_to_page(api_key, parent_page_id, title, content)`

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

#### `process_directory(api_key, dir_path, parent_page_id, results, custom_title)`

递归处理目录的核心逻辑：

1. 为当前目录创建父页面
2. 遍历目录下所有条目
3. 对于 Markdown 文件：创建子页面并上传内容
4. 对于子目录：递归调用 `process_directory()`
5. 跳过隐藏文件/目录（以 `.` 开头）

### 扩展开发

如需添加新的 Markdown 格式支持，修改 `markdown_to_notion_blocks()`：

```python
# 示例：添加表格支持
elif is_table_line(line):
    table_block = parse_table(lines[i:])
    blocks.append(table_block)
    i += table_block['table']['table_width']
```

### 依赖要求

- Python 3.7+
- 标准库：`os`, `sys`, `json`, `re`, `pathlib`, `typing`, `urllib`
- 无需第三方依赖

---

## 工具检查

在开始分析前，检查以下工具是否可用：

```bash
# 检查 git
command -v git &> /dev/null && echo "git: OK" || echo "git: MISSING"

# 检查 opencode
command -v opencode &> /dev/null && echo "opencode: OK" || echo "opencode: NOT FOUND"

# 检查 claude CLI
command -v claude &> /dev/null && echo "claude: OK" || echo "claude: NOT FOUND"

# 检查 codex
command -v codex &> /dev/null && echo "codex: OK" || echo "codex: NOT FOUND"

# 检查 Notion API 密钥
[ -f ~/.config/notion/api_key ] && echo "notion: CONFIGURED" || echo "notion: NOT CONFIGURED"
```
