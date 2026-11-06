"""หน้า /pregnancy — คู่มือคุณแม่ตั้งครรภ์ (เน้นคนที่อยู่คนเดียว) ข้อมูลจาก core/pregnancy_guide.py

สร้าง HTML ฝั่งเซิร์ฟเวอร์ทั้งหน้า ไม่มี JavaScript — เปิดได้แม้เน็ตช้า พิมพ์เก็บไว้ข้างเตียงได้
ใช้หน้าตาชุดเดียวกับคู่มือเอาชีวิตรอด (core/survival_page.py) · ทุกข้อความผ่าน html.escape
"""
from __future__ import annotations

from html import escape as e

from core.pregnancy_guide import GUIDE, SOURCES
from core.survival_page import _CSS

_HOT = [("1669", "เจ็บป่วยฉุกเฉิน · เจ็บท้องคลอด · น้ำเดิน"), ("1330", "สปสช. สิทธิบัตรทอง (ฝากครรภ์ คลอด)"),
        ("1300", "พม. 24 ชม. ที่พักปลอดภัย ความช่วยเหลือ"), ("1663", "ปรึกษาท้องไม่พร้อม (ความลับ)"),
        ("1506", "ประกันสังคม ค่าคลอด ลาคลอด"), ("1323", "สุขภาพจิต 24 ชม.")]


def render() -> str:
    hot = "".join(f'<li><a href="tel:{n}"><b>{n}</b></a>{e(label)}</li>' for n, label in _HOT)
    toc = "".join(f'<li><a href="#{k}">{e(title)}</a></li>' for k, title, _ in GUIDE)
    cards = "".join(
        f'<section class="card" id="{k}" aria-labelledby="h-{k}"><h2 id="h-{k}">{e(title)}</h2>'
        + (f'<ol class="during">' if k == "danger" else "<ul>") + "".join(f"<li>{e(r)}</li>" for r in rows)
        + ("</ol>" if k == "danger" else "</ul>") + "</section>"
        for k, title, rows in GUIDE)
    return f"""<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#04050d">
<title>คู่มือคุณแม่ตั้งครรภ์ (อยู่คนเดียวก็ปลอดภัย) · KING DIADEM</title>
<link rel="canonical" href="https://king-diadem.onrender.com/pregnancy">
<link rel="icon" href="/static/icons/favicon-48.png" sizes="48x48" type="image/png">
<meta name="description" content="สัญญาณอันตรายตอนตั้งครรภ์ที่ต้องไปโรงพยาบาลทันที แผนสำหรับคุณแม่ที่อยู่คนเดียว การฝากครรภ์ การกินอยู่ สิทธิ์และเบอร์ช่วยเหลือ — อ่านเก็บไว้ก่อนวันที่ต้องใช้">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Sans+Thai+Looped:wght@400;600&display=swap">
<style>{_CSS}</style>
</head>
<body>
<main>
<div class="top"><a href="/">← กลับไปคุยกับ LYLA</a><a href="/survival">คู่มือเอาชีวิตรอด</a></div>
<h1>คู่มือคุณแม่ตั้งครรภ์</h1>
<p class="lead">อ่านเก็บไว้ตอนนี้ ตอนที่ยังสบายดี · ถ้าอยู่คนเดียว เตรียมแผนไว้ก่อนวันที่ต้องใช้ — ข้อที่ช่วยชีวิตอยู่บนสุด</p>
<section class="card" aria-label="เบอร์ช่วยเหลือ"><h2>เบอร์ช่วยเหลือ (ประเทศไทย)</h2><ul class="hot">{hot}</ul></section>
<nav aria-label="หัวข้อ"><ul class="toc">{toc}</ul></nav>
{cards}
<p class="note">เรียบเรียงจากแนวทางสาธารณะ: {e(" · ".join(SOURCES))} — คู่มือนี้ไม่แทนการตรวจของแพทย์ ถ้าแพทย์หรือพยาบาลที่ดูแลแนะนำต่างจากนี้ ให้ทำตามแพทย์</p>
</main>
</body>
</html>"""
