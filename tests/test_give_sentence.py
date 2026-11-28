"""หน้า /give: คนส่งประโยคแบบที่พิมพ์จริงตอนแย่ๆ → เข้าคิวโต๊ะติดป้าย (ลบเบอร์/อีเมล · ไม่เก็บตัวตน)"""
import pytest
from fastapi.testclient import TestClient

import app as kd
from core import answer_reports


@pytest.fixture()
def client():
    kd._rate_bucket.clear()
    return TestClient(kd.app)


def test_page_shows_help_and_consent(client):
    html = client.get("/give").text
    assert 'id="consent"' in html and "tel:1323" in html and "ไม่มีใครตอบกลับ" in html


def test_sentence_lands_in_label_queue_scrubbed(client):
    r = client.post("/api/give-sentence", json={"sentence": "ไม่ไหวแล้ว โทรมา 0812345678 นะ", "consent": True})
    assert r.status_code == 200 and r.json()["ok"]
    q = [x for x in answer_reports.label_queue(200) if x["reason"] == "donated"][-1]
    assert "ไม่ไหวแล้ว" in q["question"] and "0812345678" not in q["question"]


@pytest.mark.parametrize("payload", [{"sentence": "ไม่ไหวแล้ว"}, {"sentence": "ไม่ไหวแล้ว", "consent": "yes"},
                                     {"sentence": " ", "consent": True}, {"sentence": ["x"], "consent": True}, {}])
def test_needs_consent_and_text(client, payload):
    assert client.post("/api/give-sentence", json=payload).status_code == 400


def test_listed_in_sitemap(client):
    assert "/give" in client.get("/sitemap.xml").text
