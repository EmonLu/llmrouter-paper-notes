# Design Targets and Principles

这个文件不再只记录抽象原则，而是直接围绕你现在明确的两个最终 design target 来组织：

1. General Router
   - 目标：面向普通 benchmark / 普通 query 数据集的通用多模型路由器
   - 场景：MMLU、GSM8K、MT-Bench、Open QA、通用 reasoning / coding / math / knowledge 数据集
   - 关注点：质量-成本-延迟 trade-off、候选模型池扩展、新模型接入成本、offline evaluation

2. Coding Agentic Router for SWE-bench
   - 目标：面向 SWE-bench 一类仓库级软件修复任务，在 agent 执行期间进行 runtime routing
   - 场景：代码库理解、检索、补丁生成、测试、反思、回滚、再尝试
   - 关注点：step-level / turn-level / workflow-level routing，模型切换、预算分配、granularity control、trajectory escalation

这两个目标相关，但不要混成一个系统：
- General Router 更像“query → model / budget”的静态或半静态决策器
- Coding Agentic Router 更像“stateful agent runtime controller”，routing 对象不只是模型，还包括执行模式、思考预算、是否 split / merge agent、是否升级到更强模型或更长轨迹

## 1. 总体判断：为什么要拆成两个 design target

如果不拆，系统设计会很快变形：
- General Router 需要的是稳定、可比较、容易 benchmark 的 policy
- Coding Agentic Router 需要的是在线状态感知、trajectory 级别控制和失败恢复

二者最大的差异不在“候选模型不同”，而在：

### 1.1 Routing state 不同
- General Router：主要看 query、本地 profile、预算约束、模型价格 / 延迟 / 能力先验
- Coding Agentic Router：要看 repo state、子任务阶段、检索结果、测试反馈、patch 规模、历史失败轨迹、上下文剩余空间、当前已花预算

### 1.2 Routing action 不同
- General Router：通常输出 `选哪个模型`，最多再加 `给多少 budget`
- Coding Agentic Router：可能输出：
  - 选哪个 backbone
  - 当前 step 用单 agent 还是多 agent
  - 用 fine-grained 还是 compound execution
  - 是否继续 rollout / reflection / self-debug
  - 是否升级到更强模型
  - 是否转入测试、检索、总结、回滚等模式

### 1.3 Evaluation 不同
- General Router：可以靠 benchmark 上的 accuracy / cost / latency frontier 来评价
- Coding Agentic Router：必须看完整任务成功率、每条 trajectory 的 token / time / test pass 情况、平均修复轮数、失败模式

所以我的建议是：
- 共享底层能力层（profile、模型池元数据、budget accounting、memory schema）
- 上层 policy 拆成两套

## 2. Target A：General Router

## 2.1 目标定义

General Router 的目标不是做最复杂的系统，而是做一个：
- 面向通用 query 的多模型选择器
- 能处理普通 benchmark / 公开数据集
- 能在质量-成本-延迟之间做稳定 trade-off
- 能在新增模型时以较低成本扩展

它更接近：

`query -> representation/profile -> router policy -> (model, optional budget)`

而不是完整 agent workflow controller。

## 2.2 推荐的最小动作空间

第一版我建议只做两级动作空间：

### 版本 A1：只做模型选择
动作：
- `a = model_id`

适合先做：
- RouteLLM / CARROT / IRT-Router / OptLLM 风格系统
- 数据集驱动实验，容易和 RouterBench 对齐

### 版本 A2：模型选择 + 预算选择
动作：
- `a = (model_id, budget_level)`

适合在 A1 站稳后再做：
- R2-Router 风格系统
- 对 reasoning-heavy 数据集更有意义

我不建议一开始就做更复杂动作空间，否则 evaluation 会很难归因。

## 2.3 推荐的状态表示

General Router 的 state 建议只保留便于 benchmark 的信号：

- query text / query embedding
- task/domain tag（如果能拿到）
- profile-based model features
- 模型价格、延迟、context window 等 metadata
- 可选：简单 difficulty proxy
- 可选：全局 budget constraint

不建议一开始就接太多在线信号，否则会把 general router 变成弱化版 agent controller。

## 2.4 推荐系统分层

### Layer A1：Representation / Profile Layer
职责：给 query 和 candidate model 建一个可以泛化的共享表征层。

最相关论文：
- RouteProfile
- IRT-Router

