# 当前仓库中的数据集与评测 Benchmark 总览

这份文档现在专门回答三件事：
1. 哪些是 benchmark，哪些是 dataset，哪些只是 method paper 里顺手释放的数据资产？
2. 这些资产的体量、类别、构建方式到底是什么？
3. 它们分别更服务于 general / coding-agentic / multimodal 哪条线？

## 1. 先给一个统一读法

### 1.1 benchmark-first
主要价值是：
- 统一 evaluator
- 统一 protocol
- 统一指标
- 统一 leaderboard 或离线比较基准

### 1.2 dataset-first
主要价值是：
- 训练 router / controller
- 扩样本
- 做 cold-start
- 做 preference / judge / profile / budget 学习

### 1.3 现在最常见的混淆
- benchmark paper 不等于没有训练资产
- method paper 不等于没有重要 dataset
- 一条资产对 general 有用，不代表它对 coding-agentic 的作用方式相同

## 2. 跨三条主线的资产总表

| track | 资产 | 类型 | 当前笔记里可确认的体量 | 类别 | 构建方式 | 最适合干什么 |
|---|---|---|---|---|---|---|
| general | RouterBench | benchmark | 8 数据集 / 64 任务 / 11 主模型 / 40.5 万+ 模型结果 | text-only query routing | 预跑多模型输出、质量、成本，冻结成离线表 | 做 frozen evaluator、benchmark ablation |
| general | RouterArena | benchmark | 8400 queries；23 源数据集；9 domains；44 categories；raw pool 约 6.2 万 | text-only query routing | 从更大 raw query 池清洗、分层、平台化评测 | 做 live leaderboard 与开放对比 |
| general | Arena preference + Dgold + Djudge | dataset | 80k + 1500 + 120k | 偏好学习 / binary routing supervision | 人类偏好 + gold label + GPT-4 judge | 训练 RouteLLM 类强弱路由器 |
| general | SPROUT | dataset | 约 44,241 query；6 benchmark；15 LLM | multi-model routing supervision | 统一采样 per-model response / score / cost | 训练 CARROT 类多模型 predictor |
| general | RouteProfile graph assets | dataset / profile asset | 15 profile datasets + 12 eval datasets；25 model graph；8 candidate models | candidate profile / cold-start | family/domain/task/query-level 信号构图 | 新模型接入、candidate 表示学习 |
| general | R2-Bench | dataset / benchmark hybrid | 当前笔记未汇总总 query 数；核心是 per-query × per-model × per-budget 曲线 | model+budget routing | 为每个 model 采多 budget 响应并打 judge 分 | 训练 / 评估 joint model+budget router |
| coding-agentic | SWE-bench | benchmark | 当前综合文档阶段先保留类别定位，精确样本量以对应单篇笔记为准 | code-repair / repo-level | 官方 benchmark | 社区默认验收基座 |
| coding-agentic | SWE-Bench Pro | benchmark | 当前综合文档阶段先保留类别定位，精确样本量以对应单篇笔记为准 | harder evaluator | 更难、更工业、更抗污染的 benchmark 设计 | 更强验收场 |
| coding-agentic | SWE-PolyBench | benchmark | 当前综合文档阶段先保留类别定位，精确样本量以对应单篇笔记为准 | engineering-friendly benchmark | 更偏工程化协议 | 高频实验与回归 |
| coding-agentic | SWE-ContextBench | benchmark | 当前综合文档阶段先保留类别定位，精确样本量以对应单篇笔记为准 | memory / context evaluator | 更偏 context reuse 测试 | 测 memory 机制 |
| coding-agentic | TwinRouterBench | benchmark | 静态轨 970 rows / 520 trajectories；动态轨支持 500-case SWE-bench Verified；论文报告 100-case held-out | step-level agent routing | 强模型成功轨迹 -> step prefix -> downgrade-and-verify -> target tier | 训练/评估 execution-time router |
| coding-agentic | Triage protocol | dataset / labeling protocol | 300 tasks；3 tiers；每 task-tier 3 次运行；总 2700 runs | task-level tier labeling | 用 verification hindsight 定义 cheapest sufficient tier | 做 issue-level coarse prior |
| coding-agentic | SWE-bench-train | dataset | 当前综合文档阶段先保留资产定位，精确体量以对应单篇笔记为准 | 同分布训练数据 | benchmark family 衍生训练 split | 扩训练量 |
| coding-agentic | Multi-SWE-RL | dataset | 当前综合文档阶段先保留资产定位，精确体量以对应单篇笔记为准 | 多语言 coding-agent 训练资产 | Multi-SWE-bench 释放的训练数据资产 | 做多语言训练 / RL |
| coding-agentic | SWE-smith | dataset-building toolchain | 工具链，不是单一静态表 | synthetic data construction | 生成 SWE 风格任务/训练数据 | 扩数据与增强 |
| multimodal | MMR-Bench | benchmark | OCRBench 1000、SEED-Bench-2-Plus 2277、MMStar 1500、RealWorldQA 765、MathVista 1000、MathVerse 788、MathVision 3040 | OCR / VQA / visual math | 统一 outcome table、统一价格、固定 10 模型池 | 做 multimodal router evaluator |

## 3. 按任务线分别看

### 3.1 General 线：评测底座和训练资产已经比较清楚

#### benchmark-first
| 资产 | 最关键体量 | 构建方式 | 设计含义 |
|---|---|---|---|
| RouterBench | 8 数据集 / 64 任务 / 11 主模型 / 40.5 万+ 输出 | 预收集离线结果表 | 适合反复做离线 router 试验 |
| RouterArena | 8400 queries / 23 源数据集 / 9 domains / 44 categories | live platform + 多指标评测 | 适合持续接入新 router 和公开比较 |
| MMR-Bench | 7 多模态数据集 + 10 模型固定池 | 多模态 outcome table | 是 multimodal 版 evaluator 模板 |

