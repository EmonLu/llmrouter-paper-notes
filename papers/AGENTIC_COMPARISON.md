# Coding-Agentic Router 跨论文对比

这份文件现在专门服务 `coding-agentic router` 设计。
它不再只回答“哪篇 paper 更像 agent work”，而是直接比较：
1. 它控制的是哪一层：task prior / workflow / granularity / budget / recovery / substrate / benchmark
2. 它看什么 state 信号
3. 它用什么决策机制
4. 数据或 benchmark 的规模、类别、构建方式是什么
5. 它的推理成本主要在哪里
6. 新模型或新 workflow 加进来时，代价高不高
7. 它适合直接复用什么，不适合照搬什么

## 1. 先给总图：Coding-Agentic Router 最终要分 6 层

### 1.1 runtime substrate
- Dive into Claude Code

### 1.2 task-level prior
- Triage

### 1.3 workflow controller
- GraphPlanner
- EcoAssistant（规则式、工具驱动）

### 1.4 granularity controller
- Agent Capsules

### 1.5 budget / adaptive compute controller
- TAB
- TrACE
- Test-time Compute
- s1

### 1.6 step-level evaluator / productized router
- TwinRouterBench
- UncommonRoute

## 2. Coding-agentic 核心论文横向总表

| 论文 / repo | 控制层 | 数据 / benchmark（体量、类别、构建方式） | 核心思想 | 输入信号 | 决策机制 | 推理成本 / 模型栈 | 新模型 / 新模式接入成本 | 优势 | 短板 |
|---|---|---|---|---|---|---|---|---|---|
| Dive into Claude Code | runtime substrate | 不是标准 benchmark；是对 Claude Code 公开源码快照 v2.1.88 的架构分析 | 真正复杂的不是 agent loop，而是 loop 外围的 permission、compaction、memory、subagent、resume/fork | 当前 query、工具结果、会话状态、CLAUDE.md、权限状态、历史 transcript | reactive query loop + permission system + hooks | 主执行模型是 Claude 系列；成本不在额外 router，而在整套 runtime 维护 | 中。换 backbone 不是最难，补权限/会话/工具语义才难 | 给你最像 production 的 coding-agent 底座 | 不是可直接训练的 routing policy；没有 step-level evaluator |
| Triage | task-level prior | SWE-bench Lite 300 tasks；3 个 tiers；每 task × tier 跑 3 次，多数表决；总 2700 agent runs 的 protocol | 利用 repo health / coverage / task metadata，在执行前先给 issue 一个 capability tier | issue 描述、目标文件 code-health、测试覆盖率、任务元数据 | heuristic / ML classifier / perfect-hindsight oracle | 输出 light/standard/heavy tier，不直接选具体模型；推理成本很低 | 中。若只换 tier 内代表模型较低，若 tier 边界变化要重新验证 pass/cost gate | 最适合当 coarse prior；解释性强 | 不是 step-level；唯一 recovery 只是 fail 后重跑 heavy |
| EcoAssistant | cheap-to-strong escalation + memory | Places/Weather/Stock 各 100；Mixed-100 等；通过 API tool-use + execution feedback 构造在线经验 | 先让便宜模型试，失败再升级；强模型成功轨迹沉淀成 future demonstrations | query、历史 demo、当前 assistant 层级、执行报错、会话历史、成功/失败信号 | 规则式 hierarchy + execution-driven retry + retrieval | 模型栈：LLaMA-2-13B / GPT-3.5 / GPT-4 + mpnet embedding + Chroma；成本主要花在多轮修复与升级 | 中。新增 API 域/模型要改 prompt、executor、evaluator、memory | 最贴近 tool-using runtime；memory/retrieval 很有启发 | 权限层很弱；恢复更像 restart+escalate，不是真正 checkpoint recovery |
| GraphPlanner | workflow controller | 14 个任务、6 个领域；大多 train/test 为 500/50；历史轨迹构成图记忆 | 直接路由整条 workflow，而不是只选模型；在每步联合选 role + backbone | query、当前 workflow graph、历史 memory graph、role set、candidate model set、cost utility | GARNet 图编码 + PPO | 候选 12 个 backbone，从 7B/8B/9B 到 70B/8x22B；训练成本主要在 RL 和图状态，而不是在线 router | 高。角色、图 schema、动作空间变化都可能要求重训 | 最接近“agentic router 本体” | 接入和训练成本高；工具环境不够重；显式 recovery 弱 |
| Agent Capsules | granularity controller | 4 条多 agent pipeline，5–14 agents；不是单一公共 benchmark，而是系统 benchmark | 控制“单 agent 调一次”还是“多个 agent 合并成 compound call” | topology、group 行为 fingerprint、rolling quality、telemetry、当前 mode | rule-based controller + quality gate + escalation ladder | 常见 backbone 是 Sonnet/Haiku，也补 GPT-4o/Gemini；成本主要在 evaluator 与 runtime telemetry，不在训练 | 中。新增 execution mode 要改 compiler/executor/evaluator | 对 token/latency 很直接；granularity action 很适合 coding agent | 强依赖 evaluator；不是模型层 router |
| TAB | turn-level budget controller | MATH-500、AMC23、MATH L5、OlympiadBench、AIME25；OOD 到 TheoremQA/BBEH-Mini/GPQA；训练用 MATH L5 | 把有限总预算分给真正关键的 turn，而不是平均分配 | 历史 trajectory、当前子问题、全局预算、可选预算桶 | GRPO-trained budget policy | 执行器 L1-Qwen3-8B-Exact；Budgeter 用 Qwen3-1.7B/4B；成本主要在训练 controller | 中到高。若从数学迁到 coding，需要重做状态与奖励 | step-level budget 思路非常直接可迁移 | 依赖子问题分解质量；工具环境外推仍有 gap |
| TrACE | cheap online budget gate | GSM8K 50 题 + MiniHouse 90 task-seed；training-free | 用多次 rollout 的 action agreement 当不确定性信号，决定是否继续采样 | 当前 prefix、候选动作集合、agreement、超参数 | training-free rule | Qwen2.5 3B Instruct + 无参数控制器；成本最低 | 中。控制器简单，但 action canonicalization 依赖接口 | 最容易先落地；几乎零训练 | agreement 高不代表动作对；对 code/tool action 需重做等价归并 |
| Test-time Compute | compute policy framework | 数学/推理 benchmark 为主；比较 parallel search vs sequential revision | 真正的动作不是只选模型，而是选 compute program | prompt、difficulty、budget、candidate traces、verifier score | heuristic difficulty-conditioned policy | 成本主要在更多 search/revision/verifier；不是轻量在线 router | 中。接入新模式主要是新 compute program，不是新模型 | 给 budget/action space 理论框架 | 不是 production runtime；权限/工具语义都没覆盖 |
| s1 | minimum continue-thinking primitive | s1K 1000 条高质量 reasoning 训练集；推理阶段主要是 budget forcing | 如果模型会基本 reasoning，就可通过 stop/continue forcing 提升性能 | 问题、当前 reasoning trace、最小/最大 thinking budget | generation-time hard rule | s1-32B 基于 Qwen2.5-32B-Instruct；成本直接体现在更长 thinking | 低。更多是 inner-loop primitive，而不是依赖候选池 | 最简单可复现的 compute 控制 primitive | 对真实 agent 过于简化；没有环境状态 |
| TwinRouterBench | step-level benchmark | 静态轨 970 rows / 520 trajectories / 5 benchmarks；动态轨支持 500-case SWE-bench Verified，论文报告 100-case held-out | 用 execution-verified label 把“当前 step 最便宜且足够的 tier”做成 benchmark | router-visible prefix：prompt、历史消息、tool output、logs、partial edits | benchmark 本身不绑定方法；代表 router 有 SR-KNN / UncommonRoute / rule-based 等 | 固定 11-model pool、4 tiers；成本主要在 benchmark label 构造和动态 replay | 高。改 model pool/tier/pricing 基本要重标或新版本化 | 终于把 step-level routing 说清楚，也给了 static+dynamic 闭环 | 强绑定当前模型生态快照；动态覆盖目前仍以 SWE 为主 |
| UncommonRoute repo | productized local router | 使用 TwinRouterBench 训练/校准/holdout 切分；产品化 control plane | 不只路由模型，还开始路由 protocol、budget cap、feedback overlay | metadata + structural + embedding + runtime-aware signals（step_type、has_tool_results、failure kind 等） | local ensemble router + calibration + policy layer | 依赖 sentence-transformers、xgboost、sklearn 等；成本主要在控制面和集成 | 中。新增上游模型、协议、预算策略需要改配置和再校准 | 最像“把 benchmark router 真落地”的工程参考 | 当前仍偏 product prototype，很多 policy 还在演化 |

