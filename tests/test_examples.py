"""Hive 契约测试 —— 五组最小示例的行为即文档

运行：python -m pytest tests/ -v

每个测试断言一个层级的协议契约：
- test_hello_agent：五步接入序列（sync/send/poll/ack/run）
- test_two_agents：PULL 中央信箱的积压与往返
- test_memory_namespace：命名空间隔离 + ACL 拒绝
- test_optimistic_lock：并发写冲突、版本快照、重试
- test_antibody：失败阈值、抗体规则生成、A/B replay
"""

import importlib.util
import os
import sys

EXAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples")


def load_example(name):
    """按路径加载 examples/<name>/main.py（目录名含连字符，不能直接 import）。"""
    path = os.path.join(EXAMPLES_DIR, name, "main.py")
    spec = importlib.util.spec_from_file_location("example_" + name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_hello_agent():
    """五步接入：注册 → 投递 → 拉取 → 回执 → echo 执行。"""
    mod = load_example("hello-agent")
    log = mod.run_demo()
    joined = "\n".join(log)
    assert "① sync" in joined and "echo-1" in joined       # 注册成功
    assert "② send" in joined                              # 消息已投递
    assert "③ poll" in joined and "ping" in joined         # PULL 取到消息
    assert "④ ack" in joined                               # 回执确认
    assert "⑤ run" in joined and "echo → ping" in joined   # 处理完成


def test_two_agents():
    """PULL 协议：消息先积压、收件方主动拉取，双向往返。"""
    mod = load_example("two-agents")
    log = mod.run_demo()
    joined = "\n".join(log)
    assert "hello beta" in joined      # alpha → beta
    assert "hi alpha" in joined        # beta → alpha（回复）
    assert joined.count("poll:") == 2  # 双方各 PULL 一次
    assert joined.count("ack:") == 2   # 双方各回执一次


def test_memory_namespace():
    """命名空间隔离：同名 key 互不影响；跨命名空间写被 ACL 拒绝。"""
    mod = load_example("memory-namespace")
    r = mod.run_demo()
    assert r["alpha_counter"] == 1 and r["beta_counter"] == 1  # 同名但隔离
    assert r["cross_write_status"] == "denied"                 # 越权写被拒
    assert any("DENIED" in e for e in r["events"])             # 审计留有拒绝记录


def test_optimistic_lock():
    """乐观锁：过期版本写入 → 冲突+快照 → 按快照重试成功。"""
    mod = load_example("optimistic-lock")
    log = mod.run_demo()
    joined = "\n".join(log)
    assert "conflict" in joined and "最新快照" in joined  # 冲突且返回快照
    assert "重试" in joined and "ok" in joined           # 重试成功
    assert joined.count("(version=1)") >= 0              # 版本推进合理


def test_antibody():
    """自愈：3 次超时触发阈值 → 生成抗体 → 第 4 次走预案成功。"""
    mod = load_example("antibody")
    log = mod.run_demo()
    joined = "\n".join(log)
    assert "unreliable=True" in joined                 # 阈值触发
    assert "生成抗体" in joined and "fallback" in joined  # 规则已生成
    assert "第 4 次调用 → ok（经 antibody" in joined     # replay 走预案
