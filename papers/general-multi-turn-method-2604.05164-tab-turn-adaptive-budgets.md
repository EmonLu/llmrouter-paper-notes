# Not All Turns Are Equally Hard: Adaptive Thinking Budgets For Efficient Multi-Turn Reasoning

## 1. 论文基本信息
- 标题：Not All Turns Are Equally Hard: Adaptive Thinking Budgets For Efficient Multi-Turn Reasoning
- 作者 / 机构：Neharika Jali, Anupam Nayak, Gauri Joshi / Carnegie Mellon University
- 发表时间：2026-04-14（arXiv v2）
- 会议 / 期刊 / arXiv：arXiv:2604.05164 [cs.LG]
- 论文链接：https://arxiv.org/abs/2604.05164
- 代码链接：未验证到公开代码仓库；arXiv abs / HTML / PDF 均未给出可访问仓库 URL
- 项目链接 / 文档链接（如果有）：未验证到公开入口
- 研究方向关键词：
  - `Adaptive Compute`
  - `Budget Controller`
  - `Multi-turn Reasoning`
  - `Trajectory-level Control`
  - `GRPO`
  - `Sequential Compute Allocation`

## 2. 一句话总结
- 总结：这篇论文把多轮推理中的“每一步该想多久”建模成一个跨轨迹的预算控制问题，用 GRPO 训练的 TAB 在每个 turn 动态分配 thinking budget，在保持或提升正确率的同时，相比静态预算与现成 LLM judge 基线最多节省 35% token；若提前知道完整子问题计划，TAB All-SubQ 最多节省 40%。

## 3. 这篇论文到底在解决什么问题？

### 3.1 核心问题是什么？
- 现有 test-time compute / difficulty-based budget 方法大多把预算控制当成 single-turn 问题：对整道题或当前一步只做一次静态判断。
- 但多轮推理里不同 turn 的难度高度不均，有的步骤只是 bookkeeping，有的步骤决定整条轨迹是否成功。
- 核心问题因此变成：在一条 sequential reasoning trajectory 中，如何把有限总 token 预算分配给真正关键的 turn，而不是每一步平均分配。

### 3.2 为什么这个问题在 agent 系统里重要？
- 在 agent runtime 里，很多成本不是来自“选错模型”，而是来自“在错误的步骤上花了过多 compute”。
- 早期 turn 的长输出还会进入后续上下文，带来累计上下文成本，所以预算浪费会沿轨迹放大。
- 因此 TAB 虽然不是典型 tool-use 论文，但它非常像一个 trajectory-level runtime budget controller。

### 3.3 它主要在优化什么目标？
- 目标类型：质量、成本、推理效率、轨迹级 compute 利用率、长上下文开销控制
- 我的理解：TAB 不是简单压缩输出长度，而是在“把 token 留给关键步骤”这个意义上优化 trajectory-level accuracy-cost trade-off。

### 3.4 它的控制对象到底是什么？
- 控制对象：每个 turn 的 thinking token budget
- 控制粒度：turn-level，且受整题全局 budget 约束
- 我对其定位的判断：这是一个很典型的 runtime budget controller，而不是模型 router

### 3.5 它更像哪一类工作？
- `budget controller`
- `workflow controller`
- `observability / recovery framework`
- 我的判断：它最核心的是 budget controller；若迁移到 coding agent，可作为 recovery 之前的“先加计算预算”控制层

## 4. Agent Loop / Runtime Mechanism

### 4.1 它提出的核心机制是什么？
- TAB 把多轮推理形式化为一个 multi-objective MDP。
- 当前状态由历史对话轨迹和当前子问题组成；动作是从离散预算桶中选择本轮 thinking budget。
- 预算器通过 GRPO 学习，在全局 per-problem token constraint 下最大化最终任务正确率。
- 扩展版本 TAB All-SubQ 允许预算器在当前决策时额外看到未来所有子问题，从而做更强的 planning-style allocation。

### 4.1.1 核心直觉是什么？
- 同一条推理轨迹里的不同步骤并不等难。
- 真正应该自适应的不是“这道题整体该想多久”，而是“当前这一步值不值得花更多 token”。
- 如果控制器能读到历史轨迹，它就能学会对简单步骤少给预算、对关键步骤加码，从而把全局预算用在真正影响最后答案的地方。

