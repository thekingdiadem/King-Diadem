"""ข้อมูลลับที่ผู้ใช้พิมพ์ไม่ต้องส่งให้ AI ภายนอก (ข่าว พ.ย. 2569: ผู้ให้บริการ AI บางรายเก็บ/รั่ว prompt)
ซ่อนก่อนส่งที่จุดเดียว (_build_contents) — เบอร์ฉุกเฉิน เงิน อายุ ค่าเลือด ต้องอยู่ครบ"""
import pytest

from core.llm_gemini import _build_contents, scrub_secrets


@pytest.mark.parametrize("text,gone,kept", [
    ("โอนไปบัญชี 123-4-56789-0 แล้ว", "56789", "7890"),
    ("บัตรประชาชน 1103700012345", "11037000", "2345"),
    ("เบอร์ 081-234-5678 โทรมาบอกว่าเป็นตำรวจ", "081-234", "5678"),
    ("password: hunter22", "hunter22", "password"),
    ("รหัส OTP 482913 ส่งให้เขาไปแล้ว", "482913", "OTP"),
    ("ติดต่อ boss@gmail.com", "boss@gmail.com", "[อีเมล]"),
])
def test_secrets_are_hidden(text, gone, kept):
    out = scrub_secrets(text)
    assert gone not in out and kept in out


@pytest.mark.parametrize("text", ["โทร 1669 ด่วน แม่หมดสติ", "เงินเดือน 25,000 บาท อายุ 45 ปี", "ค่าไต eGFR 45 ครีเอตินีน 1.6",
                                  "ยอด 1,250,000 บาท", "ความดัน 150/95", "โทร 191 หรือ 1323"])
def test_useful_numbers_are_kept(text):
    assert scrub_secrets(text) == text


def test_every_message_sent_to_the_ai_is_scrubbed():
    hist = [{"role": "user", "content": "บัญชีผม 1234567890123"}, {"role": "assistant", "content": "โอเค"}]
    contents = _build_contents(hist, "ส่ง OTP 556677 ไปแล้ว อีเมล me@x.co", "บริบท 0899999999")
    blob = repr(contents)
    for secret in ("1234567890123", "556677", "me@x.co", "0899999999"):
        assert secret not in blob, secret
