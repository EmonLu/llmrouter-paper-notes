# Survey 中六种 Routing 范式整理

这份文档的目的，不是重复 survey 摘要，而是把那篇综述里最关键的六种 routing 范式，压缩成一份更适合系统设计和后续实现决策的速查表。

对应 survey：
- `papers/general-single-turn-survey-2603.04445-survey-dynamic-model-routing-and-cascading.md`
- 原始六类范式：
  1. difficulty-aware
  2. preference-aligned
  3. clustering-based
  4. reinforcement learning / bandit
  5. uncertainty-based
  6. cascading systems

我这里重点整理 6 个问题：
- 这个范式的概念到底是什么
- 它主要依赖什么输入信号
- 它通常在什么时候做决策
- 它的核心优点是什么
- 它的核心缺点是什么
- 它更适合支撑 General Router，还是 Coding Agentic Router

## 1. 先给一个总览

| 范式 | 一句话概念 | 决策时机 | 主要信号 | 最大优点 | 最大缺点 | 更适合哪个 target |
|---|---|---|---|---|---|---|
| Difficulty-aware | 先估计 query 难度，再决定是否用强模型 | pre-generation | query 本身、difficulty proxy、query-model compatibility | 延迟低、部署干净 | 看不到真实输出，容易误判伪简单 query | General Router |
| Preference-aligned | 按人类偏好/胜率来学“哪个模型更受欢迎” | 主要是 pre-generation | pairwise preference、Arena 风格偏好数据、reward model | 更贴近真实用户体验 | 偏好数据贵、分布漂移明显 | General Router |
| Clustering-based | 先把 query 空间划分成簇，再给每个区域配模型 | pre-generation | query embedding、cluster structure、cluster-level profile | 简单直观、接新模型相对友好 | cluster 太粗会吞掉细粒度差异 | General Router |
| RL / Bandit | 把 routing 当成在线策略学习问题 | online / adaptive | reward、反馈、上下文状态、历史结果 | 能随环境变化持续适应 | 训练和部署复杂，探索成本高 | General Router 向 Agentic 过渡 |
| Uncertainty-based | 先判断当前回答是否可信，再决定是否升级 | post-generation | confidence、perplexity、judge、verifier、agreement | 很适合 quality gate 和 deferral | 可靠 uncertainty 很难拿 | Coding Agentic Router / cascade bridge |
| Cascading systems | 先便宜试，再按规则逐级升级 | multi-stage | query、response、verifier、stop rule、成本约束 | 最贴近真实生产系统 | 链路长、工程复杂、额外 latency 高 | 两边都适合，偏 Agentic bridge |

## 2. 统一观察框架

为了避免只记住方法名，我建议以后看任何 routing 论文时，都先用下面四个维度定位它：

1. 决策时机是什么
   - pre-generation
   - post-generation
   - multi-stage
   - online / adaptive

2. 依赖什么信号
   - query
   - model metadata
   - response
   - feedback
   - verifier / judge

3. 决策对象是什么
   - 选模型
   - 是否升级
   - 是否 early stop
   - 是否继续算
   - 是否切 workflow / budget

4. 主要代价来自哪里
   - 数据标注
   - 训练复杂度
   - 多次模型调用
   - verifier 开销
   - 在线探索成本

下面六种范式，最好都按这个框架理解。

## 3. Difficulty-aware routing

## 3.1 概念

Difficulty-aware routing 的核心想法是：

> 先判断一个 query 难不难，再决定它值不值得交给更强、更贵的模型。

它通常不等模型先回答，而是在生成前直接做分流。
所以它最像一个典型的 query-time router。

## 3.2 核心特征

- 决策时机：`pre-generation`
- 决策粒度：`query-level`
- 常见输入：
  - query embedding
  - query complexity
  - difficulty proxy
  - query-model compatibility
- 常见输出：
  - 选哪个模型
  - 是否送往强模型
- 常见实现：
  - heuristic difficulty rule
  - query classifier
  - compatibility scorer

## 3.3 这个范式最像什么

如果用系统类比，它更像：

- 一个入口分诊器
- 一个 intake router
- 一个“先粗分流”的控制器

它最关心的是：
- 这个请求是不是足够难，值得花更贵预算

而不是：
- 这个回答看起来靠不靠谱

## 3.4 优点

- 延迟低，因为生成前就做决策
- 工程链路短，容易部署
- 很适合做第一层粗粒度分流
- 对 General Router 很自然，容易接 benchmark
- 成本收益通常很直观：简单 query 不必总走最强模型

## 3.5 缺点

