"""
core/history_export.py — KING DIADEM
ส่งออกประวัติการปรึกษาของบัญชีให้เจ้าของ: ไฟล์ข้อความ (ดาวน์โหลด) และส่งเข้าอีเมลของบัญชีนั้น

ประวัติเก็บไว้ในบัญชี (DATABASE.db.decision_log ต่ออีเมล) — ส่งออกได้เฉพาะของตัวเอง และส่งได้เฉพาะอีเมลของบัญชีนั้น
(ไม่รับอีเมลปลายทางจากผู้ใช้ — กันไม่ให้ใช้ระบบเป็นช่องส่งเมลหาคนอื่น)

การส่งอีเมลใช้ SMTP ของเจ้าของระบบ (ตั้งค่าบน Render) — ไม่ได้ตั้ง = ปิด ใช้ดาวน์โหลดแทนได้เสมอ
  SMTP_HOST   เช่น smtp.gmail.com
  SMTP_PORT   587 (STARTTLS) หรือ 465 (SSL) — ค่าเริ่ม 587
  SMTP_USER / SMTP_PASS   (Gmail ใช้ App Password)
  MAIL_FROM   ผู้ส่งที่แสดง — ค่าเริ่ม = SMTP_USER
"""

from __future__ import annotations

import os
import smtplib
import ssl
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage

_ROUTE_TH = {"general": "ทั่วไป", "risk": "ความเสี่ยง", "survival": "รอดชีวิต", "collapse": "วิกฤต",
             "civil": "สังคม", "vega": "VEGA", "stable": "ทั่วไป", "crisis": "วิกฤต", "business": "ธุรกิจ"}
_TH = timezone(timedelta(hours=7))


def _when(v) -> str:
    """created_at ของ SQLite เป็น UTC ('YYYY-MM-DD HH:MM:SS') → เวลาไทย"""
    try:
        t = datetime.strptime(str(v)[:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        return t.astimezone(_TH).strftime("%d/%m/%Y %H:%M")
    except (TypeError, ValueError):
        return str(v or "")


def format_history(rows: list, email: str) -> str:
    now = datetime.now(_TH).strftime("%d/%m/%Y %H:%M")
    head = [
        "KING DIADEM — ประวัติการปรึกษา",
        f"บัญชี: {email}",
        f"ส่งออกเมื่อ: {now} (เวลาไทย) · ทั้งหมด {len(rows)} ครั้ง",
        "ไฟล์นี้เป็นของคุณ — ระบบส่งให้เฉพาะเจ้าของบัญชี · การเลือกสุดท้ายเป็นของคุณเสมอ",
        "=" * 48,
    ]
    body = []
    for i, r in enumerate(rows, 1):
        route = _ROUTE_TH.get(str(r.get("route") or ""), str(r.get("route") or "—"))
        persona = str(r.get("persona") or "").strip()
        body += [
            "",
            f"#{i} · {_when(r.get('created_at'))} · เส้นทาง {route}" + (f" · {persona}" if persona else ""),
            "คุณ:",
            str(r.get("input") or "").strip(),
            "",
            "คำตอบ:",
            str(r.get("response") or "").strip(),
            "-" * 48,
        ]
    if not rows:
        body = ["", "ยังไม่มีประวัติในบัญชีนี้"]
    return "\n".join(head + body) + "\n"


def filename() -> str:
    return "king-diadem-history-" + datetime.now(_TH).strftime("%Y%m%d-%H%M") + ".txt"


def email_configured() -> bool:
    return bool(os.getenv("SMTP_HOST") and os.getenv("SMTP_USER") and os.getenv("SMTP_PASS"))


def send_history_email(to_email: str, text: str, timeout: float = 20.0) -> None:
    """ส่งประวัติเป็นไฟล์แนบเข้าอีเมลของบัญชี — ล้มเมื่อไหร่ให้ exception ขึ้นไป (endpoint แปลงเป็นข้อความสุภาพ)"""
    if not email_configured():
        raise RuntimeError("smtp not configured")
    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT") or 587)
    user, pw = os.getenv("SMTP_USER", ""), os.getenv("SMTP_PASS", "")
    sender = os.getenv("MAIL_FROM") or user

    msg = EmailMessage()
    msg["Subject"] = "ประวัติการปรึกษา KING DIADEM ของคุณ"
    msg["From"] = sender
    msg["To"] = to_email
    msg.set_content(
        "สวัสดีค่ะ\n\n"
        "นี่คือประวัติการปรึกษาในบัญชี KING DIADEM ของคุณ ตามที่ขอส่งออกไว้ (ไฟล์แนบ)\n"
        "ถ้าคุณไม่ได้เป็นคนกดขอ ไม่ต้องทำอะไร — ระบบส่งได้เฉพาะอีเมลของเจ้าของบัญชีเท่านั้น\n\n"
        "— LYLA ◈ KING DIADEM\n"
    )
    msg.add_attachment(text.encode("utf-8"), maintype="text", subtype="plain", filename=filename())

    ctx = ssl.create_default_context()
    if port == 465:
        with smtplib.SMTP_SSL(host, port, timeout=timeout, context=ctx) as s:
            s.login(user, pw)
            s.send_message(msg)
    else:
        with smtplib.SMTP(host, port, timeout=timeout) as s:
            s.starttls(context=ctx)
            s.login(user, pw)
            s.send_message(msg)
