"""
core/cyber_scam.py — กลโกงไซเบอร์ที่ผู้ใช้จะพิมพ์มาเล่า (ไทย/อังกฤษ)

ที่มา: เจ้าของโปรเจกต์แคปโพสต์ของตำรวจไซเบอร์มาให้ (ต.ค.–พ.ย. 2569) แล้วให้กรองก่อนใช้
เก็บเฉพาะ "สถานการณ์ที่คนทั่วไปเจอแล้วพิมพ์มาถาม" และ "หลักที่จริงเสมอ" เช่น เจ้าหน้าที่จริงไม่มารับเงินถึงบ้าน
ไม่เก็บ: ตัวเลขความเสียหาย/จำนวนเหยื่อที่ยืนยันไม่ได้ · รายละเอียดเทคนิคการเจาะ (ชิป WiFi, Plex2Shell, APT29) ·
ชื่อมัลแวร์เฉพาะตัว — ผู้ใช้ไม่ได้พิมพ์เรื่องเหล่านี้มาขอความช่วยเหลือ และชื่อเปลี่ยนเร็วกว่าที่เราตามทัน

เดิมเกือบทุกประโยคได้ความเสี่ยงศูนย์ หรือตอบผิดกรอบ:
"SMS ใบสั่งจราจรให้กดลิงก์" → คำตอบเรื่องหนี้ · "ตำรวจให้ถอนเงินไปซื้อทอง" → คำแนะนำการลงทุน
"got a text about an unpaid toll" → "เสียใจด้วยที่โดนโกง" ทั้งที่ยังไม่ได้กดลิงก์

จับจากรูปของสถานการณ์ ไม่ใช่คำเดียว: [ช่องทาง] + [ลิงก์] + [เรื่องเร่งด่วนที่ต้องจ่าย/ยืนยัน] ฯลฯ
"""
import re

_G = r"[^\n]"

# ชนิด → (ความเสี่ยง, รูปประโยค) · เรียงจากด่วนที่สุด
PATTERNS = (
    # ให้สิทธิ์ช่วยเหลือการเข้าถึงแก่แอปจากลิงก์ไปแล้ว = แอปควบคุมเครื่องและเห็นรหัสได้ — ด่วนที่สุด
    ("accessibility", 85, re.compile(
        r"(?:สิทธิ์|สิทธิ|การตั้งค่า)\s*(?:การ)?ช่วยเหลือ(?:การ)?เข้าถึง|accessibility\s+(?:permission|service|access|setting)s?|"
        r"(?:อนุญาต|กดตกลง|กดยอม)" + _G + r"{0,10}?(?:ให้)?(?:แอป|แอพ)" + _G + r"{0,10}?(?:ควบคุม|คุม)(?:เครื่อง|มือถือ|หน้าจอ)|"
        r"(?:แอป|app)" + _G + r"{0,30}?(?:ควบคุม|คุม)(?:เครื่อง|มือถือ|หน้าจอ)" + _G + r"{0,10}?(?:อนุญาต|กดยอม|กดตกลง)|"
        r"(?:มือถือ|เครื่อง|โทรศัพท์)" + _G + r"{0,10}?(?:ค้าง|จอดำ|ขยับเอง|กดเอง|ถูกควบคุม)" + _G + r"{0,30}?(?:แอป|ลิงก์|ติดตั้ง)", re.I)),
    # คนอ้างเป็นเจ้าหน้าที่ ให้ถอนเงินสด/ซื้อทอง/บัตรของขวัญ/ฝากตู้คริปโต หรือจะส่งคนมารับที่บ้าน
    ("courier_cash", 80, re.compile(
        # ต้องมี "คนสั่ง" — "ถอนเงินไปซื้อทองเก็บไว้เอง" ไม่ใช่การถูกหลอก
        r"(?:ให้|สั่งให้|บอกให้)(?:ไป)?(?:ถอน(?:เงิน)?(?:สด)?|เอาเงินสด)" + _G + r"{0,30}?(?:ซื้อทอง|มารับ|ส่งคนมา|ให้คนมา|ฝากตู้)|"
        r"(?:มารับ|ส่งคนมารับ|ส่งเจ้าหน้าที่มารับ)(?:เงิน|ทอง|ของ)?" + _G + r"{0,10}?(?:ที่บ้าน|ถึงบ้าน|หน้าบ้าน)|"
        r"(?:ซื้อ|เติม)?บัตร(?:ของขวัญ|เติมเงิน|กิฟต์|gift)" + _G + r"{0,30}?(?:ส่งรหัส|บอกรหัส|ถ่ายรูป|คดี|เคลียร์|ตำรวจ|เจ้าหน้าที่)|"
        r"(?:ตำรวจ|เจ้าหน้าที่|DSI|ดีเอสไอ|ปปง|ศาล|อัยการ|ธนาคาร|กรม)" + _G + r"{0,40}?(?:ฝากตู้|ตู้(?:บิตคอยน์|คริปโต|bitcoin|crypto)|ซื้อทอง|บัตรของขวัญ)|"
        r"\b(?:withdraw|take out)\b" + _G + r"{0,30}?\b(?:cash|money)\b" + _G + r"{0,30}?\b(?:buy (?:gold|bitcoin|crypto)|courier|pick (?:it )?up|bitcoin atm)\b|"
        r"\b(?:courier|agent|officer|someone)\b" + _G + r"{0,20}?\b(?:pick up|collect) (?:the |my |your )?(?:cash|gold|money)\b|"
        r"\b(?:pay|buy)\b" + _G + r"{0,20}?\bgift ?cards?\b" + _G + r"{0,40}?\b(?:arrest|warrant|police|fbi|irs|officer|government|case|fine)\b|"
        r"\b(?:fbi|irs|police|officer|government|agent|customs)\b" + _G + r"{0,50}?\b(?:gift ?cards?|bitcoin atm|crypto atm|buy gold)\b", re.I)),
    # ให้ติดตั้งแอป/ไฟล์ .apk จากลิงก์ (มักทำหน้าตาเหมือน Google Play หรือแอปหน่วยงาน)
    ("apk", 70, re.compile(
        r"\.?\bapk\b|(?:โหลด|ลง|ติดตั้ง)(?:แอป|แอพ|ไฟล์)" + _G + r"{0,20}?(?:จาก|ผ่าน|ใน)\s*(?:ลิงก์|ลิ้งก์|ลิ้ง|แชท|ไลน์|SMS|เอสเอ็มเอส|ข้อความ|โฆษณา)|"
        r"(?:ลิงก์|ลิ้งก์|ลิ้ง|โฆษณา)" + _G + r"{0,30}?(?:ให้)?(?:โหลด|ลง|ติดตั้ง)(?:แอป|แอพ|ไฟล์)|(?:ติดตั้ง|โหลด)ไฟล์เพิ่ม|"
        r"(?:แอป|แอพ)" + _G + r"{0,30}?(?:โหลด|ลง|ติดตั้ง)" + _G + r"{0,6}?(?:ผ่าน|จาก|ใน)\s*(?:ลิงก์|ลิ้งก์|ลิ้งค์|ลิงค์|ลิ้ง|แชท|ไลน์|เฟซ|SMS|เอสเอ็มเอส|ข้อความ|โฆษณา)|"
        r"\b(?:install|download)(?:ed)?\b" + _G + r"{0,20}?\b(?:app|file)\b" + _G + r"{0,20}?\bfrom (?:a|the|this) (?:link|text|sms|message|ad)\b|"
        r"\b(?:link|ad|text)\b" + _G + r"{0,30}?\b(?:install|download)\b" + _G + r"{0,10}?\b(?:an? )?(?:app|file)\b|\bsideload", re.I)),
    # เพื่อน/ญาติทักมายืมเงินทางแชท/อีเมล — "ถามกลับทางเดิม" ไม่ใช่การยืนยัน (คนที่ตอบอาจเป็นคนที่ยึดบัญชีไว้)
    ("friend_account", 65, re.compile(
        r"(?:เพื่อน|ญาติ|พี่|น้อง|แม่|พ่อ|ลูก|หัวหน้า|เจ้านาย)" + _G + r"{0,20}?(?:ทัก|ส่ง(?:เมล|ข้อความ|ไลน์)?|อินบ็อกซ์|แชท)" + _G + r"{0,20}?(?:ยืมเงิน|ขอยืม|ขอเงิน|ให้โอน|โอนเงิน|ให้ช่วยโอน)|"
        r"\b(?:friend|cousin|boss|mom|dad|son|daughter|brother|sister)\b" + _G + r"{0,30}?\b(?:emailed|texted|messaged|dm'?d|wrote)\b" + _G + r"{0,30}?\b(?:money|borrow|transfer|send (?:him|her|them) )", re.I)),
    # แอปจ่ายเงินเล็กน้อยแลกกับให้ใช้ซิม/เครื่องเราส่ง SMS — เบอร์เรากลายเป็นเบอร์ที่ส่งลิงก์หลอกคนอื่น
    ("sim_rent", 65, re.compile(
        r"(?:แอป|แอพ)" + _G + r"{0,30}?(?:จ่าย|ให้เงิน|ได้เงิน)" + _G + r"{0,30}?(?:ใช้ซิม|ส่ง\s*(?:SMS|เอสเอ็มเอส|ข้อความ)|ปล่อยเครื่อง|เปิดเครื่องทิ้งไว้)|"
        r"(?:แอป|แอพ)" + _G + r"{0,20}?(?:เปิดเครื่องทิ้งไว้|ปล่อยเครื่อง(?:ทิ้งไว้)?|ใช้ซิม)" + _G + r"{0,20}?(?:ได้เงิน|ได้ค่า|จ่าย)|"
        r"(?:ให้เช่า|เช่า)(?:ซิม|เบอร์)" + _G + r"{0,30}?(?:ส่ง\s*SMS|ได้เงิน|รายได้)|"
        r"\bapp\b" + _G + r"{0,30}?\b(?:pays?|paid|earn)\b" + _G + r"{0,30}?\b(?:send(?:s|ing)? (?:sms|texts?|messages?)|use my (?:sim|phone number))\b", re.I)),
    # หน้าเว็บให้กดยืนยันว่าไม่ใช่หุ่นยนต์ แล้วให้กรอก OTP/รหัส — หน้ายืนยันไม่ได้พิสูจน์ว่าเว็บจริง
    ("otp_page", 70, re.compile(
        r"(?:ไม่ใช่หุ่นยนต์|captcha|แคปช่า)" + _G + r"{0,60}?(?:OTP|โอทีพี|รหัส|พาสเวิร์ด|รหัสผ่าน|ล็อกอิน|เข้าสู่ระบบ)|"
        r"(?:ลิงก์|ลิ้งก์|ลิ้ง|เว็บ)" + _G + r"{0,30}?(?:ให้)?(?:กรอก|ใส่|พิมพ์)\s*(?:OTP|โอทีพี|รหัส\s*OTP)|"
        r"\b(?:i'?m not a robot|captcha)\b" + _G + r"{0,60}?\b(?:otp|code|password|log ?in|sign ?in)\b|"
        r"\b(?:link|site|page)\b" + _G + r"{0,30}?\b(?:asked|asks|wants) (?:me )?(?:for|to enter) (?:my |the |an? )?(?:otp|one-time code|verification code)\b", re.I)),
    # SMS/ข้อความ + ลิงก์ + เรื่องเร่งให้จ่าย/ยืนยัน (ใบสั่ง ค่าปรับ พัสดุ ภาษีคืน บัญชีถูกระงับ คะแนนหมดอายุ)
    ("sms_link", 65, re.compile(
        r"(?:SMS|เอสเอ็มเอส|ข้อความ|ไลน์|อีเมล|เมล)" + _G + r"{0,50}?(?:ใบสั่ง|ค่าปรับ|พัสดุ|ภาษีคืน|คืนภาษี|เงินคืน|บัญชี(?:ถูก)?(?:ระงับ|อายัด)|"
        r"คะแนน" + _G + r"{0,6}?หมดอายุ|ค่าไฟ(?:ค้าง)?|การไฟฟ้า|กรมที่ดิน|สรรพากร|ประกันสังคม|ได้รับสิทธิ์|รางวัล)" + _G + r"{0,40}?(?:ลิงก์|ลิ้งก์|ลิ้ง|กด|คลิก)|"
        r"(?:ลิงก์|ลิ้งก์|ลิ้งค์|ลิงค์|ลิ้ง|ลิงก)" + _G + r"{0,30}?(?:ใบสั่ง|ค่าปรับ|พัสดุ|ภาษีคืน|คืนภาษี|บัญชี(?:ถูก)?(?:ระงับ|อายัด)|คะแนน" + _G + r"{0,6}?หมดอายุ|ค่าไฟ)|"
        r"\b(?:text|sms|message|email)\b" + _G + r"{0,50}?\b(?:toll|fine|ticket|parcel|package|delivery|tax refund|refund|account (?:is )?(?:suspended|locked|on hold)|points expir\w*)\b" + _G + r"{0,40}?\b(?:link|click|pay)\b|"
        r"\blink\b" + _G + r"{0,30}?\b(?:unpaid toll|toll|fine|parcel|package|tax refund|account suspended)\b", re.I)),
    # ข่าวลือว่าธนาคารโดนแฮ็ก/ล่ม แล้วจะแห่ไปถอน
    ("bank_rumor", 50, re.compile(
        r"(?:ข่าว|ได้ยินมาว่า|เขาว่ากันว่า|แชร์กันว่า)" + _G + r"{0,20}?ธนาคาร" + _G + r"{0,30}?(?:โดนแฮ็ก|ถูกแฮ็ก|แฮก|ล่ม|จะปิด|เจ๊ง)" + _G + r"{0,40}?(?:ถอน|ย้ายเงิน)|"
        r"\b(?:rumou?r|news|heard)\b" + _G + r"{0,30}?\bbank\b" + _G + r"{0,30}?\b(?:hacked|collaps\w*|going under|breach\w*)\b" + _G + r"{0,40}?\b(?:withdraw|pull (?:my|all)|move my money)\b", re.I)),
    # วงที่ "จ่ายจริงมาหลายปี" และได้เงินจากการชวนคนเพิ่ม — แชร์ลูกโซ่ที่พังแรงมักเป็นวงที่เคยจ่ายจริง
    ("ponzi", 65, re.compile(
        r"(?:จ่าย|ได้)(?:ปันผล|ผลตอบแทน|เงิน)?(?:จริง)" + _G + r"{0,20}?(?:มา|มาแล้ว)?\s*(?:\d+|หลาย|สอง|สาม)\s*(?:ปี|เดือน)" + _G + r"{0,50}?(?:ชวน|แนะนำ|ดาวน์ไลน์|ค่าคอม)|"
        r"(?:ชวน|หา)(?:คน|สมาชิก|ดาวน์ไลน์)(?:เพิ่ม|ต่อ)?" + _G + r"{0,20}?(?:ได้ค่าคอม|ได้เปอร์เซ็นต์|ได้ส่วนแบ่ง)" + _G + r"{0,30}?(?:ลงทุน|ปันผล|ผลตอบแทน)|"
        r"(?:ลงทุน|ปันผล|ผลตอบแทน)" + _G + r"{0,40}?(?:ชวน|หา)(?:คน|สมาชิก|ดาวน์ไลน์)(?:เพิ่ม|ต่อ)?" + _G + r"{0,20}?(?:ได้ค่าคอม|ได้เปอร์เซ็นต์|ได้ส่วนแบ่ง)|"
        r"\bpaid (?:out )?(?:for|every month for) (?:\d+|two|three|several) (?:years|months)\b" + _G + r"{0,50}?\b(?:recruit|refer|bring in|commission)\b|"
        r"\b(?:recruit|refer|bring in)\b" + _G + r"{0,30}?\b(?:commission|bonus|cut)\b" + _G + r"{0,30}?\b(?:returns?|dividends?|invest\w*)\b", re.I)),
)

