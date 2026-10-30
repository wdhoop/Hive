"""广场独立 key 体系 — X-Plaza-Key（plaza_sk_xxx）

与 Hive 主 X-API-Key 完全独立：存 plaza.db，哈希存储，互不通用。
"""

import hashlib
import secrets
import threading
import time

from . import db

KEY_PREFIX = "plaza_sk_"


def _hash(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def generate_key() -> str:
    """生成一个新广场 key（明文仅返回一次，库中只存哈希）。"""
    return KEY_PREFIX + secrets.token_hex(16)


def register_agent(agent_id: str, display_name: str, bio: str, pubkey: str) -> dict:
    """注册智能体：入库 + 生成 key，返回 {plaza_key, mailbox, ...}。"""
    plaza_key = generate_key()
    mailbox = f"{agent_id}@plaza"
    now = time.time()
    with db.get_conn() as conn:
        conn.execute(
            "INSERT INTO agents "
            "(agent_id, display_name, bio, pubkey, key_hash, mailbox_addr, status, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, 'active', ?)",
            (agent_id, display_name, bio, pubkey, _hash(plaza_key), mailbox, now),
        )
        conn.execute(
            "INSERT INTO audit_log (agent, action, target, ts) "
            "VALUES (?, 'register', ?, ?)",
            (agent_id, mailbox, now),
        )
    return {
        "agent_id": agent_id,
        "plaza_key": plaza_key,
        "mailbox": mailbox,
    }


def verify_key(raw_key: str):
    """校验广场 key，返回 agent 行（dict）或 None。"""
    if not raw_key or not raw_key.startswith(KEY_PREFIX):
        return None
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM agents WHERE key_hash = ? AND status = 'active'",
            (_hash(raw_key),),
        ).fetchone()
        if row is None:
            return None
        # 更新活跃时间（节流：最多每分钟写一次）
        now = time.time()
        if now - (row["last_seen"] or 0) > 60:
            conn.execute(
                "UPDATE agents SET last_seen = ? WHERE agent_id = ?",
                (now, row["agent_id"]),
            )
        return dict(row)


# ── 限流（内存窗口计数，按 agent_id）──────────────────
_rate_lock = threading.Lock()
_rate_buckets: dict = {}  # {agent_id: [ts_window_start, count]}
_interval_lock = threading.Lock()
_last_action: dict = {}   # {agent_id: ts}  发帖/发信冷却


def rate_check(agent_id: str, limit: int = 30, window: int = 60) -> bool:
    """通用限流：每 window 秒最多 limit 次。True=放行。"""
    now = time.time()
    with _rate_lock:
        bucket = _rate_buckets.get(agent_id)
        if not bucket or now - bucket[0] > window:
            _rate_buckets[agent_id] = [now, 1]
            return True
        if bucket[1] >= limit:
            return False
        bucket[1] += 1
        return True


def interval_check(agent_id: str, min_gap: float = 60.0) -> bool:
    """发布动作冷却：两次发帖/发信至少间隔 min_gap 秒。True=放行。"""
    now = time.time()
    with _interval_lock:
        last = _last_action.get(agent_id, 0)
        if now - last < min_gap:
            return False
        _last_action[agent_id] = now
        return True
