"""ประโยคที่ทำให้คำตอบ "ได้ใจ" — ตอบสิ่งที่ผู้ใช้รู้สึก ไม่ใช่แค่ขั้นตอน

หลักของ KING DIADEM: "บางครั้งเราไม่ได้ต้องการคำตอบที่สมบูรณ์แบบ เราแค่ต้องการรู้ว่าเรายังมีทางเลือกอยู่ในคำตอบนั้นหรือเปล่า"
ไฟล์นี้เติมประโยคหนึ่งบรรทัดหลังประโยคเปิด เมื่อผู้ใช้เล่าความรู้สึกที่ขั้นตอนอย่างเดียวตอบไม่ถึง
· โดนหลอกแล้วโทษตัวเองว่าโง่ → บอกว่าแก๊งเก่งเรื่องโกหก ไม่ใช่เขาโง่
· เสียเงินก้อนใหญ่จนหมดตัว → เงินหายได้ แต่ยังมีทางเลือก + 1323 เผื่อใจไม่ไหว
· ถูกทำร้ายแต่ "ไม่มีที่ไป" (มีลูก) → มีที่พักฉุกเฉินแม่ลูก ไม่ต้องมีเงินก่อน
· ถูกทำร้าย "อีกแล้ว" → การยังอยู่ไม่ใช่ความผิดของเขา วางแผนออกเมื่อพร้อมได้
ไม่แตะคำตอบวิกฤต (มีบทของมันเอง) และเติมได้อย่างมากสองบรรทัด
"""
import re

_SHAME_TH = re.compile(r"รู้สึก(?:ตัวเอง)?โง่|โง่มาก|โง่จัง|โง่ที่|อายมาก|อายจน|ไม่กล้าบอก(?:ใคร|ที่บ้าน|ครอบครัว|แฟน)|โทษตัวเอง")
_SHAME_EN = re.compile(r"(?i)\b(?:feel|felt|am|i'?m)\s+(?:so\s+|really\s+|such\s+an?\s+)?(?:stupid|dumb|idiot|ashamed|embarrassed)\b|\bblame\s+myself\b")
_BIG_LOSS_TH = re.compile(r"หมดตัว|ไปหมด(?:แล้ว)?|เงินเก็บ(?:ทั้งหมด|ทั้งชีวิต)|ทั้งชีวิต|หลายแสน|\d\s?แสน|ล้านบาท|\d\s?ล้าน|เงินเกษียณ")
_BIG_LOSS_EN = re.compile(r"(?i)\b(?:all\s+(?:of\s+)?my|my\s+(?:life|entire|whole))\s+(?:savings|money|retirement)\b|\bout\s+of\s+my\s+savings\b|\blost\s+everything\b")
_NOWHERE_TH = re.compile(r"ไม่มีที่ไป|ไม่รู้จะไปไหน|ไปไหนไม่ได้|ไม่มีที่พัก|ไม่มีที่อยู่")
_NOWHERE_EN = re.compile(r"(?i)\b(?:nowhere\s+(?:else\s+)?to\s+go|no\s+place\s+to\s+go|can'?t\s+afford\s+to\s+leave)\b")
_AGAIN_TH = re.compile(r"อีกแล้ว|อีกครั้ง|ทุกครั้งที่|เป็นประจำ|หลายครั้งแล้ว|ซ้ำๆ")
_AGAIN_EN = re.compile(r"(?i)\b(?:again|every\s+time|keeps?\s+(?:hitting|hurting|beating))\b")

_HIDE_TH = re.compile(r"ไม่กล้าบอก|ไม่กล้าออกจากบ้าน|อายจน|อายมาก|ปิดบัง|โกหกที่บ้าน|ทำเป็นออกไปทำงาน")
_HIDE_EN = re.compile(r"(?i)\b(?:ashamed|embarrassed|afraid)\s+to\s+tell\b|\bhaven'?t\s+told\b|\bhiding\s+it\b|\bpretend(?:ing)?\s+to\s+go\s+to\s+work\b")
_GUILT_TH = re.compile(r"ไม่ได้อยู่ข้าง|ไม่ทันได้|ไม่ได้ร่ำลา|ไม่ได้บอกลา|รู้สึกผิด|โทษตัวเอง|น่าจะทำ\S{0,8}มากกว่านี้")
_GUILT_EN = re.compile(r"(?i)\bwasn'?t\s+there\b|\bdidn'?t\s+(?:get\s+to\s+)?say\s+goodbye\b|\bguilt|\bblame\s+myself\b|\bshould\s+have\b")

