# OptLLM: Optimal Assignment of Queries to Large Language Models

## 1. 论文基本信息
> 记录论文的元信息，便于快速定位、引用和分类。

- 标题：OptLLM: Optimal Assignment of Queries to Large Language Models
- 作者 / 机构：Yueyue Liu, Hongyu Zhang, Yuantian Miao, Van-Hoang Le, Zhiqiang Li；The University of Newcastle、Chongqing University、Shaanxi Normal University
- 发表时间：2024-05
- 会议 / 期刊：arXiv preprint
- 论文链接：https://arxiv.org/abs/2405.15130
- 代码链接：https://github.com/superyue72/OptLLM
- 研究方向关键词：
  - `LLM Routing`
  - `Query Assignment`
  - `Cost-Accuracy Tradeoff`
  - `Multi-objective Optimization`
  - `Performance Prediction`

## 2. 一句话总结
> 用一句话说明：这篇论文解决了什么问题、用了什么方法、取得了什么结果。

- 总结：OptLLM 将“把每个 query 分配给哪个 LLM”建模为一个同时最小化成本、最大化准确率的多目标优化问题，先用带不确定性估计的 multi-label predictor 预测各候选模型在每个 query 上的成功概率，再用 destruction-reconstruction 式启发式搜索生成 Pareto 最优解集，实验表明它在多个 NLP 与 log parsing 任务上可在保持最佳模型精度的同时节省 2.40%–49.18% 成本，且优于多种经典多目标优化算法。

## 3. 研究问题
> 这一部分回答“为什么要做这件事”。

### 3.1 核心问题是什么？
- 当有多种 API LLM 可用时，不同模型的价格、能力和任务偏好都不同。
- 用户面临的问题不是“哪个模型平均最好”，而是“对每个具体 query，应该分配给哪个模型才能最好地平衡成本与准确率”。
- 论文关注的是离线 / 批量场景下，给定一组 queries 与一组候选 LLM，如何找到一批 Pareto-optimal assignment solutions。

### 3.2 为什么这个问题在大模型路由场景中重要？
- 这是非常典型的 query-level LLM routing 问题，而且比很多二分类 router 更一般：
  - 支持多个候选模型；
  - 明确优化 cost-performance Pareto frontier；
  - 输出不是单一策略，而是一组可选最优解。
- 对实际部署很重要，因为不同企业 / 产品在不同时间点会有不同预算约束，并不希望只得到一个固定解。

### 3.3 该问题主要对应哪些目标？
> 可多选：质量、成本、延迟、可扩展性、鲁棒性、可解释性、在线适应性、部署效率等。

- 目标类型：质量、成本、可扩展性、部署效率
- 我的理解：论文明确将 cost 与 accuracy 作为两大主要目标，延迟不是重点。

## 4. 方法概览
> 这一部分回答“它是怎么做的”。

### 4.1 论文提出的方法是什么？
- OptLLM 是一个由 prediction + optimization 两部分组成的框架：
  1. Prediction：预测每个 query 在每个候选 LLM 上的成功概率 / 预期准确率；
  2. Optimization：根据预测结果与成本表，搜索非支配解集（non-dominated solutions）。
- 核心思想是：先把 query-LLM 匹配关系变成一个“预测的 accuracy table”，再在该表上做多目标优化。

### 4.2 Router 的输入是什么？
> 例如：query、历史对话、用户画像、候选模型特征、预算、延迟约束、环境状态等。

- 输入：
  - query 文本内容
  - 候选 LLM 集合
  - 每个候选 LLM 的成本表
  - 由 predictor 产生的每个 query-LLM 对应的 predicted accuracy
  - 在优化阶段还用到 grid parameter、当前解等搜索状态

### 4.3 Router 的输出是什么？
> 例如：选择哪个模型、是否 fallback、是否 cascade、是否继续推理、分配多少预算等。

- 输出：
  - 对每个 query 分配哪一个 LLM
  - 更准确地说，输出是一组 Pareto non-dominated solutions
  - 用户可从中选择“最高精度”“最低成本”或中间 trade-off 解

### 4.4 Routing 决策是如何产生的？
> 例如：规则、分类器、打分器、排序器、policy、bandit、gating network 等。

- 决策机制：
  - 第一步，多标签分类器预测每个 query 在各 LLM 上成功的概率；
  - 第二步，通过 robust-aware aggregation 把 bootstrap mean prediction 与标准差组合为更稳健的 predicted accuracy；
  - 第三步，在 predicted accuracy table 上使用 destruction + reconstruction 启发式搜索生成非支配解。
