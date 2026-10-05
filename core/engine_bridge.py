"""
core/engine_bridge.py — สะพานจากข้อความของผู้ใช้ไปยังเครื่องยนต์ที่เคยไม่มีใครเรียก

เครื่องยนต์ 4 ตัวนี้คำนวณได้ดี แต่รับข้อมูลเป็นตัวเลข/ธง ส่วนผู้ใช้พิมพ์เป็นประโยค
ไฟล์นี้อ่านเฉพาะสิ่งที่ผู้ใช้บอกเองจริงๆ (ไม่เดาตัวเลขแทน) แล้วส่งให้:
- ENGINE/debt_engine.py         แผนปลดหนี้ avalanche/snowball
- ENGINE/resource_estimator.py  เงิน/อาหาร/น้ำ พอใช้อีกกี่วัน
- ENGINE/relationship_engine.py สัญญาณความรุนแรง/ควบคุมในความสัมพันธ์
- ENGINE/choice_optimizer.py    เรียงทางเลือกของผู้ใช้จากรอดสุด → เสี่ยงสุด
- DOMAINS/survival_engine.py    ภัยที่กำลังเจอ (น้ำท่วม แผ่นดินไหว ไฟไหม้ พายุ ยิงกัน) → ระดับภัย
- ENGINE/tool_executor.py       คิดเลขที่ผู้ใช้ถามให้ตรง (ไม่ให้ AI เดาผลคูณ/ผลบวก)
- WORLD_MODEL/human_bias.py     กับดักความคิดตอนตัดสินใจ (เสียดายของที่ลงไปแล้ว · ติดแบบเดิม)
- ENGINE/map_bridge.py          ปุ่มหาโรงพยาบาล/ศูนย์พักพิง/ตำรวจใกล้ตัว (ไม่ส่งพิกัดมาที่เซิร์ฟเวอร์)

คืน {"lines": [...ข้อความสำหรับคำตอบ...], "llm_ctx": "...", "data": {...}}
"""
from __future__ import annotations

import re

_UNITS = {"พัน": 1e3, "หมื่น": 1e4, "แสน": 1e5, "ล้าน": 1e6, "k": 1e3}
_AMOUNT = re.compile(r"(\d[\d,]*(?:\.\d+)?)\s*(พัน|หมื่น|แสน|ล้าน|k|K)?(?!\s*(?:%|เปอร์|ปี|เดือน|วัน|ครั้ง|งวด|มื้อ|ลิตร|ขวด|คน|ชม|ชั่วโมง))")


def _amounts(seg: str, minimum: float = 100) -> list:
    out = []
    for m in _AMOUNT.finditer(seg):
        try:
            v = float(m.group(1).replace(",", "")) * _UNITS.get((m.group(2) or "").lower(), 1)
        except ValueError:
            continue
        if v >= minimum:
            out.append(v)
    return out


def _after(text: str, words: str):
    """จำนวนเงินตัวแรกหลังคำ เช่น "เงินเดือน 18,000" """
    m = re.search(rf"(?:{words})\D{{0,14}}?(\d[\d,]*(?:\.\d+)?)\s*(พัน|หมื่น|แสน|ล้าน|k|K)?"
                  r"(?!\s*(?:%|มื้อ|วัน|เดือน|ปี|ชม|ชั่วโมง|ครั้ง|คน|ลิตร|ขวด|ซอง|ห่อ|กล่อง))", text)
    if not m:
        return None
    try:
        return float(m.group(1).replace(",", "")) * _UNITS.get((m.group(2) or "").lower(), 1)
    except ValueError:
        return None


# ── 1. หนี้ ─────────────────────────────────────────────────────────────
_DEBT_KIND = (
    ("บัตรกดเงินสด", 25.0), ("สินเชื่อบุคคล", 25.0), ("บัตรเครดิต", 16.0), ("บัตร", 16.0),
    ("นอกระบบ", None), ("กยศ", 1.0), ("บ้าน", 6.0), ("รถ", 6.0), ("หนี้", None), ("กู้", None),
    ("ยืม", 0.0), ("สินเชื่อ", 25.0),           # ยืมคนรู้จัก — ปกติไม่คิดดอก (บอกดอกมาจะใช้ค่าจริง)
)
_PER_MONTH = re.compile(r"เดือนละ|ต่อเดือน|/เดือน|ต่อด|ต่องวด|งวดละ")


