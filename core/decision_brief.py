"""สรุปการตัดสินใจแบบไม่ใช้ AI — ให้สภา 6 เสียงและ VEGA ตอบจาก "เรื่องจริงของผู้ใช้" ไม่ใช่ประโยคกลางๆ

เจ้าของโปรเจกต์: "สภาคำตอบผิวเผินมากๆ เวก้าด้วย" — เดิมแต่ละเสียงพูดประโยคที่ใช้กับคำถามไหนก็ได้
("เงินน้อยไม่ได้แปลว่าไม่มีทาง" กับคนที่มีเงินเก็บ 300,000) และไม่มีใครใช้ตัวเลขที่ผู้ใช้ให้มาเลย

ทำอะไร:
  1. ดึงข้อเท็จจริง: รายได้/เดือน · รายจ่าย/เดือน · เงินเก็บ · เงินลงทุน · หนี้ · ชนิดการตัดสินใจ · คนที่ได้รับผล · สิ่งที่ย้อนกลับยาก
  2. คำนวณ (ตรวจได้ ค่าเดิมได้ผลเดิม): เงินอยู่ได้กี่เดือนถ้ารายได้หยุด · ลงทุนได้สูงสุดเท่าไหร่โดยยังเหลือสำรอง 6 เดือน
  3. สร้างประตู "เดินหน้าได้เมื่อ" และ "หยุดเมื่อ" จากตัวเลขจริง — ใช้ทั้งในคำตอบไม่มี AI และส่งให้ AI เป็นบริบท

ข้อสมมติทุกข้อพูดออกมาตรงๆ ในคำตอบ (เช่น "ถ้าใช้จ่ายราวเงินเดือน") ไม่ซ่อน
"""
from __future__ import annotations

import re

FLOOR_MONTHS = 6          # เงินสำรองที่ไม่ควรแตะ (FATE K4 Floor Before Growth · แนวทางเงินฉุกเฉิน 3–6 เดือน ใช้ขอบบน)

_NUM = r"(\d[\d,]*(?:\.\d+)?)\s*(พัน|หมื่น|แสน|ล้าน|k|K|m|M)?"
_MULT = {"พัน": 1e3, "หมื่น": 1e4, "แสน": 1e5, "ล้าน": 1e6, "k": 1e3, "K": 1e3, "m": 1e6, "M": 1e6}
_LABELS = {
    "income":   r"เงินเดือน|รายได้(?:ต่อเดือน|เดือนละ)?|ได้เดือนละ|\b(?:salary|income|earn(?:ing)?|make)\b",
    "expense":  r"รายจ่าย|ค่าใช้จ่าย(?:ต่อเดือน|เดือนละ)?|ใช้(?:จ่าย)?เดือนละ|\b(?:expenses?|spend(?:ing)?|living costs?|cost of living)\b",
    "savings":  r"เงินเก็บ|เงินออม|เก็บ(?:เงิน)?(?:ไว้|ได้)|มีเงิน(?:สด)?|เงินสำรอง|\b(?:savings?|saved|in the bank|emergency fund)\b",
    "invest":   r"(?:เงิน)?(?:ลงทุน|ทุน)(?:เปิด|ทำ)?|ค่าตกแต่ง|ค่าแฟรนไชส์|ต้องใช้เงิน|\b(?:invest(?:ment)?|start-?up cost|upfront|cost to (?:open|start)|franchise fee)\b",
    "debt":     r"หนี้|ผ่อน(?:บ้าน|รถ)?(?:เดือนละ)?|\b(?:debt|loan|owe|mortgage)\b",
}
_LABEL_RX = {k: re.compile(rf"(?:{v})[^\d\n]{{0,14}}?{_NUM}", re.I) for k, v in _LABELS.items()}

