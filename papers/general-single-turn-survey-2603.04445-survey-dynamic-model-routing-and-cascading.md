# Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey

## 1. 基本信息
> 记录综述论文的基本元信息，方便引用和回溯。

- 标题：Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey
- 作者 / 机构：Yasmin Moslem, John D. Kelleher / ADAPT Centre, School of Computer Science & Statistics, Trinity College Dublin
- 发表时间：2026-03（arXiv v1），当前本地 PDF 为 2026-04-21 的 v2
- 会议 / 期刊 / arXiv：arXiv:2603.04445 [cs.NI]
- 论文链接：https://arxiv.org/abs/2603.04445
- 代码 / 配套资源链接（如果有）：未见官方代码仓库
- 综述主题关键词：
  - `LLM Routing`
  - `Dynamic Model Routing`
  - `Model Cascading`
  - `Adaptive Inference`
  - `Multi-LLM Deployment`
  - `Cost-Latency-Quality Trade-off`

## 2. 一句话总结
> 用一句话说明：这篇综述覆盖了什么主题、是如何组织文献的、它最大的价值是什么。

- 总结：这篇 survey 系统梳理了“多个独立 LLM 之间的动态路由与级联推理”方法，既按 difficulty / preference / clustering / RL / uncertainty / cascading 等范式分类，又提出了一个很实用的 when / what / how 三维统一分析框架。

## 3. 综述范围（Scope）
> 先搞清楚它“综述了什么”和“没有综述什么”。

### 3.1 它覆盖哪些问题？
- 推理时在多个独立训练 LLM 之间做动态模型选择。
- 根据 query 难度、偏好、不确定性、聚类信息或反馈信号做 routing。
- 级联式推理（cascade / escalation / fallback），即先尝试小模型，再根据质量信号升级到更强模型。
- 多模态 routing 的新进展（作为较短章节覆盖）。
- routing 的评估基准、指标和部署中常见的质量-成本-延迟权衡。

### 3.2 它不覆盖哪些问题？
- 不覆盖 mixture-of-experts（MoE）这类“单个模型内部专家路由”问题；论文明确强调自己研究的是多个 independently trained LLM 之间的 routing。
- 不重点讨论训练时模型压缩、蒸馏或参数高效微调本身。
- 不聚焦单一系统实现细节，而是更偏“方法地图 + 设计空间”。

### 3.3 它更偏向哪些视角？
> 例如：
> - 方法分类
> - 系统架构
> - 训练方式
> - 评估基准
> - 部署与工程
> - 开放问题

- 主要视角：方法 taxonomy、统一系统设计空间、评估框架、未来方向。
- 我的判断：这篇综述不只是“列论文”，而是在尝试回答“一个 router 到底由哪些决策维度组成、部署时该怎么比较方法”。这对后续读具体方法论文很有帮助。

## 4. 论文试图回答的核心问题
> 综述论文通常不是提新算法，而是试图回答“这个领域到底该怎么看”。

### 4.1 它试图统一回答什么问题？
- 多模型 LLM routing 到底有哪些主流范式？
- routing 和 cascading 在系统上分别发生在什么阶段、依赖什么信息、以什么机制产生决策？
- 一个实用 router 应该如何同时平衡质量、成本、延迟，而不是只优化单一准确率？
- 为什么现实系统往往是“组合式”的，而不是只属于某一个纯粹范式？

### 4.2 为什么这些问题在大模型路由场景中重要？
- 因为不同 query 的复杂度、领域、容错要求不同，统一把所有请求都发给最强模型会浪费大量成本。
- 单一小模型虽然便宜，但在复杂推理、代码、数学、专业任务上容易失败；router 的价值就是把计算预算投到“真正值得用强模型”的请求上。
- 真正上线的系统不只看质量，还要看 TTFT、TPOT、吞吐量、token 成本、能耗和安全性，因此需要一个统一视角来比较方案。

### 4.3 对应哪些核心目标？
> 可多选：质量、成本、延迟、扩展性、鲁棒性、部署效率、可解释性、online adaptation 等。

- 目标类型：质量、成本、延迟、扩展性、部署效率、鲁棒性、能效。
- 我的理解：这篇 survey 最有价值的一点，是把 router 明确定位为“受部署约束驱动的多目标决策问题”，而不是简单的 query classifier。