### 4.1.2 整个 agent loop 按步骤是怎么运行的？
- Step 1：User LLM 把原始数学题分解成多轮子问题序列。
- Step 2：在第 t 轮，TAB 读取已有历史轨迹 `x1:t-1` 与当前子问题 `qt`。
- Step 3：Budgeter 从离散预算集合 `B = {256, 512, 1024, 2048, 4096}` 中选择当前 turn 的 budget `bt`。
- Step 4：Solver 在给定 `bt` 的约束下生成该轮推理输出 `yt`。
- Step 5：输出被拼回 trajectory，系统进入下一 turn。
- Step 6：整条轨迹结束后，根据最终正确性和总 token 消耗计算 reward，反向更新 Budgeter policy。

### 4.1.3 如果把它压缩成一个决策流 / 伪代码，它长什么样？
- 原题 → 子问题分解 → 对每个 turn：读取历史轨迹 → 选 budget → 限制 solver 在该 budget 下作答 → 更新轨迹 → 直到整题结束 → 按“正确率 - 超预算惩罚”计算 trajectory reward

### 4.2 runtime 的输入 state 是什么？
- 当前 turn 之前的 conversation trajectory
- 当前子问题 `qt`
- 隐含的全局 per-problem budget 约束
- TAB All-SubQ 中还包括全部 past / future sub-questions
- 对应到 agent 视角，这就是一个最小状态编码器：history + current step + remaining global budget

### 4.3 runtime 的输出 action 是什么？
- 当前 turn 的 token budget `bt`
- 间接决定本轮允许的思考深度
- 不直接改模型、不直接改 workflow，只控制 compute 分配

### 4.4 决策是怎么产生的？
- 决策机制：训练得到的 policy model
- 是否训练：`是`
- 如果训练，训练数据是什么：MATH 训练集中的 Level-5 问题，经 User LLM 分解成多轮子问题轨迹，再由 solver 与 budgeter 交互形成训练样本
- 训练目标是什么：最大化最终任务正确率，同时惩罚超出全局 token 预算的轨迹

### 4.5 这个控制回路是单步的还是跨轨迹持续更新的？
- 控制范围：单条 trajectory 内多步控制；训练时通过整条轨迹末端奖励做 delayed credit assignment
- 我的理解：这正是它相对 single-turn budgeter 的关键升级点

### 4.6 这套机制最依赖哪些关键信号？
- 当前 turn 之前的完整历史轨迹
- 当前子问题内容
- 全局 token budget 约束
- 最终任务正确性反馈
- 各 turn 对最终成功的 delayed credit assignment

### 4.7 这套机制最容易失败在哪一步？
- 若子问题分解本身质量差，预算器再好也只是在错误的 decomposition 上做精细分配。
- 若未来关键 turn 不可见，早期 budget 决策可能仍然出现“提前透支”或“过度保守”。
- 若迁移到开放环境，最终 reward 不像数学题那样明确，TAB 的 RL credit assignment 会更难。

## 5. Context / State / Memory Management

### 5.1 系统如何表示当前状态？
- 状态表示：历史 conversation trajectory + 当前子问题；在 TAB All-SubQ 中还额外拼入全部子问题序列
- 是否结构化：`部分是`
- 我对这种表示的理解：它不是复杂的 graph state，但已经体现了最关键的 runtime state——历史、当前步、全局预算

### 5.2 Context 是如何组织的？
- 上下文组织方式：按多轮推理顺序保留前序 turn，并把当前子问题附在末尾
- 上下文来源：User LLM 生成的子问题序列 + Solver 历史回答
- 对成本 / 质量的影响：早期冗长回答会膨胀后续上下文，因此动态 budget 本身也是一种 context-growth 控制

### 5.3 是否讨论了 context compaction / summarization / truncation？
- 是否支持：`否`
- 具体怎么做：论文没有专门设计 compaction 机制
- compaction 触发条件：无
- 潜在风险：随着轨迹增长，context inflation 仍会持续累积，这在真实 agent runtime 中会更严重

### 5.4 是否有 memory 机制？
- 是否有 memory：`否`
- memory 类型：无显式长期 / 短期 memory 模块
- 读写时机：无
- 写入内容：无
- 检索方式：无
- 我对其价值的判断：TAB 依赖的是“当前轨迹历史”，而不是跨任务 memory

### 5.5 是否有 session persistence / artifact persistence？
- 是否持久化：`否`
- 持久化对象：论文未设计持久化 runtime artifact
- 恢复方式：无专门恢复机制
- 对 recovery 的意义：在数学 benchmark 中问题不大，但在长程 coding agent 场景里这会成为缺口

### 5.6 如果上下文爆掉、会话中断或执行被打断，系统怎么恢复？
- 论文没有讨论中断恢复、会话续跑或 context overflow 之后的恢复方案。

