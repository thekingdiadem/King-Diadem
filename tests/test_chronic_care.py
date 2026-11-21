"""แผนดูแลไต/เบาหวาน/ความดัน/ไขมัน — ตัวเลขต้องตรงแนวทาง และต้องไม่สัญญาว่าหายขาด"""
import pytest
from core import chronic_care as cc


def test_egfr_matches_ckd_epi_2021():
    assert cc.egfr_ckd_epi_2021(1.0, 60, "m") == pytest.approx(86, abs=1)
    assert cc.egfr_ckd_epi_2021(1.0, 60, "f") == pytest.approx(64.5, abs=1)
    assert cc.egfr_ckd_epi_2021(88.4, 60, "male", "umol/L") == pytest.approx(86, abs=1)


def test_egfr_refuses_bad_input():
    assert cc.egfr_ckd_epi_2021(1.0, 12, "m") is None      # เด็กใช้สมการอื่น
    assert cc.egfr_ckd_epi_2021(0, 50, "m") is None
    assert cc.egfr_ckd_epi_2021(1.0, 50, "?") is None
    assert cc.egfr_ckd_epi_2021("abc", 50, "m") is None


@pytest.mark.parametrize("egfr,g", [(95, "G1"), (60, "G2"), (59.9, "G3a"), (44, "G3b"), (29, "G4"), (10, "G5")])
def test_gfr_category(egfr, g):
    assert cc.gfr_category(egfr) == g


def test_albuminuria_and_monitoring():
    assert [cc.albuminuria_category(x) for x in (10, 30, 300, 301)] == ["A1", "A2", "A2", "A3"]
    assert cc.checks_per_year("G3b", "A2") == 3
    assert cc.checks_per_year("G4", None) == 4          # ไม่รู้ A → เลือกถี่สุด
    assert cc.needs_nephrologist("G4", "A1") and cc.needs_nephrologist("G2", "A3")
    assert cc.needs_nephrologist("G2", "A1", egfr_drop_per_year=6)
    assert not cc.needs_nephrologist("G3a", "A1")


def test_targets():
    assert cc.bp_status(185, 100) == "crisis" and cc.bp_status(135, 70) == "high"
    assert cc.a1c_target(80) == 8.0 and cc.a1c_target(50) == 7.0
    assert cc.ldl_target(False, True, None) == 55
    assert cc.statin_discussion(55, False, True, False)
    assert not cc.statin_discussion(55, False, True, False, dialysis=True)


def test_metformin_and_nsaid_warnings():
    w = cc.medication_warnings(["metformin 500", "ibuprofen"], [], "G4", True)
    assert "metformin_stop" in w and "nsaid" in w and "star_fruit" in w and "herbs" in w
    assert "metformin_reduce" in cc.medication_warnings(["เมทฟอร์มิน"], [], "G3b", True)
    assert "potassium" in cc.medication_warnings([], ["กล้วย"], "G4", True)
    assert "potassium" not in cc.medication_warnings([], ["กล้วย"], "G2", False)


def test_plan_is_honest_and_personal():
    r = cc.plan({"creatinine": 1.6, "age": 62, "sex": "m", "uacr": 120, "sleep_hours": 5,
                 "sitting_hours": 9, "weight_kg": 70, "diabetes": True}, "th")
    assert r["stage"]["g"] == "G3a" and r["stage"]["a"] == "A2"
    assert "หายขาดไม่ได้" in r["text"] and "ชะลอได้" in r["text"]
    assert "ไม่เดา" in r["text"]
    assert "56 กรัม" in r["text"]                      # 0.8 × 70
    assert {"sleep_short", "sitting", "protein"} <= set(r["lifestyle"])
    assert "1669" in r["text"]


def test_plan_asks_instead_of_guessing():
    r = cc.plan({}, "th")
    assert r["stage"] is None and len(r["ask"]) == 2


def test_every_string_has_all_seven_languages():
    for key, row in cc.T.items():
        if key == "lang_fallback":
            continue
        assert set(cc.LANGS) <= set(row), key


def test_unsupported_language_falls_back_to_english_and_says_so():
    r = cc.plan({"egfr": 50}, "fr")
    assert r["lang"] == "en" and not r["lang_supported"]
    assert "isn't available in your language" in r["text"]


@pytest.mark.parametrize("lang", cc.LANGS)
def test_plan_renders_in_every_language(lang):
    r = cc.plan({"egfr": 40, "uacr": 400, "sys_bp": 190, "dia_bp": 100, "hba1c": 8.2, "ldl": 140,
                 "diabetes": True, "meds": ["metformin"], "standing_hours": 8}, lang)
    assert r["lang"] == lang and "{" not in r["text"]


def test_api_endpoint():
    from fastapi.testclient import TestClient
    import app
    c = TestClient(app.app)
    r = c.post("/api/chronic-care", json={"lang": "en", "profile": {"egfr": 50}})
    assert r.status_code == 200 and r.json()["stage"]["g"] == "G3a"
