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


# โมเดลสำรอง — ลองตัวถัดไปเฉพาะตอนที่โมเดลหลักใช้ไม่ได้ (ถูกเลิก/ไม่รองรับ) ไม่ใช่ตอนโควตาเต็ม เพื่อไม่ให้เสียเงินซ้ำ
IMAGE_GEN_FALLBACKS = [m.strip() for m in os.getenv("IMAGE_GEN_FALLBACKS", "gemini-2.5-flash-image").split(",") if m.strip()]


class ImageGenError(RuntimeError):
    """kind: quota · model · safety · auth · busy · other"""
    def __init__(self, kind: str, detail: str = ""):
        super().__init__(f"{kind}: {detail}"[:300])
        self.kind, self.detail = kind, detail


def classify(err) -> str:
    """แยกสาเหตุจากข้อความ error ของ Gemini — ใช้เลือกคำอธิบายให้ผู้ใช้ และบันทึกให้ผู้ดูแลเห็น"""
    if isinstance(err, ImageGenError):
        return err.kind
    e = str(err).lower()
    if any(k in e for k in ("429", "resource_exhausted", "resource exhausted", "quota", "rate limit")):
        return "quota"
    if any(k in e for k in ("404", "not_found", "not found", "not supported", "is not supported", "unsupported", "response modalit")):
        return "model"
    if any(k in e for k in ("safety", "blocked", "prohibited", "image_safety")):
        return "safety"
    if any(k in e for k in ("401", "403", "permission", "api key", "api_key", "unauthenticated", "billing")):
        return "auth"
    if any(k in e for k in ("500", "503", "unavailable", "overloaded", "high demand", "timeout", "timed out", "deadline")):
        return "busy"
    return "other"


def _extract(resp) -> tuple[bytes, str]:
    texts, reasons = [], []
    fb = getattr(resp, "prompt_feedback", None)
    if fb is not None and getattr(fb, "block_reason", None):
        raise ImageGenError("safety", f"prompt blocked: {fb.block_reason}")
    for cand in (getattr(resp, "candidates", None) or []):
        fr = getattr(cand, "finish_reason", None)
        if fr is not None:
            reasons.append(str(getattr(fr, "name", fr)))
        for part in (getattr(getattr(cand, "content", None), "parts", None) or []):
            inline = getattr(part, "inline_data", None)
            data = getattr(inline, "data", None) if inline else None
            if data:
                if isinstance(data, str):                  # บางรุ่นของไลบรารีคืน base64 เป็นข้อความ
                    data = base64.b64decode(data)
                return data, (getattr(inline, "mime_type", None) or "image/png")
            if getattr(part, "text", None):
                texts.append(part.text)
    why = " ".join(reasons).upper()
    if any(k in why for k in ("SAFETY", "PROHIBITED", "BLOCKLIST", "RECITATION", "IMAGE_OTHER")):
        raise ImageGenError("safety", why)
    # ได้แต่ข้อความกลับมา = โมเดลไม่ยอมวาดเรื่องนี้ (มักเป็นเหตุผลด้านเนื้อหา)
    raise ImageGenError("safety" if texts else "other", (why + " " + " ".join(texts))[:200] or "no image in response")


def generate(client, prompt: str, model: str = "") -> tuple[bytes, str]:
    """เรียกโมเดลสร้างภาพของ Gemini — คืน (bytes, mime) · ไม่ได้ภาพ = ImageGenError (ผู้เรียกคืนเครดิต)"""
    from google.genai import types as gt
    cfg = gt.GenerateContentConfig(response_modalities=["IMAGE", "TEXT"])
    models = []
    for m in [model or IMAGE_GEN_MODEL] + IMAGE_GEN_FALLBACKS:
        if m and m not in models:
            models.append(m)
    last = None
    for m in models:
        try:
            resp = client.models.generate_content(model=m, contents=_GUIDE + prompt, config=cfg)
        except Exception as e:
            kind = classify(e)
            last = ImageGenError(kind, f"{m}: {type(e).__name__}: {str(e)[:200]}")
            if kind == "model":
                continue                                   # โมเดลนี้ใช้ไม่ได้ → ลองตัวสำรอง
            raise last from e
        return _extract(resp)
    raise last or ImageGenError("model", "no image model configured")


# ข้อความที่ผู้ใช้เห็น — บอกตามจริงว่าเป็นที่ระบบหรือที่คำบรรยาย
USER_MESSAGE = {
    "quota":  ("ระบบสร้างภาพใช้ครบโควตาชั่วคราวค่ะ (ไม่เกี่ยวกับคำบรรยาย) — คืนเครดิตให้แล้ว ลองใหม่อีกสักพักนะคะ",
               "Image generation has hit its temporary quota (not your prompt) — credit refunded, please try again later."),
    "model":  ("ตอนนี้โมเดลสร้างภาพยังไม่พร้อมค่ะ (ไม่เกี่ยวกับคำบรรยาย) — คืนเครดิตให้แล้ว ทีมงานกำลังดูให้นะคะ",
               "The image model isn't available right now (not your prompt) — credit refunded."),
    "auth":   ("ระบบสร้างภาพยังเชื่อมต่อไม่ได้ค่ะ (ไม่เกี่ยวกับคำบรรยาย) — คืนเครดิตให้แล้ว ทีมงานกำลังดูให้นะคะ",
               "Image generation can't connect right now (not your prompt) — credit refunded."),
    "busy":   ("ระบบสร้างภาพยุ่งอยู่ค่ะ — คืนเครดิตให้แล้ว รอสักครู่แล้วลองใหม่ได้เลยนะคะ",
               "The image service is busy — credit refunded, please try again in a moment."),
    "safety": ("โมเดลไม่ยอมวาดภาพนี้ค่ะ — คืนเครดิตให้แล้ว ลองเปลี่ยนคำบรรยายดูนะคะ",
               "The model declined to draw this — credit refunded, try rewording your prompt."),
    "other":  ("สร้างภาพไม่สำเร็จค่ะ — คืนเครดิตให้แล้ว ลองใหม่อีกครั้งนะคะ",
               "Couldn't create the image — credit refunded, please try again."),
}


def data_url(data: bytes, mime: str) -> str:
    mime = mime if mime in ("image/png", "image/jpeg", "image/webp") else "image/png"
    return f"data:{mime};base64," + base64.b64encode(data).decode()
