"""DriftZero — โหมดตรวจการตัดสินใจระดับองค์กร/โครงการ/นโยบาย (แยกจากโหมดปรึกษา)

ที่มา: README ของ repo KING-DIADEM-DriftZero (Deterministic Governance Kernel v0.1.0)
  Tier 1 Humility gate · E1–E3 (convenience · waterline · stabilize first) · K4–K14 · Deployment SOP 7 ขั้น
เจ้าของโปรเจกต์อยากให้เป็น "โหมดแยก" ไม่รวมกับการปรึกษาเรื่องส่วนตัว — ด่านพวกนี้เข้มเกินไปสำหรับเรื่องบ้านๆ

หลัก:
  · ตรวจจากข้อความอย่างเดียว ไม่ใช้ AI — ข้อความเดิมได้ผลเดิมทุกครั้ง (deterministic)
  · ไม่เดาตัวเลขที่ไม่มี — DHD (Daily Harm Delta) ยังไม่มีสูตรในต้นฉบับ จึง "ถามหา" ข้อมูลที่ต้องใช้วัด
  · ด่านที่ติด = หยุดก่อน (STOP) · ข้อมูลไม่พอ = ถาม (ASK) · ไม่เจอสัญญาณ = ผ่าน (PASS)
  · คนเป็นผู้ตัดสินใจและเซ็นรับผิดชอบเสมอ — ระบบไม่อนุมัติแทน
"""
from __future__ import annotations

import functools
import re

STOP, ASK, PASS = "stop", "ask", "pass"


def _rx(*parts: str) -> re.Pattern:
    return re.compile("|".join(parts), re.I)


# (id, ชื่อไทย, ชื่ออังกฤษ, regex, คำอธิบายเมื่อติด th, en)
# ด่านทั้งหมดอยู่ในตารางข้อมูล ENGINE/driftzero_gates.py (รูปแบบทีละบรรทัด พร้อมที่มาของแต่ละด่าน)
# ที่นี่แค่ประกอบกลับเป็น (id, ชื่อไทย, ชื่ออังกฤษ, regex, เหตุผลไทย, เหตุผลอังกฤษ) — โครงเดิมที่ทุกส่วนใช้อยู่
from ENGINE.driftzero_gates import GATES_DATA as _GATES_DATA

GATES = [(g["id"], g["th"], g["en"], _rx(*g["patterns"]), g["why_th"], g["why_en"]) for g in _GATES_DATA]

_GATE_INFO = {g[0]: g for g in GATES}

# สัญญาณว่ามีการพูดถึงผลเสียแล้ว (SOP 2) และมีคนรับผิดชอบ (SOP 6)
_DOWNSIDE = _rx(r"ความเสี่ยง|ผลเสีย|ข้อเสีย|ถ้าพลาด|ถ้าล้มเหลว|เสียหาย|ขาดทุน|แผนสำรอง|risk|downside|worst case|if it fails|fallback")
_FLOOR = _rx(r"ขั้นต่ำ|ไม่ต่ำกว่า|อย่างน้อย|สำรอง(?:ไว้)?\s*\d|เงินสดสำรอง|runway|minimum|at least|floor|reserve of")
_OWNER = _rx(r"ผู้รับผิดชอบ|รับผิดชอบโดย|เซ็นอนุมัติ|ผู้อนุมัติ|คณะกรรมการ|บอร์ด|ผู้จัดการ|หัวหน้าโครงการ|accountab|sign(?:ed|s)? off|approv(?:er|ed by)|\bboard\b|\bowner\b")
_DRIFT = _rx(r"ทุกวัน|ต่อวัน|รายวัน|วันละ|/วัน|ต่อเดือน|เดือนละ|/เดือน|ทีละนิด|สะสม|เพิ่มขึ้นเรื่อยๆ|ลดลงเรื่อยๆ|per day|daily|per month|accumulat|gradually")
_NUM = re.compile(r"\d")
# เป็นเรื่องตัดสินใจขององค์กร/โครงการจริงไหม — ไม่ใช่ ให้แนะนำโหมดปรึกษา
_ORG = _rx(r"empresa|negocio|tienda|clientes|empleados|công ty|cửa hàng|khách hàng|nhân viên|公司|客户|员工|店铺|회사|가게|직원|고객|会社|店舗|従業員|顧客|店を|社員|残業|工場|事業|คลินิก|โรงพยาบาล|โรงเรียน|มหาวิทยาลัย|ครู|นักเรียน|คนไข้|ผู้ป่วย|ฟาร์ม|ไร่|แปลง|คนงาน|ไซต์งาน|ผู้รับเหมา|มูลนิธิ|สมาคม|สหกรณ์|วัด|เทศบาล|อบต|clinic|farm|charity|foundation|nonprofit|ngo|contractor|drivers?|patients?|students?|board|investors?|บริษัท|องค์กร|โครงการ|โรงงาน|ธุรกิจ|ร้าน|สาขา|นโยบาย|ชุมชน|หน่วยงาน|ทีม|พนักงาน|ลูกค้า|ซัพพลายเออร์|งบประมาณ|ลงทุน|ผลิต|"
           r"company|organi[sz]ation|project|factory|business|policy|team|staff|budget|invest|supplier|community|plant|"
           r"\bstores?\b|\bshops?\b|branch|employee|customer|startup|school|hospital|department|government|firm|launch|hire|hiring|layoff|"
           # ผู้ใช้จริงคนแรกถามว่า "spend 10k on facebook ads" แล้วโดนบอกว่า "ดูเหมือนเป็นเรื่องส่วนตัว" — งานขาย/การตลาดก็คือการตัดสินใจของกิจการ
           r"\bads?\b|advertis|marketing|campaign|revenue|\bsales\b|clients?\b|product|vendor|contract|pricing|\bbrand\b|"
           r"โฆษณา|การตลาด|แคมเปญ|ยอดขาย|สินค้า|รายได้|กิจการ|แบรนด์|ยิงแอด|เปิดร้าน")

SOP = [
    ("กำหนดเรื่องที่จะตัดสินใจให้ชัด", "Define input clearly"),
    ("ดูผลเสียก่อน", "Identify downside first"),
    ("วัดการไหลลงทีละนิด (DHD)", "Measure drift (DHD)"),
    ("ผ่านด่าน K4–K14", "Pass K4–K14 gates"),
    ("อธิบายได้ใน 2 นาที", "Explain within 2 minutes"),
    ("คนเซ็นรับผิดชอบ", "Human signs accountability"),
    ("ตรวจหลังทำ แล้วปิดวงจร", "Post-audit and close loop"),
]


def _money(v) -> str:
    if v is None:
        return "-"
    for unit, d in (("พันล้าน", 1e9), ("ล้าน", 1e6)):
        if abs(v) >= d:
            return f"{v / d:,.2f}".rstrip("0").rstrip(".") + " " + unit
    return f"{v:,.0f}"


def _money_en(v) -> str:
    if v is None:
        return "-"
    for unit, d in (("B", 1e9), ("M", 1e6)):
        if abs(v) >= d:
            return f"{v / d:,.2f}".rstrip("0").rstrip(".") + unit
    return f"{v:,.0f}"


@functools.lru_cache(maxsize=128)
def _read(text: str) -> tuple:
    """อ่านข้อความด้วยตัวจับหลักครั้งเดียว แล้วใช้ซ้ำ — เดิม DriftZero เรียกซ้ำ 2-3 รอบต่อข้อความ
    (ข้อความยาว 4,000 ตัวอักษรใช้เวลาถึง 1.7 วินาที) คืนเป็น tuple ที่แก้ไม่ได้ กันไม่ให้ผลในแคชถูกแก้โดยไม่ตั้งใจ"""
    from core.kernel_voice import assess
    a = assess(text)
    return (bool(a.get("crisis")), tuple(a.get("topics") or ()), a.get("text_risk", 0))


