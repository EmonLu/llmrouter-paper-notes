# TwinRouterBench: Fast Static and Live Dynamic Evaluation for Realistic Agentic LLM Routing

## 1. 论文基本信息
- 标题：TwinRouterBench: Fast Static and Live Dynamic Evaluation for Realistic Agentic LLM Routing
- 作者 / 机构：Pei Yang, Wanyi Chen, Tongyun Yang, Pengbin Feng, Jiarong Xing, Wentao Guo, Yuhang Yao, Yuhang Han, Hanchen Li, Xu Wang, Zeyu Wang, Jie Xiao, Anjie Yang, Liang Tian, Lynn Ai, Eric Yang, Tianyu Shi；论文首页可见作者列表，正文未在当前抽取片段中完整展开机构映射
- 发表时间：2026-05-14（arXiv v1）
- 会议 / 期刊：arXiv:2605.18859 [cs.LG, cs.AI]
- 论文链接：https://arxiv.org/abs/2605.18859
- 代码链接：https://github.com/CommonstackAI/TwinRouterBench
- 本地 PDF：`pdfs/coding-agentic-multi-turn-benchmark-2605.18859-twinrouterbench.pdf`
- 抽取文本：`.tmp_pdftext/coding-agentic-multi-turn-benchmark-2605.18859-twinrouterbench.txt`
- 研究方向关键词：
  - `Agentic LLM Routing`
  - `Step-level Routing Benchmark`
  - `Coding Agent Evaluation`
  - `Static + Dynamic Evaluation`
  - `SWE-bench Verified`

## 2. 一句话总结
- 总结：这篇论文不是再提一个普通 query-level router，而是为 agent 轨迹里的逐步路由建立了一套可训练、可离线快速迭代、又能在线端到端验证的双轨 benchmark：静态轨给 step prefix 和 execution-verified tier label，动态轨在 SWE-bench Verified 上真实跑 agent，看 resolve rate 与真实 API 花费，证明 step-level supervision 可以训练出在真实动态执行里显著降本而不明显伤害成功率的 router。

## 3. 研究问题
### 3.1 核心问题是什么？
- 现有 router benchmark 基本都把“整个 query”作为一次路由决策对象。
- 但 coding agent、deep research、computer-use agent 的真实执行是多步的：一次用户请求会拆成很多 LLM 调用，每一步看到的 prefix、工具输出、日志、代码状态都不同。
- 因此真正有价值的问题不是“这个问题整体该选哪个模型”，而是“在轨迹的当前这一步，最便宜但仍足够的 tier 是什么”。

### 3.2 为什么这个问题重要？
- 对 agent 系统来说，很多成本不是出在最终 patch 生成那一步，而是出在前面的检索、分析、调试、工具调用等大量中间步骤。
- 如果还是 issue-level 一次性选模型，就会把很多明显可以降级的中间步骤也一并交给昂贵模型。
- 这篇论文的价值在于把“逐步路由”从概念变成一个可复现实验对象。

### 3.3 主要优化目标是什么？
- 目标类型：成本、成功率、评测速度、可复现性、训练监督可用性
- 我的理解：作者想解决的是 agentic routing 的评测底座问题，而不是只展示一个新 policy。

## 4. 方法概览
### 4.1 提出的方法是什么？
- 提出 TwinRouterBench，一个 step-level routing benchmark，包含两条互补轨道：
  1. 静态轨（static track）：给出 router-visible prefix 和 execution-verified target tier，可毫秒级离线打分，无需评测时在线 LLM judge。
  2. 动态轨（dynamic track）：用真实 agent harness 在 SWE-bench Verified 上逐步执行路由策略，最终看官方 resolution predicate 和真实 API spend。

### 4.1.1 核心直觉是什么？
- agent 路由应该基于“当前可见 prefix”做条件化逐步决策，而不是基于任务标题或整题摘要做一次性粗判。
- 如果每一步的 tier label 只靠 LLM judge 拍脑袋，会很不稳定；更可靠的办法是通过 end-to-end execution verification 反推出该步是否真的能安全降级。
- 真正能服务系统设计的 benchmark，不能只有静态标签，还必须有 live execution 的动态验证环节。

### 4.1.2 方法按步骤是怎么运行的？
- Step 1：先收集强模型成功跑通的原始轨迹。
  - SWE-bench 部分要求 Claude Opus 4.6 或 GPT-5.4 通过 mini-swe-agent 跑出通过官方 FAIL_TO_PASS 测试的 patch。
- Step 2：把每个轨迹拆成 step-level row，每一行暴露 router 在该步真实能看到的 prefix。
- Step 3：用 fixed downgrade-and-cascade protocol 搜索更低 tier 是否仍能保留最终任务成功。
- Step 4：如果降级后的 mixed-model trajectory 仍能 pass，则接受更低 tier；否则维持更高 tier。
- Step 5：对多步可执行 workload 做人工审计，校验 release label 是否已经接近 conditional optimum。
- Step 6：静态轨用确定性算分公式评估 router；动态轨则把 router 接入 mini-swe-agent，在 SWE-bench Verified 上真实执行整条轨迹。