设计启发：
- 不要把 router 只做成“query classifier”
- 要显式维护 candidate model profile
- 新模型接入时，优先争取通过 profile / metadata / 少量校准完成，而不是全量重训

### Layer A2：Policy Layer
职责：给定 query state，输出最合适的模型或 `(model, budget)`。

最相关论文：
- RouteLLM
- CARROT
- OptLLM
- IRT-Router
- R2-Router（如果做联合预算）

设计启发：
- RouteLLM 适合做 binary strong/weak baseline
- CARROT 适合做 multi-model cost-aware policy
- OptLLM 适合做显式 Pareto / constrained assignment
- IRT-Router 适合做可解释 query-model matching
- R2-Router 适合把动作空间从 model 扩展到 budget

### Layer A3：Evaluation Layer
职责：统一比较不同 router policy 的 cost-quality-latency frontier。

最相关论文：
- RouterBench
- Survey

设计启发：
- 一定要有 zero router / oracle / simple heuristic baseline
- 一定要把“平均准确率”变成“frontier”视角
- General Router 的 design 成败，很大程度取决于 evaluation 是否清楚

## 2.5 对这个 target 最重要的论文排序

### 第一梯队：必须读透
1. RouteLLM
2. CARROT
3. RouteProfile
4. RouterBench

### 第二梯队：决定你系统上限
5. IRT-Router
6. OptLLM
7. R2-Router

### 第三梯队：提供扩展思路
8. FrugalGPT
9. AutoMix
10. Survey

## 2.6 我建议的 General Router 第一版设计

### 第一版不要做什么
- 不要做多 agent workflow routing
- 不要做太复杂的在线 memory
- 不要把 rollout / reflection / test-time compute 全揉进去

### 第一版应该做什么
- 目标：一个可复现、可 benchmark、可比较的多模型 router
- 动作：先从 `model_id` 开始，后续再扩成 `(model_id, budget_level)`
- 候选模型池：控制在 4-8 个模型
- 核心模块：
  1. Query encoder
  2. Candidate model profile store
  3. Cost-quality predictor
  4. Routing policy
  5. Frontier evaluator

### 最值得直接借鉴的 paper 组合
- RouteLLM：做 baseline policy
- CARROT：做 multi-model risk objective
- RouteProfile：做 profile / cold-start layer
- RouterBench：做 evaluation protocol
- R2-Router：在第二版加入 budget action

## 2.7 这个 target 的核心 design 原则

### 原则 A1：先把 router 做成“选模型”，再做“选模型+预算”
如果一开始就把动作空间拉到 workflow 级别，会失去 benchmark 可解释性。

### 原则 A2：candidate model profile 是一等公民
General Router 要长期可扩展，profile layer 比换一个 classifier 更关键。

### 原则 A3：以 frontier 而不是单点 accuracy 为中心
如果不能清楚描述 cost-quality frontier，就很难判断 router 是否真的有价值。

### 原则 A4：新增模型接入成本必须被显式记录
每个设计都应该回答：新增一个候选模型时，需要重新训练多少、重标注多少、重跑多少 benchmark。

## 3. Target B：Coding Agentic Router for SWE-bench

## 3.1 目标定义

这个 target 不是一个普通 query router，而是：

- 在 SWE-bench 一类 repo-level bug fixing 任务里
- 让 agent 在执行过程中动态决定：
  - 当前该用哪个模型
  - 当前是否需要更长思考 / 更多 rollout
  - 当前是继续单 agent 还是切多 agent
  - 当前是否应该 merge / split 子流程
  - 当前是否该升级到更强模式或回退到更稳模式

也就是说，这个 router 更像：

`trajectory state -> runtime control action`

它是 online、stateful、multi-step 的控制器，而不是静态 query classifier。

## 3.2 为什么 SWE-bench 会逼出不同设计

SWE-bench 和普通 benchmark 最大差别在于：
- 任务不是一次性回答，而是一段 trajectory
- 中间会经过检索、理解 repo、定位 bug、写 patch、跑测试、根据报错修复
- 失败信息可以反馈到下一步 routing
- 成本不只是一次 LLM call，而是整条 agent 执行轨迹的累计消耗

所以这里的 router state 至少要覆盖：
- 当前任务阶段（理解 / 检索 / 修复 / 测试 / 反思）
- 当前 repo 状态
- 当前 patch 状态
- 当前测试状态
- 当前 trajectory 已花费 budget
- 最近几步是否反复失败
- 是否需要更强 reasoning、更多并行候选或更细粒度执行

