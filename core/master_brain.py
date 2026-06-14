"""
core/master_brain.py
KING DIADEM — Master Brain (v2)

ของเดิม run_system() เรียก 6 ฟังก์ชันที่ไม่มีอยู่จริงในระบบ:
  load_world_state(), analyze_human(), analyze_risk(input_data, world, human),
  simulate_outcome(), make_decision(), update_world()
→ ถ้า run จะ NameError ทันที (dead code)

ไฟล์นี้ wire ใหม่ ใช้แต่ฟังก์ชันที่มีจริงและ import ได้จริง:
  - ENGINE.language_detector.detect_language
  - ENGINE.human_state_engine.analyze_human_state / evaluate_human_state
  - ENGINE.risk_engine.analyze_risk
  - ENGINE.collapse_predictor.predict_collapse
  - ENGINE.intervention_engine.intervention
  - ENGINE.persona_engine.resolve_persona
  - core.memory_store.log_decision

⚠️ ยังไม่ wire (เพราะไฟล์ที่ import ต่อยังไม่มี/ไม่ได้ส่งมา):
  - ENGINE.decision_engine.run_decision()
      ต้องการ SIMULATIONS.scenario_tree.simulate_paths  (ไม่มีไฟล์นี้)
  - ENGINE.future_simulator.forecast()
      ต้องการ ENGINE.world_model.build_world_state       (ไม่มีไฟล์นี้)
  - ENGINE.dialogue_engine.generate_reply()
      ต้องการ WORLD_MODEL.human_behavior                 (ไม่มีไฟล์นี้)

ถ้าจะเปิดใช้ 3 ตัวนี้ ส่งไฟล์ที่ขาดมา แล้วค่อย wire เพิ่ม
"""

from ENGINE.language_detector import detect_language
from ENGINE.human_state_engine import analyze_human_state, evaluate_human_state
from ENGINE.risk_engine import analyze_risk
from ENGINE.collapse_predictor import predict_collapse
from ENGINE.intervention_engine import intervention
from ENGINE.persona_engine import resolve_persona
from core.memory_store import log_decision


# world_state เริ่มต้น — ใช้เมื่อ caller ไม่ได้ส่ง state มา
# (สำคัญ: ห้ามใช้ mutable default ที่ค้างข้าม request — ใช้ dict literal ใหม่ทุกครั้ง)
DEFAULT_WORLD_STATE = {
    "entropy": 10,
    "resource": 80,
    "stability": 60,
    "drift": 0,
    "choices": 2,
}


def run_system(input_data: dict, user: str = "anonymous") -> dict:
    """
    Pipeline จริงต่อ 1 request:

      1. ตรวจภาษา
      2. วิเคราะห์สัญญาณมนุษย์จากข้อความ (depression/fear/dependency/violence)
      3. คำนวณ risk จาก world_state ของ "เทิร์นนี้เท่านั้น"
         (รับจาก input_data['world_state'] ถ้ามี ไม่งั้นใช้ DEFAULT_WORLD_STATE
         → กัน state ค้างจากเทิร์นก่อนทับ route ของเทิร์นใหม่)
      4. ทำนาย collapse + เลือก intervention
      5. ตัดสิน route + persona
      6. log decision

    input_data ตัวอย่าง:
      {
        "message": "...",
        "food": 5,
        "money": 100,
        "risk": 0,
        "world_state": {"entropy": 10, "resource": 80, "stability": 60, "drift": 0, "choices": 2}
      }
    """

    if not isinstance(input_data, dict):
        input_data = {}

    text = str(input_data.get("message", "") or "")

    # 1. ภาษา
    lang = detect_language(text)

    # 2. สัญญาณมนุษย์ — มาจากข้อความ
    human_flags = analyze_human_state(text)

    food = input_data.get("food", 5)
    money = input_data.get("money", 100)
    risk_input = input_data.get("risk", 0)
    human_score = evaluate_human_state(food, money, risk_input)

    # 3. world state ของเทิร์นนี้ (ไม่ persist ข้าม request โดยอัตโนมัติ)
    world_state = {**DEFAULT_WORLD_STATE, **(input_data.get("world_state") or {})}
    risk = analyze_risk(world_state)

    # 4. collapse + intervention
    collapse = predict_collapse(risk["risk_score"])

    if risk["level"] == "CRITICAL":
        risk_state = "critical"
    elif risk["level"] == "HIGH":
        risk_state = "unstable"
    else:
        risk_state = "stable"

    action = intervention(risk_state)

    # 5. route + persona
    #    - violence_risk / depression → crisis เสมอ (ไม่ขึ้นกับ risk_score)
    #    - ไม่งั้นใช้ decision_level จาก risk_engine
    if human_flags.get("violence_risk") or human_flags.get("depression"):
        route = "crisis"
    elif risk["decision_level"] in ("HIGH", "MEDIUM"):
        route = "risk"
    else:
        route = "general"

    persona = resolve_persona(route=route, voice_mode="lyla")

    decision = {
        "language": lang,
        "human_flags": human_flags,
        "human_score": human_score,
        "risk": risk,
        "collapse": collapse,
        "intervention": action,
        "route": route,
        "persona": persona["name"],
        "signature": persona["signature"],
    }

    # 6. log
    log_decision({"user": user, "input": input_data, "result": decision})

    return decision
