# Coding Agentic Router Experiment Plan for SWE-bench

> 目标：把 `coding-agentic-router-spec.md` 变成一套可以逐步落地的实验路线，验证在 SWE-bench 类 repo-level bug fixing 任务中，runtime routing 是否能比固定 agent policy 更高效、更稳。

## 1. 核心实验问题

这组实验要回答 6 个核心问题：

1. 在 SWE-bench 这类任务上，runtime routing 是否真的优于固定 backbone / 固定 workflow / 固定 budget 的 coding agent？
2. backbone routing、budget routing、workflow routing、granularity routing、recovery routing 中，哪一层最先带来收益？
3. cheap online signals（agreement、测试反馈、patch 失败模式）是否足以支持有效 routing？
4. step-level budget control 是否比统一大 budget 更高效？
5. fine-grained vs compound execution 的切换是否真的能带来 token/time 节省而不明显伤害成功率？
6. recovery gate 是否能降低 stuck trajectory 比例？

## 2. 总体实验路线

建议按 5 个 phase 做，且每个 phase 只新增一个主要 routing 维度。

```text
Phase 0: 固定 agent baseline
Phase 1: 只加 backbone routing
Phase 2: 加 budget routing
Phase 3: 加 workflow / granularity routing
Phase 4: 加 recovery routing
```

不要一开始就端到端统一 controller，否则无法归因。

## 3. Phase 0：建立固定 agent baseline

## 3.1 目标
先定义一个稳定的、可复现实验底座。

## 3.2 基础 agent 设定
固定一个标准 agent 流程：
1. retrieve
2. inspect
3. localize
4. patch
5. test
6. reflect
7. retry（若允许）

固定：
- 单 backbone
- 固定 budget
- 固定 workflow
- 固定 granularity
- 无 recovery routing

## 3.3 必备 baseline
至少准备以下几类：
1. strongest-model single-agent baseline
2. mid-model single-agent baseline
3. strongest-model planner-patcher-tester baseline
4. fixed multi-agent baseline
5. fixed high-budget baseline
6. fixed low-budget baseline

## 3.4 Phase 0 指标
必须记录：
- task success rate
- average token cost per task
- average wall-clock time per task
- average model calls
- average test iterations
- stuck trajectory ratio
- rollback ratio

## 3.5 Phase 0 交付物
- 一个统一的 trajectory log schema
- 一个统一 evaluator
- 若干固定 agent baseline 结果

## 4. Phase 1：只加 backbone routing

## 4.1 目标
回答：

> 仅在 coding trajectory 的不同 step 之间切 backbone，是否已经能带来明显收益？

## 4.2 动作空间
只开放：
- `A1 = backbone selection`

其他都固定：
- budget 固定
- workflow 固定
- granularity 固定
- recovery 固定

## 4.3 路由粒度
建议只在关键 step 上开放 backbone routing：
- localize
- patch
- reflect

不要在 test step 上做复杂 routing。

## 4.4 对比方案
1. fixed strongest backbone
2. fixed medium backbone
3. backbone router using simple heuristics
4. backbone router using profile-aware scorer

## 4.5 假设
- 不同 step 对模型能力需求不同：
  - inspect / retrieve 不一定需要最强模型
  - patch / reflect 更可能需要强模型
- 一个简单的 step-aware backbone router 就可能带来显著收益

## 4.6 指标
- 按 step type 的 model selection frequency
- patch step 的成功率变化
- reflect step 的边际收益
- backbone 路由是否减少高价模型总调用量

## 5. Phase 2：加入 budget routing

## 5.1 目标
回答：

> step-level budget control 是否比全程固定高 budget 更高效？

## 5.2 动作空间
开放：
- `A1 = backbone selection`
- `A2 = budget selection`

budget 先离散化：
- low
- medium
- high

budget 映射到：
- max reasoning tokens
- max rollout count
- reflection enable/disable
- retry allowance

## 5.3 推荐 cheap signal
优先用：
- inter-rollout agreement
- 最近测试结果变化
- patch 重复失败次数
- 当前上下文压力
- 当前 issue / diff 复杂度 proxy

## 5.4 对比方案
1. fixed backbone + fixed high budget
2. fixed backbone + adaptive budget
3. adaptive backbone + fixed budget
4. adaptive backbone + adaptive budget

## 5.5 关键分析
- 哪些 step 最值得加 budget？
- budget 提升是否主要提升 patch / reflect 阶段？
- cheap signal 是否足以判断“该不该继续算”？

## 6. Phase 3：加入 workflow / granularity routing

## 6.1 目标
回答：

> runtime 是否应该在不同任务 / 不同步骤间切换 workflow template 和执行粒度？

## 6.2 动作空间
开放：
- `A1 = backbone selection`
- `A2 = budget selection`
- `A3 = workflow selection`
- `A4 = granularity selection`

