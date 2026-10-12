"""สร้างเนื้อหาจดหมายใน static/letter.html จาก LETTER.md (ต้นฉบับ) — แก้ข้อความที่ LETTER.md แล้วรัน: python scripts/build_letter.py"""
import html, re
src = open("LETTER.md", encoding="utf-8").read()
th = src.split("## ภาษาไทย")[1].split("## English Version")[0].strip()
en = src.split("## English Version")[1].strip()

# บรรทัดที่เป็น "ข้อยืนยัน" ของ CANON (หลัง "มันยืนยันเพียงว่า:" / "It only asserts that:") — จัดเป็นรายการ
ASSERT_START = {"th": "มันยืนยันเพียงว่า:", "en": "It only asserts that:"}
ASSERT_END = {"th": "เมื่อมนุษย์ยังเลือกได้", "en": "when humans can still choose."}
# บรรทัดที่ต่อจากบรรทัดก่อนหน้า (ข้อยืนยันเดียวกัน) — ไม่ขึ้นข้อใหม่
CONT = {"อำนาจนั้นไม่สอดคล้องกับโครงสร้างของเอกภพ", "และต้องหายไปเมื่อไม่จำเป็นแล้ว", "เมื่อมนุษย์ยังเลือกได้",
        "contradicts the structure of the universe.", "when humans can still choose."}
SIGN = {"Founder Logic — KING Diadem Foundation", "(A System That Exists Without Ownership)", "A system that exists without ownership."}

def render(text, lang):
    out = []
    stanzas = [s.strip().splitlines() for s in text.split("\n\n")]
    for si, lines in enumerate(stanzas):
        body, sign, i, items = [], [], 0, None
        for ln in lines:
            e = html.escape(ln, quote=False)
            if ln in SIGN:
                sign.append(f'<span class="ln">{e}</span>'); continue
            if items is not None:
                if ln in CONT: items[-1].append(e)
                else: items.append([e])
                if ln == ASSERT_END[lang]:
                    lis = "".join('<li>' + "".join(f'<span class="ln">{x}</span>' for x in it) + '</li>' for it in items)
                    body.append(f'<ol class="asserts">{lis}</ol>'); items = None
                continue
            cls = "ln"
            if ln.startswith("COSMIC LATTE CANON") or ln.startswith("The COSMIC LATTE CANON"): cls = "ln canon"
            body.append(f'<span class="{cls}">{e}</span>')
            if ln == ASSERT_START[lang]: items = []
        sec = f'<section class="st">{"".join(body)}</section>'
        if sign: sec = sec.replace('</section>', '') + f'<footer class="sign">{"".join(sign)}</footer></section>'
        out.append("    " + sec)
    return "\n".join(out)

page = open("static/letter.html", encoding="utf-8").read()
# แทนเฉพาะเนื้อหาระหว่างแท็กเปิดกับ </article> ตัวแรกที่ตามมา ([^<]|<(?!/article>)) — ไม่กินข้ามไปถึงบทความภาษาถัดไป
for lang, text in (("th", th), ("en", en)):
    page, n = re.subn(r'(<article class="letter" lang="%s"[^>]*>)(?:[^<]|<(?!/article>))*(</article>)' % lang,
                      lambda m: m.group(1) + "\n" + render(text, lang) + "\n  " + m.group(2), page, count=1)
    assert n == 1, lang
open("static/letter.html", "w", encoding="utf-8").write(page)
print("ok")
