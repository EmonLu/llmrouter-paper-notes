# General / Multimodal Router 跨论文对比

这份文件不再只是“哪些 paper 值得读”。
它现在直接回答 6 个系统设计问题：
1. 每篇方法到底吃什么输入信号？
2. 决策机制是分类、打分、优化、cascade，还是 joint model+budget？
3. 它依赖哪些数据集，数据体量和构建方式是什么？
4. 推理成本主要花在哪里：router 本身、候选模型池，还是多次调用？
5. 如果 model pool 里加入一个新模型，代价到底高不高？
6. 它的优势、短板、最适合落到哪一层系统？

## 1. 先给结论：General Router 这条线已经可以拆成 5 层

### 1.1 evaluator / benchmark 层
- RouterBench：离线、冻结、可复现实验底座
- RouterArena：开放平台、live leaderboard、多维评价
- MMR-Bench：多模态固定池离线 evaluator

### 1.2 query-only policy 层
- RouteLLM：二元强弱模型路由，最适合做干净 baseline
- CARROT：多模型 risk minimization，最适合做主 policy 雏形
- OptLLM：多目标优化视角，适合离线批量 assignment
- IRT-Router：能力-难度匹配，解释性最好

### 1.3 candidate representation / cold-start 层
- RouteProfile：不是直接替代 router，而是补齐 candidate side representation

### 1.4 cascade / runtime extension 层
- FrugalGPT：早期 cascade 模板
- AutoMix：self-verification + escalation

### 1.5 model + budget joint action 层
- R2-Router：最关键的 bridge paper，把“选模型”扩展成“选模型+选预算”

## 2. General / Multimodal 关键论文横向总表

