# ENGINE/realhuman_survivorengine.py
# KING DIADEM — Real Human Survivor Engine
# พี่เขียน logic หลักไว้ดีแล้ว — เพิ่ม wire เข้า emotion_state + input_interpreter + ai_council

from __future__ import annotations
from dataclasses import dataclass, field

# ── Optional wires ────────────────────────────────────────────────
try:
    from ENGINE.emotion_state    import get_emotion_state
    _EMOTION_LOADED = True
except ImportError:
    _EMOTION_LOADED = False

try:
    from ENGINE.input_interpreter import parse_context
    _INTERPRETER_LOADED = True
except ImportError:
    _INTERPRETER_LOADED = False

try:
    from ENGINE.ai_council import ai_council
    _COUNCIL_LOADED = True
except ImportError:
    _COUNCIL_LOADED = False


def _money(v) -> str:
    return "ไม่ระบุ" if v is None else f"{v:.0f}"


# ── Data structures ───────────────────────────────────────────────

@dataclass
class HumanState:
    energy:          float = 50.0
    money:           float | None = None   # None = ผู้ใช้ไม่ได้บอก (ไม่ใช่ "ไม่มีเงิน")
    food_access:     bool  = True
    safe_place:      bool  = True
    mental_state:    str   = "stable"   # stable / stressed / overwhelmed
    time_available:  float = 8.0
    sleep_hours:     float = 6.0
    days_in_crisis:  int   = 0


@dataclass
class SurvivalOutput:
    status:           str
    priority:         str
    context_for_lyla: str
    waterline:        float
    can_decide:       bool
    flags:            list = field(default_factory=list)
    council:          dict = field(default_factory=dict)   # ★ เพิ่ม
    emotion:          str  = "NEUTRAL"                     # ★ เพิ่ม


# ── Engine ────────────────────────────────────────────────────────