## 3.3 建议的 routing 粒度

我建议 SWE-bench router 至少分三层：

### B1：Task-level routing
在任务开始时决定：
- 初始 backbone 是什么
- 总预算上限是多少
- 初始 workflow 走单 agent 还是多 agent

### B2：Step-level routing
在每个关键阶段决定：
- 当前 step 用哪个模型
- 要不要提高 reasoning budget
- 要不要切换成 retrieval-heavy / patch-heavy / test-heavy mode

### B3：Recovery / escalation routing
当出现失败信号时决定：
- 是否继续当前策略
- 是否 rollback
- 是否切更强模型
- 是否切更细粒度 agent
- 是否再开一个 verifier / reviewer / tester 角色

不要一开始做 token-level router；那样工程复杂度太高，且很难归因。

## 3.4 推荐的状态信号

Coding Agentic Router 的 state 应该显式包含：

### 静态信号
- repo 规模
- 语言 / 框架
- 测试数量
- issue 文本长度
- 可疑文件范围

### 动态信号
- 当前 step 类型：retrieve / inspect / patch / run tests / reflect
- 最近一次测试结果：通过数、失败数、错误类型
- patch 大小、patch 触及文件数
- 最近几步是否重复无效修改
- rollout 间方案一致性 / 分歧度
- 当前上下文窗口压力
- 当前累计 token / time / cost
- 历史同类任务的成功模式记忆

### 低成本置信度信号
- TrACE 风格的 inter-rollout agreement
- 测试通过率变化
- 检索到的证据是否一致
- patch 后报错是否从 syntax → semantic → edge-case 收敛

这些 cheap signal 对 SWE-bench 特别重要，因为它们可以在线更新。

## 3.5 推荐动作空间

我建议把 Coding Agentic Router 的动作拆成 4 类：

### Action B1：Backbone selection
- 选哪个模型做当前 step
- 适合借鉴：RouteLLM / CARROT / RouteProfile / R2-Router

### Action B2：Budget allocation
- 给当前 step 多少 reasoning budget / rollout budget
- 适合借鉴：TAB / TrACE / Test-time Compute / s1 / R2-Router

### Action B3：Workflow topology / role selection
- 当前要不要切多 agent
- 当前要不要引入 reviewer / tester / retriever / planner 角色
- 适合借鉴：GraphPlanner

### Action B4：Granularity / execution mode control
- 当前是 fine-grained sequential execution，还是 compound execution
- 当前是否 merge 某些子步骤
- 适合借鉴：Agent Capsules

如果你最后真做 SWE-bench router，我最建议的不是训练一个统一大 policy，而是把这四种动作分模块控制。

## 3.6 推荐系统分层

### Layer B1：Repository / Task State Encoder
职责：把 issue、repo、当前 trajectory 状态编码成 router 可用状态。

当前仓库最接近的启发来源：
- GraphPlanner（历史图记忆）
- EcoAssistant（工具使用 + past successful solutions）
- Agent Capsules（runtime telemetry）

### Layer B2：Backbone Router
职责：针对当前 step 选择最合适的模型。

最相关论文：
- RouteLLM
- CARROT
- RouteProfile
- IRT-Router
- R2-Router

这里它们不再是最终系统本体，而是成为 coding agent router 的一个子模块。

### Layer B3：Budget Controller
职责：决定当前 step 是否值得更长思考 / 更多 rollout / 更高 compute。

最相关论文：
- TAB
- TrACE
- Test-time Compute
- s1
- R2-Router

### Layer B4：Workflow Controller
职责：决定单 agent / 多 agent、role 分配、是否切 reviewer / tester / planner。

最相关论文：
- GraphPlanner
- EcoAssistant

### Layer B5：Execution Granularity Controller
职责：决定当前是细粒度逐步执行，还是将多个 agent / substep 合并执行。

最相关论文：
- Agent Capsules

### Layer B6：Memory / Recovery Layer
职责：记录失败模式、成功模式、相似 repo 经验，用于 recovery routing。

当前仓库没有 SWE-bench 专用 paper 来直接支撑这层，但：
- EcoAssistant 给了“历史成功解法检索”的方向
- GraphPlanner 给了图记忆方向
- TrACE 给了 cheap uncertainty signal

