BIASES = {
    "loss_aversion":  0.7,
    "overconfidence": 0.4,
    "status_quo_bias": 0.6,
    "panic_bias":     0.2
}


def apply_bias(decision_score, context="normal"):

    try:
        score = float(decision_score)
    except (TypeError, ValueError):
        score = 0.0

    if context == "loss":
        score *= (1 - BIASES["loss_aversion"])

    if context == "panic":
        score *= (1 - BIASES["panic_bias"])

    if context == "overconfident":
        score *= (1 - BIASES["overconfidence"])

    if context == "familiar":
        score *= (1 - BIASES["status_quo_bias"])

    return max(0.0, round(score, 4))


def detect_bias_context(text):

    # เดิม "เสีย" "หาย" "ไม่ได้" "เคย" "เดิม" อยู่แทบทุกประโยค (หายใจ/เสียงดัง/ทำไม่ได้) → วลีที่บอก bias จริง
    t = str(text or "").lower()

    if any(w in t for w in ["กลัวเสีย", "เสียดาย", "ไม่อยากเสีย", "กลัวหาย", "กลัวขาดทุน"]):
        return "loss"

    if any(w in t for w in ["ตื่นตระหนก", "ด่วน", "เร็วๆ", "รีบ"]):
        return "panic"

    if any(w in t for w in ["แน่ใจ", "ชัวร์", "แน่นอน"]):
        return "overconfident"

    if any(w in t for w in ["แบบเดิม", "เหมือนเดิม", "เคยชิน", "เหมือนเก่า"]):
        return "familiar"

    return "normal"
