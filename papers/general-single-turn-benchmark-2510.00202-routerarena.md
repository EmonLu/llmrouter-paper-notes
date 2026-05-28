# RouterArena: An Open Platform for Comprehensive Comparison of LLM Routers

## 1. 论文基本信息
- 标题：RouterArena: An Open Platform for Comprehensive Comparison of LLM Routers
- 作者 / 机构：Yifan Lu, Rixin Liu, Jiayi Yuan, Xingqi Cui, Shenrun Zhang, Hongyi Liu, Jiarong Xing；Rice University
- 发表时间：2025-09（arXiv 首次提交），当前查看版本为 2025-11-27 的 v3
- 会议 / 期刊：Preprint / arXiv
- 论文链接：https://arxiv.org/abs/2510.00202
- 代码链接：
  - GitHub：https://github.com/RouteWorks/RouterArena
  - leaderboard：https://routeworks.github.io/
  - 数据集：https://huggingface.co/datasets/RouteWorks/RouterArena
- 本地 PDF：`pdfs/general-single-turn-benchmark-2510.00202-routerarena.pdf`
- 抽取文本：`.tmp_pdftext/general-single-turn-benchmark-2510.00202-routerarena.txt`
- 研究方向关键词：
  - `LLM Routing Benchmark`
  - `Router Leaderboard`
  - `Multi-metric Evaluation`
  - `Difficulty-aware Benchmarking`
  - `Commercial + Open-source Router Evaluation`

## 2. 一句话总结
- 总结：RouterArena 不是再提出一个新 router，而是把“谁来评测 router、怎么公平比较 router”这件事做成开放平台：它构建了一个覆盖 9 个知识域、44 个类别、8400 条 query 的难度分层数据集，定义 accuracy / cost / optimality / robustness / latency 五类指标和一个 live leaderboard，并同时纳入 academic router 与 commercial router，结果显示当前 router 普遍还不会高效识别“什么时候便宜模型已经够了”。

## 3. 研究问题
### 3.1 核心问题是什么？
- 现在问题已经不只是“给 query 选哪个模型”，而是“面对越来越多 router，该选哪个 router”。
- 现有 router benchmark 往往有四个缺口：
  - query 类别覆盖不够广
  - 没有真正区分难度层级
  - 指标只看 accuracy 或 deferral curve，缺少 optimality / robustness / latency
  - 很少把 commercial router 和 academic router 放在统一协议下比较
- 论文要解决的是：如何建立一个像模型竞技场那样、面向 router 的开放评测平台和排行榜。

### 3.2 为什么这个问题重要？
- 对 General Router 这条线来说，没有统一 evaluator，就很难判断一个新 router 的提升到底来自方法本身，还是来自它刚好绑定了更强模型池。
- 只看 accuracy 或 cost 单点会误导设计：实际部署里还要关心路由是否选到了“最便宜但仍正确”的模型、对噪声 query 是否稳定、路由自身是否太慢。
- 这篇 paper 的价值不在“教你一个更强 policy”，而在“把 router research 从各说各话，推进到统一 benchmark + leaderboard”。

### 3.3 主要优化目标是什么？
- 目标类型：评测标准化、cost-quality 比较、公平横评、部署相关指标补全、持续更新能力
- 我的理解：这篇论文服务的是 Track A（General Router）的 evaluation layer，而不是 policy layer。

## 4. 方法概览
### 4.1 提出的方法是什么？
- 论文提出的是一个开放评测平台，而不是单一新 router，核心有三层：
  1. 数据集层：基于 DDC（Dewey Decimal Classification）做知识域覆盖，基于 Bloom taxonomy 做认知层级覆盖，再用 42 个模型的经验正确率定义真实难度带
  2. 指标层：不仅看 query-answer accuracy 和 cost，还看 routing optimality、robustness、latency
  3. 框架层：提供自动评测框架，让新 router 可以提交预测结果或接入 API，自动更新 leaderboard
- 它和 RouterBench 的差别是：RouterBench 更像“冻结数据上的离线 benchmark”，RouterArena 更像“活的 leaderboard + evaluation service”。

### 4.1.1 算法的核心直觉是什么？
- 如果你想比较 router，就不能只固定一个小任务集或只看平均 accuracy。
- 一个真正有用的 router benchmark，至少要同时回答五件事：
  - 它在广泛 domain 上是否能工作
  - 它在 easy / medium / hard query 上是否呈现不同 routing 行为
  - 它是否真的省钱，而不只是追求高准确率
  - 它是否接近“最便宜的正确选择”
  - 它在 noisy input 和在线部署 latency 下是否仍可用
