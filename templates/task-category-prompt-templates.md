# 按任务类别划分的提示词模板

这份文件专门存放“你以后可以直接复制给 Hermes 的提示词模板”。

目标不是写成抽象说明，而是给出可直接复用的、中文优先的 prompt 块。

适用场景：
- 新 ingest 一篇 paper 后，让 Hermes 继续精读
- 新 paper 含 dataset / benchmark / label protocol 时，要求同步更新总览文档
- 按不同任务类别（general / coding-agentic / multimodal）使用不同关注点
- 按不同资料类型（method / dataset / benchmark / survey / repo）切换不同模板

---

## 0. 使用方法

推荐工作流：

1. 先运行自动 ingest：

`python3 auto_generate_paper_note.py /path/to/paper.pdf --copy`

2. 再从下面挑一个最接近的模板，替换其中的 `<新文件>.md` 或 `<论文标题>` 后直接发给 Hermes。

3. 如果这篇 paper 含 dataset / benchmark / label asset，优先使用“带同步更新总览文档”的版本。

---

## 1. 通用基础版

适合：
- 你刚 ingest 完一篇 paper
- 暂时不想细分类型
- 先要一个高强度精读版

可直接复制：

请继续按仓库当前高强度标准精读 `papers/<新文件>.md`。
要求：
1. 补齐 appendix 里的模型表、开源链接、数据开放状态、可复现信息
2. 清理所有待补、TODO、不确定占位
3. 强调算法流程、router 输入输出、router 自身模型、候选模型池、评测协议
4. 最后给出“这篇 paper 对我做 router 设计最有用的结论”
如果这篇 paper 含 dataset、benchmark 或 label protocol，请同时更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`
- `coding-agent-datasets-comparison.md`（如果属于 coding-agent 方向）

---

## 2. General 类模板

### 2.1 General / Method

适合：
- query-level router
- budget-aware router
- profile / cold-start / candidate representation
- cascade / escalation / risk minimization

可直接复制：

请按 general router 方向高强度精读 `papers/<新文件>.md`。
这篇 paper 请重点补齐：
1. 算法核心直觉
2. step-by-step 决策流程
3. router 的输入、输出、决策机制
4. router 本身用的模型、大小、是否训练
5. 候选模型池由哪些模型组成，模型差异如何被利用
6. 如果新增一个候选模型，是否需要重训、重标、重跑 benchmark
7. 这篇方法更适合放在 policy、profile、budget 还是 cascade 层
最后请给出：
- 它最适合服务我 general router 的哪一层
- 它最不适合直接照搬的部分
如果出现 dataset / benchmark / label asset，请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`

### 2.2 General / Dataset

适合：
- SPROUT 这类训练资产
- Arena preference / Dgold / Djudge 这类监督资产
- RouteProfile graph assets 这类 candidate-side 资产
- R2-Bench 这类带 budget 曲线数据

可直接复制：

请按 general router 的 dataset-first 视角精读 `papers/<新文件>.md`。
不要把它只写成“这篇论文用了哪些 benchmark”，而要重点回答：
1. 这个数据资产的样本粒度是什么：query、query×model、query×model×budget，还是 pairwise preference
2. 显式字段有哪些
3. 标签类型是什么：answer、score、preference、budget、tier 等
4. 是否包含 per-model outcome、cost、token、response
5. 它更适合做 evaluator、training asset，还是 label protocol
6. 对 general router 来说，它更适合训练哪一层：binary router、multi-model predictor、candidate profile、budget router
请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`
并在单篇笔记中明确写出你对其 schema 家族的判断。

### 2.3 General / Benchmark

适合：
- RouterBench
- RouterArena
- 其他 leaderboard / evaluator / benchmark protocol

可直接复制：

请按 general router evaluator 视角高强度精读 `papers/<新文件>.md`。
重点不要放在“提出了什么新 policy”，而是回答：
1. 这个 benchmark 到底评什么对象：模型、router、还是 router-of-routers
2. 样本粒度是什么：query、query×model outcome table，还是平台协议
3. 显式字段和评测结果字段有哪些
4. 指标体系有哪些：accuracy、cost、optimality、robustness、latency 等
5. 它更像 frozen offline evaluator，还是 live leaderboard / open platform
6. 如果以后接入一个新 router 或新模型，代价在哪里
7. 对我 general router 研究，最值得复用的是 evaluator、数据 schema，还是 leaderboard protocol
如果这篇 paper 带数据集或字段结构描述，请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`

