# papers/INDEX

这个页面现在不再只是“领域综述目录”，而是直接围绕你的两个最终 design target 来组织：

1. General Router
   - 面向普通 benchmark / 普通 query 数据集
   - 重点解决：选哪个模型、是否分配额外 budget、如何维持 cost-quality frontier

2. Coding Agentic Router for SWE-bench
   - 面向 repo-level bug fixing / coding agent trajectory
   - 重点解决：在 agent 执行期间，如何做 backbone routing、budget routing、workflow routing、granularity routing、recovery routing

如果一句话概括：

> 这个仓库现在服务的不是一个统一“router”，而是两条设计路线：一条是 benchmark-ready general router，一条是面向 SWE-bench runtime control 的 coding agentic router。

## 1. 两个最终 target 的本质区别

| 维度 | General Router | Coding Agentic Router |
|---|---|---|
| 任务对象 | 单个 query / 单轮请求 | 一条多步 agent trajectory |
| 典型数据集 | MMLU, GSM8K, MT-Bench, RouterBench, Open QA | SWE-bench 风格 repo-level bug fixing |
| Routing state | query + model/profile + cost/budget | repo state + step state + test feedback + history + budget |
| Routing action | 选模型，最多加选 budget | 选模型 + 选 budget + 选 workflow + 选 granularity + 选 recovery |
| 评价目标 | frontier：质量 / 成本 / 延迟 | task success + token/time/cost + trajectory 稳定性 |
| 推荐设计风格 | benchmark-friendly, modular, interpretable | runtime-control-first, online, stateful |

所以后面看每篇 paper，不要再只问“它是不是 router paper”，而要问：
- 它是更支持 General Router，还是更支持 Coding Agentic Router？
- 它解决的是 backbone selection，还是 budget / workflow / runtime control？

## 2. 面向两个 target 的总览地图

```text
Track A: General Router

Survey / evaluation
├── Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey
└── RouterBench

Core query routing
├── RouteLLM
├── OptLLM
├── CARROT
├── IRT-Router
└── R2-Router   (第二阶段，加入 budget action)

Supporting layer
└── RouteProfile

Cascade extensions
├── FrugalGPT
└── AutoMix
```

```text
Track B: Coding Agentic Router (SWE-bench)

Closest-to-runtime-control papers
├── GraphPlanner
├── Agent Capsules
├── TrACE
├── TAB
└── R2-Router

Backbone-selection submodule support
├── RouteProfile
├── CARROT
├── RouteLLM
└── IRT-Router

System-control inspiration
├── EcoAssistant
├── AutoMix
├── Test-time Compute
└── s1
```

## 3. Track A：General Router 该怎么看这些 paper

## 3.1 这个 track 的目标

General Router 目标不是做复杂 agent，而是做一个可 benchmark、可比较、可扩展的多模型路由器：
- 给定一个 query
- 输出一个模型，或 `(模型, budget)`
- 在 quality / cost / latency 之间做稳定 trade-off
- 新模型加入时接入成本尽量低

## 3.2 Track A 的核心论文分组

### A. 地图与评测层

#### 2603.04445 — Survey
- 文件：`2603.04445-survey-dynamic-model-routing-and-cascading.md`
- 用途：给 General Router 定义方法 taxonomy 和统一视角
- 对 Track A 的价值：
  - 帮你区分 difficulty routing、preference routing、uncertainty routing、cascading
  - 帮你避免把所有 query router 混成一类

#### 2403.12031 — RouterBench
- 文件：`2403.12031-routerbench.md`
- 用途：给 General Router 提供 benchmark / frontier evaluator
- 对 Track A 的价值：
  - 没有它，你很难判断新 router 是否真的优于 heuristic
  - 它是 Track A 的 evaluation anchor

### B. Query-level backbone selection 主线

#### 2406.18665 — RouteLLM
- 文件：`2406.18665-routellm.md`
- 角色：binary strong/weak baseline
- 为什么重要：
  - 它把问题讲得最清楚：query-level router 最小可行形态是什么
  - 很适合作为你的第一版 baseline

#### 2502.03261 — CARROT
- 文件：`2502.03261-carrot.md`
- 角色：cost-aware multi-model router
- 为什么重要：
  - 把二元路由扩展成多模型风险最小化
  - 对 General Router 比 RouteLLM 更贴近长期目标

#### 2405.15130 — OptLLM
- 文件：`2405.15130-optllm.md`
- 角色：Pareto / constrained assignment router
- 为什么重要：
  - 对“给定预算下如何全局分配”有直接启发
  - 很适合做 constrained policy 视角

#### 2506.01048 — IRT-Router
- 文件：`2506.01048-irt-router.md`
- 角色：可解释 route matching
- 为什么重要：
  - 如果你后面很看重新模型接入和解释性，这篇会比 RouteLLM 更有启发

### C. 支撑层：让 router 可扩展

#### 2605.00180 — RouteProfile
- 文件：`2605.00180-routeprofile.md`
- 角色：profile / representation layer
- 为什么重要：
  - 它直接服务 Track A 的关键问题：新增一个候选模型时怎么办
  - 我认为这是 Track A 最关键的“非 policy 层”论文

