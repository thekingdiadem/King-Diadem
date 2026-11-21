"""ครอบครัว — แต่ละบ้านเรื่องคล้ายกันแต่คำพูดต่างกัน จึงเทสต์หลายสำนวนต่อหนึ่งแบบ

แบบที่ 1: พ่อแม่ที่ทั้งรักและทำร้าย — Understanding ≠ Justification · Recognizing Harm ≠ Denying Goodness · One Person Can Contain Both
แบบที่ 2: ถูกนอกใจ — สิ่งที่หายไปคือความไว้ใจในคนคนหนึ่ง ไม่ใช่ค่าของคุณ · มองสิ่งที่ยังเหลืออยู่
แบบที่ 3: รู้ว่าพ่อหรือแม่นอกใจ — ไม่ใช่ความผิดของลูก ไม่ต้องแบกความลับคนเดียว
"""
import pytest
from core.heart_lines import LINES, lines_for
from core.kernel_voice import assess, compose


def _has(q, key):
    return any(LINES[key][0] in g or LINES[key][1] in g for g in lines_for(q, assess(q)))


@pytest.mark.parametrize("q", [
    "พ่อกินเหล้าแล้วด่าแม่ทุกคืน แต่พ่อก็ทำงานหนักเพราะไม่อยากให้เราลำบาก", "แม่ตีหนูบ่อย แต่แม่ก็เลี้ยงหนูมาคนเดียว",
    "พ่อเมาทุกคืน ทั้งที่พ่อก็รักพวกเรา", "รักแม่นะ แต่แม่ชอบตะคอกใส่", "ทั้งรักทั้งเกลียดพ่อ",
    "พ่อเลี้ยงด่าหนูแรงๆ แต่ก็ส่งเสียให้เรียน", "แม่ดูถูกหนูตลอด แต่แม่ก็ทำงานหนักเพื่อเรา",
    "พ่อเคยดีกับเรามาก แต่ตอนนี้ติดเหล้าแล้วทุบของ",
    "I love my mom but she screams at me every day", "my father hits us but he provides for everything",
])
def test_parent_who_both_loves_and_harms(q):
    assert _has(q, "both")


@pytest.mark.parametrize("q", [
    "แฟนนอกใจ", "ผัวมีเมียน้อย", "เมียแอบคุยกับผู้ชายอื่น", "สามีมีกิ๊กมาสองปี", "จับได้ว่าแฟนแอบคุยกับคนอื่น",
    "my wife had an affair", "my boyfriend has been cheating with my best friend", "found out my partner is sleeping with someone else",
])
def test_cheated_on_sees_what_remains(q):
    assert _has(q, "cheated")


@pytest.mark.parametrize("q", ["พ่อนอกใจแม่ หนูรู้แต่แม่ยังไม่รู้", "รู้ว่าพ่อมีเมียน้อย", "แม่มีผัวใหม่ทั้งที่ยังอยู่กับพ่อ",
                               "พ่อแอบมีครอบครัวใหม่", "my mom is having an affair", "I caught my dad texting another woman"])
def test_child_who_knows_parent_cheated(q):
    assert _has(q, "parent_cheat") and not _has(q, "cheated")


@pytest.mark.parametrize("q", ["พ่อรักแม่มาก", "แม่ทำงานหนักเพื่อเรา", "แม่ตีกลองเก่ง แต่แม่ก็รักเรา", "พ่อดูซีรีส์นอกใจ",
                               "ดูละครเรื่องเมียน้อย", "รักแฟนมาก"])
def test_no_line_without_the_story(q):
    assert not lines_for(q, assess(q))


def test_family_line_appears_in_the_real_reply():
    r = compose("แม่ตีหนูบ่อย แต่แม่ก็เลี้ยงหนูมาคนเดียว")
    assert "คนคนเดียวมีได้ทั้งด้านที่รักเราและด้านที่ทำให้เราเจ็บ" in r and "ไม่ได้แปลว่าคุณต้องเป็นเหมือนเขา" in r


# แบบที่ 4 — พ่อหรือแม่เลิกกันแล้วไปมีครอบครัวใหม่ตอนลูกยังเล็ก · โตมาถูกเปรียบเทียบ (ญาติก็เปรียบได้)
@pytest.mark.parametrize("q", [
    "พ่อเลิกกับแม่ตอนเรายังเล็ก แล้วไปมีครอบครัวใหม่", "พ่อมีเมียใหม่ตั้งแต่หนูเด็กๆ", "แม่ทิ้งเราไปมีผัวใหม่",
    "my dad left us for his new family when I was 5", "my mom started a new family",
])
def test_parent_left_for_new_family(q):
    assert _has(q, "left") and not _has(q, "parent_cheat")


@pytest.mark.parametrize("q", [
    "ญาติชอบเอาเราไปเทียบกับลูกบ้านนั้นที่รวยกว่า", "ญาติชอบถามว่าเงินเดือนเท่าไหร่ แล้วบอกว่าลูกคนอื่นได้ดีกว่า",
    "แม่ชอบเปรียบเทียบหนูกับพี่", "ป้าพูดว่าหลานคนอื่นเก่งกว่า", "my parents always compared me to my cousin",
    "relatives say his new kids are more successful",
])
def test_being_compared(q):
    assert _has(q, "compare")


@pytest.mark.parametrize("q", ["เปรียบเทียบราคามือถือสองรุ่น", "ช่วยเทียบสเปกคอมให้หน่อย", "compare these two laptops"])
def test_comparing_things_is_not_comparing_people(q):
    assert not _has(q, "compare")


def test_left_line_says_being_their_child_never_changes():
    r = compose("พ่อเลิกกับแม่ตอนเรายังเล็ก แล้วไปมีครอบครัวใหม่")
    assert "คำว่า \"ลูก\" ของคุณไม่มีวันเปลี่ยนสถานะ" in r
