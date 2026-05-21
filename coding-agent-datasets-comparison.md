# Coding Agent 数据集 / Benchmark 对比表

这份文档不再按“每篇论文逐条填空”的方式写，而是改成更适合做选型的表格化对比。

核心目标只有三个：
- 这些数据集 / benchmark 各自在补什么空白？
- 它们更适合拿来训练 agent，还是更适合做 benchmark？
- 如果后面要做 coding agent router / runtime evaluator，应该优先用哪几个？

## 1. 本次已下载到仓库的 PDF

| 论文 / 报告 | 本地 PDF |
|---|---|
| SWE-bench | `pdfs/agentic-2024-swe-bench.pdf` |
| Multi-SWE-bench | `pdfs/agentic-2504.02605-multi-swe-bench.pdf` |
| SWE-PolyBench | `pdfs/agentic-2504.08703-swe-polybench.pdf` |
| SWE-Bench Pro | `pdfs/agentic-2025-swe-bench-pro.pdf` |
| SWE-ContextBench | `pdfs/agentic-2602.08316-swe-context-bench.pdf` |

## 2. 一页看懂：这 5 篇到底分别在补什么

| 名称 | 最核心要解决的问题 | 它在整个版图里的位置 | 最短判断 |
|---|---|---|---|
| SWE-bench | 给 coding agent 一个标准 repo-level issue resolving benchmark | 基础主基准 | 最权威、最默认、最该先对齐 |
| Multi-SWE-bench | 补足 SWE-bench 的单语言缺陷，并往训练数据社区延展 | 多语言 benchmark + RL 数据入口 | 最像“多语言评测 + 训练资源”二合一 |
| SWE-PolyBench | 做一个工程化更强、自动化更顺手的多语言 benchmark | 多语言 benchmark 基础设施 | 最适合反复跑实验 |
| SWE-Bench Pro | 补足 SWE-bench 难度不够、污染风险高、工业味不足的问题 | harder / enterprise benchmark | 最像后期验收集 |
| SWE-ContextBench | 不再只测是否做对，而是测能否复用历史经验 | memory / retrieval / context benchmark | 最贴 runtime / memory / context routing |

## 3. 主对比表：按“做研究/做系统时真正关心的维度”来比

| 名称 | 时间 / 来源 | 任务规模 | 语言覆盖 | 任务形态 | 公开性 | 官方 GitHub / star | 最适合做什么 | 最不适合做什么 | 一句话优缺点 |
|---|---|---:|---|---|---|---|---|---|---|
| SWE-bench | 2024，Princeton + PLI + UChicago | 2,294 benchmark 任务；另有 19,000 条 `SWE-bench-train` | Python | repo-level issue resolving，execution-based | 高，公开 benchmark + 训练数据 + eval harness | `SWE-bench/SWE-bench`，约 4985 star | 主 benchmark、和社区对齐、训练 open model / agent | 测多语言泛化、测视觉任务、测 memory reuse | 优点是权威度最高；缺点是 Python 偏置明显 |
| Multi-SWE-bench | 2025-04，ByteDance Seed | 1,632 benchmark；另有 4,723 条 `Multi-SWE-RL` | Java / TS / JS / Go / Rust / C / C++ | 多语言 issue resolving，容器化实例 | 高，benchmark + pipeline + RL 数据社区 | `multi-swe-bench/multi-swe-bench`，约 332 star | 多语言 benchmark、多语言 agent 训练、RL 数据起点 | 作为唯一主 benchmark 替代 SWE-bench | 优点是语言最广且兼顾训练；缺点是主流权威性仍弱于 SWE-bench |
| SWE-PolyBench | 2025-04，AWS AI Labs / Amazon Science | 2,110；另有 `SWE-PolyBench500` | Java / JS / TS / Python | repo-level、execution-based、带 task category 和 AST 指标 | 高，HF 数据集 + evaluation harness 公开 | `amazon-science/SWE-PolyBench`，约 84 star | 自动化 benchmark、快速反复实验、低成本 ablation | 作为训练主数据集 | 优点是工程化最顺手；缺点是训练属性较弱 |
| SWE-Bench Pro | 2025，Scale AI | 1,865 = public 731 + commercial 276 + held-out 858 | 论文中明确出现 Python / JS / TS / Go，整体偏多语言工业仓库 | long-horizon、enterprise-level issue resolving | 中，public 部分公开，held-out / commercial 不公开 | `scaleapi/SWE-bench_Pro-os`，约 395 star | harder benchmark、工业化 benchmark、抗污染评测 | 开放训练主语料 | 优点是更难更真实；缺点是不完全公开、复现性较弱 |
| SWE-ContextBench | 2026-02 / 2026-05，Oxford / Edinburgh / TUM / MBZUAI / NUS / CMU / MemoraX AI 等 | 1,476 = 1,100 base + 376 related；Lite 399 | Python / JS / Ruby / Rust / Java / Go / PHP / C / C++ | 跨任务 context reuse / retrieval / memory benchmark | 中，论文公开；本次未检索到明确官方仓库 | 未检索到明确官方官方 repo，star 暂无法统计 | memory / retrieval / context learning 研究，runtime router 研究 | 作为大规模训练主语料 | 优点是问题意识最新；缺点是生态还早、入口不如前几篇成熟 |

