"""Hive 通信层 — 公共数据契约（开源架构版）

本文件是 Hive 消息体系的**唯一事实来源**：
所有通信模块（总线 / 中央信箱 / SDK / 路由）共用同一套数据结构。
骨架版给出完整字段定义，便于社区按契约二次实现。
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class MessageType(str, Enum):
    """消息类型。"""

    TEXT = "text"                # 普通文本
    COMMAND = "command"          # 指令
    TASK = "task"                # 任务
    TASK_RESULT = "task_result"  # 任务结果
    STATUS = "status"            # 状态上报
    HEARTBEAT = "heartbeat"      # 心跳
    ACK = "ack"                  # 回执
    EVENT = "event"              # 事件


class AgentStatus(str, Enum):
    """智能体在线状态。"""

    ONLINE = "online"
    OFFLINE = "offline"
    BUSY = "busy"
    IDLE = "idle"
    ERROR = "error"


@dataclass
class Message:
    """智能体间消息。

    消息生命周期：send 写入中央信箱 → 收件方 poll/fetch → 处理 → ack 回执。
    TTL 过期后由网关清理，防止死信堆积。
    """

    id: str = field(default_factory=lambda: uuid.uuid4().hex)
    sender: str = ""                      # 发送方 agent_id
    recipient: str = ""                   # 收件方 agent_id（空 = 广播）
    msg_type: MessageType = MessageType.TEXT
    content: str = ""                     # 正文（UTF-8）
    topic: str = ""                       # 可选主题（路由用）
    timestamp: float = field(default_factory=time.time)
    ttl: int = 86400                      # 生存期（秒）
    meta: Dict[str, Any] = field(default_factory=dict)

    def is_expired(self) -> bool:
        """是否超过 TTL。"""
        return time.time() - self.timestamp > self.ttl

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "sender": self.sender,
            "recipient": self.recipient,
            "msg_type": self.msg_type.value,
            "content": self.content,
            "topic": self.topic,
            "timestamp": self.timestamp,
            "ttl": self.ttl,
            "meta": self.meta,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            id=data.get("id", uuid.uuid4().hex),
            sender=data.get("sender", ""),
            recipient=data.get("recipient", ""),
            msg_type=MessageType(data.get("msg_type", "text")),
            content=data.get("content", ""),
            topic=data.get("topic", ""),
            timestamp=data.get("timestamp", time.time()),
            ttl=data.get("ttl", 86400),
            meta=data.get("meta", {}),
        )


@dataclass
class AgentRecord:
    """智能体注册记录（注册表条目）。"""

    agent_id: str
    agent_name: str = ""
    status: AgentStatus = AgentStatus.OFFLINE
    namespace: str = "default"            # 归属命名空间
    capabilities: list = field(default_factory=list)  # 能力标签
    last_heartbeat: float = field(default_factory=time.time)
    meta: Dict[str, Any] = field(default_factory=dict)

    def is_online(self, timeout: int = 300) -> bool:
        """按心跳间隔判断是否在线。"""
        return time.time() - self.last_heartbeat <= timeout

    def to_dict(self) -> dict:
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "namespace": self.namespace,
            "capabilities": self.capabilities,
            "last_heartbeat": self.last_heartbeat,
            "meta": self.meta,
        }
