"""มิจฉาชีพในภาษาที่หน้าเว็บรองรับ (เวียดนาม จีน ญี่ปุ่น เกาหลี สเปน)
เดิม "Công an gọi bảo chuyển tiền vào tài khoản an toàn" (ตำรวจโทรมาให้โอนเข้าบัญชีปลอดภัย) ได้ Risk 0 ไม่มีสัญญาณเลย"""
import pytest

from core.kernel_voice import assess


@pytest.mark.parametrize("text", [
    "Công an gọi bảo chuyển tiền vào tài khoản an toàn",
    "Có người gọi nói là ngân hàng, xin mã OTP",
    "Tôi trúng thưởng xe máy nhưng phải đóng phí trước",
    "警察打电话让我把钱转到安全账户",
    "警察から電話で安全な口座に振り込めと言われた",
    "경찰이라며 안전계좌로 돈을 보내래요",
    "Me llamó la policía y dice que transfiera mi dinero a una cuenta segura",
    "Ganaste un premio, solo debes pagar una comisión",
])
def test_scam_seen_in_every_ui_language(text):
    a = assess(text)
    assert a.get("scam") and a["text_risk"] >= 60


@pytest.mark.parametrize("text", [
    "Tôi chuyển tiền qua ngân hàng cho mẹ", "Ngân hàng gửi mã OTP khi tôi tự đăng nhập",
    "我在银行转账给妈妈", "銀行で振り込みをした", "은행에서 엄마에게 송금했어요",
    "Fui al banco a transferir dinero a mi madre", "Mi papá es policía",
])
def test_everyday_banking_is_not_a_scam(text):
    a = assess(text)
    assert not a.get("scam") and a["text_risk"] < 60
