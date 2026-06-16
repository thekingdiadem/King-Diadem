"""
SIMULATIONS/scenario_tree.py — KING DIADEM
Scenario Tree: เส้นทางที่เป็นไปได้ตาม context
ไม่ใช่ template แข็ง — ปรับตาม route และ state
"""

_ROUTE_PATHS = {
    "survival": [
        {"path": "secure_minimum",  "description": "รักษาทรัพยากรขั้นต่ำที่ต้องการ — อาหาร น้ำ ที่พัก", "risk": 2},
        {"path": "seek_support",    "description": "ขอความช่วยเหลือจากคนที่ไว้ใจได้ 1 คน",              "risk": 2},
        {"path": "reduce_burn",     "description": "ตัดรายจ่ายที่ไม่จำเป็นทั้งหมดชั่วคราว",             "risk": 3},
        {"path": "wait",            "description": "รอและรวบรวมข้อมูลเพิ่มก่อนตัดสินใจใหญ่",            "risk": 4},
    ],
    "risk": [
        {"path": "hedge",           "description": "กระจายความเสี่ยง — ไม่วางทุกอย่างไว้ที่เดียว",      "risk": 3},
        {"path": "downside_first",  "description": "ประเมินสิ่งที่เสียได้มากที่สุดก่อนตัดสินใจ",         "risk": 2},
        {"path": "small_experiment","description": "ทดลองเล็กๆ ก่อนลงทุนเต็ม",                          "risk": 3},
        {"path": "reframe",         "description": "มองปัญหาจากมุมที่ต่างออกไป",                         "risk": 2},
    ],
    "collapse": [
        {"path": "stop_bleeding",   "description": "หยุดความสูญเสียก่อน — ไม่ทำให้แย่ลง",               "risk": 1},
        {"path": "one_path",        "description": "เลือก 1 ทางรอดที่เป็นไปได้ที่สุด แล้วโฟกัส",         "risk": 2},
        {"path": "call_for_help",   "description": "ติดต่อคนที่ช่วยได้ทันที — ไม่แก้คนเดียว",           "risk": 2},
    ],
    "vega": [
        {"path": "strategic_pause", "description": "หยุดก่อน 24h — วิเคราะห์ด้วย FATE™ ก่อนเดิน",       "risk": 1},
        {"path": "90day_view",      "description": "มองผล 90 วันข้างหน้า ไม่ใช่แค่วันนี้",                "risk": 2},
        {"path": "audit_trail",     "description": "บันทึกเหตุผลทุกขั้นตอน ตรวจสอบได้ภายหลัง",           "risk": 1},
    ],
    "general": [
        {"path": "wait",            "description": "รวบรวมข้อมูลเพิ่มก่อนตัดสินใจ",                      "risk": 2},
        {"path": "act",             "description": "ลองทำเล็กๆ ก่อน ดูผล แล้วค่อยขยาย",                  "risk": 3},
        {"path": "reframe",         "description": "เปลี่ยนมุมมอง — ปัญหาเดิมอาจมีทางออกใหม่",           "risk": 2},
        {"path": "collaborate",     "description": "หาคนร่วมคิด — 2 มุมมองดีกว่า 1 เสมอ",               "risk": 2},
    ],
}


def simulate_paths(problem: str | dict, route: str = "general") -> list:
    """
    คืนเส้นทางที่เป็นไปได้ตาม route
    เรียงจาก risk ต่ำ → สูง
    """
    route = str(route).lower()
    paths = _ROUTE_PATHS.get(route, _ROUTE_PATHS["general"])

    # inject problem context เข้าไปใน description
    if isinstance(problem, str) and problem.strip():
        paths = [
            {**p, "context": problem[:100]}
            for p in paths
        ]

    return sorted(paths, key=lambda x: x["risk"])


def build_tree(problem: str, state: dict = None) -> dict:
    """
    สร้าง decision tree เต็มรูปแบบ
    """
    state = state or {}
    entropy  = float(state.get("entropy",  50))
    stability= float(state.get("stability",60))

    # auto-select route จาก state
    if entropy > 75 and stability < 30:
        route = "collapse"
    elif entropy > 60:
        route = "survival"
    elif stability < 40:
        route = "risk"
    else:
        route = "general"

    paths = simulate_paths(problem, route)

    return {
        "problem":      problem,
        "route":        route,
        "paths":        paths,
        "recommended":  paths[0] if paths else None,
        "fate_axiom":   "Deferred is better than reckless.",
        "choice_count": len(paths),
    }
