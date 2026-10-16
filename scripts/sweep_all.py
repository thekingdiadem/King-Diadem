"""
scripts/sweep_all.py — กวาดหาบั๊กทั้งชุดในคำสั่งเดียว (รวมตัวกวาดที่ใช้ไล่บั๊กรอบ PR #78–#83)

ห้าชุด:
  urgent   ผู้ประสบเหตุ × อาการด่วน × สำนวน      → ต้องได้ Risk ≥ 60 และไม่ได้คำตอบทั่วไป
  violence ความรุนแรง ค้ามนุษย์ สุขภาพจิต (ไทย+อังกฤษ) → ต้องได้ Risk ≥ เกณฑ์ของแต่ละเรื่อง
  benign   สำนวนชีวิตประจำวันที่มีคำน่ากลัว            → ต้องไม่เป็นวิกฤต และ Risk < 60
  typing   พิมพ์รีบ (ไม่มีวรรณยุกต์ เว้นวรรคทุกตัว แสลง) → ต้องยังได้ Risk ≥ 60
  followup ตอบสั้นๆ ต่อจากเรื่องด่วน (ผ่าน API จริง)   → ต้องยังได้เบอร์ช่วยเหลือของเรื่องเดิม
  intl     เรื่องด่วน + ประโยคธรรมดา ภาษาจีน ญี่ปุ่น เกาหลี สเปน → ด่วนต้อง ≥ 60 · ธรรมดาต้อง < 60
  en_crisis สำนวนความคิดอยากตายภาษาอังกฤษ (3,696) → ต้องเป็นวิกฤตหรือสัญญาณเตือน (≥ 65) · สำนวนธรรมดาต้อง < 60
  th_crisis สำนวนความคิดอยากตายภาษาไทย (5,250) → ต้องเป็นวิกฤตหรือสัญญาณเตือน (≥ 65) · สำนวนธรรมดาต้อง < 60
  th_violence ใครทำร้าย × การกระทำ × สำนวน ภาษาไทย (10,080) → ต้อง Risk ≥ 60 · กฎบ้าน/เล่นกันต้อง < 60
  en_violence ใครทำร้าย × การกระทำ × สำนวน ภาษาอังกฤษ (10,200) → ต้อง Risk ≥ 60 · สำนวนธรรมดาต้อง < 60
  en       ผู้ประสบเหตุ × อาการด่วน × สำนวน ภาษาอังกฤษ + สำนวนธรรมดา → ด่วนต้อง ≥ 60 ไม่ได้คำตอบทั่วไป · ธรรมดาต้อง < 60

รัน:  python scripts/sweep_all.py                  → ทุกชุด เต็มจำนวน (~1 นาที + followup)
      python scripts/sweep_all.py urgent benign    → เฉพาะชุดที่เลือก
      python scripts/sweep_all.py --sample 800     → สุ่มชุดละ 800 ข้อความ (tests/test_sweep_all.py ใช้แบบนี้)
ออกด้วย exit 1 ถ้ามีข้อความหลุด
"""
import itertools
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.kernel_voice import assess, compose  # noqa: E402

GENERIC = ("เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว", "ถ้าอาการแย่ลงเร็ว มีไข้สูงไม่ลด", "ให้เวลาตัวเอง 24–72 ชั่วโมง",
           "Write what happened in one sentence")

# ── urgent ──────────────────────────────────────────────────────
URGENT_WHO = ["", "ลูก", "แม่", "พ่อ", "ยาย", "ตา", "เพื่อน", "สามี", "แฟน", "น้อง", "หลาน", "ทารก", "คนข้างบ้าน", "ฉัน", "ผม", "หนู"]
# (เหตุการณ์, ระดับขั้นต่ำที่คาด) — ทุกอันควรได้ Risk ≥ 60
URGENT_EVENTS = [
 "หมดสติ", "ไม่หายใจ", "หัวใจหยุดเต้น", "จมน้ำ", "ตกน้ำ", "ชัก", "ชักไม่หยุด", "เจ็บหน้าอกมาก", "หายใจไม่ออก",
 "ปากเบี้ยว พูดไม่ชัด", "แขนขาอ่อนแรงข้างเดียว", "เลือดออกไม่หยุด", "เลือดพุ่ง", "เลือดกำเดาไหลไม่หยุด",
 "อาเจียนเป็นเลือด", "ไอเป็นเลือด", "ถ่ายเป็นเลือด", "ถ่ายดำ", "กินยาเกินขนาด", "กินยาไปทั้งแผง", "กินยาฆ่าหญ้า",
 "กินน้ำยาล้างห้องน้ำ", "กลืนถ่านกระดุม", "กลืนเหรียญ", "โดนงูกัด", "โดนหมากัด", "โดนผึ้งต่อยหน้าบวม",
 "กินถั่วแล้วปากบวม", "กินกุ้งแล้วหายใจลำบาก", "แพ้ยาหน้าบวม", "โดนไฟช็อต", "โดนน้ำร้อนลวก", "ไฟไหม้ตัว",
 "นิ้วขาด", "กระดูกหัก", "กระดูกโผล่", "หัวฟาดพื้นแล้วอาเจียน", "ตกบันได", "ถูกรถชน", "รถคว่ำ",
 "ตาโดนสารเคมี", "น้ำยาเข้าตา", "ปูนเข้าตา", "เป็นลมแดด ตัวร้อนจัด", "สับสนกะทันหัน", "จำใครไม่ได้กะทันหัน",
 "ไข้สูง คอแข็ง", "ไข้สูงซึมมาก", "ปวดท้องขวาล่างมีไข้", "ตัวเหลืองมาก ไม่กินนม", "ท้องเสีย ปากแห้ง ไม่ฉี่",
 "ปวดหัวรุนแรงที่สุดในชีวิต", "น้ำตาลต่ำ หน้ามืด", "เมาจนปลุกไม่ตื่น", "เสพยาแล้วตัวร้อนชัก", "กินยาอีแล้วตัวร้อน",
 "ดมกลิ่นเครื่องปั่นไฟแล้วปวดหัว", "ถูกแทง", "ถูกยิง", "ถูกทำร้ายจนเลือดออก", "ถูกขังไว้", "ถูกข่มขืน",
 "ถูกบังคับให้มีเพศสัมพันธ์", "บอกว่าอยากตาย", "พูดว่าจะฆ่าตัวตาย", "กรีดแขนเลือดไม่หยุด",
]
URGENT_FRAME = ["{w}{e}", "{w}{e} ทำไงดี", "ช่วยด้วย {w}{e}", "ตอนนี้{w}{e}", "{w}เพิ่ง{e}", "{w}{e} ค่ะ", "{w}{e} ครับ",
         "{w}{e} ต้องไปโรงพยาบาลไหม", "ด่วน {w}{e}", "เมื่อกี้{w}{e}", "{w} {e}", "{w}{e}อยู่ ต้องทำยังไง"]

