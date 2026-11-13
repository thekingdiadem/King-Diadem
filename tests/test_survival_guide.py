"""คู่มือเอาชีวิตรอดฉบับเต็ม (core/survival_guide.py · /survival)
เจ้าของโปรเจกต์: "วิธีเอาชีวิตรอดแบบละเอียด ตรงนี้จะพลาดไม่ได้เลย"
เทสต์นี้ล็อกข้อเท็จจริงที่ช่วยชีวิต (ตรงกับ USGS · FEMA · NOAA · WHO · CDC · กาชาด) และห้ามคำแนะนำที่ทำให้คนตาย"""
import re

import pytest

from core import survival_guide as sg

SECTIONS = ("signs", "before", "during", "after", "vulnerable", "myths")


def _all(key, lang=0, secs=SECTIONS):
    return " ".join(r[lang] for s in secs for r in sg.HAZARDS[key][s])


def test_every_hazard_is_complete_in_thai_and_english():
    assert set(sg.ORDER) == set(sg.HAZARDS) and len(sg.ORDER) >= 14
    for key, h in sg.HAZARDS.items():
        assert h["name"][0] and h["name"][1] and h["icon"], key
        assert len(h["during"]) >= 2 and h["before"] and h["after"] and h["signs"], key
        assert len(h["sources"]) >= 2, key                              # ทุกภัยมีแหล่งอ้างอิงอย่างน้อย 2 แห่ง
        for sec in SECTIONS:
            for th, en in h[sec]:
                assert re.search(r"[ก-๙]", th) and not re.search(r"[ก-๙]", en) and en.strip(), (key, sec, en[:40])


@pytest.mark.parametrize("key,th,en", [
    # แผ่นดินไหว: หมอบ ป้อง เกาะ · ไม่วิ่งออกระหว่างสั่น · ไม่ใช้ลิฟต์ · ริมทะเลสั่นแรง/นาน = ขึ้นที่สูงเลย
    ("quake", ["หมอบ ป้อง เกาะ", "อย่าวิ่งออก", "ห้ามใช้ลิฟต์", "ขึ้นที่สูงทันที", "อาฟเตอร์ช็อก"],
     ["Drop, Cover, Hold On", "don't run outside", "Never use lifts", "high ground"]),
    # สึนามิ: สัญญาณธรรมชาติ · ไม่รอประกาศ · 30 ม./3 กม. · หลายลูก ลูกแรกไม่ใหญ่สุด · ห้ามลงไปดูทะเลลด
    ("tsunami", ["น้ำทะเลลดลงผิดปกติ", "30 เมตร", "3 กม.", "ลูกแรกมักไม่ใช่ลูกใหญ่ที่สุด", "ชั้น 3"],
     ["sea suddenly drawing back", "30 m", "3 km", "first is often not the largest"]),
    # น้ำท่วม: 15 ซม. ล้ม · 30 ซม. รถลอย · ไม่ขึ้นห้องใต้หลังคาปิดตาย · ฉี่หนู · ต้มน้ำ 1 นาที · ห้ามปั่นไฟในบ้าน
    ("flood", ["15 ซม.", "30 ซม.", "ห้องใต้หลังคาที่ปิดตาย", "ฉี่หนู", "อย่างน้อย 1 นาที", "คาร์บอนมอนอกไซด์"],
     ["15 cm", "30 cm", "closed attic", "leptospirosis", "carbon monoxide"]),
    ("storm", ["ตาพายุ", "ห้องด้านในที่ไม่มีหน้าต่าง", "สายไฟ"], ["eye", "interior room", "live"]),
    ("landslide", ["ด้านข้าง", "อย่าวิ่งตามทางน้ำ"], ["sideways", "never down a channel"]),
    ("wildfire", ["นอนลงที่พื้นรถ", "N95"], ["lie on the floor", "N95"]),
    # ฮีตสโตรก: โทร 1669 + ลดอุณหภูมิเร็ว · ไม่ป้อนน้ำคนไม่รู้สึกตัว · ไม่ทิ้งเด็กในรถ
    ("heat", ["1669", "แช่น้ำเย็น", "ห้ามป้อนน้ำคนที่ไม่รู้สึกตัว", "ห้ามทิ้งเด็ก"], ["1669", "immersion", "not fully alert", "Never leave children"]),
    ("haze", ["N95", "HEPA", "Air4Thai"], ["N95", "HEPA"]),
    # ฟ้าผ่า: ฟ้าร้องเข้าอาคาร · รอ 30 นาที · ผู้ถูกผ่าไม่มีไฟค้าง เริ่ม CPR
    ("lightning", ["ฟ้าร้องเมื่อไหร่ เข้าอาคารทันที", "รอ 30 นาที", "ไม่มีไฟฟ้าค้าง", "CPR"], ["When thunder roars", "30 minutes", "no charge", "CPR"]),
    ("cold", ["เตาถ่าน", "คาร์บอนมอนอกไซด์", "ถอดเสื้อผ้าเปียก"], ["charcoal", "carbon monoxide", "wet clothing"]),
    ("drought", ["อย่างน้อย 1 นาที", "2 หยด", "30 นาที"], ["rolling boil", "2 drops", "30 minutes"]),
    # ไฟไหม้: ออกทันที ไม่ใช้ลิฟต์ · ก้มต่ำ · แตะประตูด้วยหลังมือ · หยุด ล้ม กลิ้ง · แผลไฟไหม้ราดน้ำ 20 นาที
    ("fire", ["ไม่ใช้ลิฟต์", "ก้มต่ำ", "หลังมือ", "หยุด ล้มลง กลิ้ง", "20 นาที", "199"], ["never use lifts", "get low", "back of your hand", "stop, drop and roll", "20 minutes"]),
    ("gas", ["ห้ามกดสวิตช์", "โทรจากข้างนอก", "เหนือลม"], ["no switches", "call from there", "upwind"]),
    ("volcano", ["ลาฮาร์", "N95"], ["lahar", "N95"]),
])
def test_life_saving_facts_are_present(key, th, en):
    t, n = _all(key, 0), _all(key, 1)
    for w in th:
        assert w in t, (key, w)
    for w in en:
        assert w.lower() in n.lower(), (key, w)


