# =========================
# 👑 KING DIADEM — app.py v4.9
# LYLA (หญิง/ค่ะ) · VEGA (ชาย/ครับ)
# โพธิปักขิยธรรม 37 · ปฏิจสมุปบาท · โยนิโสมนสิการ · สุญยตา
# Fail less. Harm less. Restore more.
#
# PATCH v4.9
# - king_diadem_core v2.0 wired: quick_assess() แทน _paticcasamuppada_context()
# - bodhipakkhiya_engine: 6-layer channel ก่อน LLM ทุกครั้ง
# - cosmic_latte_canon: validate_output() gate ก่อน return
# - wise_ctx inject เข้า LLM prompt
# - LYLA tone: น่ารัก เข้าอกเข้าใจ ไม่เทศ
# =========================

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
import os, json, stripe, math, time, threading
from urllib.parse import quote, unquote

# ── ENGINE ────────────────────────────────────────────────────────
try:
    from ENGINE.decision_engine import DecisionEngine, run_decision as full_run_decision
except Exception as e:
    print(f"⚠ DecisionEngine: {e}")
    DecisionEngine = None
    full_run_decision = None

try:
    from ENGINE.human_engine import analyze_human
except Exception:
    analyze_human = None

try:
    from ENGINE.collapse_predictor import predict_collapse
except Exception as e:
    print(f"⚠ collapse_predictor: {e}")
    predict_collapse = None

try:
    from ENGINE.consensus_engine import build_consensus
except Exception as e:
    print(f"⚠ consensus_engine: {e}")
    build_consensus = None

try:
    from ENGINE.simulation_engine import simulate
except Exception as e:
    print(f"⚠ simulation_engine: {e}")
    simulate = None

try:
    from ENGINE.risk_engine import assess as assess_risk
except Exception as e:
    print(f"⚠ risk_engine: {e}")
    assess_risk = None

try:
    from ENGINE.realhuman_survivorengine import (
        RealHumanSurvivorEngine,
        parse_state_from_context,
    )
    _survivor_engine = RealHumanSurvivorEngine()

    def survivor_analyze(text, context):
        state = parse_state_from_context(context or {})
        out   = _survivor_engine.run(state)
        return {
            "context":    out.context_for_lyla,
            "can_decide": out.can_decide,
            "status":     out.status,
            "route":      "survival" if not out.can_decide else "general",
        }
except Exception as e:
    print(f"⚠ survivor_engine: {e}")
    survivor_analyze = None

try:
    from ENGINE.universal_engine import run_engine as _universal_run
    print("✅ Universal engine loaded")
except Exception as e:
    print(f"⚠ universal_engine: {e}")
    _universal_run = None

try:
    from AI.intent_engine import analyze_intent
    from AI.freedom_signal import record_question, freedom_index, record_choice, record_crisis
except Exception as e:
    print(f"⚠ AI MODULE: {e}")
    analyze_intent = record_question = freedom_index = None
    record_choice  = record_crisis = None

# ── KING DIADEM CORE v2.0 — v4.9 ─────────────────────────────────
try:
    from king_diadem_core import quick_assess, king_diadem_decision, core_status
    print("✅ king_diadem_core v2.0 loaded")
    _CORE_OK = True
except Exception as e:
    print(f"⚠ king_diadem_core: {e}")
    _CORE_OK = False
    def quick_assess(context, pattern):
        return {
            "peace": True, "causal_ctx": "", "wise_ctx": "",
            "recommend_route": None, "should_pause": False,
            "bodhi_verdict": "", "drift_alert": False,
            "bodhi_structure": 0.5,
        }
    def core_status(): return {"core_version": "fallback"}
    king_diadem_decision = None

# ── COSMIC LATTE CANON — v4.9 ─────────────────────────────────────
try:
    from core.cosmic_latte_canon import validate_output as canon_validate, evaluate_task
    print("✅ Cosmic Latte Canon loaded")
    _CANON_OK = True
except Exception as e:
    print(f"⚠ cosmic_latte_canon: {e}")
    _CANON_OK = False
    def canon_validate(result): return result
    def evaluate_task(t): return {"canon_aligned": True, "violations": []}

# ── CORE ──────────────────────────────────────────────────────────
try:
    from core.llm_gemini import get_llm
    from core.lyla_kernel import LylaKernel
    lyla = LylaKernel()
    llm  = get_llm()
    print("✅ LYLA & Gemini loaded")
except Exception as e:
    print(f"⚠ LLM/LYLA: {e}")
    llm = lyla = None

try:
    from core.system_orchestrator import get_orchestrator
    orchestrator = get_orchestrator()
    print("✅ Orchestrator loaded")
except Exception as e:
    print(f"⚠ Orchestrator: {e}")
    orchestrator = None

