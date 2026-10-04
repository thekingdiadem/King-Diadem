# ENGINE/emotion_state.py — KING DIADEM
# (เดิมไฟล์นี้ไม่มีนามสกุล .py จึง import ไม่ได้ — ระบบจำอารมณ์ไม่เคยทำงาน)
# track อารมณ์ข้ามหลายเทิร์น + inject context ให้ LYLA
# ไฟล์นี้ logic ดีแล้ว — ปรับ CRISIS persistence + brain.py integration

from __future__ import annotations
import time
import threading
from collections import deque, OrderedDict
from typing import Literal

EmotionT = Literal[
    "CRISIS", "SAD", "STRESSED", "LONELY",
    "JOY", "LOVE", "WORK_WIN", "NEUTRAL"
]

_PRIORITY: dict[str, int] = {
    "CRISIS":   10,
    "SAD":       7,
    "STRESSED":  6,
    "LONELY":    5,
    "LOVE":      4,
    "WORK_WIN":  4,
    "JOY":       3,
    "NEUTRAL":   0,
}

_SIGNALS: list[tuple[str, list[str]]] = [
    ("CRISIS",   ["อยากตาย","ไม่อยากอยู่","ฆ่าตัว","จบชีวิต","ทนไม่ไหวแล้ว",
                  "suicid","want to die","end it","kill myself"]),
    # หมายเหตุ: เดิมมี "หมดแล้ว" ทำให้ "เงินหมดแล้ว" ถูกนับเป็น CRISIS (ความเสี่ยงชีวิต) — เอาออก
    ("SAD",      ["เสียใจ","ร้องไห้","เศร้า","หมดหวัง","ท้อ","เจ็บปวด",
                  "อกหัก","เลิกกัน","แฟนทิ้ง","sad","cry","heartbreak","hopeless"]),
    ("STRESSED", ["เครียด","กังวล","กลัว","ตื่นตระหนก","หนักใจ","วิตก","ไม่ไหว",
                  "panic","stress","anxious","scared","overwhelm"]),
    ("LONELY",   ["เหงา","โดดเดี่ยว","ไม่มีใคร","อ้างว้าง","ว้าเหว่",
                  "lonely","alone","isolated","no one"]),
    ("LOVE",     ["แฟนใหม่","ตกหลุมรัก","ชอบคนนี้","มีความรู้สึก","คนที่ชอบ",
                  "รักแล้ว","สารภาพรัก","in love","crush","confession","dating"]),
    ("WORK_WIN", ["ได้งาน","ได้โปรเจกต์","สำเร็จแล้ว","ผ่านแล้ว","ทำสำเร็จ",
                  "milestone","promotion","got the job","landed","accepted","achieved"]),
    ("JOY",      ["มีความสุข","ดีใจ","ตื่นเต้น","สนุก","ยินดี","เยี่ยม",
                  "happy","excited","great","wonderful","amazing","joy"]),
]

_RESPONSE_GUIDE: dict[str, str] = {
    "CRISIS":   "GUIDE:ช้าลง รับรู้ก่อน อย่ารีบวิเคราะห์ — Choice(t)≥1 ยังเป็นจริง",
    "SAD":      "GUIDE:รับรู้ความรู้สึกก่อน 1 ประโยค แล้วค่อยเปิดทางออก",
    "STRESSED": "GUIDE:ลดความกดดัน ให้ก้าวเล็กๆ ที่ทำได้วันนี้",
    "LONELY":   "GUIDE:อยู่เป็นเพื่อน ไม่ต้องรีบแก้ปัญหา",
    "JOY":      "GUIDE:รับอารมณ์บวก ไม่ต้องกังวลแทน",
    "LOVE":     "GUIDE:รับฟังเรื่องรัก ไม่ตัดสิน ไม่ over-advise",
    "WORK_WIN": "GUIDE:ชื่นชม ถามถึง milestone ถัดไปได้",
}

# จำนวนเทิร์น POSITIVE ที่ต้องเห็นก่อน CRISIS จะ clear
_CRISIS_RECOVERY_TURNS = 3


def detect_emotion(text: str) -> EmotionT:
    if not text:
        return "NEUTRAL"
    t = text.lower()
    found: list[tuple[int, str]] = []
    for emotion, keywords in _SIGNALS:
        hits = sum(1 for k in keywords if k in t)
        if hits:
            found.append((_PRIORITY[emotion] * hits, emotion))
    if not found:
        return "NEUTRAL"
    return max(found, key=lambda x: x[0])[1]  # type: ignore


class EmotionState:
    def __init__(self, maxlen: int = 20):
        self._log: deque[dict] = deque(maxlen=maxlen)
        self.current: EmotionT = "NEUTRAL"
        self.prev:    EmotionT = "NEUTRAL"
        self._positive_streak = 0  # ติดตาม recovery จาก CRISIS

    def update(self, text: str) -> EmotionT:
        emotion = detect_emotion(text)
        self.prev = self.current

        # CRISIS persistence — ต้องเห็น positive N เทิร์นติดกันก่อน clear
        if self.current == "CRISIS":
            if emotion in ("JOY", "WORK_WIN", "NEUTRAL"):
                self._positive_streak += 1
                if self._positive_streak >= _CRISIS_RECOVERY_TURNS:
                    self.current = emotion
                    self._positive_streak = 0
                else:
                    emotion = "CRISIS"  # ยังอยู่ใน crisis
            else:
                self._positive_streak = 0
                self.current = emotion
        else:
            self._positive_streak = 0
            self.current = emotion

        self._log.append({
            "ts":      time.time(),
            "emotion": self.current,
            "text":    text[:120],
        })
        return self.current

    @property
    def trajectory(self) -> str:
        p, c = self.prev, self.current
        neg = {"CRISIS", "SAD", "STRESSED", "LONELY"}
        pos = {"JOY", "LOVE", "WORK_WIN"}
        if p == "CRISIS" and c in neg - {"CRISIS"}:
            return "RECOVERING"
        if p in neg and c in pos:
            return "IMPROVING"
        if p in pos | {"NEUTRAL"} and c in neg:
            return "WORSENING"
        return "STABLE"

    def context_note(self) -> str:
        """inject เข้า LLM context"""
        parts = [f"EMOTION:{self.current}"]
        if self.prev != self.current:
            parts.append(f"prev:{self.prev}")
        t = self.trajectory
        if t != "STABLE":
            parts.append(f"trend:{t}")
        guide = _RESPONSE_GUIDE.get(self.current, "")
        if guide:
            parts.append(guide)
        return " | ".join(parts)

    def reset(self):
        self._log.clear()
        self.current = "NEUTRAL"
        self.prev    = "NEUTRAL"
        self._positive_streak = 0


# ── State ต่อ session (จำกัดจำนวน กันหน่วยความจำโตไม่หยุด) ─────────
_MAX_SESSIONS = 5000
_sessions: "OrderedDict[str, EmotionState]" = OrderedDict()
_lock = threading.Lock()

def get_emotion_state(session_id: str = "default") -> EmotionState:
    with _lock:
        es = _sessions.get(session_id)
        if es is None:
            es = _sessions[session_id] = EmotionState()
            while len(_sessions) > _MAX_SESSIONS:
                _sessions.popitem(last=False)
        else:
            _sessions.move_to_end(session_id)
        return es

def clear_emotion_state(session_id: str = "default") -> None:
    with _lock:
        _sessions.pop(session_id, None)