## 4. 如果按“训练价值 vs 评测价值”来比

### 4.1 训练价值 / benchmark 价值 / router 价值矩阵

| 名称 | 训练价值 | benchmark 价值 | 对 coding agent router / runtime 的价值 | 说明 |
|---|---|---|---|---|
| SWE-bench | 高 | 很高 | 中高 | 是主 benchmark，同时有 `SWE-bench-train`，但更偏 Python 单任务解题 |
| Multi-SWE-bench | 很高 | 高 | 中高 | `Multi-SWE-RL` 让它在训练侧非常强，但主流主榜地位还不如 SWE-bench |
| SWE-PolyBench | 中 | 高 | 中 | 更像标准化 evaluator，不是训练集中心设计 |
| SWE-Bench Pro | 低 | 很高 | 高 | 更适合做 harder / deployment-style evaluator，不适合开放训练 |
| SWE-ContextBench | 低到中 | 高（机制型） | 很高 | 最适合研究 memory / retrieval / context routing，不适合主训练底座 |

### 4.2 最适合拿来训练 agent 的资源

| 排名 | 名称 | 为什么 |
|---|---|---|
| 1 | `Multi-SWE-RL`（来自 Multi-SWE-bench） | 明确就是面向 RL / agent training 的容器化 issue-resolving 数据 |
| 2 | `SWE-bench-train` | 官方训练数据，和主 benchmark 对齐度高 |
| 3 | SWE-PolyBench | 可以辅助训练，但设计主轴是 benchmark，不是训练集 |
| 4 | SWE-ContextBench | 更适合 memory / summarization / retrieval 机制研究 |
| 5 | SWE-Bench Pro | 高价值部分不公开，更适合测而不是训 |

### 4.3 最适合拿来做 benchmark 的资源

| 排名 | 名称 | 为什么 |
|---|---|---|
| 1 | SWE-bench | 社区默认主 benchmark |
| 2 | SWE-Bench Pro | 更难、更像真实工业任务 |
| 3 | SWE-PolyBench | 工程化最好，适合规范横评 |
| 4 | Multi-SWE-bench | 多语言很强，但主流共识稍弱 |
| 5 | SWE-ContextBench | 更偏机制 benchmark，不是通用主榜 benchmark |

## 5. 如果按“你想测什么能力”来选

