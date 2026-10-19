# 80 账号精选｜本地交付报告

整理日期：2026-10-19。

## 已完成与未完成

- 完成：从原 100 条中建立独立 80 条精选草案，首页展示全部条目，20 条未纳入理由记录齐全，原始 100 条数据保持原样。
- 完成：对全部候选进行公开材料查阅或失败尝试记录，不复制原推荐点评，区分组织与个人。
- 部分完成：精选中 44 条有公开依据、14 条依据有限，22 条仍缺个人优势证据。**不是 80 个全部完成独立优势核查的最终名单。**
- 未进行：GitHub 建仓、commit、push、产品性能测试、完整 X 推文阅读及当前账号身份认证。
- 权利说明：减少数量不使原选编自动成为原创；来源署名保留。独立说明与取舍属于新增工作，第三方内容转载范围仍需确认。

## 文件入口

- [全部 80 条、优势说明与引用](../README.md)
- [全部 100 个候选研究及 20 个取舍理由](RESEARCH.md)
- [原始 100 条快照](ORIGINAL_100.md)
- [方法和局限](METHODOLOGY.md)
- [来源及权利说明](SOURCES.md)
- [80 条结构化数据](../data/curated80.json)
- [100 候选研究数据](../data/research_notes.json)

精选类别数量依次为：4、11、5、13、7、3、10、7、12、8。编号为阅读顺序，不是排名。

## 22 个待核验精选条目

司徒K、AYi、Orange AI、亦仁、Yangyi、向阳乔木、Yc、符尧、刘江、meng shao、小互、AIGCLINK、Gorden Sun、花叔、Jason Young、Geek、雪踏乌云、李韭二、Sac、黄赟、李岳、Berryxia.AI。

以上 `advantage` 均为 `null`，没有编造个人特色。部分同名 GitHub/网站没有明确 X 关联，不能拿来代替本人证据。需要本人公开作品、文章或账号介绍的可读材料才能完成。

## 20 个未纳入账号

Greg Brockman、Sundar Pichai、Elon Musk、Tibo、Alex Albert、cat、Jeff Dean、Oriol Vinyals、Mckay Wrigley、金尘马、余温、huangserva、叫我阿杭、老杨、droidHZ、硅谷王川、凡人小北、实践哥 Li、逸尘、木马人。

具体理由见研究报告。未纳入不表示能力更差；尤其在同样缺证的候选间，无法作已证实的优劣判断。本次只是控制 80 条数量的暂定取舍。

## 实测校验结果

- 原 100 条：校验通过；数据 SHA256 保持 `76675a9c4a792dd9b102df808b748e36ab882a12a9bba41a85430b5fbdbd4d17`。
- 精选：恰好 80 条；原编号映射、名称、handle、URL、类别与原快照一致；恰好 20 条未纳入。
- 全部 100 候选：公开依据 46 条，有限依据 16 条，待核验 38 条。
- 标准库 unittest：13 项全部通过，包含数量、重复、错误字段、标记、转义和证据状态检查。
- README、原快照文档、研究报告：连续生成两次，SHA256 不变；两个 `--check` 均通过。
- 本地 Markdown 链接与显式类别锚点：检查通过。
- 全部 X 身份核验日期：`null`；未声称链接当前有效。

实际使用本机 `C:\Users\R26501\.local\bin\python3.12.exe`；本机通用 `python` 别名不可用。无依赖安装，无开发服务器。

## 维护命令

在项目根目录执行（Python 命令未配置时，用上述解释器路径替代）：

```bash
python scripts/validate.py
```

```bash
python scripts/validate_curated.py
```

```bash
python scripts/generate_readme.py --check
```

```bash
python scripts/generate_curated.py --check
```

```bash
python -m unittest discover -s tests -v
```

## 准确的下一步

补充 22 个待核验条目的公开作品和身份关联资料，再复核有限依据条目。若需要无缺证的 80 条，应进一步取得材料，或另经用户同意调整候选范围，而不是凭空补充优势。确认公开转载范围及目标仓库，并获得发布授权后再推送 GitHub。
