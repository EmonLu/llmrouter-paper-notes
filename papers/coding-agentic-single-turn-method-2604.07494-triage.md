# Triage: Routing Software Engineering Tasks to Cost-Effective LLM Tiers via Code Quality Signals

## 1. 论文基本信息
- 标题：Triage: Routing Software Engineering Tasks to Cost-Effective LLM Tiers via Code Quality Signals
- 作者 / 机构：Lech Madeyski / Wroclaw University of Science and Technology
- 发表时间：2026-04-08（arXiv v1）
- 会议 / 期刊 / arXiv：arXiv:2604.07494 [cs.SE]
- 论文链接：https://arxiv.org/abs/2604.07494
- HTML 入口：https://arxiv.org/html/2604.07494v1
- 代码链接：未验证到公开代码仓库；当前 arXiv abs / HTML 页面未见可访问 repo URL
- 项目链接 / 文档链接（如果有）：无
- 本地 PDF：pdfs/coding-agentic-single-turn-method-2604.07494-triage.pdf
- 抽取来源：arXiv HTML 页面
- 研究方向关键词：
  - `Task-level Routing`
  - `Coding Agent Router`
  - `Code Health`
  - `Verification Gate`
  - `SWE-bench Lite`
  - `Cost-aware Model Selection`

## 2. 一句话总结
- 总结：这篇论文不是做 step-level agentic routing，而是把 coding agent 的“整条 issue 先交给哪一档模型”重新定义成一个 SE-specific task-level routing 问题：利用代码健康度、测试覆盖率和任务元数据，在 generation 之前一次性把任务分配给最便宜但仍能通过同一 verification gate 的模型 tier，并给出一套可证伪、可复用的 SWE-bench Lite 评估协议。

## 3. 这篇论文到底在解决什么问题？

### 3.1 核心问题是什么？
- 现有 coding agent 常常把每个软件工程任务都直接发给 frontier model，导致大量本来可以由便宜模型完成的 routine task 也付了最高成本。
- 同时，大部分 query router 关注的是 token-level 或 query-level difficulty / self-confidence，而没有利用软件工程任务天然可获得的 repo metadata。
- 这篇论文要回答的是：能不能在 issue 开始前，用代码健康度这类 SE 特有信号，判断“这条任务是否可以安全地下放给更便宜的 tier”？

### 3.2 为什么这个问题重要？
- 对 coding agent 来说，任务对象不是抽象问答，而是 repo-level bug fix / feature task；这里有文件属性、耦合、复杂度、覆盖率等结构化元数据可用。
- 如果 verification gate 存在（测试、lint、type check），就可以把“先试便宜模型，再失败时回退 heavy”变成一个可计算的成本问题，而不是拍脑袋的 heuristic。
- 这让 routing 从通用 NLP 难度判断，变成了带工程语义的 deployment decision。

### 3.3 它主要在优化什么目标？
- 目标类型：成本、任务成功率、可解释性、SE-specific routing signal 可用性
- 我的理解：这篇论文更像“SE 任务级 router 的问题定义 + evaluation protocol”论文，而不是已经被充分验证的强方法论文。

### 3.4 它的控制对象到底是什么？
- 控制对象：单个软件工程任务 / issue 在 generation 开始前应分配到哪个 capability tier
- 控制粒度：task-level / issue-level
- 我对其定位的判断：它是 coding-agent 语境下的 coarse-grained backbone router，而不是 execution-time step router

### 3.5 它更像哪一类工作？
- `task-level coding-agent router`
- `SE-specific feature router`
- `evaluation protocol / falsifiable framework`
- 我的判断：它是 TwinRouterBench 之前那一代“issue-level routing”代表，非常适合与你现在做的 step-level router 形成对照组

## 4. Agent Loop / Runtime Mechanism

### 4.1 它提出的核心机制是什么？
- Triage 用三阶段 pipeline 做 task-level routing：
  1. 预计算每个文件的 code health 子因子与测试覆盖率。
  2. 给定 issue 描述及其引用文件，生成一次 routing decision，选择 `light / standard / heavy` 三档之一。
  3. 选中的 tier 生成结果后，经同一个 verification gate 检查；若失败，则回退到 heavy tier 重跑。
- 论文同时定义三类 policy：heuristic threshold、trained ML classifier、perfect-hindsight oracle。

### 4.1.1 核心直觉是什么？
- 作者借用 Borg et al. 2026 的发现：中档模型在 clean code 上的 break rate 明显下降，但 frontier model 对 code health 的敏感度没那么大。
- 因此，代码越健康，越有可能安全地下放给低成本 tier；代码越糟糕，就越应该保守地用更强模型。
- 这是一种“结构复杂度 → 所需能力档位”的映射，而不是“语言表面难度 → 所需模型”的映射。