- 因此作者把“数据覆盖、难度建模、多维指标、自动评测”捆在一起设计，而不是只发一个静态数据包。

### 4.1.2 算法按步骤是怎么运行的？
- Step 1：从两个已有 LLM benchmark 数据集和 21 个开源领域数据集收集原始 query，得到约 62,000 条原始样本
- Step 2：按 DDC 思路整理出 9 个顶层 domain、44 个 category，并按 science : humanities = 2 : 1 做配额分配
- Step 3：用 DeepSeek-V3.1 做 LLM-as-a-judge，给 query 打 Bloom taxonomy 认知层级，用于保证认知技能覆盖；作者还做了小规模人工验证
- Step 4：用 sentence-transformers/all-MiniLM-L6-v2 做去重，选出覆盖广、重复少的最终样本
- Step 5：让 42 个模型回答这些 query，用“答对该题的模型数”来定义经验难度，并分成 hard / medium / easy 三档
- Step 6：对被测 router，收集其 model selection、latency、必要时的 confidence score
- Step 7：按 accuracy、cost、optimality、robustness、latency 计算分数，并汇总成 Arena leaderboard

### 4.1.3 如果把它压缩成一个伪代码 / 决策流，它长什么样？
- 数据构建：`raw datasets -> category balancing -> Bloom coverage labeling -> dedup -> final benchmark`
- 难度定义：`query -> run on 42 models -> #correct -> {hard, medium, easy}`
- Router 评测：`router API / prediction file -> model selection -> platform-side inference / cache -> metric computation -> leaderboard update`
- 排名逻辑：`accuracy + normalized cost -> Arena Score`，再加上 optimality / robustness / latency 等 rank 做综合排序

### 4.2 Router 的输入是什么？
- 对被测 router：输入是 benchmark query
- 对 RouterArena 框架：输入还包括
  - router 的访问方式（API / prediction file）
  - router 返回的 model selection
  - 某些 open-source router 的 confidence scores
- 对 Arena 排名器：输入是每个 router 的 accuracy、cost、optimality、robustness、latency 结果

### 4.3 Router 的输出是什么？
- 对被测 router：输出是选择哪个 candidate model，有些商业 router 直接返回最终答案
- 对评测平台：输出是多维 metric 和 leaderboard 排名

### 4.4 Routing 决策如何产生？
- 这篇 paper 本身不定义统一 routing policy；它评的是别人的 router。
- 被评估对象包括：
  - commercial：NotDiamond、Azure-Router、GPT-5 内置 router
  - open-source / academic：RouterBench-KNN、RouterBench-MLP、GraphRouter、CARROT、RouterDC、RouteLLM、vLLM-SR，以及 leaderboard 中出现的 MIRT-BERT / NIRT-BERT 等实现名
- 也就是说，RouterArena 的“决策机制”是：让各 router 保持原方法，平台只统一输入、记录输出、计算指标。

### 4.5 是否需要训练 Router？
- 对 RouterArena 平台本身：`否`
- 对被测 router：`部分需要`
  - commercial router：直接调用 API，无需额外训练
  - academic router：按各自论文 / 开源实现的原始训练流程训练
- 论文明确说，他们尽量不修改原始训练数据、任务分类与模型池配置。

### 4.6 涉及哪些学习机制？
- 平台本身涉及：
  - LLM-as-a-judge（Bloom 层级标注）
  - embedding-based deduplication
  - multi-metric ranking
- 被测 router 涉及的学习机制则很多：
  - KNN / MLP
  - graph neural network routing
  - contrastive learning
  - item response theory
  - binary strong/weak routing
  - semantic category routing
- 我的理解：这篇论文的重要点不是发明新学习算法，而是把异构 router 放到统一 protocol 下。

## 5. 系统架构
### 5.1 整体 Pipeline
- Dataset builder：构建 9 domain / 44 category / 8400 query 的评测集
- Difficulty engine：基于 42 模型正确数定义经验难度
- Metric engine：计算 accuracy、cost、optimality、robustness、latency
- Evaluation runner：向 router 发送 query，必要时在平台侧执行模型推理并使用缓存
- Leaderboard layer：生成 Arena score 与其他子榜单
- Submission workflow：支持提交新 router 预测结果并触发自动评测

