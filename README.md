# LLM Router / Agentic Router 论文笔记库

这是一个面向 `LLM router` / `agentic router` 系统设计的论文精读仓库。

目标不是泛泛整理 paper，而是围绕“我如何真正做出一个可落地的 router 系统”来组织阅读、记录与沉淀。

这里重点关注的问题包括：

- 如何做 model routing
- 如何做 budget routing
- 如何做 workflow topology routing
- 如何做 uncertainty / escalation control
- 如何把 memory / historical experience 纳入 routing
- 如何把 query-level、turn-level、step-level、agent-level 决策串成统一系统

## 你可以先看哪里

如果你第一次进入这个仓库，建议按下面顺序看：

1. `reading-queue.md`：当前推荐阅读顺序
2. `design-principles.md`：跨论文沉淀出的系统设计原则
3. `papers/2603.04445-survey-dynamic-model-routing-and-cascading.md`：当前最适合作为入口的综述
4. `templates/`：普通论文模板、survey 模板、总览模板
5. `LOCAL_PDF_INDEX.md`：本地 PDF 索引

## 仓库结构

```text
llmrouter-paper-notes/
├── README.md
├── LOCAL_PDF_INDEX.md
├── design-principles.md
├── reading-queue.md
├── papers-manifest.json
├── download-results.json
├── pdfs/
├── papers/
├── templates/
└── assets/
```

## 当前资源概览

- 已下载 PDF：15 篇
- 已建立论文 stub：15 篇
- 普通论文模板：`templates/paper-template.md`
- 综述论文模板：`templates/survey-template.md`
- 总览模板：`templates/overview-template.md`
- 仓库结构建议：`templates/repo-structure.md`

## 研究主线

- [ ] Query / task-level routing
- [ ] Turn-level budget routing
- [ ] Step-level uncertainty routing
- [ ] Workflow topology routing
- [ ] Multi-agent granularity control
- [ ] Memory-augmented routing
- [ ] Escalation / fallback routing

## 当前优先读的核心论文

- Dynamic Model Routing and Cascading (2603.04445)  
  `papers/2603.04445-survey-dynamic-model-routing-and-cascading.md`
- Turn-Adaptive Budgets (2604.05164)  
  `papers/2604.05164-tab-turn-adaptive-budgets.md`
- GraphPlanner (2604.23626)  
  `papers/2604.23626-graphplanner.md`
- TrACE (2604.08369)  
  `papers/2604.08369-trace-dont-overthink-it.md`
- Agent Capsules (2605.00410)  
  `papers/2605.00410-agent-capsules.md`

## 当前基础论文

- RouteLLM (2406.18665)  
  `papers/2406.18665-routellm.md`
- AutoMix (2310.12963)  
  `papers/2310.12963-automix.md`
- EcoAssistant (2310.03046)  
  `papers/2310.03046-ecoassistant.md`
- FrugalGPT (2305.05176)  
  `papers/2305.05176-frugalgpt.md`
- Test-time Compute (2408.03314)  
  `papers/2408.03314-test-time-compute.md`
- s1 (2501.19393)  
  `papers/2501.19393-s1.md`
- RouterBench (2403.12031)  
  `papers/2403.12031-routerbench.md`
- OptLLM (2405.15130)  
  `papers/2405.15130-optllm.md`
- RouteProfile (2605.00180)  
  `papers/2605.00180-routeprofile.md`
- IRT-Router (2506.01048)  
  `papers/2506.01048-irt-router.md`

## 推荐阅读路线

### 第一阶段：先建立问题地图

- 先读 survey，建立 routing 问题空间
- 明确 router 的输入、输出、决策时机、优化目标、fallback 机制
- 把“方法分类”转换成“系统设计分层”

建议先读：

- `papers/2603.04445-survey-dynamic-model-routing-and-cascading.md`
- `design-principles.md`

### 第二阶段：补 query / model routing 基础

重点理解：

- 路由信号从哪里来
- 如何在质量 / 成本 / 延迟之间做权衡
- heuristic、preference、uncertainty、ranking 各自适合什么场景

建议接着读：

- `papers/2406.18665-routellm.md`
- `papers/2305.05176-frugalgpt.md`
- `papers/2405.15130-optllm.md`
- `papers/2403.12031-routerbench.md`

### 第三阶段：补 agentic routing 视角

重点理解：

- router 不再只是“选模型”，而是“选下一步怎么做”
- 如何做 workflow routing、budget routing、escalation routing
- 如何让 planner / executor / verifier 成为 routing 对象

建议继续读：

- `papers/2604.05164-tab-turn-adaptive-budgets.md`
- `papers/2604.23626-graphplanner.md`
- `papers/2604.08369-trace-dont-overthink-it.md`
- `papers/2605.00410-agent-capsules.md`

## 这个仓库适合怎么用

建议你每读完一篇论文，都做三件事：

1. 更新对应的 `papers/*.md`
2. 把真正可复用的结论沉淀到 `design-principles.md`
3. 回头修正你自己的 router 问题分层

这样这个仓库最后沉淀出来的，不只是论文摘要，而是一套可以反哺系统实现的研究地图。

## 自动化入口

如果你以后想让我“给一篇 paper 就自动建档并生成对应 markdown 骨架”，现在仓库里已经有最小自动化入口：

- 脚本：`auto_generate_paper_note.py`
- 说明：`AUTOMATION.md`

典型用法：

`python3 auto_generate_paper_note.py /path/to/paper.pdf --copy`

它会：
- 把 PDF 纳入仓库
- 生成对应 `papers/*.md` 骨架
- 抽取 `pdftotext` 文本到 `.tmp_pdftext/`
- 尽量同步更新 `papers-manifest.json`、`reading-queue.md`、`LOCAL_PDF_INDEX.md`

然后再继续让我按高强度标准把这篇论文精读完整。

## 下一步

当前最值得继续推进的事情：

- 完善 survey 笔记中的 taxonomy 与代表方法表
- 补一个总览页，把 paper 间关系画清楚
- 开始从“paper reading”过渡到“router design spec”
- 继续把自动化入口升级成“一步生成高质量初稿 + 自动跑 leftover scan”的完整流水线