### 4.1.2 整个 agent loop / 控制流按步骤是怎么运行的？
- Step 1：对 repo 中文件预先计算 CodeHealth 子因子、覆盖率等静态特征。
- Step 2：当新任务到来时，解析 issue 描述与其引用文件。
- Step 3：从特征表中取出目标文件对应特征，送入 heuristic / classifier / oracle policy。
- Step 4：输出一个 capability tier。
- Step 5：对应 tier 的模型执行整条任务。
- Step 6：verification gate 给出 pass/fail；若失败则 fallback 到 heavy tier。
- Step 7：verification 结果还能回流，用于后续训练 / 校准 classifier。

### 4.1.3 如果把它压缩成一个决策流 / 伪代码，它长什么样？
- `issue -> infer referenced files -> lookup precomputed code-health features -> predict cheapest sufficient tier -> run selected tier -> verification gate -> if fail then rerun heavy`

### 4.2 runtime 的输入 state 是什么？
- 任务描述 / issue 描述
- 目标文件的 code health 子因子（25+）
- 测试覆盖率
- 任务元数据
- 可能的文件引用信息
- 注意：它并不读取执行中的 tool trace、历史 patch、shell 输出，因此 state 远比 TwinRouterBench 弱

### 4.3 runtime 的输出 action 是什么？
- 输出是一个 tier：`light`、`standard`、`heavy`
- 不是具体模型 ID，而是能力档位
- 也不是 step-level 动作；整个任务生命周期只做一次决策

### 4.4 决策是怎么产生的？
- 决策机制：
  - heuristic threshold
  - trained ML classifier
  - perfect-hindsight oracle
- 是否训练：可选
- 如果训练，训练数据是什么：论文设想用 oracle label 监督 feature-to-tier classifier
- 训练目标：预测“最便宜且足够通过 verification gate 的 tier”

### 4.5 这个控制回路是单步的还是跨轨迹持续更新的？
- 控制范围：单次 task-level 决策
- 运行时不会在 agent 执行过程中再次改判
- 我的理解：这是它相对于 step-level agentic router 的最大局限，也是它对你项目最重要的边界提醒

### 4.6 这套机制最依赖哪些关键信号？
- CodeHealth composite / sub-factors
- 测试覆盖率
- issue 引用文件的准确识别
- verification gate 的可靠性
- tier 成本差

### 4.7 这套机制最容易失败在哪一步？
- 若 issue 无法准确映射到目标文件，router 的输入就会错。
- 若 code health 与真正任务难度高度混淆，很难区分“代码脏”与“任务本身复杂”。
- 若测试覆盖率不足，即使低档模型做错了，也可能被 verification 漏检。
- 若任务是多文件、多阶段 agent workflow，单次 task-level 决策会错过中间步骤大量可降级空间。

## 5. Context / State / Memory Management

### 5.1 系统如何表示当前状态？
- 状态表示：静态文件特征 + 任务元数据
- 是否结构化：是
- 我对这种表示的理解：非常像 repo metadata table 上的 lookup，而不是 trajectory encoder

### 5.2 Context 是如何组织的？
- 通过预计算 feature table 组织，而不是把 repo 上下文全文送入 router
- 每个任务只查询相关文件特征
- 对成本的影响：routing 本身几乎无额外 latency，是非常 deployment-friendly 的轻量方案

### 5.3 是否讨论了 context compaction / summarization / truncation？
- 是否支持：否
- 原因：它不是 step-level online router，不维护长上下文

### 5.4 是否有 memory / session / artifact persistence？
- 有无长期记忆：无显式 memory 模块
- 有无 session persistence：无
- 有无 artifact persistence：主要是预计算的特征表
- 我的理解：它保留的是 metadata cache，而不是 agent experience memory

### 5.5 对你做 coding agent router 的启发
- 这篇论文告诉你：在 coding 任务里，routing signal 不一定要从 LLM prefix 本身来，也可以来自 repo 静态元数据。
- 但如果你要做 execution-time router，这些信号更适合做“初始先验”或“pre-routing prior”，而不是唯一状态。

## 6. Tool Use / Environment Interaction

### 6.1 它如何与外部环境交互？
- 与 repo 交互：读取预计算代码健康度与测试覆盖率
- 与 agent harness 交互：把整个 task 分配到某个 tier 跑完
- 与验证环境交互：通过测试 / lint / type checker 获得二元 pass/fail

