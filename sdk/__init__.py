"""Hive 接入 SDK（开源架构版）

智能体侧客户端：同步、拉取、发送、回执与常驻循环。
"""

from .hive_agent_client import HiveAgentClient, DEFAULT_UA

__all__ = ["HiveAgentClient", "DEFAULT_UA"]
