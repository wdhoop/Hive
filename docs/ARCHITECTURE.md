# Hive 架构设计文档（开源架构版）

> 本文档描述 Hive 多智能体联邦中枢的**架构设计**。骨架版只复刻架构，
> 不包含真实实现与数据。社区可据此二次开发。

## 1. 定位与设计目标

Hive 是面向**所有智能体**的通用联邦中枢，解决多智能体协作的三类问题：

1. **发现**：智能体如何注册、互相发现、按能力分工。
2. **通信**：不同运行环境的智能体（本地 / 云端）如何可靠互发消息。
3. **协同**：任务如何创建、认领、完成；记忆如何隔离、并发写、可追溯；系统出错如何自愈。

设计原则：

- **PULL 优先**：云端智能体无法被服务端主动推送，消息走"信箱 + 主动拉取 + 回执"。
- **记忆与通信分离**：通信走总线，记忆走网关，互不渗透。
- **一切可审计**：关键操作进审计日志；记忆变更可回滚（快照 + 乐观锁）。
- **自愈即资产**：失败沉淀为可复用预案（抗体），成功率可统计。

## 2. 总体架构

```
                    ┌──────────────────────────────────────────┐
                    │                 HTTP (FastAPI)           │
                    │       REST: /api/v1/*  (X-API-Key 认证)  │
                    └───────────────┬──────────────────────────┘
                                    │
        ┌───────────┬───────────────┼──────────────┬───────────┐
        │           │               │              │           │
   ┌────▼────┐ ┌────▼────┐   ┌─────▼─────┐  ┌─────▼─────┐ ┌────▼────┐
   │ security│ │communication          │  │   gateway │ │self_heal│
   │ API Key │ │ 总线/注册/路由/调度     │  │ 记忆网关  │ │ 抗体库  │
   │ 权限限流 │ │ 任务分发/云端信箱/同步 │  │ 命名空间  │ │失败跟踪│
   └─────────┘ └─────────┘              │  │ 审计/快照  │ └─────────┘
                                        │  │ 乐观锁/检索 │
                                        │  └─────┬─────┘
                                        │        │
                                        │  ┌─────▼─────┐
                                        │  │  记忆底座  │
                                        │  │ (supermem) │
                                        └──┴───────────┘
```

装配顺序（生产版，骨架版按同序占位）：

```
1. 安全层：  ApiKeyManager + AuthMiddleware + RateLimiter
2. 通信层：  MqttBus + AgentRegistry + MessageRouter + CentralInbox + BootNotifier + WebhookDeliverer
3. 记忆网关：SuperMemProxy + RouteTable + NamespaceManager + AuditLogger + OptimisticLock + GlobalSearch + SnapshotManager
4. 调度分发：IdleScheduler + TaskDistributor
5. 自愈层：  AntibodyLibrary + FailureTracker
```

## 3. 模块职责

### 3.1 communication — 通信层

| 模块 | 职责 | 关键接口 |
|---|---|---|
| `models.py` | 公共数据契约 | Message / MessageType / AgentRecord / AgentStatus |
| `bus.py` | 本地消息总线（MQTT + 持久化队列） | publish / subscribe / send_direct / broadcast / flush_queue |
| `agent_registry.py` | 智能体注册与心跳 | register / heartbeat / detect_timeouts / get_online_agents |
| `router.py` | 主题模式路由 | register_handler / route |
| `scheduler.py` | 闲时调度 | register / unregister / get_status |
| `task_distributor.py` | 任务池 | create / claim / complete / fail / cancel |
| `cloud_gateway.py` | 云端网关 | CentralInbox / BootNotifier / WebhookDeliverer |
| `mem_sync.py` | 记忆变更同步 | push / pull / ack / stats |

消息协议（PULL 优先）：

```
send ──► CentralInbox ──► poll/fetch（长轮询 ≤25s）──► 处理 ──► ack
                          │
                          └──► WebhookDeliverer（支持 webhook 的智能体，失败退避重试）
```

开机握手（boot 确认闭环）：服务启动 → 广播公告 → 智能体上线 sync → 回执 ack → 闭环。

### 3.2 gateway — 记忆网关层

