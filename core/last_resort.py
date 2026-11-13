"""
core/last_resort.py — ชั้นสุดท้ายเมื่อทุกอย่างพัง (ไม่ import อะไรของระบบเลย)

ที่มา: Microsoft ล่มทั่วโลก 12–13 พ.ย. 2569 จากการตั้งค่าเซิร์ฟเวอร์หลังอัปเดต — โรงพยาบาลต้องยกเลิกการผ่าตัด
เจ้าของโปรเจกต์ให้ดูว่าเหตุแบบเดียวกันเกิดกับเราได้ตรงไหน ("ธรรมเหล่าใดเกิดแต่เหตุ")
ทดลองแล้ว: ถ้าตัวประเมินหรือสมการพังหลังอัปเดต และ AI ล่มพร้อมกัน คนที่พิมพ์ "อยากตาย" ได้ error 500 ไม่มีเบอร์เลย

ไฟล์นี้จึงไม่พึ่งโมดูลอื่นของระบบ ไม่ใช้ AI ไม่อ่านฐานข้อมูล — มีแค่ข้อความตายตัวกับการดูตัวอักษร
ถ้า /run พังด้วยเหตุใดก็ตาม ผู้ใช้ยังได้เบอร์ฉุกเฉินในภาษาของตัวเอง
"""
import re

LINES = {
    "th": "ขอโทษนะคะ ระบบขัดข้องชั่วคราว — ถ้าเป็นเรื่องด่วน โทรได้เลยไม่ต้องรอ:\n"
          "1669 เจ็บป่วยฉุกเฉิน · 191 ตำรวจ · 1323 สายด่วนสุขภาพจิต (ฟรี 24 ชม.) · 1300 ศูนย์ช่วยเหลือสังคม · 1441 ถูกหลอกออนไลน์\n"
          "ถ้าตอนนี้ไม่ปลอดภัย ไปอยู่ใกล้คนอื่นก่อนนะคะ แล้วลองพิมพ์มาใหม่อีกครั้ง",
    "en": "Sorry — the system is having a problem right now. If this is urgent, please call now, don't wait:\n"
          "In Thailand 1669 medical · 191 police · 1323 mental health (24h) · 1155 tourist police (English) · elsewhere your local emergency number (911 / 112) or findahelpline.com\n"
          "If you're not safe, get near other people first, then try writing again.",
    "ja": "申し訳ありません、システムが一時的に不調です。急ぎの場合はすぐに電話してください：\n"
          "タイ：1669 救急 · 191 警察 · 1323 心の相談（24時間）· 1155 観光警察 ／ 日本：119 · 110 · いのちの電話 0570-783-556",
    "zh": "抱歉，系统暂时出了问题。如果情况紧急，请马上打电话，不用等：\n"
          "泰国：1669 急救 · 191 报警 · 1323 心理援助（24小时）· 1155 旅游警察 ／ 中国：120 · 110 · 12356",
    "ko": "죄송해요, 시스템에 일시적인 문제가 있어요. 급한 일이라면 기다리지 말고 바로 전화하세요:\n"
          "태국: 1669 응급 · 191 경찰 · 1323 정신건강 상담(24시간) · 1155 관광경찰 ／ 한국: 119 · 112 · 109",
    "es": "Lo siento, el sistema tiene un problema ahora mismo. Si es urgente, llama ya, no esperes:\n"
          "Tailandia: 1669 emergencias · 191 policía · 1323 salud mental (24 h) · 1155 policía turística ／ España 112 · 024 ／ México 911",
    "vi": "Xin lỗi, hệ thống đang gặp sự cố. Nếu việc gấp, hãy gọi ngay, đừng chờ:\n"
          "Thái Lan: 1669 cấp cứu · 191 cảnh sát · 1323 sức khỏe tâm thần (24 giờ) · 1155 cảnh sát du lịch ／ Việt Nam: 115 · 113",
}
_VI = re.compile(r"[ăđơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]", re.I)
_ES = re.compile(r"[ñ¿¡áéíóú]|\b(?:quiero|estoy|tengo|ayuda|morir|no puedo)\b", re.I)


def lang(text) -> str:
    t = str(text or "")
    if re.search(r"[฀-๿]", t):
        return "th"
    if re.search(r"[가-힯]", t):
        return "ko"
    if re.search(r"[぀-ヿ]", t):
        return "ja"
    if re.search(r"[一-鿿]", t):
        return "zh"
    if len(_VI.findall(t)) >= 1:
        return "vi"
    if _ES.search(t):
        return "es"
    return "en" if re.search(r"[A-Za-z]", t) else "th"


def reply(text) -> str:
    return LINES[lang(text)]


# ── canary: ตรวจตอนเปิดเซิร์ฟเวอร์และที่ /health ว่าเรื่องวิกฤตยังได้เบอร์ทุกภาษา ──
# Microsoft ไม่รู้ตัวจนผู้ใช้ทั่วโลกเจอ — เราลองตอบข้อความวิกฤตเองก่อน ถ้าพังจะเห็นที่ /health ทันที
CANARY = {"th": "อยากตาย", "en": "i want to die", "ja": "死にたい", "zh": "我想死", "ko": "죽고 싶어", "es": "quiero morir", "vi": "tôi muốn chết"}
_NUM = re.compile(r"(?<!\d)(?:1323|1669|191|110|112|119|109|115|911|988)(?!\d)|findahelpline")


def canary() -> dict:
    """{"ok": bool, "failed": [ภาษาที่ไม่ได้เบอร์หรือพัง]}"""
    failed = []
    try:
        from core.kernel_voice import compose
    except Exception as e:
        return {"ok": False, "failed": ["import:" + type(e).__name__]}
    for lg, t in CANARY.items():
        try:
            if not _NUM.search(compose(t) or ""):
                failed.append(lg)
        except Exception as e:
            failed.append(f"{lg}:{type(e).__name__}")
    return {"ok": not failed, "failed": failed}
