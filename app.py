# =========================
# 👑 KING DIADEM — app.py v5.0
# LYLA (หญิง/ค่ะ) · VEGA (ชาย/ครับ)
# โพธิปักขิยธรรม 37 · ปฏิจสมุปบาท · โยนิโสมนสิการ · สุญยตา
# Fail less. Harm less. Restore more.
#
# PATCH v4.9
# - king_diadem_core v2.0 wired: quick_assess() แทน _paticcasamuppada_context()
# - bodhipakkhiya channel ก่อน LLM ทุกครั้ง (อยู่ใน core/king_diadem_core.quick_assess —
#   ไฟล์ ENGINE/bodhipakkhiya_engine.py ไม่มีอยู่จริง)
# - cosmic_latte_canon: validate_output() gate ก่อน return
# - wise_ctx inject เข้า LLM prompt
# - LYLA tone: น่ารัก เข้าอกเข้าใจ ไม่เทศ
#
# PATCH v4.9.1
# - SECRET_KEY: ลบ hardcoded default, raise ถ้าไม่ได้ตั้ง env
# - route resolution: severity-ranked escalation (_escalate_route), ห้าม downgrade เงียบๆ
# - belief_report=None guard ก่อนส่งเข้า belief_enforce, เพิ่ม governance_warning
#
# PATCH v5.0
# - cookies: httponly/secure/samesite ทุกจุดที่ set_cookie
# - /analyze-image: guard ขนาดไฟล์ (10MB) + mime type whitelist
# - stripe webhook: credit ผูกกับ price_id จริง ไม่ใช่ quantity จาก client
# - rate limit /run /decision: 20 req / 60s ต่อ identity (in-memory)
# - canon gate: hard block จริงสำหรับ severe violations (choice_collapse/coercion/forced_identity)
#   + canon_notice โชว์ให้ user เห็น ไม่ใช่แค่ print server-side
# - payload ส่ง wise_context/causal_context/core_verdict เป็น field แยก ไม่ใช่แค่ text ต่อท้าย
# - LYLA/VEGA tone instruction ผูกเข้า additional_context จริง
# =========================

from fastapi import FastAPI, Request, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
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
    from ENGINE.risk_engine import assess as assess_risk, evaluate_risk as text_risk
except Exception as e:
    print(f"⚠ risk_engine: {e}")
    assess_risk = None
    text_risk = None

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
    from core.king_diadem_core import quick_assess, king_diadem_decision, core_status
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

# ── KERNEL VOICE — ตอบได้แม้ไม่มี AI (core/kernel_voice.py) ──────────
try:
    from core.kernel_voice import compose as kernel_compose, simulate as kernel_simulate, assess as kernel_assess
    from core.thai_signals import OFFER_FLAG_TH
    from core.lang_signals import detect_lang
    from core.engine_bridge import analyze as bridge_analyze
except Exception as e:
    print(f"⚠ kernel_voice: {e}")
    kernel_compose = kernel_simulate = kernel_assess = None
    OFFER_FLAG_TH = {}
    detect_lang = None
    bridge_analyze = None

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
        set_password, verify_password, user_exists,
        stripe_event_done, mark_stripe_event, add_credits_once, premium_subscription,
        set_premium_until, get_premium_until, email_for_stripe_customer,
        spend_credit, credit_history, take_free_run, give_back_free_run, free_runs_used,
        open_charge, close_charge, reclaim_stale_charges,
    )
    init_db()
    print("✅ Database initialized")
except Exception as e:
    print(f"⚠ DB: {e}")
    init_db = log_decision = get_credits = add_credits = None
    ensure_user = save_chat_state = load_chat_state = None
    set_password = verify_password = user_exists = None
    stripe_event_done = mark_stripe_event = add_credits_once = premium_subscription = None
    set_premium_until = get_premium_until = email_for_stripe_customer = None
    spend_credit = credit_history = take_free_run = give_back_free_run = free_runs_used = None
    open_charge = close_charge = reclaim_stale_charges = None

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
    from AI.civilization_engine import add_node, get_nodes, node_summary
    print("✅ Civilization loaded")
except Exception as e:
    print(f"⚠ CIVILIZATION: {e}")
    planetary_status = get_learning = get_nodes = None
    record_learning  = add_node = node_summary = None

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
# ใช้ singleton ตัวเดียวกับ run_decision() — เดิมสร้าง DecisionEngine ตัวที่สองแยกไว้เฉยๆ (โหลด LLM/router ซ้ำ)
try:
    from ENGINE.decision_engine import _engine as _decision_engine_singleton
    engine = _decision_engine_singleton() if DecisionEngine else None
except Exception:
    engine = DecisionEngine() if DecisionEngine else None
app.mount("/static", StaticFiles(directory="static"), name="static")


# ══════════════════════════════════════════════════════════════════
# ERROR MESSAGE HELPER
# ══════════════════════════════════════════════════════════════════
def _friendly_error(err: str) -> str:
    e = str(err).lower()
    if "403" in e or "permission_denied" in e or "permission denied" in e:
        return "ระบบ AI ยังเข้าใช้งานไม่ได้ตอนนี้ค่ะ ลองใหม่อีกครั้งนะคะ"
    if "503" in e or "unavailable" in e or "high demand" in e:
        return "AI ยุ่งอยู่นิดหน่อยค่ะ รอสักครู่แล้วลองใหม่ได้เลยนะคะ"
    if "429" in e or "quota" in e or "rate limit" in e:
        return "ใช้งานถึงขีดจำกัดชั่วคราวค่ะ รอสักครู่แล้วลองอีกทีนะคะ"
    if "404" in e or "not found" in e or "not supported" in e:
        return "โมเดล AI ยังไม่พร้อมค่ะ ระบบกำลังสลับไปใช้ตัวสำรองนะคะ"
    if "auth" in e or "api_key" in e or "api key" in e:
        return "ระบบกำลังตรวจสอบการเชื่อมต่อค่ะ ลองใหม่อีกครั้งนะคะ"
    if "timeout" in e or "timed out" in e:
        return "การเชื่อมต่อช้าไปหน่อยค่ะ ลองใหม่ได้เลยนะคะ"
    return "ระบบขอพักสักครู่ค่ะ ลองใหม่อีกครั้งนะคะ"


# ══════════════════════════════════════════════════════════════════
# REQUEST HELPERS
# ══════════════════════════════════════════════════════════════════
_PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "https://king-diadem.onrender.com").rstrip("/")

def _public_url(path: str) -> str:
    return _PUBLIC_BASE_URL + path

# จำนวน proxy ที่เชื่อถือได้หน้าแอป (Render = 1) — proxy จะ "ต่อท้าย" IP จริงใน X-Forwarded-For
_TRUSTED_PROXY_HOPS = max(0, int(os.getenv("TRUSTED_PROXY_HOPS", "1")))
# Render วิ่งผ่าน Cloudflare ซึ่งเขียนทับ cf-connecting-ip ทุกครั้ง (client ปลอมไม่ได้) → เชื่อเมื่อรันบน Render
# (Render ตั้ง env RENDER ให้เอง) ที่อื่นปิดไว้ เว้นแต่ตั้ง TRUST_CF_HEADER=1
_TRUST_CF_HEADER    = os.getenv("TRUST_CF_HEADER", "1" if os.getenv("RENDER") else "0") == "1"

def _client_ip(request: Request) -> str:
    """IP จริงของผู้ใช้หลัง proxy

    เดิมเชื่อ cf-connecting-ip / true-client-ip / X-Forwarded-For "ตัวแรก" ซึ่ง client ใส่เองได้
    → ผู้ใช้ไม่ล็อกอินปลอม IP ใหม่ทุกครั้ง = โควตาฟรีไม่จำกัด + หลบ rate limit + เดารหัสผ่านไม่จำกัด
    ตอนนี้: นับจากขวาตามจำนวน proxy ที่เชื่อถือ (ค่าที่ proxy เติมเอง client ปลอมไม่ได้)
    """
    h = request.headers
    if _TRUST_CF_HEADER and h.get("cf-connecting-ip"):
        return h.get("cf-connecting-ip").strip()
    if _TRUSTED_PROXY_HOPS:
        parts = [p.strip() for p in h.get("x-forwarded-for", "").split(",") if p.strip()]
        if len(parts) >= _TRUSTED_PROXY_HOPS:
            return parts[-_TRUSTED_PROXY_HOPS]
    return request.client.host if request.client else "unknown"

def _is_premium(email: str) -> bool:
    if not email or not get_premium_until:
        return False
    try:
        return get_premium_until(email) > time.time()
    except Exception:
        return False