### 5.2 包含哪些模型 / 模块？
- 数据构建模块：
  - DDC-based domain/category organizer
  - Bloom coverage annotator
  - deficit redistribution sampler
  - deduplication module
- 评测模块：
  - router adapter / API 接入层
  - latency monitor
  - metric calculator
  - leaderboard aggregator
- 模型相关：
  - 42 个模型用于经验难度定义
  - 各 router 保持自己的独立 model pool，而不是强行统一成单一候选池
  - Table 3 给出了各 router 的 model pool，例如 RouterBench、GraphRouter、Universal、CARROT、RouterDC、IRT-Router、RouteLLM 等各不相同

### 5.2.1 Router 本身用的是什么模型？
- 这篇 paper 不是单一 router 论文，因此这一栏应该理解为“被评估的 router 类型谱系”：
  - 商业托管 router / API router
  - KNN / MLP baseline
  - GNN router
  - contrastive router
  - IRT-style router
  - binary router
  - BERT-based semantic router
- 我对这个设计的理解：作者有意避免把平台绑死在某一类 router 上，而是把不同 family 都纳入。

### 5.2.2 候选大模型池由哪些模型组成？
- 没有一个统一候选池。
- 每个 router 继承自己的原始 model pool，因此这篇论文更像“router-of-routers benchmark”，而不是“同池比拼”的单一实验。
- 平台另外使用 42 个模型来定义经验难度，这 42 个模型来自各 router 的 pool，覆盖不同参数规模、架构和 provider。

### 5.2.3 这些模型之间的能力差异是怎么被利用的？
- 一方面，router 本身利用不同模型的 cost / capability 差异做选择。
- 另一方面，平台反过来利用这些差异来定义 query 的经验难度：如果很多模型都能答对，就是 easy；只有极少数模型能答对，就是 hard。
- 这是这篇 paper 最值得记的一点：它不是直接用“题目来源”或“人类主观难度”定义难题，而是用模型群体行为定义难题。

### 5.3 路由发生在哪个阶段？
- 路由阶段：query-level，模型生成前
- 评测阶段：router 选模型后，平台记录其选择、推理成本、结果质量与额外开销

### 5.4 是否支持 fallback / cascade / online update？
- 动态 fallback：`取决于被测 router，本平台可评但自己不定义`
- cascade：`取决于被测 router`
- multi-step decision：`主协议是单次 query-level 选择，不是 agent runtime 多步控制`
- online update：`平台支持 leaderboard 持续更新，但不是在线学习型 router`

### 5.5 我的理解
- RouterArena 是 RouterBench 的下一阶段：
  - RouterBench 偏离线、偏 frozen corpus
  - RouterArena 偏开放平台、偏 live leaderboard
- 它对你当前仓库的直接价值很高，因为它把“数据集、难度、指标、公开提交流程”一次性补齐了。
- 如果 Track A 要做成长期研究工作台，RouterArena 比单篇 policy paper 更像“评测底座 blueprint”。

### 5.6 如果新增一个候选大模型，router 需要付出什么代价？
- 这篇论文关注的是“新增一个 router 怎么接入 arena”，不是“单个 router 新增模型怎么重训”。
- 从平台角度看：
  - 是否支持低成本新增 router：`相对支持`
  - 新增 router 时需要做什么：提供 API / prediction file，按其 model pool 跑评测
  - 是否需要平台重训：`不需要`
  - 是否需要重跑 benchmark：`需要重新在 benchmark 上评测该 router`
  - 我判断的接入成本：中
  - 原因：评测协议公开、自动化程度高，但若 router 绑定商业模型或私有 API，评测成本和权限门槛仍在

## 6. 实验设置
### 6.1 使用了哪些数据集？
- RouterArena 自建评测集：最终 `8,400` 条 query，来自 `23` 个源数据集
- 原始收集阶段：来自 `2` 个已有 LLM benchmark 数据集 + `21` 个开源领域数据集，共约 `62,000` 条 raw queries
- 额外附录实验：LongBench-v2 长上下文子集（随机采样 100 条 short / medium length queries）

### 6.1.1 数据集是怎么来的？
- 数据来源：已有 benchmark + 多个开源领域数据集
- 构造方式：
  - 按 DDC 做 domain / category 覆盖
  - 按 Bloom taxonomy 做认知层级覆盖
  - 按 deficit redistribution 做配额平衡
  - 按 embedding 相似度去重
  - 按 42 模型正确率定义最终难度带
