"""
ENGINE/bodhipakkhiya_engine.py — โพธิปักขิยธรรม 37 · 6-Layer Structural Guardian

ตามแบบใน KERNEL/dharma-governance-kernel.md หัวข้อ 15–16:
    guardian_check(context, pattern)
    → structural_check()   # 6 layer: สติปัฏฐาน 4 · สัมมัปปธาน 4 · อิทธิบาท 4 · อินทรีย์ 5 / พละ 5 · โพชฌงค์ 7 · มรรค 8
    → bojjhanga_loop()     # วน 7 ขั้น: สติ → ธัมมวิจยะ → วิริยะ → ปีติ → ปัสสัทธิ → สมาธิ → อุเบกขา
    → {peace, final_verdict, recommend_route, ...}

ดีเทอร์มินิสติก — ไม่ใช้ AI · input เดิม = ผลเดิม · อ่านสัญญาณจากทั้ง "สถานะ" (E/R/S) และ "ข้อความ"
เดิมช่องนี้คิดจาก E/R/S อย่างเดียว ผู้ใช้ที่ไม่ได้กรอกสถานะจึงได้ "PEACE — ดำเนินการได้" แม้พิมพ์ว่า
"ลูกกลืนถ่านกระดุม" หรือ "เอาเงินเก็บทั้งหมดไปลงคริปโต"

สงบ > ทำลาย เสมอ · ไม่ตัดสินแทนคน · คืนทางเลือก ≥ 1
"""

from __future__ import annotations
from math import isfinite as _isfinite


def _f(v, d: float) -> float:
    try:
        return float(v) if _isfinite(float(v)) else d   # nan/inf เคยหลุดผ่าน
    except (TypeError, ValueError):
        return d


def structure_score(pattern: dict) -> float:
    """สุขภาพโครงสร้าง 0–1 จาก E/R/S: ((100−E) + R + S) / 300"""
    e = max(0.0, min(100.0, _f(pattern.get("entropy"), 40)))
    r = max(0.0, min(100.0, _f(pattern.get("resource"), 50)))
    s = max(0.0, min(100.0, _f(pattern.get("stability"), 60)))
    return round(((100.0 - e) + r + s) / 300.0, 3)


# ── สัญญาณของมรรคแต่ละองค์ (ข้อความของผู้ใช้เอง — เดิมมรรคมีแค่ 3 ข้อ "โกหกลูกค้า" "โกรธจนจะลาออกเดี๋ยวนี้" ผ่านหมด)
import re as _re

FALSE_SPEECH = _re.compile(   # สัมมาวาจา — ตั้งใจพูดเท็จ ใส่ร้าย บิดข้อมูล
    r"(จะ|อยาก|ควร|ต้อง|ขอ|ช่วย)\s*(โกหก|ปั้นเรื่อง|แต่งเรื่อง|ใส่ร้าย|ใส่ความ|ปล่อยข่าว|ปิดบัง|บิดเบือน|ปลอมเอกสาร)"
    r"|รีวิวปลอม|ปลอมรีวิว|เขียนรีวิวเอง|หลอกลูกค้า|โกหกลูกค้า|โกหกแฟน|โกหกพ่อแม่|โกหกหัวหน้า|โกหกเจ้านาย"
    r"|\b(lie to|lying to|fake reviews?|make up a story|spread (a )?rumou?r|cover (it )?up)\b", _re.I)
ILL_WILL = _re.compile(       # สัมมาสังกัปปะ — เจตนามุ่งร้าย อยากเอาคืน
    r"แก้แค้น|เอาคืน|ล้างแค้น|ให้มันโดน|ให้มันพัง|ให้มันเจ็บ|ให้มันรู้สำนึก|สะใจ|เอาให้หมดอนาคต|ทำให้มันอับอาย"   # ไม่มี "ประจาน": "ขู่จะประจาน" คือคนอื่นขู่ผู้ใช้
    r"|\b(revenge|get back at|make (him|her|them) pay|ruin (him|her|them|their))\b", _re.I)
WRONG_LIVING = _re.compile(   # สัมมาอาชีวะ — หาเงินทางทุจริต
    r"(จะ|อยาก|ควร|ช่วย)\S{0,6}(โกงลูกค้า|โกงเงิน|หลอกขาย|ขายของปลอม|ขายของก็อป|เลี่ยงภาษี|หนีภาษี|ฟอกเงิน|ปั่นหุ้น|ยักยอก|ขายบัญชีม้า|รับเปิดบัญชีม้า)"
    r"|เงินใต้โต๊ะ|ค่าน้ำร้อนน้ำชา|รับสินบน|ให้สินบน|บัญชีม้า"
    r"|\b(evade tax(es)?|launder|embezzle|sell (fake|counterfeit)|pump and dump)\b", _re.I)
