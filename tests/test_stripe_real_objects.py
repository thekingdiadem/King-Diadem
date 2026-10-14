"""Stripe ของจริง: ลายเซ็นจริง + ผลจาก SDK ที่ไม่ใช่ dict

stripe-python ตั้งแต่ v15 คืน Event / ListObject / Subscription / Price ที่ไม่ใช่ dict แล้ว — เรียก .get() พัง
เดิม webhook ใช้ผลของ construct_event ตรงๆ: event ที่เซ็นถูกต้องทุกตัวล่ม 500 ลูกค้าจ่ายเงินแล้วไม่ได้เครดิต/Premium
(เทสต์เดิมแทน construct_event ด้วย dict เลยไม่เคยเห็น) — ไฟล์นี้ใช้ construct_event จริงกับ HMAC จริง
"""
import hashlib
import hmac
import json
import time
import uuid

import stripe

from DATABASE.db import ensure_user, get_credits, get_premium_until

SECRET = "whsec_test_real"


def _signed_post(client, event):
    body = json.dumps(event)
    t = str(int(time.time()))
    sig = hmac.new(SECRET.encode(), f"{t}.{body}".encode(), hashlib.sha256).hexdigest()
    return client.post("/webhook/stripe", content=body,
                       headers={"stripe-signature": f"t={t},v1={sig}", "content-type": "application/json"})


def _obj(d):
    return stripe.StripeObject.construct_from(d, "sk_test_x")


def test_signed_topup_event_credits_the_account(client, monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    email, cs = f"r{uuid.uuid4().hex[:8]}@x.co", "cs_" + uuid.uuid4().hex[:10]
    ev = {"id": "evt_" + cs, "object": "event", "type": "checkout.session.completed", "data": {"object": {
        "id": cs, "object": "checkout.session", "payment_status": "paid", "client_reference_id": email,
        "currency": "thb", "amount_total": 5000, "metadata": {"kind": "wallet_topup", "email": email}}}}
    ensure_user(email)                     # บัญชีใหม่ได้ 10 เครดิตต้อนรับก่อน — วัดเฉพาะส่วนที่ได้จากการจ่าย
    before = get_credits(email)
    r = _signed_post(client, ev)
    assert r.status_code == 200, r.text
    assert get_credits(email) == before + 50


def test_bad_signature_still_rejected(client, monkeypatch):
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    r = client.post("/webhook/stripe", content=b'{"id":"evt_x","type":"invoice.paid"}',
                    headers={"stripe-signature": "t=1,v1=deadbeef"})
    assert r.status_code == 400


def test_subscription_checkout_with_real_sdk_objects(client, monkeypatch):
    """list_line_items / Subscription.retrieve คืน StripeObject (ไม่ใช่ dict) แบบที่ SDK ปัจจุบันคืนจริง"""
    monkeypatch.setenv("STRIPE_WEBHOOK_SECRET", SECRET)
    monkeypatch.setenv("STRIPE_PREMIUM_PRICE_ID", "price_prem")
    monkeypatch.setattr(stripe.checkout.Session, "list_line_items",
                        lambda sid: _obj({"object": "list", "data": [{"price": {"id": "price_prem"}, "quantity": 1}]}))
    monkeypatch.setattr(stripe.Subscription, "retrieve", lambda sid: _obj({"id": sid, "status": "active"}))
    email, cs = f"s{uuid.uuid4().hex[:8]}@x.co", "cs_" + uuid.uuid4().hex[:10]
    ev = {"id": "evt_" + cs, "object": "event", "type": "checkout.session.completed", "data": {"object": {
        "id": cs, "object": "checkout.session", "payment_status": "paid", "mode": "subscription",
        "client_reference_id": email, "customer": "cus_1", "subscription": "sub_1"}}}
    r = _signed_post(client, ev)
    assert r.status_code == 200, r.text
    assert get_credits(email) >= 100
    assert get_premium_until(email) > time.time()


def test_pricing_reads_real_price_object(client, monkeypatch, app_module):
    monkeypatch.setenv("STRIPE_SECRET_KEY", "sk_test_x")
    monkeypatch.setenv("STRIPE_PREMIUM_PRICE_ID", "price_prem")
    monkeypatch.setattr(stripe.Price, "retrieve",
                        lambda pid: _obj({"id": pid, "unit_amount": 27900, "currency": "thb", "recurring": {"interval": "month"}}))
    monkeypatch.setitem(app_module._PRICE_CACHE, "t", 0)
    assert client.get("/pricing").json()["premium"] == {"amount": 279.0, "currency": "THB", "interval": "month"}
