/* ================================================================
   KING DIADEM — Galaxy Scene v40 ULTRA CINEMATIC SOLAR SYSTEM
   144hz-240hz capable  ·  Delta-time physics  ·  Pastel deep space
   Full solar system: Mercury Venus Earth Moon Mars Jupiter Saturn
   Uranus Neptune + VEGA node  ·  Saturn rings  ·  Asteroid belt
   Volumetric nebula  ·  Star diffraction  ·  Lens flare  ·  Corona
   ================================================================ */
(function(){
'use strict';

/* ── CANVAS SETUP ── */
var cv = document.getElementById('galaxy');
if(!cv) return;
var ctx = cv.getContext('2d', {alpha:true, desynchronized:true});
/* desynchronized:true → bypass vsync lock → native 144/240hz capable */

var W=0, H=0;
var _raf=null, _last=0, _dt=0;
var activeRoute = 'general';

/* Route → hue mapping for ambient tint */
var ROUTE_HUE = {
  general: 208,
  risk:     22,
  collapse: 338,
  survival: 142,
  civil:    268,
  vega:     286
};
var _tgtHue = 208, _curHue = 208;

/* ================================================================
   HIGH REFRESH RATE LOOP
   performance.now() delta → physics correct at any Hz
   ================================================================ */
function loop(now){
  _raf = requestAnimationFrame(loop);
  _dt  = Math.min(now - _last, 50); /* cap at 50ms to prevent spiral */
  _last = now;
  render(_dt, now);
}

/* ── RESIZE ── */
var _rT;
function doResize(){
  W = cv.width  = window.innerWidth;
  H = cv.height = window.innerHeight;
  buildStars();
  buildDust();
  buildAsteroidBelt();
}
window.addEventListener('resize', function(){
  clearTimeout(_rT);
  _rT = setTimeout(doResize, 80);
}, {passive:true});

/* ================================================================
   STAR FIELD
   500 stars · 4 size tiers · color temperature · pastel tint
   cross diffraction spikes on bright stars
   ================================================================ */
var STARS = [];
function buildStars(){
  STARS = [];
  var n = Math.min(500, Math.floor(W * H / 2800));
  for(var i=0; i<n; i++){
    var sz = Math.random();
    var bright = sz > 0.93;
    STARS.push({
      x:  Math.random() * W,
      y:  Math.random() * H,
      r:  sz < 0.50 ? 0.28 + Math.random()*0.45 :
          sz < 0.78 ? 0.45 + Math.random()*0.75 :
          sz < 0.93 ? 0.75 + Math.random()*1.10 :
                      1.20 + Math.random()*2.20,
      a:  0.06 + Math.random()*0.72,
      ph: Math.random() * Math.PI * 2,
      sp: 0.15 + Math.random() * 0.70,
      /* color temperature: blue-white / white / warm */
      ct: Math.random()<0.28 ? 'blue' :
          Math.random()<0.15 ? 'warm' : 'white',
      cross:   bright && Math.random()<0.55,
      twinkle: Math.random()<0.65,
      /* pastel tint — subtle, muted */
      pastel:  Math.random()<0.18,
      pastelH: [265,285,305,185,340][Math.floor(Math.random()*5)]
    });
  }
}

function drawStars(now){
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  for(var i=0; i<STARS.length; i++){
    var s = STARS[i];
    var tw = s.twinkle
      ? s.a * (0.42 + 0.58 * Math.sin(now * s.sp * 0.00048 + s.ph))
      : s.a;
    /* color */
    var col;
    if(s.pastel){
      col = 'hsla(' + s.pastelH + ',28%,82%,' + tw.toFixed(3) + ')';
    } else if(s.ct === 'blue'){
      col = 'rgba(165,200,255,' + tw.toFixed(3) + ')';
    } else if(s.ct === 'warm'){
      col = 'rgba(255,228,185,' + tw.toFixed(3) + ')';
    } else {
      col = 'rgba(210,225,248,' + tw.toFixed(3) + ')';
    }
    /* diffraction cross on bright stars */
    if(s.cross && tw > s.a * 0.62){
      ctx.save();
      ctx.strokeStyle = col;
      ctx.lineWidth   = 0.45;
      var cl = s.r * 3.8;
      ctx.beginPath(); ctx.moveTo(s.x-cl, s.y);   ctx.lineTo(s.x+cl, s.y);   ctx.stroke();
      ctx.beginPath(); ctx.moveTo(s.x,   s.y-cl); ctx.lineTo(s.x,   s.y+cl); ctx.stroke();
      ctx.lineWidth   = 0.22;
      ctx.globalAlpha = 0.38;
      var cl2 = cl * 0.62;
      ctx.beginPath(); ctx.moveTo(s.x-cl2, s.y-cl2); ctx.lineTo(s.x+cl2, s.y+cl2); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(s.x+cl2, s.y-cl2); ctx.lineTo(s.x-cl2, s.y+cl2); ctx.stroke();
      ctx.restore();
    }
    ctx.beginPath();
    ctx.arc(s.x, s.y, s.r, 0, Math.PI*2);
    ctx.fillStyle = col;
    ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   VOLUMETRIC DUST — nebula particles, pastel haze
   Hues: dusty violet, muted rose, pale teal, sage
   ================================================================ */
var DUST = [];
function buildDust(){
  DUST = [];
  var n = Math.min(200, Math.floor(W * H / 7000));
  var hues = [265, 285, 305, 185, 200, 340, 355, 210];
  for(var i=0; i<n; i++){
    DUST.push({
      x:   Math.random() * W,
      y:   Math.random() * H,
      r:   12 + Math.random() * 42,
      a:   0.005 + Math.random() * 0.018,
      ph:  Math.random() * Math.PI * 2,
      sp:  0.055 + Math.random() * 0.175,
      hue: hues[Math.floor(Math.random() * hues.length)],
      sat: 16 + Math.random() * 26, /* desaturated = pastel */
      lum: 55  + Math.random() * 22
    });
  }
}

function drawDust(now){
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  for(var i=0; i<DUST.length; i++){
    var d = DUST[i];
    var da = d.a * (0.42 + 0.58 * Math.sin(now * d.sp * 0.00020 + d.ph));
    var g = ctx.createRadialGradient(d.x,d.y,0, d.x,d.y,d.r);
    g.addColorStop(0, 'hsla(' + d.hue + ',' + d.sat + '%,' + d.lum + '%,' + da.toFixed(4) + ')');
    g.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.fillRect(d.x - d.r, d.y - d.r, d.r*2, d.r*2);
  }
  ctx.restore();
}

/* ================================================================
   ASTEROID BELT — micro particles between Mars & Jupiter
   ================================================================ */
var BELT = [];
function buildAsteroidBelt(){
  BELT = [];
  /* y range between Mars (yF≈0.530) and Jupiter (yF≈0.668) */
  var y1 = H * 0.600, y2 = H * 0.640;
  var n  = Math.min(140, Math.floor(W / 5.5));
  for(var i=0; i<n; i++){
    BELT.push({
      x:  Math.random() * W,
      y:  y1 + Math.random() * (y2 - y1),
      r:  0.4 + Math.random() * 1.8,
      a:  0.06 + Math.random() * 0.32,
      ph: Math.random() * Math.PI * 2,
      sp: 0.08 + Math.random() * 0.32,
      vx: (Math.random() - 0.5) * 0.10
    });
  }
}

function drawBelt(dt, now){
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  for(var i=0; i<BELT.length; i++){
    var b = BELT[i];
    b.x += b.vx * (dt / 16);
    if(b.x < -4) b.x = W + 4;
    if(b.x > W+4) b.x = -4;
    var ba = b.a * (0.38 + 0.62 * Math.sin(now * b.sp * 0.00038 + b.ph));
    ctx.beginPath();
    ctx.arc(b.x, b.y, b.r, 0, Math.PI*2);
    ctx.fillStyle = 'rgba(185,175,160,' + ba.toFixed(3) + ')';
    ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   DEEP SPACE BACKGROUND
   Layered radial + linear gradients · pastel nebula undertone
   ================================================================ */
function drawBg(now){
  ctx.clearRect(0, 0, W, H);

  /* primary — blue-black deep space */
  var bg = ctx.createLinearGradient(0, 0, 0, H);
  bg.addColorStop(0,    '#0d1528');
  bg.addColorStop(0.18, '#09101e');
  bg.addColorStop(0.40, '#070e1a');
  bg.addColorStop(0.65, '#060c16');
  bg.addColorStop(0.85, '#050a12');
  bg.addColorStop(1,    '#03070e');
  ctx.fillStyle = bg;
  ctx.fillRect(0, 0, W, H);

  ctx.save();
  ctx.globalCompositeOperation = 'screen';

  /* LEFT nebula — dusty violet (pastel, power) */
  var nb1 = ctx.createRadialGradient(W*0.12, H*0.32, 0, W*0.12, H*0.32, W*0.58);
  nb1.addColorStop(0, 'rgba(88,60,138,0.068)');
  nb1.addColorStop(0.40, 'rgba(68,48,108,0.030)');
  nb1.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = nb1;
  ctx.fillRect(0, 0, W, H);

  /* RIGHT nebula — dusty rose */
  var nb2 = ctx.createRadialGradient(W*0.90, H*0.60, 0, W*0.90, H*0.60, W*0.52);
  nb2.addColorStop(0, 'rgba(128,60,88,0.058)');
  nb2.addColorStop(0.45, 'rgba(98,44,66,0.025)');
  nb2.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = nb2;
  ctx.fillRect(0, 0, W, H);

  /* CENTER spine — pale teal backlight behind planet column */
  var spine = ctx.createRadialGradient(W*0.5, H*0.5, 0, W*0.5, H*0.5, W*0.42);
  spine.addColorStop(0, 'rgba(42,82,118,0.050)');
  spine.addColorStop(0.6, 'rgba(28,52,78,0.018)');
  spine.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = spine;
  ctx.fillRect(0, 0, W, H);

  /* BOTTOM — deep void gradient */
  var bot = ctx.createRadialGradient(W*0.5, H*0.95, 0, W*0.5, H*0.95, W*0.6);
  bot.addColorStop(0, 'rgba(5,15,35,0.06)');
  bot.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = bot;
  ctx.fillRect(0, 0, W, H);

  /* route hue ambient tint */
  _curHue += (_tgtHue - _curHue) * 0.005 * (_dt / 16);
  var rt = ctx.createRadialGradient(W*0.5, H*0.5, 0, W*0.5, H*0.5, W*0.82);
  rt.addColorStop(0, 'hsla(' + _curHue + ',30%,16%,0.028)');
  rt.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = rt;
  ctx.fillRect(0, 0, W, H);

  ctx.restore();
}

/* ================================================================
   SUN — proportional corona, animated granulation, sunspots
   lens flare, solar wind rays, chromosphere
   ================================================================ */
function drawSun(now){
  var cx = W * 0.50;
  var cy = H * (-0.015);
  /* proportional radius — 28-34% of min dimension */
  var Rs = Math.min(W, H) * (W < 420 ? 0.34 : W < 680 ? 0.30 : 0.27);

  ctx.save();

  /* ── OUTER CORONA — 3 layered radial glows ── */
  ctx.globalCompositeOperation = 'screen';
  var CORONA = [
    [Rs*5.2, 0.038, '255,92,6'],
    [Rs*3.0, 0.082, '255,112,10'],
    [Rs*1.82, 0.158, '255,128,16']
  ];
  CORONA.forEach(function(c){
    var g = ctx.createRadialGradient(cx, cy, Rs*0.38, cx, cy, c[0]);
    g.addColorStop(0,   'rgba(' + c[2] + ',' + c[1] + ')');
    g.addColorStop(0.42, 'rgba(' + c[2] + ',' + (c[1]*0.38).toFixed(3) + ')');
    g.addColorStop(1,   'rgba(0,0,0,0)');
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, H);
  });

  /* ── SOLAR WIND RAYS — 14 animated streamers ── */
  ctx.save();
  for(var ri=0; ri<14; ri++){
    var rayAng = (ri / 14) * Math.PI * 2 + now * 0.000019;
    var rayLen = Rs * (1.38 + 0.28 * Math.sin(now * 0.00016 + ri * 0.78));
    ctx.globalCompositeOperation = 'screen';
    ctx.globalAlpha = 0.025 + 0.012 * Math.abs(Math.sin(now * 0.00022 + ri));
    var rx1 = cx + Math.cos(rayAng) * Rs * 0.52;
    var ry1 = cy + Math.sin(rayAng) * Rs * 0.52;
    var rx2 = cx + Math.cos(rayAng) * rayLen;
    var ry2 = cy + Math.sin(rayAng) * rayLen;
    var rg  = ctx.createLinearGradient(rx1, ry1, rx2, ry2);
    rg.addColorStop(0, 'rgba(255,148,28,0.90)');
    rg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.strokeStyle = rg;
    ctx.lineWidth   = Rs * 0.075;
    ctx.lineCap     = 'round';
    ctx.beginPath();
    ctx.moveTo(rx1, ry1);
    ctx.lineTo(rx2, ry2);
    ctx.stroke();
  }
  ctx.globalAlpha = 1;
  ctx.restore();

  /* ── CHROMOSPHERE — red-orange flare rim ── */
  ctx.globalCompositeOperation = 'source-over';
  var CHR = ctx.createRadialGradient(cx, cy, Rs*0.88, cx, cy, Rs*1.20);
  CHR.addColorStop(0,    'rgba(148,16,0,0)');
  CHR.addColorStop(0.26, 'rgba(212,44,4,0.54)');
  CHR.addColorStop(0.52, 'rgba(255,65,8,0.34)');
  CHR.addColorStop(0.76, 'rgba(198,36,0,0.14)');
  CHR.addColorStop(1,    'rgba(0,0,0,0)');
  ctx.fillStyle = CHR;
  ctx.beginPath();
  ctx.arc(cx, cy, Rs*1.20, 0, Math.PI*2);
  ctx.fill();

  /* ── SOLAR PROMINENCES — 3 bright flare arcs ── */
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  for(var pi=0; pi<3; pi++){
    var pAng  = (pi / 3) * Math.PI * 2 + now * 0.000010 + pi * 0.8;
    var pLen  = Rs * (0.25 + 0.18 * Math.abs(Math.sin(now * 0.000012 + pi)));
    var px2   = cx + Math.cos(pAng) * Rs;
    var py2   = cy + Math.sin(pAng) * Rs;
    var px3   = cx + Math.cos(pAng + 0.35) * (Rs + pLen);
    var py3   = cy + Math.sin(pAng + 0.35) * (Rs + pLen);
    var pGrad = ctx.createLinearGradient(px2, py2, px3, py3);
    pGrad.addColorStop(0, 'rgba(255,120,30,0.35)');
    pGrad.addColorStop(1, 'rgba(255,60,0,0)');
    ctx.strokeStyle = pGrad;
    ctx.lineWidth   = Rs * 0.038;
    ctx.lineCap     = 'round';
    ctx.beginPath();
    ctx.moveTo(px2, py2);
    ctx.quadraticCurveTo(
      cx + Math.cos(pAng + 0.18) * (Rs * 1.3),
      cy + Math.sin(pAng + 0.18) * (Rs * 1.3),
      px3, py3
    );
    ctx.stroke();
  }
  ctx.restore();

  /* ── PHOTOSPHERE body ── */
  var PH = ctx.createRadialGradient(cx - Rs*0.20, cy - Rs*0.15, 0, cx + Rs*0.06, cy + Rs*0.08, Rs);
  PH.addColorStop(0,    '#fff8d5');
  PH.addColorStop(0.08, '#ffde45');
  PH.addColorStop(0.25, '#ffaa15');
  PH.addColorStop(0.50, '#ff6505');
  PH.addColorStop(0.72, '#d02200');
  PH.addColorStop(0.88, '#981000');
  PH.addColorStop(1,    '#6a0800');
  ctx.fillStyle = PH;
  ctx.beginPath();
  ctx.arc(cx, cy, Rs, 0, Math.PI*2);
  ctx.fill();

  /* ── GRANULATION — 26 animated convection cells ── */
  ctx.save();
  ctx.beginPath();
  ctx.arc(cx, cy, Rs * 0.99, 0, Math.PI*2);
  ctx.clip();
  ctx.globalCompositeOperation = 'overlay';
  for(var gi=0; gi<26; gi++){
    var gAng  = (gi / 26) * Math.PI * 2 + now * 0.000046;
    var gDist = Rs * (0.16 + 0.46 * Math.abs(Math.sin(gi * 1.618 + now * 0.000052)));
    var gx    = cx + Math.cos(gAng) * gDist * (0.58 + 0.42 * Math.cos(gi * 0.9));
    var gy    = cy + Math.sin(gAng) * gDist * (0.48 + 0.42 * Math.sin(gi * 1.1));
    var gr    = Rs * (0.046 + 0.036 * Math.abs(Math.sin(gi * 0.7 + now * 0.000062)));
    var gg    = ctx.createRadialGradient(gx, gy, 0, gx, gy, gr);
    gg.addColorStop(0, 'rgba(255,242,105,0.24)');
    gg.addColorStop(0.5, 'rgba(255,200,60,0.09)');
    gg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = gg;
    ctx.fillRect(0, 0, W, H);
  }
  /* ── SUNSPOTS — 4 dark patches ── */
  ctx.globalCompositeOperation = 'multiply';
  for(var si=0; si<4; si++){
    var sAng  = (si / 4) * Math.PI * 2 + 0.6 + now * 0.000010;
    var sDist = Rs * (0.22 + 0.18 * Math.sin(si * 2.1));
    var sx2   = cx + Math.cos(sAng) * sDist;
    var sy2   = cy + Math.sin(sAng) * sDist;
    var sr    = Rs * (0.032 + 0.016 * Math.abs(Math.sin(si * 1.4)));
    var sg    = ctx.createRadialGradient(sx2, sy2, 0, sx2, sy2, sr);
    sg.addColorStop(0, 'rgba(0,0,0,0.58)');
    sg.addColorStop(0.5, 'rgba(0,0,0,0.28)');
    sg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = sg;
    ctx.fillRect(0, 0, W, H);
  }
  ctx.restore();

  /* ── SPECULAR HIGHLIGHT ── */
  ctx.globalCompositeOperation = 'screen';
  var HI = ctx.createRadialGradient(cx - Rs*0.16, cy - Rs*0.10, 0, cx, cy, Rs);
  HI.addColorStop(0,    'rgba(255,252,205,0.60)');
  HI.addColorStop(0.32, 'rgba(255,215,80,0.10)');
  HI.addColorStop(1,    'rgba(0,0,0,0)');
  ctx.fillStyle = HI;
  ctx.beginPath();
  ctx.arc(cx, cy, Rs, 0, Math.PI*2);
  ctx.fill();

  /* ── LENS FLARE — primary + 2 artifacts ── */
  var lfx = cx + Rs*0.10, lfy = cy + Rs*0.06;
  var LF  = ctx.createRadialGradient(lfx, lfy, 0, lfx, lfy, Rs*0.22);
  LF.addColorStop(0, 'rgba(255,255,240,0.32)');
  LF.addColorStop(0.4, 'rgba(255,225,100,0.08)');
  LF.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = LF;
  ctx.fillRect(0, 0, W, H);

  var lf2x = cx - Rs*0.38, lf2y = cy + Rs*0.28;
  var LF2  = ctx.createRadialGradient(lf2x, lf2y, 0, lf2x, lf2y, Rs*0.10);
  LF2.addColorStop(0, 'rgba(180,210,255,0.14)');
  LF2.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = LF2;
  ctx.fillRect(0, 0, W, H);

  var lf3x = cx + Rs*0.55, lf3y = cy + Rs*0.42;
  var LF3  = ctx.createRadialGradient(lf3x, lf3y, 0, lf3x, lf3y, Rs*0.06);
  LF3.addColorStop(0, 'rgba(255,220,150,0.10)');
  LF3.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = LF3;
  ctx.fillRect(0, 0, W, H);

  ctx.restore();
}

/* ================================================================
   ORBIT RING — elliptical, gradient glow, shimmer dot, CA
   ================================================================ */
function drawOrbit(py, rx, ry, isActive, now){
  ctx.save();
  ctx.globalCompositeOperation = 'screen';

  /* active backlight */
  if(isActive){
    var glow = ctx.createRadialGradient(W*0.5, py, 0, W*0.5, py, ry*3.8);
    glow.addColorStop(0, 'rgba(78,138,218,0.058)');
    glow.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = glow;
    ctx.fillRect(0, 0, W, H);
  }

  /* ring gradient — fades to transparent at edges */
  var a  = isActive ? 0.54 : 0.14;
  var g  = ctx.createLinearGradient(W*0.5 - rx, py, W*0.5 + rx, py);
  g.addColorStop(0,    'rgba(98,146,215,0)');
  g.addColorStop(0.10, 'rgba(135,180,242,' + (a*0.52) + ')');
  g.addColorStop(0.30, 'rgba(165,206,252,' + (a*0.82) + ')');
  g.addColorStop(0.50, 'rgba(194,220,255,' + a + ')');
  g.addColorStop(0.70, 'rgba(165,206,252,' + (a*0.82) + ')');
  g.addColorStop(0.90, 'rgba(135,180,242,' + (a*0.52) + ')');
  g.addColorStop(1,    'rgba(98,146,215,0)');
  ctx.strokeStyle = g;
  ctx.lineWidth   = isActive ? 1.80 : 0.58;
  ctx.beginPath();
  ctx.ellipse(W*0.5, py, rx, ry, 0, 0, Math.PI*2);
  ctx.stroke();

  /* shimmer dot on active orbit */
  if(isActive){
    var ang = now * 0.00044;
    var sx  = W*0.5 + rx * Math.cos(ang);
    var sy  = py   + ry * Math.sin(ang);
    /* white core */
    var sg  = ctx.createRadialGradient(sx, sy, 0, sx, sy, 9);
    sg.addColorStop(0, 'rgba(228,242,255,1.0)');
    sg.addColorStop(0.35, 'rgba(192,220,255,0.55)');
    sg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = sg;
    ctx.fillRect(0, 0, W, H);
    /* chromatic aberration on dot */
    ctx.globalAlpha = 0.28;
    var ra = ctx.createRadialGradient(sx+2.2, sy, 0, sx+2.2, sy, 5.5);
    ra.addColorStop(0, 'rgba(255,55,55,0.88)');
    ra.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = ra;
    ctx.fillRect(0, 0, W, H);
    var ba = ctx.createRadialGradient(sx-2.2, sy, 0, sx-2.2, sy, 5.5);
    ba.addColorStop(0, 'rgba(55,55,255,0.88)');
    ba.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = ba;
    ctx.fillRect(0, 0, W, H);
    ctx.globalAlpha = 1;
  }
  ctx.restore();
}

/* ================================================================
   SHARED PLANET HELPERS
   ================================================================ */
/* Radial gradient base */
function pBase(x,y,r, c0,c1,c2,c3,c4){
  var g = ctx.createRadialGradient(x - r*0.28, y - r*0.22, 0, x + r*0.10, y + r*0.12, r*1.04);
  g.addColorStop(0,    c0);
  g.addColorStop(0.22, c1);
  g.addColorStop(0.50, c2);
  g.addColorStop(0.76, c3);
  g.addColorStop(1,    c4);
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI*2);
  ctx.fill();
}

/* Limb highlight — bright edge on lit side */
function pLimb(x,y,r, col){
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  var g = ctx.createRadialGradient(x - r*0.30, y - r*0.24, 0, x, y, r*1.04);
  g.addColorStop(0,    col);
  g.addColorStop(0.40, 'rgba(255,255,255,0.028)');
  g.addColorStop(1,    'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI*2);
  ctx.fill();
  ctx.restore();
}

/* Shadow terminator — dark side */
function pDark(x,y,r, strength){
  if(strength === undefined) strength = 0.65;
  ctx.save();
  ctx.globalCompositeOperation = 'multiply';
  var g = ctx.createRadialGradient(x + r*0.36, y + r*0.30, 0, x, y, r*1.04);
  g.addColorStop(0,    'rgba(0,0,0,' + strength + ')');
  g.addColorStop(0.42, 'rgba(0,0,0,' + (strength*0.35).toFixed(3) + ')');
  g.addColorStop(1,    'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI*2);
  ctx.fill();
  ctx.restore();
}

/* Specular microglint */
function pSpec(x,y,r, alpha){
  if(alpha === undefined) alpha = 0.20;
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  var g = ctx.createRadialGradient(x - r*0.24, y - r*0.20, 0, x - r*0.04, y - r*0.04, r*0.62);
  g.addColorStop(0,    'rgba(255,255,255,' + alpha + ')');
  g.addColorStop(0.5,  'rgba(255,255,255,' + (alpha*0.18).toFixed(3) + ')');
  g.addColorStop(1,    'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.beginPath();
  ctx.arc(x, y, r, 0, Math.PI*2);
  ctx.fill();
  ctx.restore();
}

/* Atmosphere rim scatter */
function pAtm(x,y,r, col, strength){
  if(strength === undefined) strength = 0.18;
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  var g = ctx.createRadialGradient(x, y, r*0.80, x, y, r*1.34);
  /* parse col to inject strength */
  var c0 = col.replace(/[\d.]+\)$/, strength.toFixed(3) + ')');
  var c1 = col.replace(/[\d.]+\)$/, (strength*0.35).toFixed(3) + ')');
  g.addColorStop(0,    c0);
  g.addColorStop(0.5,  c1);
  g.addColorStop(1,    'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  ctx.restore();
}

/* Active route — gold pulse glow + chromatic aberration ring */
function pActive(x,y,r, now){
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  var pulse = 0.68 + 0.32 * Math.sin(now * 0.0030);
  var g = ctx.createRadialGradient(x, y, r*0.52, x, y, r*2.5);
  g.addColorStop(0,    'rgba(200,168,75,' + (0.30*pulse).toFixed(3) + ')');
  g.addColorStop(0.40, 'rgba(200,168,75,' + (0.12*pulse).toFixed(3) + ')');
  g.addColorStop(1,    'rgba(0,0,0,0)');
  ctx.fillStyle = g;
  ctx.fillRect(0, 0, W, H);
  /* CA ring */
  ctx.globalAlpha = 0.20 * pulse;
  ctx.strokeStyle = 'rgba(255,50,50,0.72)';
  ctx.lineWidth   = 1.5;
  ctx.beginPath(); ctx.arc(x+1.8, y, r*1.10, 0, Math.PI*2); ctx.stroke();
  ctx.strokeStyle = 'rgba(50,50,255,0.72)';
  ctx.beginPath(); ctx.arc(x-1.8, y, r*1.10, 0, Math.PI*2); ctx.stroke();
  ctx.globalAlpha = 1;
  ctx.restore();
}

/* ================================================================
   MERCURY — heavily cratered, grey-brown, barren
   ================================================================ */
function drawMercury(x,y,r,now){
  ctx.save();
  pBase(x,y,r, '#e0c8a0','#c09860','#966c38','#6a4820','#3c2810');

  /* craters with rim highlights */
  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  var CRATERS = [
    [0.32, 0.18, 0.20], [-0.28, 0.32, 0.16], [ 0.08,-0.28, 0.19],
    [-0.12, 0.05, 0.10], [ 0.42,-0.15, 0.13], [-0.38,-0.22, 0.14],
    [ 0.18, 0.40, 0.11], [-0.05,-0.45, 0.12], [ 0.35, 0.42, 0.08],
    [-0.42, 0.18, 0.09], [ 0.05, 0.55, 0.07], [ 0.50,-0.35, 0.10]
  ];
  CRATERS.forEach(function(c){
    var cx2 = x + c[0]*r, cy2 = y + c[1]*r, cr = c[2]*r;
    /* dark bowl */
    var cg = ctx.createRadialGradient(cx2,cy2,0, cx2,cy2,cr);
    cg.addColorStop(0, 'rgba(38,20,8,0.60)');
    cg.addColorStop(0.55,'rgba(62,36,14,0.28)');
    cg.addColorStop(0.82,'rgba(148,110,58,0.10)');
    cg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.globalCompositeOperation = 'multiply';
    ctx.fillStyle = cg; ctx.fillRect(0,0,W,H);
    /* rim highlight */
    ctx.globalCompositeOperation = 'screen';
    var rim = ctx.createRadialGradient(cx2-cr*0.3,cy2-cr*0.3,cr*0.62, cx2,cy2,cr);
    rim.addColorStop(0, 'rgba(0,0,0,0)');
    rim.addColorStop(0.82,'rgba(202,178,132,0.16)');
    rim.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = rim; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();

  pLimb(x,y,r, 'rgba(228,192,120,0.64)');
  pDark(x,y,r, 0.64);
  pSpec(x,y,r, 0.12);
  ctx.restore();
}

/* ================================================================
   VENUS — thick sulphur clouds, orange-yellow banded atmosphere
   ================================================================ */
function drawVenus(x,y,r,now){
  ctx.save();
  pBase(x,y,r, '#ffe8a8','#ecc040','#c88520','#9c5c10','#683808');

  /* rotating cloud bands */
  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  for(var i=0; i<7; i++){
    var by = y - r*0.75 + i*r*0.26 + Math.sin(now*0.000011 + i*1.2)*r*0.034;
    var ba = 0.14 + 0.11*Math.abs(Math.sin(i*0.8 + now*0.000009));
    var bd = ctx.createLinearGradient(x-r, by, x+r, by+r*0.09);
    bd.addColorStop(0, 'rgba(255,238,165,0)');
    bd.addColorStop(0.35,'rgba(255,238,165,' + ba + ')');
    bd.addColorStop(0.65,'rgba(240,205,100,' + ba + ')');
    bd.addColorStop(1, 'rgba(255,238,165,0)');
    ctx.globalCompositeOperation = 'overlay';
    ctx.fillStyle = bd;
    ctx.fillRect(x-r, by, r*2, r*0.20);
  }
  ctx.restore();

  pAtm(x,y,r, 'rgba(255,210,80,0.18)', 0.18);
  pLimb(x,y,r, 'rgba(255,228,138,0.66)');
  pDark(x,y,r, 0.58);
  pSpec(x,y,r, 0.14);
  ctx.restore();
}

/* ================================================================
   EARTH — blue oceans, continents, polar ice, clouds, city lights
   ================================================================ */
function drawEarth(x,y,r,now){
  ctx.save();
  pBase(x,y,r, '#88c8f5','#2878d0','#1558a8','#0c3870','#082448');

  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* continents */
  var CONT = [
    [-0.24,-0.22, 0.26,0.28, 58,138,52, 0.88], /* N America */
    [-0.10, 0.18, 0.16,0.28, 48,122,40, 0.82], /* S America */
    [ 0.12,-0.18, 0.14,0.18, 66,152,58, 0.85], /* Europe    */
    [ 0.12, 0.10, 0.18,0.30, 88,168,72, 0.80], /* Africa    */
    [ 0.38,-0.15, 0.28,0.28, 78,152,62, 0.82], /* Asia      */
    [ 0.38, 0.30, 0.15,0.18,200,168,88, 0.75], /* Australia */
    [ 0.00, 0.78, 0.38,0.14,220,238,255,0.85]  /* Antarctica*/
  ];
  CONT.forEach(function(c){
    var eg = ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0, x+c[0]*r,y+c[1]*r,c[2]*r);
    eg.addColorStop(0,   'rgba(' + c[4] + ',' + c[5] + ',' + c[6] + ',' + c[7] + ')');
    eg.addColorStop(0.50,'rgba(' + c[4] + ',' + c[5] + ',' + c[6] + ',' + (c[7]*0.52).toFixed(2) + ')');
    eg.addColorStop(1,   'rgba(0,0,0,0)');
    ctx.globalCompositeOperation = 'source-over';
    ctx.fillStyle = eg;
    ctx.fillRect(0, 0, W, H);
  });

  /* polar ice caps */
  ctx.globalCompositeOperation = 'screen';
  var np = ctx.createRadialGradient(x, y-r*0.78, 0, x, y-r*0.78, r*0.28);
  np.addColorStop(0, 'rgba(235,248,255,0.92)');
  np.addColorStop(0.5,'rgba(220,240,255,0.55)');
  np.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = np; ctx.fillRect(0,0,W,H);

  var sp = ctx.createRadialGradient(x, y+r*0.82, 0, x, y+r*0.82, r*0.24);
  sp.addColorStop(0, 'rgba(230,245,255,0.85)');
  sp.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = sp; ctx.fillRect(0,0,W,H);

  /* cloud layer — 6 wisps */
  for(var ci=0; ci<6; ci++){
    var cang  = (ci/6)*Math.PI*2 + now*0.000016;
    var cdist = r * (0.22 + 0.32*Math.abs(Math.sin(ci*1.7 + now*0.000014)));
    var cxp   = x + Math.cos(cang)*cdist*(0.62+0.38*Math.cos(ci*0.9));
    var cyp   = y + Math.sin(cang)*cdist*(0.52+0.38*Math.sin(ci*1.1));
    var crr   = r * (0.10 + 0.08*Math.random());
    var clg   = ctx.createRadialGradient(cxp,cyp,0, cxp,cyp,crr);
    clg.addColorStop(0, 'rgba(240,248,255,0.22)');
    clg.addColorStop(0.5,'rgba(225,240,255,0.10)');
    clg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.fillStyle = clg; ctx.fillRect(0,0,W,H);
  }

  /* city lights on dark side */
  var night = ctx.createRadialGradient(x+r*0.44,y+r*0.34,0, x+r*0.44,y+r*0.34,r*0.52);
  night.addColorStop(0, 'rgba(255,240,180,0.058)');
  night.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = night; ctx.fillRect(0,0,W,H);

  ctx.restore(); /* end clip */

  pAtm(x,y,r, 'rgba(65,140,255,0.22)', 0.22);
  pLimb(x,y,r, 'rgba(110,195,255,0.70)');
  pDark(x,y,r, 0.60);
  pSpec(x,y,r, 0.18);
  ctx.restore();
}

/* ================================================================
   MOON — grey, maria, craters, no atmosphere
   ================================================================ */
function drawMoon(x,y,r,now){
  ctx.save();
  pBase(x,y,r, '#d8d0c2','#a89882','#7a6a52','#524438','#302820');

  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* maria (dark basalt plains) */
  var MARIA = [[-0.12,-0.08,0.38],[0.20,0.15,0.28],[-0.30,0.25,0.22],[0.05,-0.30,0.20]];
  MARIA.forEach(function(m){
    var mg = ctx.createRadialGradient(x+m[0]*r,y+m[1]*r,0, x+m[0]*r,y+m[1]*r,m[2]*r);
    mg.addColorStop(0, 'rgba(52,42,34,0.52)');
    mg.addColorStop(0.55,'rgba(62,50,38,0.26)');
    mg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.globalCompositeOperation = 'multiply';
    ctx.fillStyle = mg; ctx.fillRect(0,0,W,H);
  });

  /* craters */
  var MCRATERS = [[0.25,0.10,0.15],[-0.18,-0.25,0.12],[0.05,0.35,0.10],[-0.35,0.08,0.11],[0.38,-0.20,0.08]];
  MCRATERS.forEach(function(c){
    var cg = ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0, x+c[0]*r,y+c[1]*r,c[2]*r);
    cg.addColorStop(0, 'rgba(28,20,14,0.55)');
    cg.addColorStop(0.6,'rgba(48,36,26,0.24)');
    cg.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.globalCompositeOperation = 'multiply';
    ctx.fillStyle = cg; ctx.fillRect(0,0,W,H);
  });

  ctx.restore();

  pLimb(x,y,r, 'rgba(215,205,188,0.54)');
  pDark(x,y,r, 0.66);
  pSpec(x,y,r, 0.10);
  ctx.restore();
}

/* ================================================================
   MARS — red desert, Valles Marineris, Olympus Mons, dust storms
   ================================================================ */
function drawMars(x,y,r,now){
  ctx.save();
  pBase(x,y,r, '#e8a078','#c05838','#984028','#703018','#481808');

  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* Valles Marineris canyon system */
  ctx.globalCompositeOperation = 'multiply';
  var vm = ctx.createLinearGradient(x-r*0.58,y+r*0.04, x+r*0.58,y+r*0.18);
  vm.addColorStop(0,   'rgba(78,16,6,0)');
  vm.addColorStop(0.18,'rgba(52,10,4,0.56)');
  vm.addColorStop(0.50,'rgba(52,10,4,0.60)');
  vm.addColorStop(0.82,'rgba(52,10,4,0.52)');
  vm.addColorStop(1,   'rgba(78,16,6,0)');
  ctx.fillStyle = vm;
  ctx.fillRect(x-r, y+r*0.02, r*2, r*0.15);

  /* Olympus Mons — volcanic shield shadow */
  var om = ctx.createRadialGradient(x-r*0.28,y-r*0.18,0, x-r*0.28,y-r*0.18,r*0.24);
  om.addColorStop(0,  'rgba(38,8,4,0.42)');
  om.addColorStop(0.6,'rgba(58,16,6,0.20)');
  om.addColorStop(1,  'rgba(0,0,0,0)');
  ctx.fillStyle = om; ctx.fillRect(0,0,W,H);

  /* polar ice caps */
  ctx.globalCompositeOperation = 'screen';
  var np = ctx.createRadialGradient(x,y-r*0.76,0, x,y-r*0.76,r*0.28);
  np.addColorStop(0, 'rgba(238,228,215,0.90)');
  np.addColorStop(0.5,'rgba(220,215,205,0.52)');
  np.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = np; ctx.fillRect(0,0,W,H);

  var sp = ctx.createRadialGradient(x,y+r*0.80,0, x,y+r*0.80,r*0.20);
  sp.addColorStop(0, 'rgba(232,222,210,0.80)');
  sp.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = sp; ctx.fillRect(0,0,W,H);

  /* animated dust storm */
  ctx.globalCompositeOperation = 'overlay';
  var ds  = now * 0.000013;
  var dsx = x + Math.cos(ds)*r*0.82;
  var dsy = y + Math.sin(ds)*r*0.58;
  var dg  = ctx.createRadialGradient(dsx,dsy,0, dsx,dsy,r*0.38);
  dg.addColorStop(0, 'rgba(200,140,80,0.20)');
  dg.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = dg; ctx.fillRect(0,0,W,H);

  ctx.restore();

  pAtm(x,y,r, 'rgba(200,100,50,0.12)', 0.12);
  pLimb(x,y,r, 'rgba(235,158,108,0.64)');
  pDark(x,y,r, 0.62);
  pSpec(x,y,r, 0.12);
  ctx.restore();
}

/* ================================================================
   JUPITER — 10 cloud bands, GRS, polar hexagon, animated
   ================================================================ */
function drawJupiter(x,y,r,now){
  ctx.save();
  pBase(x,y,r, '#f0e0c0','#d8c090','#b89860','#8a6830','#604020');

  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* 10 animated cloud bands */
  var BANDS = [
    [-0.72, 0.14, 'rgba(162,110,52,0.60)'],
    [-0.55, 0.10, 'rgba(205,165,95,0.46)'],
    [-0.42, 0.16, 'rgba(148,90,38,0.64)'],
    [-0.23, 0.12, 'rgba(198,160,90,0.50)'],
    [-0.08, 0.18, 'rgba(140,88,36,0.66)'],
    [ 0.12, 0.14, 'rgba(185,135,65,0.52)'],
    [ 0.28, 0.18, 'rgba(122,72,28,0.64)'],
    [ 0.48, 0.12, 'rgba(192,148,75,0.48)'],
    [ 0.62, 0.16, 'rgba(152,100,48,0.56)'],
    [ 0.78, 0.12, 'rgba(168,118,52,0.54)']
  ];
  BANDS.forEach(function(bd, idx){
    var yo  = bd[0] + Math.sin(now*0.0000045 + idx*0.6) * 0.012;
    var lg  = ctx.createLinearGradient(x-r, y+yo*r, x+r, y+(yo+bd[1])*r);
    var col = bd[2];
    var ct  = col.replace(/[\d.]+\)$/, '0)');
    lg.addColorStop(0,   ct);
    lg.addColorStop(0.28, col);
    lg.addColorStop(0.72, col);
    lg.addColorStop(1,   ct);
    ctx.globalCompositeOperation = 'overlay';
    ctx.fillStyle = lg;
    ctx.fillRect(x-r, y+yo*r, r*2, bd[1]*r);
  });

  /* Great Red Spot — animated oval */
  var grsx = x + r*0.22 + Math.sin(now*0.0000055)*r*0.04;
  var grsy = y + r*0.12;
  ctx.globalCompositeOperation = 'source-over';
  /* outer halo */
  var grs0 = ctx.createRadialGradient(grsx,grsy,r*0.12, grsx,grsy,r*0.26);
  grs0.addColorStop(0, 'rgba(140,30,8,0.40)');
  grs0.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grs0; ctx.fillRect(0,0,W,H);
  /* core */
  var grs1 = ctx.createRadialGradient(grsx,grsy,0, grsx,grsy,r*0.18);
  grs1.addColorStop(0, 'rgba(182,50,20,0.88)');
  grs1.addColorStop(0.45,'rgba(162,38,12,0.72)');
  grs1.addColorStop(0.78,'rgba(138,28,8,0.42)');
  grs1.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grs1; ctx.fillRect(0,0,W,H);
  /* inner bright swirl */
  ctx.globalCompositeOperation = 'screen';
  var grs2 = ctx.createRadialGradient(grsx-r*0.04,grsy-r*0.02,0, grsx,grsy,r*0.09);
  grs2.addColorStop(0, 'rgba(220,92,32,0.62)');
  grs2.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = grs2; ctx.fillRect(0,0,W,H);

  /* polar hexagon hint */
  ctx.globalCompositeOperation = 'multiply';
  var phx = ctx.createRadialGradient(x,y-r*0.70,0, x,y-r*0.70,r*0.36);
  phx.addColorStop(0, 'rgba(80,55,30,0.42)');
  phx.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = phx; ctx.fillRect(0,0,W,H);

  ctx.restore();

  pLimb(x,y,r, 'rgba(242,215,165,0.54)');
  pDark(x,y,r, 0.55);
  pSpec(x,y,r, 0.12);
  ctx.restore();
}

/* ================================================================
   SATURN — ring system (D/C/B/Cassini/A/F), cloud bands
   ================================================================ */
function drawSaturn(x,y,r,now){
  ctx.save();

  /* ring x-extent and perspective tilt */
  var ringW = r * 2.65;
  var ringH = r * 0.27;

  /* BACK rings (behind planet) — top half clip */
  ctx.save();
  ctx.beginPath();
  ctx.rect(x - ringW, y - ringH, ringW*2, ringH + 1);
  ctx.clip();
  _saturnRings(x, y, ringW, ringH, 0.52, now);
  ctx.restore();

  /* planet body */
  pBase(x,y,r, '#f8ead8','#e8d0a0','#c8a868','#9a7840','#6e5025');

  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  var SBANDS = [
    [-0.56,0.14,'rgba(200,168,100,0.44)'],
    [-0.38,0.10,'rgba(228,195,135,0.36)'],
    [-0.22,0.16,'rgba(185,148,82,0.50)'],
    [-0.03,0.12,'rgba(215,180,118,0.40)'],
    [ 0.11,0.16,'rgba(175,138,72,0.52)'],
    [ 0.30,0.12,'rgba(208,172,105,0.42)'],
    [ 0.45,0.14,'rgba(182,148,78,0.46)']
  ];
  SBANDS.forEach(function(bd){
    var lg = ctx.createLinearGradient(x-r, y+bd[0]*r, x+r, y+(bd[0]+bd[1])*r);
    var ct = bd[2].replace(/[\d.]+\)$/, '0)');
    lg.addColorStop(0, ct); lg.addColorStop(0.5, bd[2]); lg.addColorStop(1, ct);
    ctx.globalCompositeOperation = 'overlay';
    ctx.fillStyle = lg;
    ctx.fillRect(x-r, y+bd[0]*r, r*2, bd[1]*r);
  });
  ctx.restore();

  pAtm(x,y,r, 'rgba(220,185,120,0.12)', 0.12);
  pLimb(x,y,r, 'rgba(248,228,180,0.60)');
  pDark(x,y,r, 0.52);
  pSpec(x,y,r, 0.15);

  /* FRONT rings (over planet) — bottom half clip */
  ctx.save();
  ctx.beginPath();
  ctx.rect(x - ringW, y, ringW*2, ringH + 2);
  ctx.clip();
  _saturnRings(x, y, ringW, ringH, 0.92, now);
  ctx.restore();

  ctx.restore();
}

/* Saturn ring bands: D · C · B · Cassini Division · A · F */
function _saturnRings(x,y,ringW,ringH,alpha,now){
  var RINGS = [
    {i0:0.40, i1:0.50, col:'rgba(168,142,92,0.18)'},   /* D ring */
    {i0:0.50, i1:0.68, col:'rgba(208,182,128,0.38)'},   /* C ring */
    {i0:0.68, i1:0.92, col:'rgba(228,202,150,0.56)'},   /* B ring */
    {i0:0.92, i1:0.96, col:'rgba(18,12,6,0.04)'},       /* Cassini Division */
    {i0:0.96, i1:1.15, col:'rgba(215,188,138,0.50)'},   /* A ring */
    {i0:1.15, i1:1.20, col:'rgba(188,162,112,0.24)'}    /* F ring */
  ];
  ctx.save();
  RINGS.forEach(function(rg){
    /* radial gradient for ring depth */
    var gr = ctx.createRadialGradient(x,y,rg.i0*ringW, x,y,rg.i1*ringW);
    var baseA = parseFloat(rg.col.match(/[\d.]+\)$/)[0]);
    var a0 = (baseA * alpha).toFixed(3);
    var atop = rg.col.replace(/[\d.]+\)$/, '0)');
    var amid = rg.col.replace(/[\d.]+\)$/, a0 + ')');
    gr.addColorStop(0, atop);
    gr.addColorStop(0.25, amid);
    gr.addColorStop(0.75, amid);
    gr.addColorStop(1, atop);
    ctx.fillStyle = gr;
    ctx.beginPath();
    /* outer ellipse */
    ctx.ellipse(x, y, rg.i1*ringW, rg.i1*ringH, 0, 0, Math.PI*2, false);
    /* inner ellipse (hole) */
    ctx.ellipse(x, y, rg.i0*ringW, rg.i0*ringH, 0, Math.PI*2, 0, true);
    ctx.fill();
  });
  ctx.restore();
}

/* ================================================================
   URANUS — ice giant, pale cyan-green, tilted rings
   ================================================================ */
function drawUranus(x,y,r,now){
  ctx.save();
  pBase(x,y,r, '#c8f0f5','#78d0dc','#38a8bc','#1878a0','#0c5072');

  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  /* subtle cloud banding */
  for(var i=0; i<5; i++){
    var uy = y - r*0.60 + i*r*0.30;
    var ubg = ctx.createLinearGradient(x-r, uy, x+r, uy+r*0.10);
    ubg.addColorStop(0, 'rgba(80,200,220,0)');
    ubg.addColorStop(0.5,'rgba(80,200,220,0.11)');
    ubg.addColorStop(1, 'rgba(80,200,220,0)');
    ctx.globalCompositeOperation = 'screen';
    ctx.fillStyle = ubg;
    ctx.fillRect(x-r, uy, r*2, r*0.18);
  }
  ctx.restore();

  /* tilted ring system — nearly perpendicular to our view */
  ctx.save();
  ctx.globalCompositeOperation = 'screen';
  /* ring 1 */
  ctx.strokeStyle = 'rgba(160,220,232,0.30)';
  ctx.lineWidth   = 1.2;
  ctx.beginPath();
  ctx.ellipse(x, y, r*1.42, r*0.17, Math.PI*0.08, 0, Math.PI*2);
  ctx.stroke();
  /* ring 2 */
  ctx.strokeStyle = 'rgba(140,205,220,0.20)';
  ctx.lineWidth   = 0.7;
  ctx.beginPath();
  ctx.ellipse(x, y, r*1.58, r*0.20, Math.PI*0.08, 0, Math.PI*2);
  ctx.stroke();
  /* ring 3 */
  ctx.strokeStyle = 'rgba(120,190,208,0.12)';
  ctx.lineWidth   = 0.5;
  ctx.beginPath();
  ctx.ellipse(x, y, r*1.70, r*0.22, Math.PI*0.08, 0, Math.PI*2);
  ctx.stroke();
  ctx.restore();

  pAtm(x,y,r, 'rgba(80,210,230,0.20)', 0.20);
  pLimb(x,y,r, 'rgba(178,242,250,0.66)');
  pDark(x,y,r, 0.55);
  pSpec(x,y,r, 0.20);
  ctx.restore();
}

/* ================================================================
   NEPTUNE — deep blue, cloud streaks, Great Dark Spot, Triton
   ================================================================ */
function drawNeptune(x,y,r,now){
  ctx.save();
  pBase(x,y,r, '#8ab8f8','#2858e0','#1235b8','#0c2290','#081870');

  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* bright cloud streaks */
  ctx.globalCompositeOperation = 'screen';
  for(var i=0; i<4; i++){
    var ny  = y - r*0.38 + i*r*0.25 + Math.sin(now*0.000016 + i*2.1)*r*0.042;
    var nba = 0.18 + 0.10*Math.abs(Math.sin(i*1.2 + now*0.000012));
    var nb  = ctx.createLinearGradient(x-r, ny, x+r, ny+r*0.06);
    nb.addColorStop(0, 'rgba(180,215,255,0)');
    nb.addColorStop(0.38,'rgba(180,215,255,' + nba + ')');
    nb.addColorStop(0.62,'rgba(180,215,255,' + nba + ')');
    nb.addColorStop(1, 'rgba(180,215,255,0)');
    ctx.fillStyle = nb;
    ctx.fillRect(x-r, ny, r*2, r*0.12);
  }

  /* Great Dark Spot */
  ctx.globalCompositeOperation = 'multiply';
  var gds = ctx.createRadialGradient(x-r*0.18,y+r*0.08,0, x-r*0.18,y+r*0.08,r*0.22);
  gds.addColorStop(0, 'rgba(4,8,58,0.58)');
  gds.addColorStop(0.55,'rgba(6,12,76,0.28)');
  gds.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = gds; ctx.fillRect(0,0,W,H);

  ctx.restore();

  pAtm(x,y,r, 'rgba(60,130,255,0.20)', 0.20);
  pLimb(x,y,r, 'rgba(130,200,255,0.66)');
  pDark(x,y,r, 0.58);
  pSpec(x,y,r, 0.18);
  ctx.restore();
}

/* ================================================================
   VEGA NODE — sci-fi crystalline energy orb
   ================================================================ */
function drawVegaNode(x,y,r,now){
  ctx.save();
  pBase(x,y,r, '#e0d0ff','#9870e0','#6840b8','#402080','#200848');

  ctx.save();
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* energy lattice */
  ctx.globalCompositeOperation = 'screen';
  for(var i=0; i<10; i++){
    var va = (i/10)*Math.PI*2 + now*0.000016;
    var vr = r * (0.10 + 0.64*Math.abs(Math.sin(i*0.9 + now*0.000011)));
    ctx.beginPath();
    ctx.moveTo(x + Math.cos(va)*r*0.07, y + Math.sin(va)*r*0.07);
    ctx.lineTo(x + Math.cos(va)*vr,     y + Math.sin(va)*vr);
    ctx.strokeStyle = 'rgba(200,168,255,0.20)';
    ctx.lineWidth   = 0.7;
    ctx.stroke();
  }
  /* core pulse */
  var pulse = 0.22 + 0.16*Math.sin(now*0.0036);
  var cp    = ctx.createRadialGradient(x,y,0, x,y,r*0.45);
  cp.addColorStop(0, 'rgba(228,212,255,' + pulse + ')');
  cp.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = cp; ctx.fillRect(0,0,W,H);

  ctx.restore();

  /* outer energy corona */
  ctx.globalCompositeOperation = 'screen';
  var ec = ctx.createRadialGradient(x,y,r*0.48, x,y,r*2.15);
  ec.addColorStop(0, 'rgba(155,95,255,' + (0.30+0.12*Math.sin(now*0.0024)).toFixed(3) + ')');
  ec.addColorStop(0.38,'rgba(120,70,220,0.10)');
  ec.addColorStop(1, 'rgba(0,0,0,0)');
  ctx.fillStyle = ec; ctx.fillRect(0,0,W,H);

  pAtm(x,y,r, 'rgba(155,95,255,0.26)', 0.26);
  pLimb(x,y,r, 'rgba(198,168,255,0.70)');
  pDark(x,y,r, 0.55);
  pSpec(x,y,r, 0.22);
  ctx.restore();
}

/* ================================================================
   PLANET TABLE — Solar System + VEGA route node
   yF: fraction of screen height · rf: fraction of min(W,H) radius
   ================================================================ */
var PT = [
  {id:'mercury', label:'GENERAL',  route:'general',
   yF:0.185, rf:0.036, draw:drawMercury,
   orx:0.455, ory:0.027},
  {id:'venus',   label:'RISK',     route:'risk',
   yF:0.295, rf:0.052, draw:drawVenus,
   orx:0.460, ory:0.026},
  {id:'earth',   label:'SURVIVAL', route:'survival',
   yF:0.405, rf:0.058, draw:drawEarth,
   orx:0.463, ory:0.025, moon:true},
  {id:'mars',    label:'COLLAPSE', route:'collapse',
   yF:0.515, rf:0.044, draw:drawMars,
   orx:0.460, ory:0.025},
  {id:'jupiter', label:'CIVIL',    route:'civil',
   yF:0.648, rf:0.082, draw:drawJupiter,
   orx:0.462, ory:0.026},
  {id:'saturn',  label:'SATURN',   route:'general',
   yF:0.775, rf:0.058, draw:drawSaturn,
   orx:0.464, ory:0.026},
  {id:'vega',    label:'VEGA',     route:'vega',
   yF:0.930, rf:0.035, draw:drawVegaNode,
   orx:0.452, ory:0.024}
];

function getR(p){ return Math.min(W,H) * p.rf; }

/* ── LABEL with glow ── */
function drawLabel(p, now){
  var px = W*0.50, py = H*p.yF, pr = getR(p);
  var isAct = p.route === activeRoute;
  var fs    = Math.max(8, Math.min(13, pr*0.50));
  ctx.save();
  ctx.font          = '500 ' + fs + 'px "DM Mono",monospace';
  ctx.textAlign     = 'center';
  ctx.textBaseline  = 'top';
  if(isAct){
    ctx.shadowColor = 'rgba(200,168,75,0.88)';
    ctx.shadowBlur  = 10;
    ctx.fillStyle   = 'rgba(248,208,102,0.97)';
  } else {
    ctx.fillStyle   = 'rgba(128,166,218,0.42)';
  }
  ctx.fillText(p.label, px, py + pr + 8);
  ctx.restore();
}

/* ── CLICK / TOUCH ── */
cv.addEventListener('click', function(e){
  var rc = cv.getBoundingClientRect();
  var cx = e.clientX - rc.left;
  var cy = e.clientY - rc.top;
  PT.forEach(function(p){
    var px = W*0.5, py = H*p.yF, pr = getR(p)*1.65;
    var dx = cx-px, dy = cy-py;
    if(dx*dx + dy*dy < pr*pr) window.KD_setRoute && window.KD_setRoute(p.route);
  });
}, {passive:true});

cv.addEventListener('touchend', function(e){
  if(e.changedTouches.length === 1){
    var tc = e.changedTouches[0];
    cv.dispatchEvent(new MouseEvent('click', {clientX:tc.clientX, clientY:tc.clientY}));
  }
}, {passive:true});

/* ================================================================
   MAIN RENDER — called every frame at native refresh rate
   ================================================================ */
function render(dt, now){
  drawBg(now);
  drawDust(now);
  drawStars(now);
  drawBelt(dt, now);

  /* orbit rings */
  PT.forEach(function(p){
    drawOrbit(H*p.yF, W*p.orx, H*p.ory, p.route===activeRoute, now);
  });

  drawSun(now);

  /* active glow under planet */
  PT.forEach(function(p){
    if(p.route === activeRoute) pActive(W*0.5, H*p.yF, getR(p), now);
  });

  /* planets + labels */
  PT.forEach(function(p){
    var px = W*0.5, py = H*p.yF, pr = getR(p);
    p.draw(px, py, pr, now);
    if(p.moon) drawMoon(px + pr*1.58, py + pr*0.32, pr*0.31, now);
    drawLabel(p, now);
  });
}

/* ================================================================
   PUBLIC API — compatible with galaxy_scene_api.js
   ================================================================ */
window.KD_setState = function(s){
  if(!s) return;
  /* future: blackhole mode when waterline < 20 */
};

window.KD_setRoute = function(r){
  if(!ROUTE_HUE[r]) return;
  activeRoute = r;
  _tgtHue     = ROUTE_HUE[r] || 208;
  document.querySelectorAll('.rpill,.ctx-tag,.route-chip').forEach(function(el){
    el.classList.toggle('active', el.dataset.r === r);
  });
};

window.KD_pulse       = function(){};
window.LYLA_thinking  = function(){};
window.LYLA_answered  = function(){};
window.setRoute       = window.KD_setRoute; /* legacy compat */

/* ================================================================
   INIT — dual resize for mobile high-DPI viewport settle
   ================================================================ */
doResize();
requestAnimationFrame(function(now){
  doResize(); /* second pass — mobile viewport settles after first paint */
  _last = now;
  _raf  = requestAnimationFrame(loop);
});

})();
