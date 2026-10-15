# KING DIADEM

**ระบบช่วยตัดสินใจที่จับสัญญาณก่อนทางเลือกจะหมด — ตรรกะตรวจสอบได้เป็นแกน AI เป็นแค่เสียงพูด**

> คนไม่ได้ล้มเพราะพังวันเดียว
> คนล้มเพราะทางเลือกหายไปทีละนิด จนวันหนึ่งไม่เหลือทางไปต่อ
> KING DIADEM สร้างมาเพื่อจับสัญญาณนั้น ก่อนที่มันจะสาย

ลองใช้ได้ที่ [king-diadem.onrender.com](https://king-diadem.onrender.com) — ติดตั้งเป็นแอปบนมือถือได้ (ถ้าไม่มีคนใช้สักพัก ครั้งแรกอาจโหลดช้าราว 1 นาที)

[![Website](https://img.shields.io/badge/Website-king--diadem.onrender.com-181717?style=for-the-badge&logo=render&logoColor=white)](https://king-diadem.onrender.com)
[![Instagram](https://img.shields.io/badge/Instagram-@thekingdiadem-E4405F?style=for-the-badge&logo=instagram&logoColor=white)](https://www.instagram.com/thekingdiadem)
[![Fastwork](https://img.shields.io/badge/Fastwork-Hire%20Me-3B5BFE?style=for-the-badge&logoColor=white)](https://fastwork.co/byob/CtqOnVfzC7)

<p>
<a href="https://king-diadem.onrender.com"><img src="https://www.google.com/s2/favicons?domain=render.com&sz=64" width="28" height="28" alt="Website"/></a>&nbsp;&nbsp;
<a href="https://www.instagram.com/thekingdiadem"><img src="https://www.google.com/s2/favicons?domain=instagram.com&sz=64" width="28" height="28" alt="Instagram"/></a>&nbsp;&nbsp;
<a href="https://fastwork.co/byob/CtqOnVfzC7"><img src="https://www.google.com/s2/favicons?domain=fastwork.co&sz=64" width="28" height="28" alt="Fastwork"/></a>
</p>

---

## หลักคิดเดียว

```
Choice(t) ≥ 1 → collapse = False
```

ลองนึกถึงเข็มวัดน้ำมันรถ มันเตือนก่อนน้ำมันหมด ไม่ใช่ตอนรถดับกลางทาง KING DIADEM ทำแบบเดียวกันกับทางเลือกในชีวิต ธุรกิจ หรือระบบ

แต่ **"มีทางเดียว" ไม่เท่ากับ "มีทางเลือกจริง"** ระบบนับทางเลือกเฉพาะทางที่ผ่านครบ 3 ข้อ (`titan_choice_existence`):

- **survivable** — เดินแล้วรอด ไม่ใช่แค่ยังไม่ตายตอนนี้
- **escapable** — ออกจากทางนี้ได้ ไม่ใช่ทางที่ปิดตายไปเรื่อยๆ
- **unpunished** — ออกแล้วไม่โดนลงโทษซ้ำ

ขาดข้อใดข้อหนึ่ง ทางนั้นไม่ถูกนับ ต่อให้ตัวเลขดูเหมือนยังเหลือทาง ระบบก็ยังเตือนได้

---

## ข้อความหนึ่งข้อความเดินทางอย่างไร

ตรรกะอยู่ทั้งก่อนและหลัง AI — AI ทำหน้าที่เรียบเรียงคำพูดเท่านั้น ถ้า AI ล่มหรือไม่มี ระบบยังตอบได้จากสมการ

```
คนพิมพ์ → ตรวจโควตา · จับสัญญาณอันตราย (กฎตายตัว ไม่ใช่ AI) · อ่านความเสี่ยงและเส้นทาง
       → สภา 6 เสียง + เครื่องยนต์ตัดสินใจ (เหตุปัจจัย · waterline · ตัวเลขจริง)
       → Gemini เรียบเรียงคำตอบ หรือคำตอบจากสมการเมื่อไม่มี AI
       → ประตู Canon: ทางเลือกไม่เกิน 3 · ตรวจคำตอบก่อนส่ง
       → คนอ่าน แล้วเลือกเอง
```

ผังเต็มพร้อมแผนที่ไฟล์ทั้งหมด (สร้างจาก repo อัตโนมัติ ไม่ได้วาดมือ) ดูได้ที่หน้า [/architecture](https://king-diadem.onrender.com/architecture)

เมื่อข้อความมีสัญญาณอันตราย — อยากทำร้ายตัวเอง เจ็บป่วยฉุกเฉิน ภัยพิบัติ มิจฉาชีพ — ระบบจับด้วยกฎที่ตรวจสอบได้ก่อนถึง AI แล้วให้เบอร์ที่ตรงเรื่องทันที (1669 · 191 · 1323 ฯลฯ) ใช้ได้แม้ AI ล่ม และแม้ออฟไลน์

---

## สภา 6 เสียง

ไม่มีเสียงเดียวตัดสินแทนใคร LYLA เป็นเสียงที่คุยกับผู้ใช้ อีก 5 เสียงตรวจอยู่เบื้องหลัง (กดปุ่ม "สภา" บนเว็บเพื่อฟังครบ)

| เสียง | มุมที่มอง | หน้าที่ตอนลงมติ |
|---|---|---|
| **LYLA ◈** | รับรู้ความรู้สึก อยู่เคียงข้าง เปิดทางเลือก | นับทางเลือกที่ยังเหลือ — Choice(t) ≥ 1 |
| **VEGA ◆** | Downside-first ตรรกะ deterministic | ความเสี่ยงสูง → ตั้งรับก่อน |
| **PATICCA ☸** | ปฏิจจสมุปบาท — ตามสายเหตุปัจจัยหาต้นเหตุ | เหตุซ้อนจนใกล้ล่ม → หยุดตัดสินใจใหญ่ |
| **TITAN ▲** | เส้นทางขั้นต่ำที่ทำให้รอดวันนี้ | พื้นขั้นต่ำ: อาหาร ที่พัก waterline |
| **COSMOS ✦** | ภาพใหญ่ระยะยาว | ปั่นป่วนสูง → มองยาวก่อนเร่ง |
| **CIVIL ⬡** | แรงกระเพื่อม — เรื่องนี้ไปถึงใคร ใครช่วยแบกได้ | อยู่คนเดียว → หาแรงหนุนก่อน |

ถ้าสภาเห็นไม่ตรงกัน ระบบไม่เดาและไม่เฉลี่ย — หยุดแล้วส่งให้คนตัดสินใจ

FATE™ Axioms: Logic over Persona · Rule over Authority · Determinism (input เดิม = output เดิม) · Downside Before Upside · Explainability = 100% · **Human retains Final Authority**

---

## บนเว็บมีอะไร

| หน้า | ใช้ทำอะไร |
|---|---|
| [`/`](https://king-diadem.onrender.com) | คุยกับ LYLA / VEGA / สภา · จำลองทางเลือก · วิเคราะห์ภาพ · จักรวาลของการตัดสินใจ |
| [`/ask`](https://king-diadem.onrender.com/ask) | ถามแบบมีตัวเลือก A / B ให้ชั่งตรงๆ |
| [`/guide`](https://king-diadem.onrender.com/guide) | คู่มือใช้งานแบบอ่านง่าย |
| [`/letter`](https://king-diadem.onrender.com/letter) | จดหมายจากผู้ก่อตั้ง — COSMIC LATTE CANON (ไทย / English) |
| [`/architecture`](https://king-diadem.onrender.com/architecture) | สถาปัตยกรรมและแผนที่ไฟล์ทั้งระบบ |
| `/report/<id>` | รายงานที่ผู้ใช้กดแชร์เอง — เปิดได้ 90 วัน เจ้าของลบได้ |
| [`/wallet`](https://king-diadem.onrender.com/wallet) | เครดิต · Premium · จัดการสมาชิก |

ใช้ได้ทั้งภาษาไทย อังกฤษ และญี่ปุ่น · ตัวจับเรื่องเร่งด่วนอ่านได้อีกหลายภาษา · ติดตั้งเป็นแอป (PWA) และเปิดหน้าเบอร์ฉุกเฉินได้ตอนไม่มีเน็ต

---

## ความเป็นส่วนตัวและความปลอดภัย

- ไม่ล็อกอิน = ไม่เก็บข้อความ · ล็อกอินแล้ว ประวัติเป็นของบัญชีนั้น ดาวน์โหลดหรือส่งเข้าอีเมลของตัวเองได้
- log ของเซิร์ฟเวอร์ไม่บันทึกข้อความผู้ใช้
- cookie เซ็นด้วยกุญแจลับ · รหัสผ่านแฮช PBKDF2 · จำกัดการเดารหัสและการสมัครรัวๆ
- เครดิตผูกกับยอดที่ Stripe เก็บจริง ตรวจลายเซ็น webhook และกันเติมซ้ำ
- จำกัดขนาดคำขอ กันคำขอก้อนเดียวทำเซิร์ฟเวอร์ล่ม

---

## กฎที่ใช้แม้แต่กับผู้สร้างเอง

1. **ดูของจริงก่อนสรุป** — ไม่เดา ต้องมีหลักฐาน
2. **ใครก็หยุดระบบได้ ถ้าเห็นว่ากำลังจะพัง**
3. **ซ่อมฐานให้แน่นก่อน ค่อยต่อเติม**

override ทุกครั้งต้องมีหลักฐาน ผู้ลงนามจริง วันหมดอายุ และ audit ย้อนหลัง — ผู้สร้างเองก็ไม่มีสิทธิพิเศษ ถ้าเจ้าของขอ override ก็โดน flag ให้ถอนตัว (auto-recusal) เหมือนกัน

**"The system does not break. It refuses."**

เมื่อคุณตัดสินใจแล้ว ระบบหยุดพูดและถอยออกไป — ทางเลือกสุดท้ายเป็นของคุณเสมอ

---

## เบื้องหลังทางเทคนิค

**Stack:** FastAPI · Python · Google Gemini · SQLite · HTML / CSS / JS (canvas + WebGL) · Render
**Scale:** 397 ไฟล์ · Python ที่ใช้งานจริง 192 ไฟล์ (+ โค้ดเก่าเก็บไว้ใน [`legacy/`](legacy/README.md)) · 1,900+ commits

| โฟลเดอร์ | หน้าที่ |
|---|---|
| `app.py` | เว็บเซิร์ฟเวอร์และเส้นทางของ `/run` ทั้งหมด |
| `core/` | แก่นตรรกะ — อ่านสัญญาณภาษา · คำตอบจากสมการ · สมอง AI · ประตู Canon |
| `ENGINE/` `DOMAINS/` | เครื่องยนต์ตัดสินใจ · เหตุปัจจัย · หนี้ · ธุรกิจ |
| `AI/` `AI_KERNEL/` | สภา 6 เสียง · หน่วยความจำการตัดสินใจ · Cosmic Latte |
| `DATABASE/` | บัญชี · เครดิต · ประวัติ (SQLite) |
| `SECURITY/` `WORLD_MODEL/` `SIMULATIONS/` | ตัววัดโหลด · แบบจำลองคนและโลก · การจำลอง |
| `static/` | หน้าเว็บทั้งหมด · service worker · ไอคอนแอป |
| `tests/` | ชุดทดสอบ |

### รันบนเครื่อง

```
pip install -r requirements-dev.txt
export SECRET_KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
export GEMINI_API_KEY=...        # ไม่ใส่ก็ได้ — ระบบตอบจากสมการแทน
uvicorn app:app --reload
```

### ทดสอบ

```
pytest                          # 1,870+ ข้อ — ไม่ใช้เน็ต ไม่เสียค่า AI (Gemini เป็นตัวปลอม)
python scripts/eval_corpus.py   # วัดผลกับประโยคที่คนพิมพ์จริง 492 ประโยค
```

`tests/corpus/messages.tsv` คือประโยคจริงพร้อมผลที่ควรได้ — เจอประโยคที่ระบบพลาด เพิ่มลงไฟล์นี้ก่อนแก้

---

## ไม่ได้สร้างมาเพื่อชนะ

สร้างมาเพื่อ **ไม่พังซ้ำ**

**Fail less. Harm less. Restore more.**

---

## Support

จ้างงานได้ที่ [Fastwork](https://fastwork.co/byob/CtqOnVfzC7) หรือทักผ่าน [Instagram](https://www.instagram.com/thekingdiadem) — รับสร้างระบบ AI / decision infrastructure แบบนี้โดยตรง

## License

[GNU AGPL-3.0](LICENSE) — ใครเอาไปเปิดเป็นบริการ ต้องเปิดซอร์สโค้ดให้ผู้ใช้ด้วย
ลิขสิทธิ์และเจตนารมณ์ของผู้สร้างอยู่ใน [NOTICE](NOTICE)

Open governance framework. No proprietary claim. Not for profit. Use it to survive.
