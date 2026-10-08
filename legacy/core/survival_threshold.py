# core/survival_threshold.py
# Layer 0 Law: Choice(t) >= 1 → collapse = False

class SurvivalThreshold:
    MINIMUM_CHOICES = 1  # ถ้า viable paths < 1 → intervention required
