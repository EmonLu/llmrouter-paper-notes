# SWE-bench Agent Router v1

这份文档的目的，是把 `coding-agentic-router-spec.md` 和 `coding-agentic-router-experiment-plan.md` 压缩成一个可以真正落地的 v1 系统设计。

它不是“最终形态的统一 controller”，而是一个：
- 明确边界
- 明确模块
- 明确日志 schema
- 明确先做哪些 routing action、后做哪些 routing action
的实现版本。

一句话定义：

> SWE-bench Agent Router v1 是一个面向 repo-level bug fixing trajectory 的 runtime controller。它不再把任务看成单次 query，而是根据 agent 当前所处步骤、测试反馈、patch 状态和预算状态，动态决定当前该用哪个 backbone、该花多少预算、以及何时触发恢复动作。

## 1. v1 目标

v1 只想先证明 3 件事：

1. 在 SWE-bench 类任务里，step-aware backbone routing 值得做
2. step-level budget routing 值得做
3. 简单 recovery gate 能减少 stuck trajectory 和浪费

也就是说，v1 先不追求完整的 workflow / granularity / branching super-controller。
先证明最核心的 runtime control 确实带来收益。

## 2. v1 不做什么

第一版明确不做：
- 不做端到端统一 RL controller
- 不做自动发现 workflow ontology
- 不做复杂 multi-agent branching tree search
- 不做连续 token-level budget control
- 不做太重的 online learning
- 不做过度泛化到所有代码 agent 场景

v1 的边界要非常克制。
否则系统会立刻变成：
- 太难调
- 太难归因
- 太难比较 baseline

## 3. v1 的核心判断

我建议 SWE-bench 这一条线的 v1，不要从 workflow routing 开始，而是从下面三个模块开始：

1. backbone router
2. budget controller
3. recovery gate

原因：
- backbone routing 最容易和 General Router 共享底层能力
- budget routing 最能体现 runtime routing 和普通 query router 的本质区别
- recovery gate 最能体现 trajectory control 的价值

而 workflow routing / granularity routing 虽然重要，但更适合在 v2 引入。

所以 v1 的主线不是：
- “做一个大而全的 agent orchestrator”

而是：
- “在固定 agent skeleton 上，给关键步骤加 runtime control”

## 4. v1 系统边界

## 4.1 任务对象

v1 目标任务：
- SWE-bench 类 repo-level bug fixing
- 输入：issue / problem statement + repository snapshot
- 输出：能通过测试的 patch

## 4.2 固定的 agent skeleton

v1 应该先固定住一个基础执行骨架：

1. retrieve
2. inspect
3. localize
4. patch
5. test
6. reflect
7. retry / recover

也就是说：
- v1 的流程骨架是固定的
- routing 只发生在关键控制点

这样做的好处是：
- 更容易做 ablation
- 更容易比较固定 baseline
- 更容易判断收益来自哪里

## 4.3 v1 开放的动作空间

v1 只开放 3 类动作：

### A1. Backbone selection
为当前 step 选择模型。

### A2. Budget selection
为当前 step 选择预算等级。

### A3. Recovery action
当卡住时，决定是否切强模型、加预算、回滚、重新定位或终止。

v1 不开放：
- workflow template selection
- granularity mode selection
- 自由 branching policy

这两类动作放到后续版本。

## 5. v1 推荐的 step 级 routing 方式

## 5.1 哪些 step 允许 backbone routing

我建议 v1 只在这几个 step 开放 backbone routing：
- `localize`
- `patch`
- `reflect`

其他 step 先固定：
- `retrieve`：便宜模型 / 固定模型
- `inspect`：中等模型 / 固定模型
- `test`：不是语言模型决策主场，不做复杂 router

原因：
- `localize`、`patch`、`reflect` 对能力差异最敏感
- 这些地方最可能真正体现“强模型值不值得花”

## 5.2 哪些 step 允许 budget routing

我建议 v1 只在这几个 step 开放 budget routing：
- `patch`
- `reflect`
- `retry / recover`

预算等级先离散为：
- `low`
- `medium`
- `high`

budget 对应的控制项可以先定义为：
- reasoning token 上限
- rollout 数量
- reflection 是否开启
- retry allowance

不要一开始就做连续 budget 分配。

## 5.3 recovery gate 在哪里触发

v1 recovery gate 建议只在两种时机触发：

1. test 失败后
2. 连续若干步无进展后

也就是：
- recovery 不要每一步都检查
- 只在真正的高风险节点做

否则 controller 自己会成为额外噪声源。

