# Hive API 契约（开源架构版）

> 本文档为**清洗版端点契约**：保留生产系统的端点分组与语义，
> 删除一切真实地址 / 凭据 / 内部实现细节。骨架版所有业务端点返回 501。

- 服务端口：`8764`（默认，可配置 `HIVE_PORT`）
- 认证：HTTP Header `X-API-Key: <full_key>`
- 公开端点：`/health`、`/api/v1/init-key`
- 全部端点响应格式：`application/json`

## 1. 系统

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/health` | 健康检查（骨架版真实实现） | 公开 |
| GET | `/api/v1/init-key` | 获取初始 Master Key（生产版） | 公开（首次） |

## 2. API Key 管理

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/api/v1/keys` | 列出 API Key | admin |
| POST | `/api/v1/keys` | 签发 API Key | admin |
| DELETE | `/api/v1/keys/{key_id}` | 吊销 | admin |
| POST | `/api/v1/keys/{key_id}/rotate` | 轮换 | admin |
| GET | `/api/v1/keys/stats` | Key 统计 | admin |

## 3. 记忆操作（经记忆网关）

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/memory` | 写入记忆 | write |
| GET | `/api/v1/memory/{node_id}` | 读取 | read |
| PUT | `/api/v1/memory/{node_id}` | 更新（带版本） | write |
| DELETE | `/api/v1/memory/{node_id}` | 删除 | write |

## 4. Agent 管理

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/agents/{agent_id}/register` | 注册 | write |
| POST | `/api/v1/agents/{agent_id}/heartbeat` | 心跳 | write |
| GET | `/api/v1/agents/{agent_id}` | 查询 | read |
| GET | `/api/v1/agents` | 列表（可按状态过滤） | read |
| GET | `/api/v1/agents/online` | 在线列表 | read |
| DELETE | `/api/v1/agents/{agent_id}` | 注销 | write |

## 5. 消息收发（PULL 优先）

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/sync` | 状态同步 + 领取公告 | write |
| GET | `/api/v1/inbox` | 拉取消息（长轮询 ≤25s） | read |
| POST | `/api/v1/send` | 发送消息 | write |
| POST | `/api/v1/ack` | 回执确认 | write |

## 6. MQTT 通信

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/bus/publish` | 发布到主题 | write |
| POST | `/api/v1/bus/subscribe` | 订阅主题 | write |
| GET | `/api/v1/bus/stats` | 总线统计 | read |

## 7. 命名空间

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/namespaces` | 创建命名空间 | admin |
| GET | `/api/v1/namespaces` | 列表 | read |
| GET | `/api/v1/namespaces/{name}` | 查询 | read |
| DELETE | `/api/v1/namespaces/{name}` | 删除 | admin |
| POST | `/api/v1/namespaces/{name}/acl` | 授权 | admin |
| DELETE | `/api/v1/namespaces/{name}/acl` | 移除权限 | admin |

## 8. 审计日志

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/api/v1/audit` | 查询审计记录 | admin |
| GET | `/api/v1/audit/stats` | 审计统计 | admin |

## 9. 自愈机制

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/selfheal/antibody` | 生成抗体 | write |
| GET | `/api/v1/selfheal/antibody/match` | 匹配抗体 | read |
| POST | `/api/v1/selfheal/antibody/{id}/result` | 反馈结果 | write |
| GET | `/api/v1/selfheal/antibodies` | 抗体列表 | read |
| GET | `/api/v1/selfheal/stats` | 自愈统计 | read |

## 10. 任务分发

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/tasks` | 创建任务 | write |
| POST | `/api/v1/tasks/{id}/claim` | 认领 | write |
| POST | `/api/v1/tasks/{id}/complete` | 完成 | write |
| POST | `/api/v1/tasks/{id}/fail` | 失败 | write |
| POST | `/api/v1/tasks/{id}/cancel` | 取消 | write |
| GET | `/api/v1/tasks/{id}` | 查询 | read |
| GET | `/api/v1/tasks` | 列表（按状态/认领人） | read |

## 11. 版本快照

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/snapshots` | 创建快照 | write |
| GET | `/api/v1/snapshots/{node_id}` | 节点快照列表 | read |
| GET | `/api/v1/snapshots/{node_id}/latest` | 最新快照 | read |

## 12. 搜索与提取

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/api/v1/search` | 全局检索（按命名空间过滤） | read |
| GET | `/api/v1/extract` | 文本提取 | read |

## 13. 闲时调度

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| POST | `/api/v1/scheduler/register` | 注册周期任务 | write |
| GET | `/api/v1/scheduler/status` | 调度状态 | read |

## 14. 路由表与统计

| 方法 | 路径 | 说明 | 权限 |
|---|---|---|---|
| GET | `/api/v1/routes` | 路由表 | read |
| GET | `/api/v1/stats` | 系统统计聚合 | read |

## 错误语义

| 状态码 | 含义 |
|---|---|
| 200 | 成功 |
| 401 | 认证失败（X-API-Key 缺失/无效） |
| 403 | 权限不足 / 命名空间 ACL 拒绝 |
| 404 | 资源不存在 |
| 409 | 版本冲突（乐观锁 LockConflict） |
| 429 | 限流 |
| 501 | Not Implemented（骨架版全部业务端点） |
