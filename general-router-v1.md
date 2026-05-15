# General Router v1

这份文档不是再讲一遍 long-term vision，而是把当前的 `general-router-spec.md` 和 `general-router-experiment-plan.md` 压缩成一个真正可以开始实现的 v1 方案。

目标不是一步做到最强，而是先做出一个：
- 可复现
- 可评测
- 可扩展
- 能明确回答“router 到底有没有价值”的最小系统

一句话定义：

> General Router v1 是一个 query-time 多模型选择系统。它先不做复杂 agent runtime control，只解决“给一个普通 query，应该把它交给哪个模型”这个问题，并且把质量、成本、延迟统一放进同一个 evaluation 框架里。

## 1. v1 目标

v1 只做 4 件事：

1. 建一个 4-6 模型的异质 candidate pool
2. 给每个 query 输出一个 `selected_model_id`
3. 用统一 evaluator 画出 cost-quality-latency frontier
4. 明确测量“新增模型接入成本”

v1 追求的是：
- 比 strongest-only 明显更省钱
- 比 cheapest-only 明显更准
- 比简单 heuristic 更稳
- 比 binary strong-vs-weak router 更容易扩到多模型场景

## 2. v1 不做什么

这一版明确不做：
- 不做 `(model_id, budget_level)` 联合动作
- 不做 online learning / bandit / RL
- 不做复杂 uncertainty gate
- 不做 cascade / escalation pipeline
- 不做 workflow routing
- 不做 agent runtime control
- 不做连续 budget regression

这些都留给后续版本。

如果 v1 一开始把动作空间做大，最后很容易变成“系统看起来复杂，但无法判断收益到底来自哪一层”。

## 3. v1 的核心判断

我建议 v1 不要从 RouteLLM 风格的 binary router 起步，而是直接做：

> profile-aware 的 per-model scorer

原因很简单：
- 你的最终目标不是二选一 router，而是一般的多模型 router
- binary strong-vs-weak 很适合做 baseline，但不适合作为最终骨架
- 如果一开始就把 candidate model profile 作为一等公民，后面接新模型会顺很多

所以 v1 的角色分工应该是：
- RouteLLM：baseline
- CARROT：policy 主线
- RouteProfile：profile / onboarding 主线
- RouterBench：evaluation 主线
- IRT-Router：解释性备选线

## 4. v1 系统边界

## 4.1 输入

每条 query 的输入 state 建议限制为：
- `query_text`
- `query_embedding`
- `dataset_name`
- `task_tag`（如果有）
- `budget_constraint`（可选）
- `latency_constraint`（可选）
- `candidate_model_profiles`
- `candidate_model_metadata`

其中：
- `candidate_model_profiles` 用来表达能力画像
- `candidate_model_metadata` 用来表达价格、延迟、窗口等系统属性

## 4.2 输出

v1 输出非常简单：
- `selected_model_id`
- `selection_scores`
- `selection_reason`（可解释字段，哪怕先做简单版）

这里的 `selection_reason` 很重要。
即使第一版只是输出：
- 预测质量最高
- 满足预算约束下 utility 最优
- 在当前 task_tag 下 profile 最匹配

也比一个完全黑盒的 argmax 更适合后续分析。

## 5. v1 候选模型池

## 5.1 模型池规模

建议第一版固定在 4-6 个模型。
不要上来就 10+ 个，否则：
- 评测成本变高
- 路由误差更难定位
- 新模型接入实验更难做干净

## 5.2 模型池组成原则

v1 的 pool 必须显式异质：
- 1 个便宜小模型
- 1-2 个中等模型
- 1 个强推理模型
- 1 个强 instruction / chat 模型
- 可选 1 个强 coding 模型

重点不是追求“最强榜单”，而是制造足够清晰的 capability 差异。
如果模型池内部差异太小，router 很难学到稳定边界。

## 5.3 每个模型必须维护的字段

