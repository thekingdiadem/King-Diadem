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


@pytest.mark.parametrize("text,opener", [
    ("Công an gọi bảo chuyển tiền vào tài khoản an toàn", "Đây rất giống lừa đảo"),
    ("Có người gọi nói là ngân hàng, xin mã OTP", "Đây rất giống lừa đảo"),
    ("Tôi trúng thưởng xe máy nhưng phải đóng phí trước", "Đây rất giống lừa đảo"),
    ("警察打电话让我把钱转到安全账户", "这很像诈骗"),
    ("警察から電話で安全な口座に振り込めと言われた", "詐欺の可能性が高い"),
    ("경찰이라며 안전계좌로 돈을 보내래요", "보이스피싱"),
    ("Me llamó la policía y dice que transfiera mi dinero a una cuenta segura", "Esto tiene señales de estafa"),
])
def test_offline_scam_answer_is_in_the_users_language(text, opener):
    """ตอนไม่มี AI: เดิมเวียดนามได้คำตอบภาษาอังกฤษ ญี่ปุ่น/สเปนบางประโยคได้คำแนะนำทั่วไป ไม่ได้เตือนมิจฉาชีพ"""
    from core.kernel_voice import compose
    out = compose(text)
    assert out.startswith(opener), out[:80]
    assert "(75/100)" in out and "Risk right now" not in out


def test_vietnamese_answers_show_risk_in_vietnamese():
    from core.kernel_voice import compose
    assert "Rủi ro lúc này" in compose("Tôi mất ngủ nhiều ngày rồi")
