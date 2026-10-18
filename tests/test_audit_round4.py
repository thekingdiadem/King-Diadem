"""รอบหาบั๊ก 4 — ไทย 312 · หลายภาษา 297 · เว็บแอป (ข้อความตัวอย่างจากชุดที่เคยหลุดหรือเตือนผิด)"""
import pytest

from core.kernel_voice import assess, compose


def _caught(a):
    return a["crisis"] or a["text_risk"] >= 50 or a["scam"] or a["disaster"] or a["intl_urgent"]


DANGER = [
    # ไทย: พูดอ้อม สแลง อีสาน แก๊งงานต่างประเทศ
    "ยืนอยู่บนดาดฟ้าคอนโด ชั้น25 ลาก่อนนะ", "ผูกเชือกไว้ที่ขื่อแล้ว", "เปิดแก๊สในห้องแล้ว", "ทานยาไปหมดขวดแล้วค่ะ",
    "พรุ่งนี้จะไม่มีกูอยู่แล้ว", "ไม่มีเหตุผลที่จะอยู่ต่อ", "cut แขนอีกแล้ว ปิดแผลไม่อยู่", "OD ยาแล้ว",
    "อีพ่อล้มบ่ฟื้น เฮ็ดจั่งได๋ดี", "แม่เป็นลม หายใจรวยริน", "ทั้งบ้านกินปลาปักเป้า ชาปาก",
    "เด็กเล่นในรถ ประตูล็อค อากาศร้อนมาก ร้องไห้อยู่ข้างใน", "ผัวกินเหล้าแล้วซ้อมทุกคืน", "อ้ายเพิ่นตีข่อย เจ็บหลาย",
    "ใครก็ได้ช่วยด้วย ผัวจะฆ่า", "หัวหน้าบังคับให้มีอะไรด้วย ไม่งั้นไล่ออก", "โอนเงินให้มิจไปแล้ว5หมื่น",
    "กู้แอปแล้วโดนทวงโหด โทรประจานหาเพื่อนทุกคน", "น้องชายไปทำงานกัมพูชา ถูกบังคับให้หลอกคน โดนช็อตไฟฟ้า",
    "เรือประมงบังคับทำงาน ไม่ได้ขึ้นฝั่งปีนึงแล้ว", "มีคนแปลกหน้าพาลูกขึ้นรถไป", "ก๊าซรั่วในคอนโด ได้กลิ่นแรงมาก",
    "ระเบิดในโรงงาน คนบาดเจ็บหลายคน",
    # อังกฤษ
    "i cant do this anymore, gonna end it tonite", "thinking about hanging myself", "k1ll myself", "sui cide seems like the only way",
    "im on the bridge rn and i think im gonna jump", "I am 82 and I fell in the bathroom, cannot get up, alone",
    "tuk tuk driver locked doors and wont let me out", "my grandson called saying he's in jail and needs money wired quick",
    "snake bit my leg in the garden, swelling fast",
    # จีน ญี่ปุ่น เกาหลี สเปน และภาษาอื่น
    "救命！有人闯进我家", "孩子在夜市走丢了", "我想从楼上跳下去", "もう限界、首を吊ろうと思う", "蛇に噛まれた、足が腫れている",
    "다리 위에 있어 뛰어내릴 거야", "방콕에서 납치당했어요", "ayuda, alguien entró a mi casa", "ich bringe mich heute um",
    "я покончу с собой сегодня", "النجدة، شخص اقتحم منزلي", "बाढ़ आ गई है, पानी बढ़ रहा है", "ຂ້ອຍຈະຂ້າຕົວຕາຍ",
    "toi muon chet, khong ai can toi", "có người giả công an bắt tôi chuyển tiền", "ငလျင်လှုပ်နေတယ်",
    # ตัวอักษรตกแต่งที่เคยหลบการตรวจ
    "k​i​l​l my​self", "อ​ยากตาย", "ｉ ｗａｎｔ ｔｏ ｄｉｅ", "i want to d̷i̷e̷",
]

BENIGN = [
    "I want to die my hair pink", "the drowning scene in Titanic made me cry", "地震の歴史について調べている",
    "the 2004 tsunami killed many in Phuket, writing a report", "we survived the flood of 2011, long time ago",
    "แม่ทำกับข้าวอร่อยจนอยากตาย", "เพลง อยากตาย ของวงอะไร", "ฆ่าตัวตายในละครเมื่อคืน ดราม่ามาก",
    "ซีรีส์เกาหลีเรื่องนี้นางเอกโดนลักพาตัว ลุ้นมาก", "ลูกเคยไข้ชักตอนเด็ก ตอนนี้โตแล้วไม่เป็นแล้ว",
    "วิธีปฐมพยาบาลคนจมน้ำ อยากเรียนไว้", "ดูสารคดีเรื่องการค้ามนุษย์ ได้ความรู้เยอะ", "แมวกัดสายชาร์จ ขาดอีกแล้ว",
    "ฝันว่าตกตึก ตื่นมาใจเต้น", "เชือกผูกรองเท้าขาด", "วิธีป้องกันแก๊งคอลเซ็นเตอร์มีอะไรบ้าง",
    "เมื่อปีที่แล้วเคยโดนมิจหลอก ตอนนี้ได้เงินคืนแล้ว", "ข่าวแก๊สรั่ว", "I am not going to kill myself",
]


@pytest.mark.parametrize("t", DANGER)
def test_danger_is_caught(t):
    assert _caught(assess(t)), t


@pytest.mark.parametrize("t", BENIGN)
def test_benign_is_calm(t):
    a = assess(t)
    assert not a["crisis"] and a["text_risk"] < 60, (t, a["text_risk"], a["topics"])