_DEBT_KW = re.compile("|".join(k for k, _ in _DEBT_KIND))
_STOP_KW = re.compile(r"เงินเดือน|รายได้|รายจ่าย|ค่าใช้จ่าย|ใช้จ่าย|ได้เดือนละ|ใช้เดือนละ|จ่ายเดือนละ")


def _debt_segments(text: str) -> list:
    """แบ่งข้อความเป็นช่วงละหนึ่งหนี้: จากคำว่า หนี้/บัตร/กู้... ไปจนถึงคำถัดไป
    (เดิมแบ่งด้วยลูกน้ำ ทำให้ "20,000" ขาดเป็นสองท่อน)"""
    starts, last = [], -10
    for m in _DEBT_KW.finditer(text):
        # "หนี้บัตรเครดิต" = หนี้ก้อนเดียว — คำที่ติดกัน (ห่างไม่เกิน 2 ตัว) ไม่นับเป็นก้อนใหม่
        if m.start() - last > 2:
            starts.append(m.start())
        last = m.end()
    segs = []
    for i, a in enumerate(starts):
        b = starts[i + 1] if i + 1 < len(starts) else len(text)
        seg = text[a:b]
        stop = _STOP_KW.search(seg)
        segs.append(seg[:stop.start()] if stop else seg)
    return segs


# คำที่บอกว่าเป็น "หนี้" จริง — "ซื้อบัตรคอนเสิร์ต 3,500" "อยากซื้อรถ 500,000" "บ้านราคา 2 ล้าน" ไม่ใช่หนี้
_DEBT_CTX = re.compile(r"หนี้|ค้าง|ผ่อน|กู้|ยืม|สินเชื่อ|บัตรเครดิต|บัตรกดเงินสด|ยอดบัตร|รูดบัตร|กยศ|นอกระบบ|ดอกเบี้ย|ดอก\s*\d")


def parse_debts(text: str) -> list:
    debts = []
    for seg in _debt_segments(text):
        kind = next(((k, r) for k, r in _DEBT_KIND if k in seg), None)
        if not kind or not _DEBT_CTX.search(seg):
            continue
        # "ผ่อนบ้านเดือนละ 8,000" = ค่างวด ไม่ใช่ยอดหนี้
        if _PER_MONTH.search(seg) and not re.search(r"ยอด|คงเหลือ|เหลือ|ทั้งหมด", seg) and "%" not in seg:
            continue
        amts = _amounts(seg)
        if not amts:
            continue
        rate_m = re.search(r"(\d+(?:\.\d+)?)\s*(?:%|เปอร์เซ็นต์)", seg)
        rate, assumed = None, False
        if rate_m:
            rate = float(rate_m.group(1))
            if re.search(r"(?:%|เปอร์เซ็นต์)\s*(?:ต่อเดือน|/เดือน|เดือนละ)", seg):
                rate *= 12                                  # ดอกรายเดือน (มักเป็นหนี้นอกระบบ) → ต่อปี
        elif kind[1] is not None:
            rate, assumed = kind[1], True
        else:
            rate, assumed = 18.0, True
        name = ("เงินยืม" if kind[0] == "ยืม" else
                "หนี้" + kind[0] if kind[0] not in ("หนี้", "กู้") else "หนี้ก้อนที่ " + str(len(debts) + 1))
        debts.append({"name": name, "balance": amts[0], "annual_rate": rate, "assumed_rate": assumed})
    return debts[:8]


