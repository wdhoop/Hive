"""examples/two-agents — 两个 mock agent 经中央信箱互发（PULL 长轮询）

演示内容：PULL 优先协议 —— 服务端不推送，收件方主动 poll；
消息积压在信箱里，掉线/离线也不丢，重连后补齐。
业务是两个 counter agent 互致问候（技术原语，零业务泄露）。

运行：python examples/two-agents/main.py
"""

import time
from collections import deque


class CentralInbox:
    """模拟中央信箱：注册 + 投递 + PULL 拉取。"""

    def __init__(self):
        self.inboxes = {}

    def register(self, agent_id):
        self.inboxes[agent_id] = deque()

    def deliver(self, recipient, message):
        self.inboxes[recipient].append(message)
        return {"status": "ok", "message_id": message["id"]}

    def poll(self, agent_id, timeout=0.5):
        """长轮询：等待最多 timeout 秒，无消息返回空列表。"""
        deadline = time.time() + timeout
        while time.time() < deadline:
            if self.inboxes[agent_id]:
                return [self.inboxes[agent_id].popleft()]
            time.sleep(0.05)
        return []


def new_message(sender, recipient, content):
    return {"id": "m-%d-%s" % (int(time.time() * 1000), sender),
            "sender": sender, "recipient": recipient,
            "msg_type": "text", "content": content}


def run_demo():
    """alpha 与 beta 互发一条消息，返回往返轨迹。"""
    hive = CentralInbox()
    alpha, beta = "alpha", "beta"
    hive.register(alpha)
    hive.register(beta)
    log = []

    # alpha 发消息给 beta（消息立即进入 beta 的信箱，不依赖 beta 在线）
    m1 = new_message(alpha, beta, "hello beta")
    hive.deliver(beta, m1)
    log.append("send: %s → %s  '%s' (已积压，beta 可稍后拉取)" % (alpha, beta, m1["content"]))

    # beta 长轮询拉取（PULL）
    got = hive.poll(beta)
    log.append("poll: %s 取到 %d 条 → %s" % (beta, len(got), got[0]["content"]))

    # beta 回执并回复
    log.append("ack:  %s 确认 %s" % (beta, got[0]["id"]))
    m2 = new_message(beta, alpha, "hi alpha")
    hive.deliver(alpha, m2)

    # alpha 长轮询拉取 beta 的回复
    got2 = hive.poll(alpha)
    log.append("poll: %s 取到 %d 条 → %s" % (alpha, len(got2), got2[0]["content"]))
    log.append("ack:  %s 确认 %s" % (alpha, got2[0]["id"]))
    return log


if __name__ == "__main__":
    for line in run_demo():
        print("[two-agents]", line)
