"""หน้า /survival — คู่มือเอาชีวิตรอดฉบับเต็ม (ข้อมูลจาก core/survival_guide.py)

สร้าง HTML ฝั่งเซิร์ฟเวอร์ทั้งหน้า ไม่มี JavaScript: ตอนเกิดภัยเน็ตช้า มือถือเก่า แบตใกล้หมด ก็ยังเปิดอ่านได้ และพิมพ์เก็บได้
ทุกข้อความผ่าน html.escape · ลิงก์ภายนอกเป็นข้อความ (ชื่อหน่วยงาน · โดเมน) ไม่ใช่ลิงก์กดได้ — ผู้ใช้พิมพ์เองตรวจได้
"""
from __future__ import annotations

from html import escape as e

from core.survival_guide import public

_T = {
    "th": {"title": "คู่มือเอาชีวิตรอดจากภัยพิบัติ", "lead": "ทำข้อแรกก่อนเสมอ — ข้อที่ช่วยชีวิตอยู่บนสุดของแต่ละหมวด · อ่านตอนนี้ตอนที่ยังปลอดภัย จะจำได้ตอนตกใจ",
           "signs": "สัญญาณ", "before": "เตรียมก่อนเกิด", "during": "ขณะเกิด — ทำตามลำดับ", "after": "หลังเกิด",
           "vulnerable": "เด็ก ผู้สูงอายุ ผู้พิการ", "myths": "ความเชื่อผิดที่อันตราย", "sources": "อ้างอิง",
           "kit": "กระเป๋าฉุกเฉิน (เตรียมไว้ใช้ได้ทุกภัย)", "hot": "เบอร์ฉุกเฉิน (ประเทศไทย)", "back": "← กลับไปคุยกับ LYLA",
           "note": "คู่มือนี้รวบรวมจากแนวทางของกาชาด/IFRC · WHO · ปภ. · FEMA · USGS · NOAA · CDC — ถ้าเจ้าหน้าที่ในพื้นที่สั่งต่างจากนี้ ให้ทำตามเจ้าหน้าที่",
           "other": "English"},
    "en": {"title": "Disaster survival guide", "lead": "Always do the first step first — the life-saving step is at the top of each list · read it now while you're safe so you remember it in a panic",
           "signs": "Warning signs", "before": "Prepare", "during": "During — in this order", "after": "Afterwards",
           "vulnerable": "Children, older people, disabilities", "myths": "Dangerous myths", "sources": "Sources",
           "kit": "Emergency bag (works for every hazard)", "hot": "Emergency numbers (Thailand)", "back": "← Back to LYLA",
           "note": "Compiled from Red Cross/IFRC · WHO · Thai DDPM · FEMA · USGS · NOAA · CDC guidance — if local officials tell you otherwise, follow them",
           "other": "ภาษาไทย"},
}

_CSS = """
:root{--bg:#04050d;--ink:#eef1fa;--ink-2:#c4cbe0;--ink-3:#8e97b5;--line:rgba(160,180,255,.18);--gold:#ffd28f;--bad:#ffb3b3;--ok:#a8f0c8;
  --f:"Noto Sans Thai Looped",system-ui,-apple-system,"Segoe UI",sans-serif}
*{box-sizing:border-box}html{background:var(--bg);color:var(--ink)}
body{margin:0;font:400 16px/1.75 var(--f);background:radial-gradient(1200px 600px at 50% -10%,#141a44 0%,var(--bg) 60%)}
main{max-width:820px;margin:0 auto;padding:22px 16px 80px}
a{color:var(--gold)}.top{display:flex;justify-content:space-between;align-items:center;gap:12px;margin-bottom:12px;font-weight:600}
.top a{text-decoration:none}h1{font-size:27px;line-height:1.35;margin:6px 0}.lead{color:var(--ink-2);margin:0 0 16px}
.toc{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 18px;padding:0;list-style:none}
.toc a{display:inline-flex;align-items:center;gap:6px;min-height:40px;padding:6px 14px;border:1px solid var(--line);border-radius:999px;text-decoration:none;color:var(--ink);background:rgba(20,26,64,.4)}
.card{border:1px solid var(--line);border-radius:18px;padding:16px 18px;background:rgba(20,26,64,.35);margin:0 0 16px;scroll-margin-top:12px}
.card h2{font-size:22px;margin:0 0 6px}.card h3{font-size:15.5px;margin:14px 0 4px;color:var(--gold);letter-spacing:.01em}
.card ul,.card ol{margin:0;padding-left:22px}.card li{color:var(--ink-2);margin:4px 0}
.card ol.during li{color:var(--ink)}.card ol.during li:first-child{font-weight:600}
.kd-i{width:1.15em;height:1.15em;vertical-align:-.22em;flex:none}
.card .myths li{color:var(--bad);list-style:none;margin-left:-22px}.card .src{color:var(--ink-3);font-size:13.5px}
.card .hot{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px;margin:8px 0 0;padding:0;list-style:none}
.hot li{border:1px solid var(--line);border-radius:12px;padding:8px 12px;color:var(--ink-2)}.hot b{display:block;font-size:22px;color:var(--gold)}
.hot a{text-decoration:none}.note{color:var(--ink-3);font-size:14px}
:focus-visible{outline:2px solid var(--gold);outline-offset:2px}
@media print{body{background:#fff;color:#000}.card{break-inside:avoid;border-color:#999;background:none}.card li,.lead,.note{color:#000}.toc,.top{display:none}}
"""



