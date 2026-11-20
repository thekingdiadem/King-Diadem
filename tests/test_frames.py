"""ตัวจับแบบประกอบชิ้นส่วน (core/frames.py + core/frames_lexicon.tsv)

ข้อความในไฟล์นี้เขียนขึ้นใหม่เพื่อทดสอบกลไก — ไม่ได้มาจาก tests/blind/blind.tsv (ชุดปิดตาห้ามใช้จูน)
"""
import pytest

from core.frames import FRAMES, explain, frames, lexicon

DANGER = [
    "น้องกลืนน้ำยาล้างจานเข้าไปเยอะ", "ลูกสำลักลูกอม", "he swallowed a bunch of his mom's antidepressants",
    "a kid swallowed thirty tablets", "my daughter is choking on a candy", "grandpa fell into the canal and can't swim",
    "el niño tragó gasolina", "bé uống phải xăng", "他把整瓶退烧药都吃了", "妈妈掉进水库里了，救命",
    # ตัวกันเตือนเกินต้องไม่กลืนเรื่องจริง: น้ำท่วม + มีคนจมน้ำ · "ไม่รู้วิธีช่วย" ตอนลูกสำลัก
    "น้ำท่วมบ้าน ลูกจมน้ำ", "ไม่รู้วิธีช่วย ลูกสำลักลูกอม", "방법이 없어요 아이가 사탕이 목에 걸렸어요",
    "아이가 휘발유를 마셨어요", "아이가 청소용 세제를 마셨어요", "息子が灯油を飲んだ", "子どもが掃除用洗剤を飲んだ",
]

# กับดัก: คำแรงแต่ไม่ใช่อันตราย — แต่ละข้อคือเหตุผลที่มีตัวกันเตือนเกินหรือรูปคำพิเศษในคลังคำ
CALM = [
    "ยายกินข้าวแล้ว",                                  # "ยา" ใน "ยาย"
    "พยายามกินยาให้ตรงเวลาทุกวัน",                     # "ยา" ใน "พยายาม" + กิจวัตร
    "ทานตะวันบานสวย",
    "ล้างห้องน้ำด้วยน้ำยาแล้วกินข้าว",                   # ใช้สารเคมีตามปกติ
    "ยาหมดแล้วต้องไปรับเพิ่มที่โรงพยาบาล",              # ยาหมด ≠ กินหมด
    "I take my pills every morning, all good",          # "all good" ไม่ใช่ "all my pills"
    "ate lunch then sprayed the weed killer on the lawn",  # กินคนละเรื่องกับสารเคมี
    "my pills ran out, need a refill",
    "choking with laughter at that joke",
    "I'm drowning in work this week",
    "what happens if a dog eats rat poison",
    "in the movie he drank poison",
    "we swam in the river and had fun",
    "다 알아요 약속 시간에 먹었어요",                    # "알" ใน "알아요" · "약" ใน "약속"
    "吃完饭吃了一片药",                                  # "吃完" = กินข้าวเสร็จ ไม่ใช่กินหมด
]


@pytest.mark.parametrize("text", DANGER)
def test_danger_is_assembled_from_parts(text):
    assert frames(text) == [("medical", "health_emergency")], explain(text)


@pytest.mark.parametrize("text", CALM)
def test_calm_text_is_not_flagged(text):
    assert frames(text) == [], explain(text)


def test_word_order_does_not_matter():
    # ข้อดีหลักของการประกอบชิ้นส่วน — เล่าผลก่อนเหตุก็ยังจับได้
    assert frames("ยาฆ่าแมลง น้องกินเข้าไป") == [("medical", "health_emergency")]
    assert frames("poison — the toddler drank it") == [("medical", "health_emergency")]


def test_parts_must_be_near_each_other():
    far = "I ate a big breakfast with my family this morning before we went to the farm and later my uncle used weed killer"
    assert frames(far) == []


def test_blank_and_odd_input():
    for x in (None, "", "   ", 123, ["x"]):
        assert frames(x) == []


