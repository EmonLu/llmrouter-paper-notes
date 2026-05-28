# Doing More with Less: A Survey on Routing Strategies for Resource Optimisation in Large Language Model-Based Systems

## 1. 基本信息
> 记录综述论文的基本元信息，方便引用和回溯。

- 标题：Doing More with Less: A Survey on Routing Strategies for Resource Optimisation in Large Language Model-Based Systems
- 作者 / 机构：Clovis Varangot-Reille, Christophe Bouvard, Antoine Gourru, Mathieu Ciancone, Marion Schaeffer, François Jacquenet / Wikit, Laboratoire Hubert Curien, INSA Rouen Normandie
- 发表时间：2025-02（arXiv v1），当前查看版本为 2025-07-21 的 v3
- 会议 / 期刊 / arXiv：arXiv:2502.00409 [cs.AI, cs.CL]
- 论文链接：https://arxiv.org/abs/2502.00409
- 代码 / 配套资源链接（如果有）：未见官方代码仓库；HTML 页面提到的链接主要是被综述引用的方法仓库与工具链接，不是这篇 survey 自己的 repo
- 综述主题关键词：
  - `LLM Routing`
  - `Resource Optimisation`
  - `Pre-generation Routing`
  - `Post-generation Routing`
  - `Cascade Routing`
  - `Adaptive LLM-based Systems`

## 2. 一句话总结
> 用一句话说明：这篇综述覆盖了什么主题、是如何组织文献的、它最大的价值是什么。

- 总结：这篇 survey 比 `Dynamic Model Routing and Cascading` 更偏“系统资源优化”视角，它不是按六种 paradigm 做高层地图，而是围绕三个问题来组织文献：routing 到底在优化什么、应该何时发生、以及应该如何实现，因此对搭建实际控制平面尤其有用。

## 3. 综述范围（Scope）
> 先搞清楚它“综述了什么”和“没有综述什么”。

### 3.1 它覆盖哪些问题？
- LLM-based systems 中的 routing 问题，不仅限于单纯多模型选择，也包括把 query 路由到不同组件、工作流、prompt、embedding 策略或专家模型。
- pre-generation routing：在回答生成前，基于 query topic、复杂度或候选能力做分流。
- post-generation routing / cascade routing：先生成，再基于回答质量或置信度决定是否升级到更强模型。
- routing 的实现方法：similarity-based、supervised、reinforcement learning-based、generative。
- 实际部署中的资源优化目标：不仅是 token 费用，也包括 latency、计算成本、环境成本。
- 产业视角下的轻量路由实践、benchmark 缺口、标准化评测和自适应路由方向。

### 3.2 它不覆盖哪些问题？
- 不研究传统 MoE 中的内部 gating；正文明确区分了 external router 与模型内部 expert gating。
- 不以 agentic workflow routing 为主线；虽然提到 prompt、pipeline、RAG、context size、tool 选择都可以成为 routing 对象，但还没有真正深入 GraphPlanner / Agent Capsules 这种 runtime controller 层。
- 不以某一条特定算法线为中心，而是偏“资源优化导向的系统地图”。

### 3.3 它更偏向哪些视角？
> 例如：
> - 方法分类
> - 系统架构
> - 训练方式
> - 评估基准
> - 部署与工程
> - 开放问题

- 主要视角：系统优化目标、路由时机、实现策略、工业实践、benchmark 标准化、可扩展性。
- 我的判断：这篇 survey 比较像“routing system design review”，而不只是 literature map。它把 router 明确写成性能-成本优化器，并强调 routing 候选不一定只是 LLM，也可以是 workflow、数据源或系统组件。

## 4. 论文试图回答的核心问题
> 综述论文通常不是提新算法，而是试图回答“这个领域到底该怎么看”。

### 4.1 它试图统一回答什么问题？
- routing 优化的目标函数到底是什么？
- routing 应该发生在什么时候：pre-generation 还是 post-generation？
- routing 应该怎么实现：similarity、supervised、RL，还是 generative？
- 一个实用 router 除了节省钱，还应该如何考虑 latency、计算与环境成本？
- 新 routing option 不断加入时，系统如何避免频繁整体重训？