## 6. Tool Use / Environment Interaction

### 6.1 系统能调用哪些工具 / 环境？
- 论文环境主要是多轮数学推理，不涉及外部工具调用。
- 环境更接近“多步 reasoning simulator”，而不是 tool-use agent。

### 6.2 工具调用的语义是什么？
- 工具调用方式：无
- 工具结果回流方式：无
- 我的理解：TAB 控制的是纯 thinking compute，而不是 tool invocation

### 6.3 工具执行有哪些边界？
- 环境边界：封闭 benchmark 环境
- 隔离方式：无专门讨论
- 权限范围：无 tool / filesystem / network 权限问题

### 6.4 是否有 permission / approval / safety model？
- 是否有权限系统：`否`
- 权限粒度：无
- 是否需要用户确认：无
- 哪些动作需要确认：无
- 自动允许的动作：预算分配与 solver 作答
- 自动拒绝或升级的动作：无专门安全策略
- 我的理解：这篇论文不是安全或 approval 设计论文

### 6.5 系统如何处理 tool failure / environment failure？
- 无显式工具失败处理；主要失败形式是 budget allocation 失误导致后续 turn 资源不足。

## 7. Orchestration / Subagents / Human-in-the-loop

### 7.1 系统是单 agent 还是多 agent？
- 类型：功能上是多角色串行系统，但不是多智能体协作框架
- 角色划分：User LLM 负责分解，Budgeter 负责分配预算，Solver 负责生成当前 turn 回答
- 为什么这样设计：把 decomposition、control、execution 解耦，便于把预算控制当成独立 policy 学习

### 7.2 是否支持 subagent / delegation？
- 是否支持：`否`
- 谁负责发起 delegation：无
- subagent 的输入是什么：无
- subagent 的输出如何汇总：无
- 代价 / 风险是什么：无

### 7.3 多 agent / 多模块之间是怎么通信的？
- 通信方式：共享同一条 conversation trajectory
- 是否共享同一上下文：`是`
- 是否存在局部私有状态：Budgeter 的内部 policy 参数可看作私有，但运行态输入基本共享
- 我的理解：这是最简洁的 artifact handoff——每一轮输出直接进入后续上下文

### 7.4 人类在回路中的位置是什么？
- human-in-the-loop 角色：无
- 介入时机：无
- 介入信号：无
- 如果没有人类介入会怎样：系统本来就是全自动 benchmark 推理流程

### 7.5 如果把这个系统迁移到 coding agent 场景，哪些协作机制最值得保留？
- 保留“controller 与 executor 解耦”的设计
- 保留“按 step type / trajectory history 分配预算”的思想
- 保留“全局预算约束 + 当前步预算动作”的双层控制

## 8. Extensibility / Integration / Engineering Cost

### 8.1 系统包含哪些关键模块？
- 子问题分解器（User LLM）
- Budgeter policy
- 受 budget 约束的 Solver
- trajectory reward / verifier
- TAB All-SubQ 的 planning-style state augmentation

### 8.2 是否支持插件化 / MCP / provider adapter / tool registry？
- 是否支持：`否`
- 扩展点在哪里：主要是替换 User、Budgeter、Solver 模型，以及替换预算桶集合
- 新增一个 tool / provider / module 需要做什么：论文未提供专门插件层

### 8.3 如果要新增一个 agent role / tool / workflow mode，系统代价有多大？
- 新增对象：新的 step type、tool-use 步骤或新的 workflow mode
- 是否需要改 prompt：`是`
- 是否需要改 controller：`大概率需要`
- 是否需要新增 state 字段：`是`
- 是否需要新增评测：`是`
- 我判断的接入成本：中 / 高
- 原因：当前状态空间仍围绕“数学子问题 + thinking budget”定义，迁移到 coding agent 需要重新设计状态与奖励

### 8.4 系统最强的工程设计点是什么？
- 最强点是把“预算控制”单独抽成一个明确 controller，而不是把它埋进 solver prompt 里。

### 8.5 系统最脆弱的工程点是什么？
- 对 reward 明确性依赖很强；在开放式任务里，correctness 信号不如数学题干净。
- 没有处理 context compaction、session persistence、tool telemetry 等真实 agent runtime 问题。

## 9. Observability / Debuggability / Recovery

### 9.1 系统是否暴露 runtime telemetry？
- 是否可观测：`是`
- 观测指标：accuracy、total tokens used、不同 budget bucket 的分配分布、不同 benchmark 的 token-accuracy trade-off
- 这些指标对控制器有什么用：能直接判断预算是否被合理地留给关键 turn

