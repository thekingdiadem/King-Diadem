"""
scripts/build_allsky.py — ภาพท้องฟ้าทั้งท้องฟ้าจากข้อมูลจริง สำหรับฉากหลังหน้าแรก (มุมมองผู้สังเกต)

เจ้าของโปรเจกต์: "อยากได้แนวออฟเซิร์ฟเวอร์ · ฟ้าจากข้อมูลจริงบนหน้าแรก"
แทนแถบทางช้างเผือกที่วาดด้วยสูตรสุ่ม — ทางช้างเผือก ร่องฝุ่น และเมฆดาวในภาพนี้ไม่ได้ถูกวาดขึ้น
แต่เกิดจากตำแหน่งจริงของดาว:
  · ดาว Gaia DR3 765,134 ดวง (10 < G ≤ 11) จาก static/sky/gaia/ (ESA/Gaia/DPAC, CC BY-SA 3.0 IGO)
    ความหนาแน่นของดาว = แสงเรืองของทางช้างเผือก · ที่ดาวน้อยผิดปกติกลางแถบ = ฝุ่นบังจริง
    สีจาก BP−RP ของแต่ละดวง
  · ดาวสว่าง 5,044 ดวงถึงโชติมาตร 6 จาก static/sky/catalog.json (Hipparcos/HYG ผ่าน d3-celestial)

ผลลัพธ์: static/sky/allsky.jpg — พิกัดดาราจักรแบบ equirectangular · ใจกลางทางช้างเผือก (l=0, b=0) อยู่กลางภาพ
  u = 0.5 − l/360 (l เพิ่มไปทางซ้ายแบบที่มองจากข้างใน) · v = 0.5 − b/180
รัน: python scripts/build_allsky.py   (ใช้ numpy + Pillow · ไม่ต้องต่ออินเทอร์เน็ต)
"""
from __future__ import annotations

import json
import pathlib

import numpy as np
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKY = ROOT / "static" / "sky"
W, H = 3072, 1536

# เมทริกซ์ ICRS → พิกัดดาราจักร (IAU 1958 / Hipparcos)
_EQ2GAL = np.array([[-0.0548755604, -0.8734370902, -0.4838350155],
                    [+0.4941094279, -0.4448296300, +0.7469822445],
                    [-0.8676661490, -0.1980763734, +0.4559837762]])


def to_gal(ra_deg, de_deg):
    ra, de = np.radians(ra_deg), np.radians(de_deg)
    v = np.stack([np.cos(de) * np.cos(ra), np.cos(de) * np.sin(ra), np.sin(de)])
    g = _EQ2GAL @ v
    l = np.degrees(np.arctan2(g[1], g[0]))
    b = np.degrees(np.arcsin(np.clip(g[2], -1, 1)))
    return l, b


def to_px(l, b, w, h):
    u = (0.5 - l / 360.0) % 1.0
    v = np.clip(0.5 - b / 180.0, 0, 0.999999)
    return (u * w).astype(np.int64) % w, (v * h).astype(np.int64)


def bv_rgb(bv):
    """สีดาวจาก B−V โดยประมาณ (น้ำเงิน → ขาว → ส้ม)"""
    t = np.clip((bv + 0.4) / 2.4, 0, 1)
    r = np.clip(0.62 + 0.55 * t, 0, 1)
    g = np.clip(0.72 + 0.25 * t - 0.35 * t * t, 0, 1)
    b = np.clip(1.0 - 0.75 * t, 0, 1)
    return np.stack([r, g, b], -1)


def blur(img, sigma):
    """เบลอแบบเกาส์ด้วย FFT (วนรอบแนวนอน เพราะท้องฟ้าต่อกันรอบตัว)"""
    h, w = img.shape[:2]
    fy, fx = np.fft.fftfreq(h)[:, None], np.fft.fftfreq(w)[None, :]
    k = np.exp(-2 * (np.pi * sigma) ** 2 * (fx * fx + fy * fy))
    if img.ndim == 2:
        return np.real(np.fft.ifft2(np.fft.fft2(img) * k))
    return np.stack([np.real(np.fft.ifft2(np.fft.fft2(img[..., c]) * k)) for c in range(img.shape[2])], -1)


