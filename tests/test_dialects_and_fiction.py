"""สำเนียงถิ่น และเรื่องแต่ง (ดาราศาสตร์ วิทยาศาสตร์ แฟนตาซี ไซไฟ)

เจ้าของโปรเจกต์: "รองรับสำเนียงทุกภาคส่วน ... รวมหมดเลยพวกดาราศาสตร์ วิทยาศาสตร์ แฟนตาซี ไซไฟ"
สำเนียง: ต้องไม่หลุด — เดิม "ผัวตุบฮา" (เหนือ) "ผัวตีฉานเหลย" (ใต้) "แม่บ่ได้หายใจแล้ว" "อยากไปเกิดใหม่" ได้ Risk 0
เรื่องแต่ง: ต้องไม่ตกใจผิด — เดิม "ตัวละครในนิยายแฟนตาซีอยากตาย" ได้วิกฤต 95
แต่คนที่พูดถึงตัวละครแล้วพูดถึงตัวเองด้วย ยังต้องถูกจับเหมือนเดิม
"""
import pytest

from core.kernel_voice import assess

DIALECT_HOT = {
    "อีสาน": ["บ่อยากอยู่แล้ว", "อยากตายคักๆ", "บ่อยากมีชีวิตอยู่แล้วเด้อ", "ผัวตีข่อย", "แม่บ่หายใจ"],
    "เหนือ": ["บ่อยากอยู่แล้วเจ้า", "อยากต๋ายแล้ว", "ผัวตุบฮา", "ผัวตุบฮาทุกคืน", "แม่บ่ได้หายใจแล้ว", "แม่อุ๊ยบ่หายใจแล้ว"],
    "ใต้": ["ไม่อยากอยู่แล้วหนิ", "อยากตายแล้วหิ", "ผัวตีฉานเหลย", "แม่ไม่หายใจแล้วหนิ", "เหนื่อยจังหู้ ไม่อยากอยู่แล้ว"],
    "สำนวน": ["อยากหลับยาว", "อยากไปเกิดใหม่", "อยากไปเกิดใหม่จริงๆ เหนื่อยกับชีวิตนี้", "อยากตายห่าเลย"],
}
# ตัวละครที่อยากตาย: ไม่ใช่วิกฤตของผู้ใช้ แต่ได้การถามไถ่เบาๆ (Risk 45) ตามการออกแบบเดิม — คนเขียนเรื่องหนักก็ควรถูกถามว่าโอเคไหม
CHARACTER_SOFT = ["ตัวละครในนิยายแฟนตาซีอยากตาย"]
FICTION_LIGHT = ["ดาวฤกษ์ดวงนี้กำลังจะตาย กลายเป็นซูเปอร์โนวา",
                 "ยานอวกาศระเบิดในตอนจบซีรีส์ไซไฟ", "หลุมดำกลืนกินดาวทั้งดวง", "เซลล์มะเร็งตายหมดหลังให้ยา", "ในเกมฉันตายไปสามรอบ",
                 "จักรวาลจะดับในอีกหลายล้านล้านปี", "มังกรเผาหมู่บ้านในเรื่องที่ฉันเขียน", "ตัวร้ายในการ์ตูนอยากทำลายโลก",
                 "อยากเกิดใหม่ในเกมเป็นตัวละครเทพ", "the star is dying and will go supernova", "my character wants to die in the fantasy novel",
                 "the spaceship explodes at the end", "the villain wants to kill the hero in my story"]
FICTION_LIGHT = [x for x in FICTION_LIGHT if x not in CHARACTER_SOFT]
STILL_HOT = ["ตัวละครในนิยายอยากตาย เหมือนฉันตอนนี้", "ตัวละครในนิยายอยากตาย เหมือนฉันเลย ฉันก็อยากตาย", "my character wants to die. i want to die too", "เล่นเกมอยู่ แต่จริงๆ อยากตาย"]


@pytest.mark.parametrize("region,text", [(r, t) for r, xs in DIALECT_HOT.items() for t in xs])
def test_every_regional_way_of_saying_it_is_caught(region, text):
    a = assess(text)
    assert a["crisis"] or a["text_risk"] >= 60, (region, a["text_risk"])


@pytest.mark.parametrize("text", FICTION_LIGHT)
def test_space_science_and_fiction_do_not_alarm(text):
    a = assess(text)
    assert not a["crisis"] and a["text_risk"] < 35, a


@pytest.mark.parametrize("text", STILL_HOT)
def test_talking_about_a_character_and_yourself_is_still_caught(text):
    assert assess(text)["crisis"]


@pytest.mark.parametrize("text", CHARACTER_SOFT)
def test_a_character_wanting_to_die_gets_a_gentle_check_not_a_crisis(text):
    a = assess(text)
    assert not a["crisis"] and 35 <= a["text_risk"] < 60, a
