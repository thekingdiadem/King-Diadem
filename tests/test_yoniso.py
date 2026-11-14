"""โยนิโสมนสิการ 4 วิธีคิดอยู่ในคำสั่งของ LYLA (เจ้าของโปรเจกต์ส่งหลักนี้มา พ.ย. 2569)"""
from core import llm_gemini


def test_four_ways_of_wise_attention_in_prompt():
    src = open(llm_gemini.__file__, encoding="utf-8").read()
    for k in ("สืบสาวเหตุปัจจัย", "แยกแยะส่วนประกอบ", "อริยสัจ 4", "รู้เท่าทันธรรมดา", "ไม่ใช่หาคนผิด"):
        assert k in src, k
