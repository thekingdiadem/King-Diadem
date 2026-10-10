"""Stripe webhook: ล่มกลางทางแล้วส่งซ้ำต้องได้เครดิตครบครั้งเดียว · event มาไม่เรียงต้องไม่คืน premium"""
import time
import uuid

import pytest
import stripe

from DATABASE.db import get_credits, get_premium_until, credit_history


@pytest.fixture
def hook(client, monkeypatch):
    ev = {}
    monkeypatch.setattr(stripe.Webhook, "construct_event", lambda payload, sig, secret: ev["e"])
    def post(e):
        ev["e"] = e
        r = client.post("/webhook/stripe", content=b"{}", headers={"stripe-signature": "s"})
        return r.status_code, r.json().get("status") or r.json().get("error")
    return post


def _topup(email, cs):
    return {"id": "evt_" + cs, "type": "checkout.session.completed", "data": {"object": {
        "id": cs, "payment_status": "paid", "client_reference_id": email, "currency": "thb",
        "amount_total": 5000, "metadata": {"kind": "wallet_topup", "email": email}}}}


def test_crash_after_grant_is_not_double_credited(hook, app_module, monkeypatch):
    email, cs = f"t{uuid.uuid4().hex[:8]}@x.co", "cs_" + uuid.uuid4().hex[:8]
    real_mark = app_module.mark_stripe_event
    monkeypatch.setattr(app_module, "mark_stripe_event", lambda *a: (_ for _ in ()).throw(RuntimeError("crash")))
    assert hook(_topup(email, cs))[0] == 500
    after_first = get_credits(email)
    monkeypatch.setattr(app_module, "mark_stripe_event", real_mark)
    assert hook(_topup(email, cs))[0] == 200
    assert get_credits(email) == after_first          # ส่งซ้ำหลังล่มไม่เติมซ้ำ
    assert hook(_topup(email, cs))[1] == "duplicate"


def test_crash_before_grant_retries_and_credits(hook, monkeypatch):
    email, cs = f"p{uuid.uuid4().hex[:8]}@x.co", "cs_" + uuid.uuid4().hex[:8]
    fail = {"n": 1}
    def items(sid):
        if fail["n"]:
            fail["n"] -= 1
            raise RuntimeError("network")
        return {"data": [{"price": {"id": "price_prem"}, "quantity": 1}]}
    monkeypatch.setattr(stripe.checkout.Session, "list_line_items", items)
    ev = {"id": "evt_" + cs, "type": "checkout.session.completed", "data": {"object": {
        "id": cs, "payment_status": "paid", "client_reference_id": email, "mode": "subscription",
        "customer": "cus_" + cs, "subscription": "sub_old_" + cs, "metadata": {}}}}
    assert hook(ev)[0] == 500
    assert not [h for h in credit_history(email, 50) if h.get("reason") == "stripe_plan"]
    assert hook(ev)[0] == 200
    assert hook(ev)[1] == "duplicate"
    grants = [h for h in credit_history(email, 50) if h.get("reason") == "stripe_plan"]
    assert [g["delta"] for g in grants] == [100]       # ได้ครั้งเดียว ครบ 100
    assert get_premium_until(email) > time.time()


def test_stale_invoice_after_cancel_does_not_restore_premium(hook, monkeypatch):
    email, cs = f"s{uuid.uuid4().hex[:8]}@x.co", uuid.uuid4().hex[:8]
    monkeypatch.setattr(stripe.checkout.Session, "list_line_items", lambda sid: {"data": []})
    cus, old, new = "cus_" + cs, "sub_old_" + cs, "sub_new_" + cs
    hook({"id": "evt_c" + cs, "type": "checkout.session.completed", "data": {"object": {
        "id": "cs_" + cs, "payment_status": "paid", "client_reference_id": email, "mode": "subscription",
        "customer": cus, "subscription": old, "metadata": {}}}})
    hook({"id": "evt_d" + cs, "type": "customer.subscription.deleted", "data": {"object": {"id": old, "customer": cus}}})
    assert get_premium_until(email) <= time.time() + 1
    subs = {old: {"status": "canceled", "current_period_end": int(time.time()) + 30 * 86400},
            new: {"status": "active", "items": {"data": [{"current_period_end": int(time.time()) + 30 * 86400}]}}}
    monkeypatch.setattr(stripe.Subscription, "retrieve", lambda sid: subs[sid])
    hook({"id": "evt_i_old" + cs, "type": "invoice.paid", "data": {"object": {"customer": cus, "subscription": old}}})
    assert get_premium_until(email) <= time.time() + 1          # ใบเสร็จเก่าไม่คืน premium
    hook({"id": "evt_i_new" + cs, "type": "invoice.paid", "data": {"object": {"customer": cus,
          "parent": {"subscription_details": {"subscription": new}}}}})
    assert get_premium_until(email) > time.time() + 29 * 86400  # subscription ใหม่ต่ออายุได้
    hook({"id": "evt_d2" + cs, "type": "customer.subscription.deleted", "data": {"object": {"id": old, "customer": cus}}})
    assert get_premium_until(email) > time.time() + 29 * 86400  # ยกเลิกอันเก่าทีหลังไม่ตัดอันใหม่


