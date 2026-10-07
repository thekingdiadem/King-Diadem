# ENGINE/decision_engine.py
# KING DIADEM — Decision Engine · ระบบที่รันไฟล์ของพี่คิงต้องกลางทุกสรรพสิ่ง 
# v5.3 — wire ENGINE/human_engine.py (entropy-aware) เข้า pattern
#         แก้ RISK 45 ซ้ำทุกครั้ง (entropy/resource เคยใช้ default 40/50 เสมอ)
#         threading timeout 1.5s on eternal_snapshot (แก้ 502) — คงไว้จาก v5.2

import json
import re
import threading

from ENGINE.pattern_engine import analyze_pattern
from core.llm_gemini import get_llm          # ← singleton
from core.emptiness_guard import emptiness_guard

# ── Wisdom Index (พี่คิง 2026-07-04): Wisdom = Outcome Usefully / Spent Energy
try:
    from ENGINE.freedom_signal import wisdom_index as _wisdom_index, snapshot as _wisdom_snapshot
except Exception:
    _wisdom_index = None
    _wisdom_snapshot = None


_ROUTE_SEVERITY = {"stable": 0, "general": 0, "uncertain": 1, "civil": 1, "risk": 2,
                   "survival": 3, "collapse": 4, "crisis": 5}

def _max_route(current: str, candidate: str) -> str:
    return candidate if _ROUTE_SEVERITY.get(candidate, 0) >= _ROUTE_SEVERITY.get(current, 0) else current


