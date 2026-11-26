"""ลูกโลกคมทั้งโลก: ซูมลงแล้วดึงไทล์ NASA GIBS เฉพาะบริเวณที่มอง มาผสมในเชดเดอร์"""
from pathlib import Path

JS = Path("static/cockpit_earth.js").read_text(encoding="utf-8")
APP = Path("app.py").read_text(encoding="utf-8")


def test_shader_blends_two_crossfading_patches_for_day_and_lights():
    assert "uniform sampler2D pd0,pl0,pd1,pl1;uniform vec4 pb0,pb1;uniform vec2 pa0,pa1;" in JS
    assert "land=mix(land,texture2D(pd0,q0).rgb,w0*pa0.x)" in JS
    assert "L=mix(L,pbm(texture2D(pl0,q0).rgb),w0*pa0.y)" in JS
    assert "log(tan(PI*.25+clamp(la,-1.4,1.4)*.5))" in JS          # พิกัด Web Mercator ตรงกับไทล์


def test_free_public_domain_tiles_via_fetch_allowed_by_csp():
    assert "VIIRS_Black_Marble/default/2016-01-01/GoogleMapsCompatible_Level8/" in JS
    assert "BlueMarble_ShadedRelief_Bathymetry/default/2004-08-01/GoogleMapsCompatible_Level8/" in JS
    assert "fetch(url, { mode: 'cors', credentials: 'omit' })" in JS
    assert "connect-src 'self'" in APP and "https://gibs.earthdata.nasa.gov" in APP


def test_only_requests_when_camera_settled_and_only_needed_kind():
    assert "var settled = !busy && Math.abs(S.tL - S.L) < .03" in JS
    assert "if (pWant !== key) return;" in JS                       # เลื่อนไปที่อื่นแล้ว ทิ้งของเก่า
    assert "SHIP.on ? [1, 1] : dayOn() ? [1, 0] : [0, 1]" in JS        # นอกยานโหลดแค่กลางวันหรือกลางคืน


def test_phone_memory_bounded():
    assert "PN = light ? 5 : 6" in JS and "PCACHE = light ? 50 : 140" in JS
    assert "b.close()" in JS


def test_opalite_dawn_ring_and_title():
    assert "vec3 opal=vec3(.58,.5,.66)" in JS and "float dawn=pow(" in JS and "*(1.-near);}'" in JS   # ในยานปิด
    uni = Path("static/king_diadem_universe.html").read_text(encoding="utf-8")
    assert "@keyframes kd-opal" in uni and "#hero .hero-title{animation:none}" in uni   # ลดการเคลื่อนไหว = นิ่ง


def test_equation_in_cosmic_latte():
    uni = Path("static/king_diadem_universe.html").read_text(encoding="utf-8")
    assert ".hero-rule span{color:#fff8e7;" in uni and "#hero .hero-rule{color:#fff8e7;" in uni



def test_hero_title_bold_opal_gradient():
    uni = Path("static/king_diadem_universe.html").read_text(encoding="utf-8")
    assert "#ffa6dc 0%,#e3a4ff 22%,#bca6ff 40%,#98bcff 58%,#7fe2ff 76%,#72f5dc 100%" in uni
    assert "drop-shadow(0 0 14px rgba(190,160,255,.5))" in uni