KINDS = (
    ("quit_job", r"ลาออก|ออกจากงาน|\bquit(?:ting)? (?:my )?job\b|\bresign\w*\b|\bleave my job\b"),
    ("start_business", r"เปิด(?:ร้าน|ธุรกิจ|กิจการ|คาเฟ่|สาขา)|ทำธุรกิจ|ทำร้าน|ซื้อแฟรนไชส์|\bstart (?:a |my own )?business\b|\bopen (?:a |my own )?(?:cafe|café|shop|restaurant|store|business)\b|\bfranchise\b"),
    ("invest", r"ลงทุน(?!เปิด)|ซื้อหุ้น|คริปโต|กองทุน|\binvest(?:ing)? in\b|\bbuy (?:stocks|crypto|bitcoin)\b"),
    ("buy_big", r"ซื้อ(?:บ้าน|คอนโด|รถ|ที่ดิน)|ดาวน์(?:บ้าน|รถ)|\bbuy (?:a |the )?(?:house|condo|car|apartment|land)\b|\bmortgage\b"),
    ("move", r"ย้าย(?:ไป|บ้าน|ประเทศ|จังหวัด)|ไปทำงานต่างประเทศ|\bmov(?:e|ing) (?:to|abroad|overseas)\b|\brelocat\w*\b"),
    ("study", r"เรียนต่อ|ลาไปเรียน|ป\.?\s*โท|\b(?:go back to school|master'?s|mba|phd)\b"),
)
_KIND_RX = [(k, re.compile(v, re.I)) for k, v in KINDS]
_DEPENDENTS = re.compile(r"ลูก(?!ค้า|น้อง|หนี้)|พ่อแม่|แม่(?!ค้า)|พ่อ(?!ค้า)|ภรรยา|สามี|แฟน|ครอบครัว|\b(?:kids?|children|son|daughter|wife|husband|partner|parents?|family)\b", re.I)
_LEASE = re.compile(r"สัญญาเช่า|เซ้ง|ค่าเช่าที่|\blease\b|\brent (?:a |the )?(?:space|shop|unit)\b", re.I)
_LOAN = re.compile(r"กู้|เอาบ้านค้ำ|จำนอง|บัตรเครดิต|\b(?:loan|borrow|mortgage|credit card)\b", re.I)
_DECIDE = re.compile(r"ดีไหม|ดีมั้ย|ควร(?:ทำ|จะ)?(?:ไหม|มั้ย|หรือเปล่า|ดี)?|ตัดสินใจ|เลือก(?:ระหว่าง|อะไร)|หรือ(?:ว่า|จะ)|คุ้มไหม|\b(?:should i|is it (?:wise|smart|worth)|worth it|decide|decision|or should)\b", re.I)


def _amount(m: re.Match) -> float:
    v = float(m.group(1).replace(",", ""))
    return v * _MULT.get(m.group(2) or "", 1)


def extract(text: str) -> dict:
    t = str(text or "")
    nums = {}
    for k, rx in _LABEL_RX.items():
        m = rx.search(t)
        if m:
            v = _amount(m)
            if v >= 100:                     # ตัดเลขเล็ก (อายุ จำนวนปี) ที่บังเอิญตามหลังคำ
                nums[k] = v
    kinds = [k for k, rx in _KIND_RX if rx.search(t)]
    return {"nums": nums, "kinds": kinds, "dependents": bool(_DEPENDENTS.search(t)),
            "lease": bool(_LEASE.search(t)), "loan": bool(_LOAN.search(t)), "asks": bool(_DECIDE.search(t))}


def applies(text: str) -> bool:
    """เป็นคำถามตัดสินใจที่มีสาระพอจะวิเคราะห์ (ชนิดการตัดสินใจ + ถามว่าควรไหม หรือมีตัวเลข)"""
    f = extract(text)
    return bool(f["kinds"]) and (f["asks"] or len(f["nums"]) >= 2)


def _b(v: float) -> str:
    return f"{v:,.0f}"


