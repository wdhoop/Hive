"""Hive 开源骨架 — 导入与装配验证脚本

用法：python scripts/_verify_imports.py
（脚本位于 hive/scripts/ 下，自动推导项目根目录）
"""

import os
import sys
import traceback

HIVE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HIVE_DIR)

mods = [
    "communication",
    "communication.models",
    "communication.bus",
    "communication.agent_registry",
    "communication.router",
    "communication.scheduler",
    "communication.task_distributor",
    "communication.cloud_gateway",
    "communication.mem_sync",
    "gateway",
    "gateway.memory_proxy",
    "gateway.router",
    "gateway.namespace",
    "gateway.audit",
    "gateway.optimistic_lock",
    "gateway.search",
    "gateway.snapshot",
    "security",
    "security.models",
    "security.api_key_manager",
    "security.middleware",
    "self_heal",
    "self_heal.antibody",
    "self_heal.failure_tracker",
    "sdk",
    "sdk.hive_agent_client",
    "config",
    "config.settings",
]

failed = []
for m in mods:
    try:
        __import__(m)
    except Exception:
        failed.append(m)
        print("FAIL:", m)
        traceback.print_exc()

if failed:
    print("RESULT: FAIL", len(failed), "个模块导入失败:", failed)
    sys.exit(1)

try:
    import server
    app = server.create_app()
    print("RESULT: OK — 全部", len(mods), "个模块可导入；服务装配成功:", app.title)
except Exception:
    print("server 装配失败:")
    traceback.print_exc()
    sys.exit(1)