- 优化从两个极端解开始：
  - 最高 predicted accuracy 解
  - 最低 cost 解
- 然后迭代破坏当前解中部分分配，再基于启发式规则重建新解。

### 4.5 是否需要训练 Router？
- 是否训练：`是`
- 如果需要，训练数据是什么：
  - 从一小部分 query 上，分别调用各候选 LLM，记录输出及是否正确；
  - query 文本作为特征输入，LLM response correctness 作为多标签监督信号。
- 训练目标是什么：
  - 预测每个 query 对应每个候选 LLM 的成功概率 / 正确率
  - 文中使用 bootstrap ensemble 的 Random Forest multi-label classifier

### 4.6 涉及哪些学习机制？
> 可多选：强化学习、监督学习、蒸馏、bandit、ranking、classification、gating、heuristic 等。

- 学习机制：监督学习、multi-label classification、uncertainty estimation、heuristic search
- 我的理解：真正“学”的部分是 predictor；真正“路由”的部分则更像 combinatorial optimization。

## 5. 系统架构
> 这一部分回答“它在系统里怎么接入”。

### 5.1 整体 Pipeline 是怎样的？
- Pipeline：
  1. 从小规模已标注 query-LLM 响应数据构造训练集；
  2. 用预训练词向量抽取 query 特征；
  3. 训练多个 bootstrap Random Forest predictor；
  4. 聚合得到 weighted mean prediction 和 uncertainty；
  5. 形成 robust-aware predicted accuracy table；
  6. 基于成本表做 destruction-reconstruction 搜索；
  7. 输出一组 Pareto-optimal assignment solutions。

### 5.2 包含哪些模型 / 模块？
- Word embedding feature extractor（具体预训练词向量模型文中未在截取部分展开）
- 多个 bootstrap Random Forest 分类器
- Robust-aware aggregation 模块
- 初始化模块（最高精度解、最低成本解）
- Heuristic optimization 模块（destruction + reconstruction）
- 仓库侧已确认的实现目录也和论文结构一致：
  - `prediction/`：bootstrap prediction、feature extraction、prediction model
  - `baselines/`：NSGA-II、R-NSGA-II、SMS-EMOA、MOEA/D、MOEA/D-GEN、MOPSO
  - `datasets/`：公开仓库中可见数据相关文件，但不是完整原始多模型调用结果全集

### 5.3 路由发生在哪个阶段？
> 例如：请求进入前、生成前、生成中、agent planning 阶段、tool 调用前后等。

- 路由阶段：请求进入后、模型调用前
- 更准确地说，这是生成前的 query-level routing。

### 5.4 是否支持以下能力？
- 动态 fallback：`否`
- cascade：`否`
- multi-step decision：`部分是（优化阶段多步迭代，但线上单 query 选择是一步完成）`
- online update：`否`

### 5.5 我对系统架构的理解
- OptLLM 不是在线实时 adaptive system，而更像“批量 query assignment optimizer”。
- 它很适合：
  - 批量任务调度；
  - 离线评估不同预算下的最佳模型组合；
  - 给运维 / 产品经理一个完整的 Pareto 备选集。
- 如果做成在线系统，还需要一个简化版本，把当前 query 直接映射到单个模型，而不是每次都做完整多目标搜索。

## 6. 实验设置
> 这一部分记录实验是否可信、是否和你的场景相关。

### 6.1 使用了哪些数据集？
- 5 个 benchmark：
  - LogPai：log parsing
  - AGNEWS：text classification
  - COQA：question answering
  - HEADLINES：sentiment analysis
  - SCIQ：reasoning
- 数据划分（表 I）：
  - 训练集与验证集各取 1%
  - 测试集占 98%
- 表 I 中给出的规模：
  - LogPai：train 320 / val 320 / test 31360
  - AGNEWS：76 / 76 / 7448
  - COQA：80 / 80 / 7822
  - HEADLINES：100 / 100 / 9800
  - SCIQ：117 / 117 / 11443

### 6.2 对比了哪些 Baseline？
- Individual LLM baseline：把所有 query 都发给同一个 LLM
- 经典多目标优化算法：
  - NSGA-II
  - MOPSO
  - MOEA/D
  - R-NSGA-II
  - SMS-EMOA
  - MOEA/D-GEN
- 论文强调：这些 baseline 与 OptLLM 共用同一个 prediction component，以保证对比公平。

