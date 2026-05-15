# General Router Experiment Plan

> 目标：把 `general-router-spec.md` 变成一套可执行、可比较、可迭代的实验路线，优先验证“query-time 多模型路由器”是否能在普通 benchmark 上形成稳定的 cost-quality-latency frontier。

## 1. 实验目标

这组实验要回答 5 个核心问题：

1. 一个简单但设计干净的 query-time router，能否稳定优于 strongest-only / cheapest-only / heuristic baseline？
2. profile layer 是否真的能提升跨任务泛化与新模型接入能力？
3. 多模型 risk objective（CARROT / OptLLM 风格）是否比 binary strong-vs-weak routing（RouteLLM 风格）更适合长期扩展？
4. 将动作从 `model_id` 扩展到 `(model_id, budget_level)` 后，frontier 是否进一步改善？
5. 新增模型时，到底哪种方案接入成本最低、收益最高？

## 2. 总体实验路线

建议按 4 个 phase 走，而不是一开始就把所有东西混在一起。

```text
Phase 0: 建 benchmark 与日志面板
Phase 1: 只做 model selection
Phase 2: 引入 profile layer / 新模型接入实验
Phase 3: 扩展到 (model, budget) 联合动作
```

## 3. Phase 0：评测与数据基线准备

## 3.1 目标
先建立统一实验底座，避免后面每个 router 都换一套评价方式。

## 3.2 数据集
建议优先使用：
- MT-Bench
- MMLU / MMLU-Pro
- GSM8K
- MATH-500
- RouterBench（如果以预计算结果为主）

数据组织建议：
- `data/general-router/<dataset>/queries.jsonl`
- `data/general-router/<dataset>/labels.jsonl`
- `data/general-router/<dataset>/model_outputs/<model_id>.jsonl`
- `data/general-router/<dataset>/cost_latency/<model_id>.jsonl`

## 3.3 候选模型池
第一阶段控制在 4-6 个模型，必须有明显异质性：
- 一个便宜小模型
- 一个中等模型
- 一个强推理模型
- 一个强 chat / instruction 模型
- 可选一个强 coding 模型

记录字段：
- model_id
- provider
- size_bucket
- input/output price
- latency statistics
- context window
- task notes

## 3.4 统一评测指标
必须统一输出：
- task metric（accuracy / win rate / pass-like score）
- average cost
- average latency
- cost-quality frontier
- latency-quality frontier
- oracle gap
- zero-router gap
- per-dataset breakdown

## 3.5 必备 baseline
所有 phase 都要保留：
1. strongest-only
2. cheapest-only
3. random routing
4. round-robin（可选）
5. heuristic difficulty rule
6. zero router / convex hull baseline（若能对齐 RouterBench 视角）
7. oracle router

## 3.6 Phase 0 交付物
- 一个统一 evaluator
- 一个模型池元数据表
- 一个 benchmark dashboard schema
- 所有 baseline 的首轮结果

## 4. Phase 1：只做 model selection

## 4.1 目标
验证一个干净的 query-time router 是否足以形成可观收益。

动作空间：
- `a = model_id`

## 4.2 第一批要比较的 router family

### Router A：Binary router
- 风格：RouteLLM
- 作用：给 strongest-vs-cheapest 提供最小可行 baseline
- 用途：验证“query router 能不能成立”

### Router B：Per-model score predictor
- 风格：CARROT / OptLLM
- 作用：预测每个模型对 query 的 expected utility
- 用途：验证 multi-model routing 是否比 binary routing 更稳

### Router C：Interpretable latent matcher
- 风格：IRT-Router
- 作用：做 query-model matching 并保留一定解释性
- 用途：看可解释路由是否会明显损失效果

## 4.3 Phase 1 的核心对比问题
- binary vs multi-model：谁的 frontier 更好？
- rule-based utility vs learned predictor：谁更稳？
- 单任务训练 vs 混合任务训练：谁泛化更好？
- 是否显式建模 latency 会改变最优 policy？

## 4.4 Phase 1 指标
除统一指标外，额外看：
- 每个模型被选中的频率
- 高难 query 被送往强模型的比例
- 简单 query 被错误送往强模型的浪费率
- 低成本模型承担的有效请求比例

## 4.5 Phase 1 成功标准
满足以下之一即可认为值得进入 Phase 2：
- 在多个数据集上相对 strongest-only 显著降成本，且质量下降可接受
- 在多个数据集上明显优于 heuristic difficulty baseline
- multi-model router 在 frontier 上稳定优于 binary router

## 5. Phase 2：引入 profile layer 与新模型接入实验

## 5.1 目标
回答最关键的工程问题：

> 新增一个候选模型时，router 到底需要付出多大代价？

