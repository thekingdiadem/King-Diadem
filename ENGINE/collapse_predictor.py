# ENGINE/collapse_predictor.py
# KING DIADEM Collapse Predictor
#
# v2 — เพิ่ม analyze(pattern) ให้ตรงกับที่
#       DecisionEngine._run_route() เรียก:
#         from ENGINE.collapse_predictor import analyze
#         return analyze(pattern)
#       เดิมมีแค่ predict_collapse(risk_score) → import error ทุกครั้ง
#       ที่ route="collapse" (กรณี engine_router โหลดไม่ได้)

def predict_collapse(risk_score):

    if risk_score > 80:
        return "high collapse probability"

    if risk_score > 60:
        return "moderate collapse probability"

    return "low collapse probability"


def analyze(pattern: dict) -> dict:
    """
    Wrapper ให้ DecisionEngine._run_route() เรียกได้ตรง ๆ
    pattern: dict จาก analyze_pattern() — มี entropy/resource/stability
    """
    if not isinstance(pattern, dict):
        pattern = {}

    entropy  = float(pattern.get("entropy",  40))
    resource = float(pattern.get("resource", 50))

    # risk_score scale 0-100 (สูตรเดียวกับ emptiness_guard)
    risk_score = entropy * 0.5 + (100.0 - resource) * 0.5

    probability = predict_collapse(risk_score)

    return {
        "route":       "collapse",
        "risk_score":  risk_score,
        "probability": probability,
        "status":      "pass_to_llm",
    }
