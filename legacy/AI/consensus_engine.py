# AI/consensus_engine.py — KING DIADEM
# Consensus Engine: weighted vote + evidence audit + FATE™ guard
# ต่างจาก council_engine.py — อันนี้คือ pure aggregation layer
# council_engine ใช้ consensus_engine เป็น sub-module ได้
# FATE™: Determinism · Explainability=100% · Choice(t) ≥ 1
# Fail less. Harm less. Restore more.

from __future__ import annotations
from collections import Counter
import time

_SAFE_ACTION  = "stabilize"
_MIN_EVIDENCE = "ไม่มีหลักฐานระบุ"

# weight ต่อ member — ปรับได้ตาม system config
_MEMBER_WEIGHT: dict[str, float] = {
    "LYLA":    1.0,
    "VEGA":    1.2,   # FATE™ analytical — weight สูงกว่าเล็กน้อย
    "TITAN":   1.1,   # survival-first
    "PATICCA": 1.0,
    "COSMOS":  0.9,   # long-term view — weight ต่ำกว่าในวิกฤต
}


def build_consensus(
    council_results: dict,
    route: str = "general",
    require_evidence: bool = True,
) -> dict:
    """
    Weighted consensus จาก council results

    Args:
        council_results: {member: result_dict_or_str}
        route:           active route — กระทบ weight adjustment
        require_evidence: ถ้า True → member ที่ไม่มี evidence ได้ weight ลด 50%

    Returns:
        summary str, final_action, confidence, consensus_level,
        audit_trail, fate_audit
    """
    if not isinstance(council_results, dict) or not council_results:
        return {
            "summary":      "ไม่มีผลจาก council",
            "final_action": _SAFE_ACTION,
            "confidence":   0.0,
            "consensus":    "DEFERRED",
            "agreement_pct": 0.0,
            "audit_trail":  [],
            "fate_audit":   {"choice_count": 0, "system_pause": True},
        }

    lines:        list[str]   = []
    action_votes: dict[str, float] = {}  # action → weighted vote
    conf_total:   float = 0.0
    weight_total: float = 0.0
    audit:        list[dict]  = []

    for member, result in council_results.items():
        base_weight = _MEMBER_WEIGHT.get(member, 1.0)

        # route adjustment — survival/collapse → TITAN/VEGA weight up
        if route in ("survival", "collapse"):
            if member == "TITAN":  base_weight *= 1.3
            if member == "VEGA":   base_weight *= 1.2
            if member == "COSMOS": base_weight *= 0.7  # ลด long-term ในวิกฤต

        if isinstance(result, dict):
            action   = str(result.get("action") or result.get("decision") or "observe").strip()
            try:
                conf = float(result.get("confidence", 0.5))
            except (TypeError, ValueError):
                conf = 0.5
            if conf > 1:          # บาง engine ส่งเป็นเปอร์เซ็นต์ (เช่น 80) → ค่าเฉลี่ยเพี้ยน
                conf = conf / 100.0
            conf = max(0.0, min(1.0, conf))
            evidence = str(result.get("evidence") or result.get("reason") or result.get("message") or _MIN_EVIDENCE)
            downside = str(result.get("downside") or "")

            # ลด weight ถ้าไม่มี evidence
            if require_evidence and evidence == _MIN_EVIDENCE:
                base_weight *= 0.5

            line = f"[{member}] {action}"
            if evidence != _MIN_EVIDENCE:
                line += f" — {evidence}"
            if downside:
                line += f" | ⚠ downside: {downside}"
        else:
            action   = str(result).strip() or "observe"
            conf     = 0.5
            evidence = _MIN_EVIDENCE
            if require_evidence:
                base_weight *= 0.5
            line = f"[{member}] {action} (no structured result)"

        lines.append(line)
        action_votes[action] = action_votes.get(action, 0.0) + base_weight
        conf_total   += conf * base_weight
        weight_total += base_weight

        audit.append({
            "member":   member,
            "action":   action,
            "evidence": evidence,
            "conf":     round(conf, 3),
            "weight":   round(base_weight, 3),
        })

    # final action = highest weighted vote
    final_action = max(action_votes, key=action_votes.get) if action_votes else _SAFE_ACTION
    avg_conf     = round(conf_total / weight_total, 3) if weight_total > 0 else 0.0

    # agreement = top action weight / total weight
    top_weight  = action_votes.get(final_action, 0.0)
    agreement   = round(top_weight / weight_total, 3) if weight_total > 0 else 0.0

    if agreement >= 0.70:   consensus = "STRONG"
    elif agreement >= 0.50: consensus = "MODERATE"
    elif agreement >= 0.35: consensus = "WEAK"
    else:                   consensus = "SPLIT"

    # FATE™: SPLIT → SYSTEM_PAUSE → fallback
    system_pause = consensus == "SPLIT"
    if system_pause:
        final_action = _SAFE_ACTION

    unique_actions = list(action_votes.keys())

    return {
        "summary":       "\n".join(lines),
        "final_action":  final_action,
        "confidence":    avg_conf,
        "consensus":     consensus,
        "agreement_pct": round(agreement * 100, 1),
        "action_votes":  {k: round(v, 3) for k, v in action_votes.items()},
        "audit_trail":   audit,
        "computed_at":   int(time.time()),
        "fate_audit": {
            "choice_count":  len(unique_actions),
            "system_pause":  system_pause,
            "pause_reason":  "SPLIT consensus → fallback stabilize" if system_pause else None,
            "route":         route,
            "evidence_required": require_evidence,
        },
    }
