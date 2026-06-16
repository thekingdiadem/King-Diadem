"""
AI/choice_points.py — KING DIADEM
Point system: ติดตาม choice credits ของแต่ละ user
ไม่ใช้ global dict เดี่ยว — รองรับ multi-user
"""
import json, os, threading

_STORE_PATH = "data/choice_points.json"
_lock = threading.Lock()


def _load() -> dict:
    try:
        if os.path.exists(_STORE_PATH):
            with open(_STORE_PATH, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}


def _save(db: dict):
    os.makedirs("data", exist_ok=True)
    with open(_STORE_PATH, "w") as f:
        json.dump(db, f, indent=2)


def add_points(user: str, amount: float) -> float:
    """เพิ่ม points ให้ user — คืนยอดใหม่"""
    with _lock:
        db = _load()
        db[user] = round(db.get(user, 0.0) + amount, 4)
        _save(db)
        return db[user]


def deduct_points(user: str, amount: float) -> tuple[bool, float]:
    """หัก points — คืน (success, remaining)"""
    with _lock:
        db = _load()
        current = db.get(user, 0.0)
        if current < amount:
            return False, current
        db[user] = round(current - amount, 4)
        _save(db)
        return True, db[user]


def get_points(user: str) -> float:
    """ดูยอด points ปัจจุบัน"""
    return _load().get(user, 0.0)


def reset_points(user: str) -> float:
    """รีเซ็ต points เป็น 0"""
    with _lock:
        db = _load()
        db[user] = 0.0
        _save(db)
        return 0.0


def get_all_points() -> dict:
    """ดู leaderboard ทั้งหมด"""
    return _load()
