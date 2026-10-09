# core/system_orchestrator.py
# KING DIADEM — System Orchestrator v4.0
# แก้: analyze_chain → analyze | assess_risk(3args) → assess(dict) | CollapsePredictor → analyze
# เพิ่ม: run_with_survivor_engine คืน survivor_context ให้ app.py ครบ

from typing import Dict, Any, Optional

from core.thai_signals import NOT_WANT_TO_LIVE, NO_MONEY_ESSENTIAL, DISCOURAGED, BREAKUP, PARTNER, has as _has


class SystemOrchestrator:

    def route(self, user_input: str, voice_mode: str = "lyla") -> str:
        t = str(user_input or "").lower()
        if any(_has(t, w) for w in ["อยากตาย",NOT_WANT_TO_LIVE,"ฆ่าตัว","จบชีวิต","suicid"]) or voice_mode == "crisis":
            return "crisis"
        if any(w in t for w in ["ระยะยาว","อนาคต","กลยุทธ์","strategic","ภาพรวม"]) or voice_mode == "vega":
            return "vega"
        # อารมณ์เศร้า/เหนื่อย/กลัว → LYLA รับรู้ก่อน (เดิมส่งไป VEGA ซึ่งห้าม emoji และเน้นวิเคราะห์)
        if any(_has(t, w) for w in ["เครียด",DISCOURAGED,"เสียใจ","หมดหวัง","เหนื่อย","กลัว","ร้องไห้","โดดเดี่ยว"]):
            return "general"
        # เดิมมี "จน" (ติด "จนกว่า" "จนถึง") และ "หิว" (ติด "หิวข้าว") → ประโยคทั่วไปเป็น survival
        if any(_has(t, w) for w in ["ไม่มีกิน",NO_MONEY_ESSENTIAL,"อดข้าว","หมดเงิน","ตกงาน","ยากจน","หนี้"]):
            return "survival"
        if any(w in t for w in ["เสี่ยง","อันตราย","ล้มละลาย","พังหมด","collapse","ขาดทุน"]):
            return "risk"
        if any(_has(t, w) for w in [PARTNER,BREAKUP,"ทะเลาะ","ครอบครัว","ความสัมพันธ์"]):
            return "relationship"
        if any(w in t for w in ["ธุรกิจ","บริษัท","ลูกค้า","โปรเจกต์","เจ้านาย"]):
            return "civil"
        return "general"

    def _resolve_persona(self, route: str, voice_mode: str, locked: bool = False) -> str:
        # ผู้ใช้เลือกเสียงเอง (ปุ่ม LYLA/VEGA หรือเรียกชื่อ) → ห้ามสลับตามเส้นทาง
        if locked and voice_mode in ("lyla", "vega"):
            return voice_mode
        if voice_mode == "crisis" or route == "crisis":
            return "lyla"
        if voice_mode == "vega" or route == "vega":
            return "vega"
        return "lyla"

    def _paticcasamuppada(self, text: str) -> str:
        # FIX: ชื่อจริงคือ analyze() ไม่ใช่ analyze_chain()
        try:
            from ENGINE.paticcasamuppada_engine import analyze, llm_note
            # เดิมส่ง "ต้นเหตุ: craving | วงจรวิ่งถึง decay_suffering | UAP: ..." แล้ว LLM ยกไปพูดกับผู้ใช้
            note = llm_note(analyze({"input": text}))
            if note:
                return note
        except Exception:
            pass
        # เดิมคืน "[โยนิโสมนสิการ: วิเคราะห์ต้นเหตุ...]" เมื่อไม่มีสัญญาณ → "ตอบไวดี" ก็ถูกสั่งให้วิเคราะห์ต้นเหตุ
        return ""

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
        data       = data if isinstance(data, dict) else {}
        user_input = str(data.get("input", "") or "")
        context    = data.get("context") if isinstance(data.get("context"), dict) else {}
        voice_mode = data.get("voice_mode", "lyla")
        persona    = self._resolve_persona(route, voice_mode, bool(data.get("voice_locked")))

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
            # STABLE = ค่าเริ่มต้น (ไม่ได้บอกสถานะ) — ไม่ส่ง ไม่งั้น LLM คิดว่าผู้ใช้ส่งรายงานสถานะมา
            if survival.context_for_lyla and survival.status != "STABLE":
                ctx_parts.append(survival.context_for_lyla)
        except Exception:
            pass

        # 5. Route engines
        if route == "survival":
            try:
                from ENGINE.survival_advisor import advise
                r = advise(data)
                if r: ctx_parts.append(f"[SURVIVAL] {r}")
            except Exception:
                pass

        elif route == "risk":
            try:
                # FIX: assess(dict) ไม่ใช่ assess_risk(energy, food, safe)
                from ENGINE.risk_engine import assess
                st = context.get("state")
                r = assess({**(st if isinstance(st, dict) else result["pattern"]), "raw_input": user_input})
                if isinstance(r, dict) and r.get("level"):
                    ctx_parts.append(f"[RISK: {r['level']} score={r.get('risk_score',0):.0f}]")
                    result["risk_score"] = float(r.get("risk_score", 10))
            except Exception:
                pass
            try:
                # FIX: analyze(pattern) ไม่ใช่ CollapsePredictor().predict()
                from ENGINE.collapse_predictor import analyze as collapse_analyze
                col = collapse_analyze(result["pattern"])
                if isinstance(col, dict) and col.get("collapse_level"):
                    ctx_parts.append(f"[COLLAPSE: {col['collapse_level']} prob={col.get('probability',0):.0%}]")
            except Exception:
                pass

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
            except Exception:
                pass

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
        # เดิม import assess ที่ไม่มีใน escape_routes → ล้มเงียบทุกครั้ง ไม่เคยเติมเส้นทางออกเลย
        if result["risk_score"] > 55 or not result["can_decide"]:
            try:
                from ENGINE.escape_routes import generate_escape_routes
                esc = generate_escape_routes(risk=result["risk_score"] / 10.0, context=context)
                labels = [r.get("label") for r in (esc or [])[:3] if isinstance(r, dict) and r.get("label")]
                if labels:
                    ctx_parts.append(f"[ESCAPE_ROUTES] {' | '.join(labels)}")
            except Exception:
                pass

        result["context_for_lyla"] = "\n".join(p for p in ctx_parts if p)
        return result

    def run(self, data: Dict[str, Any]) -> Dict[str, Any]:
        data = data if isinstance(data, dict) else {}
        user_input = data.get("input", "")
        voice_mode = data.get("voice_mode", "lyla")
        route = data.get("route") or "general"
        if route == "general":
            # จัดเส้นทางจากข้อความที่ผู้ใช้พิมพ์จริง — "input" มีบริบทที่ระบบต่อเพิ่ม (คำอย่าง "อนาคต" ในบริบทเคยพาไป VEGA)
            route = self.route(data.get("raw_input") or user_input, voice_mode)

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
            except Exception:
                result["ai_response"] = None      # ไม่ส่งข้อความ error ภายใน (key/โควตา) ให้ผู้ใช้

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
