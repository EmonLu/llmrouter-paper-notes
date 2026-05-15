# 三篇主综述对比：LLM Routing Surveys Comparison

## 1. 这份文档的目的

这不是再重复三篇 survey 的摘要，而是回答一个更实际的问题：

- 这三篇综述各自最适合承担什么角色？
- 如果我要围绕 `General Router` 和 `Coding Agentic Router` 继续设计系统，应该优先反复参考哪一篇？
- 这三篇并排读时，信息是互补的，还是重复的？

当前对比的三篇主综述是：

1. `2603.04445`
   - `Dynamic Model Routing and Cascading for Efficient LLM Inference: A Survey`
2. `2502.00409`
   - `Doing More with Less: A Survey on Routing Strategies for Resource Optimisation in Large Language Model-Based Systems`
3. `2506.06579`
   - `Towards Efficient Multi-LLM Inference: Characterization and Analysis of LLM Routing and Hierarchical Techniques`

---

## 2. 一句话定位

### 2.1 如果每篇只用一句话概括

- `2603.04445`：最适合做“方法空间地图”的主综述。
- `2502.00409`：最适合做“控制面 / system design 拆解”的主综述。
- `2506.06579`：最适合做“deployment-aware 约束与 evaluator 扩展”的补充综述。

### 2.2 如果只保留每篇最强的一点

- `2603.04445`
  - 最强点：把 routing 方法族讲清楚，尤其是六种 paradigm + `when / what / how`。
- `2502.00409`
  - 最强点：把 routing 重新定义成“带预算约束的系统资源优化器”，并且把 baseline / benchmark / onboard cost 问题提到台前。
- `2506.06579`
  - 最强点：把 memory / energy / scalability / edge-cloud / distributed inference 这些真实部署约束系统性拉进来。

---

## 3. 总表：三篇综述最核心的差异

| 维度 | 2603.04445 | 2502.00409 | 2506.06579 |
|---|---|---|---|
| 核心定位 | 方法 taxonomy survey | system-design / resource optimisation survey | deployment-aware / edge inference analysis |
| 最强视角 | 六种 routing 范式 + `when/what/how` | `optimize what / when route / how implement` 三问 | constraints matrix：compute/memory/energy/latency/scalability |
| 更偏算法还是系统 | 偏方法地图 | 偏系统控制平面 | 偏部署与评测平面 |
| 对 General Router 的价值 | 很高 | 非常高 | 高 |
| 对 Coding Agentic Router 的直接价值 | 中等 | 中等偏高 | 中等 |
| 对 evaluator 的启发 | 中等偏高 | 很高 | 很高 |
| 对 candidate onboarding 问题的重视 | 有，但不是最突出 | 很突出 | 有，但不如 2502.00409 突出 |
| 对 edge / distributed / infra feedback 的重视 | 有，但不是重点 | 有提及 | 非常突出 |
| 对 benchmark / baseline 标准化的推动 | 有 | 非常突出 | 突出 |
| 最适合作为什么 | 领域地图 | 设计主线 | 部署补强 |

---

## 4. 分别看：每篇到底最适合拿来做什么

### 4.1 `2603.04445`：领域地图

这篇最适合回答：
- 这个领域有哪些主要 routing 范式？
- difficulty-aware / preference-aligned / clustering / RL / uncertainty / cascading 之间到底差在哪里？
- 一篇 routing 论文大致应该落在哪个方法桶里？

它最适合承担的角色：
- 作为你整个仓库的“方法论地图”
- 作为 `survey-six-routing-paradigms.md` 的上游依据
- 作为把新论文快速归类进方法空间的母综述

它最强的地方：
- 分类最稳定
- 方法家族最清晰
- 对入门和建立全局认识最友好
- `when / what / how` 三维分析框架很适合长期复用

它的短板：
- 对 benchmark / baseline / 工业评测协议的推动不如 `2502.00409`
- 对 edge / memory / energy / distributed inference 的 deployment 约束讨论不如 `2506.06579`
- 对 candidate onboarding 成本不是最强重点

我的使用建议：
- 当我想问“这篇新论文属于什么范式”时，先看这篇
- 当我想给 `papers/INDEX.md` 继续做方法映射时，先看这篇
- 当我想梳理 Track A / Track B 共用的理论 vocabulary 时，也先看这篇

### 4.2 `2502.00409`：控制面设计主综述

