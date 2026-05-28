# Agent Capsules: Quality-Gated Granularity Control for Multi-Agent LLM Pipelines

## 1. 论文基本信息
> 先把元信息记全，方便回溯、引用和后续索引。

- 标题：Agent Capsules: Quality-Gated Granularity Control for Multi-Agent LLM Pipelines
- 作者 / 机构：Aninda Ray
- 发表时间：2026-05-01
- 会议 / 期刊 / arXiv：arXiv:2605.00410 [cs.CL]
- 论文链接：https://arxiv.org/abs/2605.00410
- 代码链接：https://github.com/aray-17/agent-capsules
- 项目链接 / 文档链接（如果有）：arXiv abs comments 指向 GitHub 仓库；仓库远程入口可验证
- 研究方向关键词：
  - `Agent Runtime`
  - `Granularity Control`
  - `Quality Gate`
  - `Compound Execution`
  - `Multi-Agent Pipeline`
  - `Runtime Controller`

## 2. 一句话总结
> 用一句话说明：这篇论文到底在研究哪个 agent 机制问题、提出了什么机制、带来了什么结果或设计价值。

- 总结：论文把多 agent pipeline 里“每个 agent 单独调一次模型”还是“多个 agent 合并成 compound call”视为一个运行时可控变量，提出由 composition score、quality gate 和 escalation ladder 组成的控制器，在质量底线约束下自动切换执行粒度，并在 14-agent LangGraph 与 5-agent DSPy 基线上分别拿到 42%~51% 和 19%~68% 的 token 节省，同时保持或提升质量。

## 3. 这篇论文到底在解决什么问题？
> 这一部分回答“为什么这个 agent 机制值得研究”。

### 3.1 核心问题是什么？
- 多 agent pipeline 默认是 N 个 agent 对应 N 次 LLM 调用，导致重复 prefill、重复 prompt、重复调度成本。
- 直觉上把多个 agent 合并成一次 compound call 能省 token，但会产生两类典型失败：
  - tool loss：合并后工具型 agent 失去显式工具调用结构
  - prompt compression：合并 prompt 后模型更倾向于浅层归纳，而非逐 agent 深度执行
- 因此核心问题是：什么时候值得合并、合并到什么粒度、质量掉了之后如何自动恢复。

### 3.2 为什么这个问题在 agent 系统里重要？
- 传统 router 主要路由模型；这篇论文路由的是 execution granularity。
- 在真实 agent 系统里，调用粒度往往比模型切换更直接影响 token 成本和吞吐。
- 对 coding agent router 来说，这意味着“选工作模式”可能和“选模型”一样重要，甚至更重要。

### 3.3 它主要在优化什么目标？
> 可多选：质量、成功率、成本、延迟、鲁棒性、可控性、可恢复性、可解释性、可扩展性、可观测性、安全性。

- 目标类型：成本、延迟、质量、可恢复性、部署可控性
- 我的理解：它不是简单追求省 token，而是追求“在质量底线约束下尽可能 aggressive 地省 token”。

### 3.4 它的控制对象到底是什么？
> 这一步很关键。不要只说“优化 agent”，而要说清楚它在控制哪一层。
>
> 常见对象：
> - model / backbone
> - reasoning budget
> - execution granularity
> - workflow structure
> - tool usage
> - memory read/write
> - delegation / subagent spawning
> - recovery / retry / rollback
> - permission / approval

- 控制对象：group execution mode / execution granularity
- 控制粒度：group-level，跨请求持续更新
- 我对其定位的判断：这是 runtime granularity controller，不是模型 router。

### 3.5 它更像哪一类工作？
> 可多选。

- `agent runtime architecture`
- `workflow controller`
- `granularity router`
- `budget controller`
- `observability / recovery framework`
- 我的判断：最像 granularity router + quality-gated runtime controller。

## 4. Agent Loop / Runtime Mechanism
> 这是 agentic paper 最核心的一部分。重点回答：系统到底怎么跑。

