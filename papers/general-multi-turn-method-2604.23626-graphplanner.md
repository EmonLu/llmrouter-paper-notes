# GraphPlanner: Graph Memory-Augmented Agentic Routing for Multi-Agent LLMs

## 1. 论文基本信息
> 先把元信息记全，方便回溯、引用和后续索引。

- 标题：GraphPlanner: Graph Memory-Augmented Agentic Routing for Multi-Agent LLMs
- 作者 / 机构：Tao Feng，Haozhen Zhang，Zijie Lei，Peixuan Han，Jiaxuan You / University of Illinois Urbana-Champaign
- 发表时间：2026-04-26
- 会议 / 期刊 / arXiv：ICLR 2026 conference paper；arXiv:2604.23626 [cs.CL]
- 论文链接：https://arxiv.org/abs/2604.23626
- 代码链接：https://github.com/ulab-uiuc/GraphPlanner
- 项目链接 / 文档链接（如果有）：代码仓库入口可验证
- 研究方向关键词：
  - `Agentic Routing`
  - `Workflow Generation`
  - `Graph Memory`
  - `Multi-Agent LLMs`
  - `Reinforcement Learning`
  - `Historical Memory`

## 2. 一句话总结
> 用一句话说明：这篇论文到底在研究哪个 agent 机制问题、提出了什么机制、带来了什么结果或设计价值。

- 总结：GraphPlanner 把路由对象从“给 query 选一个模型”提升到“为 query 生成整条多智能体工作流”，用 GARNet 异构图联合编码当前 workflow memory 与历史交互 memory，再用 PPO 在每一步联合选择 agent role 和 LLM backbone，在 14 个任务上相对单轮/多轮 router 最高带来 +9.3% 准确率提升，并把训练 GPU 计算开销压到 1.04 GiB 量级。

## 3. 这篇论文到底在解决什么问题？
> 这一部分回答“为什么这个 agent 机制值得研究”。

### 3.1 核心问题是什么？
- 传统 router 只解决“给当前 query 选哪个模型”。
- 复杂任务往往需要任务分解、多轮协作、角色分工与历史经验复用，只做单步 model selection 不足以表达这种协作结构。
- 核心问题因此变成：能不能让 router 直接生成多 agent workflow，并在流程中同步决定“哪个角色、配哪个模型、下一步如何扩图”。

### 3.2 为什么这个问题在 agent 系统里重要？
- agent setting 下的错误不是局部错误，而是会顺着工作流往后传播的 delayed reward 问题。
- query 的最优求解方式可能不是“用最强模型一次答完”，而是“让不同角色和不同模型分工合作”。
- 历史成功 / 失败轨迹本来就是极有价值的 agent memory，但大多数 router 只用当前 query 或短上下文，浪费了这些轨迹。

### 3.3 它主要在优化什么目标？
> 可多选：质量、成功率、成本、延迟、鲁棒性、可控性、可恢复性、可解释性、可扩展性、可观测性、安全性。

- 目标类型：质量、成本、泛化性、可扩展性
- 我的理解：这篇论文真正想做的是“workflow-level accuracy-cost tradeoff”，而不再是单步分类器式路由。

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

- 控制对象：workflow structure + agent role + model backbone
- 控制粒度：step-level decision，累积成 workflow-level graph
- 我对其定位的判断：这是 workflow router / role-model joint router，而不是普通 model router。

### 3.5 它更像哪一类工作？
> 可多选。

- `agent runtime architecture`
- `workflow controller`
- `memory / context manager`
- `subagent orchestration`
- 我的判断：最像 learned workflow controller + graph-memory-based agentic router。

## 4. Agent Loop / Runtime Mechanism
> 这是 agentic paper 最核心的一部分。重点回答：系统到底怎么跑。

### 4.1 它提出的核心机制是什么？
- GraphPlanner 把 workflow generation 建模成 MDP 中的 sequential graph generation。
- 在每一个 step，动作不是单一模型，而是 `(agent role, model backbone)` 二元组。
- GARNet 把当前 workflow graph 和历史 interaction graph 编到同一状态表示里，再由 PPO 学习 policy。

### 4.1.1 核心直觉是什么？
> 用自己的话说明：作者到底利用了什么结构、状态、规则或反馈，来控制 agent 的运行。