# เล่าเรื่องคนอื่น/ข่าว/สอนหนังสือ — ไม่ใช่สิ่งที่เกิดกับผู้ใช้เอง ("วิธีป้องกัน apk" "ข่าวแก๊งคอลเซ็นเตอร์")
_NOT_MINE = re.compile(r"วิธี(?:ป้องกัน|สังเกต|เช็ก)|สอน(?:วิธี)?|ทำรายงาน|เขียนบทความ|ข่าว(?!ลือ|ว่า)|"
                       r"\b(?:how (?:to|do (?:i|you)) (?:spot|avoid|protect|prevent)|write an? (?:article|report)|for (?:a|my) (?:class|report))\b",
                       re.I)
# คนพิมพ์คือนักพัฒนา/คนตั้งค่าเครื่อง ไม่ใช่เหยื่อ ("build an apk" "สร้างไฟล์ apk")
_DEV = re.compile(r"(?:สร้าง|build|compile|sign|debug|gradle|android studio)" + _G + r"{0,20}?\bapk\b|\bapk\b" + _G + r"{0,20}?(?:build|debug|gradle|ของ(?:แอป)?(?:ฉัน|ผม|เรา)เอง)", re.I)


def cyber_kind(text) -> tuple | None:
    """→ (ชนิด, ความเสี่ยง) ของกลโกงไซเบอร์ที่ผู้ใช้กำลังเจอ หรือ None"""
    t = str(text or "")
    if not t.strip() or _NOT_MINE.search(t) or _DEV.search(t):
        return None
    intl = cyber_kind_intl(t)               # ภาษาอื่นตรวจด้วยรูปประโยคของภาษานั้นก่อน (ไทย/อังกฤษไม่เข้าเงื่อนไขนี้)
    if intl:
        return intl
    for kind, risk, rx in PATTERNS:
        if rx.search(t):
            return kind, risk
    return None


