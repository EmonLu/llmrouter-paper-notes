# papers/INDEX

这个页面现在按三维 taxonomy 组织，而不是按历史上的 `core / foundation / agentic` 来分。

核心规则：
- 第一维：任务类别 `general / coding-agentic / multimodal`
- 第二维：交互形态 `single-turn / multi-turn`
- 第三维：资料类型 `survey / method / dataset / benchmark / repo`

最重要的一点：
- 文件前缀表达“这份资料本身属于什么”
- 设计解读表达“这份资料对哪条 router 设计线最有帮助”
- 这两件事不完全相同，所以不要混在一起看

## 1. 三条主线怎么理解

### 1.1 General
目标：做 query-level、多模型、可 benchmark、可比较的 router。

典型动作：
- 选模型
- 选 budget
- 维持 cost-quality frontier
- 提升新模型接入泛化

### 1.2 Coding-Agentic
目标：做 repo-level、trajectory-level、runtime-control-first 的 coding agent router。

典型动作：
- task-level triage
- workflow routing
- granularity routing
- budget gate
- recovery / escalation
- step-level tier selection

### 1.3 Multimodal
目标：做图文混合输入下的路由与 evaluator。

典型动作：
- 图文输入编码
- multimodal cue 融合
- 不同 MLLM 的 cost-quality routing

## 2. 按文件前缀看：仓库里现在有哪些资料

### 2.1 General / Single-turn / Survey
- `general-single-turn-survey-2502.00409-routing-strategies-survey.md`
- `general-single-turn-survey-2603.04445-survey-dynamic-model-routing-and-cascading.md`
- `general-single-turn-survey-2506.06579-multi-llm-inference-routing-and-hierarchical-techniques.md`

用途：搭建 general router 的问题地图、taxonomy 和开放问题视角。

### 2.2 General / Single-turn / Method
- `general-single-turn-method-2305.05176-frugalgpt.md`
- `general-single-turn-method-2310.12963-automix.md`
- `general-single-turn-method-2405.15130-optllm.md`
- `general-single-turn-method-2406.18665-routellm.md`
- `general-single-turn-method-2408.03314-test-time-compute.md`
- `general-single-turn-method-2501.19393-s1.md`
- `general-single-turn-method-2502.03261-carrot.md`
- `general-single-turn-method-2506.01048-irt-router.md`
- `general-single-turn-method-2602.02823-r2-router.md`
- `general-single-turn-method-2605.00180-routeprofile.md`

用途：解决 query-level routing policy、cost-aware routing、profile、budget-aware routing 等问题。

### 2.3 General / Single-turn / Benchmark
- `general-single-turn-benchmark-2403.12031-routerbench.md`
- `general-single-turn-benchmark-2510.00202-routerarena.md`

用途：为 general router 提供 offline evaluator + live leaderboard 两种评测底座。

### 2.4 General / Multi-turn / Method
- `general-multi-turn-method-2310.03046-ecoassistant.md`
- `general-multi-turn-method-2604.05164-tab-turn-adaptive-budgets.md`
- `general-multi-turn-method-2604.08369-trace-dont-overthink-it.md`
- `general-multi-turn-method-2604.23626-graphplanner.md`
- `general-multi-turn-method-2605.00410-agent-capsules.md`
- `general-multi-turn-method-2605.16637-hexagent.md`

用途：虽然很多最终会服务 coding-agentic 设计，但这些论文本体更像通用 multi-turn controller / runtime method，因此文件前缀仍是 `general`。

### 2.5 Coding-Agentic / Single-turn / Method
- `coding-agentic-single-turn-method-2604.07494-triage.md`

用途：任务开始前的 coarse prior / issue-level triage。

### 2.6 Coding-Agentic / Multi-turn / Method
- `coding-agentic-multi-turn-method-2604.14228-agent-design-mechanism.md`

用途：coding agent runtime substrate / control plane 设计空间。

### 2.7 Coding-Agentic / Multi-turn / Benchmark
- `coding-agentic-multi-turn-benchmark-2605.18859-twinrouterbench.md`
- 配套 benchmark 资产（当前以 PDF/总览为主，尚未全部拆成单篇 md）：SWE-bench、SWE-Bench Pro、SWE-PolyBench、SWE-ContextBench