### 4.1 它提出的核心机制是什么？
- Agent Capsules 在现有 pipeline 外包一层运行时控制器，不改写开发者原有 agent 框架，而是把 group 作为 compound capsule 来管理。
- 三个核心部件：
  - composition score：预测某个 group 是否有合并机会
  - quality gate：约束 FINE→COMPOUND 切换与 COMPOUND→FINE 回退
  - escalation ladder：standard → two-phase → sequential 逐层升级，而不是一次失败就完全回到 FINE

### 4.1.1 核心直觉是什么？
> 用自己的话说明：作者到底利用了什么结构、状态、规则或反馈，来控制 agent 的运行。

- 直觉一：不是所有 group 都值得 compound，关键看该 group 在 FINE 模式下暴露出的行为 fingerprint。
- 直觉二：是否允许合并不能由静态规则拍脑袋决定，而要由滚动质量观测来 gate。
- 直觉三：compound execution 不是开或关，而是一条粒度连续谱；质量不够时，应该逐步升到更保守的 compound tier，而不是直接放弃全部收益。

### 4.1.2 整个 agent loop 按步骤是怎么运行的？
> 尽量写成 step-by-step。要能让未来你自己据此实现一个最小版本。

- Step 1：开发者声明 pipeline、group、agent、依赖和工具；运行时将每个 group 编译成 CompoundCapsule。
- Step 2：先在 FINE 模式运行，采集 coordination overhead、agent count、tool-call density、dependency depth 等行为信号。
- Step 3：根据这些信号计算 composition score；若超过 compose_at 且满足最小观测数与置信条件，则允许尝试 compound。
- Step 4：控制器按当前策略选择具体 mode：standard compound、two-phase compound 或 sequential compound。
- Step 5：执行该 group，并通过 evaluator 计算质量分、记录 token 与 latency。
- Step 6：若 shadow-evaluated quality 低于 quality_floor，则阻止 FINE→COMPOUND 切换；若 rolling mean quality 低于 floor，则回退或升级模式。
- Step 7：如果某个 compound tier 失败，则通过 escalation ladder 向更保守的执行模式升级；如果仍失败，再 hard revert 到 FINE，并重置相关窗口。
- Step 8：将 telemetry 留给后续请求使用，因此控制器是跨请求持续演化的。

### 4.1.3 如果把它压缩成一个决策流 / 伪代码，它长什么样？
- 可以写成：
  - observe group in FINE
  - score = composition_score(signals)
  - if score < compose_at: run FINE
  - else:
    - try current_compound_tier
    - q = evaluate(output)
    - if q >= quality_floor: keep / maybe de-escalate later
    - else if ladder_enabled: escalate to safer compound tier
    - else: revert to FINE
- 其中关键不在 learned policy，而在“观测-评分-门控-升级”的闭环。

### 4.2 runtime 的输入 state 是什么？
> 不要只写“prompt”。要写清楚系统运行时实际依赖哪些状态。
>
> 例如：
> - task metadata
> - 当前 step type
> - 工具结果摘要
> - patch state
> - test state
> - 当前预算
> - 历史失败次数
> - context pressure
> - memory / session state

- 输入 state：
  - pipeline topology
  - group 内 agent 数、依赖深度、工具调用密度
  - FINE 模式下测得的 coordination overhead
  - 当前 group 的 execution mode
  - 最近窗口内质量分数 rolling mean
  - compose_at / decompose_at / confidence / minimum observations / quality_floor
  - 当前 provider / model 行为特征
  - 历史 mode switch 记录与 revert 状态

### 4.3 runtime 的输出 action 是什么？
> 例如：
> - 调哪个模型
> - 分配多少 budget
> - 是否调用工具
> - 是否压缩上下文
> - 是否写入 memory
> - 是否 spawn subagent
> - 是否 rollback / retry / escalate / terminate

- 输出 action：
  - FINE / standard compound / two-phase compound / sequential compound 模式选择
  - 是否 FINE→COMPOUND 切换
  - 是否升级到更保守 compound tier
  - 是否 revert 回 FINE
  - 是否启用 concise output guidance、predecessor-only context injection 等提示策略

### 4.4 决策是怎么产生的？
> 例如：规则、有限状态机、打分器、policy、verifier、gate、LLM-as-controller、混合控制器。

