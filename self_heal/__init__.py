"""Hive 自愈层（开源架构版）

自愈层让系统从错误中"长记性"：失败被跟踪、沉淀为可复用的修复预案（抗体），
后续同类错误直接命中预案自动处理。
本骨架复刻全部接口契约。
"""

from .antibody import Antibody, AntibodyLibrary
from .failure_tracker import FailureTracker

__all__ = ["Antibody", "AntibodyLibrary", "FailureTracker"]