class RealHumanSurvivorEngine:

    ENERGY_MIN      = 20
    ENERGY_CRITICAL = 10
    SLEEP_MIN       = 4
    CRISIS_LIMIT    = 7

    def run(
        self,
        state:      HumanState,
        session_id: str = "default",
        text:       str = "",
    ) -> SurvivalOutput:

        flags     = self._scan_flags(state)
        waterline = self._calc_waterline(state)

        # ── Emotion context ───────────────────────────────────────
        emotion_note = ""
        current_emotion = "NEUTRAL"
        if _EMOTION_LOADED and text:
            es = get_emotion_state(session_id)
            current_emotion = es.update(text)
            emotion_note    = es.context_note()

        # ── Council vote ──────────────────────────────────────────
        council_result: dict = {}
        if _COUNCIL_LOADED:
            try:
                council_result = ai_council(
                    money    = state.money,
                    food     = 1.0 if state.food_access else 0.0,
                    risk     = "critical" if waterline < 25 else
                               "high"     if waterline < 45 else
                               "moderate" if waterline < 65 else "low",
                    context  = {
                        "waterline":  waterline,
                        "energy":     state.energy,
                        "safe_place": state.safe_place,
                        "relationships": 50,
                    },
                )
            except Exception:
                pass

        # ── Level 0: overwhelmed ──────────────────────────────────
        if state.mental_state == "overwhelmed" or state.energy < self.ENERGY_CRITICAL:
            return SurvivalOutput(
                status   = "RESET_REQUIRED",
                priority = "หยุดก่อน ร่างกายและจิตใจต้องการ reset",
                context_for_lyla = self._ctx(
                    "OVERWHELMED",
                    f"energy={state.energy:.0f} mental={state.mental_state} "
                    f"sleep={state.sleep_hours:.1f}h days_crisis={state.days_in_crisis}",
                    "ห้ามตัดสินใจใหญ่ตอนนี้ — ให้ LYLA โฟกัสที่การ stabilize ก่อน "
                    "ไม่ใช่ให้คำแนะนำเชิงกลยุทธ์",
                    flags, emotion_note,
                ),
                waterline      = waterline,
                can_decide     = False,
                flags          = flags,
                council        = council_result,
                emotion        = current_emotion,
            )

        # ── Level 1: no food ──────────────────────────────────────
        if not state.food_access:
            return SurvivalOutput(
                status   = "CRITICAL_NO_FOOD",
                priority = "หาอาหารก่อนทุกอย่าง",
                context_for_lyla = self._ctx(
                    "NO_FOOD",
                    f"energy={state.energy:.0f} money={_money(state.money)}",
                    "LYLA ต้องช่วยหาทางได้อาหารทันที ไม่ใช่วางแผนระยะยาว",
                    flags, emotion_note,
                ),
                waterline  = waterline,
                can_decide = False,
                flags      = flags,
                council    = council_result,
                emotion    = current_emotion,
            )

        # ── Level 1: no shelter ───────────────────────────────────
        if not state.safe_place:
            return SurvivalOutput(
                status   = "CRITICAL_NO_SHELTER",
                priority = "หาที่ปลอดภัยก่อน",
                context_for_lyla = self._ctx(
                    "NO_SHELTER",
                    f"energy={state.energy:.0f}",
                    "LYLA ต้องช่วยหาพื้นที่ปลอดภัยก่อน ทุกเรื่องอื่นรอได้",
                    flags, emotion_note,
                ),
                waterline  = waterline,
                can_decide = False,
                flags      = flags,
                council    = council_result,
                emotion    = current_emotion,
            )

        # ── Level 2: low energy / sleep ───────────────────────────
        if state.energy < self.ENERGY_MIN or state.sleep_hours < self.SLEEP_MIN:
            return SurvivalOutput(
                status   = "LOW_ENERGY",
                priority = "พักก่อน ร่างกายไม่พร้อมทำงาน",
                context_for_lyla = self._ctx(
                    "LOW_ENERGY",
                    f"energy={state.energy:.0f} sleep={state.sleep_hours:.1f}h money={_money(state.money)}",
                    "LYLA แนะนำให้พักก่อน อย่าผลักดันให้ตัดสินใจใหญ่ "
                    "ถ้าต้องทำอะไรให้เลือกอย่างเดียวที่เล็กที่สุดก่อน",
                    flags, emotion_note,
                ),
                waterline  = waterline,
                can_decide = False,
                flags      = flags,
                council    = council_result,
                emotion    = current_emotion,
            )

        # ── Level 3: stressed ─────────────────────────────────────
        if state.mental_state == "stressed" or state.days_in_crisis > 3:
            return SurvivalOutput(
                status   = "STRESSED_FUNCTIONAL",
                priority = "ทำได้แต่ต้องระวัง — จำกัดการตัดสินใจ",
                context_for_lyla = self._ctx(
                    "STRESSED",
                    f"energy={state.energy:.0f} days_crisis={state.days_in_crisis} "
                    f"time={state.time_available:.1f}h",
                    "LYLA เสนอทางเลือกที่ใช้แรงน้อยก่อน "
                    "อย่าให้ list ยาว ให้โฟกัสหนึ่งอย่าง",
                    flags, emotion_note,
                ),
                waterline  = waterline,
                can_decide = True,
                flags      = flags,
                council    = council_result,
                emotion    = current_emotion,
            )

        # ── Level 4: stable ───────────────────────────────────────
        return SurvivalOutput(
            status   = "STABLE",
            priority = "พร้อมทำงานปกติ",
            context_for_lyla = self._ctx(
                "STABLE",
                f"energy={state.energy:.0f} time={state.time_available:.1f}h money={_money(state.money)}",
                "LYLA วิเคราะห์ได้เต็มที่ เสนอทางเลือกได้หลายทาง",
                flags, emotion_note,
            ),
            waterline  = waterline,
            can_decide = True,
            flags      = flags,
            council    = council_result,
            emotion    = current_emotion,
        )

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _ctx(
        status:       str,
        metrics:      str,
        instruction:  str,
        flags:        list,
        emotion_note: str,
    ) -> str:
        parts = [f"[SURVIVOR ENGINE] สถานะ: {status} | {metrics}"]
        parts.append(instruction)
        if flags:
            parts.append(f"flags={flags}")
        if emotion_note:
            parts.append(emotion_note)
        return " | ".join(parts)

    def _scan_flags(self, state: HumanState) -> list:
        flags = []
        if state.energy < self.ENERGY_CRITICAL:   flags.append("CRITICAL_ENERGY")
        if state.sleep_hours < self.SLEEP_MIN:     flags.append("SLEEP_DEBT")
        if not state.food_access:                  flags.append("NO_FOOD")
        if not state.safe_place:                   flags.append("NO_SHELTER")
        if state.days_in_crisis >= self.CRISIS_LIMIT: flags.append("CHRONIC_CRISIS")
        if state.money is not None and state.money <= 0: flags.append("NO_MONEY")
        return flags

    def _calc_waterline(self, state: HumanState) -> float:
        score = 100.0
        score -= max(0, (50 - state.energy))
        score -= max(0, (6  - state.sleep_hours) * 5)
        if not state.food_access:                      score -= 30
        if not state.safe_place:                       score -= 40
        if state.mental_state == "overwhelmed":        score -= 25
        if state.mental_state == "stressed":           score -= 10
        score -= min(20, state.days_in_crisis * 2)
        return max(0.0, min(100.0, score))


