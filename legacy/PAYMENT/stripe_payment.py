"""
PAYMENT/stripe_payment.py — KING DIADEM
Legacy entry point — delegate ไปที่ create_checkout.py
ไม่ hardcode URL ไม่ hardcode price
"""
import os
import stripe
from PAYMENT.create_checkout import create_checkout as _create_checkout

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")


def create_checkout(email: str = "", plan: str = "basic") -> str | None:
    """
    Backward-compatible wrapper
    คืน URL หรือ None ถ้า error
    """
    result = _create_checkout(email=email, plan=plan)
    if "error" in result:
        print(f"⚠ stripe_payment.create_checkout error: {result['error']}")
        return None
    return result.get("url")