class DecisionEngine:

    def __init__(self):
        # ── LLM — ใช้ singleton เดียวกับทั้งระบบ ─────────────
        try:
            self.llm = get_llm()
            print("✅ DecisionEngine: GeminiLLM loaded (singleton)")
        except Exception as e:
            print(f"❌ DecisionEngine: GeminiLLM failed - {e}")
            self.llm = None

        # ── LYLA Kernel ───────────────────────────────────────
        try:
            from core.lyla_kernel import LylaKernel
            self.lyla = LylaKernel()
            print("✅ DecisionEngine: LYLA loaded")
        except Exception:
            self.lyla = None

        # ── UDOK v2.0 — paticcasamuppada ─────────────────────
        try:
            from ENGINE.paticcasamuppada_engine import analyze as paticca_analyze
            self.paticca = paticca_analyze
            print("✅ DecisionEngine: paticcasamuppada UDOK v2.0 loaded")
        except Exception as e:
            print(f"⚠️  DecisionEngine: paticca fallback - {e}")
            self.paticca = None

        # ── Engine Router ─────────────────────────────────────
        try:
            from ENGINE.engine_router import run as router_run
            self.router = router_run
            print("✅ DecisionEngine: engine_router loaded")
        except Exception as e:
            print(f"⚠️  DecisionEngine: router fallback - {e}")
            self.router = None

        # ── Core Loop ─────────────────────────────────────────
        try:
            from core.core_loop import run_core
            self.core_loop = run_core
        except Exception:
            self.core_loop = None

    # ══════════════════════════════════════════════════════════
    # MAIN RUN
    # ══════════════════════════════════════════════════════════
    def run(self, data: dict) -> dict:
        user_input = data.get("input") or data.get("text") or ""

        if not user_input:
            return {
                "observer": "KING DIADEM",
                "status":   "ERROR",
                "message":  "ไม่พบ input",
            }

        # ── STEP 0: Emotion State ────────────────────────────
        session_id = str(data.get("session_id") or data.get("user_email") or "default")
        emotion_ctx = "EMOTION:NEUTRAL"
        try:
            from ENGINE.emotion_state import get_emotion_state
            es = get_emotion_state(session_id)
            es.update(str(data.get("raw_input") or user_input))   # ข้อความดิบของผู้ใช้ ไม่ใช่ prompt ที่ต่อบริบทแล้ว
            emotion_ctx = es.context_note()
        except Exception:
            pass

        # ── STEP 1: Pattern Analysis ─────────────────────────
        # data ตอนนี้มี entropy/resource/stability จริงแล้ว
        # (ถ้า ENGINE/human_engine.py คำนวณได้ — ดู run_decision())
        pattern = analyze_pattern(data, session_id)   # เดิมไม่ส่ง → ทุกคนแชร์ tracker "default"
        route   = pattern.get("route", "general")

        # ── STEP 1.5: Human Engine override ──────────────────
        # ถ้า RealHumanSurvivorEngine บอกว่า "ยังไม่ควรตัดสินใจใหญ่"
        # บังคับ route ไป survival (ยกเว้นอยู่ใน vega/crisis อยู่แล้ว)
        human_engine_result = data.get("_human_engine")
        if (
            isinstance(human_engine_result, dict)
            and human_engine_result.get("can_decide") is False
            and route not in ("vega", "crisis")
        ):
            route = "survival"

        # ── STEP 2: Emptiness Guard ──────────────────────────
        guarded = emptiness_guard(pattern)

        if guarded.get("blocked") and guarded.get("reason") in (
            "CHOICE_COLLAPSE", "KERNEL_IMPORT_FAIL", "invalid_state"
        ):
            collapse = guarded.get("reason") == "CHOICE_COLLAPSE"
            return {
                "observer":    "KING DIADEM",
                "route":       "BLOCKED",
                "reason":      guarded.get("reason", "GUARD_BLOCK"),
                "action":      "stabilize",
                "status":      "BLOCKED",
                # ทางเลือกเหลือศูนย์ = คนกำลังลำบากจริง ไม่ใช่ "ระบบมีปัญหา" — ให้ทางช่วยเหลือทันที
                "ai_response": (
                    "ตอนนี้ยังไม่ต้องตัดสินใจอะไรใหญ่ค่ะ ขอให้อยู่ในที่ปลอดภัยก่อน "
                    "ถ้ารู้สึกไม่ไหว โทร 1323 (สายด่วนสุขภาพจิต 24 ชม.) หรือ 1669 ได้เลย "
                    "— ยังมีทางเสมอ Choice(t) ≥ 1"
                ) if collapse else "ระบบพบปัญหาภายใน กรุณาลองใหม่อีกครั้งครับ",
                "risk_score":  guarded.get("risk_score", 0),
                "persona":     "LYLA",
                "pattern": {
                    "entropy":   pattern.get("entropy"),
                    "resource":  pattern.get("resource"),
                    "stability": pattern.get("stability"),
                },
            }

        if guarded.get("emotional_flag") or guarded.get("suggested_route") == "vega":
            route = "vega"
        elif guarded.get("forced_action") == "stabilize":
            if route not in ("survival", "collapse", "vega"):
                route = "survival"

        # ── STEP 3: Persona / Voice Mode ─────────────────────
        raw_vm = str(data.get("voice_mode") or "lyla").lower()
        if   route == "crisis" or raw_vm == "crisis": voice_mode = "crisis"
        elif raw_vm == "council":                      voice_mode = "council"   # สภา 6 เสียง
        elif route == "vega"   or raw_vm == "vega":   voice_mode = "vega"
        else:                                          voice_mode = "lyla"

        persona = {"vega": "VEGA", "council": "COUNCIL"}.get(voice_mode, "LYLA")

        # ── STEP 4: Core Loop ────────────────────────────────
        core_result = None
        if self.core_loop:
            try:
                core_result = self.core_loop({
                    "entropy":   pattern.get("entropy",   40),
                    "resource":  pattern.get("resource",  50),
                    "stability": pattern.get("stability", 60),
                    "drift":     0,
                })
                if core_result.get("status") == "HALT" and route != "vega":
                    route = "survival"
            except Exception:
                pass

        # ── STEP 5: UDOK v2.0 — paticcasamuppada ─────────────
        paticca_result = None
        if self.paticca:
            try:
                paticca_result = self.paticca(pattern)
            except Exception:
                pass

        if paticca_result:
            if paticca_result.get("nirvana_mode") and route not in ("collapse", "crisis", "vega"):
                route = "stable" if route != "survival" else route
            uap = paticca_result.get("uap", {})
            if uap.get("should_pause") and route == "general":
                route = "uncertain"

        # ── STEP 6: Engine Router ────────────────────────────
        router_result = None
        if self.router:
            try:
                router_payload = {
                    **pattern,
                    "input":      user_input,
                    "raw_input":  data.get("raw_input") or "",
                    "voice_mode": voice_mode,
                    "route_hint": route,
                    "paticca":    paticca_result,
                }
                router_result = self.router(router_payload)
                if router_result and router_result.get("route") not in (None, "error"):
                    if voice_mode not in ("vega", "crisis"):
                        # router ยกระดับได้ แต่ห้ามลด — เดิมเขียนทับ "survival" ที่ survivor engine
                        # ตั้งไว้ (เช่นคนที่ไม่มีอาหาร) กลับเป็น "general"
                        route = _max_route(route, router_result["route"])
            except Exception as e:
                router_result = {"error": f"router fail: {e}"}
        else:
            router_result = self._run_route(route, pattern)

        # ── STEP 7: LLM ──────────────────────────────────────
        ai_response = None
        llm_error   = None
        if self.llm:
            try:
                context_parts = [
                    f"Route: {route}",
                    f"Entropy: {pattern.get('entropy')}",
                    f"Resource: {pattern.get('resource')}",
                    f"Stability: {pattern.get('stability')}",
                ]

                if guarded.get("emotional_flag"):
                    context_parts.append("EMOTIONAL_FLAG: true — ผู้ใช้อาจอยู่ในสถานการณ์ยาก")

                # ── Wisdom Index: Outcome Usefully / Spent Energy ────
                if _wisdom_index is not None:
                    try:
                        w = _wisdom_index()
                        if w > 0:
                            tag = "ต่ำกว่า 1 (เสียพลังงานมากกว่าที่ได้ผล)" if w < 1 else "≥ 1 (ได้ผลคุ้มพลังงานที่เสีย)"
                            context_parts.append(f"Wisdom Index: {w:.2f} — {tag}")
                    except Exception:
                        pass

                # ── Human Engine context (entropy-aware) ─────
                # STABLE = ค่าเริ่มต้นเมื่อผู้ใช้ไม่ได้บอกสถานะ — เดิมส่ง "[SURVIVOR ENGINE] สถานะ: STABLE ..."
                # ทุกข้อความ แล้ว LLM ตอบ "รับทราบสถานะของระบบแล้ว" กับคนที่พิมพ์แค่ "ตอบไวดี"
                if isinstance(human_engine_result, dict) and human_engine_result.get("status") != "STABLE":
                    if human_engine_result.get("context_for_lyla"):
                        context_parts.append(human_engine_result["context_for_lyla"])
                    if human_engine_result.get("priority"):
                        context_parts.append(f"Priority: {human_engine_result['priority']}")

                if paticca_result:
                    # ภาษาคน ไม่ใช่ชื่อตัวแปร (root/kill_zone/UAP) — LLM เคยยกไปพูดกับผู้ใช้ตรงๆ
                    try:
                        from ENGINE.paticcasamuppada_engine import llm_note
                        note = llm_note(paticca_result)
                    except Exception:
                        note = ""
                    if note and note not in user_input:
                        context_parts.append(note)

                if router_result:
                    action = router_result.get("action", "")
                    if action:
                        context_parts.append(f"Router action: {action}")

                ai_response = self.llm.generate_with_governance(
                    prompt             = user_input,
                    additional_context = " | ".join(context_parts),
                    history            = data.get("history", []),
                    route              = route,
                    voice_mode         = voice_mode,
                    emotion_state      = emotion_ctx,
                    # ความจำข้ามแชท — อีเมลมาจาก session ของเซิร์ฟเวอร์ (app.py ทับค่าจาก client เสมอ)
                    user_email         = str(data.get("user_email") or ""),
                )
            except Exception as e:
                # เดิมส่ง "[Gemini unavailable: <error>]" เป็นคำตอบให้ผู้ใช้ (หลุดรายละเอียดภายใน
                # และ app.py ไม่รู้ว่าล้ม จึงไม่คืนเครดิต) — ตอนนี้ส่งเป็น error ให้ app จัดการ
                print(f"⚠ DecisionEngine LLM error: {e}")
                ai_response, llm_error = None, "LLM_UNAVAILABLE"

        # ── STEP 8: LYLA Observation ─────────────────────────
        lyla_note = None
        if self.lyla:
            try:
                # ข้อความผู้ใช้จริง — user_input คือ prompt ที่ต่อบริบท/นิทานแล้ว ("พัง" ในนิทาน = CRITICAL)
                lyla_note = self.lyla.observe(str(data.get("raw_input") or user_input))
            except Exception:
                pass

        return {
            "observer":   "KING DIADEM — Decision Engine · กลางทุกสรรพสิ่ง",
            "status":     "SUCCESS",
            "route":      route,
            "persona":    persona,
            "voice_mode": voice_mode,
            # (เดิมส่ง "input" = prompt ภายในทั้งก้อนกลับหน้าเว็บ — เอาออก)
            "pattern": {
                "entropy":    pattern.get("entropy"),
                "resource":   pattern.get("resource"),
                "stability":  pattern.get("stability"),
                "confidence": pattern.get("confidence"),
                "warnings":   pattern.get("warnings", []),
            },
            "human_engine":    human_engine_result,
            "collapse_chain":  paticca_result,
            "engine_result":   router_result,
            "ai_response":     ai_response,
            "core_loop":       core_result,
            "lyla":            lyla_note,
            "risk_score":      guarded.get("risk_score", 0),
            "emotional_flag":  guarded.get("emotional_flag", False),
            "wisdom":          _wisdom_snapshot() if _wisdom_snapshot else None,
            **({"error": llm_error} if llm_error else {}),
        }

    def _run_route(self, route: str, pattern: dict) -> dict:
        try:
            if route == "survival":
                from ENGINE.survival_advisor import advise
                return advise(pattern)
            elif route == "risk":
                from ENGINE.risk_engine import assess
                return assess(pattern)
            elif route == "collapse":
                from ENGINE.collapse_predictor import analyze
                return analyze(pattern)
            elif route == "uncertain":
                from ENGINE.consensus_engine import resolve
                return resolve(pattern)
            elif route == "civil":
                from ENGINE.civil_work_engine import assess
                return assess(pattern)
            elif route in ("vega", "stable"):
                return {"route": route, "status": "pass_to_llm"}
            else:
                from ENGINE.strategy_planner import plan
                return plan(pattern)
        except Exception as e:
            return {"error": f"ENGINE ROUTE FAIL [{route}]: {str(e)}"}


