"""
PAYMENT/stripe_webhook.py — KING DIADEM
Webhook handler — signature verify + idempotency + fraud guard

LEGACY: webhook ที่ใช้งานจริงคือ /webhook/stripe ใน app.py — ไฟล์นี้ไม่มีผู้เรียก
"""
import os
import time
import stripe
from DATABASE.credit_store import add_credits

stripe.api_key     = os.getenv("STRIPE_SECRET_KEY")
WEBHOOK_SECRET     = os.getenv("STRIPE_WEBHOOK_SECRET")

# Idempotency cache — event_id → timestamp
# ใช้ dict พร้อม TTL แทน set เพื่อไม่ให้ memory รั่ว
_processed: dict[str, float] = {}
_TTL = 86400  # 24 ชั่วโมง


def _clean_old_events():
    """ล้าง event เก่ากว่า TTL"""
    now = time.time()
    expired = [k for k, t in _processed.items() if now - t > _TTL]
    for k in expired:
        del _processed[k]


def _safe_meta(session: dict, key: str, max_len: int = 200) -> str:
    val = session.get("metadata", {}).get(key, "")
    return str(val).strip()[:max_len]


def handle_webhook(payload: bytes, sig_header: str) -> tuple[str, int]:
    """
    ตรวจสอบ Stripe webhook signature แล้ว process event
    คืน (message, http_status)
    """
    if not WEBHOOK_SECRET:
        return "Webhook secret ไม่ได้ตั้งค่า", 500

    # ── Signature verification (CRITICAL — ห้ามข้าม) ────────────
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, WEBHOOK_SECRET)
    except Exception:
        return "Invalid signature", 400

    # ── Idempotency guard ────────────────────────────────────────
    # เดิมใช้ dict ในหน่วยความจำ — restart/หลาย worker แล้ว Stripe ส่งซ้ำ = เติมเครดิตซ้ำ
    event_id = event.get("id", "")
    try:
        from DATABASE.db import claim_stripe_event
        if not claim_stripe_event(event_id, event.get("type", "")):
            return "duplicate", 200
    except Exception:
        _clean_old_events()
        if event_id in _processed:
            return "duplicate", 200
        _processed[event_id] = time.time()

    # ── Event routing ────────────────────────────────────────────
    event_type = event.get("type", "")

    if event_type == "checkout.session.completed":
        _handle_checkout_completed(event["data"]["object"])

    elif event_type == "payment_intent.payment_failed":
        _handle_payment_failed(event["data"]["object"])

    # log event type (ไม่ log payload เต็ม — PII)
    print(f"✅ Webhook processed: {event_type} | id={event_id}")
    return "ok", 200


def _handle_checkout_completed(session: dict):
    """เติม credits หลังชำระเงินสำเร็จ"""
    payment_status = session.get("payment_status")
    if payment_status != "paid":
        print(f"⚠ checkout.session.completed but payment_status={payment_status} — skip")
        return

    api_key = _safe_meta(session, "api_key")
    email   = _safe_meta(session, "email") or session.get("customer_email", "")
    plan    = _safe_meta(session, "plan", 50)

    if not api_key and not email:
        print(f"⚠ webhook: ไม่พบ api_key หรือ email ใน metadata")
        return

    # คำนวณ credits จาก plan ไม่ใช่ amount (ป้องกัน manipulation)
    PLAN_CREDITS = {
        "basic":        100,
        "civilization": 500,
        "topup":        50,
    }
    # plan ที่ไม่รู้จัก = 0 เครดิต (เดิมคิดจาก amount_total ซึ่งไม่ผูกกับราคาที่ตกลงไว้)
    credits = PLAN_CREDITS.get(plan, 0)
    if not credits:
        print(f"⚠ unknown plan in webhook: {plan!r} — 0 credits")
        return

    identifier = api_key or email
    try:
        add_credits(identifier, credits)
        print(f"✅ Credits added: {credits} → {identifier} (plan={plan})")
    except Exception as e:
        print(f"❌ add_credits failed: {type(e).__name__}")


def _handle_payment_failed(payment_intent: dict):
    """Log เมื่อชำระไม่สำเร็จ"""
    pi_id = payment_intent.get("id", "—")
    print(f"⚠ Payment failed: intent={pi_id}")
