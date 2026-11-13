"""กลโกงไซเบอร์ในอีก 5 ภาษาของเว็บ (core/cyber_scam.py · INTL / REPLY_INTL)

แรงงานและนักท่องเที่ยวในไทยโดนหลอกแบบเดียวกับคนไทย — เดิมเกือบทุกสถานการณ์ได้ Risk 0
และ "tải ứng dụng từ link, file apk" ได้ "I'm sorry this happened" เป็นภาษาอังกฤษ ทั้งที่ยังไม่ได้ติดตั้ง
"""
import re

import pytest

from core.kernel_voice import assess, compose

FIRST = {'ja': [('交通違反の罰金が未納とSMSが来た、リンクから支払えと', 'sms_link'), ('リンクからアプリをインストールしてと言われた、apkファイル', 'apk'), ('アプリにユーザー補助の権限を許可してしまった', 'accessibility'), ('警察を名乗る人から電話、現金を引き出して金を買え、家に取りに行くと', 'courier_cash'), ('画面でロボットではないを押したらOTPを入力しろと出た', 'otp_page'), ('友達からLINEでお金を貸してと来た', 'friend_account')], 'zh': [('收到短信说有交通罚单没交，让点链接付款', 'sms_link'), ('对方让我点链接下载安装一个apk', 'apk'), ('我给那个应用开了无障碍权限', 'accessibility'), ('自称泰国警察打电话，让我取现金买黄金，会派人上门取', 'courier_cash'), ('网页让我点我不是机器人然后输入验证码', 'otp_page'), ('朋友微信找我借钱', 'friend_account')], 'ko': [('교통 벌금 미납이라고 문자가 왔어 링크로 내래', 'sms_link'), ('링크로 앱을 설치하래 apk 파일이야', 'apk'), ('앱에 접근성 권한을 허용해 버렸어', 'accessibility'), ('경찰이라면서 현금 찾아서 금을 사래 집으로 가지러 온대', 'courier_cash'), ('로봇이 아닙니다 누르니까 인증번호 입력하래', 'otp_page'), ('친구가 카톡으로 돈 빌려달래', 'friend_account')], 'es': [('me llegó un SMS de una multa de tráfico pendiente con un enlace para pagar', 'sms_link'), ('me pidieron instalar una app desde un enlace, un archivo apk', 'apk'), ('le di permiso de accesibilidad a la app', 'accessibility'), ('un supuesto policía me dijo que saque efectivo y compre oro, que vendrán a recogerlo a casa', 'courier_cash'), ('la página tenía un no soy un robot y luego pedía el código OTP', 'otp_page'), ('un amigo me escribió por WhatsApp pidiendo dinero prestado', 'friend_account')], 'vi': [('nhận tin nhắn phạt nguội giao thông, bảo bấm link để nộp phạt', 'sms_link'), ('họ bảo tải ứng dụng từ link, file apk', 'apk'), ('tôi đã cấp quyền trợ năng cho ứng dụng đó', 'accessibility'), ('người xưng là công an bảo rút tiền mặt mua vàng, sẽ cho người đến nhà lấy', 'courier_cash'), ('trang web bắt bấm tôi không phải robot rồi nhập mã OTP', 'otp_page'), ('bạn nhắn Zalo hỏi mượn tiền', 'friend_account')]}
MORE = {'ja': ['不在通知のSMSに荷物の再配達リンクがあった', '銀行を名乗る男がギフトカードで払えと言ってる', '母からLINEで今すぐ振り込んでと来た'], 'zh': ['对方让我点链接下载安装一个apk', '收到信息说包裹地址有问题让点链接', '冒充银行的人让我买礼品卡把卡号发给他', '我妈妈微信说急需转账'], 'ko': ['택배 주소 오류라고 문자 왔는데 링크 누르래', '은행이라고 사칭하면서 상품권 사서 번호 보내래', '엄마가 카톡으로 급하게 송금해달래'], 'es': ['me llegó un whatsapp de un paquete retenido con un link para pagar', 'dijo ser del banco y que pague con tarjetas de regalo', 'mi mamá me escribió por whatsapp pidiendo una transferencia urgente'], 'vi': ['có tin nhắn báo bưu kiện bị giữ, bấm link để nộp phí', 'mẹ nhắn zalo bảo chuyển tiền gấp', 'người giả danh công an bảo mang tiền mặt, sẽ cho người đến nhà lấy']}
LIGHT = {'ja': ['荷物が届いた、ありがとう', 'ギフトカードを友達の誕生日に買った', 'アプリをApp Storeからインストールした', '母とLINEで話した'], 'zh': ['包裹已经到了', '给朋友买了礼品卡当生日礼物', '从应用商店安装了银行App', '和妈妈微信聊天'], 'ko': ['택배 잘 받았어', '친구 생일 선물로 상품권 샀어', '앱스토어에서 은행 앱 설치했어', '엄마랑 카톡했어'], 'es': ['ya llegó mi paquete', 'compré una tarjeta de regalo para el cumpleaños de mi amiga', 'instalé la app del banco desde la Play Store', 'hablé con mi mamá por whatsapp'], 'vi': ['bưu kiện đã đến rồi', 'mua thẻ quà tặng sinh nhật cho bạn', 'cài app ngân hàng từ cửa hàng ứng dụng', 'nói chuyện với mẹ qua zalo']}
SCRIPT = {"ja": r"[\u3040-\u30ff]", "zh": r"[\u4e00-\u9fff]", "ko": r"[\uac00-\ud7af]", "es": r"\b(?:el|la|de|que|no)\b",
          "vi": r"[ăâđêôơưạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹ]"}


@pytest.mark.parametrize("lang,text,kind", [(lg, t, k) for lg, rows in FIRST.items() for t, k in rows])
def test_each_scam_is_named_and_answered_in_the_users_language(lang, text, kind):
    a = assess(text)
    assert a["cyber"] == kind and a["text_risk"] >= 60, a
    r = compose(text)
    assert "1441" in r
    assert re.search(SCRIPT[lang], r.split("\n")[0], re.I), r[:80]


@pytest.mark.parametrize("lang,text", [(lg, t) for lg, xs in MORE.items() for t in xs])
def test_other_wordings_are_caught(lang, text):
    assert assess(text)["cyber"]


@pytest.mark.parametrize("lang,text", [(lg, t) for lg, xs in LIGHT.items() for t in xs])
def test_everyday_parcels_gift_cards_and_family_chats_stay_light(lang, text):
    a = assess(text)
    assert not a["cyber"] and a["text_risk"] < 35, a