## 3. Coding-agent 数据集 / benchmark 应该怎么汇总

### 3.1 你当前最该区分的三类资产
| 层 | 资产 | 当前可确认体量 / 备注 | 构建方式 | 主要用途 |
|---|---|---|---|---|
| benchmark | SWE-bench / SWE-Bench Pro / SWE-PolyBench / SWE-ContextBench | 当前综合阶段先保留 benchmark 角色划分，精确体量统一以各自单篇笔记为准 | benchmark-first evaluator | 验收与对外比较 |
| step-level benchmark | TwinRouterBench | 静态轨 970 rows / 520 trajectories；动态轨支持 500-case SWE Verified | 强模型成功轨迹 -> step prefix -> downgrade-and-verify -> cheapest sufficient tier | 训练/评估 step-level router |
| dataset / training asset | SWE-bench-train / Multi-SWE-RL / SWE-smith | 当前综合阶段先保留训练资产角色划分，精确体量统一以各自单篇笔记为准 | 同分布训练集、数据扩增、synthetic toolchain | 扩训练量与冷启动 |

### 3.2 现在最缺的不是“再多一个 benchmark 名字”，而是三种可训练信号
1. task-level 先验信号
   - repo health
   - test coverage
   - file-level complexity
   - issue metadata

2. step-level runtime signal
   - 当前 prefix
   - tool failure kind
   - 当前 patch / edit / test 状态
   - disagreement / retry history / stall pattern