- 直觉一：复杂 query 的最佳求解方式是一条协作工作流，不是单次模型调用。
- 直觉二：历史 agent 交互轨迹里藏着成功的角色搭配和模型分工模式，应该结构化为图记忆而不是简单拼成文本。
- 直觉三：因为早期路由决策影响后续整条轨迹，所以要用 sequence-level RL，而不是只做一步分类。

### 4.1.2 整个 agent loop 按步骤是怎么运行的？
> 尽量写成 step-by-step。要能让未来你自己据此实现一个最小版本。

- Step 1：给定 query，初始化当前 workflow memory graph `Gworkflow`。
- Step 2：读取历史 interaction memory graph `Ghistory`，其中编码过往 query、agent、response、性能与成本关系。
- Step 3：GARNet 对 `Gworkflow ∪ Ghistory` 做异构图编码，得到当前状态表示。
- Step 4：policy 从候选动作空间中选择一个 `(role, model)` 动作，role 取自 Planner / Executor / Summarizer，model 取自候选 LLM pool。
- Step 5：执行该动作，对当前 query 或 sub-query 产出中间响应，并把新的节点 / 边写回 `Gworkflow`。
- Step 6：重复步骤 3–5，逐步扩展 workflow，直到到达终止条件并由 Summarizer 角色整合最终答案。
- Step 7：依据最终任务效用与累计成本计算 reward，用 PPO 更新 policy。
- Step 8：episode 结束后，把整条轨迹整合进 `Ghistory`，供后续 episode 参考。

### 4.1.3 如果把它压缩成一个决策流 / 伪代码，它长什么样？
- 伪代码可以概括为：
  - init Gworkflow
  - while not terminal:
    - s_t = GARNet(Gworkflow, Ghistory, query)
    - a_t = policy(s_t) = (role_t, model_t)
    - o_t = run(role_t, model_t)
    - update Gworkflow with new nodes/edges
  - reward = utility(final_answer) - α * cost
  - PPO update
  - merge episode into Ghistory

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
  - 当前 query / sub-query
  - 当前 workflow graph `Gworkflow`
  - 历史 memory graph `Ghistory`
  - 候选 role 集合
  - 候选 LLM backbone 集合及其成本 / 性能属性
  - 当前步骤在 workflow 中的位置
  - 历史响应与中间结果
  - utility-cost 权衡系数 `α`

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
  - 选择哪个 role
  - 选择哪个 model
  - 如何扩展 workflow graph
  - 何时终止并进入最终 summarization

### 4.4 决策是怎么产生的？
> 例如：规则、有限状态机、打分器、policy、verifier、gate、LLM-as-controller、混合控制器。

- 决策机制：graph encoder + PPO policy
- 是否训练：`是`
- 如果训练，训练数据是什么：14 个任务、6 个领域的 routing episodes 与历史交互轨迹
- 训练目标是什么：最大化 task utility 与成本权衡后的长期回报

### 4.5 这个控制回路是单步的还是跨轨迹持续更新的？
> 区分：
> - 单次调用内控制
> - 单条 trajectory 内多步控制
> - 跨请求 / 跨会话在线更新

- 控制范围：单条 trajectory 内多步控制 + 跨 episode 利用历史 memory
- 我的理解：训练时是跨 episode 学习，推理时通过历史图做 memory-augmented inference，但不是线上持续 RL 更新。

### 4.6 这套机制最依赖哪些关键信号？
> 例如：测试反馈、verifier 分数、tool success、上下文拥塞、用户批准、历史 telemetry、agreement / disagreement。

- 当前 workflow 结构信号
- 历史 interaction memory
- role 与 model 的联合效果
- 最终任务效用与 token 成本
- inductive / transductive 模式下保留的历史图信息

### 4.7 这套机制最容易失败在哪一步？
> 帮助你识别 failure mode，而不是只看 paper 的“主线成功故事”。

- 历史 graph 若带偏，可能把旧模式迁移到不适合的新任务。
- role 空间固定为 Planner / Executor / Summarizer，若任务超出该抽象，动作空间会变得过粗。
- RL 奖励主要看最终表现，中间错误归因仍然困难。

## 5. Context / State / Memory Management
> 这部分是普通 routing 模板里缺失、但 agent 机制论文里非常关键的内容。

