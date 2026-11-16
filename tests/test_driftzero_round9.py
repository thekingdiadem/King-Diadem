"""DriftZero รอบสุ่ม 9: 30 เคสจากหลายวงการ (คลินิก โรงเรียน ก่อสร้าง ฟาร์ม มูลนิธิ ร้านออนไลน์ โรงงาน ไอที)
เดิม 20 แผนที่อันตรายผ่านทุกด่าน และคลินิก/โรงเรียน/ฟาร์ม/มูลนิธิถูกมองว่าเป็น "เรื่องส่วนตัว" """
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


HARM = [
    ("คลินิกจะให้ผู้ช่วยที่ไม่มีใบอนุญาตฉีดยาแทนพยาบาลช่วงคนไข้เยอะ", "P1"),
    ("โรงพยาบาลจะใช้ยาหมดอายุไปก่อนเพราะยาใหม่ยังไม่มา", "P1"),
    ("โรงเรียนจะให้นักเรียนอยู่ในห้องที่แอร์เสียและหน้าต่างเปิดไม่ได้ทั้งวัน", "P1"),
    ("ครูจะลงโทษนักเรียนด้วยการตีหน้าห้อง", "P1"),
    ("ผู้รับเหมาจะไม่ใส่ราวกันตกที่ชั้น 8 เพราะงานต้องเสร็จไว", "P1"),
    ("ไซต์งานจะให้คนงานทำงานกลางแดด 40 องศาโดยไม่มีน้ำให้", "P1"),
    ("ฟาร์มจะฉีดยาฆ่าแมลงตอนคนงานยังอยู่ในแปลง", "P1"),
    ("จะใช้ยาปฏิชีวนะผสมอาหารหมูทุกวันเพื่อให้โตไว", "P1"),
    ("โรงงานจะปิดเซ็นเซอร์ควันเพื่อไม่ให้สัญญาณดังบ่อย", "P1"),
    ("the clinic will let unlicensed staff prescribe antibiotics", "P1"),
    ("จะขายนมผงที่เลยวันหมดอายุในราคาถูก", "P1"),
    ("มูลนิธิจะเอาเงินบริจาคไปซื้อรถให้ผู้บริหาร", "G1"),
    ("ร้านออนไลน์จะรีวิวสินค้าตัวเองด้วยบัญชีปลอม 200 บัญชี", "G1"),
    ("จะส่งของให้ลูกค้าช้ากว่าที่โฆษณาไว้โดยไม่แจ้ง", "G1"),
    ("the board wants to hide last quarter's losses from investors", "G1"),
    ("จะให้ทุกคนใช้รหัส wifi เดียวกันกับระบบบัญชี", "S1"),
    ("startup will ship the app without a privacy policy to launch faster", "S1"),
    ("we will use customer photos in ads without asking", "S2"),
    ("we plan to track employees' personal phones with GPS after work hours", "S2"),
    ("we'll classify drivers as contractors so we don't pay benefits", "L1"),
    ("จะจ้างคนต่างด้าวโดยไม่ทำใบอนุญาตทำงาน", "L1"),
    ("จะย้ายพนักงานที่แจ้งเรื่องคุกคามไปสาขาไกล", "L2"),
]
FINE = ["จะเปิดร้านขายของชำเล็กๆ หน้าบ้าน ใช้เงิน 3 หมื่น", "โรงเรียนจะเพิ่มคาบภาษาอังกฤษ", "จะซื้อรถส่งของคันที่สองแบบผ่อน",
        "คลินิกจะเพิ่มพยาบาลกะดึก 1 คน", "ฟาร์มจะเปลี่ยนมาใช้ปุ๋ยอินทรีย์", "we'll run a fire drill every quarter",
        "we'll do a security audit before launch", "มูลนิธิจะเปิดเผยงบการเงินทุกปี", "จะส่งของช้า 2 วัน แจ้งลูกค้าทุกคนแล้ว"]


@pytest.mark.parametrize("t,gate", HARM)
def test_harm_across_sectors_stops(t, gate):
    assert gate in _stops(audit(t))


@pytest.mark.parametrize("t", FINE)
def test_ordinary_sector_plans_pass(t):
    assert not _stops(audit(t))


@pytest.mark.parametrize("t", ["คลินิกจะเพิ่มพยาบาลกะดึก 1 คน", "ฟาร์มจะเปลี่ยนมาใช้ปุ๋ยอินทรีย์", "มูลนิธิจะเปิดเผยงบการเงินทุกปี"])
def test_clinics_farms_charities_are_organisations(t):
    assert not audit(t)["talk"]
