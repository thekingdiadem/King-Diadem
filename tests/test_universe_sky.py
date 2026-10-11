"""แท็บจักรวาล: ท้องฟ้าจากข้างในทางช้างเผือก — ไม่มีใจกลาง ผู้สังเกตเป็นฝ่ายเคลื่อน แสงเดียวกันแผ่ถึงทุกคน
แนวคิดของพี่: "จักรวาลไม่ได้หมุนรอบใคร แต่ทุกคนร่วมกันเป็นส่วนหนึ่งของทั้งจักรวาล" """
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HTML = (ROOT / "static" / "index.html").read_text(encoding="utf-8")
I18N = (ROOT / "static" / "i18n.js").read_text(encoding="utf-8")


def _shader_to_world(v, yaw, pitch):
    """ทิศจากจอ → โลก ตามสูตรใน shader ท้องฟ้า"""
    x, y, z = v
    cp, sp = math.cos(pitch), math.sin(pitch)
    y, z = y * cp - z * sp, y * sp + z * cp
    cy, sy = math.cos(yaw), math.sin(yaw)
    return (x * cy - z * sy, y, x * sy + z * cy)


def _world_to_camera(p, yaw, pitch):
    """จุดในโลก → กล้อง ตามสูตรใน sp3() ที่วางดาว 2D"""
    x, y, z = p
    cyw, syw, cpt, spt = math.cos(yaw), math.sin(yaw), math.cos(pitch), math.sin(pitch)
    x1, z1 = x * cyw + z * syw, -x * syw + z * cyw
    y2, z2 = y * cpt + z1 * spt, -y * spt + z1 * cpt
    return (x1, y2, z2)


def test_sky_and_stars_share_one_camera():
    """ฟ้า (shader) กับดาว 2D (sp3) ใช้กล้องเดียวกันทุกประการ — หันมองรอบตัวแล้วดาวต้องไม่เลื่อนหลุดจากฟ้า"""
    assert "v=vec3(v.x,v.y*cp-v.z*sp,v.y*sp+v.z*cp)" in HTML
    assert "vec3 d=vec3(v.x*cy-v.z*sy,v.y,v.x*sy+v.z*cy)" in HTML
    assert ("x1 = x * s.cyw + z * s.syw, z1 = -x * s.syw + z * s.cyw, "
            "y2 = y * s.cpt + z1 * s.spt, z2 = -y * s.spt + z1 * s.cpt") in HTML
    rnd = random.Random(7)
    for _ in range(300):
        yaw, pitch = rnd.uniform(-3.2, 3.2), rnd.uniform(-1.3, 1.3)
        v = (rnd.uniform(-1, 1), rnd.uniform(-1, 1), -1.0)
        back = _world_to_camera(_shader_to_world(v, yaw, pitch), yaw, pitch)
        assert all(abs(a - b) < 1e-9 for a, b in zip(back, v))


def _galactic_center(portrait):
    """จำลอง galFrame() จากค่าคงที่ในไฟล์จริง → ทิศของใจกลางกาแล็กซี"""
    body = HTML[HTML.index("function galFrame("):HTML.index("function galFrame(") + 800]
    F = [float(x) for x in re.search(r"var F = v3n\(\[([^\]]+)\]\)", body).group(1).split(",")]
    tl = [float(x) for x in re.search(r"tl = portrait \? ([\d.]+) : ([\d.]+)", body).groups()]
    al = [float(x) for x in re.search(r"var a = portrait \? ([\d.]+) : ([\d.]+)", body).groups()]
    tl, a = (tl[0], al[0]) if portrait else (tl[1], al[1])

    def unit(v):
        n = math.sqrt(sum(c * c for c in v))
        return [c / n for c in v]

    F = unit(F)
    T0 = [math.cos(tl), math.sin(tl), 0.0]
    k = T0[0] * F[0] + T0[1] * F[1]
    T = unit([T0[0] - k * F[0], T0[1] - k * F[1], -k * F[2]])
    return unit([F[i] * math.cos(a) + T[i] * math.sin(a) for i in range(3)])


def test_galactic_center_is_out_of_view():
    """ใจกลางกาแล็กซีอยู่นอกจอเสมอ เห็นแค่แสงอุ่นที่ขอบ — เราไม่ใช่ใจกลาง และไม่มีจุดให้ทุกอย่างหมุนรอบ
    (มุมกว้างครึ่งจอตามแนวทแยง ~43° · ใจกลางต้องห่างจากทิศที่มองตรงเกินนั้นชัดเจน)"""
    for portrait in (False, True):
        G = _galactic_center(portrait)
        off = math.degrees(math.acos(-G[2]))
        assert off > 55, (portrait, off)


