"""บันทึกตรวจสอบย้อนหลัง (core/audit_log.py) — แก้บรรทัดกลางไฟล์แล้วต้องจับได้ และต้องไม่มีข้อความผู้ใช้

เดิมระบบมีแค่ civilization node ที่เขียนทับทั้งไฟล์ (เก็บ 500 node ล่าสุด) ผู้ตรวจจึงพิสูจน์ไม่ได้ว่าบันทึกไม่ถูกแก้
"""
import json
import os

from core import audit_log
from tests._front import front_page


def _rows(path):
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


def test_chain_verifies_and_detects_tampering(tmp_path):
    audit_log._last.clear()
    for r in (10, 85, 40):
        audit_log.record({"kind": "decision", "route": "talk", "risk": r, "topics": ["money"]}, root=str(tmp_path))
    path = str(next(tmp_path.glob("audit-*.jsonl")))
    assert audit_log.verify(path) == {"ok": True, "rows": 3, "broken_at": None}

    rows = _rows(path)
    rows[1]["risk"] = 5                                   # มีคนแก้คะแนนความเสี่ยงย้อนหลัง
    with open(path, "w", encoding="utf-8") as f:
        f.write("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))
    assert audit_log.verify(path)["broken_at"] == 2

    with open(path, "w", encoding="utf-8") as f:         # ลบบรรทัดกลางทิ้ง
        f.write("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in (rows[0], rows[2])))
    assert not audit_log.verify(path)["ok"]


def test_user_text_never_enters_the_log(tmp_path):
    audit_log._last.clear()
    row = audit_log.record({"kind": "decision", "text": "อยากตาย", "email": "a@b.c", "response": "...", "risk": 90},
                           root=str(tmp_path))
    raw = open(next(tmp_path.glob("audit-*.jsonl")), encoding="utf-8").read()
    assert "text" not in row and "email" not in row and "อยากตาย" not in raw and "a@b.c" not in raw


def test_retention_never_deletes_by_itself(tmp_path):
    for name in ("audit-2025-01.jsonl", "audit-2026-10.jsonl"):
        (tmp_path / name).write_text("")
    now = 1793923200                                       # 6 พ.ย. 2026
    assert audit_log.prunable(root=str(tmp_path), now=now) == ["audit-2025-01.jsonl"]
    assert os.path.exists(tmp_path / "audit-2025-01.jsonl")


def test_front_page_says_lyla_is_ai():
    """EU AI Act Art. 50: ผู้ใช้ต้องรู้ว่ากำลังคุยกับ AI ตั้งแต่ก่อนพิมพ์ ไม่ใช่ต่อเมื่อถาม"""
    page = front_page()
    assert 'id="ai-note"' in page and "เป็นระบบ AI ไม่ใช่คน" in page


def test_governance_documents_exist():
    root = os.path.join(os.path.dirname(__file__), "..", "docs", "governance")
    for name in ("AI_POLICY.md", "RISK_REGISTER.md", "INCIDENT_RUNBOOK.md", "VENDOR_RISK.md"):
        assert os.path.getsize(os.path.join(root, name)) > 500
