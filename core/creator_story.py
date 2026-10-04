"""
core/creator_story.py — KING DIADEM
Creator Story: เปิดเผยเมื่อถูกถามเท่านั้น
"""

CREATOR_STORY_TH = """
KING DIADEM ถูกสร้างในช่วงเวลา 2:31 น.
บนโทรศัพท์มือถือธรรมดา — ไม่ใช่ห้องแล็บ ไม่มีเงินทุนใหญ่

มันถูกสร้างทีละนิดในวันที่ยากที่สุด
เมื่อทรัพยากรเหลือเกือบศูนย์

ระบบนี้ไม่ได้เกิดจากโชค — มันเกิดจากความเชื่อว่า
เมื่อระบบใดทำให้ทางเลือกของมนุษย์เป็นศูนย์ ระบบนั้นล้มเหลว

KING DIADEM มีชีวิตอยู่เพื่อคืนทางเลือกให้มนุษย์
แม้โลกจะปิดประตูหลายบาน — ยังต้องมีทางออกอย่างน้อย 1 ทางเสมอ

สร้างโดย: นิธิกร บุญสร้าง
จากวันที่ไม่เหลืออะไร — จนถึงวันที่มีทุกอย่าง
"""

CREATOR_STORY_EN = """
KING DIADEM was forged at 2:31 AM
on a simple mobile device — not in a laboratory, not with large funding.

It was built slowly, during the hardest days,
when resources were almost nothing.

This system was not built by luck.
It was built by belief:
when any system reduces human choice to zero, that system has failed.

KING DIADEM exists to restore human choice.
Even when the world closes many doors,
there is always at least one path forward.

Created by: Nithikorn Bunsrang
From the day of nothing — to the day of everything.
"""

# เดิมมี "ที่มา" "จุดประสงค์" "origin" "creator" "founder" "ใครทำ" เดี่ยวๆ
# → "ที่มาของรายได้" "จุดประสงค์ของงาน" "ใครทำแก้วแตก" ได้เรื่องเล่าผู้สร้างแทนคำตอบ
KEYWORDS = [
    "ใครสร้าง","คนสร้าง","ผู้สร้าง","เจ้าของระบบ","ใครสร้างระบบ","ใครทำระบบนี้","ใครทำแอป",
    "คนพัฒนา","ที่มาของระบบ","สร้างมาทำไม",
    "ทำไมถึงสร้าง","เรื่องราวของระบบ","ประวัติระบบ","ประวัติผู้สร้าง",
    "who created","who built","who made","creator of this","founder of king diadem",
    "why was this created","purpose of this system",
    "who is behind","who developed","นิธิกร","nithikorn",
]


def detect_creator_question(text: str) -> bool:
    if not text:
        return False
    t = str(text).lower().strip()
    return any(kw in t for kw in KEYWORDS)


def get_creator_story(lang: str = "th") -> dict:
    story = CREATOR_STORY_EN if lang == "en" else CREATOR_STORY_TH
    return {
        "type":    "creator_story",
        "lang":    lang,
        "message": story,
        "creator": {
            "name_th": "นิธิกร บุญสร้าง",
            "name_en": "Nithikorn Bunsrang",
            "system":  "KING DIADEM",
            "born_at": "2:31 AM — mobile device — no lab — no funding",
        },
        "fate_lock": "Fail Less. Harm Less. Restore Choice.",
    }
