# 当前仓库中的数据集与评测 Benchmark 总览

这份文档不是单纯列名字，而是回答三个更重要的问题：

1. 现在仓库里到底有哪些“数据集 / benchmark / agent 环境”值得记？
2. 它们分别服务于哪条设计线：General Router 还是 Coding Agentic Router？
3. 哪些是真正应该优先复用的评测底座，哪些只是论文内部的训练数据或辅助数据？

如果一句话先说结论：

- Track A（General Router）最值得优先盯住的评测底座是：`RouterBench` + `RouterArena`
- Track A 里最值得额外关注的新数据资产是：`SPROUT`、`R2-Bench`、`Dgold/Djudge`、`s1K`
- Track B（Coding Agentic Router）目前仓库里真正比较像“agent 环境 / system benchmark”的是：`MiniHouse` 和 `Agent Capsules` 的自建 multi-agent pipeline benchmark
- 但如果你的目标是最后做 SWE-bench runtime router，那么当前仓库里还没有一个真正等价于“SWE-bench trajectory arena”的成熟公开 benchmark；这仍然是明显空位

## 1. 先给一个分类框架

为了避免后面讨论混乱，这里把仓库中的“数据相关对象”分成 5 类：

### A. Router 专用 benchmark / evaluator
- 目标：直接评 query-level router 的好坏
- 典型代表：`RouterBench`, `RouterArena`, `R2-Bench`, `SPROUT`

### B. Router 训练数据 / 偏好数据 / profile 构造数据
- 目标：不是最终 evaluator，而是拿来训练 router、做增强、构建 model profile
- 典型代表：`Chatbot Arena`, `Dgold`, `Djudge`, `s1K`, `RouteProfile` 所依赖的 interaction graph 数据来源

### C. 通用公共 benchmark
- 目标：本来不是为 routing 提出的，但被大量 router paper 拿来做评测
- 典型代表：`MMLU`, `GSM8K`, `MT-Bench`, `MATH500`, `GPQA`, `HumanEval`, `MBPP`

### D. Agent 环境 / system benchmark
- 目标：测 sequential decision、tool use、多 agent pipeline 或 runtime control
- 典型代表：`MiniHouse`, `Agent Capsules` 的自建 pipeline benchmark

### E. 论文内部构造的辅助数据包
- 目标：服务某篇方法，但不一定适合作为长期公共 evaluator
- 典型代表：`s1-prob`, `s1-teasers`，以及一些论文内部 rollout / trace / judge 缓存

这个分类很重要，因为：
- A 类最适合做“你的最终 evaluator 底座”
- B 类最适合做“训练数据或冷启动信号”
- C 类最适合做“横向对齐公共认知”
- D 类最适合迁移到 agentic runtime benchmark 设计
- E 类通常更适合作为方法内部资源，而不是长期主评测集

## 2. 最短结论：如果现在就要选一套最值得保留的数据 / benchmark 地图

### 2.1 对 General Router
优先级建议：

1. `RouterBench`
   - 适合做 frozen offline evaluator
   - 强项：便于复现、便于训练/比较 router
   - 弱项：偏离线，对 live deployment 指标覆盖不够

2. `RouterArena`
   - 适合做开放 leaderboard 和多指标 live evaluator
   - 强项：accuracy / cost / optimality / robustness / latency 更完整
   - 弱项：时间漂移更强，不是纯 frozen benchmark

3. `SPROUT`
   - 适合做多模型 cost-quality routing 训练 / 对比
   - 强项：更贴近现代多模型路由
   - 弱项：主要还是 query-level benchmark，不是 runtime 系统 benchmark

4. `R2-Bench`
   - 适合做 `(model, budget)` 联合路由评测
   - 强项：把 token budget 这一维显式拉进来了
   - 弱项：当前未验证到明确公开下载入口

### 2.2 对 Coding Agentic Router
优先级建议：

1. `MiniHouse`
   - 价值：提供一个轻量 sequential decision 环境，能测试按 timestep 自适应加 compute
   - 但它离真实 coding agent 还远

2. `Agent Capsules` 自建 pipeline benchmark
   - 价值：已经开始测 multi-agent topology、粒度控制、质量门控
   - 但它不是标准公共基准，更多是系统论文内 benchmark

3. `s1 / TAB / Test-time Compute` 这条线使用的 reasoning benchmark
   - 价值：能给 budget controller 一个清晰、干净的起点
   - 但它们更接近 reasoning control，不是 repo-level agent benchmark