### 4.2 为什么这些问题在大模型路由场景中重要？
- 因为单一 generalist LLM 虽然强，但对简单 query 往往成本过高。
- 实际系统不是只有“选哪个模型”这一件事，query 还可能需要不同预处理、不同上下文策略、不同检索或 prompt pipeline。
- 若只优化 financial cost，容易忽略 latency、计算需求和能耗，导致 paper 结果难以转化为真实部署优势。
- 若没有统一 benchmark 和 baseline，很多 routing 方法的收益到底来自 candidate pool 还是 router 架构本身，很难分清。

### 4.3 对应哪些核心目标？
> 可多选：质量、成本、延迟、扩展性、鲁棒性、部署效率、可解释性、online adaptation 等。

- 目标类型：质量、token 成本、延迟、计算成本、环境成本、可扩展性、自适应能力。
- 我的理解：这篇 survey 把 routing 从“选谁回答”提升成“在预算约束下的系统级资源分配”，这一点和你后面做 General Router / Coding Agentic Router 的控制平面视角是非常一致的。

## 5. 分类框架 / Taxonomy
> 这是综述论文最重要的一部分。重点记录它怎么切分方法空间。

### 5.1 它是怎么分类已有工作的？
- 分类主轴 1：优化目标（performance 要最大化什么，cost 要最小化什么）。
- 分类主轴 2：routing 时机（pre-generation vs post-generation / cascade）。
- 分类主轴 3：实现方式（similarity-based、supervised、reinforcement learning-based、generative）。

### 5.2 每个大类下面分别有什么代表方法？
- 类别 A：Similarity-based routing
  - 代表论文：Semantic Router、RouterDC、若干 kNN / clustering / preference similarity 路由、RouteLLM 的相似度加权版本
  - 核心特点：依赖 query 相似度、cluster、preference similarity 等弱监督或无监督信号，轻量、可部署，但在复杂任务上容易失效。
- 类别 B：Supervised routing
  - 代表论文：FrugalGPT（answer confidence inference 也在这一大类讨论里）、HybridLLM、MixLLM、OptLLM、GraphRouter、RouteLLM 中的矩阵分解 / 分类变体
  - 核心特点：把 routing 作为 recommendation、domain classification、complexity inference、knowledge graph edge prediction、confidence estimation 等监督任务来做。
- 类别 C：Reinforcement learning-based routing
  - 代表论文：PickLLM、Meta-LLM、Tryage、Zooter 等
  - 核心特点：通过在线奖励、bandit 或状态依赖反馈学策略，更适合动态环境和持续适应，但系统复杂度高。
- 类别 D：Generative routing
  - 代表论文：HuggingGPT、Self-Route、Automix、EcoAssistant、Mixture-of-Thoughts、Gorilla 风格的 API call routing
  - 核心特点：直接利用 LLM 的生成、置信、验证、代码执行或 repeated calls 能力来做 routing，覆盖 prompt-based、token probability、sequence probability、fine-tuned LLM、repeated calls、code execution 等多种形式。

### 5.3 这套分类是否清晰、实用？
- 很实用，因为它比“只按方法家族名”更工程化：先问目标函数，再问时机，再问机制。
- 它把 similarity / supervised / RL / generative 四类实现方式讲得很具体，尤其适合你从“能不能直接做系统”的角度选路线。
- 不足是它把一些本质上跨层的方法分散到不同章节里，例如 FrugalGPT 同时有 cascade 和 confidence gate 的味道，Automix 既是 repeated-calls 也是 cascade 系统，真正部署时还是要回到控制流视角而不是死守单标签。

### 5.4 如果让我重画 taxonomy，我会怎么改？
- 我会把“routing 对象”单独拉出来，明确区分：model、prompt、retrieval、context size、workflow、tool、recovery。
- 我会把 similarity / supervised / RL / generative 视为“how”，再把 pre/post/multi-stage 视为“when”，形成二维表，而不是线性章节。
- 我会补一个“可扩展到新 candidate 的成本”维度，因为这篇 survey 反复强调这是现有方法的关键瓶颈。

