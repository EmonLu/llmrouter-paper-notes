# MMR-Bench: A Comprehensive Benchmark for Multimodal LLM Routing

## 1. 论文基本信息
- 标题：MMR-Bench: A Comprehensive Benchmark for Multimodal LLM Routing
- 作者 / 机构：Haoxuan Ma, Guannan Lai, Han-Jia Ye / 南京大学人工智能学院；南京大学软件新技术全国重点实验室
- 发表时间：2026-01-25（arXiv v1）
- 会议 / 期刊 / arXiv：arXiv:2601.17814 [cs.AI]
- 论文链接：https://arxiv.org/abs/2601.17814
- HTML 入口：https://arxiv.org/html/2601.17814v1
- 代码链接：https://github.com/Hunter-Wrynn/MMR-Bench
- 本地 PDF：`pdfs/multimodal-single-turn-benchmark-2601.17814-mmr-bench.pdf`
- 抽取来源：arXiv HTML 页面 + appendix HTML
- 研究方向关键词：
  - `Multimodal Routing`
  - `MLLM Benchmark`
  - `Cost-aware Routing`
  - `Vision-Language Routing`
  - `Offline Evaluation`
  - `Cross-modal Feature Fusion`

## 2. 一句话总结
- 总结：这篇论文的核心贡献不是提出一个特别强的新 router，而是第一次把“多模态模型路由”单独做成了一个预算感知、离线可复现、候选模型池固定的 benchmark：它把 OCR、通用 VQA、视觉数学三类任务统一到同一个 MLLM routing 环境中，证明 multimodal signal 确实比 text-only routing 更强，并且在固定候选池下，路由系统能以大约最强单模型 33% 的成本达到甚至超过其准确率。

## 3. 这篇论文到底在解决什么问题？

### 3.1 核心问题是什么？
- 传统 LLM routing 大多默认输入是纯文本。
- 但在 MLLM / VLM 场景里，输入往往同时包含文本与图像，不同模型在 OCR、图像理解、视觉数学上的强弱差异也更大。
- 因此这篇论文要回答的是：
  - 如何定义一个标准化的 multimodal routing 问题？
  - 如何在固定候选模型池与统一成本模型下，比较不同 multimodal router 的 cost-accuracy frontier？

### 3.2 为什么这个问题重要？
- 多模态部署里“一个模型包打天下”的浪费会比纯文本更严重：
  - 简单 OCR 请求不需要最强大模型
  - 视觉数学和图表推理又很容易把弱模型打爆
- 纯文本 router 直接迁移到多模态场景会丢掉 image-side signal，因此常常只能做粗糙路由。
- 对你的 router 研究来说，这篇论文很重要，因为它把“modality-aware signal 是否真的能改善 routing”从直觉变成了可测试命题。

### 3.3 它主要在优化什么目标？
- 目标类型：准确率、成本、预算鲁棒性、跨数据集泛化
- 我的理解：MMR-Bench 的核心价值是 benchmark / evaluation substrate，而不是某个特定 router family 本身

### 3.4 它的控制对象到底是什么？
- 控制对象：单个 multimodal query 应该路由到候选 MLLM 池中的哪个模型
- 控制粒度：query-level
- 我对其定位的判断：这是 multimodal query router benchmark，不是 agent runtime router

### 3.5 它更像哪一类工作？
- `multimodal benchmark / evaluator`
- `query-level cost-aware router`
- `feature-fusion-aware routing`
- 我的判断：它最像多模态版的 RouterBench / offline routing benchmark，但更强调 modality gap 与跨模态特征融合

## 4. 方法概览

### 4.1 提出的方法是什么？
- 论文提出 MMR-Bench，一个针对 MLLM routing 的统一 benchmark。
- benchmark 提供：
  1. multimodal query
  2. 每个候选模型在该 query 上的 raw output
  3. task-specific utility score
  4. 在统一价格体系下归一化后的 inference cost
- router 不需要重新调用任何 MLLM，只需在离线环境里基于特征做选择，然后索引固定的 `{utility, cost}` outcome table 即可评测。

### 4.1.1 核心直觉是什么？
- 多模态 routing 的关键不只是“不同模型有不同强项”，而是：
  - 文本信号与图像信号对 routing 的贡献并不恒定
  - 某些任务文本就足够，某些任务图像才是决定性信号，另一些任务必须看跨模态一致性/冲突
