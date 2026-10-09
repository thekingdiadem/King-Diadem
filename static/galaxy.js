// static/galaxy.js — KING DIADEM Solar System v2
(function () {
  const canvas = document.getElementById("galaxy") || document.getElementById("solar");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");

  function resize() { canvas.width = innerWidth; canvas.height = innerHeight; }
  resize(); addEventListener("resize", resize);

  // ── STARS — สว่างขึ้น เยอะขึ้น ─────────────────────────────
  const STARS = Array.from({length:1100}, () => ({
    x: Math.random()*4000-2000,
    y: Math.random()*4000-2000,
    s: Math.random()*2.0+0.3,
    a: Math.random()*0.9+0.2,
    f: (Math.random()-0.5)*0.006,
    c: Math.random()>0.88?"255,160,60":Math.random()>0.65?"180,200,255":Math.random()>0.5?"255,240,200":"255,255,255"
  }));

  // ── MILKY WAY BAND ────────────────────────────────────────────
  const BAND = Array.from({length:600}, () => ({
    x: (Math.random()-0.5)*6000,
    y: (Math.random()-0.5)*700,
    s: Math.random()*1.2+0.3,
    a: Math.random()*0.28+0.04,
    c: Math.random()>0.5?"200,180,255":"255,220,180"
  }));

  // ── NEBULA CLOUDS — บางลงมาก ดาวโผล่ชัด ─────────────────────
  /* ร้อนสลับเย็น (ภาษาเดียวกับแท็บจักรวาล): ซ้ายคราม/เทอร์ควอยซ์ · ขวากุหลาบ/อำพัน */
  const NEBULA = [
    {x:-420, y:-120, r:320, c:"40,70,190",  a:0.10},
    {x:-260, y:240,  r:260, c:"20,120,140", a:0.07},
    {x:420,  y:-160, r:300, c:"170,60,110", a:0.08},
    {x:520,  y:200,  r:280, c:"200,110,40", a:0.07},
    {x:40,   y:-320, r:200, c:"110,70,190", a:0.05},
  ];

  // ── SOLAR SYSTEM — ดาวเคราะห์ใหญ่ขึ้น ──────────────────────
  const PLANETS = [
    {name:"",          color:"#c0c0c0", size:5,   orbit:75,  speed:0.0045, angle:0,    rings:false},
    {name:"",          color:"#f0c060", size:9,   orbit:120, speed:0.0035, angle:1.2,  rings:false},
    {name:"",          color:"#3366ff", size:10,  orbit:175, speed:0.0025, angle:2.5,  rings:false, moon:true},
    {name:"",          color:"#dd4422", size:7,   orbit:230, speed:0.002,  angle:4.0,  rings:false},
    {name:"",          color:"#d4a060", size:22,  orbit:325, speed:0.001,  angle:1.8,  rings:false},
    {name:"",          color:"#eed898", size:18,  orbit:430, speed:0.0007, angle:3.2,  rings:true},
    {name:"",          color:"#88ddee", size:13,  orbit:520, speed:0.0005, angle:5.5,  rings:false},
    {name:"",          color:"#2255cc", size:12,  orbit:600, speed:0.0003, angle:2.8,  rings:false},
    // KING DIADEM nodes
    {name:"LYLA",      color:"#ffcf7a", size:7,   orbit:155, speed:0.0018, angle:0.5,  rings:false, kd:true},
    {name:"VEGA",      color:"#8cc2ff", size:6,   orbit:278, speed:0.0014, angle:3.5,  rings:false, kd:true},
    {name:"DRIFTZERO", color:"#ff6a00", size:4,   orbit:200, speed:0.003,  angle:1.0,  rings:false, kd:true},
    {name:"CIVIL",     color:"#aa88ff", size:5,   orbit:465, speed:0.0004, angle:4.5,  rings:false, kd:true},
  ];

  const SUN_R = 30, SUN_GLOW = 95;
  let frame = 0;

  function draw() {
    frame++;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const cx = canvas.width / 2;
    const cy = canvas.height / 2;

    // Milky Way band
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(0.28);
    for (const b of BAND) {
      ctx.beginPath();
      ctx.arc(b.x, b.y, b.s, 0, Math.PI*2);
      ctx.fillStyle = `rgba(${b.c},${b.a})`;
      ctx.fill();
    }
    ctx.restore();

    // Nebula (บาง)
    for (const n of NEBULA) {
      const g = ctx.createRadialGradient(cx+n.x, cy+n.y, 0, cx+n.x, cy+n.y, n.r);
      g.addColorStop(0,   `rgba(${n.c},${n.a})`);
      g.addColorStop(0.4, `rgba(${n.c},${n.a*0.35})`);
      g.addColorStop(1,   "transparent");
      ctx.beginPath();
      ctx.arc(cx+n.x, cy+n.y, n.r, 0, Math.PI*2);
      ctx.fillStyle = g;
      ctx.fill();
    }

    // Stars (สว่าง)
    for (const s of STARS) {
      s.a = Math.max(0.1, Math.min(1.0, s.a + s.f));
      if (s.a <= 0.1 || s.a >= 1.0) s.f *= -1;
      ctx.beginPath();
      ctx.arc((cx+s.x) % canvas.width, (cy+s.y) % canvas.height, s.s, 0, Math.PI*2);
      ctx.fillStyle = `rgba(${s.c},${s.a*0.85})`;
      ctx.fill();
    }

    // Orbit rings
    for (const p of PLANETS) {
      ctx.beginPath();
      ctx.ellipse(cx, cy, p.orbit, p.orbit*0.28, 0, 0, Math.PI*2);
      const og = ctx.createLinearGradient(cx - p.orbit, 0, cx + p.orbit, 0);
      og.addColorStop(0, `rgba(110,170,255,${p.kd ? 0.16 : 0.07})`); og.addColorStop(0.5, "rgba(220,220,255,0.05)"); og.addColorStop(1, `rgba(255,190,120,${p.kd ? 0.16 : 0.07})`);
      ctx.strokeStyle = og;
      ctx.lineWidth = 0.8;
      ctx.stroke();
    }

    // แก่นแสง: ไม่ใช่ลูกบอลส้ม — จุดคมกลางฮาโลอุ่น ขอบนอกเย็น + เส้นแสงแนวนอนฟ้า→ทอง + วงทรงกลดสีรุ้ง
    const br = 1 + Math.sin(frame * 0.02) * 0.06;
    ctx.globalCompositeOperation = "lighter";
    const halo = ctx.createRadialGradient(cx, cy, 0, cx, cy, SUN_GLOW * 1.6 * br);
    halo.addColorStop(0,    "rgba(255,240,220,0.55)");
    halo.addColorStop(0.08, "rgba(255,200,130,0.30)");
    halo.addColorStop(0.3,  "rgba(220,110,150,0.10)");
    halo.addColorStop(0.6,  "rgba(90,130,255,0.05)");
    halo.addColorStop(1,    "transparent");
    ctx.fillStyle = halo;
    ctx.beginPath(); ctx.arc(cx, cy, SUN_GLOW * 1.6 * br, 0, Math.PI*2); ctx.fill();
    const L = Math.min(canvas.width * 0.42, 420), hz = ctx.createLinearGradient(cx - L, cy, cx + L, cy);
    hz.addColorStop(0, "rgba(90,200,230,0)"); hz.addColorStop(0.35, "rgba(110,170,255,0.22)"); hz.addColorStop(0.5, "rgba(255,245,235,0.6)");
    hz.addColorStop(0.65, "rgba(255,150,190,0.22)"); hz.addColorStop(1, "rgba(255,180,100,0)");
    ctx.fillStyle = hz; ctx.fillRect(cx - L, cy - 0.6, L * 2, 1.2);
    for (let k = 0; k < 3; k++) {
      ctx.strokeStyle = ["rgba(255,120,120,0.07)", "rgba(255,220,140,0.06)", "rgba(120,170,255,0.07)"][k];
      ctx.lineWidth = 1.4;
      ctx.beginPath(); ctx.arc(cx, cy, SUN_GLOW * 0.95 - k * 2.2, 0, Math.PI*2); ctx.stroke();
    }
    ctx.globalCompositeOperation = "source-over";
    ctx.fillStyle = "#fff6ea";
    ctx.beginPath(); ctx.arc(cx, cy, 3.2 * br, 0, Math.PI*2); ctx.fill();

    // Planets
    for (const p of PLANETS) {
      p.angle += p.speed;
      const x = cx + Math.cos(p.angle) * p.orbit;
      const y = cy + Math.sin(p.angle) * p.orbit * 0.28;

      // Atmosphere glow
      const ag = ctx.createRadialGradient(x, y, 0, x, y, p.size*4);
      ag.addColorStop(0, p.color+"55");
      ag.addColorStop(1, "transparent");
      ctx.beginPath();
      ctx.arc(x, y, p.size*4, 0, Math.PI*2);
      ctx.fillStyle = ag;
      ctx.fill();

      // Planet body
      // ทรงกลมรับแสงจากแก่น: ด้านที่หันเข้าหาแก่นสว่างอุ่น ด้านหลังมืดเย็น
      const lx = cx - x, ly = cy - y, ll = Math.hypot(lx, ly) || 1;
      const pg = ctx.createRadialGradient(x + lx/ll*p.size*0.45, y + ly/ll*p.size*0.45, p.size*0.05, x, y, p.size*1.05);
      pg.addColorStop(0,    "#fff3e2");
      pg.addColorStop(0.3,  p.color);
      pg.addColorStop(0.75, "#1a2350");
      pg.addColorStop(1,    "#070a1c");
      ctx.beginPath();
      ctx.arc(x, y, p.size, 0, Math.PI*2);
      ctx.fillStyle = pg;
      ctx.fill();

      // Saturn rings
      if (p.rings) {
        ctx.save();
        ctx.translate(x, y);
        ctx.scale(1, 0.28);
        ctx.beginPath();
        ctx.ellipse(0, 0, p.size*2.5, p.size*2.5, 0, 0, Math.PI*2);
        ctx.strokeStyle = "rgba(238,216,152,0.65)";
        ctx.lineWidth = 4;
        ctx.stroke();
        ctx.beginPath();
        ctx.ellipse(0, 0, p.size*3.2, p.size*3.2, 0, 0, Math.PI*2);
        ctx.strokeStyle = "rgba(238,216,152,0.3)";
        ctx.lineWidth = 2;
        ctx.stroke();
        ctx.restore();
      }

      // Earth moon
      if (p.moon) {
        const ma = p.angle * 8;
        const mx = x + Math.cos(ma)*22;
        const my = y + Math.sin(ma)*6;
        ctx.beginPath();
        ctx.arc(mx, my, 3, 0, Math.PI*2);
        ctx.fillStyle = "rgba(210,210,210,0.8)";
        ctx.fill();
      }

      // KD node labels
      if (p.kd) {
        ctx.fillStyle = "rgba(230,224,245,0.6)";
        ctx.font = "7px 'Share Tech Mono',monospace";
        ctx.fillText(p.name, x+p.size+4, y+3);
      }
    }

    // Supply chain pulse
    if (frame % 220 === 0) {
      let ripR = 0, ripA = 0.14;
      (function ripple() {
        ripR += 4; ripA -= 0.0025;
        if (ripR < 550 && ripA > 0) {
          ctx.beginPath();
          ctx.arc(cx, cy, ripR, 0, Math.PI*2);
          ctx.strokeStyle = `rgba(0,212,255,${ripA})`;
          ctx.lineWidth = 1;
          ctx.stroke();
          requestAnimationFrame(ripple);
        }
      })();
    }

    requestAnimationFrame(draw);
  }

  draw();
})();