def _debt(text: str) -> dict | None:
    debts = parse_debts(text)
    if not debts:
        return None
    income = _after(text, r"เงินเดือน|รายได้|ได้เดือนละ|ทำได้เดือนละ|รับเดือนละ")
    expense = _after(text, r"รายจ่าย|ค่าใช้จ่าย|ใช้จ่าย|ใช้เดือนละ|จ่ายเดือนละ")
    lines, data = [], {"debts": debts, "income": income, "expense": expense}
    total = sum(d["balance"] for d in debts)
    order = sorted(debts, key=lambda d: d["annual_rate"], reverse=True)
    tag = lambda d: f"{d['name']} {d['balance']:,.0f} บาท ดอก {d['annual_rate']:g}%{'*' if d['assumed_rate'] else ''}"
    if len(debts) == 1:
        lines.append("หนี้ที่คุณเล่ามา: " + tag(debts[0]))
    else:
        lines.append(f"หนี้ที่คุณเล่ามา {len(debts)} ก้อน รวม {total:,.0f} บาท — ดอกสูงก่อน: " +
                     " → ".join(f"{d['name']} {d['annual_rate']:g}%{'*' if d['assumed_rate'] else ''}" for d in order))
    if any("นอกระบบ" in d["name"] for d in debts):
        lines.append("หนี้นอกระบบ: กฎหมายให้ดอกเบี้ยเงินกู้ระหว่างบุคคลไม่เกิน 15% ต่อปี — "
                     "ปรึกษาหรือร้องเรียนได้ที่ศูนย์ดำรงธรรม 1567")
    if any(d["assumed_rate"] for d in debts):
        lines.append("* ดอกเบี้ยที่ใช้เป็นค่าทั่วไปของหนี้ประเภทนั้น บอกดอกจริงมาจะคำนวณแม่นขึ้น")
    if income is not None and expense is not None:
        try:
            from ENGINE.debt_engine import run_debt_freedom
            r = run_debt_freedom([{k: d[k] for k in ("name", "balance", "annual_rate")} for d in debts],
                                 income, expense)
            data["plan"] = {k: r.get(k) for k in ("status", "recommended_strategy", "monthly_extra", "note", "message")}
            if r.get("status") == "OK":
                strat = "ก้อนดอกสูงก่อน (avalanche)" if r["recommended_strategy"] == "avalanche" else "ก้อนเล็กก่อน (snowball)"
                lines.append(f"แผนปลดหนี้: เงินเหลือโปะ {r['monthly_extra']:,.0f} บาท/เดือน · โปะ{strat} · {r['note']}")
            elif r.get("message"):
                lines.append("แผนปลดหนี้: " + r["message"])
        except Exception as e:  # pragma: no cover
            print(f"⚠ debt_engine: {type(e).__name__}")
    else:
        lines.append("บอกรายได้และรายจ่ายต่อเดือนมาด้วย ระบบจะคำนวณให้ว่าปลดหนี้ได้ในกี่เดือน")
    return {"lines": lines, "data": data}


# ── 2. เงิน/อาหาร/น้ำ พอใช้อีกกี่วัน ───────────────────────────────────
def _runway(text: str) -> dict | None:
    # เงินที่ "เหลือ" จริง — ไม่ใช่ "มีเงินเดือน 15,000" / "มีเงินเก็บ" และไม่ใช่ "เหลือแค่ 2 มื้อ" "เหลืออยู่ 3 วัน"
    money = _after(text, r"เหลือเงิน|เงินเหลือ|เงินติดตัว|มีเงิน(?:อยู่)?(?:แค่|เหลือ)|เหลือ(?:แค่|อยู่)?(?=\s*\d[\d,]*\s*บาท)")
    meals_m = re.search(r"(\d+)\s*(?:มื้อ|ซอง|ห่อ|กล่อง)", text)
    water_m = re.search(r"น้ำ\D{0,8}?(\d+(?:\.\d+)?)\s*(?:ลิตร|ขวด)", text)
    no_shelter = bool(re.search(r"ไม่มีที่อยู่|ไม่มีที่นอน|นอนข้างถนน|ถูกไล่ออกจากบ้าน|ไม่มีที่พัก", text))
    if money is None and not meals_m and not water_m:
        return None
    try:
        from ENGINE.resource_estimator import estimate_resources
    except Exception:  # pragma: no cover
        return None
    # สิ่งที่ผู้ใช้ไม่ได้บอก → ไม่ให้เป็นตัวจำกัด (ไม่เดาว่าไม่มี)
    r = estimate_resources(
        food=float(meals_m.group(1)) if meals_m else 9999,
        money=money if money is not None else 1e9,
        water_liters=float(water_m.group(1)) * (1.5 if water_m and "ขวด" in water_m.group(0) else 1) if water_m else 9999,
        shelter_ok=not no_shelter,
    )
    known = {"money": money is not None, "food": bool(meals_m), "water": bool(water_m)}
    parts = []
    if known["money"]:
        parts.append(f"เงิน {money:,.0f} บาท ÷ {r['daily_expense']:,.0f} บาท/วัน ≈ {r['money_days']:g} วัน")
    if known["food"]:
        parts.append(f"อาหาร {r['food']:g} มื้อ ≈ {r['food_days']:g} วัน")
    if known["water"]:
        parts.append(f"น้ำ ≈ {r['water_days']:g} วัน")
    lines = ["เวลาที่มีจริง: " + " · ".join(parts)]
    factor = r["binding_factor"]
    if no_shelter:
        lines.append("ที่พักมาก่อนทุกอย่าง — ศูนย์ช่วยเหลือสังคม 1300 (24 ชม.) ช่วยหาที่พักฉุกเฉินได้")
    elif sum(known.values()) >= 2 and known.get(factor):
        th = {"money": "เงิน", "food": "อาหาร", "water": "น้ำ"}[factor]
        lines.append(f"สิ่งที่จะหมดก่อนคือ{th} — แก้เรื่องนี้ก่อน")
    return {"lines": lines, "data": {k: r[k] for k in ("money_days", "food_days", "water_days",
                                                      "survival_days", "binding_factor", "status")} | {"known": known}}


