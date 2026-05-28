# RouteProfile: Elucidating the Design Space of LLM Profiles for Routing

## 1. 论文基本信息
> 记录论文的元信息，便于快速定位、引用和分类。

- 标题：RouteProfile: Elucidating the Design Space of LLM Profiles for Routing
- 作者 / 机构：Jingjun Xu, Hongji Pu, Tao Feng, Haozhen Zhang, Jiaxuan You, Ge Liu；University of Illinois Urbana-Champaign、Nanyang Technological University
- 发表时间：2026-04 / 2026-05（首页显示 arXiv:2605.00180v1，提交日期为 2026-04-30）
- 会议 / 期刊：Preprint / arXiv
- 论文链接：https://arxiv.org/abs/2605.00180
- 代码链接 / 资源：Hugging Face Collection: `ulab-uiuc/RouteProfile`
- 研究方向关键词：
  - `LLM Routing`
  - `Model Profiling`
  - `Cold-start Routing`
  - `Graph-based Profiling`
  - `Profile-Router Co-design`

## 2. 一句话总结
> 用一句话说明：这篇论文解决了什么问题、用了什么方法、取得了什么结果。

- 总结：RouteProfile 不再把重点放在 router 机制本身，而是系统研究“LLM profile 如何设计”这一此前被忽视的环节，把 profile 设计抽象为组织形式、表示类型、聚合深度和学习配置四个维度，并在 SimRouter、MLPRouter、GraphRouter 上系统比较，发现 structured profile 持续优于 flat profile、query-level 信号比 domain-level 更可靠、对新模型冷启动泛化最有帮助的是 trainable structured profiles。

## 3. 研究问题
> 这一部分回答“为什么要做这件事”。

### 3.1 核心问题是什么？
- 现有 LLM routing 研究大多聚焦于 router 机制设计，但 candidate LLM 的 profile（模型能力表示）设计常被混在系统里，缺少独立研究。
- 论文要回答：不同 profile design 会如何影响 routing performance，以及这种影响是否跨 router 机制稳定存在。
- 更进一步，它问的是：routing 的性能提升，到底来自更强 router，还是更强 model profile？

### 3.2 为什么这个问题在大模型路由场景中重要？
- 这篇论文直接命中多模型路由中的一个关键盲点：
  - query 有 embedding，很多人认真做；
  - candidate model 往往只给一个 one-hot ID 或一句描述，信息很弱。
- 如果 profile 不够好，再强的 router 也只能在很弱的 candidate representation 上做决策。
- 对公平比较也很关键：不同论文如果 profile side 差异很大，就很难说是谁的 router 更好。

### 3.3 该问题主要对应哪些目标？
> 可多选：质量、成本、延迟、可扩展性、鲁棒性、可解释性、在线适应性、部署效率等。

- 目标类型：质量、泛化性、可扩展性、冷启动能力、可解释性
- 我的理解：论文最主要的目标不是 cost，而是提高 router 对模型能力差异的建模质量，特别是提高对新引入模型的泛化能力。

## 4. 方法概览
> 这一部分回答“它是怎么做的”。

### 4.1 论文提出的方法是什么？
- 论文提出一个通用的 LLM profiling 设计空间框架 RouteProfile，把 profile construction 抽象为四个维度：
  1. Organizational form：Flat / Structured
  2. Representation type：Text / Embedding
  3. Aggregation depth：hop K
  4. Learning configuration：Training-free / Trainable
- 它不提出单一新 router，而是提出统一 profile construction framework，并在多个已有 router 上做系统评估。

### 4.2 Router 的输入是什么？
> 例如：query、历史对话、用户画像、候选模型特征、预算、延迟约束、环境状态等。

- 输入：
  - query 文本，经 Longformer 编码成 query representation
  - candidate model profile
- profile 的原始信息来源包括四类：
  - model family
  - domain coverage
  - task evaluation
  - query-level instance
- 这些信息被组织为异构 interaction graph。

### 4.3 Router 的输出是什么？
> 例如：选择哪个模型、是否 fallback、是否 cascade、是否继续推理、分配多少预算等。