def test_every_frame_concept_exists_in_every_language():
    lex = lexicon()
    langs = {"th", "en", "es", "vi", "zh", "ko", "ja"}
    for name, _k, _t, options, blockers in FRAMES:
        for need in options:
            for c in need:
                assert langs <= set(lex[c]), (name, c, langs - set(lex[c]))
        for b in blockers:
            missing = langs - set(lex.get(b, {}))
            assert b.startswith("IDIOM_") or not missing      # สำนวนมีเฉพาะบางภาษา, (name, b, missing)


def test_assess_uses_frames(app_module):
    from core.kernel_voice import assess
    a = assess("ยาฆ่าแมลง น้องกินเข้าไป")
    assert "health_emergency" in (a.get("topics") or [])


# ── รอบ 2: บีบคอ · แรงงานบังคับ · หมดสติ · เลือดออกไม่หยุด (ชุดปิดตา E ล็อกไว้ก่อนเขียนคลังคำ) ──
DANGER_2 = [
    ("เขาบีบคอฉันทุกครั้งที่เมา", "violence"), ("he grabbed me by the throat", "violence"),
    ("me agarró del cuello y me tiró al suelo", "violence"), ("anh ta bóp cổ tôi", "violence"),
    ("他掐住我的脖子", "violence"), ("그가 제 목을 졸랐어요", "violence"), ("彼に首を絞められた", "violence"),
    ("they took our passports and force us to work without pay", "violence"),
    ("我们被关在工地干活，不给工资", "violence"), ("빚 때문에 가둬놓고 일을 시켜요", "violence"),
    ("my uncle passed out on the floor", "health_emergency"), ("แม่หมดสติในครัว", "health_emergency"),
    ("la vecina se desmayó en la calle", "health_emergency"), ("老人晕倒在路边", "health_emergency"),
    ("ลูกหกล้มหัวแตก เลือดไหลไม่หยุด", "health_emergency"), ("he's bleeding everywhere from his head", "health_emergency"),
    ("다리에서 피가 계속 나요", "health_emergency"), ("腕から血が止まらない", "health_emergency"),
]

CALM_2 = [
    "ขอซื้อคอมพิวเตอร์ใหม่ กดคีย์บอร์ดไม่ติด",      # "คอ" ใน "คอมพิวเตอร์"
    "my phone isn't responding again", "the stock market collapsed today",
    "I almost passed out from laughing",
    "커피를 많이 마셨더니 피곤해요",                    # "피" ใน "커피" "피곤"
    "血压一直很高", "血圧がずっと高い",                  # จีน/ญี่ปุ่นใช้ตัวอักษรร่วมกัน — ข้อยกเว้นต้องครบทั้งสองแบบ
    "手首が痛い", "cổ phiếu giảm mạnh", "목요일에 목표를 세웠어요",
    "mẹ bắt tôi làm bài tập về nhà", "my boss makes me work late sometimes", "แม่บังคับให้ทำงานบ้าน",
    "hugged him around the neck", "this tie is choking me lol",
    "เลือดออกตามไรฟันนิดหน่อย", "ชักชวนเพื่อนไปเที่ยว", "ช็อกมากที่สอบตก", "我一直很喜欢喝咖啡",
    "เมื่อคืนเมาจนหลับไม่รู้สึกตัว ตื่นมาปวดหัว",          # หมดสติแล้วฟื้นแล้ว ไม่ใช่เหตุตอนนี้
]


@pytest.mark.parametrize("text,topic", DANGER_2)
def test_round2_danger(text, topic):
    assert any(t == topic for _k, t in frames(text)), explain(text)


@pytest.mark.parametrize("text", CALM_2)
def test_round2_calm(text):
    assert frames(text) == [], explain(text)


def test_forced_labor_needs_two_signals():
    # "บังคับให้ทำงาน" ตามลำพังไม่พอ — ต้องมีขัง/ยึดค่าจ้าง/หนี้ ร่วมด้วย
    assert frames("my boss forces me to work on weekends") == []
    assert frames("my boss forces me to work on weekends without pay") == [("violence", "violence")]