这篇最适合回答：
- router 在系统里到底是在优化什么？
- routing 应该在 pre-generation 发生，还是 post-generation，还是 multi-stage？
- similarity / supervised / RL / generative 这些只是实现方式，真正的系统控制点在哪里？
- 为什么 benchmark / baseline / oracle gap 必须标准化？

它最适合承担的角色：
- 作为 `General Router` 的系统设计 grounding
- 作为 evaluator / baseline protocol 的设计依据
- 作为把 router 从“选模型器”提升成“系统控制器”的主综述

它最强的地方：
- 非常贴合 system design
- 明确指出 routing 对象不必只是模型，也可以是 prompt / retrieval / context / component
- 明确强调 benchmark + baseline 套件 + oracle gap
- 对“新增 routing option / 新 candidate 接入成本”问题更敏感

它的短板：
- taxonomy 不如 `2603.04445` 稳定和直观
- 对 edge / memory / distributed serving 约束没有 `2506.06579` 那么系统
- 对真正 agent runtime 里的 trajectory / recovery / workflow control 仍然只是哲学前导，不是完整方案

我的使用建议：
- 当我想问“General Router v1 到底应该长什么样”时，先看这篇
- 当我想设计 benchmark / baseline / evaluator 时，优先看这篇
- 当我想把 routing object 从 `model` 扩展到 `prompt/retrieval/context/workflow` 时，优先看这篇

### 4.3 `2506.06579`：部署与约束补强综述

这篇最适合回答：
- 如果把 routing / HI 放进真实 edge-cloud deployment 环境，到底应该看哪些成本项？
- 为什么 memory / energy / scalability / modality compatibility 不能继续被忽略？
- 如何把 routing 评估从 cloud-only API cost 扩展到 deployment-aware evaluator？

它最适合承担的角色：
- 作为 deployment-aware 补充综述
- 作为 `General Router evaluator` 的约束扩展文献
- 作为以后做 infra-aware / runtime telemetry-aware router 的启发来源

它最强的地方：
- 对 deployment constraints 的覆盖最完整
- Table II / III / IV / V 这种“约束覆盖 / benchmark / open questions”整理对系统设计很有价值
- 提出了 IES（Inference Efficiency Score）作为统一指标雏形
- 对 multimodality、distributed inference、privacy-aware routing 的开放问题组织得很清楚

它的短板：
- 方法 taxonomy 深度不如 `2603.04445`
- control-plane 组织感不如 `2502.00409`
- 对 onboarding 新模型 / 新 candidate 的机制性讨论不算最强

我的使用建议：
- 当我想补强 evaluator 时看这篇
- 当我想把 router 从“省 token 成本”推进到“真实 deployment optimizer”时看这篇
- 当我以后要接 edge / local / on-prem / distributed serving 约束时看这篇

---

## 5. 三篇综述之间的互补关系

### 5.1 它们不是重复，而是三张不同的图

我现在更倾向把它们理解成三张互补的图：

1. `2603.04445` = 方法空间图
- 回答：有哪些范式？它们有什么优缺点？

2. `2502.00409` = 控制面设计图
- 回答：系统里应该优化什么、何时路由、怎么做决策？

3. `2506.06579` = 部署面约束图
- 回答：真实部署里有哪些资源与基础设施约束必须进 evaluator？

### 5.2 如果并排读，它们的分工很明确

- 先用 `2603.04445` 建立方法 vocabulary
- 再用 `2502.00409` 决定系统控制平面的组织方式
- 再用 `2506.06579` 把 evaluator / serving / deployment constraints 补完整

### 5.3 如果混成一篇会丢什么信息

- 只看 `2603.04445`
  - 你会知道“有哪些方法”
  - 但不一定知道“怎样把这些方法组织成系统控制面”
- 只看 `2502.00409`
  - 你会知道“如何搭系统”
  - 但不一定形成最稳固的 method taxonomy
- 只看 `2506.06579`
  - 你会很清楚 deployment constraints
  - 但会缺少方法地图和控制面设计的完整性

---

## 6. 对两个最终目标的作用对比

### 6.1 对 `General Router` 的价值排序

我的当前排序：

1. `2502.00409`
2. `2603.04445`
3. `2506.06579`

原因：
- `General Router` 最核心的是：
  - query-time decision
  - quality-cost-latency objective
  - clean policy family
  - standardized benchmark/baseline
- 这几点里，`2502.00409` 和你的目标贴合得最直接
- `2603.04445` 负责补方法地图
- `2506.06579` 负责补 deployment 侧 evaluator 与 serving constraints