## 6. 统一问题定义
> 综述通常会给出一个统一视角：什么是 routing、输入输出是什么、优化目标是什么。

### 6.1 它如何定义 routing 问题？
- 给定候选集合 `M = {M1, ..., Mn}` 和 query `q`，router 要在预算约束下选出能最大化评分函数 `s(q, M)` 的 candidate，同时满足 `C_M(q) <= B`。
- 这里的 candidate 不限于模型，还可以是 workflow、数据源或系统组件。

### 6.2 它如何描述 router 的输入 / 输出？
- 输入：
  - user query
  - query 的 topic / complexity / embedding
  - 候选模型或候选组件的成本信息
  - post-generation 场景下的回答质量信号、confidence、verifier 输出
  - 部署过程中的反馈或上下文信息
- 输出：
  - 选择哪个模型或组件
  - 是否升级到更大模型
  - 是否切换 prompt / retrieval / context 策略
  - 是否继续 cascade 到下一跳

### 6.3 它如何定义优化目标？
> 例如：质量-成本、质量-延迟、success-cost、Pareto frontier 等。

- 核心是 performance-cost trade-off。
- performance 不一定是单一 accuracy，也可以是 human preference、semantic similarity、LLM judge score、task success。
- cost 不仅是 API price/token，也包括 latency、computational cost、environmental footprint。
- 这一点比很多 router 论文更系统，因为它明确要求未来把 non-financial cost 纳入成本函数。

### 6.4 它有没有给出统一的系统框架？
- `有`
- 如果有，框架是什么：围绕三个问题组织：
  - Q1: What should routing optimise?
  - Q2: When should routing take place?
  - Q3: How routing should be implemented?
- 这套框架没有 2603.04445 那篇 survey 的 when / what / how 那么抽象统一，但更贴近“我要怎么搭一个真正的路由系统”。

## 7. 方法维度总结
> 这里不是逐篇复述，而是把综述中提炼出的“方法维度”总结出来。

### 7.0 这个领域里的算法主线到底有哪些？
> 你最关心的是“算法本身怎么想、怎么分流、怎么升级”。这里先把算法家族归纳出来。

- 算法主线 1：pre-generation routing
  - 先估计 query topic / complexity / candidate compatibility，再做一次性分流。
- 算法主线 2：post-generation / cascade routing
  - 先让当前模型作答，再看 answer confidence / verifier 结果决定是否升级。
- 算法主线 3：generative / adaptive routing
  - 直接让 LLM 参与 routing 决策，或者通过 repeated calls、prompt、code execution 来产生 routing signal。
- 我的总结：这篇 survey 的主线组织比 2603.04445 更偏“控制点设计”，非常适合拿来拆你自己的 control plane。

### 7.1 训练方式维度
> 例如：监督学习、强化学习、bandit、ranking、heuristic、training-free 等。

- similarity-based / weak supervision
- supervised classification / regression / recommendation
- graph-based supervised learning
- contextual bandit / Q-learning / RL
- prompt-based / fine-tuned LLM routing
- repeated-calls / confidence estimation / execution-based routing

### 7.2 决策粒度维度
> 例如：query-level、turn-level、step-level、trajectory-level、workflow-level。

- query-level：最主流，尤其是 pre-generation routing
- response-level：典型于 FrugalGPT、Self-Route 一类 confidence / post-generation gate
- multi-stage level：典型于 cascade / repeated-calls / escalation 系统
- system-step level：文中提到 routing 不应只发生在 generation，也可发生于 retrieval、prompt、context size 选择等步骤

### 7.3 路由对象维度
> 例如：模型选择、cascade、budget、agent role、workflow、granularity、fallback。

- 模型选择
- 级联升级
- prompt 选择
- retrieval strategy 选择
- context size 选择
- embedding strategy / database / similarity function 选择
- 更广义地说，是系统组件选择

