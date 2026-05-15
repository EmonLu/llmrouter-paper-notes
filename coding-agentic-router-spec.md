# Coding Agentic Router Spec for SWE-bench

> 目标：实现一个面向 SWE-bench 类 repo-level bug fixing 任务的 coding agent runtime router，在 agent 执行期间动态决定 backbone、budget、workflow、granularity 和 recovery 策略。

## 1. 设计目标

这个系统解决的不是“给一个 query 选哪个模型”这么简单的问题，而是：

- 面对一个 SWE-bench 任务
- agent 在 repo 理解、检索、定位、打补丁、跑测试、修复失败的整条 trajectory 中
- 每一步都根据当前 state 动态决定：
  - 当前用哪个 backbone
  - 当前给多少 reasoning / rollout budget
  - 当前是否需要多 agent 协作
  - 当前是否要 fine-grained 执行，还是 compound execution
  - 当前是否应该升级、回滚、分支重试或终止

一句话定义：

> Coding Agentic Router 是一个 stateful runtime controller，作用对象不是单个 query，而是一条 repo-level software repair trajectory。

## 2. 非目标

第一版明确不做：
- 端到端统一 RL 训练整个 agent controller
- token-level 连续控制
- 自动学习所有 step type 和 role ontology
- 脱离 SWE-bench 的超泛化 workflow planner

第一版重点是：
- 模块化
- 可解释
- 可记录失败原因
- 可做 ablation

## 3. 设计原则

### 原则 1：trajectory-first，而不是 query-first
SWE-bench 是一条连续轨迹，不是独立 query 序列。

### 原则 2：routing action 不止 model id
真正重要的动作至少包括：
- model
- budget
- workflow mode
- granularity mode
- recovery mode

### 原则 3：cheap online signals 非常关键
测试反馈、rollout agreement、patch 无效次数、上下文压力，这些比静态难度预测更重要。

### 原则 4：先模块化 controller，再考虑统一 policy
需要能分辨收益来自 backbone router、budget controller、workflow controller 还是 recovery gate。

### 原则 5：evaluation 以任务成功率和轨迹成本为核心
不能只看单步准确率。

## 4. 任务对象

### 4.1 目标任务
- repo-level bug fixing
- 输入通常包括 issue / problem statement + repository snapshot
- 输出是能通过测试的 patch

### 4.2 环境特点
- 任务长程依赖强
- 中途存在工具调用（检索、grep、测试、diff、lint 等）
- 测试失败会提供强反馈
- patch 的局部正确不等于任务成功
- 整体成本由完整轨迹决定，而不是单次调用决定

## 5. 系统输入 / 输出

## 5.1 输入 state
建议把 runtime state 拆成 6 个部分：

### S1. Task metadata
- issue text
- repo name
- language
- framework
- test suite size
- suspected file scope

### S2. Step context
- 当前 step type
  - retrieve
  - inspect
  - localize
  - patch
  - test
  - reflect
  - summarize
- 当前上下文长度
- 已使用工具结果摘要

### S3. Patch state
- 当前 patch 是否存在
- patch 文件数
- patch 大小
- 最近 patch 是否重复修改同一区域

### S4. Test / verifier state
- 最近一次测试结果
- failing tests 数量
- error 类型分布
- 是否从 syntax error 收敛到 semantic / edge-case error

### S5. Trajectory budget state
- 当前累计 token
- 当前累计时间
- 当前累计 API 成本
- 剩余 budget

### S6. History / uncertainty state
- 最近 k 步是否卡住
- rollout 之间方案一致性
- 历史同类任务成功模式
- 当前策略的最近成功率

## 5.2 输出 action
建议把 action 拆成 5 类：

### A1. Backbone selection
- 选择当前 step 使用的模型

### A2. Budget selection
- 选择当前 step 的 reasoning / rollout / reflection budget level

### A3. Workflow selection
- 选择当前 step 用单 agent、双 agent，还是 planner-reviewer-tester 结构

### A4. Granularity selection
- 选择 fine-grained sequential execution 还是 compound execution

