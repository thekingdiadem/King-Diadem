# วางไฟล์นี้ที่ ENGINE/eternal_snapshot_patch.py
# แล้ว copy ฟังก์ชันนี้ไปแทนใน ENGINE/decision_engine.py

def eternal_snapshot_for_decision(state: dict) -> dict:
    """
    Non-blocking snapshot — timeout 2s
    ★ FIX: worker ตายเพราะ eternal_runtime block >120s
    """
    import threading
    result = {"skipped": True, "reason": "not_started"}

    def _run():
        try:
            from ENGINE.eternal_runtime import eternal_snapshot
            r = eternal_snapshot(state)
            result.clear()
            result.update(r)
        except Exception as e:
            result["error"] = str(e)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=2.0)   # ★ max 2s — ไม่งั้น worker timeout
    return result
