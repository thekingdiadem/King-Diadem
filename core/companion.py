"""สัญญาณการพึ่งพา — FATE™ Ethical Kernel ข้อ 5 "รู้ทันการพึ่งพา (Dependency Awareness)"

ถ้าคนคนเดียวคุยเรื่องหนักใจเรื่องเดิมถี่ผิดปกติ LYLA ช่วยได้ แต่ไม่ควรเป็นที่พึ่งเดียว
ระบบจึงชวนให้มีคนจริงอยู่ข้างๆ ด้วย — วันละครั้ง ไม่บังคับ ไม่ปิดการคุย

เก็บอะไร: แค่ (วัน, รหัสผู้ใช้แบบ HMAC, หัวข้อ, จำนวนครั้ง) — ไม่เก็บข้อความ · เก็บ 14 วันแล้วลบ
ตัดสินยังไง: กฎตายตัว ค่าเดิมได้ผลเดิมเสมอ (ไม่ใช้ AI)
  · หัวข้อเดิมโผล่ ≥ DAYS_MIN วัน ใน WINDOW_DAYS วันล่าสุด  → "days"
  · หรือหัวข้อเดิม ≥ BURST_MIN ครั้งในวันนี้                   → "burst"
ข้อความวิกฤตไม่นับ — มีเบอร์สายด่วนในคำตอบอยู่แล้ว
"""
from __future__ import annotations

# หัวข้อที่คนมักกลับมาคุยซ้ำเพราะหนักใจ (ชื่อจาก core/kernel_voice.TOPICS)
HEAVY = frozenset({"lonely", "stress", "grief", "relationship", "family", "panic", "sleepless",
                   "addiction", "caregiver", "bullying", "eating", "friendship"})
# หัวข้อที่ควรมีสายด่วนสุขภาพจิตให้ด้วย
_MIND = frozenset({"lonely", "stress", "grief", "panic", "sleepless", "eating", "addiction"})

WINDOW_DAYS = 7
DAYS_MIN = 4
BURST_MIN = 10
KEEP_DAYS = 14
SHOWN = "_shown"            # แถวพิเศษ: วันนี้ชวนไปแล้ว


def heavy_topics(topics) -> list[str]:
    return sorted(set(topics or ()) & HEAVY)


def signal(history: dict, today: str) -> dict | None:
    """history = {day: {topic: n}} ของคนนี้ (WINDOW_DAYS วันล่าสุด รวมวันนี้) → {topic, kind} หรือ None"""
    if (history.get(today) or {}).get(SHOWN):
        return None                                       # วันนี้ชวนไปแล้ว
    days, burst = {}, {}
    for day, counts in history.items():
        for topic, n in (counts or {}).items():
            if topic in HEAVY and n > 0:
                days[topic] = days.get(topic, 0) + 1
                if day == today:
                    burst[topic] = n
    hit = [(t, "burst") for t, n in burst.items() if n >= BURST_MIN] + [(t, "days") for t, d in days.items() if d >= DAYS_MIN]
    if not hit:
        return None
    topic, kind = sorted(hit, key=lambda x: (x[1] != "days", -days.get(x[0], 0), x[0]))[0]
    return {"topic": topic, "kind": kind, "days": days.get(topic, 0)}


def message(sig: dict) -> dict:
    """ข้อความชวนแบบอ่อนโยน (ไทย/อังกฤษ) — ไม่ตำหนิ ไม่ปิดทาง"""
    if sig["kind"] == "days":
        th = f"เราคุยเรื่องนี้กันมา {sig['days']} วันแล้วในสัปดาห์นี้ — LYLA ยังอยู่ตรงนี้เสมอ "
        en = f"We've talked about this on {sig['days']} days this week — LYLA is still here. "
    else:
        th = "วันนี้เราคุยเรื่องนี้กันหลายรอบแล้ว — LYLA ยังอยู่ตรงนี้เสมอ "
        en = "We've come back to this many times today — LYLA is still here. "
    th += "แต่เรื่องที่หนักใจซ้ำๆ มักเบาลงเมื่อมีคนจริงช่วยแบกด้วย ลองเล่าให้คนที่ไว้ใจฟังสักคนไหม"
    en += "But things that keep weighing on us often get lighter with a real person beside us. Is there someone you trust you could tell?"
    if sig["topic"] in _MIND:
        th += " · อยากคุยกับผู้เชี่ยวชาญ โทร 1323 (สายด่วนสุขภาพจิต ฟรี 24 ชม.)"
        en += " · To talk with a professional in Thailand, call 1323 (free, 24h mental health line)."
    return {"th": th, "en": en, "topic": sig["topic"]}