# ── 3. ความสัมพันธ์ ─────────────────────────────────────────────────────
_REL_CTX = re.compile(r"แฟน|สามี|ภรรยา|เมีย|ผัว|คู่รัก|คนรัก|พ่อ|แม่|ครอบครัว|ญาติ|คนที่บ้าน|พี่ชาย|น้องชาย")
_REL_FLAGS = {
    # "ตี" เดี่ยวๆ ไปติด "ตีกอล์ฟ" "ตีความ" — ใช้รูปที่หมายถึงการทำร้ายคน
    "violence_risk": r"ตบ|ตี(?:ฉัน|หนู|ผม|เรา|ลูก|หัว|หน้า|จน|แรง)|(?:ถูก|โดน)\S{0,8}?ตี|ทุบ|ทำร้าย|เตะ|บีบคอ|"
                     r"ขู่ฆ่า|ขู่จะทำร้าย|ซ้อม|ผลัก|ข่มขืน|ใช้กำลัง",
    "financial_control": r"ยึดเงิน|คุมเงิน|ไม่ให้ใช้เงิน|เอาเงินไปหมด|ยึดบัตร|เอาบัตรไป|ไม่ให้ทำงาน",
    "isolation": r"ไม่ให้เจอเพื่อน|ห้ามเจอ|ห้ามคุย|ไม่ให้ออกจากบ้าน|ห้ามออกจากบ้าน|ตัดขาด|ไม่ให้ติดต่อ|ยึดโทรศัพท์|ยึดมือถือ",
    "dependency": r"ต้องพึ่งเขา|ไม่มีรายได้ของตัวเอง|ไม่มีที่ไป|ออกไปก็ไม่มีที่อยู่",
    "trust_broken": r"นอกใจ|มีคนอื่น|มีกิ๊ก|โกหก|หลอกลวง",
    "fear": r"กลัวเขา|กลัวกลับบ้าน|กลัวโดน",
    "depression": r"ซึมเศร้า|หมดหวัง",
}
_REL_TH = {"violence_risk": "การทำร้ายร่างกาย/ขู่", "financial_control": "การควบคุมเงิน",
           "isolation": "การตัดขาดจากคนอื่น", "dependency": "การต้องพึ่งพาฝ่ายเดียว",
           "trust_broken": "ความไว้ใจที่พัง", "fear": "ความกลัว", "depression": "ความหมดหวัง"}
_REL_ACTION = {
    "collapse_risk": "ความปลอดภัยของร่างกายมาก่อนทุกอย่าง — ไปอยู่ที่ปลอดภัยก่อน แล้วค่อยคิดเรื่องอื่น",
    "critical": "อย่าแก้คนเดียว — บอกคนที่ไว้ใจได้ หรือโทรศูนย์ช่วยเหลือสังคม 1300",
    "unstable": "ตั้งขอบเขตให้ชัด และหาคนที่ไว้ใจได้ช่วยมองอีกมุม",
    "warning": "สังเกตว่าเรื่องนี้เกิดซ้ำไหม — ถ้าเกิดซ้ำคือรูปแบบ ไม่ใช่เหตุบังเอิญ",
}