- 决策机制：规则 + behavioral score + quality gate + escalation ladder
- 是否训练：`否`
- 如果训练，训练数据是什么：无
- 训练目标是什么：无

### 4.5 这个控制回路是单步的还是跨轨迹持续更新的？
> 区分：
> - 单次调用内控制
> - 单条 trajectory 内多步控制
> - 跨请求 / 跨会话在线更新

- 控制范围：跨请求持续更新
- 我的理解：控制器根据一个 group 最近多次运行的观测结果来决定后续请求的 execution mode，因此是典型 deployment-time adaptive controller。

### 4.6 这套机制最依赖哪些关键信号？
> 例如：测试反馈、verifier 分数、tool success、上下文拥塞、用户批准、历史 telemetry、agreement / disagreement。

- composition score 四个行为信号：coordination overhead、agent count、tool-call density、dependency depth
- evaluator 给出的质量分数
- rolling mean quality 与 threshold crossing
- 不同 mode 下的 token / latency telemetry

### 4.7 这套机制最容易失败在哪一步？
> 帮助你识别 failure mode，而不是只看 paper 的“主线成功故事”。

- standard compound 最容易因 prompt compression 失败。
- tool-heavy group 容易因 merged call 失去工具行为而失败。
- 如果 quality evaluator 不稳定，rolling gate 会被噪声拖动。
- 对非常弱的基础模型，即使 score 高也可能永远无法跨过 quality floor，只能停留在 FINE。

## 5. Context / State / Memory Management
> 这部分是普通 routing 模板里缺失、但 agent 机制论文里非常关键的内容。

### 5.1 系统如何表示当前状态？
> 是 message history、structured state、graph、scratchpad、capsule、trajectory record，还是别的形式？

- 状态表示：以 group 为单位的结构化 runtime state，包括 telemetry、policy、quality history 和 mode state；执行单元叫 CompoundCapsule
- 是否结构化：`是`
- 我对这种表示的理解：它把 multi-agent pipeline 从“prompt 串”提升为“可观测 group state”。

### 5.2 Context 是如何组织的？
> 例如：
> - 纯对话历史
> - role-based prompt assembly
> - tool result summary
> - topology-aware context injection
> - selective retrieval
> - 分层上下文

- 上下文组织方式：根据 pipeline topology 做 group 级 prompt assembly，并支持 sequential compound 下的 predecessor-only context injection
- 上下文来源：group 内 agent prompt、依赖输出、工具结果、policy 配置、output guidance
- 对成本 / 质量的影响：作者明确证明“更多上下文塞进 merged prompt”并不能解决 compression，反而可能更糟，因此 context organization 本身就是性能关键。

### 5.3 是否讨论了 context compaction / summarization / truncation？
- 是否支持：`部分支持`
- 具体怎么做：不是通用会话 compaction，而是通过 compound mode、predecessor-only context injection、concise output guidance 来控制每层上下文与输出规模
- compaction 触发条件：进入 sequential / merged execution 时按 mode 注入不同上下文粒度
- 潜在风险：过度压缩会伤害质量，尤其在 reasoning-heavy 或 tool-heavy group 上最明显

### 5.4 是否有 memory 机制？
> 例如：短期 memory、长期 memory、session storage、经验缓存、历史解法库。

- 是否有 memory：`有，但不是传统记忆系统`
- memory 类型：controller observations、rolling quality history、composition score window
- 读写时机：每次 group 执行后写入；下一次 mode decision 前读取
- 写入内容：tokens、latency、quality、score、mode switch 结果
- 检索方式：按 group / pipeline 读取最近窗口
- 我对其价值的判断：这是 deployment telemetry memory，而非知识记忆，但对运行时控制非常关键。

### 5.5 是否有 session persistence / artifact persistence？
> 例如：日志、状态快照、patch、计划、工具输出是否能在下一轮恢复。

- 是否持久化：`是，支持持久化 controller state`
- 持久化对象：observations、quality history、controller state
- 恢复方式：默认内存态重启即丢；生产环境可接 Redis backend，在多 worker 间共享状态并跨重启保留
- 对 recovery 的意义：避免每个 worker 都从零校准，支持分布式一致切换决策