### A5. Recovery action
- keep current strategy
- increase budget
- switch stronger model
- add reviewer / tester
- rollback patch
- restart from localization
- spawn alternative branch
- terminate

## 6. 推荐系统架构

```text
issue + repo snapshot
  ↓
task initializer
  ↓
trajectory state encoder
  ↓
┌───────────────────────────────┐
│ backbone router              │
│ budget controller            │
│ workflow controller          │
│ granularity controller       │
│ recovery gate                │
└───────────────────────────────┘
  ↓
execution planner
  ↓
agent step execution
  ↓
observe logs / tests / patch / agreement
  ↓
state update
  ↓
next control step
```

## 7. 核心模块定义

## 7.1 Task Initializer
职责：任务开始时给出初始策略。

输入：
- issue
- repo metadata

输出：
- 初始 backbone tier
- 初始总 budget
- 初始 workflow mode
- 初始 granularity mode

建议：
- 不需要太复杂，rule-based + 轻量 classifier 即可
- 目标是防止一开始就把所有任务都送到最贵模式

## 7.2 Trajectory State Encoder
职责：把 repo/task/trajectory 的多源状态编码成 controller 可用表示。

输入：
- task metadata
- step context
- patch state
- test state
- history state

输出：
- compact state vector / structured state dict

要求：
- 支持增量更新
- 支持解释当前状态为何被判定为 hard / stuck / risky

可借鉴：
- GraphPlanner 的历史图记忆
- EcoAssistant 的 past solution retrieval
- Agent Capsules 的 runtime telemetry

## 7.3 Backbone Router
职责：为当前 step 选最合适模型。

输入：
- trajectory state
- step type
- candidate model profiles

输出：
- selected model id

适合借鉴：
- RouteProfile
- CARROT
- RouteLLM
- IRT-Router
- R2-Router

建议：
- 不要让 backbone router 单独控制全部系统
- 它只是 runtime controller 的一个子模块

## 7.4 Budget Controller
职责：决定当前 step 要花多少 compute。

控制对象：
- reasoning token budget
- rollout count
- reflection depth
- retry allowance

输出：
- budget tier: low / medium / high
- rollout cap
- reflection enable/disable

适合借鉴：
- TAB
- TrACE
- Test-time Compute
- s1
- R2-Router

建议：
- 先离散化 budget
- 先把 budget decision 绑到 step type 上

## 7.5 Workflow Controller
职责：决定当前 step 用什么 agent topology。

可能动作：
- single agent
- planner + executor
- executor + reviewer
- planner + executor + tester
- retriever + patcher + tester

适合借鉴：
- GraphPlanner
- EcoAssistant

建议：
- 第一版不要自动生成任意 graph
- 先从有限个 workflow template 中选

## 7.6 Granularity Controller
职责：决定当前是把子步骤拆开执行，还是合并执行。

动作：
- fine-grained sequential
- standard compound
- two-phase compound
- sequential compound

适合借鉴：
- Agent Capsules

这个模块对 SWE-bench 很重要，因为：
- 简单任务不值得每一步都独立调用
- 复杂修复任务又不能过度合并，否则质量下降

## 7.7 Recovery Gate
职责：根据失败信号决定是否升级 / 回退 / 分支重试。

输入：
- test failures
- repeated patch failures
- low agreement
- context overflow pressure
- no-progress streak

输出：
- keep
- escalate model
- escalate budget
- add reviewer/tester
- rollback
- branch retry
- stop

这个模块是 SWE-bench routing 的关键创新空间。

## 8. Step taxonomy

建议先把 coding trajectory 固定成如下 step taxonomy：

1. `retrieve`
2. `inspect`
3. `localize`
4. `patch`
5. `test`
6. `reflect`
7. `summarize`

为什么要固定：
- 方便记录 policy
- 方便做 ablation
- 方便后续统计“哪个阶段最值得升级模型 / 加预算”

## 9. v1 实现策略

## 9.1 第一版建议采用“模块 + 规则 + 轻量打分器”
而不是统一 learned policy。

