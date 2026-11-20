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

_RESENT_TH = re.compile(r"โกรธ(?:แม่|พ่อ|ยาย|ตา|เขา|สามี|ภรรยา|ลูก)|หงุดหงิดใส่|รำคาญ(?:แม่|พ่อ|เขา)|อยากให้มันจบ|เกลียดตัวเองที่")
_RESENT_EN = re.compile(r"(?i)\b(?:resent|angry\s+at|snap(?:ped)?\s+at|hate\s+myself\s+for|wish\s+it\s+(?:was|were)\s+over)\b")
_WORTHLESS_TH = re.compile(r"ไม่มีค่า|ไร้ค่า|ไม่เอาไหน|ไม่ได้เรื่อง|ไม่ดีพอ|ห่วยแตก|มันโง่|ล้มเหลว(?:ทั้งชีวิต)?")
_WORTHLESS_EN = re.compile(r"(?i)\b(?:worthless|not\s+good\s+enough|a\s+failure|useless|unlovable)\b")

# แบบที่ 1 — พ่อแม่ที่ทั้งรักและทำร้าย (Understanding ≠ Justification · One Person Can Contain Both)
_PARENT = r"(?:พ่อ(?!ค้า)|แม่(?!น้ำ|ค้า)|พ่อเลี้ยง|แม่เลี้ยง)"
_HARM_TH = r"(?:ด่า|ตี(?!กลอง|ลูก|เทนนิส|แบด|ปิงปอง|ไข่|ตั๋ว|พิมพ์|ราคา|ความ|โจทย์|กอล์ฟ)|ทำร้าย|กินเหล้า|ติดเหล้า|เมา|ตะคอก|ทุบ|ดูถูก|ประชด|ไล่ออกจากบ้าน|ไม่สนใจ|ทิ้ง)"
_CARE_TH = r"(?:รัก|ดูแล|ทำงานหนัก|เหนื่อย|ไม่อยากให้\S{0,6}ลำบาก|เลี้ยง|ส่งเสีย|เคยดี|เสียสละ|ห่วง)"
_BOTH_TH = re.compile(_PARENT + r"[^\n]{0,40}?" + _HARM_TH + r"[^\n]{0,60}?(?:แต่|ทั้งที่)[^\n]{0,40}?" + _CARE_TH
                      + r"|(?=[^\n]*" + _PARENT + r")" + _CARE_TH + r"[^\n]{0,40}?(?:แต่)[^\n]{0,40}?" + _HARM_TH
                      + r"|" + _PARENT + r"[^\n]{0,30}?" + _CARE_TH + r"[^\n]{0,40}?(?:แต่)[^\n]{0,40}?" + _HARM_TH
                      + r"|ไม่รู้จะรักหรือเกลียด|ทั้งรักทั้งเกลียด|รักก็รัก\S{0,4}เกลียดก็เกลียด")
_P_EN = r"(?:dad|father|mom|mum|mother|stepdad|stepmom|parents?)"
_HARM_EN = r"(?:drinks|yells|hits|hurts|screams|beats|insults|belittles|shouts|scream|yell|hit)"
_BOTH_EN = re.compile(r"(?i)\b(?:my\s+)?" + _P_EN + r"\b[^\n]{0,40}?\b" + _HARM_EN + r"\b[^\n]{0,60}?\bbut\b[^\n]{0,40}?\b(?:loves?|works?\s+(?:so\s+)?hard|cares?|provides?|tries|raised)\b"
                      r"|\blove\s+my\s+" + _P_EN + r"\b[^\n]{0,20}?\bbut\b[^\n]{0,40}?\b" + _HARM_EN + r"\b"
                      r"|\b(?:love|hate)\s+(?:and|or)\s+(?:hate|love)\s+(?:him|her|them)\b|\bdon'?t\s+know\s+(?:whether|if)\s+(?:i|to)\s+(?:love|hate)\b")