### 5.1 系统如何表示当前状态？
> 是 message history、structured state、graph、scratchpad、capsule、trajectory record，还是别的形式？

- 状态表示：异构图状态，由 `Gworkflow` 与 `Ghistory` 组成
- 是否结构化：`是`
- 我对这种表示的理解：相比把历史轨迹拼成长文本，图表示更适合表达 query、agent、response、LLM-role 节点及其关系。

### 5.2 Context 是如何组织的？
> 例如：
> - 纯对话历史
> - role-based prompt assembly
> - tool result summary
> - topology-aware context injection
> - selective retrieval
> - 分层上下文

- 上下文组织方式：不是纯文本上下文，而是由 GARNet 统一读取当前 workflow 图与历史 memory 图
- 上下文来源：当前 episode 的节点 / 边、历史 query-agent-response 轨迹、候选模型 / 角色信息
- 对成本 / 质量的影响：结构化图上下文让 policy 更容易利用长期经验，同时避免简单文本拼接导致的冗余和噪声

### 5.3 是否讨论了 context compaction / summarization / truncation？
- 是否支持：`否，非本文主轴`
- 具体怎么做：未重点讨论文本压缩，而是通过图状态抽象来间接规避长文本历史拼接
- compaction 触发条件：无显式 compaction policy
- 潜在风险：图状态虽然省文本窗口，但可能在实现上更重，需要维护图构建与消息传递成本

### 5.4 是否有 memory 机制？
> 例如：短期 memory、长期 memory、session storage、经验缓存、历史解法库。

- 是否有 memory：`是`
- memory 类型：workflow memory + historical interaction memory
- 读写时机：episode 内不断读写 `Gworkflow`；episode 结束后把完整轨迹写入 `Ghistory`
- 写入内容：query、agent role、response、LLM-role 节点、acc-cost 边等结构化交互轨迹
- 检索方式：GARNet 通过异构图消息传递统一检索与聚合
- 我对其价值的判断：这是论文最关键的创新之一，把“历史经验”从文本缓存变成可训练的结构化 memory。

### 5.5 是否有 session persistence / artifact persistence？
> 例如：日志、状态快照、patch、计划、工具输出是否能在下一轮恢复。

- 是否持久化：`部分有`
- 持久化对象：训练 / 推理使用的历史 interaction graph
- 恢复方式：通过 inductive 或 transductive inference 模式读取保留的历史 memory
- 对 recovery 的意义：更像经验复用，而不是运行时中断恢复

### 5.6 如果上下文爆掉、会话中断或执行被打断，系统怎么恢复？
- 论文没有设计像 Claude Code 那样的 transcript recovery。
- 它的“恢复”更偏统计意义上的：利用历史图对未来 workflow 进行更稳的决策。
- 若某条轨迹选错，主要依赖后续 RL 训练修正 policy，而不是运行时 rollback。

## 6. Tool Use / Environment Interaction
> 这部分回答 agent 如何真正接触外部世界。

### 6.1 系统能调用哪些工具 / 环境？
- 论文主要研究 role × model 路由，不强调外部工具体系。
- agent role 主要是 Planner、Executor、Summarizer，环境更像“多模型协作求解任务”而非富工具环境。

### 6.2 工具调用的语义是什么？
> 例如：
> - LLM 直接生成 tool call
> - planner 先决定，再由 executor 调
> - 工具结果回填到主上下文
> - 工具输出经过摘要 / 过滤后再注入

- 工具调用方式：更准确地说是 role invocation 而不是工具调用
- 工具结果回流方式：每个 `(role, model)` 动作的响应被写入 workflow graph，作为后续节点的上下文
- 我的理解：GraphPlanner 的“环境交互”主要发生在 workflow graph 的扩展，而不是 OS 级工具操作

### 6.3 工具执行有哪些边界？
> 例如：是否有 sandbox、文件系统边界、网络边界、命令执行边界。

- 环境边界：论文未提供专门 sandbox / filesystem / network boundary 设计
- 隔离方式：无明确讨论
- 权限范围：无明确讨论

### 6.4 是否有 permission / approval / safety model？
> 这是 agentic paper 非常关键的一栏。

