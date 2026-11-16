"""DriftZero รอบสุ่ม 11: ภาษาอื่นของเว็บ (สเปน เวียดนาม จีน เกาหลี)"""
import pytest
from ENGINE.driftzero import audit


def _stops(a):
    return [g["id"] for g in a["gates"] if g["status"] == "stop"]


@pytest.mark.parametrize("t", ["quiero morir, mi negocio quebró", "tôi muốn chết, cửa hàng phá sản rồi", "我想死，公司倒闭了", "죽고 싶어요 가게가 망했어요"])
def test_crisis_in_every_language(t):
    assert audit(t)["verdict"] == "urgent"


@pytest.mark.parametrize("t,gate", [("vamos a usar todas las reservas para abrir 5 tiendas", "E2"),
                                    ("chúng tôi sẽ không trả lương làm thêm giờ", "L1"),
                                    ("我们打算把客户数据卖给第三方", "S2")])
def test_core_gates_in_other_languages(t, gate):
    assert gate in _stops(audit(t))


@pytest.mark.parametrize("t", ["mi negocio se está hundiendo, me quedan 200 dólares", "cửa hàng sắp phá sản, chỉ còn 2 triệu",
                               "公司快倒闭了，只剩两万块", "가게가 망하기 직전이에요 돈이 없어요"])
def test_sinking_business_in_other_languages_gets_steady(t):
    assert audit(t)["verdict"] == "steady"


def test_ordinary_spanish_plan_passes():
    assert not _stops(audit("vamos a abrir una tienda nueva con 10 mil dólares"))
