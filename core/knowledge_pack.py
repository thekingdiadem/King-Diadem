"""ชุดความรู้ที่ระบบเคยไม่รู้ — แต่ละเรื่องเคยได้คำตอบกลาง ("ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน") ความเสี่ยง 0/100

ไฟล์เดียว เพิ่มเรื่องใหม่ได้โดยไม่ต้องแก้ kernel: core/kernel_voice.py อ่าน PACK แล้วสร้างหัวข้อให้เอง
(ไทยใน TOPICS · อังกฤษใน EN_TOPIC · ด่วนเข้า _URGENT_TOPICS · คะแนนเข้า _TOPIC_RISK)

แต่ละเรื่อง: ชื่อหัวข้อ · regex (ไทย|อังกฤษ) · ความเสี่ยง · ด่วนไหม · คำตอบไทย (เปิด, ขั้น ≤3, คำถาม) · คำตอบอังกฤษ
เขียนเองจากแนวทางสาธารณะ (WHO · กรมควบคุมโรค · ศูนย์พิษวิทยารามาธิบดี · พ.ร.บ.คุ้มครองแรงงาน · สคบ.) — ไม่แทนแพทย์/ทนาย
เบอร์ที่ใช้: 1669 ฉุกเฉิน · 1367 ศูนย์พิษวิทยา · 1300 พม. · 1546 แรงงาน · 1166 สคบ. · 1167 สภาทนายความ · 1600 เลิกบุหรี่ · 1165 ยาเสพติด · 1323 สุขภาพจิต · 1663 ท้องไม่พร้อม
"""
from __future__ import annotations

import re

_EMS_EN = "call emergency services now (1669 in Thailand, 911 in the US, 112 in Europe, 999 in the UK)"
_EMS_EN_CAP = "C" + _EMS_EN[1:]