### 6.2 它是否真的建模了 tool-use agent 的执行细节？
- 没有。
- 它假设下游 agent 已经存在，并把 routing 抽象为 generation 前的一次 tier 分配。
- 所以它更像“outer-loop task triage”，不是“inner-loop agent policy”。

### 6.3 verification gate 在这里扮演什么角色？
- verification gate 同时承担：
  - 验证当前 routing decision 是否成功
  - 为 trained classifier 提供后续监督信号
  - 定义 cost equation 里的 fallback penalty
- 这点很重要，因为它把 routing 成败落到了真实执行结果，而不是人工偏好标注

### 6.4 它的环境交互边界有什么局限？
- 在论文评估里，target files 可由 ground-truth patch 知道；但在真实部署里，issue 是否能准确指向目标文件仍是开放问题。
- 也就是说，它把一个非常关键的问题——target file inference——留到了系统外部。

## 7. Orchestration / Subagents / Human-in-the-loop

### 7.1 是否是多 agent / 多角色系统？
- 不是
- 更像一个 single routing layer，挂在现有 coding agent 前面

### 7.2 是否讨论 subagent / delegation？
- 未讨论

### 7.3 是否讨论 human-in-the-loop？
- 未作为系统核心讨论
- 人的角色主要体现在研究设计与后验解释，不在运行时闭环内

## 8. Extensibility / Integration / Engineering Cost

### 8.1 它的工程实现复杂度高吗？
- 不算高
- 真正麻烦的不是 classifier，而是：
  - code health 特征如何稳定预计算
  - issue 到目标文件的映射
  - verification gate 的覆盖率

### 8.2 如果替换底层模型，会发生什么？
- 因为它路由的是 capability tier 而不是固定 model name，理论上换模型只需做 tier-to-model 的重新校准
- 这是它的一个优点：抽象层比直接 route 到具体 model id 更稳

### 8.3 如果新增一个候选模型，接入成本高吗？
- 中等
- 若只是在已有 `light / standard / heavy` tier 中替换代表模型，接入成本较低
- 若新增模型改变 tier 边界或成本比，则需要重新验证 pass rate 与 cost gate 条件
- 我的判断：比 step-level benchmark 重新标注便宜，但仍不是零成本

### 8.4 对你项目的真正工程价值是什么？
- 最适合拿来做 execution-time router 的初始 prior：
  - repo health 好 → 初始 backbone / budget 可以更激进地下放
  - repo health 差 → 初始 tier 保守，后续再靠 execution state 细化
- 也可以作为与你现有 235b vs 397b 观察互证的一条线：workflow fragility 之外，repo health 可能是 task-level 先验信号

## 9. Observability / Debuggability / Recovery

### 9.1 这套系统容易观察吗？
- 比 step-level router 容易很多
- 因为输入就是结构化特征表，输出就是 tier，决策链更可解释

### 9.2 是否支持解释为什么选这个 tier？
- 支持到一定程度
- 论文还专门计划用 SHAP 分析子因子重要性，回答 composite score 是否优于 individual sub-factors

### 9.3 它的 recovery 机制是什么？
- 唯一 recovery 是 verification 失败后 fallback 到 heavy tier 重跑
- 没有 rollback / branch / replanning / online rerouting 这些 richer recovery action

### 9.4 它的典型 failure mode 是什么？
- under-triage：任务被派给太弱模型，失败后触发 fallback penalty
- over-triage：任务其实很简单，却被保守地交给 heavy，导致省钱空间浪费
- file inference 错误：看错目标文件，整条 routing decision 建在错误特征上

## 10. 实验设置

### 10.1 使用了哪些数据集？
- 核心评估数据集：SWE-bench Lite
- 规模：300 tasks
- 设定：3 个 capability tiers，每个 task 在每个 tier 上运行 3 次，用多数表决缓解非确定性
- 总 agent runs：2,700（论文设想的完整评估规模）

### 10.2 label / oracle 是怎么定义的？
- perfect-hindsight oracle：对每个 task 跑遍所有 tiers，选择最便宜且通过 verification gate 的 tier
- 这个 oracle 不是静态人工标签，而是 execution outcome 驱动的 hindsight label
- 从这个角度看，它和 TwinRouterBench 的“execution-verified label”有血缘关系，只是粒度更粗

### 10.3 比较了哪些 policy？
- heuristic thresholds
- trained ML classifier
- perfect-hindsight oracle
- baselines：always-light、always-heavy、random

### 10.4 主要指标是什么？
- task success rate
- cost per successful task
- triage accuracy（对 oracle）
- over-triage rate
- under-triage rate
- 并按 changed code 的 test coverage 分层报告

