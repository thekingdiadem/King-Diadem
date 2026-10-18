"""
scripts/build_system_map.py — สร้างแผนผังระบบ (#system-map ใน static/index.html) ใหม่จาก repo จริง

แผนผังเดิมเขียนมือ เลยค้างอยู่ที่ commit เก่า: ไฟล์ที่ต่อเข้าระบบแล้วยังขึ้นว่า "วิสัยทัศน์" และไฟล์ใหม่ไม่อยู่ในแผนผัง
สคริปต์นี้เก็บคำอธิบายเดิมไว้ทั้งหมด แล้วคำนวณสิ่งที่วัดได้ใหม่ทุกครั้ง:
  · จำนวนบรรทัด · ไฟล์ที่ย้ายไป legacy/ · ไฟล์ Python ที่ app.py เรียกถึงจริง (boot = โหลดตอนเปิดเซิร์ฟเวอร์, request = โหลดตอนมีข้อความ)
  · เส้นเชื่อม (edges) จากการ import จริง — หน้าจักรวาลใช้วาดเส้นระหว่างชิ้นส่วน

รัน:  SECRET_KEY=x python scripts/build_system_map.py           → เขียนลง static/index.html
      SECRET_KEY=x python scripts/build_system_map.py --check   → ไม่เขียน แค่บอกว่าแผนผังตรงกับ repo ไหม (exit 1 ถ้าไม่ตรง)
"""
from __future__ import annotations

import ast
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, "static", "index.html")
# ข้อมูลชุดเดียวกันเป็นไฟล์แยก ให้หน้า /architecture โหลดไปวาดแผนที่ไฟล์ทั้งหมด
JSON_OUT = os.path.join(ROOT, "static", "system_map.json")
_MAP_RE = re.compile(r'(<script type="application/json" id="system-map">)(.*?)(</script>)', re.S)

# คำอธิบายของไฟล์ที่ยังไม่เคยอยู่ในแผนผัง: [หมวด, คำอธิบาย, ป้าย]
NEW = {
    "index.html": ["site", "แกลเลอรีจักรวาล — กางงานภาพทุกชิ้นใน static/ ให้ดูและกดเล่นได้ (หน้าแรกของ GitHub Pages)", "✦ แกลเลอรี"],
    "CANON_TH.md": ["docs", "ธรรมนูญ SYSTEM CANON ฉบับภาษาไทยตัวเต็มของผู้ก่อตั้ง (มาตรา 0–15)", "🜂 canon ไทย"],
    "legacy/README.md": ["docs", "อธิบายโฟลเดอร์ legacy/ — โค้ดที่ยังไม่มีใครเรียกใช้ และวิธีย้ายกลับ", "▤ legacy"],
    "scripts/__init__.py": ["pkg", "ทำให้ scripts เป็น package (เทสต์ import สคริปต์ได้)", "□ scripts"],
    "scripts/eval_corpus.py": ["tests", "ให้คะแนนตัวตรวจจับด้วยชุดข้อความทดสอบกลาง", "✓ corpus"],
    "scripts/stress_test.py": ["tests", "ทดสอบหนัก: ดัดแปลงข้อความเป็นแสน ตรวจไม่ล้ม · ไม่เกิน 3 ทาง · คงเส้นคงวา", "⚡ stress"],
    "scripts/build_system_map.py": ["config", "สร้างแผนผังระบบในหน้าเว็บใหม่จาก repo จริง", "⌘ แผนผัง"],
    "static/i18n.js": ["web", "ข้อความหน้าเว็บหลายภาษา", "文 i18n"],
    "core/vega_kernels.py": ["request", "VEGA Human DriftZero Kernel 14 ประตู (K1–K14): อ่านสัญญาณจากข้อความ แล้วให้ VEGA ถามคำถามของประตูที่ติด", "◆ 14 gates"],
    "core/history_export.py": ["request", "ส่งออกประวัติการปรึกษาของบัญชี: ไฟล์ข้อความ (ดาวน์โหลด) และส่งเข้าอีเมลของบัญชีนั้นผ่าน SMTP", "✉ history"],
    "static/system_map.json": ["web", "ข้อมูลแผนผังระบบ (ไฟล์ · หมวด · เส้นเชื่อม) ที่หน้า /architecture โหลดไปวาด — สร้างจาก scripts/build_system_map.py", "⌘ map.json"],
    "static/earth/README.md": ["docs", "ที่มาและสัญญาอนุญาตของภาพโลกหน้าแรก (NASA · สาธารณสมบัติ)", "🜨 earth"],
    "static/earth/day.jpg": ["web", "ภาพโลกกลางวัน NASA Blue Marble 2048×1024 — ประเทศตรงตำแหน่งจริง", "🜨 day"],
    "static/earth/lights.jpg": ["web", "ไฟเมืองกลางคืน NASA Earth at Night — สกัดเฉพาะแสงเมือง", "✺ lights"],
    "static/earth/clouds.jpg": ["web", "เมฆทั้งโลก 2048×1024 — ลอยช้ากว่าพื้นโลกเล็กน้อย", "☁ clouds"],
    "tests/corpus/messages.tsv": ["tests", "ชุดข้อความทดสอบกลาง — ข้อความจริงพร้อมสิ่งที่ระบบควรตอบ", "☰ corpus"],
}
_LIVE_FROM = ("vision", "legacy", "dormant", "broken")