# ── รอบ 3: แพ้รุนแรง · ไฟไหม้/น้ำร้อนลวก · ไฟดูด · งู/สัตว์กัด (ชุดปิดตา F ล็อกไว้ก่อนเขียนคลังคำ) ──
DANGER_3 = [
    "กินปูแล้วคอบวม หายใจไม่ออก", "stung by a wasp and my throat is closing, can't breathe", "Comí mariscos y no puedo respirar",
    "ăn hải sản xong khó thở", "吃了海鲜，嘴唇肿了，呼吸困难", "새우 먹고 얼굴이 부어서 숨이 차요", "エビを食べて顔が腫れて息苦しい",
    "น้ำร้อนลวกแขนลูก ผิวพองหมด", "grease fire, his hands are blistering", "se quemó con agua hirviendo y tiene ampollas",
    "bị bỏng nước sôi, da phồng rộp", "被开水烫到，起了水泡", "끓는 물에 데어서 물집이 생겼어요", "熱湯でやけどして水ぶくれ",
    "ลุงโดนไฟดูดตกจากเสา", "he touched a live wire and got shocked", "se electrocutó con un cable", "bị điện giật",
    "他触电了", "감전됐어요", "感電した",
    "งูเห่ากัดขาพ่อ", "a rattlesnake bit my dad", "un perro me mordió", "bị chó cắn", "被蛇咬了", "뱀에 물렸어요", "ヘビに噛まれた",
    "들개가 제 손을 물었어요",
]

CALM_3 = [
    "โดนต่อยหน้าบวม",                         # ต่อย = ชก ไม่ใช่แมลงต่อย
    "my dog is a bit sick today",              # "a bit" ไม่ใช่ถูกกัด
    "发烧了，起了一大片疹子",                    # 发烧 = เป็นไข้ ไม่ใช่ไฟไหม้
    "駅のそばで蕎麦を食べた",                    # そば = ข้างๆ
    "กินปูแล้วปากบวมนิดหน่อย", "I burned my dinner", "sunburn on my face is peeling",
    "the news was shocking", "static shock from the car door", "electric bill went up",
    "the cat bit my finger playfully, no blood", "we saw cobras at the zoo",
    "강아지에 대해 선생님께 물었어요",            # 물었다 = ถาม
    "ข้อมือแพ้นาฬิกาเป็นผื่นนิดหน่อย",
]


@pytest.mark.parametrize("text", DANGER_3)
def test_round3_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_3)
def test_round3_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 4: ชัก · เส้นเลือดในสมอง · หัวกระแทก/ตกที่สูง · อุบัติเหตุรถ (ชุดปิดตา G ล็อกไว้ก่อนเขียนคลังคำ) ──
DANGER_4 = [
    "ลูกชักไม่หยุด ตัวเขียว", "my daughter is having a seizure right now", "el bebé está convulsionando", "bé đang co giật",
    "孩子在抽搐", "아기가 경련해요", "子どもがけいれんしている",
    "แม่ปากเบี้ยว พูดไม่ชัด", "grandpa's face is drooping and his speech is slurred", "mi papá tiene la boca torcida y no puede hablar bien",
    "bà bị méo miệng, nói ngọng", "爷爷嘴歪了，说话含糊不清", "할머니 입이 돌아가고 말이 어눌해요", "祖母の口が曲がって、ろれつが回らない",
    "I think dad is having a stroke", "Grandpa suddenly can't make sense when he talks",
    "เด็กตกจากต้นไม้ หัวฟาดพื้น อาเจียน", "he fell off the ladder, hit his head and is confused", "se cayó del techo y está inconsciente",
    "em bé ngã cầu thang đập đầu và nôn", "从梯子上摔下来撞到头，一直吐", "사다리에서 떨어져서 머리를 부딪치고 토해요", "はしごから落ちて頭を打ち、吐いている",
    "รถคว่ำ คนขับติดอยู่ในรถ", "there was a crash and someone is bleeding badly", "hubo un choque y hay un herido",
    "tai nạn xe, có người bị thương", "车祸了，有人流血", "교통사고가 났는데 사람이 다쳤어요", "事故で人がけがをしている",
]

