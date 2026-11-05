"""การเรียน (ทุกระดับ ในไทยและต่างประเทศ) · กฎหมายไทย · ธุรกิจ — core/knowledge_th.py
รอบแรกของชุดวัดผล 500 ข้อ: การเรียน 28% · กฎหมาย 26% · ธุรกิจ 23% (ส่วนใหญ่ได้คำตอบกลาง)
เทสต์นี้ใช้ประโยคที่ "ไม่อยู่ใน" ชุดวัดผล เพื่อดูว่าตอบได้จริง ไม่ใช่จำแค่ข้อสอบ"""
import pytest

from core.kernel_voice import compose
from core.knowledge_th import KNOWLEDGE


@pytest.mark.parametrize("text,must", [
    ("ลูกสอบตกคณิต ม.2 ทำไงดี", "สอบ"), ("อยากไปเรียนป.โทที่ญี่ปุ่น มีทุนไหม", "MEXT"),
    ("เรียนต่อที่ออสเตรเลียดีไหม", "IELTS"), ("อายุ 40 แล้วอยากเรียนให้จบ ม.6", "กศน"),
    ("IELTS ได้ 5.5 อยากได้ 7", "ข้อสอบ"), ("อยากเรียนเขียนโปรแกรมเองที่บ้าน", "Python"),
    ("อยากเรียนภาษาจีน", "ฟัง"), ("อยากให้ลูกเรียนโฮมสคูล", "เขตพื้นที่การศึกษา"),
    ("ไม่มีเงินจ่ายค่าเทอมเทอมหน้า", "กยศ"), ("อยากเป็นนักเรียนแลกเปลี่ยน", "AFS"),
])
def test_study_all_levels_and_abroad(text, must):
    assert must in compose(text)


@pytest.mark.parametrize("text,must", [
    ("เจ้าของหอไม่คืนเงินมัดจำห้อง 5000", "1166"), ("โดนฟ้องเรื่องหนี้บัตรเครดิต ศาลนัดเดือนหน้า", "กองทุนยุติธรรม"),
    ("อยากทำพินัยกรรมยกบ้านให้ลูก", "พยาน 2 คน"), ("มีคนโพสต์ด่าเราในเฟสหาว่าโกง", "3 เดือน"),
    ("ซื้อทีวีมาเสียภายในสัปดาห์ ร้านไม่ยอมเปลี่ยน", "1166"), ("นายจ้างยึดพาสปอร์ตแรงงานเมียนมา", "1300"),
    ("ถูกเลิกจ้างทันทีไม่บอกล่วงหน้า", "ค่าตกใจ"), ("อยากจดทะเบียนสมรสกับแฟนผู้หญิง", "สมรสเท่าเทียม"),
])
def test_thai_law_with_the_right_agency(text, must):
    assert must in compose(text)


@pytest.mark.parametrize("text,must", [
    ("ร้านก๋วยเตี๋ยวยอดตกช่วงนี้", "ตัวเลข"), ("จะตั้งราคาขนมเค้กยังไงดี", "ต้นทุน"),
    ("หุ้นส่วนแอบเอาเงินร้านไปใช้", "บัญชี"), ("อยากขายสินค้าไปอเมริกา", "DITP"),
    ("ร้านกาแฟเปิดใหม่ควรเช่าที่สัญญา 3 ปีไหม", "ค่าเช่า"), ("ลูกน้องลาออกพร้อมกันสี่คน", "เหตุร่วม"),
    ("อยากหานักลงทุนให้สตาร์ทอัพ", "ลูกค้าจริง"), ("สนใจซื้อแฟรนไชส์ชานมไข่มุก", "สัญญา"),
])
def test_business_from_small_shop_to_startup(text, must):
    assert must in compose(text)


@pytest.mark.parametrize("text,not_key", [
    ("ถูกตำรวจเรียกเงินใต้โต๊ะ", "ทางนี้ได้เงินเร็ว"),            # ผู้ถูกเรียกเงิน ไม่ใช่คนหาเงินไม่สุจริต
])
def test_the_user_is_not_mistaken_for_someone_else(text, not_key):
    assert not_key not in compose(text)


def test_sexual_harassment_gets_numbers_not_a_generic_answer():
    out = compose("ถูกคุกคามทางเพศในรถสาธารณะ")
    assert "191" in out and "1300" in out and "ไม่ใช่ความผิดของคุณ" in out


def test_every_answer_respects_the_three_path_canon():
    for key, _, d in KNOWLEDGE:
        assert 1 <= len(d["paths"]) <= 3, key
        assert d["ask"].endswith("?"), key