- 输出：
  - 对每个 query 选择最适合的 candidate LLM
  - 在 cold-start setting 下，也衡量是否能把 query 正确路由给 newly introduced model

### 4.4 Routing 决策是如何产生的？
> 例如：规则、分类器、打分器、排序器、policy、bandit、gating network 等。

- 决策机制不固定，论文故意把“profile design”与“router design”解耦。
- 下游使用 3 个代表性 router：
  - SimRouter：非参数，相似度匹配
  - MLPRouter：MLP 投影后做相似度排序
  - GraphRouter：基于异构图和 GNN 的路由
- RouteProfile 的作用是为这些 router 提供不同质量的 candidate profile 输入。

### 4.5 是否需要训练 Router？
- 是否训练：`视下游 router 与 profile 配置而定`
- 如果需要，训练数据是什么：
  - 对 trainable profile，使用 interaction graph 中被 mask 的 node / edge 特征做自监督重建
  - 对 MLPRouter / GraphRouter，下游还会各自训练路由模块
- 训练目标是什么：
  - Trainable GNN profile 的目标是 masked reconstruction（Lnode + Ledge，MSE）
  - 下游 router 则优化其模型选择目标

### 4.6 涉及哪些学习机制？
> 可多选：强化学习、监督学习、蒸馏、bandit、ranking、classification、gating、heuristic 等。

- 学习机制：自监督图学习、表征学习、相似度排序、MLP 投影、GNN message passing
- 我的理解：论文的关键不是换一个新的决策器，而是把 model-side representation 做强。

## 5. 系统架构
> 这一部分回答“它在系统里怎么接入”。

### 5.1 整体 Pipeline 是怎样的？
- 上游：构建 interaction graph
  - 节点类型：model、model family、domain、task、query
  - 边类型：model-family、model-task、task-domain、task-query
- 中间：根据四维设计空间构造 LLM profiles
  - flat aggregation
  - text-based GNN
  - embedding-based GNN
  - trainable GNN
- 下游：把 profile 喂给不同 router，在 standard 与 new-LLM setting 下评估路由表现。

### 5.2 包含哪些模型 / 模块？
- Interaction graph construction 模块
- Flat profile 构造器
- Text-based GNN（text-space message passing，靠 LLM summarization）
- Embedding-based GNN（GCN 风格聚合）
- Trainable GNN（HANConv backbone，自监督重建）
- 下游 routers：SimRouter、MLPRouter、GraphRouter
- Query encoder：Longformer

### 5.3 路由发生在哪个阶段？
> 例如：请求进入前、生成前、生成中、agent planning 阶段、tool 调用前后等。

- 路由阶段：请求进入后、模型调用前
- profile construction 是离线预处理；在线阶段主要是 query encoding + model selection。

### 5.4 是否支持以下能力？
- 动态 fallback：`否`
- cascade：`否`
- multi-step decision：`否（主流程是单步模型选择）`
- online update：`否`

### 5.5 我对系统架构的理解
- RouteProfile 可以看作“candidate model feature engineering / representation learning 框架”。
- 它的思想是：不要只优化 router 头部，要把 candidate side 也做成结构化知识整合系统。
- 这对后来很多 router 工作都适用，因为 profile 可插拔到不同 router 中。

## 6. 实验设置
> 这一部分记录实验是否可信、是否和你的场景相关。

### 6.1 使用了哪些数据集？
- Interaction graph 构建：15 个数据集，覆盖 4 个能力域：knowledge、reasoning、math、coding
- Downstream routing evaluation：12 个数据集，每个数据集采样 50 个样本
- Appendix / Table 7 把两部分数据拆得更清楚：
  - Profile construction 侧包括 BBH、MATH500、GPQA-Diamond、MuSR、MMLU-Pro、AGIEval、TheoremQA、DROP、TruthfulQA、WinoGrande、BoolQ、C-Eval、SQuAD、MultiPL-E、EvalPlus
  - Routing evaluation 侧包括 MGSM、GSM8K、AgentVerse、CommonsenseQA、OpenBookQA、ARC-Challenge、MMLU、NaturalQA、TriviaQA、CommonGen、MBPP、HumanEval
