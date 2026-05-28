# Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters

## 1. 论文基本信息
- 标题：Scaling LLM Test-Time Compute Optimally can be More Effective than Scaling Model Parameters
- 作者 / 机构：Charlie Snell, Jaehoon Lee, Kelvin Xu, Aviral Kumar；UC Berkeley / Google DeepMind
- 发表时间：2024-08
- 会议 / 期刊 / arXiv：arXiv preprint，2408.03314
- 论文链接：https://arxiv.org/abs/2408.03314
- 代码链接：未验证到官方公开代码仓库
- 项目链接 / 文档链接（如果有）：未验证到官方项目主页；arXiv 页面未给出明确代码入口
- 研究方向关键词：
  - `Adaptive Compute`
  - `Reasoning Budget Control`
  - `Verifier-guided Search`
  - `Revision Policy`
  - `Difficulty-conditioned Routing`
  - `Inference-time Control`

## 2. 一句话总结
- 总结：这篇论文把 test-time compute 视为一种运行时控制对象，比较“并行搜索 + verifier”与“顺序 revisions”两类策略，并给出按题目难度分配推理预算的 compute-optimal policy，结果表明统一 best-of-N 不是最优，difficulty-aware 的运行时预算控制在 MATH 上可把测试时扩展效率提升到 4× 以上。

## 3. 这篇论文到底在解决什么问题？

### 3.1 核心问题是什么？
- 当一个模型在推理时允许额外花算力，究竟该怎么花最值。
- 对不同 prompt，额外预算该用于：
  - 多采样并行探索
  - verifier / PRM 引导搜索
  - 顺序 revisions 自我修订
  - 还是上述策略的某种混合
- 论文进一步问：在同等 FLOPs 下，给小模型更多 test-time compute，是否可能比单纯把模型做大更划算。

### 3.2 为什么这个问题在 agent 系统里重要？
- 这不是传统“选哪个模型”的问题，而是“当前 runtime 应该启用哪种思考程序”的问题。
- 真实 agent 经常要决定是快速给出答案，还是继续搜索、修订、验证；这本质上就是 runtime control。
- 对 coding agent router 而言，很多决策并不发生在请求入口，而是在执行过程中决定是否继续想、继续试、继续验证。

### 3.3 它主要在优化什么目标？
- 目标类型：成功率、成本、可控性、可扩展性、一定程度的可解释性
- 我的理解：作者优化的不是 wall-clock latency，而是“单位 test-time compute 能换来多少质量增益”，也就是 quality-per-compute。

### 3.4 它的控制对象到底是什么？
- 控制对象：
  - reasoning budget
  - inference strategy
  - verifier/search/revision 的使用方式
  - prompt difficulty 对应的计算分配
- 控制粒度：query-level 为主，但策略内部包含 step-level search / revision 控制
- 我对其定位的判断：这是典型的 budget controller / granularity controller，也是 agent runtime 中“思考深度控制层”的基础论文。

### 3.5 它更像哪一类工作？
- `budget controller`
- `granularity router`
- `workflow controller`
- `observability / recovery framework`
- 我的判断：它不是 tool-use 系统，而是单模型内部的运行时预算路由器，可作为 coding agent router 的底层控制层。

## 4. Agent Loop / Runtime Mechanism

### 4.1 它提出的核心机制是什么？
- 提出一个统一视角：test-time compute 可以通过两条轴来扩展
  1. 改 proposal distribution：让模型在测试时顺序修订自己的答案
  2. 改 verifier/search：对多个候选进行打分、搜索和选优
- 再基于题目难度，为每个预算档选择最优策略，从而形成 compute-optimal scaling。

### 4.1.1 核心直觉是什么？
- 容易题通常不是“完全不会”，而是“差一点”，更适合顺序 refine。
- 难题往往需要探索不同高层解法，更适合并行样本或树搜索。
- 因此固定使用 best-of-N 或固定使用 revision 都会浪费预算，真正需要的是根据 difficulty 动态切换推理程序。

### 4.1.2 整个 agent loop 按步骤是怎么运行的？
- Step 1：输入问题 prompt 与可用 generation/compute budget。
- Step 2：估计问题 difficulty，论文里用 oracle pass@1 quantile 或 predicted difficulty bin 做近似。
- Step 3：根据 difficulty bin 与当前 budget，选择一组 test-time compute 超参数与策略族。
- Step 4：执行对应策略：
  - revision 路线：在顺序修订与并行采样之间分配预算
  - PRM 路线：在 best-of-N、beam、lookahead 等搜索方式中选配置