# ══════════════════════════════════════════════════════════════════
# BILLING — ทุกคำตอบจาก AI (/run, /simulate, /analyze-image) = 1 ข้อความ
#   premium → ไม่จำกัด
#   ฟรี FREE_DAILY_RUNS ข้อความ/วัน (นับฝั่ง server ต่ออีเมล หรือต่อ IP ถ้าไม่ล็อกอิน)
#   เกินโควตา → หัก RUN_COST เครดิต (ต้องล็อกอิน) · เครดิตไม่พอ → 402
#   ระบบตอบไม่ได้ (error / Gemini ล้ม / canon block / pause) → คืนให้
# ══════════════════════════════════════════════════════════════════
from datetime import datetime, timezone, timedelta
try:
    from core.llm_gemini import reset_fallback_flag, used_fallback, request_no_ai, ai_disabled
except Exception:
    reset_fallback_flag = lambda: None
    used_fallback = lambda: False
    request_no_ai = lambda on=True: None
    ai_disabled = lambda: True

FREE_DAILY_RUNS = max(0, int(os.getenv("FREE_DAILY_RUNS", "20")))
RUN_COST        = max(1, int(os.getenv("RUN_COST", "1")))
THB_PER_CREDIT  = max(0.01, float(os.getenv("THB_PER_CREDIT", "1")))
_BKK = timezone(timedelta(hours=7))

def _today() -> str:
    return datetime.now(_BKK).strftime("%Y-%m-%d")

def _quota_identity(email: str, request: Request) -> str:
    return email if email and email != "anonymous" else "ip:" + _client_ip(request)

def _quota_status(email: str, request: Request) -> dict:
    email = "" if email == "anonymous" else (email or "")
    used  = free_runs_used(_quota_identity(email, request), _today()) if free_runs_used else 0
    return {
        "premium":   _is_premium(email),
        "free_limit": FREE_DAILY_RUNS,
        "free_left": max(0, FREE_DAILY_RUNS - used),
        "credits":   (get_credits(email) if get_credits and email else None),
        "run_cost":  RUN_COST,
    }

def _charge(email: str, request: Request, what: str):
    """คืน (ticket, None) ถ้าใช้ได้ หรือ (None, JSONResponse 402) ถ้าโควตา/เครดิตหมด"""
    email = "" if email == "anonymous" else (email or "")
    if take_free_run is None:                       # DB ใช้ไม่ได้ → ไม่คิดเงิน
        return {"mode": "unmetered"}, None
    if _is_premium(email):
        return {"mode": "premium"}, None
    _reclaim_stale()
    ident, day = _quota_identity(email, request), _today()
    if take_free_run(ident, day, FREE_DAILY_RUNS):
        return _open({"mode": "free", "identity": ident, "day": day}), None
    if email and spend_credit and spend_credit(email, RUN_COST, what):
        return _open({"mode": "credit", "email": email, "what": what}), None
    msg = (f"วันนี้คุยครบ {FREE_DAILY_RUNS} ข้อความฟรีแล้วค่ะ พรุ่งนี้กลับมาคุยกันได้อีกนะคะ "
           + ("หรือถ้าอยากคุยต่อตอนนี้ เติมเครดิตหรือสมัคร Premium ได้เลยค่ะ" if email
              else "หรือถ้าอยากคุยต่อตอนนี้ เข้าสู่ระบบแล้วเติมเครดิต หรือสมัคร Premium ได้เลยค่ะ"))
    body = {"error": msg, "code": "quota_exhausted", "quota": _quota_status(email, request)}
    return None, JSONResponse(body, status_code=402)

def _open(ticket: dict) -> dict:
    """จดการหักลงฐานข้อมูล — ถ้า worker ตายกลางทาง _reclaim_stale จะคืนให้ภายหลัง"""
    if open_charge:
        try:
            ticket["id"] = open_charge(ticket)
        except Exception as e:
            print(f"⚠ open_charge: {type(e).__name__}")
    return ticket

def _settle(ticket):
    """ได้คำตอบแล้ว — ปิดใบเสร็จ (หักจริง)"""
    if ticket and ticket.get("id") and close_charge:
        try:
            close_charge(ticket["id"])
        except Exception as e:
            print(f"⚠ close_charge: {type(e).__name__}")

_reclaim_at = 0.0

def _reclaim_stale(force: bool = False):
    """คืนโควตา/เครดิตของ request ที่ตายไปแล้ว (ใบเสร็จค้างเกิน 5 นาที) — เช็กอย่างมาก 5 นาทีครั้ง"""
    global _reclaim_at
    now = time.time()
    if not reclaim_stale_charges or (not force and now - _reclaim_at < 300):
        return
    _reclaim_at = now
    try:
        for t in reclaim_stale_charges(300):
            _refund({k: t.get(k) for k in ("mode", "identity", "day", "email", "what")})
    except Exception as e:
        print(f"⚠ reclaim_stale_charges: {type(e).__name__}")

def _refund(ticket):
    if not ticket:
        return
    # ใบเสร็จถูกเก็บคืนไปแล้ว (reclaim) → คืนไปแล้ว ห้ามคืนซ้ำ
    if ticket.get("id") and close_charge:
        try:
            if not close_charge(ticket["id"]):
                return
        except Exception as e:
            print(f"⚠ close_charge: {type(e).__name__}")
    try:
        if ticket["mode"] == "free" and give_back_free_run:
            give_back_free_run(ticket["identity"], ticket["day"])
        elif ticket["mode"] == "credit" and add_credits:
            add_credits(ticket["email"], RUN_COST, "refund", ticket.get("what"))
    except Exception as e:
        print(f"⚠ refund failed: {e}")

def _answered(result) -> bool:
    """ผู้ใช้ได้คำตอบจริงจาก AI หรือไม่ (ไม่ใช่ error/ข้อความสำรอง/ถูกระงับ)
    คำตอบจากสมการ (answer_source=kernel) ไม่มีต้นทุน AI → ไม่หักโควตา/เครดิต"""
    if not isinstance(result, dict) or result.get("error"):
        return False
    if result.get("answer_source") == "kernel":
        return False
    if result.get("status") in ("CANON_BLOCKED", "SYSTEM_PAUSE", "BLOCKED"):
        return False
    return not used_fallback()


# ══════════════════════════════════════════════════════════════════
# GALAXY STATE
# ══════════════════════════════════════════════════════════════════
_glock = threading.Lock()
# NOTE (v5.0): _gstate ถูกเขียนทั้งจาก async def handlers (event loop thread)
# และ def handlers ธรรมดา (threadpool thread ของ FastAPI) — threading.Lock
# คือตัวที่ถูกต้อง เพราะ asyncio.Lock ป้องกันได้แค่ coroutine บน loop เดียวกัน
# ไม่ป้องกัน cross-thread race กับ threadpool เลย ห้ามเปลี่ยนเป็น asyncio.Lock
# เงื่อนไขที่ต้องรักษาไว้: ห้ามมี await ใดๆ อยู่ใน `with _glock:` block เด็ดขาด
# (ตอนนี้ทุก block เป็นแค่ dict write ล้วน ปลอดภัยอยู่)
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


# endpoint สาธารณะ — เดิมคืน route/risk/waterline ของ "ผู้ใช้คนล่าสุด" ให้ทุกคนเห็น
# (สภาวะวิกฤตของคนหนึ่งโผล่บนหน้าจอของอีกคน) ตอนนี้คืนเฉพาะวงโคจร — route ของแต่ละคนอยู่ฝั่งหน้าเว็บ
_NEUTRAL_WATERLINE = {"entropy": 40.0, "stability": 60.0, "resource": 50.0}

@app.get("/api/galaxy/nodes")
def galaxy_nodes():
    with _glock:
        nodes = _planet_positions()
    for n in nodes:
        n["active"] = False
    return {
        "ok":           True,
        "active_route": "general",
        "lyla_mode":    "idle",
        "risk_score":   0.0,
        "waterline":    dict(_NEUTRAL_WATERLINE),
        "nodes":        nodes,
        "ts":           int(time.time() * 1000),
    }


@app.post("/api/galaxy/signal")
async def galaxy_signal(data: dict):
    route = str(data.get("route", "general")).lower()
    mode  = str(data.get("lyla_mode", "idle")).lower()
    if route not in _PLANETS:
        return JSONResponse({"ok": False, "error": "unknown route"}, status_code=400)
    # ไม่เขียนสถานะรวมอีกต่อไป — เดิมใครก็เปลี่ยน route ที่ผู้ใช้ทุกคนเห็นได้
    return {"ok": True, "active_route": route, "lyla_mode": mode if mode in ("idle", "burst", "think") else "idle"}


