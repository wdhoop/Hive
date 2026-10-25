"""Hive 通信层 — 闲时调度器（开源架构版）

设计意图
--------
IdleScheduler 是"闲时自主行动系统"的调度核心（对应生产版思想）：
- 智能体不必常驻在线；调度器按周期触发注册的周期任务（handler）；
- 任务只在"空闲档位"执行，避免与主任务抢资源；
- 调度状态可查询，供控制台监控。

骨架版复刻完整接口；方法体为占位。
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional

DEFAULT_INTERVAL = 3600  # 默认周期（秒）


@dataclass
class ScheduledTask:
    """一条调度任务。"""

    name: str
    handler: Callable
    interval_seconds: int = DEFAULT_INTERVAL
    last_run: float = 0.0
    enabled: bool = True

    def due(self) -> bool:
        """是否到执行时间。"""
        return self.enabled and (time.time() - self.last_run >= self.interval_seconds)


class IdleScheduler:
    """闲时调度器。"""

    def __init__(self, supermem_base_url: str = "http://127.0.0.1:8765") -> None:
        """初始化调度器。

        :param supermem_base_url: 记忆底座地址（骨架版占位，不连接真实服务）
        """
        raise NotImplementedError("骨架版不包含调度实现")

    def register(self, name: str, handler: Callable, interval_seconds: int = DEFAULT_INTERVAL) -> None:
        """注册周期任务。"""
        raise NotImplementedError

    def unregister(self, name: str) -> None:
        """注销任务。"""
        raise NotImplementedError

    def get_status(self) -> Dict[str, Any]:
        """返回任务注册表与下次触发时间。"""
        raise NotImplementedError


def register_default_tasks(scheduler: IdleScheduler) -> None:
    """注册生产版默认周期任务（骨架版仅注释示例）。

    生产版默认任务示例：
    - memory_maintenance：记忆维护（体检 / 备份 / 索引对账）
    - heartbeat_report：心跳上报
    - message_flush：积压消息补发
    """
    raise NotImplementedError("骨架版不注册默认任务")