| 你真正想测的能力 | 最合适的数据集 / benchmark | 次优选择 | 为什么 |
|---|---|---|---|
| 主线 repo-level issue resolving 能力 | SWE-bench | SWE-bench Verified | 社区共识最强，最容易和已有工作直接对齐 |
| 更可信、更稳定的主榜对比 | SWE-bench Verified | SWE-bench | Verified 人工验证，更适合 apples-to-apples 对比 |
| 低成本快速迭代 | SWE-bench Lite | SWE-PolyBench500 | Lite 明确是为便宜、快、开发友好而设 |
| 多语言泛化 | Multi-SWE-bench / SWE-bench Multilingual | SWE-PolyBench | 前者更广，后者更兼容 SWE-bench 官方基础设施 |
| 自动化、规整、反复跑实验 | SWE-PolyBench | SWE-bench Lite | PolyBench 的 harness 和子集设计更适合工程迭代 |
| 更难、更像真实企业问题 | SWE-Bench Pro | SWE-bench | Pro 明确补 harder / enterprise / contamination resistance |
| memory / retrieval / context reuse | SWE-ContextBench | —— | 它就是围绕这个问题设计的 |
| UI / 视觉相关软件问题 | SWE-bench Multimodal | —— | 官方 SWE-bench 家族里专门补视觉证据 |

## 6. SWE-bench 官方家族：不要和配套训练/检索资源混在一起

### 6.1 benchmark 本体对比表

| SWE-bench 家族成员 | 官方定位 | 规模 | 核心差异 | 最适合的场景 | 不足 |
|---|---|---:|---|---|---|
| SWE-bench Full / Original | 主 benchmark | 2,294 | 完整版、主榜、最标准 | 最终主结果、和历史工作对齐 | 成本高、Python 偏置强 |
| SWE-bench Verified | human-validated 子集 | 500 | 人工确认可解、质量更稳 | 可信 leaderboard、公平横比 | 规模较小，仍是 Python 主线 |
| SWE-bench Lite | 低成本子集 | 300 + 23 dev | 更便宜、更快、更偏 self-contained bug fixes | 开发期、ablation、日常回归 | 不能完全代表复杂 long-horizon 问题 |
| SWE-bench Multilingual | 多语言官方扩展 | 300 | 42 仓库、9 语言、保持 SWE-bench 兼容 | 多语言泛化评测 | 覆盖广但不算深，规模仍小 |
| SWE-bench Multimodal | 多模态官方扩展 | 517 | 引入截图 / UI / mockup / visual context | 测视觉软件域、多模态 agent | test split 私有，复现和提交门槛更高 |

### 6.2 配套资源对比表

| 配套资源 | 性质 | 主要用途 | 什么时候看它 |
|---|---|---|---|
| `SWE-bench-train` | 训练数据 | 训练 open model / agent | 你要训而不是只测 |
| `Oracle Retrieval` / `BM25 Retrieval 13K/27K/40K/50K` | 检索预处理数据 | 做 RAG / retrieval baseline | 你想研究 retrieval 而不是纯 agent scaffold |
| `SWE-smith` | 训练数据构造工具链 | 扩展 SWE 风格训练数据 | 你想自己造 agent training data |

### 6.3 SWE-bench 家族的实际选型建议

| 使用目标 | 推荐 | 原因 |
|---|---|---|
| 主榜 / 主结论 | Verified + Full | Verified 更稳，Full 更完整 |
| 日常开发回归 | Lite | 便宜、快、迭代友好 |
| 多语言泛化 | Multilingual | 官方兼容、适合测试语言迁移 |
| 视觉软件问题 | Multimodal | 只有它显式处理视觉证据 |
| 训练 agent | `SWE-bench-train` / `SWE-smith` | benchmark 子集本身不是训练资源 |

## 7. 5 篇论文的“最强优点 / 最明显短板”表