### 6.3 评估了哪些任务类型？
> 例如：chat、QA、math、code、tool-use、agent tasks、benchmark routing tasks 等。

- Text classification
- Question answering
- Sentiment analysis
- Reasoning
- Log parsing（软件工程领域任务）

### 6.4 使用了哪些大模型或专家模型？
- NLP tasks 上共使用 12 个候选 LLM，来自 4 个 provider：
  - OpenAI：GPT-Curie、ChatGPT、GPT-3、GPT-4
  - AI21：Jurassic-1 Large、Grande、Jumbo
  - Cohere：Xlarge、Medium
  - Textsynth：GPT-J、FAIRSEQ、GPT-Neox
- Log parsing 上使用 8 个 LLM：
  - TogetherAI：Mixtral-8x7B、Llama-2-7B、Llama-2-13B、Llama-2-70B、Yi-34B、Yi-6B
  - AI21：Jurassic-2 Mid、Jurassic-2 Ultra

### 6.5 主要评估指标是什么？
> 例如：accuracy、win rate、cost、latency、token usage、throughput、success rate 等。

- 对单个 solution：
  - fcost：总 API 成本
  - facc：正确处理 query 的比例
- 对 solution set：
  - IGD
  - ∆（diversity / spread）
  - 执行时间（minutes）
- 论文还说明 true Pareto front 是通过 exhaustive enumeration 生成，作为 IGD / ∆ 的参考前沿；各算法统一跑 `200` iterations，并重复 `10` 次取平均

## 7. 核心结果
> 这一部分只记录最关键结果，不要机械抄整张表。

### 7.1 最重要的实验结果是什么？
- 与最佳单一 LLM 相比，OptLLM 在保持同等 accuracy 时，可节省 2.40%–49.18% 成本。
- Table II 的代表性结果：
  - AGNEWS：在 GPT-4 的 0.90 accuracy 下，成本从 126.58 降到 75.77，节省 40.14%
  - COQA：从 216.01 降到 152.63，节省 29.34%
  - HEADLINES：从 65.28 降到 40.91，节省 37.33%
  - SCIQ：从 144.86 降到 141.39，节省 2.40%
  - LogPai：从 3.68 降到 1.87，节省 49.18%
- 与其他多目标优化算法相比，论文摘要给出的整体结论是：
  - 在相同成本下，accuracy 提升 2.94%–69.05%
  - 或在相同最高可达 accuracy 下，节省 8.79%–95.87% 成本

### 7.2 相比 Baseline 提升了什么？
- 在最高 accuracy solution 上，OptLLM 始终优于所有对比优化算法。
- Table III 中代表性提升：
  - AGNEWS：0.90，相比最强 baseline 0.82 仍有 9.76% 提升
  - COQA：0.27，相比 0.23 提升 17.39%
  - HEADLINES：0.86，相比 0.82 提升 4.88%
  - SCIQ：0.70，相比 0.68 提升 2.94%
  - LogPai：0.71，相比 0.48 提升 47.92%，相比 NSGA-II 的 0.42 提升 69.05%
- 文中还给出：OptLLM 的 IGD 更小、∆ 更优，而且运行时间优势非常明显。Table V 的代表性数字：
  - AGNEWS：OptLLM `6.15 min`，而 NSGA-II / MOPSO / MOEA-D 分别为 `30.16 / 33.85 / 33.91 min`
  - COQA：OptLLM `7.64 min`，对比基线大多在 `35–40 min`
  - LogPai：OptLLM `18.14 min`，而 NSGA-II / MOPSO / MOEA-D / SMS-EMOA 在 `124–130 min`
  - 因此“约快 5 倍”只是粗略概括；在部分数据集上其实接近一个数量级

### 7.3 是否在质量、成本、延迟之间取得了更好的 trade-off？
- 是，在 cost-accuracy 上非常明确。
- 延迟不是论文重点，但 optimization execution time 方面，OptLLM 比其他多目标算法更快。
- 它适合“离线求 Pareto frontier”，并不是为了极低在线时延设计。

### 7.4 有哪些 Ablation Study 或 Sensitivity Analysis？
- RQ2 ablation：
  - 去掉 optimization component（OptLLM w/o o）
  - 去掉 robust-aware prediction（OptLLM w/o r）
- 图 5 在 AGNEWS 上表明：
  - 不带优化组件时，最高 accuracy 仅 69.54%
  - 不带 robust-aware prediction 时，83.67%
  - 完整 OptLLM 可达 88.74%