def _danger(text: str) -> tuple[bool, bool]:
    """(วิกฤตของคน, เหตุอันตรายตอนนี้)
    วิกฤตของคน (คิดทำร้ายตัวเอง) = ไม่ใช่เวลาตรวจด่าน ส่งไปหาความช่วยเหลือ
    เหตุอันตราย (สารเคมีรั่ว ไฟไหม้ คนเจ็บ) = ยังตรวจด่านได้ แต่ต้องโชว์เบอร์ฉุกเฉินก่อน — เดิม "สารเคมีรั่วในไลน์ผลิต"
    ถูกตัดไปเป็นเรื่องด่วนทั้งก้อน เลยไม่เห็นด่าน K12 Stop the line ที่ตรงที่สุด"""
    try:
        crisis_flag, topics, risk = _read(str(text or ""))
        crisis = crisis_flag or "crisis" in topics
        return crisis, (not crisis and risk >= 85)
    except Exception:
        return False, False


ASK_KEYS = ("detail", "downside", "dhd", "current", "floor", "owner")
# หัวข้อของตัวจับหลักที่แปลว่า "ผู้ใช้เองกำลังลำบาก" — เช่น Haydn ตอบคำถามด่านว่า "i can't pay rent"
# เรื่องแบบนี้ไม่ใช่การตัดสินใจขององค์กร ชวนไปโหมดปรึกษาแทนการถามด่านต่อ
_DISTRESS = {"housing", "money", "debt", "basic", "lent", "job", "labor", "stress", "lonely", "panic",
             "grief", "eating", "sleepless", "family", "relationship", "health"}
# เลขเปล่าๆ ตามด้วยหน่วย ("ขาดทุน 3 แสน" · "hire 3 people") คือจำนวน ไม่ใช่เลขข้อ — เลขข้อที่มีจุด/วงเล็บ ("3.") นับเสมอ
_UNIT = (r"(?:แสน|ล้าน|พัน|หมื่น|บาท|คน|วัน|เดือน|ปี|สัปดาห์|ชั่วโมง|นาที|เท่า|แห่ง|สาขา|ครั้ง|ตัว|ชิ้น|กิโล|ลิตร|ตัน|%|"
         r"people|persons?|staff|days?|weeks?|months?|years?|hours?|times|stores?|branches|units?|million|thousand|percent)")
_MARK = re.compile(r"(?:^|(?<=\s))(?:ข้อ\s*)?(\d{1,2})(?:\s*[).:\-]\s*|\s+(?!" + _UNIT + r"(?![a-z])))")


def parse_numbered(answer: str) -> dict[int, str]:
    """แยกคำตอบแบบเป็นข้อ "1 i do it 2. i can't pay rent 3 1k" → {1: "i do it", 2: "i can't pay rent", 3: "1k"}
    ต้องเริ่มที่ 1 และนับเรียงทีละข้อ — ตัวเลขอื่นในประโยค ("จ้าง 5 คน") ไม่ถูกนับเป็นเลขข้อ"""
    a = str(answer or "").strip()
    cuts, want = [], 1
    for m in _MARK.finditer(a):
        if int(m.group(1)) == want:
            cuts.append((want, m.start(), m.end())); want += 1
    if not cuts or cuts[0][1] != 0:
        tagged = list(re.finditer(r"(?:^|\s)ข้อ\s*(\d{1,2})\s*[).:\-]?\s*", a))   # "ข้อ 2 ขั้นต่ำ 2 แสน ข้อ 4 ผมเอง"
        if not tagged or tagged[0].start() != 0:
            return {}
        return {int(m.group(1)): a[m.end():(tagged[i + 1].start() if i + 1 < len(tagged) else len(a))].strip(" ,;\n")
                for i, m in enumerate(tagged) if a[m.end():(tagged[i + 1].start() if i + 1 < len(tagged) else len(a))].strip(" ,;\n")}
    out = {}
    for i, (n, _, end) in enumerate(cuts):
        stop = cuts[i + 1][1] if i + 1 < len(cuts) else len(a)
        part = a[end:stop].strip(" ,;\n")
        if part:
            out[n] = part
    return out


# คำตอบบอกตัวเองว่าเป็นคำตอบของข้อไหน — คนจริงข้ามข้อ ตอบทีละข้อ หรือเล่ารวดเดียว ("ขั้นต่ำ 2 แสน" = เส้นขั้นต่ำ ไม่ว่าจะอยู่ข้อไหน)
_SIGNAL = (
    ("floor", _rx(r"ขั้นต่ำ|อย่างน้อย|ไม่ต่ำกว่า|ห้ามต่ำกว่า|ต้องเหลือ|at least|minimum|floor|must not (?:go |fall )?below")),
    ("dhd", _rx(r"วันละ|ต่อวัน|เดือนละ|ต่อเดือน|/วัน|/เดือน|per day|a day|daily|per month|a month|monthly")),
    ("current", _rx(r"ตอนนี้มี|มีเงิน(?:สด)?|เงินสด(?:คงเหลือ)?|คงเหลือ|on hand|cash balance|we have|i have")),
    ("owner", _rx(r"ผมเอง|ฉันเอง|หนูเอง|ตัวเอง|เจ้าของ|รับผิดชอบ|ผู้จัดการ|หัวหน้า|บอร์ด|หุ้นส่วน|ผู้อนุมัติ|\bme\b|myself|\bi am\b|\bi'?ll\b|\bowner\b|\bmanager\b|\bboard\b|\bceo\b|\bfounder\b")),
    ("downside", _rx(r"ถ้าพลาด|ถ้าล้ม|เสีย(?:เงิน|ลูกค้า|ชื่อ|หาย)?|ขาดทุน|เจ๊ง|ปิดร้าน|\blose\b|\blost\b|worst|\bfail")),
)
_DONT_KNOW = re.compile(r"^(?:ไม่รู้|ไม่แน่ใจ|ไม่ทราบ|ยังไม่รู้|ไม่ได้จด|(?i:i\s+don'?t\s+know|not\s+sure|no\s+idea))", re.I)


def _classify(part: str, keys) -> str | None:
    for k, rx in _SIGNAL:
        if k in keys and rx.search(part or ""):
            return k
    return None


def assign(answer: str, prior_keys) -> dict:
    """จับคู่คำตอบกับคำถาม: ดูเนื้อหาก่อน (ขั้นต่ำ · วันละ · ผมเอง) แล้วค่อยใช้ลำดับเลขข้อ"""
    keys = [k for k in (prior_keys or []) if k in ASK_KEYS]
    a = str(answer or "").strip()
    out = {}
    parts = parse_numbered(a)
    if parts:
        for n, v in sorted(parts.items()):
            left = [k for k in keys if k not in out]
            pos = keys[n - 1] if 0 < n <= len(keys) and keys[n - 1] not in out else None
            k = _classify(v, left)
            # ข้อ "เล่าเพิ่ม ใครทำอะไร" ตอบว่า "me and my partner" ก็ถูกข้อแล้ว — ย้ายไปข้ออื่นเฉพาะเมื่อเป็นตัวเลข/ผลเสียชัดๆ
            if pos and (k is None or k == pos or (pos == "detail" and k == "owner")):
                k = pos
            if k:
                out[k] = v
        return out
    if not a or _DONT_KNOW.match(a):
        return out
    if len(keys) == 1:
        return {keys[0]: a}
    if re.fullmatch(r"[\d,.\s]+(?:พันล้าน|ล้าน|แสน|หมื่น|พัน|บาท|[kKmM])?\s*(?:บาท)?", a):   # ตอบตัวเลขเปล่าๆ = ข้อตัวเลขข้อแรกที่ถามอยู่
        k = next((k for k in keys if k in ("floor", "current")), None)
        return {k: a} if k else {}
    hits = sorted((m.start(), k) for k, rx in _SIGNAL if k in keys for m in [rx.search(a)] if m)
    seen = []
    for pos, k in hits:
        if k not in [x for _, x in seen]:
            seen.append((pos, k))
    for i, (pos, k) in enumerate(seen):                       # เล่ารวดเดียว: ตัดเป็นช่วงตามสัญญาณที่เจอ
        start = 0 if i == 0 else pos
        stop = seen[i + 1][0] if i + 1 < len(seen) else len(a)
        out[k] = a[start:stop].strip(" ,;")
    return out