| 名称 | 最强优点 | 最明显短板 |
|---|---|---|
| SWE-bench | 权威度最高，主流工作都认 | Python 偏置强 |
| Multi-SWE-bench | 多语言 + RL 训练数据一起给 | 主流共识还没压过 SWE-bench 主线 |
| SWE-PolyBench | benchmark 工程化最好，最适合反复跑 | 训练属性弱 |
| SWE-Bench Pro | 更难、更真、更抗污染 | 不完全公开 |
| SWE-ContextBench | 直接把 context learning 做成 benchmark | 官方生态和入口还不够成熟 |

## 8. 如果只保留一套“研究工作台”组合，怎么配

| 角色 | 推荐数据集 / benchmark | 作用 |
|---|---|---|
| 主 benchmark | SWE-bench / SWE-bench Verified | 保证和主流工作对齐 |
| harder benchmark | SWE-Bench Pro | 看系统在高难、工业、抗污染场景下是否还能成立 |
| multilingual benchmark | Multi-SWE-bench + SWE-PolyBench + SWE-bench Multilingual | 看语言泛化和工程可复现性 |
| memory / context benchmark | SWE-ContextBench | 看 runtime memory / retrieval / context reuse |
| 训练数据底座 | SWE-bench-train + Multi-SWE-RL + SWE-smith | 训练 open agent / synthetic agent 数据扩展 |
| 日常开发回归 | SWE-bench Lite | 快速验证路由、提示词、scaffold 改动 |

## 9. 最短结论

| 问题 | 最短答案 |
|---|---|
| 最权威的 coding agent benchmark 是谁？ | `SWE-bench` |
| 最适合做多语言 benchmark 的是谁？ | `Multi-SWE-bench` 和 `SWE-PolyBench`；如果只看官方 SWE-bench 家族，则是 `SWE-bench Multilingual` |
| 最适合做 harder evaluator 的是谁？ | `SWE-Bench Pro` |
| 最适合研究 memory / retrieval / context routing 的是谁？ | `SWE-ContextBench` |
| 最适合做日常开发回归的是谁？ | `SWE-bench Lite` |
| 最适合拿来训练 agent 的公开资源是谁？ | `SWE-bench-train`、`Multi-SWE-RL`、`SWE-smith` |

## 10. 建议后续纳入的 coding agent benchmark / training data 候选

这里要分两种情况看，因为“补 benchmark”和“补训练数据”不是同一个优化目标。

你现在更准确的真实用法是：
- 用 `SWE-bench Lite` 作为训练集
- 配合 `mini-swe-agent` 跑不同 LLM
- 当前瓶颈不是主 benchmark 不够，而是训练数据量不够

所以对你来说，当前第一优先级不应该是继续补一个新的 benchmark，而应该先补“可直接扩训练量”的数据源。

因此这部分我改成两套口径：
- 训练数据优先：优先补能直接扩大训练样本量的资源
- benchmark 优先：优先补能提高评测覆盖面的 benchmark

### 10.1 如果当前瓶颈是训练数据量不够，优先顺序应该这样排

| 排名 | 候选 | 为什么现在更该优先看它 |
|---|---|---|
| 1 | `SWE-bench-train` | 和你现在的 `SWE-bench Lite + mini-swe-agent` 体系最兼容，分布最接近，迁移成本最低，最像直接把训练集从“小样本”扩成“同分布大样本” |
| 2 | `Multi-SWE-RL`（来自 Multi-SWE-bench） | 这是当前最像正式训练资源的公开补充，明确面向 agent / RL 训练，而且是容器化 issue-resolving 实例，和你的 runtime 训练设定更贴 |
| 3 | `SWE-Bench++` | 它的价值不是单个 benchmark 分数，而是能持续生成大规模 repo-level 训练 / 评测实例；如果你后面要解决“训练量总是不够”的问题，它比单加一个静态 benchmark 更关键 |
| 4 | `SWE-smith` | 更偏训练数据生产工具链，适合你后面做合成扩增，但优先级略低于已经成型的现成训练资源 |
| 5 | SWE-bench Live | 很有价值，但它优先解决的是 benchmark 动态性和抗污染，不是你当下最急的训练数据量问题 |