### 7.4 系统能力维度
> 例如：是否 online、是否支持 fallback、是否支持 multi-step、是否 memory-aware。

- 支持 fallback / cascading：强，尤其在 post-generation 路线里
- 支持 online/adaptive：有，但多出现在 RL / bandit 方法里
- 支持多步骤系统：有明确讨论，特别是在 retrieval、prompt、pipeline design 等层面
- 支持新 candidate 泛化：当前整体偏弱，survey 把它当成重点挑战之一

### 7.5 综述里出现了哪些候选模型组织方式？
> 这里专门抽取“候选模型池”层面的信息：论文里提到的方法，是把模型按什么方式组织起来的？按能力层级、领域专长、成本档位，还是 profile / leaderboard / reward score？

- 按大小/能力层级组织：small → large cascade
- 按领域专长组织：domain experts
- 按 cluster-level performance 组织：Jitkrittum 等的 per-cluster error vector
- 按 preference / leaderboard 排名组织：RouteLLM / Eagle 一类
- 按 graph relation / shared semantic space 组织：GraphRouter、Meta-LLM 风格方法
- 按 quality-cost score / Pareto frontier 组织：MixLLM、OptLLM 一类

### 7.6 对“新增候选模型时 router 是否容易扩展”有什么总结？
> 这是你很关心的一点：从综述层面总结哪些路线更容易接新模型，哪些路线每加一个模型都要重训/重标注。

- 哪类方法对新增模型最友好：
  - cluster-level performance vector
  - shared semantic space / graph-based 表征
  - 某些 contextual bandit / identity vector 方法
- 哪类方法新增模型成本最高：
  - transductive supervised classifier
  - 固定模型对的 preference router
  - domain-specific fine-tuning 方案
- 我得到的经验判断：这篇 survey 比 2603.04445 更明确地把“new routing options without retraining”当成未来方向，所以它对你做 RouteProfile / inductive profile layer 这条线特别有帮助。

## 8. 评估与 Benchmark 视角
> 综述类论文的另一大价值，是帮你理解“这个领域该怎么评估”。

### 8.1 它总结了哪些常见评估指标？
- answer quality / accuracy / exact matching / semantic similarity
- human preference
- token cost / API cost
- latency
- computational cost
- environmental footprint（kWh, kgCO2eq）

### 8.1.1 这些指标分别在衡量什么？
> 不只记名字，要写清楚这些指标为什么重要、对 router 设计意味着什么。

- 指标 A：quality
  - 衡量含义：路由后最终系统回答是否足够好
  - 对系统的意义：router 的存在不是单纯省钱，必须保证不显著损伤质量
- 指标 B：financial cost
  - 衡量含义：token 价格和调用链总成本
  - 对系统的意义：决定 router 是否真的有经济价值
- 指标 C：latency / compute / environment
  - 衡量含义：时延、资源消耗、能耗与碳排
  - 对系统的意义：决定 paper-level 优势能否转化为生产级优势

### 8.2 它提到了哪些 benchmark / 数据集？
- RouterBench
- MixInstruct
- EmbedLLM
- SPROUT
- 多篇具体论文各自用到的 MT-Bench、MMLU、Arena-Hard、text-to-SQL 等任务

### 8.2.1 这些 benchmark / 数据集是怎么来的？包含什么？
> 综述里凡是重要 benchmark，尽量记：来源、样本形式、标签/评价方式、覆盖任务。

- Benchmark / 数据集 A：RouterBench
  - 来源：survey 在“标准化比较”语境下明确点名的 routing benchmark
  - 样本内容：以 `query × candidate LLM` 的大规模离线结果矩阵为核心，便于在同一候选池和同一任务集上比较不同 routing policy
  - 标签 / 评价方式：强调把 router 放到统一实验条件下比较，而不是各篇论文各用一套私有评测
  - 覆盖任务：多 benchmark、多候选模型配置，偏系统级 routing evaluation