### 9.2 是否能解释“为什么做出这次控制决策”？
- 是否支持：`部分支持`
- 解释方式：通过预算分布直方图、不同案例中的 turn-level 分配结果做后验解释
- 对调试的价值：可以看出控制器是否把高预算分给关键步骤，但不能像 rule-based controller 那样逐条给出可读理由

### 9.3 是否有 recovery / rollback / retry / escalation 机制？
- 是否有：`部分有`
- recovery 动作有哪些：提高当前关键 turn 的 budget，可视作最小形式的 escalation
- 触发条件：由 learned policy 根据历史轨迹隐式决定
- 哪种恢复最关键：在关键步骤加码，而不是继续平均分配

### 9.4 这套系统最主要的 failure modes 是什么？
- Failure mode 1：对未来关键步骤缺乏预见，导致前面花太多 token
- Failure mode 2：子问题分解质量差，控制器学到的只是错误流程上的最优预算
- Failure mode 3：在开放环境里 reward 稀疏，难以稳定复用当前训练方式

### 9.5 如果要把它落到 SWE-bench agent runtime，它最值得先保留哪三类 telemetry？
- step type × token usage
- 最近 k 步失败率 / 无效尝试率
- 测试反馈或 verifier 状态随 budget 变化的改善曲线

## 10. 实验设置

### 10.1 使用了哪些任务 / benchmark？
- 主实验：MATH-500、AMC23、MATH Level-5、OlympiadBench、AIME25
- OOD 更难测试：TheoremQA、BBEH-Mini、GPQA-Main
- 训练使用：MATH train 中的 Level-5 问题

### 10.1.1 这些任务到底在测什么？
- 任务来源：公开数学 / 科学推理 benchmark
- 样本形式：原题 → 子问题分解 → 多轮推理轨迹
- 评价目标：最终答案正确率与整题总 token 消耗
- 与真实 agent 场景的接近程度：它更像“多轮 reasoning controller”而非完整 tool-use agent，但对 runtime budget control 很接近

### 10.2 对比了哪些 baseline？
- Static 固定预算
- LLM-Judge Individual
- LLM-Judge Multi-Turn
- LLM-Judge Multi-Turn All-SubQ

### 10.3 使用了哪些模型？
- 主执行模型：L1-Qwen3-8B-Exact
- 控制器 / router / gate：Qwen3-1.7B Budgeter（另有更强 4B 预算器实验）
- judge / verifier：最终正确率与轨迹级 reward 计算；不是独立 verifier paper
- tool model / embedding model（如果有）：无
- 我的理解：这是一个“小控制器 + 固定执行器”的典型结构

### 10.4 主要评估指标是什么？
- Accuracy
- Total tokens used
- Accuracy-token trade-off

### 10.4.1 每个指标分别在衡量什么？
- 指标 A：Accuracy
  - 衡量含义：整题是否答对
  - 高/低分别意味着：高说明预算分配没有牺牲最终解题成功率；低说明可能在关键步骤预算不足
  - 对系统设计的启发：runtime controller 不能只看省 token，必须看最终任务成功率
- 指标 B：Total tokens used
  - 衡量含义：整条轨迹的 compute 消耗
  - 高/低分别意味着：低表示 controller 减少了简单步骤上的浪费；过低也可能意味着关键步骤被压缩过头
  - 对系统设计的启发：应在 trajectory level，而不是单步局部，核算 compute 成本

### 10.4.2 这些指标有没有盲点？
- 缺少真实 wall-clock latency、工具执行成本、上下文压缩代价等系统指标
- 在 coding agent 场景里，还需要 patch success、test-pass progression、rollback rate 等指标

## 11. 核心结果

### 11.1 最重要的实验结果是什么？
- TAB 在主 benchmark 上实现更优 accuracy-token trade-off，最多节省 35% token，同时保持或提升准确率。
- TAB with `B = 8k` 相比 baseline 可获得 4.4 个百分点更高准确率，同时还节省 8.5% token。
- TAB All-SubQ 若可提前看到全部子问题，最多可较 baseline 节省 40% token。
- 在 TheoremQA、BBEH-Mini、GPQA-Main 等更难 OOD 数据上仍保持更优 trade-off。

### 11.2 相比 baseline，它真正提升了什么？
- 相比 Static：不再平均分配预算
- 相比 LLM-Judge：不再只做局部难度估计，而是学会跨 turn 规划
- 相比单次 difficulty estimator：更适合 delayed reward 的多轮场景