最短结论：
如果你当前真瓶颈是“训练数据太少”，那我现在最建议你优先补的不是 `SWE-bench Live`，而是：
1. `SWE-bench-train`
2. `Multi-SWE-RL`
3. `SWE-Bench++`

### 10.2 如果以后你要补评测覆盖面，再看 benchmark 候选总表

| 候选 | 当前判断 | 为什么值得关注 | 和你现有版图的关系 | 建议优先级 |
|---|---|---|---|---|
| SWE-bench Live | 强烈建议纳入 | 它补的是“静态 benchmark 老化 / 污染 / 覆盖窄”的问题，强调 live-updatable、持续扩展、抗污染 | 很适合补在 `SWE-bench` 之后，成为更接近真实线上环境的动态 benchmark | 最高 |
| SWE-bench-java | 建议纳入 | 它是较正式的 Java repo-level issue resolving benchmark，公开了 dataset、Docker eval env、leaderboard | 适合作为 `SWE-bench` 从 Python 向单语言扩展的代表节点 | 高 |
| SWE-Bench++ | 建议关注并可纳入 | 它不只是一个 benchmark，而是 benchmark 生成框架；覆盖 11 语言、11,133 个实例、3,971 个仓库 | 很适合补“可扩展 benchmark 工厂 / 自动造 benchmark”这条新线 | 中高 |
| SWE-Bench-CL | 暂不优先 | 方向有意思，测 continual learning / experience accumulation，但和 `SWE-ContextBench` 有一定重叠 | 更像 memory / online adaptation 的专项机制 benchmark | 中 |
| Saving SWE-Bench | 暂不建议按 benchmark 本体纳入 | 更像 benchmark mutation / realism transformation 方法，而不是独立 benchmark 资产 | 更适合以后写“benchmark realism / 真实交互形态”专题时引用 | 低 |
| SWE-Bench+ | 暂不建议纳入主表 | 更像对 SWE-bench 质量问题的分析与增强，不像一个独立主线 benchmark | 适合引用，不适合现在作为主成员扩表 | 低 |
| UTBoost | 暂不建议按数据集纳入 | 更像评测增强 / 测试增强方法，不是新的 benchmark 主体 | 适合放到“评测 protocol 增强”脉络，不适合放主表 | 低 |
| SWE-Bench 5G | 暂不建议现在纳入 | 太垂直，偏 telecom network engineering domain-specific benchmark | 可以留作以后整理“行业垂类 SWE benchmark”时再补 | 低 |

### 10.3 我最建议你下一步补的 3 个（按训练数据优先）

| 排名 | 候选 | 为什么它比其他候选更值得先补 |
|---|---|---|
| 1 | `SWE-bench-train` | 它和你当前的 `SWE-bench Lite + mini-swe-agent` 设定最兼容，几乎是最低迁移成本的训练量扩展方案 |
| 2 | `Multi-SWE-RL` | 它是目前最明确面向 agent / RL 的公开训练资源之一，适合把训练分布从 Python 主线扩到更广的 repo-level issue-resolving 空间 |
| 3 | `SWE-Bench++` | 如果你想系统性解决“训练量总是不够”，那可扩展 benchmark / training instance generation framework 的长期价值非常高 |

### 10.4 如果你的目标转成“补评测覆盖面”，再看 benchmark 优先级

| 维度 | 结论 |
|---|---|
| 它补的空白 | 不是“再多一个 benchmark”，而是补 `SWE-bench` 静态、老化、易污染的问题 |
| 已核到的信息 | arXiv `2505.23419`；标题 `SWE-bench Goes Live!`；初始 `1,319` tasks；覆盖 `93` repositories；有 homepage / code / dataset 入口 |
| 对你当前方向的价值 | 很适合做 coding agent router 的后验评测场，尤其适合研究新模型上线后如何避免只在旧 benchmark 上刷分 |
| 放进文档后的角色 | 可以放成 `SWE-bench` 之后的“动态现实版 benchmark” |

