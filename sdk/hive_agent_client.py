"""Hive 接入 SDK — 智能体客户端（开源架构版）

设计意图
--------
HiveAgentClient 是智能体接入 Hive 的标准方式（PULL 优先）：
- sync：上报状态/元数据，并领取自己的待办公告（boot 确认闭环）；
- poll：长轮询拉取消息（最长 25s）；
- send：向其他智能体发送消息；
- ack：回执确认已处理；
- run：常驻主循环（poll → on_message 回调 → ack），配 stop 停止。

骨架版复刻完整接口；方法体为占位。接入示例见模块底部 docstring。
"""

from __future__ import annotations

import time
import uuid
from typing import Callable, Optional

DEFAULT_UA = (
    "HiveAgentClient/0.1 "
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)


class HiveAgentClient:
    """智能体侧 Hive 客户端（基于 httpx）。"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        agent_id: str,
        agent_name: str = "",
        user_agent: str = DEFAULT_UA,
        timeout: float = 30.0,
    ) -> None:
        """初始化客户端。

        :param base_url:   Hive 服务地址（如 http://127.0.0.1:8764）
        :param api_key:    智能体自己的 API Key（环境变量注入）
        :param agent_id:   全局唯一智能体 ID
        :param agent_name: 展示名
        :param user_agent: 与 Hive 链路约定的 UA
        :param timeout:    请求超时（秒）
        """
        self.agent_id = agent_id
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._timeout = timeout
        self._headers = {
            "X-API-Key": api_key,
            "User-Agent": user_agent or DEFAULT_UA,
            "Content-Type": "application/json",
        }
        self._running = False
        raise NotImplementedError("骨架版不包含客户端实现（构造参数已定义，供二次实现）")

    # ── 内部请求 ──────────────────────────────────────────
    def _request(
        self,
        method: str,
        path: str,
        body: Optional[dict] = None,
        timeout: Optional[float] = None,
    ) -> dict:
        """统一 HTTP 请求封装。"""
        raise NotImplementedError

    # ── 核心协议 ──────────────────────────────────────────
    def sync(self, status: str = "online", metadata: Optional[dict] = None) -> dict:
        """上报状态与元数据，返回待办公告。"""
        raise NotImplementedError

    def poll(self, timeout: Optional[int] = None, since: float = 0.0) -> list:
        """长轮询拉取新消息。"""
        raise NotImplementedError

    def send(
        self,
        recipient: str,
        content: str,
        msg_type: str = "text",
        topic: str = "",
        ttl: int = 86400,
        meta: Optional[dict] = None,
    ) -> dict:
        """发送消息。"""
        raise NotImplementedError

    def ack(self, message_id: str) -> dict:
        """回执确认。"""
        raise NotImplementedError

    # ── 常驻主循环 ────────────────────────────────────────
    def run(
        self,
        on_message: Optional[Callable] = None,
        on_announcement: Optional[Callable] = None,
        stop_check: Optional[Callable] = None,
    ) -> None:
        """进入常驻循环：poll → 回调 → ack。

        :param on_message:      消息回调（参数：message dict）
        :param on_announcement: 公告回调（参数：announcement dict）
        :param stop_check:      停止条件回调（返回 True 则退出）
        """
        raise NotImplementedError

    def stop(self) -> None:
        """停止主循环。"""
        raise NotImplementedError


# ── 接入示例（骨架版）────────────────────────────────────
#
# import os
# from sdk.hive_agent_client import HiveAgentClient
#
# client = HiveAgentClient(
#     base_url=os.getenv("HIVE_BASE_URL", "http://127.0.0.1:8764"),
#     api_key=os.getenv("AGENT_API_KEY"),
#     agent_id="my-agent",
#     agent_name="My Agent",
# )
#
# # 一次性交互
# client.sync(status="online")
# messages = client.poll(timeout=5)
# for msg in messages:
#     print("收到:", msg["content"])
#     client.ack(msg["id"])
#
# # 常驻模式
# client.run(on_message=lambda m: print("收到:", m["content"]))