# ── violence ────────────────────────────────────────────────────
TH_WHO = ["", "ฉัน", "หนู", "ผม", "แม่", "พี่สาว", "เพื่อน", "ลูกสาว", "น้อง"]
TH = [  # (เหตุการณ์, risk ขั้นต่ำ)
 ("ถูกสามีตบ", 75), ("ถูกแฟนทุบตี", 75), ("โดนผัวกระทืบ", 75), ("ถูกแฟนบีบคอ", 75), ("ถูกพ่อเลี้ยงลวนลาม", 75),
 ("ถูกข่มขืน", 75), ("โดนแฟนบังคับมีเซ็กส์", 75), ("ถูกขังไว้ในห้อง", 75), ("ถูกนายจ้างขังไว้ในโรงงาน", 60),
 ("ถูกหลอกไปทำงานต่างประเทศแล้วถูกยึดพาสปอร์ต", 60), ("ถูกพาไปทำงานแก๊งคอลเซ็นเตอร์ที่กัมพูชา", 60),
 ("ถูกนายจ้างยึดพาสปอร์ต ไม่ให้ออกไปไหน", 60), ("ถูกขู่ฆ่า", 65), ("ถูกแฟนเก่าขู่จะฆ่า", 65),
 ("ถูกขู่จะปล่อยคลิป", 75), ("ถูกแบล็กเมล์ด้วยรูปโป๊", 75), ("โดนคอลเซ็นเตอร์หลอกโอนเงิน", 60),
 ("มีคนอ้างเป็นตำรวจให้โอนเงิน", 60), ("ถูกหลอกให้ลงทุนคริปโต", 60), ("อยากตาย", 85), ("อยากฆ่าตัวตาย", 85),
 ("ไม่อยากมีชีวิตอยู่แล้ว", 85), ("คิดจะกินยาให้ตาย", 85), ("เขียนจดหมายลาตายแล้ว", 85), ("กรีดข้อมือ", 75),
 ("ทำร้ายตัวเองทุกคืน", 75), ("ได้ยินเสียงสั่งให้ฆ่าคน", 75), ("อยากฆ่าแฟน", 75), ("มีปืนอยู่ในบ้าน อยากยิงตัวเอง", 85),
 ("หายออกจากบ้านไปสองวัน", 75), ("ไม่กินข้าวมาสามวัน อาเจียนทุกครั้งที่กิน", 60), ("ถูกครูลวนลาม", 75),
 ("ถูกเพื่อนรุมแกล้งจนไม่อยากไปโรงเรียน", 0), ("โดนบูลลี่ในเน็ตจนอยากตาย", 85),
]
TH_FRAME = ["ตอนนี้{w}กำลัง{e}", "{w}{e} ต้องแจ้งใคร", "{w}{e} ใครช่วยได้บ้าง", "ขอคำแนะนำ {w}{e}", "{w}{e} กลัวมาก", "{w}{e} อยู่คนเดียว", "{w}{e}",  "{w}{e} ทำไงดี", "ช่วยด้วย {w}{e}", "ตอนนี้{w}{e}", "{w}{e} ค่ะ", "{w}{e} ครับ", "{w}{e}มาหลายวันแล้ว",
            "{w}{e} ไม่รู้จะบอกใคร", "{w} {e}", "เมื่อคืน{w}{e}"]
EN_WHO = ["I", "my sister", "my friend", "my mom", "my daughter"]
EN = [("{w} was raped", 75), ("{w} was sexually assaulted", 75), ("{w} got beaten by her husband", 75),
      ("{w} is being choked by her boyfriend", 75), ("{w} is locked in a room", 75), ("{w} wants to die", 85),
      ("{w} wants to kill herself", 85), ("{w} took a whole bottle of pills", 85), ("{w} is cutting herself", 75),
      ("{w} is being blackmailed with nude photos", 75), ("{w} got scammed and sent money", 60),
      ("{w} is trafficked and her passport was taken", 60), ("{w} is hearing voices telling her to hurt people", 75),
      ("{w} is missing since yesterday", 75), ("{w} is being stalked by her ex", 60), ("{w} was threatened with a knife", 75),
      ("{w} has a plan to end my life", 85), ("{w} is drunk and wants to drive", 75), ("{w} sees things that aren't there", 60),
      ("{w} hasn't slept for 4 days", 40), ("{w} has an eating disorder", 60), ("{w} stopped taking antidepressants", 50), ("{w} can't stop vomiting blood", 85), ("{w} overdosed on heroin", 85)]
EN_FRAME = ["{x} and I'm scared", "{x}, who can help", "urgent: {x}", "{x}!!", "{x} right now", "{x}", "{x}, what do I do", "help {x}", "{x} please help", "{x}."]

