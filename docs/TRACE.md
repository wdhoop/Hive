# 一条消息的五层流转（构造 trace 回放）

> 本文件是**构造示例**（非真实运行日志）：用假 agent、假消息、假失败构造一条
> 全链路 trace，回答"五层为什么要放在一起"——一条消息从发出到返回，
> 依次经过通信 → 安全 → 记忆 → 自愈 → 接入，每一层各管一件事。

## 场景

- `probe-1`：一个探针 agent（SDK 接入）
- `worker-1`：一个工作 agent（SDK 接入，负责处理任务）
- 消息内容：`"count 1"`（技术原语，无业务含义）

## 全链路时序

| 步骤 | 层 | 动作 | 关键数据 |
|---|---|---|---|
| 1 | **接入层** | `probe-1` 调用 `send("worker-1", "count 1")` | `msg: {sender: probe-1, recipient: worker-1, type: text}` |
| 2 | **安全层** | 请求携带 `X-API-Key`，AuthMiddleware 校验通过（含限流计数） | `permission: worker-1 可收` |
| 3 | **通信层** | 消息写入中央信箱 `worker-1` 的队列（PULL 积压，不依赖对方在线） | `inbox: worker-1 += 1 条` |
| 4 | **通信层** | `worker-1` 长轮询 `poll(timeout=25)` 取到消息 | `poll → [msg id=m-…]` |
| 5 | **记忆网关** | 落库前命名空间校验：`worker-1` 写 `worker-1:counter`（ACL 放行） | `store: worker-1:counter = 1 (v1)` |
| 6 | **记忆网关** | 写入带乐观锁版本号；若版本冲突则返回快照并重试 | `version: 1 → 2` |
| 7 | **自愈层** | 处理中出现超时失败 → FailureTracker 计数 | `failures(worker-1) = 3 → unreliable` |
| 8 | **自愈层** | 抗体库生成降级预案，下次同类调用直接走预案 | `antibody: timeout → fallback: offline-cache` |
| 9 | **接入层** | `worker-1` 回执 `ack(msg_id)` 并返回处理结果 | `ack → 消息出队，闭环完成` |

## 为什么五层放在一起

| 层 | 它独自回答的问题 |
|---|---|
| 通信层 | 消息怎么不丢、怎么到达？（PULL 信箱：离线不丢、重连补齐） |
| 安全层 | 谁在说话、能说什么？（API Key + 权限分级 + 限流） |
| 记忆网关 | 记忆怎么不串、不被覆盖？（命名空间隔离 + 乐观锁 + 审计） |
| 自愈层 | 失败一次之后怎么办？（失败沉淀为预案，越跑越抗造） |
| 接入层 | 上面这些对开发者多简单？（五步接入，其余全部封装） |

单层都能独立存在，但**只有五层串起来，一条消息才能"安全地到达、正确地落库、
失败也不慌"**——这正是 Hive 作为"底座"与散装工具的区别。

## 与 examples 的对应

- 步骤 1/4/9（接入、PULL、回执）→ `examples/two-agents`
- 步骤 5（命名空间隔离）→ `examples/memory-namespace`
- 步骤 6（乐观锁）→ `examples/optimistic-lock`
- 步骤 7/8（自愈）→ `examples/antibody`
- 五步接入全景 → `examples/hello-agent`