- Appendix / Table 5 还给出了 query node 构建所依赖的 Hugging Face dataset identifiers，例如：`HuggingFaceH4/MATH-500`、`lukaemon/bbh`、`TIGER-Lab/MMLU-Pro`、`allenai/WildBench`、`evalplus/humanevalplus` 等。
- 因此这篇论文的数据开放状态可以较明确地记为“部分公开”：底层 benchmark 与一部分 HF 数据入口公开，但 interaction graph、profile text 以及缓存的多模型交互结果仍主要依赖作者资源构建。

### 6.2 对比了哪些 Baseline？
- 论文的 baseline 重点不是其他 routing 论文，而是 profile design baseline：
  - Flat Index
  - Flat Text
  - Structured Text (different hops)
  - Structured Embedding (different hops)
  - Structured Embedding Trainable (different hops)
- 下游 router baseline：
  - SimRouter
  - MLPRouter
  - GraphRouter

### 6.3 评估了哪些任务类型？
> 例如：chat、QA、math、code、tool-use、agent tasks、benchmark routing tasks 等。

- Knowledge QA
- Reasoning
- Math
- Coding
- 冷启动新模型路由

### 6.4 使用了哪些大模型或专家模型？
- Interaction graph 中总共 25 个 LLM，来自 5 个 model families
- 下游固定 candidate pool 为 8 个 LLM，来自：
  - Qwen2 / Qwen2.5
  - Llama
  - Gemma2
  - Mistral
  - Mixtral
- Appendix / Table 8 明确给出了 8 个 candidate models：
  - Llama-3.2-3B-Instruct
  - Qwen2.5-7B-Instruct
  - Llama-3.1-8B-Instruct
  - Gemma-2-9B-IT
  - Mistral-Small-24B-Instruct-2501
  - Mixtral-8x7B-Instruct-v0.1
  - Llama-3.3-70B-Instruct
  - Mixtral-8x22B-Instruct-v0.1
- 同一张表还列出 17 个 auxiliary models，用来给 profile construction 提供图结构上下文，如 Qwen2.5-3B/14B/32B/72B、Gemma-2-2B/27B、Qwen2-7B/72B、Ministral-8B、Mistral-Nemo、Mistral-Large-Instruct-2411 等。
- 新 LLM 冷启动设置中，Mistral-Small-24B-Instruct-2501 被设为 new LLM。

### 6.5 主要评估指标是什么？
> 例如：accuracy、win rate、cost、latency、token usage、throughput、success rate 等。

- Average response performance
- Cold-start Performance = 被路由到 new LLM 且回答正确的 query 比例
- 各 profile / router 组合下的平均性能
- 不同 aggregation hop 下的敏感性分析

## 7. 核心结果
> 这一部分只记录最关键结果，不要机械抄整张表。

### 7.1 最重要的实验结果是什么？
- 核心发现 1：structured profiles consistently outperform flat profiles。
- 核心发现 2：query-level signal 比 domain-level signal 更稳定、更有用。
- 核心发现 3：面对 newly introduced models，最好的是 structured + trainable profiles。
- Table 1 中可见代表性结果：
  - SimRouter：Flat Index 0.499，Flat Text 0.554，而 Structured + Emb + Trainable 可到 0.611 / 0.613
  - MLPRouter：Flat Index 0.593，Structured text/emb 可提升到约 0.625
  - GraphRouter：不同 structured profile 也普遍优于 flat，最好约 0.614，Flat Index 为 0.532

### 7.2 相比 Baseline 提升了什么？
- 相比 flat profile，structured profile 在三种 router 上都带来稳定增益。
- 在 RQ2 中：
  - 加 query-level signal 的收益普遍高于加 domain-level signal；
  - domain 节点很多时候不仅无益，甚至会削弱 profile 质量。
- 在 RQ3 中：
  - flat profiles 的 cold-start performance 近乎为 0；
  - trainable structured profiles 的 cold-start 表现显著更强。

### 7.3 是否在质量、成本、延迟之间取得了更好的 trade-off？
- 论文主要不讨论 cost / latency，而是 routing quality 与 generalization。
- 如果从系统实现角度看：
  - flat profile 最便宜但质量较差；
  - structured trainable profile 质量更高，但构建和训练成本也更高。