def test_founder_epigraph_once_and_translated():
    """คำของพี่ปรากฏตอนเข้าจักรวาลครั้งเดียวต่อแท็บแล้วจางหาย · ลดการเคลื่อนไหว = ไม่เล่น · มีคำแปลอังกฤษ/ญี่ปุ่น"""
    assert "<p>จักรวาลไม่ได้หมุนรอบใคร</p><p>แต่ทุกคนร่วมกันเป็นส่วนหนึ่งของทั้งจักรวาล</p>" in HTML
    assert "sessionStorage.getItem('kd_epi')" in HTML and "if(!el || REDUCED) return;" in HTML
    assert "'จักรวาลไม่ได้หมุนรอบใคร': ['The universe revolves around no one'" in I18N
    assert "'แต่ทุกคนร่วมกันเป็นส่วนหนึ่งของทั้งจักรวาล': [" in I18N
    # ค้างให้อ่านชัดก่อนจาง — เดิมคีย์เฟรมไม่ล็อก blur ไว้ ตัวหนังสือค่อยๆ เบลอตั้งแต่ยังค้างอยู่
    assert "74%{opacity:1;filter:blur(0)}" in HTML
    assert "78%{opacity:1;filter:blur(0)}" in HTML                     # ชื่อเรื่องตอนเปิดเว็บก็เช่นกัน


def test_shared_light_reaches_everyone():
    """แตะดาวของเรา หรือมีดาวดวงใหม่เกิด → แสงแผ่ออกไป ดาวดวงอื่นสว่างขึ้นเมื่อแสงผ่าน ("อาบแสงเดียวกับเรา")"""
    assert "if(sel && sel.kind === 'd') ripple(sel, performance.now());" in HTML
    assert "if(!b.rip){ b.rip = 1; ripple(n, now); }" in HTML
    assert "var bo = rippleAt(q.x, q.y, now);" in HTML
    assert "function ripple(n, now){ if(!REDUCED && n)" in HTML


def test_looking_around_is_direct_and_returns_home():
    """ลากฟ้าตามนิ้ว 1:1 · ปล่อยไว้ 3.5 วินาทีค่อยหันกลับมาหากลุ่มดาวของเรา · ลดการเคลื่อนไหว = ไม่มีแรงเฉื่อย"""
    assert "cam.yaw -= mx / fz; cam.pitch = clamp(cam.pitch + my / fz, -1.3, 1.3);" in HTML
    assert "performance.now() - cam.idle > 3500" in HTML
    assert "if(REDUCED || cam.drag) return;" in HTML


def test_stars_stay_in_the_visible_area():
    """ป้ายชื่อกลุ่มดาวไม่มุดใต้แถบข้าง · จอตั้งแคบดึงกลุ่มดาวเข้าจากขอบ"""
    assert "xl = SG ? SG.cx - SG.avW / 2 + 6 : 6;" in HTML
    assert "tx = s.avW / 2 / s.f0 * (pt ? .8 : 1)" in HTML


def test_entering_twice_does_not_streak_across_the_screen():
    """เข้าจักรวาลรอบสอง: ตำแหน่งดาวเก่าต้องถูกล้างก่อนเฟรมแรก ไม่งั้นเส้นแสงตอนเคลื่อนกล้องเข้าจะลากยาวข้ามจอ"""
    body = HTML[HTML.index("setView: function(v){"):HTML.index("setView: function(v){") + 600]
    assert "SKYF.forEach(function(st){ st.lx = null; });" in body
    assert "if(warp && st.lx != null &&" in HTML


def test_front_page_planets_follow_the_sun_not_the_earth():
    """Orbiting Observer: ดาวเคราะห์หน้าแรกไม่โคจรรอบโลกแล้ว (เดิมวงโคจรมีศูนย์กลางที่ cx, cy ของโลก)
    เลื่อนไปตามเส้นสุริยวิถีที่ลากออกจากดวงอาทิตย์ · ดวงที่อยู่หลังโลก/นอกจอไม่มีป้ายค้าง"""
    body = HTML[HTML.index("function orb(k, a0, per, rad)"):HTML.index("function orb(k, a0, per, rad)") + 400]
    assert "return [sunX + e * Math.cos(eT), sunY + e * Math.sin(eT)" in body
    assert "cx + Math.cos(a) * r * k" not in HTML
    assert "Math.hypot(b[1][0] - B.cx, b[1][1] - B.cy) < R) return;" in HTML