# ── คำตอบ: เปิดด้วยสิ่งที่ทำได้ทันที · สามข้อ · คำถามหนึ่งข้อ ─────────────────────
AOC_TH = "1441 (ศูนย์ AOC ตำรวจไซเบอร์ 24 ชม.)"
REPLY = {
    "accessibility": {
        "th": ("ตอนนี้ด่วนค่ะ — สิทธิ์นี้ทำให้แอปเห็นทุกอย่างที่พิมพ์และกดแทนเราได้ รวมถึงรหัสแอปธนาคาร",
               ["ปิดเน็ตมือถือและ WiFi ทันที (เปิดโหมดเครื่องบิน) — ตัดไม่ให้แอปส่งข้อมูลหรือสั่งโอน",
                "ใช้เครื่องอื่นโทรหาธนาคารทุกแห่งที่มีแอปในเครื่องนี้ ขอระงับบัญชี/ระงับแอปชั่วคราว แล้วโทร " + AOC_TH,
                "ลบแอปนั้น (ถ้าลบไม่ได้ ให้ปิดสิทธิ์ช่วยเหลือการเข้าถึงก่อน) แล้วเปลี่ยนรหัสธนาคารและอีเมลจากเครื่องอื่น"],
               "ตอนนี้มีเงินถูกโอนออกไปแล้ว หรือยังไม่เห็นรายการแปลกคะ"),
        "en": ("This is urgent — that permission lets an app see everything you type and tap for you, including banking PINs.",
               ["Turn off mobile data and Wi-Fi now (airplane mode) so the app can't send data or move money.",
                "From another phone, call every bank whose app is on this phone and ask them to freeze the account or app. In Thailand also call 1441 (cyber police AOC, 24h).",
                "Delete the app (if it won't uninstall, switch off its accessibility access first), then change banking and email passwords from another device."],
               "Has any money already left your account, or nothing unusual yet?"),
    },
    "courier_cash": {
        "th": ("นี่คือรูปแบบของมิจฉาชีพค่ะ — เจ้าหน้าที่จริงไม่สั่งให้ถอนเงินไปซื้อทอง ซื้อบัตรของขวัญ ฝากตู้คริปโต และไม่ส่งคนมารับเงินหรือทองที่บ้าน",
               ["หยุดก่อน อย่าถอนหรือส่งอะไรเพิ่ม และไม่ต้องเปิดประตูให้ใครที่ \"มารับของ\"",
                "วางสายแล้วโทรกลับไปที่เบอร์ทางการของหน่วยงานนั้นเอง (หาเบอร์เอง ไม่ใช้เบอร์ที่เขาให้) หรือโทร " + AOC_TH,
                "ถ้าส่งเงินหรือของไปแล้ว แจ้ง 1441 และ thaipoliceonline.go.th ให้เร็วที่สุด เก็บเบอร์ แชท และรูปบัตรที่เขาส่งมาไว้เป็นหลักฐาน"],
               "ตอนนี้ส่งเงิน ทอง หรือรหัสบัตรไปแล้วหรือยังคะ"),
        "en": ("This is a scam pattern — real officials never tell you to withdraw cash to buy gold, gift cards or crypto, and never send someone to collect money at your home.",
               ["Stop — don't withdraw or hand over anything else, and don't open the door to anyone \"collecting\".",
                "Hang up and call the agency yourself on its official number (look it up, don't use the one they gave). In Thailand: 1441 (cyber police, 24h).",
                "If you already sent money or goods, report it right away (1441 / thaipoliceonline.go.th in Thailand, or your local police) and keep numbers, chats and the \"ID\" photos they sent."],
               "Have you already handed over cash, gold or card codes?"),
    },
    "apk": {
        "th": ("อย่าติดตั้งค่ะ — แอปที่ส่งมาเป็นลิงก์หรือไฟล์ .apk คือช่องทางหลักที่มิจฉาชีพใช้ขโมยเงินจากแอปธนาคาร แม้หน้าตาจะเหมือน Google Play หรือแอปหน่วยงาน",
               ["ปิดหน้านั้นไปเลย ติดตั้งแอปจาก Play Store หรือ App Store ที่เปิดเองเท่านั้น",
                "ถ้าติดตั้งไปแล้ว: เปิดโหมดเครื่องบิน ลบแอป และห้ามกดอนุญาต \"การช่วยเหลือการเข้าถึง\" เด็ดขาด",
                "ถ้าเคยเปิดแอปธนาคารหลังติดตั้ง โทรธนาคารให้ช่วยตรวจ และโทร " + AOC_TH],
               "ติดตั้งไปแล้ว หรือยังแค่เห็นลิงก์คะ"),
        "en": ("Don't install it — apps sent as links or .apk files are the main way scammers drain banking apps, even when the page looks like Google Play or a government app.",
               ["Close the page. Only install apps from the Play Store or App Store you open yourself.",
                "If you already installed it: airplane mode, delete it, and never grant it \"accessibility\" permission.",
                "If you opened a banking app after installing, call your bank to check the account (Thailand: also 1441, cyber police)."],
               "Did you install it already, or have you only seen the link?"),
    },
    "friend_account": {
        "th": ("ขอให้เช็กอีกทางก่อนโอนนะคะ — ถ้าบัญชีของเพื่อนถูกยึด คนที่ตอบ \"จริง\" ในแชทหรืออีเมลเดิมก็คือมิจฉาชีพเอง",
               ["โทรหาเพื่อนที่เบอร์เดิมที่เรามีอยู่แล้ว (ไม่ใช่เบอร์ในข้อความ) แล้วถามเรื่องที่มีแต่เราสองคนรู้",
                "ถ้าโทรไม่ติด อย่าโอนจนกว่าจะคุยกันได้ — คนที่เดือดร้อนจริงรอได้ไม่กี่นาที",
                "ถ้าเป็นบัญชีปลอม บอกเพื่อนและคนรู้จักให้ระวัง และแจ้ง " + AOC_TH + " ถ้าโอนไปแล้ว"],
               "ตอนนี้โอนไปแล้ว หรือยังคะ"),
        "en": ("Please check another way before sending — if your friend's account was taken over, the \"yes it's me\" reply comes from the scammer.",
               ["Call your friend on the number you already have (not one in the message) and ask something only the two of you know.",
                "If you can't reach them, don't send money until you do — a real emergency can wait a few minutes.",
                "If it's fake, warn your friend and mutual contacts. If you already sent money, call your bank now (Thailand: also 1441)."],
               "Have you sent anything yet?"),
    },
    "sim_rent": {
        "th": ("อย่ารับเงินแบบนี้นะคะ — แอปที่จ่ายเงินแลกกับให้ใช้ซิมหรือเครื่องเราส่ง SMS กำลังใช้เบอร์เราส่งลิงก์หลอกคนอื่น",
               ["ลบแอปและหยุดใช้ทันที แม้จะได้เงินไม่กี่บาท",
                "คนที่ถูกหลอกจะเห็นเบอร์ของเรา เราอาจถูกเรียกสอบหรือถูกระงับเบอร์ — เก็บหลักฐานว่าใครชวนและได้เงินเท่าไหร่",
                "โทร " + AOC_TH + " เพื่อแจ้งไว้ก่อน และติดต่อเครือข่ายมือถือให้ตรวจการส่ง SMS จากเบอร์เรา"],
               "ใช้แอปนี้มานานแค่ไหนแล้วคะ"),
        "en": ("Please don't take this money — apps that pay you to let them send SMS from your phone are using your number to send scam links to others.",
               ["Delete the app and stop now, even if it only pays a little.",
                "The people who get scammed see your number, so you may be questioned or have the number suspended — keep proof of who recruited you and what you were paid.",
                "Report it (Thailand: 1441, cyber police) and ask your mobile carrier to check SMS sent from your number."],
               "How long has the app been running on your phone?"),
    },
    "otp_page": {
        "th": ("หยุดก่อนกรอกค่ะ — หน้า \"ยืนยันว่าไม่ใช่หุ่นยนต์\" ไม่ได้พิสูจน์ว่าเว็บจริง มิจฉาชีพใส่ไว้เองเพื่อหลบการตรวจจับ และเห็นทุกตัวที่เราพิมพ์แบบสด",
               ["อย่ากรอก OTP หรือรหัสในเว็บที่มาจากลิงก์ — ปิดแล้วเปิดแอปหรือพิมพ์ชื่อเว็บเองแทน",
                "ถ้ากรอกไปแล้ว เปลี่ยนรหัสบัญชีนั้นทันทีจากแอปจริง และโทรธนาคารถ้าเป็นบัญชีเงิน",
                "เก็บลิงก์ไว้แจ้ง " + AOC_TH],
               "กรอกอะไรลงไปแล้วบ้างคะ"),
        "en": ("Stop before typing anything — an \"I'm not a robot\" check doesn't prove a site is real. Scammers add it to dodge detection, and they see each character you type live.",
               ["Never enter an OTP or password on a page you reached from a link — close it and open the app or type the address yourself.",
                "If you already entered it, change that password now from the real app, and call your bank if it's a money account.",
                "Keep the link to report it (Thailand: 1441, cyber police)."],
               "What have you entered so far?"),
    },
    "sms_link": {
        "th": ("อย่าเพิ่งกดลิงก์นะคะ — ข้อความเร่งให้จ่ายค่าปรับ รับพัสดุ รับเงินคืน หรือยืนยันบัญชี เป็นช่องทางหลักของมิจฉาชีพ",
               ["ไม่กดลิงก์ ไม่โทรกลับเบอร์ในข้อความ — เช็กเองจากแอปหรือเว็บทางการที่พิมพ์ชื่อเอง หรือโทรเบอร์ทางการของหน่วยงาน",
                "หน่วยงานจริงไม่ส่งลิงก์ให้โหลดแอป และไม่ให้กรอก OTP ในเว็บจากลิงก์",
                "ถ้ากดหรือกรอกข้อมูลไปแล้ว เปลี่ยนรหัส โทรธนาคาร และโทร " + AOC_TH],
               "ได้กดลิงก์หรือกรอกอะไรไปแล้วหรือยังคะ"),
        "en": ("Don't tap the link yet — urgent texts about fines, tolls, parcels, refunds or account checks are scammers' main channel.",
               ["Don't tap or call back numbers in the message — check through the official app or a site you type yourself.",
                "Real agencies don't text links to install apps or ask for an OTP on a linked page.",
                "If you already tapped or entered details, change passwords and call your bank (Thailand: also 1441, cyber police)."],
               "Have you tapped the link or entered anything yet?"),
    },
    "bank_rumor": {
        "th": ("เช็กก่อนเชื่อและก่อนแชร์นะคะ — ข่าวลือว่าธนาคารโดนแฮ็กทำให้คนแห่ไปถอนเงินได้ ทั้งที่ระบบยังปกติ",
               ["ดูประกาศจากช่องทางทางการของธนาคารนั้นเอง (แอป เว็บ เพจที่ยืนยันแล้ว) หรือโทรเบอร์บนหลังบัตร",
                "อย่ากดลิงก์ \"ตรวจสอบบัญชี\" ที่แนบมากับข่าว — มักเป็นลิงก์หลอกที่อาศัยความตกใจ",
                "ถ้าเห็นรายการแปลกในบัญชีจริงๆ โทรธนาคารให้ระงับ แล้วโทร " + AOC_TH],
               "ข่าวนี้มาจากไหนคะ — ธนาคารประกาศเอง หรือแชร์ต่อกันมา"),
        "en": ("Check before believing or sharing — a rumour that a bank was hacked can start a rush to withdraw even when the system is fine.",
               ["Look for an announcement on the bank's own official channels, or call the number on the back of your card.",
                "Don't tap \"check your account\" links that come with the rumour — panic is what scam links feed on.",
                "If you see real unfamiliar transactions, call the bank to freeze them (Thailand: also 1441)."],
               "Where did the news come from — the bank itself, or shared around?"),
    },
    "ponzi": {
        "th": ("ระวังนะคะ — วงที่ได้เงินจากการชวนคนเพิ่ม มักเป็นแชร์ลูกโซ่ และวงที่พังแรงที่สุดคือวงที่จ่ายจริงมาหลายปีจนคนเชื่อสนิท",
               ["ถามให้ชัดว่าเงินปันผลมาจากกำไรของธุรกิจอะไร มีงบการเงินหรือใบอนุญาตจาก ก.ล.ต./แบงก์ชาติไหม — ถ้าตอบไม่ได้ อย่าใส่เพิ่ม",
                "ไม่ชวนคนอื่นเข้า — ถ้าวันไหนพัง คนที่เราชวนคือญาติและเพื่อนของเราเอง",
                "ถ้าอยากถอนออก ทำทีละน้อยและเก็บหลักฐานการโอนทุกครั้ง · ปรึกษา ก.ล.ต. 1207 หรือ " + AOC_TH],
               "ตอนนี้ใส่เงินไปเท่าไหร่ และชวนใครเข้าไปแล้วหรือยังคะ"),
        "en": ("Be careful — schemes that pay you for bringing in new people are usually pyramid/Ponzi schemes, and the ones that collapse hardest are those that paid reliably for years.",
               ["Ask exactly which business profit pays the returns, and whether it's licensed by the financial regulator — if they can't show it, don't add more.",
                "Don't recruit anyone — when it collapses, the people you brought in are your own family and friends.",
                "If you want out, withdraw in steps and keep every transfer record. Report it to the regulator or police (Thailand: SEC 1207 · 1441)."],
               "How much have you put in, and have you invited anyone yet?"),
    },
}


