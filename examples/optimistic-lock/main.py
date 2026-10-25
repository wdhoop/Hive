"""examples/optimistic-lock — 并发写冲突：版本快照 + 重试

演示内容：两个智能体并发写同一记忆 key 时，后写者带过期版本号写入 →
服务端返回 409 冲突并附最新快照 → 写者按快照更新版本后重试成功。

运行：python examples/optimistic-lock/main.py
"""


class OptimisticLockStore:
    """极简乐观锁：每份数据带 version，写必须携带当前版本号。"""

    def __init__(self):
        self.data = {}  # key -> {"version": int, "value": str}

    def write(self, key, version, value):
        cur = self.data.get(key)
        if cur and version != cur["version"]:
            return {"status": "conflict", "latest": dict(cur), "key": key}
        nv = (cur["version"] + 1) if cur else 1
        self.data[key] = {"version": nv, "value": value}
        return {"status": "ok", "version": nv, "value": value}

    def read(self, key):
        return dict(self.data.get(key, {"version": 0, "value": None}))


def run_demo():
    """agent A 先写、agent B 用旧版本写 → 冲突 → 按快照重试成功。"""
    store = OptimisticLockStore()
    log = []

    # A 写入，得到版本 1
    w1 = store.write("counter", version=0, value="A:1")
    log.append("A 写 counter → %s (version=%d)" % (w1["status"], w1["version"]))

    # B 用过期版本 0 写入（模拟并发时拿到的旧快照）→ 409 冲突
    w2 = store.write("counter", version=0, value="B:1")
    log.append("B 用过期版本写 → %s，服务端返回最新快照 %s"
               % (w2["status"], w2["latest"]))

    # B 按快照的版本号重试 → 成功
    snap = w2["latest"]["version"]
    w3 = store.write("counter", version=snap, value="B:2")
    log.append("B 按快照版本 %d 重试 → %s (version=%d)"
               % (snap, w3["status"], w3["version"]))

    # 终态：后写者 B 生效，版本推进
    log.append("终态 counter = %s（后写者生效，未丢更新）"
               % store.read("counter")["value"])
    return log


if __name__ == "__main__":
    for line in run_demo():
        print("[optimistic-lock]", line)