def _relationship(text: str) -> dict | None:
    if not _REL_CTX.search(text):
        return None
    ctx = {k: True for k, rx in _REL_FLAGS.items() if re.search(rx, text)}
    if not ctx:
        return None
    try:
        from ENGINE.relationship_engine import analyze_relationship
    except Exception:  # pragma: no cover
        return None
    r = analyze_relationship(ctx)
    lines = ["สิ่งที่คุณเล่ามีสัญญาณของ " + " · ".join(_REL_TH[k] for k in ctx)]
    if r["status"] in _REL_ACTION:
        lines.append(_REL_ACTION[r["status"]])
    if ctx.get("violence_risk"):
        lines.append("ถ้ากำลังอยู่ในอันตราย โทร 191 (ตำรวจ) หรือ 1300 (ศูนย์ช่วยเหลือสังคม 24 ชม.)")
    return {"lines": lines, "data": {"status": r["status"], "risk_score": r["risk_score"], "flags": list(ctx)}}


# ── 5. ภัยที่กำลังเจอ (DOMAINS/survival_engine) ──────────────────────────
# เดิม "น้ำท่วมบ้าน" "แผ่นดินไหว ตึกสั่น" ได้ Risk 0 และคำตอบทั่วไป
# (ชนิดภัย, ประเภทใน survival_engine, ชื่อไทย, ขั้นแรกที่ทำได้ทันที)
_HAZARDS = (
    ("flood", "climate_disaster", "น้ำท่วม",
     re.compile(r"น้ำท่วม(?!ขัง|ปาก|ทุ่ง)|น้ำเข้าบ้าน|น้ำป่า|น้ำขึ้นถึง|น้ำทะลัก|เขื่อนแตก|คันกั้นน้ำแตก"),
     ["ตัดไฟที่เบรกเกอร์ถ้ามือและเท้าแห้งและน้ำยังไม่ถึงปลั๊ก — ถ้าน้ำถึงแล้ว อย่าแตะสวิตช์ อย่าลงน้ำที่อาจมีไฟรั่ว",
      "ขึ้นที่สูงหรือชั้นบนพร้อมคนในบ้าน เอายาประจำตัว เอกสาร โทรศัพท์กับพาวเวอร์แบงก์ไปด้วย",
      "อย่าเดินหรือขับรถลุยน้ำไหล — น้ำสูงแค่เข่าก็พัดคนล้มได้"]),
    ("quake", "climate_disaster", "แผ่นดินไหว",
     re.compile(r"แผ่นดินไหว|ตึกสั่น|อาคารสั่น|ตึกถล่ม|ตึกร้าว"),
     ["ถ้ายังสั่นอยู่: หมอบ ป้องศีรษะ เกาะโต๊ะที่แข็งแรง อยู่ห่างกระจกและของที่ล้มได้",
      "หยุดสั่นแล้วค่อยออกทางบันได — ไม่ใช้ลิฟต์ แล้วไปอยู่ที่โล่ง ห่างตึกและเสาไฟ",
      "ระวังอาฟเตอร์ช็อก และอย่ากลับเข้าอาคารที่มีรอยร้าวจนกว่าจะมีคนตรวจ"]),
    ("fire", "climate_disaster", "ไฟไหม้",
     re.compile(r"ไฟไหม้(?!ฟาง)|ไฟลุก|ควันเต็ม|ไฟป่า|ควันไฟเข้า"),
     ["ออกจากอาคารทันที ไม่ย้อนกลับไปเอาของ — ไม่ใช้ลิฟต์",
      "ควันเยอะ: ก้มต่ำ ใช้ผ้าชุบน้ำปิดจมูก ก่อนเปิดประตูให้ใช้หลังมือแตะลูกบิด ถ้าร้อนอย่าเปิด",
      "ออกมาแล้วโทร 199 (ดับเพลิง) และนับคนให้ครบ"]),
    ("storm", "climate_disaster", "พายุ/ดินถล่ม",
     re.compile(r"พายุเข้า|พายุพัด|พายุหนัก|หลังคาปลิว|ต้นไม้ล้มทับ|ดินถล่ม|ดินสไลด์|โคลนถล่ม"),
     ["อยู่ในอาคารที่แข็งแรง ห่างหน้าต่างและต้นไม้ใหญ่ — ถ้าอยู่ตีนเขาหรือริมลำห้วย ย้ายออกก่อน",
      "อย่าเข้าใกล้สายไฟที่ขาด และอย่าข้ามลำน้ำที่ไหลแรง",
      "เตรียมไฟฉาย น้ำดื่ม ยา และชาร์จโทรศัพท์ไว้"]),
    ("violence", "war_conflict", "เหตุยิงหรือระเบิด",
     re.compile(r"เสียงระเบิด|ระเบิดลง|ยิงกัน|มีคนยิง|กราดยิง|เสียงปืน|คนร้ายถือปืน"),
     ["หนีออกห่างจากเสียงถ้าทำได้ปลอดภัย — ถ้าหนีไม่ได้ ซ่อนในห้องที่ล็อกได้ ปิดไฟ ปิดเสียงโทรศัพท์",
      "อยู่ห่างหน้าต่างและประตู หมอบต่ำหลังสิ่งที่กันกระสุนได้ (ผนังปูน)",
      "ปลอดภัยแล้วค่อยโทร 191 บอกตำแหน่ง — ถ้ามีคนเจ็บ โทร 1669"]),
)
_HAZARD_NEAR = re.compile(r"ตอนนี้|กำลัง|ติดอยู่|ออกไม่ได้|หนีไม่ทัน|ช่วยด้วย|ถึงเอว|ถึงอก|ท่วมบ้าน|เข้าบ้าน|ในบ้าน|"
                          r"ที่บ้าน|ข้างบ้าน|ห้องข้างๆ|ที่นี่|แถวนี้|ยังสั่น|ตึกสั่น|อาคารสั่น|ควันเต็ม|ใกล้มาก")
