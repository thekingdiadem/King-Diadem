"""
core/paths.py — ที่เก็บไฟล์ข้อมูล (JSON/JSONL) ของทุกโมดูล

เดิมแต่ละโมดูลเขียนลง "data/..." แบบ relative = โฟลเดอร์โค้ด
บน Render โฟลเดอร์โค้ดถูกสร้างใหม่ทุก deploy → ข้อมูลหายทุกครั้ง
ดิสก์ถาวรคือโฟลเดอร์ของ DB_PATH (render.yaml: /var/data/king_diadem.db)

ลำดับ: KD_DATA_DIR → โฟลเดอร์ของ DB_PATH → "data"
"""
import os


def data_dir() -> str:
    d = os.getenv("KD_DATA_DIR") or os.path.dirname(os.getenv("DB_PATH", "")) or "data"
    return d


def data_path(name: str) -> str:
    return os.path.join(data_dir(), name)
