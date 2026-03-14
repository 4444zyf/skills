#!/usr/bin/env python3
"""
仓库信息收集工具 - 收集 GitHub 仓库的基本统计信息
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from collections import Counter


def run_git_command(repo_path: str, *args) -> str:
    """运行 git 命令"""
    result = subprocess.run(
        ["git", "-C", repo_path] + list(args),
        capture_output=True,
        text=True
    )
    return result.stdout.strip()


def count_files_by_extension(repo_path: str) -> dict:
    """按扩展名统计文件数量"""
    extensions = Counter()
    total_files = 0

    for root, dirs, files in os.walk(repo_path):
        # 跳过 .git 目录
        dirs[:] = [d for d in dirs if d != '.git']

        for file in files:
            total_files += 1
            ext = Path(file).suffix.lower()
            if ext:
                extensions[ext] += 1
            else:
                extensions['(no extension)'] += 1

    return {
        "total_files": total_files,
        "by_extension": dict(extensions.most_common(20))
    }


def get_git_info(repo_path: str) -> dict:
    """获取 git 相关信息"""
    try:
        # 最近提交信息
        last_commit = run_git_command(repo_path, "log", "-1", "--format=%H|%an|%ae|%ad|%s")

        # 提交总数
        commit_count = run_git_command(repo_path, "rev-list", "--count", "HEAD")

        # 分支数量
        branches = run_git_command(repo_path, "branch", "-a")
        branch_count = len([b for b in branches.split('\n') if b.strip()])

        # 贡献者数量
        contributors = run_git_command(repo_path, "log", "--format=%an")
        contributor_count = len(set(contributors.split('\n')))

        return {
            "commit_count": int(commit_count) if commit_count.isdigit() else 0,
            "branch_count": branch_count,
            "contributor_count": contributor_count,
            "last_commit": last_commit
        }
    except Exception as e:
        return {
            "error": str(e)
        }


def find_key_files(repo_path: str) -> dict:
    """识别关键文件"""
    key_files = {
        "readme": None,
        "license": None,
        "package_json": None,
        "requirements": None,
        "makefile": None,
        "dockerfile": None,
        "docker_compose": None,
        "config_files": []
    }

    for item in Path(repo_path).iterdir():
        name_lower = item.name.lower()

        if name_lower.startswith('readme'):
            key_files["readme"] = item.name
        elif name_lower.startswith('license') or name_lower.startswith('licence'):
            key_files["license"] = item.name
        elif name_lower == 'package.json':
            key_files["package_json"] = item.name
        elif name_lower in ['requirements.txt', 'requirements-dev.txt', 'pyproject.toml', 'setup.py']:
            key_files["requirements"] = item.name
        elif name_lower == 'makefile':
            key_files["makefile"] = item.name
        elif name_lower == 'dockerfile':
            key_files["dockerfile"] = item.name
        elif name_lower in ['docker-compose.yml', 'docker-compose.yaml']:
            key_files["docker_compose"] = item.name
        elif name_lower.endswith(('.yml', '.yaml', '.toml', '.ini', '.cfg', '.conf')):
            key_files["config_files"].append(item.name)

    return key_files


def estimate_code_size(repo_path: str) -> dict:
    """估算代码规模"""
    total_lines = 0
    code_lines = 0
    comment_lines = 0
    blank_lines = 0

    # 代码文件扩展名
    code_extensions = {'.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs',
                       '.cpp', '.c', '.h', '.hpp', '.rb', '.php', '.swift', '.kt',
                       '.scala', '.r', '.m', '.mm', '.cs', '.fs', '.fsx'}

    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [d for d in dirs if d != '.git']

        for file in files:
            ext = Path(file).suffix.lower()
            if ext in code_extensions:
                try:
                    file_path = Path(root) / file
                    if file_path.stat().st_size > 10 * 1024 * 1024:  # 跳过大于 10MB 的文件
                        continue

                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line in f:
                            total_lines += 1
                            stripped = line.strip()
                            if not stripped:
                                blank_lines += 1
                            elif stripped.startswith(('#', '//', '/*', '*', '-#')):
                                comment_lines += 1
                            else:
                                code_lines += 1
                except Exception:
                    pass

    return {
        "total_lines": total_lines,
        "code_lines": code_lines,
        "comment_lines": comment_lines,
        "blank_lines": blank_lines
    }


def analyze_repo(repo_path: str) -> dict:
    """分析仓库并返回综合报告"""
    repo_path = Path(repo_path).resolve()

    if not repo_path.exists():
        return {"error": f"Path does not exist: {repo_path}"}

    if not (repo_path / '.git').exists():
        return {"error": "Not a git repository"}

    result = {
        "repo_path": str(repo_path),
        "repo_name": repo_path.name,
        "file_stats": count_files_by_extension(str(repo_path)),
        "git_info": get_git_info(str(repo_path)),
        "key_files": find_key_files(str(repo_path)),
        "code_size": estimate_code_size(str(repo_path))
    }

    return result


def main():
    """命令行入口"""
    if len(sys.argv) < 2:
        print("Usage: repo_info.py <repository_path>")
        sys.exit(1)

    repo_path = sys.argv[1]
    result = analyze_repo(repo_path)

    print(json.dumps(result, indent=2, ensure_ascii=False))

    sys.exit(0 if "error" not in result else 1)


if __name__ == "__main__":
    main()
