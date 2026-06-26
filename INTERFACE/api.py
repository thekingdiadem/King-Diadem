import os

from fastapi import FastAPI, Request, Header, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

# ENGINE
from ENGINE.decision_engine import run_decision

# DATABASE
from DATABASE.credit_store import use_credit, get_credits

# PAYMENT (โฟลเดอร์จริงชื่อ PAYMENT)
from PAYMENT.create_checkout import create_checkout
from PAYMENT.stripe_webhook import handle_webhook


# =========================
# APP
# =========================

app = FastAPI(title="KING DIADEM")


# =========================
# STATIC FILES
# =========================

if os.path.exists("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")


# =========================
# HOME
# =========================

@app.get("/", response_class=HTMLResponse)
async def home():
    # Try static/index.html first (main app), fallback to INTERFACE/dashboard.html
    for path in ["static/index.html", "INTERFACE/dashboard.html", "INTERFACE/index.html"]:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
    return "<h1>KING DIADEM</h1>"


# =========================
# SYSTEM STATUS
# =========================

@app.get("/system")
async def system():

    return {
        "status": "running",
        "engine": "online",
        "payments": "enabled",
        "credits": "active"
    }


# =========================
# DECISION ENGINE
# =========================

@app.post("/decision")
async def decision(
    request: Request,
    api_key: str = Header(...)
):

    body = await request.json()

    credits = get_credits(api_key)

    if credits <= 0:
        raise HTTPException(
            status_code=402,
            detail="No credits"
        )

    use_credit(api_key)

    result = run_decision(body)

    return {
        "decision": result,
        "credits_left": credits - 1
    }


# =========================
# BUY CREDITS
# =========================

@app.get("/buy")
async def buy(
    api_key: str = Header(...)
):

    url = create_checkout(api_key)

    return {
        "checkout_url": url
    }


# =========================
# STRIPE WEBHOOK
# =========================

@app.post("/stripe/webhook")
async def stripe_webhook(request: Request):

    payload = await request.body()

    sig_header = request.headers.get("stripe-signature")

    if sig_header is None:
        raise HTTPException(
            status_code=400,
            detail="Missing Stripe signature"
        )

    result = handle_webhook(payload, sig_header)

    return {
        "status": result
    }

# =========================
# /run — main chat endpoint (called by index.html)
# =========================

@app.post("/run")
async def run(request: Request):

    body = await request.json()
    user_input = body.get("input", "")
    history = body.get("history", [])
    route = body.get("route", "general")
    voice_mode = body.get("voice_mode", "lyla")
    user_email = body.get("user_email") or body.get("email")
    context = body.get("context", {})

    if not user_input:
        raise HTTPException(status_code=400, detail="input required")

    result = run_decision({
        "input": user_input,
        "route": route,
        "voice_mode": voice_mode,
        "history": history,
        "user_email": user_email,
        "context": context,
    })

    return result


# =========================
# /simulate — future path simulation (called by Tools tab)
# =========================

@app.post("/simulate")
async def simulate(request: Request):

    body = await request.json()
    user_input = body.get("input", "")
    paths = body.get("paths", [])
    user_email = body.get("user_email") or body.get("email")

    if not user_input:
        raise HTTPException(status_code=400, detail="input required")

    result = run_decision({
        "input": user_input,
        "paths": paths,
        "mode": "simulate",
        "user_email": user_email,
    })

    return result


# =========================
# /me — auth status check
# =========================

@app.get("/me")
async def me(request: Request):
    # Extend with real session/JWT later
    return {"logged_in": False, "premium": False, "email": None}


# =========================
# /api/chat-state — cloud chat sync
# =========================

@app.get("/api/chat-state")
async def get_chat_state(request: Request):
    return {"state": None}

@app.put("/api/chat-state")
async def put_chat_state(request: Request):
    return {"ok": True}


# =========================
# /wallet/topup — credit top-up
# =========================

@app.post("/wallet/topup")
async def wallet_topup(request: Request):

    body = await request.json()
    email = body.get("email", "").strip()
    amount = float(body.get("amount", 0))

    if not email:
        raise HTTPException(status_code=400, detail="email required")
    if amount < 10:
        raise HTTPException(status_code=400, detail="minimum 10 THB")

    current = get_credits(email)
    # 1 credit = 1 THB for now
    added = int(amount)
    new_total = current + added

    return {"total_credit": new_total, "added": added}


@app.get("/wallet/balance")
async def wallet_balance_get(request: Request):
    email = request.query_params.get("email", "")
    credits = get_credits(email) if email else 0
    return {"total_credit": credits, "email": email}

@app.post("/wallet/balance")
async def wallet_balance_post(request: Request):
    body = await request.json()
    email = body.get("email", "")
    credits = get_credits(email) if email else 0
    return {"total_credit": credits, "email": email}