@pytest.mark.parametrize("key,bad", [
    # คำแนะนำที่เคยทำให้คนตาย — ต้องอยู่ในหมวดความเชื่อผิดเท่านั้น ไม่ใช่คำแนะนำ
    ("quake", r"วงกบ|doorway|สามเหลี่ยมชีวิต|triangle of life"),
    ("tsunami", r"ลงไปดู|walking out to look"),
    ("storm", r"ติดเทป|tap(e|ing)"),
    ("lightning", r"ยางรถ|tyres"),
    ("heat", r"เหล้า|alcohol"),
    ("cold", r"เหล้า|alcohol|ถู|rubbing"),
])
def test_deadly_myths_only_appear_as_myths(key, bad):
    advice = _all(key, 0, ("signs", "before", "during", "after", "vulnerable")) + _all(key, 1, ("signs", "before", "during", "after", "vulnerable"))
    assert not re.search(bad, advice, re.I), (key, bad)
    myths = _all(key, 0, ("myths",)) + _all(key, 1, ("myths",))
    assert re.search(bad, myths, re.I) and myths.count("✕") >= 2


def test_first_during_step_is_the_life_saving_action():
    firsts = {k: h["during"][0][0] for k, h in sg.HAZARDS.items()}
    assert "หมอบ ป้อง เกาะ" in firsts["quake"] and "ที่สูง" in firsts["tsunami"] and "1669" in firsts["heat"]
    assert "ออกทันที" in firsts["fire"] and "เข้าอาคาร" in firsts["lightning"]