推荐：
- backbone router：轻量 predictor
- budget controller：rule-based + cheap uncertainty signal
- workflow controller：template selector
- granularity controller：quality gate rule
- recovery gate：failure-pattern rules

原因：
- 易解释
- 易调试
- 易做 ablation
- 更贴近实际 agent 系统开发流程

## 9.2 推荐的 cheap signals
第一版强烈建议优先接这些信号：
- inter-rollout agreement
- failing tests 数量变化
- syntax -> semantic error 是否收敛
- patch 是否重复击中相同无效区域
- 当前上下文是否接近爆掉
- 最近 3 步是否无进展

这些信号很可能比训练一个大 router 更先带来收益。

## 9.3 第一版 workflow template
建议只定义少量模板：

### Template T1：single-agent
适合简单定位和简单修复。

### Template T2：patcher + tester
适合需要快速闭环的任务。

### Template T3：planner + patcher + tester
适合结构较复杂的问题。

### Template T4：patcher + reviewer + tester
适合 patch 质量不稳、需要审核的任务。

不要第一版就让 controller 自由生成任意图结构。

## 10. Evaluation protocol

## 10.1 核心指标
必须记录：
- task success rate
- average token cost per solved task
- average wall-clock time per solved task
- average number of model calls
- average number of test iterations
- patch acceptance / rollback ratio
- stuck trajectory ratio

## 10.2 按 step 分解的指标
建议额外记录：
- 每个 step type 平均调用成本
- 每个 step 的升级频率
- 不同 workflow template 的成功率
- 不同 granularity mode 的成本收益
- 不同 cheap signal 与最终成功率的相关性

## 10.3 baseline
至少要对比：
1. strongest-model single-agent baseline
2. fixed-model coding agent baseline
3. fixed-workflow multi-agent baseline
4. no-routing baseline（固定 backbone + 固定 budget + 固定 workflow）
5. only-backbone-router baseline
6. backbone+budget baseline

这样才能证明 runtime routing 的真实增益来自哪里。

## 11. 训练 / 校准数据来源

第一版不强依赖端到端监督训练。

可以收集：
- 历史 SWE-bench trajectory logs
- step-level success/failure signals
- test feedback transitions
- patch-level outcomes
- agreement / disagreement traces

如果后续做学习式 controller，可构造成：
- state-action-success tuples
- state-action-cost tuples
- state-escalation-outcome tuples

## 12. 与论文的模块映射

### 最接近系统本体
- GraphPlanner：workflow routing
- Agent Capsules：granularity control
- TrACE：cheap adaptive compute signal
- TAB：step/turn budget routing
- R2-Router：joint model + budget action

### backbone routing 子模块
- RouteProfile
- CARROT
- RouteLLM
- IRT-Router

### recovery / escalation 启发
- EcoAssistant
- AutoMix
- FrugalGPT
- Test-time Compute
- s1

## 13. v2 升级路线

### v2.1 从规则走向学习式 recovery gate
可以学习：
- 何时升级模型最划算
- 何时 rollback 最值
- 何时该开 reviewer / tester role

### v2.2 引入 memory-aware routing
让 router 使用：
- 相似 repo / 相似 bug 的历史成功轨迹
- 某类失败模式对应的高成功恢复策略

### v2.3 引入有限 branching policy
不是所有任务都值得 branch。
需要学会：
- 哪些 stuck signal 值得开分支
- 分支预算如何约束

## 14. 成功标准

若 Coding Agentic Router 做成功，应表现为：
- 相比 strongest-model baseline，有更高或相当的成功率且更低总成本
- 相比固定 workflow baseline，有更高成功率或显著更低 token/time
- 能显式解释在哪些 step 升级模型、增加 budget、切换 workflow 是值得的
- 能定位失败来源：是 backbone selection 错了、budget 不够、workflow 模式错了，还是 recovery 失败

## 15. 最终一句话

> Coding Agentic Router 的本质不是“替 coding agent 选一个模型”，而是“在 SWE-bench 这类长程修复轨迹里，持续控制 backbone、budget、workflow、granularity 与 recovery 的 runtime control plane”。