# ── benign ──────────────────────────────────────────────────────
BENIGN_PRE = ["", "วันนี้", "เมื่อวาน", "555 ", "โห ", "เฮ้อ ", "จริงๆ แล้ว", "บอกเลยว่า", "ตอนนี้"]
BENIGN_CORE = [
 "หิวจะตาย", "ขำจนจะตาย", "ร้อนจะตาย", "เหนื่อยจะตาย", "เบื่อจะตาย", "ง่วงจะตาย", "ตายแน่ถ้าส่งงานไม่ทัน", "ตายละ ลืมการบ้าน",
 "ฆ่าเวลาด้วยการดูซีรีส์", "เล่นเกมยิงกันทั้งคืน", "ดูหนังสยองขวัญแล้วนอนไม่หลับ", "หนังเรื่องนี้ฉากคนจมน้ำน่ากลัวมาก",
 "อ่านข่าวคนถูกแทงแล้วสะเทือนใจ", "เป็นแฟนคลับวงนี้จนจะตาย", "กินเผ็ดจนน้ำตาไหล", "แพ้ทางคนพูดเพราะ", "แพ้กุ้งนิดหน่อยคันๆ",
 "เมื่อวานดูบอลแล้วโดนยิงประตู", "แทงหวยไม่ถูกอีกแล้ว", "ชักช้าจัง", "แม่ชักจะบ่น", "ชักชวนเพื่อนไปวิ่ง", "กระโดดเชือกทุกเช้า",
 "ซื้อยาพาราไว้ติดบ้าน", "กินยาแก้แพ้แล้วง่วง", "เจ็บคอนิดหน่อย", "ปวดหัวเพราะเครียดงาน", "อยากหายไปเที่ยวทะเล", "อยากหลับยาวๆ ในวันหยุด",
 "ไม่อยากอยู่บ้านเฉยๆ อยากไปเที่ยว", "ไม่อยากไปทำงานวันจันทร์", "งานนี้ฆ่าฉันแน่ๆ", "เพื่อนแกล้งแซวเรื่องแฟน", "โดนหัวหน้าดุนิดหน่อย",
 "ขับรถไปต่างจังหวัด", "ว่ายน้ำได้ 1 กิโล", "สอนลูกว่ายน้ำ", "ลูกเล่นน้ำในสระ", "ไปเที่ยวน้ำตก", "ทำกับข้าวโดนมีดบาดนิดเดียว",
 "ทาครีมกันแดดแล้วไม่ไหม้", "เลือดกำเดาไหลนิดหน่อยตอนอากาศแห้ง หยุดแล้ว", "ลูกไข้ต่ำๆ ยังเล่นได้", "ตกบันไดนิดเดียวไม่เป็นไร",
 "ทะเลาะกับแฟนเรื่องไปเที่ยว", "อยากเลิกกับแฟนแต่ยังไม่แน่ใจ", "อยากลาออกไปทำธุรกิจ", "อยากเก็บเงินซื้อบ้าน", "เงินเดือน 30000 อยากออมเงิน",
 "จะสอบพรุ่งนี้ ตื่นเต้น", "อยากเรียนต่อต่างประเทศ", "หมาที่บ้านน่ารัก", "แมวกัดเล่นไม่เข้าเนื้อ", "อยากฆ่ายุงในห้อง", "ฆ่าเชื้อโรคในบ้านยังไงดี",
 "I'm dying to see the new movie", "this homework is killing me", "I could kill for a pizza", "lol I'm dead", "my boss will kill me if I'm late",
 "I shot a great photo today", "we drowned in paperwork", "I'm starving", "the gym is killing me", "I'm so bored I could die",
]
BENIGN_POST = ["", " 555", " ค่ะ", " ครับ", " 😂", " 🥲", " นะ", " อะ", " lol", "!!", " ทำไงดี"]

# ── typing ──────────────────────────────────────────────────────
TYPO_BASE = ["อยากตาย", "อยากฆ่าตัวตาย", "ไม่อยากมีชีวิตอยู่แล้ว", "คิดจะกินยาให้ตาย", "ลูกไม่หายใจ", "แม่หมดสติ", "ลูกตกน้ำ", "พ่อเจ็บหน้าอก",
        "ลูกชัก", "ถูกแทง", "ถูกสามีตบ", "ถูกข่มขืน", "โดนงูกัด", "ลูกกินยาไปทั้งแผง", "ลูกกลืนถ่านกระดุม", "ยายปากเบี้ยว พูดไม่ชัด",
        "เลือดออกไม่หยุด", "ถูกขังไว้ในห้อง", "มีคนขู่จะฆ่า", "เพื่อนบอกว่าจะฆ่าตัวตาย", "โดนแบล็กเมล์ด้วยคลิป", "ลูกหายไปตั้งแต่เมื่อวาน"]
TONES = "่้๊๋"


def mut(t, random=random):
    k = random.random()
    if k < 0.2: return "".join(c for c in t if c not in TONES)               # ไม่มีวรรณยุกต์
    if k < 0.35: return t + t[-1] * random.randint(2, 6)                     # ตัวซ้ำท้าย
    if k < 0.5: return t.replace(" ", "")                                     # ไม่มีวรรค
    if k < 0.6: return " ".join(t)                                            # เว้นทุกตัว
    if k < 0.7: return random.choice(["ช่วยด้วยยยย ", "ด่วนนนน ", "ฮือออ ", "help "]) + t
    if k < 0.8: return t + random.choice(["!!!", "...", " 😭😭", " T_T", " ค่ะะะ", " คับ", " จ้า", " อ่ะ"])
    if k < 0.9: return t.replace("ไม่", "ม่").replace("อยาก", "อยาก")      # แสลง
    return t.replace("ตาย", "ตายยย").replace("ลูก", "ลุก")                   # สะกดผิด


# ── intl ────────────────────────────────────────────────────────
INTL_URGENT = {
    "zh": ["我不想活了", "我妈妈晕倒了", "孩子吞了硬币", "我被老公打了", "我朋友想自杀", "有人要杀我", "我被骗了转账",
           "孩子发高烧抽搐", "我喝了农药", "我好饿，三天没吃饭", "他说要杀了我", "我被关在房间里", "地震了"],
    "ja": ["死にたい", "母が倒れた", "子供が電池を飲み込んだ", "夫に殴られた", "友達が死にたいと言っている", "殺すと脅された",
           "詐欺にあった", "子供が高熱でけいれん", "三日間何も食べていない", "部屋に閉じ込められている", "火事だ"],
    "ko": ["죽고 싶어", "엄마가 쓰러졌어요", "아이가 동전을 삼켰어요", "남편한테 맞았어요", "친구가 자살하고 싶대요",
           "죽인다고 협박받았어요", "사기 당했어요", "아이가 고열로 경련", "사흘 동안 아무것도 못 먹었어요", "방에 갇혀 있어요", "지진이 났어요"],
    "es": ["quiero morir", "mi madre se desmayó", "mi hijo se tragó una moneda", "mi esposo me pegó", "mi amiga quiere suicidarse",
           "me amenazaron de muerte", "me estafaron", "mi hijo tiene fiebre y convulsiones", "no he comido en tres días",
           "estoy encerrada en un cuarto", "hay un incendio"],
}
INTL_CALM = ["我饿了", "好久没吃火锅了", "三天没吃火锅了", "我被老师骂了", "死ぬほど笑った", "お腹すいた", "ゲームで殺された",
             "배고파", "오늘 너무 웃겨 죽겠어", "게임에서 죽었어", "tengo hambre", "me muero de risa", "me encerré en mi cuarto a estudiar"]