# ── DATABASE ──────────────────────────────────────────────────────
try:
    from DATABASE.db import (
        init_db, log_decision, get_credits, add_credits,
        ensure_user, save_chat_state, load_chat_state,
    )
    init_db()
    print("✅ Database initialized")
except Exception as e:
    print(f"⚠ DB: {e}")
    init_db = log_decision = get_credits = add_credits = None
    ensure_user = save_chat_state = load_chat_state = None

# ── REPORT ENGINE ─────────────────────────────────────────────────
try:
    from report_engine import create_report as _create_report, get_report as _get_report
    print("✅ Report engine loaded")
except Exception as e:
    print(f"⚠ report_engine: {e}")
    _create_report = _get_report = None

# ── CIVILIZATION ──────────────────────────────────────────────────
try:
    from AI.planetary_dashboard import planetary_status
    from AI.civilization_learning import record_learning, get_learning
    from AI.civilization_engine import add_node, get_nodes
    print("✅ Civilization loaded")
except Exception as e:
    print(f"⚠ CIVILIZATION: {e}")
    planetary_status = get_learning = get_nodes = None
    record_learning  = add_node = None

# ── BELIEF CORE — v4.8 ────────────────────────────────────────────
try:
    from AI_KERNEL.belief_core import (
        audit as belief_audit,
        enforce as belief_enforce,
        get_belief_audit,
    )
    print("✅ Belief core loaded")
except Exception as e:
    print(f"⚠ belief_core: {e}")
    belief_audit = belief_enforce = get_belief_audit = None

# ── GOOGLE OAUTH ──────────────────────────────────────────────────
try:
    from authlib.integrations.starlette_client import OAuth
    oauth = OAuth()
    oauth.register(
        name="google",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
        client_kwargs={"scope": "openid email profile"},
    )
    print("✅ Google OAuth loaded")
except Exception as e:
    print(f"⚠ OAuth: {e}")
    oauth = None

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ── APP ───────────────────────────────────────────────────────────
# SECURITY: SECRET_KEY ต้องตั้งจาก environment เท่านั้น — ห้ามมี default
# ค่า default เดิม "king-diadem-secret-2026" เคยอยู่ใน public repo git history
# ถ้าใครเดา/ดึงค่านั้นได้ = ปลอม session cookie ได้ทันที
_SECRET_KEY = os.getenv("SECRET_KEY")
if not _SECRET_KEY:
    raise RuntimeError(
        "❌ SECRET_KEY environment variable ไม่ได้ตั้งค่า — "
        "ห้าม deploy โดยไม่มี SECRET_KEY (ห้ามใช้ default ที่เคยฝังใน public repo). "
        "ตั้งค่าใน Render environment ก่อน: SECRET_KEY=<random 32+ chars>"
    )

app = FastAPI(title="KING DIADEM OS")
app.add_middleware(
    SessionMiddleware,
    secret_key=_SECRET_KEY
)
engine = DecisionEngine() if DecisionEngine else None
app.mount("/static", StaticFiles(directory="static"), name="static")


# ══════════════════════════════════════════════════════════════════
# ERROR MESSAGE HELPER
# ══════════════════════════════════════════════════════════════════
def _friendly_error(err: str) -> str:
    e = str(err).lower()
    if "403" in e or "permission_denied" in e or "permission denied" in e:
        return "ระบบ AI ไม่มีสิทธิ์เข้าถึงตอนนี้ — ลองใหม่อีกครั้งนะคะ"
    if "503" in e or "unavailable" in e or "high demand" in e:
        return "AI ยุ่งอยู่ชั่วคราว — รอสักครู่แล้วลองใหม่ได้เลยค่ะ"
    if "429" in e or "quota" in e or "rate limit" in e:
        return "ถึงขีดจำกัดชั่วคราว — รอสักครู่แล้วลองอีกทีนะคะ"
    if "404" in e or "not found" in e or "not supported" in e:
        return "โมเดล AI ไม่พร้อม — ระบบกำลังสลับไปใช้ตัวสำรองค่ะ"
    if "auth" in e or "api_key" in e or "api key" in e:
        return "กำลังตรวจสอบ API — ลองใหม่อีกครั้งนะคะ"
    if "timeout" in e or "timed out" in e:
        return "การเชื่อมต่อหมดเวลา — ลองใหม่ได้เลยค่ะ"
    return "ระบบไม่พร้อมชั่วคราว — ลองใหม่อีกครั้งนะคะ"


# ══════════════════════════════════════════════════════════════════
# GALAXY STATE
# ══════════════════════════════════════════════════════════════════
_glock = threading.Lock()
_gstate = {
    "active_route": "general",
    "lyla_mode":    "idle",
    "risk_score":   0.0,
    "entropy":      40.0,
    "stability":    60.0,
    "resource":     50.0,
    "last_updated": 0,
}

