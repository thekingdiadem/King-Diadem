"""สร้างแผ่นฟ้า Gaia (static/sky/gaia/) สำหรับหน้าดูดาว — ดาวจาง 10 < G ≤ 11 (~765,000 ดวง)

ข้อมูล: ESA/Gaia/DPAC, Gaia DR3 (gaiadr3.gaia_source) — ใช้ได้ฟรีเมื่อให้เครดิต (CC BY-SA 3.0 IGO)
  ดึงด้วย ADQL ผ่าน https://gea.esac.esa.int/tap-server/tap (async) เป็น CSV คอลัมน์ ra, de, g, c (= bp_rp)

แบ่งฟ้าเป็นช่อง 10°×10° (36 × 18 = 648 แผ่น) · หน้าดูดาวโหลดเฉพาะแผ่นที่อยู่ในมุมมอง และเฉพาะตอนซูมเข้าลึก
แผ่นละไฟล์ t<index>.bin · ดาวละ 6 ไบต์ เรียงจากสว่างไปจาง:
  uint16 ตำแหน่ง RA ในช่อง (0–65535 = 0–10°) · uint16 Dec ในช่อง · uint8 (G−10)×25 · uint8 (bp_rp+0.5)×50
index = floor((dec+90)/10) × 36 + floor(ra/10)
"""
import argparse
import csv
import json
import struct
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "static" / "sky" / "gaia"


def build(src: Path) -> dict:
    tiles = defaultdict(list)
    with src.open() as f:
        for row in csv.DictReader(f):
            try:
                ra, de, g = float(row["ra"]) % 360, float(row["de"]), float(row["g"])
                c = float(row["c"]) if row.get("c") not in (None, "") else .8
            except ValueError:
                continue
            ix, iy = min(35, int(ra // 10)), min(17, int((de + 90) // 10))
            tiles[iy * 36 + ix].append((g, ra - ix * 10, de + 90 - iy * 10, c))
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("t*.bin"):
        old.unlink()
    counts = {}
    for k, stars in tiles.items():
        stars.sort()
        buf = bytearray()
        for g, dra, dde, c in stars:
            buf += struct.pack("<HHBB", min(65535, round(dra / 10 * 65535)), min(65535, round(dde / 10 * 65535)),
                               max(0, min(255, round((g - 10) * 25))), max(0, min(255, round((c + .5) * 50))))
        (OUT / f"t{k}.bin").write_bytes(bytes(buf))
        counts[k] = len(stars)
    meta = {"source": "ESA/Gaia/DPAC, Gaia DR3 (CC BY-SA 3.0 IGO)", "g_min": 10, "g_max": 11, "cell_deg": 10, "cols": 36,
            "total": sum(counts.values()), "tiles": {str(k): v for k, v in sorted(counts.items())}}
    (OUT / "index.json").write_text(json.dumps(meta, separators=(",", ":")), encoding="utf-8")
    return meta


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=Path)
    m = build(ap.parse_args().src)
    print(m["total"], "stars in", len(m["tiles"]), "tiles", sum(p.stat().st_size for p in OUT.glob("t*.bin")), "bytes")