# การนอกใจ — ให้มองสิ่งที่ยังเหลืออยู่ · แต่ละบ้านพูดไม่เหมือนกัน (นอกใจ มีชู้ มีกิ๊ก เมียน้อย บ้านเล็ก แอบคุย)
_AFFAIR_TH = r"(?:นอกใจ|มีชู้|มีกิ๊ก|มีคนอื่น|มีคนใหม่|มีเมียน้อย|มีผัวใหม่|มีเมียใหม่|มีบ้านเล็ก|แอบคุยกับ|แอบมี(?:ครอบครัว|แฟน|คน)ใหม่|มีครอบครัวใหม่|แอบไปมีอะไร)"
_CHEATED_ME_TH = re.compile(r"(?:แฟน|สามี|ภรรยา|ผัว|เมีย)\S{0,6}" + _AFFAIR_TH)
_CHEATED_ME_EN = re.compile(r"(?i)\b(?:my\s+)?(?:husband|wife|boyfriend|girlfriend|partner|fianc[ée]e?)\s+(?:cheated|has\s+been\s+cheating|is\s+cheating|had\s+an\s+affair|is\s+having\s+an\s+affair|is\s+(?:sleeping\s+with|seeing)\s+someone\s+else)\b")
_PARENT_CHEAT_TH = re.compile(_PARENT + r"\S{0,6}" + _AFFAIR_TH)
_PARENT_CHEAT_EN = re.compile(r"(?i)\bmy\s+(?:dad|father|mom|mother)\s+(?:is\s+)?(?:cheat(?:ing|ed)|having\s+an\s+affair|had\s+an\s+affair)\b|\bcaught\s+my\s+(?:dad|father|mom|mother)\s+(?:texting|with|kissing|sleeping\s+with)\s+(?:another|some|a)\s+(?:woman|man|guy|girl|lady)\b")

# แบบที่ 4 — พ่อหรือแม่เลิกกันแล้วไปมีครอบครัวใหม่ตอนลูกยังเล็ก · โตมาถูกเปรียบเทียบกับลูกบ้านใหม่หรือลูกญาติ
_SPLIT_TH = r"(?:เลิกกัน|หย่า|แยกทาง|ทิ้ง(?:แม่|พ่อ|เรา|หนู|ผม|ไป)|ตอนเรา\S{0,6}เล็ก|ตั้งแต่\S{0,6}เด็ก|ตอนเด็ก)"
_LEFT_TH = re.compile(_PARENT + r"[^\n]{0,40}?(?:" + _SPLIT_TH + r")[^\n]{0,40}?(?:แฟนใหม่|ครอบครัวใหม่|เมียใหม่|ผัวใหม่|ลูกใหม่|บ้านใหม่)"
                      r"|" + _PARENT + r"\S{0,8}(?:ไป)?(?:มี)?(?:แฟนใหม่|ครอบครัวใหม่|เมียใหม่|ผัวใหม่)[^\n]{0,40}?" + _SPLIT_TH)
_LEFT_EN = re.compile(r"(?i)\bmy\s+(?:dad|father|mom|mother)\s+(?:left|walked\s+out|abandoned\s+us)\b[^\n]{0,60}?\b(?:new\s+(?:family|wife|husband|girlfriend|boyfriend|partner|kids))\b"
                      r"|\bmy\s+(?:dad|father|mom|mother)\s+(?:has|started)\s+a\s+new\s+family\b")
_COMPARE_TH = re.compile(r"(?:เปรียบเทียบ|เปรียบ)\S{0,4}(?:หนู|เรา|ผม|ฉัน|ลูก)|เปรียบเทียบ\S{0,6}กับ(?:พี่|น้อง|ลูก|ญาติ|เพื่อน|คนอื่น|หลาน)|เอา\S{0,8}ไปเทียบ|เทียบ(?:กับ|หนู|เรา|ผม)|ไม่เหมือนลูก\S{0,10}|ลูก(?:บ้าน|คน)(?:นั้น|อื่น|ใหม่)\S{0,10}(?:ได้ดี|รวย|เก่ง|เรียนเก่ง|ทำงานดี)"
                         r"|(?:ญาติ|ป้า|น้า|อา|ลุง|คนแถวบ้าน)\S{0,10}(?:ชอบ)?(?:พูด|ถาม|บอก|ว่า)[^\n]{0,20}?(?:รวย|ได้ดี|เก่งกว่า|ดีกว่า|เงินเดือน|ทำงานอะไร)")
