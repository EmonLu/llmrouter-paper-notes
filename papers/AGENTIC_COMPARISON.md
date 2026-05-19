# papers/AGENTIC_COMPARISON

这个文件不是论文摘要，而是专门给 `agentic` 组用的设计对照页。

它要回答的不是：
- 哪篇 paper 分数更高

而是：
- 这篇 paper 在 coding agent runtime 里控制的是哪一层？
- 它对我的 SWE-bench agent router 最有用的部件是什么？
- 哪些值得复用，哪些不能原样照搬？

当前 agentic 组共 8 篇：
- 2604.14228 — Dive into Claude Code
- 2604.23626 — GraphPlanner
- 2605.00410 — Agent Capsules
- 2604.05164 — TAB
- 2604.08369 — TrACE
- 2408.03314 — Test-time Compute
- 2501.19393 — s1
- 2310.03046 — EcoAssistant

## 1. 先给一个总分层

如果按“对 coding agent runtime 控制面的哪一层最有帮助”来分，这 8 篇最好拆成 5 组：

### A. Runtime Architecture / Control Plane
- 2604.14228 — Dive into Claude Code

作用：
- 定义 runtime substrate
- 定义 tool loop / permission / compaction / session persistence / subagent delegation
- 它不是 policy paper，而是 agent 系统底座 paper

### B. Workflow Controller
- 2604.23626 — GraphPlanner

作用：
- 定义 workflow-level routing
- 决定 role、workflow path、backbone 组合
- 最接近“agentic router 本体”

### C. Granularity Controller
- 2605.00410 — Agent Capsules

作用：
- 定义 execution granularity routing
- 决定一步一步拆开执行，还是 compound execution
- 直接对应 coding agent 里的 fine-grained vs compound mode

### D. Budget / Adaptive Compute Controller
- 2604.05164 — TAB
- 2604.08369 — TrACE
- 2408.03314 — Test-time Compute
- 2501.19393 — s1

作用：
- 决定当前 step 要不要继续想、想多久、是否追加 rollout、是否升级 compute
- 这是 coding agent router 里最容易先落地的一层

### E. Memory / Retrieval / Escalation Support
- 2310.03046 — EcoAssistant

作用：
- 提供 solved-case retrieval
- 提供 hierarchy escalation
- 提供 runtime feedback 驱动的 memory 增益思路

## 2. 横向总表

| paper | 主要角色 | 控制对象 | 控制粒度 | 决策方式 | 最适合放进哪一层 | 最值得复用的东西 | 不该原样照搬的东西 |
|---|---|---|---|---|---|---|---|
| Dive into Claude Code | runtime architecture | tool loop / permission / compaction / subagent / session | system-level | system design + runtime mechanism | control plane substrate | permission model、compaction、session persistence、delegation | 具体产品化细节与实现边界 |
| GraphPlanner | workflow controller | role + backbone + workflow path | trajectory / workflow-level | learned policy + graph memory | workflow controller | workflow routing、graph memory、role-model joint action | 直接照搬全 RL workflow generation |
| Agent Capsules | granularity controller | execution mode / group composition | group / step-level | heuristic + quality gate + escalation ladder | granularity controller | compound vs fine-grained mode、quality gate、escalation ladder | 用 LLM judge 直接替代真实代码验证 |
| TAB | budget controller | per-turn token budget | turn-level | learned budget policy | budget controller | history-aware budget allocation、global budget constraint | 数学任务 reward 与状态定义 |
| TrACE | cheap online controller | whether to continue rollout | step-level | training-free agreement rule | budget / recovery gate | disagreement 作为免费 runtime 信号 | 直接用文本 plurality 作为代码动作等价判断 |
| Test-time Compute | compute policy framework | compute allocation / revision / search depth | step / program-level | framework + policy family | budget controller 理论层 | 把 compute 当成显式动作空间 | 只用 FLOPs 近似真实 runtime 成本 |
| s1 | simple budget baseline | stop / continue thinking | generation-level | budget forcing | inner-loop budget primitive | stop/continue 硬控制、追加 think budget | 直接追加 `Wait` 这种字符串技巧 |
| EcoAssistant | retrieval + escalation support | assistant hierarchy / retrieval / escalation | runtime-level | retrieval + hierarchy + execution feedback | memory / recovery support | solved-case retrieval、execution-aware escalation | 直接照搬其数据与 memory 累积方式 |

## 3. 这 8 篇之间到底是什么关系

最短关系图可以这么看：

```text
Claude Code paper
  ↓ 给出 runtime substrate
GraphPlanner
  ↓ 决定 workflow 怎么走
Agent Capsules
  ↓ 决定 execution granularity
TAB / TrACE / Test-time Compute / s1
  ↓ 决定当前 step 给多少 compute
EcoAssistant
  ↓ 提供 retrieval / escalation / memory 增益
```

所以这几篇不是重复，而是分层互补：
- 2604.14228 解决“agent 系统底座怎么搭”
- GraphPlanner 解决“workflow 怎么选”
- Agent Capsules 解决“执行粒度怎么选”
- TAB / TrACE / Test-time Compute / s1 解决“当前 step 算多久”
- EcoAssistant 解决“失败后怎么借历史经验恢复”