### 10.5 pilot go/no-go 条件是什么？
- 成本门槛：light tier 在被路由任务上的 pass rate 必须高于成本比 `c_L / c_H`
- 信号门槛：high-CodeHealth vs low-CodeHealth 的 effect size 需达到至少 small effect，`p^ >= 0.56`
- 我的理解：这篇论文最大的贡献之一是给 routing signal 提出“是否值得继续做”的可证伪标准

## 11. 核心结果与我怎么看

### 11.1 论文已经证明方法有效了吗？
- 还没有完全证明。
- 这篇论文更像 proposal + rigorous protocol：给出分析条件、pilot gate、完整实验设计，但不是像 TwinRouterBench 那样已经交付大规模 execution-verified benchmark 与公开 leaderboard 结果。

### 11.2 目前最有价值的结论是什么？
- task-level coding-agent routing 是合理问题，不应只从普通 query router 类比过来。
- code health 可以被重新解释成 routing signal，而不只是代码可维护性诊断指标。
- 若信号太弱或不满足成本门槛，应诚实地报告负结果，而不是硬凹 router story。

### 11.3 它和 TwinRouterBench 的关系怎么理解？
- Triage：issue-level / task-level，一次性选 tier
- TwinRouterBench：step-level / execution-time，在 agent 轨迹里逐步路由
- 最关键差异：
  - Triage 的 state 是静态 metadata
  - TwinRouterBench 的 state 是 router-visible execution prefix
  - Triage 的 action 是 per-task tier
  - TwinRouterBench 的 action 是 per-step tier/model
- 所以 Triage 不是 TwinRouterBench 的替代品，更像是它的 coarse prior / predecessor

### 11.4 它和你当前项目最相关的点是什么？
- 你现在已经看到 235b vs 397b 差异很大一部分来自 workflow fragility；Triage 提供的是另一类信号：repo-level structural health prior。
- 一个很自然的组合是：
  - 任务开始前：用 Triage 类特征给 initial tier / initial backbone prior
  - 任务执行中：再用 TwinRouterBench 类 state signal 做 step-level rerouting

## 12. 开源性与可复现性

### 12.1 代码、数据、配置、日志是否公开？
- 代码是否开源：当前未验证到公开仓库
- 数据 / benchmark 是否公开：论文中使用 SWE-bench Lite，基础 benchmark 公开；但 Triage 自身完整实验产物和脚本目前未验证到公开入口
- 配置 / 运行日志是否公开：未验证到

### 12.2 复现这篇论文的主要阻碍是什么？
- CodeHealth 指标本身带有 proprietary 风险
- issue 到目标文件的映射在真实部署里并不直接可得
- 论文更偏 protocol proposal，尚未看到完整 release package

### 12.3 我对其可复现性的判断
- 中等偏弱
- 想复现思路不难，想严格复现实验细节并不容易

## 13. 对 Coding Agentic Router 的直接启发

### 13.1 哪个部件最值得拿来复用？
- `repo-health / file-health prior`
- `verification-aware cost equation`
- `pilot go/no-go falsification gate`

### 13.2 哪些不该照搬？
- 不该把 task-level 一次性 routing 当成最终形态
- 不该假设 issue 总能准确映射到目标文件
- 不该只依赖静态 code health，而忽略 execution-state fragility

### 13.3 如果把它映射到你的系统分层？
- 初始 backbone prior：强相关
- budget controller：弱相关
- workflow controller：几乎无直接内容
- granularity controller：无
- recovery gate：只有最简单 fallback
- observability：中等，有利于解释初始选择

### 13.4 对你当前双轨目标的具体作用
- 对 General Router：它启发“domain-specific metadata 可以成为 router 输入”，不一定只能看 query text
- 对 Coding Agentic Router：它启发“先验难度估计可以放在 runtime controller 之前做 coarse pre-routing”

## 14. 我会把它放在你的阅读地图什么位置？
- 更接近 Track B 的前置先验层，而不是核心 execution-time router
- 如果按系统层次看，它适合放在：
  - `issue + repo metadata -> initial backbone prior`
- 如果按论文关系看，它适合作为 TwinRouterBench 的对照读物：
  - 它回答“任务开始前怎么粗分档”
  - TwinRouterBench 回答“执行中每一步怎么再细分档”

## 15. 我的最终结论
- 这篇论文真正重要的不是它已经证明 code health routing 一定有效，而是它把“coding agent 的 task-level routing”从泛化 query routing 里独立出来，并给了一个严谨的、可证伪的 SE-specific 评估框架。
- 对你来说，它最值得吸收的不是最终 policy，而是：把 repo static health 视为 execution-time router 之前的一层 coarse prior；真正的 online routing 仍然需要 TwinRouterBench / 235b-vs-397b 这类 execution-state 证据来补完。