# พูดถึงภัยแต่ไม่ได้เกิดกับตัวตอนนี้: ข่าว · สมมติ · เรื่องเก่า → เตรียมตัว ไม่ยก Risk
_HAZARD_FAR = re.compile(r"ถ้า|หาก|เผื่อ|เตรียม(?:ตัว)?รับ|ข่าว|ดูหนัง|ในหนัง|ในเกม|ปีที่แล้ว|เมื่อปี|ตอนเด็ก|เคยเจอ|สมัยก่อน")
_HAZARD_LEVEL_TH = {"EXTREME": "สูงมาก", "HIGH": "สูง", "MODERATE": "ปานกลาง", "LOW": "ต่ำ"}


def _disaster(text: str) -> dict | None:
    hit = next((h for h in _HAZARDS if h[3].search(text)), None)
    if not hit:
        return None
    kind, event, name, _, steps = hit
    far = bool(_HAZARD_FAR.search(text)) and not _HAZARD_NEAR.search(text)
    severity = 25 if far else 85 if _HAZARD_NEAR.search(text) else 60
    try:
        from DOMAINS.survival_engine import analyze_global_event
        r = analyze_global_event(event_type=event, severity=severity)
        threat, level = float(r.get("threat_score") or 0), str(r.get("threat_level") or "")
    except Exception:  # pragma: no cover
        threat, level = 0.0, ""
    hotline = ("เบอร์ที่ใช้ได้: 1784 (ปภ. สายด่วนนิรภัย) · 1669 (เจ็บป่วยฉุกเฉิน) · 191 (ตำรวจ)"
               + (" · 199 (ดับเพลิง)" if kind == "fire" else ""))
    if far:
        lines = [f"แผนเตรียมรับ{name} — รู้ไว้ก่อนว่าถ้าเกิดจริงต้องทำอะไรก่อน: {steps[0]}", hotline]
    else:
        lv = _HAZARD_LEVEL_TH.get(level, "")
        lines = [f"ภัยที่กำลังเจอ: {name}" + (f" · ระดับภัย {lv}" if lv else "")] + steps + [hotline]
    return {"lines": lines, "data": {"kind": kind, "name": name, "active": not far,
                                     "threat": round(threat), "steps": steps}}


# ── 6. คิดเลขที่ผู้ใช้ถาม (ENGINE/tool_executor) ─────────────────────────
# ต้องมีทั้งนิพจน์ (ตัวเลข เครื่องหมาย ตัวเลข) และคำถามหาผล — "24/7" "1-2 วัน" "50/50" ไม่ใช่โจทย์
_CALC_EXPR = re.compile(r"(?<![\d/.])\d[\d,]*(?:\.\d+)?(?:\s*[+×x*÷]\s*\d[\d,]*(?:\.\d+)?)+(?![\d/])")
_CALC_ASK = re.compile(r"เท่าไหร่|เท่าไร|เท่าใด|ได้เท่า|ทั้งหมดกี่|รวมกี่|คิดยังไง|ช่วยคิด|ช่วยคำนวณ|คำนวณ|=\s*\?|=\s*$|how much", re.I)


