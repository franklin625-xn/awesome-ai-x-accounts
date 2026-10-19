"""Validate the original 100-account snapshot using only the standard library."""

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "accounts.json"
SOURCE = "isituking-2026-x100"
GROUPS = (
    (1, "实验室掌舵人：行业方向的一手信号", 1, 7),
    (2, "官方实验室：模型发布第一现场", 8, 18),
    (3, "官方产品与产品负责人：新功能最先知道", 19, 26),
    (4, "顶级研究者：看懂 AI 底层", 27, 41),
    (5, "AI 编程与 Agent：一线实践派", 42, 49),
    (6, "开源与基础设施", 50, 52),
    (7, "中文圈｜产品、业务与出海", 53, 68),
    (8, "中文圈｜消息、研究与解读", 69, 78),
    (9, "中文圈｜编程、开源与 Agent", 79, 92),
    (10, "中文圈｜视觉与内容创作", 93, 100),
)
FIELDS = {
    "id", "name", "handle", "url", "group_id", "language_group",
    "focus", "source", "verified_at",
}


def validate_accounts(accounts):
    """Return all actionable errors without assuming well-typed input."""
    errors = []
    if not isinstance(accounts, list):
        return ["JSON 顶层必须是数组。"]
    if len(accounts) != 100:
        errors.append(f"账号总数应为 100，实际为 {len(accounts)}。")

    ids, handles, groups = [], [], []
    for position, account in enumerate(accounts, 1):
        label = f"第 {position} 条"
        if not isinstance(account, dict):
            errors.append(f"{label}必须是对象。")
            continue
        missing = FIELDS - account.keys()
        extra = account.keys() - FIELDS
        if missing:
            errors.append(f"{label}缺少字段：{', '.join(sorted(missing))}。")
        if extra:
            errors.append(f"{label}未知字段：{', '.join(sorted(extra))}。")

        account_id = account.get("id")
        group_id = account.get("group_id")
        if type(account_id) is not int or not 1 <= account_id <= 100:
            errors.append(f"{label} id 必须是 1–100 的整数。")
        else:
            ids.append(account_id)
            if account_id != position:
                errors.append(f"{label} id 应为 {position}，必须保持原始顺序。")
            expected_group = next(g for g, _, start, end in GROUPS
                                  if start <= account_id <= end)
            if group_id != expected_group:
                errors.append(f"{label}应属于第 {expected_group} 组。")

        if type(group_id) is not int or not 1 <= group_id <= 10:
            errors.append(f"{label} group_id 必须是 1–10 的整数。")
        else:
            groups.append(group_id)
            expected_language = "en" if group_id <= 6 else "zh"
            if account.get("language_group") != expected_language:
                errors.append(f"{label} language_group 应为 {expected_language}。")

        for field in ("name", "handle", "url", "focus", "source", "language_group"):
            value = account.get(field)
            if not isinstance(value, str) or not value.strip():
                errors.append(f"{label} {field} 必须是非空字符串。")
            elif value != value.strip() or any(c in value for c in "\r\n\x00"):
                errors.append(f"{label} {field} 不能包含首尾空白、换行或空字符。")

        handle = account.get("handle")
        if isinstance(handle, str):
            handles.append(handle.casefold())
            if not re.fullmatch(r"[A-Za-z0-9_]{1,15}", handle):
                errors.append(f"{label} handle 格式无效（不要包含 @）。")
            if account.get("url") != f"https://x.com/{handle}":
                errors.append(f"{label} url 必须严格对应 https://x.com/<handle>。")
        if account.get("source") != SOURCE:
            errors.append(f"{label} source 应为 {SOURCE}。")

        verified_at = account.get("verified_at")
        if verified_at is not None:
            if not isinstance(verified_at, str) or not re.fullmatch(
                r"\d{4}-\d{2}-\d{2}", verified_at
            ):
                errors.append(f"{label} verified_at 必须为 null 或 YYYY-MM-DD。")
            else:
                try:
                    if date.fromisoformat(verified_at) > date.today():
                        errors.append(f"{label} verified_at 不能是未来日期。")
                except ValueError:
                    errors.append(f"{label} verified_at 不是有效日期。")

    if sorted(ids) != list(range(1, 101)):
        errors.append("ID 必须无重复、无遗漏，恰好覆盖 1–100。")
    duplicates = [handle for handle, count in Counter(handles).items() if count > 1]
    if duplicates:
        errors.append(f"handle 忽略大小写后重复：{', '.join(duplicates)}。")
    counts = Counter(groups)
    for group_id, _, start, end in GROUPS:
        expected = end - start + 1
        if counts[group_id] != expected:
            errors.append(f"第 {group_id} 组应有 {expected} 条，实际为 {counts[group_id]}。")
    return errors


def reject_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"JSON 对象包含重复字段：{key}")
        result[key] = value
    return result


def load_accounts(path=DATA_PATH):
    accounts = json.loads(Path(path).read_text(encoding="utf-8"),
                          object_pairs_hook=reject_duplicate_keys)
    errors = validate_accounts(accounts)
    if errors:
        raise ValueError("\n".join(errors))
    return accounts


def main():
    parser = argparse.ArgumentParser(description="检查 100 账号快照的完整性与字段格式。")
    parser.add_argument("--data", type=Path, default=DATA_PATH)
    args = parser.parse_args()
    try:
        accounts = load_accounts(args.data)
    except (OSError, ValueError) as error:
        print(f"校验失败：\n{error}", file=sys.stderr)
        return 1
    counts = Counter(account["group_id"] for account in accounts)
    print("校验通过：100 条账号、10 组；英文分区 52 条、中文分区 48 条。")
    print("每组数量：" + ", ".join(str(counts[g]) for g in range(1, 11)))
    print("此检查仅验证数据结构与链接格式，不代表已独立核验 X 账号身份或在线状态。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
