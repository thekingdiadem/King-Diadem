"""ชั้นตรวจที่สองของ assess() — จับเรื่องด่วนที่ชั้นแรกหลุด และลดเรื่องปกติที่ชั้นแรกตกใจเกินเหตุ

ที่มา: รอบตรวจ 302 ข้อความ (ภาษาพูด พิมพ์ผิด ข้อความลาตาย ค้ามนุษย์ หนี้นอกระบบ ฯลฯ)
หลุด 38 ข้อเป็น Risk 0 ทั้งหมด · ข้อความปกติ 12 ข้อถูกนับเป็นเรื่องด่วน

แยกเป็นตารางให้เติมได้ง่าย: UPGRADES (ยกเป็นเรื่องด่วน + หัวข้อที่ทำให้คำตอบมีเบอร์ที่ถูก)
และ DOWNGRADES (บริบทที่บอกว่าไม่ใช่เหตุตอนนี้) · ชั้นนี้ไม่ลดวิกฤตที่มีคำแทนตัวเองชัดเจน
"""
from __future__ import annotations

import re

_P = r"(?:ฉัน|หนู|ผม|เรา|กู|ตัวเอง|ดิฉัน)"
_WHO = r"(?:เพื่อน|แม่|พ่อ|ลูก|น้อง|พี่|ยาย|ตา|ปู่|ย่า|แฟน|สามี|ภรรยา|ผัว|เมีย|หลาน|คน)"