# ══════════════════════════════════════════════════════════════
# SINGLETON + PUBLIC API
# ══════════════════════════════════════════════════════════════
_ENGINE_SINGLETON = None
_ENGINE_LOCK = threading.Lock()

def _engine() -> DecisionEngine:
    global _ENGINE_SINGLETON
    if _ENGINE_SINGLETON is None:
        # BUG FIX v5.4: เดิมเช็ค None แล้วสร้างเลย ไม่มี lock —
        # ถ้า 2 request มาพร้อมกันตอนยังไม่เคย init อาจสร้าง DecisionEngine()
        # 2 ตัวซ้อนกัน (โหลด LLM/router/lyla ซ้ำ เปลือง memory และเวลา)
        with _ENGINE_LOCK:
            if _ENGINE_SINGLETON is None:  # double-check หลังได้ lock
                _ENGINE_SINGLETON = DecisionEngine()
    return _ENGINE_SINGLETON


def _build_payload(data: dict) -> dict:
    out  = dict(data) if isinstance(data, dict) else {}
    text = str(
        out.get("input") or out.get("text") or
        out.get("question") or ""
    ).strip()

    if not text:
        parts = []
        for k, label in [
            ("location", "ที่ตั้ง"), ("food", "อาหาร"),
            ("money",    "เงิน"),    ("risk", "ความเสี่ยง"),
        ]:
            v = out.get(k)
            if v not in (None, "", "unknown"):
                parts.append(f"{label}: {v}")
        text = " | ".join(parts)
    out["input"] = text

    # หมายเหตุ: เดิมคำนวณ resource = 100 − min(money, 99) → ยิ่งมีเงินมาก resource ยิ่งต่ำ (กลับด้าน)
    # และค่านี้ไปบัง resource ที่ถูกต้องจาก human_engine — ตอนนี้ให้ human_engine เป็นคนคำนวณ
    for k in ("entropy", "resource", "stability"):
        if k in out:
            try:
                out[k] = max(0.0, min(100.0, float(out[k])))
            except (TypeError, ValueError):
                out.pop(k)          # ค่าที่ไม่ใช่ตัวเลขจาก client เดิมทำให้ /run ล้ม (500)

    risk_s = str(out.get("risk", "")).lower()
    if any(w in risk_s for w in ["high", "สูง", "critical"]):
        try:
            out["entropy"] = min(95.0, float(out.get("entropy", 40)) + 20.0)
        except (TypeError, ValueError):
            out["entropy"] = 65.0

    return out


