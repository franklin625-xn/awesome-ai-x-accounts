# 贡献指南

感谢帮助维护这份导航。本项目区分司徒K的原始 100 条快照与独立的 80 条精选草案。原快照不重新评选或排序；精选可以在公开依据和明确取舍下调整，但不冒称原作者的榜单。

## 纠错与核验

通过 Issue 或 PR 提供原始编号、现有 handle、问题、建议修改及可追溯证据链接。可处理名称变更、handle 迁移、失效链接、过时说明和身份核验。

1. 只编辑 `data/accounts.json` 中对应条目；保留 `id`、`group_id`、`language_group`、`source`，不能删条、挪组或重排。
2. 名称或 handle 变化时，在 `docs/SOURCES.md` 的变更记录中写明原值、新值、原编号、证据与日期，保留来源映射。URL 同步为 `https://x.com/<handle>`。
3. 说明必须独立、简短且有依据，不复制原文推荐文案；不能凭记忆填写当前职位、粉丝数或活跃度。
4. `verified_at` 只有在独立核查身份或当前资料后才能填写 `YYYY-MM-DD`，并在来源文档记录核验范围和证据。只检查链接格式或引用原作者自述，仍应保持 `null`。
5. 运行以下命令并提交数据、生成的 README 和相关证据文档。不要手改 README 的自动生成区。

```bash
python scripts/validate.py
```

```bash
python scripts/generate_readme.py
```

```bash
python scripts/generate_readme.py --check
```

```bash
python -m unittest discover -s tests -v
```

脚本需要 Python 3.10+，只使用标准库，无需 Token 或环境变量。CI 不访问 X，不证明账号当前可用。

## 精选补证与调整

待核验条目需要本人公开文章、作品或官方资料，并明确与 X handle 的关联。修改 `data/research_notes.json` 对应记录；精选展示字段在 `data/curated80.json` 同步更新，脚本会检查它们一致。

材料只是目录、旧作品、自述或缺少 X 关联时，不升级为充分证据。失败 URL 只作为 attempts，不当作 evidence_urls。个人、组织及置顶项目的作者归属要区分；不能凭同名或 fork 认定身份及原创。

替换精选须维持 80 条并更新 20 个未纳入候选的理由，不修改原始快照。执行以下命令，并同时运行原快照命令和测试：

```bash
python scripts/validate_curated.py
```

```bash
python scripts/generate_curated.py
```

```bash
python scripts/generate_curated.py --check
```

`generate_readme.py` 现在生成 `docs/ORIGINAL_100.md`；`generate_curated.py` 生成首页及研究报告。

## 推荐新账号

先提交推荐 Issue，提供名称、handle、链接、关注主题、公开内容示例与推荐理由。**不要直接加入原始 100 条数据**。

若未来启用社区名单，应另建 `data/community.json` 和独立展示区，并声明这是社区推荐，不是司徒K原榜单。本版只收集提名，不实现扩展数据集。

## 权利与发布

署名不能代替转载授权。不提交原文全文、配图或批量复制的个人点评，也不对第三方内容附加许可证。公开发布前由仓库拥有者确认转载范围，记录许可条件；授权未明确时不得声称已获原作者许可。