## 5. 分类框架 / Taxonomy
> 这是综述论文最重要的一部分。重点记录它怎么切分方法空间。

### 5.1 它是怎么分类已有工作的？
- 分类主轴 1：按 routing paradigm 分类：difficulty-aware、human preference-aligned、clustering-based、reinforcement learning、uncertainty-based、cascading。
- 分类主轴 2：按统一设计空间分类：when decisions are made、what information is used、how decisions are computed。
- 分类主轴 3：按部署形态分类：pre-generation、post-generation、multi-stage、online/adaptive，以及是否使用 query / model metadata / response / feedback 等信号。

### 5.2 每个大类下面分别有什么代表方法？
- 类别 A：Difficulty-aware routing
  - 代表论文：BEST-Route、Semantic Router / vLLM Semantic Router、GraphRouter、ICL-Router、IRT 风格方法
  - 核心特点：在生成前基于 query complexity、query-model compatibility 或 query embedding 来决定用哪个模型，通常偏向低开销和快速分流。
- 类别 B：Preference / clustering / uncertainty-based routing
  - 代表论文：RouteLLM、Arch-Router、Prompt-to-Leaderboard、聚类路由方法、若干 uncertainty-based deferral 方法
  - 核心特点：用人类偏好、历史比较结果、聚类结构或置信度估计来做更细粒度的质量-成本平衡，适合“最优模型并不总是最贵模型”的场景。
- 类别 C：RL routing 与 cascading
  - 代表论文：Router-R1、R2-Reasoner、FrugalGPT、AutoMix，以及若干 QE / confidence driven cascade 方法
  - 核心特点：更强调 sequential decision、升级策略、cost-aware stop rule、response-level verification，适合复杂推理和多阶段系统。

### 5.3 这套分类是否清晰、实用？
- 比较清晰，尤其对入门者友好，因为它既保留“按方法家族分类”的可读性，又用 when / what / how 解释了不同论文在系统层面真正的差异。
- 一个优点是它提醒读者：很多论文名义上是 difficulty-aware，但实际还混合了 cost rule、feedback 或 post-generation signal。
- 一个不足是 preference、clustering、uncertainty 这几类在真实系统中边界有时会重叠，落地时更适合用三维框架而不是单标签归类。

### 5.4 不同方法族之间最关键的差异、优势和劣势
- Difficulty-aware routing：
  - 差异点：主要在 `pre-generation + query-level` 阶段做决策，依赖 query complexity、query embedding、query-model compatibility 或 difficulty proxy。
  - 优势：延迟低、部署干净、适合先做粗粒度分流；如果 difficulty 估计可靠，可以显著节省不必要的强模型调用。
  - 劣势：看不到模型真实输出，容易把“表面简单但实际难”的 query 分错；很多方法对训练分布和候选模型集合依赖较强。
- Preference-aligned routing：
  - 差异点：把“哪个模型更好”定义成人类偏好或 pairwise win-rate 问题，重点不只是准确率，而是主观质量与用户偏好对齐。
  - 优势：对 chat / open-ended generation 很自然，能更贴近真实用户体验；如果有 Arena 一类偏好数据，router 学到的是“用户更喜欢谁”而不是单一任务分数。
  - 劣势：偏好数据昂贵且可能随任务变化漂移；若方法依赖固定模型对或固定 reward model，新模型接入成本会偏高。
- Clustering-based routing：
  - 差异点：先把 query 空间聚成若干簇，再给每个 cluster 配更合适的模型，本质上更像“按区域分治”而不是单样本精细打分。
  - 优势：实现简单、直观，可在无标签或弱标签条件下工作；像 UniRoute 这种方法对新增模型尤其友好，只需在已有 cluster 上补 profile，不一定重训 router。
  - 劣势：cluster 边界粗糙时，单个 query 的细粒度差异容易被吞掉；如果任务分布漂移明显，聚类结构会老化。
- Reinforcement learning / bandit routing：
  - 差异点：把 routing 当成 sequential decision 或 online learning 问题，不只看离线静态标签，而是允许通过交互反馈持续更新策略。
  - 优势：适合动态环境、候选模型集变化和在线反馈场景；bandit 方法特别适合边部署边学。
  - 劣势：训练与部署复杂度高，探索成本也高；policy optimization 类方法往往引入多次模型调用，延迟和系统复杂度明显上升。