def test_only_hotlines_we_are_sure_of():
    assert {n for n, _, _ in sg.HOTLINES} == {"1784", "1669", "191", "199", "1323"}
    numbers = set(re.findall(r"(?<![\d.])1\d{3}(?![\d.])", " ".join(_all(k) for k in sg.HAZARDS)))
    assert numbers <= {"1784", "1669", "191", "199", "1323"}, numbers


def test_page_renders_without_scripts_in_both_languages(client):
    th = client.get("/survival")
    assert th.status_code == 200 and "<script" not in th.text and 'lang="th"' in th.text
    for k in sg.ORDER:
        assert f'id="{k}"' in th.text
    assert 'href="tel:1669"' in th.text and "หมอบ ป้อง เกาะ" in th.text
    en = client.get("/survival?lang=en").text
    assert 'lang="en"' in en and "Drop, Cover, Hold On" in en and "ภาษาไทย" in en
    assert client.get("/survival?lang=<script>").text == th.text       # ภาษาแปลกๆ = ไทย ไม่สะท้อนกลับ


def test_chat_links_to_the_right_guide(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    assert client.post("/run", json={"input": "น้ำท่วมบ้านแล้วตอนนี้ ระดับน้ำถึงเข่า"}).json().get("survival") == "flood"
    assert client.post("/run", json={"input": "สวัสดีค่ะ"}).json().get("survival") is None


def test_chat_card_is_saved_and_rendered():
    from tests._front import front_page
    page = front_page()
    assert "s: d.survival" in page and "survivalCard(m.s)" in page and "function survivalCard(k)" in page


# ── แชทตอนไม่มี AI: ภัยที่เดิมตอบผิด (ช่องโหว่ที่เจอระหว่างทำคู่มือ) ──────────────────────
@pytest.mark.parametrize("text,must", [
    ("อยู่ภูเก็ต น้ำทะเลลดลงผิดปกติมาก", "ขึ้นที่สูง"),            # เดิม: คำตอบกลาง "เขียนสิ่งที่เกิดขึ้นเป็นประโยคเดียว"
    ("ได้ยินเสียงเตือนสึนามิ", "30 เมตร"),
    ("the sea is pulling back fast at the beach", "high ground"),  # เดิม: "This needs a doctor now"
    ("tsunami warning siren", "high ground"),                       # เดิม: "drop, cover" ของแผ่นดินไหว
    ("หนาวมากตัวสั่น จุดเตาถ่านในห้องได้ไหม", "คาร์บอนมอนอกไซด์"),  # เดิม: คำตอบกลาง
    ("generator in the garage running all night", "carbon monoxide"),
    ("อยู่บาหลี ภูเขาไฟระเบิด", "N95"),
    ("ดินเริ่มแยก ต้นไม้เอียง ฝนตกหนัก", "ด้านข้าง"),
    ("ฝนตกหนักสามวันแล้ว ดินหลังบ้านเริ่มแยก", "ด้านข้าง"),          # บริบทมาก่อนสัญญาณก็ต้องจับได้
    ("น้ำในห้วยขุ่นข้นทันที ทั้งที่ฝนยังตกอยู่บนเขา", "ด้านข้าง"),
    ("แผ่นดินไหว ตึกสั่น", "หมอบ"),                                 # ของเดิมต้องยังถูก
])
def test_chat_answers_every_hazard_with_the_first_life_saving_step(text, must):
    from core.kernel_voice import compose
    assert must in compose(text)


@pytest.mark.parametrize("text", ["ทะเลวันนี้สวยมาก", "น้ำลงแล้วไปเดินหาดกัน", "ดินในกระถางแตก", "เราใช้เตาถ่านปิ้งหมูหน้าบ้าน",
                                  "ปลูกต้นไม้บนเนิน ดินแตกระแหงเพราะแล้ง"])
def test_ordinary_sentences_are_not_mistaken_for_disasters(text):
    from core.kernel_voice import compose
    out = compose(text)
    assert "ขึ้นที่สูง" not in out and "คาร์บอนมอนอกไซด์" not in out and "ขวางทิศดินไหล" not in out
