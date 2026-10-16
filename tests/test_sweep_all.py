"""ตัวกวาดทั้งห้าชุดของ scripts/sweep_all.py แบบสุ่มตัวอย่าง — รันทุกครั้งที่รันเทสต์
ถ้ามีการแก้ที่ทำให้เรื่องด่วนหลุด หรือทำให้สำนวนธรรมดากลายเป็นเรื่องด่วน เทสต์นี้จะแดงทันที
(รันเต็มจำนวน: python scripts/sweep_all.py)"""
import pytest

from scripts import sweep_all


@pytest.mark.parametrize("suite,n", [("urgent", 1500), ("violence", 1000), ("benign", 1500), ("typing", 0), ("intl", 0), ("en", 600), ("en_violence", 1000), ("th_violence", 1000), ("th_crisis", 1200), ("en_crisis", 1000), ("th_scam", 600)])
def test_sweep_suite_has_no_slips(suite, n):
    total, bad = sweep_all.SUITES[suite](n)
    assert total > 0
    assert not bad, f"{suite}: หลุด {len(bad)}/{total} เช่น {bad[:5]}"


def test_followup_suite_has_no_slips(client, monkeypatch):
    monkeypatch.setenv("KD_AI", "off")
    import itertools
    hist = lambda p: [{"role": "user", "content": p}, {"role": "assistant", "content": "..."}]
    bad = []
    pairs = list(itertools.product(sweep_all.FOLLOW_PRIOR.items(), ["ค่ะ", "ไม่มีใคร", "แล้วไงต่อ"]))
    for i, ((prior, need), f) in enumerate(pairs):
        d = client.post("/run", json={"input": f, "history": hist(prior)},
                        headers={"cf-connecting-ip": f"10.8.0.{i}"}).json()
        out = str(d.get("ai_response", ""))
        if need not in out or "Risk 0" in out:
            bad.append(f"{prior} → {f}")
    assert not bad, bad
