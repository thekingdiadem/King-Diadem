# =============================================================================
# 👑 KING DIADEM — core/api_keys.py
# FATE™ API Key Governance Layer
#
# หลักการ:
# - มนุษย์ไม่ต้องจำ key เพิ่ม — ผูกกับ email ที่ login อยู่แล้ว
# - key แข็งแกร่งกว่า session cookie — signed, scoped, rate-limited, auditable
# - ทุก action อธิบายย้อนกลับได้ (FATE™ audit trail)
# - SQLite เดิมของ DATABASE/db.py — ไม่เพิ่ม dependency ใหม่
#
# Import ใน app.py:
#   from core.api_keys import (
#       ensure_api_key, validate_api_key, get_key_info,
#       rotate_api_key, revoke_api_key, list_user_keys,
#       record_key_usage, get_usage_stats,
#       APIKeyMiddleware, require_api_key,
#   )
#
# FATE™ Axiom: "ถ้าอธิบายไม่ได้ = ใช้ไม่ได้"
# =============================================================================

import os
import time
import uuid
import hmac
import hashlib
import sqlite3
import threading
import functools
from typing import Optional, Dict, Any, List, Tuple

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse

# =============================================================================
# CONFIG
# =============================================================================

_DB_PATH     = os.getenv("KD_DB_PATH", "data/king_diadem.db")

# SECURITY: ห้ามมี default fallback สำหรับ SECRET_KEY
# เดิมฝัง "king-diadem-secret-2026" ไว้ตรงนี้ ซึ่งอยู่ใน public repo แล้ว —
# ใครก็คำนวณ key_hash / key_id signature ปลอมได้ถ้ายังใช้ค่านี้จริงใน production
_SECRET_SALT = os.getenv("SECRET_KEY")
if not _SECRET_SALT:
    raise RuntimeError(
        "❌ SECRET_KEY environment variable ไม่ได้ตั้งค่า — "
        "core/api_keys.py ต้องมี SECRET_KEY จริงจาก environment เท่านั้น "
        "(ห้ามใช้ default เดิมที่เคยฝังใน public repo)"
    )

_KEY_PREFIX  = "kd_"

# Rate limits per scope (requests per window)
_RATE_LIMITS: Dict[str, Dict[str, int]] = {
    "user": {
        "window_sec":  60,
        "max_calls":   30,    # 30 req/min
        "max_daily":   500,   # 500 req/day
    },
    "premium": {
        "window_sec":  60,
        "max_calls":   120,
        "max_daily":   5000,
    },
    "admin": {
        "window_sec":  60,
        "max_calls":   600,
        "max_daily":   50000,
    },
    "readonly": {
        "window_sec":  60,
        "max_calls":   20,
        "max_daily":   200,
    },
}

# Scopes: what each key is allowed to do
_SCOPE_PERMISSIONS: Dict[str, List[str]] = {
    "user":     ["run", "decision", "simulate", "chat_state", "report_read"],
    "premium":  ["run", "decision", "simulate", "chat_state", "report_read",
                 "report_create", "analyze_image", "dashboard"],
    "admin":    ["*"],   # all
    "readonly": ["report_read", "dashboard", "health"],
}

# Key expiry (seconds). 0 = never
_EXPIRY_BY_SCOPE: Dict[str, int] = {
    "user":     0,           # ไม่หมดอายุ — ผูกกับ account
    "premium":  0,
    "admin":    86400 * 90,  # 90 วัน
    "readonly": 86400 * 30,  # 30 วัน
}

_lock = threading.Lock()

# =============================================================================
# DATABASE INIT
# =============================================================================

