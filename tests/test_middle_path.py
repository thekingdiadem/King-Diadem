"""ตัวตรวจทางสายกลาง — ไม่เชียร์อย่างเดียว ไม่ห้ามจนไม่เหลือทาง"""
from pathlib import Path

from core import middle_path as mp


def test_upside_only_gets_downside_question():
    r = mp.balance("จะกู้เงินมาลงทุนคริปโต 2 แสน", "ลุยเลยค่ะ โอกาสทองแบบนี้ไม่ได้มีบ่อย\n\n— LYLA ◈")
    assert "เสียได้มากสุดเท่าไหร่" in r and r.rstrip().endswith("— LYLA ◈")


def test_cheer_with_risk_already_is_left_alone():
    rep = "ลุยเลยค่ะ แต่เก็บเงินสำรองไว้ 6 เดือน และคิดไว้ก่อนว่าถ้าพลาดจะเสียเท่าไหร่"
    assert mp.balance("อยากลงทุนเปิดร้าน", rep) == rep


def test_only_prohibitions_gets_a_way_forward():
    r = mp.balance("I want to quit my job", "Don't quit. Never decide angry. Stop and avoid big moves.")
    assert "smallest step" in r


def test_prohibitions_with_steps_left_alone():
    rep = "อย่ารีบ ไม่ควรเซ็น ห้ามโอนก่อน\n1. โทรถามธนาคาร\n2. ขอสำเนาสัญญา"
    assert mp.balance("จะกู้ซื้อบ้าน", rep) == rep


def test_everyday_and_crisis_untouched():
    assert mp.balance("ขอสูตรต้มยำ", "ใส่ข่าตะไคร้ค่ะ") == "ใส่ข่าตะไคร้ค่ะ"
    rep = "อย่า หยุด ห้าม"
    assert mp.balance("อยากตาย", rep, {"crisis": True}) == rep


def test_wired_after_safety_line_and_in_health():
    src = Path("app.py").read_text(encoding="utf-8")
    assert src.index("ensure_safety_line(user_input") < src.index("_mp_balance(user_input")
    assert '"middle_path": _middle_path_stats()' in src