每个 candidate model 至少记录：
- `model_id`
- `provider`
- `family`
- `size_bucket`
- `context_window`
- `input_price`
- `output_price`
- `avg_latency`
- `p50_latency`
- `p95_latency`
- `strength_reasoning`
- `strength_knowledge`
- `strength_instruction`
- `strength_coding`
- `notes`

这里不要只存原始 benchmark 分数。
要同时存“结构化 profile”和“系统元数据”。

## 6. v1 最小系统架构

```text
query
  ↓
query encoder
  ↓
query feature
  ↓
profile-aware scorer  ←  model profile store + model metadata table
  ↓
utility layer
  ↓
selected_model_id
  ↓
executor
  ↓
logging + evaluator
```

v1 不需要把模块拆得太花，但这 6 层最好从一开始就逻辑分开。

## 7. v1 核心模块

## 7.1 Query Encoder

职责：把 query 变成 router 可消费的特征。

v1 建议：
- 先用固定 embedding encoder
- 先不把 router 本体做成大语言模型
- 先做 query-only representation，再视情况加 task tag / difficulty proxy

输出字段建议：
- `query_embedding`
- `query_length`
- `task_tag`
- `difficulty_proxy`（可选）

v1 的关键不是 encoder 花哨，而是后面的 scoring 和 evaluation 结构清楚。

## 7.2 Model Profile Store

职责：维护每个模型的统一能力画像。

v1 每个模型的 profile 至少包含：
- `task_strength_vector`
- `cost_profile`
- `latency_profile`
- `reliability_estimate`
- `family_embedding` 或等价的结构化表征

profile 的来源建议混合：
- benchmark 结果
- representative query set 上的表现
- 官方元数据
- 人工规则补充

v1 不必追求最优 profile learning。
但一定要把 profile 层做出来，否则后面讨论新模型接入就没有抓手。

## 7.3 Per-model Scorer

职责：给每个 `(query, model)` 打分。

v1 推荐输出：
- `expected_quality`
- `expected_cost`
- `expected_latency`
- `confidence`

然后统一变成：
- `utility_score`

建议的 utility 形式：

`U(q, m) = quality_score - λ_cost * cost - λ_latency * latency`

这里最重要的不是公式多高级，而是：
- 参数可调
- 可以画 frontier
- 可以做不同 λ 下的比较

## 7.4 Policy Layer

职责：从多模型分数里做最终选择。

v1 直接做：
- `selected_model = argmax_m U(q, m)`

同时保留：
- top-k scores
- second-best margin
- 触发预算约束时的过滤信息

这样后面做 error analysis 会容易很多。

## 7.5 Logging + Evaluator

这是 v1 里和 router 本身同样重要的一层。

每次路由至少记录：
- `query_id`
- `dataset_name`
- `selected_model_id`
- `utility_score`
- `predicted_quality`
- `predicted_cost`
- `predicted_latency`
- `actual_quality`
- `actual_cost`
- `actual_latency`
- `top2_margin`
- `task_tag`

如果没有这层日志，后面你会很难分析：
- router 为什么把 query 送错了
- 是 profile 不对，还是 scorer 不对
- 是对 cost 估计错了，还是对质量估计错了

## 8. v1 训练与数据组织

## 8.1 benchmark 范围

我建议 v1 先覆盖：
- MT-Bench
- MMLU 或 MMLU-Pro
- GSM8K
- MATH-500
- RouterBench 可对齐子集

这个组合的好处是：
- 有对话 / instruction
- 有知识
- 有 math / reasoning
- 能让模型池差异显出来

## 8.2 数据目录建议

```text
data/general-router/
  datasets/
    <dataset>/queries.jsonl
    <dataset>/labels.jsonl
    <dataset>/responses/<model_id>.jsonl
    <dataset>/metrics/<model_id>.jsonl
  models/
    model_metadata.json
    model_profiles.json
  router_training/
    train.jsonl
    val.jsonl
    test.jsonl
  runs/
    <run_id>/predictions.jsonl
    <run_id>/summary.json
```