def answered_keys(answer: str, prior_keys) -> set[str]:
    """คำถามรอบก่อนข้อไหนที่ผู้ใช้ตอบแล้ว"""
    return set(assign(answer, prior_keys))


def distress(text: str) -> bool:
    try:
        return bool(_DISTRESS & set(_read(str(text or ""))[1]))
    except Exception:
        return False


# คำตอบแต่ละข้อถูกเก็บต่อท้ายเรื่องเดิมเป็นบรรทัดที่มีป้ายกำกับ — ตัววัด Waterline อ่านตัวเลขจากป้ายได้ทันที
# ("floor: 1k" · "cash on hand: 3k") และใบสรุปอ่านคำตอบกลับออกมาได้โดยไม่ต้องให้หน้าเว็บจำอะไรเพิ่ม
LABELS = {"detail": "detail", "downside": "worst case", "floor": "floor", "current": "cash on hand",
          "dhd": "drift per day", "owner": "accountable"}
_LABEL_LINE = re.compile(r"^(" + "|".join(re.escape(v) for v in LABELS.values()) + r"): (.+)$", re.M)
_BRIEF_ROWS = (("downside", "ถ้าพลาด", "Worst case"), ("floor", "เส้นขั้นต่ำ", "Floor"), ("current", "ตอนนี้มี", "On hand now"),
               ("dhd", "สิ่งที่ต้องเฝ้าดูทุกวัน", "Watch daily"), ("owner", "คนรับผิดชอบ", "Accountable"), ("detail", "รายละเอียด", "Details"))


def brief(text: str, wl: dict) -> dict | None:
    """ใบสรุปการตัดสินใจ — รวมสิ่งที่ผู้ใช้ตอบมา + ตัวเลขที่คำนวณได้ + กติกาหยุด เป็นแผ่นเดียวที่คัดลอกไปใช้ต่อได้
    เดิมตอบครบแล้วได้แค่ "ผ่านทุกด่าน" คนที่อุตส่าห์ตอบไม่ได้อะไรกลับไปเลย"""
    by_label = {v: k for k, v in LABELS.items()}
    got = {}
    for m in _LABEL_LINE.finditer(text):
        got[by_label[m.group(1)]] = m.group(2).strip()
    if not got:
        return None
    decision = _LABEL_LINE.split(text)[0].strip()
    rows = [{"k": "decision", "th": "เรื่องที่จะตัดสินใจ", "en": "Decision", "v": decision[:400]}]
    rows += [{"k": k, "th": th, "en": en, "v": got[k][:400]} for k, th, en in _BRIEF_ROWS if k in got]
    fl, cur, sp, after = wl.get("floor"), wl.get("current"), wl.get("spend"), wl.get("after")
    rule = None
    if after is not None and wl.get("level") == "below":
        room = cur - fl
        if room > 0:
            rule = {"th": f"ขนาดนี้ยังไม่ควรทำ: จะเหลือ {_money(after)} ต่ำกว่าเส้นขั้นต่ำ {_money(fl)} · ทำได้มากสุด {_money(room)} โดยไม่หลุดเส้น — ลดขนาดหรือแบ่งทำเป็นช่วง",
                    "en": f"Not at this size: you would be left with {_money_en(after)}, under your floor of {_money_en(fl)}. "
                          f"The most you can put in without crossing it is {_money_en(room)} — shrink it or do it in phases."}
        else:
            rule = {"th": f"ตอนนี้อยู่ที่เส้นขั้นต่ำ ({_money(fl)}) หรือต่ำกว่าแล้ว — ยังไม่ควรใช้เพิ่ม ทำให้กลับมาเหนือเส้นก่อน",
                    "en": f"You are already at or under your floor ({_money_en(fl)}) — don't put more in; get back above it first."}
    elif after is not None:
        rule = {"th": f"หลังทำจะเหลือ {_money(after)} ยังเหนือเส้นขั้นต่ำ {_money(fl)} · กติกาหยุด: ถ้าลงมาแตะ {_money(fl)} ให้หยุดแล้วตรวจใหม่ทันที",
                "en": f"After this you would have {_money_en(after)}, still above your floor of {_money_en(fl)}. "
                      f"Stop rule: the moment it reaches {_money_en(fl)}, pause and re-check."}
        d = wl.get("days_to_floor")
        if d is not None:
            rule["th"] += f" · ด้วยอัตราตอนนี้จะถึงเส้นในอีก {d} วัน"
            rule["en"] += f" At the current pace you reach it in {d} days."
    elif fl is not None:
        rule = {"th": f"กติกาหยุด: ถ้าลงมาแตะ {_money(fl)} ให้หยุดแล้วตรวจใหม่ทันที",
                "en": f"Stop rule: the moment you reach {_money_en(fl)}, pause and re-check."}
    return {"rows": rows, "rule": rule,
            "next": {"th": "ทำแล้วกลับมาตรวจอีกครั้งว่าเกิดอะไรขึ้นจริง (ตรวจหลังทำ) — คุณเป็นคนตัดสินใจเสมอ",
                     "en": "After you act, come back and check what actually happened (post-audit) — the decision is always yours."}}


# ผู้ใช้จริงคนแรกงงกับหน้าจอ แล้วพิมพ์ถามในโหมดนี้ว่า "what does drift zero do?" — เดิมระบบเอาคำถามนั้นไปตรวจด่านเหมือนเป็นการตัดสินใจ
_ABOUT = _rx(r"what (?:does|is) (?:this|it|drift ?zero)\b|how (?:does|do) (?:this|it|drift ?zero|i use)\b|what (?:do|should) i (?:do|type|write)\b|"
             r"^\s*(?:help|\?+|how to use)\s*\??\s*$|i(?:'m| am) confused|i don'?t (?:understand|get it)|"
             r"drift ?zero (?:คืออะไร|ทำอะไร|ใช้ยังไง|ใช้อย่างไร)|(?:โหมดนี้|อันนี้|นี่)(?:คืออะไร|ทำอะไร|ใช้ยังไง)|ใช้ยังไง|ต้องพิมพ์อะไร|ไม่เข้าใจ|(?<!โร)งง(?!าน)")   # "งง" ต้องไม่ใช่ส่วนของคำว่า "โรงงาน"
ABOUT_TEXT = {
    "th": "DriftZero คือรายการตรวจก่อนตัดสินใจเรื่องใหญ่ เช่น \"ใช้เงิน 10,000 ยิงโฆษณา\" — ตรวจด้วยกฎ ไม่ใช้ AI ข้อความเดิมได้ผลเดิมเสมอ\n"
          "วิธีใช้: 1) พิมพ์สิ่งที่กำลังจะตัดสินใจ  2) ตอบคำถามสั้นๆ ที่ระบบถามกลับ พิมพ์เป็นข้อ (1 … 2 …) ได้  "
          "3) รับใบสรุป: ควรทำ รอ หรือหยุด พร้อมตัวเลขว่าทำได้มากสุดเท่าไหร่ — คุณเป็นคนตัดสินใจเสมอ\n"
          "ถ้าอยากคุยเล่าเรื่องทั่วไป กดไปโหมดปรึกษาได้เลยค่ะ",
    "en": "DriftZero is a pre-decision checklist for a big call like \"spend 10k on Facebook ads\". It runs on rules, not AI, so the same text always gives the same result.\n"
          "How to use it: 1) type the decision you are about to make  2) answer the few short questions it asks back — numbered replies (1 … 2 …) are fine  "
          "3) get a brief: go, wait or stop, with the most you can put in safely. The decision is always yours.\n"
          "For an open conversation, switch to Talk mode.",
}