### 10.5 为什么 SWE-bench-java 值得补，但排在 Live 后面

| 维度 | 结论 |
|---|---|
| 它补的空白 | 把 `SWE-bench` 从 Python 主线扩到 Java repo-level issue resolving |
| 已核到的信息 | arXiv `2408.14354`；标题 `SWE-bench-java: A GitHub Issue Resolving Benchmark for Java`；论文明确写了公开 dataset、Docker-based evaluation environment、leaderboard |
| 优点 | 非常适合补“单语言扩展 benchmark”这个生态节点 |
| 为什么不是第一 | 它补的是语言覆盖，而不是 benchmark 范式本身的升级；相对来说没有 `SWE-bench Live` 那么强的系统意义 |

### 10.5 为什么 SWE-Bench++ 值得放进候选池

| 维度 | 结论 |
|---|---|
| 它补的空白 | 不只是扩 benchmark，而是把 benchmark 生成流程做成框架 |
| 已核到的信息 | arXiv `2512.17419`；标题 `SWE-Bench++: A Framework for the Scalable Generation of Software Engineering Benchmarks from Open-Source Repositories`；摘要给出 `11,133` instances、`3,971` repositories、`11` languages |
| 最大价值 | 对长期建设 benchmark 工厂、持续扩容训练/评测数据、降低人工构造成本很重要 |
| 为什么目前先放候选而不是立刻主推 | 目前我还没像 `SWE-bench Live` 那样核到同等清晰度的官方入口和生态信号，所以更适合先列为高潜力候选 |

### 10.6 不建议现在扩进主表的几类候选

| 类型 | 代表 | 暂不优先的原因 |
|---|---|---|
| benchmark realism / mutation 方法 | `Saving SWE-Bench` | 更像 benchmark 改写方法，不是独立 benchmark 资产 |
| benchmark 质量分析 / 增强研究 | `SWE-Bench+` | 更适合作为引用材料，不适合作为当前主表成员 |
| evaluation protocol 增强方法 | `UTBoost` | 它强化的是评测严格性，不是新数据集本体 |
| 垂直行业 benchmark | `SWE-Bench 5G` | 太早期、太垂类，容易把当前主线打散 |
| continual learning 专项 benchmark | `SWE-Bench-CL` | 有价值，但和 `SWE-ContextBench` 的“跨任务经验复用”线有一定重叠，当前优先级不如 Live / Java / ++ |

### 10.7 如果按你当前工作台来落地，我建议的扩充顺序

| 阶段 | 推荐补入 | 目的 |
|---|---|---|
| 第一批 | SWE-bench Live | 补动态 benchmark / 抗污染 / 持续更新 |
| 第二批 | SWE-bench-java | 补单语言扩展生态节点 |
| 第三批 | SWE-Bench++ | 补 benchmark generation framework / benchmark factory |
| 后续专题再补 | SWE-Bench-CL / Saving SWE-Bench / UTBoost / SWE-Bench 5G | 等你后面分别写 continual learning、benchmark realism、evaluation protocol、domain-specific benchmark 时再纳入 |

## 11. 说明

| 项目 | 说明 |
|---|---|
| GitHub star | 为本次检索时的近似值，会随时间变化 |
| SWE-ContextBench 仓库 | 本次未检索到明确官方 GitHub 仓库，因此没有给官方 star |
| SWE-Bench Pro | 其高价值部分包含 held-out / commercial，因此 benchmark 价值高于训练价值 |
| Multi-SWE-bench | 要和 `Multi-SWE-RL` 一起看，否则会低估它在训练侧的价值 |
| SWE-bench 家族 | benchmark 本体（Full / Verified / Lite / Multilingual / Multimodal）和训练/检索配套资源应分开看 |
| 候选纳入原则 | 当前候选排序是基于“你已经在使用 `SWE-bench`，因此优先补非重复能力维度”这一前提 |