### 2.3 一个非常关键的判断
如果你后面要做两条最终设计线，最稳的做法不是只选一套 benchmark，而是明确分裂成两套：

- Track A evaluator：`RouterBench + RouterArena (+ SPROUT / R2-Bench)`
- Track B evaluator：当前只能先用 `MiniHouse + pipeline benchmark + reasoning budget benchmark` 做过渡，最终仍要自建更像 SWE-bench trajectory 的 benchmark

## 3. 当前仓库里最重要的数据集 / benchmark 总表

## 3.1 真正应该重点保留的“核心数据 / benchmark”

| 名称 | 类型 | 首要服务对象 | 关联论文 | 公开状态 | 最值得记住的一句话 |
|---|---|---|---|---|---|
| RouterBench | Router benchmark / 离线 evaluator | General Router | `2403.12031-routerbench.md` | 部分公开 | 最适合做 frozen、可复现、低成本的 router 训练与对比底座 |
| RouterArena | Router benchmark + leaderboard | General Router | `2510.00202-routerarena.md` | 是（但完整复刻商业 router 需额外条件） | 最适合做 live、多指标、开放提交流程的 router 评测基础设施 |
| SPROUT | 新 routing dataset | General Router | `2502.03261-carrot.md` | 公开 | CARROT 的关键训练 / 评测数据资产，强调多模型质量-成本建模 |
| R2-Bench | reasoning-based routing benchmark | General Router（尤其 model+budget routing） | `2602.02823-r2-router.md` | 论文提出，但未验证到明确公开下载入口 | 目前仓库里最像“把 budget 也纳入动作空间”的 benchmark |
| Chatbot Arena 80k battles | 偏好训练数据 | General Router | `2406.18665-routellm.md` | 公开来源 | RouteLLM 的主训练信号，不是 router benchmark，但非常关键 |
| Dgold | 增强训练数据 | General Router | `2406.18665-routellm.md` | 派生自公开 benchmark | 用 gold label 补强 OOD routing 训练 |
| Djudge | judge 合成偏好数据 | General Router | `2406.18665-routellm.md` | 原始来源多公开，但最终增强包未见统一发布 | 用 GPT-4 judge 打出来的大规模偏好增强数据 |
| s1K | 小规模高质量训练集 | budget / reasoning controller | `2501.19393-s1.md` | 是 | 很适合研究“小而精训练集如何影响 test-time compute” |
| MiniHouse | 轻量 agent 环境 | Coding Agentic Router 过渡评测 | `2604.08369-trace-dont-overthink-it.md` | 论文称已 release，但当前未验证到直接仓库入口 | 当前仓库里最像 sequential decision benchmark 的轻量环境 |
| Agent Capsules 自建 pipeline benchmark | system benchmark | Coding Agentic Router | `2605.00410-agent-capsules.md` | 部分公开 | 当前仓库里最接近“测多 agent 粒度控制”的系统 benchmark |

## 3.2 次一级但仍常出现的公共 benchmark

这些 benchmark 不是 routing 论文自己提出的，但在仓库中重复出现很多次，因此仍然应该在设计上保留：

| 名称 | 主要出现在哪些论文 | 更偏哪条设计线 | 备注 |
|---|---|---|---|
| MMLU / MMLU-Pro | RouteLLM, R2-Router, RouteProfile, RouterBench | General Router | 最典型的知识/理解类公共基准 |
| GSM8K | RouteLLM, TrACE, RouteProfile | General Router / budget control 过渡 | 常被用来测 reasoning routing 或 adaptive compute |
| MT-Bench | RouteLLM, RouterBench | General Router | 开放问答、judge-based 评测常见 |
| MATH500 / MATH-500 | s1, TAB, RouteProfile | budget / reasoning control | 对 test-time compute 很关键 |
| GPQA / GPQA Diamond | s1, TAB, RouteProfile | budget / reasoning control | 偏更难推理题 |
| BBH | TAB, RouteProfile | General / reasoning | 常作 OOD 或 reasoning 广覆盖评测 |
| HumanEval / MBPP | RouteProfile | General Router / coding 子能力 | 可以服务 coding 能力画像，但不是 agent runtime benchmark |
| LongBench-v2 | RouterArena | General Router | 长上下文 routing 的重要补充评测 |
| RAGBench | R2-Router | General Router | 对 retrieval / long-context 更相关 |
| ToolBench 子集 | EcoAssistant | Agentic 支撑层 | 更像工具代理数据来源，不是 routing evaluator |

