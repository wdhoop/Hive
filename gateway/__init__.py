"""Hive 记忆网关层（开源架构版）

记忆网关统一封装对记忆底座的访问：代理、路由、命名空间隔离、审计、并发保护、
全局检索与版本快照。本骨架复刻全部接口契约。
"""

from .memory_proxy import SuperMemProxy
from .router import HiveRoute, RouteTable
from .namespace import NamespaceManager, NamespaceConfig
from .audit import AuditLogger
from .optimistic_lock import OptimisticLock, LockConflict
from .search import GlobalSearch
from .snapshot import SnapshotManager, Snapshot

__all__ = [
    "SuperMemProxy",
    "HiveRoute", "RouteTable",
    "NamespaceManager", "NamespaceConfig",
    "AuditLogger",
    "OptimisticLock", "LockConflict",
    "GlobalSearch",
    "SnapshotManager", "Snapshot",
]