# (รูปแบบ, ชนิด) · ชนิด "crisis" = อยากตาย/ทำร้ายตัวเอง · อื่นๆ = ชื่อหัวข้อใน kernel_voice.TOPICS
UPGRADES: list[tuple[re.Pattern, str]] = [
    # ── อยากตาย: สถานที่/วิธี/ข้อความลา/พิมพ์ผิด ─────────────────────────
    (re.compile(r"(?:ดาดฟ้า|ขอบตึก|ริมสะพาน|บนสะพาน|ขอบระเบียง|หน้าผา)[^\n]{0,24}?(?:จะโดด|กำลังจะโดด|โดดลง|กระโดดลง|ลมแรงดี|มองลงไป|ข้างล่าง)"), "crisis"),   # "ยืนอยู่บนสะพาน" เฉยๆ กำกวม (ชมวิวก็ได้) — ต้องมีอีกคำบอก
    (re.compile(r"ถ่าน[^\n]{0,14}?(?:เผา|จุด)[^\n]{0,14}?(?:ในห้อง|ปิดห้อง|ห้องปิด)|(?:เผา|จุด)ถ่าน[^\n]{0,10}?(?:ในห้อง|ปิดห้อง)"), "crisis"),
    (re.compile(r"ข้อความสุดท้าย(?!ของ(?:วัน|ปี|เดือน))|^\s*ขอลาก่อน(?:นะ)?(?:ทุกคน)?\s*[.!…]*\s*$|"
                r"ฝากดูแล(?:แมว|หมา|ลูก|แม่|พ่อ|น้อง|ยาย)[^\n]{0,14}?(?:ไปละ|ไปแล้ว|ลาก่อน|ไม่อยู่แล้ว)|"
                r"ไปให้พ้นๆ?\s*จากโลก|ตายๆ\s*ไป(?:ซะ|เลย)?|อยาก(?:จะ)?ตายๆ|"
                r"(?<![ก-๙])อย(?:า)?กต(?:า)?ย(?![ก-๙])|อยาก\s+(?:จะ\s*)?ตาย(?!\S{0,3}\s*(?:ตอน|เมื่อ)แก่)|"
                rf"ถ้า{_P}ตาย(?:ไป)?(?:ก็)?คงไม่มีใคร|ถ้าไม่ตื่น(?:ขึ้น)?มาอีก(?:ก็)?คงดี|"
                r"ขังตัวเอง[^\n]{0,20}?(?:จะตาย|จะฆ่าตัวตาย|ไม่อยากอยู่)|"
                r"(?i:\bme\s+quiero\s+matar\b|\bquiero\s+matarme\b)"), "crisis"),
    # ── ร่างกาย/ยา/คลอด ───────────────────────────────────────────────
    (re.compile(rf"(?:ดูด|เสพ|กิน|เมา|ล้ม|ชัก|ยาบ้า|ไอซ์)[^\n]{{0,20}}?ไม่ตอบสนอง|{_WHO}[^\n]{{0,12}}?ไม่(?:ตอบสนอง|ได้สติ)"), "health_emergency"),
    (re.compile(r"กระท่อม[^\n]{0,20}?(?:ยาแก้ไอ|ยาแก้แพ้|ยานอนหลับ)[^\n]{0,24}?(?:ใจสั่น|ชัก|หายใจ|หมดสติ|อาเจียน|จะตาย)"), "overdose"),
    (re.compile(r"น้ำเดิน(?:แล้ว)?|น้ำคร่ำแตก|คลอดลูก(?:ที่บ้าน|ในรถ|เอง|คนเดียว)|(?:กำลัง|จะ)คลอด(?:แล้ว)?(?!\S{0,6}(?:เดือน|อาทิตย์|สัปดาห์|ปี))|ปวดท้องคลอด"), "health_emergency"),
    (re.compile(r"^\s*(?:เป็น)?ลมแดด\s*[!.]*\s*$|(?i:\bthere'?s a fire(?![a-z])|\b(?:my|the|our) (?:house|room|building|apartment|flat|kitchen) is on fire(?![a-z]))"), "health_emergency"),
    # ── ความรุนแรง / ลักพา / ทวงหนี้โหด ─────────────────────────────────
    (re.compile(r"ตัวประกัน|ซ้อม(?:เมีย|ผัว|ภรรยา|สามี|ลูก|แม่)|(?:สาด|ราด)น้ำกรด|น้ำกรด[^\n]{0,8}?(?:สาด|ราด)|"
                r"รุม(?:กระทืบ|ทำร้าย|ซ้อม|ตี)|ลักพาตัว|ถูกจับตัวไป|โดนจับตัวไป|"
                r"ตีด้วย(?:ไม้|เข็มขัด|สายไฟ|ไม้แขวน)[^\n]{0,12}?(?:จน)?(?:เลือด|ช้ำ|เขียว|บวม)|"
                r"ขู่(?:จะ)?(?:ตัดนิ้ว|เอาลูก|ฆ่า|ทำร้าย|เผาบ้าน)|ทุบรถ[^\n]{0,12}?ขู่|"
                r"(?i:\bsomeone (?:broke|is breaking|just broke) into\b|\bintruder\b|\b(?:is|keeps) chok(?:ing|es) me\b)"), "violence"),
    (re.compile(r"ชน(?:คน|เด็ก)[^\n]{0,20}?(?:นอนนิ่ง|ไม่ขยับ|ไม่ตอบ|เลือดออก|หมดสติ)|(?:นอนนิ่ง|ไม่ขยับ)[^\n]{0,10}?(?:หลังชน|ข้างถนน)"), "health_emergency"),
    (re.compile(r"มอมยา|รุมโทรม|โดนข่มขืน|ถูกข่มขืน"), "sexual_abuse"),
    (re.compile(r"(?:ลูก|น้อง|เด็ก|หลาน)[^\n]{0,24}?(?:รูปโป๊|ภาพโป๊|รูปเปลือย|คลิปโป๊)|(?:รูปโป๊|ภาพโป๊|รูปเปลือย)[^\n]{0,16}?(?:ลูก|น้อง|เด็ก|หลาน)"), "online_grooming"),
    (re.compile(r"ห้ามออก(?:ไปไหน|จากที่พัก)?[^\n]{0,12}?(?:ยึด|พาสปอร์ต)|(?:กัมพูชา|เมียวดี|ชายแดน|ต่างประเทศ)[^\n]{0,30}?(?:ยึดพาสปอร์ต|ห้ามออก|ออกไม่ได้)|ชวน(?:ไป)?ขายตัว|ให้(?:ไป)?ขายบริการ|ล่ามโซ่|โดนหลอกไปทำงาน[^\n]{0,20}?(?:ห้ามออก|ออกไม่ได้|กักตัว)"), "trafficking"),
    (re.compile(r"(?:แคป|แคปหน้าจอ|อัดคลิป|อัดหน้าจอ)[^\n]{0,20}?(?:เรียก(?:เงิน|ค่าไถ่)|ขู่)|เรียกค่าไถ่"), "sextortion"),
    (re.compile(r"แก๊งคอลเซ็นเตอร์|กู้หมวกกันน็อค|เงินกู้นอกระบบ[^\n]{0,30}?(?:ขู่|ทวงโหด|ทำร้าย)"), "threat"),
    (re.compile(r"ช่วยด้วย[^\n]{0,6}?ด่วน|ด่วน[^\n]{0,6}?ช่วยด้วย"), "help"),
    # ── เด็กและผู้สูงอายุ / มิจฉาชีพรูปแบบใหม่ (รอบตรวจ 20 ข้อความ หลุด 4) ─────────────────
    (re.compile(r"(?:ในเกม|ในแชท|ในไลน์|ในเน็ต|คนแปลกหน้า|ผู้ชาย|ผู้ใหญ่|เขา)[^\n]{0,20}?(?:รูป|คลิป|วิดีโอ)[^\n]{0,14}?(?:ตอนอาบน้ำ|อาบน้ำ|ในห้องน้ำ|โป๊|เปลือย|ไม่ใส่เสื้อ|ชุดชั้นใน)"), "online_grooming"),
    (re.compile(r"(?:หนู|ผม|ลูก|น้อง|เด็ก|ยาย|ตา)\S{0,4}หลงทาง|หลงทาง[^\n]{0,14}?(?:กลับบ้านไม่ได้|ไม่รู้จะกลับ|หาบ้านไม่เจอ)"), "stranded"),
    # กินยาผิดตัว/ซ้ำสองรอบ (ไม่ใช่ "กินยาผิดเวลา" ซึ่งมีคำตอบของตัวเอง และไม่ใช่คำถาม "...ไหม")
    (re.compile(r"กินยา(?:ผิดตัว|ผิดชนิด|ผิดขวด|ของคนอื่น)|กินยา[^\n]{0,16}?(?:ไปสองรอบ|ไป\s*2\s*รอบ|ซ้ำสองรอบ|เบิ้ลไป|ไปสองเท่า)(?![^\n]{0,10}?(?:ไหม|มั้ย|หรือเปล่า|ได้หรือ|\?))"), "overdose"),
    (re.compile(r"สแกน\s*(?:คิวอาร์|QR|qr)[^\n]{0,30}?(?:เงินหาย|ดูดเงิน|หมดบัญชี|เงินในบัญชีหาย)|(?:โดน|ถูก)ดูดเงิน|เงิน(?:ในบัญชี)?หาย(?:หมด|เกลี้ยง)(?:บัญชี)?"), "scam"),
    # ── ภาษาอังกฤษ: รอบตรวจ 30 ข้อความ หลุด 12 (รวม "i wanna die" และอาการหัวใจวาย) ──────────
    (re.compile(r"(?i)\bi\s*(?:wanna|want to|just want to|wish i could|'?d rather|would rather)\s+die\b(?!\s+(?:laughing|of (?:embarrassment|laughter|cringe)|happy|old|in my sleep at \d))|"
                r"\b(?:want|need)\s+(?:it all|everything|all of (?:this|it))\s+to\s+(?:end|stop)(?=\s*(?:$|[.!?,…]|now\b|already\b|forever\b|tonight\b|please\b|for good\b))|"
                r"\brope\b[^.\n]{0,30}?\b(?:keep looking|keep staring|staring at|ready|tied (?:it|a noose))\b"), "crisis"),
    (re.compile(r"(?i)\b(?:took|swallowed|taken|ate|downed)\b[^.\n]{0,24}?\b(?:bunch|handful|bottle|all|whole|lot|box)\b[^.\n]{0,16}?\b(?:pills|tablets|meds)\b|"
                r"\bswallowed\b[^.\n]{0,20}?\b(?:sleeping|pain(?:killer)?|my (?:mom|dad|mum)'?s?)\b[^.\n]{0,10}?\b(?:pills|tablets|meds)\b"), "overdose"),
    (re.compile(r"(?i)\bfell\b[^.\n]{0,16}?\bcan'?t get up\b|\bchest\s+(?:hurts|pain)\b[^.\n]{0,30}?\b(?:arm|jaw)\b[^.\n]{0,12}?\bnumb\b|"
                r"\bleft arm (?:is |feels )?numb\b|\b(?:bit|bitten) by a (?:snake|cobra|viper)\b|"
                r"\bsmoke everywhere\b|\bcan'?t get out\b[^.\n]{0,20}?\b(?:fire|smoke|flood|water)\b|\b(?:fire|smoke|flood(?:ing)?)\b[^.\n]{0,24}?\b(?:can'?t get out|trapped)\b"), "health_emergency"),
    (re.compile(r"(?i)\bmy (?:dad|father|stepdad|husband|boyfriend|brother|uncle|mom|mother)\s+(?:hit|beat|punched|kicked|stabbed|choked)\s+(?:my|me|her|him)\b"), "violence"),
    (re.compile(r"(?i)\b(?:from|say they'?re from|claims? to be (?:from )?)\s*(?:the )?bank\b[^.\n]{0,40}?\b(?:otp|one[- ]time (?:code|password)|verification code|pin|password)\b"), "scam"),
    (re.compile(r"(?i)\b(?:standing|sitting)\s+on\s+(?:the|a)\s+(?:bridge|ledge|roof(?:top)?)\b(?![^.\n]{0,30}?\b(?:view|photo|beautiful|sunset|watching))"), "soft_check"),

    # "I can't do this anymore" — มักแปลว่าหมดแรง แต่บางคนหมายถึงไม่อยากอยู่ → ถามไถ่เบาๆ พร้อมเบอร์ (ไม่ใช่โหมดวิกฤต)
    (re.compile(r"(?i)\bi\s+can'?t\s+(?:do|take|handle|keep doing)\s+(?:this|it)\s+any\s?more\b(?![^\n]{0,24}?\b(?:job|work|class|course|game|diet)\b)"), "soft_check"),
]
_UP_RISK = {"crisis": 95, "health_emergency": 85, "overdose": 85, "violence": 85, "sexual_abuse": 85,
            "trafficking": 85, "sextortion": 80, "threat": 70, "help": 60, "soft_check": 45, "online_grooming": 90, "scam": 60, "stranded": 60}