def is_about(text: str) -> bool:
    t = str(text or "").strip()
    return len(t) <= 80 and bool(_ABOUT.search(t)) and not parse_numbered(t) and not _SINKING.search(t)


def about(prior: dict | None = None) -> dict:
    """คำอธิบายโหมด — ถ้ากำลังตอบคำถามค้างอยู่ คำถามเดิมยังอยู่ครบ ตอบต่อได้เลย ไม่ต้องเริ่มใหม่"""
    r = dict(prior) if prior else {"text": "", "talk": False, "gates": [], "asks": [], "sop": [], "note": None,
                                   "emergency": False, "brief": None, "waterline": None}
    r.update(verdict="about", about=True, summary=dict(ABOUT_TEXT), talk=True if not prior else r.get("talk", False))
    return r


def follow_up(prior_text: str, prior_keys, answer: str) -> dict:
    """ตรวจรอบต่อ: รวมเรื่องเดิมกับคำตอบ แล้วถามเฉพาะข้อที่ยังขาด — เดิมตรวจแค่ข้อความใหม่ เลยถามซ้ำครบทุกข้อ"""
    prior_text = str(prior_text or "").strip()[:4000]
    answer = str(answer or "").strip()[:4000]
    if is_about(answer):
        return about(audit(prior_text))
    if _danger(answer)[0]:                       # คำตอบรอบต่อเป็นเรื่องชีวิต ("อยากตายเลย") — ช่วยเหลือฉุกเฉินมาก่อนทุกอย่าง
        return audit(answer)
    if _CANCEL.search(answer):
        return cancelled(prior_text)
    if list(prior_keys or []) == ["dhd"] and sinking(prior_text):
        return steady_runway(prior_text, answer)
    pairs = assign(answer, prior_keys)
    got = set(pairs)
    skipped = None
    if not pairs and _DONT_KNOW.match(answer.strip()):
        keys_left = [k for k in (prior_keys or []) if k in ASK_KEYS]
        if keys_left:
            skipped = keys_left[0]                # "ไม่รู้" = ข้ามข้อนั้นไปก่อน ไม่ถามซ้ำวนไม่จบ
            got.add(skipped)
    parts = parse_numbered(answer)
    body = " ".join(parts.values()) if parts else answer
    lines = [f"{LABELS[k]}: {v}" for k, v in pairs.items()] if pairs else [answer]
    if skipped:
        lines = [f"{LABELS[skipped]}: (ยังไม่ทราบ)"]       # เก็บไว้ในเรื่อง รอบต่อไปจะได้ไม่ถามข้อนี้ซ้ำ
    lines = [" ".join(x.split()) for x in lines if x]              # หนึ่งคำตอบ = หนึ่งบรรทัด
    r = audit((prior_text + "\n" + "\n".join(lines)).strip(), answered=got)
    r["answered"] = sorted(got)
    if skipped:
        r["skipped"] = skipped
    if r["verdict"] != "urgent" and distress(body):
        r["note"] = {"th": "ฟังดูเหมือนคุณเองกำลังลำบากเรื่องนี้อยู่ — DriftZero ตรวจการตัดสินใจขององค์กร "
                           "ส่วนเรื่องเงิน ที่พัก หรือความเครียดของตัวเอง โหมดปรึกษาช่วยได้ตรงกว่า ลองเล่าที่นั่นได้เลยนะคะ",
                     "en": "It sounds like you're going through this yourself — DriftZero checks decisions made by organisations. "
                           "For your own money, housing or stress, Talk mode can help much more. You can tell LYLA there."}
        r["talk"] = True
    return r


_WORST_LINE = re.compile(r"^worst case: .*$", re.M)


def _answered_before(text: str) -> set[str]:
    by_label = {v: k for k, v in LABELS.items()}
    return {by_label[m.group(1)] for m in _LABEL_LINE.finditer(text or "")}


# ด่านที่ดูเฉพาะตัวแผน (ไม่ดูคำตอบข้อ "ถ้าพลาด") — คนที่ตอบตรงๆ ว่าอาจเสียอะไรต้องไม่โดนหยุดเพราะความซื่อสัตย์
_PLAN_ONLY = {"H1", "S1", "S2", "A1", "L1", "L2", "G1", "P1", "F1"}
# คำปฏิเสธนำหน้า: "จะไม่ขายข้อมูลลูกค้า" "ห้ามจ่ายใต้โต๊ะ" "we will never sell customer data" — เป็นนโยบายที่ดี ไม่ใช่สิ่งที่ต้องหยุด
_NEG_BEFORE = re.compile(r"(?:ไม่|ห้าม|ไม่มีการ|ไม่ยอม|ปฏิเสธ|เลิก|หยุด|ต่อต้าน|ป้องกัน(?:การ)?)\s*(?:\S{0,6})?\s*$|"
                         r"(?i:\b(?:not|never|no|won'?t|don'?t|do\s+not|will\s+not|refuse\s+to|stop|avoid|prevent|against|bans?|banned|forbids?|forbidden|prohibits?|prohibited|zero\s+tolerance\s+(?:for|on))\b[\w\s'-]{0,12}$)")


_TREATED = re.compile(r"บำบัด|ผ่านการบำบัด|ที่มีใบอนุญาต|ได้รับอนุญาต|ได้มาตรฐาน|แทนการเผา|(?i:\btreat(?:ed|ment)\b|\blicensed\b|\binstead\s+of\s+burning\b)")
_ENV_WORD = re.compile(r"น้ำ|คลอง|แม่น้ำ|กาก|ขยะ|สาร|เผา|ตอซัง|(?i:waste|water|river|burn|tailings|chemical)")


def _negated(text: str, m) -> bool:
    before = text[max(0, m.start() - 16):m.start()]
    # คำปฏิเสธที่อยู่ในตัวรูปประโยคเอง ("ไม่จ่ายค่าโอที" "โดยไม่ขอความยินยอม") คือสิ่งที่ผิด ไม่ใช่การปฏิเสธการทำผิด
    return bool(_NEG_BEFORE.search(before)) and not re.match(r"(?:ไม่|ยังไม่|โดยไม่|no\b|without\b|not\b)", m.group(0), re.I)


_CANCEL = re.compile(r"^(?:ขอ)?(?:ยกเลิก|ไม่ทำแล้ว|เลิกคิด|ไม่เอาแล้ว|พอแล้ว)|ไม่ทำแล้ว|(?i:^(?:cancel|never\s?mind|forget\s+it)\b|\bnot\s+doing\s+it\b|\bwon'?t\s+do\s+it\b)")


def cancelled(prior_text: str) -> dict:
    """ผู้ใช้เปลี่ยนใจไม่ทำ — การไม่ทำก็เป็นการตัดสินใจที่ดีได้ ไม่ถามต่อ"""
    msg = {"th": "ได้เลยค่ะ การตัดสินใจไม่ทำก็เป็นการตัดสินใจที่ดีได้เหมือนกัน — ถ้าวันไหนอยากกลับมาคิดใหม่ เล่ามาได้เสมอนะคะ",
           "en": "Of course — choosing not to do it can be a good decision too. If you want to think it through again, just tell me any time."}
    return {"text": "", "verdict": "pass", "talk": False, "gates": [], "sop": [], "asks": [], "emergency": False,
            "brief": None, "waterline": None, "note": None, "summary": msg, "lyla": msg, "cancelled": True}