# ══════════════════════════════════════════════════════════════
# eternal_snapshot_for_decision — v5.2 FIX (คงไว้)
# threading timeout 1.5s → ป้องกัน eternal_runtime block → 502
# ══════════════════════════════════════════════════════════════
def eternal_snapshot_for_decision(state: dict) -> dict:
    """
    เรียก eternal_snapshot พร้อม timeout 1.5s
    ถ้าช้าเกิน → คืน fallback dict แทน (ไม่ block request)
    """
    result = {}
    error  = {}

    def _run():
        try:
            from ENGINE.eternal_runtime import eternal_snapshot
            result["data"] = eternal_snapshot(state)
        except Exception as e:
            error["msg"] = str(e)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=1.5)

    if t.is_alive():
        # timeout — คืน fallback ทันที ไม่รอ
        print("⚠️  eternal_snapshot timeout (>1.5s) — using fallback")
        return {
            "status":  "TIMEOUT",
            "entropy": state.get("entropy",   40),
            "resource": state.get("resource", 50),
            "stability": state.get("stability", 60),
        }

    if error:
        return {"status": "ERROR", "error": error["msg"]}

    return result.get("data", {"status": "EMPTY"})


def run_decision(data) -> dict:
    if not isinstance(data, dict):
        data = {"input": str(data)}

    merged = _build_payload(data)
    if not (merged.get("input") or "").strip():
        return {
            "observer": "KING DIADEM",
            "status":   "ERROR",
            "message":  "ไม่พบ input",
        }

    # ── v5.3: Human Engine (entropy-aware) ───────────────────
    # วิเคราะห์สถานะมนุษย์จริงจาก context ที่ frontend ส่งมา
    # แล้ว merge entropy/resource/stability เข้า merged
    # (ถ้า frontend ไม่ได้ส่งค่าเหล่านี้มาเอง)
    # ← นี่คือจุดที่แก้ RISK 45 ซ้ำทุกครั้ง
    try:
        from ENGINE.human_engine import analyze_human
        human_ctx = data.get("context") if isinstance(data.get("context"), dict) else {}
        human_result = analyze_human(human_ctx)
        merged["_human_engine"] = human_result
        if isinstance(human_result, dict):
            for k in ("entropy", "resource", "stability"):
                # BUG FIX v5.4: เดิมเช็ค `k not in data` (payload ดิบจาก frontend)
                # ทำให้ resource ที่ _build_payload คำนวณจาก money ไปแล้ว
                # (ผ่าน out.setdefault("resource", ...)) โดน human_engine ทับทิ้งเงียบๆ
                # ทุกครั้งที่ frontend ส่ง "money" มาแทนที่จะส่ง "resource" ตรงๆ
                # ตอนนี้เช็คจาก merged (payload ที่ผ่านการคำนวณแล้ว) แทน
                if k in human_result and k not in merged:
                    merged[k] = human_result[k]
    except Exception:
        merged["_human_engine"] = None

    # ← ตอนนี้ไม่ block แล้ว (timeout 1.5s)
    merged["_eternal_snapshot"] = eternal_snapshot_for_decision({
        "entropy":   float(merged.get("entropy",   40)),
        "resource":  float(merged.get("resource",  50)),
        "stability": float(merged.get("stability", 60)),
    })

    try:
        from ENGINE.self_learning import analyze_patterns
        merged["_learning_patterns"] = analyze_patterns()
    except Exception:
        merged["_learning_patterns"] = None

    return _engine().run(merged)


