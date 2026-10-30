"""Hive 安全层 — 认证中间件与限流（开源架构版）

设计意图
--------
AuthMiddleware 拦截全部请求：
- 解析 X-API-Key → 校验 → 注入 AgentIdentity 到 request.state；
- 公开端点（/health、/api/v1/init-key）白名单放行；
- RateLimiter 按 agent_id 做滑动窗口限流，防滥用。

骨架版复刻完整接口；方法体为占位。
注意：主系统认证在生产版实现；本骨架仅**完整实现**广场隔离中间件
（PlazaIsolationMiddleware），因为广场是独立子模块、开箱即用。
"""

from __future__ import annotations

import os
import time
from types import SimpleNamespace
from typing import Callable, List, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from .models import AgentIdentity


class AuthMiddleware(BaseHTTPMiddleware):
    """认证中间件（FastAPI/Starlette）。"""

    def __init__(self, app, key_manager, public_paths: Optional[List[str]] = None) -> None:
        """初始化。

        :param app:          FastAPI 应用
        :param key_manager:  ApiKeyManager（校验用）
        :param public_paths: 白名单路径前缀
        """
        super().__init__(app)
        raise NotImplementedError("骨架版不包含认证中间件实现")

    async def dispatch(self, request, call_next):
        """拦截请求：认证 → 放行 / 401。"""
        raise NotImplementedError


def require_permission(required: List[str]):
    """端点装饰器：要求当前身份具备指定权限。

    用法（生产版）：
        @router.post("/api/v1/memory")
        @require_permission(["write"])
        def add_memory(request): ...
    """

    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            raise NotImplementedError("骨架版不包含权限装饰器实现")

        return wrapper

    return decorator


class RateLimiter:
    """滑动窗口限流器。"""

    def __init__(self) -> None:
        raise NotImplementedError("骨架版不包含限流实现")

    def check(self, agent_id: str, limit: int, window: int) -> bool:
        """窗口内是否允许（True=放行）。"""
        raise NotImplementedError

    def get_remaining(self, agent_id: str, limit: int, window: int) -> int:
        """剩余配额。"""
        raise NotImplementedError

    def reset(self, agent_id: str) -> None:
        """重置计数。"""
        raise NotImplementedError


# ══════════════════════════════════════════════════════════════════
# 智能体广场隔离中间件（独立子模块，完整实现）
# ══════════════════════════════════════════════════════════════════
#
# 广场是 Hive 的一个**独立子模块**：
#   - 独立数据库 data/plaza.db（SQLite WAL），与主系统完全分离；
#   - 独立钥匙体系 X-Plaza-Key（plaza/keys.py，库中仅存 sha256 哈希）；
#   - 路由级隔离：两套钥匙互不通用。
#
# 隔离规则（/api/v1/plaza/*）：
#   1. 公开端点（GET 浏览类 + POST /register）→ 免钥匙放行；
#   2. /admin/* 管理端点 → 主 X-API-Key，且必须等于 HIVE_MASTER_KEY；
#   3. 其余广场端点 → 校验 X-Plaza-Key 并注入 request.state.plaza_agent。
# 非广场路径原样放行（由主系统处理，骨架版保持 501 占位）。

PLAZA_PREFIX = "/api/v1/plaza"
PLAZA_KEY_HEADER = "X-Plaza-Key"
MAIN_KEY_HEADER = "X-API-Key"


def _is_plaza_public(method: str, rest_path: str) -> bool:
    """广场公开端点（无需任何钥匙）：浏览类 + 注册。"""
    if method == "GET":
        if rest_path in ("", "/health", "/guide", "/boards", "/announcements"):
            return True
        if rest_path == "/threads" or rest_path.startswith("/threads/"):
            return True
    if method == "POST" and rest_path == "/register":
        return True
    return False


class PlazaIsolationMiddleware(BaseHTTPMiddleware):
    """广场隔离中间件（完整实现，开箱即用）。"""

    def __init__(self, app, master_key: Optional[str] = None) -> None:
        super().__init__(app)
        self._master_key = master_key or os.getenv(
            "HIVE_MASTER_KEY", "replace-with-strong-master-key"
        )

    async def dispatch(self, request, call_next):
        path = request.url.path
        if path != PLAZA_PREFIX and not path.startswith(PLAZA_PREFIX + "/"):
            # 非广场路径：放行（主系统由生产版中间件处理；骨架版保持 501）
            return await call_next(request)

        rest = path[len(PLAZA_PREFIX):]
        method = request.method.upper()

        # 管理台：主 X-API-Key == HIVE_MASTER_KEY
        if rest == "/admin" or rest.startswith("/admin/"):
            raw = request.headers.get(MAIN_KEY_HEADER)
            if not raw or raw != self._master_key:
                return JSONResponse(
                    status_code=401,
                    content={"error": "缺少或无效的管理员钥匙", "detail": "管理台需要 HIVE_MASTER_KEY"},
                )
            request.state.agent = SimpleNamespace(agent_id="admin", permissions=["admin"])
            return await call_next(request)

        # 公开端点放行
        if _is_plaza_public(method, rest):
            return await call_next(request)

        # 广场钥匙校验（独立钥匙表，不触主系统）
        plaza_key = request.headers.get(PLAZA_KEY_HEADER)
        try:
            from plaza.keys import verify_key as verify_plaza_key
        except Exception:  # pragma: no cover
            verify_plaza_key = None
        agent = verify_plaza_key(plaza_key) if (plaza_key and verify_plaza_key) else None
        if not agent:
            return JSONResponse(
                status_code=401,
                content={"error": "缺少或无效的 X-Plaza-Key", "detail": "请先注册广场获取专属钥匙"},
            )
        request.state.plaza_agent = agent
        return await call_next(request)