- 是否有权限系统：`否`
- 权限粒度：未讨论
- 是否需要用户确认：未讨论
- 哪些动作需要确认：未讨论
- 自动允许的动作：未讨论
- 自动拒绝或升级的动作：未讨论
- 我的理解：这篇论文把安全边界留给外部系统，它更纯粹地研究 routing / orchestration。

### 6.5 系统如何处理 tool failure / environment failure？
- 没有显式 tool failure controller。
- 失败主要体现在最终 reward 变差，并通过 RL 间接惩罚不良工作流。
- 这是它与工程型 runtime 论文的重要差异：恢复更偏训练层，不偏执行层。

## 7. Orchestration / Subagents / Human-in-the-loop
> 这部分回答“系统是不是单 agent”“多个 agent 如何协作”“人类在什么位置做决定”。

### 7.1 系统是单 agent 还是多 agent？
- 类型：多 agent
- 角色划分：Planner、Executor、Summarizer 三种核心角色
- 为什么这样设计：作者认为它们足以覆盖 agentic workflow 的关键功能：分解、执行、汇总

### 7.2 是否支持 subagent / delegation？
- 是否支持：`是，但以 role-based workflow 形式体现`
- 谁负责发起 delegation：GraphPlanner policy
- subagent 的输入是什么：当前 query / sub-query 与图状态
- subagent 的输出如何汇总：写入 workflow graph，最终由 Summarizer 聚合为 final answer
- 代价 / 风险是什么：动作空间膨胀为 `3K`（三角色 × K 个模型），训练与推理复杂度都上升

### 7.3 多 agent / 多模块之间是怎么通信的？
> 例如：共享上下文、消息传递、结构化状态、artifact handoff、graph edge。

- 通信方式：通过 workflow graph 中的节点与边做结构化 handoff
- 是否共享同一上下文：`不是共享原始文本上下文，而是共享图状态`
- 是否存在局部私有状态：`有，当前节点局部执行后再写回全局图`
- 我的理解：GraphPlanner 的关键优势就是把 agent communication 显式化为 graph edge，而不是隐式拼接上下文。

### 7.4 人类在回路中的位置是什么？
> 例如：批准者、监督者、终止者、纠偏者、只在高风险动作时介入。

- human-in-the-loop 角色：主要是离线训练与部署配置者
- 介入时机：定义任务、候选模型池、角色集合、utility-cost 目标
- 介入信号：无在线审批设计
- 如果没有人类介入会怎样：系统仍可自动生成工作流，因为它本来就是自动 policy

### 7.5 如果把这个系统迁移到 coding agent 场景，哪些协作机制最值得保留？
- 把 role × model 联合动作空间当成一等控制对象
- 用 graph 记录计划-执行-总结的真实协作结构
- 用历史轨迹图而不是长文本 history 来驱动 router

## 8. Extensibility / Integration / Engineering Cost
> 这部分比“新增候选模型成本”更重要：你更关心新工具、新角色、新控制器怎么接入。

### 8.1 系统包含哪些关键模块？
- workflow memory graph `Gworkflow`
- historical memory graph `Ghistory`
- GARNet
- PPO policy / value network
- role set
- candidate LLM pool
- inference modes：inductive / transductive

### 8.2 是否支持插件化 / MCP / provider adapter / tool registry？
- 是否支持：`部分支持候选模型池扩展，但不是插件框架论文`
- 扩展点在哪里：candidate model pool、role set、graph schema、reward design、inference mode
- 新增一个 tool / provider / module 需要做什么：
  - 新模型：加入候选池并补成本属性与评估
  - 新角色：扩动作空间、图节点类型、训练流程
  - 新任务：补数据、utility 定义、reward 计算

### 8.3 如果要新增一个 agent role / tool / workflow mode，系统代价有多大？
- 新增对象：role、graph node type、reward 信号、candidate model
- 是否需要改 prompt：需要
- 是否需要改 controller：需要，尤其动作空间和状态编码要变
- 是否需要新增 state 字段：需要
- 是否需要新增评测：需要
- 我判断的接入成本：高
- 原因：这是 learned graph policy，不是轻量规则控制器，任何动作空间变化都可能要求重训。

### 8.4 系统最强的工程设计点是什么？
- 用图统一表示当前 workflow 和记忆轨迹，使“路由 + 协作 + 经验复用”进入同一状态空间。
- 角色与模型联合决策，而不是先选角色再选模型的串联启发式。

