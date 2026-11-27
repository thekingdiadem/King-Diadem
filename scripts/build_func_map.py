"""
scripts/build_func_map.py — แผนผังระดับฟังก์ชัน (static/func_map.json) จากโค้ด Python จริง

หน้าวงจร (/circuit) ใช้ซูมลงจากระดับไฟล์ไปถึงระดับฟังก์ชัน:
  · ทุกฟังก์ชัน/คลาส/เมธอดใน .py ที่อยู่ในแผนผังระบบ = จุดหนึ่งจุด (ผูกกับไฟล์ของมัน)
  · ทุกการเรียกที่ชี้ชัดได้ว่าไปหาฟังก์ชันไหน = เส้นหนึ่งเส้น
ชี้ชัดเท่านั้น — ไม่เดา: เรียกชื่อในไฟล์เดียวกัน · ชื่อที่ import มาตรงๆ (from x import f) ·
mod.f() เมื่อ mod คือโมดูลใน repo · self.m() ภายในคลาสเดียวกัน ส่วนที่ชี้ไม่ได้ไม่ถูกนับ

รัน:  python scripts/build_func_map.py
"""
from __future__ import annotations

import ast
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAP = os.path.join(ROOT, "static", "system_map.json")
OUT = os.path.join(ROOT, "static", "func_map.json")


def mod_name(path: str) -> str:
    p = path[:-3].replace("/", ".")
    return p[:-9] if p.endswith(".__init__") else p


def main() -> None:
    sm = json.load(open(MAP, encoding="utf-8"))
    files = [f[0] for f in sm["files"]]
    fidx = {p: i for i, p in enumerate(files)}
    pys = [p for p in files if p.endswith(".py") and os.path.exists(os.path.join(ROOT, p))]
    mods = {mod_name(p): p for p in pys}

    nodes = []            # [file_index, name, lines, kind(0 def · 1 class · 2 method)]
    by_file = {}          # path -> {name: node_id}  (ระดับบนสุด)
    by_class = {}         # (path, class) -> {method: node_id}
    trees = {}
    for p in pys:
        try:
            tree = ast.parse(open(os.path.join(ROOT, p), encoding="utf-8").read())
        except (SyntaxError, UnicodeDecodeError, ValueError):
            continue
        trees[p] = tree
        top = by_file.setdefault(p, {})
        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                ln = (getattr(n, "end_lineno", n.lineno) or n.lineno) - n.lineno + 1
                top[n.name] = len(nodes)
                nodes.append([fidx[p], n.name, ln, 1 if isinstance(n, ast.ClassDef) else 0])
                if isinstance(n, ast.ClassDef):
                    meth = by_class.setdefault((p, n.name), {})
                    for m in n.body:
                        if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                            mln = (getattr(m, "end_lineno", m.lineno) or m.lineno) - m.lineno + 1
                            meth[m.name] = len(nodes)
                            nodes.append([fidx[p], n.name + "." + m.name, mln, 2])

    edges = set()
    for p, tree in trees.items():
        imported = {}     # local name -> node id
        modalias = {}     # local name -> repo path
        for n in ast.walk(tree):
            if isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                src = mods.get(n.module)
                for a in n.names:
                    full = n.module + "." + a.name
                    if full in mods:
                        modalias[a.asname or a.name] = mods[full]
                    elif src and a.name in by_file.get(src, {}):
                        imported[a.asname or a.name] = by_file[src][a.name]
            elif isinstance(n, ast.Import):
                for a in n.names:
                    if a.name in mods:
                        modalias[a.asname or a.name.split(".")[0] if not a.asname else a.asname] = mods[a.name]

        def scan(body_owner, caller, cls):
            for n in ast.walk(body_owner):
                if not isinstance(n, ast.Call):
                    continue
                f, tgt = n.func, None
                if isinstance(f, ast.Name):
                    tgt = by_file.get(p, {}).get(f.id, imported.get(f.id))
                elif isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name):
                    v = f.value.id
                    if v == "self" and cls:
                        tgt = by_class.get((p, cls), {}).get(f.attr)
                    elif v in modalias:
                        tgt = by_file.get(modalias[v], {}).get(f.attr)
                if tgt is not None and tgt != caller:
                    edges.add((caller, tgt))

        for n in tree.body:
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
                scan(n, by_file[p][n.name], None)
            elif isinstance(n, ast.ClassDef):
                for m in n.body:
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        scan(m, by_class[(p, n.name)][m.name], n.name)

    out = {"commit": sm.get("commit", ""), "nodes": nodes, "edges": sorted(edges)}
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, separators=(",", ":"))
    cross = sum(1 for a, b in edges if nodes[a][0] != nodes[b][0])
    print(f"ฟังก์ชัน/คลาส {len(nodes)} · การเรียกที่ชี้ชัด {len(edges)} (ข้ามไฟล์ {cross}) · {os.path.getsize(OUT) // 1024} KB")


if __name__ == "__main__":
    main()
