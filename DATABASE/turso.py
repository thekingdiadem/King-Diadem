"""ต่อ Turso ด้วย Python ล้วนผ่าน HTTPS (โปรโตคอล Hrana v2: POST /v2/pipeline)

เดิมใช้ไลบรารี libsql (โค้ด Rust/C ข้างใน) — บนเว็บจริงเซิร์ฟเวอร์ตายแบบ segfault (exit 139) เป็นพักๆ
Python ล้วนทำให้โปรเซสตายแบบนั้นไม่ได้: อย่างแย่ที่สุดคำสั่งนั้น error แล้วเว็บทำงานต่อ

ใช้เหมือน sqlite3: execute / fetchone / fetchall / r["col"] / commit / BEGIN IMMEDIATE ... COMMIT
- คำสั่งเดี่ยวนอก transaction = commit ทันที (โค้ดเดิม commit หลังเขียนทุกครั้งอยู่แล้ว)
- BEGIN ... COMMIT/ROLLBACK = ใช้ stream เดียวกัน (baton) ล็อกอยู่บนเซิร์ฟเวอร์จนจบ
"""
import base64
import sqlite3
import threading

import httpx

_client = None
_client_lock = threading.Lock()


def client() -> httpx.Client:
    """httpx client ตัวเดียวทั้งโปรเซส (เก็บการเชื่อมต่อไว้ใช้ซ้ำ ไม่จับมือ TLS ใหม่ทุกคำสั่ง) · เทสต์เปลี่ยนเป็นเซิร์ฟเวอร์จำลองได้"""
    global _client
    with _client_lock:
        if _client is None:
            _client = httpx.Client(timeout=httpx.Timeout(20.0, connect=10.0))
        return _client


def set_client(c) -> None:
    global _client
    with _client_lock:
        _client = c


def _http_url(url: str) -> str:
    url = url.strip().rstrip("/")
    for a, b in (("libsql://", "https://"), ("wss://", "https://"), ("ws://", "http://")):
        if url.startswith(a):
            return b + url[len(a):]
    return url


def _arg(v):
    if v is None:
        return {"type": "null"}
    if isinstance(v, bool):
        return {"type": "integer", "value": str(int(v))}
    if isinstance(v, int):
        return {"type": "integer", "value": str(v)}
    if isinstance(v, float):
        return {"type": "float", "value": v}
    if isinstance(v, (bytes, bytearray, memoryview)):
        return {"type": "blob", "base64": base64.b64encode(bytes(v)).decode().rstrip("=")}
    return {"type": "text", "value": str(v)}


def _val(c):
    t = c.get("type")
    if t == "integer":
        return int(c["value"])
    if t == "float":
        return float(c["value"])
    if t == "text":
        return c["value"]
    if t == "blob":
        b = c.get("base64", "")
        return base64.b64decode(b + "=" * (-len(b) % 4))
    return None


def _error(e: dict):
    msg = (e or {}).get("message") or "database error"
    code = (e or {}).get("code") or ""
    if "CONSTRAINT" in code or "constraint failed" in msg:
        return sqlite3.IntegrityError(msg)
    if "BUSY" in code or "LOCKED" in code or "locked" in msg:
        return sqlite3.OperationalError(msg)
    return sqlite3.DatabaseError(msg)


class Row(tuple):
    """แถวแบบ sqlite3.Row: r[0] · r["email"] · dict(r) · r.keys()"""
    __slots__ = ()
    _names = ()
    _index = {}

    def __getitem__(self, k):
        if isinstance(k, str):
            i = self._index.get(k)
            if i is None:
                i = self._index.get(k.lower())
            if i is None:
                raise IndexError(f"No item with that key: {k}")
            return tuple.__getitem__(self, i)
        return tuple.__getitem__(self, k)

    def keys(self):
        return list(self._names)


def _row_class(names):
    names = tuple(names)
    idx = {n: i for i, n in enumerate(names)}
    idx.update({n.lower(): i for i, n in enumerate(names) if n.lower() not in idx})
    return type("Row", (Row,), {"__slots__": (), "_names": names, "_index": idx})