### D. 第二阶段：从选模型扩展到选预算

#### 2602.02823 — R2-Router
- 文件：`2602.02823-r2-router.md`
- 角色：joint `(model, budget)` router
- 为什么重要：
  - 它告诉你 Track A 的第二阶段动作空间应该长什么样
  - 不是只选模型，而是对 reasoning-heavy 请求连 budget 一起选

### E. 扩展系统思路

#### 2305.05176 — FrugalGPT
#### 2310.12963 — AutoMix
- 作用：提供 escalation / fallback / cascade 的系统直觉
- 对 Track A 的意义：
  - 不是第一版核心，但可以作为后续从静态 router 扩到多阶段系统的参考

## 3.3 Track A 的推荐阅读顺序

### 最小闭环顺序
1. Survey
2. RouterBench
3. RouteLLM
4. CARROT
5. RouteProfile

如果你只想先把 Track A 设计做出来，这 5 篇最关键。

### 完整顺序
6. IRT-Router
7. OptLLM
8. R2-Router
9. FrugalGPT
10. AutoMix

## 3.4 Track A 的设计结论

Track A 最后应该沉淀成这样一套系统图：

```text
query
  ↓
query encoder / difficulty features
  ↓
candidate model profile store
  ↓
cost-quality predictor
  ↓
routing policy
  ↓
model_id           (v1)
(model_id, budget) (v2)
```

在这个 track 里，最值得优先打磨的是：
- RouteProfile 对应的 profile layer
- CARROT / RouteLLM 对应的 policy layer
- RouterBench 对应的 evaluator

## 4. Track B：Coding Agentic Router for SWE-bench 该怎么看这些 paper

## 4.1 这个 track 的目标

Track B 不是问“给这个 query 选哪个模型”，而是问：

- 对一个 SWE-bench task，初始应该怎么启动 agent？
- 在 repo 理解、定位、写 patch、跑测试、反思、再尝试的过程中
- 每一步应该用什么 backbone、给多少预算、采用什么 execution mode、什么时候升级或回滚？

所以 Track B 的 router 本质上是：

`trajectory-state -> runtime-control action`

## 4.2 Track B 的核心论文分组

### A. Runtime architecture / workflow / granularity

#### 2604.14228 — Dive into Claude Code
- 文件：`2604.14228-agent-design-mechanism.md`
- 角色：runtime control plane substrate
- 为什么重要：
  - 它定义的不是某个局部 policy，而是 coding agent 底座怎么搭
  - 对 permission、compaction、session persistence、subagent delegation 特别关键

#### 2604.23626 — GraphPlanner
- 文件：`2604.23626-graphplanner.md`
- 角色：workflow-level multi-agent router
- 为什么重要：
  - 它最接近“agentic router”本体
  - 它把 routing 对象从 model 扩成了 workflow path 与 role/backbone selection

#### 2605.00410 — Agent Capsules
- 文件：`2605.00410-agent-capsules.md`
- 角色：execution granularity controller
- 为什么重要：
  - 对 SWE-bench 很关键，因为 coding agent 经常会遇到：到底是一步一步拆开执行，还是合并多个子步骤一起做
  - 它给了你 granularity routing 的直接设计灵感

- 相关总览：`papers/AGENTIC_COMPARISON.md`

### B. 在线 budget / compute controller

#### 2604.08369 — TrACE
- 文件：`2604.08369-trace-dont-overthink-it.md`
- 角色：cheap online uncertainty signal
- 为什么重要：
  - coding agent 很需要便宜的 runtime signal
  - rollout agreement 这种信号在 SWE-bench 环境里很可能比静态 difficulty classifier 更值钱

#### 2604.05164 — TAB
- 文件：`2604.05164-tab-turn-adaptive-budgets.md`
- 角色：turn-level budget controller
- 为什么重要：
  - 它适合映射到 coding agent 的 step-level compute budget 分配

#### 2408.03314 — Test-time Compute
- 文件：`2408.03314-test-time-compute.md`
- 角色：test-time compute 的总框架
- 为什么重要：
  - 给 Track B 的 budget controller 提供总理论背景

#### 2501.19393 — s1
- 文件：`2501.19393-s1.md`
- 角色：simple budget forcing baseline
- 为什么重要：
  - 提供非常简单但实用的预算控制思路
  - 很适合做 coding agent 里最初级的 budget baseline

#### 2602.02823 — R2-Router
- 文件：`2602.02823-r2-router.md`
- 角色：joint model + budget action
- 为什么重要：
  - 对 Track B 特别关键，因为 coding step 往往本来就需要同时决定 backbone 和 compute budget

### C. backbone selection 子模块

#### 2605.00180 — RouteProfile
#### 2502.03261 — CARROT
#### 2406.18665 — RouteLLM
#### 2506.01048 — IRT-Router
- 作用：它们不是 Track B 的完整系统，但非常适合拿来做 coding agent 中的 backbone router 子模块