_PLANETS = {
    "general":  {"orbit": 95,  "period": 0.241},
    "risk":     {"orbit": 138, "period": 0.615},
    "survival": {"orbit": 145, "period": 1.000},
    "collapse": {"orbit": 188, "period": 1.881},
    "civil":    {"orbit": 238, "period": 11.86},
    "vega":     {"orbit": 292, "period": 29.46},
}

def _planet_positions():
    now, BASE = time.time(), 0.000055
    nodes = []
    for role, p in _PLANETS.items():
        angle = (now * BASE / p["period"] * 1000) % (2 * math.pi)
        nodes.append({
            "role":   role,
            "angle":  round(angle, 4),
            "orbit":  p["orbit"],
            "active": role == _gstate["active_route"],
        })
    return nodes

def _sync_galaxy(result: dict):
    try:
        with _glock:
            _gstate["active_route"] = result.get("route", "general")
            _gstate["risk_score"]   = float(result.get("risk_score", 0))
            _gstate["lyla_mode"]    = "burst" if result.get("ai_response") else "idle"
            _gstate["last_updated"] = int(time.time() * 1000)
            pat = result.get("pattern", {})
            if pat:
                _gstate["entropy"]   = float(pat.get("entropy",   40))
                _gstate["stability"] = float(pat.get("stability", 60))
                _gstate["resource"]  = float(pat.get("resource",  50))
    except Exception:
        pass


@app.get("/api/galaxy/nodes")
def galaxy_nodes():
    with _glock:
        return {
            "ok":           True,
            "active_route": _gstate["active_route"],
            "lyla_mode":    _gstate["lyla_mode"],
            "risk_score":   _gstate["risk_score"],
            "waterline": {
                "entropy":   _gstate["entropy"],
                "stability": _gstate["stability"],
                "resource":  _gstate["resource"],
            },
            "nodes": _planet_positions(),
            "ts":    int(time.time() * 1000),
        }


@app.post("/api/galaxy/signal")
async def galaxy_signal(data: dict):
    route = str(data.get("route", "general")).lower()
    mode  = str(data.get("lyla_mode", "idle")).lower()
    if route not in _PLANETS:
        return JSONResponse({"ok": False, "error": "unknown route"}, status_code=400)
    with _glock:
        _gstate["active_route"] = route
        _gstate["lyla_mode"]    = mode
        _gstate["last_updated"] = int(time.time() * 1000)
    return {"ok": True, "active_route": route, "lyla_mode": mode}


@app.get("/api/galaxy/state")
def galaxy_state_debug():
    with _glock:
        return {**_gstate, "nodes": _planet_positions()}


# ── PAGES ─────────────────────────────────────────────────────────
@app.get("/")
@app.head("/")
def root():
    return FileResponse("static/index.html")

@app.get("/favicon.ico")
def favicon():
    return FileResponse("static/logo.png")

@app.get("/wallet")
async def wallet_page():
    return FileResponse("static/wallet.html")

@app.get("/guide")
async def guide_page():
    return FileResponse("static/guide.html")

@app.get("/ask")
async def ask_page():
    return FileResponse("static/ask.html")


# ── HEALTH ────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status":             "alive 👑",
        "version":            "4.9",
        "llm_loaded":         llm is not None,
        "engine_loaded":      engine is not None,
        "lyla_loaded":        lyla is not None,
        "universal_engine":   _universal_run is not None,
        "collapse_predictor": predict_collapse is not None,
        "consensus_engine":   build_consensus is not None,
        "simulation_engine":  simulate is not None,
        "risk_engine":        assess_risk is not None,
        "survivor_engine":    survivor_analyze is not None,
        "belief_core":        belief_audit is not None,
        "king_diadem_core":   core_status(),        # ← v4.9
        "cosmic_latte_canon": _CANON_OK,            # ← v4.9
        "galaxy_api":         True,
        "stripe_loaded":      bool(os.getenv("STRIPE_SECRET_KEY")),
        "freedom_score":      freedom_index() if freedom_index else 0,
        "db_initialized":     init_db is not None,
    }


# ── DASHBOARD ─────────────────────────────────────────────────────
@app.get("/dashboard")
async def dashboard():
    try:    status   = planetary_status() if planetary_status else {}
    except: status   = {}
    try:    learning = get_learning()     if get_learning     else []
    except: learning = []
    try:    nodes    = get_nodes()        if get_nodes        else []
    except: nodes    = []
    return {
        "observer":  "KING DIADEM",
        "planetary": status,
        "supply_chain": {
            "global_food_security":   "DECLINING",
            "energy_drift_daily":     0.1,
            "water_stress_index":     72.4,
            "choice_collapse_risk":   "MODERATE",
            "lyla_signal":            "Systems losing 0.1% choice daily",
            "intervention_threshold": "Choice < 30%",
        },
        "recent_learning": learning[-10:] if learning else [],
        "active_nodes":    nodes[-10:]    if nodes    else [],
        "freedom_index":   freedom_index() if freedom_index else 50,
    }