# บริบทที่บอกว่าคำน่ากลัวไม่ใช่เหตุตอนนี้ — ใช้เฉพาะเมื่อไม่มีคำบอกว่า "กำลังเกิด"
DOWNGRADES: list[tuple[re.Pattern, tuple]] = [
    (re.compile(r"อยาก(?:จะ)?ตาย(?:ตอน|เมื่อ)(?:แก่|อายุ\s*\d)|ตายอย่างสงบตอนแก่"), ("crisis",)),
    (re.compile(r"ทะเลแห่ง(?:ความ|รัก)|จมน้ำ(?:ตา|ในความ)"), ("health_emergency", "first_aid")),
    (re.compile(r"(?:ตอนเด็ก|เมื่อก่อน|สมัยก่อน|ปีที่แล้ว|หลายปีก่อน)[^\n]{0,10}?เคย[^\n]{0,24}?(?:ตอนนี้|แต่ตอนนี้)[^\n]{0,10}?(?:หาย|ดีขึ้น|ว่ายเป็น|ปกติ|ไม่เป็นไร)"),
     ("health_emergency", "first_aid", "violence")),
    (re.compile(r"ตีลูก[^\n]{0,8}?(?:แบด|ขนไก่|เทนนิส|กอล์ฟ|ปิงปอง|เบสบอล)|(?:ไม้แบด|ไม้เทนนิส|ไม้กอล์ฟ|ไม้ปิงปอง)"), ("violence",)),
    (re.compile(r"ไฟฟ้าสถิต"), ("first_aid", "health_emergency")),
]
_MONEY_GONE = re.compile(r"เงินหาย|ดูดเงิน|โอนไปแล้ว|ถอน(?:เงิน)?ไม่ได้|(?i:\bmoney (?:is )?(?:gone|stolen)\b|\bdrained\b)")
_TRAPPED = re.compile(r"ยึด(?:พาสปอร์ต|หนังสือเดินทาง|บัตร)|ห้ามออก|ออกไม่ได้|กักตัว|ขังไว้|ล่ามโซ่|ไม่ให้กลับ")
_NOW = re.compile(r"ตอนนี้\S{0,8}(?:หายใจ|ไม่|เลือด|ชัก)|เมื่อกี้|เดี๋ยวนี้|ช่วยด้วย|ด่วน|\b(?:now|right now|help)\b", re.I)


