"""
core/problem_lens.py — เลนส์ปัญหา: มองให้ทะลุก่อนตอบ (ตอนไม่มี AI)

เจ้าของโปรเจกต์: "เราต้องทำให้ระบบเรามองทะลุทุกปัญหา ตอบอย่างมีเหตุผล"

ก่อนมีเลนส์นี้ ระบบจับคำได้ แต่ไม่ได้ถามว่า "ปัญหานี้เป็นของใคร" และ "แก่นจริงคืออะไร" เช่น
- "แม่ป่วยติดเตียง ต้องลาออกมาดูแล เงินเก็บใกล้หมด" ได้คำตอบเรื่องไข้สูงหายใจลำบาก (เหมือนผู้ใช้ป่วยเอง)
- "พ่อติดเหล้า เมาแล้วด่าแม่ทุกคืน" ได้วิธีเลิกเหล้า (เหมือนผู้ใช้ติดเอง) และไม่เห็นว่าแม่กำลังถูกทำร้ายทางใจ
- "แฟนขอเลิก คบกันมา 7 ปี" ได้ "ไม่ต้องรีบตัดสินใจ" ทั้งที่อีกฝ่ายตัดสินใจไปแล้ว
- เรื่องอีก 7 จาก 20 ข้อได้แม่แบบกลาง "ขอเรียงเรื่องนี้ให้เห็นเป็นขั้นก่อน" ที่ใช้ได้กับทุกเรื่อง

ทุกเลนส์ตอบ 3 อย่างตามลำดับ:
1. open — อ่านเรื่องให้ถูก: ปัญหาของใคร แก่นคืออะไร "เพราะ" อะไร (เหตุผล ไม่ใช่คำปลอบลอยๆ)
2. paths — 3 ขั้นที่เจาะจงกับเรื่องนั้น เรียงจากทำได้ก่อน/ย้อนกลับได้ก่อน
3. ask — คำถามเดียวที่ช่วยให้เห็นทางต่อ

ไม่แย่งเรื่องวิกฤต: kernel_voice เรียกเลนส์หลังด่านวิกฤต มิจฉาชีพ และการทำร้ายร่างกาย
และเลนส์ทุกตัวมี `no` กันคำที่บอกว่าเป็นเรื่องอื่น (เช่น ตี/ทำร้าย → ให้คำตอบเรื่องความปลอดภัยรับไป)
"""
from __future__ import annotations

import re

_I = re.I

# คนในครอบครัว/คนใกล้ตัว — ใช้แยก "ปัญหาของเขา" ออกจาก "ปัญหาของฉัน"
_KIN = r"(?:พ่อ|แม่|ปู่|ย่า|ตา|ยาย|สามี|ภรรยา|ภรรยา|เมีย|ผัว|แฟน|พี่ชาย|พี่สาว|น้องชาย|น้องสาว|ลูก|ป้า|ลุง|น้า|อา)"
# การทำร้ายร่างกาย — เรื่องแบบนี้ต้องได้คำตอบด้านความปลอดภัย (kernel_voice: FAMILY_WITNESS / SAFETY) ไม่ใช่เลนส์
# "ตี" ต้องไม่ใช่ส่วนหนึ่งของคำอื่น — "ติดเ*ตี*ยง" "เ*ตี*ยม" "*ตี*น" "*ตี*สาม" เคยทำให้เลนส์คนดูแลผู้ป่วยถอยไปเอง
# "มีด" ต้องไม่ใช่ "สามีดูถูก" "มีดี" — ภาษาไทยไม่เว้นวรรคระหว่างคำ คำสั้นจึงซ้อนอยู่ในคำอื่นได้ง่าย
_PHYSICAL = r"(?<![เแ])ตี(?![ยนมสหค])|ต่อย|(?<![ป])ตบ(?!แต่ง)|เตะ|ทุบ|ทำร้าย|บีบคอ|(?<!สา)มีด(?![ีูน])|ปืน|เลือด|ฆ่า"


def _rx(p: str) -> re.Pattern:
    return re.compile(p, _I)