# ── GOOGLE OAUTH ──────────────────────────────────────────────────
def _cookie_ascii(value: str) -> str:
    return quote(str(value or ""), safe="")


@app.get("/login/google")
async def google_login(request: Request):
    if not oauth:
        return JSONResponse({"error": "OAuth not configured"}, status_code=500)
    redirect_uri = os.getenv(
        "GOOGLE_REDIRECT_URI",
        "https://king-diadem.onrender.com/auth/google/callback"
    )
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.get("/auth/google/callback")
async def google_callback(request: Request):
    if not oauth:
        return RedirectResponse("/static/login.html?error=oauth_disabled")
    try:
        token = await oauth.google.authorize_access_token(request)
        user  = token.get("userinfo")
        email = user.get("email", "unknown")
        name  = user.get("name", email)
        if ensure_user: ensure_user(email)
        if get_credits and add_credits and get_credits(email) == 0:
            add_credits(email, 10)
        try:
            sess = getattr(request, "session", None)
            if sess:
                for k in list(sess.keys()):
                    if isinstance(k, str) and (
                        k.startswith("_state") or "oauth" in k.lower() or k.endswith("_token")
                    ):
                        sess.pop(k, None)
        except Exception:
            pass
        response = RedirectResponse("/")
        response.set_cookie("kd_email", _cookie_ascii(email), max_age=86400*30)
        response.set_cookie("kd_name",  _cookie_ascii(name),  max_age=86400*30)
        return response
    except Exception as e:
        print(f"google_callback error: {repr(e)}")
        return RedirectResponse("/static/login.html?error=oauth_error")


@app.get("/me")
async def me(request: Request):
    email = unquote(request.cookies.get("kd_email") or "")
    name  = unquote(request.cookies.get("kd_name")  or "")
    if not email:
        return {"logged_in": False}
    credits = get_credits(email) if get_credits else 0
    return {"logged_in": True, "email": email, "name": name, "credits": credits}


@app.post("/logout")
async def logout():
    r = JSONResponse({"status": "ok"})
    r.delete_cookie("kd_email")
    r.delete_cookie("kd_name")
    return r


# ── EMAIL LOGIN / REGISTER ────────────────────────────────────────
@app.post("/register")
async def register(data: dict):
    email = (data.get("email") or "").strip()
    if not email:
        return {"status": "error", "message": "กรุณากรอก email นะคะ"}
    if ensure_user: ensure_user(email)
    if add_credits and get_credits and get_credits(email) == 0:
        add_credits(email, 10)
    credits = get_credits(email) if get_credits else 0
    r = JSONResponse({"status": "ok", "email": email, "credits": credits})
    r.set_cookie("kd_email", _cookie_ascii(email), max_age=86400*30)
    r.set_cookie("kd_name",  _cookie_ascii(email), max_age=86400*30)
    return r


@app.post("/login")
async def login_email(data: dict):
    email = (data.get("email") or "").strip()
    if not email:
        return {"status": "error"}
    if ensure_user: ensure_user(email)
    credits = get_credits(email) if get_credits else 0
    r = JSONResponse({"status": "ok", "email": email, "credit": credits})
    r.set_cookie("kd_email", _cookie_ascii(email), max_age=86400*30)
    r.set_cookie("kd_name",  _cookie_ascii((data.get("name") or email).strip()), max_age=86400*30)
    return r


# ── CHAT STATE ────────────────────────────────────────────────────
@app.get("/api/chat-state")
async def get_chat_state(request: Request):
    email = unquote(request.cookies.get("kd_email") or "").strip()
    if not email or not load_chat_state:
        return {"state": None}
    raw = load_chat_state(email)
    if not raw:
        return {"state": None}
    try:    return {"state": json.loads(raw)}
    except: return {"state": None}


@app.put("/api/chat-state")
async def put_chat_state(request: Request, data: dict):
    email = unquote(request.cookies.get("kd_email") or "").strip()
    if not email or not save_chat_state:
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    state = data.get("state") if isinstance(data.get("state"), dict) else data
    if not isinstance(state, dict):
        return JSONResponse({"ok": False, "error": "invalid"}, status_code=400)
    save_chat_state(email, json.dumps(state, ensure_ascii=False))
    return {"ok": True}


@app.post("/api/chat-state")
async def post_chat_state(request: Request, data: dict):
    return await put_chat_state(request, data)


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════
def _route_bias(route: str, text: str) -> str:
    tags = {
        "risk":     "[โหมด: ประเมินความเสี่ยง/ผลกระทบ]",
        "survival": "[โหมด: ความอยู่รอดพื้นฐาน — อาหาร ที่พัก ความปลอดภัย]",
        "collapse": "[โหมด: ลูกโซ่ความเสียหาย/แรงกดดันสะสม]",
        "civil":    "[โหมด: งาน/พลเมือง/ความรับผิดชอบต่อส่วนรวม]",
        "vega":     "[โหมด: VEGA — strategic analysis ระยะยาว]",
    }
    tag = tags.get(route, "")
    return f"{tag} {text}".strip() if tag else text