### 8.5 系统最脆弱的工程点是什么？
- 系统链路长，训练与部署复杂。
- role 空间固定且人为定义，未来扩展到更丰富 agent 生态时会有表示瓶颈。
- transductive 模式效果更好，但要维护更重的历史 memory。

## 9. Observability / Debuggability / Recovery
> 这部分很像真实系统设计文档里必须有、但论文常常写不全的内容。

### 9.1 系统是否暴露 runtime telemetry？
> 例如：token、latency、tool success、trajectory status、failure reason、quality score。

- 是否可观测：`部分是`
- 观测指标：task Acc、Cost、training tokens、GPU compute、average LLM calls、Pareto frontier
- 这些指标对控制器有什么用：主要用于离线训练和比较不同 router，而不是在线 runtime 调参

### 9.2 是否能解释“为什么做出这次控制决策”？
- 是否支持：`部分支持`
- 解释方式：可从 workflow graph 与 GARNet 状态抽象解释，但不像规则系统那样天然可解释
- 对调试的价值：图结构比纯黑箱 MLP router 好，但 RL policy 仍有解释门槛

### 9.3 是否有 recovery / rollback / retry / escalation 机制？
- 是否有：`否，至少不是显式执行级 recovery`
- recovery 动作有哪些：无明确 rollback / retry / escalation 设计
- 触发条件：无
- 哪种恢复最关键：若硬要说，inductive / transductive 是部署时的模式切换，而不是失败恢复

### 9.4 这套系统最主要的 failure modes 是什么？
- Failure mode 1：历史 memory 分布偏移导致错误迁移。
- Failure mode 2：固定角色集无法覆盖复杂协作任务。
- Failure mode 3：学习到的 workflow 在新领域上结构失配。

### 9.5 如果要把它落到 SWE-bench agent runtime，它最值得先保留哪三类 telemetry？
- role × model action trace
- workflow graph growth statistics
- utility-cost trajectory 与 final verifier signal

## 10. 实验设置
> 记录实验是否真的能支撑它的系统主张。

### 10.1 使用了哪些任务 / benchmark？
- 共 14 个任务、6 个领域
- in-domain 任务包括：
  - Math：GSM8K、MATH
  - Code：MBPP、HumanEval
  - Commonsense：CommonsenseQA、ARC、OpenBookQA
  - World knowledge：NaturalQuestions、TriviaQA
  - Popular exam：MMLU、GPQA
- out-of-domain / unseen 数据集：LogicGrid、MGSM、CommonGen
- appendix Table 8 给出训练 / 测试样本规模；大多数任务训练 / 测试为 500/50，MBPP 374/50，HumanEval 120/44，GPQA 400/44，未见任务各 50 测试样本

### 10.1.1 这些任务到底在测什么？
> 不要只抄名字，要写清楚它们是在测 agent loop、tool use、code repair、planning、long-horizon execution，还是别的能力。

- 任务来源：公开 benchmark 与作者定义的 agentic routing 设置
- 样本形式：数学、代码、常识、开放问答、综合学科、未见泛化任务
- 评价目标：测 role-model workflow generation 是否比单轮 / 多轮 router 更适合复杂任务
- 与真实 agent 场景的接近程度：比普通路由 benchmark 更接近 agentic routing，但仍以 benchmark 任务为主，不是重工具环境任务

### 10.2 对比了哪些 baseline？
- Single-round routers：RouterKNN、RouterMLP、RouterSVM、RouterDC、GraphRouter
- Multi-round routers：Prompt LLM、Router-KNN-MR、R2-Reasoner、Router-R1

### 10.3 使用了哪些模型？
> 这里关注的是 backbone / judge / verifier / controller 各自用什么，而不是普通 routing 模板里的“候选模型池”。

- 主执行模型：12 个候选 LLM，覆盖 small / medium / large 三档，如 Qwen2.5-7B、CodeGemma-7B、Mistral-7B、LLaMA-3.1-8B、Gemma-2-9B、ChatQA-70B、Mixtral 8×22B 等
- 控制器 / router / gate：GARNet + PPO policy
- judge / verifier：任务指标直接评估，不依赖统一 LLM judge
- tool model / embedding model（如果有）：candidate embedding dim 1536；state embedding dim 768；未单列外部 embedding 模型
- 我的理解：真实成本被显式建模，候选模型不是只按大小分桶，而是附带价格信息