class Cursor:
    def __init__(self, result=None):
        r = result or {}
        cols = [c.get("name") or "" for c in r.get("cols") or []]
        R = _row_class(cols) if cols else None
        self._rows = [R(tuple(_val(c) for c in row)) for row in r.get("rows") or []] if R else []
        self.description = tuple((c, None, None, None, None, None, None) for c in cols) or None
        self.rowcount = int(r.get("affected_row_count") or 0) if cols == [] else -1
        lid = r.get("last_insert_rowid")
        self.lastrowid = int(lid) if lid not in (None, "") else None
        self._i = 0

    def fetchone(self):
        if self._i >= len(self._rows):
            return None
        self._i += 1
        return self._rows[self._i - 1]

    def fetchall(self):
        out, self._i = self._rows[self._i:], len(self._rows)
        return out

    def __iter__(self):
        return iter(self.fetchall())


class Connection:
    def __init__(self, url: str, token: str):
        self._url = _http_url(url)
        self._token = token
        self._baton = None
        self._base = None
        self.in_transaction = False
        self.row_factory = None

    def _pipeline(self, reqs, keep: bool):
        body = {"baton": self._baton, "requests": list(reqs) + ([] if keep else [{"type": "close"}])}
        headers = {"Authorization": f"Bearer {self._token}"} if self._token else {}
        try:
            r = client().post((self._base or self._url) + "/v2/pipeline", json=body, headers=headers)
        except httpx.HTTPError as e:
            self._reset()
            raise sqlite3.OperationalError(f"Turso unreachable: {type(e).__name__}") from e
        if r.status_code != 200:
            self._reset()
            raise sqlite3.OperationalError(f"Turso HTTP {r.status_code}: {r.text[:200]}")
        d = r.json()
        self._baton = d.get("baton") if keep else None
        if d.get("base_url"):
            self._base = d["base_url"].rstrip("/")
        out = []
        for res in d.get("results") or []:
            if res.get("type") == "error":
                if not keep:
                    self._reset()
                raise _error(res.get("error"))
            out.append((res.get("response") or {}))
        return out

    def _reset(self):
        self._baton = None
        self._base = None
        self.in_transaction = False

    def execute(self, sql, params=()):
        head = sql.lstrip().split(None, 1)[0].upper() if sql.strip() else ""
        if head == "PRAGMA" and "=" in sql:     # ตั้งค่าไฟล์ (journal_mode, busy_timeout) ไม่มีความหมายบนคลาวด์ · อ่านอย่าง table_info ได้
            raise sqlite3.DatabaseError("PRAGMA setting is not supported on the cloud database")   # โค้ดเดิมจับไว้แล้ว
        starts = head == "BEGIN"
        ends = head in ("COMMIT", "END", "ROLLBACK")
        keep = (self.in_transaction or starts) and not ends
        stmt = {"sql": sql, "args": [_arg(p) for p in (params or ())]}
        try:
            res = self._pipeline([{"type": "execute", "stmt": stmt}], keep)
        except sqlite3.Error:
            if self.in_transaction and not ends:
                self._rollback_quiet()
            raise
        if starts:
            self.in_transaction = True
        if ends:
            self._reset()
        return Cursor((res[0].get("result") if res else None))

    def executemany(self, sql, seq):
        cur = None
        for p in seq:
            cur = self.execute(sql, p)
        return cur or Cursor()

    def executescript(self, script):
        self._pipeline([{"type": "sequence", "sql": script}], self.in_transaction)
        return Cursor()

    def _rollback_quiet(self):
        try:
            if self._baton:
                self._pipeline([{"type": "execute", "stmt": {"sql": "ROLLBACK"}}], False)
        except Exception:
            pass
        self._reset()

    def commit(self):
        if self.in_transaction:
            self.execute("COMMIT")

    def rollback(self):
        if self.in_transaction:
            self._rollback_quiet()

    def close(self):
        self.rollback()
        if self._baton:
            try:
                self._pipeline([], False)
            except Exception:
                pass
        self._reset()

    def __enter__(self):
        return self

    def __exit__(self, et, ev, tb):
        if et is None:
            self.commit()
        else:
            self.rollback()
        return False
