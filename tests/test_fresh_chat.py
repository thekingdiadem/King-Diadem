"""แชทใหม่ต้องเริ่มใหม่ — หน้าจอจริงของพี่คิง: เล่าเรื่องหนี้บัตร 50,000 ในแชทหนึ่ง ลบแชทนั้นทิ้ง เปิดแชทใหม่พิมพ์ "สวัสดี"
แต่ได้ VEGA · COLLAPSE ตอบสรุปเรื่องหนี้และที่พัก (ความจำแนบข้อความดิบจากแชทอื่น + สถานะที่บันทึกไว้ยกโหมดเป็น collapse)
· หน้าแชทโล่งแบบแอปทั่วไป: ใต้ช่องพิมพ์เหลือบรรทัดเดียว รายละเอียดอยู่หน้า /privacy#ai"""
from pathlib import Path

from core.intent import is_bare_greeting
from tests._front import front_page

ROOT = Path(__file__).resolve().parent.parent


def test_bare_greetings_are_recognized_but_not_greeting_plus_story():
    for t in ("สวัสดี", "สวัสดีค่ะ", "หวัดดีจ้า 👋", "hi there", "good morning lyla"):
        assert is_bare_greeting(t), t
    for t in ("สวัสดี อยากตาย", "สวัสดีครับ มีเรื่องจะถาม", "hi I lost my job"):
        assert not is_bare_greeting(t), t


def test_memory_never_sends_raw_text_from_other_chats():
    src = (ROOT / "DATABASE" / "db.py").read_text(encoding="utf-8")
    fn = src[src.index("def build_memory_context"):src.index("def auto_extract_memory")]
    assert "[บทสนทนาล่าสุด]" not in fn and "r['input']" not in fn
    assert "ห้ามเปิดเรื่องจากความจำเอง" in fn


def test_greeting_skips_memory_and_collapse():
    llm = (ROOT / "core" / "llm_gemini.py").read_text(encoding="utf-8")
    assert "if user_email and not greet_only else" in llm and "[ผู้ใช้แค่ทักทาย:" in llm
    app = (ROOT / "app.py").read_text(encoding="utf-8")
    assert 'route not in ("vega",) and not _bare(user_input):' in app


def test_chat_footer_is_one_quiet_line():
    page = front_page()
    i = page.index('id="ai-note"'); note = page[i:page.index("</p>", i)]
    assert "เป็นระบบ AI ไม่ใช่คน" in note and 'href="/privacy#ai"' in note and "Gemini" not in note
    priv = (ROOT / "static" / "privacy.html").read_text(encoding="utf-8")
    assert '<h2 id="ai">' in priv and "ตอบจากสมการของระบบ" in priv and "Gemini" in priv