def _plan_event(email, cs, price):
    return {"id": "evt_" + cs, "type": "checkout.session.completed", "data": {"object": {
        "id": cs, "payment_status": "paid", "client_reference_id": email, "mode": "subscription",
        "customer": "cus_" + cs, "subscription": "sub_" + cs, "metadata": {}}}}, price


def test_basic_plan_gives_credits_not_unlimited_premium(hook, monkeypatch):
    """เดิมแพ็กเกจพื้นฐาน (+10 เครดิต) ได้ Premium ไม่จำกัดไปด้วย — Premium ต้องมาจากราคา Premium เท่านั้น"""
    monkeypatch.setenv("STRIPE_PRICE_ID", "price_basic")
    monkeypatch.setenv("STRIPE_PREMIUM_PRICE_ID", "price_prem")
    email, cs = f"b{uuid.uuid4().hex[:8]}@x.co", "cs_" + uuid.uuid4().hex[:8]
    monkeypatch.setattr(stripe.checkout.Session, "list_line_items",
                        lambda sid: {"data": [{"price": {"id": "price_basic"}, "quantity": 1}]})
    ev, _ = _plan_event(email, cs, "price_basic")
    assert hook(ev)[0] == 200
    assert [h["delta"] for h in credit_history(email, 50) if h.get("reason") == "stripe_plan"] == [10]
    assert (get_premium_until(email) or 0) < time.time()


def test_basic_renewal_adds_credits_each_cycle(hook, monkeypatch):
    monkeypatch.setenv("STRIPE_PRICE_ID", "price_basic")
    monkeypatch.setenv("STRIPE_PREMIUM_PRICE_ID", "price_prem")
    email = f"r{uuid.uuid4().hex[:8]}@x.co"
    monkeypatch.setattr(stripe.Subscription, "retrieve", lambda sid: {
        "status": "active", "current_period_end": int(time.time()) + 30 * 86400,
        "items": {"data": [{"price": {"id": "price_basic"}}]}})
    inv = {"id": "evt_inv_" + email, "type": "invoice.paid", "data": {"object": {
        "id": "in_" + email, "customer": "cus_none", "customer_email": email,
        "subscription": "sub_x", "billing_reason": "subscription_cycle"}}}
    assert hook(inv)[0] == 200
    assert [h["delta"] for h in credit_history(email, 50) if h.get("reason") == "stripe_renewal"] == [10]
    assert (get_premium_until(email) or 0) < time.time()


def test_checkout_requires_login(client):
    """เดิมรับอีเมลที่พิมพ์มาเอง — เครดิตไปลงอีเมลใครก็ได้"""
    r = client.post("/create-checkout-session", json={"plan": "basic", "email": "someone@else.co"})
    assert r.status_code == 401


def test_promptpay_credits_after_async_success(hook):
    """PromptPay: completed มาแบบ unpaid (ยังไม่สแกน) ต้องไม่เติม · async_payment_succeeded แล้วค่อยเติม"""
    email, cs = f"q{uuid.uuid4().hex[:8]}@x.co", "cs_" + uuid.uuid4().hex[:8]
    ev = _topup(email, cs); ev["data"]["object"]["payment_status"] = "unpaid"
    topups = lambda: [h["delta"] for h in credit_history(email, 50) if h.get("reason") == "topup"]
    assert hook(ev)[0] == 200 and topups() == []
    ok = _topup(email, cs); ok["id"] = "evt_async_" + cs; ok["type"] = "checkout.session.async_payment_succeeded"
    assert hook(ok)[0] == 200 and topups() == [50]


def test_billing_portal_needs_login_and_pricing_safe_without_key(client):
    assert client.post("/billing-portal").status_code == 401
    assert client.get("/pricing").json()["premium"] is None