3. recovery signal
   - 哪些失败值得加 budget
   - 哪些失败值得换 workflow
   - 哪些失败要直接升级 backbone 或 verifier

## 4. 按你最关心的几个问题给设计结论

### 4.1 哪些论文最适合回答“router 输入 state 应该长什么样？”
- Triage：任务开始前的 repo/static prior
- TwinRouterBench：执行时的 router-visible prefix
- EcoAssistant：tool error + retrieval + escalation state
- GraphPlanner：workflow state + memory graph
- Agent Capsules：telemetry + quality gate state
- TAB / TrACE：turn-level compute signal

结论：
Coding-agent router 至少需要两层 state：
- issue-level coarse prior
- step-level runtime state

### 4.2 哪些论文最适合回答“动作空间不能只是一组 model id”?
- GraphPlanner：role × backbone × workflow
- Agent Capsules：execution granularity
- TAB：budget bucket
- TrACE：continue sampling or stop
- TwinRouterBench / Triage：tier 而不是固定 model id
- UncommonRoute：甚至把 protocol / transport 也拉进动作空间

### 4.3 哪些方法最适合第一版落地？
- Triage：先做 issue-level coarse prior
- TrACE：先上 cheap online signal
- Agent Capsules：把 granularity 当可控变量
- TwinRouterBench-lite：用你自己的 mini-swe-agent 日志切 step prefix

### 4.4 哪些方法最容易变成长期维护负担？
- GraphPlanner：动作空间一变就可能重训
- TwinRouterBench：model pool 一变就重标
- EcoAssistant：memory 污染与 evaluator 误判
- Agent Capsules：若 evaluator 不稳，整个 quality gate 会漂

### 4.5 如果你要把 235B vs 397B 观察接进系统，最自然的接法是什么？
- Triage 风格：把 repo health / 任务静态特征接成 pre-run prior
- TwinRouterBench 风格：把 agent 轨迹切成 step prefix，标出“这一步 235B 是否已经足够”
- TrACE / TAB 风格：再判断失败是“模型能力不够”还是“预算/rollout 不够”
- Agent Capsules 风格：对某些模式失败，判断是否该改执行粒度而不是只换模型

## 5. 直接给一套最小系统蓝图

### Phase A：先做能跑的 version
- runtime substrate：Claude Code paper 的 while-loop + tool loop 思路
- task prior：Triage 式 repo health signal
- step signal：TwinRouterBench prefix schema + TrACE disagreement
- action：先只做 {small/large} × {normal budget/high budget}
- recovery：verification fail -> raise budget -> switch stronger model -> heavy fallback

### Phase B：再做更强的 version
- workflow：引入 GraphPlanner 式 role/backbone 联合动作
- granularity：引入 Agent Capsules 式 group mode
- memory：引入 EcoAssistant 式 solved-case retrieval，但存更细的 patch/test/tool trace
- benchmark：做 TwinRouterBench-lite + dynamic replay

## 6. 一句话结论

> Coding Agentic Router 不是把 query router 搬到 SWE-bench 上，而是把 `task prior + step prefix + budget + granularity + recovery + benchmark` 这六层拼起来；其中 TwinRouterBench 负责评测接口，Triage 负责起跑先验，TrACE/TAB 负责预算，Agent Capsules 负责粒度，EcoAssistant 负责 memory/recovery，GraphPlanner 决定长期上限。