- Uncertainty-based routing：
  - 差异点：不直接预测“哪个模型最好”，而是先判断当前回答是否足够可信，再决定是否升级到更强模型。
  - 优势：天然适合做 post-generation quality gate；在 edge-cloud、SLM→LLM deferral 场景里尤其有用。
  - 劣势：可靠 uncertainty 很难得到；survey 明确指出 probe / perplexity 往往比 verbalization 更可靠，而自报置信度经常不准。
- Cascading systems：
  - 差异点：不是一次性选模型，而是多阶段地 `先便宜试 → 再决定是否升级`，把 routing 与 verification / stop rule / escalation policy 串起来。
  - 优势：更贴近真实部署；能把 query-level router、response-level verifier 和 escalation policy 组合起来，通常比纯单步路由更灵活。
  - 劣势：系统复杂、链路更长、额外 verifier/judge 会带来 latency 和工程负担；如果 stop / quality estimation 不准，cascade 容易既慢又不省钱。

### 5.5 如果只从系统设计角度选，我会怎么用这些方法族？
- 如果目标是做 `general router`：优先 difficulty / preference / clustering / profile-based 方法，因为它们更容易形成干净的 query-time policy，并能接 RouterBench 一类 benchmark。
- 如果目标是做 `coding agentic router`：优先 cascading、uncertainty、adaptive compute、workflow 控制这类思路，因为 agent 运行期间更需要的是 response-aware / trajectory-aware control，而不是一次性 query classification。
- 如果目标是长期可扩展：我会特别看 clustering/profile 路线，因为它们往往对新模型接入更友好。
- 如果目标是线上闭环自适应：我会特别看 bandit / online feedback 路线，因为 survey 明确指出“response-level + online adaptation”仍然是空白区，这恰好是很好的研究空间。

### 5.6 如果让我重画 taxonomy，我会怎么改？
- 我会把“路由对象”单独拉出来作为第四个维度：模型选择、是否升级、是否 early stop、是否组合多模型、是否改变 workflow。
- 我会把 agentic routing / workflow routing 作为 survey 后续扩展方向单列，因为它已经不仅是 model routing，而是“任务结构 + 角色 + 模型”的联合决策。
- 我会增加 deployment readiness 维度，例如是否需要额外 judge、是否需要在线反馈、是否依赖多个模型并发调用。

## 6. 统一问题定义
> 综述通常会给出一个统一视角：什么是 routing、输入输出是什么、优化目标是什么。

### 6.1 它如何定义 routing 问题？
- 在多个 independently trained LLM 中，根据输入查询特征与系统约束，动态决定最合适的模型或级联路径，使系统在质量、成本、延迟等目标之间取得更优折中。

### 6.2 它如何描述 router 的输入 / 输出？
- 输入：
  - query 本身的 lexical / semantic 特征
  - 模型元信息，如 cost、latency、domain specialization
  - post-generation 场景下的 response-level 信号，如 confidence、token probabilities、verifier output
  - 部署期间累积的 feedback / user interaction / downstream performance
- 输出：
  - 选择哪个模型
  - 是否升级到更强模型
  - 级联中的下一跳
  - 在一些组合系统中，是否继续推理或采用多模型融合

### 6.3 它如何定义优化目标？
> 例如：质量-成本、质量-延迟、success-cost、Pareto frontier 等。

- 重点是 quality-cost-latency 的联合优化。
- 文中明确强调 Pareto frontier 视角：一个好的 router 应该在给定成本预算或延迟约束下支配单模型方案。
- 综述还补充了 energy / carbon footprint 这类环境指标，说明“高效部署”不仅是 API 账单问题。

### 6.4 它有没有给出统一的系统框架？
- `有`
- 如果有，框架是什么：论文提出了三维统一分析框架：
  - when the routing decision is made
  - what information the routing mechanism uses
  - how the decision is computed

## 7. 方法维度总结
> 这里不是逐篇复述，而是把综述中提炼出的“方法维度”总结出来。