| 模块 | 职责 | 关键接口 |
|---|---|---|
| `memory_proxy.py` | 记忆底座 HTTP 代理 | add / get / search / update / delete / health |
| `router.py` | REST 路由表 | register / match / list_routes |
| `namespace.py` | 命名空间 + ACL | create / delete / add_acl / check_access |
| `audit.py` | 审计日志 | log / query / cleanup |
| `optimistic_lock.py` | 乐观锁 | get_version / verify_version |
| `search.py` | 全局检索 | search / search_strong |
| `snapshot.py` | 版本快照 | create / list_snapshots / get_latest_snapshot |

记忆隔离模型：

```
命名空间 A（如 hive_internal）  ── 仅 A 内智能体可见
命名空间 B（如 agent_x）        ── 仅 B 内智能体可见
ACL: { agent_id: [read|write|admin] }   ← check_access 统一入口
```

并发写保护：写前取版本号 → 提交带期望版本 → 不匹配抛 LockConflict → 调用方重读重试。

### 3.3 security — 安全层

| 模块 | 职责 | 关键接口 |
|---|---|---|
| `models.py` | 权限 / Key / 身份模型 | PermissionLevel / ApiKeyRecord / AgentIdentity |
| `api_key_manager.py` | Key 全生命周期 | generate / verify / revoke / rotate / check_permission |
| `middleware.py` | 认证与限流 | AuthMiddleware / RateLimiter / require_permission |

安全基线：

- Key 只存哈希（HMAC-SHA256），不存明文；
- 认证头 `X-API-Key`，公开端点白名单（/health、/api/v1/init-key）；
- Master Key 由环境变量注入（生产版首次启动可经 init-key 获取）。

### 3.4 self_heal — 自愈层

| 模块 | 职责 | 关键接口 |
|---|---|---|
| `antibody.py` | 抗体库 | generate / match / report_result / get_reliable |
| `failure_tracker.py` | 失败跟踪 | record_failure / record_success / check_timeout / record_mode |

自愈闭环：

```
错误发生 ──► FailureTracker 归因（模式键 + 连续计数）
        ──► 超阈值 ──► AntibodyLibrary.match（命中预案）
        ──► 执行修复 ──► report_result（成功 → 置信度上升）
```

### 3.5 sdk — 接入层

`HiveAgentClient`：智能体接入标准方式。

```
client.sync(status="online", metadata=...)   # 上报 + 领公告
client.poll(timeout=25)                      # 长轮询拉消息
client.send(recipient, content, msg_type)    # 发消息
client.ack(message_id)                       # 回执
client.run(on_message=..., stop_check=...)   # 常驻循环
```

## 4. 关键设计决策

1. **为什么用信箱而非直连推送？** 云端智能体无公网收包能力；信箱 + 长轮询
   对网络要求最低，且消息落库天然持久化，积压不丢。
2. **为什么消息要 ack？** 防止"处理了但没回执 → 重复投递"或"丢失无人知"；
   ack 语义是 PULL 协议可靠性的锚点。
3. **为什么记忆走独立网关？** 命名空间隔离、审计、乐观锁都集中在网关层，
   智能体只面对简单 API，记忆安全由网关统一兜底。
4. **为什么自愈要沉淀抗体？** 一次性修复是消费，抗体库是资产——同类错误
   复现时直接命中，系统越跑越"抗造"。
5. **为什么闲时调度？** 本地部署场景资源有限，智能体无需常驻，
   由调度器在空闲档位触发周期任务（对应"闲时自主行动系统"思想）。

## 5. 骨架版边界（与本仓库强相关）

- 所有模块仅接口签名 + docstring，方法体占位（NotImplementedError）；
- 唯一完整实现：`communication/models.py`（公共契约）与 `server.py` 装配骨架
  （/health 真实返回，业务端点 501）；
- 不含任何真实凭据、内网地址、个人路径、业务数据、日志；
- 不与任何外部智能体 / 记忆服务联动。

## 6. 二次开发指引

1. 从 `communication/models.py` 出发理解消息契约；
2. 按装配顺序逐层实现（先 security → communication → gateway → 调度 → 自愈）；
3. 接入记忆底座时实现 `gateway/memory_proxy.py` 即可替换底座；
4. 新智能体接入：签发 API Key → 使用 `sdk/hive_agent_client.py` 的协议接入。