def _resolve_voice_mode(data: dict, route: str) -> str:
    vm = str(data.get("voice_mode") or "").lower().strip()
    if vm == "crisis":                   return "crisis"
    if vm == "vega" or route == "vega":  return "vega"
    return "lyla"


# ── ROUTE SEVERITY — v4.9.1 ──────────────────────────────────────
# ป้องกัน route ถูก downgrade เงียบ ๆ เมื่อหลาย engine เขียนทับกัน
# (risk_engine / king_diadem_core / survivor_engine / belief_core)
# ต้อง escalate ตามลำดับความรุนแรงเท่านั้น ห้ามลดระดับโดยไม่ตั้งใจ
_ROUTE_SEVERITY = {
    "general": 0, "risk": 1, "civil": 1,
    "survival": 2, "collapse": 3,
}

def _escalate_route(current: str, candidate: str) -> str:
    if not candidate or candidate == "vega":
        return current
    if _ROUTE_SEVERITY.get(candidate, 0) >= _ROUTE_SEVERITY.get(current, 0):
        return candidate
    print(f"⚠ ROUTE DOWNGRADE BLOCKED: {current} → {candidate} (ignored, kept {current})")
    return current


def _enrich_with_universal(result: dict, payload: dict) -> dict:
    if not _universal_run:
        return result
    try:
        uni = _universal_run(payload)
        if not isinstance(uni, dict) or uni.get("status") == "blocked":
            return result
        for key in ("council", "consensus", "state", "decision"):
            if key in uni and key not in result:
                result[key] = uni[key]
        if "risk" in uni and isinstance(uni["risk"], dict):
            result.setdefault("universal_risk", uni["risk"])
    except Exception as e:
        result.setdefault("universal_engine_error", str(e))
    return result