@app.get("/api/galaxy/state")
def galaxy_state_debug():
    # debug เดิมคืน _gstate ทั้งก้อน (ข้อมูลของผู้ใช้คนล่าสุด) — เหลือเฉพาะวงโคจร
    with _glock:
        return {"nodes": _planet_positions(), "last_updated": _gstate["last_updated"]}


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
        "version":            "5.0",
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
        "stripe_webhook":     bool(os.getenv("STRIPE_WEBHOOK_SECRET")),
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
        # ค่าใน supply_chain เป็นค่าคงที่ที่เขียนไว้ในโค้ด ไม่ได้มาจากแหล่งข้อมูลจริง
        "supply_chain": {
            "source":                 "static_placeholder — not live data",
            "global_food_security":   "DECLINING",
            "energy_drift_daily":     0.1,
            "water_stress_index":     72.4,
            "choice_collapse_risk":   "MODERATE",
            "lyla_signal":            "Systems losing 0.1% choice daily",
            "intervention_threshold": "Choice < 30%",
        },
        # /dashboard เปิดสาธารณะ — ไม่ส่งข้อความคำถาม/การตัดสินใจของผู้ใช้ออกไป เหลือแค่ผลลัพธ์
        "recent_learning": [
            {k: e.get(k) for k in ("id", "timestamp", "success", "outcome_label")}
            for e in (learning[-10:] if learning else []) if isinstance(e, dict)
        ],
        "active_nodes":    [
            {k: n.get(k) for k in ("id", "recorded_at", "node_type")}
            for n in (nodes[-10:] if nodes else []) if isinstance(n, dict)
        ],
        "freedom_index":   freedom_index() if freedom_index else 50,
        "civilization":    (node_summary() if node_summary else {}),
    }


# ── GOOGLE OAUTH ──────────────────────────────────────────────────
def _cookie_ascii(value: str) -> str:
    return quote(str(value or ""), safe="")

_COOKIE_KW = dict(httponly=True, secure=True, samesite="lax")
_SESSION_MAX_AGE = 86400 * 30

# SECURITY: cookie ตัวตนต้องเซ็นด้วย SECRET_KEY — เดิมเก็บอีเมลเปล่าๆ
# ใครตั้ง cookie kd_email เป็นอีเมลคนอื่นก็อ่านแชท/ความจำ/เครดิตของคนนั้นได้
from itsdangerous import URLSafeTimedSerializer, BadSignature
_session_signer = URLSafeTimedSerializer(_SECRET_KEY, salt="kd-auth-v1")

def _set_auth_cookies(response, email: str, name: str):
    response.set_cookie("kd_email", _session_signer.dumps(email), max_age=_SESSION_MAX_AGE, **_COOKIE_KW)
    response.set_cookie("kd_name",  _cookie_ascii(name),  max_age=_SESSION_MAX_AGE, **_COOKIE_KW)

def _session_email(request: Request, default: str = "") -> str:
    """อีเมลของผู้ใช้จาก cookie ที่เซ็นแล้วเท่านั้น — cookie ปลอม/หมดอายุ = ไม่ได้ล็อกอิน"""
    raw = request.cookies.get("kd_email") or ""
    if not raw:
        return default
    try:
        email = _session_signer.loads(raw, max_age=_SESSION_MAX_AGE)
    except BadSignature:
        return default
    return str(email).strip() or default

# จำกัดการเดารหัสผ่าน: 8 ครั้ง / 10 นาที ต่อ (IP, อีเมล)
_login_lock = threading.Lock()
_login_fail: dict = {}
_LOGIN_MAX, _LOGIN_WINDOW = 8, 600

_LOGIN_MAX_PER_EMAIL = 30   # ต่ออีเมล ไม่ว่ามาจากกี่ IP (กันเดารหัสจากหลายเครื่อง)

def _prune(store: dict, window: float, now: float):
    """ทิ้ง key ที่ไม่มีเหตุการณ์ในหน้าต่างเวลา — เดิม dict โตไม่หยุด (หนึ่ง key ต่อ IP/อีเมลที่เคยเห็น)"""
    if len(store) > 10000:
        for k in [k for k, v in store.items() if not v or now - v[-1] >= window]:
            store.pop(k, None)

def _login_blocked(key: str) -> bool:
    now = time.time()
    email_key = "email|" + key.split("|", 1)[-1]
    with _login_lock:
        _prune(_login_fail, _LOGIN_WINDOW, now)
        hits = [t for t in _login_fail.get(key, []) if now - t < _LOGIN_WINDOW]
        _login_fail[key] = hits
        ehits = [t for t in _login_fail.get(email_key, []) if now - t < _LOGIN_WINDOW]
        _login_fail[email_key] = ehits
        return len(hits) >= _LOGIN_MAX or len(ehits) >= _LOGIN_MAX_PER_EMAIL

def _login_failed(key: str):
    with _login_lock:
        now = time.time()
        _login_fail.setdefault(key, []).append(now)
        _login_fail.setdefault("email|" + key.split("|", 1)[-1], []).append(now)

_EMAIL_RE = __import__("re").compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


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
        user  = token.get("userinfo") or {}
        email = str(user.get("email") or "").strip().lower()
        # ต้องเป็นอีเมลที่ Google ยืนยันแล้ว — เดิมไม่ตรวจ และถ้าไม่มีอีเมลใช้ "unknown" ร่วมกันทุกคน
        if not email or not _EMAIL_RE.match(email) or user.get("email_verified") is False:
            return RedirectResponse("/static/login.html?error=oauth_unverified")
        name  = str(user.get("name") or email)[:80]
        # ensure_user ให้ 10 เครดิตครั้งแรกครั้งเดียว — เดิมเติม 10 ทุกครั้งที่ login ตอนเครดิตเป็น 0
        # (login ซ้ำ = เครดิตฟรีไม่จำกัด)
        if ensure_user: ensure_user(email)
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
        _set_auth_cookies(response, email, name)
        return response
    except Exception as e:
        print(f"google_callback error: {repr(e)}")
        return RedirectResponse("/static/login.html?error=oauth_error")


@app.get("/me")
async def me(request: Request):
    email = _session_email(request)
    name  = unquote(request.cookies.get("kd_name")  or "")
    if not email:
        q = _quota_status("", request)
        return {"logged_in": False, "free_left": q["free_left"], "free_limit": q["free_limit"]}
    credits = get_credits(email) if get_credits else 0
    until   = get_premium_until(email) if get_premium_until else 0
    q       = _quota_status(email, request)
    return {"logged_in": True, "email": email, "name": name, "credits": credits,
            "premium": until > time.time(), "premium_until": int(until) if until else None,
            "free_left": q["free_left"], "free_limit": q["free_limit"], "run_cost": RUN_COST}


@app.post("/logout")
async def logout():
    r = JSONResponse({"status": "ok"})
    r.delete_cookie("kd_email")
    r.delete_cookie("kd_name")
    return r


# ── EMAIL LOGIN / REGISTER ────────────────────────────────────────
# SECURITY: เดิม /login และ /register รับแค่อีเมล ไม่มีรหัสผ่าน
# = ใครก็เข้าบัญชีใครก็ได้ ตอนนี้ต้องมีรหัสผ่าน (PBKDF2) และจำกัดการเดา
@app.post("/register")
async def register(request: Request, data: dict):
    email    = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    if not _EMAIL_RE.match(email) or len(email) > 254:
        return JSONResponse({"status": "error", "message": "อีเมลดูไม่ถูกรูปแบบนิดหน่อยค่ะ ลองเช็กอีกครั้งนะคะ"}, status_code=400)
    if len(password) < 6:
        return JSONResponse({"status": "error", "message": "ขอรหัสผ่านอย่างน้อย 6 ตัวอักษรนะคะ"}, status_code=400)
    if not set_password:
        return JSONResponse({"status": "error", "message": "ระบบบัญชีขอพักสักครู่นะคะ ลองใหม่อีกทีได้เลยค่ะ"}, status_code=503)
    # 409 บอกได้ว่าอีเมลนี้มีบัญชี — จำกัดต่อ IP ไม่ให้ไล่เช็กอีเมลจำนวนมาก (8 ครั้ง / 10 นาที)
    reg_key = f"reg|{_client_ip(request)}"
    if _login_blocked(reg_key):
        return JSONResponse({"status": "error", "message": "ลองสมัครหลายครั้งแล้ว พักสัก 10 นาทีแล้วค่อยลองใหม่นะคะ"},
                            status_code=429)
    # อีเมลที่มีอยู่แล้ว (เช่นเคยเข้าด้วย Google) ห้ามตั้งรหัสผ่านทับ — ไม่งั้นยึดบัญชีคนอื่นได้
    if (user_exists and user_exists(email)) or not set_password(email, password):
        _login_failed(reg_key)
        return JSONResponse(
            {"status": "error", "message": "อีเมลนี้เคยสมัครไว้แล้วค่ะ เข้าสู่ระบบด้วยรหัสผ่านเดิม หรือด้วย Google ได้เลยนะคะ"},
            status_code=409,
        )
    if ensure_user: ensure_user(email)
    credits = get_credits(email) if get_credits else 0
    r = JSONResponse({"status": "ok", "email": email, "credits": credits})
    _set_auth_cookies(r, email, email)
    return r