- Benchmark / 数据集 B：MixInstruct
  - 来源：survey 明确列为 routing strategy 标准化比较基座之一
  - 样本内容：instruction-following 为主，覆盖不同复杂度、不同风格的 prompts
  - 标签 / 评价方式：更适合比较 pre-generation routing 对 query complexity 的建模能力
  - 覆盖任务：通用 instruction / assistant 类场景
- Benchmark / 数据集 C：EmbedLLM
  - 来源：survey 在标准化 benchmark 盘点中点名
  - 样本内容：更强调 LLM representation / compact embedding 视角下的模型比较与路由
  - 标签 / 评价方式：适合观察 shared representation / inductive generalization 这类方法
  - 覆盖任务：多域 query 到多候选模型的匹配问题
- Benchmark / 数据集 D：SPROUT
  - 来源：survey 将其列为标准化 routing benchmark 之一
  - 样本内容：服务于 multi-model routing 中 cost-quality 比较与统一实验协议
  - 标签 / 评价方式：支持跨路由器结构的标准化 comparison
  - 覆盖任务：更偏 multi-model routing / budget-aware 评测
- 我的补充理解：这篇 survey 的重点不是把每个 benchmark 的数据 schema 全部展开，而是明确提出“以后大家至少应该在同一批公开 benchmark 和同一组 baseline 上比较”，这点对 system design 比 benchmark 细枝末节更重要。

### 8.3 它认为当前评估体系有哪些问题？
- 缺乏统一 benchmark 和统一 baseline。
- 很多论文只和 non-routing baseline 或自定义 baseline 比，导致无法客观比较。
- 很难判断收益来自 candidate pool 还是 router 架构。
- financial cost 被过度关注，而 latency / compute / ecological cost 经常被忽略。

### 8.4 它有没有提出更好的评估标准？
- 有，而且不是只停留在“多报几个指标”这种泛泛建议，而是给出了相对具体的 baseline 套件：
  1. random routing
  2. oracle routing
  3. best standalone LLM
  4. alternative routing strategies reviewed in the survey
- 它还强调应把 theoretical improvement margin（oracle 与 best standalone 的差）单独报出来，这样才能区分：
  - 你的 router 已经逼近候选池上限；还是
  - 候选池本身还有很大可挖空间。
- 另外它明确提醒：不要只报 financial cost，还要把 latency、computational cost、environmental cost 拉进 objective。
- 这一点对你做 evaluator 非常有用，因为它实际上已经把“最小可用评测协议”说出来了：统一 benchmark + 统一 baseline 套件 + 明确 oracle gap + 多维成本指标。

## 9. 关键结论
> 提炼综述的核心 takeaways，而不是抄摘要。

### 9.1 最重要的 3~5 个结论
- 结论 1：routing 的核心是 performance-cost optimisation，而不仅仅是 query classification。
- 结论 2：pre-generation routing 资源更省、更适合轻量部署；post-generation/cascade 更灵活，但通常更贵更慢。
- 结论 3：lightweight routing 也能做出不错效果，不一定要上重型 RL 或 fine-tuned LLM。
- 结论 4：新 candidate 的泛化能力是现有方法最重要的瓶颈之一。
- 结论 5：标准化 benchmark 和 baseline 缺失，是这个领域当前最大的评测障碍之一。

### 9.2 我最认同的结论
- 我最认同“不要只看金融成本”的观点。对真实系统来说，latency、compute、环境成本如果不进 objective，router 很容易在 paper 里省钱、在线上却不一定更好。

### 9.3 我不完全认同的结论
- 它对 agentic / workflow-level routing 只做到“顺带指出可扩展到别的步骤”，还没有真正把 runtime telemetry、trajectory state、recovery control 纳入统一框架。所以它更适合做你 Track A 的地基，而不是 Track B 的总纲。

## 10. 开放问题与未来方向
> 综述论文通常会指出未来研究方向，这是你做选题最有价值的部分之一。

### 10.1 作者提出了哪些 open problems？
- 超越 financial cost，把 computational 与 environmental cost 纳入目标函数
- routing strategy experiment 的标准化
- 使用互补而不是冗余的 routing candidates
- 把 LLM-based system 的各步骤都视为 routing possibility
- 支持新 routing option 的 autonomous adaptive routing