### 7.1 训练方式维度
> 例如：监督学习、强化学习、bandit、ranking、heuristic、training-free 等。

- heuristic / threshold-based
- supervised classifier / ranker
- preference learning
- contextual bandit
- PPO / RL policy
- uncertainty estimation / judge-based routing
- cascading 中常见的 training-free stop / escalation 规则

### 7.2 决策粒度维度
> 例如：query-level、turn-level、step-level、trajectory-level、workflow-level。

- query-level：最常见，收到请求后直接选模型
- post-generation level：先生成，再根据响应质量或置信度决定是否升级
- multi-stage level：在 cascade 中逐层决定是否继续
- online / adaptive level：少数 bandit / online learning 方法在部署中更新策略

### 7.3 路由对象维度
> 例如：模型选择、cascade、budget、agent role、workflow、granularity、fallback。

- 模型选择（select one model）
- 级联升级（escalation / deferral）
- fallback / reject / defer
- 多模型组合与集成
- 多模态模型选择

### 7.4 系统能力维度
> 例如：是否 online、是否支持 fallback、是否支持 multi-step、是否 memory-aware。

- 支持 fallback / cascading：是，尤其在 FrugalGPT、AutoMix 一类系统中很明显。
- 支持 online：部分方法支持，如 bandit / contextual adaptation；但 survey 认为“response-level + online adaptation”仍存在明显空白。
- 支持多目标优化：多数论文显式或隐式考虑成本；更少论文真正把质量、延迟、成本统一建模。
- 支持多模态：有初步覆盖，如 ReLope、MMR-Bench，但仍属于早期方向。

## 8. 评估与 Benchmark 视角
> 综述类论文的另一大价值，是帮你理解“这个领域该怎么评估”。

### 8.1 它总结了哪些常见评估指标？
- Routing accuracy：是否把 query 路由到“最优模型”。
- Task performance：最终答案质量，如 accuracy、exact match、pass@k、chrF、COMET。
- Win rate：在 preference-based routing 中常用。
- AUC：总结不同 cost budget / threshold 下的整体表现。
- Latency：文中点名 TTFT、TPOT。
- Throughput / Goodput：TPS、QPS，以及满足约束条件后的有效吞吐。
- Cost：API 账单、token 数、算力成本。
- Environmental metrics：energy consumption、carbon footprint。

### 8.2 它提到了哪些 benchmark / 数据集？
- RouterBench：40.5 万以上预计算输出，覆盖 11 个 LLM、7 个任务。
- RouterEval：2 亿以上性能记录、8500+ LLM、12 个 benchmark。
- MixInstruct：11 万 instruction-following 样本，偏 preference-based routing / ensemble。
- LLMRouterBench：40 万+ 实例、21 个数据集、33 个模型，并带 10 个 routing baseline。
- 标准 benchmark 也常被复用：MT-Bench、MMLU、MATH-500、GSM8K 等。
- 多模态评测：MMR-Bench。

### 8.3 它认为当前评估体系有哪些问题？
- 许多论文只报质量或 cost 的一部分，缺少统一的 Pareto 视角。
- 很多 benchmark 仍偏离真实部署场景，对 latency、throughput、concurrency、token budget 约束覆盖不够。
- 不少方法在固定 LLM 集上评估，泛化到新模型、新领域时证据不足。
- 多模态 routing benchmark 仍明显不成熟。

### 8.4 它有没有提出更好的评估标准？
- 它没有提出一个全新的统一 benchmark，但明确建议把 routing 作为系统级对象来评估：同时报告质量、成本、延迟、吞吐、goodput，最好使用 Pareto frontier 展示。
- 这篇 survey 还强调环境指标值得进入评估框架，这点比很多 routing 论文更前瞻。

## 9. 关键结论
> 提炼综述的核心 takeaways，而不是抄摘要。

### 9.1 最重要的 3~5 个结论
- 结论 1：动态 routing / cascading 的核心价值是把模型能力与 query 难度、领域和部署约束匹配起来，而不是默认调用最大模型。
- 结论 2：真实生产系统通常是组合式的，不会只依赖单一 paradigm。
- 结论 3：when / what / how 三维框架比单纯按方法名分类更能解释 router 的系统差异。
- 结论 4：优秀 routing 系统有机会在质量-成本 Pareto 上超过任何单一模型。
- 结论 5：跨模型架构、跨模态、跨应用泛化，仍然是这个领域最顽固的开放问题之一。

