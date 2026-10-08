# DATABASE/init_db.py
# KING DIADEM — DB Initializer
# thin wrapper — logic จริงอยู่ใน db.py ทั้งหมด
# ไม่ duplicate schema ที่นี่

from __future__ import annotations


def init_db() -> bool:
    """
    Initialize ทุก table ที่ระบบต้องการ
    เรียกครั้งเดียวตอน app.py startup
    Return True ถ้าสำเร็จ
    """
    try:
        from DATABASE.db import init_db as _init
        if _init:
            _init()
        return True
    except Exception as e:
        print(f"⚠ init_db: {e}")
        return False


def ensure_all_tables() -> dict:
    """
    ตรวจและสร้างทุก table — return status ของแต่ละ table
    """
    status = {}

    # ── users ──────────────────────────────────────────────────
    try:
        from DATABASE.db import get_conn
        conn = get_conn()
        tables = [r[0] for r in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()]
        conn.close()
        status["tables_found"] = tables
    except Exception as e:
        status["db_error"] = str(e)
        return status

    # ── credit_store ─────────────────────────────────────────
    try:
        from DATABASE.credit_store import _ensure_table as _ct
        _ct()
        status["credit_store"] = "ok"
    except Exception as e:
        status["credit_store"] = f"error: {e}"

    # ── decision_history ──────────────────────────────────────
    try:
        from DATABASE.decision_history import _ensure_table as _dh
        _dh()
        status["decision_history"] = "ok"
    except Exception as e:
        status["decision_history"] = f"error: {e}"

    status["ready"] = all(
        v == "ok" for k, v in status.items()
        if k not in ("tables_found",)
    )
    return status


if __name__ == "__main__":
    result = ensure_all_tables()
    print("DB init result:", result)