### 4.1.3 如果把它压缩成伪代码 / 决策流，它长什么样？
- 静态数据构建：`strong successful trajectory -> extract router-visible prefixes -> downgrade one step under fixed protocol -> verify end-to-end pass -> assign cheapest sufficient tier`
- 静态评测：`predict tier for each row -> compute row/trajectory/cost metrics`
- 动态评测：`at each LLM call router selects concrete model -> run full agent trajectory -> compute official resolution + realized API cost + failure penalty`

### 4.2 Router 的输入是什么？
- 输入不是单个 user query，而是当前 step 的完整 router-visible prefix `x_i`。
- 包括：
  - system prompt
  - user request
  - 历史 assistant messages
  - tool outputs
  - retrieval snippets
  - logs
  - partial code edits

### 4.3 Router 的输出是什么？
- 输出是 tier `t_i ∈ {low, mid, mid_high, high}`。
- 动态轨里，tier 还会进一步映射到 locked pool 里的具体模型。

### 4.4 Routing 决策如何产生？
- 这篇 paper 主要提出 benchmark，不强绑定某一种 router。
- 文中评了：
  - SR-KNN
  - ClawRouter（rule-based）
  - UncommonRoute（rule-based）
  - UncommonRoute（trained）
  - Claude Opus 4.6 作为 LLM-as-router 诊断
- 作者自己训练的“trained UncommonRoute”本质上是一个轻量监督式 tier classifier。

### 4.5 是否需要训练 Router？
- 对 benchmark 本身：`否`
- 对被评 router：`可选`
- 论文里的 trained variant：`是`
  - 用 frozen BAAI/bge-small-en-v1.5 embedding + routing-time metadata
  - 训练一个带 L2 正则的 multinomial logistic regression
  - embedding 不做 fine-tune

### 4.6 涉及哪些学习机制？
- execution-verified label construction
- 轻量监督分类器
- calibration split 做置信度校准
- 但 benchmark 的核心价值仍是“label 和 evaluator 设计”，不是分类模型本身

## 5. 系统架构
### 5.1 整体 Pipeline
- 强模型成功轨迹采集
- step-level prefix 抽取
- fixed downgrade-and-cascade 搜索
- execution verification + manual audit
- static scorer
- dynamic SWE-bench harness
- leaderboard bill / resolve rate / API spend 汇总

### 5.2 包含哪些模型 / 模块？
- 一个固定的 11-model pool，跨 4 个 tier
- 静态轨只公开 tier label，不公开 vendor model id
- 动态轨使用 locked pool 中的具体模型 id
- 共享 agent harness：mini-swe-agent v2.2.8

### 5.3 路由发生在哪个阶段？
- 路由发生在每一次 LLM call 之前，而不是整个 issue 只路由一次。
- 这是这篇 paper 和传统 RouterBench / RouterArena / issue-level Triage 最关键的区别。

### 5.4 是否支持 fallback / cascade / online update？
- benchmark 构建阶段明确使用 downgrade-and-cascade protocol 搜 label。
- 动态评测允许 policy 在每一步选不同模型。
- 论文没有提出在线学习 router，本身主要是评测与监督底座。

### 5.5 我的理解
- 这篇 paper 对你现在的 Coding Agentic Router 方向特别有价值，因为它第一次把“step-level routing for real agents”做成了一个成体系 benchmark。
- 它不是简单把 SWE-bench 当 single-query 任务，而是真正把轨迹内部的中间步骤暴露给 router。

### 5.6 如果新增一个候选模型，router 需要付出什么代价？
- benchmark 的 label 与 score 绑定固定 11-model pool、tier membership 和价格表。
- 因此如果加入新模型并改变 pool / tier / pricing，原则上要重新标注或至少重新定义 benchmark 版本。
- 这说明它比 RouterArena 更“任务内生”，但也更依赖当前模型生态快照。

## 6. 实验设置
### 6.1 使用了哪些数据集？
- 静态轨：970 个 step-level rows，来自 520 个 trajectory instances，覆盖 5 个 benchmark：
  - SWE-bench
  - BFCL
  - mtRAG
  - QMSum
  - PinchBench
- 动态轨：支持完整 500-case SWE-bench Verified；论文里实际报告 100-case held-out split。

### 6.1.1 数据集是怎么来的？
- 不是直接从公开 benchmark 文本抽一行做 label。
- 而是：先拿强模型成功轨迹，再在固定协议下对其中某步做 downgrade 搜索，并用 end-to-end execution 是否仍然 pass 来反推出该步的 cheapest sufficient tier。
- 这是它和纯静态 LLM judge 方案的根本差别。