def load_gaia():
    meta = json.loads((SKY / "gaia" / "index.json").read_text())
    ra, de, mag, bv = [], [], [], []
    for k in meta["tiles"]:
        i = int(k)
        ra0, de0 = (i % 36) * 10, (i // 36) * 10 - 90
        b = np.fromfile(SKY / "gaia" / f"t{k}.bin", dtype=np.uint8).reshape(-1, 6)
        u16 = b[:, :4].copy().view("<u2").reshape(-1, 2)
        ra.append(ra0 + u16[:, 0] / 65535 * 10)
        de.append(de0 + u16[:, 1] / 65535 * 10)
        mag.append(10 + b[:, 4] / 25)
        bv.append(np.clip(b[:, 5] / 50 - .5, -.4, 3) * .98 - .2)
    return np.concatenate(ra), np.concatenate(de), np.concatenate(mag), np.concatenate(bv)


def main():
    ra, de, mag, bv = load_gaia()
    l, b = to_gal(ra, de)
    flux = 10 ** (-0.4 * (mag - 10))
    rgb = bv_rgb(bv)

    # 1) แสงเรืองจากความหนาแน่นของดาว (ครึ่งความละเอียด แล้วเบลอสองระดับ: เมฆดาว + แสงกว้าง)
    w2, h2 = W // 2, H // 2
    x, y = to_px(l, b, w2, h2)
    acc = np.zeros((h2, w2, 3))
    np.add.at(acc, (y, x), rgb * flux[:, None])
    # พื้นที่ต่อพิกเซลเล็กลงใกล้ขั้ว (equirectangular) — ชดเชยไม่ให้ขั้วสว่างเกินจริง
    lat = np.radians(90 - (np.arange(h2) + .5) / h2 * 180)
    acc /= np.maximum(np.cos(lat), 0.05)[:, None, None]
    fine = blur(acc, 1.6)
    wide = blur(acc, 9.0)
    glow = fine * .55 + wide * .9
    lum = glow.mean(-1)
    ref = np.percentile(lum, 99.7)
    glow = np.arcsinh(glow / ref * 6) / np.arcsinh(6)                 # บีบช่วงสว่าง ให้ฝุ่นมืดยังเห็นรายละเอียด
    glow = np.clip(glow, 0, 1)

    # โทนลึกลับมีอำนาจ: พื้นครามลึก · แสงเรืองคงสีจริงของดาว แต่ดันเงาไปทางม่วงคราม และแกนไปทางทอง
    base = np.array([.006, .007, .018])
    tint_lo, tint_hi = np.array([.30, .26, .74]), np.array([1.0, .78, .5])
    m = glow.mean(-1, keepdims=True)
    m = np.clip((m - .18) / .82, 0, 1)                                # ตัดหมอกจางนอกแถบ ให้ฟ้าลึกมืดจริง
    tone = tint_lo * (1 - m ** 1.5) + tint_hi * m ** 1.5               # ขอบแถบครามม่วง · แกนทอง
    sky = base + (glow * .35 + tone * .6) * np.power(m, 1.7) * .95
    sky = np.array(Image.fromarray(np.uint8(np.clip(sky, 0, 1) * 255)).resize((W, H), Image.LANCZOS)) / 255.0

    # 2) ดาว Gaia แต่ละดวงเป็นจุดจางๆ ความละเอียดเต็ม (ให้แถบเป็นเม็ดดาวจริง ไม่ใช่หมอกเรียบ)
    x, y = to_px(l, b, W, H)
    pts = np.zeros((H, W, 3))
    np.add.at(pts, (y, x), rgb * (flux[:, None] * .5))
    sky += np.clip(blur(pts, .55) * .7, 0, .6) * (.35 + .65 * np.array(Image.fromarray(np.uint8(m[..., 0] * 255)).resize((W, H), Image.BILINEAR))[..., None] / 255)

    # 3) ดาวสว่างจากแคตตาล็อก (โชติมาตร ≤ 6) เป็นจุดแสงคมพร้อมรัศมีบางๆ
    cat = json.loads((SKY / "catalog.json").read_text())["stars"]
    cra, cde, cmag, cbv = (np.array([s[i] for s in cat], float) for i in range(4))
    cl, cb = to_gal(cra, cde)
    cx, cy = to_px(cl, cb, W, H)
    cf = 10 ** (-0.4 * (cmag - 6))
    bright = np.zeros((H, W, 3))
    np.add.at(bright, (cy, cx), bv_rgb(cbv) * np.minimum(cf, 120)[:, None])
    sky += np.clip(blur(bright, .7) * .9, 0, 1) + blur(bright, 3.0) * .03

    out = np.uint8(np.clip(sky, 0, 1) ** (1 / 1.05) * 255)
    Image.fromarray(out).save(SKY / "allsky.jpg", quality=80, optimize=True, progressive=True)
    print("static/sky/allsky.jpg", (SKY / "allsky.jpg").stat().st_size // 1024, "KB")


if __name__ == "__main__":
    main()