def tracked() -> list[str]:
    out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True).split("\n")
    return [f for f in out if f and "__pycache__" not in f]


def line_count(path: str) -> int:
    try:
        with open(os.path.join(ROOT, path), "rb") as f:
            return f.read().count(b"\n")
    except OSError:
        return 0


def module_map(files: list[str]) -> dict[str, str]:
    m = {}
    for f in files:
        if f.endswith(".py") and not f.startswith("legacy/"):
            name = f[:-3].replace("/", ".")
            m[name[:-9] if name.endswith(".__init__") else name] = f
    return m


def imports_of(path: str, mods: dict[str, str]) -> set[str]:
    """ไฟล์ใน repo ที่ path import ถึง — รวมการโหลดด้วยชื่อ (importlib / _try_import("ENGINE.x", ...))"""
    try:
        tree = ast.parse(open(os.path.join(ROOT, path), encoding="utf-8").read())
    except (OSError, SyntaxError):
        return set()
    pkg = path[:-3].replace("/", ".").rsplit(".", 1)[0] if "/" in path else ""
    names = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            names.update(a.name for a in n.names)
        elif isinstance(n, ast.ImportFrom):
            base = n.module or ""
            if n.level:
                parts = pkg.split(".") if pkg else []
                base = ".".join(parts[:len(parts) - (n.level - 1)] + ([base] if base else []))
            names.add(base)
            names.update(base + "." + a.name for a in n.names)
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value in mods:
            names.add(n.value)
    hit = set()
    for name in names:
        parts = name.split(".")
        for i in range(1, len(parts) + 1):
            k = ".".join(parts[:i])
            if k in mods and mods[k] != path:
                hit.add(mods[k])
    return hit


def reachable(start: str, mods: dict[str, str]) -> tuple[set[str], list[tuple[str, str]]]:
    seen, edges, stack = set(), [], [start]
    while stack:
        f = stack.pop()
        if f in seen:
            continue
        seen.add(f)
        for g in sorted(imports_of(f, mods)):
            edges.append((f, g))
            stack.append(g)
    return seen, edges


def boot_modules(mods: dict[str, str]) -> set[str]:
    """ไฟล์ที่ถูกโหลดทันทีตอน import app (เปิดเซิร์ฟเวอร์)"""
    code = ("import sys, json; sys.path.insert(0, %r); import app; "
            "print(json.dumps(sorted(m for m in sys.modules)))") % ROOT
    env = {**os.environ, "SECRET_KEY": os.environ.get("SECRET_KEY") or "x" * 40,
           "DB_PATH": os.environ.get("DB_PATH") or os.path.join("/tmp", "kd_map.db")}
    try:
        out = subprocess.check_output([sys.executable, "-c", code], cwd=ROOT, env=env, text=True,
                                      stderr=subprocess.DEVNULL)
        loaded = json.loads(out.strip().splitlines()[-1])
    except Exception:
        return set()
    return {mods[m] for m in loaded if m in mods}


