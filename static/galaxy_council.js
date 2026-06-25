// static/galaxy_council.js
// KING DIADEM™ — Council Vote Renderer
// Supports: LYLA · VEGA · TITAN · PATICCA · COSMOS (dynamic from backend)

(function () {
  // Member identity map — visual signature per persona
  const MEMBER_META = {
    LYLA: {
      color: "#e879a0",
      glow: "#e879a044",
      icon: "◈",
      role_fallback: "Warmth · Logic Core",
    },
    VEGA: {
      color: "#3a86f5",
      glow: "#3a86f544",
      icon: "◆",
      role_fallback: "Analytical · Strategic",
    },
    TITAN: {
      color: "#c8a440",
      glow: "#c8a44044",
      icon: "▲",
      role_fallback: "Truth Mode · Prime Axiom",
    },
    PATICCA: {
      color: "#a78bfa",
      glow: "#a78bfa44",
      icon: "◎",
      role_fallback: "Dependent Origination",
    },
    COSMOS: {
      color: "#22d3ee",
      glow: "#22d3ee44",
      icon: "✦",
      role_fallback: "Universal Lattice",
    },
  };

  const DEFAULT_META = {
    color: "#6b7280",
    glow: "#6b728044",
    icon: "○",
    role_fallback: "Council Member",
  };

  function getMeta(name) {
    if (!name) return DEFAULT_META;
    const key = name.toUpperCase().trim();
    return MEMBER_META[key] || DEFAULT_META;
  }

  function scoreBar(score) {
    // score: 0–1 float or 0–100 or null
    if (score == null || score === "n/a") return null;
    let n = parseFloat(score);
    if (isNaN(n)) return null;
    if (n > 1) n = n / 100;
    n = Math.max(0, Math.min(1, n));
    return n;
  }

  function actionBadge(action, color) {
    if (!action || action === "n/a") return "";
    return `<span style="
      display:inline-block;
      padding:2px 8px;
      background:${color}18;
      border:1px solid ${color}55;
      border-radius:3px;
      font-size:9px;
      color:${color};
      letter-spacing:1.5px;
      text-transform:uppercase;
    ">${action}</span>`;
  }

  function buildVoteRow(vote, index) {
    const meta = getMeta(vote.member);
    const name = (vote.member || "UNKNOWN").toUpperCase();
    const role = vote.role || meta.role_fallback;
    const action = vote.action || "—";
    const bar = scoreBar(vote.score);
    const barPct = bar != null ? Math.round(bar * 100) : null;
    const reasoning = vote.reason || vote.reasoning || null;
    const weight = vote.weight != null ? `×${vote.weight}` : null;

    return `
<div class="kd-council-vote" style="
  display:grid;
  grid-template-columns: 32px 1fr;
  gap:0 12px;
  padding:12px 14px;
  background:${index % 2 === 0 ? "#080b13" : "#060910"};
  border-bottom:1px solid #0f1420;
  position:relative;
  transition: background 0.2s;
" onmouseover="this.style.background='#0d1120'" onmouseout="this.style.background='${index % 2 === 0 ? "#080b13" : "#060910"}'">

  <!-- icon column -->
  <div style="
    display:flex;
    align-items:flex-start;
    padding-top:2px;
    font-size:16px;
    color:${meta.color};
    text-shadow: 0 0 8px ${meta.glow};
  ">${meta.icon}</div>

  <!-- content column -->
  <div>
    <!-- name + role -->
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:5px;">
      <div>
        <span style="font-size:11px; color:${meta.color}; font-weight:700; letter-spacing:2px;">${name}</span>
        ${weight ? `<span style="font-size:8px; color:#3d4560; margin-left:6px;">${weight}</span>` : ""}
      </div>
      <span style="font-size:8px; color:#3d4560; letter-spacing:1px;">${role}</span>
    </div>

    <!-- action badge -->
    <div style="margin-bottom:${bar != null ? "8px" : "0"};">
      ${actionBadge(action, meta.color)}
    </div>

    <!-- score bar -->
    ${bar != null ? `
    <div style="display:flex; align-items:center; gap:8px;">
      <div style="flex:1; background:#0f1520; border-radius:2px; height:3px; overflow:hidden;">
        <div style="
          width:${barPct}%;
          height:100%;
          background:${meta.color};
          box-shadow:0 0 4px ${meta.glow};
          transition:width 0.8s ease;
        "></div>
      </div>
      <span style="font-size:9px; color:${meta.color}; min-width:28px; text-align:right;">${barPct}%</span>
    </div>` : ""}

    <!-- reasoning (optional) -->
    ${reasoning ? `
    <div style="
      margin-top:7px;
      font-size:9px;
      color:#4a5568;
      font-style:italic;
      line-height:1.5;
    ">${reasoning}</div>` : ""}
  </div>
</div>`;
  }

  function buildCouncilPanel(votes, councilScore, councilAction, dissent) {
    const ts = new Date().toISOString().replace("T", " ").slice(0, 19);
    const scoreBar_val = scoreBar(councilScore);
    const scorePct = scoreBar_val != null ? Math.round(scoreBar_val * 100) : null;

    const voteRows = votes.map((v, i) => buildVoteRow(v, i)).join("");

    return `
<div class="kd-council-panel" style="
  background:#060910;
  border:1px solid #1a2030;
  border-top:2px solid #c8a440;
  border-radius:8px;
  overflow:hidden;
  font-family:'JetBrains Mono','Fira Code',monospace;
  color:#cdd6f4;
  position:relative;
">
  <!-- header -->
  <div style="
    display:flex;
    justify-content:space-between;
    align-items:center;
    padding:12px 16px;
    background:linear-gradient(90deg, #0a0d14 0%, #08090f 100%);
    border-bottom:1px solid #0f1420;
  ">
    <div style="display:flex; align-items:center; gap:8px;">
      <span style="font-size:8px; letter-spacing:3px; color:#c8a440;">◆ COUNCIL ASSEMBLY</span>
      <span style="
        font-size:7px;
        padding:1px 6px;
        border:1px solid #c8a44055;
        border-radius:2px;
        color:#c8a44099;
        letter-spacing:1px;
      ">${votes.length} ACTIVE</span>
    </div>
    <span style="font-size:8px; color:#2a3048;">${ts} UTC</span>
  </div>

  <!-- votes -->
  <div class="kd-council-votes">
    ${voteRows.length ? voteRows : `
    <div style="padding:24px; text-align:center; color:#2a3048; font-size:10px; letter-spacing:2px;">
      AWAITING COUNCIL INPUT...
    </div>`}
  </div>

  <!-- council summary footer -->
  ${(scorePct != null || councilAction) ? `
  <div style="
    padding:12px 16px;
    background:#080b14;
    border-top:1px solid #0f1420;
    display:grid;
    grid-template-columns:1fr auto;
    gap:8px;
    align-items:center;
  ">
    <div>
      ${councilAction ? `
      <div style="font-size:8px; color:#5a6480; letter-spacing:2px; margin-bottom:4px;">COUNCIL VERDICT</div>
      <div style="font-size:13px; color:#e8d5a3; font-weight:600; letter-spacing:1px;">${councilAction}</div>
      ` : ""}
      ${dissent ? `
      <div style="font-size:8px; color:#f87171; margin-top:5px; letter-spacing:1px;">⚠ DISSENT RECORDED</div>
      ` : ""}
    </div>
    ${scorePct != null ? `
    <div style="text-align:right;">
      <div style="font-size:8px; color:#5a6480; letter-spacing:2px; margin-bottom:4px;">COUNCIL SCORE</div>
      <div style="font-size:20px; color:#c8a440; font-weight:700;">${scorePct}<span style="font-size:10px; color:#8b7320;">%</span></div>
    </div>` : ""}
  </div>` : ""}

  <!-- lock line -->
  <div style="
    padding:6px 16px;
    background:#050710;
    font-size:7px;
    color:#1a2035;
    letter-spacing:2px;
    text-align:center;
  ">KING DIADEM™ · HUMAN FINAL AUTHORITY · FATE™ A6</div>
</div>`;
  }

  function renderCouncil(payload) {
    const target = window.KD?.byId("council");
    if (!target) return;

    const council = payload?.council || {};
    const votes = Array.isArray(council.votes) ? council.votes : [];

    if (!votes.length) {
      target.innerHTML = `
<div style="
  font-family:'JetBrains Mono',monospace;
  padding:20px;
  text-align:center;
  color:#2a3048;
  font-size:9px;
  letter-spacing:3px;
  border:1px solid #0f1420;
  border-radius:8px;
  background:#060910;
">WAITING FOR COUNCIL...</div>`;
      return;
    }

    const councilScore = council.score ?? null;
    const councilAction = council.final_action || council.action || null;
    const dissent = council.dissent ?? false;

    target.innerHTML = buildCouncilPanel(votes, councilScore, councilAction, dissent);
  }

  window.renderCouncil = renderCouncil;

  window.addEventListener("KD:response", (event) => {
    renderCouncil(event.detail);
  });
})();
