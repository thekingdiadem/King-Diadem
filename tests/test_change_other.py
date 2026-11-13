"""อยากเปลี่ยนคนอื่น → พากลับมาที่สิ่งที่ผู้ใช้ควบคุมได้ (หลักของเจ้าของโปรเจกต์: ห้ามแทรกแซงชีวิตใด หากเจ้าของปัญหายังไม่อยากเปลี่ยน)
แต่ถ้ามีการทำร้าย ต้องไปทางความปลอดภัย ไม่ใช่ "เปลี่ยนเขาไม่ได้" """
import pytest

from core.kernel_voice import compose


@pytest.mark.parametrize("text", ["จะทำยังไงให้แฟนเลิกเล่นเกม", "อยากให้แม่เปลี่ยนนิสัย",
                                  "how do I make my husband stop drinking", "how can I change my boss"])
def test_wanting_to_change_someone_gets_what_you_can_control(text):
    r = compose(text)
    assert r.startswith(("เปลี่ยนใครแทนเขาไม่ได้", "You can't change someone for them")), r[:80]
    assert "ขอบเขต" in r or "boundary" in r


@pytest.mark.parametrize("text", ["อยากเปลี่ยนงาน", "I want to change my job",
                                  "แฟนตบหน้าทุกวัน ทำยังไงให้แฟนเลิกทำร้าย", "how do I make my bf stop hitting me", "อยากตาย"])
def test_own_change_harm_and_crisis_do_not_get_this_reply(text):
    r = compose(text)
    assert not r.startswith(("เปลี่ยนใครแทนเขาไม่ได้", "You can't change someone for them")), (text, r[:80])