# ══════════════════════════════════════════════════════════════════
# /run  +  /decision — v4.9
# ══════════════════════════════════════════════════════════════════
@app.post("/run")
@app.post("/decision")
async def run_kernel(request: Request, data: dict):
    user_input = data.get("input") or data.get("text") or ""
    if not user_input:
        return {"error": "Input is required"}

    email   = unquote(request.cookies.get("kd_email") or "anonymous")
    route   = data.get("route") or "general"
    vm      = _resolve_voice_mode(data, route)
    history = data.get("history") or []

    if record_question: record_question()

    # ── human state ──────────────────────────────────────────────
    human_state = {"entropy": 40, "resource": 50, "stability": 60, "risk_score": 10}
    if analyze_human:
        try: human_state = analyze_human(data.get("context", {})) or human_state
        except Exception: pass

    # ── intent ───────────────────────────────────────────────────
    intent = {"intent": "general", "confidence": 0.5}
    if analyze_intent:
        try: intent = analyze_intent(user_input) or intent
        except Exception: pass

    # ── risk ─────────────────────────────────────────────────────
    risk_ctx = ""
    if assess_risk:
        try:
            r = assess_risk(human_state)
            if isinstance(r, dict) and r.get("level"):
                risk_ctx = f"[Risk: {r['level']}]"
                if r.get("level") in ("HIGH", "CRITICAL") and route not in ("vega",):
                    route = _escalate_route(route, "collapse")
        except Exception: pass

    # ── collapse ─────────────────────────────────────────────────
    collapse_ctx = ""
    if predict_collapse:
        try:
            c = predict_collapse(human_state.get("risk_score", human_state.get("entropy", 40)))
            if isinstance(c, dict) and c.get("probability", 0) > 0.6:
                collapse_ctx = f"[Collapse probability: {c['probability']:.0%}]"
        except Exception: pass

    # ══════════════════════════════════════════════════════════════
    # KING DIADEM CORE v2 — BODHIPAKKHIYA CHANNEL — v4.9
    # แทนที่ _paticcasamuppada_context() เดิม
    # ══════════════════════════════════════════════════════════════
    core_result  = quick_assess(user_input, human_state)
    paticca_ctx  = core_result.get("causal_ctx", "")   # จาก paticcasamuppada
    wise_ctx_str = core_result.get("wise_ctx", "")     # จาก yonisomanasikara

    # bodhi recommend route
    if core_result.get("recommend_route") and route not in ("vega",):
        route = _escalate_route(route, core_result["recommend_route"])

    # drift alert log
    if core_result.get("drift_alert"):
        print(f"⚠ DRIFT ALERT | route={route} | {user_input[:60]}")

    # ── survivor ─────────────────────────────────────────────────
    survivor_ctx = ""
    if orchestrator:
        try:
            sr = orchestrator.run_with_survivor_engine(
                user_input=user_input,
                human_context=data.get("context", {})
            )
            survivor_ctx = sr.get("survivor_context", "")
            if not sr.get("can_decide", True) and route not in ("vega",):
                route = _escalate_route(route, sr.get("route", route))
        except Exception: pass
    elif survivor_analyze:
        try:
            sr = survivor_analyze(user_input, data.get("context", {}))
            survivor_ctx = sr.get("context", "")
            if not sr.get("can_decide", True) and route not in ("vega",):
                route = _escalate_route(route, sr.get("route", route))
        except Exception: pass

    # ── BELIEF CORE AUDIT — v4.8 ─────────────────────────────────
    belief_report = None
    if belief_audit:
        try:
            belief_ctx    = {**human_state, **data.get("context", {})}
            belief_report = belief_audit(belief_ctx)

            if not belief_report["survival_ok"] and route not in ("vega",):
                route = _escalate_route(route, "survival")

            if belief_report["pause_required"]:
                pause_result = {
                    "observer":      "KING DIADEM",
                    "status":        "SYSTEM_PAUSE",
                    "route":         route,
                    "persona":       "VEGA" if vm == "vega" else "LYLA",
                    "voice_mode":    vm,
                    "ai_response":   "",
                    "pattern":       human_state,
                    "risk_score":    human_state.get("risk_score", 0),
                    "bodhipakkhiya": core_result.get("bodhi_verdict", ""),
                }
                pause_result = belief_enforce(pause_result, belief_report)
                _sync_galaxy(pause_result)
                return pause_result

        except Exception as _be:
            print(f"⚠ belief_audit error: {_be}")

    # ── build effective prompt ────────────────────────────────────
    extra_ctx = " ".join(p for p in [
        paticca_ctx,
        wise_ctx_str,    # ← v4.9 เพิ่ม yonisomanasikara context
        risk_ctx,
        collapse_ctx,
    ] if p)

    effective = ""
    if survivor_ctx:
        effective += survivor_ctx + "\n\n"
    effective += _route_bias(route, user_input)
    if extra_ctx:
        effective += f"\n\n{extra_ctx}"

    payload = {**data, "input": effective, "history": history}

    # ── MAIN DECISION PIPELINE ────────────────────────────────────
    if full_run_decision:
        result = full_run_decision(payload)
    elif engine:
        result = engine.run(payload)
    else:
        reply = ""
        if llm:
            try:
                reply = llm.generate_with_governance(
                    prompt=effective,
                    additional_context=(
                        f"entropy={human_state.get('entropy')}, "
                        f"stability={human_state.get('stability')}, "
                        f"voice_mode={vm}"
                    ),
                    history=history,
                    route=route,
                    voice_mode=vm,
                    user_email=email,
                )
            except Exception as e:
                print(f"⚠ LLM error: {e}")
                return {"error": _friendly_error(str(e))}

        if not reply:
            reply = "ระบบ AI ไม่พร้อมชั่วคราว — ลองใหม่อีกครั้งนะคะ\n\n— LYLA ◈"

        result = {
            "observer":      "KING DIADEM",
            "status":        "SUCCESS",
            "route":         intent.get("intent", route) if isinstance(intent, dict) else route,
            "ai_response":   reply,
            "governance":    {"intent": intent, "human_state": human_state},
            "persona":       "VEGA" if vm == "vega" else "LYLA",
            "pattern":       human_state,
            "risk_score":    human_state.get("risk_score", 0),
            "bodhipakkhiya": core_result.get("bodhi_verdict", ""),  # ← v4.9
        }

    # ── error clean ───────────────────────────────────────────────
    if result.get("error"):
        result["error"] = _friendly_error(str(result["error"]))
        return result

    result["route"]      = result.get("route") or route
    result["persona"]    = "VEGA" if vm == "vega" else "LYLA"
    result["voice_mode"] = vm

    result = _enrich_with_universal(result, payload)

    if build_consensus and result.get("ai_response"):
        try:
            cs = build_consensus({
                "text": user_input, "response": result["ai_response"],
                "route": route,     "human_state": human_state,
            })
            if isinstance(cs, dict) and cs.get("consensus"):
                result["consensus"] = cs["consensus"]
        except Exception: pass

    _sync_galaxy(result)

    # ── BELIEF ENFORCE — v4.8 (v4.9.1: safe-default guard) ────────
    # ถ้า belief_audit fail ก่อนหน้านี้ belief_report จะเป็น None
    # ห้ามส่ง None เข้า belief_enforce เงียบ ๆ — ต้อง fail loud ตาม
    # FATE™ Axiom "Explainability = 100%" ไม่ใช่ fail silent
    if belief_enforce:
        try:
            if isinstance(belief_report, dict):
                result = belief_enforce(result, belief_report)
            else:
                safe_belief_report = {
                    "survival_ok": True, "pause_required": False,
                    "note": "belief_audit unavailable — enforcement skipped",
                }
                result = belief_enforce(result, safe_belief_report)
                result["governance_warning"] = "belief_audit_failed"
                print("⚠ belief_report was None — belief_enforce ran on safe default")
        except Exception as _bfe:
            print(f"⚠ belief_enforce error: {_bfe}")
            result["governance_warning"] = "belief_enforce_failed"

    # ══════════════════════════════════════════════════════════════
    # COSMIC LATTE CANON GATE — v4.9
    # validate output ก่อน return ให้ user
    # ══════════════════════════════════════════════════════════════
    try:
        result = canon_validate(result)
        if result.get("canon_violation"):
            print(f"⚠ CANON VIOLATION: {result.get('canon_violations', [])}")
    except Exception as _cv:
        print(f"⚠ canon_validate error: {_cv}")

    if log_decision:
        try:
            log_decision(
                user_id=email, input=user_input,
                output=result.get("ai_response", ""),
                route=result.get("route", route),
                persona=result.get("persona", "LYLA"),
            )
        except Exception: pass

    # ── DECISION REPORT URL ───────────────────────────────────────
    if _create_report:
        try:
            report_id = _create_report(
                user_email=email,
                user_input=user_input,
                result=result,
            )
            result["report_url"] = f"/report/{report_id}"
            result["report_id"]  = report_id
            result["share_url"]  = f"https://king-diadem.onrender.com/report/{report_id}"
        except Exception as _re:
            print(f"⚠ report creation failed: {_re}")

    return result


