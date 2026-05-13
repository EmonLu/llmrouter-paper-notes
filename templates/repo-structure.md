# 建议仓库结构

```text
llmrouter-papers/
├── README.md                    # 总览页（用 overview-template）
├── design-principles.md         # 从论文中沉淀的设计原则
├── reading-queue.md             # 待读论文清单
├── papers/
│   ├── 2026-survey-dynamic-model-routing.md
│   ├── 2026-tab-turn-adaptive-budgets.md
│   ├── 2026-graphplanner.md
│   ├── 2026-trace.md
│   └── 2026-agent-capsules.md
├── templates/
│   ├── paper-template.md
│   └── overview-template.md
└── assets/
    └── figures/                 # 你后续自己画的框架图、表格截图、读书图
```

## 文件说明

### README.md
- 这个仓库在干什么
- 你的研究目标是什么
- 已读论文目录
- 当前系统框架
- 当前下一步行动

### design-principles.md
专门记“跨论文沉淀”的原则，例如：
- 不要只做 query-level routing，要加入 step-level uncertainty gate
- budget routing 应该是 sequential，而不是 static
- workflow topology 也是 routing 的一部分
- memory 不应该只做检索，也应该进入 routing state

### reading-queue.md
分三栏即可：
- 必读
- 已读
- 可选

### papers/*.md
每篇论文单独一份笔记，必须按统一模板写。

## 文件命名建议
统一用：
`年份-简称.md`

例如：
- `2026-survey-dynamic-model-routing.md`
- `2026-tab-turn-adaptive-budgets.md`
- `2026-graphplanner.md`
- `2026-trace.md`
- `2026-agent-capsules.md`

## 书写风格建议
- 中文为主
- 只保留必要的英文术语
- 每篇都必须写“对我的 agentic router 的直接价值”
- 每篇都必须写“我不打算照搬什么”
- 每篇都必须落到“接下来要写哪个模块”
