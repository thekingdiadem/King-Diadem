"""
core/llm_openai_compat.py — ผู้ให้บริการ AI รายที่ 2 (มาตรฐาน OpenAI-compatible)

ทำไมต้องมี:
    เงินทุน AI เริ่มตึง ราคา API และโควตาเปลี่ยนเร็ว — ถ้ามีแค่ Gemini เจ้าเดียว วันที่ Gemini มีปัญหา
    ระบบจะเหลือแค่คำตอบจากสมการ (kernel_voice) ไฟล์นี้ทำให้เปลี่ยนผู้ให้บริการได้ด้วย env อย่างเดียว

หลักการ:
    governance ทั้งหมด (CRISIS / VEGA / LYLA / COUNCIL, ตัดความคิดภายใน, cache, คำตอบสำรอง)
    อยู่ใน GeminiLLM — คลาสนี้สืบทอดมาแล้วเปลี่ยนแค่ "ท่อส่ง" (_call) จึงได้กฎชุดเดียวกันทุกเจ้า

ใช้กับ: OpenAI · DeepSeek · Qwen (DashScope compatible-mode) · OpenRouter · เซิร์ฟเวอร์ที่รัน
    โมเดลเองแบบ OpenAI-compatible (vLLM, Ollama ฯลฯ)

ตั้งค่า (Render environment):
    LLM_PROVIDER = openai_compat
    LLM_BASE_URL = https://api.deepseek.com/v1        (ตัวอย่าง — ต้องลงท้ายก่อน /chat/completions)
    LLM_API_KEY  = ...
    LLM_MODEL    = deepseek-chat
ไม่ต้องลงไลบรารีเพิ่ม — ใช้ urllib ของ Python
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from core import llm_gemini as _g


class OpenAICompatLLM(_g.GeminiLLM):
    provider = "openai_compat"

    def __init__(self, model: str = ""):          # noqa: D401 — ไม่เรียก GeminiLLM.__init__ (ไม่ต้องมี key Gemini)
        if os.getenv("KD_AI", "on").strip().lower() in ("off", "0", "false", "no"):
            raise ValueError("KD_AI=off — ปิด AI")
        self.base_url = os.getenv("LLM_BASE_URL", "").strip().rstrip("/")
        if not self.base_url.startswith(("https://", "http://")):
            raise ValueError("ไม่พบ LLM_BASE_URL (ต้องขึ้นต้นด้วย https://)")
        self._keys = [k for k in (os.getenv("LLM_API_KEY"), os.getenv("LLM_API_KEY2")) if k]
        if not self._keys:
            raise ValueError("ไม่พบ LLM_API_KEY")
        self._key_index = 0
        self.model = model or os.getenv("LLM_MODEL", "").strip()
        if not self.model:
            raise ValueError("ไม่พบ LLM_MODEL")
        self.client = None
        print(f"✅ OpenAICompatLLM ready | base={self.base_url} | model={self.model} | keys={len(self._keys)}")

    # Gemini ใช้ client ของตัวเอง — ที่นี่ส่ง HTTP ตรง
    def _init_client(self):
        self.client = None

    @staticmethod
    def _to_messages(system: str, contents: list) -> list:
        msgs = [{"role": "system", "content": system}] if system else []
        for c in contents or []:
            role = getattr(c, "role", "user")
            parts = getattr(c, "parts", None) or []
            text = "".join(str(getattr(p, "text", "") or "") for p in parts)
            if text:
                msgs.append({"role": "assistant" if role == "model" else "user", "content": text})
        return msgs

    def _post(self, payload: dict, timeout: float) -> dict:
        req = urllib.request.Request(
            self.base_url + "/chat/completions",
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={"Content-Type": "application/json",
                     "Authorization": f"Bearer {self._keys[self._key_index]}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:     # noqa: S310 — base_url มาจาก env ของเจ้าของระบบ
            return json.loads(resp.read().decode("utf-8"))

    def _call(self, system: str, contents: list,
              temperature: float = 0.72, max_tokens: int = 1024) -> str:
        prompt_text = ""
        if contents:
            parts = getattr(contents[-1], "parts", None) or []
            prompt_text = str(getattr(parts[0], "text", "") or "") if parts else ""
        if _g.ai_disabled():
            _g._tls.fallback = True
            return self._fallback_response(system, prompt_text)

        ck = _g._cache_key(system, _g._contents_text(contents), temperature)
        cached = _g._cache_get(ck)
        if cached:
            return cached

        payload = {"model": self.model, "messages": self._to_messages(system, contents),
                   "temperature": temperature, "max_tokens": max_tokens}
        deadline = time.time() + float(os.getenv("LLM_CALL_BUDGET_S", "45"))
        for attempt in range(len(self._keys) * 2):
            left = deadline - time.time()
            if left <= 1:
                break
            try:
                data = self._post(payload, timeout=min(left, 40))
                choice = (data.get("choices") or [{}])[0]
                text = str((choice.get("message") or {}).get("content") or "").strip()
                if text and choice.get("finish_reason") != "length":
                    _g._cache_set(ck, text)
                    return text
                if text:                                   # ถูกตัดกลางทาง — ตัดให้จบประโยคแล้วใช้
                    cut = _g._trim_hard(text)
                    if len(cut) >= 80:
                        return cut
            except urllib.error.HTTPError as e:
                if e.code in (401, 403):
                    print(f"⚠️ {self.provider} auth error {e.code}")
                    if len(self._keys) > 1 and attempt == 0:
                        self._rotate_key()
                        continue
                    break
                if e.code == 429:
                    self._rotate_key()
                    if time.time() + 2 > deadline:
                        break
                    time.sleep(2)
                    continue
                print(f"⚠️ {self.provider} HTTP {e.code}")
            except Exception as e:                         # เครือข่ายล่ม/ค้าง/JSON เพี้ยน
                print(f"⚠️ {self.provider} error: {type(e).__name__}")
        _g._note_total_failure()
        _g._tls.fallback = True
        return self._fallback_response(system, prompt_text)