LENSES = [
    # ── คนดูแลผู้ป่วยในบ้าน ─────────────────────────────────────────────
    {
        "key": "caregiver_load",
        "verdict": ('ยังไม่ลาออก — แบ่งภาระและดูตัวเลขให้ครบก่อน แล้วค่อยตัดสิน', "Don't quit yet — share the load and see the full numbers first, then decide"),   # เรื่องนี้เป็นสถานการณ์ ไม่ใช่การตัดสินใจ — มติสภาไม่ใช่ "เดินหน้า/ชะลอ"
        "th": _rx(rf"{_KIN}\S{{0,6}}(?:ป่วย|ติดเตียง|อัมพาต|อัมพฤกษ์|สมองเสื่อม|อัลไซเมอร์|เป็นมะเร็ง|ล้มป่วย|นอนติดเตียง)"
                  r"[^\n]{0,60}?(?:ลาออก|เงิน|ค่าใช้จ่าย|ค่ายา|พี่น้อง|ไม่มีใครช่วย|ไม่ช่วย)"),   # เหนื่อย/ดูแลไม่ไหวอย่างเดียว → คำตอบ caregiver เดิมใน kernel_voice
        "en": _rx(r"\b(?:my )?(?:mom|mum|mother|dad|father|wife|husband|grand(?:ma|pa|mother|father))\b[^\n]{0,40}?"
                  r"\b(?:is )?(?:bedridden|has (?:dementia|alzheimer'?s|cancer)|had a stroke|is (?:very )?(?:sick|ill))\b"
                  r"[^\n]{0,80}?\b(?:quit|money|savings|afford|siblings?|brothers?|sisters?|no one helps)\b"),
        "no": _rx(_PHYSICAL),
        "th_d": {
            "vega": 'ตัวแปรที่ตัดสินเรื่องนี้คือจำนวนเดือนที่เงินเก็บรองรับได้ เทียบกับระยะเวลาการดูแลที่อาจยาวเป็นปี — จุดที่ย้อนกลับยากคือการลาออก ต้องตัดสินจากตัวเลข ไม่ใช่จากความรู้สึกผิด',
            "open": ["ปัญหาจริงไม่ใช่การดูแล แต่คือคุณกำลังแบกคนเดียว ทั้งแรง เงิน และใจ "
                     "— ภาระที่ไม่มีวันหยุดแบบนี้ ถ้าไม่แบ่ง คนดูแลจะล้มก่อนคนป่วย"],
            "paths": [
                "ยังไม่ลาออกจนกว่าจะเห็นตัวเลขครบ: ค่าใช้จ่ายต่อเดือนของแม่ (ยา ผ้าอ้อม อาหาร) เทียบกับรายได้ที่จะหายไป "
                "— ถามเรื่องลาดูแลครอบครัว ทำงานจากบ้าน หรือลดเวลาก่อน เพราะลาออกแล้วกลับยาก",
                "ใช้ความช่วยเหลือที่มีจริง: ถาม รพ.สต. หรือ อบต./เทศบาล เรื่องสิทธิ์ดูแลระยะยาวสำหรับผู้มีภาวะพึ่งพิง (บัตรทอง) "
                "ซึ่งมีผู้ช่วยดูแลมาเยี่ยมบ้าน · ผู้ป่วยติดเตียงขอขึ้นทะเบียนผู้พิการเพื่อรับเบี้ยรายเดือนได้ · ครอบครัวรับไม่ไหว โทร พม. 1300 (24 ชม.)",
                "คุยกับพี่น้องด้วยตัวเลข ไม่ใช่ความรู้สึก: เขียนว่าเดือนหนึ่งใช้เงินเท่าไร ใช้เวลากี่ชั่วโมง "
                "แล้วขอสิ่งที่เจาะจง เช่น \"ช่วยเดือนละ 3,000\" หรือ \"มาเฝ้าเสาร์เว้นเสาร์\" — คำขอที่เจาะจงปฏิเสธยากกว่า",
            ],
            "ask": "ตอนนี้ใช้จ่ายเรื่องแม่เดือนละประมาณเท่าไร และเงินเก็บที่เหลืออยู่ได้อีกกี่เดือน?",
        },
        "en_d": {
            "vega": 'The deciding variable is how many months your savings cover against care that may last years. The hard-to-reverse step is quitting — decide it from the numbers, not from guilt.',
            "open": ["The real problem isn't the caring — it's that you're carrying it alone: the hours, the money and the "
                     "worry. Care with no days off wears the carer down before the patient."],
            "paths": [
                "Don't quit until you've seen the numbers: monthly care costs against the income you'd lose. Ask about "
                "family-care leave, remote work or reduced hours first — leaving a job is hard to undo.",
                "Use the help that exists: home-visit nursing from the local hospital, disability or carer allowances, "
                "and day-care or respite services in your area.",
                "Talk to your siblings with numbers, not feelings: what it costs per month and how many hours it takes, "
                "then ask for something specific (\"3,000 a month\" or \"every other Saturday\"). Specific asks are harder to refuse.",
            ],
            "ask": "Roughly how much does the care cost each month, and how many months can your savings cover?",
        },
    },
    # ── คนในบ้านติดเหล้า/พนัน แล้วลงที่คนอื่น (ไม่ใช่ผู้ใช้ติดเอง) ─────────────
    {
        "key": "family_addiction",
        "verdict": ('ความปลอดภัยของคนในบ้านมาก่อน แล้วค่อยหาทางช่วยคนที่ติด', "Everyone's safety at home first, then look for help for the person who drinks"),   # เรื่องนี้เป็นสถานการณ์ ไม่ใช่การตัดสินใจ — มติสภาไม่ใช่ "เดินหน้า/ชะลอ"
        "th": _rx(rf"{_KIN}\S{{0,4}}(?:ติดเหล้า|ติดพนัน|ติดยา|กินเหล้า|เมา|เล่นพนัน|เล่นหวย|ติดการพนัน)"
                  r"[^\n]{0,40}?(?:ด่า|ตะคอก|อาละวาด|เสียงดัง|เอาเงิน|ขโมยเงิน|ขอเงิน|ทะเลาะ|ทุกคืน|ทุกวัน|ไม่กลับบ้าน|หนี้)"),
        "en": _rx(r"\bmy (?:mom|mum|mother|dad|father|husband|wife|brother|sister|partner)\b[^\n]{0,30}?"
                  r"\b(?:drinks|is an alcoholic|gambles|is addicted|gets drunk)\b[^\n]{0,60}?\b(?:yells|screams|shouts|takes (?:our|my) money|debt|every night)\b"),
        "no": _rx(_PHYSICAL),
        "th_d": {
            "vega": 'โครงสร้างของปัญหา: คนที่ต้องเปลี่ยนคือคนที่ไม่ได้ขอความช่วยเหลือ ส่วนคนที่ขอคือคุณ — จึงลงแรงกับสิ่งที่คุณควบคุมได้ คือความปลอดภัยของคนในบ้านและของตัวเอง ก่อนพยายามเปลี่ยนเขา',
            "open": ["เรื่องนี้คุณไม่ได้เป็นคนติด แต่เป็นคนที่ต้องอยู่กับผลของมันทุกคืน "
                     "— และการถูกด่าหรืออาละวาดใส่ซ้ำๆ คือการทำร้ายทางใจ ไม่ใช่เรื่องปกติของบ้านไหน"],
            "paths": [
                "อย่าคุยหรือห้ามตอนเขาเมา — คนเมาฟังเหตุผลไม่ได้ และมักแรงขึ้น · คุยตอนเขาสร่างแล้ว ประโยคสั้นๆ "
                "ว่าเห็นอะไร รู้สึกอย่างไร เช่น \"เมื่อคืนตอนเมา ทุกคนในบ้านกลัวมาก\"",
                "ดูแลความปลอดภัยของคนในบ้านก่อนพยายามเปลี่ยนเขา: มีห้องหรือบ้านญาติที่ไปอยู่ได้ในคืนที่หนัก · ถ้าเริ่มขว้างของหรือลงมือ "
                "โทร 191 หรือ 1300 (24 ชม.) ได้ทันที",
                "คนที่ติดต้องอยากเลิกเอง แต่ครอบครัวขอคำแนะนำได้ก่อน: สายเลิกเหล้า 1413 ให้คำปรึกษาคนในครอบครัวด้วย "
                "· คลินิกยาเสพติด/สุราในโรงพยาบาลรัฐ รับปรึกษาญาติได้",
            ],
            "ask": "ตอนนี้ทุกคนในบ้านปลอดภัยไหม และเคยมีครั้งไหนที่เขาเริ่มลงมือหรือขว้างของหรือเปล่า?",
        },
        "en_d": {
            "vega": "The structure: the person who needs to change isn't the one asking for help — you are. So invest in what you control, everyone's safety, before trying to change them.",
            "open": ["You're not the one with the addiction — you're the one living with its effects every night. "
                     "Being yelled at again and again is emotional abuse, not a normal part of family life."],
            "paths": [
                "Don't argue while they're drunk — they can't hear reason and it often escalates. Talk when they're sober, "
                "briefly: what you saw and how it felt.",
                "Keep yourself and the person being yelled at safe first: somewhere to stay on bad nights, and call the "
                "police (191 in Thailand) if things are thrown or anyone is touched.",
                "They have to want to stop, but families can get help first: in Thailand 1413 also counsels relatives; "
                "elsewhere, Al-Anon or Gam-Anon groups are for families.",
            ],
            "ask": "Is everyone safe right now, and has it ever turned physical?",
        },
    },
    # ── ถูกบอกเลิก (อีกฝ่ายตัดสินใจไปแล้ว) ──────────────────────────────
    {
        "key": "breakup_received",
        "verdict": ('ดูแลใจก่อน เรื่องปฏิบัติ (ของ เงิน ที่อยู่) ค่อยตัดสินหลังสองสัปดาห์', 'Look after yourself first; settle practical things after two weeks'),   # เรื่องนี้เป็นสถานการณ์ ไม่ใช่การตัดสินใจ — มติสภาไม่ใช่ "เดินหน้า/ชะลอ"
        "th": _rx(r"(?:แฟน|สามี|ภรรยา|เมีย|ผัว|เขา|เธอ)\S{0,4}(?:ขอเลิก|บอกเลิก|ขอหย่า|ทิ้ง(?:ฉัน|เรา|หนู|ผม)|ไปมีคนใหม่|เลิกกับ(?:ฉัน|เรา|หนู|ผม))"),
        "en": _rx(r"\b(?:my )?(?:girlfriend|boyfriend|partner|wife|husband|fianc[eé]e?)\b[^\n]{0,20}?\b(?:broke up with me|dumped me|left me|wants? (?:a divorce|to break up))\b|\bgot dumped\b"),
        "no": _rx(_PHYSICAL + r"|ตาม|ขู่|แบล็กเมล|คลิป"),
        "th_d": {
            "vega": 'ข้อเท็จจริง: การตัดสินใจสิ้นสุดที่อีกฝ่ายแล้ว ตัวแปรที่ยังอยู่ในมือคือเวลาฟื้นตัวและการตัดสินใจเรื่องปฏิบัติ (ของ เงิน ที่อยู่) — อย่าตัดสินเรื่องเหล่านั้นในสองสัปดาห์แรก',
            "open": ["การตัดสินใจครั้งนี้ไม่ได้อยู่ในมือคุณ — สิ่งที่อยู่ในมือคือจะดูแลใจตัวเองช่วงนี้อย่างไร "
                     "ความเจ็บที่หนักขนาดนี้สมเหตุสมผล เพราะสิ่งที่หายไปไม่ใช่แค่คน แต่คือชีวิตประจำวันและอนาคตที่วาดไว้ด้วยกัน"],
            "paths": [
                "อย่าเพิ่งถามหาเหตุผลซ้ำหรือขอให้กลับมาในช่วงนี้ — คำตอบที่ได้ตอนอารมณ์แรงมักทำให้เจ็บเพิ่ม "
                "พัก 2–4 สัปดาห์ก่อนคุยเรื่องค้างคา (ของ เงิน ที่อยู่)",
                "ลดสิ่งที่กระตุกใจ: ปิดการแจ้งเตือนหรือซ่อนโซเชียลของเขาไว้ก่อน (ไม่ต้องบล็อกถ้ายังไม่พร้อม) "
                "· จัดวันให้มีโครง กิน นอน ออกไปข้างนอกวันละครั้ง",
                "บอกคนใกล้ตัว 1–2 คนว่าช่วงนี้ไม่ไหว ขอให้ชวนกินข้าวหรือโทรมาบ้าง "
                "· ถ้าผ่านไปหลายสัปดาห์แล้วยังกินไม่ได้นอนไม่หลับ หรือเริ่มคิดว่าไม่อยากอยู่ โทร 1323 ได้",
            ],
            "ask": "ตอนนี้สิ่งที่หนักที่สุดคืออะไร — คิดถึงเขา โกรธ หรือกลัวการเริ่มใหม่คนเดียว?",
        },
        "en_d": {
            "vega": "Fact: the decision has been made on their side. What's still in your hands is recovery time and the practical decisions (belongings, money, housing) — don't settle those in the first two weeks.",
            "open": ["This decision wasn't yours to make — what is yours is how you look after yourself now. "
                     "Hurting this much makes sense: you didn't just lose a person, you lost a daily life and a future you'd pictured together."],
            "paths": [
                "Don't keep asking why or asking them back for now — answers given in raw moments usually hurt more. "
                "Give it 2–4 weeks before sorting out practical things (belongings, money, housing).",
                "Cut the triggers: mute or hide their social media for now (no need to block if you're not ready). "
                "Give your days some shape — eat, sleep, get outside once a day.",
                "Tell one or two close people you're struggling and ask them to check in. If weeks pass and you still "
                "can't eat or sleep, or you start feeling you don't want to be here, reach out to a crisis line.",
            ],
            "ask": "What's heaviest right now — missing them, anger, or facing starting over?",
        },
    },
    # ── ขัดแย้งกับพ่อแม่ของคู่ แล้วคู่ไม่ยืนข้าง ──────────────────────────
    {
        "key": "inlaw_spouse",
        "verdict": ('ตกลงกับคู่ของคุณให้ได้ก่อน แล้วให้เขาเป็นคนคุยกับพ่อแม่ของเขา', 'Reach an agreement with your partner first, then let them talk to their parent'),   # เรื่องนี้เป็นสถานการณ์ ไม่ใช่การตัดสินใจ — มติสภาไม่ใช่ "เดินหน้า/ชะลอ"
        "th": _rx(r"(?:แม่สามี|แม่ผัว|พ่อสามี|พ่อผัว|แม่ยาย|พ่อตา|ครอบครัวสามี|ครอบครัวแฟน|บ้านสามี|ญาติสามี|ญาติแฟน)"
                  r"[^\n]{0,60}?(?:สามี|ผัว|แฟน|ภรรยา|เมีย)\S{0,6}(?:ไม่เข้าข้าง|ไม่ช่วย|เข้าข้างแม่|เข้าข้างพ่อ|ไม่พูด|เงียบ|ไม่ปกป้อง)"),
        "en": _rx(r"\b(?:mother|father)-in-law\b[^\n]{0,80}?\b(?:husband|wife|partner)\b[^\n]{0,20}?\b(?:doesn'?t|won'?t|never)\b[^\n]{0,20}?\b(?:back(?:s)? me|takes? my side|supports? me|says? anything|stands? up)"),
        "no": _rx(_PHYSICAL),
        "th_d": {
            "vega": 'จุดรับแรงที่แท้จริงคือข้อตกลงระหว่างคุณกับสามี ไม่ใช่ระหว่างคุณกับแม่สามี — ถ้าข้อตกลงนั้นยังไม่มี การปะทะกับแม่สามีจะวนซ้ำทุกเรื่อง',
            "open": ["แก่นของเรื่องไม่ใช่แม่สามี แต่คือคุณกับสามียังไม่ได้เป็นทีมเดียวกัน "
                     "— เรื่องเลี้ยงลูกเป็นการตัดสินใจของพ่อแม่สองคน ถ้าสองคนยังไม่ตกลงกัน ผู้ใหญ่คนอื่นก็จะเข้ามาเติมช่องว่างนั้นเสมอ"],
            "paths": [
                "คุยกับสามีสองต่อสองตอนที่ไม่ได้ทะเลาะ เริ่มจากสิ่งที่ทั้งคู่อยากได้เหมือนกัน (ลูกปลอดภัย บ้านไม่ตึง) "
                "แล้วค่อยถามว่า \"เรื่องไหนเราจะตัดสินใจกันเอง\" — ไม่ใช่ \"ทำไมไม่เข้าข้างฉัน\"",
                "ตกลงกันให้ชัด 2–3 เรื่องที่ไม่ยอมถอย (เช่น ยา อาหาร การตี) ส่วนเรื่องเล็กปล่อยให้ย่าทำตามแบบย่าได้ "
                "— การยอมเรื่องเล็กทำให้เรื่องใหญ่ได้รับการฟัง",
                "ให้สามีเป็นคนพูดกับแม่ของเขาเอง ในนามของ \"เรา\" — คำเดียวกันออกจากปากลูก แม่รับได้ง่ายกว่าออกจากปากลูกสะใภ้",
            ],
            "ask": "เรื่องเลี้ยงลูกเรื่องไหนที่คุณถอยไม่ได้จริงๆ และสามีเคยบอกไหมว่าเขาคิดยังไงกับเรื่องนั้น?",
        },
        "en_d": {
            "vega": 'The real load-bearing point is the agreement between you and your partner, not between you and the in-law. Without it, every clash with the in-law will repeat.',
            "open": ["The core issue isn't your in-law — it's that you and your partner aren't yet acting as one team. "
                     "Raising your child is a decision for the two of you; when you haven't agreed, other adults will always fill that gap."],
            "paths": [
                "Talk with your partner alone, when you're not fighting. Start from what you both want (a safe child, a calmer home), "
                "then ask \"which things do we decide ourselves?\" — not \"why don't you take my side?\"",
                "Agree on 2–3 non-negotiables (medicine, food, physical punishment) and let the small things go — "
                "giving way on small things gets the big ones heard.",
                "Ask your partner to speak to their own parent, as \"we\". The same words land far better from their own child.",
            ],
            "ask": "Which parenting issue can you truly not give way on, and has your partner said what they think about it?",
        },
    },
    # ── เปรียบเทียบตัวเองกับคนอื่น / รู้สึกตามไม่ทัน ─────────────────────────
    {
        "key": "comparison",
        "verdict": ('เปลี่ยนตัววัดเป็นการเติบโตของตัวเอง แล้วเลือกก้าวแรกหนึ่งข้อ', 'Switch the measure to your own growth, then pick one first step'),   # เรื่องนี้เป็นสถานการณ์ ไม่ใช่การตัดสินใจ — มติสภาไม่ใช่ "เดินหน้า/ชะลอ"
        "th": _rx(r"(?:อายุ\s?\d{2}[^\n]{0,10}?(?:ยังไม่มี|ยังไม่ได้|ยังไม่เป็น|ไม่มีอะไร)|ตามคนอื่นไม่ทัน|ตามเพื่อนไม่ทัน|"
                  r"เปรียบเทียบ(?:ตัวเอง)?กับ(?:เพื่อน|คนอื่น)|เห็นเพื่อน\S{0,20}(?:แล้ว)?(?:รู้สึก)?(?:แย่|ไร้ค่า|ด้อย|ล้มเหลว)|"
                  r"ชีวิตไม่ไปถึงไหน|ล้าหลังเพื่อน|เพื่อนไปไกลแล้ว)"),
        "en": _rx(r"\b(?:compar(?:e|ing) (?:myself|me) (?:to|with)|everyone (?:else )?is ahead|falling behind (?:my )?(?:friends|everyone|peers)|"
                  r"(?:i'?m|at) \d{2} and (?:still )?(?:have|own) nothing|feel (?:like a failure|worthless) (?:compared|when i see))"),
        "no": _rx(r"อยากตาย|ไม่อยากอยู่|ฆ่าตัว|\bkill myself\b|\bend it\b"),
        "th_d": {
            "vega": 'ตัววัดที่ใช้อยู่ผิดชุดข้อมูล: เทียบค่าเฉลี่ยชีวิตจริงของคุณกับค่าสูงสุดที่คนอื่นเลือกโชว์ — เปลี่ยนตัววัดเป็นการเติบโตของตัวเองในช่วงเวลาที่กำหนด แล้วผลจะต่างออกไป',
            "open": ["ความรู้สึกตามไม่ทันเกิดจากการเอาเบื้องหลังของเราไปเทียบกับหน้าฉากของคนอื่น "
                     "— เราเห็นความยากของตัวเองทุกวัน แต่เห็นของเขาแค่ตอนสำเร็จ ตัวเลขอายุจึงดูเหมือนเส้นชัย ทั้งที่ไม่ใช่"],
            "paths": [
                "เปลี่ยนคู่เทียบเป็นตัวเองเมื่อ 3 ปีก่อน: เขียนสิ่งที่ทำได้ รู้ หรือรอดมาได้ตั้งแต่ตอนนั้น "
                "— มักมากกว่าที่รู้สึก เพราะความเหนื่อยลบความจำเรื่องที่ผ่านมาได้",
                "ถามให้ชัดว่า \"มีอะไรเป็นของตัวเอง\" หมายถึงอะไรสำหรับคุณ — บ้าน เงินเก็บ งานที่มั่นคง หรือความรู้สึกว่ามีทาง "
                "เลือกมาหนึ่งข้อแล้ววางก้าวแรกที่ทำได้เดือนนี้",
                "ลดสิ่งที่ป้อนการเปรียบเทียบ 2 สัปดาห์: ซ่อนโพสต์ของบัญชีที่ดูแล้วรู้สึกแย่ แล้วสังเกตว่าใจเบาลงไหม",
            ],
            "ask": "ถ้าต้องเลือกหนึ่งอย่างที่อยากให้เป็นของตัวเองภายใน 3 ปี อะไรสำคัญที่สุด?",
        },
        "en_d": {
            "vega": "You're measuring against the wrong data: your real average against everyone else's chosen peaks. Switch the metric to your own growth over a set period and the result changes.",
            "open": ["Feeling behind comes from comparing your behind-the-scenes with everyone else's highlight reel. "
                     "You see your own struggle every day, but you only see theirs when they win — so age starts to look like a finish line. It isn't one."],
            "paths": [
                "Compare yourself with you three years ago instead: write down what you've learned, built or survived since then. "
                "It's usually more than it feels, because exhaustion erases memory.",
                "Pin down what \"having something\" means to you — a home, savings, steady work, or a sense of direction. "
                "Pick one and set a first step you can take this month.",
                "Cut the feed for two weeks: mute the accounts that leave you feeling worse, and notice whether your mood lifts.",
            ],
            "ask": "If you could make one thing truly yours within three years, what would matter most?",
        },
    },
    # ── ถูกเอาผลงานไปอ้าง ─────────────────────────────────────────────
    {
        "key": "credit_stolen",
        "verdict": ('เก็บหลักฐานและทำให้งานของคุณถูกเห็น ยังไม่ต้องปะทะ', 'Keep the evidence and make your work visible — no confrontation yet'),   # เรื่องนี้เป็นสถานการณ์ ไม่ใช่การตัดสินใจ — มติสภาไม่ใช่ "เดินหน้า/ชะลอ"
        "th": _rx(r"(?:เอา|ขโมย|แอบเอา|ชิง)(?:ผลงาน|งาน|ไอเดีย|เครดิต)\S{0,12}(?:ไป)?(?:เสนอ|อ้าง|พรีเซนต์|ส่ง|เคลม)|เคลมงาน(?:ของ)?(?:ฉัน|เรา|ผม|หนู)|เอาหน้า(?:จาก)?งาน"),
        "en": _rx(r"\b(?:took|takes|stole|steals|claimed|claims) (?:the )?credit for my\b|\bpresented my (?:work|idea|project) as (?:his|her|their) own\b"),
        "no": None,
        "th_d": {
            "vega": 'ปัญหาคือการมองเห็น ไม่ใช่ความยุติธรรม — ใครควบคุมช่องทางที่หัวหน้าเห็นงาน คนนั้นได้เครดิต ทางแก้ระยะยาวคือเปิดช่องทางของคุณเอง',
            "open": ["เรื่องนี้แก้ได้ด้วยหลักฐานและการมองเห็น ไม่ใช่การปะทะ "
                     "— ถ้าโวยตอนนี้ คนจะจำว่าคุณอารมณ์เสีย แต่ถ้าทำให้งานของคุณถูกเห็นตั้งแต่ต้น คนอื่นจะเอาไปอ้างยาก"],
            "paths": [
                "รวบรวมร่องรอยว่าเป็นงานของคุณ: ไฟล์ที่มีวันที่ อีเมล แชท ประวัติแก้ไขเอกสาร — เก็บไว้ก่อน ยังไม่ต้องใช้",
                "คุยกับหัวหน้าแบบเล่าข้อเท็จจริง ไม่กล่าวหา: \"งานชิ้นนี้ผมทำส่วน A และ B อยากให้หัวหน้าเห็นที่มา "
                "เผื่อมีคำถามต่อ ผมตอบได้\" — ให้หัวหน้าสรุปเอง",
                "ต่อจากนี้ทำให้งานมีชื่อคุณตั้งแต่แรก: ส่งความคืบหน้าทางอีเมลโดยสำเนาหัวหน้า ขอนำเสนอส่วนที่ทำเอง "
                "· ถ้าเกิดซ้ำกับคนเดิม ค่อยแจ้ง HR พร้อมหลักฐาน",
            ],
            "ask": "มีหลักฐานอะไรบ้างที่แสดงว่างานชิ้นนั้นเป็นของคุณ และหัวหน้ารู้ไหมว่าใครทำส่วนไหน?",
        },
        "en_d": {
            "vega": 'This is a visibility problem, not a fairness problem — whoever controls the channel your manager sees work through gets the credit. The durable fix is opening your own channel.',
            "open": ["This is solved with evidence and visibility, not confrontation. Blow up now and people remember the outburst; "
                     "make your work visible from the start and it becomes hard for anyone to claim it."],
            "paths": [
                "Gather the trail that shows it's yours — dated files, emails, chats, document edit history. Keep it; you may not need it.",
                "Talk to your manager with facts, not accusations: \"I did parts A and B of this — wanted you to know the background "
                "in case questions come up.\" Let them draw the conclusion.",
                "From now on, put your name on work early: progress updates by email with your manager copied, and ask to present "
                "your own part. If it happens again with the same person, take it to HR with the evidence.",
            ],
            "ask": "What evidence do you have that it was your work, and does your manager know who did which part?",
        },
    },
    # ── นอนดึกจนกระทบงาน ──────────────────────────────────────────────
    {
        "key": "late_sleep",
        "verdict": ('ล็อกเวลาตื่นก่อน แล้วค่อยขยับเวลานอน', 'Fix your wake time first, then move bedtime'),   # เรื่องนี้เป็นสถานการณ์ ไม่ใช่การตัดสินใจ — มติสภาไม่ใช่ "เดินหน้า/ชะลอ"
        "th": _rx(r"(?:นอน|หลับ)\S{0,4}(?:ตี\s?[2-6]|ตี(?:สอง|สาม|สี่|ห้า)|ดึก|เช้า)\S{0,8}(?:ทุกคืน|ทุกวัน|ประจำ|ตลอด)?[^\n]{0,40}?(?:ตื่น|ง่วง|ไม่สดชื่น|พลาด|ทำงาน|เรียน|ไม่มีแรง)"),
        "en": _rx(r"\b(?:sleep|go to bed|fall asleep)\b[^\n]{0,15}?\b(?:at )?(?:[2-5] ?am|really late)\b[^\n]{0,60}?\b(?:tired|groggy|mistakes|work|exhausted)\b"),
        "no": _rx(r"นอนไม่หลับ|หลับไม่ได้|\binsomnia\b|\bcan'?t sleep\b"),
        "th_d": {
            "vega": 'ตัวแปรหลักคือเวลาตื่น ไม่ใช่เวลานอน — ล็อกตัวที่ควบคุมได้ก่อน ตัวที่เหลือจะปรับตาม และต้นทุนที่จ่ายอยู่ตอนนี้คือความผิดพลาดในงาน',
            "open": ["ถ้าหลับได้แต่ไปนอนดึกเอง ปัญหามักไม่ใช่การนอน แต่คือช่วงก่อนนอนเป็นเวลาเดียวที่รู้สึกเป็นของตัวเอง "
                     "— ร่างกายจึงยอมแลกการนอนกับเวลาส่วนตัว และงานที่พลาดบ่อยคือราคาที่จ่ายอยู่"],
            "paths": [
                "ล็อกเวลาตื่นให้เท่ากันทุกวันรวมวันหยุด แล้วค่อยเลื่อนเวลานอนเร็วขึ้นทีละ 15–30 นาทีต่อสัปดาห์ "
                "— เวลาตื่นที่คงที่ดึงนาฬิการ่างกายได้ดีกว่าการบังคับตัวเองให้นอนเร็ว",
                "หาเวลาส่วนตัวให้ตอนกลางวันหรือหัวค่ำแทน 30 นาที (ดูซีรีส์ เล่นเกม เดินเล่น) "
                "— ถ้าไม่มีช่วงนั้น สมองจะทวงคืนตอนตีสองเสมอ",
                "ชั่วโมงสุดท้ายก่อนนอน: วางมือถือไว้นอกห้องหรือไกลมือ หรี่ไฟ และไม่ดื่มกาแฟหลังบ่ายสอง",
            ],
            "ask": "ช่วงก่อนนอนที่ลากไปถึงตีสาม ส่วนใหญ่คุณทำอะไรอยู่ และรู้สึกยังไงตอนนั้น?",
        },
        "en_d": {
            "vega": "The main variable is wake-up time, not bedtime — lock the one you can control and the rest follows. The cost you're paying now is mistakes at work.",
            "open": ["If you can fall asleep but keep going to bed late, the issue usually isn't sleep — it's that late night is the "
                     "only time that feels like yours. So you trade sleep for it, and the mistakes at work are the price."],
            "paths": [
                "Fix your wake-up time every day, weekends included, then bring bedtime earlier by 15–30 minutes a week. "
                "A steady wake time resets your body clock better than forcing an early night.",
                "Give yourself 30 minutes of your own time earlier in the evening (a show, a game, a walk) — "
                "if you don't, your brain takes it back at 2 a.m.",
                "Last hour before bed: phone out of reach, lights low, and no coffee after 2 p.m.",
            ],
            "ask": "What are you usually doing in those late hours, and how do you feel then?",
        },
    },
    # ── ผ่อนรถค้างงวด ────────────────────────────────────────────────
    {
        "key": "car_arrears",
        "verdict": ('ติดต่อไฟแนนซ์ก่อนค้างงวดถัดไป', 'Contact the lender before the next missed payment'),   # เรื่องนี้เป็นสถานการณ์ ไม่ใช่การตัดสินใจ — มติสภาไม่ใช่ "เดินหน้า/ชะลอ"
        "th": _rx(r"(?:(?:ผ่อน|ค่างวด|งวด|ไฟแนนซ์|ส่ง)\S{0,2}(?:รถ|มอเตอร์ไซค์|มอไซค์|มอไซ))\S{0,12}(?:ไม่ไหว|ค้าง|ขาดส่ง|ผิดนัด|ไม่ได้จ่าย|จะโดนยึด|โดนยึด)"
                  r"|รถ\S{0,8}(?:จะโดนยึด|โดนยึด|ถูกยึด)|ยึดรถ"
                  r"|ค้าง(?:ค่า)?งวดรถ|ขาดส่งรถ"),
        "en": _rx(r"\b(?:car|auto|vehicle|motorbike|motorcycle) (?:loan|payments?|finance)\b[^\n]{0,40}?\b(?:behind|missed|can'?t (?:pay|afford)|repossess)"),
        "no": None,
        "th_d": {
            "vega": 'เส้นตายของเรื่องนี้คืองวดที่ 3 — ก่อนถึงจุดนั้นคุณยังต่อรองได้ หลังจากนั้นไฟแนนซ์เป็นฝ่ายกำหนด ทางที่เสียน้อยที่สุดคือเจรจาหรือขายเองก่อนถูกยึด',
            "open": ["หนี้รถต่างจากหนี้อื่นตรงที่มีรถเป็นประกัน — ถ้าค้าง 3 งวดติด ไฟแนนซ์มีสิทธิ์บอกเลิกสัญญาและยึดรถได้ "
                     "แล้วยังตามเก็บส่วนต่างที่ขายทอดตลาดไม่พอ ตอนค้าง 2 งวดจึงยังมีทางเลือกมากที่สุด"],
            "paths": [
                "โทรหาไฟแนนซ์ก่อนครบงวดที่ 3: ขอพักชำระ ขยายงวดให้ค่างวดลดลง หรือปรับโครงสร้างหนี้ "
                "— การติดต่อก่อนทำให้มีอำนาจต่อรองมากกว่าตอนถูกตาม",
                "ถ้าคิดแล้วรถคันนี้แพงเกินชีวิตตอนนี้ การขายเองหรือขายดาวน์ให้คนรับช่วงอย่างถูกต้อง (โอนสัญญาผ่านไฟแนนซ์) "
                "มักได้เงินมากกว่าปล่อยให้ยึดไปประมูล",
                "ถ้าถูกยึดแล้วถูกเรียกเก็บส่วนต่าง อย่าเพิ่งเซ็นยอมรับยอด ขอเอกสารราคาประมูลก่อน "
                "· ปรึกษาฟรีได้ที่ สคบ. 1166 หรือคลินิกแก้หนี้",
            ],
            "ask": "รถคันนี้จำเป็นต่อการหาเงินไหม (ใช้ทำงาน) และยอดผ่อนต่อเดือนเท่าไรเทียบกับรายได้?",
        },
        "en_d": {
            "vega": 'The deadline is the next missed payment or two — before that you can negotiate, after it the lender decides. The least-loss route is negotiating or selling before repossession.',
            "open": ["A car loan is different from other debt because the car is the collateral. After a few missed payments the lender "
                     "can repossess it and still chase you for any shortfall at auction — so right now, two payments behind, is when you have the most options."],
            "paths": [
                "Call the lender before you miss another payment: ask for a payment holiday, a longer term with lower instalments, "
                "or a restructure. Calling first gives you more leverage than being chased.",
                "If the car costs more than your life can carry right now, selling it yourself (or a proper transfer of the loan) "
                "usually leaves you better off than repossession and auction.",
                "If it's repossessed and you're billed a shortfall, don't accept the figure until you've seen the auction documents; "
                "get free debt advice locally.",
            ],
            "ask": "Do you need the car to earn money, and how big is the monthly payment compared with your income?",
        },
    },
    # ── เรียนต่อคุ้มไหม ──────────────────────────────────────────────
    {
        "key": "study_decision",
        "th": _rx(r"(?:ป\.?\s?โท|ปริญญาโท|ป\.?\s?เอก|ปริญญาเอก|MBA|เรียนต่อ(?:ป|ปริญญา)\S{0,4})[^\n]{0,40}?"
                  r"(?:คุ้ม|กลัว|เสียเวลา|ไม่แน่ใจ|ดีไหม|ดีมั้ย|ควรไหม|ลังเล|อายุ|เงินเดือน|แพง)"),
        "en": _rx(r"\b(?:master'?s|masters|mba|phd|grad(?:uate)? school)\b[^\n]{0,40}?\b(?:worth it|waste|not sure|should i|afraid|too old|cost)\b"),
        "no": None,
        "th_d": {
            "vega": 'วิเคราะห์เป็นการลงทุน: ต้นทุนคือค่าเรียนบวกรายได้ที่เสียไป ผลตอบแทนคือประตูที่เปิดเพิ่ม — ถ้าระบุประตูนั้นไม่ได้ ผลตอบแทนเป็นศูนย์',
            "open": ["คำถามจริงไม่ใช่ \"เสียเวลาสองปีไหม\" แต่คือ \"ปริญญานี้เปิดประตูบานไหนที่ตอนนี้ปิดอยู่\" "
                     "— ถ้าตอบไม่ได้ สองปีนั้นแพง ถ้าตอบได้ชัด สองปีนั้นคือทางลัด"],
            "paths": [
                "เขียนงานหรือตำแหน่งที่อยากได้ใน 5 ปี แล้วเปิดประกาศรับสมัครจริง 10 ประกาศ "
                "— นับว่ากี่ประกาศต้องการ ป.โท ตัวเลขนี้ตอบได้ดีกว่าความรู้สึก",
                "คิดต้นทุนครบ: ค่าเรียน + รายได้ที่หายไปถ้าลาออกไปเรียน เทียบกับเงินเดือนที่น่าจะเพิ่ม "
                "— และดูทางที่ไม่ต้องหยุดงาน เช่น ภาคพิเศษ เรียนออนไลน์ หรือทุนจากที่ทำงาน",
                "คุยกับคนที่เรียนหลักสูตรนั้นจบแล้ว 2 คน ถามว่า \"ถ้าย้อนได้จะเรียนอีกไหม เพราะอะไร\"",
            ],
            "ask": "ถ้าเรียนจบแล้ว คุณอยากทำงานอะไรที่ตอนนี้ยังทำไม่ได้?",
        },
        "en_d": {
            "vega": "Treat it as an investment: cost is fees plus lost income; return is the doors it opens. If you can't name the door, the return is zero.",
            "open": ["The real question isn't \"is two years a waste?\" — it's \"which door does this degree open that's closed to me now?\" "
                     "If you can't name it, two years is expensive. If you can, it's a shortcut."],
            "paths": [
                "Write down the role you want in five years and open ten real job ads for it. Count how many require the degree — "
                "that number answers better than a feeling.",
                "Add up the full cost: fees plus lost income if you stop working, against the likely pay rise. Look at options that "
                "don't stop your income — part-time, online, or employer-funded.",
                "Talk to two people who finished that programme and ask: \"Would you do it again? Why?\"",
            ],
            "ask": "Once you've graduated, what work do you want to do that you can't do now?",
        },
    },
    # ── ออกไปทำเอง/ฟรีแลนซ์ ────────────────────────────────────────────
    {
        "key": "go_independent",
        "th": _rx(r"(?:ลาออก|ออกจากงาน(?:ประจำ)?)\S{0,10}(?:ไป|มา)?(?:เป็น|ทำ)(?:ฟรีแลนซ์|ฟรีแลนซ์|ธุรกิจ(?:ของ)?ตัวเอง|งานอิสระ|กิจการ|ร้าน(?:ของ)?ตัวเอง|เอง)"
                  r"|อยากเป็นฟรีแลนซ์|ออกมาทำเอง"),
        "en": _rx(r"\b(?:quit|leave) my (?:job|day job|9-?to-?5)\b[^\n]{0,30}?\b(?:to )?(?:go freelance|freelance|start (?:my own|a) business|work for myself)\b"),
        "no": None,
        "th_d": {
            "vega": 'ตัวแปรที่ตัดสินคือความผันผวนของรายได้ ไม่ใช่ค่าเฉลี่ย — วัดจากเดือนที่แย่ที่สุด แล้วถามว่าเงินสำรองรองรับได้กี่เดือน ถ้ายังไม่มีลูกค้าที่จ่ายจริง อย่าเพิ่งตัดรายได้ประจำ',
            "open": ["การออกไปทำเองไม่ได้เสี่ยงเพราะรายได้น้อยลง แต่เสี่ยงเพราะรายได้ไม่แน่นอน "
                     "— คำถามที่ต้องตอบได้ก่อนลาออกคือ \"ถ้าเดือนไหนไม่มีงานเลย ฉันอยู่ได้กี่เดือน\""],
            "paths": [
                "ทดลองก่อนกระโดด: รับงานฟรีแลนซ์ช่วงเย็นหรือวันหยุด 3 เดือน จนมีรายได้นอกงานประจำต่อเนื่อง "
                "อย่างน้อยครึ่งหนึ่งของเงินเดือน — ถ้าทำไม่ได้ตอนมีเงินเดือนรองรับ ตอนไม่มีจะยากกว่า",
                "เก็บเงินสำรองให้ได้ 6 เดือนของค่าใช้จ่าย (ไม่ใช่ของเงินเดือน) และคิดสิ่งที่งานประจำเคยจ่ายแทน "
                "— ประกันสังคม (สมัครมาตรา 39 ต่อได้) ประกันสุขภาพ ภาษี",
                "มีลูกค้าที่จ่ายเงินแล้วอย่างน้อย 2–3 ราย ก่อนยื่นใบลาออก — คำว่า \"สนใจ\" ยังไม่ใช่รายได้",
            ],
            "ask": "ตอนนี้มีลูกค้าหรือรายได้จากงานอิสระแล้วหรือยัง และค่าใช้จ่ายจริงต่อเดือนของคุณเท่าไร?",
        },
        "en_d": {
            "vega": "The deciding variable is income volatility, not the average. Plan for the worst month and how many months your reserve covers. Without paying clients, don't cut your steady income yet.",
            "open": ["Going independent isn't risky because you'll earn less — it's risky because income becomes uneven. "
                     "The question to answer before quitting: \"if I get no work for a month, how many months can I last?\""],
            "paths": [
                "Test before you jump: freelance evenings and weekends for three months until side income reliably reaches "
                "at least half your salary. If you can't do it with a salary behind you, it's harder without one.",
                "Save six months of expenses (not salary), and price what your employer used to cover — health insurance, "
                "pension or social security contributions, tax.",
                "Have at least two or three paying clients before you resign — \"interested\" isn't income.",
            ],
            "ask": "Do you already have paying clients, and what do you actually spend each month?",
        },
    },
    # ── เลือกระหว่างสองคน ─────────────────────────────────────────────
    {
        "key": "choose_two",
        "th": _rx(r"(?:มีคน(?:มา)?จีบ|คุยอยู่|ชอบ)\S{0,6}(?:สอง|2)\s?คน[^\n]{0,30}?(?:เลือก|ใคร|ไม่รู้)|เลือกระหว่าง\S{0,20}(?:สอง|2)\s?คน|ไม่รู้จะเลือกใคร"),
        "en": _rx(r"\b(?:torn|choose|choosing|pick) between two (?:guys|girls|people|men|women)\b|\btwo (?:guys|girls|people) (?:like|are into) me\b"),
        "no": None,
        "th_d": {
            "vega": 'ข้อมูลยังไม่พอจะตัดสิน — ช่วงเริ่มต้นทุกคนแสดงด้านดี ตัววัดที่เชื่อถือได้คือพฤติกรรมตอนมีแรงกดดัน และความสม่ำเสมอระหว่างคำพูดกับการกระทำ',
            "open": ["ตอนนี้คุณยังไม่ต้องเลือกใคร ต้องรู้ก่อนว่าตัวเองต้องการชีวิตคู่แบบไหน "
                     "— เพราะถ้าเลือกจากความรู้สึกช่วงเริ่ม ทั้งสองคนจะดูดีพอๆ กัน ความต่างจริงเห็นตอนเรื่องยาก"],
            "paths": [
                "เขียน 3 อย่างที่ขาดไม่ได้ในคนที่จะอยู่ด้วยยาว (เช่น พูดตรง รับผิดชอบเงิน เคารพครอบครัว) แล้วดูว่าใครมีจริง "
                "จากสิ่งที่ทำ ไม่ใช่สิ่งที่พูด",
                "สังเกตตัวเองตอนอยู่กับแต่ละคน: สบายใจ เป็นตัวเองได้ หรือต้องคอยระวัง — ความรู้สึกนี้บอกอนาคตได้ดีกว่าความตื่นเต้น",
                "ซื่อตรงกับทั้งคู่ระหว่างคิด ไม่ต้องรีบผูกมัด แต่อย่าให้ความหวังเกินที่ตั้งใจจริง",
            ],
            "ask": "อยู่กับคนไหนแล้วคุณเป็นตัวเองได้มากกว่ากัน?",
        },
        "en_d": {
            "vega": "There isn't enough data to decide yet — early on everyone shows their best side. The reliable signals are behaviour under pressure and consistency between words and actions.",
            "open": ["You don't need to choose a person yet — you need to know what kind of partnership you want. "
                     "Early on, both will seem equally good; the real differences show when things get hard."],
            "paths": [
                "Write the three things you can't do without in a long-term partner (honesty, money sense, respect for family…) "
                "and check who shows them in what they do, not what they say.",
                "Notice how you feel with each: at ease and yourself, or on guard. That predicts the future better than excitement.",
                "Be honest with both while you think — no need to rush, but don't promise more than you mean.",
            ],
            "ask": "With which of them can you be more yourself?",
        },
    },
    # ── สตาร์ทอัพเงินใกล้หมด ─────────────────────────────────────────
    {
        "key": "runway",
        "th": _rx(r"(?:สตาร์ทอัพ|สตาร์ตอัพ|บริษัท|ธุรกิจ)[^\n]{0,30}?(?:เงินเหลือ|เงินพอ|อยู่ได้)(?:อีก)?\s?\d+\s?เดือน[^\n]{0,40}?(?:นักลงทุน|ระดมทุน|VC|ไม่ตอบ|เงียบ)?"),
        "en": _rx(r"\b(?:startup|company|business)\b[^\n]{0,30}?\b\d+ months? of (?:runway|cash)\b|\brunway\b[^\n]{0,40}?\binvestors?\b"),
        "no": None,
        "th_d": {
            "vega": 'สมการคือ เวลาที่เหลือ ต้องมากกว่า เวลาที่ใช้ระดมทุน (3–6 เดือน) — ถ้าไม่ใช่ ต้องเพิ่มเวลาด้วยการลดค่าใช้จ่ายหรือหารายได้ตอนนี้ ไม่ใช่รอ',
            "open": ["เงินที่เหลือไม่กี่เดือนกับนักลงทุนที่เงียบ บอกว่าต้องเปลี่ยนจาก \"รอเงินใหม่\" เป็น \"ทำให้ไม่ต้องรอ\" "
                     "— เพราะการระดมทุนใช้เวลา 3–6 เดือน ถ้าเริ่มลดค่าใช้จ่ายตอนเหลือเดือนเดียว จะไม่มีทางเลือกเหลือ"],
            "paths": [
                "ทำตัวเลข 3 แบบวันนี้: ไม่ทำอะไร · ลดค่าใช้จ่าย 30% · ลดจนถึงจุดคุ้มทุน แล้วดูว่าแต่ละแบบอยู่ได้กี่เดือน",
                "หาเงินจากลูกค้าก่อนนักลงทุน: เก็บเงินล่วงหน้า ขายแพ็กเกจรายปี หรือรับงานที่ใกล้กับสินค้า — รายได้ซื้อเวลาได้โดยไม่เสียหุ้น",
                "ส่งอัปเดตสั้นๆ ให้นักลงทุนเดิมทุกคน: ตัวเลขจริง สิ่งที่เรียนรู้ และสิ่งที่ต้องการ — คนที่ลงไปแล้วมักช่วยต่อ (bridge) เร็วกว่าคนใหม่",
            ],
            "ask": "ถ้าลดค่าใช้จ่ายถึงจุดที่รายได้ตอนนี้จ่ายไหว ต้องตัดอะไรบ้าง?",
        },
        "en_d": {
            "vega": "The equation: runway must exceed fundraising time (3–6 months). If it doesn't, buy time now by cutting costs or earning revenue — not by waiting.",
            "open": ["A few months of runway and quiet investors means switching from \"waiting for new money\" to \"not needing it\". "
                     "Fundraising takes 3–6 months — if you only cut costs with one month left, you'll have no options."],
            "paths": [
                "Model three scenarios today: change nothing · cut costs 30% · cut to break-even. See how many months each buys.",
                "Get money from customers before investors: prepayments, annual plans, or paid work close to your product. "
                "Revenue buys time without dilution.",
                "Send every existing investor a short update — real numbers, what you've learned, what you need. "
                "Insiders often bridge faster than new investors decide.",
            ],
            "ask": "What would you have to cut to reach the point where current revenue covers your costs?",
        },
    },
]

