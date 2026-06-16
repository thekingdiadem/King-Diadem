"""
SIMULATIONS/entropy_engine.py — KING DIADEM
Entropy analysis: deterministic + signal-based
ไม่ใช้ random drift — คำนวณจาก state จริง
"""

def analyze_entropy(system_state: dict) -> dict:
    """
    วิเคราะห์ entropy และคาดการณ์ทิศทาง
    คืน state + survival score + แนวทางปฏิบัติ
    """
    if not isinstance(system_state, dict):
        system_state = {}

    entropy  = max(0.0, min(100.0, float(system_state.get("entropy",  50))))
    stability= max(0.0, min(100.0, float(system_state.get("stability",50))))
    resource = max(0.0, min(100.0, float(system_state.get("resource", 50))))

    # survival score = stability - entropy (weighted by resource)
    resource_weight = 0.5 + (resource / 200)  # 0.5–1.0
    survival_score  = round((stability - entropy) * resource_weight, 2)

    # drift projection — ถ้าไม่มีการแทรกแซง
    entropy_trend  = _trend(entropy,  high_bad=True)
    stability_trend= _trend(stability, high_bad=False)

    # state classification
    if survival_score > 30:
        state = "high_stability"
        action= "maintain"
        message = "ระบบมีเสถียรภาพดี — ไปต่อได้พอประมาณ"
    elif survival_score > 10:
        state = "balanced"
        action= "monitor"
        message = "สมดุลแต่เปราะบาง — ติดตามสัญญาณ"
    elif survival_score > -10:
        state = "unstable"
        action= "stabilize"
        message = "ระบบเริ่มเสียสมดุล — ลด entropy ก่อน"
    elif survival_score > -30:
        state = "high_risk"
        action= "secure_resources"
        message = "ความเสี่ยงสูง — รักษาทรัพยากรพื้นฐานก่อน"
    else:
        state = "collapse_risk"
        action= "emergency_stabilize"
        message = "วิกฤต — หยุดทุกอย่าง รักษา 1 ทางรอดก่อน"

    # 30-day projection
    projected_30d = round(survival_score * (0.9 if entropy > 60 else 1.05), 2)

    return {
        "entropy":        entropy,
        "stability":      stability,
        "resource":       resource,
        "survival_score": survival_score,
        "system_state":   state,
        "action":         action,
        "message":        message,
        "trends": {
            "entropy":   entropy_trend,
            "stability": stability_trend,
        },
        "projection_30d": projected_30d,
        "waterline":      "ABOVE" if survival_score > 0 else "BELOW",
    }


def _trend(value: float, high_bad: bool) -> str:
    """ประเมินทิศทางจากค่าปัจจุบัน"""
    if high_bad:
        if value > 70: return "deteriorating"
        if value > 50: return "concerning"
        return "stable"
    else:
        if value > 65: return "strong"
        if value > 40: return "moderate"
        return "weak"