# ── SIMULATE ──────────────────────────────────────────────────────
@app.post("/simulate")
async def run_simulate(request: Request, data: dict):
    user_input = str(data.get("input") or "").strip()
    paths      = data.get("paths") or []
    email      = unquote(request.cookies.get("kd_email") or "anonymous")
    if not user_input:
        return {"simulation": "พิมพ์สถานการณ์ก่อนนะคะ"}

    try:
        _llm = get_llm()
        paths_text = "\n".join("- " + str(p) for p in paths if str(p).strip()) or "ไม่ระบุ"
        prompt = (
            "[KING DIADEM — จำลองอนาคต FATE]\n\n"
            "สถานการณ์: " + user_input + "\n\n"
            "ทางเลือกที่ผู้ใช้มี:\n" + paths_text + "\n\n"
            "วิเคราะห์แต่ละทางเลือก:\n"
            "1. ความเสี่ยง (Downside First)\n"
            "2. ผลใน 30 / 90 วัน\n"
            "3. ทางที่แนะนำพร้อมเหตุผล 1 ประโยค\n\n"
            "ตอบเป็นภาษาไทย กระชับ ใช้งานได้ทันที\n— VEGA"
        )
        answer = _llm.generate_with_governance(
            prompt=prompt, route="survival",
            additional_context="mode=simulation",
            user_email=email,
        )
        if answer and len(str(answer)) > 10:
            return {"simulation": answer}
    except Exception as e:
        print(f"simulate LLM: {e}")

    if not simulate:
        return {"simulation": "ระบบจำลองไม่พร้อมชั่วคราว — ลองใหม่อีกครั้งนะคะ"}
    try:
        result = simulate({"input": user_input, "paths": paths})
        return result if isinstance(result, dict) else {"simulation": str(result)}
    except Exception as e:
        print(f"simulate error: {e}")
        return {"error": _friendly_error(str(e))}


# ── STRIPE ────────────────────────────────────────────────────────
@app.post("/create-checkout-session")
async def create_checkout(request: Request, data: dict):
    email = unquote(request.cookies.get("kd_email") or "") or data.get("email", "")
    plan  = data.get("plan", "basic")
    if plan == "civilization":
        price_id = os.getenv("STRIPE_PREMIUM_PRICE_ID") or os.getenv("STRIPE_PRICE_ID")
    else:
        price_id = os.getenv("STRIPE_PRICE_ID") or os.getenv("STRIPE_PREMIUM_PRICE_ID")
    if not price_id:
        return JSONResponse({"error": "ยังไม่ได้ตั้งค่า STRIPE_PRICE_ID"}, status_code=500)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            customer_email=email or None,
            success_url="https://king-diadem.onrender.com/?payment=success",
            cancel_url="https://king-diadem.onrender.com/?payment=cancel",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/create-subscription")
