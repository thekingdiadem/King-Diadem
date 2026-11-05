"""โหมดฝึก: จำลองวิกฤตทีละวัน ด้วยสมการเดียวกับระบบจริง (ไม่ใช่ตัวเลขตายตัวแบบเกมเดิม)

ที่มา: KING_DIADEM_Practice_Simulator ของเจ้าของโปรเจกต์ (วิกฤตโรคระบาด 4 ทาง ตัวเลข Entropy/Stability/Resources คงที่)
ตอนนี้ตัวเลขขยับตามสิ่งที่ผู้เล่นเลือก และสอน 4 หลักของระบบด้วยการเล่นจริง:
  · Choice(t) ≥ 1 → ยังไม่พัง — ทางที่ย้อนกลับไม่ได้ ปิดทางอื่นไปตลอดเกม
  · Waterline — เส้นขั้นต่ำที่ห้ามต่ำกว่า ต่ำกว่านี้ความเสียหายย้อนกลับไม่ได้
  · Downside ก่อน Upside — ทางที่ดูได้เร็วที่สุดมักมีราคาซ่อนอยู่
  · Dignity / Ethical Kernel — ทางที่ทิ้งคนหรือเบียดเบียน ระบบเตือนและนับว่าล้มเหลวทางจริยธรรม

สมการ (ชุดเดียวกับ system_orchestrator: structure = ((100−E)+R+S)/300):
  W = round(((100 − E) + R + S) / 3)          ระดับน้ำ 0–100
  Choice(t) = จำนวนทางที่ยังเปิดอยู่และมีทรัพยากรพอ
  พัง (collapse) = Choice(t) = 0 หรือ W < WATERLINE
ไม่สุ่ม — ลำดับทางเลือกเดิม ได้ผลเดิมทุกครั้ง (stateless: ผู้เล่นส่งประวัติมา เซิร์ฟเวอร์คำนวณใหม่ทั้งหมด)
"""
from __future__ import annotations

WATERLINE = 25
DAYS = 5


def _o(oid, th, en, voice, E, S, R, cost=0, reversible=True, dignity=True, closes=(), why_th="", why_en="", carry=None):
    # carry = ราคาที่จ่ายต่อทุกวันหลังเลือก (ดอกเบี้ย · ความไว้ใจที่ค่อยๆ หาย) — ทางที่ดูดีวันแรกต้องเห็นราคาจริงในวันถัดไป
    return {"id": oid, "th": th, "en": en, "voice": voice, "fx": {"E": E, "S": S, "R": R}, "cost": cost,
            "carry": carry or {"E": 0, "S": 0, "R": 0},
            "reversible": reversible, "dignity": dignity, "closes": list(closes), "why": {"th": why_th, "en": why_en}}


