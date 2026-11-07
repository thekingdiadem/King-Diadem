"""เจตนาของข้อความที่ไม่เข้าหัวข้อใดเลย — แทนคำตอบกลาง "ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน"

วัดจากประโยคจริงในเทสต์ 5,674 ประโยค: 41% ตกไปที่คำตอบกลาง ("เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว —
ปัญหาที่แท้จริงคืออะไร") รวมถึงข้อความที่ไม่ใช่ปัญหาเลย เช่น "ready to crash, goodnight" "this song slaps"
และข้อความที่ต้องการอย่างอื่น เช่น "my mom is not ok" (ห่วงคนอื่น) "อยากตื่นเช้า" (ตั้งเป้า)

หลัก (พิมพ์เขียว LYLA): ตอบให้ตรงกับที่คนพูดจริง · ไม่เร่ง · เรื่องอันตรายมาก่อนเสมอ
  · ใช้เฉพาะตอนไม่มีหัวข้อ ไม่มีวิกฤต และความเสี่ยงต่ำ — ไม่มีทางทับคำตอบเรื่องความปลอดภัย
  · ความแม่นมาก่อนความครอบคลุม: ไม่แน่ใจ = คืน None แล้วใช้คำตอบกลางเดิม
  · ไม่ใช้ AI — ไม่มีค่าโทเคน
"""
from __future__ import annotations

import re

# คำที่ทำให้ "ราตรีสวัสดิ์/ลาก่อน" อาจเป็นการบอกลาชีวิต — ไม่ตอบแบบคุยเล่นเด็ดขาด
_GRAVE = re.compile(r"ตาย|ไม่ตื่น|ตลอดไป|ลาก่อน|ครั้งสุดท้าย|หายไปเลย|ไม่ต้องรอ|ไม่อยู่แล้ว|"
                    r"\b(?:die|dead|kill|forever|never wake|end it|for good|last time|goodbye forever|won'?t be here)\b", re.I)

_CLOSE_NIGHT = re.compile(r"(?:ไปนอน(?:ก่อน|ละ|แล้ว)?|นอนก่อน|ฝันดี|ราตรีสวัสดิ์|ง่วงแล้ว)(?:นะ|ค่ะ|คะ|ครับ|จ้า|จ้ะ|น้า|ๆ|\s|[!.~])*$"
                          r"|\b(?:good ?night|gn|night night|off to (?:bed|sleep)|going to (?:bed|sleep)|heading to bed|time for bed)\b[\s!.~]*$", re.I)
_CLOSE_BYE = re.compile(r"(?:บายบาย|บ๊ายบาย|ไปก่อนนะ|แค่นี้ก่อน|ไว้คุยกันใหม่)(?:นะ|ค่ะ|คะ|ครับ|จ้า|ๆ|\s|[!.~])*$"
                        r"|\b(?:bye(?: for now)?|see (?:you|ya)(?: later| tomorrow)?|talk (?:to you )?(?:later|tomorrow)|ttyl|catch you later)\b[\s!.~]*$", re.I)

_PEOPLE_TH = r"(?:แม่|พ่อ|ลูก(?:สาว|ชาย)?|แฟน|เพื่อน|พี่(?:สาว|ชาย)?|น้อง(?:สาว|ชาย)?|สามี|ภรรยา|ยาย|ปู่|ย่า|คุณตา|คุณยาย)"
_PEOPLE_EN = r"(?:mom|mum|dad|mother|father|son|daughter|friend|best friend|partner|wife|husband|brother|sister|grandma|grandpa|boyfriend|girlfriend|roommate)"
_WORRY_OTHER = re.compile(
    _PEOPLE_TH + r"\S{0,10}?(?:ดู)?(?:ไม่โอเค|ไม่ค่อยโอเค|ไม่ค่อยดี|แปลกๆ|แปลกไป|ไม่เหมือนเดิม|ซึมๆ|ซึมไป|เงียบไป|เงียบผิดปกติ|ไม่ปกติ)|"
    r"เป็นห่วง" + _PEOPLE_TH + r"|"
    r"(?i:\bmy " + _PEOPLE_EN + r"\b[^\n]{0,20}?\b(?:is(?: not|n'?t) (?:ok(?:ay)?|doing (?:well|ok(?:ay)?)|(?:her|him)self)|seems? (?:off|different|down|not (?:ok|okay|right|herself|himself))|"
    r"(?:is|has been) acting (?:weird|strange|different|off))\b|\bworried about my " + _PEOPLE_EN + r"\b)")