# ══════════════════════════════════════════════════════════════════
# อีก 5 ภาษาของเว็บ (ja zh ko es vi) — แรงงานและนักท่องเที่ยวในไทยโดนหลอกแบบเดียวกัน
# เดิมเกือบทุกสถานการณ์ได้ Risk 0 · "tải ứng dụng từ link, file apk" ได้ "I'm sorry this happened" เป็นภาษาอังกฤษ
# หกสถานการณ์ที่เจอบ่อยที่สุด · ที่เหลือ (เช่าซิม ข่าวลือธนาคาร แชร์ลูกโซ่) ยังมีแค่ไทย/อังกฤษ
# ══════════════════════════════════════════════════════════════════
_I = r"[^\n]"
INTL = {
    "ja": (
        ("accessibility", 85, r"ユーザー補助|アクセシビリティ(?:の)?(?:権限|設定|サービス)"),
        ("courier_cash", 80, r"(?:警察|役所|銀行|検察|税務署|大使館)" + _I + r"{0,20}?(?:名乗|と言|から)" + _I + r"{0,40}?(?:現金|金を?買|ゴールド|ギフトカード|電子マネー|ビットコイン|取りに|受け取りに)|"
                             r"(?:現金|金|ゴールド)" + _I + r"{0,20}?(?:取りに(?:行く|来る)|受け取りに来)|ギフトカード" + _I + r"{0,20}?(?:番号|払え|支払|買って)"),
        ("apk", 70, r"(?<![A-Za-z])apk(?![A-Za-z])|リンクから" + _I + r"{0,10}?(?:アプリ|ファイル)" + _I + r"{0,10}?(?:インストール|ダウンロード)|(?:アプリ|ファイル)" + _I + r"{0,10}?(?:インストール|ダウンロード)" + _I + r"{0,12}?(?:リンク|SMS|メッセージ)"),
        ("otp_page", 70, r"(?:ロボットではない|CAPTCHA|キャプチャ)" + _I + r"{0,40}?(?:OTP|認証コード|ワンタイム|パスワード|暗証番号)|(?:リンク|サイト|ページ)" + _I + r"{0,20}?(?:OTP|認証コード|ワンタイムパスワード)(?:を)?入力"),
        ("sms_link", 65, r"(?:SMS|ショートメール|メッセージ|メール|LINE)" + _I + r"{0,40}?(?:罰金|反則金|未納|荷物|不在|還付|口座(?:が)?(?:凍結|停止)|ポイント)" + _I + r"{0,30}?(?:リンク|クリック|支払)|(?:罰金|未納|荷物|還付)" + _I + r"{0,20}?リンク"),
        ("friend_account", 65, r"(?:友達|友人|知人|家族|母|父|上司)" + _I + r"{0,16}?(?:LINE|メール|メッセージ|DM)" + _I + r"{0,20}?(?:お金|貸して|振り込|送金)"),
        ("sim_rent", 65, r"アプリ" + _I + r"{0,30}?(?:お金|報酬|円)" + _I + r"{0,30}?(?:SMS|ショートメール|メッセージ)(?:を)?送|SIM" + _I + r"{0,20}?(?:貸|レンタル)" + _I + r"{0,20}?(?:報酬|お金|円)"),
        ("bank_rumor", 50, r"銀行" + _I + r"{0,20}?(?:ハッキング|ハッキングされ|破綻|つぶれ|潰れ)" + _I + r"{0,30}?(?:引き出|下ろ|移)"),
        ("ponzi", 65, r"(?:紹介|勧誘)" + _I + r"{0,20}?(?:報酬|ボーナス|手数料)" + _I + r"{0,30}?(?:配当|投資|利回り)|(?:配当|投資)" + _I + r"{0,30}?(?:紹介|勧誘)" + _I + r"{0,20}?(?:報酬|ボーナス)"),
    ),
    "zh": (
        ("accessibility", 85, r"无障碍(?:权限|服务|功能)|無障礙(?:權限|服務)|辅助功能权限"),
        ("courier_cash", 80, r"(?:自称|冒充|说是|說是)" + _I + r"{0,10}?(?:警察|公安|银行|法院|检察院|大使馆)" + _I + r"{0,40}?(?:取现|现金|买黄金|买金|礼品卡|比特币|上门取|派人)|"
                             r"(?:现金|黄金|金条)" + _I + r"{0,20}?(?:上门取|派人(?:来)?取|来家里取)|礼品卡" + _I + r"{0,20}?(?:卡号|付款|买)"),
        ("apk", 70, r"(?<![A-Za-z])apk(?![A-Za-z])|(?:点|通过)链接" + _I + r"{0,10}?(?:下载|安装)(?:一个)?(?:app|应用|软件|APP)|(?:下载|安装)" + _I + r"{0,10}?(?:链接|短信)里的"),
        ("otp_page", 70, r"(?:我不是机器人|人机验证)" + _I + r"{0,30}?(?:验证码|密码|OTP)|(?:网页|链接|网站)" + _I + r"{0,16}?(?:输入|填)(?:验证码|OTP|密码)"),
        ("sms_link", 65, r"(?:短信|信息|消息|邮件)" + _I + r"{0,30}?(?:罚单|罚款|欠费|包裹|快递|退税|账户(?:被)?冻结|积分)" + _I + r"{0,30}?(?:链接|点击|付款)|(?:罚单|罚款|包裹|退税)" + _I + r"{0,16}?链接"),
        ("friend_account", 65, r"(?:朋友|亲戚|同学|妈妈|爸爸|老板|领导)" + _I + r"{0,12}?(?:微信|QQ|短信|邮件|LINE|私信)" + _I + r"{0,12}?(?:借钱|转账|汇款|要钱)"),
        ("sim_rent", 65, r"(?:应用|App|APP|软件)" + _I + r"{0,30}?(?:给钱|付钱|赚钱|元)" + _I + r"{0,30}?(?:发短信|用我的(?:卡|手机号|号码))|(?:出租|租)(?:手机卡|电话卡|SIM)"),
        ("bank_rumor", 50, r"银行" + _I + r"{0,20}?(?:被黑|被攻击|倒闭|要倒)" + _I + r"{0,30}?(?:取钱|取出|转走|提现)"),
        ("ponzi", 65, r"(?:拉人|发展下线|介绍人)" + _I + r"{0,20}?(?:提成|奖金|返利)|(?:分红|收益|投资)" + _I + r"{0,30}?(?:拉人|下线)"),
    ),
    "ko": (
        ("accessibility", 85, r"접근성\s*(?:권한|서비스|설정)"),
        ("courier_cash", 80, r"(?:경찰|검찰|금감원|은행|대사관)" + _I + r"{0,20}?(?:이라면서|이라며|사칭|이라고)" + _I + r"{0,40}?(?:현금|금을?\s*사|상품권|비트코인|가지러|찾아)|"
                             r"(?:현금|금|골드바)" + _I + r"{0,20}?(?:가지러\s*온|받으러\s*온|수거)|상품권" + _I + r"{0,20}?(?:번호|사서|보내)"),
        ("apk", 70, r"(?<![A-Za-z])apk(?![A-Za-z])|링크로" + _I + r"{0,10}?(?:앱|어플|파일)" + _I + r"{0,8}?(?:설치|다운)"),
        ("otp_page", 70, r"(?:로봇이\s*아닙니다|캡차)" + _I + r"{0,30}?(?:인증번호|OTP|비밀번호)|(?:링크|사이트|페이지)" + _I + r"{0,16}?(?:인증번호|OTP)" + _I + r"{0,6}?입력"),
        ("sms_link", 65, r"(?:문자|메시지|메일|카톡)" + _I + r"{0,30}?(?:벌금|과태료|미납|택배|환급|계좌\s*정지|포인트)" + _I + r"{0,30}?(?:링크|클릭|내래|납부)|(?:벌금|과태료|택배|환급)" + _I + r"{0,16}?링크"),
        ("friend_account", 65, r"(?:친구|지인|가족|엄마|아빠|딸|아들|상사)" + _I + r"{0,10}?(?:카톡|문자|메시지|메일|DM)" + _I + r"{0,16}?(?:돈|빌려|송금|이체)"),
        ("sim_rent", 65, r"(?:앱|어플)" + _I + r"{0,30}?(?:돈|원|보상)" + _I + r"{0,30}?(?:문자|SMS)(?:를)?\s*보내|(?:앱|어플)" + _I + r"{0,20}?(?:문자|SMS)" + _I + r"{0,20}?(?:\d+\s*원|돈)" + _I + r"{0,6}?준|(?:유심|폰|번호)\s*(?:빌려|대여)" + _I + r"{0,20}?(?:돈|원)"),
        ("bank_rumor", 50, r"은행" + _I + r"{0,20}?(?:해킹|파산|망한)" + _I + r"{0,30}?(?:인출|빼|옮)"),
        ("ponzi", 65, r"(?:지인|사람)\s*(?:소개|모집|데려오)" + _I + r"{0,20}?(?:수당|보너스|수수료)|(?:배당|수익|투자)" + _I + r"{0,30}?(?:모집|다단계|소개\s*수당)|다단계"),
    ),
    "es": (
        ("accessibility", 85, r"(?:permiso|servicio)s?\s+de\s+accesibilidad"),
        ("courier_cash", 80, r"(?:supuesto|dice\s+ser|se\s+hace\s+pasar\s+por|dijo\s+ser)" + _I + r"{0,30}?(?:polic[ií]a|banco|fiscal|embajada)" + _I + r"{0,60}?(?:efectivo|oro|tarjetas?\s+de\s+regalo|bitcoin|recoger)|"
                             r"(?:efectivo|oro|dinero)" + _I + r"{0,30}?(?:vendr[áa]n?\s+a\s+recoger|pasar[áa]n?\s+a\s+(?:buscar|recoger))|tarjetas?\s+de\s+regalo" + _I + r"{0,30}?(?:c[óo]digo|pagar|polic|multa)"),
        ("apk", 70, r"(?<![A-Za-z])apk(?![A-Za-z])|instalar\s+(?:una\s+)?app\s+desde\s+(?:un|el)\s+enlace|enlace" + _I + r"{0,20}?(?:descargar|instalar)\s+(?:una\s+)?(?:app|aplicaci[óo]n)"),
        ("otp_page", 70, r"no\s+soy\s+un\s+robot" + _I + r"{0,40}?(?:c[óo]digo|otp|contraseña)|(?:enlace|p[áa]gina|sitio)" + _I + r"{0,30}?(?:ped[ií]a|pide|meter|introducir|poner)\s+(?:el\s+)?(?:c[óo]digo|otp)"),
        ("sms_link", 65, r"(?:sms|mensaje|correo|whatsapp)" + _I + r"{0,40}?(?:multa|peaje|paquete|env[ií]o|devoluci[óo]n|reembolso|cuenta\s+(?:bloqueada|suspendida)|puntos)" + _I + r"{0,40}?(?:enlace|link|pagar|clic)"),
        ("friend_account", 65, r"(?:amig[oa]|familiar|prim[oa]|jefe|mam[áa]|pap[áa])" + _I + r"{0,20}?(?:whatsapp|mensaje|correo|escribi[óo]|dm)" + _I + r"{0,24}?(?:dinero|prestad|transfer)"),
        ("sim_rent", 65, r"app" + _I + r"{0,30}?(?:paga|pagan|dinero)" + _I + r"{0,30}?(?:enviar|mandar)\s+(?:sms|mensajes)|alquil\w*\s+(?:mi\s+)?(?:sim|chip|n[úu]mero)"),
        ("bank_rumor", 50, r"banco" + _I + r"{0,30}?(?:hackead|quebr|en\s+quiebra|colaps)" + _I + r"{0,40}?(?:sacar|retirar|mover)"),
        ("ponzi", 65, r"(?:recluta\w*|tra(?:er|es|e|igas|igo)|mete\w*)\s+(?:gente|personas|a\s+m[áa]s)" + _I + r"{0,30}?(?:comisi[óo]n|bono|ganas)|(?:pir[áa]mide|esquema\s+ponzi)"),
    ),
    "vi": (
        ("accessibility", 85, r"quyền\s+(?:trợ\s+năng|hỗ\s+trợ\s+tiếp\s+cận)"),
        ("courier_cash", 80, r"(?:xưng\s+là|giả\s+danh|tự\s+nhận\s+là|mạo\s+danh)" + _I + r"{0,20}?(?:công\s+an|cảnh\s+sát|ngân\s+hàng|tòa\s+án|đại\s+sứ\s+quán)" + _I + r"{0,50}?(?:tiền\s+mặt|mua\s+vàng|thẻ\s+quà|bitcoin|đến\s+nhà\s+lấy|cho\s+người\s+đến)|"
                             r"(?:tiền\s+mặt|vàng)" + _I + r"{0,20}?(?:đến\s+nhà\s+lấy|cho\s+người\s+(?:đến|tới)\s+lấy)"),
        ("apk", 70, r"(?<![A-Za-z])apk(?![A-Za-z])|(?:tải|cài(?:\s+đặt)?)\s+(?:ứng\s+dụng|app|file)" + _I + r"{0,10}?(?:từ|qua)\s+(?:link|đường\s+link|tin\s+nhắn)"),
        ("otp_page", 70, r"không\s+phải\s+(?:là\s+)?robot" + _I + r"{0,30}?(?:otp|mã)|(?:link|trang)" + _I + r"{0,20}?(?:nhập|điền)\s+(?:mã\s+)?otp"),
        ("sms_link", 65, r"(?:tin\s+nhắn|sms|email|zalo)" + _I + r"{0,30}?(?:phạt\s+nguội|phạt|nộp\s+phạt|bưu\s+kiện|hoàn\s+thuế|tài\s+khoản\s+bị\s+khóa|điểm)" + _I + r"{0,30}?(?:link|bấm|nhấn|nộp)"),
        ("friend_account", 65, r"(?:bạn|người\s+thân|anh|chị|em|mẹ|bố|sếp)" + _I + r"{0,12}?(?:nhắn|zalo|messenger|facebook|email)" + _I + r"{0,20}?(?:mượn\s+tiền|vay\s+tiền|chuyển\s+tiền)"),
        ("sim_rent", 65, r"(?:app|ứng\s+dụng)" + _I + r"{0,30}?(?:trả|được)\s+(?:tiền|\d+)" + _I + r"{0,30}?(?:gửi\s+tin\s+nhắn|gửi\s+sms|dùng\s+sim)|cho\s+thuê\s+sim"),
        ("bank_rumor", 50, r"ngân\s+hàng" + _I + r"{0,30}?(?:bị\s+hack|phá\s+sản|sập)" + _I + r"{0,40}?(?:rút|chuyển)\s+(?:tiền|hết)"),
        ("ponzi", 65, r"(?:rủ|kéo|giới\s+thiệu)\s+(?:thêm\s+)?(?:người|thành\s+viên)" + _I + r"{0,30}?(?:hoa\s+hồng|thưởng)|đa\s+cấp"),
    ),
}
_INTL_RX = {lg: [(k, r, re.compile(p, re.I)) for k, r, p in rows] for lg, rows in INTL.items()}


