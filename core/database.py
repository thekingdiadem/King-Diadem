"""
core/database.py — KING DIADEM
ทางเข้าฐานข้อมูลแบบเก่า (get_db / init_db) — ตอนนี้ชี้ไปที่ฐานเดียวกับแอป (DATABASE/db.py)

เดิมไฟล์นี้เปิด king_diadem.db ของตัวเอง (DB_FILE ที่ root) และมีตาราง users/payments
คนละโครงกับของแอป ถ้าวันหนึ่งมีโค้ดเรียกใช้ ข้อมูลจะแตกเป็นสองฐาน — และถ้าชี้มาที่ฐานเดียวกัน
CREATE INDEX ... ON payments(email) จะล้มเพราะตารางของแอปใช้คอลัมน์ user_email

ตอนนี้: ที่อยู่ไฟล์ · pragma · โครงตาราง มาจาก DATABASE/db.py ที่เดียว
เปิดใช้เมื่อไหร่ก็ได้ข้อมูลชุดเดียวกับแอปโดยไม่ต้องแก้อะไร
"""
import sqlite3
import threading

from DATABASE import db as _app_db

_local = threading.local()


def db_path() -> str:
    """ไฟล์ฐานข้อมูลที่ใช้จริง — ตัวเดียวกับแอป (DB_PATH)"""
    return _app_db.DB_PATH


def get_db() -> sqlite3.Connection:
    """connection ต่อ thread ไปยังฐานเดียวกับแอป (WAL · busy_timeout · row_factory แบบเดียวกัน)"""
    conn = getattr(_local, "conn", None)
    if conn is None or getattr(_local, "path", None) != _app_db.DB_PATH:
        conn = _app_db.get_conn()
        _local.conn, _local.path = conn, _app_db.DB_PATH
    return conn


def init_db():
    """สร้างตารางของแอป (idempotent) + ตาราง sessions ที่ไฟล์นี้เคยมีและแอปยังไม่มี"""
    _app_db.init_db()
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS sessions (
        id          TEXT PRIMARY KEY,
        email       TEXT,
        title       TEXT,
        created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
        updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.commit()