### 6.2 对 `Coding Agentic Router` 的价值排序

我的当前排序：

1. `2502.00409`
2. `2603.04445`
3. `2506.06579`

但这里三篇的“直接性”都没有对 `General Router` 那么高。

原因：
- `Coding Agentic Router` 真正需要的还有：
  - trajectory state
  - runtime budget control
  - workflow / granularity / recovery actions
- 这三篇更多提供的是哲学与控制思路，而不是 agent runtime policy 的完整框架
- 其中 `2502.00409` 对“routing 不只发生在 generation step”这点最有启发
- `2506.06579` 对 infra feedback / edge-cloud / deployment telemetry 有额外价值

### 6.3 它们对两个 target 的分工

- 对 `General Router`
  - `2603.04445`：方法图谱
  - `2502.00409`：系统设计主线
  - `2506.06579`：deployment-aware evaluator 补强

- 对 `Coding Agentic Router`
  - `2603.04445`：可借用 uncertainty / cascade / RL 这些范式语言
  - `2502.00409`：可借用“routing object 不只限于模型”的系统思想
  - `2506.06579`：可借用 runtime system metrics / infra feedback / edge-cloud offloading 的约束意识

---

## 7. 横向比较：优点、缺点、适用场景

### 7.1 `2603.04445`

优点：
- taxonomy 最清楚
- 方法语言最标准
- 很适合做长期知识库的上层地图

缺点：
- 对 benchmark / baseline / standardized evaluation 的系统设计感不如 2502.00409
- deployment constraints 讨论不够深

最适合：
- 建方法索引
- 给新论文分桶
- 建立共用术语体系

### 7.2 `2502.00409`

优点：
- system-design 感最强
- 把 routing object 扩展到系统组件层
- 对 benchmark / baseline / oracle gap 的意识最强
- 对新 candidate onboarding 问题最敏感

缺点：
- taxonomy 没有 2603.04445 那么“稳定好记”
- 对 deployment constraints 的覆盖没有 2506.06579 深

最适合：
- 设计 General Router
- 设计 evaluator protocol
- 设计 benchmark / baseline 套件

### 7.3 `2506.06579`

优点：
- deployment-aware 约束最完整
- memory / energy / scalability / edge-cloud / privacy 维度最系统
- 对 evaluator 扩展很有帮助

缺点：
- 算法 taxonomy 深度一般
- control-plane 组织感略弱
- 更像 analysis + characterization，而不是直接的 design 主纲

最适合：
- 补 evaluator
- 补 serving constraints
- 补 edge / distributed / infra-aware router 思路

---

## 8. 如果只想做一件事，应该先看哪篇？

### 8.1 想快速搞懂领域全貌
- 先看：`2603.04445`

### 8.2 想开始设计 `General Router`
- 先看：`2502.00409`

### 8.3 想把 evaluator 做得更接近真实部署
- 先看：`2506.06579`

### 8.4 想判断一篇新论文应该放到哪条主线
- 先看：`2603.04445`
- 再用：`2502.00409`

### 8.5 想知道系统里还缺哪些 deployment-aware 维度
- 先看：`2506.06579`

---

## 9. 我现在对这三篇综述的最终建议

### 9.1 不建议删成只剩一篇

我不建议只保留一篇，因为它们承担的是不同角色：
- 一篇做地图
- 一篇做设计
- 一篇做部署补强

### 9.2 最合理的保留方式

我建议在仓库里把它们当作一个稳定三件套：

- `2603.04445` = taxonomy anchor
- `2502.00409` = design anchor
- `2506.06579` = deployment anchor

### 9.3 对后续文档的使用原则

以后写任何与 router 设计有关的文档时，我建议默认这样引用：

- 如果是“方法分类 / 阅读导航 / 新论文归类”
  - 优先引用 `2603.04445`
- 如果是“系统设计 / v1 spec / evaluator / candidate onboarding”
  - 优先引用 `2502.00409`
- 如果是“deployment / serving / edge-cloud / infra metrics / scalability”
  - 优先引用 `2506.06579`

---

## 10. 一句话结论

> 这三篇综述不是重复收藏，而是三张不同但互补的设计图：`2603.04445` 负责告诉你“有哪些 routing 范式”，`2502.00409` 负责告诉你“一个 router 系统该如何组织控制面”，`2506.06579` 负责告诉你“真实部署时 evaluator 和 serving 约束还缺什么”。