AGITATED = _re.compile(       # สัมมาสมาธิ — ตัดสินใจตอนอารมณ์ร้อน/เร่ง
    r"โกรธมาก|โมโหมาก|หัวร้อน|ของขึ้น|ทนไม่ไหวแล้ว|ไม่สนอะไรแล้ว|ไม่สนแล้ว|เดี๋ยวนี้เลย|ตอนนี้เลย|คืนนี้เลย|ประชด"
    r"|\b(so angry|furious|right now|tonight|i don'?t care anymore)\b", _re.I)


# ── สัญญาณจากข้อความ (ใช้ตัวตรวจกลางของระบบ — ไม่สร้างกฎซ้ำ) ─────────────────
def _signals(text: str) -> dict:
    sig = {"risk": 0, "crisis": False, "urgent": False, "basic": False, "offer": False, "scam": [],
           "harm_others": False, "gates": [], "bias": False,
           "false_speech": False, "ill_will": False, "wrong_living": False, "agitated": False, "truths": {}}
    if not text.strip():
        return sig
    sig.update(false_speech=bool(FALSE_SPEECH.search(text)), ill_will=bool(ILL_WILL.search(text)),
               wrong_living=bool(WRONG_LIVING.search(text)), agitated=bool(AGITATED.search(text)))
    try:
        from core.kernel_voice import assess, council_unsuitable
        a = assess(text)
        topics = a.get("topics") or []
        sig.update(risk=int(a.get("text_risk") or 0), crisis=bool(a.get("crisis")),
                   urgent=bool(council_unsuitable(a)), basic="basic" in topics,
                   offer=bool(a.get("offer_flags")), scam=list(a.get("scam") or []),
                   harm_others="harm_others" in topics)
        if "bribery" in topics:
            sig["wrong_living"] = True
    except Exception:
        pass
    try:
        from ENGINE.ariya_sacca import four_truths
        sig["truths"] = four_truths(text)
    except Exception:
        pass
    try:
        from core.vega_kernels import evaluate
        sig["gates"] = [g["id"] for g in evaluate(text, limit=14)]
    except Exception:
        pass
    try:
        from ENGINE.yonisomanasikara_engine import wise_attention
        sig["bias"] = bool(wise_attention(text, {}).get("bias_detected"))
    except Exception:
        pass
    return sig


def _item(name: str, ok: bool, note: str, critical: bool = False) -> dict:
    return {"name": name, "ok": bool(ok), "note": note, "critical": bool(critical and not ok)}


