"""ทะเบียนเบอร์ช่วยเหลือ — แหล่งความจริงแหล่งเดียวของทุกเบอร์ที่ระบบบอกผู้ใช้

เจ้าของโปรเจกต์: "อยากให้มีเบอร์ครบเลยทั้งโลก แต่พี่ก็ไม่มั่นใจว่าเบอร์ไหนจะใช้ได้ไม่ได้"
หลัก:
  · ใส่เฉพาะเบอร์ที่มั่นใจสูงว่าเป็นของหน่วยงานนั้นจริง · ไม่แน่ใจ = ไม่ใส่ (ชี้ไปหน่วยงาน/สมุดรายชื่อทางการแทน)
  · ทุกเบอร์มีแหล่งอ้างอิง (เว็บทางการของหน่วยงาน) ให้คนตรวจซ้ำได้
  · verified = มีคนโทรทดสอบ/ตรวจกับเว็บทางการแล้วจริง · ตอนนี้ทุกเบอร์เป็น False จนกว่าเจ้าของโปรเจกต์จะยืนยัน
    (รวบรวมจากความรู้ของ Claude — ตรงกับที่ใช้ในระบบมาตลอด แต่ยังไม่ได้โทรทดสอบ)
  · tests/test_hotlines.py: เบอร์ใดก็ตามที่อยู่ในคำตอบ (โทร…/call…) ต้องอยู่ในทะเบียนนี้ — พิมพ์ผิดหรือเดาเบอร์ เทสต์ล้ม
  · scripts/hotline_review.py พิมพ์รายการให้ตรวจ เรียงตามที่ยังไม่ได้ยืนยัน
"""
from __future__ import annotations

from typing import NamedTuple


class Line(NamedTuple):
    number: str
    th: str
    en: str
    kind: str          # emergency · mental · social · poison · child · scam · consumer · health · labor · utility · legal · info
    source: str        # เว็บทางการของหน่วยงาน
    verified: bool = False


REVIEWED = "2026-11"