- 最大问题是它看不到真实输出
- 很容易把“表面简单、实际很难”的 query 送错
- 对训练分布和模型池依赖强
- 候选模型变化时，query-only 决策边界可能失效
- 如果 difficulty proxy 不可靠，整个 router 会非常脆弱

## 3.6 最适合的场景

- 通用 benchmark / 普通 query 路由
- Open QA / instruction following / math 的离线路由
- 对 latency 很敏感的线上入口路由
- 先做低成本分诊，再交给下游更复杂模块

## 3.7 对你的两个 target 的价值

### 对 General Router
非常重要，是最自然的起点。

### 对 Coding Agentic Router
只能作为弱启发。
它可以帮助做 task initializer，但不能单独承担 runtime control。

## 3.8 一句话判断

> Difficulty-aware 是最适合起步的 query router，但它的上限也最容易被“看不到 response”这件事卡住。

## 4. Preference-aligned routing

## 4.1 概念

Preference-aligned routing 的核心想法是：

> router 学的不是“标准答案意义上的最优模型”，而是“用户更喜欢哪个模型”。

它通常把 routing 问题转成：
- pairwise preference
- human win-rate
- reward / preference score

所以它特别适合 open-ended generation，而不只是 objective benchmark。

## 4.2 核心特征

- 决策时机：通常是 `pre-generation`
- 决策粒度：`query-level`
- 常见输入：
  - query embedding
  - 人类偏好数据
  - model-vs-model 胜率数据
  - reward model / preference signal
- 常见输出：
  - 选哪个模型更可能让用户满意
- 常见实现：
  - pairwise ranker
  - preference classifier
  - win-rate predictor

## 4.3 这个范式最像什么

它更像一个：
- 用户体验导向的路由器
- “谁更讨喜”的分流器

而不是严格的：
- 学术 benchmark accuracy 优化器

## 4.4 优点

- 更贴近真实用户感知质量
- 很适合 chat / assistant / open-ended 生成
- 如果有 Arena 一类数据，能学到真实主观偏好结构
- 相比只看 task metric，更符合产品视角

## 4.5 缺点

- 偏好数据贵，而且很难持续维护
- 用户偏好会漂移，数据容易过时
- 不同任务、不同用户群的偏好差异很大
- 如果依赖固定模型对或固定 reward model，新模型接入成本会很高
- 对 coding / math 这类 objective task 不一定最合适

## 4.6 最适合的场景

- 通用对话助手
- open-ended generation
- 产品导向的 chat 体验优化
- “用户满意度”比严格正确率更重要的系统

## 4.7 对你的两个 target 的价值

### 对 General Router
很有价值，尤其是如果你以后做 chat-oriented general router。

### 对 Coding Agentic Router
价值有限。
SWE-bench 更关心 patch 成功率、测试通过率和 trajectory 成本，而不是主观偏好。

## 4.8 一句话判断

> Preference-aligned 很适合 chat 产品，但如果你的目标是严肃 benchmark 或 SWE-bench，它通常不是第一主线。

## 5. Clustering-based routing

## 5.1 概念

Clustering-based routing 的核心想法是：

> 不直接对每个 query 单独精细打分，而是先把 query 空间划成若干区域，再给每个区域配置更合适的模型策略。

这是一种“按区域分治”的思路。

## 5.2 核心特征

- 决策时机：`pre-generation`
- 决策粒度：介于 `cluster-level` 与 `query-level` 之间
- 常见输入：
  - query embedding
  - cluster assignment
  - cluster-level performance summary
  - candidate profile
- 常见输出：
  - 某个簇默认使用哪个模型
  - 某个 query 属于哪个簇，再继承对应策略
- 常见实现：
  - embedding clustering
  - prototype matching
  - cluster-level profile mapping

## 5.3 这个范式最像什么

它更像：
- 地图分区
- 区域化调度
- 粗到中等粒度的 policy compression

## 5.4 优点

- 简单直观
- 在无标签或弱标签条件下也能工作
- 便于解释：可以说“这类 query 往往由这个模型处理”
- 对新增模型往往更友好，因为可以先补 cluster-level profile
- 适合长期维护 candidate pool 的结构化画像

## 5.5 缺点

- cluster 边界往往太粗
- 同一簇内的 query 细粒度差异可能很大
- 分布漂移会让 cluster 老化
- 如果聚类空间本身不稳定，整个 router 会越来越脆

## 5.6 最适合的场景

- 想做长期可维护的多模型路由
- 想降低新模型接入成本
- 想把 query router 和 profile 层结合起来
- 想要比 query classifier 更结构化的系统

## 5.7 对你的两个 target 的价值

