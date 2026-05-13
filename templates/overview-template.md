# LLM Router / Agentic Router 论文总览

## 1. 项目目标
这个仓库记录我围绕 `LLM Router / Agentic Router` 的论文精读笔记。

我的目标不是泛泛读论文，而是逐步沉淀出一个可实现的系统：
- 什么时候选哪个模型
- 什么时候增加或减少推理预算
- 什么时候切换 agent workflow
- 什么时候 split / merge 多 agent 执行粒度
- 什么时候基于 memory / 历史经验进行路由

## 2. 我的研究主线
当前主线：
- `[ ] Query / Task-level routing`
- `[ ] Turn-level budget routing`
- `[ ] Step-level uncertainty routing`
- `[ ] Workflow topology routing`
- `[ ] Multi-agent granularity control`
- `[ ] Memory-augmented routing`
- `[ ] Escalation / recovery routing`

## 3. 论文阅读地图
建议按“系统问题”组织，而不是按年份组织。

### A. Foundation
- RouteLLM
- FrugalGPT
- EcoAssistant
- AutoMix
- OptLLM
- RouterBench

### B. Agentic Router Core
- GraphPlanner
- TAB
- TrACE
- Agent Capsules
- Dynamic Model Routing and Cascading (Survey)

### C. Profiling / Preference / Calibration
- RouteProfile
- IRT-Router

### D. Inference-time Compute / Budgeting
- Test-time Compute
- s1

## 4. 当前论文清单
| 状态 | 论文简称 | 年份 | 主题 | 对我的价值 | 笔记链接 |
|---|---|---:|---|---|---|
| 未读 | Survey | 2026 | Routing taxonomy | 建立总框架 | `papers/xxxx-survey.md` |
| 未读 | TAB | 2026 | Turn budget routing | 预算分配 | `papers/xxxx-tab.md` |
| 未读 | GraphPlanner | 2026 | Agentic workflow routing | 工作流 + memory | `papers/xxxx-graphplanner.md` |
| 未读 | TrACE | 2026 | Adaptive compute | uncertainty gate | `papers/xxxx-trace.md` |
| 未读 | Agent Capsules | 2026 | Granularity control | split / merge runtime | `papers/xxxx-agent-capsules.md` |

## 5. 系统视角下的统一框架
我把未来的 agentic router 拆成以下几层：

### Layer 1: Task Intake Routing
- 判断任务类型、难度、是否需要 agentic workflow

### Layer 2: Workflow Topology Routing
- 决定单 agent、双阶段、多 agent、planner-executor-judge 等结构

### Layer 3: Model Routing
- 为不同 role / 不同步骤选择模型

### Layer 4: Budget Routing
- 为每个 turn / step 分配 token、rollout、思考预算

### Layer 5: Escalation / Recovery Routing
- 失败后决定是否升级模型、增加预算、切换 workflow

### Layer 6: Memory / Experience Routing
- 利用历史任务、历史轨迹、经验图谱做更好的 routing

## 6. 读完论文后统一更新的内容
每读完一篇论文，更新这里：

### 6.1 我新增确认的设计原则
- 原则 1：
- 原则 2：
- 原则 3：

### 6.2 我当前准备实现的模块
- `[ ] task classifier`
- `[ ] topology selector`
- `[ ] model selector`
- `[ ] budget allocator`
- `[ ] uncertainty gate`
- `[ ] escalation controller`
- `[ ] memory router`

### 6.3 当前最值得做的最小系统
- 系统名：
- 最小输入：
- 最小输出：
- 验证任务：
- baseline：

## 7. 横向对比表
| 论文 | 路由对象 | state | action | signal | objective | 适合哪一层 | 是否适合 agentic router |
|---|---|---|---|---|---|---|---|
| Survey | 多种 | - | - | - | taxonomy | 全局 | 是 |
| TAB | budget | history + budget | token budget | learned policy | accuracy-cost | L4 | 是 |
| GraphPlanner | workflow + role + model | query + graph memory | next role / model / workflow | memory + RL | performance-efficiency | L2/L6 | 非常适合 |
| TrACE | compute | rollout actions | more / stop | agreement | accuracy-compute | L4/L5 | 是 |
| Agent Capsules | granularity | runtime quality | merge / split / two-phase | quality gate | quality-cost | L2/L5 | 非常适合 |

## 8. 下一步阅读计划
### 必读
1. Survey
2. GraphPlanner
3. TAB
4. TrACE
5. Agent Capsules

### 备选补充
- RouteProfile
- IRT-Router
- RouterBench
- OptLLM

## 9. 仓库约定
- 每篇论文一个 md 文件
- 文件名统一：`papers/YYYY-paper-short-name.md`
- 总览页持续更新：`README.md`
- 如果一篇论文直接影响系统设计，要在 `design-principles.md` 里补一句原则

## 10. 当前结论（持续更新）
> 我最终想做的不是一个“只选模型的 router”，而是一个面向 agent workflow 的统一控制器：同时控制 model、budget、workflow、granularity、memory 和 escalation。