### 5.6 如果上下文爆掉、会话中断或执行被打断，系统怎么恢复？
- 论文主要关心的是执行模式恢复，而不是长会话中断恢复。
- 质量下降后，系统先 escalates 到更保守 compound tier；若仍不达标则 revert 到 FINE，并重新积累 fresh FINE observations。
- 如果运行时重启，若只用内存 backend 则控制器状态丢失；若用 Redis backend 则可恢复共享历史。

## 6. Tool Use / Environment Interaction
> 这部分回答 agent 如何真正接触外部世界。

### 6.1 系统能调用哪些工具 / 环境？
- 论文本身不是通用工具框架，而是包裹现有 multi-agent pipeline。
- 所以它继承底层 pipeline 的工具环境；文中重点讨论 research / code-review / due-diligence 等 group 中的工具型 agent。

### 6.2 工具调用的语义是什么？
> 例如：
> - LLM 直接生成 tool call
> - planner 先决定，再由 executor 调
> - 工具结果回填到主上下文
> - 工具输出经过摘要 / 过滤后再注入

- 工具调用方式：取决于底层 agent framework；Agent Capsules 自己不重定义 tool API，而是控制“几个 agent 是否合并执行”。
- 工具结果回流方式：在 compound 设计里有显著差异：
  - standard compound：合并调用，最容易丢失显式工具使用
  - two-phase compound：先在 Phase A 恢复部分工具 / reasoning 行为，再做合并
  - sequential compound：保留更强的逐 agent 执行语义，因此最稳
- 我的理解：它本质上是在“工具语义保真度”和“token 节省”之间寻找安全点。

### 6.3 工具执行有哪些边界？
> 例如：是否有 sandbox、文件系统边界、网络边界、命令执行边界。

- 环境边界：主要由被包裹的 LangGraph / DSPy / 自定义 pipeline 决定
- 隔离方式：论文未提出新的 sandbox 机制
- 权限范围：论文未设计新的 permission system

### 6.4 是否有 permission / approval / safety model？
> 这是 agentic paper 非常关键的一栏。

- 是否有权限系统：`否，重点不是安全审批`
- 权限粒度：未单独设计
- 是否需要用户确认：未强调
- 哪些动作需要确认：未强调
- 自动允许的动作：由底层框架决定
- 自动拒绝或升级的动作：这里的“升级”是 execution mode escalation，不是安全审批升级
- 我的理解：它的 safety 更接近 quality safety，而不是操作安全。

### 6.5 系统如何处理 tool failure / environment failure？
- two-phase mode 专门针对 tool loss 这一 failure mode。
- ladder 让 standard compound 失败后可以升级为 two-phase 或 sequential，以结构性恢复工具语义。
- 论文没有专门设计 OS / network failure handling，而是聚焦 execution-mode recovery。

## 7. Orchestration / Subagents / Human-in-the-loop
> 这部分回答“系统是不是单 agent”“多个 agent 如何协作”“人类在什么位置做决定”。

### 7.1 系统是单 agent 还是多 agent？
- 类型：多 agent pipeline 外挂控制器
- 角色划分：原始 pipeline 中已有多个 agent；Agent Capsules 不新增角色，而是重新组织这些 agent 的执行粒度
- 为什么这样设计：作者想最小侵入地提升已有多 agent 系统效率

### 7.2 是否支持 subagent / delegation？
- 是否支持：`不直接新增 subagent 机制`
- 谁负责发起 delegation：底层 pipeline
- subagent 的输入是什么：由底层 pipeline 决定
- subagent 的输出如何汇总：由 compound mode 决定其如何被合并或顺序串联
- 代价 / 风险是什么：合并越激进，越容易丢掉 agent 分工与工具行为

### 7.3 多 agent / 多模块之间是怎么通信的？
> 例如：共享上下文、消息传递、结构化状态、artifact handoff、graph edge。

- 通信方式：group 内 agent 通过 compound prompt、两阶段中间结果或 sequential predecessor context 交互
- 是否共享同一上下文：`部分共享，且共享程度取决于 mode`
- 是否存在局部私有状态：`有，尤其 sequential 模式更接近局部状态推进`
- 我的理解：mode 变化本质上就是改变通信拓扑和共享上下文的强度。