### 10.4 主要评估指标是什么？
> 例如：task success、quality、token、latency、tool success rate、rollback rate、recovery rate、human approval burden。

- Acc（任务对应指标）
- Cost（输入 / 输出 token 成本）
- training tokens
- GPU compute
- average LLM calls
- Pareto frontier 表现

### 10.4.1 每个指标分别在衡量什么？
- 指标 A：Acc
  - 衡量含义：最终任务表现
  - 高/低分别意味着：高说明 workflow 路由更有效
  - 对系统设计的启发：workflow controller 不能只省钱，必须最终解题更好
- 指标 B：Cost
  - 衡量含义：不同工作流对模型调用成本的消耗
  - 高/低分别意味着：低说明角色与模型分工更高效
  - 对系统设计的启发：role 与 model 应联合选，而不是默认都用强模型
- 指标 C：GPU compute / training cost
  - 衡量含义：训练 router 本身的资源需求
  - 高/低分别意味着：低说明 learned router 更有工程可行性
  - 对系统设计的启发：workflow router 也要关注自身训练代价

### 10.4.2 这些指标有没有盲点？
- 没有系统性报告真实在线 latency。
- 不涉及工具调用成功率、恢复率、权限负担等工程指标。
- 训练期指标优秀，不代表线上服务集成成本低。

## 11. 核心结果
> 只记录最重要的结论，不要机械抄表。

### 11.1 最重要的实验结果是什么？
- Phase 1 平均准确率至少比最强 baseline 高 `+3.8%`
- Phase 2 平均准确率至少比最强 baseline 高 `+9.3%`
- 训练 GPU compute 从 `186.26 GiB` 降到 `1.04 GiB`
- 未见任务零样本平均准确率达到 `78%`
  - LogicGrid：60%
  - MGSM：92%
  - CommonGen：82%
- 训练成本表明 GraphPlanner 用 `182.45k` training tokens、`1.04 GiB` GPU compute、`4.25` 平均训练 LLM calls；比 Router-R1 的 `186.26 GiB` GPU compute 轻很多

### 11.2 相比 baseline，它真正提升了什么？
- 相比 single-round router：从 one-shot model assignment 升级为 workflow generation
- 相比 multi-round router：不只是多轮上下文更新，而是显式建模角色协作结构
- 在 reasoning-heavy 的 Math 与 Code 任务上收益特别明显

### 11.3 它是在质量、成本、延迟、成功率、可控性里的哪几个维度上真正成立？
- 成立的维度：质量、成本、泛化性
- 部分成立的维度：训练效率
- 没有充分证明的维度：在线可控性、执行级恢复能力、服务 latency

### 11.4 有哪些 ablation / sensitivity / negative results？
- memory ablation：w/o History、Homo-Graph、Hetero-Graph、Full GARNet
- inference mode ablation：inductive vs transductive
- unseen tasks / unseen LLMs 泛化实验
- appendix 还提供 PPO 超参：`γ=0.99`、`ϵ=0.2`、每次更新 4 epochs、hidden dim 32、policy lr `3e-4`、gradient clipping 0.5、BF16、gradient checkpointing、单卡 A6000

### 11.5 这些结果真正说明它擅长解决什么问题？
- 擅长解决“需要显式协作结构”的复杂多模型任务。
- 特别适合把 router 从 query-level selector 推进到 workflow-level planner。

### 11.6 这些结果没有证明什么？
> 这一栏很重要，防止把 paper 的结论扩大化。

- 没有证明它在强工具使用、代码修补、长会话记忆等真实 coding runtime 中一定有效。
- 没有证明固定三角色就是最优抽象。
- 没有证明 learned workflow router 的部署成本低于规则系统，只证明其效果上有潜力。

## 12. 可复现性 / 资源开放 / 落地难度
> 这部分继续保持你的高强度精修标准。

### 12.1 代码、数据、配置、日志是否公开？
- 代码是否开源：是，GitHub 仓库入口可验证
- 数据 / benchmark 是否公开：部分公开。大多数任务来自公开 benchmark，表 8 / 9 列出了数据规模与指标；但作者额外处理的切分、cache 与全部处理产物是否都已整理公开，本文档未逐项验证到入口
- 配置 / prompt / workflow 定义是否公开：主要训练超参与候选模型池公开较充分
- 运行日志 / telemetry / traces 是否公开：未验证到完整公开入口