INTL_TAILS = ["", "！", "。", " 😭", "!!", " ...", "？"]


def intl(n=0):
    urgent_cases = [t + tail for xs in INTL_URGENT.values() for t in xs for tail in INTL_TAILS]
    calm_cases = [t + tail for t in INTL_CALM for tail in INTL_TAILS]
    bad = [t for t in urgent_cases if assess(t)["text_risk"] < 60]
    bad += [f"(ธรรมดา) {t}" for t in calm_cases if assess(t)["text_risk"] >= 60 or assess(t)["crisis"]]
    return len(urgent_cases) + len(calm_cases), bad


# ── en ──────────────────────────────────────────────────────────
EN_URG_WHO = ["my son", "my daughter", "my mom", "my dad", "my friend", "my husband", "my wife", "my baby", "my grandma", "someone", "a kid"]
EN_URG_EVENTS = ["is not breathing", "collapsed", "is unconscious", "is having a seizure", "is drowning", "fell in the pool",
      "has chest pain", "can't breathe", "is choking", "is bleeding a lot", "won't stop bleeding", "cut off a finger",
      "broke his leg", "hit his head and is vomiting", "swallowed a battery", "swallowed a coin", "drank bleach",
      "took too many pills", "overdosed", "ate rat poison", "was bitten by a snake", "was stung by a bee and his face is swelling",
      "ate peanuts and can't breathe", "got burned with boiling water", "got electrocuted", "has a high fever and a stiff neck",
      "has slurred speech", "has a drooping face", "is confused suddenly", "has heatstroke", "is vomiting blood",
      "was stabbed", "was shot", "was hit by a car", "is missing", "got chemicals in the eye", "is very drunk and won't wake up"]
EN_URG_FRAME = ["{w} {e}", "help {w} {e}", "{w} {e}, what do I do", "{w} {e} right now", "urgent: {w} {e}", "{w} {e}!!"]
EN_CALM = ["I burned my toast lol", "burned my dinner again", "I'm dying to see the new movie", "this homework is killing me",
           "I could kill for a pizza", "lol I'm dead", "I shot a great photo today", "we drowned in paperwork", "the gym is killing me",
           "my phone is dead", "my plant is dying", "I fell in love", "she cut off contact with me", "he's bleeding money on that car",
           "my son is drowning in homework", "my dad hit his head on the cabinet lol he's fine", "I'm so bored I could die",
           "I can't go on with this project", "I want to disappear for a weekend trip", "end it all with a bang at the party",
           "tonight is my last night in Bangkok", "I'm going to jump off the diving board", "I bought a rope for camping"]
# สัญญาณเตือนที่ไม่มีคำว่า die/suicide — ต้องเป็นวิกฤต
EN_WARNING = ["I wrote my goodbye letters", "I'm going to jump off the bridge tonight", "I wish I could sleep and never wake up",
              "I've been stockpiling my pills", "I'm going to overdose tonight", "I've given away my stuff", "tonight is my last night",
              "I just want the pain to stop forever", "I want to end it all", "I have a plan to end my life", "I'm going to kill myself"]


def en(n=0):
    cases = sorted({f.format(w=w, e=e).replace(" his ", " his " if w in ("my son", "my dad", "my husband", "someone", "a kid", "my baby", "my friend") else " her ")
                    for w, e, f in itertools.product(EN_URG_WHO, EN_URG_EVENTS, EN_URG_FRAME)} - {f.format(w="someone", e="is missing") for f in EN_URG_FRAME})
    cases = _sample(cases, n, 6)
    bad = [t for t in cases if assess(t)["text_risk"] < 60 or "Write what happened in one sentence" in compose(t)]
    bad += [f"(ธรรมดา) {t}" for t in EN_CALM if assess(t)["text_risk"] >= 60 or assess(t)["crisis"]]
    bad += [f"(สัญญาณเตือน) {t}" for t in EN_WARNING if not assess(t)["crisis"]]
    return len(cases) + len(EN_CALM) + len(EN_WARNING), bad


# ── en_crisis ───────────────────────────────────────────────────
ENC_PRE = ["", "honestly ", "i think ", "lately ", "tbh ", "i lost my job and ", "my girlfriend left and ", "i'm so tired, ", "nobody cares, ", "after everything, ", "i'm drowning in debt and "]
ENC_CORE = ["I want to die", "I want to kill myself", "I don't want to live anymore", "I want to end my life", "I'm going to end it tonight",
        "I wish I was dead", "I'd be better off dead", "everyone would be better off without me", "I can't keep living like this",
        "I have a plan to kill myself", "I bought pills to end it", "I'm thinking about suicide", "I keep cutting myself",
        "I want to disappear forever", "there's no point in living", "I wrote a suicide note",
        "I'm going to jump", "I don't want to wake up tomorrow", "life isn't worth it anymore", "I'm done with life",
        "I just want it all to stop", "I'm saying goodbye to everyone", "I'm a burden", "nobody would care if I died"]
ENC_POST = ["", ".", "...", " :(", " lol", " for real", " tonight", " please help", " i mean it", " idk what to do", " anymore", " 😢", " honestly", " again"]
ENC_CALM = ["I'm done with life drawing class", "I just want it all to stop raining", "I'm saying goodbye to everyone at the office party",
            "I'm going to jump into the pool", "I'm going to jump on that offer", "I don't want to wake up tomorrow early",
            "I'm ready to go", "life isn't worth living without coffee lol"]


def en_crisis(n=0):
    cases = _sample(sorted({(p + c + q).strip() for p, c, q in itertools.product(ENC_PRE, ENC_CORE, ENC_POST)}), n, 10)
    bad = []
    for t in cases:
        a = assess(t)
        if not a["crisis"] and a["text_risk"] < 65:
            bad.append(t)
    bad += [f"(ธรรมดา) {t}" for t in ENC_CALM if assess(t)["text_risk"] >= 60 or assess(t)["crisis"]]
    return len(cases) + len(ENC_CALM), bad