def static_refs(files: list[str]) -> set[str]:
    """ชื่อไฟล์ที่หน้า HTML ใน static/ โหลดผ่าน <script src> / <link href> หรือตั้ง .src ด้วย JS"""
    refs = set()
    for f in files:
        if f.startswith("static/") and f.endswith(".html"):
            html = open(os.path.join(ROOT, f), encoding="utf-8").read()
            html = _MAP_RE.sub("", html)          # ไม่นับชื่อไฟล์ที่อยู่ในข้อมูลแผนผังเอง
            refs.update(os.path.basename(m) for m in re.findall(r'(?:src|href)="([^"#?]+\.(?:js|css))"', html))
            # โหลดด้วย JS: s.src = '/static/galaxy_scene.js' (หน้า The Universe โหลดฉากแบบนี้)
            refs.update(os.path.basename(m) for m in re.findall(r"\.(?:src|href)\s*=\s*['\"]([^'\"#?]+\.(?:js|css))['\"]", html))
    return refs


def gallery_refs() -> set[str]:
    """ไฟล์ใน static/ ที่หน้าแกลเลอรี index.html (ราก — GitHub Pages) โหลดผ่าน scripts: ['static/x.js'] ของแต่ละช่อง
    เดิมไม่นับ ไฟล์พวกนี้จึงขึ้นว่า "รุ่นเก่า ไม่มีหน้าไหนโหลด" ทั้งที่แกลเลอรีกดเล่นได้อยู่"""
    try:
        html = open(os.path.join(ROOT, "index.html"), encoding="utf-8").read()
    except OSError:
        return set()
    out = set()
    for block in re.findall(r"scripts:\s*\[([^\]]*)\]", html):
        out.update(re.findall(r"['\"](static/[\w./-]+\.(?:js|css))['\"]", block))
    return out


def asset_refs(files: list[str]) -> set[str]:
    """ไฟล์ใน static/ ที่หน้าเว็บ · CSS · manifest · app.py อ้างถึงด้วย path /static/... หรือ static/..."""
    text = ""
    for f in files:
        # ไม่อ่านไฟล์ .js — JS รุ่นเก่าที่ไม่มีใครโหลดอ้างถึงกันเอง จะทำให้ดูเหมือนถูกใช้งาน
        if f in ("app.py", "static/manifest.json") or (f.startswith("static/") and f.endswith((".html", ".css"))):
            try:
                src = open(os.path.join(ROOT, f), encoding="utf-8").read()
            except (OSError, UnicodeDecodeError):
                continue
            if f == "app.py":   # นับเฉพาะสตริงในโค้ด ไม่นับคอมเมนต์ที่เล่าถึงไฟล์เก่า
                src = "\n".join(n.value for n in ast.walk(ast.parse(src))
                                 if isinstance(n, ast.Constant) and isinstance(n.value, str))
            text += src + "\n"
    text = _MAP_RE.sub("", text)
    out = {"static/" + m for m in re.findall(r"/?static/([\w./-]+\.\w+)", text)}
    # ภาพโลกและข้อมูลเมือง (static/earth/) โหลดจาก JS ที่หน้าเว็บใช้จริง ด้วยชื่อที่ประกอบตอนรัน
    # ('earth/' + file, 'cities_t' + n + '.json') — เดิมขึ้นว่าเป็นไฟล์ตั้งค่า ทั้งที่หน้าโลกโหลดทุกครั้ง
    live_js = static_refs(files)
    for f in files:
        if f.startswith("static/") and f.endswith(".js") and os.path.basename(f) in live_js:
            src = open(os.path.join(ROOT, f), encoding="utf-8").read()
            if "earth/" in src:
                out |= {g for g in files if g.startswith("static/earth/") and not g.endswith(".md")}
    return out