### 7.4 人类在回路中的位置是什么？
> 例如：批准者、监督者、终止者、纠偏者、只在高风险动作时介入。

- human-in-the-loop 角色：主要是 cloud operator / pipeline deployer，而不是逐次审批者
- 介入时机：设置 quality_floor、选择 sensitivity preset、按 group 覆盖 policy
- 介入信号：质量要求、客户分层、业务 SLA
- 如果没有人类介入会怎样：系统仍能自动切换，但 quality floor 等部署参数需要提前定义

### 7.5 如果把这个系统迁移到 coding agent 场景，哪些协作机制最值得保留？
- execution mode 作为一等路由对象
- per-group telemetry 驱动的自动 mode switch
- “失败后升级到更保守协作模式”而不是直接崩回单 agent

## 8. Extensibility / Integration / Engineering Cost
> 这部分比“新增候选模型成本”更重要：你更关心新工具、新角色、新控制器怎么接入。

### 8.1 系统包含哪些关键模块？
- CompoundCapsule / compiler
- executor
- composition scorer
- quality gate
- escalation ladder
- ControllerPolicy
- evaluator
- telemetry / state store
- provider adapters

### 8.2 是否支持插件化 / MCP / provider adapter / tool registry？
- 是否支持：`是，支持 provider adapter 与策略注入`
- 扩展点在哪里：ControllerPolicy、QualityEvaluator、state backend、provider adapter、per-group policy override
- 新增一个 tool / provider / module 需要做什么：
  - 新 provider：接一个 adapter
  - 新 evaluator：实现 QualityEvaluator protocol
  - 新持久化：替换 store backend
  - 新 group 策略：传入完整 ControllerPolicy override

### 8.3 如果要新增一个 agent role / tool / workflow mode，系统代价有多大？
- 新增对象：group policy、evaluator、backend、execution mode
- 是否需要改 prompt：通常需要，尤其新增新的 compound mode 时
- 是否需要改 controller：若仅调阈值不需要；若新增 mode 需要
- 是否需要新增 state 字段：大概率需要补 telemetry 字段
- 是否需要新增评测：需要，尤其 quality ceiling 和 token-saving 曲线
- 我判断的接入成本：中
- 原因：系统本身不重，但新增 execution mode 要同时改 compiler、executor、evaluator 与 benchmark。

### 8.4 系统最强的工程设计点是什么？
- 把所有优化行为收敛到一个 ControllerPolicy 接口，非常适合部署。
- 它不是重新发明 agent framework，而是提供一个可套在外侧的 runtime layer。

### 8.5 系统最脆弱的工程点是什么？
- 对 evaluator 质量依赖很高，quality floor 一旦失真，整个 gate 都会偏。
- composition score 是行为 fingerprint，不是能力预测，部署者需要理解其适用边界。
- 过多 preset / override / per-group 策略组合后也会增加调参复杂度。

## 9. Observability / Debuggability / Recovery
> 这部分很像真实系统设计文档里必须有、但论文常常写不全的内容。

### 9.1 系统是否暴露 runtime telemetry？
> 例如：token、latency、tool success、trajectory status、failure reason、quality score。

- 是否可观测：`是`
- 观测指标：token、latency、quality、composition score、mode status、rolling mean、switch observations
- 这些指标对控制器有什么用：composition score 决定是否触发 compound，quality gate 决定是否允许或维持 compound，latency / token 则用于部署权衡。

### 9.2 是否能解释“为什么做出这次控制决策”？
- 是否支持：`是`
- 解释方式：看 compose_at 阈值、rolling quality 是否过 floor、当前 ladder tier、最近观测窗口
- 对调试的价值：很高，因为它不是黑箱 learned policy，而是可直接用 telemetry 解释

### 9.3 是否有 recovery / rollback / retry / escalation 机制？
- 是否有：`是`
- recovery 动作有哪些：shadow gate 阻止不安全切换、rolling revert、standard→two-phase→sequential escalation、hard revert to FINE
- 触发条件：shadow quality 低于 floor，或 rolling mean quality 低于 floor
- 哪种恢复最关键：escalation ladder，因为它让 compound execution 变成可部署的渐进机制，而非一次性赌博