## 4. 逐项介绍：当前仓库中最关键的数据 / benchmark

## 4.1 RouterBench
关联论文：`papers/2403.12031-routerbench.md`

### 它是什么？
- 一个面向多 LLM 路由的标准 benchmark / dataset / evaluator
- 论文记录的规模是：`405,467` 条样本，覆盖 `11 models / 8 datasets / 64 tasks`
- 核心思想是：先离线收集多个模型在多个 benchmark 上的输出、成本和质量，再让 router 在这些静态结果上训练和评估

### 它具体包含什么？
- 样本字段至少包括：
  - sample id
  - model name
  - eval name
  - prompt
  - model response
  - performance
  - cost
  - true label
- 初始 release 覆盖的任务包括：
  - commonsense reasoning：HellaSwag、Winogrande、ARC Challenge
  - knowledge / academic benchmark：MMLU
  - math / reasoning
  - chat / preference 风格任务，如 MT-Bench
  - RAG 数据：一个 800 条、来自真实 query 的 RAG 数据集

### 它最重要的价值
- 它是最像“离线 router 实验台”的 benchmark
- 对你现在的 Track A 来说，它最大的好处不是题目多，而是：
  - 训练便宜
  - 复现实验稳定
  - 很适合比较不同 router policy
- 它解决的是“公平比较 router”的问题，而不是“更像真实线上流量”的问题

### 公开状态
- 当前仓库记录：`部分公开`
- 已确认入口：
  - GitHub README：https://github.com/withmartian/routerbench
  - Hugging Face dataset：https://huggingface.co/datasets/withmartian/routerbench
- 之所以记成“部分公开”，是因为其中还混有客户真实 query 构造的 RAG 数据与商业模型输出环境依赖

### 对设计有什么用？
- 如果你要做 General Router v1，最应该先拿它做第一版 evaluator
- 它很适合作为：
  - baseline comparison
  - ablation sandbox
  - 新 router 首轮筛选器

## 4.2 RouterArena
关联论文：`papers/2510.00202-routerarena.md`

### 它是什么？
- 一个开放的 router 评测平台，而不是单纯静态 benchmark
- 核心数据集：`8400` 条 query，来自 `23` 个源数据集
- 覆盖：`9` 个 domain，`44` 个 category
- 额外设计：
  - 基于 42 个模型的群体表现定义经验难度
  - 提供 accuracy / cost / optimality / robustness / latency 多指标评测
  - 提供 live leaderboard

### 它和 RouterBench 的关系
- RouterBench 更像 frozen offline evaluator
- RouterArena 更像 live public infrastructure
- 两者不是替代关系，而是互补关系

### 它最重要的价值
- 它补齐了 RouterBench 没完全补齐的几件事：
  - live leaderboard
  - robustness
  - latency
  - optimality
  - commercial router 的统一纳入
- 它让你看到“一个 router 不只是 accuracy 高不高”，而是：
  - 会不会花冤枉钱
  - 会不会被 query 噪声扰动
  - 自身会不会太慢

### 公开状态
- 当前仓库记录：`是，但完整复跑商业 router 需要额外条件`
- 已确认入口：
  - GitHub：https://github.com/RouteWorks/RouterArena
  - 数据集：https://huggingface.co/datasets/RouteWorks/RouterArena
  - leaderboard：https://routeworks.github.io/leaderboard

### 对设计有什么用？
- 如果你后面要做长期维护的 Track A research workbench，这篇几乎应该成为 evaluator blueprint
- 建议你把 Track A 的评测分成两层：
  - frozen 层：RouterBench 风格
  - live 层：RouterArena 风格

## 4.3 SPROUT
关联论文：`papers/2502.03261-carrot.md`

### 它是什么？
- CARROT 论文配套提出的大规模 routing dataset
- 用于支持“同时预测 per-model performance + per-model cost”的多模型路由学习
- 不是只做 binary strong/weak routing，而是面向更广的多模型池

### 它具体重要在哪？
- 传统 query router 很多时候只在小模型/大模型二元路由上做实验
- SPROUT 的价值在于：让多模型质量-成本曲线学习更自然
- 对你来说，它的重要性在于它更接近长期的 General Router，而不是只做简化二选一

