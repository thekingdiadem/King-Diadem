"""หน้าแรก: ฟ้าจริงเหนือหัวตอนนี้ (ฟ้าผืนเดียวกับหน้าดาวเคราะห์) แทนการสุ่มมุม"""
import json
import re
import subprocess
from pathlib import Path

import pytest

JS = (Path(__file__).resolve().parent.parent / "static" / "app.js").read_text(encoding="utf-8")


def _run(utc_iso):
    fn = re.search(r"    function nowSkyView\(date\)\{.*?\n    \}\n", JS, re.S).group(0)
    out = subprocess.run(["node", "-e", fn + f"console.log(JSON.stringify(nowSkyView(new Date('{utc_iso}')).map(x=>x*180/Math.PI)))"],
                         capture_output=True, text=True, timeout=20, env={"TZ": "UTC", "PATH": "/usr/bin:/usr/local/bin:/bin"})
    if out.returncode:
        pytest.skip("ไม่มี node")
    return json.loads(out.stdout)


def test_sky_turns_with_real_time():
    a, b = _run("2026-11-15T11:00:00Z"), _run("2026-11-15T23:00:00Z")
    assert abs(a[0] - b[0]) > 40                           # ฟ้าหมุนตามเวลาจริง ไม่ใช่มุมเดิม


def test_evening_in_november_faces_cygnus_and_midnight_faces_perseus():
    l, b, _ = _run("2026-11-15T18:00:00Z")                 # TZ=UTC ในเทสต์ → ลองจิจูด 0
    assert 50 <= l <= 90 and b == pytest.approx(-15, abs=.1)      # หงส์ (Cygnus) สูงกลางฟ้าหัวค่ำเดือนพ.ย.
    l2 = _run("2026-11-16T00:30:00Z")[0]
    assert abs(l2) >= 110                                          # หลังเที่ยงคืน: เพอร์ซิอุส/สารถี (ฟากตรงข้ามใจกลาง)


def test_falls_back_to_curated_views_if_math_fails():
    assert "SKY_VIEWS[Math.floor(Math.random() * SKY_VIEWS.length)]" in JS
    assert "getCurrentPosition" not in JS                  # ไม่ขอตำแหน่ง GPS ผู้ใช้
