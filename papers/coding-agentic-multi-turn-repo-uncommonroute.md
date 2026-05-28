# UncommonRoute（基于 CommonstackAI/UncommonRoute 仓库的源码笔记）

## 0. 说明
- 这不是论文笔记，而是基于 GitHub 仓库 `https://github.com/CommonstackAI/UncommonRoute` 的源码 / 文档笔记。
- 记录依据主要来自：
  - 仓库 README / README.zh-CN
  - `pyproject.toml`
  - `uncommon_route/cli.py`
  - `uncommon_route/benchmark.py`
  - `uncommon_route/router/api.py`
  - `docs/routing-strategy-analysis.md`
  - `docs/transport-routing-design.md`
  - `docs/static_benchmark_split_method.md`
- 仓库状态：浏览时 GitHub 页面显示约 668 stars、23 forks、177 commits；默认分支 `main`。
- 最近可见提交信息：`Harden routing diagnostics and privacy controls`（页面显示 2026-05-12）。

## 1. 这个仓库到底是什么？
- 最短定义：一个本地运行的 coding-agent LLM router / proxy，把 Claude Code、Cursor、Codex、OpenAI SDK 等客户端请求路由到最合适的上游模型。
- 它不是纯 benchmark repo，也不是只服务论文复现的 reference implementation，而是偏产品化的本地路由器：
  - 支持 OpenAI-compatible 与 Anthropic-compatible 接入
  - 支持 Dashboard / spend cap / diagnostics / local feedback overlay
  - 支持 BYOK provider 管理
  - 支持本地 CLI、后台代理与观测工具

## 2. 一句话总结
- 总结：UncommonRoute 可以看作 TwinRouterBench 论文里 trained router 的产品化落地版本，但仓库真正有价值的地方不只是“用静态 benchmark 训了个 tier classifier”，而是把 routing 扩展成一个完整本地控制面：模型选择、协议选择、预算上限、反馈学习、诊断导出、agent-loop composition、prefix-cache 友好的上下文压缩策略都在 repo 里开始成形。

## 3. 我为什么觉得它值得单独读？
- 因为它不是一个只给论文结果的 demo repo，而是在认真解决“router 真正上线之后会遇到什么系统问题”：
  - 客户端协议不一致（Anthropic vs OpenAI）
  - tool-heavy agent loop 会不会因跨协议转换失真
  - prefix cache 被频繁换模型打爆怎么办
  - 本地如何可视化、可调参、可反馈学习
  - 预算限制、隐私、支持包、日志、故障导出如何工程化
- 对你做 coding-agentic router，这些问题比单纯 classifier 指标更像真实系统设计问题。

## 4. 仓库结构与主要模块

### 4.1 顶层目录我看到什么？
- `bench/`：与静态 benchmark / 实验适配相关
- `docs/`：包含 routing strategy、transport routing、static split 等设计说明
- `scripts/`：训练、校准、切分、overhead benchmark 等脚本
- `uncommon_route/`：主应用代码
- `frontend/`：Dashboard 前端
- `tests/`：测试
- `openclaw-plugin/`：OpenClaw 集成

### 4.2 Python 包依赖暴露了什么系统形态？
- `pyproject.toml` 显示其核心依赖包括：
  - `httpx`
  - `uvicorn`
  - `starlette`
  - `numpy`
  - `scikit-learn`
  - `sentence-transformers`
  - `xgboost`
- 这说明它不是只靠 heuristic；至少 embedding / classifier / calibration 在产品里是常驻部件。

### 4.3 入口长什么样？
- CLI 入口：`uncommon-route = uncommon_route.cli:main`
- `cli.py` 暴露命令包括：
  - `init`
  - `route`
  - `serve`
  - `stop`
  - `doctor`
  - `logs`
  - `support`
  - `feedback`
  - `openclaw`
  - `spend`
  - `provider`
  - `config`
  - `stats`
  - `telemetry`
- 这比典型 research repo 明显更偏产品与运维。

## 5. 它的 router 到底怎么工作？

### 5.1 公开宣传层面的说法
- README 将系统描述为三类信号 ensemble：
  - Metadata
  - Embedding
  - Structural
- 路由先做复杂度分类，再从已配置的上游模型池中选择最低成本的匹配模型。
- 产品界面呈现的复杂度是 `simple / medium / complex`，而 TwinRouterBench 静态 benchmark 的内部 tier 是 `low / mid / mid_high / high`。

### 5.2 代码里能看到的更具体实现
- `uncommon_route/router/api.py` 显示 v2 使用 multi-signal ensemble：
  - `MetadataSignal`
  - `StructuralSignal`
  - `EmbeddingSignal`
  - 外加 `PlattCalibrator`
