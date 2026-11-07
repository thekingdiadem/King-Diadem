"""ความสะอาดของ repo — พี่ขอให้เอาไฟล์ที่ไม่จำเป็นออก

ตรวจแล้ว (7 พ.ย. 2026): โมดูล Python 159 ไฟล์ถูกใช้จาก app.py ทั้งหมด และไฟล์ใน static/ ทุกไฟล์มีที่อ้างถึง
ไฟล์รกที่เห็นบน GitHub อยู่ใน branch เก่า (main, King) ไม่ใช่ branch หลัก
เทสต์นี้กันไม่ให้รกกลับมา: เพิ่มโมดูลที่ไม่มีใครเรียก หรือไฟล์ใน static/ ที่ไม่มีใครอ้าง → ล้ม พร้อมบอกชื่อไฟล์
"""
import ast
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP_DIRS = {".git", "__pycache__", "tests", "node_modules"}


def _modules() -> dict:
    out = {}
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS]
        for f in files:
            if f.endswith(".py"):
                p = os.path.join(d, f)
                name = os.path.relpath(p, ROOT)[:-3].replace(os.sep, ".")
                out[name[:-9] if name.endswith(".__init__") else name] = p
    return out


def _deps(path: str, mod: str, names: set) -> set:
    def resolve(n):
        parts = n.split(".")
        for i in range(len(parts), 0, -1):
            if ".".join(parts[:i]) in names:
                return ".".join(parts[:i])
        return None
    tree = ast.parse(open(path, encoding="utf-8", errors="replace").read())
    pkg = mod if path.endswith("__init__.py") else mod.rpartition(".")[0]
    out = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            out |= {r for a in n.names if (r := resolve(a.name))}
        elif isinstance(n, ast.ImportFrom):
            base = n.module or ""
            if n.level:
                up = pkg.split(".") if pkg else []
                up = up[:len(up) - (n.level - 1)] if n.level > 1 else up
                base = ".".join([*up, base] if base else up)
            for a in n.names:
                r = (resolve(f"{base}.{a.name}") if base else resolve(a.name)) or resolve(base)
                if r:
                    out.add(r)
        # โหลดแบบระบุชื่อเป็นข้อความ (ENGINE/engine_router: _try_import("ENGINE.situation_analyzer", ...))
        elif isinstance(n, ast.Constant) and isinstance(n.value, str) and n.value in names and "." in n.value:
            out.add(n.value)
    for m in list(out):
        parts = m.split(".")
        out |= {".".join(parts[:i]) for i in range(1, len(parts)) if ".".join(parts[:i]) in names}
    return out


def test_every_module_is_reachable_from_the_running_app():
    mods = _modules()
    names = set(mods)
    roots = [m for m in names if m in ("app", "gunicorn.conf") or m.startswith("scripts.")]
    seen, stack = set(), list(roots)
    while stack:
        m = stack.pop()
        if m not in seen:
            seen.add(m)
            stack.extend(_deps(mods[m], m, names))
    dead = sorted(names - seen - {"static"})                    # static/__init__.py เป็นแค่ตัวบอกว่าเป็นแพ็กเกจ
    assert not dead, f"โมดูลที่ app.py ไม่ได้ใช้เลย: {dead} — ต่อเข้าระบบ หรือลบออก"


def test_every_static_file_is_referenced_somewhere():
    texts = []
    for d, dirs, files in os.walk(ROOT):
        dirs[:] = [x for x in dirs if x not in SKIP_DIRS | {"sky"}]
        for f in files:
            if f.endswith((".py", ".js", ".html", ".css", ".json", ".md", ".yaml", ".txt", ".webmanifest", ".xml")):
                p = os.path.join(d, f)
                if os.path.getsize(p) < 3_000_000:
                    texts.append((p, open(p, encoding="utf-8", errors="replace").read()))
    static = os.path.join(ROOT, "static")
    orphans = []
    for d, dirs, files in os.walk(static):
        dirs[:] = [x for x in dirs if x not in ("sky", "__pycache__")]   # sky/ = แคตตาล็อกดาว Gaia โหลดตามเลข tile
        for f in files:
            p = os.path.join(d, f)
            rel = os.path.relpath(p, static)
            stem = re.escape(os.path.splitext(f)[0])
            if not any(q != p and (f in t or rel in t or re.search(r"['\"/]" + stem + r"['\"._-]", t)) for q, t in texts):
                orphans.append(rel)
    assert not orphans, f"ไฟล์ใน static/ ที่ไม่มีใครอ้างถึง: {orphans}"
