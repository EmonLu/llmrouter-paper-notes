# Agentic / Agent 机制类论文记录模板

> 用途：用于记录“agent runtime / tool-use / workflow control / granularity control / recovery / permission / memory / subagent orchestration / extensibility”这类论文。
>
> 这类 paper 的重点通常不是“给一个 query 选哪个模型”，而是：
> - agent 的执行循环怎么组织
> - 系统状态如何表示和更新
> - tool 调用与环境交互如何发生
> - permission / safety / approval boundary 怎么设计
> - context compaction / memory / session persistence 怎么做
> - subagent / delegation / extensibility 怎么做
> - 这些机制对 coding agent runtime router 有什么启发
>
> 因此，这个模板不再把重点放在“候选模型池”“新增模型接入成本”上，而是转向“runtime control plane”与“agent system architecture”。

---

## 0. 使用边界

### 0.1 什么时候应该用这个模板？
- 当论文主要在讨论：
  - agent loop / runtime architecture
  - workflow control / execution granularity
  - tool invocation semantics
  - permission / approval / safety boundary
  - context compaction / memory / session storage
  - subagent / delegation / orchestration
  - runtime observability / recovery / continuation
- 当论文对你的价值主要体现在：
  - 如何设计 coding agent runtime
  - 如何做 stateful controller
  - 如何做 execution-time routing

### 0.2 什么时候不该用这个模板？
- 如果论文主要研究的是：
  - query-level model routing
  - candidate model selection
  - cost-quality trade-off 的普通 router
  - benchmark / profile / calibration / model pool design
- 那应该优先用：
  - `templates/paper-template.md`
  - `templates/survey-template.md`

### 0.3 这类论文最值得抓的不是“模型池”，而是什么？
- agent loop
- state representation
- runtime decision point
- tool boundary
- memory / compaction / persistence
- permission / safety
- human control boundary
- extensibility / orchestration
- failure recovery

---

# [论文标题]

## 1. 论文基本信息
> 先把元信息记全，方便回溯、引用和后续索引。

- 标题：
- 作者 / 机构：
- 发表时间：
- 会议 / 期刊 / arXiv：
- 论文链接：
- 代码链接：
- 项目链接 / 文档链接（如果有）：
- 研究方向关键词：
  - 例如：`Agent Runtime`、`Tool Use`、`Workflow Control`、`Granularity Control`、`Memory`、`Subagent Orchestration`

## 2. 一句话总结
> 用一句话说明：这篇论文到底在研究哪个 agent 机制问题、提出了什么机制、带来了什么结果或设计价值。

- 总结：

## 3. 这篇论文到底在解决什么问题？
> 这一部分回答“为什么这个 agent 机制值得研究”。

### 3.1 核心问题是什么？
- 

### 3.2 为什么这个问题在 agent 系统里重要？
- 

### 3.3 它主要在优化什么目标？
> 可多选：质量、成功率、成本、延迟、鲁棒性、可控性、可恢复性、可解释性、可扩展性、可观测性、安全性。

- 目标类型：
- 我的理解：

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

- 控制对象：
- 控制粒度：
- 我对其定位的判断：

### 3.5 它更像哪一类工作？
> 可多选。

- `agent runtime architecture`
- `workflow controller`
- `granularity router`
- `budget controller`
- `memory / context manager`
- `tool-use system`
- `permission / safety design`
- `subagent orchestration`
- `observability / recovery framework`
- 我的判断：

## 4. Agent Loop / Runtime Mechanism
> 这是 agentic paper 最核心的一部分。重点回答：系统到底怎么跑。

### 4.1 它提出的核心机制是什么？
- 

### 4.1.1 核心直觉是什么？
> 用自己的话说明：作者到底利用了什么结构、状态、规则或反馈，来控制 agent 的运行。

- 

### 4.1.2 整个 agent loop 按步骤是怎么运行的？
> 尽量写成 step-by-step。要能让未来你自己据此实现一个最小版本。

- Step 1：
- Step 2：
- Step 3：
- Step 4：
- Step 5（如果有）：

### 4.1.3 如果把它压缩成一个决策流 / 伪代码，它长什么样？
- 

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

### 4.4 决策是怎么产生的？
> 例如：规则、有限状态机、打分器、policy、verifier、gate、LLM-as-controller、混合控制器。

- 决策机制：
- 是否训练：`是 / 否`
- 如果训练，训练数据是什么：
- 训练目标是什么：

### 4.5 这个控制回路是单步的还是跨轨迹持续更新的？
> 区分：
> - 单次调用内控制
> - 单条 trajectory 内多步控制
> - 跨请求 / 跨会话在线更新

- 控制范围：
- 我的理解：

### 4.6 这套机制最依赖哪些关键信号？
> 例如：测试反馈、verifier 分数、tool success、上下文拥塞、用户批准、历史 telemetry、agreement / disagreement。

