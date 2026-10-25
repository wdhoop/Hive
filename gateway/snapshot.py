"""Hive 记忆网关层 — 版本快照（开源架构版）

设计意图
--------
SnapshotManager 为记忆节点提供"版本留档"：
- 关键节点每次变更前可存快照，供回滚 / 审计 / 对比；
- 生产版与乐观锁配合：写前快照、冲突时可回溯。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Snapshot:
    """一条节点快照。"""

    node_id: str
    content: str = ""
    version: int = 1
    created_at: float = field(default_factory=time.time)
    reason: str = ""
    actor: str = ""

    def to_dict(self) -> dict:
        return {
            "node_id": self.node_id,
            "content": self.content,
            "version": self.version,
            "created_at": self.created_at,
            "reason": self.reason,
            "actor": self.actor,
        }


class SnapshotManager:
    """快照管理器（SQLite 持久化，生产版）。"""

    def __init__(self, db_path: str) -> None:
        """初始化快照库。

        :param db_path: SQLite 数据库路径
        """
        raise NotImplementedError("骨架版不包含快照实现")

    def _init_db(self) -> None:
        """建表：snapshots（node_id + version 联合索引）。"""
        raise NotImplementedError

    def create(
        self,
        node_id: str,
        content: str,
        version: int,
        reason: str = "",
        actor: str = "",
    ) -> int:
        """创建快照，返回 snapshot_id。"""
        raise NotImplementedError

    def list_snapshots(
        self,
        node_id: str,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Snapshot]:
        """列出某节点的历史快照。"""
        raise NotImplementedError

    def get_snapshot(self, snapshot_id: int) -> Optional[Snapshot]:
        """按 ID 取快照。"""
        raise NotImplementedError

    def get_latest_snapshot(self, node_id: str) -> Optional[Snapshot]:
        """取最新快照。"""
        raise NotImplementedError

    def get_stats(self) -> dict:
        """快照统计。"""
        raise NotImplementedError