- 是否有人工标注：有小规模人工验证 Bloom 层级
- 是否有模型打标 / judge：是，Bloom 层级由 DeepSeek-V3.1 judge 辅助标注
- 我对数据可靠性的判断：相对强。它不是随便拼 benchmark，而是明确把“领域覆盖、认知覆盖、经验难度、去重”都写进构建流程。

### 6.1.2 数据集里具体包含什么？
- 样本形式：单条用户 query / 问题
- 输入字段：query 文本、domain/category、Bloom 相关信息、经验难度信息等
- 输出/标签字段：
  - benchmark 正确性标签
  - 各 router 的 model selection
  - accuracy / cost / optimality / robustness / latency 等评测结果
- 覆盖任务：9 个顶层 domain、44 个 category
- 数据规模：8400 query
- 我的理解：它不像 RouterBench 那样以“预收集所有模型输出”为中心，而更像“面向开放提交的 query benchmark + metric platform”。

### 6.1.3 这些数据集和真实 router 场景有多接近？
- 比传统 academic benchmark 更接近真实场景，因为它显式引入了商业 router、噪声鲁棒性和 latency。
- 但它仍然主要是单轮 query-level benchmark，不是长会话、多轮 agent、tool-use runtime benchmark。
- 所以它更适合 Track A，而不是直接作为 Coding Agentic Router 的终局评测集。

### 6.2 对比了哪些 Baseline？
- commercial routers：NotDiamond、Azure-Router、GPT-5
- academic / open-source routers：
  - RouterBench-KNN
  - RouterBench-MLP
  - GraphRouter
  - CARROT
  - RouterDC
  - RouteLLM
  - vLLM-SR
  - leaderboard 中还包含 MIRT-BERT、NIRT-BERT 等实现名
- 附录还给出各 router 的具体 model pool

### 6.3 评估了哪些任务类型？
- 广域知识问答 / 学科类 query
- 不同认知技能层级 query
- easy / medium / hard 三档经验难度 query
- noisy prompt robustness 场景
- long-context routing（LongBench-v2 子实验）

### 6.4 使用了哪些大模型或专家模型？
- 用于定义经验难度的模型总数：42
- 被测 router 总数：12 个进入主 leaderboard
- commercial router 侧：NotDiamond、Azure-Router、GPT-5 family
- open-source / academic router 侧：RouterBench 系、GraphRouter、CARROT、RouteLLM、RouterDC、vLLM-SR 等
- 关键点：每个 router 的 candidate pool 不同，因此这个 benchmark 不是“统一同池控制变量实验”，而是“真实 router 生态比较”。

### 6.5 主要评估指标是什么？
- Query-answer Accuracy
- Query-answer Cost
- Routing Optimality
  - Optimal Selection Ratio
  - Optimal Accuracy Ratio
  - Optimal Cost Ratio
- Routing Robustness
- Routing Latency
- 以及综合的 Arena Score

### 6.5.1 每个评估指标分别在衡量什么？
- Accuracy：
  - 衡量含义：router 最终把 query 导向能答对的模型的能力
  - 高/低分别意味着：高说明 quality 好；低说明选模经常错
  - 对 router 设计的启发：不能只看 cheap routing，还得看最终正确率
- Cost：
  - 衡量含义：router 路由决策带来的实际推理成本
  - 高/低分别意味着：高表示更依赖昂贵模型；低表示更会利用便宜模型
  - 对 router 设计的启发：需要显式学会“何时小模型已足够”
- Optimality：
  - 衡量含义：是否选到“最便宜但仍正确”的模型，以及与 pool 内最优上界有多接近
  - 高/低分别意味着：高说明真的会做经济型 routing；低说明经常花冤枉钱
  - 对 router 设计的启发：这是比 accuracy 更接近 deployment value 的指标
- Robustness：
  - 衡量含义：对 paraphrase、typo、语法扰动后的选择是否稳定
  - 高/低分别意味着：高说明 query 表面噪声不容易让 router 抖动；低则线上风险大
  - 对 router 设计的启发：embedding / classifier 侧的表面敏感性是个大问题
- Latency：
  - 衡量含义：router 自身引入的额外延迟
  - 高/低分别意味着：高说明 router 可能成为 critical path bottleneck；低说明部署友好
  - 对 router 设计的启发：router 不能比被选的小模型还“重”

