"""
core/llm_provider_policy.py — ต่อ AI ได้เฉพาะปลายทางทางการที่ตรวจสอบได้ (Direct Provider Enforcement)

ที่มา: ข่าว พ.ย. 2569 (HD Moore / Dragos) — ฝังความลับปลอม ~2 ล้านชิ้นใน prompt แล้วพบว่า
ผู้ให้บริการอย่างน้อย 3 รายถูกเจาะ ตัวกลาง (reseller / router) เก็บ log prompt บางรายไม่เคารพ zero-retention
และกุญแจ AWS ปลอมถูกนำไปใช้ภายในไม่กี่ชั่วโมง

หลัก:
- ส่งข้อความผู้ใช้ไปได้เฉพาะ https ไปยังโดเมนของผู้ผลิตโมเดลเอง (รายการด้านล่าง)
- ตัวกลาง/router (เช่น OpenRouter) และโดเมนที่ไม่รู้จัก = ไม่ต่อ ระบบสลับไป Gemini ทางการ หรือตอบจากสมการแทน
- เจ้าของระบบเปิดยกเว้นได้เองเท่านั้น (KD_ALLOW_UNVERIFIED_LLM=1) และระบบบันทึกว่าไม่ได้ตรวจสอบ
- Gemini ถูกล็อกปลายทางเป็นของ Google เสมอ ไม่ว่าในเครื่องจะตั้งค่าเปลี่ยนปลายทางไว้อย่างไร
"""
from __future__ import annotations

import os
from urllib.parse import urlparse

GEMINI_OFFICIAL = "https://generativelanguage.googleapis.com/"
# โดเมน API ของผู้ผลิตโมเดลโดยตรง (ไม่ใช่ตัวกลาง)
OFFICIAL_HOSTS = {
    "generativelanguage.googleapis.com": "Google (Gemini)",
    "api.openai.com": "OpenAI",
    "api.anthropic.com": "Anthropic",
    "api.deepseek.com": "DeepSeek",
    "dashscope.aliyuncs.com": "Alibaba (Qwen)",
    "dashscope-intl.aliyuncs.com": "Alibaba (Qwen)",
    "api.mistral.ai": "Mistral",
}
# ตัวกลางที่รู้จัก — บอกเหตุผลให้ชัดว่าทำไมไม่ต่อ
KNOWN_ROUTERS = ("openrouter.ai", "together.xyz", "api.together.ai", "groq.com", "fireworks.ai", "poe.com")


def _self_hosted(host: str) -> bool:
    import ipaddress
    if host in ("localhost",) or host.endswith(".internal") or host.endswith(".local"):
        return True
    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback


def allow_unverified() -> bool:
    return os.getenv("KD_ALLOW_UNVERIFIED_LLM", "").strip().lower() in ("1", "true", "yes", "on")


def check_url(url: str) -> dict:
    """{ok, host, vendor, verified, reason} — ok=False แปลว่าห้ามส่งข้อความผู้ใช้ไปที่นี่"""
    u = urlparse(str(url or "").strip())
    host = (u.hostname or "").lower()
    if host and u.scheme in ("http", "https") and _self_hosted(host):
        # โมเดลที่รันเองในเครือข่ายส่วนตัว (vLLM · Ollama) — ข้อความไม่ออกไปนอกเครื่อง ปลอดภัยที่สุด
        return {"ok": True, "host": host, "vendor": "self-hosted", "verified": True, "reason": ""}
    if u.scheme != "https" or not host:
        return {"ok": False, "host": host, "vendor": "", "verified": False,
                "reason": "ต้องเป็น https และมีโดเมนชัดเจน"}
    if host in OFFICIAL_HOSTS:
        return {"ok": True, "host": host, "vendor": OFFICIAL_HOSTS[host], "verified": True, "reason": ""}
    router = any(host == r or host.endswith("." + r) for r in KNOWN_ROUTERS)
    why = "เป็นตัวกลาง/router ไม่ใช่ผู้ผลิตโมเดลโดยตรง" if router else "ไม่อยู่ในรายชื่อปลายทางทางการ"
    if allow_unverified():
        return {"ok": True, "host": host, "vendor": "", "verified": False,
                "reason": why + " — เจ้าของระบบเปิดยกเว้นไว้ (KD_ALLOW_UNVERIFIED_LLM)"}
    return {"ok": False, "host": host, "vendor": "", "verified": False, "reason": why}


def status() -> dict:
    """ผู้ให้บริการที่ตั้งไว้ตอนนี้ — ใช้ในรายงาน audit (ไม่มี key)"""
    name = os.getenv("LLM_PROVIDER", "gemini").strip().lower() or "gemini"
    if name == "gemini":
        st = check_url(GEMINI_OFFICIAL)
    else:
        st = check_url(os.getenv("LLM_BASE_URL", ""))
    chain = [m.strip() for m in os.getenv(
        "GEMINI_FALLBACK_MODELS", "gemini-2.0-flash-lite,gemini-2.0-flash,gemini-2.5-flash-lite,gemini-2.5-flash").split(",") if m.strip()]
    return {"provider": name, **st,
            "fallback": {"gemini_models": chain, "provider_to_gemini": name != "gemini",
                         "last_resort": "คำตอบจากสมการของระบบ (ไม่ส่งข้อความออกไปไหน)"}}