### 2.4 General / Survey

适合：
- general routing survey
- method-family comparison
- 动态 routing / cascading 综述

可直接复制：

请按 general router 设计综述的标准精读 `papers/<新文件>.md`。
不要只做摘要，请重点输出：
1. 这个综述把 routing 方法分成了哪些主线
2. 每条主线的核心信号、优点、缺点、适用场景
3. 它是否讨论 candidate model pool 设计、冷启动、新模型接入成本
4. 它对 benchmark / dataset / evaluator 的总结是否足够系统
5. 它对我 general router 的 policy、profile、budget、cascade 四层分别有什么帮助
如果综述里提到关键 dataset / benchmark / training asset，请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`
- `papers/COMPARISON.md`

---

## 3. Coding-Agentic 类模板

### 3.1 Coding-Agentic / Method

适合：
- task prior
- workflow controller
- granularity control
- budget gate
- recovery / escalation
- memory / retrieval support

可直接复制：

请按 coding-agentic router 方向高强度精读 `papers/<新文件>.md`。
这篇 paper 不要只按 query router 去理解，而要重点回答：
1. 它控制的是哪一层：task prior、workflow、granularity、budget、recovery、memory，还是 runtime substrate
2. 输入 state 到底包含哪些信号：issue、repo health、messages、tool outputs、logs、partial edits、telemetry 等
3. 输出动作是什么：tier、model、budget、workflow mode、granularity mode，还是 escalation action
4. 决策是 task-level、step-level，还是 trajectory-level
5. 它最像 benchmark、method，还是 label protocol
6. 它对我的 coding-agent router 哪一层最有帮助，哪些部分不能直接照搬
如果这篇 paper 含 dataset、benchmark 或 hindsight label，请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`
- `coding-agent-datasets-comparison.md`
- `papers/AGENTIC_COMPARISON.md`

### 3.2 Coding-Agentic / Dataset

适合：
- SWE-bench-train
- Multi-SWE-RL
- Multi-SWE-bench
- 其他可训练资产

可直接复制：

请按 coding-agentic dataset-first 视角精读 `papers/<新文件>.md`。
重点不要只写 benchmark 介绍，而要回答：
1. 它是 benchmark、dataset，还是 dataset-building toolchain
2. 样本粒度是什么：issue、trajectory、step、synthetic seed，还是 repo-level task
3. 显式字段有哪些
4. 标签是什么：resolved、tier、patch、budget、tool choice，还是只含最终答案
5. 它和 SWE-bench / SWE-bench Lite / Verified 的分布关系是什么
6. 它更适合补训练量、做 step supervision，还是做 hindsight label
请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`
- `coding-agent-datasets-comparison.md`

### 3.3 Coding-Agentic / Benchmark

适合：
- TwinRouterBench
- SWE-bench family
- SWE-Bench Pro
- SWE-PolyBench
- SWE-ContextBench

可直接复制：

请按 coding-agentic benchmark 视角高强度精读 `papers/<新文件>.md`。
重点回答：
1. 这是 issue-level benchmark、step-level benchmark，还是 dynamic live eval
2. 样本粒度与显式字段是什么
3. 它评的是最终 resolved、step-level routing、memory/context，还是 budget/recovery
4. 是否提供 execution-verified hindsight label
5. 它更像 evaluator，还是同时可转成训练 supervision
6. 它和 SWE-bench family 的关系是什么
请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`
- `coding-agent-datasets-comparison.md`
- `papers/AGENTIC_COMPARISON.md`

### 3.4 Coding-Agentic / Repo

适合：
- UncommonRoute 一类 repo note
- 实现型 control plane / deployment repo

可直接复制：

