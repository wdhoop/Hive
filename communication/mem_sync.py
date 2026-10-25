"""Hive 通信层 — 记忆同步队列（开源架构版）

设计意图
--------
MemSyncStore 承担"记忆变更在多端间同步"的职责：
- push：本端记忆变更（patches）写入指定队列；
- pull：远端按增量（since / since_id）拉取；
- ack：确认已应用，队列据此清理；
- 语义与中央信箱一致：PULL 优先、积压不丢。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

from typing import List, Optional, Tuple

PULL_LIMIT = 500  # 单次拉取上限


class MemSyncStore:
    """记忆同步存储（SQLite 持久化，生产版）。"""

    def __init__(self, db_path: str) -> None:
        """初始化同步队列。

        :param db_path: SQLite 数据库路径
        """
        raise NotImplementedError("骨架版不包含记忆同步实现")

    def _conn(self) -> "sqlite3.Connection":
        raise NotImplementedError

    def _init_db(self) -> None:
        """建表：sync_queue（queue / patch_id / applied 标记）。"""
        raise NotImplementedError

    @staticmethod
    def _norm_patch(p, now: float) -> Optional[Tuple[str, dict, float]]:
        """归一化补丁条目（校验必需字段）。"""
        raise NotImplementedError

    def push(self, queue: str, patches: List[dict], source: str = "") -> int:
        """写入补丁到队列，返回成功条数。"""
        raise NotImplementedError

    def pull(
        self,
        queue: str,
        since: float = 0.0,
        since_id: int = 0,
        limit: int = PULL_LIMIT,
    ) -> List[dict]:
        """增量拉取补丁。"""
        raise NotImplementedError

    def ack(self, queue: str, patch_ids: List[int]) -> int:
        """确认已应用，返回处理条数。"""
        raise NotImplementedError

    def stats(self, queue: str) -> dict:
        """队列统计（积压 / 已确认 / 平均延迟）。"""
        raise NotImplementedError
