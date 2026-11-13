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
