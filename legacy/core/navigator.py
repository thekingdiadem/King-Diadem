"""
core/navigator.py — KING DIADEM
Truth Engine: ใช้ Gemini + FATE™ logic
ไม่ใช้ GPT (removed) — ใช้ singleton LLM
"""
import asyncio


TRUTH_PROMPT = """[KING DIADEM — TRUTH ENGINE]
กฎ:
- บรรยายความจริงตามสภาพที่เกิดขึ้น
- รักษา Choice(t) ≥ 1 เสมอ
- ไม่สั่ง ไม่ชี้นำ ไม่ตัดสิน
- อธิบายได้ภายใน 2 นาที

FORMAT:
- การปรากฏของความจริง: [สรุปสถานการณ์]
- ทางเลือกที่มีอยู่: [อย่างน้อย 2 ทาง]
- สรุป: [3 บรรทัด ชัดเจน ใช้งานได้ทันที]
"""


async def run_truth_engine(user_input: str, resource=50) -> dict:
    """
    Truth engine — Gemini only (GPT removed)
    คืน view + risk_index
    """
    # ── resource → risk ──────────────────────────────────────────
    try:
        resource_value = float(resource)
    except Exception:
        resource_value = 50.0
    risk_index = round(max(0, min(100, (100 - resource_value) * 0.75)), 2)

    # ── FATE™ validation ก่อน LLM ──────────────────────────────────
    # เดิมเรียก LLM ก่อนแล้วค่อยตรวจ: ข้อความวิกฤตได้คำตอบ "ทางเลือก" จาก LLM แทนสายด่วน
    fate_check = None
    try:
        from core.fate_core import run_fate
        fate_check = run_fate({"message": user_input})
    except Exception:
        fate_check = {"error": "FATE_UNAVAILABLE"}

    if isinstance(fate_check, dict) and fate_check.get("status") == "block":
        gemini_view = fate_check.get("safe_response", "")
    else:
        # ── Gemini via singleton ──────────────────────────────────
        # generate() เป็น sync + มี time.sleep ตอน retry → เรียกใน thread ไม่บล็อก event loop
        def _gen() -> str:
            from core.llm_gemini import get_llm
            return get_llm().generate(
                prompt=f"{TRUTH_PROMPT}\n\nสถานการณ์:\n{user_input}",
                temperature=0.65,
            )
        try:
            gemini_view = await asyncio.to_thread(_gen) or ""
        except Exception:
            gemini_view = ""           # ไม่ส่งข้อความ error ภายใน (key/โควตา) ออกไปหา client

    return {
        "view_structural":  "[GPT REMOVED — ใช้ VEGA แทน]",
        "view_possibility": gemini_view,
        "view_stability":   "FATE™ Deterministic Logic active",
        "risk_index":       risk_index,
        "fate_check":       fate_check,
        "resource":         resource_value,
    }
