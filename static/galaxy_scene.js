/* ================================================================
   KING DIADEM — Galaxy Scene v44 REALISTIC SOLAR SYSTEM
   - Perspective tilt: orbits are ellipses, not circles
   - Planets 40% smaller, proper size hierarchy
   - Planets orbit LEFT/RIGHT, not stacked center
   - Sparse-alive starfield: depth layers, not crowded
   - Sun bleeds off top edge realistically
   - Mobile adaptive
   ================================================================ */
(function(){
'use strict';

var cv = document.getElementById('galaxy');
if (!cv) return;
var ctx = cv.getContext('2d', {alpha: true, desynchronized: true});
var W = 0, H = 0, _raf = null, _last = 0, _dt = 0;
var activeRoute = 'general';
var isMobile = false;

/* ── ROUTE HUE ──────────────────────────────────────────────── */
var ROUTE_HUE = {general:208, risk:22, collapse:338, survival:142, civil:268, vega:286};
var _tgtHue = 208, _curHue = 208;

/* ── ANIMATION LOOP ─────────────────────────────────────────── */
function loop(now){
  _raf = requestAnimationFrame(loop);
  _dt = Math.min(now - _last, 50);
  _last = now;
  render(_dt, now);
}

var _rT;
function doResize(){
  W = cv.width  = window.innerWidth;
  H = cv.height = window.innerHeight;
  isMobile = W < 768;
  buildStars();
  buildDust();
}
window.addEventListener('resize', function(){ clearTimeout(_rT); _rT = setTimeout(doResize, 80); }, {passive:true});
document.addEventListener('visibilitychange', function(){
  if (document.hidden){ if (_raf){ cancelAnimationFrame(_raf); _raf = null; } }
  else { if (!_raf){ _last = performance.now(); _raf = requestAnimationFrame(loop); } }
}, {passive:true});

/* ================================================================
   STAR FIELD — 3 depth layers, sparse but alive
   ================================================================ */
var STARS = [];
function buildStars(){
  STARS = [];
  var total = isMobile ? 280 : 500;
  for (var i = 0; i < total; i++){
    var layer = Math.random();
    var sz    = layer < 0.50 ? 0 :
                layer < 0.78 ? 1 : 2;
    STARS.push({
      x:  Math.random() * W,
      y:  Math.random() * H,
      r:  [0.25 + Math.random()*0.35,
           0.45 + Math.random()*0.65,
           0.80 + Math.random()*1.30][sz],
      a:  [0.22+Math.random()*0.45,
           0.35+Math.random()*0.58,
           0.52+Math.random()*0.80][sz],
      tw: Math.random() < 0.60,
      ph: Math.random() * Math.PI * 2,
      sp: 0.15 + Math.random() * 0.65,
      ct: Math.random()<0.22?'blue': Math.random()<0.10?'warm':'white',
      cross: sz===2 && Math.random()<0.55
    });
  }
}

function drawStars(now){
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (var i = 0; i < STARS.length; i++){
    var s = STARS[i];
    var a = s.tw ? s.a*(0.38+0.62*Math.sin(now*s.sp*0.00048+s.ph)) : s.a;
    var col = s.ct==='blue'  ? 'rgba(180,215,255,'+a.toFixed(3)+')' :
              s.ct==='warm'  ? 'rgba(255,235,195,'+a.toFixed(3)+')' :
                               'rgba(225,238,255,'+a.toFixed(3)+')';
    if (s.cross && a > s.a*0.55){
      ctx.strokeStyle = col; ctx.lineWidth = 0.35;
      var cl = s.r * 3.8;
      ctx.beginPath(); ctx.moveTo(s.x-cl,s.y); ctx.lineTo(s.x+cl,s.y); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(s.x,s.y-cl); ctx.lineTo(s.x,s.y+cl); ctx.stroke();
    }
    ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
    ctx.fillStyle = col; ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   NEBULA DUST — sparse, alive, not crowded
   ================================================================ */
var DUST = [];
function buildDust(){
  DUST = [];
  var n = isMobile ? 55 : 100;
  var hues = [260,278,295,185,200,340];
  for (var i = 0; i < n; i++){
    DUST.push({
      x:   Math.random() * W,
      y:   Math.random() * H,
      r:   22 + Math.random() * 65,
      a:   0.016 + Math.random() * 0.036,
      ph:  Math.random() * Math.PI * 2,
      sp:  0.04 + Math.random() * 0.14,
      hue: hues[Math.floor(Math.random()*hues.length)],
      sat: 18 + Math.random() * 22,
      lum: 50 + Math.random() * 22
    });
  }
}

function drawDust(now){
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  for (var i = 0; i < DUST.length; i++){
    var d = DUST[i];
    var a = d.a * (0.42+0.58*Math.sin(now*d.sp*0.00019+d.ph));
    var g = ctx.createRadialGradient(d.x,d.y,0, d.x,d.y,d.r);
    g.addColorStop(0,'hsla('+d.hue+','+d.sat+'%,'+d.lum+'%,'+a.toFixed(4)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle = g; ctx.fillRect(d.x-d.r, d.y-d.r, d.r*2, d.r*2);
  }
  ctx.restore();
}

/* ================================================================
   BACKGROUND
   ================================================================ */
function drawBg(now){
  ctx.clearRect(0, 0, W, H);

  /* deep space — rich navy blue, clearly visible */
  var bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0,   '#1a2d4a');
  bg.addColorStop(0.20,'#152440');
  bg.addColorStop(0.45,'#111e36');
  bg.addColorStop(0.72,'#0e192e');
  bg.addColorStop(1,   '#0b1526');
  ctx.fillStyle = bg; ctx.fillRect(0,0,W,H);

  /* route tint — very subtle */
  _curHue += (_tgtHue - _curHue) * 0.004 * (_dt/16);
  ctx.save(); ctx.globalCompositeOperation = 'screen';
  var rt = ctx.createRadialGradient(W*0.5,H*0.4,0, W*0.5,H*0.5, W*0.70);
  rt.addColorStop(0,'hsla('+_curHue+',30%,12%,0.020)');
  rt.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = rt; ctx.fillRect(0,0,W,H);

  /* strong blue nebula center */
  var nb0 = ctx.createRadialGradient(W*0.50, H*0.50, 0, W*0.50, H*0.50, W*0.65);
  nb0.addColorStop(0,'rgba(30,80,160,0.18)'); nb0.addColorStop(0.5,'rgba(20,55,120,0.08)'); nb0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = nb0; ctx.fillRect(0,0,W,H);

  /* violet left */
  var nb1 = ctx.createRadialGradient(W*0.05, H*0.30, 0, W*0.05, H*0.30, W*0.52);
  nb1.addColorStop(0,'rgba(80,55,180,0.20)'); nb1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = nb1; ctx.fillRect(0,0,W,H);

  /* rose right */
  var nb2 = ctx.createRadialGradient(W*0.92, H*0.58, 0, W*0.92, H*0.58, W*0.45);
  nb2.addColorStop(0,'rgba(160,70,100,0.16)'); nb2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = nb2; ctx.fillRect(0,0,W,H);

  /* teal bottom */
  var nb3 = ctx.createRadialGradient(W*0.30, H*0.90, 0, W*0.30, H*0.90, W*0.50);
  nb3.addColorStop(0,'rgba(25,100,160,0.16)'); nb3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = nb3; ctx.fillRect(0,0,W,H);

  /* milky way band */
  var mw = ctx.createLinearGradient(0, H*0.40, W, H*0.60);
  mw.addColorStop(0,   'rgba(0,0,0,0)');
  mw.addColorStop(0.28,'rgba(60,100,200,0.06)');
  mw.addColorStop(0.50,'rgba(80,120,220,0.10)');
  mw.addColorStop(0.72,'rgba(60,100,200,0.06)');
  mw.addColorStop(1,   'rgba(0,0,0,0)');
  ctx.fillStyle = mw; ctx.fillRect(0, H*0.28, W, H*0.44);
  ctx.restore();
}

/* ================================================================
   SUN — realistic, bleeds off top
   ================================================================ */
function drawSun(now){
  var cx = W * 0.50;
  var cy = H * (-0.06);                 /* bleeds off top */
  var Rs = Math.min(W, H) * (isMobile ? 0.22 : 0.18);

  ctx.save();
  ctx.globalCompositeOperation = 'screen';

  /* far corona */
  var c1 = ctx.createRadialGradient(cx,cy,Rs*0.4, cx,cy, Rs*5.5);
  c1.addColorStop(0,'rgba(255,90,8,0.038)'); c1.addColorStop(0.5,'rgba(255,110,12,0.015)'); c1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = c1; ctx.fillRect(0,0,W,H);

  /* mid corona */
  var c2 = ctx.createRadialGradient(cx,cy,Rs*0.5, cx,cy, Rs*2.8);
  c2.addColorStop(0,'rgba(255,100,10,0.10)'); c2.addColorStop(0.5,'rgba(255,90,8,0.042)'); c2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = c2; ctx.fillRect(0,0,W,H);

  /* inner glow */
  var c3 = ctx.createRadialGradient(cx,cy,Rs*0.6, cx,cy, Rs*1.60);
  c3.addColorStop(0,'rgba(255,120,18,0.20)'); c3.addColorStop(0.6,'rgba(255,80,6,0.08)'); c3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = c3; ctx.fillRect(0,0,W,H);

  /* 10 solar rays */
  ctx.save();
  for (var ri = 0; ri < 10; ri++){
    var ra = (ri/10)*Math.PI*2 + now*0.000016;
    var rl = Rs * (1.25 + 0.22*Math.sin(now*0.000014+ri*0.75));
    ctx.globalAlpha = 0.018 + 0.009*Math.abs(Math.sin(now*0.00018+ri));
    var rx1=cx+Math.cos(ra)*Rs*0.5, ry1=cy+Math.sin(ra)*Rs*0.5;
    var rx2=cx+Math.cos(ra)*rl,     ry2=cy+Math.sin(ra)*rl;
    var rg = ctx.createLinearGradient(rx1,ry1,rx2,ry2);
    rg.addColorStop(0,'rgba(255,140,28,1)'); rg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle = rg; ctx.lineWidth = Rs*0.06; ctx.lineCap='round';
    ctx.beginPath(); ctx.moveTo(rx1,ry1); ctx.lineTo(rx2,ry2); ctx.stroke();
  }
  ctx.globalAlpha = 1; ctx.restore();

  /* photosphere */
  ctx.globalCompositeOperation = 'source-over';
  var ph = ctx.createRadialGradient(cx-Rs*0.20,cy-Rs*0.14,0, cx+Rs*0.08,cy+Rs*0.09, Rs);
  ph.addColorStop(0,   '#fff8d0');
  ph.addColorStop(0.10,'#ffd842');
  ph.addColorStop(0.28,'#ff9c10');
  ph.addColorStop(0.52,'#ff5c02');
  ph.addColorStop(0.75,'#cc1a00');
  ph.addColorStop(1,   '#6a0500');
  ctx.fillStyle = ph; ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();

  /* specular */
  ctx.globalCompositeOperation = 'screen';
  var hi = ctx.createRadialGradient(cx-Rs*0.14,cy-Rs*0.10,0, cx,cy,Rs);
  hi.addColorStop(0,'rgba(255,255,210,0.55)'); hi.addColorStop(0.35,'rgba(255,220,80,0.08)'); hi.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle = hi; ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

/* ================================================================
   PERSPECTIVE ORBIT SYSTEM
   Planet positions: ellipse orbits with tilt ~20 deg
   Each planet orbits around sun at (W*0.5, H*-0.06)

   We render orbits as tilted ellipses so they look like
   real solar system viewed from ~20 deg above the ecliptic.
   ================================================================ */

/* Orbit config — orbital radius as fraction of min(W,H)
   Period in arbitrary time units.
   yBase = how far down the screen center of ellipse sits
   (as fraction of H from sun center) */

var PLANETS = [
  {id:'mercury', lbl:'GENERAL',  route:'general',  orb:0.11, per:0.241, yOff:0.18, rD:0.025, rM:0.030, draw:drawMercury},
  {id:'venus',   lbl:'RISK',     route:'risk',     orb:0.17, per:0.615, yOff:0.28, rD:0.033, rM:0.040, draw:drawVenus  },
  {id:'earth',   lbl:'SURVIVAL', route:'survival', orb:0.23, per:1.000, yOff:0.38, rD:0.038, rM:0.046, draw:drawEarth, moon:true},
  {id:'mars',    lbl:'COLLAPSE', route:'collapse', orb:0.30, per:1.881, yOff:0.48, rD:0.027, rM:0.034, draw:drawMars  },
  {id:'jupiter', lbl:'CIVIL',    route:'civil',    orb:0.40, per:11.86, yOff:0.60, rD:0.050, rM:0.060, draw:drawJupiter},
  {id:'vega',    lbl:'VEGA',     route:'vega',     orb:0.46, per:29.46, yOff:0.72, rD:0.034, rM:0.042, draw:drawVega  },
];

/* Sun center */
function sunCX(){ return W * 0.50; }
function sunCY(){ return H * (-0.06); }

/* Perspective tilt factor — ellipse Y axis compressed */
var TILT = 0.28;   /* 0=side view, 1=top-down */

/* Get planet screen position at time t */
function planetPos(p, now){
  var BASE_SPEED = 0.000040;
  var angle = (now * BASE_SPEED / p.per) % (Math.PI*2);
  var R = Math.min(W,H) * p.orb;
  /* ellipse: x uses full R, y uses R*TILT + yOff offset */
  var cx = sunCX() + Math.cos(angle) * R;
  /* The orbit center drifts DOWN from sun to give depth feel */
  var oy = sunCY() + H * p.yOff;
  var cy = oy      + Math.sin(angle) * R * TILT;
  return {x:cx, y:cy, angle:angle, orbitR:R, orbitY:oy};
}

function getR(p){
  return Math.min(W,H) * (isMobile ? p.rM : p.rD);
}

/* ── ORBIT RING ─────────────────────────────────────────────── */
function drawOrbitRing(p, now){
  var R = Math.min(W,H) * p.orb;
  var oy = sunCY() + H * p.yOff;
  var isAct = p.route === activeRoute;

  ctx.save(); ctx.globalCompositeOperation = 'screen';
  /* ellipse ring */
  ctx.beginPath();
  ctx.ellipse(sunCX(), oy, R, R*TILT, 0, 0, Math.PI*2);

  var a = isAct ? 0.38 : 0.09;
  ctx.strokeStyle = isAct
    ? 'rgba(200,168,75,'+a+')'
    : 'rgba(100,150,220,'+a+')';
  ctx.lineWidth = isAct ? 1.2 : 0.45;
  ctx.stroke();

  /* active orbit glow dot (orbiting particle) */
  if (isAct){
    var pos = planetPos(p, now);
    var sg = ctx.createRadialGradient(pos.x,pos.y,0, pos.x,pos.y,8);
    sg.addColorStop(0,'rgba(255,235,120,0.90)'); sg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle = sg; ctx.fillRect(0,0,W,H);
  }
  ctx.restore();
}

/* ── LABEL ──────────────────────────────────────────────────── */
function drawLabel(p, pos){
  var isAct = p.route === activeRoute;
  var r = getR(p);
  var fs = Math.max(7, Math.min(11, r*0.55));
  ctx.save();
  ctx.font = '500 '+fs+'px "DM Mono",monospace';
  ctx.textAlign = 'center'; ctx.textBaseline = 'top';
  if (isAct){
    ctx.shadowColor = 'rgba(200,168,75,0.85)'; ctx.shadowBlur = 8;
    ctx.fillStyle = 'rgba(248,210,95,0.97)';
  } else {
    ctx.fillStyle = 'rgba(110,155,220,0.38)';
  }
  ctx.fillText(p.lbl, pos.x, pos.y + r + 6);
  ctx.restore();
}

/* ── CLICK ──────────────────────────────────────────────────── */
var _planetPositionsCache = [];
cv.addEventListener('click', function(e){
  var rc = cv.getBoundingClientRect();
  var mx = e.clientX - rc.left, my = e.clientY - rc.top;
  for (var i = 0; i < _planetPositionsCache.length; i++){
    var pp = _planetPositionsCache[i];
    var dx = mx-pp.x, dy = my-pp.y, r = getR(PLANETS[i])*1.8;
    if (dx*dx+dy*dy < r*r){
      window.KD_setRoute && window.KD_setRoute(PLANETS[i].route);
    }
  }
}, {passive:true});
cv.addEventListener('touchend', function(e){
  if (e.changedTouches.length===1){
    var t=e.changedTouches[0];
    cv.dispatchEvent(new MouseEvent('click',{clientX:t.clientX,clientY:t.clientY}));
  }
}, {passive:true});

/* ================================================================
   PLANET DRAW HELPERS
   ================================================================ */
function pBase(x,y,r,c0,c1,c2,c3,c4){
  var g=ctx.createRadialGradient(x-r*0.28,y-r*0.22,0, x+r*0.10,y+r*0.10,r*1.02);
  g.addColorStop(0,c0);g.addColorStop(0.22,c1);g.addColorStop(0.50,c2);g.addColorStop(0.76,c3);g.addColorStop(1,c4);
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
}
function pLimb(x,y,r,col){
  ctx.save();ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.30,y-r*0.24,0,x,y,r*1.02);
  g.addColorStop(0,col);g.addColorStop(0.42,'rgba(255,255,255,0.025)');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();
}
function pDark(x,y,r,s){
  s=s||0.60;ctx.save();ctx.globalCompositeOperation='multiply';
  var g=ctx.createRadialGradient(x+r*0.34,y+r*0.28,0,x,y,r*1.02);
  g.addColorStop(0,'rgba(0,0,0,'+s+')');g.addColorStop(0.45,'rgba(0,0,0,'+(s*0.32).toFixed(3)+')');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();
}
function pSpec(x,y,r,a){
  a=a||0.18;ctx.save();ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.22,y-r*0.18,0,x,y,r*0.55);
  g.addColorStop(0,'rgba(255,255,255,'+a+')');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();
}
function pAtm(x,y,r,col,s){
  s=s||0.15;ctx.save();ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x,y,r*0.82,x,y,r*1.30);
  g.addColorStop(0,col.replace(/[\d.]+\)$/,s.toFixed(3)+')'));
  g.addColorStop(0.6,col.replace(/[\d.]+\)$/,(s*0.30).toFixed(3)+')'));
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);ctx.restore();
}
function pActive(x,y,r,now){
  ctx.save();ctx.globalCompositeOperation='screen';
  var pulse=0.65+0.35*Math.sin(now*0.0026);
  var g=ctx.createRadialGradient(x,y,r*0.5,x,y,r*2.4);
  g.addColorStop(0,'rgba(200,168,75,'+(0.28*pulse).toFixed(3)+')');
  g.addColorStop(0.5,'rgba(200,168,75,'+(0.10*pulse).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  ctx.globalAlpha=0.20*pulse;
  ctx.strokeStyle='rgba(255,48,48,0.70)';ctx.lineWidth=1.2;
  ctx.beginPath();ctx.arc(x+1.5,y,r*1.08,0,Math.PI*2);ctx.stroke();
  ctx.strokeStyle='rgba(48,48,255,0.70)';
  ctx.beginPath();ctx.arc(x-1.5,y,r*1.08,0,Math.PI*2);ctx.stroke();
  ctx.globalAlpha=1;ctx.restore();
}

/* ── PLANET DRAW FUNCTIONS ───────────────────────────────────── */
function drawMercury(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#ddc8a0','#b89060','#8a6030','#5a3c18','#32200a');
  /* 6 craters */
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  [[0.3,0.15,0.20],[-0.25,0.30,0.15],[0.05,-0.28,0.18],[-0.12,0.05,0.09],[0.38,-0.18,0.12],[-0.35,-0.22,0.13]].forEach(function(c){
    var cg=ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0,x+c[0]*r,y+c[1]*r,c[2]*r);
    cg.addColorStop(0,'rgba(30,14,5,0.58)');cg.addColorStop(0.6,'rgba(50,28,10,0.26)');cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply';ctx.fillStyle=cg;ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pLimb(x,y,r,'rgba(220,185,120,0.62)');pDark(x,y,r,0.65);pSpec(x,y,r,0.10);
  ctx.restore();
}

function drawVenus(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#ffe8a5','#ecc040','#c88520','#9c5c10','#683808');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  for(var i=0;i<6;i++){
    var by=y-r*0.75+i*r*0.28+Math.sin(now*0.0000105+i*1.2)*r*0.030;
    var ba=0.12+0.10*Math.abs(Math.sin(i*0.80+now*0.0000090));
    var bd=ctx.createLinearGradient(x-r,by,x+r,by+r*0.08);
    bd.addColorStop(0,'rgba(255,238,162,0)');bd.addColorStop(0.5,'rgba(255,230,140,'+ba+')');bd.addColorStop(1,'rgba(255,238,162,0)');
    ctx.globalCompositeOperation='overlay';ctx.fillStyle=bd;ctx.fillRect(x-r,by,r*2,r*0.20);
  }
  ctx.restore();
  pAtm(x,y,r,'rgba(255,208,78,0.15)',0.15);
  pLimb(x,y,r,'rgba(255,226,136,0.65)');pDark(x,y,r,0.56);pSpec(x,y,r,0.13);
  ctx.restore();
}

function drawEarth(x,y,r,now){
  ctx.save();

  /* ── OCEAN — deep teal to navy, matches wallpaper ── */
  var ocean = ctx.createRadialGradient(x-r*0.18,y-r*0.14,0, x+r*0.12,y+r*0.14,r*1.02);
  ocean.addColorStop(0,   '#c8f0f8');  /* bright teal highlight */
  ocean.addColorStop(0.08,'#6cd4e8');
  ocean.addColorStop(0.20,'#28a8d0');
  ocean.addColorStop(0.38,'#0a70b0');
  ocean.addColorStop(0.58,'#053e80');
  ocean.addColorStop(0.78,'#031e50');
  ocean.addColorStop(1,   '#010c28');
  ctx.fillStyle = ocean;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation = 'source-over';

  /* ── LAND — continent blobs ── */
  function land(ox,oy,rx,R,G,B,a){
    var g=ctx.createRadialGradient(x+ox*r,y+oy*r,0,x+ox*r,y+oy*r,rx*r);
    g.addColorStop(0,'rgba('+R+','+G+','+B+','+a+')');
    g.addColorStop(0.45,'rgba('+R+','+G+','+B+','+(a*0.55).toFixed(2)+')');
    g.addColorStop(0.80,'rgba('+R+','+G+','+B+','+(a*0.18).toFixed(2)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  }

  /* Australia — RED/ORANGE like wallpaper */
  land( 0.46, 0.30, 0.20, 195, 80,  28, 0.96);
  land( 0.54, 0.22, 0.10, 180, 65,  20, 0.88);
  land( 0.60, 0.38, 0.08,  85,140,  55, 0.80); /* green east coast */

  /* Africa — warm brown */
  land( 0.10,-0.02, 0.20, 210,165,  80, 0.90);
  land( 0.14, 0.18, 0.15, 160,130,  60, 0.88);
  land( 0.18, 0.05, 0.10,  55,120,  45, 0.85); /* Congo green */
  land( 0.06,-0.08, 0.10, 225,180,  90, 0.85); /* Sahara */

  /* Middle East / Arabia — tan */
  land( 0.24,-0.06, 0.12, 220,185, 100, 0.88);

  /* Europe */
  land( 0.06,-0.22, 0.10,  80,150,  58, 0.84);
  land( 0.10,-0.30, 0.08,  70,140,  52, 0.80);

  /* Asia */
  land( 0.34,-0.28, 0.26,  88,155,  62, 0.80);
  land( 0.46,-0.10, 0.14, 105,165,  65, 0.82);
  land( 0.36, 0.06, 0.10, 145,175,  72, 0.84); /* India */
  land( 0.50, 0.06, 0.10,  55,125,  48, 0.82); /* SE Asia */

  /* Americas */
  land(-0.32,-0.26, 0.20,  78,138,  55, 0.86);
  land(-0.22, 0.20, 0.14,  42,108,  40, 0.90); /* Amazon */
  land(-0.30, 0.24, 0.05, 130,110,  62, 0.80); /* Andes */
  land(-0.10,-0.50, 0.08, 218,228, 238, 0.85); /* Greenland */

  /* Antarctica */
  var ant=ctx.createRadialGradient(x,y+r*0.86,0,x,y+r*0.86,r*0.28);
  ant.addColorStop(0,'rgba(248,252,255,0.96)'); ant.addColorStop(0.5,'rgba(235,245,255,0.70)'); ant.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ant; ctx.fillRect(0,0,W,H);

  /* North pole ice */
  var np=ctx.createRadialGradient(x,y-r*0.80,0,x,y-r*0.80,r*0.24);
  np.addColorStop(0,'rgba(245,252,255,0.90)'); np.addColorStop(0.5,'rgba(228,244,255,0.60)'); np.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np; ctx.fillRect(0,0,W,H);

  /* ── THICK CLOUDS — wallpaper style ── */
  ctx.globalCompositeOperation='screen';

  /* Large swirling cloud mass — top center/left (cyclone) */
  var cSpiral=now*0.000055;
  for(var ci=0;ci<5;ci++){
    var ca=cSpiral+ci*(Math.PI*2/5);
    var cr2=r*(0.12+ci*0.060);
    var cx2=x-r*0.24+Math.cos(ca)*cr2*0.55;
    var cy2=y-r*0.08+Math.sin(ca)*cr2*0.30;
    var cg=ctx.createRadialGradient(cx2,cy2,0,cx2,cy2,r*(0.18+ci*0.045));
    cg.addColorStop(0,'rgba(255,255,255,'+(0.42-ci*0.06)+')');
    cg.addColorStop(0.4,'rgba(248,252,255,'+(0.22-ci*0.03)+')');
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cg; ctx.fillRect(0,0,W,H);
  }

  /* Indian ocean cloud band */
  var cb=[
    [x+r*0.28,y+r*0.14,r*0.28,0.36],
    [x-r*0.08,y+r*0.32,r*0.24,0.30],
    [x-r*0.44,y-r*0.10,r*0.20,0.32],
    [x+r*0.46,y-r*0.18,r*0.16,0.28],
    [x-r*0.18,y-r*0.42,r*0.18,0.26],
    [x+r*0.08,y+r*0.55,r*0.22,0.24],
  ];
  cb.forEach(function(c){
    var drift=Math.sin(now*0.0000068+c[0]*0.001)*r*0.018;
    var g=ctx.createRadialGradient(c[0]+drift,c[1],0,c[0]+drift,c[1],c[2]);
    g.addColorStop(0,'rgba(255,255,255,'+c[3]+')');
    g.addColorStop(0.38,'rgba(245,250,255,'+(c[3]*0.55).toFixed(3)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  });

  /* Terminator shadow — night side */
  ctx.globalCompositeOperation='multiply';
  var term=ctx.createRadialGradient(x+r*0.30,y+r*0.24,r*0.10,x+r*0.30,y+r*0.24,r*1.12);
  term.addColorStop(0,'rgba(0,0,0,0)');
  term.addColorStop(0.55,'rgba(0,0,0,0.15)');
  term.addColorStop(0.78,'rgba(0,0,0,0.52)');
  term.addColorStop(1,'rgba(0,0,0,0.78)');
  ctx.fillStyle=term; ctx.fillRect(0,0,W,H);

  /* Ocean depth shading */
  ctx.globalCompositeOperation='multiply';
  var depth=ctx.createRadialGradient(x-r*0.42,y+r*0.10,0,x-r*0.42,y+r*0.10,r*0.50);
  depth.addColorStop(0,'rgba(0,10,40,0.22)'); depth.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=depth; ctx.fillRect(0,0,W,H);

  ctx.restore();

  /* ── ATMOSPHERE RIM — thick blue like wallpaper ── */
  ctx.save(); ctx.globalCompositeOperation='screen';

  var atm1=ctx.createRadialGradient(x,y,r*0.85,x,y,r*1.10);
  atm1.addColorStop(0,'rgba(80,180,255,0.55)');
  atm1.addColorStop(0.4,'rgba(50,145,235,0.28)');
  atm1.addColorStop(0.7,'rgba(30,110,210,0.12)');
  atm1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm1; ctx.fillRect(0,0,W,H);

  /* Outer glow */
  var atm2=ctx.createRadialGradient(x,y,r*0.94,x,y,r*1.28);
  atm2.addColorStop(0,'rgba(120,210,255,0.48)');
  atm2.addColorStop(0.35,'rgba(75,175,248,0.20)');
  atm2.addColorStop(0.65,'rgba(40,130,220,0.08)');
  atm2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm2; ctx.fillRect(0,0,W,H);

  /* Limb brightening — upper left like wallpaper */
  var limb=ctx.createRadialGradient(x-r*0.28,y-r*0.22,r*0.88,x-r*0.10,y-r*0.08,r*1.18);
  limb.addColorStop(0,'rgba(160,230,255,0.42)');
  limb.addColorStop(0.5,'rgba(100,195,255,0.16)');
  limb.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=limb; ctx.fillRect(0,0,W,H);
  ctx.restore();

  /* ── SPECULAR HIGHLIGHT — bright white top-left ── */
  ctx.save(); ctx.globalCompositeOperation='screen';
  var spec=ctx.createRadialGradient(x-r*0.20,y-r*0.16,0,x-r*0.08,y-r*0.06,r*0.52);
  spec.addColorStop(0,'rgba(255,255,255,0.72)');
  spec.addColorStop(0.18,'rgba(240,250,255,0.38)');
  spec.addColorStop(0.45,'rgba(200,235,255,0.10)');
  spec.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=spec; ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.restore();

  /* Rim darkening */
  pDark(x,y,r,0.48);

  ctx.restore();
}

function drawMoon(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#d5ccc0','#a89280','#7a6450','#524038','#302218');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  [[-0.14,-0.10,0.36],[0.18,0.14,0.26],[-0.28,0.22,0.20]].forEach(function(m){
    var mg=ctx.createRadialGradient(x+m[0]*r,y+m[1]*r,0,x+m[0]*r,y+m[1]*r,m[2]*r);
    mg.addColorStop(0,'rgba(48,36,28,0.52)');mg.addColorStop(0.6,'rgba(58,44,32,0.24)');mg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply';ctx.fillStyle=mg;ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pLimb(x,y,r,'rgba(208,198,182,0.52)');pDark(x,y,r,0.68);pSpec(x,y,r,0.09);
  ctx.restore();
}

function drawMars(x,y,r,now){
  ctx.save();
  var base=ctx.createRadialGradient(x-r*0.24,y-r*0.20,0,x+r*0.10,y+r*0.10,r*1.02);
  base.addColorStop(0,'#eeb088');base.addColorStop(0.20,'#d07048');base.addColorStop(0.42,'#b85030');
  base.addColorStop(0.65,'#8c3820');base.addColorStop(0.85,'#602010');base.addColorStop(1,'#3c1008');
  ctx.fillStyle=base;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  /* Valles Marineris */
  ctx.globalCompositeOperation='multiply';
  var vm=ctx.createLinearGradient(x-r*0.52,y+r*0.04,x+r*0.18,y+r*0.14);
  vm.addColorStop(0,'rgba(78,14,4,0)');vm.addColorStop(0.2,'rgba(40,6,2,0.65)');vm.addColorStop(0.8,'rgba(38,5,1,0.70)');vm.addColorStop(1,'rgba(78,14,4,0)');
  ctx.fillStyle=vm;ctx.fillRect(x-r,y+r*0.02,r*2,r*0.11);
  /* polar caps */
  ctx.globalCompositeOperation='screen';
  var np=ctx.createRadialGradient(x,y-r*0.75,0,x,y-r*0.75,r*0.26);
  np.addColorStop(0,'rgba(248,240,228,0.92)');np.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np;ctx.fillRect(0,0,W,H);
  ctx.restore();
  ctx.save();ctx.globalCompositeOperation='screen';
  var mAtm=ctx.createRadialGradient(x,y,r*0.87,x,y,r*1.20);
  mAtm.addColorStop(0,'rgba(205,118,58,0.14)');mAtm.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=mAtm;ctx.fillRect(0,0,W,H);ctx.restore();
  pLimb(x,y,r,'rgba(232,158,105,0.65)');pDark(x,y,r,0.60);pSpec(x,y,r,0.09);
  ctx.restore();
}

function drawJupiter(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#f0e0c0','#d8c090','#b89860','#8a6830','#604020');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  /* 7 bands */
  [[-0.65,0.13],[-0.45,0.10],[-0.28,0.15],[-0.08,0.12],[0.08,0.16],[0.28,0.12],[0.48,0.14]].forEach(function(bd,idx){
    var yo=bd[0]+Math.sin(now*0.0000042+idx*0.6)*0.010;
    var cols=['rgba(158,108,50,0.58)','rgba(200,162,92,0.44)','rgba(145,88,36,0.62)','rgba(194,158,88,0.48)','rgba(138,86,34,0.64)','rgba(182,132,62,0.50)','rgba(148,98,46,0.54)'];
    var lg=ctx.createLinearGradient(x-r,y+yo*r,x+r,y+(yo+bd[1])*r);
    var ct=cols[idx].replace(/[\d.]+\)$/,'0)');
    lg.addColorStop(0,ct);lg.addColorStop(0.3,cols[idx]);lg.addColorStop(0.7,cols[idx]);lg.addColorStop(1,ct);
    ctx.globalCompositeOperation='overlay';ctx.fillStyle=lg;ctx.fillRect(x-r,y+yo*r,r*2,bd[1]*r);
  });
  /* GRS */
  var gx=x+r*0.24+Math.sin(now*0.0000052)*r*0.04,gy=y+r*0.12;
  ctx.globalCompositeOperation='source-over';
  var grs=ctx.createRadialGradient(gx,gy,0,gx,gy,r*0.16);
  grs.addColorStop(0,'rgba(175,45,16,0.88)');grs.addColorStop(0.5,'rgba(155,32,10,0.68)');grs.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=grs;ctx.fillRect(0,0,W,H);
  ctx.restore();
  pLimb(x,y,r,'rgba(238,210,158,0.52)');pDark(x,y,r,0.54);pSpec(x,y,r,0.11);
  ctx.restore();
}

function drawVega(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#ddd0ff','#9868e0','#6838b8','#401878','#200848');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  ctx.globalCompositeOperation='screen';
  for(var vi=0;vi<10;vi++){
    var va=(vi/10)*Math.PI*2+now*0.0000145;
    var vr=r*(0.10+0.62*Math.abs(Math.sin(vi*0.88+now*0.0000108)));
    ctx.beginPath();ctx.moveTo(x+Math.cos(va)*r*0.06,y+Math.sin(va)*r*0.06);
    ctx.lineTo(x+Math.cos(va)*vr,y+Math.sin(va)*vr);
    ctx.strokeStyle='rgba(195,162,255,0.18)';ctx.lineWidth=0.65;ctx.stroke();
  }
  var pulse=0.18+0.15*Math.sin(now*0.0034);
  var cp=ctx.createRadialGradient(x,y,0,x,y,r*0.44);
  cp.addColorStop(0,'rgba(222,208,255,'+pulse+')');cp.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=cp;ctx.fillRect(0,0,W,H);
  ctx.restore();
  ctx.globalCompositeOperation='screen';
  var ec=ctx.createRadialGradient(x,y,r*0.48,x,y,r*2.10);
  ec.addColorStop(0,'rgba(148,88,255,'+(0.28+0.10*Math.sin(now*0.0022)).toFixed(3)+')');
  ec.addColorStop(0.45,'rgba(115,65,215,0.09)');ec.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ec;ctx.fillRect(0,0,W,H);
  pAtm(x,y,r,'rgba(148,88,255,0.22)',0.22);
  pLimb(x,y,r,'rgba(192,162,255,0.70)');pDark(x,y,r,0.54);pSpec(x,y,r,0.20);
  ctx.restore();
}

/* ================================================================
   RENDER
   ================================================================ */
function render(dt, now){
  drawBg(now);
  drawDust(now);
  drawStars(now);

  /* orbit rings — back layer */
  for (var i = 0; i < PLANETS.length; i++){
    drawOrbitRing(PLANETS[i], now);
  }

  drawSun(now);

  /* planets — compute positions, sort by Y (far-to-near) */
  var posed = PLANETS.map(function(p, idx){
    var pos = planetPos(p, now);
    return {p:p, pos:pos, idx:idx};
  });
  /* sort by y so nearer planets draw on top */
  posed.sort(function(a,b){ return a.pos.y - b.pos.y; });

  _planetPositionsCache = [];
  for (var i = 0; i < PLANETS.length; i++){
    _planetPositionsCache.push({x:0,y:0}); /* pre-fill */
  }

  for (var i = 0; i < posed.length; i++){
    var item = posed[i];
    var p = item.p, pos = item.pos;
    var r = getR(p);

    _planetPositionsCache[item.idx] = {x:pos.x, y:pos.y};

    if (p.route === activeRoute) pActive(pos.x, pos.y, r, now);
    p.draw(pos.x, pos.y, r, now);
    if (p.moon){
      var moonR = r * 0.29;
      var moonOff = r * 1.55 + Math.sin(now*0.00095)*r*0.12;
      drawMoon(pos.x + moonOff, pos.y + r*0.22, moonR, now);
    }
    drawLabel(p, pos);
  }
}

/* ================================================================
   PUBLIC API
   ================================================================ */
window.KD_setState = function(){};
window.KD_setRoute = function(r){
  if (!ROUTE_HUE[r]) return;
  activeRoute = r;
  _tgtHue = ROUTE_HUE[r] || 208;
  document.querySelectorAll('.rpill,.ctx-tag,.route-chip').forEach(function(el){
    el.classList.toggle('active', el.dataset.r === r);
  });
};
window.KD_pulse    = function(){};
window.LYLA_thinking = function(){};
window.LYLA_answered = function(){};
window.setRoute = window.KD_setRoute;

/* ── INIT ────────────────────────────────────────────────────── */
doResize();
if (cv.style){
  cv.style.willChange = 'transform';
  cv.style.transform  = 'translateZ(0)';
}
requestAnimationFrame(function(now){
  doResize(); _last = now;
  _raf = requestAnimationFrame(loop);
});

})();
