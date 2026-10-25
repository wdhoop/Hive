"""Hive 安全层 — API Key 管理器（开源架构版）

设计意图
--------
ApiKeyManager 统一管理智能体接入凭证：
- generate：为智能体签发 Key（可按命名空间 + 权限分级），支持强制指定值（首次 Master）；
- verify：认证请求头 X-API-Key，返回身份或 None；
- revoke / rotate：吊销与轮换；
- check_permission：细粒度权限校验（供 require_permission 装饰器使用）。
- 安全基线：Key 只存哈希（HMAC-SHA256），不存明文。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

from typing import List, Optional

from .models import AgentIdentity, ApiKeyRecord, KeyStatus, PermissionLevel


class ApiKeyManager:
    """API Key 管理器（SQLite 持久化，生产版）。"""

    def __init__(self, db_path: str) -> None:
        """初始化。

        :param db_path: SQLite 数据库路径
        """
        raise NotImplementedError("骨架版不包含 API Key 实现")

    def _init_db(self) -> None:
        """建表：api_keys（key_id 唯一，存储哈希）。"""
        raise NotImplementedError

    def _load_cache(self) -> None:
        """加载活跃 Key 缓存。"""
        raise NotImplementedError

    def _row_to_record(self, row) -> ApiKeyRecord:
        raise NotImplementedError

    @staticmethod
    def _hash_key(raw_key: str) -> str:
        """Key 哈希（HMAC-SHA256）。"""
        raise NotImplementedError

    # ── 签发与吊销 ────────────────────────────────────────
    def generate_key(
        self,
        agent_id: str,
        agent_name: str = "",
        permissions: Optional[List[str]] = None,
        permission_level: PermissionLevel = PermissionLevel.READ,
        namespace: str = "default",
        force_key_value: Optional[str] = None,
    ) -> ApiKeyRecord:
        """签发 API Key（force_key_value 用于注入指定值，如 Master）。"""
        raise NotImplementedError

    def verify_key(self, raw_key: str) -> Optional[AgentIdentity]:
        """校验请求中的 Key，成功返回身份。"""
        raise NotImplementedError

    def _touch_key(self, key_id: str) -> None:
        """更新最近使用时间。"""
        raise NotImplementedError

    def revoke_key(self, key_id: str) -> bool:
        """吊销。"""
        raise NotImplementedError

    def rotate_key(self, key_id: str) -> Optional[dict]:
        """轮换（旧 Key 吊销，新 Key 返回一次明文）。"""
        raise NotImplementedError

    # ── 查询与校验 ────────────────────────────────────────
    def list_keys(self, agent_id: Optional[str] = None) -> List[ApiKeyRecord]:
        """列出 Key（不含明文）。"""
        raise NotImplementedError

    def check_permission(self, identity: AgentIdentity, required: List[str]) -> bool:
        """细粒度权限校验。"""
        raise NotImplementedError

    def refresh_cache(self) -> None:
        """刷新缓存。"""
        raise NotImplementedError

    def get_stats(self) -> dict:
        """Key 统计（总量 / 按状态分布）。"""
        raise NotImplementedError
