"""เซิร์ฟเวอร์ Turso จำลอง (Hrana v2 /v2/pipeline) ในโปรเซสเดียวกับเทสต์ — ใช้ SQLite จริงข้างหลัง

KD_DB_DRIVER=hrana-fake → DATABASE/turso.py คุยกับตัวนี้แทน Turso จริง เทสต์ทั้งชุดจึงรันผ่านตัวต่อคลาวด์ได้
(ต่อ Turso จริงในเทสต์/CI ไม่ได้) · stream (baton) = connection SQLite แยก ใช้ทำ BEGIN ... COMMIT"""
import base64
import itertools
import json
import os
import sqlite3
import threading

import httpx

_lock = threading.Lock()
_streams = {}
_ids = itertools.count(1)


def _path():
    from DATABASE.db import DB_PATH
    d = os.path.dirname(DB_PATH)
    if d:
        os.makedirs(d, exist_ok=True)
    return DB_PATH


def _arg(a):
    t = a.get("type")
    if t == "integer":
        return int(a["value"])
    if t == "float":
        return float(a["value"])
    if t == "text":
        return a["value"]
    if t == "blob":
        b = a.get("base64", "")
        return base64.b64decode(b + "=" * (-len(b) % 4))
    return None


def _cell(v):
    if v is None:
        return {"type": "null"}
    if isinstance(v, int):
        return {"type": "integer", "value": str(v)}
    if isinstance(v, float):
        return {"type": "float", "value": v}
    if isinstance(v, bytes):
        return {"type": "blob", "base64": base64.b64encode(v).decode()}
    return {"type": "text", "value": str(v)}


def _err(e):
    code = "SQLITE_CONSTRAINT_UNIQUE" if isinstance(e, sqlite3.IntegrityError) else "SQLITE_BUSY" if "locked" in str(e) else "SQLITE_ERROR"
    return {"type": "error", "error": {"message": str(e), "code": code}}


def _handle(request: httpx.Request) -> httpx.Response:
    assert request.url.path == "/v2/pipeline", request.url.path
    assert request.headers.get("authorization", "").startswith("Bearer ")
    body = json.loads(request.content)
    with _lock:
        baton = body.get("baton")
        conn = _streams.pop(baton, None) if baton else None
        if conn is None:
            conn = sqlite3.connect(_path(), timeout=0, isolation_level=None, check_same_thread=False)
        results, closed = [], False
        for req in body.get("requests") or []:
            t = req.get("type")
            try:
                if t == "execute":
                    st = req["stmt"]
                    cur = conn.execute(st["sql"], [_arg(a) for a in st.get("args") or []])
                    cols = [{"name": d[0], "decltype": None} for d in cur.description or []]
                    rows = [[_cell(v) for v in r] for r in cur.fetchall()] if cols else []
                    res = {"cols": cols, "rows": rows, "affected_row_count": max(cur.rowcount, 0),
                           "last_insert_rowid": str(cur.lastrowid) if cur.lastrowid is not None else None}
                    results.append({"type": "ok", "response": {"type": "execute", "result": res}})
                elif t == "sequence":
                    conn.executescript(req["sql"])
                    results.append({"type": "ok", "response": {"type": "sequence"}})
                elif t == "close":
                    closed = True
                    results.append({"type": "ok", "response": {"type": "close"}})
            except sqlite3.Error as e:
                results.append(_err(e))
        new_baton = None
        if closed:
            if conn.in_transaction:
                conn.rollback()
            conn.close()
        else:
            new_baton = "b%d" % next(_ids)
            _streams[new_baton] = conn
    return httpx.Response(200, json={"baton": new_baton, "base_url": None, "results": results})


def install():
    from DATABASE import turso
    turso.set_client(httpx.Client(transport=httpx.MockTransport(_handle), base_url="http://fake-turso"))
