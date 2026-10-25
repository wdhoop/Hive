"""Hive 通信层 — 本地消息总线（开源架构版）

设计意图
--------
生产版 MqttBus 提供两种通道：
1. MQTT 实时通道：topic 发布/订阅，支持通配符（+ / #），用于局域网内实时消息；
2. SQLite 持久化队列：MQTT 不可用时消息先落库（_enqueue），恢复后 flush 补发，
   保证"消息积压不丢、开机即补"。

骨架版复刻完整接口；所有方法体为占位（NotImplementedError）。
"""

from __future__ import annotations

from typing import Callable, Optional

from .models import Message


class MqttBus:
    """本地消息总线。

    生产版依赖 paho-mqtt + sqlite3；骨架版仅声明接口。
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 1883,
        db_path: str = "",
        client_id: str = "hive_bus",
        username: str = "",
        password: str = "",
        tls: bool = False,
    ) -> None:
        """初始化总线。

        :param host/port: MQTT broker 地址
        :param db_path:   持久化队列 SQLite 路径（空 = 内存队列占位）
        :param client_id: MQTT 客户端 ID
        :param username/password: broker 凭据（环境变量注入）
        :param tls:       是否启用 TLS
        """
        raise NotImplementedError("骨架版不包含总线实现")

    # ── 连接管理 ──────────────────────────────────────────
    def connect(self) -> bool:
        """连接 broker。"""
        raise NotImplementedError

    def disconnect(self) -> None:
        """断开连接。"""
        raise NotImplementedError

    def wait_connected(self, timeout: float = 5.0) -> bool:
        """等待连接就绪。"""
        raise NotImplementedError

    def is_connected(self) -> bool:
        """是否已连接。"""
        raise NotImplementedError

    # ── 回调（生产版内部使用）─────────────────────────────
    def _on_connect(self, client, userdata, flags, rc) -> None:  # pragma: no cover
        raise NotImplementedError

    def _on_disconnect(self, client, userdata, rc) -> None:  # pragma: no cover
        raise NotImplementedError

    def _on_message(self, client, userdata, msg) -> None:  # pragma: no cover
        raise NotImplementedError

    @staticmethod
    def _topic_match(pattern: str, topic: str) -> bool:
        """MQTT 主题通配匹配（+ 单级 / # 多级）。"""
        raise NotImplementedError

    # ── 发布 ──────────────────────────────────────────────
    def publish(self, topic: str, message: Message, qos: int = 1) -> bool:
        """发布到主题。"""
        raise NotImplementedError

    def send_direct(self, message: Message) -> bool:
        """点对点发送（sender→recipient）。"""
        raise NotImplementedError

    def broadcast(self, message: Message) -> bool:
        """广播。"""
        raise NotImplementedError

    def send_to_topic(self, topic: str, message: Message, qos: int = 1) -> bool:
        """按主题发送。"""
        raise NotImplementedError

    # ── 订阅 ──────────────────────────────────────────────
    def subscribe(self, topic: str, handler: Callable, qos: int = 1) -> None:
        """订阅主题并挂接处理器。"""
        raise NotImplementedError

    def unsubscribe(self, topic: str, handler: Optional[Callable] = None) -> None:
        """取消订阅。"""
        raise NotImplementedError

    # ── 持久化队列 ────────────────────────────────────────
    def _init_db(self) -> None:
        """初始化持久化队列表。"""
        raise NotImplementedError

    def _enqueue(self, message: Message, topic: str = "") -> None:
        """消息落库（MQTT 失败时兜底）。"""
        raise NotImplementedError

    def flush_queue(self, max_batch: int = 50) -> int:
        """补发积压消息，返回补发条数。"""
        raise NotImplementedError

    # ── 统计 ──────────────────────────────────────────────
    def get_stats(self) -> dict:
        """返回总线统计（连接状态 / 积压 / 吞吐）。"""
        raise NotImplementedError