REGISTRY: dict[str, list[Line]] = {
    "TH": [
        Line("191", "ตำรวจ เหตุด่วนเหตุร้าย", "Police emergency", "emergency", "royalthaipolice.go.th"),
        Line("1669", "เจ็บป่วยฉุกเฉิน (สพฉ.)", "Medical emergency", "emergency", "niems.go.th"),
        Line("199", "ดับเพลิง", "Fire", "emergency", "disaster.go.th"),
        Line("1784", "ปภ. สายด่วนนิรภัย", "Disaster prevention & mitigation", "emergency", "disaster.go.th"),
        Line("1155", "ตำรวจท่องเที่ยว (พูดอังกฤษได้)", "Tourist police (English)", "emergency", "tourist.police.go.th"),
        Line("1323", "สุขภาพจิต 24 ชม. (กรมสุขภาพจิต)", "Mental health, 24h", "mental", "dmh.go.th"),
        Line("1300", "ศูนย์ช่วยเหลือสังคม พม. 24 ชม.", "Social assistance, 24h", "social", "m-society.go.th"),
        Line("1479", "สายด่วนคนพิการ", "Disability helpline", "social", "dep.go.th"),
        Line("1387", "สายด่วนเด็ก (Childline)", "Childline", "child", "childlinethailand.org"),
        Line("1367", "ศูนย์พิษวิทยา รพ.รามาธิบดี 24 ชม.", "Poison centre, 24h", "poison", "ramathibodi.mahidol.ac.th"),
        Line("1441", "ศูนย์แก้ไขปัญหาอาชญากรรมออนไลน์ (AOC)", "Online crime / scam centre", "scam", "thaipoliceonline.go.th"),
        Line("1207", "ก.ล.ต. ตรวจผู้ได้รับอนุญาต", "Securities & Exchange Commission", "scam", "sec.or.th"),
        Line("1166", "สคบ. คุ้มครองผู้บริโภค", "Consumer protection", "consumer", "ocpb.go.th"),
        Line("1330", "สปสช. สิทธิบัตรทอง", "Universal health coverage", "health", "nhso.go.th"),
        Line("1422", "กรมควบคุมโรค", "Disease control", "health", "ddc.moph.go.th"),
        Line("1413", "สายด่วนเลิกเหล้า", "Alcohol helpline", "health", "1413.in.th"),
        Line("1165", "สายด่วนยาเสพติด", "Drug helpline", "health", "pmnidat.go.th"),
        Line("1600", "สายด่วนเลิกบุหรี่", "Quit smoking", "health", "thailandquitline.or.th"),
        Line("1663", "ปรึกษาท้องไม่พร้อมและเอดส์", "Unplanned pregnancy & HIV", "health", "1663.or.th"),
        Line("1506", "ประกันสังคม", "Social security", "labor", "sso.go.th"),
        Line("1546", "กรมสวัสดิการและคุ้มครองแรงงาน", "Labour protection", "labor", "labour.go.th"),
        Line("1694", "กรมการจัดหางาน", "Employment department", "labor", "doe.go.th"),
        Line("1167", "สภาทนายความ (ปรึกษาฟรี)", "Lawyers Council (free advice)", "legal", "lawyerscouncil.or.th"),
        Line("1599", "ร้องเรียนตำรวจ", "Police complaints", "legal", "royalthaipolice.go.th"),
        Line("1567", "ศูนย์ดำรงธรรม", "Damrongdhama complaints centre", "legal", "damrongdhama.moi.go.th"),
        Line("1205", "ป.ป.ช.", "National Anti-Corruption Commission", "legal", "nacc.go.th"),
        Line("1584", "กรมการขนส่งทางบก", "Land Transport Department", "info", "dlt.go.th"),
        Line("1586", "กรมทางหลวง", "Highways Department", "info", "doh.go.th"),
        Line("1362", "กรมอุทยานแห่งชาติฯ (สัตว์ป่า)", "National parks / wildlife", "info", "dnp.go.th"),
        # หนี้ — ปรึกษาฟรี ไม่ต้องจ่ายใครให้ "ช่วยแก้หนี้"
        Line("1213", "ศูนย์คุ้มครองผู้ใช้บริการทางการเงิน (ธปท.)", "Bank of Thailand financial consumer protection", "debt", "bot.or.th"),
        Line("1443", "สายด่วนชนะหนี้ · คลินิกแก้หนี้ (บสส./SAM)", "Debt Clinic hotline (SAM)", "debt", "debtclinicbysam.com"),
        # น้ำ ไฟ — ขอผ่อนผันก่อนวันตัด
        Line("1130", "การไฟฟ้านครหลวง (กทม. นนทบุรี สมุทรปราการ)", "Metropolitan Electricity Authority", "utility", "mea.or.th"),
        Line("1129", "การไฟฟ้าส่วนภูมิภาค (ต่างจังหวัด)", "Provincial Electricity Authority", "utility", "pea.co.th"),
        Line("1125", "การประปานครหลวง (กทม. นนทบุรี สมุทรปราการ)", "Metropolitan Waterworks Authority", "utility", "mwa.co.th"),
        Line("1662", "การประปาส่วนภูมิภาค (ต่างจังหวัด)", "Provincial Waterworks Authority", "utility", "pwa.co.th"),
    ],
    "US": [Line("911", "ฉุกเฉิน", "Emergency", "emergency", "911.gov"),
           Line("988", "วิกฤตทางใจ (โทร/ส่งข้อความ)", "Suicide & Crisis Lifeline (call/text)", "mental", "988lifeline.org"),
           Line("211", "บริการสังคม อาหาร ที่พัก ค่าน้ำไฟ", "Food, housing, utility help", "social", "211.org"),
           Line("1-800-222-1222", "ศูนย์พิษวิทยา", "Poison Control", "poison", "poisonhelp.hrsa.gov"),
           # ใช้ในคำตอบอังกฤษของ core/knowledge_pack.py
           Line("1-800-799-7233", "สายด่วนความรุนแรงในครอบครัว", "National Domestic Violence Hotline", "social", "thehotline.org"),
           Line("1-800-656-4673", "RAINN ผู้ถูกล่วงละเมิดทางเพศ", "RAINN sexual assault hotline", "social", "rainn.org"),
           Line("1-800-422-4453", "Childhelp แจ้ง/ปรึกษาเรื่องเด็กถูกทำร้าย", "Childhelp child abuse hotline", "child", "childhelp.org"),
           Line("1-800-843-5678", "NCMEC CyberTipline เด็กถูกแสวงประโยชน์ทางเพศ", "NCMEC CyberTipline", "child", "missingkids.org"),
           Line("1-800-662-4357", "SAMHSA สารเสพติด/สุขภาพจิต", "SAMHSA National Helpline", "health", "samhsa.gov"),
           Line("1-800-GAMBLER", "ติดพนัน", "Problem gambling helpline", "health", "ncpgambling.org"),
           Line("1-800-QUIT-NOW", "เลิกบุหรี่", "Quitline", "health", "cdc.gov"),
           Line("88709", "ส่งข้อความ DITCHVAPE เลิกบุหรี่ไฟฟ้า", "Text DITCHVAPE (quit vaping)", "health", "truthinitiative.org"),
           Line("1-866-488-7386", "Trevor Project เยาวชน LGBTQ+", "The Trevor Project", "mental", "thetrevorproject.org"),
           Line("678-678", "Trevor Project (ส่งข้อความ START)", "The Trevor Project (text START)", "mental", "thetrevorproject.org"),
           Line("7726", "ส่งต่อ SMS หลอกลวง", "Forward spam texts", "scam", "fcc.gov")],
    "CA": [Line("911", "ฉุกเฉิน", "Emergency", "emergency", "canada.ca"),
           Line("988", "วิกฤตทางใจ", "Suicide Crisis Helpline", "mental", "988.ca"),
           Line("211", "บริการสังคม", "Community & social services", "social", "211.ca")],
    "UK": [Line("999", "ฉุกเฉิน", "Emergency", "emergency", "gov.uk"),
           Line("111", "NHS ไม่ฉุกเฉิน", "NHS non-emergency", "health", "nhs.uk"),
           Line("116 123", "Samaritans 24 ชม.", "Samaritans, 24h", "mental", "samaritans.org"),
           # ใช้ในคำตอบอังกฤษของ core/knowledge_pack.py
           Line("0808 2000 247", "สายด่วนความรุนแรงในครอบครัว (Refuge)", "National Domestic Abuse Helpline", "social", "nationaldahelpline.org.uk"),
           Line("0808 800 5000", "NSPCC เป็นห่วงเด็ก", "NSPCC helpline", "child", "nspcc.org.uk"),
           Line("0808 801 0331", "NAPAC ผู้ใหญ่ที่เคยถูกทำร้ายตอนเด็ก", "NAPAC (adult survivors)", "social", "napac.org.uk"),
           Line("0300 123 6600", "FRANK สารเสพติด", "FRANK drugs helpline", "health", "talktofrank.com"),
           Line("0300 123 1110", "Drinkline แอลกอฮอล์", "Drinkline", "health", "nhs.uk"),
           Line("0808 8020 133", "GamCare ติดพนัน", "National Gambling Helpline (GamCare)", "health", "gamcare.org.uk"),
           Line("7726", "ส่งต่อ SMS หลอกลวง", "Forward spam texts", "scam", "ncsc.gov.uk")],
    "EU": [Line("112", "ฉุกเฉิน (ทั่วยุโรป)", "Emergency (EU-wide)", "emergency", "europa.eu")],
    "AU": [Line("000", "ฉุกเฉิน", "Emergency", "emergency", "triplezero.gov.au"),
           Line("13 11 14", "Lifeline", "Lifeline", "mental", "lifeline.org.au")],
    "JP": [Line("110", "ตำรวจ", "Police", "emergency", "npa.go.jp"), Line("119", "ดับเพลิง/รถพยาบาล", "Fire / ambulance", "emergency", "fdma.go.jp")],
    "KR": [Line("112", "ตำรวจ", "Police", "emergency", "police.go.kr"), Line("119", "ดับเพลิง/รถพยาบาล", "Fire / ambulance", "emergency", "nfa.go.kr"),
           Line("109", "ป้องกันการฆ่าตัวตาย 24 ชม.", "Suicide prevention, 24h", "mental", "mohw.go.kr")],
    "CN": [Line("110", "ตำรวจ", "Police", "emergency", "mps.gov.cn"), Line("120", "รถพยาบาล", "Ambulance", "emergency", "nhc.gov.cn"),
           Line("119", "ดับเพลิง", "Fire", "emergency", "119.gov.cn")],
}

# สมุดรายชื่อทางการ — ใช้เมื่อไม่มีเบอร์ของประเทศนั้นในทะเบียน (ดีกว่าเดาเบอร์)
DIRECTORIES = [
    ("findahelpline.com", "สายด่วนสุขภาพใจฟรีกว่า 130 ประเทศ", "Free emotional-support helplines in 130+ countries"),
    ("211.org", "สหรัฐฯ: อาหาร ที่พัก ค่าน้ำไฟ", "US: food, housing and utility help"),
]


def all_numbers() -> set[str]:
    return {ln.number for lines in REGISTRY.values() for ln in lines}


def get(country: str, kind: str) -> list[Line]:
    return [ln for ln in REGISTRY.get(country, []) if ln.kind == kind]


def th(number: str) -> Line:
    return next(ln for ln in REGISTRY["TH"] if ln.number == number)