- 因此，真正有效的 router 需要显式利用 multimodal cues，而不是只做 text-only difficulty prediction。

### 4.1.2 算法按步骤是怎么运行的？
- Step 1：收集多模态 benchmark 数据，覆盖 OCR、通用 VQA、视觉数学三大场景。
- Step 2：对每个样本和每个候选 MLLM，预先记录输出、utility、cost，形成离线 outcome table。
- Step 3：为每个 query 提取 text embedding 与 image embedding。
- Step 4：将两种模态特征做 fusion，构成 router 输入表示。
- Step 5：router 预测每个候选模型的 utility 与 cost，或者直接通过近邻/聚类方式估计。
- Step 6：给定 trade-off weight `lambda`，按 `utility - lambda * cost` 或等价目标选择模型。
- Step 7：在离线表中查询该模型对应的真实 utility / cost，绘制 performance-cost curve 并计算指标。

### 4.1.3 如果把它压缩成一个伪代码 / 决策流，它长什么样？
- `multimodal query -> extract text/image embeddings -> fuse features -> predict per-model utility/cost -> argmax_j (u_hat - lambda * c_hat) -> lookup true outcome in offline table -> aggregate frontier metrics`

### 4.2 Router 的输入是什么？
- 输入是 multimodal query（本文聚焦 text + image 两模态）
- 形式化为：
  - 文本输入 `x_txt`
  - 图像输入 `x_img`
  - 模态可用性向量 `m_i in {(1,0),(1,1)}`
- 除此之外，router 还可以接收预算偏好 / trade-off parameter `lambda`

### 4.3 Router 的输出是什么？
- 输出是候选模型池中的模型索引 `j*`
- 不是 tier，而是直接选具体候选 MLLM
- 论文中选择依据是总体分数 `S_{i,j} = u_{i,j} - lambda * c_{i,j}`

### 4.4 Routing 决策如何产生？
- 论文实现了多类 router：
  - KMeansRouter
  - KNNRouter
  - LinearRouter
  - MLPRouter
  - LinearMFRouter
  - MLPMFRouter
  - CrossModalRouter (CMR)
  - RandomRouter
  - OracleRouter
- 本质上分为三类：
  - 非参数近邻/聚类
  - 回归型 router
  - low-rank / matrix-factorization 风格 router

### 4.5 是否需要训练 Router？
- 对 benchmark 本身：`否`
- 对 learned routers：`是`
- 训练目标：预测每个候选模型在当前 query 上的 utility 与 cost

### 4.6 涉及哪些学习机制？
- frozen multimodal embedding
- multimodal feature fusion
- multi-output regression
- low-rank factorization
- 非参数近邻检索 / 聚类估计

### 4.7 这套算法最依赖什么关键信号？
- text embedding
- image embedding
- 模态权重是否应自适应调整
- 跨模态一致性 / 差异性信号
- 候选模型在训练集上的 outcome pattern

### 4.8 这套算法最容易失败在哪一步？
- 若 fusion 太粗糙，image/text 重要性失衡会直接误导 routing。
- 若候选模型池变化很大，基于固定 outcome table 训练出的 router 可能不再稳定。
- 若 benchmark 外的任务分布变化很大，offline router 可能高估实际泛化能力。

## 5. 系统架构

### 5.1 整体 Pipeline
- 多模态 benchmark 构建
- 10-model candidate zoo 跑全量样本
- 形成 offline outcome table
- 提取 text/image frozen embeddings
- 做 multimodal fusion
- 用不同 router family 训练与评测
- 汇总 performance-cost frontier

### 5.2 包含哪些模型 / 模块？

#### 5.2.1 Router 本身用的是什么模型？
- Router 类型不是单一模型，而是一组 router families：
  - KNN / KMeans：非参数
  - Linear / MLP：回归器
  - LinearMF / MLPMF：低秩 / MF 风格 router
  - CMR：cross-modal attention 风格
- 这些 router 不是大语言模型，而是轻量学习器 + frozen embedding pipeline
- 我的理解：这篇论文更关注 benchmark 与 fusion signal，而不是训练一个很大的 router model

