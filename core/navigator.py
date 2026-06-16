"""
core/navigator.py — KING DIADEM
Truth Engine: ใช้ Gemini + FATE™ logic
ไม่ใช้ GPT (removed) — ใช้ singleton LLM
"""
import os
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

    # ── Gemini via singleton ──────────────────────────────────────
    async def get_gemini_view() -> str:
        try:
            from core.llm_gemini import get_llm
            llm = get_llm()
            result = llm.generate(
                prompt=f"{TRUTH_PROMPT}\n\nสถานการณ์:\n{user_input}",
                temperature=0.65,
            )
            return result or "[GEMINI: empty response]"
        except Exception as e:
            return f"[GEMINI ERROR] {e}"

    gemini_view = await get_gemini_view()

    # ── FATE™ validation ─────────────────────────────────────────
    fate_check = None
    try:
        from core.fate_core import run_fate
        fate_check = run_fate({"message": user_input})
    except Exception as e:
        fate_check = {"error": str(e)}

    return {
        "view_structural":  "[GPT REMOVED — ใช้ VEGA แทน]",
        "view_possibility": gemini_view,
        "view_stability":   "FATE™ Deterministic Logic active",
        "risk_index":       risk_index,
        "fate_check":       fate_check,
        "resource":         resource_value,
    }