async def create_subscription(request: Request):
    email    = unquote(request.cookies.get("kd_email") or "")
    price_id = os.getenv("STRIPE_PREMIUM_PRICE_ID") or os.getenv("STRIPE_PRICE_ID")
    if not price_id:
        return JSONResponse({"error": "ยังไม่ได้ตั้งค่า STRIPE_PRICE_ID"}, status_code=500)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            customer_email=email or None,
            success_url="https://king-diadem.onrender.com/?payment=success",
            cancel_url="https://king-diadem.onrender.com/?payment=cancel",
        )
        return {"url": session.url}
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig     = request.headers.get("stripe-signature", "")
    secret  = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    try:    event = stripe.Webhook.construct_event(payload, sig, secret)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=400)
    if event["type"] == "checkout.session.completed":
        sess  = event["data"]["object"]
        email = sess.get("customer_email")
        qty   = 1
        try:
            items = stripe.checkout.Session.list_line_items(sess["id"])
            qty   = sum(i.get("quantity", 1) for i in items.get("data", []))
        except Exception: pass
        if email and add_credits: add_credits(email, qty * 10)
    return {"status": "ok"}


@app.get("/credits")
async def get_user_credits(request: Request):
    email = unquote(request.cookies.get("kd_email") or "")
    if not email:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    credits = get_credits(email) if get_credits else 0
    return {"email": email, "credits": credits}


# ── ANALYZE IMAGE ─────────────────────────────────────────────────
@app.post("/analyze-image")
async def analyze_image(request: Request, file: UploadFile = File(...)):
    if not llm:
        return JSONResponse({"error": "LLM ไม่พร้อม"}, status_code=503)
    try:
        data = await file.read()
        mime = file.content_type or "image/jpeg"
        from google.genai import types as gt
        contents = [gt.Content(role="user", parts=[
            gt.Part.from_bytes(data=data, mime_type=mime),
            gt.Part.from_text(text=(
                "วิเคราะห์ภาพนี้ในมุม KING DIADEM Governance:\n"
                "1. มีความเสี่ยงอะไรที่เห็นได้\n"
                "2. ทางเลือกที่มีอยู่คืออะไร\n"
                "3. สัญญาณ waterline / drift ที่เห็น\n"
                "ตอบเป็นภาษาไทย กระชับ ตรงประเด็นนะคะ\n— LYLA ◈"
            ))
        ])]
        _llm = get_llm()
        cfg  = gt.GenerateContentConfig(
            system_instruction="คุณคือ LYLA governance scanner วิเคราะห์ภาพแล้วรายงาน risk/choice/waterline",
            temperature=0.5, max_output_tokens=800,
        )
        vision_model = getattr(_llm, 'vision_model', None) or 'gemini-2.0-flash'
        try:
            resp = _llm.client.models.generate_content(model=vision_model, contents=contents, config=cfg)
        except Exception:
            resp = _llm.client.models.generate_content(model='gemini-1.5-flash', contents=contents, config=cfg)
        try:
            analysis_text = resp.text or ""
        except Exception:
            parts = getattr(getattr(resp, 'candidates', [None])[0], 'content', None)
            analysis_text = " ".join(p.text for p in (getattr(parts, 'parts', []) or []) if hasattr(p,'text'))
        analysis_text = analysis_text.strip()
        if not analysis_text:
            analysis_text = "LYLA วิเคราะห์ภาพไม่ได้ค่ะ — อาจถูก Gemini safety block หรือภาพไม่ชัด"
        return {"analysis": analysis_text, "filename": file.filename}
    except Exception as e:
        print(f"⚠ analyze_image error: {e}")
        return JSONResponse({"error": _friendly_error(str(e))}, status_code=500)


# ── REPORT ROUTES ─────────────────────────────────────────────────
@app.get("/report/{report_id}")
async def report_page(report_id: str):
    html_path = os.path.join(os.path.dirname(__file__), "static", "report.html")
    if not os.path.exists(html_path):
        return JSONResponse({"error": "report.html not found"}, status_code=500)
    return FileResponse(html_path, media_type="text/html")


@app.get("/api/report/{report_id}")
async def get_report_api(report_id: str):
    if not _get_report:
        return JSONResponse({"error": "report engine not loaded"}, status_code=503)
    data = _get_report(report_id)
    if not data:
        return JSONResponse({"error": "Report not found"}, status_code=404)
    return data


@app.post("/api/report/create")
async def create_report_manual(request: Request, data: dict):
    if not _create_report:
        return JSONResponse({"error": "report engine not loaded"}, status_code=503)
    email      = unquote(request.cookies.get("kd_email") or "anonymous")
    user_input = data.get("input", "")
    result     = data.get("result", {})
    if not user_input or not result:
        return JSONResponse({"error": "input and result required"}, status_code=400)
    try:
        report_id = _create_report(user_email=email, user_input=user_input, result=result)
        return {
            "report_id":  report_id,
            "report_url": f"/report/{report_id}",
            "share_url":  f"https://king-diadem.onrender.com/report/{report_id}",
        }
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
