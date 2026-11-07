# KING DIADEM — Compliance Mapping (ISO/IEC 42001 · EU AI Act · ร่าง พ.ร.บ. AI ไทย)

อัปเดต 7 พ.ย. 2026 จากฉบับ 18 ต.ค. 2026 ใน Google Drive · สถานะทุกข้อตรวจกับ repo วันที่ 7 พ.ย. 2026

## สรุปสิ่งที่เปลี่ยน

- เทสต์อัตโนมัติ: จาก 972 เป็น **5,300+ ข้อ** ผ่านทั้งหมด
- Gap ที่ปิดแล้วหลังฉบับเดิม: แจ้งผู้ใช้ว่าเป็น AI (Art. 50), Audit log แบบ hash chain เก็บ 6 เดือน, เอกสาร AI Policy · Risk Register · Incident Runbook · Vendor Risk, เทสต์ prompt injection, การหมุน API key
- Gap ที่ยังเปิด: **เพดานการเรียก LLM / ค่าใช้จ่ายต่อวัน (spend limit)** — ตอนนี้มีแค่เพดานเวลาต่อครั้ง

## ตาราง mapping

| # | Control ใน KING DIADEM | หน้าที่ (ศัพท์มาตรฐาน) | ISO/IEC 42001 | EU AI Act | ต.ค. | พ.ย. | หลักฐานใน repo |
|---|---|---|---|---|---|---|---|
| 1 | FATE™ 6 axioms · Pure Axis | AI policy | 5.2 · A.2 | Art. 9 | บางส่วน | **มีแล้ว** | `docs/governance/AI_POLICY.md` |
| 2 | DriftZero Waterline | Performance monitoring | 9.1 · A.6.2.6 | Art. 15 · 72 | มีแล้ว | มีแล้ว | drift monitor |
| 3 | Stop-the-Line · SYSTEM_PAUSE | Kill-switch / safe stop | A.6.2.6 | Art. 14(4)(e) | มีแล้ว | มีแล้ว | `AI/council_engine.py` · `AI_KERNEL/` |
| 4 | Human Final Authority | Human oversight | A.9 | Art. 14 · 26 | บางส่วน | บางส่วน | ยังไม่มีหน้า UI ให้ผู้ดูแล approve/override |
| 5 | GALAXY Decision Trace · คำเตือนท้ายหน้า | Transparency | A.8 | Art. 13 · **50(1)** | บางส่วน | **มีแล้ว** | ท้ายหน้าแชต "LYLA และ VEGA เป็นระบบ AI ไม่ใช่คน" แปลครบ 7 ภาษา |
| 6 | risk_engine · collapse_predictor | Risk assessment | 6.1.2 · A.5 | Art. 9 | มีแล้ว | มีแล้ว | + `RISK_REGISTER.md` |
| 7 | bodhipakkhiya_engine · canon_gate | Pre-execution gate · output validation | 8.1 · A.6 | Art. 15 | มีแล้ว | มีแล้ว | ไม่ส่งเครื่องมือ (tools) ให้โมเดลเลย |
| 8 | `core/audit_log.py` | Audit trail | A.6.2.8 | Art. 12 · 26(6) | บางส่วน | **มีแล้ว** | append-only + hash chain · `RETENTION_MONTHS = 6` |
| 9 | Determinism · เทสต์ | Verification & validation | A.6.2.4 | Art. 15 | มีแล้ว (972) | มีแล้ว (5,300+) | `tests/` · ชุดทดสอบปิดตา · ทะเบียนข้อเท็จจริง |
| 10 | Agent security | Prompt injection · key mgmt · spend limit | A.6 · 8.1 | Art. 15(5) | ยังไม่มี | **บางส่วน** | `tests/test_prompt_injection.py` · หมุน API key · **ยังไม่มี spend limit** |
| 11 | Incident reporting | Incident reporting | 10.2 | Art. 73 | ยังไม่มี | **มีแล้ว** | `INCIDENT_RUNBOOK.md` |
| 12 | Gemini API (vendor) | Supplier management | A.10 | Art. 25 | ยังไม่มี | **มีแล้ว** | `VENDOR_RISK.md` · ตอบจากสมการได้เมื่อ Gemini ล่ม |

