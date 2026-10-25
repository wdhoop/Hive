"""Hive 通信层 — 智能体注册表（开源架构版）

设计意图
--------
AgentRegistry 是 Hive 的"户口本"：
- 智能体上线先 register（写入身份 / 能力 / 命名空间），周期 heartbeat 报活；
- 心跳超时由 detect_timeouts 判定下线，供调度与路由参考；
- 所有查询走统一数据访问层，供总线、网关、SDK 复用。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

from typing import List, Optional

from .models import AgentRecord, AgentStatus


class AgentRegistry:
    """智能体注册表（SQLite 持久化，生产版）。"""

    def __init__(self, db_path: str) -> None:
        """初始化注册表。

        :param db_path: SQLite 数据库路径
        """
        raise NotImplementedError("骨架版不包含注册表实现")

    def _init_db(self) -> None:
        """建表：agents（agent_id 唯一索引）。"""
        raise NotImplementedError

    # ── 生命周期 ──────────────────────────────────────────
    def register(
        self,
        agent_id: str,
        agent_name: str = "",
        namespace: str = "default",
        capabilities: Optional[List[str]] = None,
        meta: Optional[dict] = None,
    ) -> bool:
        """注册（或覆盖更新）一个智能体。"""
        raise NotImplementedError

    def unregister(self, agent_id: str) -> bool:
        """注销。"""
        raise NotImplementedError

    def heartbeat(
        self,
        agent_id: str,
        status: Optional[str] = None,
        meta: Optional[dict] = None,
    ) -> bool:
        """心跳报活，刷新 last_heartbeat。"""
        raise NotImplementedError

    # ── 查询 ──────────────────────────────────────────────
    def get_agent(self, agent_id: str) -> Optional[AgentRecord]:
        """按 ID 查单个智能体。"""
        raise NotImplementedError

    def list_agents(self, status: Optional[AgentStatus] = None) -> List[AgentRecord]:
        """按状态过滤列出。"""
        raise NotImplementedError

    def get_online_agents(self) -> List[AgentRecord]:
        """在线列表（心跳未超时）。"""
        raise NotImplementedError

    def detect_timeouts(self) -> List[AgentRecord]:
        """检测心跳超时的智能体（供下线判定）。"""
        raise NotImplementedError

    # ── 统计 ──────────────────────────────────────────────
    def get_stats(self) -> dict:
        """注册总数 / 在线数 / 超时数。"""
        raise NotImplementedError