### 6.5.2 这些指标有没有盲点？
- 最大盲点是：不同 router 的 model pool 不同，因此“整体排名”不可直接当成纯算法排名。
- 另一个盲点是：它仍然主要看 query-level 选择，不覆盖 agent trajectory 成功率。
- 对某些 commercial router，如果它不暴露 model selection，只返回最终答案，则部分 optimality 类指标无法测。

## 7. 核心结果
### 7.1 最重要的实验结果是什么？
- RouterArena 主 leaderboard 的综合排序不是“GPT-5 第一”，而是：
  1. Azure-Router（平均 rank 4.40）
  2. RouteLLM（5.0）
  3. MLP（5.67）
  4. MIRT-BERT（4.50）
  5. vLLM-SR（7.17）
  6. RouterDC（5.67）
  7. GPT-5（5.0）
  8. GraphRouter（5.50）
  9. CARROT（5.83）
  10. NIRT-BERT（6.50）
  11. KNN（6.83）
  12. NotDiamond（8.80）
- 但如果只看 Arena Score，Figure 1 给出的 quick view 更偏 accuracy-cost 维度，前几名是 MIRT-BERT、Azure-Router、NIRT-BERT，而不是综合榜单顺序。
- 这说明：你不能只看一个分数，router 评价必须多维。

### 7.2 相比 Baseline 提升了什么？
- 相比过往 benchmark：
  - query category 从 24–27 类扩展到 44 类
  - 不再只给静态 deferral curve 或 accuracy
  - 引入 commercial routers
  - 提供真正的 multi-metric leaderboard
- 相比“只看 accuracy”的思路：
  - 论文明确展示高准确率往往靠高成本换来
  - 当前 router 远没有学会稳定利用便宜模型
- 相比纯 academic offline benchmark：
  - 它把开放提交、自动化评测和 live leaderboard 带进来了

### 7.3 trade-off 如何？
- Oracle accuracy 是 `90.89%`，但现实中所有 router 都明显低于这个上界。
- Table 6 的 overall accuracy / cost 非常能说明问题：
  - GPT-5：`74.0%`，`$14.02 / 1k queries`
  - Azure-Router：`68.1%`，`$0.54`
  - NotDiamond：`68.0%`，`$9.34`
  - vLLM-SR：`67.3%`，`$1.67`
  - CARROT：`67.2%`，`$2.06`
  - MIRT-BERT：`66.9%`，`$0.15`
- 论文明确指出：
  - commercial routers 往往更偏 accuracy 端，但成本高
  - open-source routers 往往更偏效率端，但上限更早饱和
- 一个很强的结论是：像 vLLM-SR 和 CARROT 这样的 router，大约能做到“成本下降约 35%，准确率损失不到 2%”这一类更接近部署价值的 trade-off。

### 7.4 Ablation / Sensitivity / Appendix 关键补充
- 难度分层验证：
  - easy 题大多数 router 准确率都 > 89%
  - hard 题很多 router 掉到 10% 以下，说明难度带确实不是摆设
- 按难度分层的 Table 6：
  - GPT-5 在 hard query 上也只有 `27.5%`，但成本飙到 `$35.73`
  - Azure-Router 在 hard 上 `17.9%` / `$1.05`
  - MIRT-BERT 在 hard 上 `7.1%` / `$0.26`
  - 这说明“hard query 识别 + 只在必要时升级预算”仍然是巨大机会点
- Robustness / latency：
  - robustness 最好的是 RouteLLM `100.00%`、GraphRouter `94.29%`、CARROT `89.05%`
  - robustness 最差的是 vLLM-SR `35.00%`
  - latency 最慢的是 vLLM-SR `546.8ms`、RouteLLM `259.0ms`
  - latency 较好的是 MLP `11.1ms`、Kmeans `11.3ms`、MIRT-BERT `13.7ms`
- LongBench-v2：
  - GPT-5：`71% / $45.70`
  - NotDiamond：`70% / $59.30`
  - Azure-Router：`67% / $9.54`
  - NIRT-BERT：`60% / $6.60`
  - MIRT-BERT：`60% / $7.50`
  - RouteLLM 无法评测，因为其 text encoder 上限是 8192 tokens

