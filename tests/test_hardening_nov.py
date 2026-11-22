"""อุดรอยรั่วก่อนรับผู้ใช้ (พ.ย. 2569)

1. compose เรียก assess ข้อความเดิมซ้ำ 4 ครั้ง (~6 ms/ครั้ง) → ชุดกวาด CI 3 หมื่นข้อความเกิน 30 นาทีจนถูกยกเลิก
2. สร้างหน้าจ่ายเงิน Stripe ได้ไม่จำกัดครั้ง → เปลืองโควตา API
3. /api/medical-review เปิดสาธารณะ คำนวณ ~70 ms ทุกครั้ง → ยิงถี่ทำเซิร์ฟเวอร์ช้า
"""
import pytest

from core import kernel_voice as kv


def test_compose_assesses_each_text_once(monkeypatch):
    calls = []
    real = kv._assess_uncached
    monkeypatch.setattr(kv, "_assess_uncached", lambda t, p=None: calls.append(t) or real(t, p))
    kv.compose("แม่หมดสติ ช่วยด้วย")
    assert calls.count("แม่หมดสติ ช่วยด้วย") == 1


def test_memo_does_not_leak_between_messages_or_mutations(monkeypatch):
    kv.compose("วันนี้เหนื่อยจัง")
    assert getattr(kv._MEMO, "d", None) is None                    # ทิ้งหลังจบ compose
    owner = kv._memo_start()
    a = kv.assess("อยากตาย")
    a["topics"].append("แก้เล่น")
    assert "แก้เล่น" not in kv.assess("อยากตาย")["topics"]          # ได้สำเนาใหม่ทุกครั้ง
    kv._memo_stop(owner)


@pytest.mark.parametrize("path", ["/wallet/topup", "/create-checkout-session", "/billing-portal"])
def test_payment_pages_are_rate_limited(client, app_module, path):
    app_module._rate_bucket.clear()
    codes = [client.post(path, json={}).status_code for _ in range(app_module._RATE_LIMIT_N + 2)]
    assert 429 in codes
    app_module._rate_bucket.clear()


def test_public_medical_summary_is_cached(client, app_module, monkeypatch):
    from core import medical_review
    app_module._MR_CACHE.update(t=0.0, v={})
    calls = []
    real = medical_review.summary
    monkeypatch.setattr(medical_review, "summary", lambda: calls.append(1) or real())
    for _ in range(5):
        assert client.get("/api/medical-review").json()["total"] > 300
    assert len(calls) == 1


def test_server_does_not_restart_every_few_chats():
    """สถานะเบื้องหลังถามหลายครั้งต่อข้อความ — max-requests 200 ทำให้ worker เดียวรีสตาร์ตทุก ~10 ข้อความ"""
    import re
    cmd = open("render.yaml", encoding="utf-8").read()
    n = int(re.search(r"--max-requests (\d+)", cmd).group(1))
    assert n >= 2000
    from tests._front import front_page
    page = front_page()
    assert "setTimeout(tick, 700)" in page and "Date.now() - t0 < 60000" in page
