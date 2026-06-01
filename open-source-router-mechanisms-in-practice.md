# 开源项目里真实落地的 Router 机制

这份文档不整理学术论文里的 router，而是整理“已经在开源项目里真实使用”的 router / fallback / 分流 / 预算 / 升级机制。

目标：
- 给你看哪些机制真的被项目采用了
- 帮你区分哪些是“研究论文常讲”，哪些是“开源系统真在用”
- 特别标出实际部署里用到的分类模型、embedding 模型、规则引擎或运行时信号

---

## 1. 最短结论

如果只看“最值得借鉴的开源落地 router”，我建议优先看这 6 个：

1. `LiteLLM`
   - 最完整的 AI gateway 路由组合：latency / cost / usage / fallback / budget / cooldown
2. `Portkey Gateway`
   - 最像策略树：conditional routing + load balancing + fallback 可组合
3. `APISIX AI Gateway`
   - 最工程化：priority / weight / health / retry / fallback_strategy
4. `Dify`
   - 最像产品平台：模型配置级负载均衡 + workflow 分流
5. `UncommonRoute`
   - 最接近 coding-agent step router 的真实实现
6. `aider`
   - 虽然不是自动 router，但“模型角色分工 + fallback”非常实用

一句话总结：
- 通用生产路由：看 `LiteLLM / Portkey / APISIX`
- 产品工作流分流：看 `Dify`
- coding-agent 真正可借鉴：看 `UncommonRoute / aider`

---

## 2. 先按“机制类型”而不是按项目名来分

### 2.1 Provider / Deployment 路由
典型动作：
- 选 provider
- 选 deployment
- 失败后 fallback
- 健康检查摘除坏节点

代表项目：
- LiteLLM
- Portkey Gateway
- APISIX AI Gateway
- Envoy AI Gateway
- One-API

### 2.2 Workflow / 分支路由
典型动作：
- if-else 分支
- LLM classifier 决定走哪个工作流
- 选哪个 query engine / retriever / worker

代表项目：
- Dify
- Flowise
- Langflow
- Haystack
- LlamaIndex

### 2.3 Budget / Fallback / Cooldown 控制
典型动作：
- 超预算过滤候选
- 某 provider 失败后冷却
- 按 quota、429、5xx 触发回退

代表项目：
- LiteLLM
- APISIX AI Gateway
- One-API
- Dify
- UncommonRoute

### 2.4 Coding-Agent Runtime 路由
典型动作：
- per-step 选模型
- 按失败类型升级
- 按任务角色切模型
- 按 provider/model 切工具策略

代表项目：
- UncommonRoute
- aider
- Cline SDK/runtime

---

## 3. 关键项目对比总表

| 项目 | 更像哪一层 | 真实在用的核心机制 | 触发条件 | 动作 | 实际部署里用到的模型/信号 | 最值得借鉴 |
|---|---|---|---|---|---|---|
| LiteLLM | AI Gateway | latency/cost/usage/budget-aware routing + fallback + cooldown | 延迟、usage、成本、预算、失败 | 选 deployment/provider，fallback，cooldown | 内置多种 routing strategy；预算 limiter；有 adaptive/complexity router 扩展 | 最完整的生产路由基础设施 |
| Portkey Gateway | AI Gateway | strategy tree：conditional + loadbalance + fallback + retry | 条件表达式、失败、超时 | 切 target/provider/key，进入 fallback 树 | 条件规则、权重、重试策略；更偏配置驱动而非 ML 模型 | 最适合学“可组合路由策略” |
| APISIX AI Gateway | API Gateway / AI upstream | priority + weight + retries + health + fallback_strategy | 429、5xx、token exhausted、health fail | 重选实例/上游、fallback | 无需分类模型；主要靠成熟 gateway 规则与健康检查 | 最工程化、最稳 |
| Dify | 平台层 + Workflow | 模型配置级 load balancing；If-Else；Question Classifier | rate limit、auth error、条件命中、分类命中 | 切下一个模型配置；走 workflow 分支 | Question Classifier 用 LLM 做分类；workflow 记录 selected_case_id / class_name | 最像真实产品平台的双层路由 |
| UncommonRoute | Coding-agent runtime | per-step router + budget + fallback chain + feedback overlay | 复杂度、低置信度、失败类型、预算、session continuity | 选模型、升级、fallback、预算过滤、sticky/continuity | Metadata + Structural + Embedding signals；sentence-transformers、sklearn、xgboost；failure taxonomy | 最像真正的 coding-agent router |
| aider | Coding-agent runtime | 角色分工：main/weak/editor/architect + fallback | 任务角色、弱模型失败 | 切不同角色模型，失败回退 main | 弱模型/编辑模型是静态配置，不靠 classifier | 最容易先落地的 coding-agent 基线 |
| Cline SDK/runtime | Runtime substrate | model→tool routing + loop/mistake escalation + compaction | provider/model、重复错误、循环调用 | 启用/禁用工具、停止/升级、压缩上下文 | providerId/modelId 路由规则；mistake/loop tracker | 最适合学 runtime control plane |