# ── th_crisis ───────────────────────────────────────────────────
THC_PRE = ["", "หนู", "ฉัน", "ผม", "เรา", "กู", "พี่", "ตอนนี้", "เหนื่อยมาก ", "ไม่ไหวแล้ว ", "แฟนทิ้ง ", "หนี้เยอะมาก ", "ตกงาน ", "ทะเลาะกับที่บ้าน "]
THC_CORE = ["อยากตาย", "อยากฆ่าตัวตาย", "ไม่อยากมีชีวิตอยู่", "ไม่อยากอยู่แล้ว", "อยากหายไปจากโลกนี้", "อยากจบชีวิต", "อยากหลับแล้วไม่ตื่น",
        "คิดจะกินยาให้ตาย", "คิดจะกระโดดตึก", "อยากแขวนคอ", "เตรียมเชือกไว้แล้ว", "ซื้อยามาเก็บไว้แล้ว", "เขียนจดหมายลาไว้แล้ว",
        "กรีดแขนอีกแล้ว", "ทำร้ายตัวเองทุกคืน", "อยู่ไปก็เป็นภาระ", "ไม่มีใครต้องการ ตายไปคงดีกว่า", "มีชีวิตอยู่ไปทำไม",
        "ไม่เห็นทางออกแล้ว", "คืนนี้คงเป็นคืนสุดท้าย", "อยากไปให้พ้นๆ จากโลกนี้", "ไม่อยากตื่นมาเจอพรุ่งนี้", "อยากปล่อยตัวเองไป",
        "เบื่อการมีชีวิต", "ถ้าตายไปทุกคนคงสบาย"]
THC_POST = ["", " ค่ะ", " ครับ", " 😭", " จริงๆ", "...", " ช่วยด้วย", " ไม่รู้จะทำไง", " ทุกวันเลย", " นะ", " อะ", " ไม่ไหวแล้ว", " ไม่มีใครเข้าใจ", " แล้ว", " เลย"]
THC_CALM = ["อยากไปให้พ้นๆ จากที่ทำงาน", "ไม่เห็นทางออกของโจทย์ข้อนี้", "ซื้อยามาเก็บไว้แล้วเผื่อป่วย", "อยากปล่อยตัวเองไปเที่ยวทะเล",
            "คืนนี้คงเป็นคืนสุดท้ายที่นี่แล้ว", "ไม่รู้จะอยู่บ้านทำไม", "เบื่องานมาก", "อยากหลับยาวๆ ในวันหยุด"]


def th_crisis(n=0):
    cases = _sample(sorted({(p + c + q).strip() for p, c, q in itertools.product(THC_PRE, THC_CORE, THC_POST)}), n, 9)
    bad = []
    for t in cases:
        a = assess(t)
        if not a["crisis"] and a["text_risk"] < 65:
            bad.append(t)
    bad += [f"(ธรรมดา) {t}" for t in THC_CALM if assess(t)["text_risk"] >= 60 or assess(t)["crisis"]]
    return len(cases) + len(THC_CALM), bad


# ── th_violence ─────────────────────────────────────────────────
THV_PERP = ["สามี", "แฟน", "ผัว", "เมีย", "พ่อ", "พ่อเลี้ยง", "แม่", "แม่เลี้ยง", "ลุง", "น้า", "พี่ชาย", "แฟนเก่า", "เจ้านาย", "ครู", "โค้ช", "คนแปลกหน้า", "เพื่อนบ้าน", "รุ่นพี่"]
THV_ACT = ["ตบหนู", "ต่อยหนู", "เตะหนู", "บีบคอหนู", "ทุบตีหนู", "ผลักหนูตกบันได", "เอามีดขู่หนู", "ขู่จะฆ่าหนู", "ขังหนูไว้ในห้อง",
       "ไม่ให้หนูออกจากบ้าน", "ข่มขืนหนู", "ลวนลามหนู", "จับหน้าอกหนู", "สะกดรอยตามหนู", "ตามหนูกลับบ้านทุกคืน", "เอาบุหรี่จี้หนู",
       "ไม่ให้หนูกินข้าว", "ยึดพาสปอร์ตหนู", "ขู่จะปล่อยคลิปหนู", "ทำร้ายหนูจนเลือดออก"]
THV_FRAME = ["{p}{a}", "{p}{a} ทำไงดี", "ช่วยด้วย {p}{a}", "{p}{a}ทุกวัน", "เมื่อคืน{p}{a}", "{p}{a}อีกแล้ว", "{p}{a} กลัวมาก",
      "{p}{a} ไม่รู้จะบอกใคร", "{p}{a} ตอนเมา", "{p}{a} ต่อหน้าลูก", "{p}{a} ค่ะ", "{p}{a} ครับ", "ตอนนี้{p}กำลัง{a}",
      "{p} {a}", "{p}{a}มาตั้งแต่เด็ก", "{p}{a} ควรแจ้งตำรวจไหม", "{p}{a} ไม่มีที่ไป", "{p}{a} ไม่มีใครเชื่อ",
      "{p}{a} ตอนท้อง", "{p}{a}!!", "{p}{a}...", "ปกติไหมที่{p}{a}", "{p}{a} แล้วยึดโทรศัพท์", "{p}{a} ตอนอยู่กันสองคน",
      "{p}{a} ช่วยหนูด้วย", "{p}{a} ไม่อยากอยู่บ้านแล้ว", "{p}{a} 😭", "{p}ชอบ{a}"]
THV_CALM = ["พ่อไม่ให้หนูออกจากบ้านตอนกลางคืน", "น้องตามหนูกลับบ้าน", "แม่ไม่ให้หนูกินขนม", "ตีหนูในเกม", "หนูตบยุง",
            "เพื่อนผลักหนูเล่นตอนเล่นน้ำ", "แม่ไม่ให้หนูออกไปไหนช่วงสอบ"]


def th_violence(n=0):
    cases = _sample(sorted({f.format(p=p, a=a) for p, a, f in itertools.product(THV_PERP, THV_ACT, THV_FRAME)}), n, 8)
    bad = [t for t in cases if assess(t)["text_risk"] < 60]
    bad += [f"(ธรรมดา) {t}" for t in THV_CALM if assess(t)["text_risk"] >= 60]
    return len(cases) + len(THV_CALM), bad


# ── en_violence ─────────────────────────────────────────────────
ENV_PERP = ["my husband", "my boyfriend", "my wife", "my girlfriend", "my partner", "my dad", "my stepdad", "my mom", "my stepmom",
        "my uncle", "my brother", "my ex", "my boss", "my teacher", "my coach", "a stranger", "someone"]
