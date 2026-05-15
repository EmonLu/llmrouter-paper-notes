# General Router Spec

> 目标：实现一个面向普通 benchmark / 普通 query 数据集的通用多模型 router，在质量、成本、延迟之间形成稳定、可比较、可扩展的 trade-off。

## 1. 设计目标

这个系统不是 agent runtime controller，也不是 workflow orchestrator。

它解决的是一个更收敛的问题：

- 输入：一个 query
- 输出：
  - v1：`model_id`
  - v2：`(model_id, budget_level)`
- 目标：
  - 在固定模型池上显著优于单模型 baseline
  - 在新增模型时保持较低接入成本
  - 在 benchmark 上形成清晰的 cost-quality-latency frontier

一句话定义：

> General Router 是一个 benchmark-ready 的 query-time control policy，用于在候选模型池中为每个请求选择最合适的模型，后续可扩展到预算联合选择。

## 2. 非目标

第一版明确不做：
- 多 agent workflow 规划
- trajectory-level runtime routing
- rollout branching / self-debug controller
- repo state / tool state / test feedback 驱动的在线策略
- 复杂的端到端 RL

这些属于 coding agentic router 的范围，不属于这个 spec。

## 3. 设计原则

### 原则 1：先做 model selection，再做 model+budget
第一版动作空间必须小，否则 benchmark 不可解释。

### 原则 2：profile layer 是一等公民
router 不能只依赖 query classifier。必须显式建模 candidate model profile。

### 原则 3：evaluation 以 frontier 为中心
不能只报 accuracy。必须同时报质量、成本、延迟，并与 zero router / oracle / simple heuristic 比较。

### 原则 4：新增模型接入成本必须可度量
每种方案都必须回答：
- 需要不需要重训 router
- 需要不需要新标注
- 需要不需要重跑全量 benchmark
- 接入成本是低 / 中 / 高

### 原则 5：模块化优先于端到端一体化
先把 profile、predictor、policy、evaluator 分开，方便消融与替换。

## 4. 场景与数据

### 4.1 目标场景
- 通用 instruction following
- Open QA
- math / reasoning
- coding / knowledge / domain QA 的普通 query 场景
- 不要求多步 agent 执行

### 4.2 推荐 benchmark
第一阶段建议：
- MT-Bench
- MMLU / MMLU-Pro
- GSM8K / MATH-500
- RouterBench
- 可选：MixInstruct / RouterEval 中能稳定复现的子集

### 4.3 候选模型池
第一版建议控制在 4-8 个模型，覆盖明显异质性：
- 小模型：低成本、低延迟
- 中模型：中等成本、较均衡能力
- 强模型：高成本、复杂推理能力强

建议显式记录每个模型：
- model_id
- provider
- context window
- input/output price
- 平均 latency
- 适长任务类型
- reasoning / coding / knowledge 强项

## 5. 系统输入 / 输出

## 5.1 输入
每个 query 的 router state 建议包括：
- `query_text`
- `query_embedding`
- `task_tag`（如果可得）
- `budget_constraint`（可选）
- `latency_constraint`（可选）
- `candidate_model_profiles`
- `candidate_model_metadata`

其中：
- profile 是对模型能力的抽象表示
- metadata 是价格、延迟、窗口等系统约束

## 5.2 输出
### v1
- `selected_model_id`

### v2
- `selected_model_id`
- `selected_budget_level`

budget_level 可以先离散化为：
- `low`
- `medium`
- `high`

不要第一版就做连续 token budget 回归。

## 6. 推荐系统架构

```text
query
  ↓
query encoder
  ↓
query features -----------------------------┐
                                            │
model profile store ---- model metadata ----┼--> score predictor
                                            │
budget / latency constraints ---------------┘
  ↓
policy layer
  ↓
selected model (v1)
selected model + budget (v2)
  ↓
serving executor
  ↓
logging / evaluation layer
```

## 7. 核心模块定义

## 7.1 Query Encoder
职责：把 query 编码为 router 可用表征。

输入：
- query text

输出：
- dense embedding
- 可选的 task/domain logits
- 可选的 difficulty proxy

建议：
- v1 用固定 encoder 或轻量可训练 encoder
- 不要上来就用大 LLM 做 router 本体

可借鉴：
- RouteLLM 的 query-only route setting
- IRT-Router 的 query embedding
- RouteProfile 的 query-level structuring

## 7.2 Model Profile Store
职责：为每个候选模型维护统一 profile。

每个 model profile 至少包括：
- `model_id`
- `family`
- `size_bucket`
- `cost_profile`
- `latency_profile`
- `task_strength_vector`
- `reasoning_strength`
- `coding_strength`
- `knowledge_strength`
- `instruction_following_strength`
- `reliability_estimate`

