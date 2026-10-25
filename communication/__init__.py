"""Hive 通信层（开源架构版）

通信层是 Hive 的核心：让多个智能体注册、发现、互发消息、分工协作。
本骨架复刻全部接口契约，不包含真实实现。
"""

from .models import Message, MessageType, AgentRecord, AgentStatus
from .bus import MqttBus
from .agent_registry import AgentRegistry
from .router import MessageRouter
from .scheduler import IdleScheduler, ScheduledTask
from .task_distributor import TaskDistributor, HiveTask, TaskStatus
from .cloud_gateway import CloudGateway, CentralInbox, BootNotifier, WebhookDeliverer
from .mem_sync import MemSyncStore

__all__ = [
    "Message", "MessageType", "AgentRecord", "AgentStatus",
    "MqttBus", "AgentRegistry", "MessageRouter",
    "IdleScheduler", "ScheduledTask",
    "TaskDistributor", "HiveTask", "TaskStatus",
    "CloudGateway", "CentralInbox", "BootNotifier", "WebhookDeliverer",
    "MemSyncStore",
]
