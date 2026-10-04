"""
AI/choice_points.py — KING DIADEM
Point system: ติดตาม choice credits ของแต่ละ user
ไม่ใช้ global dict เดี่ยว — รองรับ multi-user
"""
import json, math, os, tempfile, threading

from core.paths import data_path

_STORE_PATH = data_path("choice_points.json")   # ข้าง DB_PATH (ดิสก์ถาวร) — ดู core/paths.py
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
    # เขียนไฟล์ชั่วคราวแล้ว os.replace — เดิมเปิด "w" ทับตรง: ล่มกลางทางยอดทุกคนหาย
    d = os.path.dirname(_STORE_PATH) or "."
    os.makedirs(d, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(db, f, indent=2)
        os.replace(tmp, _STORE_PATH)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _amount(v) -> float:
    """จำนวนต้องเป็นบวกและ finite — เดิม add(-100) หักแต้ม, deduct(-100) เพิ่มแต้มได้"""
    try:
        x = float(v)
    except (TypeError, ValueError):
        return 0.0
    return x if math.isfinite(x) and x > 0 else 0.0


def add_points(user: str, amount: float) -> float:
    """เพิ่ม points ให้ user — คืนยอดใหม่"""
    amount = _amount(amount)
    user = str(user)
    with _lock:
        db = _load()
        db[user] = round(db.get(user, 0.0) + amount, 4)
        _save(db)
        return db[user]


def deduct_points(user: str, amount: float) -> tuple[bool, float]:
    """หัก points — คืน (success, remaining)"""
    amount = _amount(amount)
    user = str(user)
    if amount <= 0:
        return False, get_points(user)
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
    """ดู leaderboard ทั้งหมด — ปิดบังอีเมล (เดิมคืน key เป็นอีเมลของทุกคน)"""
    out = {}
    for k, v in _load().items():
        name, at, dom = str(k).partition("@")
        out[(name[:2] + "***" + at + dom) if at else (str(k)[:2] + "***")] = v
    return out
