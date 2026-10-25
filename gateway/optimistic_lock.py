"""Hive 记忆网关层 — 乐观锁（开源架构版）

设计意图
--------
OptimisticLock 为多智能体并发写同一记忆节点提供保护：
- 写前取版本号，提交时带上期望版本；
- 服务端版本不匹配即抛 LockConflict，由调用方重读重试，
  避免"最后写入覆盖先写结果"。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

from typing import Any, Dict, Optional


class LockConflict(Exception):
    """版本冲突：并发写被拒绝。"""

    def __init__(self, node_id: str, expected_version: int, actual_version: int) -> None:
        self.node_id = node_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        super().__init__(
            f"LockConflict: {node_id} expected v{expected_version}, actual v{actual_version}"
        )


class OptimisticLock:
    """乐观锁辅助（对接记忆底座版本字段）。"""

    def __init__(self, supermem_base_url: str = "http://127.0.0.1:8765") -> None:
        """初始化。

        :param supermem_base_url: 记忆底座地址（骨架版占位）
        """
        raise NotImplementedError("骨架版不包含乐观锁实现")

    def get_version(self, node_data: dict) -> int:
        """从节点数据中提取版本号。"""
        raise NotImplementedError

    def prepare_payload(
        self, updates: Dict[str, Any], expected_version: int
    ) -> Dict[str, Any]:
        """构造带版本的写请求载荷。"""
        raise NotImplementedError

    def verify_version(self, current_node: dict, expected_version: int) -> bool:
        """校验当前版本是否匹配期望版本。"""
        raise NotImplementedError