### 公开状态
- 当前仓库将其视为：`公开`
- 这是目前仓库里一个明确应算作“新数据集贡献”的对象

### 对设计有什么用？
- 如果你后面想做多模型池路由，而不是只做 strong/weak routing，SPROUT 是值得保留的数据资产
- 它尤其适合作为 CARROT 风格 risk minimization 路由的训练底座

## 4.4 R2-Bench
关联论文：`papers/2602.02823-r2-router.md`

### 它是什么？
- R2-Router 配套提出的 reasoning-based routing benchmark
- 核心不是只记录 `(query, model)`，而是记录：
  - 同一个 query
  - 同一个模型
  - 在多个不同 token budget 下的回答质量与成本曲线
- 规模：`30,968` 个 query，来自 `6` 个 benchmark、`20` 个类别
- 构造方式包括：
  - 对 `15` 个 LLM
  - 在 `16` 个 token budget 下分别生成回答
  - 再用 judge 打质量分，并记录实际 token 消耗

### 它最重要的价值
- 这是当前仓库里最像“把 budget 纳入路由动作空间”的 benchmark
- 相比 RouterBench / SPROUT，它补的是“同模型不同 budget”这条维度
- 对你未来 General Router 第二阶段非常关键，因为它直接支持 `(model, budget)` action

### 公开状态
- 当前仓库的保守结论是：
  - `论文正式提出并使用了 R2-Bench`
  - `但当前未验证到明确公开下载入口`
- 所以它不能和 RouterBench / RouterArena 一样直接记成“已明确开放下载”

### 对设计有什么用？
- 如果你后面做 Track A v2（模型 + budget 联合路由），R2-Bench 非常值得保留
- 但短期内不适合把它作为唯一核心 evaluator，因为开放性还不够确定

## 4.5 RouteLLM 训练数据：Chatbot Arena / Dgold / Djudge
关联论文：`papers/2406.18665-routellm.md`

### 它们分别是什么？
- `Chatbot Arena 80k battles`
  - 主体训练数据
  - 来自人类偏好对战数据
- `Dgold`
  - 从 MMLU validation 等带 gold label benchmark 派生出来的增强数据
  - 规模约 `1500`
- `Djudge`
  - 基于 Nectar + GPT-4 judge 打标得到的约 `120K` 偏好样本

### 它们不是哪类东西？
- 它们不是最理想的长期 evaluator
- 它们更像“训练 signal”或“增强数据源”

### 它们最重要的价值
- 它们告诉你：
  - query-level routing 如果只靠单一训练来源，泛化很容易不够
  - OOD routing 往往需要额外增强数据
- 对你自己的 router 设计来说，Dgold / Djudge 这条线最重要的启发不是具体样本，而是：
  - 要区分训练数据和最终评测数据
  - 要专门给 OOD / domain shift 留增强通道

### 公开状态
- Chatbot Arena 来源公开
- Dgold 基于公开 benchmark 派生
- Djudge 的原始来源多公开，但论文页未清楚给出统一的最终增强数据包下载入口
- 所以更稳妥的理解是：`主要数据来源公开，但增强后的最终训练资产未完全统一打包公开`

### 对设计有什么用？
- 这条线更适合放进你的“router training data strategy”章节，而不是放进“最终 evaluator”章节

## 4.6 s1K / s1-prob / s1-teasers
关联论文：`papers/2501.19393-s1.md`

### 它们是什么？
- `s1K`：最终公开的小规模高质量训练集，1000 条
- `s1-prob`、`s1-teasers`：论文里一起提出的辅助数据包 / 题集
- 更大的背景池是 `16` 个来源、共 `59,029` 个问题

### 它们最重要的价值
- 它们不是 router benchmark
- 它们也不是多模型 evaluator
- 它们真正重要的点是：
  - 让你研究“小规模高质量数据 + test-time compute control”的组合是否足够强
- 对 agentic budget routing 来说，这比把它当通用 benchmark 更有价值

### 公开状态
- 当前仓库记录：`是，s1K 已公开`

### 对设计有什么用？
- 它最适合服务 budget controller / test-time scaling 研究
- 不适合作为 General Router 主评测集
- 更适合作为 Track B 里的“budget control 训练 / sanity-check 数据包”

## 4.7 MiniHouse
关联论文：`papers/2604.08369-trace-dont-overthink-it.md`

