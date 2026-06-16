"""
SIMULATIONS/future_simulator.py — KING DIADEM
จำลองอนาคต: deterministic scenarios จาก state จริง
ไม่ใช้ random drift — ใช้ logic จาก FATE™
"""
import time


def simulate_future(system_state: dict, scenarios: int = 5) -> dict:
    """
    จำลอง n scenarios จาก state ปัจจุบัน
    คืน: scenarios list + best path + worst path + recommendation
    """
    if not isinstance(system_state, dict):
        system_state = {}

    entropy  = max(0.0, min(100.0, float(system_state.get("entropy",  50))))
    stability= max(0.0, min(100.0, float(system_state.get("stability",60))))
    resource = max(0.0, min(100.0, float(system_state.get("resource", 50))))

    # สร้าง deterministic scenarios ตาม intervention type
    INTERVENTIONS = [
        {"name": "ไม่ทำอะไร (baseline)",     "e_delta": +3,  "s_delta": -2,  "r_delta": -2},
        {"name": "ลด entropy (focus)",        "e_delta": -10, "s_delta": +5,  "r_delta": -3},
        {"name": "เพิ่ม resource (secure)",   "e_delta": +2,  "s_delta": +3,  "r_delta": +12},
        {"name": "เพิ่ม stability (anchor)",  "e_delta": -5,  "s_delta": +12, "r_delta": -5},
        {"name": "emergency stabilize",       "e_delta": -15, "s_delta": +8,  "r_delta": -8},
    ]

    results = []
    for i, iv in enumerate(INTERVENTIONS[:max(1, min(scenarios, 5))]):
        ne = max(0, min(100, entropy   + iv["e_delta"]))
        ns = max(0, min(100, stability + iv["s_delta"]))
        nr = max(0, min(100, resource  + iv["r_delta"]))

        rw = 0.5 + nr / 200
        score = round((ns - ne) * rw, 2)

        results.append({
            "scenario":       i + 1,
            "intervention":   iv["name"],
            "entropy":        round(ne, 1),
            "stability":      round(ns, 1),
            "resource":       round(nr, 1),
            "survival_score": score,
            "waterline":      "ABOVE" if score > 0 else "BELOW",
        })

    best  = max(results, key=lambda x: x["survival_score"])
    worst = min(results, key=lambda x: x["survival_score"])

    return {
        "timestamp":      time.time(),
        "input_state":    {"entropy": entropy, "stability": stability, "resource": resource},
        "scenarios":      results,
        "best_path":      best,
        "worst_path":     worst,
        "recommendation": _recommend(best, worst),
        "fate_lock":      "Fail less, not win more.",
    }


def _recommend(best: dict, worst: dict) -> str:
    gap = best["survival_score"] - worst["survival_score"]
    if gap > 20:
        return f"ความแตกต่างระหว่างทางเลือกสูง — เลือก '{best['intervention']}' จะดีกว่ามาก"
    return f"ทางเลือกใกล้เคียงกัน — เลือก '{best['intervention']}' เป็นจุดเริ่มต้นที่ปลอดภัยที่สุด"
