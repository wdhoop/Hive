"""Hive 通信层 — 消息路由（开源架构版）

设计意图
--------
MessageRouter 实现"主题模式 → 处理器"的匹配分发：
- 处理器按 topic 模式注册（如 `hive/task/+/`）；
- 消息到达时按模式匹配路由到对应处理器；
- 支持通配（+ 单级 / # 多级），与 MQTT 语义一致。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

from typing import Callable, List, Optional

from .models import Message


class MessageRouter:
    """消息路由表。"""

    def __init__(self) -> None:
        """初始化空路由表。"""
        raise NotImplementedError("骨架版不包含路由实现")

    def register_handler(self, topic_pattern: str, handler: Callable) -> None:
        """注册主题模式 → 处理器。"""
        raise NotImplementedError

    def unregister_handler(self, topic_pattern: str) -> None:
        """移除处理器。"""
        raise NotImplementedError

    def route(self, message: Message, topic: str) -> Optional[Callable]:
        """按主题匹配出处理器；无匹配返回 None。"""
        raise NotImplementedError

    @staticmethod
    def _topic_match(pattern: str, topic: str) -> bool:
        """主题通配匹配。"""
        raise NotImplementedError

    def list_routes(self) -> List[dict]:
        """列出全部路由（模式 → 处理器名）。"""
        raise NotImplementedError