### 9.4 这套系统最主要的 failure modes 是什么？
- Failure mode 1：tool-heavy group 在 standard compound 下发生 tool loss。
- Failure mode 2：reasoning-heavy group 在 merged prompt 下发生 compression fail。
- Failure mode 3：judge 噪声导致不稳定 switch，需要 rolling window 来抑制。

### 9.5 如果要把它落到 SWE-bench agent runtime，它最值得先保留哪三类 telemetry？
- group-level composition score
- rolling quality floor status
- per-mode token / latency / revert history

## 10. 实验设置
> 记录实验是否真的能支撑它的系统主张。

### 10.1 使用了哪些任务 / benchmark？
- 论文不是公共 benchmark 论文，而是系统 benchmark：四条多 agent pipeline、5–14 agents、覆盖多种拓扑
- 主要 pipeline：
  - 5-agent due diligence
  - 6-agent code review
  - 8-agent long-chain research
  - 14-agent competitive intelligence
- 表 15 将它们整理为 P-1 到 P-4，并固定 pipeline 定义进行跨模型比较

### 10.1.1 这些任务到底在测什么？
> 不要只抄名字，要写清楚它们是在测 agent loop、tool use、code repair、planning、long-horizon execution，还是别的能力。

- 任务来源：作者自建多 agent pipeline benchmark，领域主要是 fintech 和 software engineering
- 样本形式：不同 topology 的 group / agent / tools 组合
- 评价目标：测 execution granularity 控制能否在多 agent tool-using pipeline 中稳定省 token 而不掉质量
- 与真实 agent 场景的接近程度：较高，尤其对工程侧 pipeline 优化非常贴近

### 10.2 对比了哪些 baseline？
- 手工调优 LangGraph 实现
- DSPy 实现
- DSPy + MIPROv2 compile-time optimization
- 内部 mode 对比：FINE / standard / two-phase / sequential

### 10.3 使用了哪些模型？
> 这里关注的是 backbone / judge / verifier / controller 各自用什么，而不是普通 routing 模板里的“候选模型池”。

- 主执行模型：Sonnet、Haiku 为核心；另有 GPT-4o、GPT-4o-mini、Gemini-2.5-flash-lite、Gemini-2.5-pro 用于补充验证
- 控制器 / router / gate：启发式控制器，不训练
- judge / verifier：Anthropic 侧主要用 claude-opus-4-6；OpenAI / Google 侧主要用 gpt-4o；框架还支持 LLMJudgeEvaluator、SchemaComplianceEvaluator、ConsistencyEvaluator
- tool model / embedding model（如果有）：无专门 embedding 模型
- 我的理解：论文最核心结论主要来自 Sonnet / Haiku，跨 provider 结果更多用于说明 score 行为的稳定性。

### 10.4 主要评估指标是什么？
> 例如：task success、quality、token、latency、tool success rate、rollback rate、recovery rate、human approval burden。

- LLM-judged quality
- input / output tokens
- wall-clock latency
- composition score
- quality floor pass/fail
- oracle agreement

### 10.4.1 每个指标分别在衡量什么？
- 指标 A：quality
  - 衡量含义：compound mode 是否保持任务输出质量
  - 高/低分别意味着：高表示可安全部署；低表示需要 revert 或 escalate
  - 对系统设计的启发：粒度优化必须带 hard quality floor，而不是只看 token
- 指标 B：token
  - 衡量含义：重复 prefill、重复 prompt、输出冗余是否被减少
  - 高/低分别意味着：越低越说明 granularity control 有效
  - 对系统设计的启发：粒度路由的直接收益首先体现在 token
- 指标 C：latency
  - 衡量含义：减少调度与串行等待后是否更快
  - 高/低分别意味着：更低说明 compound 对吞吐有帮助，但并非所有 group 都会降
  - 对系统设计的启发：单 agent group 不一定适合 compound