### 对 General Router
非常重要。
它和 profile layer 很契合，是你做长期扩展时最值得保留的思路之一。

### 对 Coding Agentic Router
中等价值。
它可以帮助 backbone profile 和 task initializer，但不够支撑 trajectory-level runtime control。

## 5.8 一句话判断

> Clustering-based 不一定是单点性能最强的，但它对“新模型接入”和“长期维护”特别有价值。

## 6. Reinforcement Learning / Bandit routing

## 6.1 概念

这一类方法的核心想法是：

> routing 不是一次性离线分类问题，而是一个可以根据反馈持续更新的策略学习问题。

这里最关键的区别是：
- 它允许在线适应
- 它允许 exploration
- 它把路由看成 sequential decision 或 adaptive control

## 6.2 核心特征

- 决策时机：`online / adaptive`
- 决策粒度：从 `query-level` 到 `multi-step` 都可能
- 常见输入：
  - 当前 state
  - 历史 reward
  - 用户反馈
  - deployment feedback
  - cost / latency / success signal
- 常见输出：
  - 选哪个模型
  - 是否继续探索
  - 是否调整策略参数
- 常见实现：
  - contextual bandit
  - PPO / RL policy
  - online reward optimization

## 6.3 这个范式最像什么

它更像：
- 会边上线边调整的控制器
- 带探索能力的调度器
- 真正意义上的 adaptive policy

## 6.4 优点

- 适合动态环境
- 适合候选模型不断变化的场景
- 适合持续有反馈流入的部署环境
- bandit 方法特别适合先做小步在线学习
- 如果反馈定义得好，长期可能比静态 router 更稳

## 6.5 缺点

- 训练和部署复杂度高
- 探索本身有成本
- online learning 需要更强的观测和回滚机制
- 多次交互/探索容易提高延迟和系统复杂度
- 很难离线完全评估真实表现

## 6.6 最适合的场景

- 有稳定在线反馈闭环
- 模型池会频繁变化
- 业务容忍逐步探索
- 已经有较成熟的 logging / monitoring / rollback 基础设施

## 6.7 对你的两个 target 的价值

### 对 General Router
现在更像中后期增强方向，不适合做 v1。

### 对 Coding Agentic Router
长期很重要，因为 agent runtime control 天然更像 sequential decision。
但第一版也不建议直接上 RL。

## 6.8 一句话判断

> RL / bandit 是长期上限高的方向，但工程和实验复杂度也最高，适合在基础控制平面稳定后再引入。

## 7. Uncertainty-based routing

## 7.1 概念

Uncertainty-based routing 的核心想法是：

> 不急着问“哪个模型最好”，先问“当前回答够不够可信”，如果不够，再升级。

这和 difficulty-aware 最大的不同在于：
- difficulty-aware 是生成前判断
- uncertainty-based 常常是生成后判断

## 7.2 核心特征

- 决策时机：`post-generation`
- 决策粒度：`response-level`
- 常见输入：
  - confidence
  - perplexity
  - token probabilities
  - verifier / judge 输出
  - agreement / disagreement
- 常见输出：
  - accept
  - defer
  - escalate
  - retry
- 常见实现：
  - uncertainty probe
  - verbalized confidence
  - perplexity threshold
  - agreement-based gate

## 7.3 这个范式最像什么

它更像：
- 质检门
- quality gate
- “先看答案靠不靠谱，再决定要不要升级”的控制器

## 7.4 优点

- 特别适合 deferral / escalation 系统
- 对 edge-cloud、SLM→LLM 分流很自然
- 可以直接利用 response-level 信号
- 对 agent runtime 很有启发，因为 agent 轨迹本身就会产生大量可观测信号

## 7.5 缺点

- 最大问题是 reliable uncertainty 很难拿
- 模型自报置信度常常不靠谱
- verifier / judge 自己也会带来成本和误差
- 如果 gate 不准，会造成不必要升级或错误放行

## 7.6 最适合的场景

- quality gate
- escalation / fallback
- post-generation deferral
- coding agent 中的 patch / test 后质量判断

## 7.7 对你的两个 target 的价值

### 对 General Router
有价值，但更适合作为第二层 gate，而不是第一层入口 router。

### 对 Coding Agentic Router
非常重要。
因为 SWE-bench 这类任务天然有大量 response-level、trajectory-level、test-level 信号。

## 7.8 一句话判断

> Uncertainty-based 不一定适合当第一层 router，但非常适合当系统里的第二道关卡。

## 8. Cascading systems

## 8.1 概念

Cascading 的核心想法是：

> 不一次性决定最终用谁，而是先让便宜模型尝试，如果信号显示不够好，再逐级升级。

