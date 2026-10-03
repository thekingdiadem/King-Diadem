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

    # ── think() อยู่ใน ENGINE/brain.py (dicision.py มีแค่ build_reply)
    try:
        from ENGINE.brain import think
    except Exception as e:
        return {"error": f"decision error: cannot import ENGINE.brain.think ({e})"}

    try:
        result = think(text, mode=mode, session_id=session_id, seed=seed)
    except Exception as e:
        return {"error": f"decision error: {str(e)}"}

    if not isinstance(result, dict):
        result = {"reply": str(result)}
    # เดิมมีขั้น brain.process() / memory.recall() ต่อท้าย แต่ทั้งสองฟังก์ชันไม่มีอยู่จริง
    # (ล้มเงียบใน except ทุกครั้ง) — think() บันทึก history ผ่าน ENGINE.memory ให้แล้ว
    return result