- 另有超参数研究（RQ3），包括 bootstrap sample number、GN、α 等，具体细节需要通读后半节与项目页补充。
- 附录表格把 RQ3 也量化得比较完整：
  - 默认超参数为 `μ=100`、`GN=50`、`α=0.5`
  - Table VII 显示 GN 从 `10 → 50 → 100 → 200` 时，解集数量显著增加，但时间也显著上升；例如 LogPai 运行时间 `7.78 → 18.14 → 37.87 → 63.60 min`
  - Table VIII 显示训练数据从 `1% → 5% → 10% → 20%` 时，IGD 一般略降、∆ 一般上升，因此作者选 `1%` 是在性能与标注成本间折中，而不是说 1% 在所有指标上都最优
  - Table IX 显示 robust parameter `α` 会明显影响 prediction accuracy，不同数据集最优趋势并不完全一致，因此 `α=0.5` 更像经验折中值

## 8. 贡献与创新点
> 这一部分用于提炼“这篇论文为什么值得记”。

### 8.1 主要贡献是什么？
- 将 query assignment to LLMs 形式化为多目标优化问题。
- 提出 prediction + optimization 的统一框架。
- 在 prediction 中引入 uncertainty-aware / robust-aware aggregation。
- 通过 destruction-reconstruction 搜索高效生成 Pareto 非支配解集。

### 8.2 相比已有方法的新意在哪里？
- 不像 FrugalGPT / FORC 那类更偏 sequential cascading 或 pairwise selection，OptLLM 明确输出整条 Pareto front。
- 相比泛化的 evolutionary algorithm，它利用了 query-LLM 预测表结构，通过问题特定启发式搜索提升效率。
- 训练数据只用 1%，也强调了 label collection cost 较低。

### 8.3 创新类型属于哪一类？
> 可多选：新的 routing 策略、新的训练目标、新的数据构造方式、新的系统架构、新的 benchmark 等。

- 创新类型：新的 routing 策略、新的优化框架、带不确定性的性能预测
- 我的判断：核心创新在“把多模型路由做成可控 Pareto 优化问题”，而不是新的 benchmark。

## 9. 局限性
> 这一部分非常重要，用来防止“只看到优点”。

### 9.1 方法有哪些假设？
- 假设少量已标注 query-LLM 交互数据足以训练出可靠 predictor。
- 假设预测准确率表足够好，以至于后续优化建立在可信 proxy 上。
- 假设 query 之间可被独立分配，不考虑会话依赖或状态依赖。

### 9.2 是否依赖特定模型、数据集或人工标注？
- 依赖离线收集的 query-LLM response correctness 数据。
- 依赖已有 benchmark，任务范围虽然多样，但仍偏标准数据集。
- 不依赖人工偏好标签，但需要 ground truth 对回答做 correctness 评估。

### 9.3 是否存在泛化性、稳定性、成本、延迟、可解释性或部署方面的问题？
- 泛化性：若线上 query 分布漂移，预测器可能失效。
- 稳定性：多标签预测误差会直接传播到优化阶段。
- 延迟：在线逐 query 调优化不一定合适，更适合离线批量方案。
- 部署：当候选模型集合频繁变化时，需要重新采样数据并训练 predictor。

### 9.4 作者自己提到的 Limitation 是什么？
- 从 related work 与方法描述可看出，作者主要是在强调现有方法训练数据需求大、优化算法效率低；
- 对自身局限在结论中未展开很多，更多是隐含在框架设定中：仍依赖预测质量与静态成本表。

### 9.5 我认为还有哪些潜在问题？
- 成本与准确率之外，没有显式建模 latency、rate limit、availability 等生产约束。
- 使用 Random Forest + 静态 embedding 特征，面对复杂长上下文 query 时可能不足。
- 输出一组 Pareto 解很好，但实际线上通常仍需要一个单点决策策略。

## 10. 对我的启发
> 这一部分是把“读论文”变成“服务我自己的研究/工作”。

### 10.1 这篇论文对我理解大模型路由有什么帮助？
- 它很好地说明了“router 不一定只输出一个模型”，也可以输出一条 Pareto front 供系统上层决策。
- 对 query routing 的一个重要启发是：要分离“性能预测”与“全局调度优化”。
- 这对做预算敏感型系统特别有价值。

### 10.2 有哪些方法可以借鉴？
- 先学一个 query→per-model success probability predictor。
- 再用优化器把局部预测转化为全局 assignment policy。
- 在 predictor 里显式引入 uncertainty，而不是只用点估计。

