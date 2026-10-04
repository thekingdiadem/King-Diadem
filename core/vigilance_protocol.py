# Vigilance Protocol
# System translation of the final Buddha teaching

VIGILANCE_KERNEL = {

    "origin_text":
    "anicca vata sankhara uppada vaya dhammino "
    "uppajjitva nirujjhanti tesam vupasamo sukho",

    "system_translation": [
        "all constructed systems are impermanent",
        "every system arises from conditions",
        "every system decays after arising",
        "stability emerges when reactive drift stops"
    ],

    "core_logic": {
        "impermanence": "all states drift over time",
        "conditional_arising": "state exists because dependencies exist",
        "decay": "every constructed state eventually dissolves",
        "vigilance": "maintain awareness of drift and prevent collapse"
    }

}


def vigilance_check(system_state):

    system_state = system_state if isinstance(system_state, dict) else {}
    try:
        stability = float(system_state.get("stability", 50))
        entropy = float(system_state.get("entropy", 50))
    except (TypeError, ValueError):
        stability, entropy = 50.0, 50.0

    if entropy > 70:
        return "high_attention_required"

    if stability < 40:
        return "stabilization_required"

    return "observe_and_preserve_choice"


def vigilance_report(system_state=None) -> dict:
    """รูปแบบ dict ที่ runtime ใช้ (vigilance_check เดิมคืน string — ผู้เรียกที่ใช้ .get() ล้ม)"""
    st = system_state if isinstance(system_state, dict) else {}
    signal = vigilance_check(st)
    alerts = [] if signal == "observe_and_preserve_choice" else [signal]
    return {"signal": signal, "alerts": alerts, "alert_count": len(alerts), "safe": not alerts}
