"""Render the account index; keep manually maintained README text intact."""

import argparse
from pathlib import Path
import sys

from validate import GROUPS, ROOT, load_accounts

START = "<!-- ACCOUNTS:START -->"
END = "<!-- ACCOUNTS:END -->"
README_PATH = ROOT / "docs" / "ORIGINAL_100.md"


def escape_cell(value):
    for character in "\\`*_{}[]<>#":
        value = value.replace(character, "\\" + character)
    return value.replace("|", "&#124;")


def render_accounts(accounts):
    lines = ["## 分类导航", "", "| 组 | 分类 | 数量 |", "|---:|---|---:|"]
    for group_id, title, start, end in GROUPS:
        lines.append(f"| {group_id} | [{title}](#group-{group_id}) | {end - start + 1} |")
    lines.extend(["", "共 **100 个账号**：英文分区 52 个，中文分区 48 个。分区沿用原文，不代表账号实际发帖语言。", "", "## 完整账号列表", ""])
    for group_id, title, start, end in GROUPS:
        lines.extend([f'<a id="group-{group_id}"></a>', "", f"### 第 {group_id} 组：{title}（{end - start + 1} 个）", "", "| 编号 | 账号名称 | X 账号 | 关注主题 |", "|---:|---|---|---|"])
        for account in accounts:
            if account["group_id"] == group_id:
                lines.append(f'| #{account["id"]} | {escape_cell(account["name"])} | [@{account["handle"]}]({account["url"]}) | {escape_cell(account["focus"])} |')
        lines.append("")
    return "\n".join(lines).rstrip()


def update_readme(text, accounts):
    if text.count(START) != 1 or text.count(END) != 1:
        raise ValueError("README 必须恰好包含一对 ACCOUNTS 标记。")
    start = text.index(START) + len(START)
    end = text.index(END)
    if start > end:
        raise ValueError("README 的 ACCOUNTS 标记顺序错误。")
    return text[:start] + "\n\n" + render_accounts(accounts) + "\n\n" + text[end:]


def main():
    parser = argparse.ArgumentParser(description="从 accounts.json 生成 README 账号区。")
    parser.add_argument("--check", action="store_true", help="只检查一致性，不修改文件")
    args = parser.parse_args()
    try:
        accounts = load_accounts()
        original = README_PATH.read_bytes().decode("utf-8")
        updated = update_readme(original, accounts)
        if updated == original:
            print("README 一致性检查通过：无需更新。")
        elif args.check:
            print("README 一致性检查失败：请运行生成脚本。", file=sys.stderr)
            return 1
        else:
            README_PATH.write_bytes(updated.encode("utf-8"))
            print("README 账号区已更新：10 组、100 个账号。")
    except (OSError, ValueError) as error:
        print(f"生成失败：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