## 4. 如果按设计价值排序

### 4.1 对系统骨架最重要
1. 2604.14228 — Dive into Claude Code
2. 2604.23626 — GraphPlanner
3. 2605.00410 — Agent Capsules

原因：
- 这三篇决定的不是某个局部超参，而是 runtime system 的基本形状
- 如果这三层没有，后面的 budget policy 很容易挂在错误的执行骨架上

### 4.2 对第一版最容易先落地
1. 2604.08369 — TrACE
2. 2501.19393 — s1
3. 2604.05164 — TAB

原因：
- TrACE：几乎可以零训练先上
- s1：给你最简单的 stop / continue primitive
- TAB：再往上升级成 history-aware budget controller

### 4.3 对长期上限最关键
1. 2604.23626 — GraphPlanner
2. 2605.00410 — Agent Capsules
3. 2604.05164 — TAB

原因：
- 这些论文都说明：真正的 agentic router 动作空间不能只有 model id
- 还必须包含 workflow、granularity、budget 这些 runtime action

## 5. 对 Coding Agentic Router 的直接映射

如果把你的目标系统拆成：
- backbone router
- budget controller
- workflow controller
- granularity controller
- recovery gate
- memory manager
- tool / permission layer
- observability layer

那么这 8 篇最自然的映射是：

### 5.1 Control Plane Substrate
- Dive into Claude Code

给你的东西：
- tool loop
- permission boundary
- compaction pipeline
- session persistence
- subagent delegation
- extensibility interface

### 5.2 Workflow Controller
- GraphPlanner

给你的东西：
- trajectory-state → workflow action
- role/backbone/workflow 联合动作
- graph memory 作为状态编码器

### 5.3 Granularity Controller
- Agent Capsules

给你的东西：
- 是否拆成多个细步执行
- 是否把多步合并成 compound call
- quality gate 与 escalation ladder

### 5.4 Budget Controller
- TAB
- TrACE
- Test-time Compute
- s1

给你的东西：
- TAB：history-aware budget allocation
- TrACE：cheap online uncertainty signal
- Test-time Compute：compute policy 的总框架
- s1：最小可用的 continue-thinking primitive

### 5.5 Memory / Recovery Support
- EcoAssistant

给你的东西：
- solved-case retrieval
- hierarchy escalation
- execution feedback 驱动的经验积累

## 6. 哪几篇应该先看，哪几篇后看

### 最小闭环阅读顺序
1. 2604.14228 — 先把 runtime substrate 看清楚
2. 2604.23626 — 再看 workflow controller
3. 2605.00410 — 再看 granularity controller
4. 2604.08369 — 再看 cheap online budget gate
5. 2604.05164 — 再看 learned budget controller
6. 2310.03046 — 最后补 memory / escalation

这 6 篇能先拼出一个最小闭环。

### 第二层补充
7. 2501.19393 — s1
8. 2408.03314 — Test-time Compute

这两篇更适合作为：
- inner-loop budget primitive
- compute policy 理论背景

## 7. 如果只保留一个最小系统设计组合

我会保留这 5 篇：
- 2604.14228
- 2604.23626
- 2605.00410
- 2604.08369
- 2310.03046

理由很简单：
- 2604.14228：给底座
- GraphPlanner：给 workflow
- Agent Capsules：给 granularity
- TrACE：给 cheap runtime signal
- EcoAssistant：给 retrieval / escalation

如果再加第 6 篇，就加：
- TAB

因为它能把 budget controller 从 heuristic 提升到 history-aware learned policy。

## 8. 哪些结论最值得固定下来

### 结论 1
Coding Agentic Router 不是 query router 的直接放大版。

### 结论 2
真正的动作空间至少应该包含：
- workflow
- granularity
- budget
- recovery
而不只是 model selection。

### 结论 3
如果没有 runtime substrate，后面的 policy 很难稳定挂上去。

### 结论 4
第一版不一定要先训复杂 controller，先上 cheap online signal 反而更现实。

### 结论 5
memory / retrieval / escalation 不是附属模块，而是 agent runtime 成败的关键部分。

## 9. 我的最终建议

如果你下一步是做系统，而不是继续读更多 paper，我建议按下面顺序推进：

### Step 1：先定 runtime substrate
参考：
- Dive into Claude Code

### Step 2：先做 rule-based workflow + granularity skeleton
参考：
- GraphPlanner
- Agent Capsules

### Step 3：先接一个 cheap budget gate
参考：
- TrACE
- s1

### Step 4：再升级成 learned budget controller
参考：
- TAB

### Step 5：最后补 retrieval / escalation / memory
参考：
- EcoAssistant

## 10. 一句话结论

> 这 8 篇 agentic paper 不是在重复讲“怎么路由”，而是在分层回答：agent runtime 底座怎么搭、workflow 怎么选、执行粒度怎么控、每一步算多久、失败后怎么靠 memory 和 escalation 继续跑。