### 6.1.2 数据集里具体包含什么？
- 每行字段包括：
  - `id`
  - `benchmark`
  - `instance_id`
  - `step_index`
  - `total_steps`
  - `messages`
  - `target_tier`
  - `target_tier_id`
- 公共 JSONL 不暴露 vendor model id，只暴露 tier。

### 6.1.3 这些数据集和真实 agent 场景有多接近？
- 很接近真实 agent routing 场景，因为它把中间 step、tool outputs、日志、partial code edits 都纳入 prefix。
- 比 issue-level / one-shot router benchmark 更接近你要做的 execution-time router。
- 但它的动态轨目前主要集中在 SWE-bench Verified，覆盖面仍然偏 coding agent。

### 6.2 对比了哪些 Baseline？
- SR-KNN（in-sample upper bound）
- ClawRouter（rule-based）
- UncommonRoute（rule-based）
- UncommonRoute（trained）
- Claude Opus 4.6 作为 LLM-as-router case study

### 6.3 评估了哪些任务类型？
- 长上下文
- multi-turn agent execution
- tool-use
- RAG
- summarization
- code-repair

### 6.4 使用了哪些大模型或专家模型？
- 固定 11-model pool，分成 4 个 capability/cost tiers
- 强轨迹种子来源里明确提到 Claude Opus 4.6 和 GPT-5.4
- 动态轨里用 locked model pool 真实付费运行

### 6.5 主要评估指标是什么？
- 静态轨：
  - ROW PASS
  - ROW EXACT
  - TRAJ PASS
  - COST SAVE
  - COMBINED
- 动态轨：
  - Resolved
  - Avg. API cost
  - API cost
  - Penalty cost
  - Leaderboard bill

## 7. 核心结果
### 7.1 最重要的实验结果是什么？
- 静态轨共有 970 rows，可在毫秒级离线打分，不需要 evaluator-side online LLM judge。
- 动态轨在 100-case held-out SWE-bench Verified 上证明：只用静态轨 supervision 训练出的 logistic router，就能在接近相同 resolve rate 下大幅降本。
- 具体地：
  - UncommonRoute（trained）：75/100 resolved，API cost $25.66，penalty $15.00，leaderboard bill $40.66
  - Opus 4.6（no routing）：74/100 resolved，API cost $54.73，penalty $15.60，leaderboard bill $70.33
- 也就是在成功率基本持平的前提下，把真实 API cost 降了约 53.1%。

### 7.2 相比 Baseline 提升了什么？
- 相对 unrouted Opus 4.6：
  - 75 vs 74 resolved，成功率没有明显恶化
  - API cost 从 $54.73 降到 $25.66，降幅约 53.1%
- 相对 rule-based UncommonRoute：
  - API cost 低约 6.7 倍
  - leaderboard bill 从 $188.76 降到 $40.66
- 这说明“有 execution-verified static supervision 的轻量 trained router”比拍规则更靠谱。

### 7.3 trade-off 如何？
- 这篇 paper 的核心结论不是“永远更低成本”，而是“通过 failure-aware cost accounting，把错误降级的代价真正算进去之后，仍然能看到 step-level routing 的真实收益”。
- 作者显式避免了一个常见陷阱：低 tier 省下来的 token 不能在 trajectory fail 时被错误记成收益。

### 7.4 Ablation / Sensitivity / Appendix 关键补充
- 人工审计：抽样 64 个多步 step，63 个被判为 tight，只有 1 个 SWE-bench step 被认定还能再降一级，并在 release 前被修正。
- Opus-as-router 诊断：在 300 个有效 SWE-bench rows 上，Claude Opus 4.6 对 147 个 verified-high steps 只预测出 7 个 high，并且 40 条 SWE 轨迹全部失败。
- 这支持了作者的一个重要论点：强模型直接 prompt 成 router，并不能替代 execution-verified supervision。

## 8. 贡献与创新点
### 8.1 主要贡献
- 提出 step-level routing benchmark，而不是继续停留在 query-level / issue-level。
- 提出 static + dynamic 的双轨评测闭环。
- 提出 execution-verified label construction，而不是依赖评测时在线 LLM judge。
- 证明 static track 不只是 evaluator，还能提供有效训练监督。

### 8.2 相比已有方法的新意
- 相比 RouterBench / RouterArena：它关心的是 agent 轨迹内部的中间步骤，而不是完整 query 一次决策。
- 相比 Triage：它不是每个 SWE issue 只选一次 tier，而是在执行中逐步路由。
- 相比 TRIM：它不是在数学 reasoning 上做抽象 step routing，而是进入 tool-use、shell trace、code state 这些真实 agent prefix。

### 8.3 创新类型
- benchmark / evaluator 创新
- 数据构造与标签协议创新
- routing supervision 设计创新