ENV_ACT = ["hits me", "beats me", "punches me", "kicks me", "slaps me", "chokes me", "strangled me", "pushed me down the stairs",
       "threatened to kill me", "said he'll kill me", "has a knife and is threatening me", "locked me in the room", "won't let me leave the house",
       "raped me", "sexually assaulted me", "keeps touching me", "groped me", "is stalking me", "is following me home",
       "burns me with cigarettes", "starves me", "took my passport", "is threatening to post my nudes", "hurt me badly"]
ENV_FRAME = ["{p} {a}", "{p} {a}, what do I do", "help, {p} {a}", "{p} {a} and I'm scared", "{p} {a} again", "{p} {a} every day",
      "I think {p} {a}", "{p} {a} last night", "{p} {a} please help", "{p} {a}. I don't know who to tell",
      "{p} {a} and I'm pregnant", "{p} {a} in front of my kids", "{p} {a}!!", "{p} {a}..", "urgent {p} {a}",
      "{p} {a} and nobody believes me", "{p} {a} and I have nowhere to go", "{p} {a} since I was 12", "{p} {a}, should I call the police",
      "{p} {a} at work", "{p} {a} when he's drunk", "{p} {a} and took my phone", "{p} {a} and I'm bleeding", "{p} {a} tonight",
      "is it normal that {p} {a}"]
ENV_CALM = ["beats me why", "beats me how he did it", "that song hits me hard", "my brother beats me at chess", "it beats me",
            "my back hurts me when I sit", "my heart hurts me", "he kicks me out of the game lol", "my cat keeps touching me",
            "my dog follows me everywhere", "the chef is holding a knife on TV", "I took my phone and locked the door to study",
            "a man with a knife on the cooking show", "it hurts me when he yells"]


def en_violence(n=0):
    cases = _sample(sorted({f.format(p=p, a=a) for p, a, f in itertools.product(ENV_PERP, ENV_ACT, ENV_FRAME)}), n, 7)
    bad = [t for t in cases if assess(t)["text_risk"] < 60]
    bad += [f"(ธรรมดา) {t}" for t in ENV_CALM if assess(t)["text_risk"] >= 60]
    return len(cases) + len(ENV_CALM), bad


# ── followup ────────────────────────────────────────────────────
FOLLOW_PRIOR = {
    "อยากตาย ไม่ไหวแล้ว": "1323", "ลูกกินยาไปทั้งแผง": "1669", "ลูกกลืนถ่านกระดุม": "1669", "สามีตบฉันทุกวัน": "191",
    "มีคนหมดสติไม่หายใจ": "1669", "ถูกนายจ้างขังไว้ในโรงงาน": "191", "ไม่มีข้าวกิน 3 วันแล้ว": "1300",
    "เพื่อนบอกว่าจะฆ่าตัวตาย": "1323", "แม่ปากเบี้ยว พูดไม่ชัด": "1669", "ถูกข่มขืนเมื่อคืน": "1300",
}
FOLLOW = ["ค่ะ", "ครับ", "โอเค", "ไม่มีใคร", "ทำไงดี", "ไม่รู้", "แล้วไงต่อ", "ไม่เป็นไรแล้ว", "อืม", "ขอบคุณ", "?", "..."]


def _sample(items, n, seed):
    items = list(items)
    if n and len(items) > n:
        random.Random(seed).shuffle(items)
        items = items[:n]
    return items


def urgent(n=0):
    cases = sorted({f.format(w=w, e=e).strip() for w, e, f in itertools.product(URGENT_WHO, URGENT_EVENTS, URGENT_FRAME)})
    bad = []
    for t in _sample(cases, n, 1):
        if assess(t)["text_risk"] < 60 or any(g in compose(t) for g in GENERIC):
            bad.append(t)
    return len(_sample(cases, n, 1)), bad


def _violence_cases():
    out = []
    for w, (e, r), f in itertools.product(TH_WHO, TH, TH_FRAME):
        if e.startswith("หายออก") and w in ("ฉัน", "หนู", "ผม", ""):
            continue
        out.append((f.format(w=w, e=e).strip(), r))
    for w, (e, r), f in itertools.product(EN_WHO, EN, EN_FRAME):
        if w == "I" and "missing" in e:
            continue
        x = e.format(w=w)
        if w == "I":
            x = (x.replace("her husband", "my husband").replace("her boyfriend", "my boyfriend").replace("herself", "myself")
                 .replace(" is ", " am ", 1).replace("I am", "I'm").replace("her ", "my ").replace("wants", "want")
                 .replace("has a plan to end my", "have a plan to end my"))
        else:
            x = x.replace("end my life", "end her life")
        out.append((f.format(x=x), r))
    return sorted(set(out))


def violence(n=0):
    cases = _sample(_violence_cases(), n, 2)
    return len(cases), [t for t, r in cases if assess(t)["text_risk"] < r]


def benign(n=0):
    cases = _sample(sorted({(p + c + q).strip() for p, c, q in itertools.product(BENIGN_PRE, BENIGN_CORE, BENIGN_POST)}), n, 3)
    bad = []
    for t in cases:
        a = assess(t)
        if a["crisis"] or a["text_risk"] >= 60:
            bad.append(t)
    return len(cases), bad




def typing(n=0):
    rnd = random.Random(4)
    cases = _sample(sorted({mut(b, rnd) for b in TYPO_BASE for _ in range(600)}), n, 4)
    return len(cases), [t for t in cases if assess(t)["text_risk"] < 60]


def followup(n=0):
    import tempfile
    tmp = tempfile.mkdtemp(prefix="kd-sweep-")
    os.environ.update({"SECRET_KEY": os.getenv("SECRET_KEY", "sweep"), "DB_PATH": os.path.join(tmp, "kd.db"), "KD_DATA_DIR": tmp,
                       "FREE_DAILY_RUNS": "100000", "KD_AI": "off", "TRUST_CF_HEADER": "1"})
    from fastapi.testclient import TestClient
    import app as appmod
    c = TestClient(appmod.app, raise_server_exceptions=False)
    pairs = _sample(list(itertools.product(FOLLOW_PRIOR.items(), FOLLOW)), n, 5)
    bad = []
    for i, ((prior, need), f) in enumerate(pairs):
        hist = [{"role": "user", "content": prior}, {"role": "assistant", "content": "..."}]
        r = c.post("/run", json={"input": f, "history": hist}, headers={"cf-connecting-ip": f"10.9.{i // 250}.{i % 250}"})
        out = str(r.json().get("ai_response", "")) if r.status_code == 200 else f"HTTP {r.status_code}"
        if need not in out or "Risk 0" in out:
            bad.append(f"{prior} → {f}")
    return len(pairs), bad


