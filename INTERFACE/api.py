"""
INTERFACE/api.py — KING DIADEM v2.0
Secondary API entry point (backup / mobile / CLI access)

ความแตกต่างจาก app.py:
- ไม่มี Google OAuth
- ไม่มี Stripe
- ใช้ api_key header แทน cookie session
- เหมาะกับ mobile_node / CLI / external integration

Wire: king_diadem_core v2.0 ครบทุก engine
Author: Nithikorn Bunsrang
"""

import os
from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ── KING DIADEM CORE v2 ───────────────────────────────────────────
try:
    from core.king_diadem_core import (
        quick_assess,
        king_diadem_decision,
        core_status,
    )
    _CORE_OK = True
except Exception as _e:
    print(f"⚠ king_diadem_core: {_e}")
    _CORE_OK = False
    def quick_assess(c, p): return {"peace": True, "should_pause": False}
    def king_diadem_decision(**kw): return {"status": "fallback"}
    def core_status(): return {}

# ── DECISION ENGINE ───────────────────────────────────────────────
try:
    from ENGINE.decision_engine import run_decision
    _DECISION_OK = True
except Exception as _e:
    print(f"⚠ decision_engine: {_e}")
    _DECISION_OK = False
    def run_decision(body): return {"error": "decision_engine not loaded"}

# ── DATABASE / CREDITS ────────────────────────────────────────────
try:
    from DATABASE.credit_store import use_credit, get_credits
    _CREDITS_OK = True
except Exception:
    _CREDITS_OK = False
    def get_credits(k): return 999
    def use_credit(k): pass

# ── PAYMENT ───────────────────────────────────────────────────────
try:
    from PAYMENT.create_checkout import create_checkout
    from PAYMENT.stripe_webhook import handle_webhook
    _PAYMENT_OK = True
except Exception:
    _PAYMENT_OK = False
    def create_checkout(k): return ""
    def handle_webhook(p, s): return "disabled"

# ── COSMIC LATTE CANON ────────────────────────────────────────────
try:
    from core.cosmic_latte_canon import evaluate_task
    _CANON_OK = True
except Exception:
    _CANON_OK = False
    def evaluate_task(t): return {"canon_aligned": True, "violations": []}

# ── LLM ───────────────────────────────────────────────────────────
try:
    from core.llm_gemini import get_llm
    _llm = get_llm()
    _LLM_OK = True
except Exception:
    _LLM_OK = False
    _llm = None

print(f"""
✅ INTERFACE/api.py v2.0
   core       : {'✅' if _CORE_OK    else '⚠'}
   decision   : {'✅' if _DECISION_OK else '⚠'}
   credits    : {'✅' if _CREDITS_OK  else '⚠'}
   payment    : {'✅' if _PAYMENT_OK  else '⚠'}
   canon      : {'✅' if _CANON_OK    else '⚠'}
   llm        : {'✅' if _LLM_OK      else '⚠'}
""")

# ══════════════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════════════
app = FastAPI(title="KING DIADEM API", version="2.0")

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# ── HELPERS ───────────────────────────────────────────────────────
def _check_credits(api_key: str) -> int:
    credits = get_credits(api_key)
    if credits <= 0:
        raise HTTPException(status_code=402, detail="No credits remaining")
    return credits

def _friendly_error(err: str) -> str:
    e = str(err).lower()
    if "quota" in e or "429" in e:
        return "ถึงขีดจำกัดชั่วคราว — ลองใหม่ในอีกสักครู่"
    if "503" in e or "unavailable" in e:
        return "ระบบ AI ยุ่งอยู่ชั่วคราว — ลองใหม่อีกครั้ง"
    return "ระบบไม่พร้อมชั่วคราว — ลองใหม่อีกครั้ง"


# ══════════════════════════════════════════════════════════════════
# ROUTES
# ══════════════════════════════════════════════════════════════════

@app.get("/", response_class=HTMLResponse)
async def home():
    for path in ["static/index.html", "INTERFACE/index.html"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>KING DIADEM API v2.0</h1>"


@app.get("/health")
async def health():
    return {
        "status":     "alive 👑",
        "version":    "api-v2.0",
        "core":       core_status(),
        "llm":        _LLM_OK,
        "decision":   _DECISION_OK,
        "credits":    _CREDITS_OK,
        "canon":      _CANON_OK,
    }


# ── /decision — protected by api_key + credits ────────────────────
@app.post("/decision")
async def decision(
    request: Request,
    api_key: str = Header(...),
):
    body    = await request.json()
    credits = _check_credits(api_key)

    user_input = str(body.get("input", "")).strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="input required")

    # ── bodhipakkhiya channel ────────────────────────────────────
    pattern = {
        "entropy":   float(body.get("risk",   40)),
        "stability": float(body.get("food",   60)),
        "resource":  float(body.get("money",  50)),
        "input":     user_input,
    }
    core_result = quick_assess(user_input, pattern)

    # ── canon check ───────────────────────────────────────────────
    canon = evaluate_task({"description": user_input})

    # ── run decision ──────────────────────────────────────────────
    result = run_decision({**body, "input": user_input})

    # ── deduct credit ─────────────────────────────────────────────
    use_credit(api_key)

    return {
        "decision":          result,
        "credits_left":      credits - 1,
        "bodhipakkhiya":     core_result.get("bodhi_verdict", ""),
        "peace":             core_result.get("peace", True),
        "canon_aligned":     canon.get("canon_aligned", True),
        "canon_violations":  canon.get("violations", []),
    }


