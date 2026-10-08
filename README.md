# KING DIADEM

**ระบบธรรมาภิบาลการตัดสินใจแบบดีเทอร์มินิสติก — จับสัญญาณก่อนทางเลือกจะเหลือศูนย์แบบย้อนกลับไม่ได้**

> คนไม่ได้ล้มเพราะพังวันเดียว
> คนล้มเพราะทางเลือกหายไปทีละนิด จนวันหนึ่งไม่เหลือทางไปต่อ
> KING DIADEM สร้างมาเพื่อจับสัญญาณนั้น ก่อนที่มันจะสาย

สร้างโดย นิธิกร บุญสร้าง

---

ลองใช้ได้ที่ [king-diadem.onrender.com](https://king-diadem.onrender.com) (เว็บฟรีบน Render — ถ้าไม่มีคนใช้สักพัก ครั้งแรกอาจโหลดช้าราว 1 นาที)
ทักงานได้ที่ Instagram หรือ Fastwork — รับสร้างระบบ AI / decision infrastructure แบบนี้โดยตรง

[![Website](https://img.shields.io/badge/Website-king--diadem.onrender.com-181717?style=for-the-badge&logo=render&logoColor=white)](https://king-diadem.onrender.com)
[![Instagram](https://img.shields.io/badge/Instagram-@thekingdiadem-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/thekingdiadem)
[![Fastwork](https://img.shields.io/badge/Fastwork-Hire%20Me-3B5BFE?style=for-the-badge&logoColor=white)](https://fastwork.co/user/thekingdiadem)

<p>
<a href="https://king-diadem.onrender.com"><img src="https://www.google.com/s2/favicons?domain=render.com&sz=64" width="28" height="28" alt="Website"/></a>&nbsp;&nbsp;
<a href="https://www.instagram.com/thekingdiadem"><img src="https://www.google.com/s2/favicons?domain=instagram.com&sz=64" width="28" height="28" alt="Instagram"/></a>&nbsp;&nbsp;
<a href="https://fastwork.co/user/thekingdiadem"><img src="https://www.google.com/s2/favicons?domain=fastwork.co&sz=64" width="28" height="28" alt="Fastwork"/></a>
</p>

---

## นี่ไม่ใช่ chatbot และไม่ใช่พรอมพ์เดียว แต่คือภาษาโครงสร้างที่ใช้ได้ทั่วโลก ทุกคนคุยกันรู้เรื่องได้ในภาษาเดียวกัน

พรอมพ์ตั้งต้นของ KING DIADEM เริ่มจากประโยคเดียว: อย่าปล่อยให้ทางเลือกเหลือศูนย์ วันนี้มันไม่ใช่แค่นั้นแล้ว

หลังจากพัฒนาต่อเนื่อง ระบบกลายเป็น **governance kernel ที่มีสภา 6 เสียง** — 341 ไฟล์ (Python 265 ไฟล์), 1,800+ commits, 19 modules ที่ประกอบด้วย axiom system ตายตัว, สภาที่ต้องมองครบทุกมุมก่อนตัดสินใจ, severity scale ที่จัดชั้นความเสียหายจริง, และกลไก anti-capture ที่บล็อกไม่ให้แม้แต่ผู้สร้างเองยึดระบบคืนได้ตามใจ

หัวใจยังเป็นสัจธรรมเดิม แต่ตอนนี้มันรันผ่านเลเยอร์จริง ไม่ใช่แค่คำเตือนลอยๆ

---

## หลักคิดตั้งต้น — และจุดที่คนมักเข้าใจผิด

ลองนึกภาพเข็มวัดน้ำมันรถ มันเตือนก่อนน้ำมันหมด ไม่ใช่ตอนรถดับกลางทาง KING DIADEM ทำแบบเดียวกันกับทางเลือกในชีวิต ธุรกิจ หรือระบบ

```
Choice(t) ≥ 1 → collapse = False
```

ถ้ายังมีทางเลือกอย่างน้อย 1 ทาง ระบบยังไม่พัง — นี่คือสัจธรรมตั้งต้น

แต่ **"มีทางเดียว" ไม่เท่ากับ "มีทางเลือกจริง"** ทางเดียวที่ยังลากไปตายอยู่ดี ไม่ใช่ทางเลือก มันคือคำนับถอยหลังที่ยังไม่มีใครประกาศ

TITAN Section 2 (`titan_choice_existence`) เช็ค 3 เงื่อนไขต่อทางเลือกทุกทางเสมอ ก่อนจะนับว่าเป็นทางเลือกจริง:

- **survivable** — เดินแล้วรอด ไม่ใช่แค่ยังไม่ตายตอนนี้
- **escapable** — ออกจากทางนี้ได้ ไม่ใช่ทางเดียวที่ปิดตายไปเรื่อยๆ
- **unpunished** — ออกแล้วไม่โดนลงโทษซ้ำ

ขาดข้อใดข้อหนึ่ง = ทางเลือกนั้นไม่ถูกนับใน O (จำนวนทางเลือกจริงที่เหลือ) ต่อให้ตัวเลขดูเหมือนมากกว่า 0 ระบบก็ยังฟันธง **collapse = True** ได้ ถ้าทุกทางที่เหลือไม่ผ่านทั้ง 3 ข้อนี้

---

## สภา 6 เสียง

ระบบไม่ตัดสินใจด้วยเสียงเดียว ทุกเรื่องผ่านสภาที่มองคนละมุม แล้วค่อยส่งกลับมาหาคน — LYLA เป็นเสียงที่คุยกับผู้ใช้ ส่วนอีก 5 เสียงช่วยตรวจอยู่เบื้องหลัง (กดปุ่ม "สภา" บนเว็บเพื่อฟังครบทุกเสียง)

| เสียง | มุมที่มอง | หน้าที่ตอนลงมติ |
|---|---|---|
| **LYLA ◈** | รับรู้ความรู้สึก อยู่เคียงข้าง เปิดทางเลือก | นับทางเลือกที่ยังเหลือ — Choice(t) ≥ 1 |
| **VEGA ◆** | Downside-first ตรรกะ deterministic | ความเสี่ยงสูง → ตั้งรับก่อน |
| **PATICCA ☸** | ปฏิจสมุปบาท — หาต้นเหตุ ตามสายเหตุปัจจัย | เหตุปัจจัยซ้อนกันจนใกล้ล่ม → หยุดตัดสินใจใหญ่ |
| **TITAN ▲** | เส้นทางขั้นต่ำที่ทำให้รอดวันนี้ | พื้นขั้นต่ำ: อาหาร ที่พัก waterline |
| **COSMOS ✦** | ภาพใหญ่ระยะยาว | ความปั่นป่วนสูง → มองยาวก่อนเร่ง |
| **CIVIL ⬡** | แรงกระเพื่อม — เรื่องนี้ไปถึงใครบ้าง ใครช่วยแบกได้ | อยู่คนเดียว → หาแรงหนุนก่อน |

ข้อห้ามร่วมทุกเสียง: ห้ามอ้างว่ามีชีวิตจริง · ห้ามอ้าง memory ถาวร · ห้ามอ้างอำนาจ · ห้ามสร้าง dependency

ถ้าสภาเห็นไม่ตรงกัน ระบบไม่เดาไม่เฉลี่ย — หยุดแล้วส่งต่อให้คนตัดสินใจ ไม่มีทางที่ AI ตัวเดียวตัดสินใจแทนคนได้

เมื่อข้อความมีสัญญาณอันตราย (อยากทำร้ายตัวเอง เจ็บป่วยฉุกเฉิน ภัยพิบัติ มิจฉาชีพ ฯลฯ) ระบบจับด้วยกฎที่ตรวจสอบได้ก่อนถึง AI แล้วให้เบอร์สายด่วนที่ตรงเรื่องทันที — ถึง AI ล่มก็ยังตอบได้

FATE™ Axioms ที่ VEGA ยึดตายตัว: Logic over Persona · Rule over Authority · Determinism (input เดิม = output เดิมเสมอ) · Downside Before Upside · Explainability = 100% · และข้อสุดท้ายที่แก้ไม่ได้เด็ดขาด — **Human retains Final Authority**

---

## กฎที่ใช้แม้แต่กับผู้สร้างเอง

1. **ดูของจริงก่อนสรุป** — ไม่เดา ไม่มโน ต้องมีหลักฐาน
2. **ใครก็หยุดระบบได้ ถ้าเห็นว่ากำลังจะพัง** — ไม่ต้องรอสั่งจากบนลงล่าง
3. **ซ่อมฐานให้แน่นก่อน ค่อยพัฒนาต่อ** — อย่าต่อเติมบนของที่พังอยู่

override ทุกครั้งต้องมีครบ: evidence file, ผู้ลงนามจริง, วันหมดอายุ, audit ย้อนหลัง ห้าม anonymous ห้าม emergency exception และ **ผู้สร้างระบบเองก็ไม่มีสิทธิพิเศษ** — ถ้าเจ้าของระบบขอ override ก็โดน flag ให้ auto-recusal เหมือนกันหมด พยายามยึดระบบ = ระบบ void ตัวเองทันที

**"The system does not break. It refuses."**

---

## ท่าทีของระบบต่อผู้ใช้

ระบบนี้ไม่ได้สร้างมาเพื่อบอกว่าใครถูกใครผิด ไม่ตัดสินคุณค่าของใคร ไม่ปลอบใจแบบลอยๆ และไม่ตามตื้อให้ทำตาม

หน้าที่ของมันคือช่วยตัดสิ่งที่ไม่จำเป็นออกไป จนเหลือแต่สิ่งที่ต้องรับผิดชอบจริงๆ ตรงหน้า

เมื่อคุณตัดสินใจแล้ว มันหยุดพูดและถอยออกไป เพราะทางเลือกสุดท้ายเป็นของคุณเสมอ ไม่ใช่ของระบบ

---

## ใช้กับใครได้บ้าง

คนที่กำลังเจอสถานการณ์จริง — ตกงาน มีหนี้ ธุรกิจจะพัง ความสัมพันธ์กำลังแตก ไม่ได้ให้คำแนะนำสวยหรู แต่คำนวณให้เห็นว่าตอนนี้ยังมีทางไหนที่ survivable + escapable + unpunished จริง ใช้ได้ทั้งกับคนคนเดียว ธุรกิจ หรือระบบ AI อื่น

---

## เบื้องหลังทางเทคนิค

```
Human Input → ตัวจับสัญญาณอันตราย (deterministic) → FATE™ Decision Engine → สภา 6 เสียง
→ ตรวจ Waterline (food/water/shelter) → คำนวณ O (ทางเลือกจริงที่เหลือ)
→ ส่งทางเลือกกลับมาอย่างน้อย 1 ทาง ที่ผ่านทั้ง survivable + escapable + unpunished
```

**Stack:** FastAPI · Python · Gemini · SQLite · HTML/JS/CSS · Render
**Scale:** 341 ไฟล์ (Python 265) · 1,800+ commits · 19 modules (core, ENGINE, DOMAINS, KERNEL, PERSONA, SECURITY, WORLD_MODEL, SIMULATIONS, AI, AI_KERNEL, AUTH, DATABASE, PAYMENT, NETWORK ฯลฯ)
**ภาษา:** ไทยเป็นหลัก · จับเรื่องเร่งด่วนได้ในภาษาอังกฤษ จีน ญี่ปุ่น เกาหลี สเปน

หน้าเว็บมี galaxy visualization แบบ canvas ที่แปลงเส้นทางการตัดสินใจให้เห็นเป็นภาพจริง ไม่ใช่แค่ text output

---

## ทดสอบ

```
pip install -r requirements-dev.txt
pytest                          # เทสต์ทั้งหมด ~1,480 ข้อ
python scripts/eval_corpus.py   # วัดผลกับประโยคจริง 459 ประโยค
```

ชุดทดสอบใน `tests/` ไม่ใช้เน็ตและไม่เสียค่า AI (Gemini เป็นตัวปลอม) ครอบคลุม: วลีไทยที่ต้องดูบริบท, ตัวจับวิกฤตทุกตัว, จับเจตนา, คำตอบจากสมการเมื่อไม่มี AI, การพักวงจรตอน AI ล่ม, โควตา/เครดิต/ล็อกอิน และ Stripe webhook

`tests/corpus/messages.tsv` คือประโยคที่คนพิมพ์จริงพร้อมผลที่ควรได้ — เจอประโยคที่ระบบพลาด ให้เพิ่มลงไฟล์นี้ก่อนแก้

---

## ไม่ได้สร้างมาเพื่อชนะ

สร้างมาเพื่อ **ไม่พังซ้ำ**

**Fail less. Harm less. Restore more.**

---

## Support

จ้างงานได้ที่ [Fastwork](https://fastwork.co/user/thekingdiadem) หรือทักผ่าน [Instagram](https://www.instagram.com/thekingdiadem)

---

## License

[GNU AGPL-3.0](LICENSE) — ใครเอาไปเปิดเป็นบริการ ต้องเปิดซอร์สโค้ดให้ผู้ใช้ด้วย
ลิขสิทธิ์และเจตนารมณ์ของผู้สร้างอยู่ใน [NOTICE](NOTICE)

Open governance framework. No proprietary claim. Not for profit. Use it to survive.
