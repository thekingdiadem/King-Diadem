"""ชุดความรู้ที่ระบบเคยไม่รู้ (core/knowledge_pack.py) — ทุกข้อในนี้เคยได้คำตอบกลาง ความเสี่ยง 0/100

เช่น ลมแดด (ตัวร้อน ไม่มีเหงื่อ สับสน) · ตาพร่าหลังดื่มเหล้าเถื่อน (เมทานอล) · ไข้ + ผื่นกดไม่จาง ·
ถ่ายดำ + เวียนหัว · ความดัน 190/120 · ลูกหายใจวี้ด · ลูก 14 มีแฟน 25 · แฟนแทร็กมือถือ · ไม่ได้โอที ฯลฯ
"""
import pytest

from core import knowledge_pack as kp
from core.kernel_voice import assess, compose

CASES = [
    ("ตากแดดทั้งวัน ตัวร้อนจัด ไม่มีเหงื่อ สับสน", "kp_heatstroke", "ประคบน้ำแข็ง"),
    ("my dad collapsed in the heat, he's confused and stopped sweating", "kp_heatstroke", "Cool them"),
    ("ดื่มเหล้าขาวเถื่อน ตาพร่า", "kp_methanol", "1367"),
    ("we drank moonshine last night and now my vision is blurry", "kp_methanol", "same bottle"),
    ("ลูกมีไข้ มีผื่นจุดเลือด กดไม่จาง", "kp_fever_rash", "แก้วใส"),
    ("my child has a high fever and a rash that doesn't fade when pressed", "kp_fever_rash", "glass test"),
    ("อุจจาระสีดำ เวียนหัว", "kp_gi_bleed", "1669"),
    ("i'm vomiting blood", "kp_gi_bleed", "blood thinners"),
    ("ความดัน 190/120 ปวดหัว", "kp_bp_crisis", "วัดใหม่"),
    ("my blood pressure is 200/110 and i have a headache", "kp_bp_crisis", "Sit for 5 minutes"),
    ("ลูกหายใจมีเสียงวี้ด หอบ", "kp_child_breath", "ปากเขียว"),
    ("my toddler is wheezing and struggling to breathe", "kp_child_breath", "inhaler"),
    ("ตามัวข้างเดียวกะทันหัน", "kp_sudden_vision", "สโตรก"),
    ("ลูกเอาถั่วยัดจมูก", "kp_object_nose_ear", "ห้ามใช้แหนบ"),
    ("i think i have food poisoning, vomiting all night", "kp_food_poison", "ORS"),
    ("ลูกสาว 14 มีแฟนอายุ 25", "kp_minor_adult_parent", "15 ปี"),
    ("my partner tracks my phone and reads my messages", "kp_coercive_control", "safe device"),
    ("แฟนติดแอปติดตามในมือถือฉัน แล้วขอรหัสทุกอย่าง", "kp_coercive_control", "1300"),
    ("ทำงานเกิน 12 ชั่วโมงทุกวัน ไม่มีโอที", "kp_overtime", "1.5 เท่า"),
    ("i lost my passport abroad", "kp_passport", "embassy"),
    ("พาสปอร์ตหายที่ญี่ปุ่น", "kp_passport", "สถานทูต"),
    ("i got a summons from court and don't know what to do", "kp_summons", "verify"),
    ("ถูกเรียกตัวไปให้ปากคำ", "kp_summons", "1167"),
    ("my landlord kept my deposit for no reason", "kp_deposit", "itemised"),
    ("แม่ติดเตียง มีแผลกดทับ", "kp_pressure_sore", "พลิกตัวทุก 2 ชั่วโมง"),
    ("วัยรุ่นสูบบุหรี่ไฟฟ้า", "kp_vape", "1600"),
    ("my cat isn't eating and hides", "kp_cat_not_eating", "male cat"),
    ("i relapsed on meth", "kp_relapse", "tolerance is lower"),
    ("i've been gambling away my salary", "kp_gambling", "1-800-GAMBLER"),
    ("my period is 3 weeks late and the test is negative", "kp_late_period", "first-morning"),
    # รอบ 2
    ("คนในบ้านมีอาการไข้ ไอ หายใจเหนื่อย ออกซิเจนปลายนิ้ว 90", "kp_low_oxygen", "นอนคว่ำ"),
    ("my oxygen saturation is 89 percent", "kp_low_oxygen", "under 90%"),
    ("ผู้ป่วยเบาหวานแผลที่เท้าดำ มีกลิ่น", "kp_diabetic_foot", "น้ำเกลือ"),
    ("my diabetic foot wound is turning black", "kp_diabetic_foot", "amputation"),
    ("กินยานอนหลับกับเหล้า", "kp_sedative_alcohol", "1367"),
    ("i took sleeping pills with alcohol", "kp_sedative_alcohol", "Don't sleep alone"),
    ("i drink every day and get the shakes when i stop", "kp_alcohol_withdrawal_en", "supervised"),
    ("ถูกแมงกะพรุนต่อยที่ทะเล", "kp_jellyfish", "น้ำส้มสายชู"),
    ("ติดอยู่ในลิฟต์", "kp_elevator", "199"),
    ("i'm stuck in an elevator", "kp_elevator", "don't fall"),
    ("the house next door is on fire", "kp_fire_en", "never the lift"),
    ("ฉันเป็นเกย์ ที่บ้านจะไล่ออก", "kp_lgbt_family", "1300"),
    ("ลูกบอกว่าเป็นทรานส์ ทำไงดี", "kp_child_came_out", "ขอบคุณที่บอก"),
    ("พ่อเสียที่บ้าน ต้องทำอะไรบ้าง", "kp_death_at_home", "24 ชั่วโมง"),
    ("แจ้งตายต้องใช้อะไร", "kp_death_at_home", "ทะเบียนบ้าน"),
    ("my mother died at home, what do i do now", "kp_death_at_home", "medical certificate"),
    ("i want to write a will", "kp_will", "witnesses"),
    ("หย่าแล้วอีกฝ่ายไม่ให้เจอลูก", "kp_custody", "ศาลเยาวชนและครอบครัว"),
    ("my ex won't let me see the kids since the divorce", "kp_custody", "family court"),
    ("someone texted me about a missed parcel with a link", "kp_parcel_sms_en", "official app"),
    ("i was abused as a child and still have nightmares", "kp_abuse_past_en", "not your fault"),
]