### 它是什么？
- 一个轻量文本 household navigation 环境
- TrACE 用它来测试 agent 在 sequential decision 过程中，是否需要继续追加 rollout / self-consistency 采样
- 论文中的规模是：`30` 个任务 × `3` 个 seed，共 `90` 个 task-seed pair

### 它最重要的价值
- 它是当前仓库里最像 agent sequential decision 环境的对象之一
- 与 GSM8K 这种单步 reasoning benchmark 不同，MiniHouse 至少已经有了：
  - timestep
  - action disagreement
  - adaptive stopping
  - wall-clock 时间

### 它的局限
- 离真实 coding agent 很远
- 没有 repo state、test feedback、patch success、rollback 等信号
- 更接近“轻量文本 agent 环境”，不是软件工程环境

### 公开状态
- 当前仓库保守记录：
  - 论文明确写 `MiniHouse tasks and evaluation code are released with this paper`
  - 但当前未验证到直接可访问仓库链接
- 所以更稳妥的理解是：`论文声称 release，但当前未验证到公开入口`

### 对设计有什么用？
- 可作为 Coding Agentic Router 的早期过渡环境
- 非常适合验证：
  - disagreement-as-difficulty
  - per-step budget allocation
  - adaptive stopping
- 但绝对不能把它当成 SWE-bench 等价物

## 4.8 Agent Capsules 自建 pipeline benchmark
关联论文：`papers/2605.00410-agent-capsules.md`

### 它是什么？
- 不是标准公共 benchmark 论文
- 它更像作者自建的 system benchmark：
  - 四条多 agent pipeline
  - 5–14 agents
  - 覆盖不同 topology
- 示例领域包括：
  - due diligence
  - research / competitive intelligence
  - code-review / software engineering 风格 pipeline

### 它最重要的价值
- 当前仓库里最接近“execution granularity control benchmark”的对象
- 它开始测的东西已经很像 agentic router 真正关心的问题：
  - 多 agent 是否合并执行
  - quality gate
  - mode switch
  - token savings vs quality

### 公开状态
- 当前仓库记录：`部分公开`
- 开源代码和系统设计入口存在
- 但 benchmark 样本、judge 缓存、全量运行记录是否都完整公开，当前未逐项验证

### 对设计有什么用？
- 如果你后面要设计 Coding Agentic Router，这篇最该借的不是具体 pipeline，而是 benchmark 设计方式：
  - 把 granularity 当成显式动作
  - 把 token 节省和质量底线同时纳入指标
  - 允许 topology / group 结构成为状态的一部分

## 5. 哪些对象是“新数据集贡献”，哪些不应该混算

这一节专门解决最容易混乱的问题：很多 paper 会“用很多 benchmark”，但不等于“提出了新数据集”。

## 5.1 严格算“提出了新数据集 / benchmark / 环境”的

### 明确属于这一类的
- `RouterBench`
- `RouterArena`
- `SPROUT`
- `R2-Bench`
- `s1K`（以及 `s1-prob`, `s1-teasers`）
- `MiniHouse`
- `Agent Capsules` 自建 pipeline benchmark

## 5.2 更像“训练增强数据 / 辅助数据”的
- `Dgold`
- `Djudge`
- Chatbot Arena 80k battles（更准确说是来源数据，而不是论文新提 benchmark）

## 5.3 不建议算成“新标准数据集”的
- EcoAssistant 的 query-code memory
- TAB / TrACE / Test-time Compute 里生成的轨迹、中间 rollout、budget 分配记录
- RouteProfile 的 interaction graph 中间产物

原因很简单：
- 它们很重要
- 但更像方法内部 artifact，而不是一个对外稳定发布、可长期引用的公共 benchmark

## 6. 当前仓库里最值得反复复用的公共 benchmark 地图

虽然上面讲的是“论文提出的新数据”，但从你后面做实验的角度，真正会高频复用的还是下面这些公共 benchmark：

### 6.1 General Router 常用
- MMLU / MMLU-Pro
- GSM8K
- MT-Bench
- BBH
- ARC-Challenge
- CommonsenseQA
- OpenBookQA
- NaturalQA
- TriviaQA
- RAGBench
- LongBench-v2

### 6.2 budget / reasoning control 常用
- MATH500 / MATH-500
- AIME24 / AIME25
- GPQA / GPQA Diamond
- OlympiadBench
- TheoremQA
- BBEH-Mini