# ── 6 layer ──────────────────────────────────────────────────────────────
def structural_check(text: str, pattern: dict, sig: dict | None = None) -> list[dict]:
    """คืน 6 layer: [{layer, dhamma, role, items:[{name, ok, note, critical}], ok}]"""
    pattern = pattern if isinstance(pattern, dict) else {}
    sig = sig if sig is not None else _signals(text)
    e, r, s = (_f(pattern.get(k), d) for k, d in (("entropy", 40), ("resource", 50), ("stability", 60)))
    st = structure_score(pattern)
    g = set(sig["gates"])
    has_text = bool(text.strip())

    layers = [
        # 1 สติปัฏฐาน 4 — DRIFT_DETECTION
        ("สติปัฏฐาน 4", "DRIFT_DETECTION", [
            _item("กาย", r >= 30, "ทรัพยากรพอ (resource ≥ 30)" if r >= 30 else "ทรัพยากรต่ำ — พื้นรอดสั่น"),
            _item("เวทนา", e <= 65 and sig["risk"] < 60,
                  "อารมณ์/ความเสี่ยงในข้อความอยู่ในระดับรับได้" if e <= 65 and sig["risk"] < 60
                  else "มีความทุกข์หรือความเสี่ยงสูงในข้อความ — รับรู้ก่อนวิเคราะห์", critical=sig["crisis"]),
            _item("จิต", has_text, "รู้ว่าผู้ใช้ถามเรื่องอะไร" if has_text else "ยังไม่มีข้อความ"),
            _item("ธรรม", not (sig["offer"] or sig["scam"] or sig["harm_others"]),
                  "ไม่มีสัญญาณละเมิดหลัก" if not (sig["offer"] or sig["scam"] or sig["harm_others"])
                  else "มีสัญญาณหลอก/เบียดเบียน — ตรวจก่อนทำตาม"),
        ]),
        # 2 สัมมัปปธาน 4 — GOVERNANCE_GATE: prevent / kill / reinforce / persist
        ("สัมมัปปธาน 4", "GOVERNANCE_GATE", [
            _item("สังวรปธาน", not (e > 65 and s < 40) and "K2" not in g,
                  "ยังไม่เห็นการไหลไปสู่ความพัง" if not (e > 65 and s < 40) and "K2" not in g
                  else "กำลังไหล (drift) หรือเสี่ยงหมดหน้าตัก — ยับยั้งก่อนเกิด"),
            _item("ปหานปธาน", not ("K13" in g or "lost" in sig["scam"] or sig["urgent"]),
                  "ไม่มีความเสียหายที่กำลังเคลื่อน" if not ("K13" in g or "lost" in sig["scam"] or sig["urgent"])
                  else "ความเสียหายกำลังเกิด — หยุดก่อน (Stop-the-Line)", critical=sig["urgent"]),
            _item("ภาวนาปธาน", True, "คำตอบต้องเพิ่มทางเลือกที่ทำได้จริง ≥ 1"),
            _item("อนุรักขนาปธาน", "K5" not in g, "ทางถอยยังอยู่" if "K5" not in g
                  else "การตัดสินใจนี้ย้อนกลับยาก — รักษาทางถอยไว้ก่อน"),
        ]),
        # 3 อิทธิบาท 4 — EXECUTION_KERNEL: purpose / retry / precision / audit
        ("อิทธิบาท 4", "EXECUTION_KERNEL", [
            _item("ฉันทะ", has_text, "มีเป้าหมายของคำถาม" if has_text else "ยังไม่รู้เป้าหมาย"),
            _item("วิริยะ", "K11" not in g, "ทำต่อได้ทีละก้าว" if "K11" not in g
                  else "อยากทำทุกอย่างพร้อมกัน — เลือกก้าวเดียวก่อน"),
            _item("จิตตะ", "K3" not in g, "เรื่องยังจับต้นชนปลายได้" if "K3" not in g
                  else "เรื่องซับซ้อนเกินไป — ตัดให้เหลือ 2 ประโยค"),
            _item("วิมังสา", "K12" not in g, "เปิดรับหลักฐาน" if "K12" not in g
                  else "มั่นใจเกินหลักฐาน — ถามว่าอะไรจะทำให้เปลี่ยนใจ"),
        ]),
        # 4a อินทรีย์ 5 — CAPABILITY_LAYER (คู่ที่ต้องสมดุล: สัทธา↔ปัญญา · วิริยะ↔สมาธิ · สติคุมทั้งหมด)
        ("อินทรีย์ 5", "CAPABILITY_LAYER", [
            _item("สัทธา–ปัญญา", not (sig["offer"] or "K2" in g or "K12" in g),
                  "ความเชื่อกับปัญญาสมดุล" if not (sig["offer"] or "K2" in g or "K12" in g)
                  else "เชื่อมากกว่าที่หลักฐานรองรับ (สัทธาเกินปัญญา)"),
            _item("วิริยะ–สมาธิ", not ("K7" in g or "K11" in g),
                  "ความเพียรกับความตั้งมั่นสมดุล" if not ("K7" in g or "K11" in g)
                  else "รีบเกินความตั้งมั่น (วิริยะเกินสมาธิ) — รอ 24 ชม. ได้ไหม"),
            _item("สติ", not sig["bias"], "เห็นภาพตรง" if not sig["bias"] else "มีอคติบิดภาพ — ลองดูเหตุผลอีกฝั่ง"),
        ]),
        # 4b พละ 5 — FORCE_LAYER → VEGA safety gate (14 Gates)
        ("พละ 5", "FORCE_LAYER", [
            _item("VEGA gates", len(g) <= 1, "ประตูของ VEGA ติดไม่เกิน 1" if len(g) <= 1
                  else f"ประตูของ VEGA ติด {len(g)} ข้อ ({', '.join(sorted(g))}) — แรงที่จะพาไปพังมากกว่าแรงต้าน"),
            _item("โครงสร้าง", st >= 0.35, f"structure {st:.2f} ≥ 0.35" if st >= 0.35
                  else f"structure {st:.2f} < 0.35 — ประคองก่อนตัดสินใจใหญ่", critical=st < 0.35),
        ]),
        # 6 มรรค 8 — FULL_STACK · ครบ 8 องค์ จัดเป็น 3 หมวด: ปัญญา (Intelligence) · ศีล (Security) · สมาธิ (Stability)
        ("มรรคมีองค์ 8", "FULL_STACK", [
            # ปัญญา
            # สัมมาทิฏฐิยืนบนอริยสัจ 4 ของเรื่องนี้ (ENGINE/ariya_sacca) — เห็นทุกข์และเหตุก่อน มรรคข้ออื่นจึงตรง
            _item("สัมมาทิฏฐิ", not (sig["bias"] or "K1" in g or "K12" in g),
                  "ยังไม่เห็นตามจริง — ความจริงก่อน" if (sig["bias"] or "K1" in g or "K12" in g)
                  else "เห็นทุกข์และเหตุชัด" if sig["truths"].get("clear")
                  else "เห็นทุกข์แล้ว แต่เหตุยังไม่ชัด — ถามหาต้นเหตุก่อน" if sig["truths"].get("seen")
                  else "เห็นตามจริง"),
            _item("สัมมาสังกัปปะ", not (sig["ill_will"] or "K14" in g),
                  "เจตนาไม่มุ่งร้าย" if not (sig["ill_will"] or "K14" in g)
                  else "เจตนามีความอยากเอาคืน/ต้องชนะ — ถามว่าอยากให้เรื่องจบแบบไหน"),
            # ศีล
            _item("สัมมาวาจา", not sig["false_speech"], "คำพูดตรงความจริง" if not sig["false_speech"]
                  else "มีการโกหก/ใส่ร้าย/บิดข้อมูล — ทางที่พูดความจริงได้มีไหม"),
            _item("สัมมากัมมันตะ", not sig["harm_others"], "การกระทำไม่เบียดเบียนผู้อื่น" if not sig["harm_others"]
                  else "การกระทำนี้เบียดเบียนผู้อื่น — หยุดก่อนลงมือ"),
            _item("สัมมาอาชีวะ", not (sig["wrong_living"] or "K10" in g),
                  "ทางหาเลี้ยงชีพสุจริต" if not (sig["wrong_living"] or "K10" in g)
                  else "รายได้/ผลประโยชน์ทางนี้ไม่สุจริต — เสี่ยงทั้งกฎหมายและความไว้ใจ"),
            # สมาธิ
            _item("สัมมาวายามะ", not ("K11" in g or "K2" in g),
                  "ความเพียรไปทางที่ไม่ทำให้พัง" if not ("K11" in g or "K2" in g)
                  else "แรงทุ่มไปทางเสี่ยงหมดตัว/ทำทุกอย่างพร้อมกัน — เพียรให้ถูกทาง"),
            _item("สัมมาสติ", not (sig["scam"] or sig["offer"]),
                  "รู้ทันสถานการณ์" if not (sig["scam"] or sig["offer"])
                  else "มีรูปแบบของการหลอก — ตั้งสติ ตรวจกับช่องทางทางการก่อนทำตาม"),
            # เหตุต่างกัน คำบอกต้องต่างกัน — เดิมคนที่นอนไม่หลับหลายวันได้คำว่าอารมณ์ร้อน ทั้งที่แค่เหนื่อย
            _item("สัมมาสมาธิ", e <= 65 and "K8" not in g and not sig["agitated"],
                  "ใจตั้งมั่นพอ" if e <= 65 and "K8" not in g and not sig["agitated"]
                  else "อารมณ์ร้อน/เร่งรีบกำลังบิดภาพ — สงบก่อนตัดสิน" if sig["agitated"]
                  else "ใจยังเหนื่อยและไม่นิ่ง — พักให้ใจสงบก่อนตัดสินเรื่องใหญ่"),
        ]),
    ]
    out = []
    for i, (dhamma, role, items) in enumerate(layers):
        out.append({"layer": ("1", "2", "3", "4a", "4b", "6")[i], "dhamma": dhamma, "role": role,
                    "items": items, "ok": all(x["ok"] for x in items)})
    return out


