// static/galaxy_decision.js
// KING DIADEM™ — Decision Summary Renderer
// Renders final decision card into #summary + dispatches KD:decision for galaxy_scene.js

(function () {
  const RISK_COLOR = {
    low: "#4ade80",
    medium: "#f59e0b",
    high: "#f87171",
    critical: "#dc2626",
  };

  const CONFIDENCE_BAR_COLOR = (v) => {
    if (v >= 0.8) return "#c8a440";
    if (v >= 0.5) return "#3a86f5";
    return "#f87171";
  };

  function parseConfidence(raw) {
    if (raw == null || raw === "n/a") return null;
    const n = parseFloat(raw);
    return isNaN(n) ? null : n > 1 ? n / 100 : n;
  }

  function parseRisk(raw) {
    if (raw == null || raw === "n/a") return { label: "n/a", color: "#888" };
    const s = String(raw).toLowerCase();
    if (RISK_COLOR[s]) return { label: s, color: RISK_COLOR[s] };
    const n = parseFloat(raw);
    if (!isNaN(n)) {
      if (n <= 0.3) return { label: "low", color: RISK_COLOR.low };
      if (n <= 0.6) return { label: "medium", color: RISK_COLOR.medium };
      if (n <= 0.85) return { label: "high", color: RISK_COLOR.high };
      return { label: "critical", color: RISK_COLOR.critical };
    }
    return { label: s, color: "#aaa" };
  }

  function buildCard(output, consensus, payload) {
    const action =
      output.action || consensus.final_action || payload.final_action || "—";
    const reason = output.reason || consensus.reason || payload.reason || "—";
    const route = payload.route || output.route || "—";
    const waterline =
      payload.waterline ?? payload.risk?.waterline ?? null;
    const axiom = payload.axiom || output.axiom || null;

    const rawRisk =
      output.risk ?? payload.risk?.risk_score ?? consensus.risk ?? null;
    const risk = parseRisk(rawRisk);

    const rawConf =
      output.confidence ?? consensus.confidence ?? payload.confidence ?? null;
    const conf = parseConfidence(rawConf);
    const confPct = conf != null ? Math.round(conf * 100) : null;
    const confColor = conf != null ? CONFIDENCE_BAR_COLOR(conf) : "#555";

    const ts = new Date().toISOString().replace("T", " ").slice(0, 19);

    return `
<div class="kd-decision-card" style="
  background: linear-gradient(135deg, #0a0d14 0%, #060810 100%);
  border: 1px solid #1e2535;
  border-left: 3px solid #c8a440;
  border-radius: 8px;
  padding: 18px 20px;
  font-family: 'JetBrains Mono', 'Fira Code', monospace;
  color: #cdd6f4;
  position: relative;
  overflow: hidden;
">
  <!-- background glow -->
  <div style="
    position:absolute; top:-40px; right:-40px;
    width:120px; height:120px;
    background: radial-gradient(circle, rgba(200,164,64,0.06) 0%, transparent 70%);
    pointer-events:none;
  "></div>

  <!-- header -->
  <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px;">
    <span style="font-size:9px; letter-spacing:3px; color:#c8a440; text-transform:uppercase;">
      ◆ FATE™ DECISION OUTPUT
    </span>
    <span style="font-size:9px; color:#3d4560;">${ts} UTC</span>
  </div>

  <!-- action -->
  <div style="margin-bottom:14px;">
    <div style="font-size:9px; color:#5a6480; letter-spacing:2px; margin-bottom:4px;">FINAL ACTION</div>
    <div style="font-size:15px; color:#e8d5a3; font-weight:600; letter-spacing:1px;">${action}</div>
  </div>

  <!-- risk + confidence row -->
  <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:14px;">
    <!-- risk -->
    <div style="
      background:#0d111c;
      border:1px solid #1a2030;
      border-radius:6px;
      padding:10px 12px;
    ">
      <div style="font-size:8px; color:#5a6480; letter-spacing:2px; margin-bottom:6px;">RISK LEVEL</div>
      <div style="display:flex; align-items:center; gap:6px;">
        <div style="width:8px; height:8px; border-radius:50%; background:${risk.color}; box-shadow:0 0 6px ${risk.color}88;"></div>
        <span style="font-size:13px; color:${risk.color}; font-weight:600; text-transform:uppercase;">${risk.label}</span>
      </div>
    </div>

    <!-- confidence -->
    <div style="
      background:#0d111c;
      border:1px solid #1a2030;
      border-radius:6px;
      padding:10px 12px;
    ">
      <div style="font-size:8px; color:#5a6480; letter-spacing:2px; margin-bottom:6px;">CONFIDENCE</div>
      ${confPct != null ? `
        <div style="font-size:13px; color:${confColor}; font-weight:600; margin-bottom:5px;">${confPct}%</div>
        <div style="background:#1a2030; border-radius:2px; height:3px; overflow:hidden;">
          <div style="width:${confPct}%; height:100%; background:${confColor}; transition:width 0.6s ease;"></div>
        </div>
      ` : `<span style="font-size:13px; color:#555;">n/a</span>`}
    </div>
  </div>

  <!-- route -->
  ${route !== "—" ? `
  <div style="margin-bottom:12px;">
    <span style="font-size:8px; color:#5a6480; letter-spacing:2px;">ROUTE → </span>
    <span style="font-size:11px; color:#3a86f5; letter-spacing:1px;">${route}</span>
  </div>` : ""}

  <!-- waterline -->
  ${waterline != null ? `
  <div style="margin-bottom:12px;">
    <span style="font-size:8px; color:#5a6480; letter-spacing:2px;">WATERLINE → </span>
    <span style="font-size:11px; color:${waterline ? "#4ade80" : "#f87171"};">
      ${waterline ? "✓ INTACT" : "⚠ BREACH DETECTED"}
    </span>
  </div>` : ""}

  <!-- reason -->
  <div style="
    background:#080b13;
    border:1px solid #141926;
    border-radius:6px;
    padding:10px 12px;
    margin-bottom:${axiom ? "12px" : "0"};
  ">
    <div style="font-size:8px; color:#5a6480; letter-spacing:2px; margin-bottom:5px;">REASON</div>
    <div style="font-size:11px; color:#8899bb; line-height:1.6;">${reason}</div>
  </div>

  <!-- axiom -->
  ${axiom ? `
  <div style="
    margin-top:12px;
    padding:8px 12px;
    border-left:2px solid #3a86f5;
    font-size:9px;
    color:#3a86f5;
    letter-spacing:1px;
    font-style:italic;
  ">${axiom}</div>` : ""}

  <!-- footer lock -->
  <div style="
    margin-top:14px;
    padding-top:10px;
    border-top:1px solid #0f1420;
    font-size:8px;
    color:#2a3048;
    letter-spacing:2px;
    text-align:right;
  ">KING DIADEM™ · FATE™ AXIS · HUMAN FINAL AUTHORITY</div>
</div>`;
  }

  function renderGalaxyDecision(payload) {
    const target = window.KD?.byId("summary");
    if (!target) return;

    const output = payload?.output || {};
    const consensus = payload?.consensus || {};

    // Render HTML card
    target.innerHTML = buildCard(output, consensus, payload);

    // Dispatch to galaxy_scene.js
    const decisionData = {
      action: output.action || consensus.final_action || payload.final_action || null,
      risk: output.risk ?? payload?.risk?.risk_score ?? null,
      confidence: output.confidence ?? consensus.confidence ?? null,
      waterline: payload.waterline ?? payload?.risk?.waterline ?? null,
      route: payload.route || output.route || null,
      reason: output.reason || consensus.reason || null,
      axiom: payload.axiom || output.axiom || null,
      raw: payload,
    };

    window.dispatchEvent(
      new CustomEvent("KD:decision", { detail: decisionData })
    );
  }

  window.renderGalaxyDecision = renderGalaxyDecision;

  window.addEventListener("KD:response", (event) => {
    renderGalaxyDecision(event.detail);
  });
})();