### 11.3 它是在质量、成本、延迟、成功率、可控性里的哪几个维度上真正成立？
- 真正成立的维度：质量、成本、trajectory-level 可控性
- 间接可能改善延迟，但论文没有系统报告 wall-clock latency

### 11.4 有哪些 ablation / sensitivity / negative results？
- 不同全局预算 `3k / 5k / 8k / 10k` 的对比
- TAB All-SubQ 证明“知道未来子问题”能进一步优化分配
- 更强预算器（Qwen3-4B）优于 1.7B 预算器
- qualitative case 显示：TAB 会对简单步骤只给 256 token，对关键步骤提高到 1024 或更高

### 11.5 这些结果真正说明它擅长解决什么问题？
- 擅长解决“固定总 compute 下，如何在多步轨迹中把算力花在关键步骤上”这个问题。

### 11.6 这些结果没有证明什么？
- 没有证明它可以直接迁移到开放式 tool-use agent
- 没有证明在存在 noisy verifier、代码测试、外部工具失败时仍然稳定
- 没有证明它能单独解决 workflow 选择或 model selection

## 12. 可复现性 / 资源开放 / 落地难度

### 12.1 代码、数据、配置、日志是否公开？
- 代码是否开源：未验证到公开代码仓库
- 数据 / benchmark 是否公开：主 benchmark 多数公开；论文构造的分解轨迹与训练中间产物未验证到统一公开包
- 配置 / prompt / workflow 定义是否公开：论文给出了较清楚的方法与 prompt 接口，但未验证到完整可运行仓库
- 运行日志 / telemetry / traces 是否公开：未验证到公开入口
- 若缺少公开资源入口，应直接写明“未验证到公开入口”。

### 12.2 实现细节是否写清楚了？
- 清晰度判断：中等偏清楚
- 缺失点：缺少完整代码、训练脚本、轨迹构造细节与中间缓存发布
- 我的判断：方法逻辑清楚，但复现到 1:1 论文结果仍有工程补口

### 12.3 真正落地它，工程难点在哪里？
- 为开放式 agent 设计可靠 reward
- 设计适合 coding 任务的 state schema
- 处理预算控制与 tool use / context growth / recovery 的耦合

## 13. 对 Coding Agentic Router 的直接启发

### 13.1 对我的 coding agent runtime controller，最值得借鉴的部件是什么？
- “controller 与 executor 解耦”的结构
- trajectory-level budget state
- 关键步骤加码而非平均分配的思想

### 13.2 哪些东西值得借鉴，但不该原样照搬？
- GRPO 学预算策略值得借鉴，但 coding agent 的 reward 远比数学题脏，不能直接照搬
- 固定预算桶很实用，但 coding agent 的动作空间要加入 workflow / recovery / model selection

### 13.3 如果把这篇 paper 映射到 SWE-bench 轨迹，它更像控制哪个层？
- `budget controller`

### 13.4 它对下面哪些问题最有帮助？
- backbone 选择：帮助较小
- budget 分配：帮助很大
- workflow 切换：间接有帮助
- granularity 控制：中等帮助
- recovery / retry / rollback：可作为 escalation 前置层
- memory / context compaction：间接有帮助
- tool use / permission：帮助较小
- observability / debugging：中等帮助

### 13.5 读完后，我会把它放进哪条设计主线？
- `Coding Agentic Router`
- `Bridge Paper`
- 我的判断：更偏 Coding Agentic Router 的 budget controller 子模块

## 14. 横向比较位置

### 14.1 和已有哪几篇最像？
- TrACE
- Test-time Compute
- s1

### 14.2 和已有哪几篇最互补？
- GraphPlanner（补 workflow control）
- Agent Capsules（补 granularity control）
- EcoAssistant（补 memory / retrieval / escalation）

### 14.3 如果我要做一个 agentic paper reading order，它应该排在哪？
- 应排在 TrACE、s1 之后，作为“trajectory-level budget controller”这一层的代表论文

## 15. 我的最终结论

### 15.1 最短结论
- 这篇最有价值的地方，是把“每一步给多少 compute”从启发式难度估计升级成了跨轨迹 policy 学习问题。

### 15.2 对设计有什么用？
- 对 SWE-bench agent router 很有用，因为它提示你：预算控制应该挂在 trajectory state 上，而不是只看当前一步 prompt。

### 15.3 我后续要不要复用它的机制？
- 是否复用：`部分复用`
- 优先复用哪部分：turn-level budget action、全局预算约束、history-aware controller
- 不复用哪部分：直接照搬其数学任务 reward 与状态定义
- 原因：控制思想很强，但具体任务接口仍需重写成 coding agent 版本