BOJJHANGA = ("สติ", "ธัมมวิจยะ", "วิริยะ", "ปีติ", "ปัสสัทธิ", "สมาธิ", "อุเบกขา")


def bojjhanga_loop(text: str, pattern: dict, layers: list[dict], sig: dict) -> dict:
    """Layer 5 — วน 7 ขั้น หยุดที่ขั้นแรกที่ยังไม่ผ่าน (ระบบไม่ crash — แค่บอกว่าควรอยู่ขั้นไหนก่อน)"""
    e = _f((pattern or {}).get("entropy"), 40)
    by = {x["name"]: x for L in layers for x in L["items"]}
    steps = (
        ("สติ", bool(text.strip())),                                         # รู้ว่าผู้ใช้พูดอะไร
        ("ธัมมวิจยะ", not sig["crisis"]),                                     # แยกได้ว่าเป็นเรื่องให้คิด ไม่ใช่วิกฤต
        ("วิริยะ", by["วิริยะ"]["ok"]),
        ("ปีติ", not sig["urgent"]),                                          # ยังมีพื้นให้ใจเบาได้
        ("ปัสสัทธิ", e <= 65 and sig["risk"] < 60 and by["วิริยะ–สมาธิ"]["ok"]),  # สงบพอจะตัดสิน
        ("สมาธิ", by["สัมมาสมาธิ"]["ok"]),
        ("อุเบกขา", by["สติ"]["ok"] and by["สัทธา–ปัญญา"]["ok"]),           # วางใจเป็นกลาง ไม่เอียงด้วยอคติ/ความหวัง
    )
    reached = 0
    for name, ok in steps:
        if not ok:
            break
        reached += 1
    return {"reached": reached, "complete": reached == len(steps),
            "stopped_at": None if reached == len(steps) else steps[reached][0]}


