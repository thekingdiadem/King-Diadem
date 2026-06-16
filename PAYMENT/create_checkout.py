"""
PAYMENT/create_checkout.py — KING DIADEM
Stripe Checkout — secure, rate-limited, plan-aware
"""
import os
import re
import stripe

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# URL จาก env — ไม่ hardcode
SUCCESS_URL = os.getenv("STRIPE_SUCCESS_URL", "https://king-diadem.onrender.com/static/index.html?payment=success")
CANCEL_URL  = os.getenv("STRIPE_CANCEL_URL",  "https://king-diadem.onrender.com/static/index.html?payment=cancel")

# Plan mapping — price_id ต้องมาจาก env เท่านั้น
PLANS = {
    "basic":       os.getenv("STRIPE_PRICE_ID"),
    "civilization":os.getenv("STRIPE_PREMIUM_PRICE_ID") or os.getenv("STRIPE_PRICE_ID"),
    "topup":       os.getenv("STRIPE_TOPUP_PRICE_ID")   or os.getenv("STRIPE_PRICE_ID"),
}

_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _validate_email(email: str) -> bool:
    return bool(email) and bool(_EMAIL_RE.match(email)) and len(email) <= 254


def _sanitize(value: str, max_len: int = 200) -> str:
    """ตัด control chars + จำกัดความยาว"""
    if not isinstance(value, str):
        return ""
    return value.strip()[:max_len]


def create_checkout(email: str, plan: str = "basic",
                    api_key: str = None, user_id: str = None) -> dict:
    """
    สร้าง Stripe Checkout Session
    คืน {"url": ..., "session_id": ...} หรือ {"error": ...}
    """
    # ── Validate ────────────────────────────────────────────────
    email = _sanitize(email)
    plan  = _sanitize(plan).lower()

    if not _validate_email(email):
        return {"error": "อีเมลไม่ถูกต้อง"}

    if plan not in PLANS:
        return {"error": f"Plan ไม่รองรับ: {plan}"}

    price_id = PLANS.get(plan)
    if not price_id:
        return {"error": f"ยังไม่ได้ตั้งค่า STRIPE_PRICE_ID สำหรับ plan={plan}"}

    if not stripe.api_key:
        return {"error": "ยังไม่ได้ตั้งค่า STRIPE_SECRET_KEY"}

    # metadata — เก็บ user context สำหรับ webhook
    metadata = {
        "plan":    plan,
        "email":   email,
        "api_key": _sanitize(api_key or email, 100),
    }
    if user_id:
        metadata["user_id"] = _sanitize(str(user_id), 100)

    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="payment",
            customer_email=email,
            metadata=metadata,
            success_url=SUCCESS_URL + "&session_id={CHECKOUT_SESSION_ID}",
            cancel_url=CANCEL_URL,
            expires_at=None,  # default 24h
        )
        return {
            "url":        session.url,
            "session_id": session.id,
            "plan":       plan,
        }
    except stripe.error.CardError as e:
        return {"error": f"Card error: {e.user_message}"}
    except stripe.error.InvalidRequestError as e:
        return {"error": f"Invalid request: {e}"}
    except stripe.error.AuthenticationError:
        return {"error": "Stripe API key ไม่ถูกต้อง"}
    except stripe.error.StripeError as e:
        return {"error": f"Stripe error: {e}"}
    except Exception as e:
        return {"error": f"ระบบชำระเงินมีปัญหา กรุณาลองใหม่"}