### 10.4.2 这些指标有没有盲点？
- quality 主要依赖 LLM judge，不是人工大规模标注。
- benchmark 域仍有限，特别是 group size 大多在 1–4 agents per group。
- 缺少 GPU 级系统指标，如 cache 压力、MFU 等。

## 11. 核心结果
> 只记录最重要的结论，不要机械抄表。

### 11.1 最重要的实验结果是什么？
- 对 14-agent LangGraph competitive intelligence pipeline：
  - fine-mode input tokens 降 `51%`
  - compound-mode input tokens 降 `42%`
  - 质量分别 `+0.020` 与 `+0.017`
- 对 5-agent DSPy due diligence pipeline：
  - 相比未编译 DSPy，token 降 `19%`，质量基本持平
  - 相比 MIPROv2，token 降 `68%`，质量 `+0.052`
- sequential compound + adaptive output guidance 在 Sonnet / Haiku 上带来 `63%~64%` 的 output-token savings；某些配置下可到 `85.5%`
- rolling window 饱和后，控制器在测得 cell 上与 hand-tuned oracle 决策一致
- escalation ladder 在 code-review review group 上把质量从 `0.313 ± 0.137` 提到 `0.724 ± 0.068`，同时 token 下降约 10%

### 11.2 相比 baseline，它真正提升了什么？
- 相比 LangGraph：即使不进入 compound，仅靠 topology-aware context injection、policy resolution、cache-aligned prompts 就有收益。
- 相比 DSPy / MIPROv2：运行时自适应在没有训练数据的情况下达到甚至超过 compile-time 优化。
- 相比 naive merged prompting：它把 compound execution 变成可观测、可门控、可回退的默认能力。

### 11.3 它是在质量、成本、延迟、成功率、可控性里的哪几个维度上真正成立？
- 真正成立的维度：成本、延迟、部署可控性、恢复能力
- 在质量维度上也成立，但前提是 quality gate 与 ladder 同时存在
- 不是单纯“更省”或“更快”，而是给出了一条可部署的 Pareto 曲线

### 11.4 有哪些 ablation / sensitivity / negative results？
- composition score 信号与权重分析
- mode 对比：standard / two-phase / sequential
- sensitivity preset：aggressive / balanced / conservative
- prompt-engineering 变体：concise output guidance、predecessor-only context injection
- 关键负结果：给 merged call 注入更多 context 不能消除 compression，反而会恶化
- quality ceiling heatmap 表明并非所有模型都适合 compound；Haiku 在 floor=0.75 下基本被 gate 回 FINE

### 11.5 这些结果真正说明它擅长解决什么问题？
- 擅长解决“多 agent pipeline 如何在不大改原框架的前提下降 token / 延迟”的问题。
- 特别适合工具型、链式、group 化明显的 pipeline 运行时优化。

### 11.6 这些结果没有证明什么？
> 这一栏很重要，防止把 paper 的结论扩大化。

- 没有证明它适用于所有 agent 框架和所有业务域。
- 没有证明 quality floor=0.75 是普适阈值；作者明确把它当作部署参数。
- 没有证明它优于 learned workflow router；它解决的是另一层问题。

## 12. 可复现性 / 资源开放 / 落地难度
> 这部分继续保持你的高强度精修标准。

### 12.1 代码、数据、配置、日志是否公开？
- 代码是否开源：是，GitHub 仓库入口可验证
- 数据 / benchmark 是否公开：部分公开。pipeline 结构、policy、协议、表格很详细；但 benchmark 样本、judge 缓存与所有运行记录是否齐全，本文档未逐项验证到公开下载入口
- 配置 / prompt / workflow 定义是否公开：大部分公开，尤其 ControllerPolicy、sensitivity preset、per-group override、evaluator 注入接口都写得很细
- 运行日志 / telemetry / traces 是否公开：未验证到完整公开入口

### 12.2 实现细节是否写清楚了？
> 例如：
> - loop 的状态转移
> - prompt assembly
> - permission policy
> - tool schema
> - memory 写入规则
> - rollback / escalation 触发条件

- 清晰度判断：清楚
- 缺失点：
  - 各 provider adapter 的实现差异未完全展开
  - benchmark 样本与仓库目录布局细节未完全验证
