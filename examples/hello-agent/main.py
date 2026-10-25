"""examples/hello-agent — 最小接入示例：一个 echo agent 走完接入五步

演示内容：sync → send → poll → ack → run 五步接入路径。
不依赖 Hive 服务端，用约 30 行内存实现模拟中央信箱，
只演示"协议长什么样"，业务只是一个 echo（技术原语，零业务泄露）。

运行：python examples/hello-agent/main.py
"""

import time
from collections import deque


# ── 模拟中央信箱（极简内存实现，仅演示协议形状）──────────────
class CentralInbox:
    def __init__(self):
        self.agents = {}      # agent_id -> 注册记录
        self.inboxes = {}     # agent_id -> 消息队列

    def register(self, agent_id, capabilities=()):
        self.agents[agent_id] = {"status": "online", "capabilities": list(capabilities)}
        self.inboxes[agent_id] = deque()
        return {"status": "ok", "announcement": {"text": "welcome to hive"}}

    def deliver(self, recipient, message):
        self.inboxes[recipient].append(message)
        return {"status": "ok", "message_id": message["id"]}

    def fetch(self, agent_id):
        return self.inboxes[agent_id].popleft() if self.inboxes[agent_id] else None


def new_message(sender, recipient, content, msg_type="text"):
    return {"id": "m-%d" % int(time.time() * 1000), "sender": sender,
            "recipient": recipient, "msg_type": msg_type, "content": content}


# ── 五步接入演示 ─────────────────────────────────────────────
def run_demo():
    """sync → send → poll → ack → run（echo），返回过程日志。"""
    hive = CentralInbox()
    agent_id = "echo-1"
    log = []

    # ① sync：上报状态与能力，领取开机公告（boot 确认闭环）
    sync = hive.register(agent_id, capabilities=["echo"])
    log.append("① sync: 注册 %s 成功 → %s" % (agent_id, sync["announcement"]))

    # ② send：投递一条消息（回环给自已，模拟 echo）
    msg = new_message(agent_id, agent_id, "ping")
    hive.deliver(msg["recipient"], msg)
    log.append("② send: 投递 msg_id=%s content=ping" % msg["id"])

    # ③ poll：长轮询拉取自己的消息
    got = hive.fetch(agent_id)
    log.append("③ poll: 取到 1 条 → sender=%s content=%s" % (got["sender"], got["content"]))

    # ④ ack：回执确认已处理
    log.append("④ ack: 确认 msg_id=%s" % got["id"])

    # ⑤ run：处理消息（echo 原样返回）
    log.append("⑤ run: echo → %s" % got["content"])
    return log


if __name__ == "__main__":
    for line in run_demo():
        print("[hello-agent]", line)
