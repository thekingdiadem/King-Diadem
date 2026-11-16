"""DriftZero รอบสุ่ม 16: ลองบนหน้าเว็บจริง — การ์ดแสดงครบ แต่ภาษาอังกฤษเขียน "6 day(s)" ดูไม่เป็นธรรมชาติ"""
from ENGINE.driftzero import audit, follow_up, lyla_voice


def test_english_plurals_read_naturally():
    a = audit("my shop is going under, 3000 dollars left and no one will lend me money")
    r = follow_up(a["text"], [q["key"] for q in a["asks"]], "500 a day, nothing coming in")
    assert "(s)" not in r["summary"]["en"] and "6 days" in r["summary"]["en"]
    one = lyla_voice(audit("we will hire 2 people, budget 3k per month, we have 50k cash, at least 20k must stay, manager approves"))
    assert "(s)" not in one["lyla"]["en"] and "(s)" not in one["summary"]["en"]
