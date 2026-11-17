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
