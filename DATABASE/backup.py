"""สำรองฐานข้อมูลอัตโนมัติ — บัญชี เครดิต ประวัติ 2FA อยู่ในไฟล์ SQLite ไฟล์เดียว
ถ้าไฟล์นั้นเสีย (เขียนค้างตอนเครื่องดับ, ดิสก์มีปัญหา, ลบผิด) จะได้มีสำเนาย้อนกลับไปได้

- ใช้ SQLite backup API: ได้สำเนาที่สมบูรณ์แม้ระหว่างนั้นมีคนเขียนอยู่ (ไม่ใช่ copy ไฟล์ดิบ)
- เขียนลงไฟล์ชั่วคราวก่อน ตรวจ PRAGMA integrity_check ผ่านแล้วค่อยเปลี่ยนชื่อ — ไม่มีสำเนาครึ่งๆ กลางๆ
- เก็บ 7 ชุดล่าสุด + ชุดสุดท้ายของแต่ละสัปดาห์ 5 สัปดาห์ล่าสุด (ย้อนได้ราว 1 เดือน กินดิสก์น้อย)
- ทำวันละครั้ง: ตอนเซิร์ฟเวอร์เริ่ม (ถ้าครั้งล่าสุดเกิน 20 ชม.) และมีเธรดเบาๆ ตรวจทุกชั่วโมง

ข้อจำกัด: สำเนาอยู่ดิสก์เดียวกับฐานข้อมูล (Render disk) — กันไฟล์เสียได้ แต่ถ้าดิสก์ทั้งก้อนหาย
สำเนาก็หายด้วย ควรดาวน์โหลดเก็บไว้นอกเครื่องเป็นครั้งคราว

กู้คืน (หยุดเซิร์ฟเวอร์ก่อน):
    python -m DATABASE.backup --list                 # ดูสำเนาที่มี
    cp /var/data/backups/kd-YYYYmmdd-HHMMSS.db /var/data/king_diadem.db
    rm -f /var/data/king_diadem.db-wal /var/data/king_diadem.db-shm
สำรองทันที:
    python -m DATABASE.backup
"""
import os
import sqlite3
import threading
import time
from datetime import datetime, timezone

KEEP_RECENT = 7
KEEP_WEEKLY = 5           # รวมสัปดาห์ปัจจุบัน → ย้อนได้ราว 1 เดือน
EVERY_SECONDS = 20 * 3600          # ห่างกันอย่างน้อย 20 ชม. (เผื่อเวลารีสตาร์ทคลาดเคลื่อน = วันละครั้ง)
PREFIX, SUFFIX = "kd-", ".db"


def _db_path():
    from DATABASE.db import DB_PATH
    return DB_PATH


def backup_dir(db_path=None):
    return os.path.join(os.path.dirname(os.path.abspath(db_path or _db_path())), "backups")


def list_backups(db_path=None):
    d = backup_dir(db_path)
    if not os.path.isdir(d):
        return []
    names = sorted(n for n in os.listdir(d) if n.startswith(PREFIX) and n.endswith(SUFFIX))
    return [os.path.join(d, n) for n in names]


def last_backup_age(db_path=None, now=None):
    """วินาทีนับจากสำรองล่าสุด (None = ยังไม่เคยสำรอง)"""
    b = list_backups(db_path)
    if not b:
        return None
    return max(0.0, (now or time.time()) - os.path.getmtime(b[-1]))


def backup_now(db_path=None, now=None):
    """สำรองทันที คืน path ของสำเนา (หรือ None ถ้ายังไม่มีฐานข้อมูล) · ตรวจไม่ผ่าน = ยกข้อผิดพลาด ไม่ทิ้งไฟล์เสียไว้"""
    src_path = db_path or _db_path()
    if not os.path.exists(src_path):
        return None
    d = backup_dir(src_path)
    os.makedirs(d, exist_ok=True)
    stamp = datetime.fromtimestamp(now or time.time(), tz=timezone.utc).strftime("%Y%m%d-%H%M%S")
    final = os.path.join(d, f"{PREFIX}{stamp}{SUFFIX}")
    tmp = final + ".tmp"
    src = sqlite3.connect(src_path, timeout=15)
    try:
        dst = sqlite3.connect(tmp)
        try:
            src.backup(dst)
            ok = dst.execute("PRAGMA integrity_check").fetchone()[0]
        finally:
            dst.close()
    finally:
        src.close()
    if ok != "ok":
        os.remove(tmp)
        raise RuntimeError(f"backup integrity_check failed: {ok}")
    os.replace(tmp, final)
    if now:
        os.utime(final, (now, now))
    prune(src_path)
    return final


def prune(db_path=None):
    """เก็บ 7 ชุดล่าสุด + ชุดสุดท้ายของแต่ละสัปดาห์ (ISO week) 5 สัปดาห์ล่าสุด · ลบไฟล์ .tmp ที่ค้างจากรอบที่ล้ม"""
    files = list_backups(db_path)
    keep = set(files[-KEEP_RECENT:])
    weeks = {}
    for f in files:
        stamp = os.path.basename(f)[len(PREFIX):-len(SUFFIX)]
        try:
            wk = datetime.strptime(stamp, "%Y%m%d-%H%M%S").isocalendar()[:2]
        except ValueError:
            continue
        weeks[wk] = f                      # ไฟล์เรียงตามเวลา — ตัวท้ายของสัปดาห์ชนะ
    for wk in sorted(weeks)[-KEEP_WEEKLY:]:
        keep.add(weeks[wk])
    for f in files:
        if f not in keep:
            os.remove(f)
    d = backup_dir(db_path)
    for n in os.listdir(d):
        if n.endswith(".tmp"):
            os.remove(os.path.join(d, n))


def backup_if_due(db_path=None, now=None):
    age = last_backup_age(db_path, now)
    if age is None or age >= EVERY_SECONDS:
        return backup_now(db_path, now)
    return None


_started = False


def start_scheduler(interval=3600):
    """เธรดเบาๆ ตรวจทุกชั่วโมงว่าถึงเวลาสำรองหรือยัง · error ไม่ทำให้แอปล้ม (แค่พิมพ์บอก)"""
    global _started
    if _started:
        return
    _started = True

    def loop():
        while True:
            try:
                p = backup_if_due()
                if p:
                    print(f"✅ DB backup: {os.path.basename(p)}")
            except Exception as e:      # noqa: BLE001 — สำรองล้มต้องไม่ทำให้เว็บล้ม
                print(f"⚠ DB backup: {e}")
            time.sleep(interval)

    threading.Thread(target=loop, name="kd-db-backup", daemon=True).start()


if __name__ == "__main__":
    import sys
    if "--list" in sys.argv:
        for f in list_backups():
            print(f, f"{os.path.getsize(f) / 1024:.0f} KB")
    else:
        print(backup_now() or "ยังไม่มีฐานข้อมูล")
