"""โหมดสร้างภาพ — ผู้ใช้บอกภาพที่อยากได้ แล้วได้ภาพกลับมาในแชท

ใช้ key Gemini ตัวเดิม (โมเดลสร้างภาพ ตั้งได้ด้วย IMAGE_GEN_MODEL) · มีค่าใช้จ่ายต่อภาพจริง จึงต้องล็อกอินและหักเครดิต
ตัวกรองคำขอทำงานก่อนเรียก AI ทุกครั้ง — คำขอที่ไม่อนุญาตไม่เสียเงิน ไม่ถึงผู้ให้บริการ AI
"""
from __future__ import annotations

import base64
import os
import re

IMAGE_GEN_MODEL = os.getenv("IMAGE_GEN_MODEL", "gemini-2.5-flash-image").strip()
MAX_PROMPT = 1000

# (เหตุผลไทย, เหตุผลอังกฤษ, regex) — ปฏิเสธก่อนเรียก AI
_BLOCK = [
    ("ภาพทางเพศหรือภาพโป๊ สร้างไม่ได้ค่ะ", "Sexual or nude images can't be created",
     re.compile(r"โป๊|เปลือย|ไม่ใส่เสื้อผ้า|ลามก|อนาจาร|ร่วมเพศ|มีเซ็กส์|ทางเพศ|nsfw|nude|naked|porn|sexual|hentai|lingerie|topless|xxx", re.I)),
    ("ภาพที่ทำร้ายร่างกายหรือเลือดสาด สร้างไม่ได้ค่ะ", "Gory or violent images can't be created",
     re.compile(r"เลือดสาด|ตัดหัว|ชำแหละ|ศพ|ทรมาน|ฆ่า(?:คน|ตัว)|ยิงหัว|gore|behead|dismember|corpse|torture|massacre", re.I)),
    ("ภาพเอกสาร บัตร หรือเงินปลอม สร้างไม่ได้ค่ะ — อาจถูกเอาไปหลอกคนอื่น",
     "Fake documents, IDs or money can't be created — they could be used to deceive people",
     re.compile(r"บัตรประชาชน|บัตรประจำตัว|พาสปอร์ต|หนังสือเดินทาง|ใบขับขี่|สลิป(?:โอน)?|ใบเสร็จ|ใบกำกับภาษี|ธนบัตร|แบงก์(?:พัน|ร้อย)|เช็คเงินสด|ปริญญาบัตร|ใบรับรองแพทย์|ใบประกาศ|"
                r"\bid card\b|passport|driver'?s licen[cs]e|bank ?slip|receipt|invoice|banknote|counterfeit|diploma|medical certificate", re.I)),
    ("ภาพคนจริงที่ปลอมขึ้น (deepfake) สร้างไม่ได้ค่ะ — ลองบอกเป็นตัวละครที่คิดขึ้นเองแทนนะคะ",
     "Fake images of real people (deepfakes) can't be created — try an invented character instead",
     re.compile(r"deep ?fake|ดีพเฟค|หน้าเหมือน(?:ดารา|นักการเมือง|คนดัง)|ใส่หน้า|เอาหน้า\S{0,12}ไปใส่|face ?swap|สลับหน้า|ภาพหลุด|"
                r"นายก(?:รัฐมนตรี)?\S{0,6}(?:กำลัง|ถูก|โดน)|ประธานาธิบดี\S{0,6}(?:กำลัง|ถูก|โดน)", re.I)),
    ("ภาพเด็กในเรื่องแบบนี้สร้างไม่ได้ค่ะ", "Images like this of children can't be created",
     re.compile(r"(?:เด็ก|นักเรียน|child|kid|minor|loli)[^\n]{0,30}(?:เซ็กซี่|ยั่ว|ชุดว่ายน้ำ|sexy|seductive|bikini)", re.I)),
    ("ภาพวิธีทำอาวุธหรือระเบิด สร้างไม่ได้ค่ะ", "Instructions for weapons or explosives can't be created",
     re.compile(r"วิธี(?:ทำ|ประกอบ)(?:ระเบิด|ปืน|อาวุธ)|สูตร(?:ระเบิด|ยาพิษ)|how to (?:make|build) (?:a )?(?:bomb|gun|weapon)", re.I)),
]


def blocked(prompt: str):
    """คืน {"th","en"} ถ้าคำขอนี้สร้างไม่ได้ · None ถ้าสร้างได้"""
    p = str(prompt or "")
    for th, en, rx in _BLOCK:
        if rx.search(p):
            return {"th": th, "en": en}
    try:                                         # ข้อความวิกฤต (คิดทำร้ายตัวเอง ฯลฯ) — ไม่ใช่เวลาสร้างภาพ
        from core.kernel_voice import assess
        a = assess(p)
        if a.get("crisis") or "crisis" in (a.get("topics") or []):
            return {"th": "ดูเหมือนกำลังเจอเรื่องหนักอยู่ — ถ้าไม่ปลอดภัย โทร 1323 (สุขภาพจิต 24 ชม.) หรือ 1669 ได้ทันทีนะคะ "
                          "หรือสลับไปโหมดปรึกษา แล้วเล่าให้ LYLA ฟังก็ได้ค่ะ",
                    "en": "It sounds like you're going through something heavy — if you're not safe, call local emergency "
                          "services now (Thailand 1323 / 1669), or switch to Talk mode and tell LYLA."}
    except Exception:
        pass
    return None


_GUIDE = ("Create one high-quality image for this request. Do not add text, watermarks or logos unless the request asks for them. "
          "Do not depict real, identifiable people. Request: ")


def generate(client, prompt: str, model: str = "") -> tuple[bytes, str]:
    """เรียกโมเดลสร้างภาพของ Gemini — คืน (bytes, mime) · ไม่ได้ภาพ = RuntimeError (ผู้เรียกคืนเครดิต)"""
    from google.genai import types as gt
    cfg = gt.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
    resp = client.models.generate_content(model=model or IMAGE_GEN_MODEL, contents=_GUIDE + prompt, config=cfg)
    for cand in (getattr(resp, "candidates", None) or []):
        for part in (getattr(getattr(cand, "content", None), "parts", None) or []):
            inline = getattr(part, "inline_data", None)
            data = getattr(inline, "data", None) if inline else None
            if data:
                if isinstance(data, str):                  # บางรุ่นของไลบรารีคืน base64 เป็นข้อความ
                    data = base64.b64decode(data)
                return data, (getattr(inline, "mime_type", None) or "image/png")
    raise RuntimeError("no image in response")


def data_url(data: bytes, mime: str) -> str:
    mime = mime if mime in ("image/png", "image/jpeg", "image/webp") else "image/png"
    return f"data:{mime};base64," + base64.b64encode(data).decode()
