# AUTH/gateway.py
# KING DIADEM — Gateway v2.0
# Fix: ตัด credit ครั้งเดียว — authorize() จัดการทุกอย่างแล้ว
# ไม่เรียก use_credit() ซ้ำอีก
# -----------------------------------------------------------------

from AUTH.auth_system import authorize


def gateway(username: str, cost: int = 1) -> dict:
    """
    Entry point สำหรับทุก request ที่ต้องใช้ credit

    Returns
    -------
    {"status": "ok",      "credits_remaining": int}
    {"status": "blocked", "reason": str}
    """
    result = authorize(username, cost)

    if result["status"] != "allowed":
        return {
            "status": "blocked",
            "reason": result.get("reason", "unknown"),
        }

    return {
        "status":            "ok",
        "credits_remaining": result.get("credits_remaining", 0),
    }