def cyber_kind_intl(text) -> tuple | None:
    from core.mood_intl import mood_lang
    t = str(text or "")
    lg = mood_lang(t)
    if lg not in _INTL_RX:
        return None
    for kind, risk, rx in _INTL_RX[lg]:
        if rx.search(t):
            return kind, risk
    return None


AOC_LINE = {
    "ja": "タイ：1441（サイバー警察 AOC・24時間）",
    "zh": "泰国：1441（网络警察 AOC，24小时）",
    "ko": "태국: 1441 (사이버 경찰 AOC, 24시간)",
    "es": "Tailandia: 1441 (policía cibernética AOC, 24 h)",
    "vi": "Thái Lan: 1441 (cảnh sát mạng AOC, 24 giờ)",
}
REPLY_INTL = {
    "accessibility": {
        "ja": ("今すぐ対応が必要です — その権限があると、アプリは入力するすべて（銀行の暗証番号も）を見て、代わりに操作できます。",
               ["すぐに機内モードにしてください（モバイルデータとWi-Fiを切る）。", "別の電話から、このスマホに入っている銀行すべてに連絡し、口座やアプリを止めてもらってください。" + AOC_LINE["ja"], "そのアプリを削除し（できなければ先にユーザー補助をオフ）、別の端末から銀行とメールのパスワードを変えてください。"],
               "もうお金が引き出されていますか？"),
        "zh": ("现在很紧急 — 有了这个权限，应用能看到你输入的一切（包括银行密码），还能替你操作。",
               ["马上开飞行模式，断开数据和 Wi-Fi。", "用另一部手机打给手机里所有银行，冻结账户或应用。" + AOC_LINE["zh"], "删除那个应用（删不掉就先关掉无障碍权限），再用别的设备改银行和邮箱密码。"],
               "钱已经被转走了吗？"),
        "ko": ("지금 급해요 — 그 권한이 있으면 앱이 입력하는 모든 것(은행 비밀번호까지)을 보고 대신 조작할 수 있어요.",
               ["바로 비행기 모드를 켜서 데이터와 와이파이를 끊으세요.", "다른 전화로 이 폰에 있는 모든 은행에 연락해 계좌나 앱을 정지해 달라고 하세요. " + AOC_LINE["ko"], "그 앱을 삭제하고(안 되면 접근성 권한부터 끄고), 다른 기기에서 은행·메일 비밀번호를 바꾸세요."],
               "이미 돈이 빠져나갔나요?"),
        "es": ("Es urgente — con ese permiso la app ve todo lo que escribes (también tus claves del banco) y puede actuar por ti.",
               ["Activa ya el modo avión (sin datos ni Wi-Fi).", "Desde otro teléfono, llama a cada banco que tengas en este móvil y pide bloquear la cuenta o la app. " + AOC_LINE["es"], "Borra esa app (si no puedes, quita primero el permiso de accesibilidad) y cambia las contraseñas del banco y del correo desde otro dispositivo."],
               "¿Ya ha salido dinero de tu cuenta?"),
        "vi": ("Việc này rất gấp — với quyền đó, ứng dụng thấy mọi thứ bạn nhập (cả mật khẩu ngân hàng) và có thể thao tác thay bạn.",
               ["Bật ngay chế độ máy bay (tắt dữ liệu và Wi-Fi).", "Dùng điện thoại khác gọi cho mọi ngân hàng có app trên máy này, yêu cầu khóa tài khoản hoặc app. " + AOC_LINE["vi"], "Xóa ứng dụng đó (nếu không xóa được, tắt quyền trợ năng trước), rồi đổi mật khẩu ngân hàng và email từ thiết bị khác."],
               "Tiền đã bị chuyển đi chưa?"),
    },
    "courier_cash": {
        "ja": ("これは詐欺の手口です — 本物の警察や役所は、現金を下ろして金やギフトカードを買えとは言いませんし、家に受け取りにも来ません。",
               ["今は何も下ろさず、渡さず、「受け取りに来た」人にドアを開けないでください。", "電話を切り、公式の番号を自分で調べてかけ直してください。" + AOC_LINE["ja"] + " · 警察 191", "もう渡してしまったら、すぐに 1441 と警察へ。番号・メッセージ・送られてきた身分証の写真を残してください。"],
               "もう現金や金、カード番号を渡しましたか？"),
        "zh": ("这是诈骗手法 — 真正的警察或政府部门不会让你取现金买黄金、买礼品卡，也不会派人上门收钱。",
               ["先停下，不要再取钱或交出任何东西，也不要给“上门取”的人开门。", "挂断电话，自己查官方号码再打回去核实。" + AOC_LINE["zh"] + " · 报警 191", "如果已经给了，马上打 1441 并报警，保留号码、聊天记录和对方发来的“证件”照片。"],
               "你已经交出现金、黄金或卡号了吗？"),
        "ko": ("이건 사기 수법이에요 — 진짜 경찰이나 기관은 현금을 찾아 금이나 상품권을 사라고 하지 않고, 집으로 받으러 오지도 않아요.",
               ["지금은 아무것도 찾거나 건네지 말고, \"받으러 온\" 사람에게 문을 열지 마세요.", "전화를 끊고 공식 번호를 직접 찾아 다시 확인하세요. " + AOC_LINE["ko"] + " · 경찰 191", "이미 건넸다면 바로 1441과 경찰에 신고하고, 번호·메시지·받은 신분증 사진을 남겨 두세요."],
               "이미 현금이나 금, 상품권 번호를 건넸나요?"),
        "es": ("Es una estafa — la policía real nunca te pide sacar efectivo para comprar oro o tarjetas regalo, ni manda a nadie a recoger dinero a tu casa.",
               ["Para: no saques ni entregues nada más, y no abras la puerta a quien venga a \"recoger\".", "Cuelga y llama tú al número oficial para comprobarlo. " + AOC_LINE["es"] + " · Policía 191", "Si ya entregaste algo, llama ya al 1441 y a la policía, y guarda números, mensajes y las fotos de \"credenciales\" que te enviaron."],
               "¿Ya entregaste efectivo, oro o códigos de tarjetas?"),
        "vi": ("Đây là chiêu lừa đảo — công an thật không bao giờ bảo rút tiền mặt mua vàng hay thẻ quà tặng, và không cho người đến nhà lấy tiền.",
               ["Dừng lại: đừng rút hay giao thêm gì, và đừng mở cửa cho người \"đến lấy\".", "Cúp máy, tự tìm số chính thức rồi gọi lại để xác minh. " + AOC_LINE["vi"] + " · Cảnh sát 191", "Nếu đã giao, gọi ngay 1441 và báo cảnh sát, giữ lại số điện thoại, tin nhắn và ảnh \"giấy tờ\" họ gửi."],
               "Bạn đã giao tiền mặt, vàng hay mã thẻ chưa?"),
    },
    "apk": {
        "ja": ("インストールしないでください — リンクや .apk で送られてくるアプリは、銀行アプリからお金を盗む一番の手口です（Google Play そっくりでも）。",
               ["そのページは閉じて、自分で開いた Play ストア / App Store からだけ入れてください。", "もう入れてしまったら：機内モードにして削除。「ユーザー補助」の許可は絶対にしないでください。", "入れた後に銀行アプリを開いたなら、銀行に確認を。" + AOC_LINE["ja"]],
               "もうインストールしましたか？"),
        "zh": ("不要安装 — 通过链接或 .apk 发来的应用，是盗取银行 App 里钱的主要手法（就算长得像 Google Play）。",
               ["关掉那个页面，只从自己打开的应用商店安装。", "如果已经装了：开飞行模式、删除它，千万不要给它“无障碍”权限。", "装完后打开过银行 App 的话，请联系银行检查。" + AOC_LINE["zh"]],
               "你已经安装了吗？"),
        "ko": ("설치하지 마세요 — 링크나 .apk로 보내는 앱은 은행 앱에서 돈을 빼가는 대표적인 수법이에요(구글 플레이처럼 보여도요).",
               ["그 페이지를 닫고, 직접 연 플레이 스토어/앱 스토어에서만 설치하세요.", "이미 설치했다면: 비행기 모드 → 삭제. \"접근성\" 권한은 절대 주지 마세요.", "설치 후 은행 앱을 열었다면 은행에 확인하세요. " + AOC_LINE["ko"]],
               "이미 설치했나요?"),
        "es": ("No la instales — las apps que llegan por enlace o como .apk son la forma principal de vaciar apps del banco, aunque parezcan Google Play.",
               ["Cierra la página e instala solo desde la Play Store o App Store que abras tú.", "Si ya la instalaste: modo avión y bórrala. Nunca le des permiso de \"accesibilidad\".", "Si abriste el banco después de instalarla, llama al banco para revisar. " + AOC_LINE["es"]],
               "¿Ya la instalaste?"),
        "vi": ("Đừng cài đặt — ứng dụng gửi qua link hoặc file .apk là cách chính để rút sạch tiền trong app ngân hàng, dù trông giống Google Play.",
               ["Đóng trang đó, chỉ cài từ Play Store / App Store do bạn tự mở.", "Nếu đã cài: bật chế độ máy bay và xóa ngay. Tuyệt đối không cấp quyền \"trợ năng\".", "Nếu đã mở app ngân hàng sau khi cài, hãy gọi ngân hàng kiểm tra. " + AOC_LINE["vi"]],
               "Bạn đã cài chưa?"),
    },
    "otp_page": {
        "ja": ("入力する前に止まってください —「ロボットではありません」の確認は本物のサイトの証明になりません。詐欺側が入れていて、打つ文字をリアルタイムで見ています。",
               ["リンクから開いたページでは OTP やパスワードを入れないでください。閉じて、アプリや自分で入力したアドレスから開き直しましょう。", "もう入力したなら、本物のアプリからすぐパスワードを変え、お金の口座なら銀行へ。", "リンクは残して通報を。" + AOC_LINE["ja"]],
               "もう何か入力しましたか？"),
        "zh": ("先别输入 —“我不是机器人”验证不能证明网站是真的，骗子自己加上去的，你输入的每个字他们都能实时看到。",
               ["不要在从链接打开的网页里输入验证码或密码，关掉后从官方 App 或自己输入网址进入。", "如果已经输入，马上用真的 App 改密码；是钱的账户就联系银行。", "保留链接去举报。" + AOC_LINE["zh"]],
               "你已经输入了什么吗？"),
        "ko": ("입력하기 전에 멈추세요 — \"로봇이 아닙니다\" 확인은 진짜 사이트라는 증거가 아니에요. 사기범이 넣어 둔 것이고, 입력하는 글자를 실시간으로 봐요.",
               ["링크로 연 페이지에서는 인증번호나 비밀번호를 넣지 마세요. 닫고 앱이나 직접 입력한 주소로 다시 여세요.", "이미 입력했다면 진짜 앱에서 바로 비밀번호를 바꾸고, 돈 계좌라면 은행에 연락하세요.", "링크는 남겨서 신고하세요. " + AOC_LINE["ko"]],
               "이미 뭔가 입력했나요?"),
        "es": ("Para antes de escribir — un \"no soy un robot\" no prueba que el sitio sea real. Lo ponen los estafadores, y ven cada letra que escribes en directo.",
               ["No metas un OTP ni contraseñas en una página abierta desde un enlace: ciérrala y entra por la app o escribiendo tú la dirección.", "Si ya lo pusiste, cambia la contraseña desde la app real y llama al banco si es una cuenta de dinero.", "Guarda el enlace para denunciarlo. " + AOC_LINE["es"]],
               "¿Ya escribiste algo?"),
        "vi": ("Dừng lại trước khi nhập — ô \"tôi không phải robot\" không chứng minh trang là thật. Kẻ lừa đảo tự gắn vào và thấy từng ký tự bạn gõ.",
               ["Đừng nhập OTP hay mật khẩu ở trang mở từ link — đóng lại và vào bằng app hoặc tự gõ địa chỉ.", "Nếu đã nhập, đổi mật khẩu ngay từ app thật và gọi ngân hàng nếu là tài khoản tiền.", "Giữ lại link để báo cáo. " + AOC_LINE["vi"]],
               "Bạn đã nhập gì chưa?"),
    },
    "sms_link": {
        "ja": ("まだリンクを押さないでください — 罰金・荷物・還付・口座確認を急がせるメッセージは、詐欺の一番の入口です。",
               ["リンクを押さず、書かれた番号にもかけ直さず、公式アプリや自分で調べたサイトで確認してください。", "本物の機関はアプリを入れさせるリンクを送らず、リンク先で OTP を求めません。", "もう押したり入力したりしたら、パスワードを変えて銀行に連絡を。" + AOC_LINE["ja"]],
               "もうリンクを押したり、何か入力したりしましたか？"),
        "zh": ("先别点链接 — 催你交罚款、领包裹、退税、核实账户的短信，是诈骗最主要的入口。",
               ["不点链接，也不回拨短信里的号码，用官方 App 或自己查的网站核实。", "真的机构不会发链接让你装 App，也不会在链接页面要验证码。", "如果已经点了或输入了信息，改密码并联系银行。" + AOC_LINE["zh"]],
               "你已经点链接或输入什么了吗？"),
        "ko": ("아직 링크를 누르지 마세요 — 벌금·택배·환급·계좌 확인을 재촉하는 문자는 사기의 대표적인 입구예요.",
               ["링크를 누르지 말고 문자 속 번호로도 전화하지 말고, 공식 앱이나 직접 찾은 사이트에서 확인하세요.", "진짜 기관은 앱 설치 링크를 보내지 않고, 링크 페이지에서 인증번호를 묻지 않아요.", "이미 눌렀거나 입력했다면 비밀번호를 바꾸고 은행에 연락하세요. " + AOC_LINE["ko"]],
               "이미 링크를 눌렀거나 뭔가 입력했나요?"),
        "es": ("No toques el enlace todavía — los mensajes que te apuran con multas, peajes, paquetes, reembolsos o revisar tu cuenta son la puerta principal de las estafas.",
               ["No toques el enlace ni llames al número del mensaje: compruébalo en la app oficial o en un sitio que busques tú.", "Las entidades reales no mandan enlaces para instalar apps ni piden un OTP en una página enlazada.", "Si ya tocaste o escribiste datos, cambia contraseñas y llama al banco. " + AOC_LINE["es"]],
               "¿Ya tocaste el enlace o escribiste algo?"),
        "vi": ("Khoan bấm link — tin nhắn hối thúc nộp phạt, nhận bưu kiện, hoàn thuế hay xác minh tài khoản là cửa ngõ chính của lừa đảo.",
               ["Đừng bấm link hay gọi lại số trong tin nhắn — kiểm tra qua app chính thức hoặc trang bạn tự tìm.", "Cơ quan thật không gửi link bắt cài app và không đòi OTP trên trang từ link.", "Nếu đã bấm hoặc nhập thông tin, đổi mật khẩu và gọi ngân hàng. " + AOC_LINE["vi"]],
               "Bạn đã bấm link hay nhập gì chưa?"),
    },
    "friend_account": {
        "ja": ("送る前に別の方法で確認してください — 友達のアカウントが乗っ取られていたら、同じチャットで「本当だよ」と返すのは詐欺師本人です。",
               ["もともと知っている番号に電話して、二人しか知らないことを聞いてください。", "連絡がつくまで送らないで。本当に困っている人も数分は待てます。", "偽物なら友達と共通の知人に知らせて。もう送ったら銀行と 1441 へ。"],
               "もう送金しましたか？"),
        "zh": ("转账前先换个方式确认 — 如果朋友的账号被盗了，在同一个聊天里回“是真的”的就是骗子本人。",
               ["打朋友原来的电话号码，问一件只有你们俩知道的事。", "联系上之前不要转。真有急事的人也能等几分钟。", "如果是假的，提醒朋友和共同好友。已经转了的话，马上联系银行和 1441。"],
               "你已经转账了吗？"),
        "ko": ("보내기 전에 다른 방법으로 확인하세요 — 친구 계정이 해킹됐다면, 같은 채팅에서 \"진짜야\"라고 답하는 건 사기범이에요.",
               ["원래 알고 있던 번호로 전화해서 둘만 아는 걸 물어보세요.", "연락이 닿기 전엔 보내지 마세요. 정말 급한 사람도 몇 분은 기다릴 수 있어요.", "가짜라면 친구와 지인들에게 알리고, 이미 보냈다면 바로 은행과 1441에 연락하세요."],
               "이미 돈을 보냈나요?"),
        "es": ("Comprueba por otra vía antes de enviar — si le robaron la cuenta a tu amigo, quien responde \"sí, soy yo\" en ese mismo chat es el estafador.",
               ["Llama a tu amigo al número que ya tenías y pregúntale algo que solo ustedes dos sepan.", "No envíes nada hasta hablar con él: una urgencia real puede esperar unos minutos.", "Si es falso, avisa a tu amigo y a conocidos en común. Si ya enviaste, llama al banco y al 1441."],
               "¿Ya enviaste dinero?"),
        "vi": ("Hãy kiểm tra bằng cách khác trước khi chuyển — nếu tài khoản của bạn bè bị chiếm, người trả lời \"đúng là mình\" trong cùng đoạn chat chính là kẻ lừa đảo.",
               ["Gọi vào số cũ bạn vẫn có và hỏi một chuyện chỉ hai người biết.", "Chưa liên lạc được thì đừng chuyển — người gặp chuyện thật vẫn chờ được vài phút.", "Nếu là giả, báo cho bạn và người quen chung. Nếu đã chuyển, gọi ngay ngân hàng và 1441."],
               "Bạn đã chuyển tiền chưa?"),
    },
}