- 同文件还显示：router 不只是看最后一句 prompt，而开始显式抽取 agentic 特征：
  - `step_type`
  - `has_tool_results`
  - `step_risk`
  - `is_agentic`
  - `is_coding`
  - 以及基于 tool result 的 failure kind 分类（environment / invocation / semantic）
- 这说明仓库已经不满足于“静态文本分类”，而是在往 runtime-aware router 演化。

### 5.3 它对 tool failure 的理解很值得注意
- `api.py` 里有一整套对 tool result 错误的检测逻辑：
  - traceback / importerror / assertionerror / no tests ran 等 marker
  - verification failure 与 environment failure 的区分
  - agent state pressure 的估计
- 这和你现在在 235b vs 397b 轨迹里看到的 workflow fragility 很像：
  - 不是所有失败都该直接升最强模型
  - environment/invocation failure 更像恢复问题
  - semantic verification failure 才更像 reasoning-capacity 问题
- 这点对 coding-agentic router 特别有价值，因为它已经开始把 failure taxonomy 编进运行时特征里。

## 6. 它和 TwinRouterBench 的关系

### 6.1 benchmark 关系
- README 明确说它在 TwinRouterBench 上评测。
- README 中复用了 TwinRouterBench 的关键数字：
  - 100-case held-out SWE-bench Verified split
  - trained router：75/100 tasks solved
  - Opus-only：74/100
  - API cost：$25.66 vs $54.73
  - 成本下降 53%

### 6.2 静态 split 关系
- `docs/static_benchmark_split_method.md` 记录了 v2 静态数据切分：
  - 970 rows
  - `train=621`
  - `calibration=153`
  - `holdout=196`
  - 分层键：`benchmark + target_tier`
- 这说明 repo 不只是“用整包 benchmark 训一下”，而是认真做了 leakage-aware 的 train/calibration/holdout 切分。

### 6.3 它不是只停留在论文里的 trained logistic router
- TwinRouterBench 论文里提到的是 frozen BGE embedding + logistic regression。
- 但仓库当前 `pyproject.toml` 同时依赖 `scikit-learn`、`sentence-transformers`、`xgboost`，并且 docs/脚本里有 calibration、param sweep、embedding classifier 等内容。
- 我的理解：repo 里的系统已经比论文里的最简 trained variant 更工程化，也可能更混合式。

## 7. 这个仓库最重要的系统设计点

### 7.1 本地 proxy + 本地控制面
- 它强调 routing 本地运行，不经过额外托管 router 服务。
- 这对隐私与可解释性都有帮助，也让它更像“coding agent runtime substrate”的一部分，而不是远端 API。

### 7.2 per-request / per-agent-step routing
- README 明说 routing 是 per request / per agent step，而不是整段 session 绑死到一个模型。
- 这和 TwinRouterBench 的 step-level 理念一致。
- 但 docs 中又开始讨论 session-level hold 与 cache 保持，说明他们已经意识到：真正工程上不能只是“每步独立判一次”，还要考虑 cache 与上下文增长。

### 7.3 transport routing
- `docs/transport-routing-design.md` 很值得读。
- 它提出 routing 不应只输出 `selected_model`，还应输出 `selected_transport`。
- 也就是：
  - 选哪个模型
  - 走哪个协议（Anthropic Messages / OpenAI Chat / 以后可能 Responses）
- 这对 Claude Code / tool-heavy agent loop 特别关键，因为协议转换本身会破坏工具语义。
- 对你来说，这是一个很实在的提醒：coding-agent router 的动作空间可能不仅是 `(model, budget)`，还包括 `transport / protocol`。

### 7.4 model composition，而不是盲目 model switching
- `docs/routing-strategy-analysis.md` 提出一个非常关键的工程观察：
  - agent loop 中 input token 才是成本大头
  - per-request model switching 会摧毁 prefix cache
  - 省下的 output 差价可能抵不过 cache miss 带来的 input 成本
- 因此 repo 开始转向 `model composition`：
  - 主模型尽量保持 session 连续
  - 便宜模型走侧通道，负责 tool result 压缩、历史 summarization、structured extraction
- 这和普通 router 论文的思路很不一样，更接近“runtime cost control architecture”。

### 7.5 可反馈学习
- README 提到 Dashboard 允许用户把路由结果标成：
  - `too strong`
  - `just right`
  - `too weak`
- 这些反馈会训练一个本地 overlay，而不会改写 base model。
- 这是一种非常产品化的在线 adaptation 设计：
  - base router 保持稳定
  - user-/org-specific 偏好通过本地 overlay 叠加
- 这对你后面做个性化 router / deployment adaptation 很有借鉴价值。

## 8. 它和你当前 coding-agent router 的直接关系