- 

### 4.7 这套机制最容易失败在哪一步？
> 帮助你识别 failure mode，而不是只看 paper 的“主线成功故事”。

- 

## 5. Context / State / Memory Management
> 这部分是普通 routing 模板里缺失、但 agent 机制论文里非常关键的内容。

### 5.1 系统如何表示当前状态？
> 是 message history、structured state、graph、scratchpad、capsule、trajectory record，还是别的形式？

- 状态表示：
- 是否结构化：`是 / 否`
- 我对这种表示的理解：

### 5.2 Context 是如何组织的？
> 例如：
> - 纯对话历史
> - role-based prompt assembly
> - tool result summary
> - topology-aware context injection
> - selective retrieval
> - 分层上下文

- 上下文组织方式：
- 上下文来源：
- 对成本 / 质量的影响：

### 5.3 是否讨论了 context compaction / summarization / truncation？
- 是否支持：`是 / 否`
- 具体怎么做：
- compaction 触发条件：
- 潜在风险：

### 5.4 是否有 memory 机制？
> 例如：短期 memory、长期 memory、session storage、经验缓存、历史解法库。

- 是否有 memory：`是 / 否`
- memory 类型：
- 读写时机：
- 写入内容：
- 检索方式：
- 我对其价值的判断：

### 5.5 是否有 session persistence / artifact persistence？
> 例如：日志、状态快照、patch、计划、工具输出是否能在下一轮恢复。

- 是否持久化：`是 / 否`
- 持久化对象：
- 恢复方式：
- 对 recovery 的意义：

### 5.6 如果上下文爆掉、会话中断或执行被打断，系统怎么恢复？
- 

## 6. Tool Use / Environment Interaction
> 这部分回答 agent 如何真正接触外部世界。

### 6.1 系统能调用哪些工具 / 环境？
- 

### 6.2 工具调用的语义是什么？
> 例如：
> - LLM 直接生成 tool call
> - planner 先决定，再由 executor 调
> - 工具结果回填到主上下文
> - 工具输出经过摘要 / 过滤后再注入

- 工具调用方式：
- 工具结果回流方式：
- 我的理解：

### 6.3 工具执行有哪些边界？
> 例如：是否有 sandbox、文件系统边界、网络边界、命令执行边界。

- 环境边界：
- 隔离方式：
- 权限范围：

### 6.4 是否有 permission / approval / safety model？
> 这是 agentic paper 非常关键的一栏。

- 是否有权限系统：`是 / 否`
- 权限粒度：
- 是否需要用户确认：
- 哪些动作需要确认：
- 自动允许的动作：
- 自动拒绝或升级的动作：
- 我的理解：

### 6.5 系统如何处理 tool failure / environment failure？
- 

## 7. Orchestration / Subagents / Human-in-the-loop
> 这部分回答“系统是不是单 agent”“多个 agent 如何协作”“人类在什么位置做决定”。

### 7.1 系统是单 agent 还是多 agent？
- 类型：
- 角色划分：
- 为什么这样设计：

### 7.2 是否支持 subagent / delegation？
- 是否支持：`是 / 否`
- 谁负责发起 delegation：
- subagent 的输入是什么：
- subagent 的输出如何汇总：
- 代价 / 风险是什么：

### 7.3 多 agent / 多模块之间是怎么通信的？
> 例如：共享上下文、消息传递、结构化状态、artifact handoff、graph edge。

- 通信方式：
- 是否共享同一上下文：
- 是否存在局部私有状态：
- 我的理解：

### 7.4 人类在回路中的位置是什么？
> 例如：批准者、监督者、终止者、纠偏者、只在高风险动作时介入。

- human-in-the-loop 角色：
- 介入时机：
- 介入信号：
- 如果没有人类介入会怎样：

### 7.5 如果把这个系统迁移到 coding agent 场景，哪些协作机制最值得保留？
- 

## 8. Extensibility / Integration / Engineering Cost
> 这部分比“新增候选模型成本”更重要：你更关心新工具、新角色、新控制器怎么接入。

### 8.1 系统包含哪些关键模块？
- 

### 8.2 是否支持插件化 / MCP / provider adapter / tool registry？
- 是否支持：`是 / 否`
- 扩展点在哪里：
- 新增一个 tool / provider / module 需要做什么：

### 8.3 如果要新增一个 agent role / tool / workflow mode，系统代价有多大？
- 新增对象：
- 是否需要改 prompt：
- 是否需要改 controller：
- 是否需要新增 state 字段：
- 是否需要新增评测：
- 我判断的接入成本：低 / 中 / 高
- 原因：

### 8.4 系统最强的工程设计点是什么？
- 

### 8.5 系统最脆弱的工程点是什么？
- 

## 9. Observability / Debuggability / Recovery
> 这部分很像真实系统设计文档里必须有、但论文常常写不全的内容。