### 9.2 我最认同的结论
- 我最认同“production systems are compositional”这一点。很多论文在实验里像单一路由器，但真正工程落地时一定会混合 query-level router、quality gate、fallback、预算控制等机制。

### 9.3 我不完全认同的结论
- survey 对 agentic / workflow-level routing 的覆盖还不够深，因此如果把它当成“所有 routing 问题的总图”，会略低估 multi-step agent 系统的复杂度。

### 9.4 它在 agentic router 全景里的位置
- 如果把整个 agentic router 版图按“路由对象”展开，这篇 survey 更像是最靠近 `model routing / cascade routing` 的总纲，而不是 workflow router 或 runtime controller 的总纲。
- 它把问题边界清楚地画在“多个独立 LLM 之间如何选、何时升级、用什么信号升级”这一层；因此它特别适合作为 FrugalGPT、RouteLLM、AutoMix、RouterBench 这类工作的统一入口。
- 对 GraphPlanner、Agent Capsules、TAB、TrACE 这类后续论文来说，这篇 survey 的价值不是直接覆盖它们，而是提供一个可扩展的底座：`when / what / how` 三轴仍然适用，只是“what”要从 query / response 扩展到 graph memory、trajectory telemetry、execution mode、turn budget 等更丰富状态。
- 所以我会把它看成“agentic router 全景中的第一层地图”：先把 model-selection 与 cascade 层讲清楚，再往上接 workflow routing、budget routing、granularity routing、memory-aware routing。

## 10. 开放问题与未来方向
> 综述论文通常会指出未来研究方向，这是你做选题最有价值的部分之一。

### 10.1 作者提出了哪些 open problems？
- Generalization：很多 router 难以泛化到新模型、新领域、新分布。
- Multi-stage cascades：比起 one-stage routing，多阶段级联和 learned escalation 仍不充分。
- Unified multi-objective optimization：很少方法真正把质量、成本、延迟作为一体化目标求解。
- Response-level signal + online adaptation 的结合目前几乎是空白。
- Multimodality：多模态输入、跨模态成本差异、模态融合带来的 routing 问题还远未解决。

### 10.2 作者认为未来最重要的方向是什么？
- 可迁移、少重训甚至 retraining-free 的 router。
- 更贴近现实部署的 multi-stage / compositional routing systems。
- 更完整的 benchmark 与 metric 体系，显式纳入 latency / throughput / goodput。
- 多模态 routing 的统一表示与决策机制。

### 10.3 哪些方向和我的目标最相关？
- deployment-aware routing
- quality-cost-latency 三目标优化
- agent 系统中的 step-level / workflow-level routing
- 可泛化到新模型池的新型 router 表征

## 11. 对我的启发
> 这一部分最重要：把综述变成你自己的研究框架。

### 11.1 这篇综述对我理解大模型路由有什么帮助？
- 它帮我把“模型选择、fallback、cascade、budget、uncertainty、online adaptation”这些原本分散的概念放进了同一个框架里。
- 我可以据此区分：一个方法到底是在路由 query、路由阶段、路由预算，还是在做 response-level escalation。

### 11.2 它帮我建立了哪些“统一视角”？
- 用 when / what / how 来拆解 router。
- 把 router 当成“系统控制器”，而不是单纯分类器。
- 评估时看 Pareto frontier，而不是孤立 accuracy。

### 11.3 它帮助我识别了哪些研究空白？
- response-level signal 和 online learning 的结合。
- agentic routing 与 multi-LLM routing 的融合。
- 可部署、可泛化、低额外开销的 router。
- 多模态与能耗指标进入路由设计目标。

### 11.4 对我的应用场景有什么启发？
- 企业内部 Copilot：可以先做 pre-generation difficulty routing，再加 post-generation quality gate。
- LLM 系统路由：需要把 model routing、budget control、fallback 统一管理。
- 多模型选择：要显式纳入 model metadata，而不是只看 query embedding。
- 成本优化：cascade 和 stop rule 往往比单次分类更接近真实省钱路径。
- Agent 系统：这篇 survey 是很好的起点，但还要继续读 GraphPlanner、Agent Capsules 这类 workflow 级论文。

