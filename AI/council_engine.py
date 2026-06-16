"""
AI/council_engine.py — KING DIADEM
build_consensus: รวมผลจาก council members → สรุปที่ใช้ได้จริง
"""

def build_consensus(council_results: dict) -> dict:
    if not council_results:
        return {
            "summary": "ไม่มีข้อมูลจาก council",
            "final_action": "stabilize",
            "confidence": 0.0,
            "member_count": 0,
            "lines": [],
        }

    lines = []
    actions = []
    confidence_total = 0.0

    for member, result in council_results.items():
        if isinstance(result, dict):
            action = result.get("action") or result.get("decision") or "—"
            conf   = float(result.get("confidence", 0.5))
            reason = result.get("reason") or result.get("message") or ""
            lines.append(f"{member}: {action} (confidence {conf:.0%}) {reason}".strip())
            actions.append(action)
            confidence_total += conf
        else:
            lines.append(f"{member}: {result}")
            actions.append(str(result))
            confidence_total += 0.5

    # หา action ที่ถูกโหวตมากที่สุด
    from collections import Counter
    final_action = Counter(actions).most_common(1)[0][0] if actions else "stabilize"
    avg_confidence = confidence_total / len(council_results)

    return {
        "summary":      "\n".join(lines),
        "final_action": final_action,
        "confidence":   round(avg_confidence, 3),
        "member_count": len(council_results),
        "lines":        lines,
    }