### 9.1 系统是否暴露 runtime telemetry？
> 例如：token、latency、tool success、trajectory status、failure reason、quality score。

- 是否可观测：`是 / 否`
- 观测指标：
- 这些指标对控制器有什么用：

### 9.2 是否能解释“为什么做出这次控制决策”？
- 是否支持：`是 / 否`
- 解释方式：
- 对调试的价值：

### 9.3 是否有 recovery / rollback / retry / escalation 机制？
- 是否有：`是 / 否`
- recovery 动作有哪些：
- 触发条件：
- 哪种恢复最关键：

### 9.4 这套系统最主要的 failure modes 是什么？
- Failure mode 1：
- Failure mode 2：
- Failure mode 3：

### 9.5 如果要把它落到 SWE-bench agent runtime，它最值得先保留哪三类 telemetry？
- 

## 10. 实验设置
> 记录实验是否真的能支撑它的系统主张。

### 10.1 使用了哪些任务 / benchmark？
- 

### 10.1.1 这些任务到底在测什么？
> 不要只抄名字，要写清楚它们是在测 agent loop、tool use、code repair、planning、long-horizon execution，还是别的能力。

- 任务来源：
- 样本形式：
- 评价目标：
- 与真实 agent 场景的接近程度：

### 10.2 对比了哪些 baseline？
- 

### 10.3 使用了哪些模型？
> 这里关注的是 backbone / judge / verifier / controller 各自用什么，而不是普通 routing 模板里的“候选模型池”。

- 主执行模型：
- 控制器 / router / gate：
- judge / verifier：
- tool model / embedding model（如果有）：
- 我的理解：

### 10.4 主要评估指标是什么？
> 例如：task success、quality、token、latency、tool success rate、rollback rate、recovery rate、human approval burden。

- 

### 10.4.1 每个指标分别在衡量什么？
- 指标 A：
  - 衡量含义：
  - 高/低分别意味着：
  - 对系统设计的启发：
- 指标 B：
  - 衡量含义：
  - 高/低分别意味着：
  - 对系统设计的启发：

### 10.4.2 这些指标有没有盲点？
- 

## 11. 核心结果
> 只记录最重要的结论，不要机械抄表。

### 11.1 最重要的实验结果是什么？
- 

### 11.2 相比 baseline，它真正提升了什么？
- 

### 11.3 它是在质量、成本、延迟、成功率、可控性里的哪几个维度上真正成立？
- 

### 11.4 有哪些 ablation / sensitivity / negative results？
- 

### 11.5 这些结果真正说明它擅长解决什么问题？
- 

### 11.6 这些结果没有证明什么？
> 这一栏很重要，防止把 paper 的结论扩大化。

- 

## 12. 可复现性 / 资源开放 / 落地难度
> 这部分继续保持你的高强度精修标准。

### 12.1 代码、数据、配置、日志是否公开？
- 代码是否开源：
- 数据 / benchmark 是否公开：
- 配置 / prompt / workflow 定义是否公开：
- 运行日志 / telemetry / traces 是否公开：
- 如果没有公开，要明确写“未验证到公开入口”，不要含糊写“待核实”。

### 12.2 实现细节是否写清楚了？
> 例如：
> - loop 的状态转移
> - prompt assembly
> - permission policy
> - tool schema
> - memory 写入规则
> - rollback / escalation 触发条件

- 清晰度判断：清楚 / 中等 / 不清楚
- 缺失点：
- 我的判断：

### 12.3 真正落地它，工程难点在哪里？
- 

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

- 

### 13.2 哪些东西值得借鉴，但不该原样照搬？
- 

### 13.3 如果把这篇 paper 映射到 SWE-bench 轨迹，它更像控制哪个层？
> 例如：
> - backbone router
> - budget controller
> - workflow controller
> - granularity controller
> - recovery controller
> - memory manager
> - tool policy layer

- 

### 13.4 它对下面哪些问题最有帮助？
- backbone 选择：
- budget 分配：
- workflow 切换：
- granularity 控制：
- recovery / retry / rollback：
- memory / context compaction：
- tool use / permission：
- observability / debugging：

### 13.5 读完后，我会把它放进哪条设计主线？
- `General Router`
- `Coding Agentic Router`
- `Bridge Paper`
- 我的判断：

## 14. 横向比较位置
> 方便后面做 agentic 组的 comparison / index。

### 14.1 和已有哪几篇最像？
- 

### 14.2 和已有哪几篇最互补？
- 

### 14.3 如果我要做一个 agentic paper reading order，它应该排在哪？
- 

## 15. 我的最终结论
> 尽量短一点，直接说“它对设计有什么用”。

### 15.1 最短结论
- 

### 15.2 对设计有什么用？
- 

### 15.3 我后续要不要复用它的机制？
- 是否复用：`是 / 否 / 部分复用`
- 优先复用哪部分：
- 不复用哪部分：
- 原因：
