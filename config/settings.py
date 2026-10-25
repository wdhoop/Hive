"""Hive 配置模板（开源骨架版）

安全说明
--------
本文件只声明配置项与默认值，**不包含任何真实凭据**。
所有敏感值必须通过环境变量注入；缺失时使用占位默认值，
生产环境接入请参考 `.env.example` 约定（本仓库不提交 `.env`）。

环境变量速查
------------
- HIVE_HOST / HIVE_PORT     服务监听地址与端口
- HIVE_MASTER_KEY           初始 Master API Key（首次启动生成，可覆盖）
- SUPERMEM_BASE_URL         记忆底座地址（骨架版占位，不依赖真实服务）
- HIVE_DB_PATH              状态库路径（SQLite）
- HIVE_LOG_LEVEL            日志级别
"""

import os
from pathlib import Path
from typing import Optional


class HiveSettings:
    """Hive 统一配置。

    生产版配置项均已在此收敛；骨架版只保留架构所需的最小集合。
    """

    # ── 服务 ────────────────────────────────────────────────
    HOST: str = os.getenv("HIVE_HOST", "127.0.0.1")
    PORT: int = int(os.getenv("HIVE_PORT", "8764"))

    # ── 安全 ────────────────────────────────────────────────
    # 占位默认值：任何真实部署必须显式注入，禁止沿用此值
    HIVE_MASTER_KEY: str = os.getenv("HIVE_MASTER_KEY", "replace-with-strong-master-key")

    # ── 记忆底座 ────────────────────────────────────────────
    # 骨架版指向占位地址；不连接任何真实记忆服务
    SUPERMEM_BASE_URL: str = os.getenv("SUPERMEM_BASE_URL", "http://127.0.0.1:8765")
    SUPERMEM_TOKEN: Optional[str] = os.getenv("SUPERMEM_TOKEN", None)

    # ── 存储 ────────────────────────────────────────────────
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DB_PATH: str = os.getenv("HIVE_DB_PATH", str(BASE_DIR / "data" / "hive.db"))

    # ── 日志 ────────────────────────────────────────────────
    LOG_LEVEL: str = os.getenv("HIVE_LOG_LEVEL", "INFO")

    # ── 通信参数（默认值参考生产设计）───────────────────────
    MQTT_HOST: str = os.getenv("MQTT_HOST", "127.0.0.1")
    MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
    INBOX_POLL_TIMEOUT: int = int(os.getenv("INBOX_POLL_TIMEOUT", "25"))  # 长轮询上限（秒）
    MESSAGE_TTL: int = int(os.getenv("MESSAGE_TTL", "86400"))              # 消息默认 TTL（秒）

    # ── 自愈 ────────────────────────────────────────────────
    FAILURE_THRESHOLD: int = int(os.getenv("FAILURE_THRESHOLD", "3"))


def get_settings() -> HiveSettings:
    """返回配置单例（骨架版：每次构造即可，无缓存副作用）。"""
    return HiveSettings()