### 12.2 实现细节是否写清楚了？
> 例如：
> - loop 的状态转移
> - prompt assembly
> - permission policy
> - tool schema
> - memory 写入规则
> - rollback / escalation 触发条件

- 清晰度判断：中等到清楚
- 缺失点：
  - 部分图消息传递细节与 role 扩展关系没有完全展开
  - 仓库数据预处理与 full reproduction 路线仍需要自己补
- 我的判断：论文级复现信息足够，但要做稳定工程实现仍较重。

### 12.3 真正落地它，工程难点在哪里？
- 需要维护候选模型池、价格表、任务 reward 和图状态编码。
- 动作空间一旦扩展，就会牵动重训。
- 若迁移到真实 coding agent，还要再补工具边界、权限层和执行级恢复层。

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

- 用 graph state 替代长文本 history，编码计划-执行-总结关系
- 把 role × model 作为联合动作空间
- 用历史轨迹图做 memory，而不是只看当前 repo state
- 用 utility-cost joint objective 学工作流，而不是只学“选最强模型”

### 13.2 哪些东西值得借鉴，但不该原样照搬？
- 固定三角色适合作为最小起点，但 coding agent 很可能还需要 verifier、editor、tester、retriever 等角色。
- 纯 RL 学全部工作流过重，实际可先用规则工作流，再在局部节点用 learned policy。

### 13.3 如果把这篇 paper 映射到 SWE-bench 轨迹，它更像控制哪个层？
> 例如：
> - backbone router
> - budget controller
> - workflow controller
> - granularity controller
> - recovery controller
> - memory manager
> - tool policy layer

- `workflow controller`
- `memory manager`
- `subagent orchestration`
- 我的判断：它最适合启发“复杂 bug 修复要不要先 plan，再 verify，再 summarize，以及每步配什么模型”。

### 13.4 它对下面哪些问题最有帮助？
- backbone 选择：很强，但和 role 联合发生
- budget 分配：强，体现在 cost-aware reward
- workflow 切换：极强
- granularity 控制：中等，重点不是合并粒度
- recovery / retry / rollback：较弱
- memory / context compaction：强，但体现在图 memory，不是文本压缩
- tool use / permission：较弱
- observability / debugging：中等

### 13.5 读完后，我会把它放进哪条设计主线？
- `General Router`
- `Coding Agentic Router`
- `Bridge Paper`
- 我的判断：`Bridge Paper`

## 14. 横向比较位置
> 方便后面做 agentic 组的 comparison / index。

### 14.1 和已有哪几篇最像？
- 和所有把 router 输出从单次模型选择扩展到多步 workflow 的工作最像。
- 在这组三篇里，它和 Agent Capsules 都是 workflow 层控制，但 GraphPlanner 是 learned generation，Agent Capsules 是 heuristic runtime control。

### 14.2 和已有哪几篇最互补？
- 和 Claude Code 最互补：Claude Code 讲工程型 runtime harness，GraphPlanner 讲 learned workflow policy。
- 和 Agent Capsules 最互补：前者决定“做什么工作流”，后者决定“以什么粒度执行这个工作流”。

### 14.3 如果我要做一个 agentic paper reading order，它应该排在哪？
- 适合放在读完工程型 runtime 论文之后，再读这篇作为“从 runtime 控制走向 workflow 生成”的升级篇。

## 15. 我的最终结论
> 尽量短一点，直接说“它对设计有什么用”。

### 15.1 最短结论
- GraphPlanner 的核心价值，是把 router 从模型选择器升级成工作流生成器。

### 15.2 对设计有什么用？
- 如果我要做复杂 coding agent router，这篇论文提醒我：最终输出也许不该是“选哪个模型”，而该是“下一段轨迹应该由哪个角色、配哪个模型、按什么拓扑继续”。

### 15.3 我后续要不要复用它的机制？
- 是否复用：`部分复用`
- 优先复用哪部分：graph memory、role × model 联合动作空间、cost-aware workflow objective
- 不复用哪部分：直接照搬完整 PPO 工作流生成训练
- 原因：思想非常强，但完整系统太重，实际更适合先做轻量 hybrid 版本。