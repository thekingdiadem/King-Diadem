"""SEO หลายภาษา — ให้คนทั่วโลกค้นเจอ

เดิมหน้าแรกมีชื่อเรื่องและคำอธิบายเป็นภาษาไทยอย่างเดียว ภาษาอื่นแปลด้วย JavaScript หลังโหลดหน้า
เครื่องมือค้นหา (Google · Bing · Naver · Yandex · Baidu) จึงเห็นแต่หน้าไทยหน้าเดียว คนที่ค้นเป็นภาษาของตัวเองหาไม่เจอ

ตอนนี้แต่ละภาษามีลิงก์ของตัวเอง (`/?lang=en` …) ที่เซิร์ฟเวอร์ใส่ชื่อเรื่อง คำอธิบาย ภาษาของหน้า
และ hreflang บอกว่ามีหน้าภาษาไหนบ้าง — static/i18n.js เปิดหน้าเป็นภาษานั้นทันทีเมื่อมี ?lang=
"""
import html
import re

# ภาษาที่หน้าเว็บแปลได้ครบ (static/i18n.js: en ja + ชุดเสริม zh ko es vi)
# เน้นระบบและคำสอน: ไม่มีเรื่องส่วนตัว ไม่เปรียบเทียบกับใคร — บอกว่าระบบนี้ทำงานอย่างไร
META = {
    "th": ("KING DIADEM — ระบบช่วยตัดสินใจที่ทุกคำตอบต้องเหลือทางเลือก",
           "ระบบตัดสินใจที่ตรวจสอบได้ ทำงานด้วยสมการ ไม่ใช่การเดา: ทุกคำตอบต้องเหลือทางให้ไปต่ออย่างน้อยหนึ่งทาง (O ≥ 1) · DriftZero ตรวจแผนก่อนลงมือ · มองปัญหาผ่านอริยสัจ 4 และสภา 6 เสียง · LYLA ฟังและตอบด้วยใจ · ฟรี ไม่ต้องสมัคร", "th_TH"),
    "en": ("KING DIADEM — A decision system where every answer leaves you a way forward",
           "A verifiable decision kernel that works by equations, not guesses: every answer must leave at least one way forward (O ≥ 1) · DriftZero checks a plan before you act · problems seen through the Four Noble Truths and a council of six voices · LYLA listens and answers with care · Free, no sign-up.", "en_US"),
    "ja": ("KING DIADEM — どの答えにも必ず進む道が残る意思決定システム",
           "推測ではなく数式で動く、検証できる意思決定カーネル。すべての答えに少なくとも一つの道を残す（O ≥ 1）· DriftZeroが行動前に計画を点検 · 四諦と六つの声の評議会で問題を見つめる · LYLAが耳を傾け心で答える · 無料・登録不要。", "ja_JP"),
    "zh": ("KING DIADEM — 每个答案都为你留下一条出路的决策系统",
           "可验证的决策内核，以方程运作而非猜测：每个答案至少留下一条可走的路（O ≥ 1）· DriftZero 在行动前检查计划 · 以四圣谛和六声议会看待问题 · LYLA 倾听并用心回应 · 免费，无需注册。", "zh_CN"),
    "ko": ("KING DIADEM — 모든 답에 나아갈 길이 남는 의사결정 시스템",
           "추측이 아닌 방정식으로 작동하는 검증 가능한 의사결정 커널: 모든 답은 적어도 하나의 길을 남깁니다(O ≥ 1) · DriftZero가 행동 전에 계획을 점검 · 사성제와 여섯 목소리의 회의로 문제를 바라봄 · LYLA가 귀 기울이고 마음으로 답함 · 무료, 가입 불필요.", "ko_KR"),
    "es": ("KING DIADEM — Un sistema de decisión donde cada respuesta deja un camino",
           "Un núcleo de decisión verificable que funciona con ecuaciones, no con suposiciones: cada respuesta deja al menos un camino (O ≥ 1) · DriftZero revisa el plan antes de actuar · los problemas se miran a través de las Cuatro Nobles Verdades y un consejo de seis voces · LYLA escucha y responde con cuidado · Gratis, sin registro.", "es_ES"),
    "vi": ("KING DIADEM — Hệ thống ra quyết định mà câu trả lời nào cũng để lại lối đi",
           "Lõi ra quyết định có thể kiểm chứng, vận hành bằng phương trình chứ không phỏng đoán: mỗi câu trả lời đều để lại ít nhất một lối đi (O ≥ 1) · DriftZero kiểm tra kế hoạch trước khi hành động · nhìn vấn đề qua Tứ Diệu Đế và hội đồng sáu tiếng nói · LYLA lắng nghe và trả lời bằng sự quan tâm · Miễn phí, không cần đăng ký.", "vi_VN"),
}
LANGS = list(META)


def lang_of(request_lang) -> str:
    lg = str(request_lang or "").lower().split("-")[0]
    return lg if lg in META else "th"


def _url(base: str, lg: str) -> str:
    return base + "/" + ("" if lg == "th" else f"?lang={lg}")


def head_for(page: str, lg: str, base: str) -> str:
    """แก้ส่วนหัวของ static/index.html ให้เป็นภาษา lg และใส่ hreflang ทุกภาษา"""
    title, desc, locale = (html.escape(x, quote=True) for x in META[lg])
    url = _url(base, lg)
    out = page.replace('<html lang="th">', f'<html lang="{lg}">', 1)
    out = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", out, count=1)
    for prop, val in (("og:title", title), ("twitter:title", title)):
        out = re.sub(rf'(<meta (?:property|name)="{prop}" content=")[^"]*(">)', rf"\g<1>{val}\g<2>", out, count=1)
    for prop in ("description", "og:description", "twitter:description"):
        out = re.sub(rf'(<meta (?:property|name)="{prop}" content=")[^"]*(">)', lambda m: m.group(1) + desc + m.group(2), out, count=1)
    out = re.sub(r'(<meta property="og:url" content=")[^"]*(">)', rf"\g<1>{url}\g<2>", out, count=1)
    out = re.sub(r'(<link rel="canonical" href=")[^"]*(">)', rf"\g<1>{url}\g<2>", out, count=1)
    alts = "\n".join(f'<link rel="alternate" hreflang="{x}" href="{_url(base, x)}">' for x in LANGS)
    alts += f'\n<link rel="alternate" hreflang="x-default" href="{_url(base, "en")}">'
    alts += "".join(f'\n<meta property="og:locale:alternate" content="{META[x][2]}">' for x in LANGS if x != lg)
    out = re.sub(r'(<meta property="og:locale" content=")[^"]*(">)', rf"\g<1>{locale}\g<2>\n{alts}", out, count=1)
    return out


def sitemap_home(base: str) -> str:
    """รายการหน้าแรกทุกภาษาใน sitemap พร้อม xhtml:link บอกว่าเป็นหน้าเดียวกันคนละภาษา"""
    links = "".join(f'<xhtml:link rel="alternate" hreflang="{x}" href="{html.escape(_url(base, x))}"/>' for x in LANGS)
    links += f'<xhtml:link rel="alternate" hreflang="x-default" href="{html.escape(_url(base, "en"))}"/>'
    return "".join(f"<url><loc>{html.escape(_url(base, x))}</loc>{links}<changefreq>daily</changefreq><priority>1.0</priority></url>" for x in LANGS)
