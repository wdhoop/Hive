"""Hive 骨架自检示例（开源架构版）

本测试仅验证"架构契约存在且可导入"，不依赖任何真实实现。
运行：python -m pytest tests/ -v
"""

import importlib

PACKAGES = ["communication", "gateway", "security", "self_heal", "sdk"]
CONTRACT_MODULES = [
    "communication.models",       # 消息 / 智能体数据契约
    "communication.bus",          # MqttBus
    "communication.agent_registry",  # AgentRegistry
    "communication.router",       # MessageRouter
    "communication.scheduler",    # IdleScheduler
    "communication.task_distributor",  # TaskDistributor
    "communication.cloud_gateway",    # CloudGateway / CentralInbox
    "communication.mem_sync",     # MemSyncStore
    "gateway.memory_proxy",       # SuperMemProxy
    "gateway.router",             # RouteTable
    "gateway.namespace",          # NamespaceManager
    "gateway.audit",              # AuditLogger
    "gateway.optimistic_lock",    # OptimisticLock
    "gateway.search",             # GlobalSearch
    "gateway.snapshot",           # SnapshotManager
    "security.models",            # 权限 / Key / 身份模型
    "security.api_key_manager",   # ApiKeyManager
    "security.middleware",        # AuthMiddleware / RateLimiter
    "self_heal.antibody",         # AntibodyLibrary
    "self_heal.failure_tracker",  # FailureTracker
    "sdk.hive_agent_client",      # HiveAgentClient
]


def test_all_packages_importable():
    for pkg in PACKAGES:
        importlib.import_module(pkg)


def test_all_contract_modules_importable():
    for mod in CONTRACT_MODULES:
        importlib.import_module(mod)


def test_message_contract_fields():
    """核心数据契约字段存在（唯一完整实现的模块）。"""
    from communication.models import Message, MessageType, AgentStatus

    m = Message(sender="a", recipient="b", msg_type=MessageType.TEXT, content="hi")
    d = m.to_dict()
    assert d["sender"] == "a"
    assert d["recipient"] == "b"
    assert m.is_expired() is False
    assert Message.from_dict(d).to_dict() == d
    assert {s.value for s in AgentStatus} == {"online", "offline", "busy", "idle", "error"}


def test_scaffold_server_assembles():
    """主服务可装配（不启动网络端口）。"""
    import server

    app = server.create_app()
    assert app.title.startswith("Hive")


def test_every_placeholder_raises_not_implemented():
    """占位实现必须抛 NotImplementedError（防止"假装实现"）。"""
    from communication.bus import MqttBus

    bus = MqttBus.__new__(MqttBus)  # 绕过 __init__ 占位
    try:
        bus.connect()
    except NotImplementedError:
        pass
    else:
        raise AssertionError("MqttBus.connect 应抛出 NotImplementedError")
