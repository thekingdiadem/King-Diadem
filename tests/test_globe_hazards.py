"""ภัยจริงบนลูกโลกหน้าแรก — /api/quakes และ /api/hazards เคยมีแต่หน้าเว็บไม่เคยเรียก (โผล่แค่ตอนถามในแชท)
ตอนนี้ปักจุดลงบนลูกโลก แตะแล้วเห็นรายละเอียดและคู่มือเอาชีวิตรอดของภัยนั้น"""
import re

from tests._front import front_page

PAGE = front_page()


def _fn(name):
    i = PAGE.index("function " + name + "(")
    depth, j = 0, PAGE.index("{", i)
    for k in range(j, len(PAGE)):
        depth += {"{": 1, "}": -1}.get(PAGE[k], 0)
        if depth == 0:
            return PAGE[i:k + 1]


def test_marker_projection_uses_the_same_numbers_as_the_globe_shader():
    """shader: lon=atan(ng.x,ng.z)+uSpin · เอียง ct=.985 st=.174 · uSpin=1.885+spin−t·.025 — แก้ฝั่งเดียว จุดจะเลื่อนผิดที่"""
    shader_tilt = re.search(r"float ct=([\d.]+),st=([\d.]+);", PAGE).groups()
    spin = re.search(r"uSpin, ([\d.]+) \+ \(d\.spin \|\| 0\) - \(REDUCED \? 0 : tsec \* ([\d.]+)\)", PAGE).groups()
    draw = _fn("drawHazards")
    assert f"ct = {shader_tilt[0]}, st = {shader_tilt[1]}" in draw
    assert f"S = {spin[0]} + DAWN.spinOff - (REDUCED ? 0 : tsec * {spin[1]})" in draw
    assert "nz < .08" in draw                                       # ไม่วาดจุดด้านหลังโลก


def test_live_data_comes_from_both_feeds_and_links_only_to_official_sources():
    load = _fn("loadHazards")
    assert "/api/quakes" in load and "/api/hazards" in load and ".slice(0, 24)" in load
    pop = _fn("showHazard")
    assert "/survival" in pop and r"(?:earthquake\.usgs\.gov|www\.gdacs\.org)" in pop and "esc(" in pop


def test_tap_does_not_steal_buttons_or_chat_and_popup_is_announced():
    assert "e.target.closest('a,button,input,textarea,.m')" in PAGE and "DAWN.show < .5" in PAGE
    assert 'id="hz-pop"' in PAGE and 'aria-live="polite"' in PAGE[PAGE.index('id="hz-pop"') - 80:PAGE.index('id="hz-pop"') + 120]
    assert "drawHazards(cx, cy, r, tsec, DAWN.show)" in PAGE and "!CINEMA.on" in PAGE
