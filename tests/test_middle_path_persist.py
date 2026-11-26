"""ตัวเลขทางสายกลางต้องเก็บลงฐานข้อมูล ไม่หายตอน Render หลับหรือ deploy"""
import app
from core import middle_path


def _fresh(monkeypatch, tmp_path):
    import DATABASE.db as db
    monkeypatch.setattr(db, "DB_PATH", str(tmp_path / "kd.db"))
    db.init_db()
    app._mp_cache.update(at=0.0, v=None)


def test_counts_survive_memory_reset(monkeypatch, tmp_path):
    _fresh(monkeypatch, tmp_path)
    reply = "ไปเลย! สู้ๆ คุณทำได้แน่นอน"
    before = app._mp_mem()
    middle_path.balance("ฉันจะลาออกพรุ่งนี้แล้วเอาเงินเก็บทั้งหมดไปลงทุน", reply)
    app._mp_record(before, app._mp_mem())

    monkeypatch.setattr(middle_path, "_STATS", {"checked": 0, "upside": 0, "constraint": 0})  # เหมือนรีสตาร์ต
    s = app._middle_path_stats()
    assert s["source"] == "db"
    assert s["checked"] >= 1


def test_falls_back_to_memory_when_db_broken(monkeypatch):
    import DATABASE.db as db
    app._mp_cache.update(at=0.0, v=None)
    monkeypatch.setattr(db, "metric_report", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("down")))
    s = app._middle_path_stats()
    assert s is None or (s["source"] == "memory" and {"checked", "upside", "constraint"} <= set(s))


def test_record_only_counts_increases(monkeypatch):
    seen = []
    monkeypatch.setattr(app, "_metric", lambda name, *a, **k: seen.append(name))
    app._mp_record({"checked": 3, "upside": 1, "constraint": 0}, {"checked": 4, "upside": 2, "constraint": 0})
    assert seen == ["middle_path:checked", "middle_path:upside"]
