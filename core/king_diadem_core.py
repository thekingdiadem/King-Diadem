"""
KING DIADEM CORE
Civilization Decision Infrastructure

Architect: Nithikorn Bunsrang
"""

from ENGINE.survival_advisor import survival_advisor
from ENGINE.world_intel import analyze_location
from ENGINE.choice_optimizer import optimize_choice


# =========================
# NORTH PRINCIPLE
# =========================

def north_principle(actions):
    """
    Filter actions based on KING DIADEM core law
    """
    filtered = []

    for action in actions:

        if action["harm_life"] == True:
            continue

        if action["break_ethics"] == True:
            continue

        if action["reality_violation"] == True:
            continue

        filtered.append(action)

    return filtered


# =========================
# CHOICE PRESERVATION
# =========================

def preserve_choice(actions):
    """
    Ensure at least one option always exists
    """
    if len(actions) == 0:

        return [{
            "action": "SYSTEM_PAUSE",
            "reason": "No safe action available. Preserve existence."
        }]

    return actions


# =========================
# DECISION CORE
# =========================

def king_diadem_decision(location, lat, lng, food, money, risk):

    world = analyze_location(lat, lng)

    survival = survival_advisor(food, money, risk)

    actions = survival["recommended_actions"]

    actions = north_principle(actions)

    actions = preserve_choice(actions)

    ranked = optimize_choice(actions)

    best = ranked[0]

    return {
        "system": "KING DIADEM",
        "location": location,
        "zone": world["zone"],
        "survival_score": survival["survival_score"],
        "north_direction": best["action"],
        "alternatives": ranked
    }
