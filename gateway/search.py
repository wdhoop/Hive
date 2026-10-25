"""Hive 记忆网关层 — 全局检索（开源架构版）

设计意图
--------
GlobalSearch 提供跨命名空间的统一检索入口：
- 通过记忆底座 /search 执行语义检索；
- 在网关层按命名空间过滤可见范围（只返回调用方有权限的结果）；
- 生产版支持混合检索（向量 + 标签 + 权重）。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

from typing import List


class GlobalSearch:
    """全局检索。"""

    def __init__(self, supermem_base_url: str = "http://127.0.0.1:8765") -> None:
        """初始化。

        :param supermem_base_url: 记忆底座地址（骨架版占位）
        """
        raise NotImplementedError("骨架版不包含全局检索实现")

    def search(
        self,
        query: str,
        agent_id: str = "",
        namespace: str = "",
        limit: int = 10,
        **kwargs,
    ) -> List[dict]:
        """检索，并按命名空间 ACL 过滤。"""
        raise NotImplementedError

    def search_strong(
        self,
        query: str,
        agent_id: str = "",
        namespace: str = "",
        limit: int = 10,
    ) -> List[dict]:
        """强检索（高置信模式）。"""
        raise NotImplementedError