- Step 5：使用 verifier 或 majority 等方式聚合最终答案。
- Step 6：输出答案并统计在该预算下的精度收益。

### 4.1.3 如果把它压缩成一个决策流 / 伪代码，它长什么样？
- `estimate_difficulty(q) -> choose policy(theta | difficulty, budget) -> run search/revision executor -> aggregate answers -> return best answer`
- 若放进 agent runtime，可理解为：`state -> budget policy -> inference program -> verifier -> termination`。

### 4.2 runtime 的输入 state 是什么？
- 输入 state：
  - 原始问题 prompt
  - 给定 test-time compute budget / generation budget
  - difficulty 估计值或难度桶
  - 候选答案轨迹
  - verifier / PRM 打分
  - revision 历史
  - 所选搜索超参数（beam width、lookahead steps、顺序/并行比等）

### 4.3 runtime 的输出 action 是什么？
- 输出 action：
  - 选择哪种 test-time compute 策略
  - 选择对应超参数
  - 决定预算在并行采样与顺序修订间如何分配
  - 决定是否进行 verifier-guided search
  - 决定最终答案的聚合方式

### 4.4 决策是怎么产生的？
- 决策机制：difficulty-conditioned heuristic policy
- 是否训练：`部分是`
- 如果训练，训练数据是什么：
  - PRM 用 Monte Carlo rollout 软标签训练
  - revision model 用构造的 revision trajectories 做 SFT
  - policy 本身主要靠验证集/交叉验证选每个 difficulty bin 的最优配置，不是端到端训练的 router
- 训练目标是什么：
  - PRM 学 step-level correctness / reward-to-go
  - revision model 学会在已有错误轨迹基础上修正答案

### 4.5 这个控制回路是单步的还是跨轨迹持续更新的？
- 控制范围：单条 query 内多步控制
- 我的理解：这是“单次请求内”的持续预算调度，不涉及跨会话在线学习或长期记忆更新。

### 4.6 这套机制最依赖哪些关键信号？
- 问题 difficulty 估计
- PRM / ORM / verifier score
- revision 轨迹中的答案质量变化
- 给定预算下不同策略的历史验证表现

### 4.7 这套机制最容易失败在哪一步？
- difficulty 估计错误，导致预算分错策略。
- verifier 失真，导致 search 方向偏掉。
- revision 训练不足时，顺序修订会反复在错误附近震荡。
- 策略在 MATH 上有效，不保证迁移到开放式 agent 任务仍成立。

## 5. Context / State / Memory Management

### 5.1 系统如何表示当前状态？
- 状态表示：prompt + difficulty bin + 候选推理轨迹 + verifier score + revision history
- 是否结构化：`是`
- 我对这种表示的理解：这篇论文虽然不是显式 agent 系统，但它其实已经有一套结构化 runtime state，只是状态主要围绕 reasoning 轨迹，而不是工具世界状态。

### 5.2 Context 是如何组织的？
- 上下文组织方式：
  - revision 路线中，把之前的错误答案/修订历史放入后续生成上下文
  - verifier/search 路线中，把 step-by-step 解题轨迹当作 PRM 的评分对象
- 上下文来源：
  - 原问题
  - 过往 revision 尝试
  - 搜索中间节点 / 候选答案
  - few-shot prompt（PRM 使用 4-shot prompt）
- 对成本 / 质量的影响：更丰富的过程上下文有助于修订和验证，但也增加推理计算与序列长度。

### 5.3 是否讨论了 context compaction / summarization / truncation？
- 是否支持：`否`
- 具体怎么做：论文没有专门讨论 context compaction，重点在预算分配而非上下文压缩
- compaction 触发条件：无
- 潜在风险：若迁移到长轨迹 agent 场景，revision history 和搜索轨迹会迅速膨胀

### 5.4 是否有 memory 机制？
- 是否有 memory：`部分有`
- memory 类型：单请求内短期轨迹记忆，而非跨请求长期 memory
- 读写时机：revision 时读取之前的错误尝试；verifier 时读取步骤级轨迹
- 写入内容：当前请求内的中间候选、修订序列、step 分数
- 检索方式：不是外部检索库，而是当前轨迹内直接访问
- 我对其价值的判断：它不是长期记忆论文，但说明了“轨迹状态本身就是一种 memory”，对 coding agent 很有启发。

