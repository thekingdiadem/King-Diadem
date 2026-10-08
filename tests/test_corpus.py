"""ชุดข้อความทดสอบกลาง (tests/corpus/messages.tsv) — ทุกข้อที่ไม่ได้ติด ?known ต้องผ่าน

ดูคะแนนรายหมวด: python scripts/eval_corpus.py
"""
import pytest

from scripts.eval_corpus import evaluate, load

ROWS = load()


def test_corpus_is_big_enough():
    assert len(ROWS) >= 300


@pytest.mark.parametrize("row", [r for r in ROWS if not r["known"]], ids=lambda r: f"L{r['line']}")
def test_corpus_row(row):
    res = evaluate([row])[0]
    assert res["ok"], f"{row['text']!r} พลาด {res['failed']} · ได้ {res['got']}"
