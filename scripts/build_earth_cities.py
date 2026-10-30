"""สร้างชื่อเมืองของหน้า Universe จาก GeoNames — เรียงตามความสำคัญ ป้ายใหญ่ได้ที่ก่อนเมื่อชนกัน

ต้นฉบับ: all-the-cities@3.1.0 (MIT) — ข้อมูล GeoNames (CC BY 4.0) · ไฟล์ cities.pbf

ใช้:  npm pack all-the-cities@3.1.0   (แล้วแตกไฟล์)
      python scripts/build_earth_cities.py <โฟลเดอร์ package ของ all-the-cities>

ไฟล์ที่ได้ (static/earth/):
  admin1.json      เมืองศูนย์กลางจังหวัด/รัฐ (GeoNames PPLA) — เดิมไม่มีชั้นนี้ "อ่างทอง" เลยแพ้ป้าย "โพธิ์ทอง"
  cities_t2..t5    เมืองอื่นตามช่วงประชากร 200k+ · 50k+ · 15k+ · 5k+ — เรียงใหญ่ไปเล็ก (เดิมไม่เรียง)
  capitals.json    เติมชื่อไทยให้กรุงเทพฯ (ช่องที่ 6) — ข้อมูลเดิมไม่เปลี่ยน
รูปแบบแถว: [ชื่อ, lat, lon] หรือ [ชื่อ, lat, lon, ชื่อไทย] สำหรับจังหวัดของไทย
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "earth")
BANDS = ((2, 200_000, None), (3, 50_000, 200_000), (4, 15_000, 50_000), (5, 5_000, 15_000))

# 76 จังหวัด + กรุงเทพมหานคร — ชื่อใน GeoNames → ชื่อไทย
TH = {
    "Bangkok": "กรุงเทพมหานคร", "Amnat Charoen": "อำนาจเจริญ", "Ang Thong": "อ่างทอง", "Bueng Kan": "บึงกาฬ",
    "Buri Ram": "บุรีรัมย์", "Chachoengsao": "ฉะเชิงเทรา", "Chai Nat": "ชัยนาท", "Chaiyaphum": "ชัยภูมิ",
    "Chanthaburi": "จันทบุรี", "Chiang Mai": "เชียงใหม่", "Chiang Rai": "เชียงราย", "Chon Buri": "ชลบุรี",
    "Chumphon": "ชุมพร", "Kalasin": "กาฬสินธุ์", "Kamphaeng Phet": "กำแพงเพชร", "Kanchanaburi": "กาญจนบุรี",
    "Khon Kaen": "ขอนแก่น", "Krabi": "กระบี่", "Lampang": "ลำปาง", "Lamphun": "ลำพูน", "Loei": "เลย",
    "Lop Buri": "ลพบุรี", "Mae Hong Son": "แม่ฮ่องสอน", "Maha Sarakham": "มหาสารคาม", "Mueang Nonthaburi": "นนทบุรี",
    "Mukdahan": "มุกดาหาร", "Nakhon Nayok": "นครนายก", "Nakhon Pathom": "นครปฐม", "Nakhon Phanom": "นครพนม",
    "Nakhon Ratchasima": "นครราชสีมา", "Nakhon Sawan": "นครสวรรค์", "Nakhon Si Thammarat": "นครศรีธรรมราช",
    "Nan": "น่าน", "Narathiwat": "นราธิวาส", "Nong Bua Lamphu": "หนองบัวลำภู", "Nong Khai": "หนองคาย",
    "Pathum Thani": "ปทุมธานี", "Pattani": "ปัตตานี", "Phang Nga": "พังงา", "Phatthalung": "พัทลุง",
    "Phayao": "พะเยา", "Phetchabun": "เพชรบูรณ์", "Phetchaburi": "เพชรบุรี", "Phichit": "พิจิตร",
    "Phitsanulok": "พิษณุโลก", "Phra Nakhon Si Ayutthaya": "พระนครศรีอยุธยา", "Phrae": "แพร่", "Phuket": "ภูเก็ต",
    "Prachin Buri": "ปราจีนบุรี", "Prachuap Khiri Khan": "ประจวบคีรีขันธ์", "Ranong": "ระนอง", "Ratchaburi": "ราชบุรี",
    "Rayong": "ระยอง", "Roi Et": "ร้อยเอ็ด", "Sa Kaeo": "สระแก้ว", "Sakon Nakhon": "สกลนคร",
    "Samut Prakan": "สมุทรปราการ", "Samut Sakhon": "สมุทรสาคร", "Samut Songkhram": "สมุทรสงคราม",
    "Saraburi": "สระบุรี", "Satun": "สตูล", "Si Sa Ket": "ศรีสะเกษ", "Sing Buri": "สิงห์บุรี", "Songkhla": "สงขลา",
    "Sukhothai": "สุโขทัย", "Suphan Buri": "สุพรรณบุรี", "Surat Thani": "สุราษฎร์ธานี", "Surin": "สุรินทร์",
    "Tak": "ตาก", "Trang": "ตรัง", "Trat": "ตราด", "Ubon Ratchathani": "อุบลราชธานี", "Udon Thani": "อุดรธานี",
    "Uthai Thani": "อุทัยธานี", "Uttaradit": "อุตรดิตถ์", "Yala": "ยะลา", "Yasothon": "ยโสธร",
}


def read_pbf(path):
    """ถอด cities.pbf (protobuf ที่ all-the-cities เขียนเอง) — พิกัดเก็บเป็นผลต่างสะสม ×1e5"""
    b = open(path, "rb").read()
    pos, last_lat, last_lon, out = 0, 0, 0, []

    def varint(p):
        r = s = 0
        while True:
            x = b[p]
            p += 1
            r |= (x & 0x7F) << s
            s += 7
            if x < 0x80:
                return r, p

    def zz(v):
        return (v >> 1) ^ -(v & 1)

    names = {2: "name", 3: "country", 7: "fc"}
    while pos < len(b):
        n, pos = varint(pos)
        end, c = pos + n, {"pop": 0}
        while pos < end:
            key, pos = varint(pos)
            tag, wt = key >> 3, key & 7
            if wt == 2:
                ln, pos = varint(pos)
                if tag in names:
                    c[names[tag]] = b[pos:pos + ln].decode("utf-8", "replace")
                pos += ln
            else:
                v, pos = varint(pos)
                if tag == 9:
                    c["pop"] = v
                elif tag == 10:
                    last_lon += zz(v)
                    c["lon"] = last_lon / 1e5
                elif tag == 11:
                    last_lat += zz(v)
                    c["lat"] = last_lat / 1e5
        out.append(c)
    return out


def row(c):
    r = [c["name"], round(c["lat"], 3), round(c["lon"], 3)]
    if c.get("country") == "TH" and c["name"] in TH:
        r.append(TH[c["name"]])
    return r


def dump(name, data):
    path = os.path.join(OUT, name)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, separators=(",", ":"))
    print(name, len(data) if isinstance(data, list) else "", os.path.getsize(path) // 1024, "KB")


def main(pkg):
    cs = [c for c in read_pbf(os.path.join(pkg, "cities.pbf")) if "lat" in c and "lon" in c and c.get("name")]
    cs.sort(key=lambda c: -c["pop"])
    admin1 = [c for c in cs if c.get("fc") == "PPLA"]
    taken = {id(c) for c in admin1} | {id(c) for c in cs if c.get("fc") == "PPLC"}
    dump("admin1.json", [row(c) for c in admin1])
    for t, lo, hi in BANDS:
        dump(f"cities_t{t}.json", [row(c) for c in cs
                                   if id(c) not in taken and c["pop"] >= lo and (hi is None or c["pop"] < hi)])
    cap_path = os.path.join(OUT, "capitals.json")
    caps = json.load(open(cap_path, encoding="utf-8"))
    for c in caps["capitals"]:
        if c[1] == "TH" and c[0] in TH:
            c[5:] = [TH[c[0]]]
    if "th" not in caps["fields"]:
        caps["fields"].append("th")
    dump("capitals.json", caps)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
