// static/ai_thinking_orbit.js
// KING DIADEM™ — AI Thinking Orbit Visualizer v2.0
// Delta-time physics · Persona-aware particles · KD event integration

(function () {
  const canvas = document.getElementById("thinkingOrbit");
  if (!canvas) {
    console.warn("[KD:orbit] thinkingOrbit canvas not found");
    return;
  }

  const ctx = canvas.getContext("2d", { desynchronized: true });

  // ─── PERSONA PALETTE ──────────────────────────────────────────────────────
  const PERSONA = {
    LYLA:    { color: "#e879a0", glow: "rgba(232,121,160,0.18)", trail: "rgba(232,121,160,0.08)", radius: 2.5 },
    VEGA:    { color: "#3a86f5", glow: "rgba(58,134,245,0.18)",  trail: "rgba(58,134,245,0.08)",  radius: 2.2 },
    TITAN:   { color: "#c8a440", glow: "rgba(200,164,64,0.22)",  trail: "rgba(200,164,64,0.10)",  radius: 3.0 },
    PATICCA: { color: "#a78bfa", glow: "rgba(167,139,250,0.18)", trail: "rgba(167,139,250,0.08)", radius: 2.0 },
    COSMOS:  { color: "#22d3ee", glow: "rgba(34,211,238,0.18)",  trail: "rgba(34,211,238,0.08)",  radius: 2.2 },
    DEFAULT: { color: "#66ccff", glow: "rgba(102,204,255,0.12)", trail: "rgba(102,204,255,0.06)", radius: 2.0 },
  };

  // ─── STATE ────────────────────────────────────────────────────────────────
  let particles = [];
  let thoughtBursts = [];  // text label particles from injectThought
  let activePersonas = new Set(["DEFAULT"]);
  let phase = "idle";      // idle | thinking | consensus | complete
  let lastTime = 0;
  let animId = null;

  // ─── RESIZE ───────────────────────────────────────────────────────────────
  function resize() {
    canvas.width = canvas.offsetWidth || window.innerWidth;
    canvas.height = 300;
  }
  resize();
  window.addEventListener("resize", resize);

  // ─── PARTICLE FACTORY ─────────────────────────────────────────────────────
  function createParticle(opts = {}) {
    const persona = opts.persona || "DEFAULT";
    const meta = PERSONA[persona] || PERSONA.DEFAULT;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    // orbit params
    const orbitR = opts.orbitR ?? (60 + Math.random() * 160);
    const angle  = opts.angle  ?? Math.random() * Math.PI * 2;
    const speed  = opts.speed  ?? (0.3 + Math.random() * 0.5) * (Math.random() < 0.5 ? 1 : -1);

    return {
      persona,
      color: meta.color,
      glow: meta.glow,
      trail: meta.trail,
      radius: meta.radius + Math.random() * 0.8,

      // orbital
      orbitR,
      angle,
      speed,   // rad/sec

      // cartesian (computed each frame)
      x: cx + Math.cos(angle) * orbitR,
      y: cy + Math.sin(angle) * orbitR,

      // drift (slight brownian noise)
      driftX: (Math.random() - 0.5) * 0.4,
      driftY: (Math.random() - 0.5) * 0.4,

      // connection weight
      linkDist: 90 + Math.random() * 40,

      // phase-specific
      pulsePhase: Math.random() * Math.PI * 2,
      opacity: 0,   // fade in
      born: performance.now(),
    };
  }

  function spawnPersonaCluster(persona, count = 8) {
    for (let i = 0; i < count; i++) {
      particles.push(createParticle({
        persona,
        orbitR: 50 + Math.random() * 180,
        speed: (0.25 + Math.random() * 0.55) * (Math.random() < 0.5 ? 1 : -1),
      }));
    }
  }

  // ─── INIT IDLE PARTICLES ──────────────────────────────────────────────────
  function initIdle() {
    particles = [];
    for (let i = 0; i < 30; i++) {
      particles.push(createParticle({ orbitR: 40 + Math.random() * 200 }));
    }
  }
  initIdle();

  // ─── THOUGHT BURST ────────────────────────────────────────────────────────
  window.injectThought = function (text, persona = "DEFAULT") {
    const meta = PERSONA[persona] || PERSONA.DEFAULT;
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    // spawn burst particles from center
    for (let i = 0; i < 6; i++) {
      const p = createParticle({
        persona,
        orbitR: 20 + Math.random() * 60,
        speed: (0.5 + Math.random() * 1.0) * (Math.random() < 0.5 ? 1 : -1),
      });
      p.opacity = 1;
      particles.push(p);
    }

    // add text label
    thoughtBursts.push({
      text,
      x: cx + (Math.random() - 0.5) * 120,
      y: cy + (Math.random() - 0.5) * 80,
      color: meta.color,
      opacity: 1,
      vy: -0.4,
      life: 1,  // 0→1 decay
    });
  };

  // ─── PHASE CONTROL ────────────────────────────────────────────────────────
  function setPhase(newPhase, personas = []) {
    phase = newPhase;

    if (newPhase === "thinking") {
      // spawn persona clusters
      personas.forEach(p => {
        if (!activePersonas.has(p)) {
          activePersonas.add(p);
          spawnPersonaCluster(p, 7);
        }
      });
      // cap total
      if (particles.length > 120) particles = particles.slice(-100);
    }

    if (newPhase === "consensus") {
      // pull all particles inward — tighten orbitR
      particles.forEach(p => { p.orbitR *= 0.5; });
    }

    if (newPhase === "complete" || newPhase === "idle") {
      setTimeout(() => {
        initIdle();
        activePersonas = new Set(["DEFAULT"]);
        thoughtBursts = [];
      }, 1200);
    }
  }

  // ─── DRAW ─────────────────────────────────────────────────────────────────
  function drawGlow(x, y, radius, color, alpha) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, radius * 6);
    g.addColorStop(0, color.replace(")", `,${alpha})`).replace("rgb", "rgba"));
    g.addColorStop(1, "transparent");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(x, y, radius * 6, 0, Math.PI * 2);
    ctx.fill();
  }

  function drawCenter(cx, cy, t) {
    // pulsing core
    const pulse = 0.7 + 0.3 * Math.sin(t * 1.5);
    const r = 6 * pulse;

    const g = ctx.createRadialGradient(cx, cy, 0, cx, cy, 40);
    g.addColorStop(0, `rgba(200,164,64,${0.9 * pulse})`);
    g.addColorStop(0.3, `rgba(200,164,64,${0.3 * pulse})`);
    g.addColorStop(1, "transparent");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(cx, cy, 40, 0, Math.PI * 2);
    ctx.fill();

    ctx.beginPath();
    ctx.arc(cx, cy, r, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(200,164,64,${pulse})`;
    ctx.fill();
  }

  // ─── ANIMATE LOOP ─────────────────────────────────────────────────────────
  function animate(now = 0) {
    animId = requestAnimationFrame(animate);

    const dt = Math.min((now - lastTime) / 1000, 0.05); // seconds, capped at 50ms
    lastTime = now;

    const cx = canvas.width / 2;
    const cy = canvas.height / 2;
    const t  = now / 1000;

    // ── clear with fade trail
    ctx.fillStyle = "rgba(4,6,14,0.35)";
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // ── center core
    drawCenter(cx, cy, t);

    // ── update + draw particles
    const toRemove = [];
    particles.forEach((p, idx) => {
      // fade in
      const age = (now - p.born) / 1000;
      p.opacity = Math.min(1, age * 2);

      // orbital motion (delta-time)
      p.angle += p.speed * dt;

      // gentle drift on orbitR
      p.orbitR += Math.sin(t * 0.3 + p.pulsePhase) * 0.08;

      // compute position
      p.x = cx + Math.cos(p.angle) * p.orbitR + p.driftX * Math.sin(t * 0.7 + p.pulsePhase);
      p.y = cy + Math.sin(p.angle) * p.orbitR + p.driftY * Math.cos(t * 0.5 + p.pulsePhase);

      // pulse radius
      const r = p.radius * (1 + 0.3 * Math.sin(t * 2 + p.pulsePhase));

      // glow
      const grd = ctx.createRadialGradient(p.x, p.y, 0, p.x, p.y, r * 5);
      grd.addColorStop(0, p.color + "cc");
      grd.addColorStop(1, "transparent");
      ctx.globalAlpha = p.opacity * 0.4;
      ctx.fillStyle = grd;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r * 5, 0, Math.PI * 2);
      ctx.fill();

      // dot
      ctx.globalAlpha = p.opacity;
      ctx.beginPath();
      ctx.arc(p.x, p.y, r, 0, Math.PI * 2);
      ctx.fillStyle = p.color;
      ctx.fill();

      ctx.globalAlpha = 1;
    });

    // ── connections
    ctx.lineWidth = 0.5;
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const a = particles[i];
        const b = particles[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const maxDist = (a.linkDist + b.linkDist) / 2;

        if (dist < maxDist) {
          const alpha = (1 - dist / maxDist) * 0.18 * Math.min(a.opacity, b.opacity);
          // cross-persona links are gold, same-persona are persona color
          const samePersona = a.persona === b.persona;
          ctx.strokeStyle = samePersona
            ? a.color + Math.round(alpha * 255).toString(16).padStart(2, "0")
            : `rgba(200,164,64,${alpha * 0.6})`;
          ctx.beginPath();
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }

    // ── thought bursts (text labels)
    thoughtBursts.forEach((tb, idx) => {
      tb.y += tb.vy;
      tb.life -= dt * 0.4;
      tb.opacity = Math.max(0, tb.life);

      if (tb.opacity <= 0) {
        thoughtBursts.splice(idx, 1);
        return;
      }

      ctx.globalAlpha = tb.opacity;
      ctx.font = "9px 'JetBrains Mono', monospace";
      ctx.fillStyle = tb.color;
      ctx.fillText(tb.text.slice(0, 32), tb.x, tb.y);
      ctx.globalAlpha = 1;
    });
  }

  // ─── KD EVENT INTEGRATION ─────────────────────────────────────────────────
  window.addEventListener("KD:thinking", (e) => {
    const { personas = [], phase: p = "thinking" } = e.detail || {};
    setPhase(p, personas);
  });

  window.addEventListener("KD:response", (e) => {
    setPhase("consensus");
    setTimeout(() => setPhase("complete"), 800);
  });

  window.addEventListener("KD:decision", (e) => {
    const { action, confidence } = e.detail || {};
    if (action) injectThought(`→ ${action}`, "TITAN");
  });

  // expose phase control
  window.KDOrbit = { setPhase, injectThought: window.injectThought };

  // ─── START ────────────────────────────────────────────────────────────────
  animate();
})();