### 5.5 是否有 session persistence / artifact persistence？
- 是否持久化：`否`
- 持久化对象：论文未描述跨请求持久化
- 恢复方式：无专门会话恢复设计
- 对 recovery 的意义：对真实 agent runtime 来说，这正是需要额外补上的工程层。

### 5.6 如果上下文爆掉、会话中断或执行被打断，系统怎么恢复？
- 论文没有研究中断恢复或轨迹快照恢复。
- 若映射到 agent 场景，只能把它视作“在单次调用内反复修订/搜索”的控制器，而不是具备 durability 的 runtime。

## 6. Tool Use / Environment Interaction

### 6.1 系统能调用哪些工具 / 环境？
- verifier / PRM
- revision model
- search procedure（best-of-N、beam search、lookahead search）
- grading function（用于数学任务最终答案判定）

### 6.2 工具调用的语义是什么？
- 工具调用方式：controller 先决定采用哪条推理程序，再由对应 executor 执行；不是 LLM 自由生成 tool call
- 工具结果回流方式：PRM 分数、ORM 分数、majority 结果进入最终聚合或下一步策略比较
- 我的理解：这里的“工具”更像 internal reasoning operators，而不是外部 API；对 coding agent 来说可类比 test runner、verifier、static analyzer。

### 6.3 工具执行有哪些边界？
- 环境边界：主要在受控的数学推理评估环境内，没有真实文件系统/网络工具
- 隔离方式：论文未讨论沙箱，因为实验几乎不涉及开放环境工具执行
- 权限范围：局限于推理、验证、聚合这类封闭式过程

### 6.4 是否有 permission / approval / safety model？
- 是否有权限系统：`否`
- 权限粒度：无
- 是否需要用户确认：否
- 哪些动作需要确认：无
- 自动允许的动作：预算分配、搜索、修订、验证
- 自动拒绝或升级的动作：无显式权限升级，只有策略切换
- 我的理解：这篇论文几乎不涉及安全边界，若迁移到 coding agent router，需要额外叠加 permission layer。

### 6.5 系统如何处理 tool failure / environment failure？
- 没有真实工具失败的恢复设计；主要问题是 verifier 不准、difficulty 估计不准或 revision/search 无效。
- 从论文角度，失败表现为某策略在某类难题上收益不佳，而不是 runtime exception。

## 7. Orchestration / Subagents / Human-in-the-loop

### 7.1 系统是单 agent 还是多 agent？
- 类型：单主模型 + 辅助 verifier / revision 模块
- 角色划分：
  - base LM / revision model：生成与修订答案
  - PRM / ORM：评估候选答案
  - policy：按难度与预算选择策略
- 为什么这样设计：把生成、验证、预算控制拆分，有利于分析哪类 test-time compute 真正有效。

### 7.2 是否支持 subagent / delegation？
- 是否支持：`否`
- 谁负责发起 delegation：无显式 subagent 机制
- subagent 的输入是什么：不适用
- subagent 的输出如何汇总：不适用
- 代价 / 风险是什么：缺少任务拆分和专门化角色，因此更像“单 agent 的内部计算扩展”而不是多 agent 编排。

### 7.3 多 agent / 多模块之间是怎么通信的？
- 通信方式：结构化分数、候选答案集、revision 轨迹
- 是否共享同一上下文：部分共享；revision verifier 可带历史上下文，PRM 则以步骤文本为输入
- 是否存在局部私有状态：有；搜索节点、revision chain 都属于局部轨迹状态
- 我的理解：这是一个模块化控制栈，而非对话式多 agent。

### 7.4 人类在回路中的位置是什么？
- human-in-the-loop 角色：无直接在线角色
- 介入时机：主要体现在离线实验与评估阶段
- 介入信号：无运行时用户审批
- 如果没有人类介入会怎样：系统本身就是自治推理控制实验，不依赖人类干预

### 7.5 如果把这个系统迁移到 coding agent 场景，哪些协作机制最值得保留？
- 生成器、验证器、预算控制器三分离
- 按 difficulty 切换“快速草案 / 局部修补 / 重搜索”三种模式
- 用 verifier score 驱动是否继续思考，而不是固定思考长度

## 8. Extensibility / Integration / Engineering Cost

### 8.1 系统包含哪些关键模块？
- Difficulty estimator
- Budget policy / compute-optimal selector
- Revision model
- PRM / ORM verifier
- Search executor
- Answer aggregator