- 这更像 representation quality 与 system complexity 的 trade-off。

### 7.4 有哪些 Ablation Study 或 Sensitivity Analysis？
- aggregation hop 分析：1/2/3/4 hop
- training-free vs trainable
- text vs embedding representation
- query/task/domain signal source ablation
- standard routing vs new-LLM cold-start routing
- profile–router co-design 分析

## 8. 贡献与创新点
> 这一部分用于提炼“这篇论文为什么值得记”。

### 8.1 主要贡献是什么？
- 明确提出“LLM profile design 是 routing 的独立研究问题”。
- 给出统一的四维设计空间框架。
- 用 interaction graph 形式化多源异构模型能力信息。
- 系统展示 profile design 对标准路由与新模型冷启动路由的显著影响。

### 8.2 相比已有方法的新意在哪里？
- 与大多数论文只比较 router 机制不同，RouteProfile 把 profile 设计从附属输入提升为主研究对象。
- 它不局限某个固定 router，而是跨多个 router 展示 profile 设计的普适效果。
- 对“新模型冷启动”这一实际问题给出了系统视角。

### 8.3 创新类型属于哪一类？
> 可多选：新的 routing 策略、新的训练目标、新的数据构造方式、新的系统架构、新的 benchmark 等。

- 创新类型：新的系统架构、新的表征构造方式、针对 routing 的 profiling 框架
- 我的判断：这是“把 profile 侧方法论系统化”的论文，属于 routing 研究中的基础设施型工作。

## 9. 局限性
> 这一部分非常重要，用来防止“只看到优点”。

### 9.1 方法有哪些假设？
- 假设模型能力可由历史 benchmark interaction graph 充分刻画。
- 假设这些异构历史信号对真实线上 query routing 具有代表性。
- 假设 profile 质量提升能平移到不同 router / deployment setup。

### 9.2 是否依赖特定模型、数据集或人工标注？
- 依赖 benchmark interaction histories。
- 部分 node / task / model 描述需要由额外强 LLM 生成文本描述。
- trainable GNN profile 依赖图结构和足够多的辅助模型节点。

### 9.3 是否存在泛化性、稳定性、成本、延迟、可解释性或部署方面的问题？
- 成本：构建 interaction graph 和 trainable profile 本身有额外离线成本。
- 泛化性：虽然做了 new-LLM 测试，但仍基于 benchmark 数据，和真实线上 query 分布存在差异。
- 稳定性：随着 hop 增加，trainable setting 会出现 over-smoothing。
- 部署：若候选模型频繁变化，需要重复更新 profile graph。

### 9.4 作者自己提到的 Limitation 是什么？
- 结论中强调 gains are not realized uniformly across routers，说明 profile 与 router 需要 co-design，而不是 profile 越强越万能。
- 文中也显示 trainable 设置下更深 hop 会在 MLPRouter、GraphRouter 上退化，体现 profile 设计存在过平滑问题。

### 9.5 我认为还有哪些潜在问题？
- 论文更关注 average performance，没有显式纳入成本 / 延迟维度，因此对生产系统的指导还不完整。
- profile 构造依赖大量 benchmark 和结构知识，对新领域 / 私有任务接入门槛较高。
- 文中有些表格信息较密，若要复现需要仔细对齐具体数据源与模型列表。

## 10. 对我的启发
> 这一部分是把“读论文”变成“服务我自己的研究/工作”。

### 10.1 这篇论文对我理解大模型路由有什么帮助？
- 它让我更明确地意识到：router 的 query encoder 很多人在卷，但 candidate encoder / profile side 可能更被低估。
- 如果只用 one-hot 或模型名字符串做 candidate feature，很多路由能力其实还没被挖出来。

### 10.2 有哪些方法可以借鉴？
- 用 interaction graph 统一组织 model、family、task、query、domain 信息。
- 对新模型冷启动，不要只靠名字或参数规模，要利用 family / task / benchmark 结构信号。
- 做 router 实验时，应该把 profile design 作为独立变量控制住。