SCENARIOS = {
    "pandemic": {
        "title": {"th": "โรคระบาด · ห่วงโซ่อาหารขาด", "en": "Pandemic · food supply collapse"},
        "intro": {"th": "ชุมชน 300 ครัวเรือน ร้านค้าปิด ของในตลาดหมดเร็ว คนเริ่มกลัว — คุณเป็นคนประสานงานของชุมชน",
                  "en": "A community of 300 households. Shops closed, markets running out, people afraid — you coordinate the community."},
        "start": {"E": 70, "S": 35, "R": 45},
        "events": [
            {"th": "วันที่ 1: ข่าวลือว่าข้าวสารจะหมดภายในสัปดาห์", "en": "Day 1: rumours that rice will run out within a week", "fx": {"E": 4, "S": -2, "R": -3}},
            {"th": "วันที่ 2: มีผู้ป่วยในชุมชน 6 คน", "en": "Day 2: six people in the community fall ill", "fx": {"E": 5, "S": -3, "R": -2}},
            {"th": "วันที่ 3: รถขนส่งจากจังหวัดข้างเคียงมาได้บางส่วน", "en": "Day 3: some trucks arrive from the next province", "fx": {"E": -2, "S": 1, "R": 4}},
            {"th": "วันที่ 4: ผู้สูงอายุหลายบ้านออกมาซื้อของไม่ได้", "en": "Day 4: many elderly people cannot get out to buy food", "fx": {"E": 3, "S": -2, "R": -2}},
            {"th": "วันที่ 5: หน่วยงานรัฐแจ้งว่าความช่วยเหลือจะมาถึงในอีก 3 วัน", "en": "Day 5: the authorities say aid arrives in 3 days", "fx": {"E": -3, "S": 2, "R": 0}},
        ],
        "options": [
            _o("share", "ตั้งครัวกลาง แบ่งอาหารตามจำนวนคนในบ้าน", "Set up a shared kitchen and ration by household size",
               "LYLA", -6, 5, -4, cost=10, why_th="ลดความกลัวและไม่มีใครถูกทิ้ง แต่ใช้ทรัพยากรเร็วขึ้นเล็กน้อย",
               why_en="Less fear and no one is left out, though resources are used a little faster"),
            _o("sources", "หาแหล่งอาหารหลายทาง: เกษตรกรใกล้เคียง วัด อบต.", "Find several food sources: nearby farmers, temples, local office",
               "VEGA", -3, 3, 6, cost=5, why_th="กระจายความเสี่ยง ไม่พึ่งทางเดียว", why_en="Spreads the risk — no single point of failure"),
            _o("minimize", "ลดการเดินทาง จัดคนส่งของให้บ้านที่มีผู้ป่วยและผู้สูงอายุ", "Cut travel; deliver to homes with the sick and elderly",
               "TITAN", -4, 4, -2, why_th="ทางรอดขั้นต่ำที่ทำได้ทันที ปกป้องผู้เปราะบาง", why_en="The minimum survival path you can do now, protecting the vulnerable"),
            _o("grow", "เริ่มแปลงผักชุมชนและเก็บเมล็ดพันธุ์", "Start a community vegetable plot and save seeds",
               "COSMOS", 1, 2, 2, cost=8, why_th="ช้าในระยะสั้น แต่ทำให้ชุมชนยืดหยุ่นขึ้นในระยะยาว", why_en="Slow at first, but builds long-term resilience"),
            _o("hoard", "ให้ทีมประสานงานเก็บอาหารที่ดีที่สุดไว้ก่อน ที่เหลือค่อยแบ่ง", "Let the coordinators keep the best food first, share the rest later",
               "—", 10, -14, 6, reversible=False, dignity=False, closes=["share"], carry={"E": 3, "S": -4, "R": 0},
               why_th="ทรัพยากรของทีมเพิ่มทันที แต่ความไว้ใจในชุมชนพัง และปิดทางครัวกลางไปตลอด",
               why_en="The team gains resources fast, but community trust breaks and the shared kitchen closes for good"),
        ],
    },
    "jobloss": {
        "title": {"th": "ตกงานกะทันหัน · มีหนี้บัตร", "en": "Sudden job loss · credit card debt"},
        "intro": {"th": "ถูกเลิกจ้างวันนี้ มีเงินเก็บพอ 2 เดือน หนี้บัตร 80,000 บาท ลูก 1 คน",
                  "en": "Laid off today. Savings for 2 months, 80,000 baht card debt, one child."},
        "start": {"E": 65, "S": 40, "R": 50},
        "events": [
            {"th": "วันที่ 1: บิลบัตรเครดิตเดือนนี้มาถึง", "en": "Day 1: this month's card bill arrives", "fx": {"E": 3, "S": -1, "R": -5}},
            {"th": "วันที่ 2: มีคนชวนลงทุนออนไลน์ การันตีกำไรเดือนละ 20%", "en": "Day 2: someone offers an online investment 'guaranteed 20% a month'", "fx": {"E": 2, "S": 0, "R": 0}},
            {"th": "วันที่ 3: ค่าเทอมลูกต้องจ่ายภายในสิ้นเดือน", "en": "Day 3: the child's school fee is due by month end", "fx": {"E": 3, "S": -2, "R": -4}},
            {"th": "วันที่ 4: ได้นัดสัมภาษณ์งาน 1 ที่", "en": "Day 4: you get one job interview", "fx": {"E": -3, "S": 2, "R": 0}},
            {"th": "วันที่ 5: นอนไม่หลับมา 3 คืน", "en": "Day 5: you haven't slept well for 3 nights", "fx": {"E": 4, "S": -3, "R": 0}},
        ],
        "options": [
            _o("rights", "ยื่นขอค่าชดเชยและลงทะเบียนว่างงานกับประกันสังคม", "Claim severance and register as unemployed with social security",
               "VEGA", -5, 4, 8, why_th="เงินที่เป็นสิทธิ์อยู่แล้ว — ทางที่ย้อนกลับได้และไม่มีราคาซ่อน",
               why_en="Money you are already entitled to — reversible, no hidden cost"),
            _o("restructure", "โทรหาธนาคาร ขอปรับโครงสร้างหนี้ก่อนผิดนัด", "Call the bank to restructure the debt before missing a payment",
               "PATICCA", -4, 5, 3, why_th="ตัดต้นเหตุที่ทำให้หนี้พอกพูน", why_en="Cuts the cause that makes the debt grow"),
            _o("cut", "ตัดรายจ่ายที่ไม่จำเป็น เหลือแค่ของกิน ที่อยู่ ค่าเรียนลูก", "Cut non-essential spending — keep food, housing, the child's school",
               "TITAN", -2, 3, 5, why_th="ยืดเงินที่มีให้อยู่ได้นานขึ้น", why_en="Makes the money you have last longer"),
            _o("talk", "บอกครอบครัวหรือเพื่อนสนิท 1 คนว่ากำลังเจออะไร", "Tell one family member or close friend what is happening",
               "LYLA", -6, 3, 0, why_th="ไม่ต้องแบกคนเดียว — ความเครียดลดลงชัดเจน", why_en="You don't carry it alone — stress drops noticeably"),
            _o("invest", "เอาเงินเก็บทั้งหมดไปลงทุนที่การันตี 20% ต่อเดือน", "Put all savings into the '20% a month guaranteed' investment",
               "—", 12, -12, -30, reversible=False, dignity=True, closes=["cut", "rights"],
               why_th="การันตีผลตอบแทนสูงคือสัญญาณหลอกลงทุน — เงินเก็บหายและย้อนกลับไม่ได้",
               why_en="A guaranteed high return is the classic investment-scam sign — savings vanish and can't be recovered"),
        ],
    },
    "shop": {
        "title": {"th": "ร้านอาหาร · เงินสดใกล้เส้นขั้นต่ำ", "en": "Restaurant · cash near the floor"},
        "intro": {"th": "ร้านมีพนักงาน 6 คน ยอดขายตก 30% สามเดือนติด เงินสดเหลือพอจ่าย 6 สัปดาห์",
                  "en": "A restaurant with 6 staff. Sales down 30% for three months, cash for 6 weeks."},
        "start": {"E": 60, "S": 42, "R": 40},
        "events": [
            {"th": "วันที่ 1: ซัพพลายเออร์ขึ้นราคาวัตถุดิบ 10%", "en": "Day 1: supplier raises prices 10%", "fx": {"E": 3, "S": -1, "R": -4}},
            {"th": "วันที่ 2: ลูกค้ารีวิวในเพจว่าอาหารช้า", "en": "Day 2: a customer reviews the shop as slow", "fx": {"E": 2, "S": -2, "R": -1}},
            {"th": "วันที่ 3: ธนาคารเสนอวงเงินกู้ดอกสูง ใช้บ้านค้ำ", "en": "Day 3: the bank offers a high-interest loan secured on your house", "fx": {"E": 1, "S": 0, "R": 0}},
            {"th": "วันที่ 4: พนักงาน 1 คนขอลาออก", "en": "Day 4: one staff member resigns", "fx": {"E": 3, "S": -3, "R": 1}},
            {"th": "วันที่ 5: เทศกาลในย่าน คนเดินผ่านมากขึ้น", "en": "Day 5: a local festival brings more foot traffic", "fx": {"E": -3, "S": 1, "R": 4}},
        ],
        "options": [
            _o("numbers", "ดูตัวเลข: เมนูไหนกำไร เมนูไหนขาดทุน แล้วตัดเมนูที่ขาดทุน", "Read the numbers: which dishes earn, which lose — cut the losers",
               "VEGA", -4, 4, 5, why_th="Downside ก่อน: รู้ว่าเงินรั่วตรงไหนก่อนจะเติม", why_en="Downside first: find the leak before adding money"),
            _o("customers", "ถามลูกค้าประจำ 5 คนว่าทำไมมาน้อยลง แล้วแก้ทีละเรื่อง", "Ask 5 regulars why they come less, fix one thing at a time",
               "PATICCA", -3, 3, 3, why_th="หาต้นเหตุจริง ไม่เดา", why_en="Find the real cause instead of guessing"),
            _o("team", "คุยกับพนักงานตรงๆ เรื่องสถานการณ์ ปรับกะแทนการไล่ออก", "Be honest with staff; adjust shifts instead of firing",
               "CIVIL", -4, 5, 1, why_th="รักษาคนและความไว้ใจ — ร้านเล็กอยู่ได้ด้วยทีม", why_en="Keeps people and trust — a small shop survives on its team"),
            _o("delivery", "ทดลองเดลิเวอรี่และเมนูชุด 2 สัปดาห์", "Trial delivery and set menus for 2 weeks",
               "COSMOS", 0, 2, 4, cost=6, why_th="ทดลองเล็ก วัดผลได้ ย้อนกลับได้", why_en="A small, measurable, reversible experiment"),
            _o("allin", "กู้เต็มวงเงินโดยเอาบ้านค้ำ แล้วขยายร้านเพื่อพลิกสถานการณ์", "Max out the loan against your house and expand to turn things around",
               "—", 8, -10, 25, reversible=False, closes=["delivery", "numbers"], carry={"E": 3, "S": -3, "R": -9},
               why_th="เงินเข้าทันที แต่ถ้าไม่เวิร์ก บ้านคือเดิมพัน — ต่ำกว่าเส้นขั้นต่ำแบบย้อนกลับไม่ได้",
               why_en="Cash now, but if it fails the house is the stake — crossing the floor with no way back"),
        ],
    },
}