PACK = [
    # ── ด่วน: อันตรายถึงชีวิต ─────────────────────────────────────────────────────────────────────────
    ("kp_heatstroke",
     r"ลมแดด|ฮีท\s?สโตรก|(?:ตัวร้อน|ร้อน)(?:จัด|มาก|จี๋)?[^\n]{0,30}?(?:ไม่มีเหงื่อ|เหงื่อไม่ออก|สับสน|เพ้อ|พูดไม่รู้เรื่อง|ซึม|ชัก|หมดสติ)"
     r"|\bheat ?stroke\b|\b(?:overheat\w*|very hot|in the heat)\b[^\n]{0,40}?\b(?:confused|not sweating|stopped sweating|collapsed|passed out)\b",
     85, True,
     ("ตัวร้อนจัดร่วมกับไม่มีเหงื่อหรือสับสน คือลมแดด (ฮีทสโตรก) — อันตรายถึงชีวิต ต้องลดความร้อนเดี๋ยวนี้",
      ["โทร 1669 ตอนนี้ แล้วพาเข้าที่ร่มหรือห้องแอร์ ถอดเสื้อผ้าที่หนาออก",
       "ทำให้ตัวเย็นเร็วที่สุด: ราดหรือเช็ดน้ำเย็นทั้งตัวแล้วเปิดพัดลมเป่า ประคบน้ำแข็งที่คอ รักแร้ ขาหนีบ — ทำต่อจนรถพยาบาลมา",
       "ถ้าสับสนหรือไม่รู้สึกตัว ห้ามป้อนน้ำ (สำลักได้) ยาลดไข้ช่วยไม่ได้ในลมแดด — ถ้ายังรู้สึกตัวดีให้จิบน้ำเย็นทีละน้อย"],
      "ตอนนี้เขายังรู้สึกตัว พูดตอบได้อยู่ไหม?"),
     ("Very hot skin with no sweating or confusion is heat stroke — it can kill, cool them down now.",
      [f"{_EMS_EN_CAP}, then move them into shade or air conditioning and remove heavy clothing.",
       "Cool them as fast as you can: soak or sponge with cold water and fan them, ice packs on the neck, armpits and groin — keep going until help arrives.",
       "If they are confused or unconscious, give nothing to drink; fever medicine doesn't help heat stroke."],
      "Are they awake and able to answer you right now?")),

    ("kp_methanol",
     r"^(?=[\s\S]*(?:(?:เหล้า|สุรา)(?:ขาว)?(?:เถื่อน|ต้ม|ขาวปลอม|ปลอม|ไม่มียี่ห้อ|หมักเอง)|เมทานอล|ยาดองเถื่อน"
     r"|\b(?:methanol|moonshine|bootleg (?:alcohol|liquor|spirits?|vodka)|homemade (?:alcohol|liquor)|counterfeit (?:alcohol|vodka|liquor))\b))"
     r"(?=[\s\S]*(?:ตา(?:พร่า|มัว|บอด)|มองไม่(?:เห็น|ชัด)|ปวดท้อง|หอบ|อาเจียน|ซึม|ชัก|เวียนหัว|หมดสติ|หายใจ"
     r"|\b(?:blurr\w*|vision|can'?t see|vomit\w*|breath\w*|drowsy|seizure|passed out|belly pain|stomach pain)\b))",
     85, True,
     ("ตาพร่า ปวดท้อง หอบ หรือซึม หลังดื่มเหล้าเถื่อน อาจเป็นพิษเมทานอล — รักษาได้ถ้าถึงมือแพทย์เร็ว อย่ารอให้หายเอง",
      ["โทร 1669 หรือไปห้องฉุกเฉินเดี๋ยวนี้ แม้อาการยังน้อย — อาการมักเริ่ม 12–24 ชั่วโมงหลังดื่ม และตาบอดถาวรได้",
       "เอาขวดหรือบอกยี่ห้อ/แหล่งที่ซื้อไปด้วย · บอกทุกคนที่ดื่มขวดเดียวกันให้ไปโรงพยาบาลพร้อมกัน",
       "แพทย์ปรึกษาศูนย์พิษวิทยารามาธิบดี 1367 ได้ 24 ชม. — ห้ามทำให้อาเจียน และห้ามดื่มเหล้าเพิ่มเพื่อ 'แก้'"],
      "ดื่มไปนานกี่ชั่วโมงแล้ว และมีคนอื่นดื่มขวดเดียวกันไหม?"),
     ("Blurred vision, belly pain, fast breathing or drowsiness after bootleg alcohol can be methanol poisoning — it's treatable if you get there fast.",
      [f"{_EMS_EN_CAP} or go to the ER, even if symptoms are mild — they often start 12–24 hours after drinking and blindness can be permanent.",
       "Take the bottle or the brand with you, and tell everyone who drank from the same bottle to go too.",
       "Don't make yourself vomit and don't drink more alcohol to 'treat' it."],
      "How many hours ago did you drink, and did anyone else drink from the same bottle?")),

    ("kp_fever_rash",
     r"(?:ไข้)[^\n]{0,40}?(?:ผื่น|จุดเลือด|จ้ำเลือด|จุดแดง)[^\n]{0,20}?(?:กดไม่จาง|กดแล้วไม่(?:จาง|หาย)|ไม่จาง|ลาม(?:เร็ว)?)|(?:ผื่น|จุดเลือด|จ้ำ)[^\n]{0,20}?(?:กดไม่จาง|กดแล้วไม่(?:จาง|หาย))[^\n]{0,40}?ไข้"
     r"|\b(?:rash|spots)\b[^\n]{0,30}?\b(?:doesn'?t fade|does not fade|won'?t fade|non-?blanching|under (?:a|the) glass)\b|\bnon-?blanching rash\b",
     85, True,
     ("ไข้ร่วมกับผื่นหรือจุดเลือดที่กดแล้วไม่จาง อาจเป็นการติดเชื้อในกระแสเลือดหรือเยื่อหุ้มสมองอักเสบ — นับเป็นชั่วโมง ไปห้องฉุกเฉินเดี๋ยวนี้",
      ["โทร 1669 หรือไปห้องฉุกเฉินทันที อย่ารอดูว่าไข้ลงไหม — โดยเฉพาะถ้าซึม คอแข็ง มือเท้าเย็น หรือปวดขามาก",
       "วิธีเช็ค: เอาแก้วใสกดลงบนผื่น ถ้ายังเห็นจุดชัดผ่านแก้ว แปลว่ากดไม่จาง (ผิวคล้ำให้ดูที่ฝ่ามือ ฝ่าเท้า หรือในเปลือกตา)",
       "ไข้ร่วมกับจุดเลือดในช่วงไข้เลือดออกระบาดก็ต้องให้แพทย์ดูวันนี้ — ห้ามกินแอสไพรินหรือไอบูโพรเฟน"],
      "ตอนนี้ยังตื่นดี ตอบสนองปกติไหม และมีอาการคอแข็งหรือซึมไหม?"),
     ("A fever with a rash or spots that don't fade when pressed can be sepsis or meningitis — hours matter, go to the ER now.",
      [f"{_EMS_EN_CAP} or go straight to the ER — don't wait to see if the fever comes down, especially with drowsiness, a stiff neck, cold hands and feet or bad leg pain.",
       "The glass test: press a clear glass on the rash; if you can still see the spots through it, they don't fade (on darker skin, check palms, soles and inside the eyelids).",
       "Avoid aspirin and ibuprofen until a doctor has seen them."],
      "Are they awake and responding normally, and is there a stiff neck or drowsiness?")),

    ("kp_gi_bleed",
     r"(?:อุจจาระ|ถ่าย|อึ)\S{0,6}(?:สี)?ดำ|ถ่ายเป็นเลือด|อาเจียน\S{0,4}(?:เป็นเลือด|สีกาแฟ|สีน้ำตาลเข้ม)|อ้วกเป็นเลือด"
     r"|\b(?:black|tarry) (?:stool|stools|poop|poo)\b|\b(?:vomit\w*|throwing up) (?:blood|coffee[- ]grounds?)\b|\bblood in (?:my|his|her) (?:stool|poop|vomit)\b",
     80, True,
     ("ถ่ายดำเหนียว ถ่ายเป็นเลือด หรืออาเจียนเป็นเลือด/สีกาแฟ อาจเป็นเลือดออกในทางเดินอาหาร — ต้องให้แพทย์ดูวันนี้",
      ["ถ้าเวียนหัว ใจสั่น หน้ามืด เหงื่อแตก หรือเลือดออกมาก โทร 1669 ตอนนี้ — นอนราบ อย่าลุกเดินเอง",
       "งดกินและดื่มไว้ก่อนจนแพทย์ตรวจ · บอกแพทย์ถ้ากินยาแก้ปวดกลุ่ม NSAID แอสไพริน ยาละลายลิ่มเลือด หรือดื่มเหล้าประจำ",
       "ยาเม็ดธาตุเหล็กทำให้อุจจาระดำได้ แต่ถ้ามีอาการเวียนหัวหรืออ่อนเพลียร่วมด้วย ให้ไปโรงพยาบาลก่อน แล้วค่อยถามทีหลัง"],
      "ตอนนี้เวียนหัวหรือหน้ามืดไหม และมีใครอยู่ด้วย?"),
     ("Black tarry stools, blood in your stool, or vomiting blood or 'coffee grounds' can mean bleeding in the gut — it needs a doctor today.",
      [f"If you feel dizzy, faint, sweaty or your heart is racing, {_EMS_EN} — lie down and don't walk on your own.",
       "Don't eat or drink until you're seen, and tell the doctor about painkillers like ibuprofen or aspirin, blood thinners, or regular drinking.",
       "Iron tablets can turn stool black, but with dizziness or weakness go in first and ask later."],
      "Are you dizzy or faint right now, and is anyone with you?")),

    ("kp_bp_crisis",
     r"ความดัน\S{0,6}\s?(?:1[89]\d|2\d\d)\s?/\s?(?:1[0-9]\d|9\d)|ความดัน(?:สูง)?(?:มาก|พุ่ง)[^\n]{0,30}?(?:ปวดหัว|ตามัว|ตาพร่า|เจ็บหน้าอก|แขน\S{0,4}อ่อนแรง|พูดไม่ชัด|หายใจลำบาก)"
     r"|\b(?:blood pressure|bp)\b[^\n]{0,12}?\b(?:1[89]\d|2\d\d) ?(?:/|over) ?(?:1[0-9]\d|9\d)\b",
     75, True,
     ("ความดันตั้งแต่ 180/120 ขึ้นไป ถ้ามีอาการร่วม ถือเป็นภาวะฉุกเฉิน",
      ["นั่งพัก 5 นาทีแล้ววัดใหม่ · ถ้ายังสูงและมีปวดหัวรุนแรง ตามัว เจ็บหน้าอก หายใจลำบาก แขนขาอ่อนแรง หรือพูดไม่ชัด โทร 1669 ตอนนี้",
       "ถ้าสูงแต่ไม่มีอาการใดเลย ให้โทรปรึกษาโรงพยาบาลหรือไปพบแพทย์วันนี้ — อย่าเพิ่มยาความดันเองหลายเม็ด เพราะลดเร็วเกินไปก็อันตราย",
       "จดตัวเลขกับเวลาที่วัด และยาที่กินวันนี้ ไว้บอกแพทย์"],
      "วัดซ้ำแล้วได้เท่าไร และมีอาการปวดหัว เจ็บหน้าอก หรือแขนขาอ่อนแรงไหม?"),
     ("A blood pressure of 180/120 or higher with symptoms is an emergency.",
      [f"Sit for 5 minutes and measure again. If it's still that high with a severe headache, blurred vision, chest pain, breathlessness, weakness or slurred speech, {_EMS_EN}.",
       "If it's high but you feel fine, call your doctor or go in today — don't take extra doses of your pills, because dropping too fast is dangerous too.",
       "Write down the readings, the times, and what medicines you took today."],
      "What was the second reading, and do you have a headache, chest pain or weakness?")),

    ("kp_child_breath",
     r"(?:ลูก|เด็ก|หลาน)[^\n]{0,20}?(?:หายใจ\S{0,6}(?:วี้ด|ครืด|มีเสียง|หอบ|เร็ว|ลำบาก|ไม่ทัน)|หอบ(?:เหนื่อย)?|อกบุ๋ม|ปากเขียว)"
     r"|\b(?:my )?(?:child|kid|son|daughter|toddler|baby|boy|girl)\b[^\n]{0,30}?\b(?:wheez\w*|struggling to breathe|can'?t breathe|breathing (?:fast|hard)|blue lips)\b",
     80, True,
     ("เด็กหายใจมีเสียงวี้ดหรือหอบ ต้องดูสัญญาณอันตรายตอนนี้",
      ["โทร 1669 ทันทีถ้าปากเขียว พูดหรือร้องไม่เป็นคำ ซี่โครงบุ๋มตอนหายใจ ซึม หรือกินยาพ่นแล้วไม่ดีขึ้น",
       "ให้นั่งตัวตรงหรือเอนไปข้างหน้า ปลอบให้ใจเย็น · ถ้ามียาพ่นที่หมอสั่ง ใช้ตามขนาดที่หมอบอก",
       "ถ้าไม่มีสัญญาณข้างบน ให้พบแพทย์วันนี้ — หายใจหอบในเด็กเล็กแย่ลงเร็ว โดยเฉพาะตอนกลางคืน"],
      "ตอนนี้ปากเขียวหรือพูด/ร้องไม่ออกไหม?"),
     ("Wheezing or struggling to breathe in a child — check the danger signs now.",
      [f"{_EMS_EN_CAP} if their lips turn blue, they can't speak or cry, the skin pulls in between the ribs, they're drowsy, or the inhaler isn't helping.",
       "Sit them upright or leaning forward and keep them calm; if they have a prescribed inhaler, use it as the doctor told you.",
       "Without those signs, they still need a doctor today — breathing trouble in young children can get worse quickly, especially at night."],
      "Are their lips blue, or are they unable to talk or cry right now?")),

    ("kp_sudden_vision",
     r"(?:มองไม่เห็น|ตามัว|มองไม่ชัด|ตาบอด|เห็นเป็นม่าน|มองเห็นครึ่งเดียว)[^\n]{0,16}?(?:กะทันหัน|ทันที|ปุบปับ|ข้างเดียว|เฉียบพลัน)|(?:กะทันหัน|ทันที|ปุบปับ)[^\n]{0,10}?(?:มองไม่เห็น|ตามัว|มองไม่ชัด)"
     r"|ตา\S{0,4}(?:แดง)?\S{0,6}(?:ปวด|เจ็บ)\S{0,4}(?:มาก|รุนแรง)[^\n]{0,20}?(?:มองไม่ชัด|ตามัว|คลื่นไส้|เห็นแสงรุ้ง)"
     r"|\bsudden(?:ly)? (?:lost|losing|loss of|blurr\w*|can'?t see|blind\w*)\b|\b(?:curtain|shadow) (?:over|across) (?:my|his|her) (?:vision|eye)\b",
     80, True,
     ("มองไม่เห็นหรือตามัวกะทันหัน ต้องให้แพทย์ดูวันนี้ — บางสาเหตุรักษาได้เฉพาะในไม่กี่ชั่วโมง",
      ["ถ้ามีหน้าเบี้ยว แขนขาอ่อนแรง หรือพูดไม่ชัดร่วมด้วย อาจเป็นสโตรก โทร 1669 ตอนนี้",
       "ตาแดงปวดมาก ตามัว คลื่นไส้ เห็นแสงรุ้งรอบไฟ (ต้อหินเฉียบพลัน) หรือเห็นเป็นม่านบัง (จอประสาทตาหลุด) ไปห้องฉุกเฉินหรือโรงพยาบาลที่มีจักษุแพทย์เดี๋ยวนี้",
       "ถ้าสารเคมีเข้าตา ล้างด้วยน้ำสะอาดไหลผ่านต่อเนื่อง 15–20 นาทีก่อน แล้วค่อยไป — อย่าขยี้ตา"],
      "เป็นข้างเดียวหรือสองข้าง และมีอาการแขนขาอ่อนแรงหรือพูดไม่ชัดไหม?"),
     ("Sudden loss of vision or blurring needs a doctor today — some causes can only be treated within hours.",
      [f"With a drooping face, weakness or slurred speech it may be a stroke — {_EMS_EN}.",
       "A painful red eye with blurring, nausea or halos around lights, or a curtain or shadow over your vision, needs the ER or an eye hospital now.",
       "If chemicals got in the eye, rinse with running water for 15–20 minutes first, then go — don't rub it."],
      "Is it one eye or both, and is there any weakness or trouble speaking?")),

    ("kp_object_nose_ear",
     r"(?:ถั่ว|เม็ด\S{0,4}|ลูกปัด|ของเล่น|ยางลบ|กระดุม|ถ่าน|หิน|ข้าวโพด)\S{0,10}(?:เข้า|ยัด|อุด|ติด)\S{0,6}(?:รู)?(?:จมูก|หู)"
     r"|\b(?:bead|pea|bean|peanut|battery|toy|button|crayon|rock|small object)\b[^\n]{0,20}?\b(?:up|in|into|stuck in) (?:his|her|my|their|the) (?:nose|ear|nostril)\b",
     60, False,
     ("ของเข้าจมูกหรือหู ส่วนใหญ่เอาออกได้ปลอดภัยที่โรงพยาบาล — อย่าแคะเองจนมันลึกขึ้น",
      ["ถ้าเป็นถ่านกระดุม (ถ่านนาฬิกา) หรือแม่เหล็ก ไปห้องฉุกเฉินเดี๋ยวนี้ — กัดเนื้อเยื่อได้ภายในไม่กี่ชั่วโมง",
       "ห้ามใช้แหนบ คีม หรือคอตตอนบัดแคะ · ถ้าเป็นจมูก ให้ปิดรูจมูกอีกข้างแล้วสั่งน้ำมูกแรงๆ ได้ 1–2 ครั้ง (ห้ามสูดเข้า)",
       "ถ้าหายใจลำบาก มีเลือดออก ปวดมาก หรือเอาไม่ออก พบแพทย์วันนี้ — แมลงเข้าหู หยอดน้ำมันพืชให้แมลงหยุดดิ้นก่อนได้ ถ้าแก้วหูไม่ทะลุ"],
      "เข้าไปเมื่อไร และเป็นถ่านหรือแม่เหล็กหรือเปล่า?"),
     ("Something stuck in the nose or ear can usually be removed safely at a clinic — don't dig, it pushes it deeper.",
      ["If it's a button battery or a magnet, go to the ER now — it can burn tissue within hours.",
       "No tweezers or cotton buds; for the nose, close the other nostril and blow hard once or twice (don't sniff in).",
       "See a doctor today if there's trouble breathing, bleeding, pain, or it won't come out."],
      "When did it go in, and could it be a battery or magnet?")),

    ("kp_food_poison",
     r"\bfood poisoning\b|\b(?:vomit\w*|throwing up|diarrh\w*)\b[^\n]{0,30}?\b(?:all night|since (?:last night|this morning|yesterday)|after (?:eating|dinner|lunch))\b",
     45, False,
     ("อาหารเป็นพิษส่วนใหญ่หายเองใน 1–2 วัน สิ่งสำคัญคือไม่ให้ขาดน้ำ และรู้ว่าตอนไหนต้องไปโรงพยาบาล",
      ["จิบผงเกลือแร่ (ORS) ทีละน้อยแต่บ่อย · อย่าใช้เครื่องดื่มเกลือแร่สำหรับนักกีฬาแทน",
       "ไปโรงพยาบาลถ้ามีเลือดปน ดื่มน้ำแล้วอาเจียนออกหมดเกิน 12 ชั่วโมง ไม่ปัสสาวะ 8 ชั่วโมง ไข้สูง หรือเวียนหัวจนยืนไม่ไหว",
       "ถ้าเพิ่งกินเห็ดป่า ปลาปักเป้า หรือหอยแล้วชา อาเจียน — ไปห้องฉุกเฉินเลย และโทรศูนย์พิษวิทยา 1367"],
      "เริ่มเป็นกี่ชั่วโมงแล้ว และยังดื่มน้ำแล้วเก็บไว้ได้ไหม?"),
     ("Most food poisoning settles in a day or two — the key is staying hydrated and knowing when to go in.",
      ["Sip oral rehydration solution (ORS) little and often; sports drinks aren't a good substitute.",
       "Go to a doctor if there's blood, you can't keep fluids down for 12 hours, no urine for 8 hours, a high fever, or you're too dizzy to stand.",
       "If you ate wild mushrooms, pufferfish or shellfish and feel numb or keep vomiting, go to the ER now."],
      "How many hours has it been, and can you keep water down?")),

    # ── ปกป้องเด็ก / ความสัมพันธ์ที่ควบคุม ─────────────────────────────────────────────────────────────
    ("kp_minor_adult_parent",
     r"(?:ลูก|หลาน|น้อง)(?:สาว|ชาย)?\s?(?:อายุ\s?)?(?:1[0-5]|[89])\s?(?:ปี|ขวบ)?[^\n]{0,16}?(?:มีแฟน|คบ(?:กับ)?|คุยกับ|ไปเจอ)[^\n]{0,16}?(?:อายุ\s?)?(?:[2-9]\d)(?:\s?ปี)?"
     r"|\bmy (?:daughter|son|kid|child|niece|nephew|sister|brother) (?:is |who'?s )?(?:1[0-5]|thirteen|fourteen|fifteen)\b[^\n]{0,40}?\b(?:boyfriend|girlfriend|dating|seeing)\b[^\n]{0,24}?\b[2-9]\d\b",
     75, True,
     ("ผู้ใหญ่ที่คบเด็กอายุเท่านี้ ผิดที่ฝั่งผู้ใหญ่ — ลูกเป็นผู้ถูกกระทำ ไม่ใช่คนผิด",
      ["คุยกับลูกด้วยน้ำเสียงสงบ อย่าเริ่มด้วยการดุหรือยึดโทรศัพท์ — ลูกจะหลบไปคุยลับๆ แทน · บอกว่าไม่โกรธลูก แต่ห่วงเพราะผู้ใหญ่คนนี้ทำไม่ถูก",
       "เก็บหลักฐานไว้ (แชท รูป การนัดเจอ) อย่าลบ และอย่าไปเผชิญหน้ากับผู้ใหญ่คนนั้นเอง",
       "ตามกฎหมายไทย การมีเพศสัมพันธ์กับเด็กอายุต่ำกว่า 15 ปีเป็นความผิด แม้เด็กจะยินยอม — ปรึกษา 1300 (พม. 24 ชม.) หรือแจ้งตำรวจ 191"],
      "ลูกกับผู้ใหญ่คนนี้เจอกันตัวต่อตัวแล้วหรือยัง?"),
     ("An adult dating a child this age is wrong on the adult's side — your child is the one being harmed, not the one at fault.",
      ["Talk calmly; starting with punishment or taking the phone usually pushes it underground. Say you're not angry with them, you're worried because this adult is doing something wrong.",
       "Keep the evidence (messages, photos, meet-ups), don't delete anything, and don't confront the adult yourself.",
       "Report it — to the police, or a child protection line (in the US, NCMEC CyberTipline 1-800-843-5678; in Thailand 1300)."],
      "Have they already met in person?")),

    ("kp_coercive_control",
     r"(?:แฟน|สามี|ภรรยา|เมีย|ผัว)[^\n]{0,12}?(?:ติดตาม(?:ตำแหน่ง)?|แทร็ก|ติดแอป\S{0,6}(?:ติดตาม|ดักฟัง)|ส่องมือถือ|เช็ค(?:มือถือ|โทรศัพท์)|อ่านแชท|ขอรหัส|บังคับให้เปิด(?:มือถือ|ตำแหน่ง)|ห้ามออกจากบ้าน|ยึดโทรศัพท์)"
     r"|\bmy (?:partner|boyfriend|girlfriend|husband|wife|ex)\b[^\n]{0,16}?\b(?:tracks?|monitors?|reads?)\b[^\n]{0,16}?\b(?:my )?(?:phone|messages|texts|location)\b",
     60, False,
     ("ติดตามตำแหน่ง อ่านแชท หรือบังคับขอรหัส ไม่ใช่ความรัก แต่เป็นการควบคุม — และมักหนักขึ้นเรื่อยๆ",
      ["ก่อนเปลี่ยนรหัสหรือลบแอปติดตาม ให้คิดเรื่องความปลอดภัยก่อน ถ้าเขารู้ตัวแล้วอาจโกรธหนักขึ้น — ใช้เครื่องอื่นที่ปลอดภัย (เช่นของเพื่อน) ปรึกษาก่อน",
       "เช็คในเครื่อง: แอปที่ไม่รู้จัก การแชร์ตำแหน่ง (Find My, Google Maps) อุปกรณ์ที่ล็อกอินบัญชีอยู่ แล้วจดเก็บเป็นหลักฐาน",
       "ปรึกษา 1300 (พม. 24 ชม.) ได้ แม้ยังไม่มีการทำร้ายร่างกาย · ถ้าถูกขู่หรือทำร้าย โทร 191"],
      "ถ้าเขารู้ว่าคุณปิดการติดตาม คุณจะปลอดภัยไหม?"),
     ("Tracking your location, reading your messages or demanding passwords isn't love — it's control, and it usually escalates.",
      ["Think about safety before changing passwords or removing tracking apps; if they notice, it can get worse. Plan from a safe device (a friend's) first.",
       "Check your phone for unknown apps, location sharing (Find My, Google Maps) and devices logged into your accounts, and note them as evidence.",
       "Talk to a domestic abuse line even if there's no violence (US 1-800-799-7233, UK 0808 2000 247, Thailand 1300)."],
      "If they found out you turned the tracking off, would you be safe?")),

    # ── สิทธิ์ แรงงาน กฎหมาย ────────────────────────────────────────────────────────────────────────
    ("kp_overtime",
     r"ทำงาน(?:เกิน|วันละ|ทุกวัน)\s?(?:1[0-6]|9)\s?(?:ชั่วโมง|ชม)|(?:ไม่(?:ได้|มี|จ่าย)|ไม่เคยได้)\s?(?:ค่า)?(?:โอที|ล่วงเวลา)|บังคับ(?:ทำ)?โอที|ไม่มีวันหยุด"
     r"|\b(?:unpaid overtime|no overtime pay|not paid (?:for )?overtime|forced (?:to work )?overtime|(?:1[2-6])[- ]hour (?:shifts|days) (?:every day|with no)\b)",
     40, False,
     ("ตามกฎหมายแรงงานไทย ค่าล่วงเวลาเป็นสิทธิ์ของคุณ ไม่ใช่น้ำใจของนายจ้าง",
      ["เวลาทำงานปกติไม่เกิน 8 ชั่วโมงต่อวัน 48 ชั่วโมงต่อสัปดาห์ · โอทีวันทำงานต้องได้ไม่น้อยกว่า 1.5 เท่าของค่าจ้างรายชั่วโมง โอทีวันหยุดไม่น้อยกว่า 3 เท่า และต้องมีวันหยุดอย่างน้อยสัปดาห์ละ 1 วัน",
       "เก็บหลักฐานตั้งแต่วันนี้: ถ่ายรูปบัตรตอก แชทสั่งงานนอกเวลา สลิปเงินเดือน — จดวันและเวลาเข้าออกทุกวัน",
       "ยื่นคำร้องที่สำนักงานสวัสดิการและคุ้มครองแรงงานในพื้นที่ได้ฟรี โดยไม่ต้องมีทนาย — โทรถามก่อนที่ 1546"],
      "คุณทำงานจริงวันละกี่ชั่วโมง และมีหลักฐานเวลาเข้าออกไหม?"),
     ("Overtime pay is your legal right, not a favour.",
      ["Keep a record from today: photos of time cards, messages asking you to work late, payslips, and a daily log of your hours.",
       "In Thailand, normal hours are capped at 8 a day and 48 a week, overtime is at least 1.5× (3× on holidays), with at least one day off a week; elsewhere, check your country's labour office.",
       "You can usually file a free claim with the labour office without a lawyer (Thailand: 1546)."],
      "How many hours a day are you actually working, and do you have any record of it?")),

    ("kp_passport",
     r"(?:พาสปอร์ต|หนังสือเดินทาง)\S{0,10}(?:หาย|ถูกขโมย|โดนขโมย)|(?:หาย|ขโมย)\S{0,8}(?:พาสปอร์ต|หนังสือเดินทาง)"
     r"|\b(?:lost|stolen|losing|someone stole) (?:my |our |his |her )?passports?\b|\bpassports? (?:was |got |were )?(?:lost|stolen|taken)\b",
     45, False,
     ("พาสปอร์ตหายแก้ได้ — ทำตามลำดับนี้จะเร็วที่สุด",
      ["แจ้งความที่สถานีตำรวจในพื้นที่ แล้วขอใบแจ้งความ (police report) ไว้ใช้ทำเอกสารใหม่",
       "ติดต่อสถานทูตหรือสถานกงสุลของประเทศคุณ — ขอทำหนังสือเดินทางฉุกเฉิน (Emergency Travel Document) หรือเล่มใหม่ เตรียมรูปถ่าย สำเนาพาสปอร์ตเดิม และตั๋วเดินทาง",
       "ถ้านายจ้างหรือนายหน้ายึดพาสปอร์ตไว้ไม่ให้คืน นั่นผิดกฎหมายและเป็นสัญญาณการค้ามนุษย์ — แจ้ง 1300 หรือสถานทูต"],
      "ตอนนี้อยู่ประเทศไหน และมีสำเนาหรือรูปถ่ายหน้าพาสปอร์ตเก็บไว้ไหม?"),
     ("A lost passport abroad is fixable — this order is fastest.",
      ["Report it at a local police station and ask for a written police report.",
       "Contact your country's embassy or consulate for an emergency travel document or a new passport; bring photos, a copy of the old passport if you have one, and your tickets.",
       "If an employer or agent is holding your passport and won't give it back, that's illegal and a sign of trafficking — tell your embassy."],
      "Which country are you in, and do you have a copy or photo of the passport page?")),

    ("kp_summons",
     r"ไปให้ปากคำ|เรียก(?:ตัว)?ไป(?:ให้)?(?:ปากคำ|สอบสวน)"
     r"|\b(?:court summons|summons from (?:court|the court)|got a summons|subpoena\w*|being sued|got sued|served (?:with )?papers|called (?:in )?for questioning)\b",
     45, False,
     ("หมายศาลหรือหมายเรียกอย่าเพิกเฉย — มีเวลาเตรียมตัว และขอความช่วยเหลือทางกฎหมายฟรีได้",
      ["ดูให้ชัด: ศาลหรือหน่วยงานไหน คดีเลขอะไร นัดวันไหน — แล้วโทรเช็คกับศาลหรือสถานีตำรวจนั้นโดยตรงจากเบอร์ในเว็บไซต์ทางการ (มิจฉาชีพปลอมหมายศาลบ่อย ห้ามโอนเงินตามหมาย)",
       "ปรึกษาทนายฟรี: สภาทนายความ 1167 หรือศูนย์ช่วยเหลือทางกฎหมายที่ศาล · ถ้าถูกฟ้อง ต้องยื่นคำให้การภายในเวลาที่หมายกำหนด ไม่งั้นแพ้คดีโดยขาดนัดได้",
       "ถ้าถูกเรียกไปให้ปากคำ คุณมีสิทธิ์มีทนายหรือคนที่ไว้ใจอยู่ด้วย และมีสิทธิ์ไม่ให้การที่เป็นปฏิปักษ์ต่อตัวเอง"],
      "หมายนี้นัดวันไหน และมาจากศาลหรือตำรวจ?"),
     ("Don't ignore a summons — you usually have time to prepare, and free legal help exists.",
      ["Read it closely: which court or agency, the case number and the date. Then verify by calling the court directly using the number on its official website — fake summonses are a common scam; never pay money because of one.",
       "Get free or low-cost legal advice (legal aid, a law clinic, or the bar association's referral line). If you're being sued, file your response by the deadline or you can lose by default.",
       "If you're called in for questioning, you have the right to have a lawyer present and to stay silent."],
      "What date is on it, and is it from a court or the police?")),

    ("kp_deposit",
     r"(?:เงิน)?(?:ประกัน|มัดจำ)\S{0,6}(?:ห้อง|หอ|ค่าเช่า|คอนโด|บ้านเช่า)?\S{0,10}(?:ไม่(?:ได้)?คืน|ไม่ยอมคืน|ยึด|หักหมด|โดนหัก)"
     r"|\b(?:landlord|property manager)\b[^\n]{0,30}?\b(?:kept|keeping|won'?t return|didn'?t return|withh(?:e|o)ld\w*)\b[^\n]{0,20}?\bdeposit\b|\b(?:security|rental) deposit (?:back|not returned)\b",
     40, False,
     ("ผู้ให้เช่ายึดเงินประกันโดยไม่มีเหตุไม่ได้ — คุณขอคืนได้",
      ["ตามประกาศคุ้มครองผู้บริโภค ผู้ให้เช่าที่มีห้องตั้งแต่ 5 ห้องขึ้นไป ต้องคืนเงินประกันภายใน 7 วันหลังย้ายออก หักได้เฉพาะความเสียหายจริงที่แจ้งรายการให้ดู",
       "ส่งข้อความหรือหนังสือขอคืนเป็นลายลักษณ์อักษร พร้อมรูปห้องตอนย้ายออก สัญญาเช่า และใบเสร็จ — ขอรายการหักเงินเป็นข้อๆ",
       "ถ้ายังไม่คืน ร้องเรียน สคบ. 1166 หรือฟ้องคดีผู้บริโภคที่ศาลได้โดยไม่ต้องมีทนายและไม่เสียค่าธรรมเนียม"],
      "ย้ายออกมานานแค่ไหนแล้ว และมีรูปห้องตอนคืนกุญแจไหม?"),
     ("A landlord can't keep your deposit without a reason — you can ask for it back.",
      ["Ask in writing for the deposit and an itemised list of any deductions, attaching your lease, receipts and move-out photos.",
       "Most places only allow deductions for real damage beyond normal wear and tear, and set a deadline for returning it (in Thailand, 7 days for landlords with 5+ rooms).",
       "If they still refuse, file a complaint with your consumer or tenant agency, or a small-claims case."],
      "How long ago did you move out, and do you have photos from the day you handed back the keys?")),

    # ── ดูแลคนป่วยที่บ้าน · สุขภาพทั่วไป ───────────────────────────────────────────────────────────────
    ("kp_pressure_sore",
     r"แผลกดทับ|\b(?:bed ?sores?|pressure (?:sores?|ulcers?|injur\w*))\b",
     40, False,
     ("แผลกดทับป้องกันและดูแลที่บ้านได้ ถ้าเริ่มเร็ว",
      ["พลิกตัวทุก 2 ชั่วโมง ใช้หมอนรองให้ส้นเท้าและก้นกบลอยจากที่นอน · ที่นอนลมช่วยได้มาก — ยืมได้จาก รพ.สต. หรือกองทุนผู้สูงอายุในพื้นที่",
       "ผิวต้องแห้งและสะอาด เปลี่ยนผ้าอ้อมทันทีที่เปียก · ให้กินโปรตีน (ไข่ นม เนื้อ) และน้ำพอ แผลจึงหาย",
       "พบแพทย์หรือพยาบาลถ้าแผลมีกลิ่น มีหนอง ขอบดำ ลึกขึ้น หรือมีไข้ — ขอพยาบาลเยี่ยมบ้านจาก รพ.สต. หรือ อสม. ใกล้บ้านได้"],
      "แผลอยู่ตรงไหน และตอนนี้ดำ มีกลิ่น หรือมีไข้ไหม?"),
     ("Pressure sores can be prevented and cared for at home if you start early.",
      ["Turn them every 2 hours and use pillows so heels and the tailbone float off the bed; an air mattress helps a lot.",
       "Keep skin clean and dry, change pads as soon as they're wet, and make sure they get enough protein and fluids so wounds can heal.",
       "See a nurse or doctor if the wound smells, has pus, turns black, gets deeper, or there's a fever — ask about home nursing visits."],
      "Where is the sore, and is it black, smelly, or is there a fever?")),

    ("kp_vape",
     r"บุหรี่ไฟฟ้า|พอต(?:ไฟฟ้า)?|\bvap(?:e|es|ing|er)\b|\be-?cig\w*\b|\bjuul\w*\b",
     30, False,
     ("บุหรี่ไฟฟ้ามีนิโคตินสูง ติดได้เร็วโดยเฉพาะวัยรุ่น — เลิกได้ และมีคนช่วยฟรี",
      ["ถ้าเป็นลูก: ถามด้วยความอยากรู้ ไม่ใช่การจับผิด เช่น \"สูบแล้วรู้สึกยังไง\" — การดุหรือยึดอย่างเดียวมักทำให้ไปสูบลับๆ",
       "สายเลิกบุหรี่ 1600 ให้คำปรึกษาฟรี ทั้งตัววัยรุ่นและพ่อแม่ · ตั้งวันเลิก และเตรียมรับมืออาการอยากใน 1–2 สัปดาห์แรก",
       "ในไทยการขายและนำเข้าบุหรี่ไฟฟ้าผิดกฎหมาย — ถ้ามีคนขายให้เด็กในโรงเรียน แจ้งครูหรือ สคบ. 1166"],
      "คนที่สูบคือคุณเองหรือคนในบ้าน และสูบมานานแค่ไหนแล้ว?"),
     ("Vapes carry a lot of nicotine and get teens hooked quickly — quitting is possible and free help exists.",
      ["If it's your child, ask with curiosity rather than accusation (\"what does it do for you?\"); punishment alone usually drives it underground.",
       "Free quit support: in the US text \"DITCHVAPE\" to 88709 or call 1-800-QUIT-NOW; UK NHS Smokefree; Thailand 1600.",
       "Pick a quit date and plan for cravings in the first 1–2 weeks — they peak early and then fade."],
      "Is it you or someone at home who vapes, and for how long?")),

    ("kp_cat_not_eating",
     r"แมว\S{0,8}(?:ไม่(?:ยอม)?กิน|ไม่กินข้าว|ซ่อนตัว|หลบ|ซึม|ฉี่ไม่ออก|เบ่งฉี่)|\bmy cat\b[^\n]{0,20}?\b(?:isn'?t eating|not eating|won'?t eat|stopped eating|hiding|can'?t pee|straining)\b",
     45, False,
     ("แมวไม่กินอาหารเกิน 1–2 วันอันตรายกว่าที่คิด — ตับอาจเสียหายได้",
      ["แมวตัวผู้เบ่งฉี่แต่ไม่ออก ร้องตอนฉี่ หรือหายใจอ้าปาก ไปโรงพยาบาลสัตว์เดี๋ยวนี้ — ทางเดินปัสสาวะอุดตันถึงชีวิตได้ในวันเดียว",
       "ไม่กินเกิน 24 ชั่วโมง ซ่อนตัวและซึม ให้พาไปหาสัตวแพทย์ภายในวันนี้หรือพรุ่งนี้ — อย่าบังคับป้อนเอง",
       "จดไว้บอกหมอ: ไม่กินมากี่ชั่วโมง ฉี่และอึครั้งสุดท้ายเมื่อไร อาเจียนไหม และกินของแปลก (เชือก ด้าย ต้นลิลลี่) หรือเปล่า"],
      "แมวไม่กินมากี่ชั่วโมงแล้ว และยังฉี่ได้ปกติไหม?"),
     ("A cat that stops eating for more than a day or two is more serious than it looks — their liver can be damaged.",
      ["A male cat straining to pee with little or nothing coming out, crying in the litter box, or breathing with an open mouth needs an emergency vet now.",
       "Not eating for 24 hours plus hiding or lethargy means a vet visit today or tomorrow — don't force-feed.",
       "Note for the vet: hours without food, last pee and poop, vomiting, and anything odd eaten (string, thread, lilies)."],
      "How many hours since your cat ate, and are they peeing normally?")),

    # ── เสพติด · พนัน ──────────────────────────────────────────────────────────────────────────────
    ("kp_relapse",
     r"(?:กลับไป|กลับมา)(?:เสพ|ใช้ยา|ดื่ม|เล่นยา|สูบ(?:ยา|ไอซ์)?)\S{0,6}(?:อีก)?|เลิก(?:ยา|เหล้า)\S{0,10}(?:แล้ว)?\S{0,6}(?:กลับไป|กลับมา|เผลอ)|รีแลปส์"
     r"|\brelaps\w*\b|\bwent back to (?:using|drinking|meth|heroin|cocaine|pills)\b|\bused again after\b",
     50, False,
     ("การกลับไปใช้ซ้ำเกิดได้บ่อยระหว่างการเลิก — ไม่ได้แปลว่าล้มเหลว และไม่ต้องเริ่มจากศูนย์",
      ["วันนี้บอกคนหนึ่งคน (ผู้ดูแลการบำบัด เพื่อนที่เลิกด้วยกัน หรือคนในบ้านที่ไว้ใจ) — ความลับคือเชื้อเพลิงของการใช้ต่อ",
       "สายด่วนยาเสพติด 1165 ปรึกษาฟรีและเป็นความลับ · กำจัดของที่เหลือและเบอร์คนขายออกจากเครื่อง",
       "หลังเว้นไปนาน ร่างกายทนยาน้อยลง ใช้ขนาดเดิมเสี่ยงเกินขนาดมาก — ถ้าหายใจช้า เรียกไม่ตื่น หรือเจ็บหน้าอก โทร 1669 ทันที"],
      "อะไรเกิดขึ้นก่อนที่จะกลับไปใช้ครั้งนี้?"),
     ("Relapse is common in recovery — it doesn't erase your progress or mean you've failed.",
      ["Tell one person today — a counsellor, sponsor or someone you trust; secrecy fuels the next use.",
       "Free confidential help: US SAMHSA 1-800-662-4357, UK Frank 0300 123 6600. Get rid of what's left and delete dealer contacts.",
       f"After a break your tolerance is lower, so your old dose can overdose you — slow breathing, can't be woken, or chest pain: {_EMS_EN}."],
      "What was happening right before you used this time?")),

    ("kp_gambling",
     r"\bgambl\w*\b[^\n]{0,24}?\b(?:away|addict\w*|my (?:salary|savings|paycheck|rent)|can'?t stop|lost (?:all|everything))\b|\b(?:can'?t stop|addicted to) (?:betting|gambling|slots|online casino)\b",
     50, False,
     ("การพนันออกแบบมาให้หยุดยาก — ไม่ใช่เพราะคุณอ่อนแอ แต่เพราะมันถูกสร้างมาแบบนั้น",
      ["ปิดทางเข้าวันนี้: ลบแอป บล็อกเว็บ ปิดการผูกบัญชีธนาคารกับเว็บพนัน และให้คนที่ไว้ใจถือบัตร ATM ชั่วคราว",
       "อย่ายืมเงินเพื่อ 'ตามทุนคืน' — ทุกครั้งที่ตามคือเสียเพิ่ม · จดหนี้ทั้งหมดไว้ที่เดียว แล้วปรึกษาหมอหนี้ 1443 ก่อนกู้นอกระบบ",
       "ปรึกษาสายด่วนสุขภาพจิต 1323 เรื่องติดพนันได้ฟรี — เป็นอาการที่รักษาได้เหมือนการติดสารเสพติด"],
      "ตอนนี้เป็นหนี้จากการพนันประมาณเท่าไร และมีใครรู้เรื่องนี้บ้างไหม?"),
     ("Gambling is designed to be hard to stop — it's not weakness, it's how it was built.",
      ["Shut the doors today: delete apps, install a gambling blocker, use your bank's gambling block, and let someone you trust hold your cards for a while.",
       "Don't borrow to win it back; chasing losses always costs more. List every debt in one place before you take on any new loan.",
       "Free help: US 1-800-GAMBLER, UK GamCare 0808 8020 133 — gambling disorder is treatable."],
      "Roughly how much do you owe from gambling, and does anyone know?")),

    ("kp_late_period",
     r"ประจำเดือน\S{0,6}(?:ไม่มา|ขาด|เลื่อน|มาช้า|หาย)|เมนส์\S{0,4}(?:ไม่มา|ขาด|เลื่อน)|\b(?:my )?period(?: is| has been| was)? (?:\w+ (?:days?|weeks?) )?(?:late|missed|hasn'?t come|didn'?t come)\b|\bmissed (?:my )?period\b",
     30, False,
     ("ประจำเดือนเลื่อนเกิดได้หลายสาเหตุ ไม่ได้แปลว่าตั้งครรภ์เสมอไป",
      ["ตรวจครรภ์ให้แม่นที่สุด: ใช้ปัสสาวะแรกตอนเช้า ตรวจหลังมีเพศสัมพันธ์อย่างน้อย 3 สัปดาห์ ถ้าผลลบแต่ยังไม่มา ตรวจซ้ำอีก 1 สัปดาห์",
       "สาเหตุอื่นที่พบบ่อย: เครียด นอนน้อย น้ำหนักขึ้นลงเร็ว ออกกำลังหนัก ถุงน้ำรังไข่หลายใบ (PCOS) หรือไทรอยด์ — ขาดเกิน 3 เดือนให้พบแพทย์",
       "ปวดท้องน้อยข้างเดียวรุนแรง มีเลือดออก หรือหน้ามืด ไปห้องฉุกเฉินทันที (อาจเป็นท้องนอกมดลูก) · ถ้าผลบวกและยังไม่พร้อม ปรึกษา 1663 ได้ฟรีและเป็นความลับ"],
      "เลื่อนมากี่วันแล้ว และตรวจครรภ์ไปตอนไหน?"),
     ("A late period has many causes — it doesn't always mean pregnancy.",
      ["For the most accurate test, use first-morning urine at least 3 weeks after sex; if it's negative and your period still hasn't come, test again in a week.",
       "Other common causes: stress, poor sleep, fast weight change, hard exercise, PCOS or thyroid problems — see a doctor if you miss 3 periods.",
       "Severe one-sided lower belly pain, bleeding or fainting needs the ER now (it can be an ectopic pregnancy)."],
      "How many days late is it, and when did you test?")),
]