def analyze(text: str) -> dict:
    f = extract(text)
    n = f["nums"]
    monthly = n.get("expense") or n.get("income")
    assumed = "expense" not in n and "income" in n
    out = dict(f, monthly=monthly, monthly_assumed=assumed, runway=None, runway_after=None, max_invest=None, floor=None)
    if monthly and n.get("savings"):
        out["runway"] = n["savings"] / monthly
        out["floor"] = FLOOR_MONTHS * monthly
        out["max_invest"] = max(0.0, n["savings"] - out["floor"])
        if n.get("invest"):
            out["runway_after"] = max(0.0, n["savings"] - n["invest"]) / monthly
    out["go_if"], out["stop_if"] = _gates(out)
    return out


def _gates(a: dict) -> tuple[list, list]:
    go, stop = [], []
    k = set(a["kinds"])
    if "start_business" in k or "invest" in k:
        go.append("ทดลองขายหรือทดสอบจริงก่อน 4–8 สัปดาห์ (ตลาดนัด ป๊อปอัป ขายออนไลน์ หรือรับพรีออเดอร์) แล้วจดยอดขายจริงทุกวัน"
                  if "start_business" in k else "ลงทุนก้อนแรกเฉพาะเงินที่เสียได้ทั้งหมดโดยชีวิตไม่สะดุด และรู้ว่าได้กำไรจากอะไร")
        stop.append("ยอดจริงต่ำกว่าจุดคุ้มทุน (ค่าเช่า + ค่าแรง + วัตถุดิบ) ติดกัน 3 เดือน" if "start_business" in k
                    else "มีคนการันตีผลตอบแทน หรือเร่งให้โอนเพิ่มเพื่อถอนเงิน")
    if a.get("max_invest") is not None:
        go.append(f"ใช้เงินลงทุนไม่เกิน {_b(a['max_invest'])} บาท เพื่อเก็บสำรอง {FLOOR_MONTHS} เดือน ({_b(a['floor'])} บาท) ไว้ไม่แตะ")
        stop.append(f"เงินสำรองลดต่ำกว่า {_b(a['floor'])} บาท — นั่นคือพื้นที่ห้ามต่ำกว่า")
    if "quit_job" in k:
        go.append("มีรายได้ใหม่ที่พิสูจน์แล้ว หรือลองทำควบคู่งานเดิมก่อน (ลาพักร้อน/วันหยุด/พาร์ทไทม์)")
    if a["lease"]:
        stop.append("สัญญาเช่ายาวที่ออกก่อนกำหนดไม่ได้ — ขอสัญญาสั้นหรือมีเงื่อนไขออกก่อน")
    if a["loan"]:
        stop.append("ต้องกู้หรือเอาทรัพย์สินค้ำเพื่อเริ่ม — ถ้าพลาด ความเสียหายไม่หยุดที่เงินลงทุน")
    if a["dependents"]:
        go.append("คนในบ้านที่ได้รับผลรู้ตัวเลขทั้งหมดและตกลงด้วย")
    return go[:3], stop[:3]


def facts_line(a: dict) -> str:
    """ตัวเลขสั้นๆ ที่ส่งให้ AI เป็นบริบท ([DECISION BRIEF]) — AI ต้องใช้ตัวเลขนี้ ไม่เดาเพิ่ม"""
    n = a["nums"]
    bits = [f"{k}={_b(v)}" for k, v in n.items()]
    if a["runway"] is not None:
        bits.append(f"runway≈{a['runway']:.1f} เดือน{'(สมมติใช้จ่ายราวรายได้)' if a['monthly_assumed'] else ''}")
    if a["max_invest"] is not None:
        bits.append(f"ลงทุนได้ไม่เกิน≈{_b(a['max_invest'])} (เหลือสำรอง {FLOOR_MONTHS} เดือน)")
    if a["runway_after"] is not None:
        bits.append(f"หลังลงทุนเหลืออยู่ได้≈{a['runway_after']:.1f} เดือน")
    return ("[DECISION BRIEF: " + " · ".join(bits + [f"ชนิด={','.join(a['kinds'])}"]) +
            (" · เดินหน้าเมื่อ: " + " / ".join(a["go_if"]) if a["go_if"] else "") +
            (" · หยุดเมื่อ: " + " / ".join(a["stop_if"]) if a["stop_if"] else "") + "]")


