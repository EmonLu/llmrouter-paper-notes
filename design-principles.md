# Design Principles

这个文件专门沉淀“跨论文”的系统设计原则，而不是单篇论文摘录。

## 使用规则
- 每读完一篇论文，只补充真正能跨论文复用的原则
- 原则必须能指导系统设计或实验设计
- 原则尽量写成一句话 + 一段说明

## 当前初版原则

### 原则 1：不要把 router 限定为“只选模型”
对于 agentic system，routing 至少还包括 budget、workflow topology、granularity、escalation 和 memory usage。

### 原则 2：routing 决策应该分层发生
把 task-level、turn-level、step-level、trajectory-level 混在一起，通常会让系统难以解释和难以调试。

### 原则 3：便宜的不确定性信号很重要
在真实系统里，agreement、tool failure、历史成功率这类 cheap signal 往往比复杂训练式 router 更易落地。

### 原则 4：memory 不只是检索模块，也应该进入 routing state
如果历史 workflow 成败信息不能反哺 router，系统会一直重复低效决策。

### 原则 5：先做可解释的模块化 router，再考虑端到端学习
先把 topology selector、budget allocator、uncertainty gate 等模块做清楚，更利于验证和迭代。

## 待补充原则
- [ ] 什么时候应该升级模型
- [ ] 什么时候应该增加思考预算
- [ ] 什么时候应该 split / merge 多 agent pipeline
- [ ] 如何把 profile / calibration 信号接入 router