### 10.2 作者认为未来最重要的方向是什么？
- shared semantic space / inductive 方法，以支持新 candidate 接入
- dynamic system 视角下的 routing，而不是静态一次性分类器
- 在更多 pipeline steps 上应用 routing，而不只是在 generation step
- 统一 benchmark 与 baseline 框架

### 10.3 哪些方向和我的目标最相关？
- 对 General Router：
  - 标准化 benchmark / baseline
  - quality-cost-latency 统一目标
  - 可泛化到新模型的 profile / graph / semantic-space 方法
- 对 Coding Agentic Router：
  - “all steps are routing possibilities” 这个判断很重要
  - prompt / retrieval / context size / workflow selection 这些都可以被纳入 runtime control
  - 但真正的 trajectory-aware routing 还需要更靠后续论文补齐

## 11. 对我的启发
> 这一部分最重要：把综述变成你自己的研究框架。

### 11.1 这篇综述对我理解大模型路由有什么帮助？
- 它把 router 明确定义成“外部系统控制器”，并强调 candidate 不必只是 LLM，这对我后面把 routing object 扩展到 workflow / prompt / retrieval 很有帮助。
- 它提供了一个非常工程化的拆法：先问优化目标，再问时机，再问实现机制。

### 11.2 它帮我建立了哪些“统一视角”？
- 把 routing 看成带预算约束的选择问题
- 把 pre-generation / post-generation 明确分成两种不同控制点
- 把 similarity / supervised / RL / generative 视为可替换的实现层，而不是 mutually exclusive 的系统类型

### 11.3 它帮助我识别了哪些研究空白？
- generalized onboarding of new routing options
- 标准化实验协议
- 把 routing 扩展到 generation 之外的系统步骤
- 把 latency / compute / ecological cost 纳入统一 objective

### 11.4 从综述中的实验与 benchmark 讨论里，我能看出哪些方法优势？
> 不是只抄 survey 结论，而是自己总结：现有实验设计整体说明了哪些路线更强、强在什么地方。

- similarity-based 很轻量，适合作为低成本 baseline，但复杂任务和 OOD 泛化常常不稳。
- supervised routing 在 query complexity / quality-cost score / recommendation 这几条线上最成熟，尤其适合做干净的 General Router。
- graph / shared representation 路线在新模型接入上明显更有前途，是比纯 classifier 更有长期价值的方向。
- post-generation confidence / repeated-calls / code execution 路线更适合作为 runtime control 的第二层，而不是第一层入口策略。

### 11.5 对我的应用场景有什么启发？
- 企业内部 Copilot：不该只路由到不同 LLM，也应该把 retrieval strategy、prompt strategy、context size 视为 routing options。
- LLM 系统路由：Router 不应该只管理模型池，还应该管理系统组件池。
- General Router：可以直接继承这篇 survey 对 baseline、cost objective 和 onboarding 问题的强调。
- Coding Agentic Router：这篇 survey 提供了“routing 不止 generation”这个很好的哲学起点，但真正的 runtime state/action 设计还要结合 GraphPlanner、Agent Capsules、TAB、TrACE。

### 11.6 如果把这篇 survey 变成系统模块，我会怎么落地
- 模块 1：Objective layer
  - 统一记录 quality、financial cost、latency、compute cost、environment cost
- 模块 2：Decision timing layer
  - intake router（pre-generation）
  - quality gate（post-generation）
  - cascade / recovery layer（multi-stage）
- 模块 3：Mechanism layer
  - similarity baseline
  - supervised scorer
  - adaptive / bandit enhancer
  - generative verifier
- 模块 4：Candidate registry
  - 不只管 LLM，还管 prompt、retrieval、workflow、context strategy

### 11.7 和仓库中其他论文的关系
- 和 `general-single-turn-survey-2603.04445-survey-dynamic-model-routing-and-cascading.md` 对照：
  - 那篇更像领域地图，强调六种 routing paradigm 和 `when / what / how` 三轴
  - 这篇更像系统设计 review，强调 objective、timing、implementation 和 industrial considerations
