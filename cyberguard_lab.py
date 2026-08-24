"""CyberGuard AI safe authorization lab.

This module provides a real, runnable training workflow for isolated labs.
It deliberately does not execute exploitation, credential theft, malware,
persistence, evasion, or attacks against external targets.
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone

DB = os.getenv("CYBERGUARD_DB", "cyberguard.db")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def init_db() -> None:
    with sqlite3.connect(DB) as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS authorizations (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            target TEXT NOT NULL,
            scope TEXT NOT NULL,
            start_at TEXT NOT NULL,
            end_at TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            approved_by TEXT,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            actor TEXT NOT NULL,
            details TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)


def request_authorization(user_id: str, target: str, scope: str,
                          start_at: str, end_at: str) -> str:
    auth_id = "AUTH-" + uuid.uuid4().hex[:10].upper()
    with sqlite3.connect(DB) as con:
        con.execute(
            "INSERT INTO authorizations VALUES (?, ?, ?, ?, ?, ?, 'pending', NULL, ?)",
            (auth_id, user_id, target, scope, start_at, end_at, now()),
        )
        con.execute(
            "INSERT INTO audit_log(event,actor,details,created_at) VALUES(?,?,?,?)",
            ("authorization_requested", user_id,
             json.dumps({"authorization_id": auth_id, "target": target, "scope": scope}), now()),
        )
    return auth_id


def approve_authorization(auth_id: str, admin_id: str) -> None:
    with sqlite3.connect(DB) as con:
        cur = con.execute(
            "UPDATE authorizations SET status='approved', approved_by=? WHERE id=? AND status='pending'",
            (admin_id, auth_id),
        )
        if cur.rowcount != 1:
            raise ValueError("Authorization not found or already processed")
        con.execute(
            "INSERT INTO audit_log(event,actor,details,created_at) VALUES(?,?,?,?)",
            ("authorization_approved", admin_id,
             json.dumps({"authorization_id": auth_id}), now()),
        )


def deny_authorization(auth_id: str, admin_id: str) -> None:
    with sqlite3.connect(DB) as con:
        con.execute("UPDATE authorizations SET status='denied', approved_by=? WHERE id=?", (admin_id, auth_id))
        con.execute(
            "INSERT INTO audit_log(event,actor,details,created_at) VALUES(?,?,?,?)",
            ("authorization_denied", admin_id, json.dumps({"authorization_id": auth_id}), now()),
        )


def list_pending() -> list[tuple]:
    with sqlite3.connect(DB) as con:
        return con.execute(
            "SELECT id,user_id,target,scope,start_at,end_at,status,approved_by FROM authorizations WHERE status='pending'"
        ).fetchall()


if __name__ == "__main__":
    init_db()
    print("CyberGuard AI lab database initialized.")
    print("Mode: SAFE / AUTHORIZATION REQUIRED / ISOLATED LABS ONLY")
