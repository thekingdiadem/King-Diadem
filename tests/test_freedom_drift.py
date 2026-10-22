"""AI/freedom_signal — record_drift ต้องถูกเรียกจริง ไม่งั้น D ใน R = (D × T) / C มาจากวิกฤตอย่างเดียว"""
import AI.freedom_signal as F
from AI.freedom_signal import drift_from_risk_score


def test_risk_score_maps_to_drift():
    assert drift_from_risk_score(45) == 0.45
    assert drift_from_risk_score(250) == 1.0
    assert drift_from_risk_score(-3) == 0.0
    assert drift_from_risk_score(None) == 0.0


def test_normal_answer_records_drift(client):
    before = len(F._stats["drift_events"])
    crisis_before = F._stats["crisis"]
    r = client.post("/run", json={"input": "ทำงานเหนื่อยมาก ไม่อยากไปทำงานเลย"})
    assert r.status_code == 200
    if F._stats["crisis"] == crisis_before:          # ไม่ใช่วิกฤต → ต้องมี drift ใหม่ 1 รายการ
        assert len(F._stats["drift_events"]) == before + 1
        assert 0.0 <= F._stats["drift_events"][-1][1] <= 1.0
