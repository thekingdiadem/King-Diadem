# INTEGRATIONS/google_search.py
# KING DIADEM — Google Search real integration
# ใช้ Google Custom Search JSON API
# ต้องการ: GOOGLE_API_KEY + GOOGLE_CSE_ID (Custom Search Engine ID)

import os
import json
import urllib.request
import urllib.error
import urllib.parse

SEARCH_API = "https://www.googleapis.com/customsearch/v1"


def _creds() -> tuple[str, str]:
    key    = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    if not key:
        raise EnvironmentError("ไม่พบ GOOGLE_API_KEY ใน environment")
    if not cse_id:
        raise EnvironmentError(
            "ไม่พบ GOOGLE_CSE_ID ใน environment — "
            "สร้าง Custom Search Engine ที่ https://cse.google.com"
        )
    return key, cse_id


def _get(url: str) -> dict:
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"Search API error {e.code}: {e.read().decode()}")


# ── PUBLIC FUNCTIONS ──────────────────────────────────────────────

def search(
    query: str,
    num: int = 5,
    lang: str = "th",
    safe: str = "active",
) -> dict:
    """ค้นหาจริงผ่าน Google Custom Search API"""
    key, cse_id = _creds()
    url = (
        f"{SEARCH_API}"
        f"?key={key}"
        f"&cx={cse_id}"
        f"&q={urllib.parse.quote(query)}"
        f"&num={min(num, 10)}"
        f"&hl={lang}"
        f"&safe={safe}"
    )
    data = _get(url)

    items = data.get("items", [])
    results = [
        {
            "title":   item.get("title", ""),
            "url":     item.get("link", ""),
            "snippet": item.get("snippet", ""),
        }
        for item in items
    ]

    info = data.get("searchInformation", {})
    return {
        "query":        query,
        "total_results": info.get("formattedTotalResults", "0"),
        "search_time":  info.get("searchTime", 0),
        "results":      results,
        "platform_neutral": True,
    }


def search_news(query: str, num: int = 5) -> dict:
    """ค้นหาข่าวล่าสุด — เพิ่ม dateRestrict เพื่อกรองเฉพาะข่าวใหม่"""
    key, cse_id = _creds()
    url = (
        f"{SEARCH_API}"
        f"?key={key}"
        f"&cx={cse_id}"
        f"&q={urllib.parse.quote(query)}"
        f"&num={min(num, 10)}"
        f"&dateRestrict=d7"        # 7 วันล่าสุด
        f"&sort=date"
    )
    data = _get(url)
    items = data.get("items", [])
    return {
        "query":   query,
        "type":    "news",
        "results": [
            {
                "title":   item.get("title", ""),
                "url":     item.get("link", ""),
                "snippet": item.get("snippet", ""),
                "source":  item.get("displayLink", ""),
            }
            for item in items
        ],
    }


def quick_answer(query: str) -> str:
    """Return snippet แรกที่เจอ — สำหรับ LYLA ตอบคำถามเร็ว"""
    result = search(query, num=1)
    if result["results"]:
        r = result["results"][0]
        return f"{r['title']}\n{r['snippet']}\n{r['url']}"
    return f"ไม่พบข้อมูลสำหรับ: {query}"