def decide(input=None, intent=None, risk=None, **kwargs) -> dict:
    chunks = []
    if input  is not None: chunks.append(str(input))
    if intent is not None:
        chunks.append("บริบท: " + (
            json.dumps(intent, ensure_ascii=False)
            if isinstance(intent, dict) else str(intent)
        ))
    if risk is not None:
        chunks.append("ความเสี่ยง: " + (
            json.dumps(risk, ensure_ascii=False)
            if isinstance(risk, dict) else str(risk)
        ))
    for k, v in kwargs.items():
        if v is not None:
            chunks.append(f"{k}: {v}")
    return run_decision({"input": "\n".join(chunks).strip()})


def generate_choices(location, food, money, risk) -> list:
    body = {"input": (
        f"เสนอทางเลือก 3–5 ข้อ สั้น กระชับ "
        f"บริบท: ที่ตั้ง {location} อาหาร {food} เงิน {money} ความเสี่ยง {risk}"
    )}
    out = run_decision(body)
    ai  = out.get("ai_response") or ""
    lines = [
        re.sub(r"^[\d\.\)\-\*•]+\s*", "", s.strip())
        for s in str(ai).splitlines()
        if len(s.strip()) > 3
    ]
    if len(lines) >= 3:
        return lines[:10]
    return [
        "แยกปัญหาเป็น วันนี้ / สัปดาห์นี้ / เดือนนี้ แล้วทำแค่วันนี้ก่อน",
        "หาตัวเลขขั้นต่ำที่ต้องมี แล้วลดรายจ่ายอื่นชั่วคราว",
        "ถ้าเสี่ยงสูง อย่าตัดสินใจถาวรวันนี้ เลือกแค่ปลอดภัยชั่วคราว",
        "ติดต่อคนที่ไว้ใจได้หนึ่งคน ขอให้ช่วยฟังหรือช่วยคิด",
    ]