_COMPARE_EN = re.compile(r"(?i)\b(?:compar(?:e|es|ed|ing)\s+(?:me|us)|always\s+compared|why\s+can'?t\s+you\s+be\s+(?:more\s+)?like)\b|\b(?:half[-\s]?(?:brother|sister|siblings?)|cousins?|(?:his|her)\s+(?:new\s+)?(?:kids|children|son|daughter))\b[^\n]{0,30}?\b(?:richer|more\s+successful|doing\s+better|better\s+than\s+me)\b")

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
    "resent": ("การโกรธหรือเหนื่อยใส่คนที่เราดูแล ไม่ได้แปลว่าคุณรักเขาน้อยลง — มันคือสัญญาณว่าคุณแบกมานานเกินคนคนเดียวจะแบกไหว",
               "Feeling anger or resentment toward the person you care for doesn't mean you love them less — it's a sign you've carried this longer than one person can."),
    "worth_love": ("ความรักที่จบลงไม่ได้วัดค่าของคุณ — มันบอกแค่ว่าความสัมพันธ์นี้ไปต่อไม่ได้ ไม่ได้บอกว่าคุณไม่ควรค่ากับการถูกรัก",
                   "A relationship ending doesn't measure your worth — it says this relationship couldn't continue, not that you aren't worth loving."),
    "worth_exam": ("ผลสอบเป็นข้อมูลว่าวิธีอ่านแบบนี้ยังไม่เวิร์ก ไม่ใช่ป้ายที่บอกว่าคุณเป็นคนแบบไหน",
                   "A result tells you the way you studied didn't work yet — it isn't a label for who you are."),
    "both": ("คนคนเดียวมีได้ทั้งด้านที่รักเราและด้านที่ทำให้เราเจ็บ — คุณเข้าใจเขาได้โดยไม่ต้องยอมรับสิ่งที่ทำร้าย และยอมรับว่าเขาทำร้ายได้โดยไม่ต้องลบวันที่เขาเคยดูแล · และการเข้าใจเขา ไม่ได้แปลว่าคุณต้องเป็นเหมือนเขา",
             "One person can hold both the side that loves you and the side that hurts you — you can understand them without accepting the harm, and name the harm without erasing the days they cared · and understanding them doesn't mean you have to become like them."),
    "cheated": ("สิ่งที่หายไปคือความไว้ใจในคนคนหนึ่ง ไม่ใช่ค่าของคุณ — ลองนับสิ่งที่ยังอยู่: ตัวคุณเอง คนที่ยังอยู่ข้างคุณ และสิทธิ์ที่จะเลือกเองว่าจะไปต่อหรือพอ",
                "What broke is your trust in one person, not your worth — count what is still here: you, the people still beside you, and your right to choose whether to continue or stop."),
    "parent_cheat": ("สิ่งที่พ่อแม่เลือกทำกับความสัมพันธ์ของเขา ไม่ใช่ความผิดของคุณ และคุณไม่จำเป็นต้องแบกความลับนี้ไว้คนเดียว — ครอบครัวอาจเปลี่ยนรูป แต่ความรักที่เขามีต่อลูก และตัวตนของคุณ ยังอยู่",
                     "What your parent chose to do in their relationship is not your fault, and you don't have to carry this secret alone — the family may change shape, but their love for you and who you are remain."),
    "left": ("การที่พ่อหรือแม่เลือกไปเริ่มชีวิตใหม่ตอนคุณยังเล็ก เป็นการตัดสินใจของผู้ใหญ่ ไม่ได้เกิดเพราะคุณดีไม่พอ — ไม่ว่าเขาจะไปสร้างบ้านใหม่กี่หลัง คำว่า \"ลูก\" ของคุณไม่มีวันเปลี่ยนสถานะ และชีวิตของคุณไม่ได้ถูกวัดจากบ้านที่เขาไปสร้าง",
             "A parent choosing to start a new life when you were small was an adult's decision, not because you weren't enough — however many new homes they build, being their child is a status that never changes, and your life isn't measured against the home they went on to build."),
    "compare": ("คนที่เริ่มจากจุดต่างกันเอามาเทียบกันไม่ได้ — คุณโตมากับสิ่งที่ต้องแบกเองตั้งแต่เด็ก การที่คุณยังยืนอยู่ตรงนี้ก็มีค่าแล้ว ค่าของคนไม่ได้วัดจากเงินหรือคำพูดของญาติ",
                "People who started from different places can't be fairly compared — you grew up carrying things on your own, and still standing here already means something. Your worth isn't measured by money or relatives' words."),
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
    if "caregiver" in topics and (_RESENT_EN if en else _RESENT_TH).search(text):
        pick.append("resent")
    if (_WORTHLESS_EN if en else _WORTHLESS_TH).search(text):
        if "relationship" in topics or "breakup" in topics:
            pick.append("worth_love")
        elif any(t in topics for t in ("study", "kp_exam_fail", "exam")):
            pick.append("worth_exam")
    fiction = re.search(r"ละคร|ซีรีส์|นิยาย|หนังเรื่อง|การ์ตูน|(?i:\b(?:movie|show|series|novel|episode)\b)", text)
    if not fiction and (_BOTH_EN if en else _BOTH_TH).search(text):
        pick.append("both")
    left = not fiction and (_LEFT_EN if en else _LEFT_TH).search(text)
    if left:
        pick.append("left")
    if not fiction and (_COMPARE_EN if en else _COMPARE_TH).search(text):
        pick.append("compare")
    if fiction or left:
        pass                                   # เลิกกันแล้วมีครอบครัวใหม่ ไม่ใช่การนอกใจ
    elif (_PARENT_CHEAT_EN if en else _PARENT_CHEAT_TH).search(text):
        pick.append("parent_cheat")
    elif (_CHEATED_ME_EN if en else _CHEATED_ME_TH).search(text):
        pick.append("cheated")
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