来源：
- 预计算 benchmark 结果
- 代表性 query set 上的表现
- 官方 metadata
- 经验聚类 / capability fingerprint

可借鉴：
- RouteProfile
- IRT-Router
- ICL-Router / GraphRouter / SCOPE 在 survey 里的相关思想

## 7.3 Cost-Quality Predictor
职责：估计给定 query 交给某模型时的预期收益与代价。

输入：
- query features
- candidate model profile
- candidate metadata

输出：
- `expected_quality`
- `expected_cost`
- `expected_latency`
- `confidence`

实现选项：
1. binary strong-vs-weak classifier
2. per-model score predictor
3. pairwise preference / win predictor
4. latent ability matching

建议顺序：
- v1：pairwise / per-model score predictor
- v2：联合 quality-cost predictor

可借鉴：
- RouteLLM
- CARROT
- OptLLM
- IRT-Router

## 7.4 Policy Layer
职责：根据 predictor 输出做最终动作选择。

### v1 policy
`argmax_j U(q, j)`

其中：
- `U = quality_score - λ_cost * cost - λ_latency * latency`

### v2 policy
`argmax_(j,b) U(q, j, b)`

其中 budget 是离散动作。

策略要求：
- 可解释
- 可调 trade-off
- 可画 frontier

不建议第一版上复杂 RL policy。

## 7.5 Serving Executor
职责：执行最终调用，并把真实结果回写日志。

记录：
- selected model
- predicted score
- actual response
- token cost
- latency
- success metric

## 7.6 Evaluation Layer
职责：统一评估 router 是否真有价值。

必须输出：
- cost-quality frontier
- latency-quality frontier
- average cost
- average latency
- task metric
- oracle gap
- zero-router gap
- 新模型接入成本

对照 baseline：
- strongest model only
- cheapest model only
- random / round-robin
- zero router
- oracle router
- simple heuristic router

## 8. v1 训练与实现方案

## 8.1 数据构造
对每条 query 收集：
- 每个候选模型的输出
- 质量标签 / preference label
- cost
- latency

标签形式可以有三种：
1. 绝对任务得分
2. pairwise preference
3. relative gain over baseline

建议：
- 若数据以 preference 为主，先走 RouteLLM / CARROT 风格
- 若数据以 per-model score 为主，走 OptLLM / IRT-Router 风格

## 8.2 第一版模型
推荐一个够稳的起步组合：
- query encoder：轻量文本 encoder
- profile layer：静态 + 少量可训练投影
- predictor：MLP / pairwise scorer
- policy：显式 utility rule

为什么不直接上 LLM-as-router：
- 成本高
- latency 差
- benchmark 解释性弱
- 新模型接入流程不清楚

## 8.3 第一版实验配置
- 先固定一个 4-6 模型池
- 先做 query-level single-shot routing
- 先只优化 quality-cost
- latency 先做记录，不做主目标
- 先验证能否稳定超过 strongest-only / cheapest-only / heuristic

## 9. v2 升级路线

## 9.1 加入 budget action
从：
- `model_id`

扩成：
- `(model_id, budget_level)`

参考：
- R2-Router
- test-time compute 类论文

## 9.2 加入更低成本的新模型接入机制
目标：
- 不重训或少重训
- 不全量重跑 benchmark
- 通过 profile / fingerprint / calibration 接入

参考：
- RouteProfile
- clustering / fingerprint / graph-based generalization 思路

## 9.3 加入在线校准，但不把系统变成 agent controller
可以加入：
- 在线温度标定
- 轻量 bandit 校正
- deployment drift detection

但不要演化成完整 trajectory routing。

## 10. 成功标准

若 General Router 做成功，应该满足：
- 在多个 benchmark 上形成稳定 frontier
- 相比 strongest-only 显著降成本
- 相比 cheapest-only 显著提质量
- 在固定模型池上优于简单 heuristic
- 新模型接入成本可描述且可接受
- 输出可解释，不只是“黑箱觉得这个模型更好”

## 11. 对应论文映射

### 最关键
- RouteLLM：binary baseline
- CARROT：multi-model cost-aware routing
- RouteProfile：profile / expansion cost
- RouterBench：evaluation protocol

### 强相关
- IRT-Router：interpretable matching
- OptLLM：constrained assignment / Pareto search
- R2-Router：joint model+budget action

### 扩展参考
- FrugalGPT
- AutoMix
- Survey

## 12. 最终一句话

> 先把 General Router 做成一个可 benchmark、可解释、可扩展的 query-time model selector；只有在这一步站稳后，再把动作空间扩成 `(model, budget)`，而不是一开始就把它做成弱化版 agent runtime controller。