@app.post("/login")
async def login_email(request: Request, data: dict):
    email    = str(data.get("email") or "").strip().lower()
    password = str(data.get("password") or "")
    ip       = _client_ip(request)
    key      = f"{ip}|{email}"
    if _login_blocked(key):
        return JSONResponse({"status": "error", "message": "ลองหลายครั้งแล้ว พักสัก 10 นาทีแล้วค่อยลองใหม่นะคะ"}, status_code=429)
    if not email or not password or not verify_password or not verify_password(email, password):
        _login_failed(key)
        return JSONResponse({"status": "error", "message": "อีเมลหรือรหัสผ่านยังไม่ตรงค่ะ ลองอีกครั้งนะคะ"}, status_code=401)
    if ensure_user: ensure_user(email)
    credits = get_credits(email) if get_credits else 0
    r = JSONResponse({"status": "ok", "email": email, "credits": credits})
    _set_auth_cookies(r, email, (str(data.get("name") or "").strip() or email)[:80])
    return r


# ── CHAT STATE ────────────────────────────────────────────────────
_CHAT_STATE_MAX_BYTES = 2 * 1024 * 1024   # กันคนยัด JSON ขนาดใหญ่เข้า SQLite
@app.get("/api/chat-state")
async def get_chat_state(request: Request):
    email = _session_email(request)
    if not email or not load_chat_state:
        return {"state": None}
    raw = load_chat_state(email)
    if not raw:
        return {"state": None}
    try:    return {"state": json.loads(raw)}
    except: return {"state": None}


@app.put("/api/chat-state")
async def put_chat_state(request: Request, data: dict):
    email = _session_email(request)
    if not email or not save_chat_state:
        return JSONResponse({"ok": False, "error": "unauthorized"}, status_code=401)
    # ต้องห่อใน {"state": {...}} เท่านั้น — เดิม fallback เป็นทั้ง body ทำให้สคริปต์รุ่นเก่า (static/app.js
    # ส่ง {session_id, history}) เขียนทับประวัติแชทจริงของบัญชีด้วยรูปแบบที่หน้าเว็บอ่านไม่ได้
    state = data.get("state")
    if not isinstance(state, dict):
        return JSONResponse({"ok": False, "error": "invalid"}, status_code=400)
    blob = json.dumps(state, ensure_ascii=False)
    if len(blob.encode("utf-8")) > _CHAT_STATE_MAX_BYTES:
        return JSONResponse({"ok": False, "error": "chat state too large"}, status_code=413)
    save_chat_state(email, blob)
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
    # "crisis" จากหน้าเว็บเป็นแค่การเดาด้วยคำ (เคยนับ "ตาย" คำเดียว: "แบตมือถือตาย" "ขำจะตาย")
    # ให้เซิร์ฟเวอร์ยืนยันด้วยตัวจับสัญญาณทำร้ายตัวเองก่อน ถึงจะใช้ prompt โหมดวิกฤต
    if vm == "crisis":
        try:
            if not text_risk or text_risk(str(data.get("input") or "")).get("self_harm"):
                return "crisis"              # ไม่มีตัวตรวจ → ปลอดภัยไว้ก่อน
        except Exception:
            return "crisis"
        vm = ""
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
_VALID_ROUTES = ("general", "risk", "civil", "survival", "collapse", "vega")

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
        if isinstance(result.get("state"), dict):
            # ไม่ส่งข้อความ/prompt กลับซ้ำ (เดิม state.input = prompt ภายในทั้งก้อน)
            result["state"] = {k: v for k, v in result["state"].items() if k not in ("input", "raw_input")}
        if "risk" in uni and isinstance(uni["risk"], dict):
            result.setdefault("universal_risk", uni["risk"])
    except Exception as e:
        print(f"⚠ universal_engine error: {e}")          # เดิมส่งข้อความ error ภายในกลับหน้าเว็บ
        result.setdefault("universal_engine_error", True)
    return result


# ── RATE LIMIT — v5.0 ────────────────────────────────────────────
# /run และ /decision เรียก Gemini ทุกครั้ง = แพงสุดในระบบ
# จำกัดต่อ identity (email ถ้า login, ไม่งั้น IP) แบบ in-memory sliding window
# หมายเหตุ: in-memory ใช้ได้กับ single-process deploy เท่านั้น ถ้า scale หลาย
# worker/instance ต้องย้ายไป Redis-based limiter
_rate_lock   = threading.Lock()
_rate_bucket: dict = {}
_RATE_LIMIT_N       = 20     # จำนวนครั้ง
_MAX_INPUT_CHARS    = max(200, int(os.getenv("MAX_INPUT_CHARS", "4000")))
_RATE_LIMIT_WINDOW  = 60     # ต่อกี่วินาที

def _rate_check(identity: str) -> bool:
    now = time.time()
    with _rate_lock:
        _prune(_rate_bucket, _RATE_LIMIT_WINDOW, now)
        hits = _rate_bucket.get(identity, [])
        hits = [t for t in hits if now - t < _RATE_LIMIT_WINDOW]
        if len(hits) >= _RATE_LIMIT_N:
            _rate_bucket[identity] = hits
            return False
        hits.append(now)
        _rate_bucket[identity] = hits
        return True


# ══════════════════════════════════════════════════════════════════
# /run  +  /decision — v5.0
# ══════════════════════════════════════════════════════════════════
@app.post("/run")
@app.post("/decision")
def run_kernel(request: Request, data: dict):
    # sync handler → FastAPI รันใน threadpool: การรอ Gemini (และ time.sleep ตอน retry)
    # จะไม่บล็อก event loop ของ worker เดียวที่ทุกคนใช้ร่วมกัน
    user_input = data.get("input") or data.get("text") or ""
    if not isinstance(user_input, str):
        user_input = str(user_input)
    if not user_input.strip():
        return {"error": "พิมพ์ข้อความก่อนนะคะ"}
    # เดิมไม่จำกัดความยาว — ข้อความ 1MB ถูกส่งเข้า LLM (ค่าใช้จ่าย) และเก็บลง log ทั้งก้อน
    if len(user_input) > _MAX_INPUT_CHARS:
        return JSONResponse({"error": f"ข้อความยาวเกิน {_MAX_INPUT_CHARS} ตัวอักษร — ลองสรุปให้สั้นลงนะคะ"},
                            status_code=413)

    email = _session_email(request, "anonymous")
    _identity = email if email != "anonymous" else _client_ip(request)
    if not _rate_check(_identity):
        return JSONResponse(
            {"error": f"ส่งถี่ไปนิดนึงค่ะ (ได้ {_RATE_LIMIT_N} ครั้งต่อ {_RATE_LIMIT_WINDOW} วินาที) พักสักครู่แล้วส่งใหม่ได้เลยนะคะ"},
            status_code=429
        )

    ticket, denied = _charge(email, request, "run")
    if denied:
        return denied
    # ตัวตนของ session มาจาก server เท่านั้น — เดิมไม่ส่งเลย ทุกคนใช้ "default" ร่วมกัน
    # (state อารมณ์/วิกฤตของคนหนึ่งจะไปติดในคำตอบของอีกคน) และห้ามเชื่อค่าที่ client ส่งมา
    data = {**data, "session_id": _quota_identity(email, request),
            "user_email": email if email != "anonymous" else "",
            # context มาจาก client — ไม่ใช่ dict (list/str) ทำให้ engine ข้างล่างล้มทีละตัวแบบเงียบ
            "context": data.get("context") if isinstance(data.get("context"), dict) else {}}
    reset_fallback_flag()
    # นับโควตาไม่ได้ (ฐานข้อมูลล่ม) → ยังตอบได้ แต่ตอบจากสมการเท่านั้น ไม่เปิดทางให้ใช้ AI ที่มีต้นทุนฟรีไม่จำกัด
    request_no_ai(ticket.get("mode") == "unmetered")
    try:
        result = _run_kernel_impl(data, user_input, email)
    except Exception:
        _refund(ticket)
        raise
    finally:
        request_no_ai(False)
    if not _answered(result):
        _refund(ticket)
    else:
        _settle(ticket)
    if isinstance(result, dict):
        result["quota"] = {**_quota_status(email, request), "charged": ticket["mode"]}
    return result