### 8.2 是否支持插件化 / MCP / provider adapter / tool registry？
- 是否支持：`部分支持`
- 扩展点在哪里：可替换 verifier、revision model、difficulty estimator、aggregation strategy
- 新增一个 tool / provider / module 需要做什么：
  - 接入新的 verifier 或 executor
  - 重新做 difficulty-conditioned policy sweep
  - 校验新模块与现有 budget policy 的兼容性

### 8.3 如果要新增一个 agent role / tool / workflow mode，系统代价有多大？
- 新增对象：新 verifier、新搜索器、新 compute 档位
- 是否需要改 prompt：通常需要，尤其 few-shot 或 revision prompt
- 是否需要改 controller：需要
- 是否需要新增 state 字段：需要，如新的分数、轨迹统计、停止条件
- 是否需要新增评测：需要
- 我判断的接入成本：中到高
- 原因：控制栈清晰，但每加一个策略都要重新做策略表和预算评估，不是即插即用。

### 8.4 系统最强的工程设计点是什么？
- 把“额外推理算力怎么花”显式建模成可比较、可分桶、可选策略的控制问题，而不是把 test-time compute 当作固定超参。

### 8.5 系统最脆弱的工程点是什么？
- difficulty 估计本身很贵，甚至可能吃掉收益。
- verifier / revision 的分布偏移会让策略表失效。
- 论文以 FLOPs 为主，不足以直接支撑低延迟产品化决策。

## 9. Observability / Debuggability / Recovery

### 9.1 系统是否暴露 runtime telemetry？
- 是否可观测：`是`
- 观测指标：MATH accuracy、relative improvement from test-time compute、generation budget、difficulty bins、PRM/ORM score、不同 sequential/parallel ratio 的表现
- 这些指标对控制器有什么用：
  - 可用于构建 difficulty -> budget policy 表
  - 可用于识别哪些题型适合 revision、哪些适合 search
  - 可用于判断 verifier 是否值得继续保留

### 9.2 是否能解释“为什么做出这次控制决策”？
- 是否支持：`部分支持`
- 解释方式：策略按 difficulty bin 映射，具有一定可解释性；可说“因为此题难度位于某桶，所以采用某预算方案”
- 对调试的价值：高；比黑盒 learned router 更容易看出错误来源是估难错还是 verifier 错

### 9.3 是否有 recovery / rollback / retry / escalation 机制？
- 是否有：`部分有`
- recovery 动作有哪些：更多并行采样、更多顺序 revisions、切换 search algorithm，本质上是预算追加与策略切换
- 触发条件：预算设定与策略选择，而非运行中异常检测
- 哪种恢复最关键：`基于 difficulty 的预算重分配`

### 9.4 这套系统最主要的 failure modes 是什么？
- Failure mode 1：difficulty predictor 不准，简单题被过度搜索或难题被错误用 revision 处理
- Failure mode 2：PRM/ORM 打分与真实正确性脱节
- Failure mode 3：顺序 revisions 在难题上收益不足，甚至浪费预算

### 9.5 如果要把它落到 SWE-bench agent runtime，它最值得先保留哪三类 telemetry？
- 任务难度/不确定性估计信号
- 每追加一档预算后的边际收益
- verifier / test signal 与最终真实成功率的一致性

## 10. 实验设置

### 10.1 使用了哪些任务 / benchmark？
- 主要 benchmark：MATH
- 使用 Lightman et al. 的设置：12k train、500 test
- PRM 与 revision 训练依赖 MATH / PRM800k 相关 prompt 与 grading 资源

### 10.1.1 这些任务到底在测什么？
- 任务来源：竞赛数学推理
- 样本形式：需要逐步推理并输出可判定最终答案的题目
- 评价目标：推理正确率、在给定预算下通过 search / revision 提高正确率的能力
- 与真实 agent 场景的接近程度：对“思考预算控制”很接近；对工具使用、外部环境交互则较远

### 10.2 对比了哪些 baseline？
- Majority voting
- Best-of-N weighted
- ORM best-of-N weighted
- PRM best-of-N weighted
- Beam search
- Lookahead search
- Revision 中的 parallel / sequential / mixed ratio
- 更大模型的 greedy decoding（FLOPs-matched 对比）