def _clip(v):
    return max(0, min(100, round(v)))


def waterline(st) -> int:
    return round(((100 - st["E"]) + st["R"] + st["S"]) / 3)


def public(sid: str, lang_keys=("th", "en")) -> dict:
    sc = SCENARIOS[sid]
    return {"id": sid, "title": sc["title"], "intro": sc["intro"], "days": DAYS, "waterline": WATERLINE,
            "options": [{k: o[k] for k in ("id", "th", "en", "voice", "reversible", "dignity")} for o in sc["options"]]}


def run(sid: str, choices: list) -> dict:
    """เล่นซ้ำจากจุดเริ่มด้วยลำดับทางเลือก — คืนสถานะปัจจุบัน + บันทึกทุกวัน"""
    if sid not in SCENARIOS:
        raise KeyError(sid)
    sc = SCENARIOS[sid]
    opts = {o["id"]: o for o in sc["options"]}
    st = dict(sc["start"])
    closed, used, log, harm = set(), {}, [], 0
    carry = {"E": 0, "S": 0, "R": 0}
    choices = [str(c) for c in (choices or [])][:DAYS]
    collapsed = False
    for day, cid in enumerate(choices):
        o = opts.get(cid)
        avail = _available(sc, st, closed)
        if not o or cid not in avail:
            break
        k = used.get(cid, 0)
        damp = 1 / (1 + k)                  # ใช้ทางเดิมซ้ำ ได้ผลน้อยลง — สอนให้มีหลายทาง ไม่พึ่งทางเดียว
        # ลดเฉพาะผลดี (E ลด · S/R เพิ่ม) ผลเสียไม่ลดตาม
        fx = {key: (v * damp if (v < 0 if key == "E" else v > 0) else v) for key, v in o["fx"].items()}
        st = {key: _clip(st[key] + fx[key]) for key in st}
        st["R"] = _clip(st["R"] - o["cost"] * 0.5)
        ev = sc["events"][day]
        st = {key: _clip(st[key] + ev["fx"][key] + carry[key]) for key in st}
        carry = {key: carry[key] + o["carry"][key] for key in carry}
        used[cid] = k + 1
        if not o["reversible"]:
            closed.update(o["closes"])
            closed.add(cid)
        if not o["dignity"]:
            harm += 1
        w = waterline(st)
        log.append({"day": day + 1, "choice": cid, "voice": o["voice"], "why": o["why"], "event": {"th": ev["th"], "en": ev["en"]},
                    "state": dict(st), "W": w, "reversible": o["reversible"], "dignity": o["dignity"],
                    "repeat": k > 0})
        if w < WATERLINE or not _available(sc, st, closed):
            collapsed = True
            break
    avail = _available(sc, st, closed)
    w = waterline(st)
    done = collapsed or len(log) >= DAYS
    return {"scenario": sid, "day": len(log), "state": st, "W": w, "choice_t": len(avail), "available": sorted(avail),
            "closed": sorted(closed), "collapsed": collapsed, "done": done, "log": log, "harm": harm,
            "next_event": None if done else {"th": sc["events"][len(log)]["th"], "en": sc["events"][len(log)]["en"]},
            "summary": _summary(st, w, closed, harm, collapsed, used) if done else None}