@pytest.mark.parametrize("text,topic,must", CASES)
def test_pack_gives_specific_answer(text, topic, must):
    a = assess(text)
    assert a["topics"][0] == topic and a["text_risk"] >= kp.RISK[topic] - 5
    assert must in compose(text)


@pytest.mark.parametrize("text", [
    "ความดัน 120/80 ปกติดี", "แมวกินเก่งมาก อ้วนขึ้น", "ประจำเดือนมาปกติทุกเดือน", "ซื้อเหล้าขาวยี่ห้อดังไปงานบวช",
    "my cat is eating well", "ลูกสาว 14 มีเพื่อนอายุ 15", "แฟนส่งรูปมือถือเครื่องใหม่มาให้ดู", "ทำงานวันละ 8 ชั่วโมง มีโอทีครบ",
    "ลูกหายใจปกติ นอนหลับสบาย", "the passport office opens at 9",
    "ออกซิเจนปลายนิ้ว 98 ปกติ", "ไปเที่ยวทะเลดูแมงกะพรุนที่พิพิธภัณฑ์สัตว์น้ำ", "ลิฟต์ที่คอนโดเสีย ต้องเดินขึ้นบันได",
    "เพื่อนเป็นเกย์ เขามีแฟนแล้ว", "หย่าแล้วแต่เลี้ยงลูกด้วยกันดี",
])
def test_pack_does_not_overfire(text):
    assert not set(kp.match(text)) & set(assess(text)["topics"])


def test_every_entry_is_complete():
    for n, _rx, risk, urgent, th, en in kp.PACK:
        assert n.startswith("kp_") and 0 < risk <= 85
        assert len(th[1]) <= 3 and len(en[1]) == 3 and en[2].endswith("?")
        if th[0]:
            assert len(th[1]) == 3 and th[2].endswith("?")
        if urgent and th[0]:   # เรื่องด่วนต้องมีเบอร์ฉุกเฉินในคำตอบไทย
            assert any(x in " ".join(th[1]) for x in ("1669", "191", "1300", "1367"))
    # อังกฤษต้องไม่ถูก .capitalize() ทำให้ชื่อประเทศเป็นตัวเล็ก
    assert not any("in thailand" in p for *_x, en in kp.PACK for p in en[1])
