"""หน้าผลงาน (portfolio.html) ต้องตรงกับระบบจริง — คนจ้างงาน/สัมภาษณ์เปิดโค้ดเทียบได้
เดิมเขียนว่าใช้ Flask · Anthropic API · JWT · WebSocket และอ้าง server.py / AUTH/gateway.py ซึ่งไม่ตรงกับโค้ด"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PF = (ROOT / "portfolio.html").read_text(encoding="utf-8")
REQ = (ROOT / "requirements.txt").read_text(encoding="utf-8")


def test_stack_matches_requirements():
    assert "fastapi" in REQ and "flask" not in REQ.lower()
    assert ">FastAPI<" in PF and ">Flask<" not in PF
    assert "google-genai" in REQ and ">Google Gemini<" in PF
    assert ">JWT<" not in PF and "JWT" not in PF and "WebSocket" not in PF
    assert "authlib" in REQ and ">Google OAuth<" in PF


def test_skills_from_elsewhere_are_labelled_as_skills_not_this_stack():
    """Anthropic API / MCP เป็นทักษะที่พี่ใช้ที่อื่น — อยู่ในบรรทัดทักษะ ไม่ใช่ "Built With" ของระบบนี้"""
    stack = PF[PF.index('<div class="stk">'):PF.index('<p class="also">')]
    assert "Anthropic" not in stack and "MCP" not in stack
    assert "Anthropic API (Claude)" in PF and "MCP Protocol" in PF


def test_every_file_named_on_the_portfolio_exists_and_is_live():
    import json
    rows = {r[0]: r for r in json.loads((ROOT / "static" / "system_map.json").read_text(encoding="utf-8"))["files"]}
    named = set(re.findall(r'<span class="mod">([^<]+)</span>', PF))
    named |= {f.strip() for line in re.findall(r'<div class="anode-f">([^<]+)</div>', PF)
              for f in re.split(r"·|→", line) if f.strip().endswith(".py") or f.strip().endswith(".html")}
    assert len(named) >= 12
    for f in named:
        assert (ROOT / f).exists(), f
        assert rows[f][2] in ("boot", "request", "web"), (f, rows[f][2])
    assert "server.py" not in PF


def test_links_point_to_the_real_repo_and_profile():
    assert "varjayd01" not in PF
    assert PF.count("https://github.com/thekingdiadem/King-Diadem") >= 3
    assert 'href="https://fastwork.co/byob/CtqOnVfzC7"' in PF          # ลิงก์จริงจากพี่ (เดิมพาไปหน้าแรกของ Fastwork)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "fastwork.co/user/" not in PF + readme and readme.count("https://fastwork.co/byob/CtqOnVfzC7") == 3


def test_unused_files_moved_out_of_live_folders():
    for f in ("AUTH/gateway.py", "PAYMENT/stripe_payment.py", "NETWORK/global_chat.py", "AI_KERNEL/reality_constraint.py",
              "WORLD_MODEL/human_state.py", "SECURITY/emergency_mode.py"):
        assert not (ROOT / f).exists(), f
    assert not (ROOT / "legacy").exists()          # โฟลเดอร์โค้ดที่ไม่ได้ใช้ ลบแล้ว (พี่อนุญาต)


def test_thai_text_has_a_looped_font():
    assert "Noto+Sans+Thai+Looped" in PF and "'DM Sans','Noto Sans Thai Looped'" in PF


def test_code_block_keeps_its_lines():
    """กล่อง FATE™ Core Law เคยแสดงทุกบรรทัดต่อกันเป็นก้อนเดียว (ไม่มี white-space:pre)"""
    css = PF[PF.index(".code{"):PF.index("}", PF.index(".code{"))]
    assert "white-space:pre-wrap" in css
