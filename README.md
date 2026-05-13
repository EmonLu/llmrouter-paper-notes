# LLMRouter / Agentic Router Papers

这个目录是我为构建 `LLM agentic router` 而维护的本地论文资料库与精读工作区。

目标不是泛泛整理论文，而是逐步沉淀出一个可实现的系统：
- 如何进行 model routing
- 如何进行 budget routing
- 如何进行 workflow topology routing
- 如何进行 uncertainty / escalation control
- 如何把 memory / historical experience 纳入 routing

## 当前目录结构

```text
llmrouter-paper-notes-kit/
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

## 当前资源

- 已下载 PDF: 15 篇
- 单篇精读模板: `templates/paper-template.md`
- 总览模板: `templates/overview-template.md`
- 建议仓库结构: `templates/repo-structure.md`

## 研究主线

- [ ] Query / Task-level routing
- [ ] Turn-level budget routing
- [ ] Step-level uncertainty routing
- [ ] Workflow topology routing
- [ ] Multi-agent granularity control
- [ ] Memory-augmented routing
- [ ] Escalation / recovery routing

## 当前核心论文（优先读）

- Dynamic Model Routing and Cascading (2603.04445) -> `papers/2603.04445-survey-dynamic-model-routing-and-cascading.md`
- Turn-Adaptive Budgets (2604.05164) -> `papers/2604.05164-tab-turn-adaptive-budgets.md`
- GraphPlanner (2604.23626) -> `papers/2604.23626-graphplanner.md`
- TrACE (2604.08369) -> `papers/2604.08369-trace-dont-overthink-it.md`
- Agent Capsules (2605.00410) -> `papers/2605.00410-agent-capsules.md`

## 当前基础论文（作为背景）

- RouteLLM (2406.18665) -> `papers/2406.18665-routellm.md`
- AutoMix (2310.12963) -> `papers/2310.12963-automix.md`
- EcoAssistant (2310.03046) -> `papers/2310.03046-ecoassistant.md`
- FrugalGPT (2305.05176) -> `papers/2305.05176-frugalgpt.md`
- Test-time Compute (2408.03314) -> `papers/2408.03314-test-time-compute.md`
- s1 (2501.19393) -> `papers/2501.19393-s1.md`
- RouterBench (2403.12031) -> `papers/2403.12031-routerbench.md`
- OptLLM (2405.15130) -> `papers/2405.15130-optllm.md`
- RouteProfile (2605.00180) -> `papers/2605.00180-routeprofile.md`
- IRT-Router (2506.01048) -> `papers/2506.01048-irt-router.md`

## 下一步建议

1. 先从 core 论文开始，按模板逐篇写精读笔记
2. 每读完一篇，更新 `design-principles.md`
3. 当目录和模板稳定后，再创建 GitHub repo 并整体推上去
