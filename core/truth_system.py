"""
core/truth_system.py — KING DIADEM
Truth Infrastructure: สะท้อนความจริง + เปิดทางเลือก
ไม่ใช้ GPT — ใช้ singleton Gemini + FATE™ + Survivor Engine
"""

import asyncio
import os

# ══════════════════════════════════════════════════════════════════
# TRUTH KERNEL PROMPT
# ══════════════════════════════════════════════════════════════════
KERNEL_PROMPT = """[KING DIADEM — ETERNAL TRUTH MODE]

กฎของระบบ:
- สะท้อนความจริงตามสภาพที่เกิดขึ้น ไม่บิดเบือน ไม่ปลอบใจเกินจริง
- รักษา Choice(t) ≥ 1 เสมอ — ทางเลือกต้องไม่เคยเป็นศูนย์
- ไม่สั่ง ไม่ชี้นำ ไม่ตัดสิน — เปิดทางให้มนุษย์เลือก
- อธิบายได้ภายใน 2 นาที (FATE™ Axiom 5)

FORMAT การตอบ:
- ความจริงที่ปรากฏ: [สรุปสถานการณ์จริงๆ]
- ทางเลือกที่มีอยู่: [อย่างน้อย 2 ทาง]
- สรุป 3 บรรทัด: [ชัดเจน ใช้งานได้ทันที]

Fail Less. Harm Less. Restore Choice.
"""


# ══════════════════════════════════════════════════════════════════
# TRUTH SYSTEM CLASS
# ══════════════════════════════════════════════════════════════════
class TruthSystem:
    def __init__(self):
        self._llm = None

    def _get_llm(self):
        if self._llm is None:
            try:
                from core.llm_gemini import get_llm
                self._llm = get_llm()
            except Exception as e:
                print(f"⚠ TruthSystem: LLM unavailable — {e}")
        return self._llm

    async def gemini_view(self, context: str) -> str:
        llm = self._get_llm()
        if not llm:
            return "[Gemini unavailable — LLM not loaded]"
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: llm.generate(
                    prompt=f"{KERNEL_PROMPT}\n\nบริบท:\n{context}",
                    temperature=0.65,
                    max_tokens=800,
                )
            )
            return result or "[Gemini: empty response]"
        except Exception as e:
            return f"[Gemini ERROR] {e}"

    async def gpt_view(self, context: str) -> str:
        # GPT removed — ใช้ VEGA mode แทน
        return "[GPT REMOVED — ใช้ VEGA ◆ strategic mode แทน]"

    async def fate_view(self, message: str) -> dict:
        try:
            from core.fate_core import run_fate
            return run_fate({"message": message})
        except Exception as e:
            return {"error": str(e)}

    async def entropy_view(self, state: dict) -> dict:
        try:
            from core.entropy_guard import analyze_entropy_state
            return analyze_entropy_state(state)
        except Exception as e:
            return {"error": str(e)}


# ══════════════════════════════════════════════════════════════════
# MAIN: run_truth_infrastructure
# ══════════════════════════════════════════════════════════════════
async def run_truth_infrastructure(user_input: str, state_dict: dict) -> dict:
    """
    Truth infrastructure pipeline:
    1. Survivor Engine — วิเคราะห์สถานะมนุษย์จริง
    2. Entropy Guard — คำนวณ entropy state
    3. FATE™ — ตรวจสอบ logic
    4. Gemini — สะท้อนความจริง + เปิดทางเลือก
    """
    state_dict = state_dict if isinstance(state_dict, dict) else {}

    # ── 1. Survivor Engine ───────────────────────────────────────
    survival_json = {}
    try:
        from ENGINE.realhuman_survivorengine import RealHumanSurvivorEngine, HumanState
        survivor = RealHumanSurvivorEngine()
        h_state  = HumanState(**{
            k: state_dict[k] for k in state_dict
            if k in HumanState.__dataclass_fields__
        }) if hasattr(HumanState, '__dataclass_fields__') else HumanState(**state_dict)
        survival_out = survivor.run(h_state)
        survival_json = {
            "status":  str(getattr(survival_out, "status",  "unknown")),
            "actions": str(getattr(survival_out, "actions", "none")),
            "can_decide": getattr(survival_out, "can_decide", True),
        }
    except Exception as e:
        survival_json = {"error": str(e), "status": "unavailable"}

    # ── 2. Build context ─────────────────────────────────────────
    context = (
        f"สถานะระบบ:\n{survival_json}\n\n"
        f"เหตุการณ์:\n{user_input}"
    )

    ts = TruthSystem()

    # ── 3. Run parallel ──────────────────────────────────────────
    results = await asyncio.gather(
        ts.gemini_view(context),
        ts.fate_view(user_input),
        ts.entropy_view(state_dict),
        return_exceptions=True,
    )

    def _safe(r):
        return f"[ERROR] {r}" if isinstance(r, Exception) else r

    gemini_result  = _safe(results[0])
    fate_result    = _safe(results[1])
    entropy_result = _safe(results[2])

    # ── 4. Risk assessment ───────────────────────────────────────
    try:
        resource_value = float(state_dict.get("resource", 50))
    except Exception:
        resource_value = 50.0
    risk_index = round(max(0, min(100, (100 - resource_value) * 0.75)), 2)

    return {
        "survival":    survival_json,
        "perspectives": {
            "gemini": gemini_result,
            "vega":   "[ใช้ VEGA mode ผ่าน /run?voice_mode=vega]",
        },
        "fate_check":    fate_result,
        "entropy_state": entropy_result,
        "risk_index":    risk_index,
        "truth_lock":    "Choice(t) ≥ 1 → collapse = False",
    }


# ══════════════════════════════════════════════════════════════════
# SYNC HELPER
# ══════════════════════════════════════════════════════════════════
def run_sync(user_input: str, state_dict: dict) -> dict:
    """Helper สำหรับ sync context เรียก async"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                future = pool.submit(
                    asyncio.run,
                    run_truth_infrastructure(user_input, state_dict)
                )
                return future.result(timeout=30)
        return loop.run_until_complete(
            run_truth_infrastructure(user_input, state_dict)
        )
    except Exception as e:
        return {"error": str(e), "truth_lock": "Choice(t) ≥ 1 → collapse = False"}
