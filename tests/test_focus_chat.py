"""หน้าแชทว่างต้องโล่ง — แผงสูตรด้านขวาโผล่เฉพาะเมื่อมีคำตอบให้อธิบายแล้ว

เจ้าของโปรเจกต์: "สูตรข้างๆ เราควรซ่อนไว้ไหม แบบคนจะได้มีสมาธิพิมพ์"
เดิมแผงสูตร (W · E, R · Risk · C · P) ขึ้นเต็มขวาตั้งแต่ยังไม่ได้คุยสักคำ
"""
from pathlib import Path

SRC = (Path(__file__).resolve().parent.parent / "static" / "index.html").read_text(encoding="utf-8")


def test_app_starts_without_trace_panel():
    assert '<div id="app">' in SRC and '<div id="app" class="has-trace">' not in SRC


def test_trace_panel_follows_answers():
    body = SRC[SRC.index("function syncTrace(v){"):]
    body = body[:body.index("\n}")]
    assert "x.tr" in body and "v === 'chat' && has" in body
    assert "syncTrace(v);" in SRC                      # เปลี่ยนหน้าแล้วตัดสินใหม่
    paint = SRC[SRC.index("function paintEq(){"):]
    assert "syncTrace();" in paint[:paint.index("\n}")]  # ได้คำตอบแรกแล้วแผงขึ้นเอง