所以这一层属于你后续系统创新空间。

## 3.7 这个 target 最重要的论文排序

### 第一梯队：最接近系统本体
1. GraphPlanner
2. Agent Capsules
3. TrACE
4. TAB
5. R2-Router

### 第二梯队：做 backbone selection 子模块
6. RouteProfile
7. CARROT
8. RouteLLM
9. IRT-Router

### 第三梯队：做系统控制与恢复启发
10. EcoAssistant
11. AutoMix
12. Test-time Compute
13. s1
14. FrugalGPT

## 3.8 我建议的 SWE-bench Coding Agentic Router 第一版设计

### 第一版目标
不是直接做最复杂的 end-to-end learned policy，而是先做：
- 一个模块化 runtime controller
- 显式分成 backbone router + budget controller + workflow controller + recovery gate

### 第一版推荐的最小系统

#### 模块 1：Task initializer
输入：issue + repo metadata
输出：
- 初始 backbone
- 初始 token / time budget
- 是否启用 reviewer / tester role

#### 模块 2：Step router
输入：当前 step 状态
输出：
- 当前 backbone
- 当前思考 budget level
- 当前执行模式

#### 模块 3：Recovery gate
输入：测试失败、patch 无效、agreement 低、重复卡住
输出：
- 保持当前策略
- 增加 budget
- 切强模型
- 切 reviewer / tester
- rollback 并重开 trajectory branch

#### 模块 4：Memory store
记录：
- 哪类错误在哪种策略下容易修好
- 某 repo / 框架的历史高成功 workflow
- 某些 cheap signal 与成功率的关系

## 3.9 对这个 target 的关键判断

### 原则 B1：不要把 coding agent router 简化成 query router
SWE-bench 不是一次性问答；router 必须感知 trajectory。

### 原则 B2：先模块化，再考虑端到端学习
先把 backbone routing、budget routing、workflow routing、granularity routing 分开，才能知道收益来自哪里。

### 原则 B3：cheap online signals 非常关键
agreement、测试反馈、patch 失败模式，比离线训练出的静态 difficulty predictor 更有实战价值。

### 原则 B4：router 的动作不应只包含 model id
对于 coding agent，真正有价值的动作还包括：budget、mode、role、granularity、recovery。

### 原则 B5：SWE-bench target 的创新空间主要在“runtime control”
当前仓库里的论文多数不是直接针对 SWE-bench，因此你真正的研究空间不在 query routing，而在把 routing 扩展成 agent runtime control。

## 4. 两个 target 的关系：哪些模块共享，哪些模块分开

## 4.1 可以共享的层
- candidate model metadata / pricing / latency registry
- model profile layer
- backbone selector 的部分特征工程
- budget accounting
- 基础 calibration / evaluation tooling

## 4.2 必须分开的层
- state encoder
- action space
- evaluation protocol
- memory schema
- recovery logic

## 4.3 我的总体建议

### 先做什么
先做 General Router。

原因：
- easier to benchmark
- easier to build clean baselines
- 可以先把 model/profile/cost/budget 这些基础层做稳

### 再做什么
再做 Coding Agentic Router。

原因：
- 它会复用 General Router 的部分 backbone selection 能力
- 但真正难的是 runtime control，而这需要一个更成熟的系统框架

## 5. 最后沉淀成什么样的 repo 结构最合理

我建议后续把仓库设计理解成两个平行 design 方向：

### Track A：General Router Track
重点 paper：
- RouteLLM
- CARROT
- RouteProfile
- RouterBench
- IRT-Router
- OptLLM
- R2-Router

主要产出：
- benchmark-ready router design
- candidate model pool design
- profile / calibration strategy
- cost-quality frontier evaluation

### Track B：Coding Agentic Router Track
重点 paper：
- GraphPlanner
- Agent Capsules
- TrACE
- TAB
- R2-Router
- EcoAssistant
- RouteProfile

主要产出：
- runtime routing state schema
- step-level action space
- escalation / recovery policy
- workflow / granularity controller
- SWE-bench evaluation protocol

## 6. 一句话总纲

如果只保留一句设计总纲，我会写成：

> General Router 解决的是“对一个 query 选哪个模型 / 给多少预算”；Coding Agentic Router 解决的是“在一条 SWE-bench agent trajectory 里，何时用什么模型、给多少计算、采用什么 workflow 与执行粒度、何时升级或回退”。
