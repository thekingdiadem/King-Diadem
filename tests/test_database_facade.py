"""core/database.py ต้องใช้ฐานเดียวกับแอป — เปิดใช้เมื่อไหร่ข้อมูลก็ไม่แตกเป็นสองฐาน"""
import importlib


def test_core_database_points_to_app_db():
    from core import database
    from DATABASE import db
    assert database.db_path() == db.DB_PATH
    database.init_db()                       # เดิม: CREATE INDEX ON payments(email) ล้มบนฐานของแอป
    db.ensure_user("facade@test.local")
    db.add_credits("facade@test.local", 7, reason="test")
    row = database.get_db().execute("SELECT amount FROM credits WHERE user_email=?", ("facade@test.local",)).fetchone()
    assert row and row["amount"] == db.get_credits("facade@test.local")
    tables = {r[0] for r in database.get_db().execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert {"users", "credits", "payments", "sessions"} <= tables


def test_misspelled_module_renamed():
    assert importlib.import_module("ENGINE.decision").build_reply
    import ENGINE.brain  # noqa: F401  — import ชื่อใหม่ได้