def _ic(name: str) -> str:
    """ไอคอนลายเส้นจาก static/icons/kd.svg (แทนอิโมจิ) — ชื่อมาจาก core/survival_guide.py เท่านั้น ไม่ใช่จากผู้ใช้"""
    name = name if name.isalnum() else "spark"
    return f'<svg class="kd-i" width="1.15em" height="1.15em" aria-hidden="true"><use href="/static/icons/kd.svg#{name}"/></svg>'

def render(lang: str = "th") -> str:
    lang = "en" if lang == "en" else "th"
    t, g = _T[lang], public(lang)
    other = "en" if lang == "th" else "th"
    hot = "".join(f'<li><a href="tel:{e(h["n"])}"><b>{e(h["n"])}</b></a>{e(h["label"])}</li>' for h in g["hotlines"])
    toc = "".join(f'<li><a href="#{e(h["key"])}">{_ic(h["icon"])} {e(h["name"])}</a></li>' for h in g["hazards"])

    def sec(key, rows, tag="ul", cls=""):
        if not rows:
            return ""
        items = "".join(f"<li>{e(r)}</li>" for r in rows)
        return f'<h3>{e(t[key])}</h3><{tag}{f" class={chr(34)}{cls}{chr(34)}" if cls else ""}>{items}</{tag}>'

    cards = "".join(
        f'<section class="card" id="{e(h["key"])}" aria-labelledby="h-{e(h["key"])}">'
        f'<h2 id="h-{e(h["key"])}">{_ic(h["icon"])} {e(h["name"])}</h2>'
        + sec("during", h["during"], "ol", "during") + sec("signs", h["signs"]) + sec("before", h["before"])
        + sec("after", h["after"]) + sec("vulnerable", h["vulnerable"]) + sec("myths", h["myths"], "ul", "myths")
        + f'<h3>{e(t["sources"])}</h3><p class="src">{e(" · ".join(h["sources"]))}</p></section>'
        for h in g["hazards"])
    kit = "".join(f"<li>{e(k)}</li>" for k in g["kit"])
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#04050d">
<title>{e(t["title"])} · KING DIADEM</title>
<link rel="canonical" href="https://king-diadem.onrender.com/survival{"?lang=en" if lang == "en" else ""}">
<link rel="icon" href="/static/icons/favicon-48.png" sizes="48x48" type="image/png">
<meta name="description" content="{e(t["lead"])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai+Looped:wght@400;600&display=swap">
<style>{_CSS}</style>
</head>
<body>
<main>
<div class="top"><a href="/">{e(t["back"])}</a><a href="/survival?lang={other}" hreflang="{other}">{e(t["other"])}</a></div>
<h1>{e(t["title"])}</h1>
<p class="lead">{e(t["lead"])}</p>
<section class="card" aria-label="{e(t["hot"])}"><h2>{e(t["hot"])}</h2><ul class="hot">{hot}</ul></section>
<nav aria-label="{e(t["title"])}"><ul class="toc">{toc}</ul></nav>
{cards}
<section class="card" id="kit"><h2>{_ic("bag")} {e(t["kit"])}</h2><ul>{kit}</ul></section>
<p class="note">{e(t["note"])}</p>
</main>
</body>
</html>"""