### 10.3 有哪些想法可以扩展？
- 扩展到 online routing：把 destruction-reconstruction 简化成 query-level greedy / bandit policy。
- 把 latency、context length、地区可用性等因素加入多目标优化。
- 把 OptLLM 与 test-time compute routing 结合，形成“选模型 + 选思考预算”的联合 Pareto 优化。

### 10.4 是否能用于以下场景？
- 企业内部 Copilot：适合，尤其适合离线评估不同预算档位
- LLM 系统路由：非常适合
- 多模型选择：直接适用
- 成本优化：非常适合
- Agent 系统：部分适合，但还需纳入 tool-use / multi-step 状态信息

## 11. 可复现性记录
> 这一部分帮助你判断：这篇论文是“能落地”还是“只能参考思想”。

### 11.1 是否开源代码？
- `是`
- 链接：https://github.com/superyue72/OptLLM
- 已确认仓库包含 `baselines/`、`prediction/`、`parameter_setting/`、`datasets/` 等核心目录，足以支撑代码层复现

### 11.2 是否开源数据？
- `部分公开`
- 已确认入口：
  - GitHub：https://github.com/superyue72/OptLLM
  - 公开 benchmark 依赖：LogPai benchmark、Chen et al. / FrugalGPT 原始多模型调用数据（论文与 README 均有说明）
- 判断依据：
  - 官方仓库可见 `datasets/` 目录与数据相关工件
  - 但 README 明确说明 NLP 原始数据来自 Chen et al.、Log parsing 数据来自 LogPai
  - 未验证到作者将完整的原始 query-LLM 调用结果全集、成本表与所有复现实验缓存统一发布在单一公开入口，因此记为“部分公开”更稳妥

### 11.3 关键实现细节是否清楚？
- 主体较清楚：
  - bootstrap 数量 μ=100
  - GN=50
  - α=0.5
  - train/val/test 划分
  - 迭代终止条件 200 次
  - exhaustive enumeration 生成 true Pareto front
  - 训练/验证/测试划分是 `1% / 1% / 98%`
- README / 仓库还能补上几项落地细节：
  - `prediction/feature_extract.py` 与 `prediction_model.py` 对应论文 prediction component
  - `parameter_setting/` 保存了 baseline 调参记录
  - `baselines/` 中明确给出 NSGA-II、R-NSGA-II、SMS-EMOA、MOEA/D、MOEA/D-GEN、MOPSO 实现
- 仍不够透明的地方主要有两个：
  - 论文正文没有把 feature extractor 的具体词向量配置写得特别展开
  - 完整原始多模型输出数据并不完全由作者仓库直接托管，导致“从零复验论文全部数字”仍需额外数据整理

### 11.4 复现难度如何？
> 可用：低 / 中 / 高

- 复现难度：中
- 原因：
  - 算法本身不复杂；
  - 但需要访问一组多模型输出数据与成本数据；
  - 若从零采集数据，会有较高 API 成本。

### 11.5 如果我要复现，第一步应该做什么？
- 先在一个小型多模型数据集上复现 prediction table 的构造，再实现 destruction-reconstruction 搜索。
- 如果没有完整 API 预算，优先从作者开源仓库里的缓存结果或公开原始数据开始。

## 12. 横向比较字段
> 这一部分专门为后续表格对比服务，尽量用简短字段填写。

- Routing 对象：query → LLM assignment
- Routing 粒度：query-level（批量优化）
- Router 类型：predictor + multi-objective heuristic optimizer
- 是否训练：是
- 训练信号：query-LLM correctness labels
- 优化目标：maximize accuracy + minimize cost
- 支持的模型数量：多模型（实验中 8–12 个候选）
- 是否考虑成本：是
- 是否考虑延迟：否（未重点建模）
- 是否 online：否
- 是否开源：是
- 主要优点：输出 Pareto front、成本收益明确、可扩展到多模型
- 主要缺点：依赖离线数据和预测器质量，在线化不足

## 13. 阅读后的评分
> 建议按 1-5 打分，便于后续快速筛选重点论文。

- 相关性：`5`
- 方法新颖性：`4`
- 实验可信度：`4`
- 工程可落地性：`4`
- 对我研究 / 工作的启发：`5`

### 总评
- 是否值得精读：`是`
- 是否值得复现：`是`
- 是否值得纳入自己的系统设计：`是`
- 一句话结论：OptLLM 是一篇很典型也很实用的多模型 query assignment 论文，特别适合作为“成本-效果 Pareto 路由”基线与系统设计参考。