def web_edges(files: list[str]) -> list[tuple[str, str]]:
    """เส้น "ส่งให้/โหลด" ฝั่งเว็บ: app.py → หน้า HTML ที่ส่งด้วย FileResponse · หน้า HTML → JS/CSS ที่หน้าโหลด"""
    static_by_name = {}
    for f in files:
        if f.startswith("static/") and f.endswith((".js", ".css")):
            static_by_name.setdefault(os.path.basename(f), f)
    out = []
    app_src = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
    pages = set(re.findall(r'"(static/[\w./-]+\.html)"', app_src))
    pages |= {"static/" + n for n in re.findall(r'"static",\s*"([\w.-]+\.html)"', app_src)}   # os.path.join(..., "static", "x.html")
    for page in sorted(pages):
        if page in files:
            out.append(("app.py", page))
    for f in files:
        if f.startswith("static/") and f.endswith(".html"):
            html = _MAP_RE.sub("", open(os.path.join(ROOT, f), encoding="utf-8").read())
            names = re.findall(r'(?:src|href)="([^"#?]+\.(?:js|css))"', html)
            names += re.findall(r"\.(?:src|href)\s*=\s*['\"]([^'\"#?]+\.(?:js|css))['\"]", html)
            for n in sorted(set(os.path.basename(x) for x in names)):
                if n in static_by_name:
                    out.append((f, static_by_name[n]))
    return out