_GOAL = re.compile(
    r"(?:^|\s)(?:ฉัน|ผม|หนู|เรา)?\s*(?:อยาก|ตั้งใจจะ|พยายามจะ|จะ)(?:เริ่ม|ฝึก)?(?:ตื่นเช้า|ตื่นเร็ว|นอนเร็ว|นอนให้เร็วขึ้น|ออกกำลังกาย|ไปยิม|วิ่ง(?:ทุกวัน|ตอนเช้า)?|"
    r"อ่านหนังสือ(?:ทุกวัน|ให้มากขึ้น)|เลิกเล่นมือถือ|เล่นมือถือน้อยลง|กินคลีน|ฝึกภาษา|เรียนภาษา\S{0,8}|ทำสมาธิ|นั่งสมาธิ|มีวินัย|เขียนไดอารี่|ดื่มน้ำ(?:ให้)?มากขึ้น)|"
    r"(?i:\bi (?:want|wanna|would like|am trying|'m trying|plan|need) to (?:start )?(?:wake up early|get up earlier|get up early|wake up earlier|sleep earlier|go to bed earlier|exercise|work out|"
    r"start running|run every day|read more|meditate|learn (?:a new language|\w+ (?:language|faster))|eat healthier|drink more water|stop scrolling|use my phone less|be more disciplined|build better habits)\b)")

_SAFETY_Q = re.compile(r"(?:ปลอดภัย|อันตราย)(?:ไหม|มั้ย|รึเปล่า|หรือเปล่า|หรือไม่)|"
                       r"(?i:\bis it (?:safe|dangerous|risky) to\b|\bis (?:it|this|that|\w+(?: \w+){0,3}) (?:safe|dangerous)\s*\?)")

# แบ่งปันเรื่องดี — ต้องมีคำบวกชัดๆ และไม่มีคำบอกปัญหา ("เพิ่งรู้ว่าแฟนมีคนอื่น" ต้องไม่ได้ "ฟังแล้วดีจัง")
_GOOD = re.compile(r"สนุก(?:มาก|ดี|สุดๆ)?|ชอบมาก|ดีใจ|มีความสุข|อร่อย|สวยมาก|ประทับใจ|ภูมิใจ|ได้รางวัล|"
                   r"(?i:\b(?:love (?:it|this)|enjoy(?:ed|ing)?|so much fun|great day|awesome|happy|slaps|amazing|beautiful|delicious|proud of)\b)")
_PROBLEM = re.compile(r"ไม่|เครียด|เศร้า|กลัว|เหนื่อย|ปัญหา|หนี้|ทะเลาะ|เจ็บ|ป่วย|ห่วง|กังวล|หงุดหงิด|โกรธ|เสีย|แย่|ร้องไห้|เลิก|นอกใจ|มีคนอื่น|ตาย|"
                      r"(?i:\b(?:sad|stress\w*|worr\w*|anxious|scared|afraid|tired|problem|hate|can'?t|cannot|not|never|hurt|sick|lost|fail\w*|cry\w*|broke(?:n| up)|cheat\w*|lonely|die|dead)\b)", re.I)
_QUESTION = re.compile(r"\?|ไหม|มั้ย|ยังไง|อย่างไร|อะไร|ทำไม|เมื่อไร|ที่ไหน|ใคร|เท่าไร|ดีไหม|"
                       r"(?i:\b(?:how|what|why|when|where|who|should|can i|do i|is it|does)\b)")


def detect(text: str) -> str | None:
    """เจตนาของข้อความที่ไม่มีหัวข้อ: closing_night · closing_bye · worry_other · goal · safety_q · share_good"""
    t = str(text or "").strip()
    if not t or len(t) > 160 or _GRAVE.search(t):
        return None
    if len(t) <= 80 and _CLOSE_NIGHT.search(t):
        return "closing_night"
    if len(t) <= 80 and _CLOSE_BYE.search(t):
        return "closing_bye"
    if _WORRY_OTHER.search(t):
        return "worry_other"
    if _SAFETY_Q.search(t):
        return "safety_q"
    if _GOAL.search(t):
        return "goal"
    if len(t) <= 100 and _GOOD.search(t) and not _PROBLEM.search(t) and not _QUESTION.search(t):
        return "share_good"
    return None


# คำตอบสั้น (ไม่มีขั้นตอน) — ปิดบทสนทนาแบบอบอุ่น ไม่ต้องมีสถานะความเสี่ยง
SHORT = {
    "th": {"closing_night": "ฝันดี{end} พักให้เต็มที่นะ พรุ่งนี้มีอะไรค่อยมาคุยกันต่อได้เสมอ",
           "closing_bye": "ไว้คุยกันใหม่{end} มีเรื่องไหนอยากคิดต่อ พิมพ์มาได้ตลอดนะ",
           "share_good": "ฟังแล้วดีจัง{end} เล่าต่อได้นะ — หรือถ้ามีเรื่องไหนที่กำลังคิดหรือตัดสินใจอยู่ ก็พิมพ์มาได้เลย"},
    "en": {"closing_night": "Good night — rest well. We can pick this up tomorrow.",
           "closing_bye": "Take care — come back any time you want to think something through.",
           "share_good": "That sounds really nice — tell me more if you like, or bring me anything you're trying to figure out."},
}

