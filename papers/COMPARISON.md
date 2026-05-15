# papers/COMPARISON

这个文件不是论文摘要，而是面向系统设计的横向对比表。

核心问题不是“哪篇 paper 更好”，而是：
- 它更适合支持 General Router 还是 Coding Agentic Router？
- 它解决的是哪一层 routing 问题？
- router 本体长什么样？
- 候选模型池怎么处理？
- 新模型接入成本高不高？
- 是否支持 online adaptation？
- 是否涉及 workflow / granularity / budget？

## 1. 先给一个总分层

可以把仓库里的论文按“最适合支撑哪一层系统”来粗分：

### 更适合 General Router
- RouteLLM
- CARROT
- IRT-Router
- OptLLM
- RouteProfile
- RouterBench
- Survey

### 更适合 Coding Agentic Router
- GraphPlanner
- Agent Capsules
- TrACE
- TAB
- EcoAssistant

### 两边都能桥接
- R2-Router
- AutoMix
- FrugalGPT
- Test-time Compute
- s1

## 2. 横向对比总表

| paper | 主要角色 | 更适合哪个 target | routing object | router 类型 | 是否训练 router | 候选模型池处理 | 新模型接入成本 | 是否 online | 是否 budget-aware | 是否 workflow-aware | 是否 granularity-aware | 我最看重的价值 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Survey | taxonomy / map | 两者都适合 | 方法空间 | 分析框架 | 否 | 总结式讨论 | 中 | 否 | 部分讨论 | 弱 | 弱 | 帮你定义问题边界 |
| RouterBench | benchmark | General Router | 评测对象 | benchmark / evaluator | 否 | 固定模型池 benchmark | 中 | 否 | 间接 | 否 | 否 | 提供统一比较坐标系 |
| RouteLLM | query router | General Router | model selection | preference router / win predictor | 是 | 强弱模型二元为主 | 中偏高 | 否 | 否 | 否 | 否 | 干净的 query-level baseline |
| OptLLM | query router | General Router | model selection | multi-objective optimizer | 是 | 多模型显式比较 | 中 | 否 | 部分 | 否 | 否 | 约束式 / Pareto 视角强 |
| CARROT | query router | General Router | model selection | cost-aware plug-in router | 是 | 多模型统一风险最小化 | 中 | 否 | 强 | 否 | 否 | 很适合长期 multi-model policy |
| IRT-Router | query router | General Router | model selection | latent ability matcher | 是 | 多模型能力/难度建模 | 中 | 否 | 强 | 否 | 否 | 可解释性与配对建模好 |
| RouteProfile | profile layer | 两者都适合 | model profile | profile / representation layer | 部分 | 重点研究 profile 组织 | 低到中 | 否 | 否 | 否 | 否 | 新模型接入与 cold-start 关键 |
| FrugalGPT | cascade | 桥接 | escalation / cascade | router + scorer + stop judge | 部分 | 固定多层级链 | 中 | 否 | 强 | 否 | 否 | 早期系统级 cascade 代表 |
| AutoMix | cascade | 桥接 | escalation / cascade | self-verification + POMDP | 是 | 多模型升级链 | 中 | 否 | 强 | 否 | 否 | black-box API 场景很实用 |
| EcoAssistant | system routing | Coding Agentic Router | assistant / execution strategy | hierarchy + retrieval + executor | 部分 | 更偏 assistant 角色组织 | 中 | 部分 | 间接 | 中 | 弱 | 离 agent runtime 很近 |
| Test-time Compute | adaptive compute | 桥接偏 Coding | compute allocation | search / revision / budget policy | 部分 | 单模型或少量模型 | 中 | 否 | 强 | 否 | 否 | 证明“算多久”本身是路由问题 |
| s1 | adaptive compute baseline | 桥接偏 Coding | reasoning budget | budget forcing | 否/弱训练 | 主要是单模型 | 低 | 否 | 强 | 否 | 否 | 简单 baseline 很有参考价值 |
| TAB | adaptive compute | Coding Agentic Router | turn-level budget | GRPO budget controller | 是 | 与模型选择解耦 | 中 | 否 | 强 | 中 | 否 | 很适合 step-level budget router |
| TrACE | adaptive compute signal | Coding Agentic Router | whether to continue compute | training-free agreement signal | 否 | 与模型池可解耦 | 低 | 在线可用 | 强 | 中 | 否 | cheap online signal 非常宝贵 |
| R2-Router | joint router | 两者都适合 | model + budget | reasoning-based joint router | 是 | 候选模型 × budget 联合动作 | 中 | 否 | 强 | 弱 | 否 | 是连接 Track A 和 B 的关键桥 |
| GraphPlanner | workflow router | Coding Agentic Router | agent role + backbone + workflow | graph-memory RL router | 是 | 多 agent + 多 backbone | 中到高 | 部分 | 中 | 强 | 弱 | 最接近 agentic router 本体 |
| Agent Capsules | runtime controller | Coding Agentic Router | execution granularity | quality-gated granularity controller | 部分 | 更偏执行模式而非模型池 | 中 | 在线可用 | 间接 | 强 | 强 | granularity routing 的关键启发 |