#### dataset-first
| 资产 | 当前可确认体量 | 构建方式 | 用途 |
|---|---|---|---|
| Arena preference | 80k | 人类偏好 | 训练 binary router |
| Dgold | 约 1500 | golden labels | OOD 增强 |
| Djudge | 约 120k | GPT-4 judge | 大规模偏好补齐 |
| SPROUT | 约 44,241 query / 15 LLM | per-model response/score/cost 统一采集 | 训练 multi-model risk router |
| RouteProfile assets | 15 + 12 datasets；25 model graph | profile graph construction | candidate 表示 / cold-start |
| R2-Bench | 当前综合文档阶段先记为“多 budget 曲线数据资产”，精确总量以单篇笔记为准 | multi-budget sampling + judge | model+budget curve 学习 |

### 3.2 Coding-agentic 线：最该把 benchmark、training asset、label protocol 分开

#### benchmark-first
| 资产 | 当前可确认体量 | 类别 | 构建方式 | 用途 |
|---|---|---|---|---|
| SWE-bench | 当前综合文档阶段先保留 benchmark 定位，精确总量以单篇笔记为准 | code repair | 官方 benchmark | 社区默认主基线 |
| SWE-Bench Pro | 当前综合文档阶段先保留 benchmark 定位，精确总量以单篇笔记为准 | harder code repair | 官方 harder evaluator | 更强验收 |
| SWE-PolyBench | 当前综合文档阶段先保留 benchmark 定位，精确总量以单篇笔记为准 | engineering-friendly benchmark | benchmark-first | 高频工程实验 |
| SWE-ContextBench | 当前综合文档阶段先保留 benchmark 定位，精确总量以单篇笔记为准 | context/memory benchmark | benchmark-first | 测 memory / retrieval |
| TwinRouterBench | 970 rows / 520 trajectories；动态 500-case support | step-level agent routing | execution-verified step labeling | 直接服务 step-level router |

#### dataset-first / training-asset-first
| 资产 | 当前可确认体量 | 类别 | 构建方式 | 用途 |
|---|---|---|---|---|
| SWE-bench-train | 当前综合文档阶段先保留训练资产定位，精确体量以单篇笔记为准 | train split | 与 benchmark 同分布训练资产 | 扩训练量 |
| Multi-SWE-RL | 当前综合文档阶段先保留训练资产定位，精确体量以单篇笔记为准 | 多语言 RL / SFT 训练数据 | Multi-SWE-bench 释放资产 | 多语言 controller / agent 训练 |
| SWE-smith | 工具链，不是静态体量 | synthetic data generation | 自动造 SWE 风格数据 | 持续扩样本 |
| Triage hindsight labels | 300 tasks / 2700 runs | task-level tier label protocol | 运行多 tier，取 cheapest sufficient tier | 训练 issue-level triage |

### 3.3 Multimodal 线：现在只有一篇，但结构很完整

| 资产 | 体量 | 类别 | 构建方式 | 用途 |
|---|---|---|---|---|
| MMR-Bench | 7 数据集，总样本数可由各 split 相加得到 | OCR / VQA / visual math | 统一预跑 10 模型 outcome、统一价格与 scorer | 做 multimodal query router evaluator |

## 4. 这三条线各自最该优先补什么

### 4.1 如果你做 General Router
优先保留：
- RouterBench
- RouterArena
- SPROUT
- RouteProfile assets
- R2-Bench

原因：
- 这几项分别对应 evaluator、开放比较、multi-model policy、cold-start、budget joint action

### 4.2 如果你做 Coding-Agentic Router
优先保留：
- SWE-bench / SWE-Bench Pro / TwinRouterBench
- SWE-bench-train / Multi-SWE-RL / SWE-smith
- Triage 的 task-level hindsight label protocol

原因：
- benchmark 负责验收
- dataset 负责扩训练
- hindsight label protocol 负责生成 router supervision

### 4.3 如果你做 Multimodal Router
优先保留：
- MMR-Bench
- 后续应补更多 multimodal agent / screenshot-aware benchmark

原因：
- 现在 evaluator 基本有了，但 training asset 和 runtime benchmark 还没成型

## 5. 对你现在最有用的结论

### 结论 1
仓库里最值钱的数据资产，不一定在 benchmark PDF 名字里最显眼。
真正该盯的是：
- Arena preference / Djudge
- SPROUT
- RouteProfile graph assets
- R2-Bench
- SWE-bench-train / Multi-SWE-RL
- TwinRouterBench step rows

### 结论 2
如果你的目标是做 router，而不是只做 benchmark 复现，最该补齐的是 4 类数据：
- per-model quality/cost table
- candidate profile / metadata
- step-level runtime prefix label
- recovery / budget / escalation hindsight label

### 结论 3
现在 coding-agentic 线最缺的不是 evaluator 名字，而是：
- 训练用 step-level label
- repo health / task-level prior
- 失败模式与 recovery label

## 6. 一句话结论

> benchmark 是验收底座，dataset 是训练资产，label protocol 是把 benchmark 变成可学习 router supervision 的那一步；如果按这个视角整理，General 线最值钱的是 SPROUT / RouteProfile / R2-Bench，Coding-Agentic 线最值钱的是 TwinRouterBench step rows + SWE-bench-train / Multi-SWE-RL，Multimodal 线最值钱的是 MMR-Bench outcome table。