def _run_kernel_impl(data: dict, user_input: str, email: str):
    # route มาจาก client — ไม่ใช่ชื่อเส้นทางจริง (เช่น dict/list) เคยทำ /run ล่ม 500 ที่ _route_bias
    route   = data.get("route") if data.get("route") in _VALID_ROUTES else "general"
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

    # ── risk จากข้อความ ──────────────────────────────────────────
    # เดิม assess_risk ได้แค่ human_state จาก context → คนที่พิมพ์ว่า "ไม่มีข้าวกิน" ไปทาง general
    # ทำร้ายตัวเอง → collapse (มีสายด่วน) / ขาดปัจจัยพื้นฐานหรือหนักหลายเรื่อง → survival
    if text_risk:
        try:
            tr = text_risk(user_input)
            if route not in ("vega",):
                if tr.get("self_harm"):
                    route = _escalate_route(route, "collapse")
                elif tr.get("basic_needs") or tr.get("level") == "high":
                    route = _escalate_route(route, "survival")
        except Exception: pass

    # ── ตัวเลขจากข้อความ (kernel): risk ของข้อความ + โครงสร้างข้อเสนอเงิน ──────────
    # risk_score ที่ engine คืนคิดจากสถานะร่างกายอย่างเดียว ("อยากตาย" เคยได้ Risk 0)
    k_assess, offer_ctx = {}, ""
    if kernel_assess:
        try:
            k_assess = kernel_assess(user_input, human_state if data.get("context") else None) or {}
        except Exception as e:
            print(f"⚠ kernel_assess: {type(e).__name__}")
    # [Risk: LOW] จากสถานะร่างกาย ขัดกับข้อความที่เสี่ยงชัด → บอก LLM ระดับจากข้อความแทน
    t_risk = k_assess.get("text_risk", 0) or 0
    if t_risk >= 35:
        t_lvl = "CRITICAL" if t_risk >= 75 else "HIGH" if t_risk >= 55 else "MEDIUM"
        if not risk_ctx or "LOW" in risk_ctx or ("MEDIUM" in risk_ctx and t_lvl != "MEDIUM"):
            risk_ctx = f"[Risk: {t_lvl} จากข้อความ]"
    # ถูกทำร้าย/ถูกควบคุมในความสัมพันธ์ → เส้นทางความเสี่ยง (ความปลอดภัยมาก่อน)
    if k_assess.get("relationship") in ("collapse_risk", "critical") and route not in ("vega",):
        route = _escalate_route(route, "risk")
    offer_flags = k_assess.get("offer_flags") or []
    if offer_flags:
        if route not in ("vega",):
            route = _escalate_route(route, "risk")
        offer_ctx = ("[ข้อเสนอมีสัญญาณเสี่ยง: " + ", ".join(OFFER_FLAG_TH.get(f, f) for f in offer_flags) +
                     " — พบบ่อยในการหลอกลงทุน/แชร์ลูกโซ่ ชี้ให้ผู้ใช้เห็นสัญญาณเหล่านี้ตรงๆ อย่างสุภาพ "
                     "ไม่ร่วมตื่นเต้น ไม่ชมว่าเป็นโอกาสดี แนะนำให้ชะลอ ขอเอกสาร และตรวจกับ ก.ล.ต. 1207]")

    # ── collapse ─────────────────────────────────────────────────
    collapse_ctx = ""
    if predict_collapse:
        try:
            c = predict_collapse(human_state.get("risk_score", human_state.get("entropy", 40)))
            # predict_collapse() คืนข้อความ ("high/moderate/low collapse probability")
            # เดิมเช็คแค่ dict จึงไม่เคยเติมบริบทนี้ให้ LLM เลย
            if isinstance(c, dict) and c.get("probability", 0) > 0.6:
                collapse_ctx = f"[Collapse probability: {c['probability']:.0%}]"
            elif isinstance(c, str) and not c.startswith("low"):
                collapse_ctx = f"[Collapse: {c}]"
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
    # ตัวเลขจากเครื่องยนต์ที่ต่อใหม่ (หนี้ · เวลาที่มีจริง · ความสัมพันธ์) — ให้ LLM ใช้ตัวเลขจริงแทนการเดา
    calc_ctx = ""
    if bridge_analyze and not offer_flags:
        try:
            calc_ctx = bridge_analyze(user_input).get("llm_ctx", "")
        except Exception as e:
            print(f"⚠ engine_bridge: {type(e).__name__}")
    extra_ctx = " ".join(p for p in [
        offer_ctx,
        calc_ctx,
        paticca_ctx,
        wise_ctx_str,    # ← v4.9 เพิ่ม yonisomanasikara context
        risk_ctx,
        collapse_ctx,
    ] if p and p not in survivor_ctx)     # orchestrator ใส่บริบทเหตุ-ปัจจัยไว้แล้ว — ไม่ส่งซ้ำ

    effective = ""
    if survivor_ctx:
        effective += survivor_ctx + "\n\n"
    effective += _route_bias(route, user_input)
    if extra_ctx:
        effective += f"\n\n{extra_ctx}"
    # ภาษาของผู้ใช้ (ดูจากข้อความดิบ — prompt ที่ต่อแล้วมีบริบทภาษาไทยปน) ให้ LLM ตอบภาษาเดียวกัน
    if detect_lang:
        u_lang = detect_lang(user_input)
        if u_lang != "th":
            effective += f"\n\n[ภาษาผู้ใช้: {u_lang}]"

    # v5.0: ส่ง context แยกเป็น field ชัดๆ ด้วย ไม่ใช่ฝังใน "input" text อย่างเดียว
    # เผื่อ full_run_decision / DecisionEngine รองรับ field เหล่านี้โดยตรง
    # (ถ้า engine ไม่รู้จัก field พวกนี้ ก็ยังมี text ใน "input" เป็น fallback เดิม)
    payload = {
        **data,
        "voice_mode":     vm,            # ค่าที่เซิร์ฟเวอร์ยืนยันแล้ว ไม่ใช่ค่าที่หน้าเว็บเดามา
        "raw_input":      user_input,
        "input":          effective,
        "history":        history,
        "wise_context":   wise_ctx_str,
        "causal_context": paticca_ctx,
        "core_verdict":   core_result.get("bodhi_verdict", ""),
    }

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
                        f"voice_mode={vm}, "
                        f"tone={'น่ารัก เข้าอกเข้าใจ ไม่เทศน์ ใช้คำลงท้าย ค่ะ' if vm != 'vega' else 'กระชับ ตรงประเด็น วิเคราะห์เชิงกลยุทธ์ ใช้คำลงท้าย ครับ'}"
                    ),
                    history=history,
                    route=route,
                    voice_mode=vm,
                    user_email=email,
                )
            except Exception as e:
                # ไม่มี AI ก็ต้องมีคำตอบ — ปล่อย reply ว่าง ให้ kernel_voice ตอบด้านล่าง
                print(f"⚠ LLM error: {e}")
                reply = ""

        result = {
            "observer":      "KING DIADEM",
            "status":        "SUCCESS",
            # intent ("question"/"joy"/...) ไม่ใช่ route — ใช้แทนได้เฉพาะเมื่อ route ยังเป็น general
            # และเป็นชื่อ route จริง ไม่งั้น survival/collapse ที่ยกระดับไว้จะหาย
            "route":         (intent.get("intent") if route == "general" and isinstance(intent, dict)
                              and intent.get("intent") in ("vega", "civil", "risk", "survival", "collapse")
                              else route),
            "ai_response":   reply,
            "governance":    {"intent": intent, "human_state": human_state},
            "persona":       "VEGA" if vm == "vega" else "LYLA",
            "pattern":       human_state,
            "risk_score":    human_state.get("risk_score", 0),
            "bodhipakkhiya": core_result.get("bodhi_verdict", ""),  # ← v4.9
        }

    # ── KERNEL VOICE: มี AI ก็ดี ไม่มีก็ต้องมีคำตอบ ──────────────────
    # AI ล้ม/โควตาหมด/ไม่มี key/ไม่มีไลบรารี/คำตอบว่าง → ตอบจากสมการของระบบ (deterministic)
    if not isinstance(result, dict):
        result = {}
    ai_text = result.get("ai_response")
    if kernel_compose and (used_fallback() or result.get("error")
                           or not (isinstance(ai_text, str) and ai_text.strip())):
        k_route = result.get("route") if _ROUTE_SEVERITY.get(result.get("route"), -1) > _ROUTE_SEVERITY.get(route, 0) else route
        result.pop("error", None)
        result.update({
            "observer":      result.get("observer") or "KING DIADEM",
            "status":        "SUCCESS",
            "route":         k_route,
            # สถานะร่างกายใช้เฉพาะเมื่อผู้ใช้ส่งมาจริง — context ว่างให้ค่า W 100/Risk 0 ที่ไม่จริง
            "ai_response":   kernel_compose(user_input, route=k_route, voice_mode=vm,
                                            pattern=human_state if data.get("context") else None),
            "answer_source": "kernel",
        })
        result.setdefault("pattern", human_state)
        result.setdefault("risk_score", human_state.get("risk_score", 0))
        result.setdefault("bodhipakkhiya", core_result.get("bodhi_verdict", ""))
    else:
        result.setdefault("answer_source", "llm")

    # risk ที่แสดง = max(สถานะ, สัญญาณในข้อความ) — สมการเดียวกับ kernel_voice.assess
    try:
        engine_risk = float(result.get("risk_score") or 0)
    except (TypeError, ValueError):
        engine_risk = 0.0
    if k_assess.get("text_risk", 0) > engine_risk:
        result["risk_score"] = float(k_assess["text_risk"])
    if offer_flags:
        result["offer_flags"] = offer_flags

    # ── error clean ───────────────────────────────────────────────
    if result.get("error"):
        result["error"] = _friendly_error(str(result["error"]))
        return result

    result["route"]      = result.get("route") or route
    # route ที่ app ยกระดับไว้ (ขาดอาหาร/วิกฤต จากข้อความ, survivor, belief audit) ต้องไม่หาย
    # เพราะ engine ตัดสินจาก pattern อีกชุด — ยกขึ้นได้อย่างเดียว ไม่ลด vega/stable ที่ engine เลือก
    if _ROUTE_SEVERITY.get(route, 0) > _ROUTE_SEVERITY.get(result["route"], 0):
        result["route"] = route
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

    # ── CIVILIZATION GRAPH: ทุกการตัดสินใจเป็น 1 node (ไม่มีข้อความ/อีเมล) ──
    if add_node:
        try:
            k = k_assess
            add_node({"type": "decision", "route": result.get("route"),
                      "source": result.get("answer_source"),
                      "W": k.get("W"), "risk": k.get("risk"), "topics": (k.get("topics") or [])[:3]})
        except Exception as e:
            print(f"⚠ civilization node: {type(e).__name__}")

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
    # COSMIC LATTE CANON GATE — v4.9 (v5.0: no longer a silent no-op)
    # ตาม axiom เดิม: ไม่ block hard ทุกกรณี (Human Final Authority)
    # แต่ severe categories (choice_collapse / coercion / forced_identity)
    # ต้อง block จริง ไม่ใช่แค่ print — ไม่งั้น gate นี้ไม่มีผลอะไรเลย
    # ══════════════════════════════════════════════════════════════
    # coercion_detected ไม่อยู่ใน hard block (เดิมเขียน "coercion" ซึ่งไม่ตรงกับชื่อจริงเลยไม่เคยทำงาน)
    # เพราะ "คุณต้อง..." ในภาษาไทยมักเป็นคำแนะนำด้วยความห่วงใย — flag อย่างเดียวพอ
    _CANON_HARD_BLOCK = {"choice_collapse", "forced_identity"}
    try:
        result = canon_validate(result)
        violations = result.get("canon_violations", []) or []
        if result.get("canon_violation"):
            print(f"⚠ CANON VIOLATION: {violations}")
            # ให้ user เห็นจริง ไม่ใช่แค่ log server-side
            result["canon_notice"] = f"ตรวจพบความเบี่ยงเบนจาก canon: {violations}"
            severe = [v for v in violations if str(v).lower() in _CANON_HARD_BLOCK]
            if severe:
                print(f"⛔ CANON HARD BLOCK: {severe}")
                # ระงับคำตอบ AI แล้วยังต้องมีคำตอบ — ใช้คำตอบจากสมการแทน (เดิมผู้ใช้ได้แค่ "ถูกระงับ")
                b_route = result.get("route", route)
                fallback, source = "ขอโทษนะคะ คำตอบที่เตรียมไว้ยังไม่ดีพอจะส่งให้ ลองเล่าเพิ่มอีกนิดได้ไหมคะ ฉันอยู่ตรงนี้ค่ะ", None
                if kernel_compose:
                    try:
                        fallback = kernel_compose(user_input, route=b_route, voice_mode=vm,
                                                  pattern=human_state if data.get("context") else None)
                        source = "kernel"
                    except Exception as _kc:
                        print(f"⚠ kernel_compose after canon block: {type(_kc).__name__}")
                blocked = {
                    "observer":        "KING DIADEM",
                    "status":          "CANON_BLOCKED",
                    "route":           b_route,
                    "persona":         result.get("persona"),
                    "risk_score":      result.get("risk_score", 0),
                    "ai_response":     fallback,
                    "canon_violation": True,
                    "canon_violations": severe,
                }
                if source:
                    blocked["answer_source"] = source
                return blocked
    except Exception as _cv:
        print(f"⚠ canon_validate error: {_cv}")

    # ── Freedom signal: R = (D × T) / C ──────────────────────────
    # เดิมไม่มีใครเรียก record_choice/record_crisis → C = 0 ตลอด freedom_index() คืน 0 เสมอ
    try:
        if record_crisis and result.get("route") in ("collapse", "crisis"):
            record_crisis()
        if record_choice and result.get("ai_response"):
            offered = (result.get("canon_check") or {}).get("choices_offered", 0) or 0
            record_choice(max(1, int(offered)))
    except Exception:
        pass

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
            result["share_url"]  = _public_url(f"/report/{report_id}")
        except Exception as _re:
            print(f"⚠ report creation failed: {_re}")

    return result


