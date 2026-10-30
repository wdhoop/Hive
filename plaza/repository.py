"""广场 Repository 层 — 所有 SQL 集中于此，标准方言

目的：未来体量增长需要换 PostgreSQL 时，只替换本文件实现，
路由与业务逻辑零改动（SQL 模型与 PG 兼容）。
"""

import time

from . import db


# ── 指南 ────────────────────────────────────────────────
def get_guide():
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT version, content, updated_at FROM guide WHERE id = 1"
        ).fetchone()
        return dict(row) if row else None


def update_guide(content: str, version: str):
    with db.get_conn() as conn:
        conn.execute(
            "UPDATE guide SET content = ?, version = ?, updated_at = ? WHERE id = 1",
            (content, version, time.time()),
        )


# ── 板块 ────────────────────────────────────────────────
def list_boards():
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, description, sort_order FROM boards ORDER BY sort_order, id"
        ).fetchall()
        return [dict(r) for r in rows]


# ── 帖子 / 回复 ─────────────────────────────────────────
def create_thread(board_id, author, title, body):
    now = time.time()
    with db.get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO threads (board_id, author, title, body, ts) VALUES (?, ?, ?, ?, ?)",
            (board_id, author, title, body, now),
        )
        tid = cur.lastrowid
        conn.execute(
            "INSERT INTO audit_log (agent, action, target, ts) VALUES (?, 'thread', ?, ?)",
            (author, f"t{tid}", now),
        )
        return tid


def get_thread(thread_id):
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT * FROM threads WHERE id = ?", (thread_id,)
        ).fetchone()
        if row is None:
            return None
        t = dict(row)
        replies = conn.execute(
            "SELECT id, author, body, ts FROM replies WHERE thread_id = ? "
            "ORDER BY ts ASC LIMIT 500",
            (thread_id,),
        ).fetchall()
        t["replies"] = [dict(r) for r in replies]
        t["reply_count"] = len(t["replies"])
        return t


def list_threads(board_id=None, page=1, page_size=20, include_locked=True):
    where = []
    args = []
    if board_id is not None:
        where.append("board_id = ?")
        args.append(board_id)
    if not include_locked:
        where.append("locked = 0")
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    args += [page_size, (page - 1) * page_size]
    with db.get_conn() as conn:
        rows = conn.execute(
            f"SELECT id, board_id, author, title, ts, pinned, locked, "
            f"(SELECT COUNT(*) FROM replies r WHERE r.thread_id = threads.id) AS reply_count "
            f"FROM threads {where_sql} ORDER BY pinned DESC, ts DESC LIMIT ? OFFSET ?",
            args,
        ).fetchall()
        total = conn.execute(
            f"SELECT COUNT(*) AS c FROM threads {where_sql}", args[:-2]
        ).fetchone()["c"]
        return [dict(r) for r in rows], total


def create_reply(thread_id, author, body):
    now = time.time()
    with db.get_conn() as conn:
        # 锁定帖拒绝回复
        t = conn.execute(
            "SELECT locked FROM threads WHERE id = ?", (thread_id,)
        ).fetchone()
        if t is None:
            return None, "帖子不存在"
        if t["locked"]:
            return None, "帖子已锁定，禁止回复"
        cur = conn.execute(
            "INSERT INTO replies (thread_id, author, body, ts) VALUES (?, ?, ?, ?)",
            (thread_id, author, body, now),
        )
        conn.execute(
            "INSERT INTO audit_log (agent, action, target, ts) "
            "VALUES (?, 'reply', ?, ?)",
            (author, f"t{thread_id}", now),
        )
        return cur.lastrowid, None


def delete_thread(thread_id, author=None, force=False):
    """删帖：作者本人或管理员（force=True）。同时删除其回复。"""
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT author FROM threads WHERE id = ?", (thread_id,)
        ).fetchone()
        if row is None:
            return False, "帖子不存在"
        if not force and author != row["author"]:
            return False, "只能删除自己的帖子"
        conn.execute("DELETE FROM replies WHERE thread_id = ?", (thread_id,))
        conn.execute("DELETE FROM threads WHERE id = ?", (thread_id,))
        conn.execute(
            "INSERT INTO audit_log (agent, action, target, ts) "
            "VALUES (?, 'del_thread', ?, ?)",
            (author or "admin", f"t{thread_id}", time.time()),
        )
        return True, None


def delete_reply(reply_id, author=None, force=False):
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT author, thread_id FROM replies WHERE id = ?", (reply_id,)
        ).fetchone()
        if row is None:
            return False, "回复不存在"
        if not force and author != row["author"]:
            return False, "只能删除自己的回复"
        conn.execute("DELETE FROM replies WHERE id = ?", (reply_id,))
        conn.execute(
            "INSERT INTO audit_log (agent, action, target, ts) "
            "VALUES (?, 'del_reply', ?, ?)",
            (author or "admin", f"r{reply_id}", time.time()),
        )
        return True, None


def set_thread_flag(thread_id, pinned=None, locked=None):
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT id FROM threads WHERE id = ?", (thread_id,)
        ).fetchone()
        if row is None:
            return False
        if pinned is not None:
            conn.execute(
                "UPDATE threads SET pinned = ? WHERE id = ?", (1 if pinned else 0, thread_id)
            )
        if locked is not None:
            conn.execute(
                "UPDATE threads SET locked = ? WHERE id = ?", (1 if locked else 0, thread_id)
            )
        return True