#### 5.2.2 候选大模型池由哪些模型组成？
- 候选池共 `K=10` 个模型：
  - 开源/开放权重：InternVL3-78B、Qwen2.5-VL-3B、Qwen2.5-VL-7B、Qwen2.5-VL-72B、Gemma3-4B
  - 商业模型：GPT-5-0807、GPT-5-Nano-0807、Claude 3.7 Sonnet、Gemini 2.5 Pro、Gemini 2.5 Flash
- 参数/等级和统一输出 token 价格表在 appendix C 中给出

#### 5.2.3 这些模型之间的能力差异是怎么被利用的？
- 小模型负责超低成本 OCR / 简单理解
- 中档商业模型和中大开源模型负责 cost-accuracy 中间段
- 最强模型负责复杂视觉数学和 hardest cases
- router 的目标就是在这些 heterogeneous candidates 中，找到每个 query 的 best trade-off 点

### 5.3 路由发生在哪个阶段？
- 路由发生在 query-level inference 前
- 不是 token-level，不是 step-level，也不是 agent trajectory-level

### 5.4 是否支持 fallback / cascade / online update？
- benchmark 主要是 offline one-shot routing，不强调 online fallback
- 没有像 FrugalGPT / TwinRouterBench 那样强调 execution-time cascading

### 5.5 我的理解
- 这篇论文对你最有价值的地方不是“多模态也能路由”这件事本身，而是它把 modality-aware feature 作为 router 输入的一级公民。
- 这会提醒你：未来如果 coding-agent router 也接图像 / screenshot / UI / diagram，text-only state encoder 很可能不够。

### 5.6 如果新增一个候选大模型，router 需要付出什么代价？
- benchmark 是离线 outcome table 驱动的，因此新增模型的成本不低：
  - 需要把新模型在全 benchmark 上跑一遍
  - 需要记录新的 utility / cost
  - learned router 可能需要重新训练
- 我判断的接入成本：`高`
- 原因：该 benchmark 的 evaluator 和训练样本都绑定固定 candidate pool

## 6. 实验设置

### 6.1 使用了哪些数据集？
- 三大场景、七个主要数据集：
  - OCR / 文档理解：OCRBench, SEED-Bench-2-Plus
  - 通用 VQA：MMStar, RealWorldQA
  - 视觉数学：MathVista, MathVerse, MathVision
- Appendix B 给出的测试集规模：
  - OCRBench：1000
  - SEED-Bench-2-Plus：2277
  - MMStar：1500
  - RealWorldQA：765
  - MathVista：1000
  - MathVerse：788
  - MathVision：3040

### 6.1.1 数据集是怎么来的？
- 不是作者自己新造 query，而是从现有多模态 benchmark 中选取典型数据集并统一预处理。
- 用 VLMEvalKit 做处理与评测，尽可能保证输入格式标准化。

### 6.1.2 数据集里具体包含什么？
- multimodal query
- 每个候选模型的输出
- 每个模型对应的 utility score
- 统一价格模型下的 normalized cost
- frozen split 与 deterministic scorer

### 6.1.3 这些数据集和真实多模态场景有多接近？
- 相对接近通用 multimodal deployment：
  - OCR
  - 图片问答
  - 图表/数学推理
- 但仍然主要是 query-level benchmark，不含真实 agent tool-use / environment interaction

### 6.2 对比了哪些 Baseline？
- RandomRouter
- OracleRouter
- KNNRouter
- KMeansRouter
- LinearRouter / MLPRouter
- LinearMFRouter / MLPMFRouter
- CMR
- 还和 best single model 做对照

### 6.3 主要评估指标是什么？
- nAUC：performance-cost curve 的 normalized AUC
- Peak Score (`P_s`)：曲线上可达到的最高 performance
- QNC：达到 best single model 同等质量所需的相对成本

## 7. 核心结果

### 7.1 最重要的实验结果是什么？
- multimodal signal 相比 text-only routing 有明显收益。
- 经验上，multimodal cues 能改善 cost-accuracy frontier。
- 论文摘要的最醒目结论是：routed system 可以用大约最强单模型 `33%` 的成本达到甚至超过其准确率。

### 7.2 相比 baseline 提升了什么？
- 相比 best single model：router 在不少数据集上能用更低成本达到相同或更高 peak score。
- 相比 naive unimodal fusion / text-only routing：multimodal routing 更稳定，也更接近 oracle frontier。
- 相比简单非参数方法：MF 系列 router 在 full-dataset average 上更稳。

