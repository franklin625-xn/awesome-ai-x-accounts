"""Generate the selection and research report from locally reviewed records."""

import argparse
from collections import Counter
import sys

from generate_readme import escape_cell
from validate import GROUPS, ROOT
from validate_curated import load_curated

STATUS_LABELS = {
    "supported": "公开依据",
    "limited": "有限依据",
    "pending": "待核验",
}
TITLES = (
    "行业战略与科学方向", "模型与实验室入口", "产品与开发者入口",
    "研究与学习", "AI 编程与 Agent 工程", "开放生态与运行工具",
    "中文产品、业务与出海", "中文资讯与研究解读", "中文开发与开源",
    "视觉与内容创作",
)


def evidence_links(urls):
    return " · ".join(f"[依据 {i}]({url})" for i, url in enumerate(urls, 1)) or "未取得公开依据"


def replace_block(text, start, end, content):
    if text.count(start) != 1 or text.count(end) != 1:
        raise ValueError(f"文档应恰好包含一对 {start} / {end} 标记。")
    left = text.index(start) + len(start)
    right = text.index(end)
    if left > right:
        raise ValueError("生成标记顺序错误。")
    return text[:left] + "\n\n" + content.rstrip() + "\n\n" + text[right:]


def render_curated(accounts):
    counts = Counter(a["category"] for a in accounts)
    lines = ["## 分类导航", "", "| 类别 | 数量 |", "|---|---:|"]
    for category, title in enumerate(TITLES, 1):
        lines.append(f"| [{title}](#curated-{category}) | {counts[category]} |")
    lines.extend(["", "共 **80 个账号、10 个分类**。编号方便阅读，不代表排名。", ""])
    for category, title in enumerate(TITLES, 1):
        lines.extend([f'<a id="curated-{category}"></a>', "", f"### {title}（{counts[category]} 个）", "", "| 编号 | 名称 / X | 关注方向 |", "|---:|---|---|"])
        for a in accounts:
            if a["category"] != category:
                continue
            focus = a["advantage"] or f"分类导航：{title}"
            if a["evidence_status"] == "limited":
                focus = {
                    6: "AI 社会影响、风险与发展议题。",
                    12: "Meta AI 产品、模型与研究。",
                    21: "Gemini 应用与写作、规划、学习。",
                    35: "进化算法与群体学习。",
                    41: "AI 研究通讯与分析。",
                    42: "AI 应用界面与部署。",
                    43: "Claude Code 与开发者工具。",
                    46: "自然语言构建应用与部署。",
                    57: "工程实验、产品与团队协作。",
                    61: "费曼式学习与知识整理。",
                    82: "浏览器端图像处理、WebGPU 与 WASM 项目。",
                    88: "个人博客与中文工程阅读入口。",
                    97: "结构化提示写作与学习、写作技能。",
                    100: "设计资源、产品设计通讯与学习社区。",
                }.get(a["original_id"], f"分类导航：{title}")
            lines.append(f'| {a["order"]} | {escape_cell(a["name"])} [@{a["handle"]}]({a["url"]}) | {escape_cell(focus)} |')
        lines.append("")
    return "\n".join(lines)


def render_research(accounts, original, research):
    selected = {a["original_id"] for a in accounts}
    notes = {n["id"]: n for n in research["records"]}
    status = Counter(n["status"] for n in research["records"])
    lines = ["## 研究覆盖与局限", "", f'研究日期：**{research["research_date"]}**。全部 100 个候选有查阅或失败尝试记录，不等于全部研究成功。', "", f"有公开依据 {status['supported']} 条；有限依据 {status['limited']} 条；待核验 {status['pending']} 条。", "", "未读取全部推文，未测试产品性能，未独立确认 X 账号当前状态。网页里的自述、文章目录和组织功能不可直接证明个人推文质量或活跃度。", "", "## 20 个未纳入账号及取舍理由", "", "缺证账号间无法客观比较；相关取舍是控制数量的暂定编辑选择，不是‘更差’的结论。", "", "| 原编号 | 账号 | 本次未纳入理由 |", "|---:|---|---|"]
    for a in original:
        if a["id"] not in selected:
            n = notes[a["id"]]
            lines.append(f'| {a["id"]} | {escape_cell(a["name"])} [@{a["handle"]}]({a["url"]}) | {escape_cell(n["reason"])} |')
    lines.extend(["", "## 100 个候选的逐项记录", ""])
    for group_id, title, _, _ in GROUPS:
        lines.extend([f"### 原第 {group_id} 组：{title}", ""])
        for a in original:
            if a["group_id"] != group_id:
                continue
            n = notes[a["id"]]
            disposition = "纳入 80 条" if a["id"] in selected else "未纳入"
            lines.extend([f'#### 原 #{a["id"]}：{a["name"]} / @{a["handle"]}', "", f'- 选择：{disposition}；材料状态：**{STATUS_LABELS[n["status"]]}**。', f'- 实际取得：{n["finding"]}', f'- 特色与限制：{n["advantage"] or "未取得足够依据，不编写个人优势。"}', f'- 适合：{n["audience"]}。', f'- 选择依据：{n["reason"]}', f'- 可读来源：{evidence_links(n["sources"])}。'])
            for attempt in n["attempts"]:
                lines.append(f"- 失败尝试 / 不能采用的线索：{attempt}")
            lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="生成 80 条精选及 100 候选研究报告。")
    parser.add_argument("--check", action="store_true", help="只检查，不写文件")
    args = parser.parse_args()
    try:
        accounts, original, research = load_curated()
        documents = [
            (ROOT / "README.md", "<!-- CURATED:START -->", "<!-- CURATED:END -->", render_curated(accounts)),
            (ROOT / "docs" / "RESEARCH.md", "<!-- RESEARCH:START -->", "<!-- RESEARCH:END -->", render_research(accounts, original, research)),
        ]
        updates = []
        for path, start, end, content in documents:
            text = path.read_bytes().decode("utf-8")
            updated = replace_block(text, start, end, content)
            if text != updated:
                updates.append((path, updated))
        if args.check and updates:
            print("生成一致性检查失败：" + ", ".join(str(p.relative_to(ROOT)) for p, _ in updates), file=sys.stderr)
            return 1
        for path, text in updates:
            path.write_bytes(text.encode("utf-8"))
        print("精选与研究报告一致性检查通过。" if not updates else "已生成 80 条精选与 100 候选研究记录。")
    except (OSError, ValueError) as error:
        print(f"精选生成失败：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
