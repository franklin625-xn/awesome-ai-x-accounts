"""Validate the independent selection and its evidence trail, offline."""

import json
from collections import Counter
from datetime import date
import re
import sys
from urllib.parse import urlsplit

from validate import ROOT, load_accounts, reject_duplicate_keys

CURATED_PATH = ROOT / "data" / "curated80.json"
RESEARCH_PATH = ROOT / "data" / "research_notes.json"
STATUSES = {"supported", "limited", "pending"}
FIELDS = {
    "order", "original_id", "name", "handle", "url", "category", "language_group",
    "advantage", "audience", "selection_reason", "evidence_urls", "research_date",
    "evidence_status", "verified_at",
}


def valid_date(value):
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        return date.fromisoformat(value) <= date.today()
    except ValueError:
        return False


def valid_url(value):
    if not isinstance(value, str) or re.search(r"[\s<>\[\]()\\]", value):
        return False
    try:
        parsed = urlsplit(value)
        return parsed.scheme == "https" and bool(parsed.hostname) and not parsed.username
    except ValueError:
        return False


def nonempty(value):
    return (isinstance(value, str) and bool(value.strip()) and value == value.strip()
            and not any(c in value for c in "\r\n\x00"))


def validate_curated(accounts, original, research):
    errors = []
    if not isinstance(accounts, list):
        return ["精选 JSON 必须是数组。"]
    if len(accounts) != 80:
        errors.append("精选应恰好为 80 条。")
    original_by_id = {a["id"]: a for a in original}
    if not isinstance(research, dict) or not isinstance(research.get("records"), list):
        return errors + ["研究记录必须包含 records 数组。"]
    research_date = research.get("research_date")
    if not valid_date(research_date):
        errors.append("研究日期无效。")
    notes = research["records"]
    note_by_id = {}
    for position, note in enumerate(notes, 1):
        if not isinstance(note, dict):
            errors.append(f"研究第 {position} 条不是对象。")
            continue
        note_id = note.get("id")
        if type(note_id) is not int or note_id not in original_by_id:
            errors.append(f"研究第 {position} 条原编号无效。")
            continue
        if note_id in note_by_id:
            errors.append(f"研究记录重复原编号 {note_id}。")
        note_by_id[note_id] = note
        for field in ("finding", "reason", "audience"):
            if not nonempty(note.get(field)):
                errors.append(f"研究 #{note_id} {field} 不能为空。")
        if not isinstance(note.get("attempts"), list) or not all(
            nonempty(v) for v in note.get("attempts", [])
        ):
            errors.append(f"研究 #{note_id} attempts 应为字符串数组。")
        sources = note.get("sources")
        if not isinstance(sources, list) or not all(valid_url(v) for v in sources):
            errors.append(f"研究 #{note_id} 来源 URL 格式错误。")
        status = note.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            errors.append(f"研究 #{note_id} 核验状态无效。")
        elif status == "pending":
            if note.get("advantage") is not None or sources:
                errors.append(f"研究 #{note_id} 待核验不能伪装成已证实优势。")
        elif not nonempty(note.get("advantage")) or not sources:
            errors.append(f"研究 #{note_id} 有依据状态必须有优势和来源。")
    if sorted(note_by_id) != list(range(1, 101)) or len(notes) != 100:
        errors.append("研究记录应覆盖全部 100 个候选，无遗漏或重复。")

    ids, handles = [], []
    for position, account in enumerate(accounts, 1):
        label = f"精选第 {position} 条"
        if not isinstance(account, dict):
            errors.append(f"{label}不是对象。")
            continue
        if set(account) != FIELDS:
            errors.append(f"{label}字段不完整或包含未知字段。")
        if type(account.get("order")) is not int or account["order"] != position:
            errors.append(f"{label} order 应保持连续顺序。")
        original_id = account.get("original_id")
        if type(original_id) is not int or original_id not in original_by_id:
            errors.append(f"{label} original_id 无效。")
            continue
        ids.append(original_id)
        source = original_by_id[original_id]
        for field in ("name", "handle", "url", "language_group"):
            if account.get(field) != source[field]:
                errors.append(f"{label} {field} 与原快照映射不符。")
        if type(account.get("category")) is not int or account["category"] != source["group_id"]:
            errors.append(f"{label}类别应对应原分组。")
        handles.append(source["handle"].casefold())
        for field in ("audience", "selection_reason"):
            if not nonempty(account.get(field)):
                errors.append(f"{label} {field} 必须非空。")
        if not valid_date(account.get("research_date")) or account.get("research_date") != research_date:
            errors.append(f"{label}研究日期与研究记录不一致。")
        note = note_by_id.get(original_id)
        if note:
            mapping = {"advantage": "advantage", "audience": "audience",
                       "selection_reason": "reason", "evidence_urls": "sources",
                       "evidence_status": "status"}
            for field, note_field in mapping.items():
                if account.get(field) != note.get(note_field):
                    errors.append(f"{label} {field} 与研究记录不一致。")
        if account.get("verified_at") is not None:
            errors.append(f"{label}本轮未核验 X 当前状态，verified_at 应为 null。")
    if len(set(ids)) != len(ids) or len(set(handles)) != len(handles):
        errors.append("精选原编号或 handle 重复。")
    if len(set(original_by_id) - set(ids)) != 20:
        errors.append("应恰好有 20 个未纳入候选。")
    return errors


def load_curated():
    original = load_accounts()
    accounts = json.loads(CURATED_PATH.read_text(encoding="utf-8"),
                          object_pairs_hook=reject_duplicate_keys)
    research = json.loads(RESEARCH_PATH.read_text(encoding="utf-8"),
                          object_pairs_hook=reject_duplicate_keys)
    errors = validate_curated(accounts, original, research)
    if errors:
        raise ValueError("\n".join(errors))
    return accounts, original, research


def main():
    try:
        accounts, _, _ = load_curated()
    except (OSError, ValueError) as error:
        print(f"精选校验失败：\n{error}", file=sys.stderr)
        return 1
    counts = Counter(a["evidence_status"] for a in accounts)
    print("精选校验通过：80 条、20 个未纳入候选；全部 100 个候选有研究/尝试记录。")
    print(f"公开依据：{counts['supported']}；有限依据：{counts['limited']}；待核验：{counts['pending']}。")
    print("以上为材料范围检查，不证明优势客观排名、X 内容或账号当前状态。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
