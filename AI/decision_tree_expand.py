# AI/decision_tree_expand.py
# KING DIADEM — Expanding Decision Tree
# FATE™ Axiom compliance: Determinism · Explainability=100% · Choice(t) ≥ 1
# Fail less. Harm less. Restore more.

# ── BRANCH REGISTRY ───────────────────────────────────────────────
# ทุก node มี: risk(0–1), reversible(bool), consequence(str)

_BRANCH_REGISTRY: dict[str, dict] = {
    "advance": {
        "risk": 0.55,
        "reversible": False,
        "consequence": "ใช้ resource — ผลชัดเจนใน 30–90 วัน",
        "children_keys": ["collect information", "reduce risk"],
    },
    "wait": {
        "risk": 0.20,
        "reversible": True,
        "consequence": "ไม่เสียทรัพยากร แต่หน้าต่างโอกาสอาจปิด",
        "children_keys": ["observe situation", "build alliance"],
    },
    "pivot": {
        "risk": 0.40,
        "reversible": False,
        "consequence": "เปลี่ยนทิศทาง — สูญ momentum เดิม",
        "children_keys": ["collect information", "advance"],
    },
    "reduce risk": {
        "risk": 0.10,
        "reversible": True,
        "consequence": "ลด exposure — อาจพลาดโอกาสสูง",
        "children_keys": ["wait", "observe situation"],
    },
    "explore opportunity": {
        "risk": 0.50,
        "reversible": True,
        "consequence": "เปิดข้อมูลใหม่ — risk ขึ้นกับสิ่งที่พบ",
        "children_keys": ["advance", "pivot"],
    },
    "observe situation": {
        "risk": 0.15,
        "reversible": True,
        "consequence": "ใช้เวลา — ไม่เสียอะไรนอกจาก window",
        "children_keys": ["wait", "collect information"],
    },
    "collect information": {
        "risk": 0.12,
        "reversible": True,
        "consequence": "เพิ่มความแม่นยำการตัดสินใจ",
        "children_keys": ["advance", "wait"],
    },
    "build alliance": {
        "risk": 0.30,
        "reversible": True,
        "consequence": "ขยายทรัพยากร — ขึ้นกับความไว้วางใจ",
        "children_keys": ["advance", "observe situation"],
    },
    "exit safely": {
        "risk": 0.08,
        "reversible": False,
        "consequence": "หยุด exposure — สูญสิ่งที่ลงทุนไปแล้ว",
        "children_keys": ["wait", "observe situation"],
    },
}

_ROUTE_ROOT_MAP: dict[str, list[str]] = {
    "survival": ["exit safely",  "reduce risk",         "observe situation"],
    "collapse": ["exit safely",  "reduce risk",         "wait"],
    "risk":     ["reduce risk",  "observe situation",   "collect information"],
    "general":  ["advance",      "wait",                "pivot"],
    "civil":    ["build alliance","wait",               "observe situation"],
    "vega":     ["advance",      "explore opportunity", "collect information"],
}


class ExpandingTree:
    """
    Deterministic decision tree generator
    FATE™ guarantee: Choice(t) ≥ 1 → always returns ≥ 1 node
    """

    def generate(
        self,
        problem: str,
        route: str = "general",
        depth: int = 1,
    ) -> list[dict]:
        """
        สร้าง decision tree จาก route + problem context
        depth=1 → root + immediate children เท่านั้น
        """
        roots = _ROUTE_ROOT_MAP.get(route, _ROUTE_ROOT_MAP["general"])
        nodes = []

        for root_key in roots:
            node = self._build_node(root_key, depth=depth, problem=problem)
            nodes.append(node)

        # เรียง risk ASC (Axiom 4)
        nodes.sort(key=lambda x: x["risk"])
        return nodes

    def _build_node(self, key: str, depth: int, problem: str) -> dict:
        base     = _BRANCH_REGISTRY.get(key, _BRANCH_REGISTRY["observe situation"])
        children = []

        if depth > 0:
            for child_key in base.get("children_keys", []):
                child_data = _BRANCH_REGISTRY.get(child_key, {})
                children.append({
                    "name":        child_key,
                    "risk":        child_data.get("risk", 0.30),
                    "reversible":  child_data.get("reversible", True),
                    "consequence": child_data.get("consequence", "—"),
                })

        return {
            "name":        key,
            "risk":        base["risk"],
            "reversible":  base["reversible"],
            "consequence": base["consequence"],
            "children":    children,
            "fate_note":   "irreversible — WARN" if not base["reversible"] else "reversible — OK",
        }
