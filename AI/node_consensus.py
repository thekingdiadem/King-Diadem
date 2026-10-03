"""
AI/node_consensus.py — KING DIADEM™
Node Consensus Engine — Deterministic Weighted Voting

❌ REMOVED: random.choices — ผลลัพธ์ไม่ reproducible
✅ REBUILT: deterministic weighted vote ตาม trust score + option rank

FATE™ A3: Same Input → Same Output
Article B-1: Choice(t) >= 1 → collapse = False
"ถ้าอธิบายไม่ได้ = ใช้ไม่ได้"
"""

import time
from typing import Optional

# ══════════════════════════════════════════════════════════════════
# VOTE STRATEGY REGISTRY — deterministic, no random
# ══════════════════════════════════════════════════════════════════

# แต่ละ node เลือก option ตาม bias strategy
# HIGH trust → เลือก option ที่ risk ต่ำสุด (Downside First)
# LOW trust  → เลือก option กลาง

TRUST_THRESHOLDS = {
    "high":   0.7,   # เลือก option อันดับ 1 (safest / best ranked)
    "medium": 0.4,   # เลือก option อันดับ 2
    "low":    0.0,   # เลือก option อันดับสุดท้าย (risky)
}


def _resolve_node_choice(options: list, trust: float, index: int) -> str:
    """
    Deterministic choice per node — ไม่มี random
    trust สูง → เลือก option ต้นลิสต์ (Downside First — ปลอดภัยกว่า)
    trust ต่ำ → เลือก option ท้ายลิสต์
    index ใช้เป็น tiebreaker

    FATE™ A3 — Same trust + index → same choice เสมอ
    """
    n = len(options)
    if n == 0:
        return ""
    if trust >= TRUST_THRESHOLDS["high"]:
        # high trust → top option
        return options[0]
    elif trust >= TRUST_THRESHOLDS["medium"]:
        # medium trust → middle option
        mid = min(1, n - 1)
        return options[mid]
    else:
        # low trust → last option (risky, least preferred)
        # but use index as offset to avoid all low-trust nodes voting same
        pick = (n - 1 - (index % max(1, n - 1))) % n
        return options[pick]


def node_vote(options: list, nodes: list, weights: list = None) -> dict:
    """
    Deterministic weighted vote
    รับ: options = ทางเลือก (Downside First order แนะนำ)
         nodes   = รายชื่อ node
         weights = trust score แต่ละ node (0.0–1.0)
    คืน: { votes, winner, confidence, ranked }

    FATE™ A3 — input เดิม = output เดิมเสมอ
    """
    # options ต้อง hash ได้ (เป็น key ของ votes) — dict/list ทำให้ TypeError
    options = [o if isinstance(o, (str, int, float, tuple)) else str(o) for o in (options or [])]
    if not options:
        return {
            "votes":      {},
            "winner":     None,
            "confidence": 0.0,
            "node_count": 0,
            "ranked":     [],
            "axiom":      "Choice(t) >= 1 → collapse = False",
        }

    # virtual nodes ถ้าไม่มี
    if not nodes:
        nodes = ["virtual_alpha", "virtual_beta", "virtual_gamma"]

    n = len(nodes)

    # normalize weights
    def _w(x):
        try:
            return max(0.01, min(1.0, float(x)))
        except (TypeError, ValueError):
            return 0.5
    if isinstance(weights, (list, tuple)) and len(weights) == n:
        w = [_w(x) for x in weights]
    else:
        w = [0.5] * n   # default trust = 0.5

    votes: dict = {o: 0.0 for o in options}

    for i, node in enumerate(nodes):
        trust  = w[i] if i < len(w) else 0.5
        choice = _resolve_node_choice(options, trust, i)
        if choice in votes:
            votes[choice] += trust   # vote weight = trust score

    total  = sum(votes.values()) or 1.0
    ranked = sorted(votes.items(), key=lambda x: x[1], reverse=True)
    winner = ranked[0][0]
    confidence = round(ranked[0][1] / total, 4)

    return {
        "votes":      {k: round(v, 3) for k, v in votes.items()},
        "winner":     winner,
        "confidence": confidence,
        "node_count": n,
        "ranked":     [{"option": k, "score": round(v / total, 4)} for k, v in ranked],
        "axiom":      "FATE™ A3 — deterministic | Downside First",
        "checked_at": time.time(),
    }