- 我的判断：复现控制器本身不难，完整复现论文所有 head-to-head 流水线仍有工程成本。

### 12.3 真正落地它，工程难点在哪里？
- 需要可靠 evaluator，否则 quality gate 不稳。
- 需要给不同 group 做 policy 校准，尤其 quality_floor 与 compose_at。
- 需要把底层 agent framework 的真实工具语义和 telemetry 暴露出来，否则 composition score 不可用。

## 13. 对 Coding Agentic Router 的直接启发
> 这是这个模板相对普通论文模板最重要的一部分。

### 13.1 对我的 coding agent runtime controller，最值得借鉴的部件是什么？
> 例如：
> - state encoder
> - recovery gate
> - permission system
> - compaction policy
> - subagent orchestration
> - telemetry schema

- group-level composition score，把执行粒度变成可观测控制对象
- rolling quality gate，避免一次坏样本引发剧烈切换
- escalation ladder，把失败恢复做成 tiered fallback 而非二元开关
- Redis 共享 controller state，适合多 worker coding agent 部署

### 13.2 哪些东西值得借鉴，但不该原样照搬？
- composition score 的具体四个信号很有启发，但对 coding agent 还应加入 test feedback、patch churn、tool failure ratio 等编码场景信号。
- LLM-judge quality 可借鉴，但 coding agent 应优先引入可执行验证器，如 tests / lint / static analysis。

### 13.3 如果把这篇 paper 映射到 SWE-bench 轨迹，它更像控制哪个层？
> 例如：
> - backbone router
> - budget controller
> - workflow controller
> - granularity controller
> - recovery controller
> - memory manager
> - tool policy layer

- `granularity controller`
- `workflow controller`
- `recovery controller`
- 我的判断：它最适合作为 coding agent 中“单 agent 执行、双 agent 讨论、swarm 并行、sequential handoff”之间的运行时切换层。

### 13.4 它对下面哪些问题最有帮助？
- backbone 选择：中等，可与 model routing 组合
- budget 分配：很强
- workflow 切换：很强
- granularity 控制：极强
- recovery / retry / rollback：很强
- memory / context compaction：中等，主要是 mode-level context injection
- tool use / permission：中等，主要体现为 tool-loss-aware mode 设计
- observability / debugging：很强

### 13.5 读完后，我会把它放进哪条设计主线？
- `General Router`
- `Coding Agentic Router`
- `Bridge Paper`
- 我的判断：`Bridge Paper`

## 14. 横向比较位置
> 方便后面做 agentic 组的 comparison / index。

### 14.1 和已有哪几篇最像？
- 和将 execution mode 当成控制对象的 runtime controller 论文最像。
- 在这组三篇里，它和 GraphPlanner 都是在做 workflow 层控制，但它不学 policy，而是做 heuristic + gate。

### 14.2 和已有哪几篇最互补？
- 和 Claude Code 互补：Claude Code 解决单 agent runtime harness；Agent Capsules 解决多 agent pipeline 的粒度控制。
- 和 GraphPlanner 互补：GraphPlanner 解决 role × model × workflow 生成，Agent Capsules 解决给定 workflow 下的执行粒度最优化。

### 14.3 如果我要做一个 agentic paper reading order，它应该排在哪？
- 很适合作为“先理解 runtime granularity control”的中间篇，读完 Claude Code 的基础设施后再读这篇会很顺。

## 15. 我的最终结论
> 尽量短一点，直接说“它对设计有什么用”。

### 15.1 最短结论
- Agent Capsules 最重要的贡献，是证明“执行粒度”本身就是 agent router 应该显式控制的一层。

### 15.2 对设计有什么用？
- 如果我要做 coding agent router，我不会只在 query 入口选模型，而会在运行时按 group / phase 决定：单独跑、合并跑、两阶段跑还是顺序复合跑。

### 15.3 我后续要不要复用它的机制？
- 是否复用：`是`
- 优先复用哪部分：composition score 思路、quality floor、escalation ladder、shared state backend
- 不复用哪部分：完全依赖 LLM judge 的质量定义
- 原因：控制框架非常强，但 coding 场景更应把 executable verifier 放到 quality gate 核心位置。