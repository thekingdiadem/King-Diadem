"""สร้าง static/sky/catalog.json สำหรับหน้าดูดาว (static/sky.html)

ข้อมูลต้นทาง: d3-celestial 0.7.35 (BSD-3 · Olaf Frohn) — ตำแหน่งดาวจาก XHIP/Hipparcos ผ่าน HYG
  npm pack d3-celestial@0.7.35 แล้วชี้ --src ไปที่โฟลเดอร์ package/data
ย่อให้เล็ก: ดาวถึงโชติมาตร 6 เป็น [ra°, dec°, mag, bv] ทศนิยมพอดีความแม่นของจอ (~0.01°)
ชื่อไทยใส่เองเฉพาะดาวและกลุ่มดาวที่คนรู้จัก — ที่เหลือใช้ชื่อสากล (ไม่เดาชื่อไทย)
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

STAR_TH = {
    "Sirius": "ซิริอัส", "Canopus": "คาโนปุส", "Arcturus": "อาร์คตุรุส", "Vega": "เวกา", "Capella": "คาเพลลา",
    "Rigel": "ไรเจล", "Procyon": "โปรซิออน", "Betelgeuse": "เบเทลจุส", "Achernar": "อาเคอร์นาร์", "Hadar": "ฮาดาร์",
    "Altair": "อัลแทร์", "Acrux": "อาครักซ์", "Aldebaran": "อัลดิบาแรน", "Antares": "แอนทาเรส", "Spica": "สไปกา",
    "Pollux": "พอลลักซ์", "Fomalhaut": "โฟมาลฮอต", "Deneb": "เดเนบ", "Mimosa": "มิโมซา", "Regulus": "เรกูลัส",
    "Adhara": "อาดารา", "Castor": "แคสเตอร์", "Shaula": "ชอลา", "Gacrux": "กาครักซ์", "Bellatrix": "เบลลาทริกซ์",
    "Elnath": "เอลนัท", "Alnilam": "อัลนิลัม", "Alnitak": "อัลนิทัก", "Mintaka": "มินทากา", "Polaris": "ดาวเหนือ",
    "Rigil Kentaurus": "แอลฟาเซนทอรี", "Dubhe": "ดูเบ", "Alkaid": "อัลคาอิด", "Mizar": "มิซาร์", "Alioth": "อาลิออธ",
    "Menkalinan": "เมนคาลิแนน", "Saiph": "ไซฟ์", "Alphard": "อัลฟาร์ด", "Denebola": "เดเนโบลา", "Algol": "อัลกอล",
    "Mirfak": "เมียร์ฟัก", "Alpheratz": "อัลเฟอแรตซ์", "Markab": "มาร์คาบ", "Scheat": "ชีต", "Algenib": "อัลเจนิบ",
    "Enif": "เอนิฟ", "Hamal": "ฮามาล", "Schedar": "เชดาร์", "Caph": "แคฟ", "Nunki": "นุงกิ", "Kaus Australis": "เคาส์ ออสตราลิส",
    "Alcyone": "อัลไซโอนี", "Mirach": "มิแรค", "Almach": "อัลมาค", "Rasalhague": "ราซัลเฮก", "Kochab": "โคแคบ",
}
CON_TH = {
    "Ari": "แกะ", "Tau": "วัว", "Gem": "คนคู่", "Cnc": "ปู", "Leo": "สิงโต", "Vir": "หญิงสาว", "Lib": "คันชั่ง",
    "Sco": "แมงป่อง", "Sgr": "คนยิงธนู", "Cap": "แพะทะเล", "Aqr": "คนแบกหม้อน้ำ", "Psc": "ปลา",
    "Ori": "นายพราน", "UMa": "หมีใหญ่", "UMi": "หมีเล็ก", "Cas": "แคสสิโอเปีย", "Cyg": "หงส์", "Lyr": "พิณ",
    "Aql": "นกอินทรี", "Peg": "ม้าบิน", "And": "แอนดรอมิดา", "Per": "เพอร์ซิอัส", "Aur": "สารถี",
    "CMa": "หมาใหญ่", "CMi": "หมาเล็ก", "Cru": "กางเขนใต้", "Cen": "คนครึ่งม้า", "Dra": "มังกร", "Boo": "คนเลี้ยงสัตว์",
    "Her": "เฮอร์คิวลีส", "Lep": "กระต่าย", "Crv": "อีกา", "Hya": "งูไฟ", "Car": "กระดูกงูเรือ", "Del": "โลมา",
    "CrB": "มงกุฎเหนือ", "Cep": "เซเฟอัส", "Oph": "คนแบกงู", "Eri": "แม่น้ำ", "Col": "นกพิราบ", "PsA": "ปลาใต้",
}
PLANET_TH = {"mer": "ดาวพุธ", "ven": "ดาวศุกร์", "mar": "ดาวอังคาร", "jup": "ดาวพฤหัสบดี", "sat": "ดาวเสาร์",
             "ura": "ดาวยูเรนัส", "nep": "ดาวเนปจูน", "ter": "โลก"}


def ra(lon):
    return round(lon % 360, 3)


def build(src: Path) -> dict:
    stars = json.loads((src / "stars.6.json").read_text())["features"]
    names = json.loads((src / "starnames.json").read_text())
    lines = json.loads((src / "constellations.lines.json").read_text())["features"]
    cons = json.loads((src / "constellations.json").read_text())["features"]
    planets = json.loads((src / "planets.json").read_text())
    out_stars, named = [], []
    for f in sorted(stars, key=lambda f: f["properties"]["mag"]):
        lon, lat = f["geometry"]["coordinates"]
        bv = f["properties"].get("bv")
        try:
            bv = round(float(bv), 2)
        except (TypeError, ValueError):
            bv = 0.6
        out_stars.append([ra(lon), round(lat, 3), round(f["properties"]["mag"], 2), bv])
        nm = (names.get(str(f["id"])) or {}).get("name") or ""
        if nm and f["properties"]["mag"] <= 2.6 or nm in STAR_TH:
            named.append([len(out_stars) - 1, nm, STAR_TH.get(nm, "")])
    out_lines = {f["id"]: [[[ra(p[0]), round(p[1], 3)] for p in seg] for seg in f["geometry"]["coordinates"]] for f in lines}
    out_cons = []
    for f in cons:
        lon, lat = f["geometry"]["coordinates"]
        p = f["properties"]
        out_cons.append({"id": f["id"], "en": p.get("en") or p.get("name"), "th": CON_TH.get(f["id"], ""),
                         "at": [ra(lon), round(lat, 2)], "rank": int(p.get("rank") or 3)})
    out_planets = {k: {"el": planets[k]["elements"][0], "th": PLANET_TH[k], "en": planets[k]["en"], "H": planets[k].get("H")}
                   for k in PLANET_TH}
    return {"source": "d3-celestial 0.7.35 (BSD-3, Olaf Frohn) · XHIP/Hipparcos via HYG · JPL approximate elements",
            "stars": out_stars, "named": named, "lines": out_lines, "cons": out_cons, "planets": out_planets}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True, type=Path)
    a = ap.parse_args()
    data = build(a.src)
    out = ROOT / "static" / "sky" / "catalog.json"
    out.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(out, out.stat().st_size, len(data["stars"]), "stars", len(data["named"]), "named")
