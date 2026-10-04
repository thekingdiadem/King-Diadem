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
    d = domain.lower().strip() if isinstance(domain, str) else ""
    context = context if isinstance(context, dict) else {}

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
    scored = []   # (waterline, domain) — เดิมหา lowest_domain จาก index ของ waterlines
                  # ซึ่งเพี้ยนเมื่อมี domain ที่ไม่คืน waterline

    for d in (domains if isinstance(domains, (list, tuple)) else []):
        if not isinstance(d, str):
            continue
        r = route_domain(d, context)
        results[d] = r
        if r.get("error"):
            continue   # unknown domain คืน waterline 50 ปลอม — ไม่นับรวม
        try:
            scored.append((float(r.get("waterline")), d))
        except (TypeError, ValueError):
            pass

    lowest = min(scored) if scored else None

    return {
        "domains":            results,
        "combined_waterline": round(lowest[0], 1) if lowest else 50.0,
        "lowest_domain":      lowest[1] if lowest else None,
    }