# ── SIMULATE ──────────────────────────────────────────────────────
@app.post("/simulate")
def run_simulate(request: Request, data: dict):
    user_input = str(data.get("input") or "").strip()
    paths      = data.get("paths") or []
    # ทางเลือกสูงสุด 7 ทาง ทางละ ≤ 300 ตัวอักษร — เดิมไม่จำกัดทั้งจำนวนและความยาว (ส่งเข้า LLM ทั้งหมด)
    paths      = [str(p)[:300] for p in (paths if isinstance(paths, list) else [])][:7]
    email      = _session_email(request, "anonymous")
    if not user_input:
        return {"simulation": "พิมพ์สถานการณ์ก่อนนะคะ"}
    if len(user_input) > _MAX_INPUT_CHARS:
        return JSONResponse({"error": f"ข้อความยาวเกิน {_MAX_INPUT_CHARS} ตัวอักษร ลองสรุปให้สั้นลงนะคะ"}, status_code=413)
    if not _rate_check(email if email != "anonymous" else _client_ip(request)):
        return JSONResponse({"error": "ส่งถี่ไปนิดนึงค่ะ พักสักครู่แล้วลองใหม่ได้เลยนะคะ"}, status_code=429)
    ticket, denied = _charge(email, request, "simulate")
    if denied:
        return denied
    reset_fallback_flag()
    request_no_ai(ticket.get("mode") == "unmetered")
    try:
        result = _simulate_impl(user_input, paths, email)
    except Exception:
        _refund(ticket)
        raise
    finally:
        request_no_ai(False)
    if not (isinstance(result, dict) and result.get("source") == "llm" and not used_fallback()):
        _refund(ticket)
    else:
        _settle(ticket)
    result["quota"] = {**_quota_status(email, request), "charged": ticket["mode"]}
    return result


def _simulate_impl(user_input: str, paths: list, email: str) -> dict:
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
        if answer and len(str(answer)) > 10 and not used_fallback():
            return {"simulation": answer, "source": "llm"}
    except Exception as e:
        print(f"simulate LLM: {e}")

    # ไม่มี AI → จำลองจากสมการ (Downside ก่อน · ทางที่ย้อนกลับได้ชนะ)
    if kernel_simulate:
        try:
            return {"simulation": kernel_simulate(user_input, paths), "source": "kernel"}
        except Exception as e:
            print(f"kernel simulate: {e}")

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
    email = _session_email(request) or data.get("email", "")
    plan  = data.get("plan", "basic")
    if plan == "civilization":
        price_id = os.getenv("STRIPE_PREMIUM_PRICE_ID") or os.getenv("STRIPE_PRICE_ID")
    else:
        price_id = os.getenv("STRIPE_PRICE_ID") or os.getenv("STRIPE_PREMIUM_PRICE_ID")
    if not price_id:
        return JSONResponse({"error": "ยังไม่ได้ตั้งค่า STRIPE_PRICE_ID"}, status_code=503)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            customer_email=email or None,
            success_url=_public_url("/?payment=success"),
            cancel_url=_public_url("/?payment=cancel"),
            client_reference_id=email or None,
        )
        return {"url": session.url}
    except Exception as e:
        # ข้อความ error ของ Stripe อาจมีบางส่วนของ key/request id — log ฝั่ง server เท่านั้น
        print(f"⚠ stripe checkout error: {type(e).__name__}: {e}")
        return JSONResponse({"error": "ระบบชำระเงินขัดข้องชั่วคราวค่ะ ยังไม่มีการตัดเงิน ลองใหม่อีกครั้งนะคะ"}, status_code=502)


