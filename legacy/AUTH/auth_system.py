# AUTH/auth_system.py
# KING DIADEM — Authorization System v2.0
# ใช้ use_credit จาก api_key_manager — ไม่ตัด credit ซ้ำ
# -----------------------------------------------------------------

from AUTH.api_key_manager import use_credit, get_credits


def authorize(username: str, cost: int = 1) -> dict:
    """
    ตรวจสอบและตัด credit ในขั้นตอนเดียว

    Returns
    -------
    {"status": "allowed", "credits_remaining": int}
    {"status": "blocked",  "reason": "no_credits" | "user_not_found"}
    """
    if not username or not username.strip():
        return {"status": "blocked", "reason": "no_username"}

    ok = use_credit(username, cost)

    if not ok:
        balance = get_credits(username)
        reason  = "insufficient_credits" if balance == 0 else "credit_below_cost"
        return {"status": "blocked", "reason": reason, "credits": balance}

    return {
        "status":            "allowed",
        "credits_remaining": get_credits(username),
    }
