"""สร้างสถานที่ท่องเที่ยวบนลูกโลกหน้า Universe จาก Wikidata (CC0) — ข้อมูลจริง ไม่แต่งเอง

ชุดที่ 1: มรดกโลกของ UNESCO ทุกแห่งที่มีพิกัด (Wikidata P1435 = Q9259)
ชุดที่ 2: สถานที่ท่องเที่ยวสำคัญในประเทศไทย (วัด อุทยานแห่งชาติ เกาะ น้ำตก โบราณสถาน) ที่มีบทความหลายภาษา

ใช้:  python scripts/build_earth_places.py            (ต้องต่อ query.wikidata.org ได้)
ไฟล์ที่ได้: static/earth/places.json
รูปแบบแถว: [ชื่ออังกฤษ, ชื่อไทยหรือ "", lat, lon, ระดับ 1–3 (1 = คนรู้จักมากที่สุด), คำอธิบายสั้นไทยหรืออังกฤษ, Q-id, มรดกโลก 1/0]
ระดับคิดจากจำนวนภาษาที่มีบทความ Wikipedia (sitelinks) — ป้ายที่คนรู้จักมากได้ที่ก่อนเมื่อชนกัน
"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "static", "earth", "places.json")
API = "https://query.wikidata.org/sparql"
UA = "KingDiademBuild/1.0 (static data build; https://king-diadem.onrender.com)"

WHS = """
SELECT ?s ?en ?th ?c ?links ?dth ?den WHERE {
  ?s wdt:P1435 wd:Q9259; wdt:P625 ?c; wikibase:sitelinks ?links.
  OPTIONAL { ?s rdfs:label ?en FILTER(lang(?en) = "en") }
  OPTIONAL { ?s rdfs:label ?th FILTER(lang(?th) = "th") }
  OPTIONAL { ?s schema:description ?dth FILTER(lang(?dth) = "th") }
  OPTIONAL { ?s schema:description ?den FILTER(lang(?den) = "en") }
}"""

# วัด (Q44613 วัดพุทธ) · อุทยานแห่งชาติ (Q46169) · เกาะ (Q23442) · น้ำตก (Q34038) · โบราณสถาน (Q839954) · ชายหาด (Q40080)
THAI = """
SELECT ?s ?en ?th ?c ?links ?dth ?den WHERE {
  VALUES ?k { wd:Q44613 wd:Q46169 wd:Q23442 wd:Q34038 wd:Q839954 wd:Q40080 wd:Q570116 }
  ?s wdt:P17 wd:Q869; wdt:P31 ?k; wdt:P625 ?c; wikibase:sitelinks ?links.
  FILTER(?links >= 6)
  OPTIONAL { ?s rdfs:label ?en FILTER(lang(?en) = "en") }
  OPTIONAL { ?s rdfs:label ?th FILTER(lang(?th) = "th") }
  OPTIONAL { ?s schema:description ?dth FILTER(lang(?dth) = "th") }
  OPTIONAL { ?s schema:description ?den FILTER(lang(?den) = "en") }
}"""


def run(q):
    url = API + "?" + urllib.parse.urlencode({"query": q, "format": "json"})
    for i in range(4):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)["results"]["bindings"]
        except Exception as e:                      # noqa: BLE001 — เครือข่ายหลุดให้ลองใหม่
            print("retry", i + 1, e, file=sys.stderr)
            time.sleep(65)                          # Wikidata จำกัดราว 1 ครั้ง/นาทีช่วงระบบหนัก
    raise SystemExit("ต่อ query.wikidata.org ไม่ได้")


def point(wkt):
    lon, lat = wkt.replace("Point(", "").replace(")", "").split()
    return round(float(lat), 4), round(float(lon), 4)


def rows(bindings, whs):
    out = {}
    for b in bindings:
        qid = b["s"]["value"].rsplit("/", 1)[1]
        v = lambda k: b.get(k, {}).get("value", "")  # noqa: E731
        en = v("en")
        if not en or en == qid or not v("c").startswith("Point("):
            continue
        lat, lon = point(v("c"))
        links = int(v("links") or 0)
        desc = v("dth") or v("den")
        old = out.get(qid)
        if old is None or (not old[1] and v("th")):
            out[qid] = [en, v("th"), lat, lon, links, desc[:90], qid, whs]
    return out


def dedupe(places):
    """จุดเดียวกันซ้ำสองชื่อ (เช่น "Historic City of Ayutthaya" มรดกโลก กับ "Ayutthaya Historical Park") ห่างกันไม่ถึง ~1 กม.
    — เก็บแถวที่คนรู้จักมากกว่า แล้วรวมชื่อไทย/คำอธิบาย/ธงมรดกโลกจากอีกแถว (ลำดับ: รู้จักมากไปน้อย)"""
    out = []
    for r in places:
        twin = next((o for o in out if abs(o[2] - r[2]) < .009 and abs(o[3] - r[3]) < .009), None)
        if twin is None:
            out.append(r)
            continue
        twin[1] = twin[1] or r[1]
        twin[5] = twin[5] or r[5]
        twin[7] = max(twin[7], r[7])
    return out


def main(argv=None):
    if argv and argv[0] == "--dedupe-only":        # ใช้ไฟล์ที่ดึงไว้แล้ว ไม่ต้องยิง Wikidata ซ้ำ (จำกัดราว 1 ครั้ง/นาที)
        d = json.load(open(OUT, encoding="utf-8"))
        d["places"] = dedupe(d["places"])
        json.dump(d, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
        print(len(d["places"]), "places")
        return
    allp = rows(run(WHS), 1)
    time.sleep(65)
    for k, r in rows(run(THAI), 0).items():
        allp.setdefault(k, r)
    places = dedupe(sorted(allp.values(), key=lambda r: -r[4]))
    for r in places:                                # ระดับจากจำนวนภาษา: 1 = รู้จักทั่วโลก
        r[4] = 1 if r[4] >= 40 else 2 if r[4] >= 15 else 3
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"source": "Wikidata (CC0) — UNESCO World Heritage + Thai attractions",
                   "places": places}, f, ensure_ascii=False, separators=(",", ":"))
    print(len(places), "places →", OUT, os.path.getsize(OUT), "bytes")


if __name__ == "__main__":
    main(sys.argv[1:])