def guardian_check(context, pattern=None) -> dict:
    """จุดเข้าเดียว — เรียกจาก core/king_diadem_core.quick_assess() ก่อน LLM ทุกครั้ง"""
    text = str(context or "")[:4000]
    pattern = pattern if isinstance(pattern, dict) else {}
    sig = _signals(text)
    layers = structural_check(text, pattern, sig)
    loop = bojjhanga_loop(text, pattern, layers, sig)
    items = [x for L in layers for x in L["items"]]
    failed = [x for x in items if not x["ok"]]
    critical = [x for x in failed if x["critical"]]
    health = round(sum(x["ok"] for x in items) / len(items), 3)
    st = structure_score(pattern)

    magga_ok = layers[-1]["ok"]          # มรรค 8 = Final Governance Lock: ข้อใดไม่ผ่าน ไม่ให้ PEACE (เดิม "จะโกหกลูกค้า" ได้ PEACE)
    peace = not critical and loop["complete"] and health >= 0.8 and magga_ok
    # สงบ > ทำลาย: ยกไป survival เฉพาะเมื่อพื้นรอดพังจริง (โครงสร้างต่ำ หรือขาดปัจจัยพื้นฐาน)
    recommend_route = "survival" if (st < 0.35 or sig["basic"]) else None
    if peace:
        verdict = "PEACE — โครงสร้างพอ ดำเนินการได้"
    elif recommend_route:
        verdict = "STABILIZE — พื้นรอดยังไม่มั่นคง ประคองก่อนตัดสินใจใหญ่"
    elif critical:
        verdict = "STOP — เรื่องนี้ต้องได้ความช่วยเหลือก่อน ไม่ใช่การชั่งทางเลือก"
    else:
        verdict = "PAUSE — ทบทวนก่อนตัดสินใจ" + (f" (โพชฌงค์หยุดที่{loop['stopped_at']})" if loop["stopped_at"] else "")
    return {
        "peace": peace,
        "final_verdict": verdict,
        "recommend_route": recommend_route,
        "health": health,
        "structure": st,
        "layers": layers,
        "bojjhanga": loop,
        "failed": [{"name": x["name"], "note": x["note"]} for x in failed],
        "magga": {x["name"]: x["ok"] for x in layers[-1]["items"]},
        "ariya": {k: sig["truths"].get(k) for k in ("dukkha", "samudaya", "nirodha", "magga", "clear")} if sig["truths"] else None,
    }


def llm_hint(result: dict) -> str:
    """บริบทแนบให้ LLM — เฉพาะเมื่อมีธรรมข้อที่ยังไม่ผ่าน (ไม่ให้ยกศัพท์ไปพูดกับผู้ใช้)"""
    f = (result or {}).get("failed") or []
    ar = ""
    try:
        from ENGINE.ariya_sacca import llm_hint as _ah
        a = (result or {}).get("ariya")
        ar = _ah(a) if a and a.get("dukkha") != "ยังไม่ชัด" else ""
    except Exception:
        pass
    if not f:
        return ar
    return ((ar + " ") if ar else "") + ("[โพธิปักขิยธรรม: " + (result.get("final_verdict") or "") + " · ยังไม่ผ่าน: "
            + "; ".join(f"{x['name']} — {x['note']}" for x in f[:4]) + "]")
