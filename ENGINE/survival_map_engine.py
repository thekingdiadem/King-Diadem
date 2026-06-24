# ENGINE/survival_map_engine.py
"""
KING DIADEM — Survival Map Engine
Build complete survival picture: nodes + escape routes + waterline
"""
from __future__ import annotations
from typing import Optional

from ENGINE.survival_nodes import find_survival_nodes

try:
    from ENGINE.escape_routes import generate_escape_routes
    _ESCAPE_LOADED = True
except ImportError:
    _ESCAPE_LOADED = False

try:
    from ENGINE.intervention_engine import intervene
    _INTERVENTION_LOADED = True
except ImportError:
    _INTERVENTION_LOADED = False


def build_survival_map(
    lat:     float,
    lng:     float,
    context: Optional[dict] = None,
) -> dict:
    """
    Full survival picture สำหรับ lat/lng
    context: {money, food, energy, risk_score, vehicle}
    """
    ctx = context or {}

    # Node scan
    nodes = find_survival_nodes(lat, lng)

    # Escape routes
    if _ESCAPE_LOADED:
        risk_score = float(ctx.get("risk_score", 50))
        routes = generate_escape_routes(
            location={"lat": lat, "lng": lng},
            risk=risk_score / 10,  # normalize 0-10
            context=ctx,
        )
    else:
        routes = {
            "status":  "escape_engine_unavailable",
            "note":    "ประเมินเส้นทางออกด้วยตัวเอง — หาถนนหลักที่ใกล้ที่สุด",
            "maps_url": f"https://www.google.com/maps/dir/{lat},{lng}/",
        }

    # Intervention assessment
    intervention = None
    if _INTERVENTION_LOADED:
        money  = float(ctx.get("money",  100))
        food   = float(ctx.get("food",   3))
        energy = float(ctx.get("energy", 50))
        risk   = float(ctx.get("risk_score", 50))

        if risk >= 75 or money < 50 or food <= 1:
            risk_level = "critical"
        elif risk >= 50 or money < 200 or food <= 2:
            risk_level = "unstable"
        else:
            risk_level = "moderate"

        intervention = intervene(risk_level, ctx)

    # Waterline composite
    node_ok     = nodes.get("choice_exists", False)
    route_ok    = isinstance(routes, dict) and routes.get("status") != "escape_engine_unavailable"
    waterline   = 70 if (node_ok and route_ok) else 40 if node_ok else 20

    return {
        "lat":          lat,
        "lng":          lng,
        "nodes":        nodes,
        "escape_routes":routes,
        "intervention": intervention,
        "waterline":    waterline,
        "status":       "STABLE" if waterline >= 55 else "WARNING" if waterline >= 30 else "CRITICAL",
        "axiom":        "Choice(t) ≥ 1 → collapse = False",
    }