def multi_round_vote(options: list, nodes: list,
                     rounds: int = 3, weights: list = None) -> dict:
    """
    โหวตหลายรอบ — deterministic ทุกรอบ
    เพราะ node_vote ไม่มี random แล้ว ผลทุกรอบเหมือนกัน
    ใช้ multi-round เพื่อ weight amplification
    """
    options = [o if isinstance(o, (str, int, float, tuple)) else str(o) for o in (options or [])]
    if not options:
        return {"winner": None, "rounds": rounds, "confidence": 0.0}
    # ผลทุกรอบเหมือนกัน (deterministic) — rounds ใหญ่ๆ แค่เผา CPU จึงจำกัดไว้
    try:
        rounds = max(1, min(int(rounds), 100))
    except (TypeError, ValueError):
        rounds = 3

    win_count: dict = {o: 0 for o in options}

    for _ in range(rounds):
        result = node_vote(options, nodes, weights)
        if result["winner"]:
            win_count[result["winner"]] += 1

    total  = sum(win_count.values()) or 1
    winner = max(win_count, key=win_count.get)

    return {
        "winner":     winner,
        "win_counts": win_count,
        "rounds":     rounds,
        "confidence": round(win_count[winner] / total, 4),
        "axiom":      "FATE™ A3 — deterministic multi-round",
        "checked_at": time.time(),
    }


def weighted_consensus(options: list, node_trust_map: dict) -> dict:
    """
    รับ dict {node_id: trust_score} แทน list แยก
    ใช้ใน consensus_engine ที่มี node_trust.py
    """
    node_trust_map = node_trust_map if isinstance(node_trust_map, dict) else {}
    nodes   = list(node_trust_map.keys())
    weights = [node_trust_map[n] for n in nodes]
    return node_vote(options, nodes, weights)


# ── Self-test ─────────────────────────────────────────────────────
def _self_test() -> dict:
    options = ["reduce_exposure", "wait_and_observe", "advance"]
    nodes   = ["nodeA", "nodeB", "nodeC"]
    weights = [0.9, 0.5, 0.2]

    # determinism — same input same output
    r1 = node_vote(options, nodes, weights)
    r2 = node_vote(options, nodes, weights)
    assert r1["winner"] == r2["winner"], "non-deterministic!"
    assert r1["confidence"] == r2["confidence"]

    # high trust nodes → prefer first option (Downside First)
    r3 = node_vote(options, ["n1"], [0.95])
    assert r3["winner"] == options[0], f"expected {options[0]} got {r3['winner']}"

    # empty options → no crash
    r4 = node_vote([], nodes, weights)
    assert r4["winner"] is None

    # multi-round deterministic
    mr1 = multi_round_vote(options, nodes, rounds=5, weights=weights)
    mr2 = multi_round_vote(options, nodes, rounds=5, weights=weights)
    assert mr1["winner"] == mr2["winner"]

    # weighted_consensus
    trust_map = {"alpha": 0.9, "beta": 0.6, "gamma": 0.3}
    wc = weighted_consensus(options, trust_map)
    assert wc["winner"] in options

    return {"status": "OK", "module": "node_consensus"}


if __name__ == "__main__":
    import json
    options = ["survival_mode", "reduce_exposure", "wait_and_observe", "advance"]
    nodes   = ["vega_node", "lyla_node", "civil_node"]
    weights = [0.85, 0.70, 0.45]
    print(json.dumps(node_vote(options, nodes, weights), indent=2, default=str))
    print(_self_test())
