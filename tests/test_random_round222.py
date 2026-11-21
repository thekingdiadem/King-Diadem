"""รอบสุ่ม 222 (อังกฤษ): เล่าตรงๆ แต่ระบบเคยได้ 0 — อดอาหารตัวเอง · ทำร้ายเด็ก · ถูกวางยา · ขังในห้อง/ไม่ให้กิน · ผู้ใหญ่ขอรูปโป๊
และกันบั๊กทั้งระบบ: ทุกหัวข้อที่ชั้นสองยกขึ้นต้องมีค่าความเสี่ยง (เคยล่มด้วย KeyError) และมีคำตอบภาษาอังกฤษ"""
import pytest
from core.kernel_voice import assess, EN_TOPIC, TOPICS
import core.second_layer as S


@pytest.mark.parametrize("q,floor", [
    ("i've been starving myself", 70), ("my boyfriend beats his daughter", 80), ("my mom hits my little brother", 80),
    ("somebody drugged me at the club", 75), ("my parents lock me in the basement for hours", 80),
    ("a coach asked for my nudes", 80), ("he punches doors and then me", 80),
])
def test_plain_english_danger(q, floor):
    assert assess(q)["risk_shown"] >= floor


@pytest.mark.parametrize("q", [
    "i'm starving, let's get pizza", "my son beat his little brother at chess", "he hits the kids' baseballs really far",
    "i was drugged after surgery so i slept", "my coach sends me workout pics",
])
def test_everyday_stays_calm(q):
    assert assess(q)["risk_shown"] < 60


def test_every_upgrade_topic_has_a_risk_value():
    missing = sorted({k for _, k in S.UPGRADES if k not in S._UP_RISK})
    assert not missing, f"หัวข้อเหล่านี้ไม่มีค่าใน _UP_RISK จะทำให้ assess ล่ม: {missing}"


def test_every_upgrade_topic_has_thai_and_english_replies():
    names = {t[0] for t in TOPICS}
    kinds = {k for _, k in S.UPGRADES if k != "crisis" and not k.startswith("kp_")}
    assert not sorted(kinds - names), "ไม่มีคำตอบภาษาไทย"
    assert not sorted(kinds - set(EN_TOPIC)), "ไม่มีคำตอบภาษาอังกฤษ"


@pytest.mark.parametrize("q,floor", [
    ("น่าจะโดนมอมยาในแก้วเหล้าตอนเที่ยว", 75), ("ไม่กินข้าวมาหลายวันเพราะกลัวอ้วน", 70), ("แฟนทุบโต๊ะแล้วหันมาตบหนู", 80),
    ("หลังผ่าตัด ดมยาแล้วไม่ตื่น", 80),
])
def test_thai_versions(q, floor):
    assert assess(q)["risk_shown"] >= floor


@pytest.mark.parametrize("q", ["โดนวางยาสลบตอนผ่าตัด", "อดอาหารสามวันตามหมอสั่งก่อนตรวจ", "วางยาฆ่าแมลงไว้ในครัว", "แม่ตีกลองเก่งมาก"])
def test_thai_everyday(q):
    assert assess(q)["risk_shown"] < 60