def steady_runway(prior_text: str, answer: str) -> dict:
    """รอบต่อของ "ตั้งหลักก่อน": คำนวณว่าเงินที่เหลือพาไปได้กี่วัน แล้วไม่ถามอะไรเพิ่ม"""
    from ENGINE.waterline_gauge import gauge
    wl = gauge(prior_text)
    r = steady(prior_text, wl)
    r["asks"] = []
    r["answered"] = ["dhd"]
    cur, out = wl.get("current"), _daily_out(answer)
    inflow = not re.search(r"ไม่มี(?:เงิน)?เข้า|(?i:\bnothing\s+(?:is\s+)?coming\s+in|no\s+(?:money|income)\s+(?:is\s+)?coming)", answer or "")
    if cur and out:
        days = int(cur // out)
        r["runway_days"] = days
        th = f"ด้วยเงินออกวันละ {_money(out)} เงิน {_money(cur)} ที่เหลือพาไปได้ราว {days} วัน"
        en = f"At {_money_en(out)} going out a day, the {_money_en(cur)} you have left lasts about {days} day{'' if days == 1 else 's'}"
        if not inflow:
            th += " และตอนนี้ยังไม่มีเงินเข้า — ข้อ 1–3 ข้างล่างคือสิ่งที่ยืดเวลานี้ได้มากที่สุด เริ่มวันนี้เลยนะคะ"
            en += ", with nothing coming in yet — steps 1–3 below are what stretch that time the most. Start today."
        else:
            th += " — ข้อ 1–3 ข้างล่างช่วยยืดเวลานี้ได้ เริ่มวันนี้เลยนะคะ"
            en += " — steps 1–3 below help stretch that. Start today."
    elif cur and _due(answer):
        due = _due(answer)
        left = cur - due
        r["after_due"] = left
        if left >= 0:
            th = (f"ถ้าจ่าย {_money(due)} ตามที่ต้องจ่าย จะเหลือ {_money(left)} — กันเงินก้อนนี้ไว้ก่อนเลย "
                  "แล้วใช้ข้อ 1–3 ข้างล่างหาทางให้เงินที่เหลือพอไปอีกนิดนะคะ")
            en = (f"If you pay the {_money_en(due)} that's due, {_money_en(left)} is left — set that payment aside first, "
                  "then use steps 1–3 below to stretch the rest.")
        else:
            th = (f"ที่ต้องจ่าย {_money(due)} มากกว่าเงินที่มี {_money(cur)} อยู่ {_money(-left)} — "
                  "รีบคุยกับคนที่จะเก็บเงิน (เจ้าของที่ ธนาคาร) ตอนนี้เลย ขอแบ่งจ่ายหรือเลื่อนก่อนถึงวันครบกำหนด ข้อ 3 ข้างล่างค่ะ")
            en = (f"What's due ({_money_en(due)}) is {_money_en(-left)} more than you have ({_money_en(cur)}) — "
                  "talk to whoever you owe (landlord, bank) now and ask to split or delay before the due date (step 3 below).")
    else:
        th = "ขอบคุณที่เล่าค่ะ — ข้อ 1–3 ข้างล่างคือสิ่งที่ช่วยยืดเวลาได้มากที่สุด เริ่มจากข้อ 1 วันนี้เลยนะคะ"
        en = "Thank you for telling me — steps 1–3 below are what buy you the most time. Start with step 1 today."
    r["summary"] = {"th": th, "en": en}
    return r


# คนที่กำลังจะไม่ไหว ไม่ใช่องค์กรที่กำลังวางแผน — "ธุรกิจกำลังจะพัง เงินเหลือ 3000 กู้ใครก็ไม่ได้แล้ว กำลังล้ม"
# เดิมโดนถาม "Waterline คือเท่าไหร่ · DHD · ใครเซ็นรับผิดชอบ" ทั้งที่บอกตัวเลขมาแล้ว และน้ำเสียงกำลังจะล้ม
_SINKING = re.compile(r"se está hundiendo|a punto de quebrar|en quiebra|no puedo pagar|sắp phá sản|phá sản|không trả nổi|快倒闭|要倒闭|撑不下去|快破产|망하기 직전|망할 것 같|폐업 직전|倒産しそう|潰れそう|กำลัง(?:จะ)?(?:ล้ม|พัง|เจ๊ง|จม)|จะ(?:ล้ม|พัง|เจ๊ง)แล้ว|(?:ร้าน|ธุรกิจ|กิจการ|บริษัท|โรงงาน)\S{0,6}จะ(?:เจ๊ง|พัง|ล้ม)(?!\S{0,3}(?:ไหม|มั้ย|หรือเปล่า|ถ้า))|ไม่ไหวแล้ว|หมดทาง|ไม่รู้จะ(?:ทำ|ไป)(?:ยังไง|ไง|ไหน)|"
                      r"กู้\S{0,6}(?:ไม่ได้|ไม่ผ่าน)|ไม่มีใครให้(?:ยืม|กู้)|ยืมใครก็ไม่ได้|ไม่เหลืออะไร|สิ้นหวัง|ไปต่อไม่ไหว|"
                      r"(?i:\b(?:going\s+under|losing\s+everything|(?:can'?t|cannot)\s+(?:pay|borrow|keep\s+going)|"
                      r"no\s+one\s+will\s+lend|don'?t\s+know\s+what\s+to\s+do|about\s+to\s+collapse|i'?m\s+(?:sinking|drowning|done))\b)")


_MONEY_TALK = re.compile(r"negocio|tienda|dinero|dólares|cửa hàng|tiền|triệu|công ty|公司|店|钱|가게|돈|회사|お金|会社|เงิน|หนี้|ขาดทุน|กู้|ยืม|ค่าเช่า|เจ๊ง|ร้าน|กิจการ|ธุรกิจ|"
                         r"[$฿€£]\s?\d|(?i:\b(?:money|debt|loan|lend|borrow|rent|dollars?|baht|cash|shop|store|restaurant|business|company|bills?|pay|wages?|salar(?:y|ies)|staff)\b)")
_NO_MONEY = re.compile(r"เงินหมด|ไม่มีเงิน(?:เหลือ)?|ไม่เหลือเงิน|หมดตัว|(?i:\b(?:no\s+money\s+left|out\s+of\s+money|broke|nothing\s+left)\b)")
_PER_DAY = re.compile(r"(?:วันละ|ต่อวัน|(?i:\b(?:per|a|each)\s+day\b))")


def sinking(t: str) -> bool:
    """คนที่กิจการ/การเงินกำลังจะล้ม — ต้องมีเรื่องเงินหรือกิจการด้วย ("ไม่ไหวแล้ว" เฉยๆ เป็นเรื่องใจ ให้ไปคุยกับ LYLA)"""
    return bool(_SINKING.search(t or "")) and bool(_MONEY_TALK.search(t or ""))


def only_heart(t: str) -> bool:
    return bool(_SINKING.search(t or "")) and not _MONEY_TALK.search(t or "") and distress(t)


_DUE = re.compile(r"(?:ค่าเช่า|ค่าไฟ|ค่าน้ำ|ค่าแรง|เงินเดือน|หนี้|ผ่อน|ต้องจ่าย|rent|wages?|loan|payment|bill)[^\d\n]{0,12}(?P<n>\d[\d,]*(?:\.\d+)?)\s*(?P<u>หมื่น|พัน|แสน|[kK](?![a-zA-Z]))?", re.I)


def _due(answer: str):
    """ "ค่าเช่า 6000 ต้องจ่ายสิ้นเดือน" → 6000 (ไม่นับถ้าเป็นอัตราต่อวัน) """
    from ENGINE.waterline_gauge import _val
    if _PER_DAY.search(answer or ""):
        return None
    m = _DUE.search(answer or "")
    return _val(m.group("n"), m.group("u")) if m else None


def _daily_out(answer: str):
    """อ่าน "วันละ 500" · "500 ต่อวัน" · "$40 a day" → 500.0"""
    from ENGINE.waterline_gauge import _val
    num = re.compile(r"(?P<n>\d[\d,]*(?:\.\d+)?)\s*(?P<u>พันล้าน|ล้าน|แสน|หมื่น|พัน|[kK](?![a-zA-Z]))?")
    for m in _PER_DAY.finditer(answer or ""):
        after = num.search(answer[m.end():m.end() + 20])          # "วันละ 500"
        before = list(num.finditer(answer[max(0, m.start() - 20):m.start()]))   # "500 ต่อวัน"
        hit = after or (before[-1] if before else None)
        if hit:
            return _val(hit.group("n"), hit.group("u"))
    return None


def heart(t: str) -> dict:
    """"ไม่ไหวแล้ว" ที่ไม่ใช่เรื่องเงินหรือกิจการ — ไม่ใช่งานของ DriftZero ชวนไปคุยกับ LYLA แทนการให้คำแนะนำเรื่องหนี้"""
    msg = {"th": "ฟังดูเหนื่อยมากเลยนะคะ เรื่องนี้ไม่ต้องผ่านด่านอะไรเลย — มาคุยกับ LYLA ในโหมดปรึกษาได้เลย "
                 "ถ้าหนักจนเริ่มคิดว่าไม่อยากอยู่ โทร 1323 ได้ 24 ชม. ฟรีค่ะ",
           "en": "That sounds exhausting. This doesn't need any gates — come and talk it through with LYLA in Talk mode. "
                 "If it gets so heavy you start thinking you don't want to be here, call 1323 in Thailand (24h, free)."}
    return {"text": t[:4000], "verdict": "steady", "talk": True, "gates": [], "sop": [], "asks": [], "steps": [],
            "emergency": False, "brief": None, "waterline": None, "note": None, "summary": msg}


def steady(t: str, wl: dict) -> dict:
    """ตั้งหลักก่อน: ใช้ตัวเลขที่เล่ามาแล้ว · บอกสิ่งที่ทำได้ทันที · ถามแค่ข้อเดียวด้วยภาษาธรรมดา"""
    cur = wl.get("current")
    broke = cur is None and bool(_NO_MONEY.search(t or ""))
    have_th = f"เงิน {_money(cur)} ที่เหลืออยู่" if cur is not None else ("เวลาและคนที่ช่วยได้" if broke else "เงินที่เหลืออยู่")
    have_en = f"the {_money_en(cur)} you have left" if cur is not None else ("your time and the people who can help" if broke else "what you have left")
    steps = [
        {"th": "หยุดเลือดก่อน: งดรายจ่ายใหม่ทุกอย่างที่ไม่ทำให้มีเงินเข้าภายใน 7 วัน",
         "en": "Stop the bleeding first: pause every new cost that won't bring money in within 7 days"},
        {"th": "แยกสิ่งที่ต้องจ่ายเป็น 3 กอง: ต้องจ่ายแน่ (ค่าแรง ค่าเช่าที่ทำกิน) · ขอเลื่อนได้ · หยุดได้เลย",
         "en": "Sort what you owe into 3 piles: must pay (wages, the rent you trade from) · can ask to delay · can stop now"},
        {"th": "โทรคุยเจ้าหนี้หรือธนาคารก่อนผิดนัด ขอพักชำระหรือปรับโครงสร้างหนี้ — คุยก่อนผิดนัดมักได้เงื่อนไขดีกว่าหลังผิดนัด",
         "en": "Call your lenders or bank before you miss a payment and ask to pause or restructure — talking first usually gets better terms"},
        {"th": "อย่ากู้นอกระบบมาอุดช่อง — ดอกเบี้ยแบบนั้นทำให้ล้มเร็วขึ้น ไม่ได้ช่วยให้รอด",
         "en": "Don't fill the gap with loan sharks — that interest makes you fall faster, not survive"},
        {"th": "ถ้าเครียดจนนอนไม่หลับ หรือเริ่มคิดว่าไม่อยากอยู่ โทร 1323 ได้ 24 ชม. ฟรี",
         "en": "If the stress keeps you from sleeping, or you start thinking you don't want to be here, call 1323 in Thailand (24h, free)"},
    ]
    if broke:
        ask = {"key": "dhd", "sop": 3, "th": "ตอนนี้มีอะไรที่ต้องจ่ายเร็วที่สุด และต้องจ่ายภายในกี่วัน — เริ่มจากเรื่องนั้นก่อนค่ะ",
               "en": "What has to be paid soonest, and within how many days? We'll start there."}
    else:
      ask = {"key": "dhd", "sop": 3,
             "th": f"ตอนนี้แต่ละวันมีเงินออกประมาณเท่าไหร่ และยังมีเงินเข้าบ้างไหม — จะได้ดูว่า{have_th}พาไปได้อีกกี่วัน",
             "en": f"Roughly how much goes out each day, and is anything still coming in? Then we can see how many days {have_en} buys you"}
    return {"text": t[:4000], "verdict": "steady", "talk": True, "gates": [], "sop": [], "asks": [ask], "steps": steps,
            "emergency": False, "brief": None,
            "waterline": dict(wl, show={"th": {k: _money(wl[k]) for k in ("floor", "current", "after")},
                                        "en": {k: _money_en(wl[k]) for k in ("floor", "current", "after")}}),
            "note": {"th": "เรื่องที่หนักขนาดนี้ คุยกับ LYLA ในโหมดปรึกษาได้ด้วยนะคะ ไม่ต้องแบกคนเดียว",
                     "en": "Something this heavy — you can also talk it through with LYLA in Talk mode. You don't have to carry it alone."},
            "summary": {"th": f"ตั้งหลักก่อนนะคะ — ยังไม่ต้องตอบเรื่องด่านหรือแผนใหญ่ {have_th}คือของมีค่าที่สุดตอนนี้ เริ่มจากรักษามันไว้",
                        "en": f"Let's steady things first — no gates or big plans yet. {have_en[0].upper() + have_en[1:]} is the most valuable thing right now; start by protecting it."}}


def gate_scan(text: str) -> list:
    """ตรวจด่านจากตัวข้อความล้วน (ไม่เรียกตัวจับหลัก ไม่คำนวณ Waterline) — ใช้ร่วมกับสภา 6 เสียงและอริยสัจ 4
    ทุกระบบจะได้มองจากหลักฐานชุดเดียวกัน ไม่ใช่ต่างคนต่างคิดเอง"""
    t = str(text or "")
    out = []
    for gid, th, en, rx, why_th, why_en in GATES:
        # H1 ดูเฉพาะ "แผน" ไม่ดูคำตอบข้อ "ถ้าพลาดจะเสียอะไร" — ผลเสียที่เล่ามาเป็นเรื่องสมมติ ไม่ใช่สิ่งที่ตั้งใจจะทำ
        plan = _WORST_LINE.sub("", t) if gid in _PLAN_ONLY else t
        m = rx.search(plan)
        if m and gid in ("E1", "E2") and _TREATED.search(plan) and _ENV_WORD.search(m.group(0)):
            m = None                      # "ติดเครื่องบำบัดน้ำเสียก่อนปล่อยลงคลอง" · "ส่งกากให้บริษัทกำจัดที่มีใบอนุญาต" — ทำถูกแล้ว
        if m and gid in _PLAN_ONLY and _negated(plan, m):
            m = next((x for x in rx.finditer(plan) if not _negated(plan, x)), None)
        out.append({"id": gid, "name": {"th": th, "en": en}, "status": STOP if m else PASS,
                    "hit": m.group(0) if m else "", "why": {"th": why_th, "en": why_en} if m else None})
    return out


# ดูข่าว/อ่านข่าวแล้วรู้สึก ไม่ใช่แผนที่จะทำ — "ดูข่าวไฟไหม้โรงงานแล้วสงสารคนงาน" เคยถูกนับว่าข้ามเส้น
_WATCHING_NEWS = re.compile(r"(?:ดู|อ่าน|เห็น|ฟัง)ข่าว|ในข่าว|ข่าวว่า|(?i:\b(?:saw|read|watched|heard)\s+(?:the\s+|a\s+)?news\b|\bon\s+the\s+news\b)")
_PRIORITY = ["F1", "P1", "K12", "E2", "E1", "L1", "L2", "G1", "S1", "S2", "A1", "K7", "H1"]
_SHARED = set(_PRIORITY)
_PLANNING = re.compile(r"(?:^|\s|ร้าน|บริษัท|โรงงาน|เรา|ผม|ฉัน)จะ|(?i:\b(?:we|i|they)(?:'ll|\s+will|\s+plan\s+to|\s+want\s+to)\b)")


def stop_reasons(text: str) -> list:
    """[(id, เหตุผลประโยคแรก th, en)] ของด่านที่ติด — สำหรับสภา 6 เสียงและอริยสัจ 4
    นับเฉพาะเมื่อข้อความเป็น "แผนที่จะทำ" หรือเรื่ององค์กร — คนที่เล่าว่าหมดไฟหรือไม่ได้นอน ไม่ได้กำลังวางแผนอะไร"""
    t = str(text or "")
    if not (_ORG.search(t) or _PLANNING.search(t)) or _WATCHING_NEWS.search(t):
        return []
    hits = [(g["id"], re.split(r" — | · ", g["why"]["th"])[0].strip(), re.split(r" — | · ", g["why"]["en"])[0].strip())
            for g in gate_scan(t) if g["status"] == STOP and g["id"] in _SHARED]
    return sorted(hits, key=lambda h: _PRIORITY.index(h[0]))      # เรื่องหนักสุดมาก่อน — มิจฉาชีพ/ชีวิต ก่อนเรื่องรอง


def audit(text: str, answered=()) -> dict:
    t = str(text or "").strip()
    answered = set(answered or ())
    if not answered and is_about(t):
        return about()
    crisis, emergency = _danger(t)
    if crisis:
        return {"verdict": "urgent", "gates": [], "asks": [], "sop": [],
                "summary": {"th": "เรื่องนี้เกี่ยวกับความปลอดภัยของชีวิต — ขอให้ติดต่อคนที่ช่วยได้ทันที "
                                  "(1669 เจ็บป่วยฉุกเฉิน · 191 ตำรวจ · 1323 สุขภาพจิต) แล้วค่อยกลับมาที่โหมดปรึกษานะคะ",
                            "en": "This is about someone's safety — please contact help now (in Thailand 1669 medical · 191 police · "
                                  "1323 mental health), then come back in Talk mode."}}
    from ENGINE.waterline_gauge import gauge
    wl = gauge(t)
    gates = []
    for g in gate_scan(t):
        if g["id"] == "E2":
            if wl["level"] == "below":                      # L0: ต่ำกว่าเส้นไม่ได้เด็ดขาด
                g.update(status=STOP, hit=g["hit"] or f"{_money(wl['after'])} < {_money(wl['floor'])}",
                         why={"th": f"ใต้ระดับน้ำ (Below Water) — หลังตัดสินใจเหลือ {_money(wl['after'])} ต่ำกว่าเส้น {_money(wl['floor'])} "
                                    "· Stop-the-Line: ต่ำกว่าเส้นนี้ความเสียหายย้อนกลับไม่ได้ ลดขนาดหรือแบ่งเป็นช่วงก่อน",
                              "en": f"Below water — after this decision {_money_en(wl['after'])} is under the floor {_money_en(wl['floor'])} "
                                    "· Stop the line: below this the damage can't be undone; shrink it or phase it first"})
            elif wl["days_to_floor"] is not None and wl["days_to_floor"] <= 30:
                g.update(status=STOP, hit=g["hit"] or f"{wl['days_to_floor']} days",
                         why={"th": f"จะแตะเส้นขั้นต่ำในอีก {wl['days_to_floor']} วันด้วยอัตราไหลลงตอนนี้ "
                                    "· Stop-the-Line: ดึงความเสี่ยงกลับก่อนถึงเส้น",
                              "en": f"At the current drift you reach the floor in {wl['days_to_floor']} days "
                                    "· Stop the line: pull the risk back before you reach it"})
        gates.append(g)
    stops = [g for g in gates if g["status"] == STOP]
    if not answered and not stops and sinking(t):
        return steady(t, wl)
    if not answered and not stops and only_heart(t):
        return heart(t)              # ไม่มีแผนเสี่ยงให้หยุด แต่คนกำลังจะล้ม — ตั้งหลักก่อน

    asks = []
    if len(t) < 40:
        asks.append({"key": "detail", "sop": 1, "th": "เล่าเพิ่มอีกนิด: ใครทำอะไร ที่ไหน งบเท่าไหร่ ภายในเมื่อไหร่",
                     "en": "Say a bit more: who does what, where, with what budget, by when"})
    if not _DOWNSIDE.search(t):
        asks.append({"key": "downside", "sop": 2, "th": "ถ้าพลาด อะไรเสียหายที่สุด และใครรับผลนั้น",
                     "en": "If this fails, what is the worst damage, and who bears it?"})
    if not (_DRIFT.search(t) and _NUM.search(t)):
        asks.append({"key": "dhd", "sop": 3, "th": "DHD: ถ้าทำต่อไปเรื่อยๆ อะไรจะแย่ลงทีละนิดทุกวัน — วัดเป็นตัวเลขอะไรได้บ้าง (เช่น เงินออกวันละเท่าไหร่ · ลูกค้าหายเดือนละกี่ราย · ของเสียกี่ลิตร/วัน)",
                     "en": "DHD (daily drift): if this keeps going, what gets a little worse every day — and what number shows it? (e.g. money going out per day, customers lost per month)"})
    if wl["floor"] is not None and wl["current"] is None:
        asks.append({"key": "current", "sop": 2, "th": "Waterline: ตอนนี้มีเท่าไหร่ (เช่น เงินสดคงเหลือ) — จะได้คำนวณว่าหลังตัดสินใจยังอยู่เหนือเส้นขั้นต่ำไหม",
                     "en": "Waterline: how much do you have right now (e.g. cash on hand)? Then I can work out whether you stay above your floor"})
    if wl["floor"] is None:
        asks.append({"key": "floor", "sop": 2, "th": "Waterline: เส้นขั้นต่ำของเรื่องนี้คือเท่าไหร่ — ตัวเลขที่ห้ามต่ำกว่า ไม่งั้นความเสียหายย้อนกลับไม่ได้ "
                                    "(เช่น ต้องเหลือเงินสดไม่ต่ำกว่า 50,000 · ทีมหลักไม่ต่ำกว่า 5 คน)",
                     "en": "Waterline (your floor): what is the lowest you can safely go — the number you must not fall below, or the damage can't be undone? "
                           "(e.g. keep at least 5k in cash · at least 5 core staff)"})
    if not _OWNER.search(t):
        asks.append({"key": "owner", "sop": 6, "th": "ใครเป็นคนรับผิดชอบการตัดสินใจนี้ (ชื่อหรือตำแหน่ง)",
                     "en": "Who is responsible for this decision? (a name or a role)"})

    answered |= _answered_before(t)
    asks = [q for q in asks if q["key"] not in answered]
    asks.sort(key=lambda q: q["sop"])
    if stops:
        verdict = "stop"
        sm_th = "หยุดก่อน — ติด " + " · ".join(f"{g['id']} {g['name']['th']}" for g in stops) + \
                " · แก้ด่านที่ติดให้ผ่านก่อน แล้วค่อยตรวจใหม่ (ต้นฉบับ: ทำให้นิ่งก่อน ค่อยทำให้ดีขึ้น)"
        sm_en = "Stop first — blocked at " + " · ".join(f"{g['id']} {g['name']['en']}" for g in stops) + \
                " · resolve these gates, then re-check (stabilize before optimizing)"
    elif asks:
        verdict = "ask"
        sm_th = f"ยังไม่เจอด่านที่ติด แต่ข้อมูลยังไม่ครบ {len(asks)} ข้อ — ตอบในช่องพิมพ์ได้เลย จะพิมพ์เป็นข้อ (1 … 2 …) ก็ได้"
        sm_en = f"No gate blocked yet, but {len(asks)} answer{' is' if len(asks) == 1 else 's are'} missing — reply below, numbered (1 … 2 …) is fine"
    else:
        verdict = "pass"
        sm_th = "ผ่านทุกด่านจากข้อมูลที่ให้มา — ยังต้องมีคนเซ็นรับผิดชอบ และตรวจหลังทำ (SOP 7)"
        sm_en = "Passes every gate on the information given — a human still signs off, and a post-audit closes the loop"

    done = {1: len(t) >= 40 or "detail" in answered, 2: bool(_DOWNSIDE.search(t)) or "downside" in answered,
            3: bool(_DRIFT.search(t) and _NUM.search(t)) or "dhd" in answered,
            4: not stops, 5: True, 6: bool(_OWNER.search(t)) or "owner" in answered, 7: False}
    sop = [{"n": i + 1, "th": th, "en": en, "done": done[i + 1]} for i, (th, en) in enumerate(SOP)]
    note = None
    if not _ORG.search(t):
        note = {"th": "ดูเหมือนเป็นเรื่องส่วนตัว — โหมดปรึกษาน่าจะช่วยได้ตรงกว่านะคะ",
                "en": "This looks personal — Talk mode will probably help more."}
    return {"text": t[:4000], "talk": bool(note), "verdict": verdict, "gates": gates, "asks": asks, "sop": sop, "note": note, "emergency": emergency, "brief": brief(t, wl), "waterline": dict(wl, show={
                "th": {k: _money(wl[k]) for k in ("floor", "current", "after")},
                "en": {k: _money_en(wl[k]) for k in ("floor", "current", "after")}}),
            "summary": {"th": sm_th, "en": sm_en}}


def lyla_voice(r: dict) -> dict:
    """LYLA รัน DriftZero แล้วเล่าผลเอง — บรรทัดแรกเป็นภาษาคน ส่วนด่าน/SOP อยู่ในการ์ดข้างล่าง"""
    v = r.get("verdict")
    if r.get("cancelled"):
        return r
    if v in ("urgent", "steady", "about") or not isinstance(r, dict):
        r["lyla"] = r.get("summary")
        return r
    stops = [g for g in r.get("gates") or [] if g.get("status") == STOP]
    # เรื่องหนักสุดมาก่อน (มิจฉาชีพ ชีวิต เส้นขั้นต่ำ) — เดิมคนที่กำลังโดนหลอกได้ยินเหตุผลแรกว่า "มั่นใจเกินจริง"
    stops.sort(key=lambda g: _PRIORITY.index(g["id"]) if g["id"] in _PRIORITY else len(_PRIORITY))
    n = len(r.get("asks") or [])
    wl = r.get("waterline") or {}
    cur = wl.get("current")
    seen_th = f" เห็นว่าตอนนี้มี {_money(cur)} นะคะ" if cur is not None else ""
    seen_en = f" I can see you have {_money_en(cur)} right now." if cur is not None else ""
    after, floor = wl.get("after"), wl.get("floor")
    if v == "stop":
        why = (stops[0].get("why") or {}) if stops else {}
        first_th = re.split(r" — | · ", why.get("th") or "")[0].strip()
        first_en = re.split(r" — | · ", why.get("en") or "")[0].strip()
        if stops and stops[0]["id"] == "E2" and wl.get("level") == "below" and after is not None and floor is not None:
            first_th = f"ถ้าทำตามนี้จะเหลือ {_money(after)} ต่ำกว่าเส้นขั้นต่ำที่ตั้งไว้ {_money(floor)} อยู่ {_money(floor - after)}"
            first_en = f"doing this leaves {_money_en(after)}, {_money_en(floor - after)} below the floor you set ({_money_en(floor)})"
        more_th = f" และอีก {len(stops) - 1} จุดในการ์ดข้างล่าง" if len(stops) > 1 else ""
        more_en = f", plus {len(stops) - 1} more in the card below" if len(stops) > 1 else ""
        th = (f"LYLA รัน DriftZero ให้แล้วค่ะ{seen_th} มีจุดที่ควรหยุดคิดก่อน: {first_th}{more_th} — "
              "ไม่ได้แปลว่าห้ามทำนะคะ แต่ถ้าแก้ตรงนี้ก่อน จะไม่เสียสิ่งที่ย้อนกลับไม่ได้")
        en = (f"I ran DriftZero for you.{seen_en} One thing to pause on: {first_en}{more_en}. "
              "That doesn't mean don't do it — fixing this first keeps you from losing something you can't get back.")
    elif v == "ask":
        th = (f"LYLA รัน DriftZero ให้แล้วค่ะ{seen_th} ยังไม่เจออะไรที่ต้องหยุด แต่ขอรู้อีก {n} อย่างจะได้ดูให้แม่นขึ้น — "
              "ตอบสั้นๆ เป็นข้อ (1 … 2 …) ก็พอค่ะ ไม่ต้องรู้ศัพท์ในการ์ดเลย")
        en = (f"I ran DriftZero for you.{seen_en} Nothing needs stopping yet, but I need {n} more thing{'' if n == 1 else 's'} to check it properly — "
              "short numbered answers (1 … 2 …) are perfect. You don't need to know the terms in the card.")
    elif after is not None and floor is not None:
        th = (f"LYLA รัน DriftZero ให้แล้วค่ะ ผ่านทุกด่าน — หลังตัดสินใจจะเหลือ {_money(after)} สูงกว่าเส้นขั้นต่ำ {_money(floor)} "
              f"อยู่ {_money(after - floor)} การตัดสินใจยังเป็นของคุณนะคะ ใบสรุปข้างล่างคัดลอกไปเก็บได้เลย")
        en = (f"I ran DriftZero for you — it passes every gate. After this you'd have {_money_en(after)}, "
              f"{_money_en(after - floor)} above your floor of {_money_en(floor)}. The decision is still yours; you can copy the summary below.")
    else:
        th = ("LYLA รัน DriftZero ให้แล้วค่ะ ผ่านทุกด่านจากข้อมูลที่ให้มา — การตัดสินใจยังเป็นของคุณนะคะ "
              "ใบสรุปข้างล่างคัดลอกไปเก็บหรือส่งต่อได้เลย แล้วกลับมาเช็คอีกครั้งหลังลงมือ")
        en = ("I ran DriftZero for you — it passes every gate on what you've told me. The decision is still yours. "
              "You can copy the summary below, and come back to check once it's under way.")
    unknown = (r.get("text") or "").count("(ยังไม่ทราบ)")
    if v == "pass" and unknown:
        th += f" — แต่ยังมี {unknown} ข้อที่ยังไม่รู้ ผลนี้จึงยังไม่แน่นอน ถ้าได้ตัวเลขเมื่อไหร่ กลับมาเช็คอีกครั้งนะคะ"
        en += f" — but {unknown} answer{' is' if unknown == 1 else 's are'} still unknown, so this isn't certain yet. Come back once you have them."
        r["unknown"] = unknown
    r["lyla"] = {"th": th, "en": en}
    return r