CALM_4 = [
    "ตกใจมากจนหัวเราะไม่ออก แล้วก็อาเจียน",       # ตก ใน ตกใจ · หัว ใน หัวเราะ
    "หัวหน้าล้มเหลวในโปรเจกต์", "ฝนตกหนัก ปวดหัว", "ล้มป่วยเป็นไข้หวัด",
    "my eyelid keeps twitching", "I had a crash course in Python, I'm fine",
    "the stock market crashed and I'm not moving my money",
    "slurred speech after too many beers, so drunk lol",
    "suddenly I can't make sense of this math",   # ไม่เข้าใจ ≠ พูดไม่รู้เรื่อง
    "mi celular se cayó y no se mueve la pantalla", "điện thoại rơi, không sao", "手机掉了，没事",
    "휴대폰이 떨어졌는데 괜찮아요", "スマホが落ちたけど大丈夫",
    "I fell asleep on the couch, head on the armrest", "we had a minor accident, nobody hurt, no pain",
]


@pytest.mark.parametrize("text", DANGER_4)
def test_round4_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_4)
def test_round4_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 5: ก๊าซรั่ว/CO · ลมแดด · น้ำตาลต่ำ · หอบหืด (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา H) ──
DANGER_5 = [
    "ถังแก๊สรั่ว ยายมึนหัวจะล้ม", "smells like gas in the basement and my husband feels dizzy",
    "เปิดฮีตเตอร์ห้องปิด พ่อคลื่นไส้", "olor a gas en el baño, mi abuela está mareada",
    "the carbon monoxide detector beeped and grandma has a bad headache",
    "ลุงเป็นลมแดดกลางนา", "the runner is burning up and confused after the race", "爷爷在田里中暑了",
    "น้องเป็นเบาหวาน ตอนนี้เหงื่อเย็นตัวสั่น", "my wife is diabetic and she's confused and shaky",
    "blood sugar just read 35", "혈당이 38이에요", "低血糖で冷や汗が止まらない",
    "หืดกำเริบ หายใจไม่ออก", "his asthma is acting up and he can't breathe", "Bà lên cơn hen, không thở được",
    "아이가 쌕쌕거리고 말을 못 해요",
]
CALM_5 = [
    "ซื้อแก๊สถังใหม่มาเปลี่ยน", "the gas bill went up this month", "ปิดห้องเปิดแอร์นอนสบาย",
    "วิธีป้องกันลมแดดสำหรับนักวิ่ง", "熱中症に注意しましょう", "the pizza oven is scorching hot",
    "แม่เป็นเบาหวาน หมอบอกน้ำตาลปกติดี", "I'm diabetic and I go to the gym every day",
    "เป็นเบาหวาน วิ่งเสร็จเหงื่อแตกสดชื่น",
    "this recipe uses 50 grams of sugar", "หลานเป็นหืดแต่คุมได้ดี", "asthma awareness week starts monday",
    "my kid wheezes a little when he has a cold",
]


@pytest.mark.parametrize("text", DANGER_5)
def test_round5_danger(text):
    assert frames(text) == [("medical", "health_emergency")], explain(text)