## 6. v1 输入 state

v1 不需要一上来把所有 runtime telemetry 都塞进去。
我建议第一版 state 限制为 5 类。

## 6.1 Task metadata
- `task_id`
- `repo_id`
- `language`
- `framework`
- `issue_length`
- `suspected_file_scope`

## 6.2 Step context
- `step_type`
- `current_context_tokens`
- `retrieval_summary`
- `recent_tool_observation`

## 6.3 Patch state
- `patch_exists`
- `patch_file_count`
- `patch_size`
- `same_region_edit_count`

## 6.4 Test state
- `last_test_status`
- `failing_test_count`
- `error_type_summary`
- `improvement_flag`

## 6.5 Budget and history state
- `total_tokens_used`
- `total_time_used`
- `remaining_budget`
- `no_progress_streak`
- `recent_rollout_agreement`

这是 v1 足够强但还不至于失控的一组 state。

## 7. v1 核心模块

## 7.1 Task Initializer

职责：任务开始时给出初始 backbone tier 和初始 budget tier。

v1 实现建议：
- rule-based
- 尽量简单

例如：
- issue 很短、疑似单文件修复：从中等 backbone + medium budget 起步
- issue 很长、跨文件、测试规模大：从较强 backbone + medium budget 起步

Task Initializer 在 v1 不需要训练得多复杂。
它的意义主要是：
- 不要让所有任务默认走最贵模式

## 7.2 Trajectory State Encoder

职责：把当前 trajectory 的关键状态编码成 router 可消费表示。

v1 实现建议：
- structured feature dict
- 必要时再加轻量 embedding

不要一开始就追求统一神经 state encoder。
第一版最重要的是：
- state 可解释
- state 可调试
- 日志里能直接看到 controller 为什么这么做

## 7.3 Backbone Router

职责：为 `localize` / `patch` / `reflect` 选择当前 backbone。

v1 建议：
- backbone router 不单独学成一个很重的 policy model
- 先做 profile-aware scorer
- 复用 General Router 的 profile / metadata 体系

它的输入建议包括：
- 当前 step type
- 当前任务复杂度 proxy
- 当前 patch / test 状态
- candidate model profiles
- candidate metadata

它的输出：
- `selected_model_id`
- `selection_reason`

## 7.4 Budget Controller

职责：决定当前 step 要花多少计算预算。

v1 预算动作：
- `low`
- `medium`
- `high`

建议先只控制：
- rollout 次数
- reflection 是否开启
- reasoning length cap
- retry allowance

推荐 cheap signals：
- 最近测试是否改善
- patch 是否反复击中同一区域
- rollout 之间是否高分歧
- 当前上下文是否接近压力上限

这个模块是 v1 里最能体现“agent runtime router 和普通 query router 不是一回事”的部分。

## 7.5 Recovery Gate

职责：在 trajectory 卡住时决定是否切换策略。

v1 recovery action 先限制在：
- keep current strategy
- increase budget
- switch stronger model
- rollback patch
- restart from localization
- terminate

先不要做：
- spawn alternative branch
- planner/reviewer 新角色动态加入
- 复杂多分支并行恢复

因为这些虽然强，但第一版很难判断值不值得。

## 8. v1 模型池建议

和 General Router 不同，这里的 candidate pool 不需要追求太宽。
我建议 v1 先只用 3 档 backbone：

- Tier 1：便宜模型
  - 用于 retrieve / 简单 inspect / 低风险步骤
- Tier 2：中等模型
  - 用于大部分默认 patch / localize
- Tier 3：强模型
  - 用于高风险 patch、反思、困难恢复

这样做的原因是：
- 在 SWE-bench 场景里，动作空间太大时 controller 很难学
- 三档 backbone 已足够验证 step-aware routing 的价值

每个 backbone 仍然要记录：
- price
- latency
- context window
- coding strength
- localization strength
- patch reliability
- reflection usefulness

## 9. v1 日志 schema

如果没有干净的 trajectory log，SWE-bench router 几乎无法研究。

每一步至少记录：
- `task_id`
- `step_idx`
- `step_type`
- `selected_model_id`
- `selected_budget_level`
- `recovery_action`
- `input_context_tokens`
- `output_tokens`
- `step_latency`
- `step_cost`
- `test_status_before`
- `test_status_after`
- `failing_test_count_before`
- `failing_test_count_after`
- `patch_size`
- `patch_file_count`
- `no_progress_streak`
- `rollout_agreement`
- `controller_reason`