def apply(text: str, a: dict) -> dict:
    """คืน assessment ที่ปรับแล้ว (ไม่แก้ dict เดิม)"""
    if not isinstance(text, str) or not text:
        return a
    a = dict(a, topics=list(a.get("topics") or []))
    caught = a["crisis"] or a["text_risk"] >= 50 or bool(a.get("scam")) or bool(a.get("disaster"))

    if not _NOW.search(text):
        for rx, kinds in DOWNGRADES:
            if rx.search(text):
                if "crisis" in kinds and a["crisis"]:
                    a.update(crisis=False, text_risk=min(a["text_risk"], 20))
                drop = [k for k in kinds if k != "crisis"]
                if drop and any(t in drop for t in a["topics"]):
                    a["topics"] = [t for t in a["topics"] if t not in drop]
                    if not a["topics"] and not a["crisis"]:
                        a["text_risk"] = min(a["text_risk"], 20)
                caught = a["crisis"] or a["text_risk"] >= 50 or bool(a.get("scam")) or bool(a.get("disaster"))

    # ถูกหลอกไปทำงาน + ยึดพาสปอร์ต = ค้ามนุษย์ ไม่ใช่โดนโกงเงิน — เดิมได้คำตอบ "รีบทำตามนี้จะได้เงินคืน" ไม่มี 191
    if "trafficking" in a["topics"] and a.get("scam") and _TRAPPED.search(text):
        a["scam"] = []
        a["topics"] = ["trafficking"] + [t for t in a["topics"] if t != "trafficking"]
        a["text_risk"] = max(a["text_risk"], 85)
    first_risk = _UP_RISK.get(a["topics"][0], 0) if a["topics"] else 0
    for rx, kind in UPGRADES:
        if rx.search(text):
            # จับได้อยู่แล้ว: ยกขึ้นเฉพาะเมื่อเรื่องนี้ด่วนกว่าหัวข้อแรก (เบอร์ในคำตอบมาจากหัวข้อแรก)
            # "ขับรถชนเสาให้ตายๆไป" เคยได้ปฐมพยาบาลไม่มี 1323 · "เมาขับชนคน คนนอนนิ่ง" ได้ "อย่าขึ้นรถ"
            if caught and (a["crisis"] or (kind != "crisis" and (kind == (a["topics"] or [None])[0]
                                                                  or _UP_RISK[kind] <= max(first_risk, 75 if a["topics"] else 0)))):
                continue
            if kind == "crisis":
                a.update(crisis=True, text_risk=max(a["text_risk"], _UP_RISK[kind]))
            else:
                a["topics"] = [kind] + [t for t in a["topics"] if t != kind]
                # เงินหายไปแล้ว (สแกน QR แล้วถูกดูดเงิน) — ต้องได้คำตอบ "รีบแจ้งธนาคารวันนี้" ไม่ใช่ "อย่าเพิ่งทำตาม"
                if kind == "scam" and _MONEY_GONE.search(text):
                    a["scam"] = ["lost"]
                a["text_risk"] = max(a["text_risk"], _UP_RISK[kind])
            a["risk"] = max(a.get("risk", 0), a["text_risk"])
            a["risk_shown"] = max(a.get("risk_shown", 0), a["text_risk"])
            break
    return a