### 7.5 从这些实验结果里，能看出这个方法真正的优势是什么？
- 真正优势不是“证明某个 router 赢了”，而是证明 router 评价必须多维。
- 它让你看到三种以前容易被混掉的对象：
  - 高 accuracy 但极贵
  - 很会省钱但 accuracy 不够
  - latency 很差、robustness 很差，即使 accuracy 还行也不适合部署
- 这对你做系统设计很关键，因为这意味着 evaluator 至少要保留 cost / quality / latency / robustness 四个轴，而不是只保留 frontier 一条线。

### 7.6 这些结果说明它更适合哪类场景？
- 非常适合：General Router 的 benchmark / evaluation anchor
- 适合：持续接入新 router 的公开 leaderboard
- 较不直接适合：SWE-bench agent trajectory 这类 runtime-control 任务
- 但有方法论启发：未来 agentic benchmark 也应该学它的多维评分和 live leaderboard 设计

## 8. 贡献与创新点
### 8.1 主要贡献
- 提出 RouterArena：面向 LLM routers 的开放评测平台
- 构建覆盖 9 domains、44 categories、8400 queries 的 query benchmark
- 用 42 模型正确率定义经验难度，而不是只靠主观难度标签
- 定义 accuracy / cost / optimality / robustness / latency 多维指标体系
- 提供自动评测框架和 live leaderboard，支持 academic + commercial router 一起比较

### 8.2 相比已有方法的新意
- 相比 RouterBench：更像 live leaderboard，而不是冻结结果集
- 相比只看 accuracy 的 benchmark：把 optimality、robustness、latency 明确拉进主指标
- 相比只评 academic router 的工作：把 commercial router 纳入统一协议
- 相比只做数据集的工作：还把自动提交、评测和排行榜工作流做出来了

### 8.3 创新类型
- 创新类型：新的 benchmark、新的评测指标组合、新的 leaderboard / evaluation framework、开放提交流程
- 我的判断：这是 routing 方向的“评测基础设施型论文”，重要性非常高。

## 9. 局限性
### 9.1 方法有哪些假设？
- 假设 query-level router 是当前最值得标准化评测的对象
- 假设不同 router 即使 model pool 不同，也仍然值得放到同一 arena 下比较
- 假设经验难度（42 模型正确数）能较好刻画 routing 难度

### 9.2 是否依赖特定模型、数据集或人工标注？
- 是。
- 难度定义依赖 42 个具体模型集合；未来模型生态变化后，难度分布可能会移动。
- Bloom 层级依赖 DeepSeek-V3.1 judge，虽然作者做了人工验证，但它仍然不是完全人工 gold label。
- commercial router 的复现依赖外部 API 和权限。

### 9.3 是否存在泛化性、稳定性、成本、延迟、可解释性或部署方面的问题？
- 存在公平性张力：不同 router 的 model pool 不同，综合榜更像“系统结果比较”，不是纯 policy apples-to-apples。
- 鲁棒性总体偏弱，尤其 BERT-based router 对表面扰动敏感。
- 某些 router latency 很高，路由自身可能成为部署瓶颈。
- 仍然局限于 query-level，不适合直接评价 agent runtime controller。

### 9.4 作者自己提到的 limitation 是什么？
- 某些 commercial router 不暴露 model selection，只返回答案，因此部分指标无法完整测量。
- 当前所有 router 都显著落后于 oracle，说明现有方法仍不会高效利用小模型。
- 不同场景下 accuracy-cost frontier 差异明显，没有 universally optimal router。
- 论文也承认 robustness 和 latency 暴露了新的研究问题，不能只盯 accuracy-cost。

### 9.5 我认为还有哪些潜在问题？
- live leaderboard 比 frozen corpus 更贴近真实世界，但也带来更弱的时间一致性：不同时间 API 价格、模型版本、路由产品都可能变化。
- 如果未来要做更严格的科学比较，可能还需要保留一套 frozen split 作为长期锚点。
- 对你来说，最大缺口是它还没有把 multi-turn agent / tool-use / repo-state 纳入评测对象。

## 10. 对我的启发
### 10.1 对 agentic router 的帮助
- 直接帮助不在“可以拿它去评 SWE-bench”，而在“可以照着它设计 agentic leaderboard”。
- 你后面如果做 Coding Agentic Router，完全可以借它的四个设计原则：
  - domain / task 覆盖要系统化
  - 难度不要只靠人工主观定义
  - 指标不能只有 success rate
  - 要支持新 controller 的持续提交和公开比较