任务级别再汇总：
- `task_success`
- `total_cost`
- `total_time`
- `total_model_calls`
- `total_test_iterations`
- `recovery_trigger_count`
- `rollback_count`

这层日志在 v1 里不是附属品，而是核心资产。

## 10. v1 baseline 设计

v1 至少要比较下面几类 baseline：

1. fixed strongest backbone + fixed medium budget
2. fixed strongest backbone + fixed high budget
3. fixed mid backbone + fixed medium budget
4. adaptive backbone only
5. adaptive budget only
6. adaptive backbone + adaptive budget
7. adaptive backbone + adaptive budget + recovery gate

这个顺序基本对应你的实验 phase。

没有这些 baseline，就无法回答：
- backbone routing 到底值多少
- budget routing 到底值多少
- recovery gate 到底值多少

## 11. v1 三组主实验

## 11.1 主实验 A：step-aware backbone routing

比较：
- fixed strongest
- fixed medium
- heuristic backbone router
- profile-aware backbone router

目标：
- 看不同 step 是否真的需要不同模型
- 看高价模型调用能否显著下降

## 11.2 主实验 B：step-level budget routing

比较：
- fixed high budget
- fixed medium budget
- adaptive budget
- adaptive backbone + adaptive budget

目标：
- 看预算是否应该集中花在 `patch` / `reflect` / `recover`
- 看是否存在“中等模型 + 高预算”优于“强模型 + 中预算”的区域

## 11.3 主实验 C：recovery gate

比较：
- no recovery gate
- rule-based recovery gate
- cheap-signal recovery gate

目标：
- 看 stuck trajectory ratio 是否下降
- 看 wasted token 是否下降
- 看最终成功率是否提升

## 12. v1 成功标准

我建议成功标准写得很具体。

只要满足下面 4 条中的 3 条，就可以认为 v1 成立：

1. adaptive backbone 相比 fixed strongest，能显著减少成本而保持接近成功率
2. adaptive budget 相比 fixed high budget，能显著减少 token / time 浪费
3. recovery gate 能明显降低 stuck trajectory ratio
4. 整体 modular controller 相比固定 agent baseline 有稳定收益，而不是只在少数任务上偶然有效

这里“稳定收益”比单次 SOTA 更重要。
因为你在做的是 runtime control 架构，不是单一 prompt trick。

## 13. v1 最大风险

## 13.1 state 过重

如果 state 设计太复杂，第一版会非常难调，最后不知道到底哪类信号真有用。

## 13.2 动作空间过大

如果一开始就做 backbone + budget + workflow + granularity + branching，全系统几乎不可归因。

## 13.3 便宜 signal 不够可靠

很多 runtime routing 的核心收益来自 cheap online signal。
如果信号定义太弱，controller 会做出很多噪声动作。

## 13.4 评测只看最终成功率

这是很危险的。
SWE-bench router 必须同时看：
- 成功率
- 成本
- 时间
- stuck ratio
- rollback / restart 行为

否则你看不见 runtime controller 的真实价值。

## 14. 我建议的 v1 实现顺序

### 第 1 步：先做固定 agent baseline + trajectory log
先把统一日志体系跑出来。

### 第 2 步：做 backbone routing
只在 `localize` / `patch` / `reflect` 上开放。

### 第 3 步：做 budget routing
先离散成三档，不要做连续预算。

### 第 4 步：做 recovery gate
先用 rule-based 和 cheap-signal 版本。

### 第 5 步：统一做 ablation
明确收益来自 backbone、budget 还是 recovery。

## 15. v1 对应的论文映射

- GraphPlanner：workflow-aware runtime controller 的上界参考
- Agent Capsules：granularity routing 的后续入口
- TrACE：cheap online signal 的关键参考
- TAB：step-level budget routing 的关键参考
- R2-Router：model + budget 联合动作的桥梁
- RouteProfile：backbone profile 层
- CARROT / RouteLLM：backbone selection 的 query-time 基础
- EcoAssistant：工具调用环境下的 runtime orchestration 启发

## 16. v2 最自然的扩展

如果 v1 跑通，v2 最自然的扩展顺序是：

1. 加 workflow template selection
2. 加 granularity routing
3. 再考虑 branch spawning
4. 最后再考虑更统一的 learned controller

也就是说，workflow / granularity 很重要，但应该建立在 backbone + budget + recovery 已经证明有效之后。

## 17. 一句话结论

> SWE-bench Agent Router v1 最值得做成“固定 agent skeleton 上的 backbone router + budget controller + recovery gate”，而不是一开始就做一个覆盖所有动作空间的庞大统一 controller。