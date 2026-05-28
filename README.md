# LLM Router / Agentic Router 论文笔记库

这是一个面向 `LLM router` / `coding agent router` / `multimodal router` 系统设计的论文与资料仓库。

这里的目标不是“收集论文摘要”，而是把阅读材料整理成三层真正能服务设计决策的结构：
- 任务类别：`general` / `coding-agentic` / `multimodal`
- 交互形态：`single-turn` / `multi-turn`
- 资料类型：`survey` / `method` / `dataset` / `benchmark` / `repo`

如果一句话概括：

> 这个仓库现在不再用 `core / foundation / agentic` 这种偏历史性的分法，而是改成“任务对象 × 对话形态 × 资料类型”的三维 taxonomy，直接服务 router 设计与实验落地。

## 1. 先看哪里

如果你第一次进入这个仓库，建议按下面顺序看：

1. `reading-queue.md`
2. `papers/INDEX.md`
3. `datasets-and-benchmarks-overview.md`
4. `coding-agent-datasets-comparison.md`
5. `papers/AGENTIC_COMPARISON.md`
6. `LOCAL_PDF_INDEX.md`

## 2. 当前三维分类

### 2.1 task-scope
- `general`：面向普通 query / benchmark / 多模型推理路由
- `coding-agentic`：面向 coding agent / SWE-bench / repo-level bug fixing runtime routing
- `multimodal`：面向图文/视觉等 multimodal 路由问题

### 2.2 turn-type
- `single-turn`：一次 query 或一次静态决策就完成路由
- `multi-turn`：沿轨迹、对话、workflow 或 agent runtime 多步做控制

### 2.3 artifact-type
- `survey`：综述 / 版图梳理
- `method`：主要贡献是方法或控制机制
- `dataset`：主要贡献是可复用数据资产或训练数据集
- `benchmark`：主要贡献是 evaluator / benchmark / leaderboard /评测协议
- `repo`：没有正式 paper，但工程实现价值很高的仓库笔记

## 3. 文件命名规则

统一格式：

`<task-scope>-<turn-type>-<artifact-type>-<paper-id-or-name>`

例子：
- `general-single-turn-method-2406.18665-routellm.md`
- `coding-agentic-multi-turn-benchmark-2605.18859-twinrouterbench.md`
- `multimodal-single-turn-benchmark-2601.17814-mmr-bench.md`
- `coding-agentic-multi-turn-repo-uncommonroute.md`

## 4. 现在仓库里最重要的三条线

### A. General Router
关注：单轮 query routing、cost-quality frontier、profile、budget-aware routing。

代表入口：
- `papers/general-single-turn-survey-2603.04445-survey-dynamic-model-routing-and-cascading.md`
- `papers/general-single-turn-benchmark-2403.12031-routerbench.md`
- `papers/general-single-turn-method-2406.18665-routellm.md`
- `papers/general-single-turn-method-2502.03261-carrot.md`
- `papers/general-single-turn-method-2605.00180-routeprofile.md`

### B. Coding-Agentic Router
关注：task prior、runtime control、workflow routing、granularity、budget gate、step-level routing。

代表入口：
- `papers/coding-agentic-single-turn-method-2604.07494-triage.md`
- `papers/coding-agentic-multi-turn-method-2604.14228-agent-design-mechanism.md`
- `papers/general-multi-turn-method-2604.23626-graphplanner.md`
- `papers/general-multi-turn-method-2605.00410-agent-capsules.md`
- `papers/coding-agentic-multi-turn-benchmark-2605.18859-twinrouterbench.md`
- `papers/coding-agentic-multi-turn-repo-uncommonroute.md`

说明：有些 paper 虽然服务 coding-agentic 设计，但论文本体更像通用 multi-turn controller，所以仍然留在 `general` scope；`papers/INDEX.md` 已把这种“设计用途”和“文件前缀分类”区分开写清楚。

### C. Multimodal Router
关注：图文混合输入下的 query routing，尤其是未来 screenshot-aware / GUI-aware / diagram-aware agent state。

代表入口：
- `papers/multimodal-single-turn-benchmark-2601.17814-mmr-bench.md`

## 5. dataset 和 benchmark 现在怎么区分

这是这次重构里最重要的一个变化。

- `benchmark`：主要用来评测 router / agent / system，关注 evaluator、协议、frontier、leaderboard。
- `dataset`：主要用来训练、构造、增强或扩充样本，关注可复用训练资产。

所以现在：
- `RouterBench` / `RouterArena` / `TwinRouterBench` / `MMR-Bench` 属于 `benchmark`
- `Multi-SWE-bench` 在当前仓库里被单独放到 `coding-agentic-multi-turn-dataset-*`，因为它除了 benchmark，更关键的价值是释放多语言训练/RL 数据资产
- `SWE-bench-train`、`Multi-SWE-RL`、`SPROUT`、`Dgold`、`Djudge`、`s1K` 这类条目，会在数据总览文档中单独当成 dataset 资产讨论，而不再混在 benchmark 叙事里

## 6. 当前资源概览

- 已下载 PDF：30 个文件
- 已建立论文 / repo 笔记：26 篇
- 分类文档：
  - `reading-queue.md`
  - `papers/INDEX.md`
  - `datasets-and-benchmarks-overview.md`
  - `coding-agent-datasets-comparison.md`
- 自动化入口：`auto_generate_paper_note.py`

## 7. 自动化入口

如果以后要继续 ingest 新 paper：

- 脚本：`auto_generate_paper_note.py`
- 说明：`AUTOMATION.md`
- 输入既支持本地 PDF，也支持 arXiv `abs/pdf` 链接

现在脚本支持：
- `--scope general|coding-agentic|multimodal`
- `--turn-type single-turn|multi-turn`
- `--artifact-type method|dataset|benchmark|survey|repo`

## 8. 下一步最值得继续做的事

- 继续补 dataset-first 资产清单，尤其是 `SWE-bench-train`、`Multi-SWE-RL`、`SPROUT`、`Dgold`、`Djudge`
- 给 coding-agentic 方向单独补一页 `state / action / label / metric` schema 文档
- 把 multimodal 这条线和 screenshot / GUI / diagram-aware coding agent state 进一步连接起来