### 8.1 哪些点和你现在的观察正好对上？
- 你当前 235b vs 397b 观察到的主问题是 workflow fragility，而不是单纯 patch quality。
- `api.py` 里已经显式区分：
  - semantic verification failure
  - environment failure
  - invocation failure
- 这说明 UncommonRoute 也在往“不要把所有失败都当成同一种升级信号”这个方向走。

### 8.2 哪些点是你现在还没有系统化写出来，但很值得吸收的？
- transport routing
- prefix-cache-aware routing
- composition-based cheap side channel
- 本地 feedback overlay
- diagnostics / support bundle / telemetry 这些可观测性机制

### 8.3 哪些点不能直接照搬？
- repo 当前更偏产品代理层，不是专门围绕 mini-swe-agent / SWE-bench 训练定制的研究系统。
- 复杂度分类仍然在 `simple / medium / complex` 这类较粗粒度上暴露，与你要做的 step-level coding agent 动作空间还不完全一致。
- 它虽开始读取 agentic signal，但离你想要的 workflow / granularity / recovery gate 全套控制器还有距离。

## 9. 我怎么看它的“研究性”与“工程性”平衡

### 9.1 研究性
- 有明确 benchmark 依托：TwinRouterBench
- 有 train/calibration/holdout 切分说明
- 有 signal、calibration、holdout 结果与 benchmark reproduction 入口
- 所以它不是纯 marketing repo

### 9.2 工程性
- CLI / daemon / doctor / provider 管理 / spend cap / support bundle / telemetry / dashboard 都说明它已经在认真做产品闭环
- 因此它比很多 paper repo 更值得你读，因为它暴露了大量论文不会写的 deployment friction

### 9.3 我对它的定位
- 最合适的定位是：`agentic router 的产品化参考实现 + 研究原型桥接层`
- 它既不是纯 benchmark，也不是纯论文复现，更不是通用 API gateway；它正在变成一个 coding-agent routing control plane

## 10. 对你项目最有用的 takeaways

### 10.1 可以直接借鉴的部件
- failure taxonomy 作为 routing feature
- transport routing 作为一级动作
- prefix-cache-aware cost model
- composition side-channel 处理大 tool outputs
- 本地 overlay feedback 学习
- train / calibration / holdout 三分切法

### 10.2 可以转成你自己 design doc 的句子
- “在 coding agent runtime 中，路由动作空间不应只包含 model id；protocol / transport 也可能是成本与稳定性的关键控制变量。”
- “在长 agent loop 中，input-token 成本与 prefix-cache 命中往往比单步 output-token 价格更重要，因此 runtime controller 应优先考虑 cache-preserving control。”
- “对 tool-heavy workflow，cheap model 的最佳角色未必是替代主模型，而可能是侧通道的 compression / extraction / summarization worker。”

### 10.3 如果你把它放进自己的系统分层
- backbone router：有
- budget / spend controller：有一部分
- transport router：有，而且很强
- workflow controller：弱
- granularity controller：弱
- recovery gate：中等，主要在 failure / pressure 信号层面
- observability / support：很强

## 11. 我认为这个 repo 最值得继续深挖的文件
- `uncommon_route/router/api.py`
  - 看 runtime feature、tool failure taxonomy、agent pressure
- `docs/transport-routing-design.md`
  - 看为什么 transport 也是 routing action
- `docs/routing-strategy-analysis.md`
  - 看 prefix cache 与 model composition
- `docs/static_benchmark_split_method.md`
  - 看 benchmark split 设计
- `scripts/train_embedding_classifier.py` / `fit_calibration.py` / `holdout_param_sweep.py`
  - 继续追训练与校准路径

## 12. 开源性与可复现性
- 仓库开源：是
- 许可证：MIT
- 安装方式：`pipx install uncommon-route` 或源码 `pip install -e .[dev]`
- benchmark 完整 reproduction：README 说明完整 Table 3 reproduction 需要 TwinRouterBench release package；repo 自身提供 overhead benchmark 与本地 router 实现
- 我的判断：这是一个“核心产品代码公开，但完整 benchmark 复现仍依赖外部 release package”的状态

## 13. 我的最终结论
- UncommonRoute 最值得你读的地方，不是它把 TwinRouterBench 的 trained router 包装成一个 CLI，而是它把“router 上线以后真正棘手的问题”全暴露出来了：协议怎么选、cache 怎么保、长 tool trace 怎么压、失败信号怎么分类、用户如何给 feedback、系统如何导出诊断。
- 如果 TwinRouterBench 主要给你 benchmark 与 label schema，那么 UncommonRoute 这个 repo 给你的就是 deployment/control-plane schema。
- 对你做 coding-agentic router，我会把它当成“研究 benchmark 走向真实系统”的桥梁材料，而不是简单的 supplementary implementation。