def _fmt(v: float) -> str:
    return f"{v:,.0f}" if abs(v - round(v)) < 1e-9 else f"{v:,.2f}"


def _calc(text: str) -> dict | None:
    if not _CALC_ASK.search(text):
        return None
    try:
        from ENGINE.tool_executor import _safe_calc
    except Exception:  # pragma: no cover
        return None
    lines, results = [], []
    for m in list(_CALC_EXPR.finditer(text))[:3]:
        raw = m.group(0)
        expr = raw.replace(",", "").replace("×", "*").replace("x", "*").replace("÷", "/")
        r = _safe_calc(expr)
        if "result" not in r:
            continue
        shown = re.sub(r"\s*([+×x*÷])\s*", lambda o: " " + {"x": "×", "*": "×", "÷": "÷"}.get(o.group(1), o.group(1)) + " ", raw)
        lines.append(f"คิดเลข: {shown.strip()} = {_fmt(float(r['result']))}")
        results.append(r["result"])
    return {"lines": lines, "data": {"results": results}} if lines else None


# ── 7. กับดักความคิดตอนตัดสินใจ (WORLD_MODEL/human_bias) ─────────────────
_DECIDING = re.compile(r"ควร.{0,40}ไหม|ดีไหม|ลังเล|ตัดสินใจ|เลือก|หรือจะ|ต่อดีหรือ|เลิกดีไหม|ไปต่อ|พอแค่นี้")
_BIAS_NOTE = {
    "loss": ("ความเสียดายสิ่งที่ลงไปแล้ว (เงิน เวลา แรง) อาจกำลังดึงการตัดสินใจอยู่ — "
             "ลองถามว่า ถ้าเริ่มจากศูนย์วันนี้ จะยังเลือกทางนี้ไหม"),
    "familiar": ("ความเคยชินกับแบบเดิมอาจทำให้ทางเดิมดูปลอดภัยกว่าที่เป็นจริง — "
                 "ลองเทียบทั้งสองทางด้วยคำถามเดียวกัน: อีก 1 ปีข้างหน้า แต่ละทางพาไปอยู่ตรงไหน"),
}


def _bias(text: str) -> dict | None:
    if not _DECIDING.search(text):
        return None
    try:
        from WORLD_MODEL.human_bias import detect_bias_context
    except Exception:  # pragma: no cover
        return None
    b = detect_bias_context(text)
    if b not in _BIAS_NOTE:            # panic/overconfident จับจากคำกว้างเกินไป ("รีบ" "แน่นอน")
        return None
    return {"lines": [_BIAS_NOTE[b]], "data": {"kind": b}}


# ── 8. ความช่วยเหลือใกล้ตัว (ENGINE/map_bridge) ──────────────────────────────
# ลิงก์ค้นหาแผนที่ "ใกล้ฉัน" — ไม่ส่งพิกัดของผู้ใช้มาที่เซิร์ฟเวอร์
_PLACES = {
    "hospital": ("โรงพยาบาล", "โรงพยาบาล ใกล้ฉัน"),
    "police":   ("สถานีตำรวจ", "สถานีตำรวจ ใกล้ฉัน"),
    "shelter":  ("ศูนย์พักพิง/อพยพ", "ศูนย์พักพิงชั่วคราว ศูนย์อพยพ ใกล้ฉัน"),
    "pharmacy": ("ร้านขายยา", "ร้านขายยา ใกล้ฉัน"),
    "water":    ("ร้านสะดวกซื้อ (น้ำดื่ม)", "ร้านสะดวกซื้อ ใกล้ฉัน"),
    "fuel":     ("ปั๊มน้ำมัน", "ปั๊มน้ำมัน ใกล้ฉัน"),
    "mechanic": ("อู่ซ่อมรถ", "อู่ซ่อมรถ ใกล้ฉัน"),
}
_NEAR_ASK = re.compile(r"ใกล้(?:ฉัน|หนู|ผม|เรา|ๆ|ที่สุด|บ้าน)|แถวนี้|อยู่ตรงไหน|ไปที่ไหนได้|หาที่ไหน")
_PLACE_WORDS = (("hospital", r"โรงพยาบาล|โรงบาล|รพ\.|คลินิก|ห้องฉุกเฉิน"), ("police", r"สถานีตำรวจ|โรงพัก|แจ้งความ"),
                ("shelter", r"ศูนย์อพยพ|ศูนย์พักพิง|ที่พักพิง|ที่หลบภัย"), ("pharmacy", r"ร้านขายยา|ซื้อยา"),
                ("fuel", r"ปั๊มน้ำมัน|เติมน้ำมัน"), ("mechanic", r"อู่ซ่อม|อู่รถ|รถเสีย|ยางแตก"))