# ── คำตอบไม่มี AI ─────────────────────────────────────────────────────────────
_KIND_TH = {"quit_job": "ลาออก", "start_business": "เปิดกิจการ", "invest": "ลงทุน", "buy_big": "ซื้อของชิ้นใหญ่", "move": "ย้ายที่อยู่", "study": "เรียนต่อ"}


def _money_view(a: dict) -> str:
    n = a["nums"]
    if a["runway"] is None:
        need = "เงินเก็บ" if "savings" not in n else "รายจ่ายต่อเดือน"
        return f"ยังขาดตัวเลขสำคัญคือ{need} — บอกมาแล้วจะคำนวณได้ว่าถ้ารายได้หยุด เงินอยู่ได้กี่เดือน"
    s = (f"เงินเก็บ {_b(n['savings'])} บาท ใช้ได้ราว {a['runway']:.1f} เดือนถ้ารายได้หยุด"
         + (f" (คิดจากใช้จ่ายราวเงินเดือน {_b(a['monthly'])} — ถ้าใช้จริงน้อยกว่านี้จะอยู่ได้นานขึ้น)" if a["monthly_assumed"] else f" (รายจ่าย {_b(a['monthly'])}/เดือน)"))
    if a["runway_after"] is not None:
        s += f" · ถ้าลงทุน {_b(n['invest'])} จะเหลืออยู่ได้ราว {a['runway_after']:.1f} เดือน"
    else:
        s += f" · ลงทุนได้ไม่เกินราว {_b(a['max_invest'])} บาท ถ้าจะเก็บสำรอง {FLOOR_MONTHS} เดือนไว้"
    if "quit_job" in a["kinds"]:
        s += " · ถ้าลาออก เงินสำรองก้อนนี้คือค่าครองชีพระหว่างที่ทางใหม่ยังไม่มีกำไร ไม่ใช่เงินเหลือ"
    return s