# เช่าซิม · ข่าวลือธนาคาร · แชร์ลูกโซ่ — สามเรื่องที่ค้างจากรอบแรก
REPLY_INTL.update({
    "sim_rent": {
        "ja": ("このお金は受け取らないでください — SMSを送るだけでお金をくれるアプリは、あなたの番号で詐欺リンクを他の人に送っています。",
               ["今すぐアプリを削除して、使うのをやめてください。", "だまされた人にはあなたの番号が見えます。誰に誘われ、いくらもらったか記録を残してください。", "先に通報しておきましょう。" + AOC_LINE["ja"]],
               "そのアプリをどのくらい使っていましたか？"),
        "zh": ("请不要拿这笔钱 — 付钱让你帮忙发短信的 App，是在用你的号码给别人发诈骗链接。",
               ["马上删掉 App，停止使用。", "被骗的人看到的是你的号码，你可能被调查或停号 — 保留是谁介绍的、收了多少钱的记录。", "先主动报备。" + AOC_LINE["zh"]],
               "这个 App 在你手机上用了多久？"),
        "ko": ("이 돈은 받지 마세요 — 문자만 보내 주면 돈을 주는 앱은 당신 번호로 다른 사람들에게 사기 링크를 보내고 있어요.",
               ["지금 바로 앱을 지우고 사용을 멈추세요.", "피해자에게는 당신 번호가 보여요. 누가 권했는지, 얼마를 받았는지 기록을 남겨 두세요.", "먼저 신고해 두세요. " + AOC_LINE["ko"]],
               "그 앱을 얼마나 오래 썼나요?"),
        "es": ("Por favor no aceptes ese dinero — las apps que te pagan por enviar SMS usan tu número para mandar enlaces de estafa a otras personas.",
               ["Borra la app y deja de usarla ya, aunque pague poco.", "Las víctimas ven tu número y podrías ser investigado o perder la línea: guarda pruebas de quién te reclutó y cuánto te pagaron.", "Denúncialo tú primero. " + AOC_LINE["es"]],
               "¿Cuánto tiempo estuvo funcionando esa app en tu teléfono?"),
        "vi": ("Đừng nhận khoản tiền này — app trả tiền để gửi tin nhắn đang dùng số của bạn gửi link lừa đảo cho người khác.",
               ["Xóa app và ngừng dùng ngay, dù tiền ít.", "Nạn nhân thấy số của bạn, bạn có thể bị điều tra hoặc khóa số — giữ lại bằng chứng ai rủ bạn và được trả bao nhiêu.", "Hãy chủ động báo trước. " + AOC_LINE["vi"]],
               "App đó đã chạy trên máy bạn bao lâu?"),
    },
    "bank_rumor": {
        "ja": ("信じる前・シェアする前に確認を — 「銀行がハッキングされた」という噂で、システムが正常でも人が引き出しに殺到することがあります。",
               ["その銀行の公式アプリ・サイト・カード裏の番号で発表を確認してください。", "噂と一緒に来る「口座を確認」リンクは押さないで。不安につけ込む詐欺リンクのことが多いです。", "本当に見覚えのない取引があれば、銀行に止めてもらってください。" + AOC_LINE["ja"]],
               "その話はどこから来ましたか？銀行自身の発表ですか？"),
        "zh": ("先核实再相信、再转发 — “银行被黑”的谣言会让大家抢着取钱，哪怕系统一切正常。",
               ["到该银行的官方 App、网站或卡背面的电话核实公告。", "别点和谣言一起传来的“检查账户”链接 — 骗子最会利用恐慌。", "如果真的看到陌生交易，马上打银行冻结。" + AOC_LINE["zh"]],
               "这个消息是银行自己发的，还是大家转来的？"),
        "ko": ("믿거나 공유하기 전에 확인하세요 — \"은행이 해킹됐다\"는 소문은 시스템이 멀쩡해도 사람들이 돈을 빼러 몰리게 만들어요.",
               ["그 은행의 공식 앱·사이트·카드 뒷면 번호로 공지를 확인하세요.", "소문과 함께 오는 \"계좌 확인\" 링크는 누르지 마세요. 불안을 노리는 사기 링크인 경우가 많아요.", "정말 모르는 거래가 보이면 은행에 정지를 요청하세요. " + AOC_LINE["ko"]],
               "그 소식은 은행이 직접 발표한 건가요, 돌고 도는 건가요?"),
        "es": ("Comprueba antes de creer o compartir — un rumor de que un banco fue hackeado puede provocar retiros masivos aunque todo funcione bien.",
               ["Busca el aviso en los canales oficiales del banco o llama al número de tu tarjeta.", "No toques enlaces de \"revisa tu cuenta\" que llegan con el rumor: el pánico es lo que usan los estafadores.", "Si ves movimientos que no reconoces, llama al banco para bloquearlos. " + AOC_LINE["es"]],
               "¿De dónde salió la noticia: del propio banco o de mensajes reenviados?"),
        "vi": ("Kiểm tra trước khi tin hay chia sẻ — tin đồn ngân hàng bị hack có thể khiến mọi người đổ xô rút tiền dù hệ thống vẫn bình thường.",
               ["Xem thông báo trên kênh chính thức của ngân hàng hoặc gọi số sau thẻ.", "Đừng bấm link \"kiểm tra tài khoản\" đi kèm tin đồn — kẻ lừa đảo lợi dụng sự hoảng loạn.", "Nếu thật sự thấy giao dịch lạ, gọi ngân hàng để khóa. " + AOC_LINE["vi"]],
               "Tin này từ chính ngân hàng hay được chuyển tiếp?"),
    },
    "ponzi": {
        "ja": ("気をつけてください — 人を紹介するとお金がもらえる仕組みは、多くがねずみ講です。何年もちゃんと配当が出ていたものほど、崩れたときの被害が大きくなります。",
               ["配当がどの事業の利益から出ているのか、金融当局の許可があるのかを確認してください。答えられないなら、追加しないで。", "誰も誘わないでください。崩れたとき、誘った相手は自分の家族や友人です。", "抜けたいなら少しずつ、送金記録をすべて残して。" + AOC_LINE["ja"]],
               "いくら入れていて、もう誰か誘いましたか？"),
        "zh": ("请小心 — 靠拉人头赚钱的模式大多是传销/庞氏骗局，而且往往是那些“稳定分红好几年”的，崩盘时伤害最大。",
               ["问清楚分红来自哪门生意的利润，有没有金融监管部门的许可 — 答不出来就别再投。", "不要再拉任何人 — 崩盘时，你拉进来的是自己的亲友。", "想退出就分批取回，保留每一笔转账记录。" + AOC_LINE["zh"]],
               "你投了多少，已经拉过人了吗？"),
        "ko": ("조심하세요 — 사람을 데려오면 돈을 주는 구조는 대부분 다단계·폰지예요. 몇 년간 꼬박꼬박 배당을 주던 곳이 무너질 때 피해가 가장 커요.",
               ["배당이 어떤 사업의 이익에서 나오는지, 금융당국 인가가 있는지 물어보세요. 대답 못 하면 더 넣지 마세요.", "아무도 데려오지 마세요. 무너지면 데려온 사람은 내 가족과 친구예요.", "빠지고 싶다면 조금씩 회수하고 모든 송금 기록을 남겨 두세요. " + AOC_LINE["ko"]],
               "얼마를 넣었고, 이미 누구를 데려왔나요?"),
        "es": ("Ten cuidado — los esquemas que pagan por traer gente suelen ser pirámides o Ponzi, y los que más daño hacen al caer son los que pagaron bien durante años.",
               ["Pregunta de qué negocio salen las ganancias y si tienen licencia del regulador financiero; si no pueden responder, no pongas más.", "No invites a nadie: cuando cae, los que trajiste son tu familia y tus amigos.", "Si quieres salir, retira poco a poco y guarda cada comprobante. " + AOC_LINE["es"]],
               "¿Cuánto has puesto y ya invitaste a alguien?"),
        "vi": ("Hãy cẩn thận — mô hình trả tiền khi rủ thêm người thường là đa cấp/Ponzi, và những nơi trả lãi đều đặn nhiều năm lại gây thiệt hại lớn nhất khi sụp đổ.",
               ["Hỏi rõ lợi nhuận đến từ việc kinh doanh nào và có giấy phép của cơ quan quản lý tài chính không — không trả lời được thì đừng bỏ thêm.", "Đừng rủ ai — khi sụp, người bạn rủ vào chính là gia đình và bạn bè mình.", "Muốn rút thì rút dần và giữ mọi biên lai chuyển tiền. " + AOC_LINE["vi"]],
               "Bạn đã bỏ vào bao nhiêu và đã rủ ai chưa?"),
    },
})
