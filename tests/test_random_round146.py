"""รอบสุ่ม 146: ทำงานไม่ได้ค่าจ้าง + ไม่ให้ออก/กลับบ้าน ใน es vi zh ko ja (ประโยคเขียนเองในรอบนี้ ไม่ได้มาจากชุดปิดตา)"""
import pytest
from core.kernel_voice import assess


@pytest.mark.parametrize("q", [
    "No me pagan y no me dejan salir de la fábrica", "Trabajo sin sueldo y el jefe no me deja volver a casa",
    "Tôi làm không công và họ không cho tôi rời khỏi nhà máy", "工厂不发工资，也不准我们离开",
    "월급을 못 받고 공장 밖으로 못 나가게 해요", "給料なしで働かされて、寮から出してもらえない",
])
def test_forced_unpaid_labour_is_urgent(q):
    assert assess(q)["risk_shown"] >= 80


@pytest.mark.parametrize("q", [
    "Mi jefe no me deja salir temprano hoy", "No me pagan las horas extra, voy a quejarme a RRHH",
    "今日は残業で帰らせてもらえない", "公司这个月工资晚发了几天", "월급이 늦게 나와서 짜증나요",
])
def test_ordinary_work_complaints_stay_calm(q):
    assert assess(q)["risk_shown"] < 60
