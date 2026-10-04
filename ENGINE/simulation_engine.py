# ENGINE/simulation_engine.py
# KING DIADEM — Simulation Engine
# Deterministic future-path simulator — FATE™ compatible
# Uses same LLM singleton as rest of system

from __future__ import annotations
import json


def simulate(data: dict) -> dict:
    """
    Input:  {"input": str, "paths": list[str]}
    Output: {"simulation": str, "paths": list, "lyla_observation": dict}
    """
    data = data if isinstance(data, dict) else {"input": str(data or "")}
    user_input: str = str(data.get("input") or "").strip()
    paths: list     = [str(p) for p in (data.get("paths") or []) if p is not None]

    if not user_input:
        return {
            "simulation": "ไม่มีสถานการณ์ให้จำลอง — กรุณาพิมพ์ก่อนนะคะ",
            "paths": paths,
            "lyla_observation": {}
        }

    # ── LLM ───────────────────────────────────────────────────────
    try:
        from core.llm_gemini import get_llm
        llm = get_llm()
    except Exception as e:
        print(f"⚠ simulate: LLM not ready: {e}")
        return {
            "simulation": "ระบบจำลองไม่พร้อมชั่วคราว — ลองใหม่อีกครั้งนะคะ",
            "paths": paths,
            "lyla_observation": {}
        }

    # ── Build prompt ──────────────────────────────────────────────
    paths_text = ""
    if paths:
        listed = "\n".join(f"  - {p}" for p in paths if p.strip())
        paths_text = f"\n\nเส้นทางที่ต้องการจำลอง:\n{listed}"

    prompt = (
        f"จำลองอนาคตสถานการณ์นี้ตามกรอบ KING DIADEM FATE™:\n\n"
        f"สถานการณ์: {user_input}"
        f"{paths_text}\n\n"
        f"วิเคราะห์:\n"
        f"1. ผลลัพธ์ที่เป็นไปได้มากที่สุด (60%+)\n"
        f"2. ความเสี่ยงหลักที่ต้องระวัง\n"
        f"3. ทางเลือกที่ยังเปิดอยู่ (Choice ≥ 1)\n"
        f"4. สัญญาณ Waterline / Drift ที่ควรติดตาม\n"
        f"5. คำแนะนำ LYLA: action ที่ Fail Less ที่สุด\n\n"
        f"ตอบเป็นภาษาไทย กระชับ ตรงประเด็น ไม่เกิน 300 คำ\n— LYLA ◈"
    )

    # ── Call LLM ──────────────────────────────────────────────────
    try:
        reply = llm.generate_with_governance(
            prompt=prompt,
            additional_context="mode=simulation,system=FATE_DETERMINISTIC",
            route="survival",
        )
        if not reply:
            raise ValueError("empty response")
    except Exception as e:
        # เดิม fallback ไปเรียก Gemini ตรงแบบไม่ผ่าน governance/เพดานเวลา และส่งข้อความ error ภายในให้ผู้ใช้
        # generate_with_governance มีการสลับโมเดลสำรองให้แล้ว — ล้มตรงนี้ให้ตอบอย่างสุภาพ
        print(f"⚠ simulate: LLM error: {e}")
        return {
            "simulation": "จำลองไม่สำเร็จชั่วคราว — ลองใหม่อีกครั้งนะคะ",
            "paths": paths,
            "lyla_observation": {}
        }

    # ── Lyla observation (lightweight pattern) ────────────────────
    obs: dict = {}
    lower = user_input.lower()
    if any(w in lower for w in ["เงิน", "หนี้", "ขาดทุน", "ล้ม"]):
        obs = {"domain": "financial", "waterline": "monitor", "drift_risk": "medium"}
    elif any(w in lower for w in ["ป่วย", "สุขภาพ", "อาการ"]):
        obs = {"domain": "health", "waterline": "caution", "drift_risk": "low"}
    elif any(w in lower for w in ["งาน", "ลาออก", "เลิกจ้าง", "บริษัท"]):
        obs = {"domain": "career", "waterline": "stable", "drift_risk": "medium"}
    elif any(w in lower for w in ["วิกฤต", "ฉุกเฉิน", "urgent", "ด่วน"]):
        obs = {"domain": "crisis", "waterline": "critical", "drift_risk": "high"}
    else:
        obs = {"domain": "general", "waterline": "stable", "drift_risk": "low"}

    return {
        "simulation": reply,
        "paths": paths,
        "lyla_observation": obs,
    }