用途：step-level routing benchmark，直接面向真实 agent 执行过程中的 tier selection；同时和 SWE-bench family / SWE-PolyBench / SWE-ContextBench 一起构成 coding-agentic benchmark 资产层。

### 2.8 Coding-Agentic / Multi-turn / Dataset
- 当前 dataset-first 代表资产：Multi-SWE-bench（已收录 PDF，当前主要在 `coding-agent-datasets-comparison.md` 中集中整理）

用途：表示可复用训练 / 扩样本资产，而不是单纯评测底座。

### 2.9 Coding-Agentic / Multi-turn / Repo
- `coding-agentic-multi-turn-repo-uncommonroute.md`

用途：本地 control plane / protocol routing / feedback overlay / budget cap / observability 的工程参考。

### 2.10 Multimodal / Single-turn / Benchmark
- `multimodal-single-turn-benchmark-2601.17814-mmr-bench.md`

用途：multimodal query router benchmark，给未来 screenshot-aware / GUI-aware / diagram-aware routing 提供前置材料。

## 3. 按设计用途看：最值得怎么读

### 3.1 如果你要做 General Router
最短闭环：
1. `general-single-turn-survey-2603.04445-survey-dynamic-model-routing-and-cascading.md`
2. `general-single-turn-benchmark-2403.12031-routerbench.md`
3. `general-single-turn-method-2406.18665-routellm.md`
4. `general-single-turn-method-2502.03261-carrot.md`
5. `general-single-turn-method-2605.00180-routeprofile.md`
6. `general-single-turn-benchmark-2510.00202-routerarena.md`

设计重点：
- policy
- profile
- evaluator
- budget-aware extension

### 3.2 如果你要做 Coding-Agentic Router
最短闭环：
1. `coding-agentic-multi-turn-method-2604.14228-agent-design-mechanism.md`
2. `coding-agentic-single-turn-method-2604.07494-triage.md`
3. `general-multi-turn-method-2604.23626-graphplanner.md`
4. `general-multi-turn-method-2605.00410-agent-capsules.md`
5. `general-multi-turn-method-2604.08369-trace-dont-overthink-it.md`
6. `coding-agentic-multi-turn-benchmark-2605.18859-twinrouterbench.md`
7. `coding-agentic-multi-turn-repo-uncommonroute.md`

设计重点：
- task prior
- runtime substrate
- workflow controller
- granularity controller
- budget / uncertainty gate
- step-level evaluator
- deployment control plane

### 3.3 如果你要做 Multimodal Router
当前入口：
1. `multimodal-single-turn-benchmark-2601.17814-mmr-bench.md`
2. 配合 `general-single-turn-survey-2603.04445-survey-dynamic-model-routing-and-cascading.md` 中的 multimodal routing 小节一起看

设计重点：
- multimodal input representation
- fixed candidate pool 的 evaluator
- 从 text-only router 升级到 text+image router

## 4. dataset 和 benchmark 的分拆解释

这次重构以后，仓库明确区分：

### 4.1 benchmark-first 资料
主要价值在于评测：
- RouterBench
- RouterArena
- TwinRouterBench
- SWE-bench
- SWE-Bench Pro
- SWE-PolyBench
- SWE-ContextBench
- MMR-Bench

### 4.2 dataset-first 资料
主要价值在于训练、扩样本或提供可复用数据资产：
- Multi-SWE-bench（当前文件前缀已单独标为 `dataset`）
- SWE-bench-train
- Multi-SWE-RL
- SWE-smith
- SPROUT
- Dgold
- Djudge
- s1K

注意：dataset-first 资产不一定都有独立 PDF 或独立笔记文件，但在 `datasets-and-benchmarks-overview.md` 和 `coding-agent-datasets-comparison.md` 里已经单独整理。

## 5. 最短结论

- `general` 线的关键是：policy + profile + evaluator
- `coding-agentic` 线的关键是：runtime substrate + workflow / granularity / budget + step-level benchmark
- `multimodal` 线虽然目前只有 1 篇，但它对应未来 screenshot / GUI / diagram state 的长期扩展方向
- `dataset` 和 `benchmark` 现在已经在仓库里显式分开，不再混写