@pytest.mark.parametrize("text", CALM_5)
def test_round5_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 6: หัวใจ · ขาดน้ำ · ติดในที่แคบ · น้ำท่วมฉับพลัน (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา I) ──
DANGER_6 = [
    "ตาแน่นหน้าอก เหงื่อแตก ร้าวไปกราม", "my husband has chest pain and is short of breath",
    "她心肌梗塞了，冷汗直流", "dolor en el pecho y le duele el brazo izquierdo",
    "น้องท้องร่วงทั้งคืน ตาโหลและซึม", "he keeps vomiting and can't keep water down", "아기가 설사하고 소변을 안 봐요",
    "ติดอยู่ในลิฟต์ หายใจลำบาก", "we're trapped in the elevator and the air is running out", "孩子被锁在车里，外面太阳很大",
    "น้ำป่าพัดบ้าน ยายติดอยู่บนหลังคา", "flash flood, we're stranded on the roof", "洪水淹到二楼，我们被困了",
]
CALM_6 = [
    "เจ็บหน้าอกเพราะไอทั้งคืน", "my chest is sore from the gym, a little sweaty", "ท้องเสียนิดหน่อย",
    "had diarrhea yesterday but feel better now", "ติดอยู่ในรถติดหนึ่งชั่วโมง", "stuck in traffic in the car for an hour",
    "the elevator is slow today",
    "I almost had a heart attack, I was so sweaty from nerves", "น้ำท่วมถนนนิดหน่อย", "flood insurance is expensive",
]


@pytest.mark.parametrize("text", DANGER_6)
def test_round6_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_6)
def test_round6_calm(text):
    assert frames(text) == [], explain(text)


def test_chinese_blocker_does_not_apply_to_japanese():
    # "作業員" (คนงาน) มีอักษรเดียวกับ "作业" (การบ้านภาษาจีน) — ต้องไม่ถูกนับเป็นคำถามเชิงความรู้
    assert frames("工事現場の作業員が体がすごく熱くて、倒れた") == [("medical", "health_emergency")]
    assert frames("中暑的作业怎么写") == []


# ── รอบ 7: ครรภ์เสี่ยง · ไข้ทารก · แผลลึก · สัตว์มีพิษในทะเล (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา J) ──
DANGER_7 = [
    "ท้องได้ 30 สัปดาห์ เลือดออกเยอะ", "she's pregnant and her water broke early", "怀孕六个月，突然大量出血",
    "หลานอายุ 3 เดือน ไข้สูง ซึมไม่ยอมกินนม", "my 6-week-old has a fever and is very lethargic", "생후 5주 아기가 열이 나고 처져 있어요",
    "เหล็กเสียบขาทะลุ เลือดไหลไม่หยุด", "a screwdriver went through my hand and it keeps bleeding", "包丁で手を深く切って骨が見える",
    "น้องโดนแมงกะพรุน หายใจลำบาก", "got stung by a lionfish, my hand is swollen and numb", "bị sứa đốt, chóng mặt",
]
CALM_7 = [
    "ท้อง 5 เดือน หมอบอกปกติดี", "I'm pregnant and so happy", "ลูกเป็นไข้ กินยาแล้วดีขึ้น",
    "the baby has a little fever but is feeding fine, better now", "ตะปูทิ่มเสื้อขาดนิดหน่อย", "a nail went through the drywall",
    "jellyfish soup was tasty", "เห็นแมงกะพรุนเยอะมาก", "ウニの殻で少し指を切った",
]


@pytest.mark.parametrize("text", DANGER_7)
def test_round7_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_7)
def test_round7_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 8 เน้นไต (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา K) ──
DANGER_8 = [
    "ปู่ฉี่ไม่ออกตั้งแต่เมื่อคืน ท้องน้อยโป่ง", "he can't pee and his belly is hard and swollen", "爸爸尿不出来，肚子胀得难受",
    "เป็นนิ่วในไต มีไข้หนาวสั่น", "kidney stone pain and now a fever", "신장결석인데 오한이 나요",
    "พ่อขาดฟอกไตมาสามวัน", "she missed dialysis this week and feels weak", "透析を休んで息ができない",
    "หมอบอกโพแทสเซียมสูง ใจเต้นผิดจังหวะ", "mi madre tiene insuficiencia renal y no puede orinar",
]
CALM_8 = [
    "ไข้หวัด ปวดหลังปวดตัว", "flu with fever and my back hurts", "ไปฟอกไตตามนัดทุกสัปดาห์", "I peed a lot after drinking tea",
    "ปวดฉี่ตอนรถติด", "kidney beans for dinner", "ค่าไตปกติดี",
]


