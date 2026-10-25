"""Hive 示例一键验证（不依赖 pytest，纯标准库）

运行：python scripts/_verify_examples.py

依次执行五组示例的 demo 并断言契约行为，全部通过输出 PASS。
同时复跑骨架导入自检（_verify_imports 的核心断言），确认示例未破坏骨架契约。
"""

import importlib.util
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAMPLES_DIR = os.path.join(ROOT, "examples")

if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

EXAMPLES = [
    ("hello-agent", "hello-agent", ["① sync", "② send", "③ poll", "④ ack", "⑤ run", "echo → ping"], "list"),
    ("two-agents", "two-agents", ["hello beta", "hi alpha", "poll:", "ack:"], "list"),
    ("memory-namespace", "memory-namespace", ["DENIED", "alpha_counter=1", "beta_counter=1", "cross_write_status=denied"], "dict"),
    ("optimistic-lock", "optimistic-lock", ["conflict", "最新快照", "重试", "ok"], "list"),
    ("antibody", "antibody", ["unreliable=True", "生成抗体", "fallback", "经 antibody"], "list"),
]


def load_example(name):
    path = os.path.join(EXAMPLES_DIR, name, "main.py")
    spec = importlib.util.spec_from_file_location("verify_" + name.replace("-", "_"), path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def flatten(kind, result):
    if kind == "list":
        return "\n".join(result)
    return "\n".join(result["events"]) + "\n" + " ".join(
        "%s=%s" % (k, v) for k, v in result.items() if k != "events"
    )


def check_skeleton_imports():
    """骨架契约仍可导入（与 tests/test_skeleton.py 同源断言）。"""
    import importlib
    for pkg in ["communication", "gateway", "security", "self_heal", "sdk"]:
        importlib.import_module(pkg)
    import server
    app = server.create_app()
    assert app.title.startswith("Hive")


def main():
    failed = 0
    for label, name, expects, kind in EXAMPLES:
        mod = load_example(name)
        joined = flatten(kind, mod.run_demo())
        missing = [k for k in expects if k not in joined]
        status = "PASS" if not missing else "FAIL"
        print("[%s] %s" % (status, label))
        if missing:
            failed += 1
            print("   missing:", missing)
    try:
        check_skeleton_imports()
        print("[PASS] skeleton imports (communication/gateway/security/self_heal/sdk/server)")
    except Exception as e:  # noqa: BLE001
        failed += 1
        print("[FAIL] skeleton imports:", e)
    print("")
    print("RESULT:", "全部通过" if failed == 0 else "%d 项未通过" % failed)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