### 11.5 和仓库中其他论文的关系
- 和 FrugalGPT 对照看：FrugalGPT 是这篇 survey 中最典型的早期 cascade system，核心是“小模型先答 + scorer 决定是否升级”；而 survey 的贡献是把它放回更大的设计空间里，提醒我 FrugalGPT 只是 `post-generation + response-level + threshold` 这一格，不是 routing 的全部。
- 和 RouteLLM 对照看：RouteLLM 代表 `pre-generation + query-only + supervised preference router`。survey 让我更容易理解它为什么延迟低、部署干净，但也更受训练分布约束。
- 和 AutoMix 对照看：AutoMix 介于 query router 与 cascade 之间，属于 `small-model answer-aware escalation`。survey 对 uncertainty / self-verification / cascading 的梳理，正好解释了 AutoMix 为什么会比纯 query router 更像一个“决策后移”的系统。
- 和 GraphPlanner、Agent Capsules 对照看：这两篇已经把 routing object 从 model 推到 workflow 与 execution mode。survey 本身没有深挖这层，但它给出了一个很有用的过渡判断标准：凡是开始依赖 multi-stage、feedback、post-generation signal 和组合式控制的系统，实际上都已经在偏离“单一模型路由器”，走向更一般的 agent runtime controller。

### 11.6 如果把 survey 里的方法变成系统模块，该怎么落地
- 我会把 survey 提到的方法落成四个可独立演进的模块，而不是一个大而全 router：
  1. Intake router：只看 query 和预算/SLA，做 pre-generation 分流，适合 RouteLLM 一类方法。
  2. Quality gate：读取回答、置信度、judge 或 verifier signal，决定 accept / escalate，适合 FrugalGPT、AutoMix 一类系统。
  3. Budget controller：不换模型，只控制 token、rollout、thinking budget，后续可以接 TAB、TrACE、s1 这类方法。
  4. Observability / benchmark layer：统一记录 quality、cost、latency、goodput，并用 RouterBench / Pareto 曲线来评估各模块组合是否真的有收益。
- 这种拆法的意义是：生产环境里 rarely 会有一个“万能 router”一次做完所有决策，更多是 control plane 里多个 gate 串起来。survey 里“practical systems are compositional”这句，放到工程上就是要支持模块化叠加与逐步上线。
- 一个实际部署顺序可以是：先上 intake router 节省最粗粒度成本；再补 quality gate 防止小模型漏答；最后再加 budget / workflow 层控制，把 compute 继续压细。这比一开始就上 RL router 更稳。

### 11.7 对 benchmark 与图表的二轮解读
- Table 1 那个 design-space matrix 的意义不只是“把论文填进表格”，而是告诉我很多方法的真正差异并不在论文标题，而在观测信号与决策时机。例如两个方法都叫 router，但一个是 query-only pre-gen，另一个可能已经是 post-gen quality gate，它们的线上成本结构、可恢复性和失败模式完全不同。
- 综述中对 RouterBench、RouterEval、LLMRouterBench 的并列讨论也很有启发：这说明 routing 研究已经开始从“单篇论文自造实验”转向“以 benchmark 评估系统 control policy”。对我做 agentic router 设计，这意味着后续论文最好都能映射到统一 cost-quality-latency 面板，而不只是报 accuracy。
- 文中强调 throughput、goodput、TTFT、TPOT 和 energy 指标，我觉得这是这篇 survey 最像“正式系统论文”的地方：它隐含地提醒我，很多 paper-level router 在真实服务里会因为额外 judge 调用、并发抖动、cache miss 或 cross-model handoff 而丢失论文里的优势。

## 12. 对我自己的研究框架的影响
> 这一部分是 survey 模板区别于普通论文模板的关键内容。

### 12.1 读完后，我会如何重画自己的问题空间？
- 我会把问题空间拆成：
  1. 决策时机（pre / post / multi-stage）
  2. 输入信号（query / model metadata / response / feedback）
  3. 决策机制（rule / supervised / bandit / RL）
  4. 路由对象（model / cascade / budget / workflow）
  5. 部署目标（quality / cost / latency / energy / safety）