@pytest.mark.parametrize("text", DANGER_8)
def test_round8_kidney_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_8)
def test_round8_kidney_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 9: ตัวเย็นเกิน · ปวดท้องรุนแรง · เลือดออกทางเดินอาหาร · เยื่อหุ้มสมองอักเสบ (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา L) ──
DANGER_9 = [
    "ยายตัวเย็นเฉียบ เรียกไม่ตอบ", "pulled him out of freezing water, he's confused and shivering nonstop", "爷爷失温了，一直发抖",
    "ปวดท้องรุนแรงมาก มีไข้", "severe abdominal pain and vomiting", "배가 너무 아프고 열이 나요",
    "อาเจียนเป็นเลือดเมื่อกี้", "my dad is vomiting blood", "タール便が出た",
    "ลูกไข้สูง คอแข็ง", "high fever and a stiff neck", "고열에 보라색 반점이 생겼어요",
]
CALM_9 = [
    "หนาวมาก ใส่เสื้อสองชั้น", "my hands are ice cold in the office", "ปวดท้องประจำเดือนมาก", "severe belly pain from period cramps",
    "ถ่ายดำเพราะกินธาตุเหล็ก", "black tarry stool from iron pills", "คอแข็งเพราะตกหมอน มีไข้นิดหน่อย", "stiff neck from sleeping wrong",
]


@pytest.mark.parametrize("text", DANGER_9)
def test_round9_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_9)
def test_round9_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 10: เมาจนเป็นพิษ · เหล้าเถื่อน · ยาเสพติดเกินขนาด · กลืนถ่าน/แม่เหล็ก (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา M) ──
DANGER_10 = [
    "เพื่อนเมาจนปลุกไม่ตื่น", "he's blackout drunk and breathing slowly", "喝完了一整瓶酒，叫不醒",
    "กินเหล้าเถื่อนแล้วตามัว", "drank moonshine and now can't see", "밀주 마시고 눈이 흐려요",
    "เพื่อนเสพยาบ้าแล้วชัก", "she took fentanyl and is barely breathing", "覚醒剤で心臓がバクバク",
    "ลูกกลืนถ่านกระดุม", "my son swallowed a magnet", "아이가 자석을 삼켰어요",
]
CALM_10 = [
    "เมารถ ตัวเย็นนิดหน่อย", "ดื่มเบียร์สองกระป๋อง", "read about the dangers of heroin", "เปลี่ยนถ่านนาฬิกา",
    "keep magnets away from kids", "ดูข่าวเหล้าเถื่อน", "say xe nên người lạnh",
]


@pytest.mark.parametrize("text", DANGER_10)
def test_round10_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_10)
def test_round10_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 11: เด็กหาย · ผู้สูงอายุเดินหลง · หลงป่า · ติดกลางทะเล (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา N) ──
DANGER_11 = [
    "ลูกหายไปจากตลาด หาไม่เจอ", "we haven't found her yet, my daughter is missing", "아들이 실종됐는데 아직 못 찾았어요",
    "Mi hijo no volvió de la escuela", "ปู่เป็นอัลไซเมอร์ ออกจากบ้านไปแล้วหาไม่เจอ", "my mom has dementia and wandered off",
    "หลงป่าบนดอย ติดต่อไม่ได้", "lost on the mountain trail, can't reach anyone", "山で遭難した",
    "เรือคว่ำกลางทะเล", "our boat is sinking at sea", "바다에서 카약이 떠밀려 돌아갈 수가 없어요",
]
CALM_11 = [
    "ลูกเล่นซ่อนแอบ หาเจอแล้ว", "found him, he was at the neighbor's", "ไปเดินป่ากับไกด์",
    "watched a documentary about people lost in the forest", "นั่งเรือเล่นที่ทะเล สนุกมาก", "my son came back home late",
]


