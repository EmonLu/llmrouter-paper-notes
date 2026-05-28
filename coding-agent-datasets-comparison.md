# Coding Agent 数据集 / Benchmark 对比表

这份文档现在只做一件事：
把 coding-agent 方向里“评测底座、训练资产、监督标签协议”彻底拆开。

## 1. 先给最短结论

如果你现在在做 `coding-agent router`，脑子里最好固定三层：
- benchmark：拿来验收
- dataset：拿来训练 / 扩样本
- label protocol：拿 benchmark 运行结果反推 router 监督信号

在当前仓库里：
- `TwinRouterBench` 最接近 step-level benchmark
- `SWE-bench / SWE-Bench Pro / SWE-PolyBench / SWE-ContextBench` 更像验收底座
- `SWE-bench-train / Multi-SWE-RL / SWE-smith` 更像训练资产
- `Triage` 其实给的是 task-level hindsight label protocol

## 2. 主对比表：别再把它们混成一类

| 名称 / 资产 | 主身份 | 当前可确认体量 | 类别 | 构建方式 | 最适合干什么 | 对 router 的直接价值 |
|---|---|---|---|---|---|---|
| SWE-bench | benchmark | 当前综合文档阶段先保留 benchmark 定位，精确体量以单篇笔记为准 | repo-level code repair | 官方 benchmark protocol | 做主验收 | 给 resolved / unresolved 最终标签 |
| SWE-Bench Pro | benchmark | 当前综合文档阶段先保留 benchmark 定位，精确体量以单篇笔记为准 | harder industrial benchmark | benchmark-first | 做 harder evaluator | 测 robustness，防“只会 Lite” |
| SWE-PolyBench | benchmark | 当前综合文档阶段先保留 benchmark 定位，精确体量以单篇笔记为准 | engineering-friendly benchmark | benchmark-first | 高频实验与回归 | 更适合反复跑工程实验 |
| SWE-ContextBench | benchmark | 当前综合文档阶段先保留 benchmark 定位，精确体量以单篇笔记为准 | memory / context benchmark | benchmark-first | 测 retrieval / memory | 把 context 机制从 backbone 里拆出来测 |
| TwinRouterBench static track | benchmark + label asset | 970 step rows / 520 trajectories | step-level router supervision | 强模型成功轨迹 -> step prefix -> downgrade-and-verify -> cheapest sufficient tier | 训练 step router、离线打分 | 直接给 execution-time router 标签 |
| TwinRouterBench dynamic track | benchmark | 支持完整 500-case SWE-bench Verified；论文报告 100-case held-out | live agent routing eval | 真实 agent harness + penalty-aware bill | 测真实 resolve/cost trade-off | 验证静态 supervision 是否真能迁移到动态执行 |
| SWE-bench-train | dataset | 当前综合文档阶段先保留训练资产定位，精确体量以单篇笔记为准 | 同分布训练集 | benchmark family 中的 train split | 扩训练量 | 训练 backbone / router / verifier |
| Multi-SWE-RL | dataset | 当前综合文档阶段先保留训练资产定位，精确体量以单篇笔记为准 | 多语言 agent / RL 训练数据 | Multi-SWE-bench 释放资产 | 多语言或更大规模 controller 训练 | 扩大训练覆盖面 |
| SWE-smith | dataset-building toolchain | 工具链，不是静态表 | synthetic data construction | 自动生成 SWE 风格任务或训练数据 | 持续扩样本 | 做 task prior / router 监督数据扩增 |
| Triage hindsight labels | label protocol | 300 tasks；3 tiers；每 task-tier 3 runs；共 2700 runs | task-level tier label | 跑全 tier，再取 cheapest sufficient tier | 训练 issue-level coarse prior | 让 router 在开跑前就有先验 |

## 3. 如果按“对 router 训练最有用的监督”来排

### 3.1 最直接可学的 supervision
1. TwinRouterBench static rows
   - 输入是当前 step prefix
   - 标签是 cheapest sufficient tier
   - 最适合做 step-level classifier / scorer

2. Triage hindsight labels
   - 输入是 issue + repo health + target-file features
   - 标签是 cheapest sufficient task tier
   - 最适合做 pre-run prior

3. SWE-bench-train / Multi-SWE-RL
   - 更像 backbone / policy / verifier 的训练数据
   - 对 router 也有用，但需要你自己加工成 routing labels

### 3.2 最直接的评测底座
1. SWE-bench / SWE-Bench Pro
2. TwinRouterBench dynamic track
3. SWE-ContextBench
4. SWE-PolyBench

## 4. 真正该记的数据字段

### 4.1 benchmark 该记什么
- 是否是 issue-level 还是 step-level
- 是否是真实动态执行还是静态离线打分
- success / cost / penalty 怎么算
- 有没有 failure-aware accounting

### 4.2 dataset 该记什么
- 样本到底是 task、step、trajectory，还是 synthetic seed
- 标签是 resolved、tier、budget、tool choice，还是 only final answer
- 是否和 benchmark 同分布
- 能否支持新 backbone / 新 router 的训练

### 4.3 label protocol 该记什么
- label 是不是 execution-verified hindsight label
- 标签粒度是 task / step / failure mode / recovery action 哪一种
- 新模型加入后是否要重标

## 5. 当前最值得固定的设计判断

### 5.1 如果你卡在训练数据量不够
优先补：
- SWE-bench-train
- Multi-SWE-RL
- SWE-smith

原因：
- 这三者解决的是“量不够”
- 不是“再多一个 benchmark 名字”

### 5.2 如果你卡在 router label 不够
优先补：
- TwinRouterBench-lite（用你的 mini-swe-agent 轨迹切 step prefix）
- Triage-lite（给 task-level prior 打 hindsight tier）
- 失败模式标签（比如 search stall / tool misuse / wrong-file / under-budget）

### 5.3 如果你卡在评测不够全面
优先保留：
- SWE-bench / SWE-Bench Pro：最终 resolve
- TwinRouterBench：step-level routing
- SWE-ContextBench：memory/context 机制
- SWE-PolyBench：工程化反复实验

## 6. 对你当前 router 项目最直接的落点

### 6.1 训练层
- 用 SWE-bench-train / Multi-SWE-RL 补 backbone 训练量
- 用你现有 235B vs 397B 轨迹，构造“哪一步小模型不够”的 step 标签

### 6.2 router 层
- task-level：做 Triage-style coarse prior
- step-level：做 TwinRouterBench-style prefix router
- recovery-level：额外标“失败后该加预算、该升模型、还是该换 workflow”

### 6.3 评测层
- 最终是否 resolved：看 SWE-bench / SWE-Bench Pro
- step 级是否路由对：看 TwinRouterBench-style static scorer
- context / retrieval 是否真有帮助：看 SWE-ContextBench 类 evaluator

## 7. 一句话结论

> 对 coding-agent router 来说，最值钱的不是“又一个 benchmark 名字”，而是能不能把 benchmark 变成 label：TwinRouterBench 给 step label，Triage 给 task-level label，SWE-bench-train / Multi-SWE-RL 给训练量，SWE-Bench Pro 给最终更难验收场。