请按 coding-agentic repo note 的标准整理 `papers/<新文件>.md`。
不要把它当普通 paper summary，而要重点写：
1. 这个仓库到底是什么，解决的是 benchmark 问题还是 deployment/control-plane 问题
2. 主要模块、代码结构、router 工作流、协议层、预算层、反馈层、可观测性层分别做什么
3. 它和相关 benchmark / paper 的关系是什么
4. 它最值得我复用的系统设计点是什么
5. 哪些实现细节不能直接照搬
如果 repo 依赖或公开了数据资产 / benchmark schema / calibration split，请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`
- `coding-agent-datasets-comparison.md`
- `papers/AGENTIC_COMPARISON.md`

### 3.5 Coding-Agentic / Runtime-Architecture 机制论文

适合：
- agent runtime architecture
- permission / memory / tool semantics / subagent orchestration
- 更适合 `agentic-paper-template.md` 的论文

可直接复制：

请用 `templates/agentic-paper-template.md` 的风格重写或精修 `papers/<新文件>.md`。
重点不要写候选模型池，而要重点写：
1. agent loop / runtime control flow
2. state / context / memory schema
3. tool-use / environment interaction model
4. permission / approval / safety boundary
5. extensibility / orchestration / subagent mechanism
6. observability / recovery / rollback / escalation
7. 它对 coding-agent runtime router 的直接启发
如果文中出现 benchmark、dataset、label schema，请同步更新相关总览文档。

---

## 4. Multimodal 类模板

### 4.1 Multimodal / Benchmark

适合：
- MMR-Bench
- multimodal router evaluator
- screenshot / GUI / diagram-aware routing benchmark

可直接复制：

请按 multimodal router benchmark 视角高强度精读 `papers/<新文件>.md`。
重点回答：
1. 它的输入是哪些模态：text、image、document、chart、GUI screenshot 等
2. 样本粒度是什么：multimodal query，还是 query×model outcome table
3. 显式字段有哪些：query、image/input、per-model output、utility、cost 等
4. 它如何把 multimodal signal 接进 router
5. 它更像 text-only RouterBench 的扩展，还是完全不同的 evaluator
6. 对未来 screenshot-aware / GUI-aware coding-agent router 有什么启发
请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`

### 4.2 Multimodal / Method

适合：
- multimodal routing method
- 融合视觉/文本特征做 routing 的论文

可直接复制：

请按 multimodal routing method 视角精读 `papers/<新文件>.md`。
重点回答：
1. 它的 router 输入除了文本以外还有哪些模态信号
2. 融合方式是什么：early fusion、late fusion、cross-modal attention、冻结 embedding 等
3. 输出动作仍然只是选模型，还是还包含 budget / cascade / confidence
4. 候选模型池是固定多模态模型池，还是异构 text-only + vision-model 混合池
5. 它对 screenshot / GUI / diagram-aware agent state 的设计启发是什么
如果含 benchmark 或数据字段，请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`

---

## 5. 按资料类型补充的短模板

### 5.1 只做“新增 paper 后的同步更新”

可直接复制：

请检查 `papers/<新文件>.md` 是否包含 dataset、benchmark 或 label protocol。
如果有，请同步更新：
- `datasets-and-benchmarks-overview.md`
- `dataset-schema-comparison.md`
- `coding-agent-datasets-comparison.md`（若适用）
并明确补齐：
- 样本粒度
- 显式字段列表
- 标签类型
- 是否含 per-model outcome
- 是否含 runtime state
- schema 家族判断

### 5.2 只做“把单篇 paper 归档进 schema 文档”

可直接复制：

请不要重写全文，只做数据资产归档工作：
1. 判断 `papers/<新文件>.md` 里的数据资产属于哪一类 schema
2. 提取显式字段、样本粒度、标签类型
3. 更新 `dataset-schema-comparison.md`
4. 如果它同时影响 general / coding-agentic / multimodal 总览，也同步更新相关 overview 文档

### 5.3 只做“补齐单篇 paper 中的数据字段部分”

可直接复制：

请只精修 `papers/<新文件>.md` 中和 dataset / benchmark 相关的部分。
重点补齐：
- 样本粒度
- 显式字段列表
- 标签类型
- outcome table / preference / budget curve / step prefix 的判断
- 对我 router 训练或 evaluator 设计的具体价值
不要改动不相关章节。

---

## 6. 建议你固定使用的最小 prompt 组合

如果你想后续尽量少想，建议固定用这 4 套：

1. 新论文通用精读版
- 用“1. 通用基础版”

2. General 数据/benchmark 版
- 用“2.2 General / Dataset”或“2.3 General / Benchmark”

3. Coding-Agentic 数据/benchmark 版
- 用“3.2 Coding-Agentic / Dataset”或“3.3 Coding-Agentic / Benchmark”

4. Runtime 机制 / repo 版
- 用“3.4 Coding-Agentic / Repo”或“3.5 Coding-Agentic / Runtime-Architecture 机制论文”

---

## 7. 一句话结论

> 后续你不需要每次重新想怎么下指令；先判断这篇资料属于 `general / coding-agentic / multimodal` 哪条线、属于 `method / dataset / benchmark / survey / repo` 哪一类，然后直接复制对应 prompt 即可。