def _available(sc, st, closed) -> list:
    return [o["id"] for o in sc["options"] if o["id"] not in closed and st["R"] >= o["cost"]]


def _summary(st, w, closed, harm, collapsed, used) -> dict:
    th, en = [], []
    if collapsed:
        th.append(f"ระบบพัง: ระดับน้ำ W = {w} ต่ำกว่าเส้น {WATERLINE} หรือไม่เหลือทางเลือก — ต่ำกว่านี้ความเสียหายย้อนกลับไม่ได้")
        en.append(f"Collapse: W = {w} fell below the floor {WATERLINE}, or no choices were left — beyond this, damage can't be undone")
    else:
        th.append(f"รอด 5 วัน · ระดับน้ำ W = {w} (เส้นขั้นต่ำ {WATERLINE}) · Choice(t) ≥ 1 ตลอด")
        en.append(f"Survived 5 days · W = {w} (floor {WATERLINE}) · Choice(t) stayed ≥ 1")
    if closed:
        th.append("ทางที่ย้อนกลับไม่ได้ปิดทางอื่นไปตลอดเกม — ในชีวิตจริงก็เป็นแบบนี้ ระบบจึงให้ดู Downside ก่อนเสมอ")
        en.append("An irreversible move closed other paths for the rest of the game — real life works the same, which is why the system looks at the downside first")
    if harm:
        th.append("มีทางที่ทิ้งคนหรือเบียดเบียน — Ethical Kernel นับว่าล้มเหลวทางจริยธรรม แม้ตัวเลขบางตัวจะดีขึ้น")
        en.append("A path that left people behind was taken — the Ethical Kernel counts that as an ethical failure even if some numbers improved")
    if len(used) >= 3:
        th.append("ใช้หลายทางร่วมกัน — ผลดีกว่าการพึ่งทางเดียว (ทางเดิมซ้ำๆ ได้ผลน้อยลง)")
        en.append("You combined several paths — better than relying on one (repeating a path gives less each time)")
    th.append("ระบบแนะนำได้ แต่คนเป็นผู้ตัดสินใจเสมอ")
    en.append("The system can advise, but a human always decides")
    return {"th": th, "en": en}
