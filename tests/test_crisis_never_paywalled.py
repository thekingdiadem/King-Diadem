"""ข้อความฉุกเฉินต้องได้คำตอบพร้อมเบอร์ช่วยเหลือเสมอ แม้โควตาฟรีหมดและไม่มีเครดิต

เดิม /run หักโควตาก่อนตรวจอะไรเลย: คนที่ใช้ครบโควตาแล้วพิมพ์ "อยากตาย ไม่ไหวแล้ว" ได้ 402
"เติมเครดิตหรือสมัคร Premium" และหน้าเว็บเปิดหน้าจ่ายเงิน — ไม่มีเบอร์ 1323 เลย
"""
import pytest


def _use_up(client, n):
    for i in range(n):
        client.post("/run", json={"input": f"ทำงานเหนื่อย {i}"})


@pytest.mark.parametrize("text,needle", [
    ("อยากตาย ไม่ไหวแล้ว", "1323"),
    ("I want to kill myself", "988"),
    ("ไม่มีข้าวกิน 3 วันแล้ว", "1300"),
    ("สามีตีหัว ซ่อนอยู่ในห้องน้ำ", "191"),
    ("น้ำท่วมบ้าน ติดอยู่บนหลังคา", "1784"),
])
def test_urgent_message_answered_after_quota(client, app_module, text, needle):
    _use_up(client, app_module.FREE_DAILY_RUNS)
    assert client.post("/run", json={"input": "ทำงานเหนื่อยอีกแล้ว"}).status_code == 402   # ปกติยังคิดโควตา
    r = client.post("/run", json={"input": text})
    assert r.status_code == 200, r.text
    d = r.json()
    assert needle in d["ai_response"]
    assert d.get("answer_source") == "kernel"                     # ตอบจากสมการ — ไม่ใช้ AI ฟรีไม่จำกัด