### 10.3 使用了哪些模型？
- 主执行模型：PaLM 2-S* (Codey) 及其 finetuned revision model
- 控制器 / router / gate：difficulty-conditioned policy，主要通过验证集选策略
- judge / verifier：PRM、ORM、majority、grading function
- tool model / embedding model（如果有）：无外部 embedding 检索模型
- 我的理解：这是“主模型 + verifier + policy”三件套，适合作为 coding agent 二级控制层原型。

### 10.4 主要评估指标是什么？
- MATH accuracy / pass@1
- relative improvement from test-time compute
- generation budget / number of samples
- difficulty-bin 分层表现
- FLOPs-matched performance comparison

### 10.4.1 每个指标分别在衡量什么？
- 指标 A：MATH accuracy
  - 衡量含义：最终推理是否正确
  - 高/低分别意味着：高表示 test-time 策略真正把更多题做对；低表示预算花法无效
  - 对系统设计的启发：预算控制最终还是要回到任务完成率，而不是只看模型自信度
- 指标 B：relative improvement from test-time compute
  - 衡量含义：额外推理算力相对 baseline 带来的增益效率
  - 高/低分别意味着：高表示预算追加值得；低表示继续想没有性价比
  - 对系统设计的启发：对 coding agent 必须追踪“多跑一轮测试/搜索到底值不值”

### 10.4.2 这些指标有没有盲点？
- 缺少真实 wall-clock latency 与交互体验指标。
- 没有覆盖工具失败、安全边界、长轨迹 context 压力。
- difficulty 估计成本在很多图里未被完整计入，产品化时会更保守。

## 11. 核心结果

### 11.1 最重要的实验结果是什么？
- compute-optimal scaling 相对统一 best-of-N baseline，把 test-time compute scaling 效率提升到 4× 以上。
- 在 revision 路线上，随着 generation budget 增长，按难度切换顺序/并行比例的策略逐渐显著优于固定 parallel baseline。
- 在 PRM search 路线上，difficulty-aware 的 compute-optimal search 相比普通 best-of-N 也有显著前期优势。
- FLOPs-matched 对比中，在小模型已有非平凡成功率的问题上，额外 test-time compute 有时可超过约 14× 更大的预训练模型。

### 11.2 相比 baseline，它真正提升了什么？
- 提升了预算利用效率，而不只是单点准确率。
- 证明最优推理程序依赖问题难度，反驳“一种 test-time trick 通吃所有题目”的假设。
- 为“模型选定之后如何继续追加推理预算”提供了明确控制框架。

### 11.3 它是在质量、成本、延迟、成功率、可控性里的哪几个维度上真正成立？
- 真正成立的维度：成功率、成本效率、可控性、一定程度的可解释性
- 不完全成立或未重点优化：低延迟、持久恢复、工具环境鲁棒性

### 11.4 有哪些 ablation / sensitivity / negative results？
- 不同 difficulty bin 上，revision 与 search 的最优性明显不同。
- PRM 聚合方式上，`last` 优于 `min` / `prod`。
- PRM 在 best-of-N 评估里持续优于 ORM，且 sample 越多优势越明显。
- predicted difficulty bins 与 oracle bins 趋势相近，但估难本身很昂贵。
- ReST 优化后的 revision model 反而在更多 sequential revisions 下显著退化，说明并非所有“进一步强化”都有效。

### 11.5 这些结果真正说明它擅长解决什么问题？
- 擅长解决“同一个模型内部，何时该多想、怎么多想”的运行时预算控制问题。
- 特别适合有 verifier、可判定正确性、问题难度差异明显的 reasoning 任务。
- 对 agent 系统最强的启发是：test-time compute 不应是一刀切默认值，而应是 state-dependent action。

### 11.6 这些结果没有证明什么？
- 没有证明它可以直接迁移到工具使用、浏览器操作、软件修复等开放环境 agent 任务。
- 没有证明 predicted difficulty 能在低成本线上服务中稳定工作。
- 没有证明 FLOPs-optimal 就等于产品延迟最优。

## 12. 可复现性 / 资源开放 / 落地难度

### 12.1 代码、数据、配置、日志是否公开？
- 代码是否开源：未验证到官方公开代码仓库
- 数据 / benchmark 是否公开：MATH、PRM800k 等底层 benchmark / prompt 资源可获取，但论文特有的采样轨迹、soft labels、revision trajectories 未见统一公开数据包
- 配置 / prompt / workflow 定义是否公开：部分公开；附录提供 PRM 训练、revision 训练、聚合与 prompting 细节
- 运行日志 / telemetry / traces 是否公开：未验证到公开 traces 入口