重点是从一开始把“模型输出”和“router 输出”分开。

## 8.3 监督信号

v1 的监督目标建议先用：
- 每个 query 在各模型上的离线质量分数
- 对应的 cost / latency
- 由此计算 utility target

也就是说，v1 更像：
- 离线 utility prediction
而不是：
- 在线 bandit learning

这是更干净的起点。

## 9. v1 baseline 设计

v1 必须同时跑这几类 baseline：

1. strongest-only
2. cheapest-only
3. random routing
4. heuristic difficulty router
5. RouteLLM-style binary router
6. oracle router

这 6 类 baseline 缺一不可。

尤其是 RouteLLM-style baseline 很重要，因为它能直接回答：
- “binary router 已经够了吗？”
- “我们直接上 multi-model scorer 是否真的值得？”

## 10. v1 最关键的主实验

我建议 v1 先只做 3 组主实验。

## 10.1 主实验 A：router 是否成立

比较：
- strongest-only
- cheapest-only
- heuristic
- binary router
- per-model scorer

目标：
- 看 per-model scorer 是否稳定形成更好的 frontier

## 10.2 主实验 B：profile 层是否有价值

比较：
- 无 profile 的 query-only scorer
- 带 profile 的 scorer

目标：
- 看 profile 是否改善跨任务泛化
- 看 profile 是否让 selection 更稳定

## 10.3 主实验 C：新模型接入成本

做 leave-one-model-out onboarding：
- 训练时拿掉一个模型
- 测试时把它作为新模型接入

比较：
- full retrain
- profile-only adaptation
- 少量 calibration

这是 v1 非常关键的一组实验。
因为它直接决定这个系统是不是有长期工程价值。

## 11. v1 成功标准

我建议把成功标准写得非常具体。

只要满足以下 4 条中的 3 条，就可以认为 v1 成立：

1. 相比 strongest-only，平均 cost 明显下降，质量下降保持在可接受范围
2. 相比 cheapest-only，质量明显提升
3. 相比 heuristic / binary router，frontier 更平滑、更稳定
4. 新模型接入时，不必每次 full retrain 才能恢复大部分性能

这里“更平滑、更稳定”比单次最优点更重要。
因为你的目标不是做一次 paper 图，而是做长期可扩展 router。

## 12. v1 最大风险

## 12.1 模型池差异不够大

如果选的模型都差不多，router 看起来没收益，但其实是实验设置太弱。

## 12.2 evaluator 不统一

如果不同 benchmark 的质量指标无法统一，最后 utility 学出来会很噪。

## 12.3 profile 做成了静态装饰

很多系统把 profile 写成 metadata 表，但训练和策略里根本没真正用到。
那样 profile 层就失去意义了。

## 12.4 一开始就追求 budget-aware

这会把问题复杂度抬太快。
v1 最该证明的是“多模型选择”本身成立。

## 13. 我建议的 v1 实现顺序

### 第 1 步：先做统一 evaluator
先别急着训练 router。
先把：
- strongest-only
- cheapest-only
- oracle
- heuristic
跑通，并确保能画 frontier。

### 第 2 步：做 model metadata + profile store
把 candidate pool 管理清楚。

### 第 3 步：做 query-only scorer baseline
先有一个最朴素版本。

### 第 4 步：做 profile-aware scorer
这是 v1 的主线版本。

### 第 5 步：做 leave-one-model-out onboarding 实验
这一步决定这个系统是否具备长期价值。

## 14. v1 对应的论文映射

- RouteLLM：binary baseline
- CARROT：multi-model utility 主线
- RouteProfile：profile 与 onboarding 主线
- RouterBench：统一评测框架
- IRT-Router：解释性参考线
- OptLLM：约束式 objective 参考线
- R2-Router：v2 的 model+budget 扩展入口

## 15. 一句话结论

> General Router v1 最值得做成“profile-aware 的 per-model utility router + 统一 frontier evaluator”，而不是先做一个更复杂但难以归因的 joint controller。