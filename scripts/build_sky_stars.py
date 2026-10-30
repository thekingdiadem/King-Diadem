"""สร้างท้องฟ้าจริงของหน้าแรก (static/earth/sky_taurus.json) จากแคตตาล็อกดาว Hipparcos

ต้นฉบับ: d3-celestial@0.7.35 (BSD-3-Clause · © 2015 Olaf Frohn) ไฟล์ data/stars.8.json
          ข้อมูลดาวมาจากแคตตาล็อก Hipparcos ของ ESA — ตำแหน่ง (RA/Dec J2000) · โชติมาตร · สี B−V
ใช้:  npm pack d3-celestial@0.7.35   (แล้วแตกไฟล์)
      python scripts/build_sky_stars.py <โฟลเดอร์ package ของ d3-celestial>

เก็บเฉพาะฟ้ารอบดาวลูกไก่ (กลุ่มดาววัว · นายพราน · เพอร์ซิอุส) ห่างไม่เกิน 55° และสว่างกว่าโชติมาตร 7.5
แถว: [RA องศา, Dec องศา, โชติมาตร, B−V]
"""
import json
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "earth", "sky_taurus.json")
CENTER = (56.75, 24.12)          # ดาวลูกไก่ (M45)
RADIUS, MAG = 55.0, 7.5


def sep(a1, d1, a2, d2):
    r = math.radians
    c = math.sin(r(d1)) * math.sin(r(d2)) + math.cos(r(d1)) * math.cos(r(d2)) * math.cos(r(a1 - a2))
    return math.degrees(math.acos(max(-1.0, min(1.0, c))))


def main(pkg):
    with open(os.path.join(pkg, "data", "stars.8.json"), encoding="utf-8") as f:
        feats = json.load(f)["features"]
    rows = []
    for ft in feats:
        p = ft.get("properties") or {}
        lon, dec = ft["geometry"]["coordinates"]
        ra = lon % 360.0
        mag = float(p.get("mag", 99))
        if mag > MAG or sep(ra, dec, *CENTER) > RADIUS:
            continue
        try:
            bv = float(p.get("bv"))
        except (TypeError, ValueError):
            bv = 0.6
        rows.append([round(ra, 3), round(dec, 3), round(mag, 2), round(bv, 2)])
    rows.sort(key=lambda r: r[2])                     # สว่างก่อน — ดาวจางวาดทีหลัง
    data = {"source": "Hipparcos via d3-celestial 0.7.35 (BSD-3-Clause, (c) 2015 Olaf Frohn)",
            "center": list(CENTER), "fields": ["ra", "dec", "mag", "bv"], "stars": rows}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"))
    print(len(rows), "stars", os.path.getsize(OUT) // 1024, "KB")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
