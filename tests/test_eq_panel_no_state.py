"""แผงสมการขวามือ: ยังไม่ระบุสถานะ ต้องไม่โชว์ "Risk 0" จากสูตร E, R คู่กับ "Risk* 55" จากข้อความ

หน้าจอจริง: "หนี้บัตรเครดิต 50000 บาท ผ่อนไม่ไหวแล้ว" แผงขวาขึ้น Risk 0.5·0 + 0.5·0 = 0 แล้วตามด้วย Risk* 55
คนอ่านไม่รู้ว่าเชื่อตัวไหน — ทั้งที่ 0 มาจาก W ค่าเริ่มต้น ไม่ใช่สภาพจริงของผู้ใช้
"""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

HTML = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")


def _fn(name):
    i = HTML.index("function " + name + "(")
    depth, j = 0, HTML.index("{", i)
    for k in range(j, len(HTML)):
        depth += {"{": 1, "}": -1}.get(HTML[k], 0)
        if depth == 0:
            return HTML[i:k + 1]


@pytest.mark.skipif(not shutil.which("node"), reason="ต้องใช้ node")
def test_no_state_shows_only_text_risk():
    js = "\n".join(_fn(n) for n in ("esc", "num", "r1", "eqRow", "eqHTML"))
    js = "var EQ=[];function eqCatalog(){return ''};\n" + js + """
    var noState = eqHTML({inp: null, wl: 100, risk: 55, sentState: false});
    var withState = eqHTML({inp: {energy: 50, sleep_hours: 6, days_in_crisis: 0}, wl: 100, risk: 55, sentState: true});
    console.log(JSON.stringify([noState, withState]));"""
    out = subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout
    no_state, with_state = json.loads(out)
    assert "0.5·" not in no_state and "E, R" not in no_state       # ไม่มีสูตรที่ได้ 0 จากค่าเริ่มต้น
    assert "Risk*" not in no_state and "<b>55</b>" in no_state       # เหลือแถวเดียวคือความเสี่ยงจากข้อความ
    assert "0.5·" in with_state and "Risk*" in with_state            # ระบุสถานะแล้ว ยังเห็นสูตรครบเหมือนเดิม
