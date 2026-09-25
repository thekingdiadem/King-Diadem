# core/system_orchestrator.py
# KING DIADEM — System Orchestrator v4.0
# แก้: analyze_chain → analyze | assess_risk(3args) → assess(dict) | CollapsePredictor → analyze
# เพิ่ม: run_with_survivor_engine คืน survivor_context ให้ app.py ครบ

from typing import Dict, Any, Optional


class SystemOrchestrator:

    def route(self, user_input: str, voice_mode: str = "lyla") -> str:
        t = (user_input or "").lower()
        if any(w in t for w in ["อยากตาย","ไม่อยากอยู่","ฆ่าตัว","จบชีวิต","suicid"]) or voice_mode == "crisis":
            return "crisis"
        if any(w in t for w in ["ระยะยาว","อนาคต","กลยุทธ์","strategic","ภาพรวม"]) or voice_mode == "vega":
            return "vega"
        if any(w in t for w in ["เครียด","ท้อ","เสียใจ","หมดหวัง","เหนื่อย","กลัว","ร้องไห้","โดดเดี่ยว"]):
            return "vega"
        if any(w in t for w in ["ไม่มีกิน","ไม่มีเงิน","หิว","หมดเงิน","ตกงาน","จน","หนี้"]):
            return "survival"
        if any(w in t for w in ["เสี่ยง","อันตราย","ล้มละลาย","พัง","collapse","ขาดทุน"]):
            return "risk"
        if any(w in t for w in ["แฟน","เลิก","ทะเลาะ","ครอบครัว","ความสัมพันธ์"]):
            return "relationship"
        if any(w in t for w in ["ธุรกิจ","บริษัท","ลูกค้า","โปรเจกต์","เจ้านาย"]):
            return "civil"
        return "general"

    def _resolve_persona(self, route: str, voice_mode: str) -> str:
        if voice_mode == "crisis" or route == "crisis":
            return "lyla"
        if voice_mode == "vega" or route == "vega":
            return "vega"
        return "lyla"

    def _paticcasamuppada(self, text: str) -> str:
        # FIX: ชื่อจริงคือ analyze() ไม่ใช่ analyze_chain()
        try:
            from ENGINE.paticcasamuppada_engine import analyze
            r = analyze({"input": text})
            if isinstance(r, dict):
                parts = []
                root    = r.get("root_cause", "")
                summary = r.get("summary", "")
                nirvana = r.get("nirvana_mode", False)
                uap     = r.get("uap", {})
                if root:     parts.append(f"ต้นเหตุ: {root}")
                if nirvana:  parts.append("chain ดับที่เวทนา")
                elif summary: parts.append(summary)
                if uap.get("should_pause"): parts.append("UAP: หยุดก่อนตัดสินใจ")
                if parts:
                    return f"[ปฏิจสมุปบาท — {' | '.join(parts)}]"
        except Exception:
            pass
        return "[โยนิโสมนสิการ: วิเคราะห์ต้นเหตุและลูกโซ่ผลกระทบก่อนตอบ]"

    def _living_water(self, text: str) -> bool:
        try:
            from AI_KERNEL.living_water import detect_leak
            return detect_leak(text)
        except Exception:
            return False

    def _cosmic_latte(self, text: str) -> str:
        try:
            from AI_KERNEL.cosmic_latte import get_context
            r = get_context(text)
            return f"[COSMIC_LATTE] {r}" if r else ""
        except Exception:
            return ""

    def execute(self, route: str, data: Dict[str, Any]) -> Dict[str, Any]:
        user_input = data.get("input", "")
        context    = data.get("context", {})
        voice_mode = data.get("voice_mode", "lyla")
        persona    = self._resolve_persona(route, voice_mode)

        result = {
            "route":            route,
            "persona":          persona.upper(),
            "voice_mode":       persona,
            "context_for_lyla": "",
            "pattern":          {"entropy": 40, "stability": 60, "resource": 50},
            "risk_score":       10.0,
            "can_decide":       True,
            "waterline":        70.0,
            "flags":            [],
            "ai_response":      None,
        }
        ctx_parts = []

        # 1. ปฏิจสมุปบาท
        paticca = self._paticcasamuppada(user_input)
        if paticca:
            ctx_parts.append(paticca)

        # 2. Cosmic Latte
        latte = self._cosmic_latte(user_input)
        if latte:
            ctx_parts.append(latte)

        # 3. Living Water
        if self._living_water(user_input) and route not in ("crisis", "vega"):
            ctx_parts.append("[LIVING_WATER: emotional signal — รับรู้ก่อนวิเคราะห์]")

        # 4. RealHuman SurvivorEngine
        try:
            from ENGINE.realhuman_survivorengine import RealHumanSurvivorEngine, parse_state_from_context
            h_state  = parse_state_from_context(context or {})
            survival = RealHumanSurvivorEngine().run(h_state)
            result["waterline"]  = survival.waterline
            result["can_decide"] = survival.can_decide
            result["flags"]      = survival.flags
            if survival.context_for_lyla:
                ctx_parts.append(survival.context_for_lyla)
        except Exception as e:
            ctx_parts.append(f"[SURVIVOR_SKIP: {e}]")

        # 5. Route engines
        if route == "survival":
            try:
                from ENGINE.survival_advisor import advise
                r = advise(data)
                if r: ctx_parts.append(f"[SURVIVAL] {r}")
            except Exception as e:
                ctx_parts.append(f"[SURVIVAL_SKIP: {e}]")

        elif route == "risk":
            try:
                # FIX: assess(dict) ไม่ใช่ assess_risk(energy, food, safe)
                from ENGINE.risk_engine import assess
                r = assess(context.get("state", result["pattern"]))
                if isinstance(r, dict) and r.get("level"):
                    ctx_parts.append(f"[RISK: {r['level']} score={r.get('risk_score',0):.0f}]")
                    result["risk_score"] = float(r.get("risk_score", 10))
            except Exception as e:
                ctx_parts.append(f"[RISK_SKIP: {e}]")
            try:
                # FIX: analyze(pattern) ไม่ใช่ CollapsePredictor().predict()
                from ENGINE.collapse_predictor import analyze as collapse_analyze
                col = collapse_analyze(result["pattern"])
                if isinstance(col, dict) and col.get("collapse_level"):
                    ctx_parts.append(f"[COLLAPSE: {col['collapse_level']} prob={col.get('probability',0):.0%}]")
            except Exception as e:
                ctx_parts.append(f"[COLLAPSE_SKIP: {e}]")

        elif route in ("vega", "crisis"):
            try:
                from core.vega_mode import vega_mode_hint
                hint = vega_mode_hint(user_input)
                if hint: ctx_parts.append(hint)
            except Exception:
                if route == "vega":
                    ctx_parts.append("[VEGA: strategic analysis — มองภาพใหญ่ระยะยาว]")

        elif route == "relationship":
            ctx_parts.append("[RELATIONSHIP] เรื่องความสัมพันธ์ — ฟังก่อน ไม่ตัดสิน")

        elif route == "civil":
            try:
                from ENGINE.strategy_planner import plan
                strat = plan(result["pattern"])
                if isinstance(strat, dict) and strat.get("options"):
                    opts = strat["options"][:3]
                    ctx_parts.append(f"[STRATEGY] {' | '.join(str(o) for o in opts)}")
            except Exception as e:
                ctx_parts.append(f"[STRATEGY_SKIP: {e}]")

        else:
            try:
                from ENGINE.pattern_engine import analyze_pattern
                pat = analyze_pattern({"input": user_input})
                if isinstance(pat, dict):
                    result["pattern"].update({k: v for k, v in pat.items() if v is not None})
            except Exception:
                pass

        # 6. Parables
        try:
            from core.parables import parable_context_note
            p = parable_context_note(user_input)
            if p: ctx_parts.append(p)
        except Exception:
            pass

        # 7. Escape routes
        if result["risk_score"] > 55 or not result["can_decide"]:
            try:
                from ENGINE.escape_routes import assess as escape_assess
                esc = escape_assess(user_input)
                if esc: ctx_parts.append(f"[ESCAPE_ROUTES] {esc}")
            except Exception:
                pass

        result["context_for_lyla"] = "\n".join(p for p in ctx_parts if p)
        return result

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        user_input = data.get("input", "")
        voice_mode = data.get("voice_mode", "lyla")
        route = data.get("route") or "general"
        if route == "general":
            route = self.route(user_input, voice_mode)

        result  = self.execute(route, data)
        persona = result.get("voice_mode", "lyla")

        # _skip_llm: ผู้เรียกต้องการแค่ survivor context (app.py สร้างคำตอบเองอยู่แล้ว)
        # เดิมเรียก LLM ทุกครั้งแล้วคำตอบถูกทิ้ง = เสีย quota 2 เท่าต่อ 1 ข้อความ
        if result.get("ai_response") is None and not data.get("_skip_llm"):
            try:
                from core.llm_gemini import get_llm
                llm = get_llm()  # ★ FIX: ใช้ singleton เดียวกับทั้งระบบ
                                  #   เดิม: GeminiLLM(model="gemini-2.0-flash") — โมเดลนี้ปลดระวางแล้ว (1 มิ.ย. 2026)
                                  #   ทำให้ _call() fail ทุกครั้ง แล้วได้ canned fallback "RISK 45" เสมอ
                result["ai_response"] = llm.generate_with_governance(
                    prompt             = user_input,
                    additional_context = result["context_for_lyla"],
                    history            = data.get("history", []),
                    route              = route,
                    voice_mode         = persona,
                )
            except Exception as e:
                result["ai_response"] = f"[LLM Error: {e}]"

        if result.get("ai_response"):
            try:
                from ENGINE.consensus_engine import build_consensus
                cs = build_consensus({
                    "text":        user_input,
                    "response":    result["ai_response"],
                    "route":       route,
                    "human_state": result.get("pattern", {}),
                })
                if isinstance(cs, dict) and cs.get("consensus"):
                    result["consensus"] = cs["consensus"]
            except Exception:
                pass

        result["route"]    = route
        result["status"]   = "SUCCESS"
        result["observer"] = "KING DIADEM"
        result["persona"]  = "VEGA" if persona == "vega" else "LYLA"
        result["governance"] = {
            "intent":      {"intent": route, "confidence": 0.8},
            "human_state": result.get("pattern", {}),
        }
        return result

    def run_with_survivor_engine(self, user_input: str, human_context: dict = None) -> Dict[str, Any]:
        """app.py เรียกตัวนี้ — normalize output ให้ app.py อ่านได้ตรง"""
        raw = self.run({"input": user_input, "context": human_context or {}, "_skip_llm": True})
        return {
            **raw,
            "survivor_context": raw.get("context_for_lyla", ""),
            "can_decide":       raw.get("can_decide", True),
            "route":            raw.get("route", "general"),
        }


_orchestrator: Optional[SystemOrchestrator] = None

def get_orchestrator() -> SystemOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = SystemOrchestrator()
    return _orchestrator