### D. 系统控制启发

#### 2310.03046 — EcoAssistant
- 文件：`2310.03046-ecoassistant.md`
- 作用：提供 tool-using assistant system 和 past successful solutions retrieval 的启发
- 对 Track B 的价值：
  - 很像 coding agent 里的“历史解法检索 + 分层协作”

#### 2310.12963 — AutoMix
- 文件：`2310.12963-automix.md`
- 作用：提供 self-verification + escalation 思路
- 对 Track B 的价值：
  - 可迁移到 patch proposal 后的自验证/升级控制

#### 2305.05176 — FrugalGPT
- 文件：`2305.05176-frugalgpt.md`
- 作用：提供 cascade 省钱思路
- 对 Track B 的价值：
  - 适合作为最简单的 escalation baseline

## 4.3 Track B 的推荐阅读顺序

### 最小闭环顺序
1. GraphPlanner
2. Agent Capsules
3. TrACE
4. TAB
5. R2-Router
6. RouteProfile

这 6 篇最能直接支撑 SWE-bench coding agent runtime router。

### 完整顺序
7. EcoAssistant
8. CARROT
9. RouteLLM
10. IRT-Router
11. Test-time Compute
12. s1
13. AutoMix
14. FrugalGPT

## 4.4 Track B 的设计结论

Track B 最后应该沉淀成这样一套系统图：

```text
issue + repo metadata
  ↓
trajectory state encoder
  ↓
[backbone router]        -> 选当前 step 用哪个模型
[budget controller]      -> 选当前 step 给多少 compute
[workflow controller]    -> 选单 agent / 多 agent / role topology
[granularity controller] -> 选 fine-grained or compound execution
[recovery gate]          -> 选是否升级 / rollback / restart / branch
  ↓
execute next step
  ↓
observe tests / logs / agreement / patch outcome
  ↓
update state and repeat
```

Track B 最重要的不是某一篇 query router paper，而是把多篇论文的部件拼起来：
- GraphPlanner：workflow routing
- Agent Capsules：granularity routing
- TrACE / TAB / R2-Router：budget routing
- RouteProfile / CARROT / RouteLLM：backbone routing
- EcoAssistant / AutoMix：memory / recovery / escalation 启发

## 5. 哪些 paper 两个 track 都重要

有几篇是双栖核心：

### RouteProfile
- Track A：candidate model profile / cold-start layer 核心
- Track B：coding agent 中 backbone routing 的可扩展输入层核心

### CARROT
- Track A：multi-model cost-aware policy 核心
- Track B：可作为 coding step 的 backbone selector 子模块

### R2-Router
- Track A：第二阶段动作空间升级
- Track B：step-level `(model, budget)` 联合动作最直接的参考

### Survey
- Track A：帮助建立 benchmark router taxonomy
- Track B：帮助确认 workflow / cascade / uncertainty 这些思想也属于 routing 扩展空间

## 6. 如果只保留一个最小阅读集合

### 对 Track A（General Router）
- Survey
- RouterBench
- RouteLLM
- CARROT
- RouteProfile
- R2-Router

### 对 Track B（Coding Agentic Router）
- GraphPlanner
- Agent Capsules
- TrACE
- TAB
- R2-Router
- RouteProfile
- EcoAssistant

## 7. 仓库里的 paper 到底该怎么重新定位

## 7.1 更偏 Track A 的 paper
- RouteLLM
- CARROT
- IRT-Router
- OptLLM
- RouteProfile
- RouterBench
- Survey

## 7.2 更偏 Track B 的 paper
- GraphPlanner
- Agent Capsules
- TrACE
- TAB
- EcoAssistant

## 7.3 同时服务两个 track 的 bridge papers
- R2-Router
- AutoMix
- FrugalGPT
- Test-time Compute
- s1

这些 bridge papers 的价值在于：
- 它们帮助你把“选模型”过渡到“选预算 / 选流程 / 选执行模式”
- 是从 General Router 走向 Coding Agentic Router 的桥

## 8. 最后的设计建议

如果后面你真的开始做系统，我建议按下面顺序推进：

### Step 1：先完成 Track A
目标：
- 做出一个 benchmark-ready 的 general router
- 把 profile / policy / evaluator 三层打稳

建议 paper 组合：
- RouteLLM + CARROT + RouteProfile + RouterBench

### Step 2：把 Track A 的 backbone routing 能力迁移到 Track B
目标：
- 在 coding agent 里复用已有 backbone router
- 先别急着端到端统一训练

### Step 3：再加 Track B 的 runtime control
目标：
- 增加 step-level budget control
- 增加 workflow / granularity control
- 增加 recovery gate

建议 paper 组合：
- GraphPlanner + Agent Capsules + TrACE + TAB + R2-Router

## 9. 一句话结论

> Track A 要解决的是“对普通 query 选哪个模型 / 给多少预算”；Track B 要解决的是“在 SWE-bench agent 运行期间，何时用什么模型、给多少计算、采用什么执行结构、何时升级或回退”。