| 论文 | routing object | 数据/评测资产（体量、类别、构建方式） | 核心思想 | 输入信号 | 决策机制 | 推理成本与模型栈 | 新模型加入 model pool 的成本 | 优势 | 短板 |
|---|---|---|---|---|---|---|---|---|---|
| RouteLLM | query -> strong/weak model | Arena 80k preference；Dgold 约1500；Djudge 约120k；主要由人类偏好 + GPT-4 judge 构造 | 把路由写成“强模型是否值得调用”的偏好预测 | query 文本；可选 query embedding | win predictor + 阈值决策 | 主对：GPT-4 vs Mixtral-8x7B；泛化到 Claude 3 Opus/Sonnet、Llama 3.1 70B/8B；router 可是 BERT/Llama3-8B/MF，部署成本很低 | 中。若换新模型对，通常要重新收集偏好数据或重做 weak/strong 定义 | baseline 干净、实现简单、成本低 | 主要是二元路由；OOD 高度依赖增广数据；不直接支持大 model pool |
| CARROT | query -> one model in multi-model pool | SPROUT 约 44,241 query；6 个 benchmark；15 个 LLM；作者统一收集 per-model response/score/cost 构成训练资产 | 先预测每个模型的质量和成本，再做显式 risk minimization | query、candidate pool、风险权重 μ | multi-label performance/cost predictor + plug-in argmin | 候选覆盖 GPT-4o/Claude 3.5 Sonnet/Llama/Qwen/Mixtral 等；router 用 text-embedding-3-small、roberta-base 一类轻量模块 | 中到高。要为新模型补 query-level response、score、cost，并更新 predictor | 天生支持多模型；理论清楚；和系统目标一致 | 维护 model profiling 成本高；价格漂移或版本漂移会让 predictor 失效 |
| RouteProfile | query + candidate profile -> model | profile 构建用 15 个数据集；下游 routing eval 用 12 个数据集；25 个模型图，8 个候选模型池 | candidate 表示比 query encoder 更容易被忽略，结构化 profile 能显著改善 routing，尤其是新模型冷启动 | query 编码 + candidate profile（family/domain/task/query-level graph） | profile layer + downstream router（SimRouter/MLPRouter/GraphRouter） | 候选池 8 个模型，主力从 3B/7B/8B/9B 到 24B/70B/8x22B；router 自身主要是 Longformer + GNN | 低到中。相比重做全量标签，更接近“先补 profile 再接入” | 对 cold-start/new model 最有价值；可插拔到别的 router | 不直接解决 cost-aware routing；图构建仍有离线成本 |
| R2-Router | query -> (model, token budget) | R2-Bench：为每个 query-model 采多 budget 响应并打 judge 分；是 multi-budget outcome table，而不是单点标签 | 一个模型不是一个点，而是一条质量-成本曲线；联合选模型和预算 | query、trade-off λ、candidate pool、budget set | per-model multi-budget quality regression + utility maximization | query encoder 用 Qwen3-Embedding-0.6B；MLP 很轻；候选池从 0.6B/1.5B/3B/4B 到 235B 级 | 中到高。要给新模型补多 budget 曲线数据；若走 Uni-R2Router 可部分借 profile 降低代价 | 是从 query router 通向 agent budget router 的最好桥梁 | 依赖多 budget 数据构造；长度约束不稳定会伤效果 |
| IRT-Router | query -> model | 20 个候选模型；依赖 query × model 交互矩阵、profile embedding、新模型泛化实验 | 用 latent ability / difficulty / relevance 对 query 与模型做配对 | query embedding、candidate profile embedding、固定 cost、能力相关向量 | IRT-style latent matching | 候选含 GPT-4o、GPT-4o-mini、Llama3.1-8B/70B/405B、QwQ-32B 等 | 中。加入新模型需要补 profile embedding、warm-up 交互数据并更新矩阵 | 可解释性强；对“什么模型擅长什么能力”更透明 | 交互矩阵采样重；候选池频繁变化时维护成本不小 |
| OptLLM | batch of queries -> Pareto assignment set | 5 个 benchmark；训练/验证/测试 1%/1%/98%；少量已标注 query-LLM 交互 | 先预测 query 在各模型上的成功概率，再在 accuracy-cost 上做 Pareto 搜索 | query、candidate pool、成本表、predicted accuracy table | Random Forest predictor + destruction/reconstruction heuristic optimizer | NLP 任务上 12 个候选 LLM，来自 4 个 provider；更像离线分配而非在线 router | 中。候选池变化时要重新采样数据并训练 predictor | 多目标视角强；适合离线规划与 cost frontier 生成 | 在线逐请求场景不自然；延迟与 availability 没建模 |
| FrugalGPT | query -> cascade chain decision | HEADLINES / OVERRULING / COQA；依赖重新调用商业 API、训练 scorer、搜索 chain | 用廉价 scorer 判断当前回答是否接受，不够好再升级 | query、当前答案、预算、预设模型链 | scorer + threshold cascade | 12 个商业 API 模型；示例链如 GPT-J -> J1-L -> GPT-4；额外有 DistilBERT scorer | 中到高。价格一变、API 一变，最优链和阈值都要重学 | 早期系统模板非常清楚；质量-成本收益直观 | 多跳调用延迟高；严重依赖训练分布和 API 价格结构 |
| AutoMix | query -> stop/escalate in staged cascade | 多数据集；主打 two-model/three-model staged routing；更像系统框架而非 benchmark 资产 | 用 self-verification 信号决定是否升级到更强模型 | query、当前模型输出、自验证结果 | self-verification + POMDP / staged escalation | SLM 常用 GPT-3.5、LLaMA2-13B、Mistral-7B；LLM 常用 GPT-4 | 中。新增模型需重估 transition / verification 行为 | 比单次路由更贴近实际 runtime control | 依赖 closed API；控制逻辑比 RouteLLM 更复杂 |
| RouterBench | benchmark / evaluator | 8 个数据集、64 个任务、11 个主模型，离线收集 40.5 万+ 推理结果 | 把模型输出与 router 训练/评测解耦，建立统一 cost-quality 坐标系 | prompt/sample，外加离线 outcome table | benchmark + zero/oracle/KNN/MLP/cascade baselines | 主要成本在离线预采样多模型输出，不在 router 本体 | 高。新增模型基本要重跑离线结果表 | 是 General Router 最稳的 frozen evaluator | 不含真实线上 latency、availability、版本漂移 |
| RouterArena | open evaluation platform | 8400 queries；23 个源数据集；9 domains、44 categories；从约 6.2 万 raw query 筛到最终 benchmark | 不统一单个 pool，而是把 router 评测做成平台和 leaderboard | benchmark query + router API/predictions + 多维 metrics | 平台统一跑评测；各 router 保持原决策方式 | 兼容学术与商业 router；成本在平台评测与维护 | 低到中。更适合作为“接入新 router”的平台；但不同 router pool 不同 | 评测维度完整，最适合长期公共比较 | 不是严格控制变量实验；对 agentic runtime 帮助是间接的 |
| MMR-Bench | multimodal query -> one MLLM | 7 个数据集：OCRBench 1000、SEED-Bench-2-Plus 2277、MMStar 1500、RealWorldQA 765、MathVista 1000、MathVerse 788、MathVision 3040；统一 outcome table | multimodal routing 需要显式融合 text/image signal，而不是 text-only 难度估计 | text embedding、image embedding、模态可用性、trade-off λ | KNN/KMeans/Linear/MLP/MF/CMR 等 router family | 候选池 10 个模型，覆盖 3B/4B/7B/72B/78B 级开源 MLLM + GPT-5/Claude/Gemini 商业模型 | 高。加入新 MLLM 要全 benchmark 重跑 utility/cost 并重训 learned router | 多模态状态设计很有前瞻价值；33% 成本达到强单模表现 | 仍是 query-level benchmark，不是 multimodal agent runtime |

