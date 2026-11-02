"""
core/human_gate.py — ประตูมนุษย์ (Human Gate)
FATE™ Axiom: Human Final Authority

กฎข้อเดียว:
    action ที่มีผลออกไปนอกระบบ (เขียนไฟล์ ส่งข้อความ เปิดลิงก์) ต้องมี "ใบอนุญาต"
    ที่มนุษย์ออกให้ผ่านช่องทางที่ AI อ่านหรือเขียนไม่ได้ (เช่น หลังยืนยัน TOTP)

ทำไมต้องมี:
    งานวิจัย Cornell Tech / Yale (พ.ย. 2026) พบว่า agent 9 ใน 10 ตัวไปหยิบรหัสอนุมัติ
    จากอีเมลมาเพิ่มวงเงินตัวเอง — เพราะรหัสอยู่ใน channel ที่ agent อ่านได้
    ที่นี่ใบอนุญาตลงลายเซ็นด้วย secret ฝั่งเซิร์ฟเวอร์ ซึ่งไม่เคยอยู่ใน prompt หรือ output ของ LLM

คุณสมบัติของใบอนุญาต (ทุกข้อตรวจแบบ deterministic):
    1. ผูกกับ action + พารามิเตอร์ชุดเดียว  — เอาใบของ "write_note A" ไปใช้กับ "write_note B" ไม่ได้
    2. มีวันหมดอายุ (ค่าเริ่มต้น 120 วินาที)
    3. ใช้ได้ครั้งเดียว
    4. ไม่มี secret = ปิดประตู (fail closed) ไม่ใช่เปิดโล่ง

ข้อห้าม:
    - ห้ามเรียก mint() จากทางที่รับข้อความจาก LLM — เรียกได้เฉพาะหลังมนุษย์ยืนยันตัวแล้วเท่านั้น
    - ห้ามส่งใบอนุญาตกลับเข้า prompt หรือ history ของ LLM
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import threading
import time

# action ที่มีผลออกนอกระบบ — ต้องผ่านประตูเสมอ
GATED_ACTIONS = frozenset({"open_url", "write_note", "send_alert"})

DEFAULT_TTL_S = 120
_MAX_TTL_S = 600

_used: dict = {}                 # nonce → เวลาหมดอายุ (กันใช้ซ้ำ)
_used_lock = threading.Lock()


def _secret() -> bytes:
    s = os.getenv("HUMAN_GATE_SECRET") or os.getenv("SECRET_KEY") or ""
    return s.encode("utf-8")


def _params_digest(action: str, params: dict) -> str:
    body = json.dumps({"action": action, "params": params or {}},
                      sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def _sign(payload: bytes, key: bytes) -> str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()


def mint(action: str, params: dict, ttl_s: int = DEFAULT_TTL_S, approver: str = "") -> str:
    """ออกใบอนุญาต — เรียกได้เฉพาะหลังมนุษย์ยืนยันตัวแล้ว (TOTP / session ที่ผ่าน 2FA)"""
    key = _secret()
    if not key:
        raise RuntimeError("ไม่มี HUMAN_GATE_SECRET / SECRET_KEY — ออกใบอนุญาตไม่ได้")
    ttl = max(1, min(int(ttl_s), _MAX_TTL_S))
    claim = {
        "d": _params_digest(action, params),
        "exp": int(time.time()) + ttl,
        "n": secrets.token_hex(12),
        "by": str(approver)[:80],
    }
    payload = json.dumps(claim, sort_keys=True).encode("utf-8")
    return (base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")
            + "." + _sign(payload, key))


def verify(token, action: str, params: dict) -> tuple:
    """ตรวจใบอนุญาต → (True, ผู้อนุมัติ) หรือ (False, เหตุผล) — ผ่านแล้วใบนั้นใช้ซ้ำไม่ได้"""
    key = _secret()
    if not key:
        return False, "gate_closed_no_secret"
    if not isinstance(token, str) or "." not in token or len(token) > 2000:
        return False, "missing_or_malformed"
    b64, sig = token.rsplit(".", 1)
    try:
        payload = base64.urlsafe_b64decode(b64 + "=" * (-len(b64) % 4))
        claim = json.loads(payload)
    except Exception:
        return False, "missing_or_malformed"
    if not hmac.compare_digest(sig, _sign(payload, key)):
        return False, "bad_signature"
    if not isinstance(claim, dict):
        return False, "missing_or_malformed"
    now = time.time()
    if int(claim.get("exp", 0)) < now:
        return False, "expired"
    if claim.get("d") != _params_digest(action, params):
        return False, "action_mismatch"
    nonce = str(claim.get("n", ""))
    with _used_lock:
        for k in [k for k, exp in _used.items() if exp < now]:
            del _used[k]
        if not nonce or nonce in _used:
            return False, "already_used"
        _used[nonce] = float(claim["exp"])
    return True, str(claim.get("by", ""))


def requires_gate(action: str) -> bool:
    return str(action or "").strip() in GATED_ACTIONS
