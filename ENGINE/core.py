# ENGINE/core.py
# v2 — แก้ 4 อย่าง:
#  1. session_id ไม่ถูกส่งต่อจากผู้เรียก -> ทุก user แชร์ session
#     "default" เดียวกันหมด (history/context cross-talk ข้าม user)
#     -> เพิ่ม param session_id/mode/seed ส่งต่อให้ ENGINE.dicision.think
#  2. return type ไม่คงเส้นคงวา: error path เดิมคืน str,
#     success path คืน dict (จาก think()) -> ทำให้ทุก path คืน dict
#  3. process()/recall() เดิมรับ result (dict) ทั้งก้อน แต่ออกแบบมาให้
#     ทำงานกับ string -> ให้ทำงานกับ result["reply"] แล้ว merge กลับ
#  4. ลบ fallback "from engine.dicision import think" (lowercase,
#     dead code บน case-sensitive filesystem) + bare except -> except Exception

def run_engine(text: str, session_id: str = "default", mode: str = "chat", seed: str = "") -> dict:
    text = (text or "").strip()

    if not text:
        return {
            "reply":      "...",
            "actions":    [],
            "intent":     "empty",
            "risk":       {"score": 0, "level": "low", "pause": False},
            "mode":       mode,
            "session_id": session_id,
        }

    # ── decision (ต้องมี) — ไฟล์จริงชื่อ dicision.py ──────────
    try:
        from ENGINE.dicision import think
    except Exception as e:
        return {"error": f"decision error: cannot import ENGINE.dicision.think ({e})"}

    try:
        result = think(text, mode=mode, session_id=session_id, seed=seed)
    except Exception as e:
        return {"error": f"decision error: {str(e)}"}

    if not isinstance(result, dict):
        result = {"reply": str(result)}

    # ── โมดูลเสริม (มีหรือไม่มีก็ไม่พัง) ──────────────────────
    # ทำงานกับ result["reply"] (string) ไม่ใช่ result ทั้ง dict
    try:
        from ENGINE.brain import process
        new_reply = process(result.get("reply", ""))
        if new_reply:
            result["reply"] = new_reply
    except Exception:
        pass

    try:
        from ENGINE.memory import recall
        new_reply = recall(result.get("reply", ""))
        if new_reply:
            result["reply"] = new_reply
    except Exception:
        pass

    return result