---

## 4. 各项目重点版

### 4.1 LiteLLM

你应该记住的不是“它支持很多 provider”，而是它已经把 production router 常见的 5 件事做进去了：
- latency-based routing
- cost-based routing
- usage-based routing
- fallback / retry
- budget limiter / cooldown

实际部署里用到的模型/信号：
- 主要不是分类模型，而是运行时统计信号：
  - latency
  - usage
  - cost
  - budget
  - health/cooldown state
- 另外有 adaptive_router / complexity_router 这类更“智能”的扩展层

最值得借鉴：
- 生产 router 不要只做一个 classifier
- 要把 fallback、budget、cooldown 当一等公民

### 4.2 Portkey Gateway

最强的点不是某个单独算法，而是“策略树”：
- conditional routing
- load balancing
- fallback
- retry
都可以组合

实际部署里用到的模型/信号：
- 更多是规则树、条件表达式、权重和重试策略
- 不强依赖分类模型

最值得借鉴：
- 真实产品里，router 常常不是单一打分器，而是组合策略图

### 4.3 APISIX AI Gateway

这类项目最值得学的是成熟网关思路：
- priority
- weight
- health check
- retry
- fallback_strategy

实际部署里用到的模型/信号：
- 不依赖 embedding/classifier
- 主要依赖 HTTP 错误、quota、health 状态、负载规则

最值得借鉴：
- AI router 可以建立在成熟 upstream/balancer 体系上
- 不一定非要从学术 router 长出来

### 4.4 Dify

Dify 其实有两层路由：

1. 模型配置层
- 多 credential / 多 config 轮询
- 某个 config 出错后 cooldown

2. 工作流层
- If-Else
- Question Classifier

实际部署里用到的模型/信号：
- Question Classifier 用 LLM 做分类
- workflow 侧会保留：
  - selected_case_id
  - class_name / class_label
- 模型接入层则用 rate limit / auth / connection error 等状态信号

最值得借鉴：
- 产品平台里的 router 往往是“模型层 + workflow 层”双层结构

### 4.5 UncommonRoute

这是目前最值得你看的 coding-agent 路由实现。

它真实在用的机制：
- per-request / per-step routing
- 低置信度升级
- budget 过滤
- fallback chain
- session continuity / sticky
- feedback overlay
- failure taxonomy

实际部署里用到的模型/信号：
- 三类主信号：
  - Metadata
  - Structural
  - Embedding
- 代码依赖显示它实际使用：
  - `sentence-transformers`
  - `scikit-learn`
  - `xgboost`
- 还有 runtime-aware 特征：
  - `step_type`
  - `has_tool_results`
  - `step_risk`
  - `failure kind`
  - `agent pressure`
- 并且有 `PlattCalibrator`

最值得借鉴：
- coding-agent router 不能只看 prompt 文本
- 要显式读 runtime state 和 failure taxonomy
- 低置信度默认升级，比盲目省钱更靠谱

### 4.6 aider

aider 不算自动 router，但它是非常值得模仿的“静态分工”案例：
- main model
- weak model
- editor model
- architect mode
- fallback to main model

实际部署里用到的模型/信号：
- 不是分类器 / embedding router
- 而是按任务角色静态分工
- 不同模型在 `model-settings.yml` 中被明确配置到不同角色

最值得借鉴：
- coding-agent 第一版不一定非要做复杂 classifier
- 先做角色分工 + fallback，往往更稳更容易落地

### 4.7 Cline SDK/runtime

Cline 更像 runtime routing substrate，而不是 classic model router。

真实在用的机制：
- model-tool routing
- loop detection
- consecutive mistake escalation
- auto compaction
- tool policy / auto approve

实际部署里用到的模型/信号：
- 主要是：
  - `providerId`
  - `modelId`
  - `mode`
  - repeated tool-call / mistake 状态
- 不是 embedding/classifier 模型，而是 runtime 规则和 tracker

最值得借鉴：
- routing 不一定只发生在 model selection
- 也可以发生在：
  - tool policy
  - recovery gate
  - compaction trigger

---

## 5. 实际部署里常见的“分类/embedding/判断器”长什么样

这部分是你特别关心的，我单独抽出来。