def decision_intelligence(state: dict, risk: dict) -> dict:
    state = state if isinstance(state, dict) else {}
    risk  = risk  if isinstance(risk,  dict) else {}
    level = str(risk.get("level", "MEDIUM")).upper()

    try:    score = float(risk.get("risk_score", 0))
    except (TypeError, ValueError): score = 0.0
    try:    res   = float(state.get("resource",  50))
    except (TypeError, ValueError): res   = 50.0
    try:    stab  = float(state.get("stability", 60))
    except (TypeError, ValueError): stab  = 60.0

    if level == "CRITICAL" or score >= 85 or res <= 10:
        return {"action": "stabilize",        "message": "ชะลอการตัดสินใจใหญ่ — ดูแลพื้นฐานก่อน"}
    if level == "HIGH"     or score >= 60 or stab < 35:
        return {"action": "stabilize",        "message": "แยกปัญหาเป็นขั้นเล็กๆ แล้วทำทีละขั้น"}
    if res < 30:
        return {"action": "recover_resource", "message": "ทรัพยากรต่ำ — เลือกสิ่งจำเป็นก่อน"}
    if stab < 45:
        return {"action": "expand_choices",   "message": "หาทางเลือกเสริม 2–3 แบบก่อนตัดสินใจ"}
    return     {"action": "maintain",         "message": "ไปต่อได้ — รักษาจังหวะพอประมาณ"}
