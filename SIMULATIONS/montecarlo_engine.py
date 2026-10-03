"""
SIMULATIONS/montecarlo_engine.py — KING DIADEM
Monte Carlo: จำลอง n runs ด้วย bounded perturbation
ไม่ใช้ pure random — perturbation ถูก anchor ด้วย state จริง
"""
import math


def _num(v, d: float) -> float:
    try:
        x = float(v)
    except (TypeError, ValueError):
        return d
    return x if x == x else d


def run_montecarlo(score: float, runs: int = 100,
                   volatility: float = 0.15) -> dict:
    """
    Monte Carlo simulation แบบ bounded
    - score: ค่าเริ่มต้น (0-1 หรือ survival score)
    - runs: จำนวน simulation
    - volatility: ความผันผวน (0.0-1.0)
    คืน stats ครบ + distribution
    """
    score      = _num(score, 0.0)
    runs       = max(10, min(int(_num(runs, 100)), 10000))
    volatility = max(0.01, min(_num(volatility, 0.15), 0.5))

    # ใช้ deterministic perturbation แทน pure random
    # (reproducible + bounded)
    results = []
    for i in range(runs):
        # pseudo-random ที่ reproducible
        phase = (i * 2.399963) % (2 * math.pi)  # golden angle
        noise = math.sin(phase) * volatility
        outcome = max(-1.0, min(2.0, score + noise))
        results.append(round(outcome, 4))

    avg    = sum(results) / len(results)
    sorted_r = sorted(results)
    p10    = sorted_r[int(runs * 0.10)]
    p25    = sorted_r[int(runs * 0.25)]
    p75    = sorted_r[int(runs * 0.75)]
    p90    = sorted_r[int(runs * 0.90)]

    variance  = sum((x - avg) ** 2 for x in results) / runs
    std_dev   = math.sqrt(variance)

    above_zero = sum(1 for r in results if r > 0)

    return {
        "runs":            runs,
        "input_score":     round(score, 4),
        "average_score":   round(avg, 4),
        "min":             round(sorted_r[0], 4),
        "max":             round(sorted_r[-1], 4),
        "std_dev":         round(std_dev, 4),
        "percentiles": {
            "p10": round(p10, 4),
            "p25": round(p25, 4),
            "p75": round(p75, 4),
            "p90": round(p90, 4),
        },
        # ค่ากระจายแบบ deterministic (golden angle) ไม่ใช่การสุ่ม — "probability" คือสัดส่วนของชุดนี้
        "survival_probability": round(above_zero / runs, 3),
        "method":          "deterministic_golden_angle",
        "verdict": _verdict(avg, std_dev),
    }


def _verdict(avg: float, std: float) -> str:
    if avg > 0.6 and std < 0.15:  return "เสถียร — ไปต่อได้"
    if avg > 0.4:                  return "พอผ่านได้ — ติดตามต่อ"
    if avg > 0.2:                  return "เปราะบาง — ต้องเสริมทรัพยากร"
    return                                "ความเสี่ยงสูง — ต้องแทรกแซงก่อน"
