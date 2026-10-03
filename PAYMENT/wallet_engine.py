"""
PAYMENT/wallet_engine.py — KING DIADEM
Wallet: topup + deduct + balance check
"""
import time
from DATABASE.credit_store import add_credits, get_credits, deduct_credits


def topup(email: str, amount: float, source: str = "manual") -> dict:
    """เติม credits — validate amount ก่อนเสมอ"""
    if not email or not isinstance(email, str):
        return {"status": "error", "message": "email ไม่ถูกต้อง"}

    # เครดิตเป็นจำนวนเต็ม — เดิม float 0.5 ถูกปัดเป็น 0 แต่รายงานว่า "added 0.5"
    try:
        amount = int(amount)
    except (TypeError, ValueError):
        amount = 0
    if amount <= 0 or amount > 100000:
        return {"status": "error", "message": "จำนวนไม่ถูกต้อง"}

    try:
        new_balance = add_credits(email.strip(), amount)
        return {
            "status":      "success",
            "added":       amount,
            "balance":     new_balance,
            "source":      source,
            "timestamp":   time.time(),
        }
    except Exception:
        return {"status": "error", "message": "wallet_unavailable"}


def spend(email: str, amount: float, reason: str = "") -> dict:
    """หัก credits — คืน success/fail + ยอดคงเหลือ"""
    if not email:
        return {"status": "error", "message": "ต้องระบุ email"}

    try:
        amount = int(amount)
    except (TypeError, ValueError):
        amount = 0
    if amount <= 0:
        return {"status": "error", "message": "จำนวนต้องเป็นจำนวนเต็มมากกว่า 0"}

    try:
        ok, remaining = deduct_credits(email.strip(), amount)
        if not ok:
            return {"status": "insufficient", "remaining": remaining,
                    "message": f"credits ไม่พอ (มี {remaining} ต้องการ {amount})"}
        return {"status": "success", "spent": amount, "remaining": remaining, "reason": reason}
    except Exception:
        return {"status": "error", "message": "wallet_unavailable"}


def balance(email: str) -> dict:
    """ดูยอด credits คงเหลือ"""
    if not email:
        return {"status": "error", "balance": 0}
    try:
        credits = get_credits(email.strip())
        return {"status": "ok", "email": email, "balance": credits}
    except Exception:
        return {"status": "error", "message": "wallet_unavailable", "balance": 0}
