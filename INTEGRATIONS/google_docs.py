# INTEGRATIONS/google_docs.py
# KING DIADEM — Google Docs real integration
# ใช้ Google Docs API v1 ผ่าน service account หรือ OAuth token

import os
import re
import json
import urllib.request
import urllib.error

_DOC_ID_RE = re.compile(r"^[A-Za-z0-9_-]{10,100}$")


def _doc_id(doc_id: str) -> str:
    """doc_id ถูกต่อเข้า path ของ URL — ต้องเป็นรูปแบบ id ของ Google เท่านั้น (กัน ../ หรือ ?param)"""
    doc_id = str(doc_id or "")
    if not _DOC_ID_RE.match(doc_id):
        raise ValueError("invalid document id")
    return doc_id

DOCS_API = "https://docs.googleapis.com/v1/documents"
DRIVE_API = "https://www.googleapis.com/drive/v3/files"


def _get_token() -> str:
    """ดึง token จาก env — รองรับทั้ง OAuth access token และ API key"""
    token = os.getenv("GOOGLE_ACCESS_TOKEN") or os.getenv("GOOGLE_API_KEY")
    if not token:
        raise EnvironmentError(
            "ไม่พบ GOOGLE_ACCESS_TOKEN หรือ GOOGLE_API_KEY ใน environment"
        )
    return token


def _headers() -> dict:
    token = _get_token()
    # ถ้าเป็น access token ใช้ Bearer, ถ้าเป็น API key ใส่ใน query แทน
    if token.startswith("ya29.") or len(token) > 100:
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
    return {"Content-Type": "application/json"}


def _api_key_param() -> str:
    token = _get_token()
    if not (token.startswith("ya29.") or len(token) > 100):
        return f"?key={token}"
    return ""


def _request(method: str, url: str, body: dict = None) -> dict:
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=_headers(), method=method)
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode()
        raise RuntimeError(f"Google API error {e.code}: {error_body}")


# ── PUBLIC FUNCTIONS ──────────────────────────────────────────────

def create_document(title: str) -> dict:
    """สร้าง Google Doc ใหม่ — return doc_id และ url"""
    url = DOCS_API + _api_key_param()
    result = _request("POST", url, {"title": title})
    doc_id = result.get("documentId", "")
    return {
        "doc_id": doc_id,
        "title": result.get("title", title),
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",
        "status": "created",
    }


def get_document(doc_id: str) -> dict:
    """อ่านเนื้อหา Google Doc"""
    doc_id = _doc_id(doc_id)
    url = f"{DOCS_API}/{doc_id}{_api_key_param()}"
    result = _request("GET", url)
    # ดึง plain text จาก body content
    text_parts = []
    for elem in result.get("body", {}).get("content", []):
        for para_elem in elem.get("paragraph", {}).get("elements", []):
            text_run = para_elem.get("textRun", {})
            if text_run.get("content"):
                text_parts.append(text_run["content"])
    return {
        "doc_id": doc_id,
        "title": result.get("title", ""),
        "text": "".join(text_parts).strip(),
        "url": f"https://docs.google.com/document/d/{doc_id}/edit",
    }


def append_text(doc_id: str, text: str) -> dict:
    """เพิ่มข้อความท้าย document"""
    doc_id = _doc_id(doc_id)
    url = f"{DOCS_API}/{doc_id}:batchUpdate{_api_key_param()}"
    body = {
        "requests": [
            {
                "insertText": {
                    "location": {"index": 1},
                    "text": text + "\n",
                }
            }
        ]
    }
    _request("POST", url, body)
    return {"doc_id": doc_id, "appended": text, "status": "ok"}


def list_recent_docs(page_size: int = 10) -> list:
    """ดู Google Docs ล่าสุด (ต้องการ OAuth token ที่มี drive.readonly scope)"""
    try:
        page_size = max(1, min(int(page_size), 100))
    except (TypeError, ValueError):
        page_size = 10
    param = _api_key_param()
    sep = "&" if param else "?"
    url = (
        f"{DRIVE_API}{param}{sep}"
        f"q=mimeType%3D%27application%2Fvnd.google-apps.document%27"
        f"&orderBy=modifiedTime+desc&pageSize={page_size}"
        f"&fields=files(id%2Cname%2CmodifiedTime%2CwebViewLink)"
    )
    result = _request("GET", url)
    return [
        {
            "doc_id": f["id"],
            "title": f["name"],
            "modified": f.get("modifiedTime", ""),
            "url": f.get("webViewLink", ""),
        }
        for f in result.get("files", [])
    ]