# ── Parse context → HumanState ───────────────────────────────────

def parse_state_from_context(context: dict) -> HumanState:
    """
    แปลง raw context dict → HumanState
    ใช้ input_interpreter ถ้าโหลดได้ ไม่งั้น fallback
    """
    if _INTERPRETER_LOADED:
        try:
            parsed = parse_context(context)
            return HumanState(
                energy         = parsed["energy"],
                money          = parsed["money"],
                food_access    = parsed["food_access"],
                safe_place     = parsed["safe_place"],
                mental_state   = parsed["mental_state"],
                time_available = parsed["time_available"],
                sleep_hours    = parsed["sleep_hours"],
                days_in_crisis = parsed["days_in_crisis"],
            )
        except Exception:
            pass

    # fallback — direct parse (แปลงค่าแบบไม่ล้ม)
    context = context if isinstance(context, dict) else {}
    def _f(v, d):
        try:
            return float(v)
        except (TypeError, ValueError):
            return d
    m = context.get("money")
    return HumanState(
        energy         = _f(context.get("energy"),         50.0),
        money          = _f(m, None) if m not in (None, "") else None,
        food_access    = context.get("food_access", True) not in (False, "false", "0", 0),
        safe_place     = context.get("safe_place",  True) not in (False, "false", "0", 0),
        mental_state   = str(context.get("mental_state", "stable")),
        time_available = _f(context.get("time_available"),  8.0),
        sleep_hours    = _f(context.get("sleep_hours"),     6.0),
        days_in_crisis = int(_f(context.get("days_in_crisis"), 0)),
    )


# ── Monday reset ─────────────────────────────────────────────────

def monday_reset(pleasure_level: float, energy: float) -> dict:
    try:
        pleasure_level, energy = float(pleasure_level), float(energy)
    except (TypeError, ValueError):
        pleasure_level, energy = 50.0, 50.0
    drop     = max(0.0, pleasure_level - energy)
    severity = "HIGH" if drop > 30 else "MODERATE" if drop > 15 else "LOW"
    return {
        "effect":   "EMOTIONAL_RESET",
        "drop":     drop,
        "severity": severity,
        "context_for_lyla": (
            f"[MONDAY_RESET] pleasure={pleasure_level:.0f} energy={energy:.0f} "
            f"drop={drop:.0f} severity={severity} | "
            f"LYLA รับรู้ว่าผู้ใช้อาจรู้สึกแย่หลังวันหยุด "
            f"ไม่ผลักดัน ช่วยหา momentum เล็กๆ ก่อน"
        ),
    }