## 3. 数据资产该怎么分层看

### 3.1 benchmark-first
| 资产 | 体量 / 类别 | 构建方式 | 你该怎么用 |
|---|---|---|---|
| RouterBench | 8 数据集 / 64 任务 / 11 模型 / 40.5 万+ 结果 | 预收集多模型输出、成本、质量，冻结成离线表 | 做 frozen evaluator、跑 ablation、验证简单 router 是否真的有效 |
| RouterArena | 8400 queries / 23 源数据集 / 9 domains / 44 categories | 从更大 raw query 池清洗、分层、平台化 | 做开放比较、持续接入新 router、对照商业系统 |
| MMR-Bench | 7 个多模态数据集 / 10 模型固定池 | 统一预跑 outcome table + multimodal fusion benchmark | 做 multimodal routing evaluator |

### 3.2 dataset-first / training-asset-first
| 资产 | 体量 / 类别 | 构建方式 | 你该怎么用 |
|---|---|---|---|
| Arena preference / Dgold / Djudge | 80k + 1500 + 120k；偏 preference / supervision | 人类偏好 + gold + GPT-4 judge | 训练 query-only binary router |
| SPROUT | 约 44,241 query；6 benchmark；15 LLM | 为每个 query 收集 per-model response、score、cost | 训练 multi-model quality/cost predictor |
| RouteProfile interaction graph | 15 profile datasets + 12 eval datasets；25 model graph | family/domain/task/query-level 信号构图 | 做 candidate profile / cold-start 层 |
| R2-Bench | 当前笔记未统一记录总 query 数；是 per-query per-model per-budget 曲线数据 | 多 budget 采样 + judge 打分 + token cost 记录 | 训练 model+budget joint router |

## 4. 按你最关心的 5 个问题直接给答案

### 4.1 哪些方法主要看“query 本身”？
- RouteLLM
- CARROT
- OptLLM
- FrugalGPT（但会再看当前答案）

适合：
- query-level general router
- 不想维护太重 runtime state 的系统

局限：
- 对 agent runtime、tool trace、prefix state 支持弱

### 4.2 哪些方法开始显式建模 candidate model side？
- RouteProfile：最系统
- IRT-Router：ability / profile embedding
- R2-Router（扩展版 Uni-R2Router）：部分支持

含义：
- 这几篇更适合回答“新模型加入 pool 怎么办”
- 如果你后面 model zoo 经常换，这类工作比单纯的 query classifier 更重要

### 4.3 哪些方法的动作已经不只是 model id？
- R2-Router：model + budget
- FrugalGPT / AutoMix：accept / escalate / continue
- MMR-Bench：虽然 benchmark 本身还是选模型，但输入已不是 text-only

这点很关键：
- 你后面做 coding-agent router 时，动作空间不能只剩下“选 235B 还是 397B”

### 4.4 推理成本主要花在哪？
- RouteLLM / CARROT / RouteProfile / IRT：主要花在离线数据构建，在线 router 很便宜
- FrugalGPT / AutoMix：在线多跳调用成本更高，换来更强动态控制
- RouterBench / MMR-Bench：成本主要在 benchmark 预构建，不在部署期
- R2-Router：介于两者之间，离线多 budget profiling 昂贵，在线推理便宜

### 4.5 如果我要做长期可扩展的 General Router，优先级怎么排？
1. RouterBench / RouterArena：先把 evaluator 定稳
2. CARROT：做多模型主 policy
3. RouteProfile：补 candidate profile 与 cold-start
4. R2-Router：把预算显式并进动作空间
5. RouteLLM：保留为最干净 binary baseline

## 5. 对你自己的系统设计，最该固定的结论

### 结论 1
General Router 不该再只看“谁分数高”，而要拆成：
- evaluator
- policy
- candidate profile
- budget layer

### 结论 2
真正决定长期可扩展性的，不是单次 benchmark 分数，而是：
- 新模型接入要不要重打大规模标签
- router 是否把 candidate side 建模清楚
- evaluator 能不能跟着 model pool 演化

### 结论 3
如果你后面想把 Track A 平滑接到 coding-agentic router，最重要的桥梁就是：
- RouteProfile：解决新增模型与 cold-start
- R2-Router：解决 model + budget 联合动作
- FrugalGPT / AutoMix：解决 staged runtime control

## 6. 一句话结论

> General Router 这条线里，真正能直接服务系统设计的不是“再找一个分数更高的 query classifier”，而是把 benchmark、multi-model policy、candidate profile、budget action 这四层拆开；其中 CARROT 管主 policy，RouteProfile 管新模型接入，R2-Router 管预算，RouterBench/RouterArena/MMR-Bench 管评测底座。