| 项目 | 实际部署里用到的分类/embedding/判断机制 | 备注 |
|---|---|---|
| LiteLLM | 主要依赖 runtime metrics；另有 adaptive/complexity router 扩展 | 偏生产规则 + 指标驱动 |
| Portkey Gateway | 条件表达式 / 规则树 | 偏配置驱动，不强调 embedding |
| APISIX AI Gateway | 健康检查、状态码、quota、priority/weight | 纯 gateway 规则式 |
| Dify | Question Classifier 用 LLM 分类；If-Else 用规则；模型配置层用 cooldown/error 状态 | 是“LLM 分类 + 规则分流”的混合体 |
| UncommonRoute | Metadata + Structural + Embedding 三类信号；`sentence-transformers`、`sklearn`、`xgboost`；Platt calibration | 目前最接近真正的 hybrid router |
| aider | 无显式分类器；静态角色分工 | 更像 role-based dispatch |
| Cline SDK/runtime | 无 embedding router；基于 provider/model/tool policy + loop/mistake tracker | 更像 runtime guardrail routing |
| Haystack | ConditionalRouter 用规则；LLMMessagesRouter 用 LLM 分类；FallbackChatGenerator 用异常触发 | pipeline 组件化明显 |
| LlamaIndex | selector：LLM selector / Pydantic selector | selector 与 executor 解耦 |

一句话：
- 真正线上最常见的不是“复杂 embedding router”
- 而是：
  - 规则分流
  - 状态/指标驱动
  - LLM classifier 做高层分类
  - 少数项目（如 UncommonRoute）才会真正把 embedding + calibration + runtime signal 结合起来

---

## 6. “学术 router vs 开源落地 router”对照表

这张表只看：哪些学术里常讲的机制，真的在开源项目里被采用了。

| 学术里常讲的机制 | 开源项目里是否常见 | 真实采用代表 | 现实情况判断 |
|---|---|---|---|
| query-level model selection | 部分常见 | UncommonRoute、LlamaIndex selector、部分 Dify classifier 分流 | 有，但没有论文里那么“纯粹” |
| strong-vs-weak binary router | 少量出现 | aider（静态角色分工接近）、UncommonRoute（升级逻辑） | 在产品里常变成角色分工或升级逻辑，而不是干净二分类器 |
| cost-aware routing | 很常见 | LiteLLM、UncommonRoute、One-API | 真正落地很常见，但多和 fallback/budget 一起出现 |
| latency-aware routing | 很常见 | LiteLLM、APISIX、Envoy/Kong 类网关 | 这类比学术里更常见 |
| uncertainty-aware escalation | 少量但重要 | UncommonRoute、Cline（mistake/loop 升级）、Flowise supervisor 式分流 | 真正在 agent runtime 里很重要 |
| cascade / staged escalation | 常见 | Portkey、Haystack FallbackChatGenerator、aider、UncommonRoute | 在工程里非常常见 |
| RL / bandit router | 很少直接落地 | LiteLLM 某些 adaptive 扩展有影子 | 论文常见，开源生产里很少成为主路径 |
| candidate profile / cold-start graph | 很少直接落地 | 暂无强开源生产代表 | 研究价值高，工程落地少 |
| query × model × budget 联合路由 | 很少直接落地 | UncommonRoute 有预算约束，离真正 R2-Router 式 joint policy 还有距离 | 学术前沿 > 工程常态 |
| workflow routing | 很常见 | Dify、Flowise、Langflow | 在产品里比 model router 更常见 |
| retriever / engine routing | 常见 | LlamaIndex、Haystack | 这是非常真实的落地方向 |
| tool / protocol routing | 在 agent 系统里越来越重要 | Cline、UncommonRoute | 学术里讲得少，工程里价值很高 |
| health / cooldown / auto-disable | 非常常见 | LiteLLM、One-API、Dify、APISIX | 这是开源落地 router 最常见的机制之一 |
| feedback-driven local adaptation | 少量出现 | UncommonRoute | 很有前景，但目前开源里不多 |

最短结论：
- 真正被开源项目广泛采用的，不是最学术化的 router
- 而是：
  1. fallback / retry / cooldown
  2. cost / latency / quota gating
  3. workflow conditional routing
  4. role-based dispatch
  5. runtime escalation / tool-policy routing

反而这些学术机制目前落地少：
- 纯 RL/bandit router
- candidate profile 图路由
- 完整 query×model×budget 联合策略

---

## 7. 如果你要做自己的系统，应该怎么吸收这些经验

### 7.1 先做“保底生产层”
先实现：
- retry
- fallback
- cooldown
- budget / quota gate
- health / auto-disable

直接对标：
- LiteLLM
- APISIX
- One-API

### 7.2 再做“逻辑分流层”
再实现：
- if-else
- classifier routing
- selector/executor 分离

直接对标：
- Dify
- Haystack
- LlamaIndex

### 7.3 最后做“agent runtime 层”
最后实现：
- per-step routing
- failure taxonomy
- tool / transport routing
- low-confidence escalation
- role-based model split

直接对标：
- UncommonRoute
- aider
- Cline

---

## 8. 一句话结论

> 学术 router 最常研究“如何更聪明地选模型”，而开源落地 router 真正常见的是“如何更稳地分流、回退、限预算、控风险”；如果你要做可落地系统，第一优先级不是 RL/gating，而是 fallback、budget、workflow routing 和 runtime escalation。