它本质上不是单步路由，而是多阶段控制流程。

## 8.2 核心特征

- 决策时机：`multi-stage`
- 决策粒度：`system-level` / `stage-level`
- 常见输入：
  - query
  - response
  - verifier signal
  - stop rule
  - cost budget
- 常见输出：
  - accept 当前结果
  - 升级到更强模型
  - 继续下一个阶段
  - 终止
- 常见实现：
  - small-first cascade
  - verifier-based escalation
  - stop / defer policy
  - 多模型分层调用链

## 8.3 这个范式最像什么

它更像：
- 一条 control pipeline
- 一个分阶段升级系统
- 真实生产环境里的分层推理链

## 8.4 优点

- 非常贴近真实部署
- 能把 query-level router、quality gate、escalation policy 串起来
- 更容易体现系统组合收益
- 对复杂任务往往比单步路由更灵活

## 8.5 缺点

- 工程复杂度高
- 调用链更长
- verifier / judge 会带来额外 latency 和成本
- stop rule 不准时，既可能多花钱，也可能错误截断
- 实验归因更难：收益到底来自 router、verifier 还是 stop rule，不容易拆清楚

## 8.6 最适合的场景

- 强烈 cost-sensitive 的推理系统
- multi-stage verification 系统
- 需要 fallback / escalation 的生产链路
- 从 query routing 向 runtime control 过渡的系统

## 8.7 对你的两个 target 的价值

### 对 General Router
有价值，尤其适合作为 v2/v3 的增强层。

### 对 Coding Agentic Router
非常重要，因为 agent 本来就是 multi-stage 过程。
很多 runtime control 本质上就是更一般化的 cascade。

## 8.8 一句话判断

> Cascading 是最接近真实系统的范式，但它也最容易把研究问题从“路由”扩展成“整条控制链设计”。

## 9. 六种范式放到一起怎么比较

## 9.1 如果只追求最干净、最容易 benchmark 的 v1

优先级通常是：
1. difficulty-aware
2. preference-aligned
3. clustering-based

因为它们更容易形成 query-time policy。

## 9.2 如果只追求最贴近真实生产系统

优先级通常是：
1. cascading
2. uncertainty-based
3. difficulty-aware

因为真实系统通常不是一次性选模型，而是“入口分流 + 质量门 + 升级链”。

## 9.3 如果最关心新模型接入成本

优先级通常是：
1. clustering-based
2. profile-based 变体
3. difficulty-aware

其中 clustering/profile 路线往往更友好。

## 9.4 如果最关心在线自适应

优先级通常是：
1. RL / bandit
2. uncertainty-based
3. cascading

因为这些范式更容易接 online feedback。

## 9.5 如果最关心 Coding Agentic Router

优先级通常是：
1. cascading
2. uncertainty-based
3. RL / bandit
4. difficulty-aware

因为 agent runtime 本质上更接近：
- 多阶段
- 有反馈
- 有恢复
- 有 budget control

## 10. 对你当前两个 target 的直接建议

## 10.1 对 General Router

我建议的主线组合是：
- 第一层：difficulty-aware / query-time scorer
- 骨架增强：clustering / profile layer
- chat 产品场景可选：preference-aligned
- 后续增强：再接 uncertainty gate 或 budget action

也就是说：

> General Router 最适合从 pre-generation 范式起步，再逐步吸收 clustering/profile 和少量 post-generation signal。

## 10.2 对 SWE-bench Agent Router

我建议的主线组合是：
- 第一层：backbone routing（弱 difficulty-aware）
- 第二层：budget controller
- 第三层：uncertainty / agreement / test-feedback gate
- 第四层：cascading / recovery policy
- 最后才考虑：RL / online adaptation

也就是说：

> SWE-bench Agent Router 不是把 query router 放大一点，而是把 uncertainty、cascade、budget、recovery 这些 runtime control 元素真正纳入控制面。

## 11. 最后给一个简短结论

如果只用一句话总结 survey 里的六种范式：

- difficulty-aware：最适合做入口分流
- preference-aligned：最适合做用户体验导向的 chat 路由
- clustering-based：最适合做长期可扩展的 profile 化路由
- RL / bandit：最适合做在线自适应，但代价最高
- uncertainty-based：最适合做 post-generation quality gate
- cascading：最接近真实生产系统，但也最复杂

对你当前的研究目标来说，最关键的不是在六种范式里只选一种，而是明确：
- General Router 应该以前三类为主
- Coding Agentic Router 应该以后两类加 runtime control 为主
- RL / bandit 更像中后期增强层，而不是第一版骨架
