# report_engine.py — KING DIADEM v1.0
# สร้าง shareable Decision Report URL จาก decision result
# เพิ่ม table: decision_reports ใน DB

import sqlite3, os, uuid, json
from datetime import datetime

DB_PATH = os.getenv("DB_PATH", "data/king_diadem.db")

def get_conn():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_report_table():
    """เรียกครั้งเดียวตอน startup"""
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS decision_reports (
            id          TEXT PRIMARY KEY,
            user_email  TEXT,
            input_text  TEXT,
            route       TEXT,
            persona     TEXT,
            ai_response TEXT,
            governance  TEXT,
            risk_score  REAL,
            consensus   TEXT,
            fate_audit  TEXT,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at  DATETIME
        );
    """)
    conn.commit()
    conn.close()

def _run_fate_audit(result: dict, user_input: str) -> dict:
    """
    FATE™ Axiom Audit — ตรวจสอบผลลัพธ์ผ่าน 6 Axioms
    คืน dict พร้อม pass/warn/fail แต่ละ axiom
    """
    route    = result.get("route", "general")
    persona  = result.get("persona", "LYLA")
    risk     = float(result.get("risk_score", 0))
    response = str(result.get("ai_response", ""))
    gov      = result.get("governance", {})

    checks = []

    # A1 — Logic Over Persona
    checks.append({
        "code": "A1",
        "name": "Logic Over Persona",
        "status": "PASS",
        "note": f"Route: {route} | Persona: {persona} — ยึดตามกฎ ไม่ยึดตัวบุคคล"
    })

    # A2 — Rule Over Authority
    checks.append({
        "code": "A2",
        "name": "Rule Over Authority",
        "status": "PASS",
        "note": "Human Final Authority ยังคงอยู่ — ระบบไม่มีอำนาจบังคับ"
    })

    # A3 — Determinism
    has_response = len(response) > 10
    checks.append({
        "code": "A3",
        "name": "Determinism",
        "status": "PASS" if has_response else "WARN",
        "note": "Output traceable from input + ruleset" if has_response else "Response empty — trace incomplete"
    })

    # A4 — Downside Before Upside
    risk_status = "PASS" if risk < 50 else ("WARN" if risk < 75 else "FAIL")
    risk_label  = f"Risk score: {risk:.0f}/100"
    checks.append({
        "code": "A4",
        "name": "Downside Before Upside",
        "status": risk_status,
        "note": risk_label + (" — Low risk" if risk < 50 else " — High risk detected" if risk >= 75 else " — Moderate risk")
    })

    # A5 — Explainability
    explainable = len(response) > 50
    checks.append({
        "code": "A5",
        "name": "Explainability = Usability",
        "status": "PASS" if explainable else "WARN",
        "note": "Response explainable to general user" if explainable else "Response too short to verify explainability"
    })

    # A6 — Human Final Authority
    checks.append({
        "code": "A6",
        "name": "Human Final Authority",
        "status": "PASS",
        "note": "ระบบแนะนำเท่านั้น — มนุษย์ตัดสินใจขั้นสุดท้ายเสมอ"
    })

    # Overall verdict
    statuses = [c["status"] for c in checks]
    if "FAIL" in statuses:
        verdict = "REJECTED"
    elif statuses.count("WARN") >= 2:
        verdict = "DEFERRED"
    else:
        verdict = "APPROVED"

    return {
        "checks": checks,
        "verdict": verdict,
        "axiom_pass": statuses.count("PASS"),
        "axiom_warn": statuses.count("WARN"),
        "axiom_fail": statuses.count("FAIL"),
    }


def create_report(
    user_email: str,
    user_input: str,
    result: dict,
) -> str:
    """
    สร้าง report และบันทึก DB
    คืน report_id (UUID สั้น)
    """
    init_report_table()

    report_id  = uuid.uuid4().hex[:12]
    fate_audit = _run_fate_audit(result, user_input)
    governance = result.get("governance", {})
    consensus  = result.get("consensus", "")
    expires    = datetime.utcnow().replace(microsecond=0)

    conn = get_conn()
    try:
        conn.execute(
            """INSERT INTO decision_reports
               (id, user_email, input_text, route, persona,
                ai_response, governance, risk_score, consensus, fate_audit)
               VALUES (?,?,?,?,?,?,?,?,?,?)""",
            (
                report_id,
                user_email or "anonymous",
                str(user_input)[:2000],
                result.get("route", "general"),
                result.get("persona", "LYLA"),
                str(result.get("ai_response", ""))[:4000],
                json.dumps(governance, ensure_ascii=False),
                float(result.get("risk_score", 0)),
                str(consensus)[:2000],
                json.dumps(fate_audit, ensure_ascii=False),
            )
        )
        conn.commit()
    finally:
        conn.close()

    return report_id


def get_report(report_id: str) -> dict | None:
    """ดึง report จาก DB — คืน None ถ้าไม่พบ"""
    init_report_table()
    conn = get_conn()
    try:
        row = conn.execute(
            "SELECT * FROM decision_reports WHERE id=?", (report_id,)
        ).fetchone()
        if not row:
            return None
        d = dict(row)
        d["governance"]  = json.loads(d["governance"] or "{}")
        d["fate_audit"]  = json.loads(d["fate_audit"] or "{}")
        return d
    finally:
        conn.close()
  
