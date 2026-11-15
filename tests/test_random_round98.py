"""รอบสุ่ม 98: เนื้อหาคำตอบต้องตรงกับเหตุการณ์ (ไม่ใช่แค่ตัวเลขความเสี่ยง)"""
import re

import pytest
from core.kernel_voice import assess, compose

CASES = [("บ้านไฟไหม้ ออกไม่ได้", "199"), ("ได้กลิ่นแก๊สรั่วในห้องครัว", "สวิตช์|ปลั๊ก|ไฟแช็ก"), ("แม่หายใจไม่ออก ปากเขียว", "1669"),
         ("สามีตีทุกคืน", "191|1300"), ("อยากตาย", "1323"), ("แท็กซี่ล็อกประตูไม่ให้ลง", "191"),
         ("เพื่อนโพสต์รูปยาเต็มมือ เขียนว่าลาก่อน", "1669|1323"), ("โดนแก๊งคอลเซ็นเตอร์หลอกโอนเงิน", "1441|ธนาคาร"),
         ("หมาท้องบวมเป่ง พยายามอ้วกแต่ไม่มีอะไรออก", "โรงพยาบาลสัตว์"), ("หลงป่าบนดอย มืดแล้ว แบตเหลือ 5% น้ำหมด", "ตำแหน่ง|1669|191"),
         ("my house is on fire and I can't get out", "fire|911|112|199"), ("I smell gas in my apartment", "switch|spark|outside|leave"),
         ("my dog's belly is swollen and he's trying to vomit", "vet")]


@pytest.mark.parametrize("q,need", CASES)
def test_reply_matches_the_situation(q, need):
    assert re.search(need, compose(q, footer=False), re.I)


@pytest.mark.parametrize("q", ["สามีตีทุกคืน", "ผัวตีทุกคืน", "แฟนตบเป็นประจำ", "พ่อเตะหลายครั้งแล้ว"])
def test_repeated_domestic_violence_with_any_frequency_word(q):
    # "สามีตีทุกคืน" เคยได้ 0 และคำตอบเรื่องความรัก "เรื่องใจไม่ต้องรีบตัดสิน"
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", ["แฟนตบมือเชียร์บอลทุกอาทิตย์", "ผัวเตะบอลกับเพื่อน", "สามีตีกลองทุกคืน", "พ่อตีกอล์ฟทุกเช้า"])
def test_clapping_and_sport_are_not_violence(q):
    assert assess(q)["risk_shown"] < 60