_HEALTH_NOW = re.compile(r"เจ็บหน้าอก|แน่นหน้าอก|หายใจไม่ออก|หมดสติ|ชัก|เลือดออกไม่หยุด|แขนขาอ่อนแรง|ปากเบี้ยว")


def nearby(text: str, disaster: dict | None = None, relationship: str | None = None) -> list:
    """[{label, url}] ที่ควรมีปุ่มให้กด — เฉพาะตอนที่ต้องไปหาที่ช่วยจริงๆ"""
    want = []
    if disaster and disaster.get("active"):
        want += ["shelter", "hospital"]
    if _HEALTH_NOW.search(text):
        want.append("hospital")
    if relationship in ("collapse_risk", "critical"):
        want.append("police")
    if _NEAR_ASK.search(text):
        want += [k for k, rx in _PLACE_WORDS if re.search(rx, text)]
    try:
        from ENGINE.map_bridge import near_me_link
    except Exception:  # pragma: no cover
        return []
    out, seen = [], set()
    for k in want:
        if k in _PLACES and k not in seen:
            seen.add(k)
            out.append({"label": _PLACES[k][0], "url": near_me_link(_PLACES[k][1])})
    return out[:3]


# ── 4. เรียงทางเลือก ────────────────────────────────────────────────────
_IRREVERSIBLE = re.compile(r"ลาออก|ขายบ้าน|ขายรถ|ขายที่ดิน|ขายกิจการ|ย้ายประเทศ|ย้ายบ้าน|หย่า|กู้|ลงทุนทั้งหมด|"
                           r"เงินเก็บทั้งหมด|ทุ่มหมด|เซ็นสัญญา|ปิดร้าน|ปิดกิจการ|quit|all in", re.I)


def rank_options(options: list, waterline: float = 50, entropy: float = 40) -> list:
    """เรียงทางเลือกด้วย choice_optimizer — ทางที่ย้อนกลับได้ได้เปรียบเมื่อสถานะต่ำ"""
    try:
        from ENGINE.choice_optimizer import optimize_choice
    except Exception:  # pragma: no cover
        return [{"action": o, "reversible": not _IRREVERSIBLE.search(o), "collapse_risk": "", "reason": ""}
                for o in options]
    acts = [{"action": o, "reversible": not _IRREVERSIBLE.search(o), "time": 1} for o in options]
    return optimize_choice(acts, {"waterline": waterline, "entropy": entropy})


# ── รวม ────────────────────────────────────────────────────────────────
def analyze(text: str) -> dict:
    text = str(text or "")
    out = {"lines": [], "llm_ctx": "", "data": {}}
    for name, fn in (("disaster", _disaster), ("relationship", _relationship), ("debt", _debt),
                     ("runway", _runway), ("calc", _calc), ("bias", _bias)):
        try:
            r = fn(text)
        except Exception as e:  # ห้ามทำให้คำตอบล้ม
            print(f"⚠ engine_bridge.{name}: {type(e).__name__}")
            r = None
        if r:
            out["lines"].extend(r["lines"])
            out["data"][name] = r["data"]
    if out["lines"]:
        out["llm_ctx"] = ("[ตัวเลขที่ระบบคำนวณจากสิ่งที่ผู้ใช้เล่า — ใช้ตัวเลขเหล่านี้ตอบผู้ใช้ได้ตรงๆ ห้ามแต่งตัวเลขเพิ่ม: "
                          + " | ".join(out["lines"]) + "]")
    return out
