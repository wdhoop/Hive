"""Hive 安全层 — 权限与身份模型（开源架构版）

公共安全契约：权限分级、Key 状态、API Key 记录、智能体身份。
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


class PermissionLevel(str, Enum):
    """权限分级。"""

    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class KeyStatus(str, Enum):
    """API Key 状态。"""

    ACTIVE = "active"
    REVOKED = "revoked"
    EXPIRED = "expired"


@dataclass
class ApiKeyRecord:
    """API Key 记录。"""

    key_id: str
    agent_id: str
    agent_name: str = ""
    permissions: List[str] = field(default_factory=lambda: ["read"])
    permission_level: PermissionLevel = PermissionLevel.READ
    namespace: str = "default"
    created_at: float = field(default_factory=time.time)
    expires_at: Optional[float] = None
    last_used_at: Optional[float] = None
    status: KeyStatus = KeyStatus.ACTIVE

    def to_dict(self) -> dict:
        return {
            "key_id": self.key_id,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "permissions": self.permissions,
            "permission_level": self.permission_level.value,
            "namespace": self.namespace,
            "created_at": self.created_at,
            "expires_at": self.expires_at,
            "last_used_at": self.last_used_at,
            "status": self.status.value,
        }


@dataclass
class AgentIdentity:
    """认证成功后的智能体身份（注入请求上下文）。"""

    agent_id: str
    key_id: str
    permissions: List[str]
    namespace: str = "default"
    meta: Dict[str, object] = field(default_factory=dict)