### 12.2 实现细节是否写清楚了？
- 清晰度判断：清楚
- 缺失点：
  - 官方实现入口未验证到
  - 大规模 difficulty 估计的工程实现细节不足
  - 没有产品级 latency / serving 细节
- 我的判断：研究复现路径相对清楚，但因依赖 PaLM 2-S* 与大规模采样，现实复现门槛仍然很高。

### 12.3 真正落地它，工程难点在哪里？
- 构造低成本但可靠的 difficulty estimator
- 训练并维护可信 verifier，避免分布偏移
- 将 FLOPs-optimal 转换成 latency-aware policy
- 把“预算控制”与外部工具、测试、检索等 agent action 统一到同一控制器里

## 13. 对 Coding Agentic Router 的直接启发

### 13.1 对我的 coding agent runtime controller，最值得借鉴的部件是什么？
- difficulty-conditioned budget policy
- 生成器 / 验证器 / 控制器三分离
- 以边际收益而不是固定回合数决定是否继续推理
- 把 search、revision、greedy 看成可切换的“推理程序模式”

### 13.2 哪些东西值得借鉴，但不该原样照搬？
- 直接用昂贵的 pass@1 估难不适合线上，应改成廉价状态特征或小模型估难
- PRM/ORM 在数学上有效，不应直接假设对代码修复或工具操作同样可靠
- 只用 FLOPs 做预算目标过于理想化，落地时必须加入 latency、工具成本和失败风险

### 13.3 如果把这篇 paper 映射到 SWE-bench 轨迹，它更像控制哪个层？
- `budget controller`
- `granularity controller`
- `workflow controller`
- `recovery controller`

### 13.4 它对下面哪些问题最有帮助？
- backbone 选择：中等帮助，提醒模型选完后还需要二级预算控制
- budget 分配：极高帮助，是全文核心
- workflow 切换：高帮助，可把 greedy / revision / search 视为不同 workflow mode
- granularity 控制：极高帮助，尤其是“继续修”还是“重新搜索”
- recovery / retry / rollback：中等偏高，提供了 retry/search 的策略依据
- memory / context compaction：低帮助于长期 memory，中等帮助于轨迹状态管理
- tool use / permission：低帮助
- observability / debugging：高帮助，强调 difficulty、verifier、边际收益等 telemetry

### 13.5 读完后，我会把它放进哪条设计主线？
- `General Router`
- `Coding Agentic Router`
- `Bridge Paper`
- 我的判断：`Bridge Paper`；它不是典型 agent paper，但对 coding agent 的运行时预算控制非常关键。

## 14. 横向比较位置

### 14.1 和已有哪几篇最像？
- 最像各类 adaptive compute / self-refinement / verifier-guided reasoning 工作，而不是普通 multi-model router。
- 若放进 agentic 语境，它更像“单模型内部的控制器论文”。

### 14.2 和已有哪几篇最互补？
- 和工具型 agent runtime 论文互补，因为它们负责环境交互，这篇负责思考预算控制。
- 和 memory/retrieval 论文互补，因为本文几乎没有长期 memory，但很好地定义了单次轨迹内的状态调度。
- 和普通 cost router 论文互补，因为它说明 action space 不能只有 model ID，还应包含 compute mode。

### 14.3 如果我要做一个 agentic paper reading order，它应该排在哪？
- 适合放在看完基础 router 之后、看复杂 coding agent runtime 之前。
- 它可以作为“从选模型过渡到选推理程序”的关键桥梁论文。

## 15. 我的最终结论

### 15.1 最短结论
- 这篇论文最重要的贡献是把“推理预算怎么花”提升为显式 runtime policy，而不是默认超参。

### 15.2 对设计有什么用？
- 对 coding agent router，它直接说明：当代理卡住时，控制器不该只想“要不要换大模型”，还该想“是否值得继续 revision、搜索、验证，以及该用哪种方式追加预算”。

### 15.3 我后续要不要复用它的机制？
- 是否复用：`部分复用`
- 优先复用哪部分：difficulty-conditioned budget policy、边际收益监控、生成器/验证器分离
- 不复用哪部分：高成本 oracle-style 难度估计、数学专用 PRM 设定、只按 FLOPs 优化的目标
- 原因：其控制思想非常适合做 coding agent 的二级 runtime controller，但必须换成更廉价、面向测试/工具反馈的估难与验证信号。
