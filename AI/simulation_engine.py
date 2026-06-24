# AI/simulation_engine.py
# KING DIADEM — Simulation Engine
# FATE™ Axiom compliance: Determinism · Downside First · Explainability=100%
# Fail less. Harm less. Restore more.

import time

# ── OUTCOME TABLE ─────────────────────────────────────────────────
# แต่ละ action มี: short_term(30d), long_term(90d), risk, reversible
_OUTCOME_TABLE: dict[str, dict] = {
    "advance": {
        "short_term":  "เห็นผลเร็ว แต่ resource burn สูง",
        "long_term":   "ถ้าสำเร็จ — ตำแหน่งแข็งแกร่ง / ถ้าไม่ — ฟื้นตัวยาก",
        "risk":        0.55,
        "reversible":  False,
        "tier":        "high",
    },
    "observe": {
        "short_term":  "ได้ข้อมูลเพิ่ม ไม่เสีย resource",
        "long_term":   "ตัดสินใจแม่นขึ้น แต่หน้าต่างโอกาสอาจปิด",
        "risk":        0.15,
        "reversible":  True,
        "tier":        "low",
    },
    "pivot": {
        "short_term":  "เปลี่ยนทิศ — momentum หยุดชั่วคราว",
        "long_term":   "ลด exposure ในทิศเดิม เพิ่ม option ใหม่",
        "risk":        0.40,
        "reversible":  False,
        "tier":        "medium",
    },
    "reduce risk": {
        "short_term":  "ลด downside ทันที",
        "long_term":   "รักษาทรัพยากร — อาจพลาดโอกาส high reward",
        "risk":        0.10,
        "reversible":  True,
        "tier":        "low",
    },
    "collect data": {
        "short_term":  "ใช้เวลา ไม่มี action",
        "long_term":   "เพิ่ม confidence ในการตัดสินใจครั้งถัดไป",
        "risk":        0.12,
        "reversible":  True,
        "tier":        "low",
    },
    "exit safely": {
        "short_term":  "หยุด exposure ทันที",
        "long_term":   "สูญสิ่งที่ลงทุน แต่รักษา core resource",
        "risk":        0.08,
        "reversible":  False,
        "tier":        "safe",
    },
    "build alliance": {
        "short_term":  "ขยายทรัพยากรผ่านความร่วมมือ",
        "long_term":   "แข็งแกร่งขึ้นถ้าพันธมิตรน่าเชื่อถือ",
        "risk":        0.30,
        "reversible":  True,
        "tier":        "medium",
    },
}

_SAFE_FALLBACK = "observe"


class Simulation:
    """
    Deterministic path simulator
    FATE™ guarantee: เรียง downside first, Choice(t) ≥ 1
    """

    def simulate(
        self,
        question: str,
        paths: list[str] | None = None,
        route: str = "general",
        n: int = 7,
    ) -> dict:
        """
        จำลองผลลัพธ์ของแต่ละ path แบบ deterministic

        Args:
            question: สถานการณ์
            paths:    รายการ action ที่ต้องการจำลอง (ถ้าว่างใช้ default 7 paths)
            route:    active route
            n:        จำนวน paths สูงสุด (default 7)

        Returns:
            outcomes list เรียงตาม risk ASC + fate_audit
        """
        if not question.strip():
            return {
                "error":     "FATE_VIOLATION: question empty",
                "outcomes":  [],
                "fate_note": "SYSTEM_PAUSE: no input",
            }

        # กำหนด paths ที่จะ simulate
        if paths and isinstance(paths, list):
            target_paths = [str(p).strip().lower() for p in paths if str(p).strip()]
        else:
            target_paths = list(_OUTCOME_TABLE.keys())

        target_paths = target_paths[:n]

        outcomes = []
        for action in target_paths:
            base = _OUTCOME_TABLE.get(action, _OUTCOME_TABLE[_SAFE_FALLBACK])
            outcomes.append({
                "action":      action,
                "short_term":  base["short_term"],
                "long_term":   base["long_term"],
                "risk":        base["risk"],
                "reversible":  base["reversible"],
                "tier":        base["tier"],
                "warn":        "⚠ irreversible — ย้อนไม่ได้" if not base["reversible"] else None,
            })

        # Downside First sort
        outcomes.sort(key=lambda x: x["risk"])

        fate_audit = {
            "total_paths":    len(outcomes),
            "choice_floor":   len(outcomes) >= 1,
            "has_safe_path":  any(o["tier"] in ("safe", "low") for o in outcomes),
            "irreversible":   [o["action"] for o in outcomes if not o["reversible"]],
        }

        return {
            "question":    question.strip(),
            "route":       route,
            "outcomes":    outcomes,
            "fate_audit":  fate_audit,
            "simulated_at": int(time.time()),
        }