- 和 `general-single-turn-survey-2506.06579-multi-llm-inference-routing-and-hierarchical-techniques.md` 对照：
  - `2502.00409` 更强在把 routing 拆成 system-design questions，并明确 baseline/benchmark 标准化问题
  - `2506.06579` 更强在 deployment constraints，尤其是 memory、energy、edge/cloud、distributed inference
  - 两篇并排读时，一个更像“控制面设计图”，一个更像“部署环境约束图”
- 和 RouteLLM / CARROT / OptLLM 对照：
  - 这篇把它们更自然地放进 supervised / recommendation / complexity inference 框架里
- 和 FrugalGPT / AutoMix / EcoAssistant 对照：
  - 这篇对 post-generation、repeated-calls、code execution 的讨论更细，所以对 runtime escalation 的工程含义解释得更直接
- 和 GraphRouter / RouteProfile 对照：
  - 这篇对“新 candidate 泛化”问题着墨更多，因此对你后面设计 model/profile registry 特别有帮助

## 12. 对我自己的研究框架的影响
> 这一部分是 survey 模板区别于普通论文模板的关键内容。

### 12.1 读完后，我会如何重画自己的问题空间？
- 我会把问题空间拆成：
  1. objective：质量、成本、延迟、compute、environment
  2. timing：pre-generation、post-generation、multi-stage
  3. mechanism：similarity、supervised、RL、generative
  4. routing object：model、prompt、retrieval、context、workflow
  5. onboarding：新 candidate 到底要不要重训

### 12.2 我会如何调整自己的论文阅读顺序？
- 先把这篇和 2603.04445 当成两张互补地图
- 再回头看：
  - RouteLLM / CARROT / OptLLM / RouterBench（General Router 主线）
  - FrugalGPT / AutoMix / EcoAssistant（post-generation 与 cascade 主线）
  - GraphRouter / RouteProfile / IRT-Router（新 candidate 泛化 / profile 主线）
- 然后再往上接 TAB / TrACE / GraphPlanner / Agent Capsules（runtime control 主线）

### 12.3 我会如何用它指导两个最终 target？
- 对 General Router：
  - 这篇非常有价值，几乎可以直接作为 v1 evaluator + policy family + objective layer 的设计参考
- 对 Coding Agentic Router：
  - 它更像前导综述，告诉我 routing object 不应只限于 model generation，但真正的 agent runtime state/action 还要靠后续 agentic 论文细化

## 13. 我对这篇 survey 的最终定位

- 它不是“替代 2603.04445 的更好版本”，而是一个不同切口：
  - `2603.04445` 更适合你做方法空间地图
  - `2502.00409` 更适合你做系统设计拆解
- 如果只保留一篇做 taxonomy，我会保留 2603.04445。
- 如果只保留一篇做 system design grounding，我会强烈保留 2502.00409。
- 最好的用法不是二选一，而是把它们并排读：
  - 一篇告诉你“有哪些范式”
  - 一篇告诉你“真正部署时要怎么组织这些范式”

## 14. 可复现性 / 资源开放记录

### 14.1 是否开源
- 论文公开页未明确给出 survey 自己的代码仓库；当前更适合记为“未验证到官方代码仓库”。

### 14.2 数据是否公开
- 这是一篇 survey，本身不依赖单一新数据集；主要引用已有 benchmark 与方法仓库。

### 14.3 关键可复现信息
- 关键可复现信息主要体现在：
  - 明确定义了 cost / performance / budget 形式化问题
  - 给出了 pre-generation 与 post-generation 的图示与定义
  - 列出 similarity / supervised / RL / generative 的方法映射表
  - 给出了标准化 benchmark 和 baseline 的建议

## 15. 一句话结论

> 这篇 survey 最适合你的地方，不是它又列了一堆 routing 论文，而是它把 router 重新定义成“带预算约束的系统资源优化器”，并明确指出 routing 不只发生在 model generation，而可以扩展到 prompt、retrieval、context 与整个 LLM-based system 的多个步骤。