@app.post("/create-subscription")
async def create_subscription(request: Request):
    email    = _session_email(request)
    price_id = os.getenv("STRIPE_PREMIUM_PRICE_ID") or os.getenv("STRIPE_PRICE_ID")
    if not price_id:
        return JSONResponse({"error": "ยังไม่ได้ตั้งค่า STRIPE_PRICE_ID"}, status_code=503)
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{"price": price_id, "quantity": 1}],
            mode="subscription",
            customer_email=email or None,
            success_url=_public_url("/?payment=success"),
            cancel_url=_public_url("/?payment=cancel"),
            client_reference_id=email or None,
        )
        return {"url": session.url}
    except Exception as e:
        # ข้อความ error ของ Stripe อาจมีบางส่วนของ key/request id — log ฝั่ง server เท่านั้น
        print(f"⚠ stripe checkout error: {type(e).__name__}: {e}")
        return JSONResponse({"error": "ระบบชำระเงินขัดข้องชั่วคราวค่ะ ยังไม่มีการตัดเงิน ลองใหม่อีกครั้งนะคะ"}, status_code=502)


# ── STRIPE WEBHOOK ────────────────────────────────────────────────
# - ทุก event ถูก claim ด้วย event.id ก่อน → Stripe ส่งซ้ำ (retry) จะไม่เติมเครดิตซ้ำ
# - subscription: checkout สำเร็จ / invoice.paid ต่ออายุ premium · subscription ถูกยกเลิก → หมด premium
#   (ใน Stripe Dashboard ต้องเปิด event: checkout.session.completed, invoice.paid,
#    customer.subscription.deleted ให้ endpoint นี้)
_PREMIUM_GRACE = 2 * 86400

def _grant_once(email: str, credits: int, reason: str, ref: str) -> None:
    """เครดิตจาก Stripe: ครั้งเดียวต่อ checkout session — ไม่มีฐานข้อมูล = error ให้ Stripe ส่งใหม่"""
    if not add_credits_once:
        raise RuntimeError("database unavailable")
    if not ref:
        raise RuntimeError("stripe object without id")
    add_credits_once(email, credits, reason, ref)


def _handle_stripe_event(event) -> None:
    etype = event["type"]
    obj   = event["data"]["object"]
    now   = time.time()

    if etype == "checkout.session.completed":
        if obj.get("payment_status") not in ("paid", "no_payment_required"):
            return
        # client_reference_id / customer_email มาจาก session ของเราตรงๆ (ตรงกับบัญชีที่ใช้อยู่)
        # อีเมลที่พิมพ์ในหน้า Stripe (customer_details) ตัวพิมพ์อาจต่างจากบัญชี → ใช้เป็นทางสุดท้ายแบบ lower
        email = (obj.get("client_reference_id")
                 or obj.get("customer_email")
                 or str((obj.get("customer_details") or {}).get("email") or "").strip().lower())
        if not email:
            print(f"⚠ stripe checkout without email: {obj.get('id')}")
            return
        meta = obj.get("metadata") or {}
        if meta.get("kind") == "wallet_topup":
            # จำนวนเครดิตคิดจากยอดที่ Stripe เก็บเงินจริง (amount_total) ไม่ใช่ค่าที่ client ส่ง
            if str(obj.get("currency", "")).lower() != "thb":
                print(f"⚠ wallet topup in unexpected currency: {obj.get('currency')}")
                return
            baht    = int(obj.get("amount_total") or 0) / 100
            credits = int(baht / THB_PER_CREDIT + 1e-9)
            target  = meta.get("email") or email
            if credits > 0:
                _grant_once(target, credits, "topup", obj.get("id"))
            return
        # ── SECURITY: credit ต้องผูกกับ price_id ที่ Stripe ยืนยันจริง
        # ห้ามคำนวณจาก quantity ที่ client ส่งมา เพราะแก้ค่านั้นได้ก่อนถึง checkout
        _CREDITS_PER_PRICE = {
            os.getenv("STRIPE_PRICE_ID"):         10,
            os.getenv("STRIPE_PREMIUM_PRICE_ID"): 100,
        }
        total_credits = 0
        items = stripe.checkout.Session.list_line_items(obj["id"])
        for i in items.get("data", []):
            price_id = (i.get("price") or {}).get("id")
            per_unit = _CREDITS_PER_PRICE.get(price_id, 0)
            if per_unit:
                total_credits += per_unit * int(i.get("quantity", 1) or 1)
            else:
                print(f"⚠ unknown price_id in webhook: {price_id} — 0 credits granted")
        if ensure_user: ensure_user(email)
        if total_credits > 0:
            _grant_once(email, total_credits, "stripe_plan", obj.get("id"))
        if obj.get("mode") == "subscription" and set_premium_until:
            set_premium_until(email, now + 32 * 86400 + _PREMIUM_GRACE,
                              obj.get("customer"), obj.get("subscription"))

    elif etype == "invoice.paid":
        customer = obj.get("customer")
        # ใช้การจับคู่ customer → บัญชีที่บันทึกไว้ตอนสมัครก่อน (ตรงตัว) แล้วค่อย customer_email
        email = ((email_for_stripe_customer(customer) if email_for_stripe_customer else None)
                 or str(obj.get("customer_email") or "").strip().lower() or None)
        if not email or not set_premium_until:
            return
        # ถามสถานะจริงจาก Stripe — event มาไม่เรียงลำดับได้: invoice.paid ฉบับเก่าที่มาถึง
        # หลัง subscription.deleted เคยคืน premium ให้บัญชีที่ยกเลิกไปแล้ว
        sub_id = (obj.get("subscription")
                  or (((obj.get("parent") or {}).get("subscription_details") or {}).get("subscription")))
        if not sub_id:
            return                                    # ใบแจ้งหนี้ครั้งเดียว ไม่ใช่สมาชิก
        sub = stripe.Subscription.retrieve(sub_id)    # ล้ม → 500 → Stripe ส่งใหม่
        if sub.get("status") not in ("active", "trialing"):
            return
        items = ((sub.get("items") or {}).get("data") or [])
        period_end = max([sub.get("current_period_end") or 0] +
                         [(it.get("current_period_end") or 0) for it in items])
        if period_end:
            set_premium_until(email, max(period_end, now) + _PREMIUM_GRACE, customer, sub_id)

    elif etype == "customer.subscription.deleted":
        customer = obj.get("customer")
        email = email_for_stripe_customer(customer) if email_for_stripe_customer else None
        if email and set_premium_until:
            # ยกเลิกเฉพาะ subscription ที่ผูกกับ premium ตอนนี้ — ยกเลิกอันเก่าหลังสมัครใหม่ต้องไม่ตัดอันใหม่
            current = premium_subscription(email) if premium_subscription else None
            if current and obj.get("id") and current != obj.get("id"):
                return
            set_premium_until(email, now, customer, obj.get("id"))


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig     = request.headers.get("stripe-signature", "")
    secret  = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    if not secret:
        return JSONResponse({"error": "webhook not configured"}, status_code=500)
    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except Exception:
        return JSONResponse({"error": "invalid signature"}, status_code=400)

    # บันทึกว่า "เสร็จ" หลังประมวลผลสำเร็จเท่านั้น — ล่มกลางทาง Stripe ส่งใหม่แล้วทำต่อได้
    # ส่วนการให้เครดิตกันซ้ำด้วย (reason, checkout id) ใน transaction เดียวกับยอด จึงประมวลผลซ้ำได้ปลอดภัย
    event_id = event.get("id", "")
    if stripe_event_done and stripe_event_done(event_id):
        return {"status": "duplicate"}
    try:
        # stripe SDK เป็น blocking I/O → ย้ายออกจาก event loop
        await run_in_threadpool(_handle_stripe_event, event)
        if mark_stripe_event:
            mark_stripe_event(event_id, event.get("type", ""))
    except Exception as e:
        print(f"❌ stripe webhook {event.get('type')} {event_id}: {type(e).__name__}")
        return JSONResponse({"error": "processing failed"}, status_code=500)
    return {"status": "ok"}