def build(old: dict) -> dict:
    files = tracked()
    mods = module_map(files)
    live, edges = reachable("app.py", mods)
    boot = boot_modules(mods)
    prev = {row[0]: row for row in old.get("files", [])}
    web_refs = static_refs(files)
    g_refs = gallery_refs()
    a_refs = asset_refs(files)
    rows = []
    for f in files:
        if f in prev:
            row = list(prev[f])
        elif f.startswith("legacy/") and f[len("legacy/"):] in prev:
            row = list(prev[f[len("legacy/"):]])
            row[0], row[2], row[5] = f, "legacy", "note"
            row[6] = "ย้ายไป legacy/ — ไม่มีโค้ดส่วนไหนเรียกใช้"
            row[7] = "ย้ายกลับได้ด้วย git mv แล้วต่อเข้ากับ app.py"
        elif "legacy/" + f in prev:
            # ย้ายกลับจาก legacy/ แล้วต่อเข้าระบบ — เดิมไม่รู้จัก ไฟล์จึงตกไปหมวด "config" ทั้งที่ทำงานจริง
            row = list(prev["legacy/" + f])
            row[0], row[5] = f, "fixed"
            row[6] = "ย้ายกลับจาก legacy/"
            row[7] = ""
        elif f in NEW:
            cat, desc, label = NEW[f]
            row = [f, 0, cat, desc, label, "new", "", ""]
        elif f.startswith("tests/") and f.endswith(".py"):
            doc = ""
            try:
                doc = (ast.get_docstring(ast.parse(open(os.path.join(ROOT, f), encoding="utf-8").read())) or "").split("\n")[0]
            except (OSError, SyntaxError):
                pass
            row = [f, 0, "tests", doc or "เทสต์", "✓ " + os.path.basename(f)[5:-3][:18], "new", "", ""]
        else:
            row = [f, 0, "docs" if f.endswith(".md") else "config", "", "· " + os.path.basename(f)[:18], "new", "", ""]
        row[1] = line_count(f)
        # ไฟล์ที่ต่อเข้าระบบแล้ว แต่แผนผังเดิมยังบอกว่าเป็นวิสัยทัศน์/รุ่นเก่า
        if f.endswith(".py") and f in live and f != "app.py":
            cat = "boot" if f in boot else "request"
            if row[2] in _LIVE_FROM:
                row[6] = (row[6] + " · " if row[6] else "") + "ต่อเข้าระบบแล้ว"
            # ไฟล์ Python ใหม่ที่ต่อเข้าระบบแล้วเคยค้างหมวด "config" (ค่าเริ่มของไฟล์ใหม่) — ทำงานจริงก็ต้องขึ้นว่าทำงาน
            if row[2] in _LIVE_FROM or row[2] in ("boot", "request", "config"):
                row[2] = cat
        # JS/CSS ใน static/: หน้าเว็บโหลดจริง = web · ไม่มีหน้าไหนโหลด = legacy
        # (เดิม galaxy_scene.js ที่ index.html โหลดอยู่ ยังถูกจัดเป็นรุ่นเก่า)
        # ไฟล์ใหม่ใน static/ เดิมได้หมวด "config" ไปก่อนแล้วไม่ถูกจัดใหม่ — หน้าเว็บโหลดอยู่ก็ยังขึ้นว่าเป็นไฟล์ตั้งค่า
        # หน้า HTML ใหม่ใน static/ ก็เคยได้ "config" (เช่น notfound.html) — เป็นหน้าเว็บ
        if f.startswith("static/") and f.endswith(".html") and row[2] == "config":
            row[2] = "web"
        if f.startswith("static/") and f.endswith((".js", ".css")) and row[2] in ("web", "legacy", "config", "site"):
            row[2] = "web" if (os.path.basename(f) in web_refs or f in a_refs) else "site" if f in g_refs else "legacy"
            if row[2] == "site" and "ไม่มีหน้าไหนโหลด" in row[3]:
                row[3] = re.sub(r"\s*—\s*ไม่มีหน้าไหนโหลด\s*\(orphan\)", " — หน้าแกลเลอรี index.html (ราก) โหลด", row[3])
        # ภาพ/manifest/หน้า HTML ใน static/ ที่มีคนอ้างถึงจริง เคยค้างหมวด "config" (เช่น hero.jpg ที่ portal.css ใช้)
        elif f.startswith("static/") and row[2] == "config" and f in a_refs:
            row[2] = "web"
        rows.append(row)
    index = {r[0]: i for i, r in enumerate(rows)}
    edge_rows = {(index[a], index[b], 0) for a, b in edges if a in index and b in index}
    edge_rows |= {(index[a], index[b], 1) for a, b in web_edges(files) if a in index and b in index}   # 1 = ส่ง/โหลดฝั่งเว็บ
    edge_rows = sorted(edge_rows)
    commit = subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    return {"commit": commit, "files": rows, "edges": [list(e) for e in edge_rows]}


def main() -> int:
    html = open(INDEX, encoding="utf-8").read()
    m = _MAP_RE.search(html)
    if not m:
        print("ไม่พบ #system-map ใน static/index.html")
        return 1
    old = json.loads(m.group(2))
    new = build(old)
    if "--check" in sys.argv:
        same = [(r[0], r[2]) for r in old.get("files", [])] == [(r[0], r[2]) for r in new["files"]]
        try:
            side = json.load(open(JSON_OUT, encoding="utf-8"))
            same = same and [(r[0], r[2]) for r in side.get("files", [])] == [(r[0], r[2]) for r in new["files"]]
        except (OSError, ValueError):
            same = False
        print("แผนผังตรงกับ repo" if same else "แผนผังไม่ตรงกับ repo — รัน scripts/build_system_map.py")
        return 0 if same else 1
    payload = json.dumps(new, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = html[:m.start(2)] + payload + html[m.end(2):]
    with open(INDEX, "w", encoding="utf-8") as f:
        f.write(html)
    with open(JSON_OUT, "w", encoding="utf-8") as f:
        f.write(json.dumps(new, ensure_ascii=False, separators=(",", ":")))
    live = sum(1 for r in new["files"] if r[2] in ("boot", "request"))
    print(f"เขียนแผนผัง {len(new['files'])} ไฟล์ · ใช้งานจริง {live} · เส้นเชื่อม {len(new['edges'])} · commit {new['commit']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