# ── /run — main chat endpoint (no credit gate — ใช้ cookie ใน app.py) ──
@app.post("/run")
async def run(request: Request):
    body       = await request.json()
    user_input = str(body.get("input", "")).strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="input required")

    route      = body.get("route", "general")
    voice_mode = body.get("voice_mode", "lyla")
    history    = body.get("history", [])
    context    = body.get("context", {})
    user_email = body.get("user_email") or body.get("email", "")

    # ── bodhipakkhiya channel ────────────────────────────────────
    pattern = {
        "entropy":   float(context.get("entropy",   40)),
        "stability": float(context.get("stability", 60)),
        "resource":  float(context.get("resource",  50)),
        "input":     user_input,
    }
    core_result = quick_assess(user_input, pattern)

    if core_result.get("recommend_route") and route not in ("vega",):
        route = core_result["recommend_route"]

    # ── run decision ──────────────────────────────────────────────
    result = run_decision({
        "input":      user_input,
        "route":      route,
        "voice_mode": voice_mode,
        "history":    history,
        "user_email": user_email,
        "context":    context,
    })

    if isinstance(result, dict) and result.get("error"):
        result["error"] = _friendly_error(str(result["error"]))

    # ── attach core data ──────────────────────────────────────────
    if isinstance(result, dict):
        result["bodhipakkhiya"] = core_result.get("bodhi_verdict", "")
        result["peace"]         = core_result.get("peace", True)
        result["causal_ctx"]    = core_result.get("causal_ctx", "")

    return result


# ── /simulate ────────────────────────────────────────────────────
@app.post("/simulate")
async def simulate(request: Request):
    body       = await request.json()
    user_input = str(body.get("input", "")).strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="input required")

    result = run_decision({
        "input":      user_input,
        "paths":      body.get("paths", []),
        "mode":       "simulate",
        "user_email": body.get("user_email", ""),
    })
    return result


# ── /assess — quick assess ด้วย core เท่านั้น (ไม่รัน LLM) ─────────
@app.post("/assess")
async def assess(request: Request):
    """
    ตรวจสอบ bodhipakkhiya + canon alignment โดยไม่เสีย credit
    ใช้สำหรับ mobile_node / GLOBAL_NODE sync
    """
    body       = await request.json()
    user_input = str(body.get("input", "")).strip()
    pattern    = {
        "entropy":   float(body.get("entropy",   40)),
        "stability": float(body.get("stability", 60)),
        "resource":  float(body.get("resource",  50)),
        "input":     user_input,
    }

    core_result = quick_assess(user_input, pattern)
    canon       = evaluate_task({"description": user_input})

    return {
        "peace":            core_result.get("peace", True),
        "should_pause":     core_result.get("should_pause", False),
        "recommend_route":  core_result.get("recommend_route"),
        "drift_alert":      core_result.get("drift_alert", False),
        "bodhi_verdict":    core_result.get("bodhi_verdict", ""),
        "canon_aligned":    canon.get("canon_aligned", True),
        "canon_violations": canon.get("violations", []),
        "causal_ctx":       core_result.get("causal_ctx", ""),
        "wise_ctx":         core_result.get("wise_ctx", ""),
    }


# ── /system ───────────────────────────────────────────────────────
@app.get("/system")
async def system():
    return {
        "status":   "running",
        "version":  "2.0",
        "engine":   "online" if _DECISION_OK else "fallback",
        "payments": "enabled" if _PAYMENT_OK else "disabled",
        "credits":  "active"  if _CREDITS_OK else "disabled",
        "core":     core_status(),
    }


# ── /me ───────────────────────────────────────────────────────────
@app.get("/me")
async def me(request: Request):
    return {"logged_in": False, "premium": False, "email": None,
            "note": "use app.py for full auth with Google OAuth"}


# ── /api/chat-state ───────────────────────────────────────────────
@app.get("/api/chat-state")
async def get_chat_state(request: Request):
    return {"state": None}

@app.put("/api/chat-state")
async def put_chat_state(request: Request):
    return {"ok": True}


# ── /buy ──────────────────────────────────────────────────────────
@app.get("/buy")
async def buy(api_key: str = Header(...)):
    if not _PAYMENT_OK:
        raise HTTPException(status_code=503, detail="Payment not configured")
    url = create_checkout(api_key)
    return {"checkout_url": url}


# ── /stripe/webhook ───────────────────────────────────────────────
@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):
    if not _PAYMENT_OK:
        raise HTTPException(status_code=503, detail="Payment not configured")
    payload    = await request.body()
    sig_header = request.headers.get("stripe-signature")
    if not sig_header:
        raise HTTPException(status_code=400, detail="Missing Stripe signature")
    result = handle_webhook(payload, sig_header)
    return {"status": result}


# ── /wallet ───────────────────────────────────────────────────────
@app.post("/wallet/topup")
async def wallet_topup(request: Request):
    body   = await request.json()
    email  = str(body.get("email", "")).strip()
    amount = float(body.get("amount", 0))
    if not email:
        raise HTTPException(status_code=400, detail="email required")
    if amount < 10:
        raise HTTPException(status_code=400, detail="minimum 10 THB")
    current   = get_credits(email)
    added     = int(amount)
    new_total = current + added
    return {"total_credit": new_total, "added": added}

@app.get("/wallet/balance")
async def wallet_balance_get(request: Request):
    email   = request.query_params.get("email", "")
    credits = get_credits(email) if email else 0
    return {"total_credit": credits, "email": email}

@app.post("/wallet/balance")
async def wallet_balance_post(request: Request):
    body    = await request.json()
    email   = body.get("email", "")
    credits = get_credits(email) if email else 0
    return {"total_credit": credits, "email": email}
