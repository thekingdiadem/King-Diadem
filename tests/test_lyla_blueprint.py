"""LYLA BELIEF IN THE UNIVERSAL — blueprint ของเจ้าของโปรเจกต์ (KERNEL/lyla-belief-in-the-universal.md)

ใส่เข้า LYLA_SYSTEM เฉพาะส่วนที่ยังไม่มี · ส่วนที่ VEGA มีแล้ว (พื้นรอด K4 · ทางออก K5 · ไม่เร่ง K7 · RC-3)
ไม่ใส่ซ้ำ · เดิม LYLA ถูกสั่งให้ "ชื่นชมจริงๆ" ซึ่งขัดกับหลักไม่ยกยอ
"""
from pathlib import Path

import core.llm_gemini as L


def test_lyla_has_the_missing_axes():
    p = L.LYLA_SYSTEM
    for needle in ("LYLA BELIEF IN THE UNIVERSAL", "ยืนข้างความจริง", "อยู่ต่อ ออก หรือปฏิเสธได้อย่างปลอดภัย",
                   "ตรวจอำนาจ", "ถือเป็นโมฆะ", "ความเงียบ", "ยกเว้นเรื่องความปลอดภัยของชีวิต",
                   "ไม่ชมเกินจริง", "ผู้สร้างหรือแพลตฟอร์ม", "ทรายละเอียด ทรายหยาบ ถ่าน หิน", "ไม่ใช่ตัวคน"):
        assert needle in p, needle


def test_what_vega_already_has_is_not_duplicated_into_lyla():
    assert "K4 Floor Before Growth" in L.VEGA_SYSTEM and "K5 Exit Must Exist" in L.VEGA_SYSTEM
    lyla_only = L.LYLA_SYSTEM[len(L.KD_DNA):]
    for dup in ("AXIS 2", "AXIS 3", "พื้นรอด:", "ทางออก:", "ไม่เร่งให้ตัดสินใจ", "ไม่ขายความหวัง"):
        assert dup not in lyla_only, dup
    assert "VEGA" not in lyla_only.split("── LYLA BELIEF")[1].split("── EMOJI")[0]   # หมายเหตุผู้ดูแลอยู่ในคอมเมนต์ ไม่ใช่ใน prompt


def test_no_overpraise_instruction_left():
    assert "ชื่นชมจริงๆ" not in L.LYLA_SYSTEM and "ชื่นชมจริงๆ" not in L.WORK_WIN_SYSTEM
    assert "ไม่ยกยอเกินจริง" in L.WORK_WIN_SYSTEM


def test_blueprint_document_kept_in_full():
    doc = (Path(__file__).resolve().parent.parent / "KERNEL" / "lyla-belief-in-the-universal.md").read_text(encoding="utf-8")
    for needle in ("A human must always have at least one real choice.", "AXIS 5 — SILENCE", "MEMORY TRUTH",
                   "ความจริงเพียงหนึ่งเดียว", "อยู่ตรงไหนในระบบ"):
        assert needle in doc, needle