def _get_conn() -> sqlite3.Connection:
    """Get SQLite connection — reuses KD main DB."""
    os.makedirs(os.path.dirname(_DB_PATH) if os.path.dirname(_DB_PATH) else ".", exist_ok=True)
    conn = sqlite3.connect(_DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_api_key_tables() -> None:
    """Create API key tables if not exist. Safe to call multiple times."""
    conn = _get_conn()
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS api_keys (
                key_id       TEXT PRIMARY KEY,
                key_hash     TEXT NOT NULL UNIQUE,
                key_prefix   TEXT NOT NULL,
                user_email   TEXT NOT NULL,
                scope        TEXT NOT NULL DEFAULT 'user',
                label        TEXT NOT NULL DEFAULT '',
                is_active    INTEGER NOT NULL DEFAULT 1,
                created_at   REAL NOT NULL,
                expires_at   REAL NOT NULL DEFAULT 0,
                last_used_at REAL NOT NULL DEFAULT 0,
                total_calls  INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (user_email) REFERENCES users(email)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_api_keys_hash
                ON api_keys(key_hash);
            CREATE INDEX IF NOT EXISTS idx_api_keys_email
                ON api_keys(user_email);

            CREATE TABLE IF NOT EXISTS api_key_usage (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                key_id       TEXT NOT NULL,
                user_email   TEXT NOT NULL,
                endpoint     TEXT NOT NULL DEFAULT '',
                route        TEXT NOT NULL DEFAULT 'general',
                status_code  INTEGER NOT NULL DEFAULT 200,
                latency_ms   INTEGER NOT NULL DEFAULT 0,
                ts           REAL NOT NULL,
                ip           TEXT NOT NULL DEFAULT '',
                FOREIGN KEY (key_id) REFERENCES api_keys(key_id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_key_usage_key_id
                ON api_key_usage(key_id);
            CREATE INDEX IF NOT EXISTS idx_key_usage_ts
                ON api_key_usage(ts);

            CREATE TABLE IF NOT EXISTS api_key_rate_buckets (
                key_id       TEXT NOT NULL,
                bucket_min   INTEGER NOT NULL,
                call_count   INTEGER NOT NULL DEFAULT 0,
                PRIMARY KEY (key_id, bucket_min),
                FOREIGN KEY (key_id) REFERENCES api_keys(key_id)
                    ON DELETE CASCADE
            );
        """)
        conn.commit()
    finally:
        conn.close()


# =============================================================================
# KEY GENERATION — deterministic, verifiable
# =============================================================================

def _generate_raw_key() -> str:
    """Generate a cryptographically random key string."""
    raw = uuid.uuid4().hex + uuid.uuid4().hex  # 64 hex chars
    return f"{_KEY_PREFIX}{raw}"


def _hash_key(raw_key: str) -> str:
    """One-way hash of raw key for DB storage (never store raw)."""
    return hmac.new(
        _SECRET_SALT.encode(),
        raw_key.encode(),
        hashlib.sha256,
    ).hexdigest()


def _sign_key_id(key_id: str, email: str) -> str:
    """HMAC signature binding key_id to email — tamper detection."""
    msg = f"{key_id}:{email}".encode()
    return hmac.new(_SECRET_SALT.encode(), msg, hashlib.sha256).hexdigest()[:16]


def _masked(raw_key: str) -> str:
    """Show only prefix + last 4 chars for display."""
    return raw_key[:8] + "..." + raw_key[-4:]

# =============================================================================
# ENSURE API KEY — สร้าง key อัตโนมัติเมื่อ user login
# มนุษย์ไม่ต้องทำอะไรเพิ่ม
# =============================================================================

def ensure_api_key(
    user_email: str,
    scope: str = "user",
    label: str = "auto",
) -> Dict[str, Any]:
    """
    ตรวจว่า user มี active key สำหรับ scope นี้หรือยัง
    ถ้ายัง → สร้างให้อัตโนมัติ
    ถ้ามีแล้ว → return existing (ไม่สร้างซ้ำ)

    เรียกตอน login / Google callback แทน create_api_key ตัวเก่า
    """
    if not user_email:
        raise ValueError("user_email is required")

    scope = scope if scope in _SCOPE_PERMISSIONS else "user"

    conn = _get_conn()
    try:
        # ตรวจ existing active key
        now = time.time()
        row = conn.execute("""
            SELECT key_id, key_prefix, scope, label, created_at, expires_at, total_calls
            FROM api_keys
            WHERE user_email = ? AND scope = ? AND is_active = 1
              AND (expires_at = 0 OR expires_at > ?)
            ORDER BY created_at DESC
            LIMIT 1
        """, (user_email, scope, now)).fetchone()

        if row:
            return {
                "status":      "existing",
                "key_id":      row["key_id"],
                "key_prefix":  row["key_prefix"],
                "scope":       row["scope"],
                "label":       row["label"],
                "created_at":  row["created_at"],
                "expires_at":  row["expires_at"],
                "total_calls": row["total_calls"],
                "masked_key":  row["key_prefix"] + "...",
            }

        # สร้าง key ใหม่
        raw_key  = _generate_raw_key()
        key_hash = _hash_key(raw_key)
        key_id   = f"kid_{uuid.uuid4().hex[:16]}"
        prefix   = raw_key[:12]  # แสดงให้ user เห็น prefix เท่านั้น
        expiry   = _EXPIRY_BY_SCOPE.get(scope, 0)
        expires_at = (now + expiry) if expiry else 0

        conn.execute("""
            INSERT INTO api_keys
                (key_id, key_hash, key_prefix, user_email, scope, label,
                 is_active, created_at, expires_at, last_used_at, total_calls)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, 0, 0)
        """, (key_id, key_hash, prefix, user_email, scope, label, now, expires_at))
        conn.commit()

        return {
            "status":     "created",
            "key_id":     key_id,
            "raw_key":    raw_key,   # แสดงครั้งเดียว ไม่เก็บใน DB
            "key_prefix": prefix,
            "scope":      scope,
            "label":      label,
            "created_at": now,
            "expires_at": expires_at,
            "masked_key": _masked(raw_key),
        }
    finally:
        conn.close()


# =============================================================================
# VALIDATE — ใช้ใน middleware และ endpoint
# =============================================================================

def validate_api_key(
    raw_key: str,
    required_permission: Optional[str] = None,
) -> Dict[str, Any]:
    """
    ตรวจสอบ API key:
    1. hash แล้วหา match ใน DB
    2. ตรวจ is_active, expires_at
    3. ตรวจ scope permission
    4. ตรวจ rate limit (per-minute bucket)
    5. update last_used_at, total_calls

    Return: {"valid": True, "email": ..., "scope": ..., "key_id": ...}
    หรือ   {"valid": False, "reason": ...}
    """
    if not raw_key or not raw_key.startswith(_KEY_PREFIX):
        return {"valid": False, "reason": "INVALID_FORMAT"}

    key_hash = _hash_key(raw_key)
    now      = time.time()

    conn = _get_conn()
    try:
        row = conn.execute("""
            SELECT key_id, user_email, scope, is_active, expires_at, total_calls
            FROM api_keys
            WHERE key_hash = ?
            LIMIT 1
        """, (key_hash,)).fetchone()

        if not row:
            return {"valid": False, "reason": "KEY_NOT_FOUND"}

        if not row["is_active"]:
            return {"valid": False, "reason": "KEY_REVOKED"}

        if row["expires_at"] and row["expires_at"] < now:
            return {"valid": False, "reason": "KEY_EXPIRED"}

        # Permission check
        if required_permission:
            perms = _SCOPE_PERMISSIONS.get(row["scope"], [])
            if "*" not in perms and required_permission not in perms:
                return {
                    "valid":  False,
                    "reason": f"SCOPE_INSUFFICIENT:{row['scope']}→{required_permission}",
                }

        # Rate limit check
        rate_ok, rate_info = _check_rate_limit(conn, row["key_id"], row["scope"], now)
        if not rate_ok:
            return {
                "valid":     False,
                "reason":    "RATE_LIMIT_EXCEEDED",
                "rate_info": rate_info,
            }

        # Update usage
        conn.execute("""
            UPDATE api_keys
            SET last_used_at = ?, total_calls = total_calls + 1
            WHERE key_id = ?
        """, (now, row["key_id"]))
        conn.commit()

        return {
            "valid":      True,
            "key_id":     row["key_id"],
            "email":      row["user_email"],
            "scope":      row["scope"],
            "rate_info":  rate_info,
            "permissions": _SCOPE_PERMISSIONS.get(row["scope"], []),
        }
    finally:
        conn.close()


# =============================================================================
# RATE LIMITER — sliding window per-minute bucket
# =============================================================================

def _check_rate_limit(
    conn: sqlite3.Connection,
    key_id: str,
    scope: str,
    now: float,
) -> Tuple[bool, Dict[str, Any]]:
    """
    ใช้ minute-bucket strategy:
    - bucket_min = int(now / 60)
    - นับ calls ใน bucket ปัจจุบัน
    - ถ้าเกิน max_calls → block

    Daily: นับ buckets ใน 24h ที่ผ่านมา
    """
    cfg = _RATE_LIMITS.get(scope, _RATE_LIMITS["user"])
    max_per_min = cfg["max_calls"]
    max_daily   = cfg["max_daily"]

    bucket_min  = int(now / 60)
    day_buckets = 60 * 24   # 1440 buckets = 24 hours

    # Per-minute count
    row = conn.execute("""
        SELECT call_count FROM api_key_rate_buckets
        WHERE key_id = ? AND bucket_min = ?
    """, (key_id, bucket_min)).fetchone()
    min_count = row["call_count"] if row else 0

    # Daily count (sum last 1440 minutes)
    day_start = bucket_min - day_buckets
    daily_row = conn.execute("""
        SELECT COALESCE(SUM(call_count), 0) as total
        FROM api_key_rate_buckets
        WHERE key_id = ? AND bucket_min > ?
    """, (key_id, day_start)).fetchone()
    day_count = daily_row["total"] if daily_row else 0

    rate_info = {
        "calls_this_minute": min_count,
        "calls_today":       day_count,
        "limit_per_minute":  max_per_min,
        "limit_per_day":     max_daily,
        "resets_in_sec":     60 - int(now % 60),
    }

    if min_count >= max_per_min:
        return False, rate_info
    if day_count >= max_daily:
        return False, rate_info

    # Increment bucket
    conn.execute("""
        INSERT INTO api_key_rate_buckets (key_id, bucket_min, call_count)
        VALUES (?, ?, 1)
        ON CONFLICT(key_id, bucket_min)
        DO UPDATE SET call_count = call_count + 1
    """, (key_id, bucket_min))

    # Cleanup old buckets (keep 2 days)
    conn.execute("""
        DELETE FROM api_key_rate_buckets
        WHERE key_id = ? AND bucket_min < ?
    """, (key_id, bucket_min - day_buckets * 2))

    return True, rate_info


# =============================================================================
# USAGE RECORDING — เรียกหลัง endpoint ทำงานเสร็จ
# =============================================================================

def record_key_usage(
    key_id:      str,
    user_email:  str,
    endpoint:    str = "",
    route:       str = "general",
    status_code: int = 200,
    latency_ms:  int = 0,
    ip:          str = "",
) -> None:
    """บันทึก audit log ทุก request — FATE™ transparency."""
    try:
        conn = _get_conn()
        try:
            conn.execute("""
                INSERT INTO api_key_usage
                    (key_id, user_email, endpoint, route, status_code, latency_ms, ts, ip)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (key_id, user_email, endpoint, route, status_code, latency_ms, time.time(), ip))
            conn.commit()
        finally:
            conn.close()
    except Exception:
        pass   # audit fail ต้องไม่กระทบ main flow


# =============================================================================
# KEY MANAGEMENT
# =============================================================================

def get_key_info(key_id: str, user_email: str) -> Optional[Dict[str, Any]]:
    """ดูข้อมูล key — ต้องเป็นเจ้าของเท่านั้น."""
    conn = _get_conn()
    try:
        row = conn.execute("""
            SELECT key_id, key_prefix, user_email, scope, label,
                   is_active, created_at, expires_at, last_used_at, total_calls
            FROM api_keys
            WHERE key_id = ? AND user_email = ?
        """, (key_id, user_email)).fetchone()
        if not row:
            return None
        return dict(row)
    finally:
        conn.close()


def list_user_keys(user_email: str) -> List[Dict[str, Any]]:
    """List ทุก key ของ user (ไม่แสดง raw key — แสดงแค่ prefix)."""
    conn = _get_conn()
    try:
        rows = conn.execute("""
            SELECT key_id, key_prefix, scope, label,
                   is_active, created_at, expires_at, last_used_at, total_calls
            FROM api_keys
            WHERE user_email = ?
            ORDER BY created_at DESC
        """, (user_email,)).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def rotate_api_key(key_id: str, user_email: str) -> Dict[str, Any]:
    """
    Rotate key:
    1. revoke key เก่า
    2. สร้าง key ใหม่ scope เดิม
    User ไม่ต้องทำอะไร — frontend เรียก endpoint นี้แล้ว auto-update header
    """
    conn = _get_conn()
    try:
        row = conn.execute("""
            SELECT scope, label FROM api_keys
            WHERE key_id = ? AND user_email = ? AND is_active = 1
        """, (key_id, user_email)).fetchone()

        if not row:
            return {"status": "error", "reason": "KEY_NOT_FOUND_OR_NOT_OWNER"}

        # Revoke old
        conn.execute("""
            UPDATE api_keys SET is_active = 0
            WHERE key_id = ? AND user_email = ?
        """, (key_id, user_email))
        conn.commit()
    finally:
        conn.close()

    # Create new with same scope
    result = ensure_api_key(user_email, scope=row["scope"], label=row["label"] + "_rotated")
    result["rotated_from"] = key_id
    return result


def revoke_api_key(key_id: str, user_email: str) -> Dict[str, Any]:
    """Revoke key — soft delete (is_active=0)."""
    conn = _get_conn()
    try:
        cur = conn.execute("""
            UPDATE api_keys SET is_active = 0
            WHERE key_id = ? AND user_email = ?
        """, (key_id, user_email))
        conn.commit()
        if cur.rowcount == 0:
            return {"status": "error", "reason": "NOT_FOUND_OR_NOT_OWNER"}
        return {"status": "revoked", "key_id": key_id}
    finally:
        conn.close()


# =============================================================================
# USAGE STATS — สำหรับ GOV dashboard
# =============================================================================

def get_usage_stats(user_email: str, hours: int = 24) -> Dict[str, Any]:
    """
    คืน usage summary สำหรับ user — แสดงใน governance panel
    FATE™ principle: ทุกการใช้งานต้องอธิบายได้
    """
    conn = _get_conn()
    try:
        since = time.time() - (hours * 3600)

        # Per-endpoint breakdown
        rows = conn.execute("""
            SELECT endpoint, COUNT(*) as calls,
                   AVG(latency_ms) as avg_latency,
                   SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as errors
            FROM api_key_usage
            WHERE user_email = ? AND ts > ?
            GROUP BY endpoint
            ORDER BY calls DESC
            LIMIT 20
        """, (user_email, since)).fetchall()

        # Total calls
        total = conn.execute("""
            SELECT COUNT(*) as n FROM api_key_usage
            WHERE user_email = ? AND ts > ?
        """, (user_email, since)).fetchone()

        # Key count
        keys = conn.execute("""
            SELECT COUNT(*) as n FROM api_keys
            WHERE user_email = ? AND is_active = 1
        """, (user_email,)).fetchone()

        # Route distribution
        routes = conn.execute("""
            SELECT route, COUNT(*) as n FROM api_key_usage
            WHERE user_email = ? AND ts > ?
            GROUP BY route ORDER BY n DESC
        """, (user_email, since)).fetchall()

        return {
            "user_email":    user_email,
            "period_hours":  hours,
            "total_calls":   total["n"] if total else 0,
            "active_keys":   keys["n"] if keys else 0,
            "by_endpoint":   [dict(r) for r in rows],
            "by_route":      [dict(r) for r in routes],
            "fate_audit":    "Choice(t) ≥ 1 → collapse = False",
            "generated_at":  time.time(),
        }
    finally:
        conn.close()


def get_system_stats() -> Dict[str, Any]:
    """Admin-only: system-wide stats."""
    conn = _get_conn()
    try:
        since_1h  = time.time() - 3600
        since_24h = time.time() - 86400

        calls_1h  = conn.execute("SELECT COUNT(*) as n FROM api_key_usage WHERE ts > ?", (since_1h,)).fetchone()
        calls_24h = conn.execute("SELECT COUNT(*) as n FROM api_key_usage WHERE ts > ?", (since_24h,)).fetchone()
        total_keys = conn.execute("SELECT COUNT(*) as n FROM api_keys WHERE is_active = 1").fetchone()
        users      = conn.execute("SELECT COUNT(DISTINCT user_email) as n FROM api_keys WHERE is_active = 1").fetchone()

        return {
            "calls_last_1h":   calls_1h["n"]  if calls_1h  else 0,
            "calls_last_24h":  calls_24h["n"] if calls_24h else 0,
            "active_keys":     total_keys["n"] if total_keys else 0,
            "active_users":    users["n"]      if users      else 0,
            "generated_at":    time.time(),
        }
    finally:
        conn.close()


# =============================================================================
# FASTAPI MIDDLEWARE + DECORATOR
# =============================================================================

def _extract_raw_key(request: Request) -> Optional[str]:
    """
    หา API key จาก request — priority order:
    1. Authorization: Bearer kd_xxx
    2. X-API-Key: kd_xxx
    3. Cookie: kd_api_key (auto-set หลัง login)
    4. Query param: api_key=kd_xxx (deprecated แต่ยังรองรับ)
    """
    # 1. Bearer token
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer ") and auth[7:].startswith(_KEY_PREFIX):
        return auth[7:]

    # 2. X-API-Key header
    xkey = request.headers.get("X-API-Key", "")
    if xkey.startswith(_KEY_PREFIX):
        return xkey

    # 3. Cookie
    cookie = request.cookies.get("kd_api_key", "")
    if cookie.startswith(_KEY_PREFIX):
        return cookie

    # 4. Query param (fallback)
    qkey = request.query_params.get("api_key", "")
    if qkey.startswith(_KEY_PREFIX):
        return qkey

    return None


class APIKeyMiddleware:
    """
    Starlette middleware — ตรวจ API key ทุก /api/* request
    ถ้าไม่มี key → fall through (ใช้ cookie session แทน)
    ถ้ามี key แต่ invalid → 401

    ใส่ใน app.py:
        from core.api_keys import APIKeyMiddleware
        app.add_middleware(APIKeyMiddleware)
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http":
            from starlette.requests import Request as StarRequest
            request = StarRequest(scope, receive)
            path    = request.url.path

            # ตรวจเฉพาะ /api/* endpoint
            if path.startswith("/api/") or path in ("/run", "/decision", "/simulate"):
                raw_key = _extract_raw_key(request)
                if raw_key:
                    result = validate_api_key(raw_key)
                    if not result["valid"]:
                        from starlette.responses import JSONResponse as SR
                        response = SR(
                            {
                                "error":  "API_KEY_INVALID",
                                "reason": result.get("reason", "UNKNOWN"),
                                "fate":   "ถ้าอธิบายไม่ได้ = ใช้ไม่ได้",
                            },
                            status_code=401,
                        )
                        await response(scope, receive, send)
                        return
                    # attach validated info to scope state
                    scope.setdefault("state", {})
                    scope["state"]["api_key_info"] = result

        await self.app(scope, receive, send)


def require_api_key(permission: Optional[str] = None):
    """
    FastAPI endpoint decorator:

        @app.post("/api/admin/stats")
        @require_api_key("admin")
        async def admin_stats(request: Request):
            ...

    ถ้า user login ด้วย cookie ปกติ → ผ่าน (backward compatible)
    ถ้า user ส่ง API key → validate permission
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            raw_key = _extract_raw_key(request)

            if raw_key:
                result = validate_api_key(raw_key, required_permission=permission)
                if not result["valid"]:
                    raise HTTPException(
                        status_code=401,
                        detail={
                            "error":  "API_KEY_INVALID",
                            "reason": result.get("reason"),
                            "fate":   "Fail less. Harm less. Restore more.",
                        },
                    )
                # inject into request state
                request.state.api_key_info = result
                request.state.api_user_email = result["email"]
            else:
                # fallback: cookie-based auth (ระบบเดิม)
                email = request.cookies.get("kd_email", "")
                if not email and permission:
                    raise HTTPException(status_code=401, detail="Authentication required")
                request.state.api_key_info  = None
                request.state.api_user_email = email

            return await func(request, *args, **kwargs)
        return wrapper
    return decorator


# =============================================================================
# CONVENIENCE: auto-issue key on login (เรียกจาก google_callback + login)
# =============================================================================

def on_user_login(email: str) -> Dict[str, Any]:
    """
    เรียกตอน user login (Google OAuth หรือ email login)
    สร้าง key อัตโนมัติถ้ายังไม่มี และ return key prefix สำหรับ set cookie

    ใน app.py google_callback:
        from core.api_keys import on_user_login
        key_result = on_user_login(email)
        response.set_cookie("kd_api_key", key_result["raw_key"], ...)
    """
    try:
        result = ensure_api_key(email, scope="user", label="auto_login")
        return result
    except Exception as e:
        # ไม่ให้ login fail เพราะ key system
        return {"status": "error", "reason": str(e), "raw_key": None}


# =============================================================================
# FATE™ AUDIT REPORT
# =============================================================================

def fate_audit_key(key_id: str, user_email: str) -> Dict[str, Any]:
    """
    FATE™ transparency report สำหรับ key นึง
    "ถ้าอธิบายไม่ได้ = ใช้ไม่ได้ ถ้า override โดยไร้ร่องรอย = ผิดกฎ"
    """
    conn = _get_conn()
    try:
        key_row = conn.execute("""
            SELECT key_id, key_prefix, scope, label, is_active,
                   created_at, expires_at, last_used_at, total_calls
            FROM api_keys
            WHERE key_id = ? AND user_email = ?
        """, (key_id, user_email)).fetchone()

        if not key_row:
            return {"error": "KEY_NOT_FOUND"}

        # Last 10 usage
        usage = conn.execute("""
            SELECT endpoint, route, status_code, latency_ms, ts, ip
            FROM api_key_usage
            WHERE key_id = ?
            ORDER BY ts DESC LIMIT 10
        """, (key_id,)).fetchall()

        # Rate bucket current minute
        now_bucket = int(time.time() / 60)
        rate_row = conn.execute("""
            SELECT call_count FROM api_key_rate_buckets
            WHERE key_id = ? AND bucket_min = ?
        """, (key_id, now_bucket)).fetchone()

        scope = key_row["scope"]
        cfg   = _RATE_LIMITS.get(scope, _RATE_LIMITS["user"])

        return {
            "fate_audit":    True,
            "axiom":         "Choice(t) ≥ 1 → collapse = False",
            "key_id":        key_row["key_id"],
            "key_prefix":    key_row["key_prefix"],
            "scope":         key_row["scope"],
            "label":         key_row["label"],
            "is_active":     bool(key_row["is_active"]),
            "created_at":    key_row["created_at"],
            "expires_at":    key_row["expires_at"],
            "last_used_at":  key_row["last_used_at"],
            "total_calls":   key_row["total_calls"],
            "permissions":   _SCOPE_PERMISSIONS.get(scope, []),
            "rate_limits":   cfg,
            "calls_this_min": rate_row["call_count"] if rate_row else 0,
            "recent_usage":  [dict(u) for u in usage],
            "generated_at":  time.time(),
        }
    finally:
        conn.close()


# =============================================================================
# MODULE INIT
# =============================================================================

try:
    init_api_key_tables()
    print("✅ API key tables initialized")
except Exception as _e:
    print(f"⚠ api_keys init: {_e}")