# ── th_scam ─────────────────────────────────────────────────────
SCAM_PRE = ["", "มีคนโทรมา", "มีคนทักไลน์มา", "มี SMS มา", "แม่บอกว่ามีคนโทรมา", "เมื่อกี้", "เพื่อนส่งลิงก์มา", "มีคนแอดเฟสมา"]
SCAM_CORE = ["บอกว่าเป็นตำรวจ บัญชีเราพัวพันฟอกเงิน ให้โอนเงินไปตรวจสอบ", "อ้างเป็น DSI ให้โอนเงินเข้าบัญชีปลอดภัย",
             "บอกว่ามีพัสดุผิดกฎหมายส่งในชื่อเรา", "บอกว่าการไฟฟ้าจะคืนเงินค่าไฟ ให้กดลิงก์", "บอกว่ากรมที่ดินให้ติดตั้งแอปอัปเดตข้อมูล",
             "ชวนทำงานกดไลก์ได้วันละ 1000 ต้องโอนค่าสมัครก่อน", "ชวนลงทุนคริปโตกำไรวันละ 10%", "ให้กู้เงินด่วน แต่ต้องโอนค่าธรรมเนียมก่อน",
             "บอกว่าถูกรางวัล ต้องจ่ายภาษีก่อนรับ", "ขอรหัส OTP ที่ส่งไปทางมือถือ", "ให้สแกนหน้าในแอปที่ส่งมา",
             "แฟนที่คุยในเน็ตขอยืมเงินค่าตั๋วเครื่องบิน", "อ้างเป็นลูกโทรมาบอกว่าโดนจับ ต้องโอนค่าประกันตัว", "บอกว่าบัตรเครดิตเราถูกใช้ผิดปกติ ขอเลขหลังบัตร",
             "ส่งลิงก์ให้ลงทะเบียนรับเงินดิจิทัล", "บอกว่าเป็นธนาคาร ให้ย้ายเงินไปบัญชีใหม่", "ให้เปิดแอปควบคุมหน้าจอเพื่อช่วยแก้ปัญหา",
             "ชวนเล่นเทรดหุ้นในกลุ่มไลน์ ถอนเงินไม่ได้", "ขายของออนไลน์ โอนแล้วไม่ส่งของ", "อ้างเป็นเจ้าหน้าที่ประกันสังคม ให้โอนเงินคืน"]
SCAM_POST = ["", " ทำไงดี", " จริงไหม", " โอนไปแล้ว", " ยังไม่ได้โอน", " ค่ะ", " ครับ", " กลัวมาก", " ควรเชื่อไหม", " โอนไปห้าหมื่นแล้ว", "!!", " ช่วยด้วย"]
SCAM_CALM = ["ธนาคารส่ง OTP มาตอนโอนเงินเอง ปกติไหม", "ลืมรหัส otp ทำไงดี", "สมัครแอปธนาคาร ต้องสแกนหน้าในแอปไหม", "หุ้นตัวนี้ปันผลดีไหม",
             "กรมที่ดินเปิดให้จองคิวออนไลน์แล้ว", "ร้านออนไลน์ส่งของไวมาก", "ไปธนาคารย้ายเงินไปบัญชีใหม่ที่เปิดเอง", "ใช้ teamviewer ทำงานที่บ้าน",
             "อยากกู้เงินซื้อบ้าน ต้องเตรียมเอกสารอะไร", "ถูกรางวัลสลากต้องเสียภาษีไหม", "ขายของออนไลน์ส่งของไม่ทัน", "ลูกค้าโอนแล้ว ร้านออนไลน์เราส่งของพรุ่งนี้"]


def th_scam(n=0):
    cases = _sample(sorted({(p + (" " if p else "") + c + q).strip() for p, c, q in itertools.product(SCAM_PRE, SCAM_CORE, SCAM_POST)}), n, 11)
    bad = []
    for t in cases:
        a = assess(t)
        if a["text_risk"] < 60 or not a.get("scam"):
            bad.append(t)
    bad += [f"(ธรรมดา) {t}" for t in SCAM_CALM if assess(t)["text_risk"] >= 60]
    return len(cases) + len(SCAM_CALM), bad


# ── en_scam ─────────────────────────────────────────────────────
ENS_PRE = ["", "someone called and", "I got a text that", "a guy on facebook", "my mom got a call,", "a man on whatsapp"]
ENS_CORE = ["said he's from the IRS and I must pay in gift cards", "asked for the code they sent to my phone", "said my bank account is frozen and I need to verify by clicking a link",
            "said I won a lottery but must pay a fee first", "wants me to invest in crypto, guaranteed 20% a week", "said he's my grandson in jail and needs bail money",
            "asked me to install AnyDesk to fix my computer", "said there's a problem with my package, click to reschedule delivery", "offered a job but I have to pay for training first",
            "my online girlfriend asked me to send money for a plane ticket", "told me to move my savings to a safe account", "said he's from Microsoft and my computer has a virus",
            "asked for my social security number to unlock my account", "sold me a puppy online and never delivered after I paid", "asked me to buy apple gift cards and send the codes",
            "said a warrant is out for my arrest unless I pay now"]
ENS_POST = ["", " what do I do", " is this real", " I already paid", " should I trust it", " help", " lol", "?"]
ENS_CALM = ["I bought a gift card for my mom", "can I pay with gift card at target", "my bank sent a verification code to my phone when I logged in",
            "what is my social security number used for", "I installed teamviewer for work", "I won the lottery at work lol", "I paid for the course and it starts monday",
            "my package is late", "the police said I should pay the parking fine", "send me the gift card code you got for christmas"]


def en_scam(n=0):
    cases = _sample(sorted({(p + " " + c + q).strip() for p, c, q in itertools.product(ENS_PRE, ENS_CORE, ENS_POST)}), n, 13)
    bad = []
    for t in cases:
        a = assess(t)
        if a["text_risk"] < 60 or not a.get("scam"):
            bad.append(t)
    bad += [f"(ธรรมดา) {t}" for t in ENS_CALM if assess(t)["text_risk"] >= 60]
    return len(cases) + len(ENS_CALM), bad