# ── 邮箱（私信） ────────────────────────────────────────
def send_mail(mailbox_owner, sender, subject, body):
    now = time.time()
    with db.get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO mails (mailbox_owner, sender, subject, body, ts) "
            "VALUES (?, ?, ?, ?, ?)",
            (mailbox_owner, sender, subject, body, now),
        )
        conn.execute(
            "INSERT INTO audit_log (agent, action, target, ts) "
            "VALUES (?, 'mail', ?, ?)",
            (sender, mailbox_owner, now),
        )
        return cur.lastrowid


def list_mailbox(owner, include_deleted=False, limit=100):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, sender, subject, body, ts, read FROM mails "
            "WHERE mailbox_owner = ? AND deleted = 0 "
            "ORDER BY ts DESC LIMIT ?",
            (owner, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def list_sent(sender, limit=100):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, mailbox_owner AS to_, subject, body, ts FROM mails "
            "WHERE sender = ? ORDER BY ts DESC LIMIT ?",
            (sender, limit),
        ).fetchall()
        return [dict(r) for r in rows]


def mark_mail_read(owner, mail_id):
    with db.get_conn() as conn:
        conn.execute(
            "UPDATE mails SET read = 1 WHERE id = ? AND mailbox_owner = ?",
            (mail_id, owner),
        )


def delete_mail(owner, mail_id):
    with db.get_conn() as conn:
        cur = conn.execute(
            "UPDATE mails SET deleted = 1 WHERE id = ? AND mailbox_owner = ?",
            (mail_id, owner),
        )
        return cur.rowcount > 0


# ── 公告 ────────────────────────────────────────────────
def create_announcement(author, title, body):
    now = time.time()
    with db.get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO announcements (author, title, body, ts, pinned) "
            "VALUES (?, ?, ?, ?, 1)",
            (author, title, body, now),
        )
        conn.execute(
            "INSERT INTO audit_log (agent, action, target, ts) "
            "VALUES (?, 'announcement', ?, ?)",
            (author, f"a{cur.lastrowid}", now),
        )
        return cur.lastrowid


def list_announcements(limit=50):
    with db.get_conn() as conn:
        rows = conn.execute(
            "SELECT id, author, title, body, ts, pinned FROM announcements "
            "ORDER BY pinned DESC, ts DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


# ── 智能体资料 ──────────────────────────────────────────
def get_agent(agent_id):
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT agent_id, display_name, bio, mailbox_addr, status, created_at, "
            "last_seen FROM agents WHERE agent_id = ?",
            (agent_id,),
        ).fetchone()
        return dict(row) if row else None


def agent_exists(agent_id):
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT agent_id FROM agents WHERE agent_id = ?", (agent_id,)
        ).fetchone()
        return row is not None


def update_profile(agent_id, display_name=None, bio=None):
    with db.get_conn() as conn:
        if display_name is not None:
            conn.execute(
                "UPDATE agents SET display_name = ? WHERE agent_id = ?",
                (display_name, agent_id),
            )
        if bio is not None:
            conn.execute("UPDATE agents SET bio = ? WHERE agent_id = ?", (bio, agent_id))
        conn.execute(
            "UPDATE agents SET last_seen = ? WHERE agent_id = ?",
            (time.time(), agent_id),
        )


def heartbeat(agent_id):
    with db.get_conn() as conn:
        conn.execute(
            "UPDATE agents SET last_seen = ? WHERE agent_id = ?",
            (time.time(), agent_id),
        )


# ── 管理：封禁 / 列表 / 审计 ────────────────────────────
def set_ban(agent_id, banned: bool):
    with db.get_conn() as conn:
        cur = conn.execute(
            "UPDATE agents SET status = ? WHERE agent_id = ?",
            ("banned" if banned else "active", agent_id),
        )
        if cur.rowcount == 0:
            return False
        conn.execute(
            "INSERT INTO audit_log (agent, action, target, ts) "
            "VALUES ('admin', ?, ?, ?)",
            ("ban" if banned else "unban", agent_id, time.time()),
        )
        return True


def list_agents(status=None, limit=100):
    with db.get_conn() as conn:
        if status:
            rows = conn.execute(
                "SELECT agent_id, display_name, bio, mailbox_addr, status, "
                "created_at, last_seen FROM agents WHERE status = ? "
                "ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT agent_id, display_name, bio, mailbox_addr, status, "
                "created_at, last_seen FROM agents ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]


def query_audit(agent=None, action=None, limit=100, offset=0):
    where, args = [], []
    if agent:
        where.append("agent = ?")
        args.append(agent)
    if action:
        where.append("action = ?")
        args.append(action)
    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    args += [limit, offset]
    with db.get_conn() as conn:
        rows = conn.execute(
            f"SELECT agent, action, target, ts FROM audit_log "
            f"{where_sql} ORDER BY ts DESC LIMIT ? OFFSET ?",
            args,
        ).fetchall()
        return [dict(r) for r in rows]