# ชุดที่ 2 จากคลังปัญหา 394 เรื่อง (core/problem_lens_more.py) — ต่อท้าย เลนส์ชุดแรกที่เจาะจงกว่าได้ก่อน
from core.problem_lens_more import LENSES_MORE  # noqa: E402

LENSES += LENSES_MORE
_BY_KEY = {L["key"]: L for L in LENSES}


def find(text: str, lang: str = "th", voice: str = "lyla"):
    """คืนเลนส์ที่ตรงกับเรื่อง (dict ของภาษานั้น: open · paths · ask · vega) หรือ None

    น้ำเสียงต่างกันตั้งแต่ประโยคแรก: LYLA เปิดด้วยการเข้าใจคน (ปัญหาของใคร รู้สึกอย่างไร เพราะอะไร)
    VEGA เปิดด้วยโครงสร้างของปัญหา (ตัวแปรที่ตัดสิน · จุดที่ย้อนกลับไม่ได้) — ขั้นตอนเหมือนกัน เพราะข้อเท็จจริงไม่เปลี่ยนตามคนพูด
    """
    if not text:
        return None
    t = str(text)
    for L in LENSES:
        rx = L.get("en" if lang == "en" else "th")
        if rx is None or not rx.search(t):
            continue
        if L.get("no") is not None and L["no"].search(t):
            continue
        if ("en_d" if lang == "en" else "th_d") not in L:
            continue
        d = dict(L["en_d" if lang == "en" else "th_d"], key=L["key"])
        if L.get("verdict"):
            d["verdict"] = L["verdict"][1 if lang == "en" else 0]
        if voice == "vega" and d.get("vega"):
            d["open"] = [d["vega"]]
        return d
    return None