## 6.3 workflow template 集合
建议第一版限制在少量模板：
- T1: single-agent
- T2: patcher + tester
- T3: planner + patcher + tester
- T4: patcher + reviewer + tester

## 6.4 granularity mode
建议先比较：
- fine-grained sequential
- standard compound
- two-phase compound

## 6.5 对比方案
1. fixed workflow + fixed granularity
2. adaptive workflow only
3. adaptive granularity only
4. adaptive workflow + granularity

## 6.6 假设
- 简单任务更适合 single-agent 或 compound mode
- 复杂任务更适合 planner/reviewer/t tester 明确分工
- granularity routing 主要影响 token / latency，不一定直接显著影响成功率

## 7. Phase 4：加入 recovery routing

## 7.1 目标
回答：

> 当 trajectory 卡住时，显式 recovery gate 是否能降低失败率和浪费？

## 7.2 动作空间
开放全部：
- backbone
- budget
- workflow
- granularity
- recovery

## 7.3 recovery action 集
- keep current strategy
- increase budget
- switch stronger model
- add reviewer / tester
- rollback patch
- restart from localization
- spawn alternative branch
- terminate

## 7.4 recovery trigger signal
建议优先用：
- failing tests 数量不降反升
- syntax error 持续重复
- patch 多次击中相同文件区域却无改善
- rollout disagreement 高
- no-progress streak >= k
- token / time nearing budget cap

## 7.5 对比方案
1. no recovery routing
2. rule-based recovery gate
3. cheap-signal recovery gate
4. full modular controller with recovery

## 7.6 核心指标
- stuck trajectory ratio
- rollback frequency
- branch retry success rate
- recovery-triggered success gain
- wasted token reduction

## 8. 日志与数据 schema

每条 trajectory 至少记录：
- task_id
- repo_id
- issue metadata
- step index
- step type
- selected backbone
- selected budget level
- selected workflow template
- selected granularity mode
- recovery action
- token cost
- latency
- test outcome
- patch summary
- agreement score
- cumulative budget usage
- final success/failure label

这个日志 schema 很关键，因为后面几乎所有分析都依赖它。

## 9. 核心消融实验

至少做以下 ablation：
- 去掉 backbone routing
- 去掉 budget routing
- 去掉 workflow routing
- 去掉 granularity routing
- 去掉 recovery gate
- 去掉 agreement signal
- 去掉 test-feedback signal
- 去掉 patch-failure signal
- 降低 candidate workflow template 数量

## 10. 失败分析框架

按以下类别做 failure bucket：
- 错 backbone：模型能力不够
- 错 budget：给得太少或太多
- 错 workflow：角色组织不对
- 错 granularity：过度拆分或过度合并
- 错 recovery：该 rollback 时没 rollback，该升级时没升级
- state sensing failure：cheap signal 误导

## 11. 推荐结果表

### 表 A：主结果表
- strongest single-agent
- strongest multi-agent fixed workflow
- adaptive backbone only
- backbone + budget
- backbone + budget + workflow
- backbone + budget + workflow + granularity
- full controller + recovery

### 表 B：分 step 结果表
列：
- step type
- strongest backbone win rate
- adaptive backbone usage
- high-budget usage
- average token cost
- contribution to final success

### 表 C：recovery 分析表
列：
- recovery trigger
- recovery action
- success delta
- extra cost
- wasted cost reduction

## 12. 推荐执行顺序

### 第一优先级
- Phase 0 baseline
- Phase 1 backbone routing

### 第二优先级
- Phase 2 budget routing
- cheap signal validation

### 第三优先级
- Phase 3 workflow / granularity routing
- Phase 4 recovery routing

## 13. 关键判断标准

如果 backbone routing 单独就没有收益，说明：
- 要么 step taxonomy 不合理
- 要么 candidate model pool 不够异质
- 要么 coding task 上真正重要的不是 backbone 而是 workflow / budget

如果 budget routing 收益大于 backbone routing，说明：
- coding agent 里的核心瓶颈更像 adaptive compute 问题，而不是 model selection 问题

如果 recovery gate 收益最大，说明：
- SWE-bench 更像 runtime control / failure recovery 问题，而不是静态路由问题

## 14. 最终目标

通过这组实验，最后要回答的不只是“router 有没有用”，而是：

- 哪一层 routing 最值钱？
- SWE-bench 上最该优化的是 backbone、budget、workflow、granularity 还是 recovery？
- coding agentic router 与 general router 的分界线到底在哪里？

## 15. 一句话结论

> Coding Agentic Router 的实验路线必须是分层增量式的：先证明 backbone routing 成立，再看 budget，接着看 workflow / granularity，最后再加 recovery gate；否则你无法知道 SWE-bench 上真正值钱的控制维度是什么。
