"""Hive 记忆网关层 — REST 路由表（开源架构版）

设计意图
--------
RouteTable 维护 Hive 对外 REST 端点的分组与注册：
- 路由分四组：memory（记忆）/ agent（智能体）/ system（系统）/ misc；
- 路由可查看、可匹配，供认证中间件与审计复用。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class HiveRoute:
    """一条路由定义。"""

    prefix: str                 # 路径前缀，如 /api/v1/memory
    name: str = ""
    group: str = "misc"         # memory / agent / system / misc
    methods: List[str] = field(default_factory=lambda: ["GET", "POST", "PUT", "DELETE"])
    permission: str = "read"    # 默认所需权限

    def to_dict(self) -> dict:
        return {
            "prefix": self.prefix,
            "name": self.name,
            "group": self.group,
            "methods": self.methods,
            "permission": self.permission,
        }


class RouteTable:
    """Hive 路由表。"""

    def __init__(self) -> None:
        raise NotImplementedError("骨架版不包含路由表实现")

    def _register_defaults(self) -> None:
        """注册生产版默认路由分组（memory / agents / system / misc）。"""
        raise NotImplementedError

    def register(self, route: HiveRoute) -> None:
        """注册路由。"""
        raise NotImplementedError

    def get_route(self, prefix: str) -> Optional[HiveRoute]:
        """按前缀取路由。"""
        raise NotImplementedError

    def match(self, path: str) -> Optional[HiveRoute]:
        """按完整路径匹配路由。"""
        raise NotImplementedError

    def list_routes(self) -> List[Dict]:
        """列出全部路由。"""
        raise NotImplementedError