# คำตอบมีขั้นตอน (open, paths, ask) — ใช้โครงเดียวกับหัวข้ออื่น
STEPS = {
    "th": {
        "worry_other": ("ดีแล้วที่สังเกตเห็น — การมีคนห่วงช่วยได้มากกว่าที่คิด",
                        ["ถามเขาตรงๆ ด้วยน้ำเสียงสบายๆ เช่น \"ช่วงนี้ดูเหนื่อยๆ เป็นอะไรรึเปล่า\" แล้วฟังก่อน ยังไม่ต้องรีบแก้ให้",
                         "สังเกตสัญญาณอันตราย: พูดถึงความตายหรือการหายไป แจกของ ไม่กินไม่นอนหลายวัน หรือป่วยกะทันหัน — ถ้ามี โทร 1323 (เรื่องใจ) หรือ 1669 (เรื่องร่างกาย) ได้ทันที",
                         "ชวนทำอะไรเล็กๆ ด้วยกัน หรืออยู่ใกล้ๆ ก็พอ — ไม่ต้องมีคำตอบให้เขาทุกเรื่อง"],
                        "เขาเป็นแบบนี้มานานแค่ไหน และมีอะไรที่ทำให้คุณห่วงเป็นพิเศษ?"),
        "goal": ("เปลี่ยนนิสัยได้ผลที่สุดตอนเริ่มเล็กจนแทบไม่ต้องใช้แรงใจ",
                 ["เริ่มเล็กที่สุดที่ทำได้ทุกวัน เช่น ตื่นเร็วขึ้นแค่ 15 นาที หรือออกกำลังกาย 5 นาที — ทำให้ติดก่อน แล้วค่อยเพิ่ม",
                  "ผูกกับสิ่งที่ทำอยู่แล้ว: \"หลังแปรงฟัน → …\" และเตรียมของไว้ตั้งแต่คืนก่อน (ชุดวิ่ง หนังสือ ขวดน้ำ)",
                  "ติ๊กในปฏิทิน 7 วัน — พลาดวันเดียวไม่เป็นไร แค่อย่าพลาดสองวันติดกัน"],
                 "ที่ผ่านมา อะไรมักทำให้แผนแบบนี้หลุด?"),
        "safety_q": ("เรื่องนี้ระบบยังไม่มีข้อมูลที่ตรวจแล้วแบบเจาะจง — ขอบอกวิธีเช็กที่เชื่อได้แทนการเดา",
                     ["เรื่องยาหรือสารเคมี: ถามเภสัชกรที่ร้านยา หรือศูนย์พิษวิทยา 1367 (24 ชม.) บอกชื่อ ปริมาณ และน้ำหนักตัว",
                      "เรื่องเงิน ลิงก์ หรือแอป: เช็กกับช่องทางทางการของหน่วยงานนั้นเอง ไม่ใช่ลิงก์ที่ถูกส่งมา · สงสัยว่าโดนหลอก โทร 1441",
                      "ถ้าทำไปแล้วและมีอาการผิดปกติ หรือมีคนเจ็บ โทร 1669 ได้เลย ไม่ต้องรอให้แน่ใจ"],
                     "เป็นเรื่องที่กำลังจะทำ หรือทำไปแล้ว?"),
    },
    "en": {
        "worry_other": ("It's good that you noticed — someone caring makes more difference than you'd think.",
                        ["Ask them directly and gently, like \"you've seemed tired lately — is something going on?\", then listen before trying to fix anything.",
                         "Watch for danger signs: talking about death or disappearing, giving things away, not eating or sleeping for days, or sudden illness — if so, call a crisis line (988 in the US, 116 123 in the UK) or emergency services.",
                         "Do something small together, or just be nearby — you don't need an answer for everything."],
                        "How long have they been like this, and what worries you most?"),
        "goal": ("Habits stick best when you start so small it barely takes willpower.",
                 ["Start with the smallest version you can do every day — 15 minutes earlier, or 5 minutes of exercise — then build up.",
                  "Attach it to something you already do (\"after brushing my teeth → …\") and set things out the night before.",
                  "Tick it off on a calendar for 7 days — missing one day is fine, just don't miss two in a row."],
                 "What has usually knocked plans like this off track before?"),
        "safety_q": ("I don't have verified information on this specific case — here's how to check reliably instead of guessing.",
                     ["For medicines or chemicals, ask a pharmacist or poison control (US 1-800-222-1222; Thailand 1367) with the name, amount and body weight.",
                      "For money, links or apps, check through the organisation's own official channel — never the link you were sent.",
                      "If it already happened and someone feels unwell or is hurt, call emergency services now — don't wait to be sure."],
                     "Is this something you're about to do, or has it already happened?"),
    },
}