# ถามเพื่อความรู้ ไม่ใช่เกิดกับใครตอนนี้ — "อธิบายลมแดดให้หน่อย จะทำรายงาน"
EDU = r"อธิบาย|ทำรายงาน|การบ้าน|คืออะไร|หมายถึงอะไร|ถามเฉยๆ|ผิดกฎหมายไหม|\b(?:explain|essay|homework|school project|for (?:a|my) (?:report|class))\b"
NEG = {
    # ธาตุเหล็กทำให้อุจจาระดำได้ — ไม่นับถ้าไม่มีอาการร่วม
    "kp_gi_bleed": r"^(?=[\s\S]*(?:ยาบำรุงเลือด|ธาตุเหล็ก|\biron\b))(?![\s\S]*(?:เวียน|หน้ามืด|ใจสั่น|อ่อนเพลีย|อาเจียน|\bdizz|\bfaint|\bvomit))",
}

NAMES = tuple(n for n, *_ in PACK)
URGENT = tuple(n for n, _rx, _r, urgent, *_ in PACK if urgent)
RISK = {n: r for n, _rx, r, *_ in PACK}
RX = {n: re.compile(r"^(?![\s\S]*(?:" + EDU + r"))" + (r"(?!" + NEG[n] + r")" if n in NEG else "") + r"[\s\S]*?(?:" + rx + r")", re.I) for n, rx, *_ in PACK}


def th_topics() -> list:
    """รูปแบบเดียวกับ TOPICS ใน kernel_voice: (ชื่อ, [regex], {open, paths, ask})"""
    return [(n, [RX[n]], {"open": [th[0]], "paths": list(th[1]), "ask": th[2]}) for n, _rx, _r, _u, th, _en in PACK]


def en_topics() -> dict:
    """รูปแบบเดียวกับ EN_TOPIC: ชื่อ → (open, [paths], ask)"""
    return {n: (en[0], list(en[1]), en[2]) for n, _rx, _r, _u, _th, en in PACK}


def match(text) -> list:
    t = str(text or "")
    return [n for n in NAMES if RX[n].search(t)]