### 12.2 我会如何调整自己的论文阅读顺序？
- 先用这篇 survey 建图。
- 再读基础 routing：FrugalGPT、RouteLLM、GraphRouter、RouterBench。
- 然后读 sequential / RL / agentic：Router-R1、R2-Reasoner、GraphPlanner、Agent Capsules。

### 12.3 我会如何调整自己的系统设计分层？
- 增加“router control plane”这一层：
  - query intake routing
  - model routing
  - response verification / escalation
  - budget routing
  - evaluation / observability

### 12.4 这篇综述对应我系统里的哪些层？
> 可多选：
> - Task intake routing
> - Model routing
> - Budget routing
> - Workflow topology routing
> - Escalation / fallback routing
> - Memory / experience routing
> - Evaluation / benchmarking layer

- Model routing
- Budget routing
- Escalation / fallback routing
- Evaluation / benchmarking layer

## 13. 综述的价值与局限
> Survey 也有局限，尤其是分类是否过时、是否偏某类方法、是否忽略工程问题。

### 13.1 这篇综述的主要价值是什么？
- 它把 multi-LLM routing 和 cascading 的主要方法谱系梳理得比较完整。
- 它不止做 taxonomy，还把评估和部署问题一起纳入讨论。
- 它提出的三维设计空间非常适合拿来做后续论文卡片和横向比较表。

### 13.2 它的局限是什么？
- 对 agentic routing、workflow routing 的覆盖较少，更多聚焦“模型级路由”。
- 对工程实现细节、系统瓶颈、缓存和并发调度等讨论仍偏概念层。
- 作为 2026 年初的综述，后续新工作可能很快让 taxonomy 的边界继续扩张。

### 13.2.1 从部署角度再补一层 caveat
- survey 已经比多数综述更强调 latency / throughput / goodput，但对“额外控制开销谁来付”仍讨论不足。例如 preference router 可能要维护 embedding / classifier 服务，cascade 可能要承受多次 prefill，judge-based system 还会再引入 verifier 成本。
- 对企业系统来说，一个常见失败模式不是路由错得离谱，而是 router 自己太重，导致只在离线 benchmark 上划算、在线并发下反而不划算。
- 因此我读这篇综述后的一个实操原则是：后续看任何 router 论文，都要额外问三件事——是否增加额外 LLM 调用、是否破坏缓存/批处理、是否引入难观测的长尾延迟。

### 13.3 是否遗漏了重要工作或重要视角？
- 以本文 scope 来看，对 agent pipeline granularity control、execution-mode routing 的关注偏少。
- 若从“更广义的推理资源路由”角度看，token-level adaptive compute 和 agent runtime control 也值得纳入下一版综述。

### 13.4 是否偏理论 / 偏工程 / 偏 benchmark / 偏某类方法？
- 整体更偏“概念框架 + 文献组织 + 评估地图”。
- 不算纯理论，也不算强工程；更像一个建立领域共识的研究综述。

## 14. 横向比较字段（Survey 专用）
> 这一部分用于你后续比较多篇综述论文。

- 覆盖主题：multi-LLM routing、dynamic model selection、cascading、multimodal routing、evaluation
- 分类主轴：六类方法 taxonomy + when/what/how 三维设计空间
- 是否有统一定义：有
- 是否有系统框架：有
- 是否有 benchmark 总结：有
- 是否讨论部署问题：有
- 是否讨论 open problems：有
- 是否适合新手入门：是
- 是否适合作为研究地图：是
- 最大优点：兼顾 taxonomy、统一分析框架、评估指标和未来方向
- 最大缺点：对 agentic / workflow-level routing 覆盖还不够深

## 15. 阅读后的评分
> 用于后续快速筛选“哪篇综述最值得作为常驻参考”。

- 相关性：`5`
- 框架清晰度：`5`
- 覆盖完整度：`4`
- 前瞻性 / 研究启发：`4`
- 对我工作的帮助：`5`

### 总评
- 是否值得反复参考：`是`
- 是否适合作为该方向入口论文：`是`
- 是否适合指导后续选题：`是`
- 一句话结论：如果要给“LLM Router / Cascade / Adaptive Inference”方向先搭一个总地图，这篇 survey 很适合作为第一篇常驻参考。
