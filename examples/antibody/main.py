"""examples/antibody — 超时失败 → 归因 → 抗体规则 → A/B replay 验证

演示内容：某 agent 连续 3 次调用超时后，失败跟踪器判定其不可靠，
抗体库自动生成一条"降级预案"；第 4 次同一请求直接走预案成功，
并用 A/B replay 对比：走旧路径失败 vs 走预案成功。

运行：python examples/antibody/main.py
"""

FAILURE_THRESHOLD = 3


class FailureTracker:
    """按 agent 累计失败次数，达到阈值标记不可靠。"""

    def __init__(self, threshold=FAILURE_THRESHOLD):
        self.threshold = threshold
        self.failures = {}
        self.unreliable = {}

    def record(self, agent_id, error):
        self.failures[agent_id] = self.failures.get(agent_id, 0) + 1
        if self.failures[agent_id] >= self.threshold:
            self.unreliable[agent_id] = True
        return {"status": "timeout", "agent": agent_id,
                "failures": self.failures[agent_id],
                "unreliable": self.unreliable.get(agent_id, False),
                "error": error}


class AntibodyLibrary:
    """失败模式 → 修复预案。"""

    def __init__(self):
        self.antibodies = {}

    def learn(self, agent_id, pattern, plan):
        self.antibodies[agent_id] = {"pattern": pattern, "plan": plan}
        return self.antibodies[agent_id]


def slow_call(agent_id, tracker):
    """模拟一次调用：超时 → 记录失败；已生成预案则直接走预案。"""
    if agent_id in tracker.unreliable:
        plan = tracker.plans[agent_id]
        return {"status": "ok", "via": "antibody", "plan": plan}
    return tracker.record(agent_id, "timeout")


def run_demo():
    """三次超时生成抗体，第四次走预案成功；返回过程日志。"""
    tracker = FailureTracker()
    library = AntibodyLibrary()
    tracker.plans = {}
    log = []

    # 前 3 次：连续超时，第 3 次触发"不可靠"标记
    for i in range(1, FAILURE_THRESHOLD + 1):
        r = slow_call("sensor-1", tracker)
        log.append("第 %d 次调用 → %s（失败累计 %d，unreliable=%s）"
                   % (i, r["status"], r["failures"], r["unreliable"]))

    # 归因 → 生成抗体规则（降级预案）
    rule = library.learn("sensor-1", "timeout", "fallback: offline-cache")
    tracker.plans["sensor-1"] = rule["plan"]
    log.append("生成抗体: pattern=%s → plan=%s" % (rule["pattern"], rule["plan"]))

    # A/B replay：第 4 次走预案成功（旧路径必然再超时，预案直接兜底）
    r4 = slow_call("sensor-1", tracker)
    log.append("第 4 次调用 → %s（经 %s，plan=%s）"
               % (r4["status"], r4["via"], r4["plan"]))
    return log


if __name__ == "__main__":
    for line in run_demo():
        print("[antibody]", line)
