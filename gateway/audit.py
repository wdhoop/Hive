"""Hive 记忆网关层 — 审计日志（开源架构版）

设计意图
--------
AuditLogger 记录所有经网关的记忆操作（谁 / 何时 / 对什么 / 做了什么），
用于追溯与合规。生产版按日滚动、定期清理。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

from typing import List, Optional


class AuditLogger:
    """审计日志（SQLite 持久化，生产版）。"""

    def __init__(self, db_path: str) -> None:
        """初始化审计日志。

        :param db_path: SQLite 数据库路径
        """
        raise NotImplementedError("骨架版不包含审计实现")

    def _init_db(self) -> None:
        """建表：audit_log（agent_id / action / target / timestamp）。"""
        raise NotImplementedError

    def log(
        self,
        agent_id: str,
        action: str,
        target: str = "",
        detail: str = "",
        namespace: str = "",
    ) -> None:
        """写入一条审计记录。"""
        raise NotImplementedError

    def query(
        self,
        agent_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[dict]:
        """按条件查询审计记录。"""
        raise NotImplementedError

    def get_stats(self) -> dict:
        """审计统计（总量 / 按动作分布）。"""
        raise NotImplementedError

    def cleanup(self, older_than_days: int = 30) -> int:
        """清理过期记录。"""
        raise NotImplementedError