สรุป: มีแล้ว 9 · บางส่วน 3 · ยังไม่มี 0 (ฉบับ ต.ค.: 5 · 4 · 3)

## Control ใหม่ที่ควรใส่ในเอกสารลูกค้า

- **Verified Fact Registry** — ทุกเบอร์โทรและตัวเลขกฎหมาย/การแพทย์ในคำตอบมีแหล่งอ้างอิงและสถานะการตรวจ (`core/hotlines.py` · `core/knowledge_pack_facts.py`) เทสต์ล้มทันทีถ้ามีตัวเลขใหม่ที่ไม่ได้ลงทะเบียน → ISO A.6.2.4 / EU Art. 15 (accuracy)
- **Life-first Response Precedence** — ถ้ามีคนไม่หายใจ ขั้นตอน CPR มาก่อนทุกคำตอบ หัวข้อเฉพาะตอบก่อนหัวข้อกว้าง → Art. 9 (risk mitigation)
- **Deterministic Crisis Response Path** — เรื่องวิกฤตตอบจากสมการ ไม่ผ่าน LLM → ลดความเสี่ยงจาก vendor และ hallucination

## Gap ที่ต้องปิดต่อ (เรียงตามผลกระทบ)

- [ ] Spend limit: เพดานจำนวนครั้งที่เรียก LLM ต่อวัน เกินแล้วตอบจากสมการแทน (#10)
- [ ] หน้า UI ให้ผู้ดูแลระบบ approve/override และบันทึกลง audit log (#4)
- [ ] ให้คนตรวจตัวเลขใน registry แล้วเปลี่ยนเป็น verified (ตอนนี้เป็น False ทุกข้อ) — `python scripts/hotline_review.py`
- [ ] ตรวจเลข clause ISO/IEC 42001 กับตัวมาตรฐานฉบับจริง
- [ ] อัปเดตตารางเมื่อ พ.ร.บ. AI ไทยประกาศในราชกิจจานุเบกษา

## Glossary สองชั้น

ชื่อภายในยังใช้ได้ เอกสารที่ส่งให้คนภายนอกใช้ชื่อมาตรฐานนำ แล้ววงเล็บชื่อภายใน

| ชื่อภายใน | ชื่อมาตรฐาน |
|---|---|
| FATE™ | Deterministic Decision Policy Framework |
| TITAN CORE · Choice(t) ≥ 1 | Minimum-Viable-Option Safeguard (fail-safe invariant) |
| DriftZero Waterline | Model Drift Monitoring & Threshold Control |
| Stop-the-Line · SYSTEM_PAUSE | Automated Safe-Stop / Kill-Switch |
| bodhipakkhiya_engine | Pre-Execution Policy Gate |
| canon_gate · validate_output | Output Validation Layer |
| Pure Axis · COSMIC LATTE CANON | Governance Principles Charter |
| VEGA Kernel | Conservative (risk-averse) Decision Mode |
| LYLA Kernel | Adaptive (throughput) Decision Mode |
| GALAXY Decision Trace | Decision Audit Trail / Explainability View |
| knowledge_pack_facts · hotlines | Verified Fact Registry |
| _specific_first · _person_first | Life-first Response Precedence |
| ตอบจากสมการ | Deterministic Crisis Response Path |

## ข้อควรระวัง

เอกสารนี้เป็นแผนที่อ้างอิงช่วยขายงาน ไม่ใช่คำรับรอง compliance และไม่ใช่คำปรึกษาทางกฎหมาย เลข clause ISO ควรตรวจกับตัวมาตรฐานจริง และร่าง พ.ร.บ. AI ไทยอาจเปลี่ยนก่อนประกาศใช้