def council(text: str, footer: bool = True) -> str:
    a = analyze(text)
    k = set(a["kinds"])
    what = " + ".join(_KIND_TH[x] for x in a["kinds"]) or "ตัดสินใจเรื่องนี้"
    irreversible = ("quit_job" in k) or a["lease"] or a["loan"]
    lyla = (f"การอยาก{what}มักมาจากทั้งแรงดึง (อยากสร้างอะไรของตัวเอง) และแรงผลัก (เหนื่อยกับที่เดิม) — ลองแยกให้ออกว่าของคุณเป็นแบบไหน "
            "เพราะถ้าเป็นแรงผลักอย่างเดียว ทางแก้อาจไม่ใช่การเปลี่ยนใหญ่ขนาดนี้")
    vega = ("ด้านเสียก่อน: " + _money_view(a) +
            (" · มีส่วนที่ย้อนกลับยาก (" + " · ".join(x for x, on in (("ลาออก", "quit_job" in k), ("สัญญาเช่า", a["lease"]), ("เงินกู้/ค้ำประกัน", a["loan"])) if on) + ")" if irreversible else ""))
    if "start_business" in k:
        paticca = ("ธุรกิจจะรอดเมื่อสมการนี้เป็นจริง: ลูกค้าต่อวัน × ยอดต่อคน × กำไรขั้นต้น ≥ ค่าเช่า + ค่าแรง + ค่าน้ำไฟ ต่อวัน — "
                   "ตอนนี้มีหลักฐานจริงของตัวเลขฝั่งซ้ายแล้วหรือยัง หรือยังเป็นความหวัง")
    elif "invest" in k:
        paticca = "ผลตอบแทนมาจากอะไรจริงๆ (ดอกเบี้ย ปันผล กำไรจากการขาย) — ถ้าอธิบายไม่ได้ใน 2 นาที แปลว่ายังไม่เข้าใจความเสี่ยงพอจะลงเงิน"
    else:
        paticca = "ข้อสมมติที่ใหญ่ที่สุดของทางนี้คืออะไร — เขียนออกมา 1 ข้อ แล้วหาวิธีพิสูจน์ด้วยเงินหรือเวลาน้อยที่สุด"
    titan = (a["go_if"][0] if a["go_if"] else "เขียนการตัดสินใจเป็น 1 ประโยค พร้อมตัวเลขที่ยอมเสียได้สูงสุด")
    cosmos = ("มองไป 12 เดือน: ทางที่ดีที่สุดคือทางที่ถ้าผิด คุณยังกลับมาได้โดยไม่เสียพื้น — "
              + ("งานประจำหาใหม่ได้ แต่เงินสำรองที่หมดไปสร้างคืนนาน " if "quit_job" in k else "")
              + "ถ้าพิสูจน์แล้วได้ผล การเปลี่ยนเต็มตัวทีหลังก็ยังทำได้")
    civil = ("คนที่ได้รับผลด้วย (ครอบครัว คนที่พึ่งรายได้คุณ) ควรเห็นตัวเลขเดียวกันกับคุณก่อนตัดสินใจ" if a["dependents"]
             else "ใครจะได้รับผลถ้าพลาด — และมีใครสักคนที่เคยทำเรื่องนี้จริงที่คุณถามได้ก่อนลงมือไหม")
    go = "\n".join(f"  ✓ {g}" for g in a["go_if"]) or "  ✓ มีหลักฐานจริงว่าข้อสมมติหลักเป็นจริง"
    stop = "\n".join(f"  ✕ {s}" for s in a["stop_if"]) or "  ✕ ความเสียหายเริ่มเกินที่ตั้งไว้"
    verdict = "ยังไม่ควรกระโดดเต็มตัวตอนนี้ — ทดลองแบบเล็กที่ย้อนกลับได้ก่อน" if irreversible or a["runway"] is not None and a["runway"] < 12 else \
              "เดินหน้าได้แบบเป็นขั้น เมื่อผ่านเงื่อนไขข้างล่าง"
    tag = "\n· ตอบจากสมการของระบบ — ไม่ได้ใช้ AI" if footer else ""
    return (f"LYLA ◈ — {lyla}\n\nVEGA ◆ — {vega}\n\nPATICCA ☸ — {paticca}\n\nTITAN ▲ — ก้าวแรกที่ทำได้: {titan}\n\n"
            f"COSMOS ✦ — {cosmos}\n\nCIVIL ⬡ — {civil}\n\n"
            f"มติสภา: {verdict}\nเดินหน้าเมื่อ:\n{go}\nหยุดเมื่อ:\n{stop}\nคุณเป็นคนตัดสินใจเสมอ\n\n— สภา KING DIADEM ✦" + tag)


def vega(text: str, footer: bool = True) -> str:
    a = analyze(text)
    k = set(a["kinds"])
    lines = ["ด้านเสียก่อน: " + _money_view(a)]
    if a["go_if"]:
        lines.append("เดินหน้าเมื่อ: " + " · ".join(a["go_if"]))
    if a["stop_if"]:
        lines.append("หยุดทันทีเมื่อ: " + " · ".join(a["stop_if"]))
    ask = ("ถ้าทดลองขายจริง 4 สัปดาห์ ยอดต่อวันต้องได้เท่าไหร่ถึงจะคุ้มค่าเช่าและค่าแรง — คุณรู้ตัวเลขนี้หรือยัง?" if "start_business" in k
           else "ถ้าทางนี้ผิด คุณจะรู้ได้เร็วที่สุดจากสัญญาณอะไร?")
    tag = "\n· ตอบจากสมการของระบบ — ไม่ได้ใช้ AI" if footer else ""
    return ("ผมดูจากตัวเลขที่คุณให้มาครับ — เป้าหมายคือไม่พลาดแบบย้อนกลับไม่ได้ ไม่ใช่ชนะให้มากที่สุด\n\n"
            + "\n".join(f"{i + 1}) {ln}" for i, ln in enumerate(lines)) + f"\n\n{ask}\n\n— VEGA ◆" + tag)
