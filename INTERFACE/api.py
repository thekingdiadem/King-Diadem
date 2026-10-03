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
# ใช้ ledger จริงเดียวกับ app.py (DATABASE/db.py) — เดิมใช้ credit_store คนละตาราง
# และถ้าโหลดไม่ได้ fallback เป็น get_credits = 999 / use_credit = ไม่หัก (ใช้ฟรีไม่จำกัด)
try:
    from DATABASE.db import spend_credit, get_credits, add_credits
    _CREDITS_OK = True
except Exception:
    _CREDITS_OK = False
    def get_credits(k): return 0
    def spend_credit(*a, **k): return False
    def add_credits(*a, **k): return None

# ── API KEY → ตัวตน ───────────────────────────────────────────────
# เดิม header api_key เป็นสตริงอะไรก็ได้ แล้วใช้เป็นตัวตนตรงๆ (ใส่อีเมลคนอื่น = ใช้เครดิตคนอื่น)
try:
    from core.api_keys import validate_api_key
except Exception:
    validate_api_key = None

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
MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "4000"))


def _auth(api_key: str, permission: str) -> str:
    """ตรวจ API key (HMAC + scope + rate limit) → อีเมลเจ้าของ key"""
    if not validate_api_key:
        raise HTTPException(status_code=503, detail="API key system unavailable")
    info = validate_api_key(api_key, required_permission=permission)
    if not info.get("valid"):
        raise HTTPException(status_code=401, detail=info.get("reason", "invalid api key"))
    return info["email"]


def _charge(email: str, what: str) -> None:
    """หักก่อนเรียก LLM แบบ atomic — เดิมเช็คยอดก่อนแล้วค่อยหักหลังรัน (ยิงพร้อมกันได้เกินยอด)"""
    if not _CREDITS_OK or not spend_credit(email, 1, what):
        raise HTTPException(status_code=402, detail="No credits remaining")


def _refund(email: str, what: str) -> None:
    try:
        add_credits(email, 1, "refund", what)
    except Exception:
        pass


