# 示例（Examples）

> 底座示例的原则：**展示接入路径，不展示业务价值**。
> 每个示例用 echo / counter / sleep 这类技术原语，演示"Hive 的协议长什么样、失败时怎么表现"，不含任何真实业务。

五个最小示例（每个单文件、纯标准库、可直接运行），分别对应一层：

| 示例 | 对应层 | 演示内容 | 运行 |
|---|---|---|---|
| [hello-agent](hello-agent/main.py) | 接入 SDK | 五步接入：sync → send → poll → ack → run（echo agent） | `python examples/hello-agent/main.py` |
| [two-agents](two-agents/main.py) | 通信层 | 两个 mock agent 经中央信箱互发，PULL 长轮询（离线不丢、重连补齐） | `python examples/two-agents/main.py` |
| [memory-namespace](memory-namespace/main.py) | 记忆网关 | 同名 key 的命名空间隔离；越权写被 ACL 拒绝 | `python examples/memory-namespace/main.py` |
| [optimistic-lock](optimistic-lock/main.py) | 记忆网关 | 并发写冲突 → 409 + 版本快照 → 按快照重试成功 | `python examples/optimistic-lock/main.py` |
| [antibody](antibody/main.py) | 自愈层 | 连续 3 次超时 → 生成抗体（降级预案）→ A/B replay 验证 | `python examples/antibody/main.py` |

## 为什么用虚构场景

- 真实在用的东西不能公开 → 示例必须干净、可复现、无业务泄露
- 读者（开发者）真正关心的是三件事：**接入多简单、协议长什么样、失败时怎么表现**
- 这三件事用 echo agent + 构造的失败 trace 就能完整覆盖

## 契约测试即文档

各层预期行为见 [tests/test_examples.py](../tests/test_examples.py)——测试本身就是协议文档。
一键验证全部示例与契约：`python scripts/_verify_examples.py`

## 可删除、可替换

`examples/` 独立成目录，与 core 无耦合，读完即删即可；每个示例只演示一个特性，刻意极简。