## 5.2 要比较的方案

### 方案 P1：无 profile，直接重训
- 最直接
- 成本最高
- 作为 upper-cost baseline

### 方案 P2：静态 profile + 少量校准
- 风格：RouteProfile
- 只补 model metadata / 少量 representative queries

### 方案 P3：latent ability / fingerprint 接入
- 风格：IRT-Router / survey 中的 fingerprint 路线
- 通过 query-performance summary 接入新模型

## 5.3 实验设计
做“留一模型接入”实验：
- 训练时移除一个候选模型
- 测试时把它当新模型接入
- 比较：
  - full retrain
  - profile-only adaptation
  - lightweight calibration

## 5.4 核心指标
- 接入后 performance drop
- 接入后 frontier 恢复速度
- 需要新增标注量
- 需要新增评测量
- 训练/校准耗时
- 接入成本等级（低/中/高）

## 5.5 关键假设
- RouteProfile 风格方法在“新增模型接入成本”上会优于纯 classifier-based router
- 多模型统一 profile 可能比单纯 query-only router 更重要

## 6. Phase 3：扩展到 `(model, budget)` 联合动作

## 6.1 目标
回答第二个关键问题：

> 把动作从“选模型”扩成“选模型 + 预算”后，收益是否足够大？

## 6.2 动作空间
建议离散成：
- low budget
- medium budget
- high budget

每个 budget 对应：
- 不同 generation length 上限
- 是否启用 reasoning mode
- 不同 sampling / self-consistency 设置（若适用）

## 6.3 参考路线
- R2-Router
- Test-time Compute
- s1（作为简单 budget forcing baseline）

## 6.4 比较对象
1. only model routing
2. fixed strongest model + variable budget
3. variable model + fixed budget
4. variable model + variable budget

## 6.5 核心指标
- budget-aware frontier 是否优于 model-only frontier
- reasoning-heavy 数据集上的增益是否更明显
- 是否出现“cheap model + higher budget”优于“strong model + low budget”的区域

## 6.6 风险
- 动作空间一扩大，policy variance 会明显上升
- 如果 evaluator 不统一，很容易出现“看起来更强，实际只是 budget 更高”

所以必须显式报：
- token usage
- length distribution
- response latency
- per-budget selection ratio

## 7. 实验矩阵

## 7.1 主实验矩阵

| 维度 | 配置 |
|---|---|
| Router family | binary / multi-model scorer / latent matcher |
| Profile | none / static profile / adaptive profile |
| Action space | model-only / model+budget |
| Objective | quality-cost / quality-cost-latency |
| Training regime | single-dataset / mixed-dataset |
| New model onboarding | full retrain / profile adaptation / lightweight calibration |

## 7.2 推荐的执行顺序
1. 跑所有 baseline
2. 跑 binary router
3. 跑 multi-model scorer
4. 跑 latent matcher
5. 固定最优 model-only 方案
6. 做新模型接入实验
7. 再扩到 model+budget

## 8. 消融实验

至少做以下 ablation：
- 去掉 profile layer
- 去掉 cost term
- 去掉 latency term
- 去掉 difficulty proxy
- 不同 candidate pool size
- 不同数据集混合策略
- 不同新模型接入方式
- 不同 budget 离散粒度

## 9. 失败分析框架

每次实验结束后，按以下类别做 error analysis：
- easy query 被错误送到强模型
- hard query 被错误送到弱模型
- 对某一任务域系统性偏置
- 对某一模型 profile 估计失真
- 新模型接入后 calibration 失败
- budget 动作选择失真

## 10. 推荐交付物

建议最终沉淀成这些表：

### 表 A：主结果表
- strongest-only
- cheapest-only
- heuristic
- binary router
- multi-model router
- latent router
- best profile-aware router
- best budget-aware router

### 表 B：新模型接入成本表
列：
- router
- 是否需要重训
- 是否需要重标注
- 是否需要补评测
- 接入耗时
- 接入后质量损失

### 表 C：frontier 图
- 每个数据集一张
- 所有数据集合并一张

## 11. 项目执行建议

## 11.1 第一阶段只回答一个问题
先回答：

> 一个 clean 的 multi-model query router，能不能稳稳优于 strongest-only / cheapest-only / heuristic？

只有这个问题回答清楚，后面 profile 与 budget 扩展才有意义。

## 11.2 优先级排序
- P0：评测与 baseline
- P1：model-only router
- P2：profile / onboarding
- P3：model+budget

## 12. 一句话结论

> General Router 的实验路线应该先用统一 evaluator 证明“query-time model selection”本身成立，再去研究 profile 层与新模型接入，最后再扩展到 `(model, budget)` 联合动作；不要一开始就把动作空间做得过大。
