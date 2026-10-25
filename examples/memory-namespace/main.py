"""examples/memory-namespace — 命名空间隔离 + ACL 拒绝

演示内容：多个智能体共用一个记忆库时，谁的记忆归谁管 ——
同名的 key 落在各自命名空间下互不可见；越权写别人的命名空间被 ACL 拒绝。

运行：python examples/memory-namespace/main.py
"""


class NamespaceManager:
    """极简记忆网关：key 按 'namespace:key' 存储，ACL 只允许写本命名空间。"""

    def __init__(self):
        self.store = {}
        self.audit = []

    def write(self, agent, namespace, key, value):
        if namespace not in agent["allowed"]:
            self.audit.append("DENIED: %s 越权写 %s:%s" % (agent["id"], namespace, key))
            return {"status": "denied", "reason": "acl", "namespace": namespace}
        self.store["%s:%s" % (namespace, key)] = value
        self.audit.append("OK: %s 写 %s:%s = %s" % (agent["id"], namespace, key, value))
        return {"status": "ok", "key": "%s:%s" % (namespace, key)}

    def read(self, agent, namespace, key):
        if namespace not in agent["allowed"]:
            self.audit.append("DENIED: %s 越权读 %s:%s" % (agent["id"], namespace, key))
            return {"status": "denied", "reason": "acl", "namespace": namespace}
        return {"status": "ok", "value": self.store.get("%s:%s" % (namespace, key))}


def run_demo():
    """两个 agent 各写同名 key，再演示一次 ACL 拒绝，返回事件记录。"""
    mgr = NamespaceManager()
    alpha = {"id": "alpha", "allowed": ["alpha"]}
    beta = {"id": "beta", "allowed": ["beta"]}

    # 两个 agent 都写 key=counter（同名，但互不可见）
    mgr.write(alpha, "alpha", "counter", 1)
    mgr.write(beta, "beta", "counter", 1)

    # 各自读自己的，值互不串扰
    v1 = mgr.read(alpha, "alpha", "counter")["value"]
    v2 = mgr.read(beta, "beta", "counter")["value"]

    # 越权：beta 试图写 alpha 的命名空间 → ACL 拒绝
    denied = mgr.write(beta, "alpha", "counter", 999)

    return {
        "events": mgr.audit,
        "alpha_counter": v1,
        "beta_counter": v2,
        "cross_write_status": denied["status"],
    }


if __name__ == "__main__":
    r = run_demo()
    print("[memory-namespace]")
    for e in r["events"]:
        print("  ", e)
    print("  隔离验证: alpha.counter = %s, beta.counter = %s（同名互不影响）"
          % (r["alpha_counter"], r["beta_counter"]))
    print("  越权写 alpha 命名空间 → %s（ACL 拒绝）" % r["cross_write_status"])
