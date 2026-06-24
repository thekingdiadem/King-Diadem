# DOMAINS/domain_router.py
# KING DIADEM — Domain Router
# route_domain() ส่ง context ไปยัง engine ที่ถูกต้อง

from DOMAINS.life_engine     import analyze_life
from DOMAINS.business_engine import analyze_business
from DOMAINS.survival_engine import analyze_survival
from DOMAINS.world_engine    import analyze_world
from DOMAINS.human_engine    import analyze_human

AVAILABLE_DOMAINS = ["life", "business", "survival", "world", "human"]


def route_domain(domain: str, context: dict) -> dict:
    """
    ส่ง context ไป domain engine ที่ตรงกัน
    return dict พร้อม waterline, risk, advice เสมอ
    """
    d = domain.lower().strip()

    if d == "life":
        return analyze_life(context)

    if d == "business":
        return analyze_business(context)

    if d == "survival":
        return analyze_survival(context)

    if d == "world":
        return analyze_world(context)

    if d == "human":
        return analyze_human(context)

    return {
        "error":             "unknown_domain",
        "requested":         domain,
        "available_domains": AVAILABLE_DOMAINS,
        "waterline":         50.0,
    }


def route_multi(domains: list, context: dict) -> dict:
    """
    วิเคราะห์หลาย domain พร้อมกัน — return combined waterline
    เช่น route_multi(["survival","business"], context)
    """
    results = {}
    waterlines = []

    for d in domains:
        r = route_domain(d, context)
        results[d] = r
        wl = r.get("waterline")
        if wl is not None:
            waterlines.append(float(wl))

    combined_waterline = min(waterlines) if waterlines else 50.0

    return {
        "domains":            results,
        "combined_waterline": round(combined_waterline, 1),
        "lowest_domain":      domains[waterlines.index(min(waterlines))] if waterlines else None,
    }