# ── WALLET ────────────────────────────────────────────────────────
# ตัวตนมาจาก cookie ที่เซ็นแล้วเท่านั้น — ไม่รับอีเมลจาก body (เดิม wallet.html ส่งอีเมลใครก็ได้มา)
_TOPUP_MIN_THB, _TOPUP_MAX_THB = 20, 10000   # Stripe เก็บ THB ขั้นต่ำ ~฿10; ตั้ง ฿20 เผื่อค่าธรรมเนียม

@app.get("/wallet/balance")
@app.post("/wallet/balance")
async def wallet_balance(request: Request):
    email = _session_email(request)
    if not email:
        return JSONResponse({"error": "เข้าสู่ระบบก่อนนะคะ", "code": "login_required"}, status_code=401)
    q = _quota_status(email, request)
    hist = credit_history(email, 20) if credit_history else []
    return {
        "email": email, "credits": q["credits"] or 0, "total_credit": q["credits"] or 0,
        "thb_per_credit": THB_PER_CREDIT, "run_cost": RUN_COST,
        "premium": q["premium"], "free_left": q["free_left"], "free_limit": q["free_limit"],
        "topup_min": _TOPUP_MIN_THB, "topup_max": _TOPUP_MAX_THB,
        "history": hist,
    }


@app.post("/wallet/topup")
async def wallet_topup(request: Request, data: dict):
    """สร้าง Stripe Checkout สำหรับเติมเครดิต — เครดิตเข้าบัญชีเมื่อ webhook ยืนยันการจ่ายเงินเท่านั้น"""
    email = _session_email(request)
    if not email:
        return JSONResponse({"error": "เข้าสู่ระบบก่อนแล้วค่อยเติมเครดิตนะคะ", "code": "login_required"}, status_code=401)
    if not os.getenv("STRIPE_SECRET_KEY"):
        return JSONResponse({"error": "ระบบชำระเงินยังไม่เปิดใช้ค่ะ ขออภัยนะคะ"}, status_code=503)
    try:
        baht = int(float(data.get("amount") or 0))
    except (TypeError, ValueError):
        baht = 0
    if baht < _TOPUP_MIN_THB or baht > _TOPUP_MAX_THB:
        return JSONResponse({"error": f"เติมได้ครั้งละ ฿{_TOPUP_MIN_THB}–฿{_TOPUP_MAX_THB:,} นะคะ"}, status_code=400)
    credits = int(baht / THB_PER_CREDIT + 1e-9)
    try:
        session = await run_in_threadpool(lambda: stripe.checkout.Session.create(
            mode="payment",
            line_items=[{"quantity": 1, "price_data": {
                "currency": "thb", "unit_amount": baht * 100,
                "product_data": {"name": f"KING DIADEM — {credits:,} เครดิต"},
            }}],
            customer_email=email,
            client_reference_id=email,
            metadata={"kind": "wallet_topup", "email": email, "credits": str(credits)},
            success_url=_public_url("/static/wallet.html?topup=success"),
            cancel_url=_public_url("/static/wallet.html?topup=cancel"),
        ))
        return {"url": session.url, "credits": credits, "amount": baht}
    except Exception as e:
        print(f"⚠ wallet topup error: {e}")
        return JSONResponse({"error": "เปิดหน้าชำระเงินไม่สำเร็จค่ะ ยังไม่มีการตัดเงิน ลองใหม่อีกครั้งนะคะ"}, status_code=502)


@app.get("/credits")
async def get_user_credits(request: Request):
    email = _session_email(request)
    if not email:
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    credits = get_credits(email) if get_credits else 0
    return {"email": email, "credits": credits}


# ── ANALYZE IMAGE ─────────────────────────────────────────────────
_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10MB
_ALLOWED_IMAGE_MIME = ("image/jpeg", "image/png", "image/webp")

@app.post("/analyze-image")
async def analyze_image(request: Request, file: UploadFile = File(...)):
    # อ่านภาพต้องใช้ AI จริง — ไม่มีสมการแทนได้ จึงบอกตรงๆ แทนการเดา
    if not llm or ai_disabled():
        return JSONResponse({"error": "ตอนนี้ระบบอ่านภาพไม่ได้ (ไม่มี AI) — พิมพ์เล่าสถานการณ์แทนได้เลยค่ะ"},
                            status_code=503)
    email = _session_email(request)
    if not _rate_check(email or _client_ip(request)):
        return JSONResponse({"error": "ส่งถี่ไปนิดนึงค่ะ พักสักครู่แล้วลองใหม่ได้เลยนะคะ"}, status_code=429)
    if file.content_type not in _ALLOWED_IMAGE_MIME:
        return JSONResponse(
            {"error": "ตอนนี้รองรับภาพ jpeg, png และ webp ค่ะ ลองเปลี่ยนไฟล์ดูนะคะ"},
            status_code=400
        )
    try:
        data = await file.read(_MAX_IMAGE_BYTES + 1)
        if len(data) > _MAX_IMAGE_BYTES:
            return JSONResponse(
                {"error": f"ไฟล์ใหญ่ไปนิดค่ะ ขอไม่เกิน {_MAX_IMAGE_BYTES // (1024*1024)}MB นะคะ"},
                status_code=413
            )
        mime = file.content_type or "image/jpeg"
    except Exception as e:
        print(f"⚠ analyze_image read error: {e}")
        return JSONResponse({"error": _friendly_error(str(e))}, status_code=500)
    ticket, denied = _charge(email, request, "analyze_image")
    if denied:
        return denied
    if ticket.get("mode") == "unmetered":          # นับโควตาไม่ได้ → ไม่เปิด AI ฟรีไม่จำกัด
        return JSONResponse({"error": "ระบบนับโควตาขอพักสักครู่ค่ะ ลองใหม่อีกทีนะคะ"}, status_code=503)
    try:
        analysis_text = await run_in_threadpool(_analyze_image_sync, data, mime)
    except Exception as e:
        print(f"⚠ analyze_image error: {e}")
        _refund(ticket)
        return JSONResponse({"error": _friendly_error(str(e))}, status_code=500)
    if analysis_text == _IMAGE_EMPTY:
        _refund(ticket)
    else:
        _settle(ticket)
    return {"analysis": analysis_text, "filename": file.filename,
            "quota": {**_quota_status(email, request), "charged": ticket["mode"]}}


_IMAGE_EMPTY = "LYLA วิเคราะห์ภาพไม่ได้ค่ะ — อาจถูก Gemini safety block หรือภาพไม่ชัด"

def _analyze_image_sync(data: bytes, mime: str) -> str:
    """เรียก Gemini vision แบบ blocking — รันใน threadpool ไม่บล็อก event loop"""
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
    # ลำดับเดียวกับ LLM หลัก (GEMINI_MODEL + GEMINI_FALLBACK_MODELS) — เดิมตายตัว 2 รุ่น 2.0
    chain  = [getattr(_llm, "vision_model", None) or getattr(_llm, "model", None) or "gemini-2.0-flash"]
    chain += list(getattr(_llm, "MODEL_FALLBACK_CHAIN", []) or ["gemini-2.0-flash-lite"])
    models = list(dict.fromkeys(m for m in chain if m))
    last = None
    for m in models:
        try:
            resp = _llm.client.models.generate_content(model=m, contents=contents, config=cfg)
            break
        except Exception as e:
            last = e
    else:
        raise last
    try:
        text = resp.text or ""
    except Exception:
        parts = getattr(getattr(resp, "candidates", [None])[0], "content", None)
        text = " ".join(p.text for p in (getattr(parts, "parts", []) or []) if hasattr(p, "text"))
    return text.strip() or _IMAGE_EMPTY


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
    email      = _session_email(request, "anonymous")
    if not _rate_check(email if email != "anonymous" else _client_ip(request)):
        return JSONResponse({"error": "ส่งถี่ไปนิดนึงค่ะ พักสักครู่แล้วลองใหม่ได้เลยนะคะ"}, status_code=429)
    user_input = data.get("input", "")
    result     = data.get("result", {})
    if not user_input or not isinstance(result, dict) or not result:
        return JSONResponse({"error": "input and result required"}, status_code=400)
    try:
        # เนื้อหามาจาก client → ติดป้าย user_submitted (ไม่ให้ดูเหมือนระบบตัดสิน)
        report_id = _create_report(user_email=email, user_input=user_input, result=result, source="user")
        return {
            "report_id":  report_id,
            "report_url": f"/report/{report_id}",
            "share_url":  _public_url(f"/report/{report_id}"),
        }
    except Exception as e:
        print(f"⚠ manual report failed: {type(e).__name__}")
        return JSONResponse({"error": "report_failed"}, status_code=500)