## 3. 关键维度展开比较

## 3.1 如果你问“哪几篇最适合做 General Router？”

首选：
1. RouteLLM
2. CARROT
3. RouteProfile
4. RouterBench
5. IRT-Router
6. OptLLM
7. R2-Router

原因：
- RouteLLM：给你最干净的 binary baseline
- CARROT：给你更一般的 multi-model cost-aware objective
- RouteProfile：解决长期扩展问题
- RouterBench：解决评测问题
- IRT-Router / OptLLM：分别补解释性和 constrained optimization
- R2-Router：第二阶段再加入 budget action

## 3.2 如果你问“哪几篇最适合做 Coding Agentic Router？”

首选：
1. GraphPlanner
2. Agent Capsules
3. TrACE
4. TAB
5. R2-Router
6. RouteProfile
7. EcoAssistant

原因：
- GraphPlanner：workflow routing
- Agent Capsules：granularity routing
- TrACE：cheap uncertainty / continuation signal
- TAB：step-level budget allocation
- R2-Router：joint model+budget
- RouteProfile：backbone routing 的可扩展输入层
- EcoAssistant：tool-using runtime system 启发

## 3.3 如果你问“哪几篇最适合当 bridge papers？”

### R2-Router
- 把 query router 与 budget router 接起来
- 是从 General Router 走向 Coding Agentic Router 的最自然桥梁

### AutoMix
- 把 single-shot route 变成 self-verification + escalation
- 是从 query-time policy 走向 multi-stage runtime control 的桥

### FrugalGPT
- 把 routing、quality estimation、stop judge 串起来
- 是系统级 control pipeline 的早期模板

### Test-time Compute / s1
- 把“选模型”问题扩展成“该不该继续算 / 算多久”
- 是 coding agent runtime budget control 的桥

## 4. 按几个最重要问题来对比

## 4.1 哪些论文最适合回答“新增模型时 router 代价有多大？”

最关键：
- RouteProfile
- IRT-Router
- CARROT（部分）
- R2-Router（部分）

最不适合直接回答：
- GraphPlanner
- Agent Capsules
- EcoAssistant

原因：
- 后三者更关注 runtime orchestration，不是 candidate model pool onboarding。

## 4.2 哪些论文最适合回答“线上是否能边跑边学？”

最关键：
- bandit / RL 路线（survey 中总结）
- TrACE（虽然不是 learning，但非常适合在线用）
- GraphPlanner（部分）

中等相关：
- Agent Capsules
- EcoAssistant

较弱：
- RouteLLM
- CARROT
- IRT-Router
- OptLLM

## 4.3 哪些论文最适合回答“routing 的动作应不应该只是一组选模型 ID？”

最关键：
- R2-Router
- TAB
- TrACE
- GraphPlanner
- Agent Capsules

这些论文共同说明：
- 动作可以是 budget
- 可以是 workflow role
- 可以是 execution granularity
- 可以是 escalation / continuation decision

## 4.4 哪些论文最接近你最后真正要做的系统？

如果按你的两个最终目标分开看：

### 对 General Router 最接近
- CARROT
- RouteProfile
- RouteLLM
- R2-Router

### 对 Coding Agentic Router 最接近
- GraphPlanner
- Agent Capsules
- TrACE
- TAB
- R2-Router
- EcoAssistant

## 5. 我对这些论文的最终定位

## 5.1 General Router 核心四件套
- RouteLLM：baseline policy
- CARROT：主 policy 方向
- RouteProfile：profile / expansion layer
- RouterBench：evaluation layer

## 5.2 Coding Agentic Router 核心四件套
- GraphPlanner：workflow controller
- Agent Capsules：granularity controller
- TrACE：cheap online signal
- TAB / R2-Router：budget controller

## 5.3 两条线共享的底层能力
- model metadata registry
- profile layer
- cost accounting
- budget accounting
- evaluation dashboard

## 6. 一句话结论

> 如果你要做 General Router，最重要的是“profile + policy + benchmark”；如果你要做 Coding Agentic Router，最重要的是“workflow + budget + granularity + recovery”，而不是把 query router 直接硬套到 SWE-bench 上。