def _input(body: dict) -> str:
    text = str(body.get("input", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="input required")
    if len(text) > MAX_INPUT_CHARS:
        raise HTTPException(status_code=413, detail="input too long")
    return text


def _ctx_num(d: dict, k: str, default: float) -> float:
    try:
        return float(d.get(k, default))
    except (TypeError, ValueError):
        return default

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
    body    = body if isinstance(body, dict) else {}
    email   = _auth(api_key, "decision")
    user_input = _input(body)
    _charge(email, "api_decision")

    # ── bodhipakkhiya channel ────────────────────────────────────
    pattern = {
        "entropy":   _ctx_num(body, "risk",  40),
        "stability": _ctx_num(body, "food",  60),
        "resource":  _ctx_num(body, "money", 50),
        "input":     user_input,
    }
    core_result = quick_assess(user_input, pattern)

    # ── canon check ───────────────────────────────────────────────
    canon = evaluate_task({"description": user_input})

    # ── run decision ──────────────────────────────────────────────
    # ตัวตน/session มาจาก key เท่านั้น — ไม่เชื่อ user_email/session_id ใน body
    result = run_decision({**body, "input": user_input, "raw_input": user_input,
                           "user_email": email, "session_id": email})
    if not isinstance(result, dict) or result.get("error"):
        _refund(email, "api_decision")

    return {
        "decision":          result,
        "credits_left":      get_credits(email),
        "bodhipakkhiya":     core_result.get("bodhi_verdict", ""),
        "peace":             core_result.get("peace", True),
        "canon_aligned":     canon.get("canon_aligned", True),
        "canon_violations":  canon.get("violations", []),
    }


# ── /run — main chat endpoint (no credit gate — ใช้ cookie ใน app.py) ──
@app.post("/run")
async def run(request: Request, api_key: str = Header(...)):
    # เดิมไม่มีการยืนยันตัวตน + รับ user_email จาก body → ดึง memory ของอีเมลใครก็ได้เข้า prompt
    # และใช้ LLM ฟรีไม่จำกัด
    body       = await request.json()
    body       = body if isinstance(body, dict) else {}
    email      = _auth(api_key, "run")
    user_input = _input(body)
    _charge(email, "api_run")

    route      = body.get("route", "general")
    voice_mode = body.get("voice_mode", "lyla")
    history    = body.get("history") if isinstance(body.get("history"), list) else []
    context    = body.get("context") if isinstance(body.get("context"), dict) else {}
    user_email = email

    # ── bodhipakkhiya channel ────────────────────────────────────
    pattern = {
        "entropy":   _ctx_num(context, "entropy",   40),
        "stability": _ctx_num(context, "stability", 60),
        "resource":  _ctx_num(context, "resource",  50),
        "input":     user_input,
    }
    core_result = quick_assess(user_input, pattern)

    if core_result.get("recommend_route") and route not in ("vega",):
        route = core_result["recommend_route"]

    # ── run decision ──────────────────────────────────────────────
    result = run_decision({
        "input":      user_input,
        "raw_input":  user_input,
        "route":      route,
        "voice_mode": voice_mode,
        "history":    history[-8:],
        "user_email": user_email,
        "session_id": user_email,
        "context":    context,
    })

    if isinstance(result, dict) and result.get("error"):
        _refund(email, "api_run")
        result["error"] = _friendly_error(str(result["error"]))

    # ── attach core data ──────────────────────────────────────────
    if isinstance(result, dict):
        result["bodhipakkhiya"] = core_result.get("bodhi_verdict", "")
        result["peace"]         = core_result.get("peace", True)
        result["causal_ctx"]    = core_result.get("causal_ctx", "")

    return result


# ── /simulate ────────────────────────────────────────────────────
@app.post("/simulate")
async def simulate(request: Request, api_key: str = Header(...)):
    body       = await request.json()
    body       = body if isinstance(body, dict) else {}
    email      = _auth(api_key, "simulate")
    user_input = _input(body)
    _charge(email, "api_simulate")

    paths = body.get("paths") if isinstance(body.get("paths"), list) else []
    result = run_decision({
        "input":      user_input,
        "raw_input":  user_input,
        "paths":      [str(p)[:300] for p in paths][:7],
        "mode":       "simulate",
        "user_email": email,
        "session_id": email,
    })
    if not isinstance(result, dict) or result.get("error"):
        _refund(email, "api_simulate")
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
    body       = body if isinstance(body, dict) else {}
    pattern    = {
        "entropy":   _ctx_num(body, "entropy",   40),
        "stability": _ctx_num(body, "stability", 60),
        "resource":  _ctx_num(body, "resource",  50),
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
    # เดิมส่ง api_key เป็น "email" ให้ create_checkout (ผิด signature → อีเมลไม่ถูกต้องทุกครั้ง)
    email = _auth(api_key, "run")
    result = create_checkout(email)
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return {"checkout_url": result.get("url") if isinstance(result, dict) else result}


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
    # เดิมตอบ "เติมแล้ว" พร้อมยอดใหม่โดยไม่มีการจ่ายเงินและไม่ได้เติมจริง — หลอกผู้ใช้
    # การเติมเงินจริงต้องผ่าน Stripe ของแอปหลัก (/wallet/topup ใน app.py)
    raise HTTPException(status_code=501, detail="top-up is available in the main app only")

@app.get("/wallet/balance")
async def wallet_balance_get(request: Request, api_key: str = Header(...)):
    # เดิมดูยอดของอีเมลใดก็ได้จาก query — ตอนนี้ดูได้เฉพาะของเจ้าของ key
    email = _auth(api_key, "report_read")
    return {"total_credit": get_credits(email), "email": email}

@app.post("/wallet/balance")
async def wallet_balance_post(request: Request, api_key: str = Header(...)):
    email = _auth(api_key, "report_read")
    return {"total_credit": get_credits(email), "email": email}