LINES = {
    "shame": ("แก๊งพวกนี้ใช้บทพูดที่ฝึกมาเป็นทีม หลอกได้ทั้งหมอ ครู และพนักงานธนาคาร — การโดนหลอกไม่ได้แปลว่าคุณโง่ แต่แปลว่าเขาเก่งเรื่องโกหก",
              "These groups work from rehearsed scripts and fool doctors, teachers and bank staff too — being scammed doesn't mean you're stupid; it means they are skilled liars."),
    "loss": ("เงินที่หายไปหนักมากจริงๆ แต่คุณยังมีทางเลือกอยู่ — ถ้าความรู้สึกหนักจนไม่อยากอยู่ต่อ โทร 1323 ได้ตลอด 24 ชม.",
             "Losing this much is crushing, but you still have choices — if it ever feels too heavy to go on, a crisis line is there 24h (1323 in Thailand, 988 in the US)."),
    "nowhere": ("ไม่มีที่ไปไม่ได้แปลว่าไม่มีทางเลือก — โทร 1300 ขอที่พักฉุกเฉินได้ทั้งแม่และลูก (บ้านพักเด็กและครอบครัวมีทุกจังหวัด) ไม่ต้องมีเงินก่อน",
                "Having nowhere to go doesn't mean having no options — shelters take parents with children, often at no cost (in Thailand call 1300; elsewhere a local domestic-violence hotline)."),
    "hide": ("ความอายทำให้เราอยากเก็บไว้คนเดียว แต่ปัญหาเงินหรืองานไม่ได้วัดค่าของคน — เลือกบอกแค่คนเดียวที่ไว้ใจก่อนก็ได้ ภาระจะเบาลงครึ่งหนึ่ง",
             "Shame makes us want to carry this alone, but money or work trouble doesn't measure your worth — you could tell just one person you trust first; the weight halves when it's shared."),
    "guilt": ("ความรู้สึกผิดแบบนี้มักมาจากความรักที่ยังอยากทำให้เขาอีก — การไม่ได้อยู่ตรงนั้นในวินาทีสุดท้าย ไม่ได้ลบทุกวันที่คุณรักเขามา",
              "Guilt like this usually comes from love that still wants to do more for them — not being there at the very end doesn't erase all the days you loved them."),
    "again": ("การที่ยังอยู่หรือเคยกลับไป ไม่ใช่ความผิดของคุณ — คุณออกได้เมื่อพร้อม และวางแผนเงียบๆ ไว้ก่อนได้ เช่น เก็บบัตรประชาชน เงินเล็กน้อย และเบอร์สำคัญไว้ที่คนที่ไว้ใจ",
              "Staying, or going back before, is not your fault — you can leave when you're ready, and quietly plan ahead: keep ID, a little money and key numbers with someone you trust."),
}


def lines_for(text: str, a: dict) -> list:
    """คืนประโยคที่ควรเติม (ภาษาเดียวกับคำตอบ) — ว่างถ้าไม่มีอะไรต้องเติม"""
    if not isinstance(text, str) or a.get("crisis"):
        return []
    topics = a.get("topics") or []
    en = not re.search(r"[฀-๿]", text)
    pick = []
    if "scam" in topics or "sextortion" in topics:
        if (_SHAME_EN if en else _SHAME_TH).search(text):
            pick.append("shame")
        if (_BIG_LOSS_EN if en else _BIG_LOSS_TH).search(text):
            pick.append("loss")
    if "violence" in topics or "control_en" in topics:
        if (_NOWHERE_EN if en else _NOWHERE_TH).search(text):
            pick.append("nowhere")
        if (_AGAIN_EN if en else _AGAIN_TH).search(text):
            pick.append("again")
    if ("debt" in topics or "job" in topics or "labor" in topics) and (_HIDE_EN if en else _HIDE_TH).search(text):
        pick.append("hide")
    if "grief" in topics and (_GUILT_EN if en else _GUILT_TH).search(text):
        pick.append("guilt")
    return [LINES[k][1 if en else 0] for k in pick[:2]]


def add(reply: str, text: str, a: dict) -> str:
    extra = lines_for(text, a)
    if not extra or not isinstance(reply, str):
        return reply
    head, sep, rest = reply.partition("\n\n")
    if not sep:
        return reply
    return head + "\n\n" + "\n".join(extra) + "\n\n" + rest