### 10.3 有哪些想法可以扩展？
- 可以在 RouteProfile 上进一步引入 cost、latency、license、tool-use capability 等系统侧特征。
- 可将 profile 与 user / org-specific history 联合，做 personalized routing。
- 可进一步做在线 profile update，把真实用户反馈纳入 graph。

### 10.4 是否能用于以下场景？
- 企业内部 Copilot：适合，尤其是候选模型多且经常新增时
- LLM 系统路由：非常适合
- 多模型选择：直接适用
- 成本优化：间接适用，需要补充成本维度
- Agent 系统：适合，可扩展到 tool / planner profile

## 11. 可复现性记录
> 这一部分帮助你判断：这篇论文是“能落地”还是“只能参考思想”。

### 11.1 是否开源代码？
- `是`
- GitHub：https://github.com/ulab-uiuc/RouteProfile
- 资源集合：Hugging Face Collection `https://huggingface.co/collections/ulab-ai/routeprofile`
- 这篇论文的 abstract / HTML 页面都直接给出了上述链接，因此这里不需要继续保留模糊占位表述。

### 11.2 是否开源数据？
- `部分是`
- 公开部分：多数底层 benchmark 可从 Hugging Face / 官方任务库获取，论文还给出了若干 query-node 构建用的 HF identifiers。
- 未完全公开部分：interaction graph、本地缓存的多模型响应、Text-GNN 生成的 profile 文本、以及 profile construction 过程中的派生 artifact 是否全部打包发布，当前未逐项验证到统一下载入口。
- 因此更准确的记录是：底层 benchmark 公开、代码和资源集合公开，但论文特有的 profiling 中间产物属于“部分公开”。

### 11.3 关键实现细节是否清楚？
- 整体设计空间、异构图定义、四类 profile 构造方式、下游 router 设置都比较清楚。
- Appendix 还补足了不少可复现信息：
  - 8 个 candidate models + 17 个 auxiliary models 的完整列表与规模
  - 15 个 profiling 数据集、12 个 routing evaluation 数据集的 cases / metric 统计
  - Text-GNN 在不同 node type 上的 prompt template
  - RQ3 新模型冷启动完整结果表
- 因而这篇论文在“实验配置和 profile 设计空间”层面已经较完整；真正较重的是要重建 interaction graph 与多模型历史交互，而不是信息完全缺失。

### 11.4 复现难度如何？
> 可用：低 / 中 / 高

- 复现难度：高
- 原因：
  - 数据与模型种类多；
  - 需要构图、文本 profile、embedding profile、trainable GNN 多套系统；
  - 还需在多个 router 上做交叉实验。

### 11.5 如果我要复现，第一步应该做什么？
- 先做最小化版本：固定一组 candidate models 和少量 benchmark，复现 Flat vs Structured profile 对 SimRouter / MLPRouter 的影响。
- 再逐步加异构图和 cold-start setting。

## 12. 横向比较字段
> 这一部分专门为后续表格对比服务，尽量用简短字段填写。

- Routing 对象：query → candidate LLM
- Routing 粒度：query-level
- Router 类型：profile framework + downstream routers
- 是否训练：可训练也可不训练
- 训练信号：self-supervised masked reconstruction（profile 侧）
- 优化目标：routing quality / cold-start generalization
- 支持的模型数量：8 candidate LLMs（图构建总计 25 models）
- 是否考虑成本：否
- 是否考虑延迟：否
- 是否 online：否
- 是否开源：是（代码与 HF 资源集合公开；数据与 profiling artifact 为部分公开）
- 主要优点：首次系统研究 profile 设计，且跨 router 有稳定发现
- 主要缺点：系统复杂、成本维度弱、复现重

## 13. 阅读后的评分
> 建议按 1-5 打分，便于后续快速筛选重点论文。

- 相关性：`5`
- 方法新颖性：`5`
- 实验可信度：`4`
- 工程可落地性：`3`
- 对我研究 / 工作的启发：`5`

### 总评
- 是否值得精读：`是`
- 是否值得复现：`部分值得`
- 是否值得纳入自己的系统设计：`是`
- 一句话结论：RouteProfile 非常适合用来补齐“候选模型表示”这一常被忽略的 routing 侧短板，是 foundation 路由研究里方法论价值很高的一篇。