### 7.3 哪类 router 最强？
- 从表 2 的 full-dataset average 看：
  - `LinearMFRouter` 的 nAUC / Peak Score 最强（约 0.7042 / 0.7533）
  - `MLPMFRouter` 紧随其后（约 0.6913 / 0.7494）
- 但 KNN / KMeans 在局部数据集上仍有尖峰优势
- 论文因此强调：low-rank / MF 风格 router 更稳，instance-based 方法更容易在局部数据分布上取胜但整体鲁棒性弱

### 7.4 Adaptive fusion 带来了什么？
- Section 6 显示 adaptive fusion 相比 equal-weight averaging 整体更好，尤其对 KMeans 提升很大。
- 这被作者解释为“modality gap”的直接证据：
  - 文本与图像的价值不恒定
  - 强行 1:1 平均会误校准 router

### 7.5 泛化表现怎么样？
- 作者报告两类泛化：
  - 同场景跨数据集泛化
  - 从 multimodal task 向 text-only benchmark 的 zero-shot 迁移
- 这点很重要，因为它在尝试证明 router 不是只记住某个数据集，而是学到了一些 transferable modality-aware difficulty signal

## 8. 我怎么看这篇论文

### 8.1 它真正的创新点是什么？
- 不是某个复杂 router，而是：
  - 首个较系统的 multimodal routing benchmark
  - 统一 outcome table + unified cost model + fixed candidate zoo
  - 显式讨论 modality gap 与 adaptive fusion

### 8.2 它的局限是什么？
- 仍然是 offline benchmark，缺少 online deployment / real latency / failure recovery 维度
- 候选模型池固定，新增模型代价高
- 主要看 query-level routing，没有 agent-level multimodal execution state

### 8.3 它对你当前项目最有帮助的点是什么？
- 你现在主要做 coding / agentic router，但这篇论文提供一个很重要的前瞻提醒：
  - 若未来 router 输入不再只是文本，而包含 screenshot、UI、图表、日志截图、网页截图，router state 设计必须显式支持 multimodal signal
- 也就是：它不是你当前主线的中心论文，但它补上了“未来前缀状态可能是多模态”的设计空间

## 9. 对你的系统设计的直接启发

### 9.1 为什么你说它是“multimodal 作为分类前缀”很合理？
- 因为这篇论文的核心不是 general text routing，也不是 coding agent runtime control，而是明确的 multimodal routing benchmark。
- 它最自然的归类就是一个独立前缀：`multimodal`
- 这样做的好处是，后续你再加入视觉 routing、screenshot-aware coding agent、GUI agent routing 时，这一类材料可以自然聚到一起，而不会混进 foundation / agentic 里被淹没。

### 9.2 它最值得你复用的三个点
- `modality-aware state representation`
- `adaptive fusion rather than equal-weight fusion`
- `offline outcome-table benchmark for fixed candidate pools`

### 9.3 哪些不该直接照搬？
- 不该把 query-level multimodal routing 直接等同于 coding-agent multimodal routing
- 不该假设新增模型成本低
- 不该忽略真实在线 latency、tool-use 和 protocol 细节

## 10. 开源性与可复现性
- 代码是否开源：是，论文给出 GitHub 仓库 `https://github.com/Hunter-Wrynn/MMR-Bench`
- 数据 / benchmark 是否公开：依赖公开 benchmark + 作者构建的 benchmark 产物，代码仓库应承担主要复现入口
- 本地 PDF：当前未加入本地仓库
- 我的判断：相对可复现，但要完整复现实验仍需重跑全部 candidate zoo，成本不低

## 11. 我的最终结论
- 如果从你的当前主线看，这篇论文不是“马上决定 coding-agent router 怎么做”的核心文献；但如果从长期系统边界看，它非常值得单独放进 `multimodal` 类别，因为它把一个关键问题提前说清楚了：router 的输入前缀不一定永远是纯文本，模态信息本身也可能决定最优模型选择。
- 最短结论就是：这篇论文对你最有价值的不是某个具体 router，而是把“多模态前缀状态”正式纳入 router 设计空间。以后你做 screenshot / GUI / diagram-aware agent router 时，这篇会变成很自然的起点。
