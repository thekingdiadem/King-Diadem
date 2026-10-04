// static/decision.js
// KING DIADEM™ — Decision Engine Interface v2.0
// Real backend call → KD:thinking → KD:response → KD:decision chain

(function () {
  // ข้อมูลจาก backend ห้ามเข้า innerHTML ดิบ (คำตอบ LLM / ข้อความ error มี < > ได้)
  const _e = (v) => String(v ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[c]);

  // ─── CONFIG ───────────────────────────────────────────────────────────────
  const API_ENDPOINT = "/run";
  const TIMEOUT_MS   = 15000;

  // ─── STATE ────────────────────────────────────────────────────────────────
  let _running = false;
  let _lastPayload = null;

  // ─── DOM HELPERS ──────────────────────────────────────────────────────────
  function byId(id) {
    return (window.KD?.byId || document.getElementById.bind(document))(id);
  }

  function getInput() {
    const el = byId("input");
    return el ? (el.value || el.textContent || "").trim() : "";
  }

  function setStatus(msg, type = "info") {
    const el = byId("status");
    if (!el) return;
    const colors = { info: "#5a6480", error: "#f87171", ok: "#4ade80", thinking: "#c8a440" };
    el.textContent = msg;
    el.style.color = colors[type] || colors.info;
  }

  function setButtonState(loading) {
    const btn = byId("submit") || byId("run") || byId("btn-run");
    if (!btn) return;
    btn.disabled = loading;
    btn.textContent = loading ? "PROCESSING..." : (btn.dataset.label || "RUN");
    btn.style.opacity = loading ? "0.5" : "1";
  }

  // ─── KD EVENT DISPATCH ────────────────────────────────────────────────────
  function dispatch(name, detail = {}) {
    window.dispatchEvent(new CustomEvent(name, { detail }));
  }

  // ─── FETCH WITH TIMEOUT ───────────────────────────────────────────────────
  async function fetchDecision(input, userEmail = null) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

    const body = { input };
    if (userEmail) body.user_email = userEmail;

    try {
      const res = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        signal: controller.signal,
      });

      clearTimeout(timer);

      if (!res.ok) {
        const errText = await res.text().catch(() => `HTTP ${res.status}`);
        throw new Error(`Backend error ${res.status}: ${errText}`);
      }

      return await res.json();
    } catch (err) {
      clearTimeout(timer);
      if (err.name === "AbortError") throw new Error("Request timeout — backend took too long");
      throw err;
    }
  }

  // ─── PARSE RESPONSE ───────────────────────────────────────────────────────
  function normalizePayload(raw) {
    // flatten various backend response shapes into one clean object
    const output    = raw.output    || raw.decision || {};
    const consensus = raw.consensus || {};
    const council   = raw.council   || {};
    const risk      = raw.risk      || {};

    return {
      // top-level passthrough
      ...raw,

      // normalized fields
      output: {
        action:     output.action     || consensus.final_action || raw.action || "—",
        message:    output.message    || consensus.message      || raw.message || "",
        confidence: output.confidence ?? consensus.confidence   ?? raw.confidence ?? null,
        risk:       output.risk       ?? risk.risk_score        ?? raw.risk_score ?? null,
        blocked:    output.blocked    ?? raw.blocked            ?? false,
        reason:     output.reason     || consensus.reason       || raw.reason || "",
        route:      output.route      || raw.route              || "",
        axiom:      output.axiom      || raw.axiom              || null,
        waterline:  output.waterline  ?? risk.waterline         ?? raw.waterline ?? null,
      },
      consensus,
      council,
      risk,
    };
  }

  // ─── RENDER DECISION ──────────────────────────────────────────────────────
  function renderDecision(payload) {
    const el = byId("decision");
    if (!el) return;

    const o = payload.output;
    const blocked = o.blocked;

    // color scheme
    const riskColors = { low: "#4ade80", medium: "#f59e0b", high: "#f87171", critical: "#dc2626" };
    const riskLabel  = String(o.risk || "").toLowerCase();
    const riskColor  = riskColors[riskLabel] || (
      o.risk != null
        ? (parseFloat(o.risk) > 0.7 ? riskColors.high : parseFloat(o.risk) > 0.4 ? riskColors.medium : riskColors.low)
        : "#5a6480"
    );

    const confPct = o.confidence != null
      ? Math.max(0, Math.min(100, Math.round((o.confidence > 1 ? o.confidence : o.confidence * 100)) || 0))
      : null;

    el.innerHTML = `
<div style="
  font-family:'JetBrains Mono','Fira Code',monospace;
  background:linear-gradient(135deg,#0a0d14,#060810);
  border:1px solid #1e2535;
  border-left:3px solid ${blocked ? "#f87171" : "#c8a440"};
  border-radius:8px;
  padding:16px 18px;
  color:#cdd6f4;
  font-size:11px;
  position:relative;
  overflow:hidden;
">
  <div style="position:absolute;top:-30px;right:-30px;width:100px;height:100px;
    background:radial-gradient(circle,rgba(200,164,64,0.05),transparent 70%);pointer-events:none;"></div>

  <div style="font-size:8px;letter-spacing:3px;color:${blocked ? "#f87171" : "#c8a440"};margin-bottom:12px;">
    ${blocked ? "⊘ BLOCKED — FATE™ GATE FAILED" : "◆ FATE™ DECISION OUTPUT"}
  </div>

  <div style="font-size:15px;color:#e8d5a3;font-weight:700;letter-spacing:1px;margin-bottom:14px;">
    ${_e(o.action)}
  </div>

  ${o.message ? `
  <div style="color:#8899bb;line-height:1.6;margin-bottom:12px;font-size:10px;">
    ${_e(o.message)}
  </div>` : ""}

  <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:12px;">
    <div style="background:#0d111c;border:1px solid #1a2030;border-radius:5px;padding:9px 11px;">
      <div style="font-size:7px;color:#5a6480;letter-spacing:2px;margin-bottom:4px;">RISK</div>
      <div style="display:flex;align-items:center;gap:5px;">
        <div style="width:7px;height:7px;border-radius:50%;background:${riskColor};box-shadow:0 0 5px ${riskColor}88;"></div>
        <span style="color:${riskColor};font-weight:600;text-transform:uppercase;font-size:11px;">
          ${_e(riskLabel || (o.risk ?? "n/a"))}
        </span>
      </div>
    </div>

    <div style="background:#0d111c;border:1px solid #1a2030;border-radius:5px;padding:9px 11px;">
      <div style="font-size:7px;color:#5a6480;letter-spacing:2px;margin-bottom:4px;">CONFIDENCE</div>
      ${confPct != null ? `
        <div style="color:#c8a440;font-weight:600;font-size:13px;margin-bottom:4px;">${confPct}%</div>
        <div style="background:#1a2030;border-radius:2px;height:3px;">
          <div style="width:${confPct}%;height:100%;background:#c8a440;"></div>
        </div>
      ` : `<span style="color:#555;font-size:11px;">n/a</span>`}
    </div>
  </div>

  ${o.route ? `
  <div style="margin-bottom:10px;">
    <span style="font-size:7px;color:#5a6480;letter-spacing:2px;">ROUTE → </span>
    <span style="color:#3a86f5;letter-spacing:1px;">${_e(o.route)}</span>
  </div>` : ""}

  ${o.waterline != null ? `
  <div style="margin-bottom:10px;">
    <span style="font-size:7px;color:#5a6480;letter-spacing:2px;">WATERLINE → </span>
    <span style="color:${o.waterline ? "#4ade80" : "#f87171"};">
      ${o.waterline ? "✓ INTACT" : "⚠ BREACH"}
    </span>
  </div>` : ""}

  ${o.reason ? `
  <div style="background:#080b13;border:1px solid #141926;border-radius:5px;padding:9px 11px;margin-bottom:${o.axiom ? "10px" : "0"};">
    <div style="font-size:7px;color:#5a6480;letter-spacing:2px;margin-bottom:4px;">REASON</div>
    <div style="color:#8899bb;line-height:1.6;">${_e(o.reason)}</div>
  </div>` : ""}

  ${o.axiom ? `
  <div style="margin-top:10px;padding:7px 11px;border-left:2px solid #3a86f5;font-size:9px;color:#3a86f5;font-style:italic;">
    ${_e(o.axiom)}
  </div>` : ""}

  <div style="margin-top:12px;padding-top:8px;border-top:1px solid #0f1420;
    font-size:7px;color:#1e2535;letter-spacing:2px;text-align:right;">
    KING DIADEM™ · FATE™ A6 · HUMAN FINAL AUTHORITY
  </div>
</div>`;
  }

  // ─── MAIN RUN ─────────────────────────────────────────────────────────────
  async function runDecision(overrideInput = null) {
    if (_running) return;

    const input = overrideInput || getInput();
    if (!input) {
      setStatus("Input required", "error");
      return;
    }

    _running = true;
    setButtonState(true);
    setStatus("Dispatching to council...", "thinking");

    // 1. Signal orbit: thinking phase
    const councilPersonas = ["LYLA", "VEGA", "TITAN", "PATICCA", "COSMOS"];
    dispatch("KD:thinking", { personas: councilPersonas, phase: "thinking" });

    try {
      // 2. Get user email if available
      const userEmail = window.KD?.userEmail || null;

      // 3. Backend call
      const raw = await fetchDecision(input, userEmail);

      // 4. Normalize
      const payload = normalizePayload(raw);
      _lastPayload = payload;

      // 5. Render decision card
      renderDecision(payload);

      // 6. Dispatch full response (→ galaxy_council.js, galaxy_decision.js)
      dispatch("KD:response", payload);

      // 7. Orbit: consensus
      dispatch("KD:thinking", { phase: "consensus" });

      // 8. Inject thought label
      if (window.injectThought) {
        const action = payload.output.action;
        if (action && action !== "—") {
          window.injectThought(`→ ${action}`, "TITAN");
        }
      }

      setStatus("Decision complete", "ok");

    } catch (err) {
      console.error("[KD:decision]", err);
      setStatus(`Error: ${err.message}`, "error");

      // show error state in decision panel
      const el = byId("decision");
      if (el) {
        el.innerHTML = `
<div style="
  font-family:'JetBrains Mono',monospace;
  background:#0a0508;
  border:1px solid #3a1515;
  border-left:3px solid #f87171;
  border-radius:8px;
  padding:16px 18px;
  color:#f87171;
  font-size:10px;
">
  <div style="font-size:8px;letter-spacing:3px;margin-bottom:8px;">⊘ SYSTEM ERROR</div>
  <div style="color:#cc5555;">${_e(err.message)}</div>
  <div style="margin-top:10px;font-size:8px;color:#5a2020;letter-spacing:2px;">
    FATE™ A5 — EXPLAINABILITY ENFORCED
  </div>
</div>`;
      }

      dispatch("KD:thinking", { phase: "idle" });
    } finally {
      _running = false;
      setButtonState(false);
    }
  }

  // ─── PUBLIC API ───────────────────────────────────────────────────────────
  window.runDecision  = runDecision;
  window.runDicision  = runDecision;   // typo compat alias

  window.KDDecision = {
    run: runDecision,
    last: () => _lastPayload,
  };

  // ─── KEYBOARD SHORTCUT ────────────────────────────────────────────────────
  document.addEventListener("keydown", (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
      e.preventDefault();
      runDecision();
    }
  });

})();