### 6.3 coding / code generation 子能力常用
- HumanEval
- MBPP
- EvalPlus
- MultiPL-E

### 6.4 agent 环境 / tool-use 过渡常用
- MiniHouse
- ToolBench 子集
- AgentVerse（在 RouteProfile 中作为下游 routing evaluation 的一部分出现）

这些公共 benchmark 的作用不是“证明你提出了新数据集”，而是：
- 给不同论文之间建立一条共同参考轴
- 让你自己的系统设计不至于完全封闭在自造数据上

## 7. 从系统设计角度看：这些数据 / benchmark 应该怎么放进你的两条 track

## 7.1 Track A：General Router
建议你直接按三层组织：

### 第一层：离线 frozen evaluator
- `RouterBench`
- 目标：低成本、稳定、可复现

### 第二层：live / deployment-facing evaluator
- `RouterArena`
- 目标：引入 robustness、latency、optimality、leaderboard

### 第三层：特化训练与扩展数据
- `SPROUT`
- `R2-Bench`
- `Chatbot Arena + Dgold + Djudge`
- 目标：支持多模型路由、model+budget routing、偏好增强和 OOD 补强

如果压缩成一句话：
- `RouterBench` 用来做基础比较
- `RouterArena` 用来做部署型比较
- `SPROUT / R2-Bench / Dgold / Djudge` 用来喂训练与扩展实验

## 7.2 Track B：Coding Agentic Router
当前更适合按三层组织：

### 第一层：budget / compute 控制起点
- `s1K`
- `MATH500 / GPQA / AIME / OlympiadBench`
- `TAB / Test-time Compute / s1` 使用的推理基准

### 第二层：轻量 sequential environment
- `MiniHouse`
- 目标：验证 disagreement、adaptive stopping、per-step compute allocation

### 第三层：system benchmark / multi-agent pipeline
- `Agent Capsules` 自建 pipeline benchmark
- `EcoAssistant` / ToolBench 风格环境作为辅助参考

### 当前仍然缺的终局层
- 一个真正针对 repo-level software repair trajectory 的公开 runtime benchmark
- 也就是：
  - 有 repo state
  - 有 test feedback
  - 有 patch success
  - 有 rollback / recovery cost
  - 有多步工具执行
- 当前仓库里还没有完全填上这个空位

## 8. 你现在最该怎么用这份清单

## 8.1 如果你接下来优先推进 General Router
建议直接采用：

1. 主 evaluator：`RouterBench`
2. 部署补充 evaluator：`RouterArena`
3. 第二阶段扩展：`SPROUT` + `R2-Bench`
4. 训练增强：`Chatbot Arena + Dgold + Djudge`

## 8.2 如果你接下来优先推进 Coding Agentic Router
建议先不要急着追求“完整最终 benchmark”，而是分阶段：

1. 用 `s1 / TAB / Test-time Compute` 这一线先建立 budget controller 直觉
2. 用 `MiniHouse` 验证 per-step 自适应 compute
3. 用 `Agent Capsules` 学会如何测 granularity / quality gate / topology-sensitive control
4. 最后再考虑做一个更像 SWE-bench trajectory 的 agentic arena

## 8.3 如果你问“当前仓库里最缺什么？”
最缺的是：
- 一个真正面向 Coding Agentic Router 的统一 evaluator 文档和 benchmark 设计稿
- 也就是说，不是缺论文，而是缺把现有 `MiniHouse + pipeline benchmark + budget benchmark` 这些东西整合成一个 agentic benchmark blueprint

## 9. 最后给一个极简版记忆卡片

### 只想记住 5 个名字
- `RouterBench`：离线 router evaluator
- `RouterArena`：live router leaderboard
- `SPROUT`：多模型 routing dataset
- `R2-Bench`：model+budget routing benchmark
- `MiniHouse`：轻量 agent sequential environment

### 只想记住 2 条设计建议
- 做 General Router：先 `RouterBench`，再 `RouterArena`
- 做 Coding Agentic Router：当前只能先用 `MiniHouse + Agent Capsules 风格 system benchmark` 过渡，最终还需要更像 SWE-bench 的 runtime benchmark

### 只想记住 1 个最重要判断
- 现在仓库里的数据 / benchmark 版图已经足够支撑 Track A 开始落地；但 Track B 还缺一个真正成熟的 repo-level runtime benchmark，这会是后面非常值得单独设计的一块。