### 10.2 可借鉴的方法部件
- 用模型群体行为定义经验难度
- 用多维指标而不是单点 accuracy 排名
- 用自动评测框架 + leaderboard 取代一次性论文表格
- 用 robust / latency 两个部署指标防止“学术上好看、工程上难用”的 router 排名过高

### 10.3 可扩展想法
- 为 General Router 单独做你自己的 frozen evaluator，同时参考 RouterArena 保留 live leaderboard
- 为 Coding Agentic Router 做一个“trajectory arena”：
  - state difficulty
  - recovery cost
  - token/time budget
  - patch success
  - trajectory robustness
- 把“最便宜但正确的 action”从 model selection 扩展到 `(model, budget, workflow, granularity)` selection

### 10.4 适用场景
- 企业 /研究团队要选一个现成 router：非常适合
- 你要比较自己新 router 和已有方法：非常适合
- 你要做 query-level General Router evaluator：非常适合
- 你要直接评 coding-agent runtime controller：不够，需要 agentic 版扩展

## 11. 可复现性记录
### 11.1 是否开源代码？
- `是`
- GitHub：https://github.com/RouteWorks/RouterArena
- README 明确提供了本地评测、下载数据集、运行 evaluation、提交 leaderboard 的流程

### 11.2 是否开源数据？
- `是，但完整复跑 commercial router 仍需要外部 API / 成本条件`
- 已确认公开入口：
  - Hugging Face dataset：https://huggingface.co/datasets/RouteWorks/RouterArena
  - live leaderboard：https://routeworks.github.io/leaderboard
- 我的判断：benchmark 数据集和自动化评测框架是公开的；但如果你想完全复刻论文里所有商业 router 结果，仍受 API 访问和时间漂移影响。

### 11.3 关键实现细节是否清楚？
- 较清楚：
  - 数据构建原则清楚
  - 8400 / 23 / 9 / 44 这些关键统计清楚
  - 42 模型定义经验难度的逻辑清楚
  - 五类指标及 Arena Score 清楚
  - 自动评测 / 提交流程在仓库 README 中可见
- 仍有几个复现摩擦点：
  - 不同 router 的实现名和 leaderboard 显示名并不总是一一对应
  - commercial router 的模型选择有时不可见
  - live leaderboard 天生会随时间变化

### 11.4 复现难度如何？
- 复现难度：中
- 原因：
  - 本地跑开源框架和公开数据集并不算难
  - 但要重跑所有商业 router、保持与论文同时间点价格和版本一致，难度明显更高

### 11.5 如果我要复现，第一步应该做什么？
- 第一阶段先别追求完整复刻论文榜单；先下载 `RouteWorks/RouterArena` 数据集和代码，跑通一个 open-source router 的本地评测流程，确认 accuracy / cost / latency / robustness 指标都能稳定算出来。

## 12. 横向比较字段
- Routing 对象：router 本身，而不是单个模型
- Routing 粒度：query-level benchmark
- Router 类型：benchmark / leaderboard / evaluation framework
- 是否训练：平台本身不训练；被测 router 部分需要
- 训练信号：各 router 使用自己的原始训练信号
- 优化目标：多维评测下的 router 比较，核心是 accuracy-cost-optimality-robustness-latency
- 支持的模型数量：难度定义用 42 个模型；主榜评估 12 个 routers
- 是否考虑成本：是
- 是否考虑延迟：是
- 是否 online：平台持续更新是，但不是 online-learning router
- 是否开源：是
- 主要优点：benchmark 设计完整、指标全面、支持 commercial router、可持续更新
- 主要缺点：不同 router 的 model pool 不统一；query-level 为主；live leaderboard 有时间漂移

## 13. 阅读后的评分
- 相关性：`5`
- 方法新颖性：`4`
- 实验可信度：`5`
- 工程可落地性：`5`
- 对我研究 / 工作的启发：`5`

### 总评
- 是否值得精读：`是`
- 是否值得复现：`是`
- 是否值得纳入自己的系统设计：`是，尤其是 Track A 的 evaluator 设计`
- 一句话结论：如果 RouterBench 解决的是“怎样做一个离线 router benchmark”，那 RouterArena 解决的就是“怎样把 router 评测做成活的公共基础设施”；对你现在的仓库，它是 General Router 这条线里非常关键的一篇评测底座论文。