@pytest.mark.parametrize("text", DANGER_11)
def test_round11_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_11)
def test_round11_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 12: แผ่นดินไหวติดใต้ซาก · ดินถล่ม · ไฟป่าลามใกล้ · ฟ้าผ่า (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา O) ──
DANGER_12 = [
    "แผ่นดินไหว พ่อติดอยู่ใต้ซากบ้าน", "after the earthquake my neighbor is pinned under the roof", "地震后有人被压在下面",
    "ดินถล่มทับบ้านเพื่อน มีคนหาย", "a landslide buried our car", "산사태로 집이 묻혔어요",
    "ไฟป่าลามมาถึงหลังบ้านแล้ว ออกไม่ได้", "the wildfire is very close and we're surrounded", "山火事がすぐ近くまで来ている",
    "ฟ้าผ่าคนข้างบ้าน ตอนนี้หมดสติ", "my dad was struck by lightning and isn't breathing", "bị sét đánh, bất tỉnh",
]
CALM_12 = [
    "ซ้อมหนีแผ่นดินไหวที่ออฟฟิศ", "earthquake drill at work today", "ควันไฟป่าไกลๆ", "photos of lightning over the city",
    "ดินพังนิดหน่อยตอนขุดดิน", "the sandcastle collapsed",
]


@pytest.mark.parametrize("text", DANGER_12)
def test_round12_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_12)
def test_round12_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 13: ความรุนแรง (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา P) ──
VIOLENCE_13 = [
    "แฟนถือมีดขู่จะแทง", "he's pointing a gun at me", "老公拿刀追我", "전 남편이 죽이겠다고 하고 지금 문 앞에 있어요",
    "มีผู้ชายตามฉันมาถึงหน้าห้อง", "someone has followed me home and is knocking on my door", "ストーカーが部屋の前にいる",
    "เพิ่งโดนลวนลามบนรถเมล์", "I was sexually assaulted at the party", "Mi hijo tiene moretones por todo el cuerpo",
]
CALM_13 = [
    "หั่นผักด้วยมีดทำกับข้าว", "kids playing with a water gun", "อ่านข่าวการข่มขืนแล้วโกรธ", "someone walked behind me the same way",
    "เด็กเล่นกัน หัวเราะกัน", "my ex wants his book back",
]


@pytest.mark.parametrize("text", VIOLENCE_13)
def test_round13_violence(text):
    assert ("violence", "violence") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_13)
def test_round13_calm(text):
    assert frames(text) == [], explain(text)


# ── รอบ 14: น้ำตาลสูงวิกฤต · ความดันวิกฤต · ลิ่มเลือด · ตามองไม่เห็นกะทันหัน (ข้อความใหม่ ไม่ได้มาจากชุดปิดตา Q) ──
DANGER_14 = [
    "น้ำตาล 600 อาเจียน ซึม", "his sugar is 550 and his breath smells fruity", "혈당이 600인데 토하고 처져요",
    "ความดัน 210/120 ปวดหัวมาก", "blood pressure 200/110 with chest pain", "血压200，胸痛",
    "นั่งเครื่องบินไกลมา เจ็บหน้าอก หายใจไม่ทัน", "after surgery I'm suddenly coughing up blood", "片足が腫れて息ができない",
    "จู่ๆ ตาข้างซ้ายมองไม่เห็น", "suddenly I can't see out of one eye", "De repente veo destellos y muchas manchas",
]
CALM_14 = [
    "น้ำตาลหลังอาหารสูงนิดหน่อย", "this cake has 450 grams of sugar", "ความดัน 130/85", "blood pressure 120/80 today",
    "นั่งรถนานขาเมื่อย", "can't see the screen without my glasses", "มีเงาดำลอยเล็กๆ มานาน",
]


@pytest.mark.parametrize("text", DANGER_14)
def test_round14_danger(text):
    assert ("medical", "health_emergency") in frames(text), explain(text)


@pytest.mark.parametrize("text", CALM_14)
def test_round14_calm(text):
    assert frames(text) == [], explain(text)
