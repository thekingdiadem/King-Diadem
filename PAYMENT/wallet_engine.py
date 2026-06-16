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

    amount = float(amount)
    if amount <= 0 or amount > 100000:
        return {"status": "error", "message": f"จำนวนไม่ถูกต้อง: {amount}"}

    try:
        new_balance = add_credits(email.strip(), amount)
        return {
            "status":      "success",
            "added":       amount,
            "balance":     new_balance,
            "source":      source,
            "timestamp":   time.time(),
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def spend(email: str, amount: float, reason: str = "") -> dict:
    """หัก credits — คืน success/fail + ยอดคงเหลือ"""
    if not email:
        return {"status": "error", "message": "ต้องระบุ email"}

    amount = float(amount)
    if amount <= 0:
        return {"status": "error", "message": "จำนวนต้องมากกว่า 0"}

    try:
        ok, remaining = deduct_credits(email.strip(), amount)
        if not ok:
            return {"status": "insufficient", "remaining": remaining,
                    "message": f"credits ไม่พอ (มี {remaining} ต้องการ {amount})"}
        return {"status": "success", "spent": amount, "remaining": remaining, "reason": reason}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def balance(email: str) -> dict:
    """ดูยอด credits คงเหลือ"""
    if not email:
        return {"status": "error", "balance": 0}
    try:
        credits = get_credits(email.strip())
        return {"status": "ok", "email": email, "balance": credits}
    except Exception as e:
        return {"status": "error", "message": str(e), "balance": 0}