@pytest.mark.parametrize("t", ["อยู่เกาหลีผีน้อย โดนตำรวจจับ กลัวมาก", "蛇に噛まれた、足が腫れている",
                               "a man on the phone says he's police and I must transfer 200k"])
def test_reply_has_a_number_to_call(t):
    import re
    assert re.search(r"1669|191|1155|1441|119|02-572-8442", compose(t)), t


def test_compose_accepts_bytes_and_numbers():
    assert compose(b"I want to die") and compose(5)


def test_money_parser_does_not_cut_numbers():
    from core.engine_bridge import _after, _amounts
    assert _after("ค่าเช่า 1200 วัน", "ค่าเช่า") is None
    assert _after("ลงทุน 150%", "ลงทุน") is None
    assert _after("เงินเดือน 18,000", "เงินเดือน") == 18000
    assert _amounts("ค่าเช่า 1200 วัน 5,000 บาท") == [5000]


def test_debt_timeline_with_duplicate_names():
    from ENGINE.debt_engine import simulate_payoff
    row = simulate_payoff([{"name": "card", "balance": 1000, "annual_rate": 0},
                           {"name": "card", "balance": 5000, "annual_rate": 24}], 2000, "avalanche")["timeline"][0]
    assert round(sum(d["payment"] for d in row["debts"])) == 2000


def test_failed_logins_cannot_block_registration_of_an_ip():
    import app
    for i in range(40):
        app._login_failed(f"10.9.{i}.1|7.7.7.7")
    assert not app._login_blocked("reg|7.7.7.7")


def test_report_note_is_capped():
    from report_engine import _run_fate_audit
    out = _run_fate_audit({"route": "R" * 200000, "persona": "P" * 5000}, "hi")
    assert len(str(out)) < 5000


# ── รอบหาบั๊ก 5: กลุ่มที่ทดสอบน้อย ─────────────────────────────────────────
R5_DANGER = [
    "เกรดออกมา1.8 แม่บอกว่าไม่ต้องกลับบ้าน หนูนั่งอยู่บนดาดฟ้าตึกเรียนตอนนี้",
    "ไม่ไหวแล้ว เครียดเรื่องสอบ ไม่ได้นอนมา3วัน กินยานอนหลับของแม่ไปหมดแผง",
    "a guy on discord says he'll send my pics to my whole school if i dont pay him tonight",
    "ลูกไม่ดิ้นเลยตั้งแต่เมื่อวาน ท้อง36วีค", "I'm 34 weeks pregnant and have severe headache, blurry vision and swelling",
    "เมียเจ็บท้องคลอดอยู่บนรถ หัวเด็กโผล่แล้ว ทำยังไงดี", "ตกบ่อพักน้ำเสียในโรงงาน 2คนลงไปช่วยแล้วไม่ขึ้นมาเลย",
    "ไรเดอร์ล้มในซอย หายใจเสียงดังครืดคราด เรียกไม่ตอบ", "Grab driver got hit, he's lying on the road and bleeding from the head",
    "พ่อฉีดยาฆ่าหญ้าแล้วเป็นลม น้ำลายฟูมปาก ตัวสั่น", "sprayed chlorpyrifos all day, now my pupils are tiny, I'm sweating and twitching",
    "พ่อเป็นอัลไซเมอร์ เดินออกจากบ้านตั้งแต่เช้า ตอนนี้ยังหาไม่เจอ ฝนตกด้วย",
    "I'm deaf and can't call, someone is trying to break into my apartment right now",
    "ตอนนี้ยืนอยู่บนสะพานพระราม8 ไม่รู้จะทำยังไงต่อ", "I've been planning it for weeks, I have the rope, tonight is the night",
    "ไม่มีใครรักเลย ทุกคนจะดีขึ้นถ้าไม่มีกู", "took too much yaba, heart is racing over 180 and my chest hurts",
    "เถ้าแก่ไม่จ่ายค่าแรง ขู่ว่าถ้าไปแจ้งแรงงานจะให้ตำรวจจับส่งกลับพม่า",
]
R5_BENIGN = ["เพลงนี้เศร้าจนอยากตาย ฟังวนเลย", "ทำโปรเจคเรื่องภัยไซเบอร์ เช่น sextortion อยากได้สถิติ",
             "แจ้งเตือน: มิจฉาชีพอ้างเป็นตำรวจระบาด บอกพ่อแม่ด้วยนะ", "เกือบแพนิคตอนพรีเซนต์ แต่หายใจลึกๆแล้วผ่านไปได้",
             "how do I know if my friend is having a panic attack and how to help"]


@pytest.mark.parametrize("t", R5_DANGER)
def test_r5_danger_is_caught(t):
    assert _caught(assess(t)), t


@pytest.mark.parametrize("t", R5_BENIGN)
def test_r5_benign_is_calm(t):
    a = assess(t)
    assert not a["crisis"] and a["text_risk"] < 60, (t, a["text_risk"], a["topics"])


def test_emergency_comes_before_addiction_advice():
    assert "1669" in compose("ผมติดยาบ้า หยุดไม่ได้ วันนี้ใช้หนักจนใจเต้นเร็วมาก เจ็บหน้าอก")


def test_ask_page_hotlines_are_tappable_and_login_fields_are_labelled():
    import os
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ask = open(os.path.join(root, "static/ask.html"), encoding="utf-8").read()
    login = open(os.path.join(root, "static/login.html"), encoding="utf-8").read()
    assert "var HOTLINES" in ask and 'href="tel:$2"' in ask
    assert 'aria-label="อีเมล"' in login and 'aria-label="รหัสผ่าน"' in login


def test_google_login_without_client_id_goes_to_email_login(client, monkeypatch):
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    r = client.get("/login/google", follow_redirects=False)
    assert r.status_code in (302, 307) and "accounts.google.com" not in r.headers.get("location", "")
