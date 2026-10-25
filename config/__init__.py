"""Hive — 多智能体联邦中枢（开源架构版）

config 包：统一配置入口。
"""

from .settings import HiveSettings, get_settings

__all__ = ["HiveSettings", "get_settings"]
