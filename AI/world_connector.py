# AI/world_connector.py
# KING DIADEM — World Signal Connector
# FATE™ Axiom compliance: Determinism · Explainability=100% · Downside First
# ใช้ urllib เท่านั้น (ไม่ต้องติดตั้ง requests) — consistent กับ app.py pattern
# Fail less. Harm less. Restore more.

import json
import time
import urllib.request
import urllib.error

_TIMEOUT = 5  # seconds

# ── ENDPOINT REGISTRY ─────────────────────────────────────────────
_ENDPOINTS = {
    "btc_price": {
        "url":    "https://api.coindesk.com/v1/bpi/currentprice.json",
        "parser": lambda d: {"btc_usd": d["bpi"]["USD"]["rate"], "source": "coindesk"},
    },
    "global_ip": {
        "url":    "https://api.ipify.org?format=json",
        "parser": lambda d: {"ip": d.get("ip", "unknown"), "source": "ipify"},
    },
}


def _fetch(url: str, timeout: int = _TIMEOUT) -> dict:
    """
    HTTP GET ด้วย urllib — ไม่ใช้ requests
    Returns: parsed JSON dict หรือ {"error": reason}
    """
    try:
        req  = urllib.request.Request(url, headers={"User-Agent": "KING-DIADEM/4.7"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}", "offline": True}
    except urllib.error.URLError as e:
        return {"error": f"URLError: {e.reason}", "offline": True}
    except json.JSONDecodeError as e:
        return {"error": f"JSON parse failed: {e}", "offline": True}
    except Exception as e:
        return {"error": f"unexpected: {type(e).__name__}: {e}", "offline": True}


class WorldConnector:
    """
    Real-world signal connector — deterministic, explicit errors
    ไม่ใช้ random — ทุก call บอกได้ว่าได้ข้อมูลจากไหน หรือ fail เพราะอะไร
    """

    def world_status(self) -> dict:
        """
        ดึงสัญญาณ real-world หลายแหล่งพร้อมกัน
        Returns: dict ที่มี per-source result + fate_note
        """
        results: dict[str, dict] = {}
        errors:  list[str]       = []

        for key, cfg in _ENDPOINTS.items():
            raw = _fetch(cfg["url"])
            if raw.get("offline") or raw.get("error"):
                results[key] = {"status": "offline", "error": raw.get("error", "unknown")}
                errors.append(key)
            else:
                try:
                    results[key] = {**cfg["parser"](raw), "status": "ok"}
                except (KeyError, TypeError) as e:
                    results[key] = {"status": "parse_error", "error": str(e)}
                    errors.append(key)

        fate_note = (
            f"OFFLINE: {', '.join(errors)} ไม่สามารถเชื่อมต่อได้"
            if errors else "✅ ทุก endpoint ตอบสนอง"
        )

        return {
            "signals":      results,
            "online_count": len(_ENDPOINTS) - len(errors),
            "total":        len(_ENDPOINTS),
            "fate_note":    fate_note,
            "fetched_at":   int(time.time()),
        }

    def btc_price(self) -> dict:
        """Single endpoint — BTC price only"""
        raw = _fetch(_ENDPOINTS["btc_price"]["url"])
        if raw.get("offline") or raw.get("error"):
            return {"btc_usd": None, "status": "offline", "error": raw.get("error")}
        try:
            return {**_ENDPOINTS["btc_price"]["parser"](raw), "status": "ok"}
        except (KeyError, TypeError) as e:
            return {"btc_usd": None, "status": "parse_error", "error": str(e)}