## 9. 局限性
### 9.1 方法假设
- cheapest-sufficient tier 依赖固定 11-model pool、tier 分组和价格快照。
- 标签依赖固定 downgrade-and-cascade protocol。

### 9.2 依赖特定模型 / 数据 / 标注吗？
- 依赖强模型成功轨迹作为种子。
- 依赖固定模型池与价格表。
- 对多步 workload 还依赖人工审计做最终校验。

### 9.3 泛化、稳定性、成本、延迟、部署问题
- 静态轨只有 970 rows、520 instances，足以做第一版诊断，但远非穷尽。
- 动态验证目前主要是 SWE-bench Verified，跨其他 agent benchmark 的 live coverage 还不够。
- 随着模型价格和能力变化，旧 label 可能会变陈旧。

### 9.4 作者自己提到的 limitation
- 静态语料规模仍有限。
- tier labels 与固定 model pool / price frontier 强绑定，未来需要 re-labeling。
- 动态覆盖超出 SWE-bench Verified 的部分仍是未来工作。

### 9.5 我认为的潜在问题
- 这个 benchmark 很强地绑定了“当前商业模型价格生态”，后续维护成本不低。
- 对真正 production router 来说，除了 tier，还可能需要联动 budget、tool policy、retry policy；TwinRouterBench 目前只评 model-tier 决策。

## 10. 对我的启发
### 10.1 对 agentic router 的帮助
- 最重要的启发：Coding Agentic Router 不能只做 issue-level routing，必须明确 step-level routing 的状态接口。
- 你如果以后做 SWE-bench agent runtime router，最有价值的输入对象应该是“当前 prefix + 工具状态 + 历史执行上下文”，而不是 issue 描述本身。

### 10.2 可借鉴的方法部件
- static supervision + dynamic validation 双轨闭环
- failure-aware cost accounting
- router-visible prefix 明确定义
- 用 end-to-end pass 反推 intermediate step sufficiency

### 10.3 可扩展想法
- 可以把现在的 mini-swe-agent 运行日志切成 step-level prefix 数据，先做你自己的 TwinRouterBench-lite。
- 除了路由模型 tier，还可以在相同框架下继续标注：
  - 是否需要更多 reasoning budget
  - 是否应该切换 agent mode
  - 是否应该调用更强 verifier / retriever

### 10.4 适用场景
- coding agent
- deep research system
- computer-use agent
- 多工具、多轮、多状态前缀的 agent execution

## 11. 可复现性记录
### 11.1 是否开源代码？
- 是。GitHub：https://github.com/CommonstackAI/TwinRouterBench

### 11.2 是否开源数据？
- 是。摘要明确写明 code and data are available；从论文描述看 release package 包含 locked data 和 scoring code。

### 11.3 关键实现细节是否清楚？
- 相对清楚。
- 公开了：
  - row schema
  - static scoring protocol
  - dynamic scoring formula
  - gamma penalty
  - logistic router 的训练特征与模型
  - mini-swe-agent 版本

### 11.4 复现难度
- 中等。
- 静态轨复现较容易；动态轨由于需要真实 API 跑 SWE-bench Verified，成本更高。

### 11.5 如果我要复现，第一步应该做什么？
- 先把静态轨 JSONL 和 scorer 跑通，确认自己能复现 Table 2。
- 然后再把 router 接进 mini-swe-agent harness，跑 100-case 动态验证。

## 12. 横向比较字段
- Routing 对象：agent trajectory 中的每次 LLM call
- Routing 粒度：step-level / prefix-level
- Router 类型：tier classifier / step router
- 是否训练：可训练，但 benchmark 本身不要求
- 训练信号：execution-verified tier labels
- 优化目标：在尽量不损失 trajectory success 的前提下降低真实 API 成本
- 支持的模型数量：固定 11-model pool，4 个 tier
- 是否考虑成本：是
- 是否考虑延迟：静态轨不主打延迟；动态轨主打 resolve + spend
- 是否 online：动态轨是 live execution；但不是在线学习
- 是否开源：是
- 主要优点：首次把真实 agent step-level routing 做成可训练、可动态验证 benchmark
- 主要缺点：依赖固定模型池与价格快照，当前动态覆盖面仍偏 SWE-bench

## 13. 阅读后的评分
- 相关性：9.5/10
- 方法新颖性：8.8/10
- 实验可信度：9.1/10
- 工程可落地性：9.4/10
- 对我研究 / 工作的启发：9.8/10

### 总评
- 是否值得精读：非常值得。
- 最短结论：如果 RouterArena 更像 Track A 的“query-level router leaderboard”，那 TwinRouterBench 就是 Track B / Coding Agentic Router 更贴近的一层评测底座：它真正把 routing decision 下沉到了 agent 运行中的每一步。