# ── world: ภาษาอื่นนอกไทย/อังกฤษ ────────────────────────────────
WORLD = {
    "zh": ["我想死", "我妈妈不能呼吸", "我老公打我"], "ja": ["死にたい", "母が息をしていない", "夫に殴られる"],
    "ko": ["죽고 싶어", "엄마가 숨을 안 쉬어", "남편이 때려요"], "es": ["quiero morir", "mi mamá no respira", "mi esposo me pega"],
    "vi": ["tôi muốn chết", "mẹ tôi không thở được", "chồng tôi đánh tôi"], "id": ["aku ingin mati", "ibuku tidak bisa bernapas", "suamiku memukulku"],
    "ms": ["saya nak mati", "ibu saya tak boleh bernafas", "suami saya pukul saya"], "tl": ["gusto ko nang mamatay", "hindi makahinga ang nanay ko", "sinasaktan ako ng asawa ko"],
    "fr": ["je veux mourir", "ma mère ne respire plus", "mon mari me frappe"], "de": ["ich will sterben", "meine mutter atmet nicht", "mein mann schlägt mich"],
    "pt": ["quero morrer", "minha mãe não respira", "meu marido me bate"], "ru": ["я хочу умереть", "мама не дышит", "муж меня бьёт"],
    "ar": ["أريد أن أموت", "أمي لا تتنفس", "زوجي يضربني"], "hi": ["मैं मरना चाहता हूँ", "माँ साँस नहीं ले रही", "पति मुझे मारता है"],
    "my": ["သေချင်တယ်", "အမေ အသက်မရှူနိုင်ဘူး", "ယောကျ်ားက ရိုက်တယ်"], "km": ["ខ្ញុំចង់ស្លាប់", "ម្តាយខ្ញុំដកដង្ហើមមិនចេញ", "ប្តីវាយខ្ញុំ"],
    "lo": ["ຂ້ອຍຢາກຕາຍ", "ແມ່ຫາຍໃຈບໍ່ໄດ້", "ຜົວຕີຂ້ອຍ"], "it": ["voglio morire", "mia madre non respira", "mio marito mi picchia"],
    "tr": ["ölmek istiyorum", "annem nefes almıyor", "kocam beni dövüyor"],
    "ne": ["मलाई मर्न मन लाग्छ", "आमाले सास फेर्न सक्दैन", "श्रीमान्ले मलाई कुट्छ"], "bn": ["আমি মরে যেতে চাই", "মা শ্বাস নিতে পারছে না", "স্বামী আমাকে মারে"],
    "ur": ["میں مرنا چاہتا ہوں", "امی سانس نہیں لے رہی", "شوہر مجھے مارتا ہے"], "ta": ["நான் சாக வேண்டும்", "அம்மா மூச்சு விடவில்லை", "கணவர் என்னை அடிக்கிறார்"],
    "si": ["මට මැරෙන්න ඕනේ", "අම්මා හුස්ම ගන්නේ නැහැ", "මහත්තයා මට ගහනවා"], "fa": ["میخوام بمیرم", "مادرم نفس نمی‌کشد", "شوهرم منو می‌زنه"],
}
# ภาษาเอเชียที่ต้องได้คำตอบในภาษาของตัวเอง (core/asia_replies.py) ไม่ใช่ภาษาอังกฤษ
WORLD_NATIVE = ("my", "km", "lo", "vi", "id", "ms", "tl", "hi", "ne", "bn", "ur", "ta", "si", "fa", "ar", "tr")
WORLD_HELP = ["救命", "助けて", "살려주세요", "ayuda", "cứu tôi với", "tolong saya", "tulong", "au secours", "hilfe", "socorro", "помогите",
              "النجدة", "बचाओ", "ကယ်ပါ", "ជួយផង", "ຊ່ວຍແດ່", "aiuto", "imdat"]
WORLD_FRAME = ["{x}", "{x}!!", "{x} ...", "{x} 😭", "{x}?"]
WORLD_CALM = ["je veux mourir de rire", "hp ku mau mati", "aku tidak sadar kalau sudah malam", "ich brauche Hilfe bei den Hausaufgaben",
              "necesito ayuda con mi tarea", "il film era da infarto", "tolong ambilkan air", "Je suis fatigué", "cảm ơn bạn",
              "Merhaba nasılsın", "Привет как дела", "مرحبا", "नमस्ते", "မင်္ဂလာပါ", "សួស្តី", "ສະບາຍດີ"]


def world(n=0):
    cases = [(f.format(x=x), 60) for xs in WORLD.values() for x in xs for f in WORLD_FRAME]
    cases += [(f.format(x=x), 50) for x in WORLD_HELP for f in WORLD_FRAME]
    bad = [t for t, need in cases if assess(t)["text_risk"] < need]
    from core.asia_replies import REPLY
    openers = {lg: {r[0] for r in REPLY[lg].values()} for lg in WORLD_NATIVE}
    for lg in WORLD_NATIVE:
        for x in WORLD[lg]:
            if compose(x).split("\n")[0] not in openers[lg]:
                bad.append(f"(ไม่ได้ตอบเป็นภาษา {lg}) {x}")
    bad += [f"(ธรรมดา) {t}" for t in WORLD_CALM if assess(t)["text_risk"] >= 50]
    return len(cases) + len(WORLD_CALM), bad


SUITES = {"urgent": urgent, "violence": violence, "benign": benign, "typing": typing, "intl": intl, "en": en, "en_crisis": en_crisis, "th_crisis": th_crisis, "th_violence": th_violence, "en_violence": en_violence, "followup": followup, "th_scam": th_scam, "en_scam": en_scam, "world": world}


def main(argv):
    n = 0
    if "--sample" in argv:
        i = argv.index("--sample")
        n = int(argv[i + 1])
        argv = argv[:i] + argv[i + 2:]
    names = [a for a in argv if a in SUITES] or list(SUITES)
    failed = 0
    for name in names:
        total, bad = SUITES[name](n)
        failed += len(bad)
        print(f"{name:9s} {total:6d} ข้อความ · หลุด {len(bad)}")
        for t in bad[:8]:
            print("   ", t)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
