"""ทะเบียนการเปลี่ยนค่าที่กระทบผู้ใช้ — FATE™ หลักการ 4 "การยกเว้นต้องมีหลักฐาน"
เดิมผู้ดูแลเปลี่ยนโควตาฟรีหรือราคาใน Render ได้เงียบๆ ไม่มีใครรู้ว่าเปลี่ยนเมื่อไหร่ เพราะอะไร"""
from core import policy_registry as pr


def test_first_run_records_every_value_as_the_starting_point():
    changes = pr.diff({"FREE_DAILY_RUNS": 20, "RUN_COST": 1}, {})
    assert ("FREE_DAILY_RUNS", "", "20") in changes and len(changes) == len(pr.WATCHED)


def test_only_changed_values_are_recorded():
    last = {k: "1" for k in pr.WATCHED}
    assert pr.diff({k: 1 for k in pr.WATCHED}, last) == []
    cur = {k: 1 for k in pr.WATCHED} | {"FREE_DAILY_RUNS": 10}
    assert pr.diff(cur, last) == [("FREE_DAILY_RUNS", "1", "10")]


def test_missing_reason_is_flagged_not_hidden():
    assert pr.clean_reason(None) == pr.NO_REASON and pr.clean_reason("   ") == pr.NO_REASON
    assert pr.clean_reason("  ค่า API   ขึ้น  ") == "ค่า API ขึ้น"
    assert len(pr.clean_reason("ก" * 1000)) == pr.MAX_REASON


def test_public_view_never_reveals_price_ids():
    row = pr.public_row({"ts": 1.0, "key": "STRIPE_PRICE_ID", "old": "price_old123", "new": "price_new456", "reason": pr.NO_REASON})
    assert "price_" not in str(row) and row["old"] != row["new"] and row["no_reason"]
    quota = pr.public_row({"ts": 1.0, "key": "FREE_DAILY_RUNS", "old": "20", "new": "10", "reason": "ลดต้นทุนช่วงทดลอง"})
    assert quota["old"] == "20" and quota["new"] == "10" and quota["label"]["en"] == "Free messages per day"


def test_sync_records_a_change_once_even_with_many_workers(app_module, monkeypatch):
    from DATABASE.db import policy_history
    app_module._policy_sync()                                   # ตั้งต้นให้ตรงค่าปัจจุบัน
    assert app_module._policy_sync() == []                     # เปิดซ้ำค่าเดิม = ไม่มีอะไรใหม่
    before = len(policy_history(200))
    monkeypatch.setattr(app_module, "FREE_DAILY_RUNS", 7)
    monkeypatch.setenv("POLICY_CHANGE_REASON", "ทดลองลดโควตาช่วงโหลดสูง")
    app_module._policy_sync()
    app_module._policy_sync()                                   # worker ที่สองเห็นค่าเดิมอยู่แล้ว ไม่บันทึกซ้ำ
    rows = policy_history(200)
    assert len(rows) == before + 1
    assert rows[0]["key"] == "FREE_DAILY_RUNS" and rows[0]["new"] == "7" and rows[0]["reason"] == "ทดลองลดโควตาช่วงโหลดสูง"


def test_policy_record_skips_a_row_another_worker_already_wrote():
    from DATABASE.db import policy_record
    assert policy_record([("IMAGE_COST", "5", "9")], "ทดสอบ", 1.0) == 1
    assert policy_record([("IMAGE_COST", "5", "9")], "ทดสอบ", 2.0) == 0


def test_everyone_can_see_prices_and_their_history(client, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "IMAGE_FREE_DAILY", 2)
    monkeypatch.delenv("POLICY_CHANGE_REASON", raising=False)
    app_module._policy_sync()
    d = client.get("/api/policy").json()
    assert d["current"]["IMAGE_FREE_DAILY"] == 2
    top = d["history"][0]
    assert top["key"] == "IMAGE_FREE_DAILY" and top["new"] == "2" and top["no_reason"]
    assert all("price_" not in str(r) for r in d["history"])


def test_admin_sees_changes_without_a_reason(user, app_module, monkeypatch):
    monkeypatch.setattr(app_module, "_ADMIN_EMAILS", {user.email.lower()})
    monkeypatch.setattr(app_module, "IMAGE_PREMIUM_DAILY", 3)
    monkeypatch.delenv("POLICY_CHANGE_REASON", raising=False)
    app_module._policy_sync()
    p = user.get("/api/admin/metrics").json()["policy"]
    assert p["unexplained_changes"] >= 1 and p["latest_unexplained"][0]["key"] == "IMAGE_PREMIUM_DAILY"
