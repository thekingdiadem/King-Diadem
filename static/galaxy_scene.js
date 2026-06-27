/* ================================================================
   KING DIADEM — Galaxy Scene v45 PHOTOREALISTIC
   - Sun tucked higher, never covers planets
   - Each planet: multi-layer radial shading, rim light,
     atmosphere halo, specular highlight, terminator shadow
   - Earth: realistic ocean/land/cloud/atm like wallpaper
   - Perspective tilt solar system, depth sort
   - Mobile adaptive, delta-time physics, GPU hints
   ================================================================ */
(function(){
'use strict';

var cv = document.getElementById('galaxy');
if (!cv) return;
var ctx = cv.getContext('2d', {alpha:true, desynchronized:true});
var W=0, H=0, _raf=null, _last=0, _dt=0;
var activeRoute = 'general';
var isMobile = false;

var ROUTE_HUE = {general:208,risk:22,collapse:338,survival:142,civil:268,vega:286};
var _tgtHue=208, _curHue=208;

function loop(now){
  _raf = requestAnimationFrame(loop);
  _dt  = Math.min(now-_last, 50);
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
window.addEventListener('resize',function(){ clearTimeout(_rT); _rT=setTimeout(doResize,80); },{passive:true});
document.addEventListener('visibilitychange',function(){
  if(document.hidden){ if(_raf){cancelAnimationFrame(_raf);_raf=null;} }
  else { if(!_raf){_last=performance.now();_raf=requestAnimationFrame(loop);} }
},{passive:true});

/* ================================================================
   STARFIELD — 3 depth layers
   ================================================================ */
var STARS=[];
function buildStars(){
  STARS=[];
  var total = isMobile ? 300 : 550;
  for(var i=0;i<total;i++){
    var layer = Math.random();
    var sz = layer<0.50?0:layer<0.78?1:2;
    STARS.push({
      x: Math.random()*W, y: Math.random()*H,
      r: [0.25+Math.random()*0.35, 0.45+Math.random()*0.65, 0.80+Math.random()*1.30][sz],
      a: [0.22+Math.random()*0.45, 0.35+Math.random()*0.58, 0.52+Math.random()*0.80][sz],
      tw: Math.random()<0.60,
      ph: Math.random()*Math.PI*2,
      sp: 0.15+Math.random()*0.65,
      ct: Math.random()<0.22?'blue':Math.random()<0.10?'warm':'white',
      cross: sz===2&&Math.random()<0.55
    });
  }
}

function drawStars(now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var a=s.tw?s.a*(0.38+0.62*Math.sin(now*s.sp*0.00048+s.ph)):s.a;
    var col = s.ct==='blue' ?'rgba(180,215,255,'+a.toFixed(3)+')':
              s.ct==='warm' ?'rgba(255,235,195,'+a.toFixed(3)+')':
                             'rgba(225,238,255,'+a.toFixed(3)+')';
    if(s.cross&&a>s.a*0.55){
      ctx.strokeStyle=col; ctx.lineWidth=0.35;
      var cl=s.r*3.8;
      ctx.beginPath();ctx.moveTo(s.x-cl,s.y);ctx.lineTo(s.x+cl,s.y);ctx.stroke();
      ctx.beginPath();ctx.moveTo(s.x,s.y-cl);ctx.lineTo(s.x,s.y+cl);ctx.stroke();
    }
    ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fillStyle=col; ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   NEBULA DUST
   ================================================================ */
var DUST=[];
function buildDust(){
  DUST=[];
  var n=isMobile?55:100;
  var hues=[260,278,295,185,200,340];
  for(var i=0;i<n;i++){
    DUST.push({
      x:Math.random()*W, y:Math.random()*H,
      r:22+Math.random()*65,
      a:0.016+Math.random()*0.036,
      ph:Math.random()*Math.PI*2,
      sp:0.04+Math.random()*0.14,
      hue:hues[Math.floor(Math.random()*hues.length)],
      sat:18+Math.random()*22, lum:50+Math.random()*22
    });
  }
}

function drawDust(now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<DUST.length;i++){
    var d=DUST[i];
    var a=d.a*(0.42+0.58*Math.sin(now*d.sp*0.00019+d.ph));
    var g=ctx.createRadialGradient(d.x,d.y,0,d.x,d.y,d.r);
    g.addColorStop(0,'hsla('+d.hue+','+d.sat+'%,'+d.lum+'%,'+a.toFixed(4)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(d.x-d.r,d.y-d.r,d.r*2,d.r*2);
  }
  ctx.restore();
}

/* ================================================================
   BACKGROUND
   ================================================================ */
function drawBg(now){
  ctx.clearRect(0,0,W,H);
  var bg=ctx.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,  '#1a2d4a');
  bg.addColorStop(0.20,'#152440');
  bg.addColorStop(0.45,'#111e36');
  bg.addColorStop(0.72,'#0e192e');
  bg.addColorStop(1,  '#0b1526');
  ctx.fillStyle=bg; ctx.fillRect(0,0,W,H);

  _curHue+=(_tgtHue-_curHue)*0.004*(_dt/16);
  ctx.save(); ctx.globalCompositeOperation='screen';

  var rt=ctx.createRadialGradient(W*0.5,H*0.4,0,W*0.5,H*0.5,W*0.70);
  rt.addColorStop(0,'hsla('+_curHue+',30%,12%,0.020)');
  rt.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=rt; ctx.fillRect(0,0,W,H);

  var nb0=ctx.createRadialGradient(W*0.50,H*0.50,0,W*0.50,H*0.50,W*0.65);
  nb0.addColorStop(0,'rgba(30,80,160,0.18)');nb0.addColorStop(0.5,'rgba(20,55,120,0.08)');nb0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb0; ctx.fillRect(0,0,W,H);

  var nb1=ctx.createRadialGradient(W*0.05,H*0.30,0,W*0.05,H*0.30,W*0.52);
  nb1.addColorStop(0,'rgba(80,55,180,0.20)');nb1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb1; ctx.fillRect(0,0,W,H);

  var nb2=ctx.createRadialGradient(W*0.92,H*0.58,0,W*0.92,H*0.58,W*0.45);
  nb2.addColorStop(0,'rgba(160,70,100,0.16)');nb2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb2; ctx.fillRect(0,0,W,H);

  var nb3=ctx.createRadialGradient(W*0.30,H*0.90,0,W*0.30,H*0.90,W*0.50);
  nb3.addColorStop(0,'rgba(25,100,160,0.16)');nb3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb3; ctx.fillRect(0,0,W,H);

  var mw=ctx.createLinearGradient(0,H*0.40,W,H*0.60);
  mw.addColorStop(0,'rgba(0,0,0,0)');
  mw.addColorStop(0.28,'rgba(60,100,200,0.06)');
  mw.addColorStop(0.50,'rgba(80,120,220,0.10)');
  mw.addColorStop(0.72,'rgba(60,100,200,0.06)');
  mw.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=mw; ctx.fillRect(0,H*0.28,W,H*0.44);
  ctx.restore();
}

/* ================================================================
   SUN — bleeds off top, corona rays, never overlaps planets
   Sun center sits at -12% H so only corona visible at top
   ================================================================ */
function sunCX(){ return W*0.50; }
function sunCY(){ return H*(-0.12); }   /* pushed up — only corona bleeds in */

function drawSun(now){
  var cx=sunCX(), cy=sunCY();
  var Rs=Math.min(W,H)*(isMobile?0.17:0.14);

  ctx.save();
  ctx.globalCompositeOperation='screen';

  /* far corona — very wide, soft orange glow filling top portion */
  var c1=ctx.createRadialGradient(cx,cy,Rs*0.3,cx,cy,Rs*6.0);
  c1.addColorStop(0,'rgba(255,100,12,0.045)');
  c1.addColorStop(0.4,'rgba(255,80,6,0.018)');
  c1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c1; ctx.fillRect(0,0,W,H);

  /* mid corona */
  var c2=ctx.createRadialGradient(cx,cy,Rs*0.5,cx,cy,Rs*3.0);
  c2.addColorStop(0,'rgba(255,110,14,0.12)');
  c2.addColorStop(0.5,'rgba(255,90,8,0.048)');
  c2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c2; ctx.fillRect(0,0,W,H);

  /* inner glow */
  var c3=ctx.createRadialGradient(cx,cy,Rs*0.6,cx,cy,Rs*1.8);
  c3.addColorStop(0,'rgba(255,130,22,0.22)');
  c3.addColorStop(0.6,'rgba(255,85,8,0.09)');
  c3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c3; ctx.fillRect(0,0,W,H);

  /* 12 rotating solar rays */
  ctx.save();
  for(var ri=0;ri<12;ri++){
    var ra=(ri/12)*Math.PI*2+now*0.000014;
    var rl=Rs*(1.30+0.25*Math.sin(now*0.000012+ri*0.8));
    ctx.globalAlpha=0.022+0.010*Math.abs(Math.sin(now*0.00016+ri));
    var rx1=cx+Math.cos(ra)*Rs*0.5, ry1=cy+Math.sin(ra)*Rs*0.5;
    var rx2=cx+Math.cos(ra)*rl,     ry2=cy+Math.sin(ra)*rl;
    var rg=ctx.createLinearGradient(rx1,ry1,rx2,ry2);
    rg.addColorStop(0,'rgba(255,150,30,1)');
    rg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle=rg; ctx.lineWidth=Rs*0.055; ctx.lineCap='round';
    ctx.beginPath();ctx.moveTo(rx1,ry1);ctx.lineTo(rx2,ry2);ctx.stroke();
  }
  ctx.globalAlpha=1; ctx.restore();

  /* photosphere body */
  ctx.globalCompositeOperation='source-over';
  var ph=ctx.createRadialGradient(cx-Rs*0.22,cy-Rs*0.16,0,cx+Rs*0.08,cy+Rs*0.10,Rs);
  ph.addColorStop(0,   '#fff9e0');
  ph.addColorStop(0.08,'#ffe050');
  ph.addColorStop(0.25,'#ff9c10');
  ph.addColorStop(0.50,'#ff5800');
  ph.addColorStop(0.75,'#cc1600');
  ph.addColorStop(1,   '#6a0400');
  ctx.fillStyle=ph;
  ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();

  /* specular top-left */
  ctx.globalCompositeOperation='screen';
  var hi=ctx.createRadialGradient(cx-Rs*0.16,cy-Rs*0.12,0,cx,cy,Rs);
  hi.addColorStop(0,'rgba(255,255,220,0.60)');
  hi.addColorStop(0.30,'rgba(255,230,80,0.10)');
  hi.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=hi;
  ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();

  ctx.restore();
}

/* ================================================================
   PLANET SYSTEM
   ================================================================ */
var TILT = 0.28;

/* yOff pushed down so mercury starts well below sun corona */
var PLANETS=[
  {id:'mercury',lbl:'GENERAL', route:'general', orb:0.10,per:0.241,yOff:0.24,rD:0.025,rM:0.032,draw:drawMercury},
  {id:'venus',  lbl:'RISK',    route:'risk',    orb:0.16,per:0.615,yOff:0.34,rD:0.033,rM:0.042,draw:drawVenus  },
  {id:'earth',  lbl:'SURVIVAL',route:'survival',orb:0.22,per:1.000,yOff:0.44,rD:0.040,rM:0.050,draw:drawEarth,moon:true},
  {id:'mars',   lbl:'COLLAPSE',route:'collapse',orb:0.29,per:1.881,yOff:0.54,rD:0.028,rM:0.036,draw:drawMars  },
  {id:'jupiter',lbl:'CIVIL',   route:'civil',   orb:0.38,per:11.86,yOff:0.64,rD:0.052,rM:0.064,draw:drawJupiter},
  {id:'vega',   lbl:'VEGA',    route:'vega',    orb:0.44,per:29.46,yOff:0.75,rD:0.036,rM:0.046,draw:drawVega  },
];

function planetPos(p,now){
  var BASE=0.000040;
  var angle=(now*BASE/p.per)%(Math.PI*2);
  var R=Math.min(W,H)*p.orb;
  var cx=sunCX()+Math.cos(angle)*R;
  var oy=sunCY()+H*p.yOff;
  var cy=oy+Math.sin(angle)*R*TILT;
  return {x:cx,y:cy,angle:angle,orbitR:R,orbitY:oy};
}

function getR(p){ return Math.min(W,H)*(isMobile?p.rM:p.rD); }

/* orbit ring */
function drawOrbitRing(p,now){
  var R=Math.min(W,H)*p.orb;
  var oy=sunCY()+H*p.yOff;
  var isAct=p.route===activeRoute;
  ctx.save(); ctx.globalCompositeOperation='screen';
  ctx.beginPath();
  ctx.ellipse(sunCX(),oy,R,R*TILT,0,0,Math.PI*2);
  var a=isAct?0.40:0.09;
  ctx.strokeStyle=isAct?'rgba(200,168,75,'+a+')':'rgba(100,150,220,'+a+')';
  ctx.lineWidth=isAct?1.2:0.45;
  ctx.stroke();
  if(isAct){
    var pos=planetPos(p,now);
    var sg=ctx.createRadialGradient(pos.x,pos.y,0,pos.x,pos.y,8);
    sg.addColorStop(0,'rgba(255,235,120,0.90)');sg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sg; ctx.fillRect(0,0,W,H);
  }
  ctx.restore();
}

function drawLabel(p,pos){
  var isAct=p.route===activeRoute;
  var r=getR(p);
  var fs=Math.max(7,Math.min(11,r*0.55));
  ctx.save();
  ctx.font='500 '+fs+'px "DM Mono",monospace';
  ctx.textAlign='center'; ctx.textBaseline='top';
  if(isAct){
    ctx.shadowColor='rgba(200,168,75,0.85)'; ctx.shadowBlur=8;
    ctx.fillStyle='rgba(248,210,95,0.97)';
  } else {
    ctx.fillStyle='rgba(110,155,220,0.38)';
  }
  ctx.fillText(p.lbl,pos.x,pos.y+r+6);
  ctx.restore();
}

/* click */
var _cache=[];
cv.addEventListener('click',function(e){
  var rc=cv.getBoundingClientRect();
  var mx=e.clientX-rc.left,my=e.clientY-rc.top;
  for(var i=0;i<_cache.length;i++){
    var pp=_cache[i];
    var dx=mx-pp.x,dy=my-pp.y,r=getR(PLANETS[i])*1.8;
    if(dx*dx+dy*dy<r*r) window.KD_setRoute&&window.KD_setRoute(PLANETS[i].route);
  }
},{passive:true});
cv.addEventListener('touchend',function(e){
  if(e.changedTouches.length===1){
    var t=e.changedTouches[0];
    cv.dispatchEvent(new MouseEvent('click',{clientX:t.clientX,clientY:t.clientY}));
  }
},{passive:true});

/* ================================================================
   PHOTOREALISTIC PLANET HELPERS
   Light source: top-left (consistent with Sun position above)
   ================================================================ */

/* Base sphere with realistic light/dark gradient */
function pSphere(x,y,r,stops){
  /* stops = array of [offset, color] */
  var g=ctx.createRadialGradient(
    x-r*0.32, y-r*0.26, r*0.01,   /* light source offset */
    x+r*0.12, y+r*0.12, r*1.04
  );
  for(var i=0;i<stops.length;i++) g.addColorStop(stops[i][0],stops[i][1]);
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
}

/* Terminator — dark crescent on the right/bottom */
function pTerminator(x,y,r,strength){
  strength=strength||0.72;
  ctx.save(); ctx.globalCompositeOperation='multiply';
  /* Two overlapping darks to create soft terminator */
  var g=ctx.createRadialGradient(x+r*0.28,y+r*0.22,r*0.05, x+r*0.32,y+r*0.26,r*1.08);
  g.addColorStop(0,'rgba(0,0,0,0)');
  g.addColorStop(0.42,'rgba(0,0,0,'+(strength*0.35).toFixed(3)+')');
  g.addColorStop(0.68,'rgba(0,0,0,'+(strength*0.70).toFixed(3)+')');
  g.addColorStop(0.84,'rgba(0,0,0,'+(strength*0.88).toFixed(3)+')');
  g.addColorStop(1,   'rgba(0,0,0,'+strength+')');
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r*1.04,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

/* Rim light — thin bright edge from sun side */
function pRimLight(x,y,r,col){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.28,y-r*0.22,r*0.82, x,y,r*1.02);
  g.addColorStop(0,col);
  g.addColorStop(0.35,'rgba(255,255,255,0.04)');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r*1.02,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

/* Specular highlight — bright spot top-left */
function pSpecular(x,y,r,a,size){
  a=a||0.22; size=size||0.45;
  ctx.save(); ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.20,y-r*0.16,0, x-r*0.06,y-r*0.04,r*size);
  g.addColorStop(0,'rgba(255,255,255,'+a+')');
  g.addColorStop(0.30,'rgba(255,255,255,'+(a*0.28).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

/* Atmosphere halo */
function pAtmosphere(x,y,r,col0,col1,size){
  size=size||1.32;
  ctx.save(); ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x,y,r*0.88,x,y,r*size);
  g.addColorStop(0,col0);
  g.addColorStop(0.45,col1);
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  ctx.restore();
}

/* Active planet glow ring */
function pActive(x,y,r,now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var pulse=0.65+0.35*Math.sin(now*0.0026);
  var g=ctx.createRadialGradient(x,y,r*0.5,x,y,r*2.6);
  g.addColorStop(0,'rgba(200,168,75,'+(0.30*pulse).toFixed(3)+')');
  g.addColorStop(0.5,'rgba(200,168,75,'+(0.10*pulse).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  ctx.globalAlpha=0.22*pulse;
  ctx.strokeStyle='rgba(255,48,48,0.72)';ctx.lineWidth=1.2;
  ctx.beginPath();ctx.arc(x+1.5,y,r*1.10,0,Math.PI*2);ctx.stroke();
  ctx.strokeStyle='rgba(48,48,255,0.72)';
  ctx.beginPath();ctx.arc(x-1.5,y,r*1.10,0,Math.PI*2);ctx.stroke();
  ctx.globalAlpha=1; ctx.restore();
}

/* ================================================================
   MERCURY — rocky, cratered, grey-brown
   ================================================================ */
function drawMercury(x,y,r,now){
  ctx.save();
  /* Base sphere: warm grey with light on top-left */
  pSphere(x,y,r,[
    [0,   '#e8d8c0'],
    [0.15,'#c8a878'],
    [0.35,'#a07848'],
    [0.58,'#6a4c28'],
    [0.80,'#3e2810'],
    [1,   '#1e1006']
  ]);

  /* Craters — clipped to sphere */
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  var craters=[
    [0.28,0.12,0.18,0.52],[-0.22,0.28,0.14,0.48],
    [0.04,-0.26,0.16,0.50],[-0.10,0.06,0.08,0.44],
    [0.36,-0.16,0.11,0.46],[-0.32,-0.20,0.12,0.50],
    [0.18,0.38,0.09,0.40],[-0.40,0.10,0.10,0.46],
    [0.42,0.30,0.08,0.38]
  ];
  craters.forEach(function(c){
    var cg=ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0,x+c[0]*r,y+c[1]*r,c[2]*r);
    cg.addColorStop(0,'rgba(18,8,2,'+c[3]+')');
    cg.addColorStop(0.5,'rgba(30,16,6,'+(c[3]*0.5).toFixed(3)+')');
    cg.addColorStop(0.85,'rgba(120,90,50,'+(c[3]*0.15).toFixed(3)+')'); /* bright rim */
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply'; ctx.fillStyle=cg; ctx.fillRect(0,0,W,H);
    /* crater rim highlight */
    ctx.globalCompositeOperation='screen';
    var rim=ctx.createRadialGradient(x+c[0]*r-c[2]*r*0.3,y+c[1]*r-c[2]*r*0.3,c[2]*r*0.7,x+c[0]*r,y+c[1]*r,c[2]*r*1.0);
    rim.addColorStop(0,'rgba(0,0,0,0)');
    rim.addColorStop(0.85,'rgba(200,170,110,0.18)');
    rim.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=rim; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();

  pTerminator(x,y,r,0.75);
  pRimLight(x,y,r,'rgba(240,200,140,0.55)');
  pSpecular(x,y,r,0.12,0.40);
  ctx.restore();
}

/* ================================================================
   VENUS — thick yellow cloud bands, hot
   ================================================================ */
function drawVenus(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,   '#fff0b0'],
    [0.12,'#f0c840'],
    [0.30,'#d09018'],
    [0.55,'#a05c08'],
    [0.80,'#6c3200'],
    [1,   '#3c1200']
  ]);

  /* Cloud bands — horizontal streaks */
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='overlay';
  for(var i=0;i<8;i++){
    var by=y-r*0.90+i*r*0.24+Math.sin(now*0.0000095+i*1.1)*r*0.025;
    var ba=0.08+0.12*Math.abs(Math.sin(i*0.72+now*0.0000080));
    var lg=ctx.createLinearGradient(x-r,by,x+r,by+r*0.06);
    lg.addColorStop(0,'rgba(255,248,180,0)');
    lg.addColorStop(0.3,'rgba(255,240,160,'+ba+')');
    lg.addColorStop(0.7,'rgba(255,240,160,'+ba+')');
    lg.addColorStop(1,'rgba(255,248,180,0)');
    ctx.fillStyle=lg; ctx.fillRect(x-r,by,r*2,r*0.18);
  }
  ctx.restore();

  pAtmosphere(x,y,r,'rgba(255,210,80,0.18)','rgba(255,180,40,0.06)',1.28);
  pTerminator(x,y,r,0.66);
  pRimLight(x,y,r,'rgba(255,240,160,0.65)');
  pSpecular(x,y,r,0.16,0.42);
  ctx.restore();
}

/* ================================================================
   EARTH — photorealistic like wallpaper
   Ocean: deep teal-blue | Land: continents | Clouds: swirl | Atm: blue rim
   ================================================================ */
function drawEarth(x,y,r,now){
  ctx.save();

  /* ── OCEAN ── */
  var ocean=ctx.createRadialGradient(x-r*0.20,y-r*0.16,0,x+r*0.14,y+r*0.16,r*1.04);
  ocean.addColorStop(0,   '#d0f2ff');
  ocean.addColorStop(0.06,'#70d8f0');
  ocean.addColorStop(0.18,'#28a8d0');
  ocean.addColorStop(0.36,'#0868a8');
  ocean.addColorStop(0.58,'#043878');
  ocean.addColorStop(0.80,'#021840');
  ocean.addColorStop(1,   '#010820');
  ctx.fillStyle=ocean;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* ── LAND CONTINENTS ── */
  function land(ox,oy,rx,R,G,B,a,blur){
    var rr=rx*r*(blur||1.0);
    var g=ctx.createRadialGradient(x+ox*r,y+oy*r,0,x+ox*r,y+oy*r,rr);
    g.addColorStop(0,'rgba('+R+','+G+','+B+','+a+')');
    g.addColorStop(0.40,'rgba('+R+','+G+','+B+','+(a*0.60).toFixed(2)+')');
    g.addColorStop(0.70,'rgba('+R+','+G+','+B+','+(a*0.22).toFixed(2)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='source-over';
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  }

  /* Australia - RED/ORANGE — dominant feature like wallpaper */
  land( 0.46, 0.28,0.22,195, 78,24,0.96);
  land( 0.54, 0.20,0.10,175, 62,18,0.90);
  land( 0.58, 0.36,0.08, 80,138,48,0.82); /* east coast green */

  /* Africa */
  land( 0.10,-0.04,0.22,205,160,75,0.92);
  land( 0.14, 0.18,0.16,158,128,58,0.88);
  land( 0.16, 0.04,0.10, 50,115,40,0.85); /* Congo rainforest */
  land( 0.06,-0.10,0.10,222,178,88,0.86); /* Sahara */

  /* Middle East */
  land( 0.24,-0.08,0.13,218,182,98,0.88);

  /* Europe */
  land( 0.06,-0.24,0.11, 75,148,55,0.84);
  land( 0.12,-0.32,0.08, 68,138,50,0.80);

  /* Asia */
  land( 0.34,-0.30,0.28, 85,152,60,0.80);
  land( 0.46,-0.12,0.14,102,162,62,0.82);
  land( 0.36, 0.04,0.11,142,172,70,0.84); /* India */
  land( 0.50, 0.04,0.10, 50,120,45,0.82); /* SE Asia */

  /* Americas */
  land(-0.32,-0.28,0.22, 75,135,52,0.86);
  land(-0.22, 0.18,0.14, 38,105,38,0.90); /* Amazon */
  land(-0.30, 0.22,0.06,128,108,60,0.80); /* Andes */
  land(-0.10,-0.52,0.08,215,226,235,0.85); /* Greenland */

  /* Antarctica */
  var ant=ctx.createRadialGradient(x,y+r*0.82,0,x,y+r*0.82,r*0.32);
  ant.addColorStop(0,'rgba(250,254,255,0.97)');
  ant.addColorStop(0.5,'rgba(235,246,255,0.72)');
  ant.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ant; ctx.fillRect(0,0,W,H);

  /* North pole */
  var np2=ctx.createRadialGradient(x,y-r*0.78,0,x,y-r*0.78,r*0.26);
  np2.addColorStop(0,'rgba(245,252,255,0.92)');
  np2.addColorStop(0.5,'rgba(228,245,255,0.62)');
  np2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np2; ctx.fillRect(0,0,W,H);

  /* ── CLOUDS ── */
  ctx.globalCompositeOperation='screen';

  /* Cyclone spiral — top area */
  var cSpiral=now*0.000048;
  for(var ci=0;ci<6;ci++){
    var ca=cSpiral+ci*(Math.PI*2/6);
    var cr2=r*(0.10+ci*0.055);
    var cx2=x-r*0.22+Math.cos(ca)*cr2*0.55;
    var cy2=y-r*0.10+Math.sin(ca)*cr2*0.28;
    var cg2=ctx.createRadialGradient(cx2,cy2,0,cx2,cy2,r*(0.16+ci*0.042));
    cg2.addColorStop(0,'rgba(255,255,255,'+(0.45-ci*0.055)+')');
    cg2.addColorStop(0.4,'rgba(250,252,255,'+(0.24-ci*0.028)+')');
    cg2.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cg2; ctx.fillRect(0,0,W,H);
  }

  /* Cloud patches */
  var cb=[
    [x+r*0.26,y+r*0.12,r*0.26,0.38],[x-r*0.06,y+r*0.30,r*0.22,0.32],
    [x-r*0.42,y-r*0.08,r*0.20,0.34],[x+r*0.44,y-r*0.16,r*0.16,0.30],
    [x-r*0.16,y-r*0.40,r*0.18,0.28],[x+r*0.06,y+r*0.52,r*0.20,0.26],
    [x+r*0.34,y+r*0.44,r*0.14,0.22],[x-r*0.34,y+r*0.44,r*0.16,0.24],
  ];
  cb.forEach(function(c){
    var drift=Math.sin(now*0.0000065+c[0]*0.001)*r*0.015;
    var g=ctx.createRadialGradient(c[0]+drift,c[1],0,c[0]+drift,c[1],c[2]);
    g.addColorStop(0,'rgba(255,255,255,'+c[3]+')');
    g.addColorStop(0.38,'rgba(246,250,255,'+(c[3]*0.55).toFixed(3)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  });

  /* Terminator night-side */
  ctx.globalCompositeOperation='multiply';
  var term=ctx.createRadialGradient(x+r*0.32,y+r*0.26,r*0.08,x+r*0.32,y+r*0.26,r*1.14);
  term.addColorStop(0,'rgba(0,0,0,0)');
  term.addColorStop(0.50,'rgba(0,0,0,0.12)');
  term.addColorStop(0.72,'rgba(0,0,0,0.50)');
  term.addColorStop(0.88,'rgba(0,0,0,0.75)');
  term.addColorStop(1,'rgba(0,5,20,0.88)');
  ctx.fillStyle=term; ctx.fillRect(0,0,W,H);

  ctx.restore(); /* clip */

  /* ── ATMOSPHERE RIM — thick blue like wallpaper ── */
  ctx.save(); ctx.globalCompositeOperation='screen';
  var atm1=ctx.createRadialGradient(x,y,r*0.84,x,y,r*1.12);
  atm1.addColorStop(0,'rgba(80,185,255,0.58)');
  atm1.addColorStop(0.38,'rgba(50,148,238,0.30)');
  atm1.addColorStop(0.68,'rgba(30,112,215,0.12)');
  atm1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm1; ctx.fillRect(0,0,W,H);

  var atm2=ctx.createRadialGradient(x,y,r*0.92,x,y,r*1.32);
  atm2.addColorStop(0,'rgba(120,215,255,0.52)');
  atm2.addColorStop(0.32,'rgba(75,178,250,0.22)');
  atm2.addColorStop(0.62,'rgba(40,132,222,0.09)');
  atm2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm2; ctx.fillRect(0,0,W,H);

  /* Limb brightening top-left */
  var limb=ctx.createRadialGradient(x-r*0.26,y-r*0.22,r*0.86,x-r*0.10,y-r*0.08,r*1.20);
  limb.addColorStop(0,'rgba(165,235,255,0.45)');
  limb.addColorStop(0.5,'rgba(100,198,255,0.18)');
  limb.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=limb; ctx.fillRect(0,0,W,H);
  ctx.restore();

  /* Specular on ocean */
  ctx.save(); ctx.globalCompositeOperation='screen';
  var spec=ctx.createRadialGradient(x-r*0.18,y-r*0.14,0,x-r*0.06,y-r*0.04,r*0.50);
  spec.addColorStop(0,'rgba(255,255,255,0.75)');
  spec.addColorStop(0.16,'rgba(240,252,255,0.40)');
  spec.addColorStop(0.42,'rgba(200,238,255,0.12)');
  spec.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=spec;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.restore();

  /* Edge darkening */
  pTerminator(x,y,r,0.55);
  ctx.restore();
}

/* ================================================================
   MOON — grey, cratered, small
   ================================================================ */
function drawMoon(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,   '#ddd4c8'],[0.18,'#b09080'],
    [0.40,'#806050'],[0.65,'#503828'],[0.85,'#302018'],[1,'#180c06']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  [[-0.12,-0.08,0.34,0.50],[0.16,0.12,0.24,0.44],[-0.26,0.20,0.18,0.42]].forEach(function(m){
    var mg=ctx.createRadialGradient(x+m[0]*r,y+m[1]*r,0,x+m[0]*r,y+m[1]*r,m[2]*r);
    mg.addColorStop(0,'rgba(40,28,18,'+m[3]+')');
    mg.addColorStop(0.6,'rgba(55,40,25,'+(m[3]*0.45).toFixed(3)+')');
    mg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply'; ctx.fillStyle=mg; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pTerminator(x,y,r,0.72);
  pRimLight(x,y,r,'rgba(210,200,185,0.50)');
  pSpecular(x,y,r,0.08,0.38);
  ctx.restore();
}

/* ================================================================
   MARS — rusty red, Valles Marineris, polar caps
   ================================================================ */
function drawMars(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,   '#f0b890'],[0.18,'#d07048'],
    [0.40,'#b85030'],[0.62,'#8c3820'],
    [0.82,'#601808'],[1,   '#380c02']
  ]);

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* Valles Marineris — long scar */
  ctx.globalCompositeOperation='multiply';
  var vm=ctx.createLinearGradient(x-r*0.55,y+r*0.06,x+r*0.20,y+r*0.14);
  vm.addColorStop(0,'rgba(80,14,4,0)');
  vm.addColorStop(0.15,'rgba(42,6,2,0.70)');
  vm.addColorStop(0.85,'rgba(38,5,1,0.72)');
  vm.addColorStop(1,'rgba(80,14,4,0)');
  ctx.fillStyle=vm; ctx.fillRect(x-r,y+r*0.04,r*2,r*0.10);

  /* Dust storm wisps */
  ctx.globalCompositeOperation='screen';
  for(var di=0;di<3;di++){
    var da=now*0.0000035+di*2.1;
    var dx2=x+Math.cos(da)*r*0.28+di*r*0.10;
    var dy2=y+Math.sin(da)*r*0.12+r*0.08;
    var dg=ctx.createRadialGradient(dx2,dy2,0,dx2,dy2,r*0.18);
    dg.addColorStop(0,'rgba(215,140,80,0.12)');
    dg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=dg; ctx.fillRect(0,0,W,H);
  }

  /* North polar cap */
  ctx.globalCompositeOperation='screen';
  var np3=ctx.createRadialGradient(x,y-r*0.72,0,x,y-r*0.72,r*0.28);
  np3.addColorStop(0,'rgba(250,242,230,0.94)');
  np3.addColorStop(0.6,'rgba(235,228,215,0.55)');
  np3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np3; ctx.fillRect(0,0,W,H);

  ctx.restore();

  /* Thin CO2 atmosphere */
  pAtmosphere(x,y,r,'rgba(205,118,58,0.12)','rgba(185,90,38,0.04)',1.22);
  pTerminator(x,y,r,0.68);
  pRimLight(x,y,r,'rgba(235,160,110,0.58)');
  pSpecular(x,y,r,0.08,0.38);
  ctx.restore();
}

/* ================================================================
   JUPITER — gas giant, horizontal bands, Great Red Spot
   ================================================================ */
function drawJupiter(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,   '#f5e5c5'],[0.15,'#ddc598'],
    [0.35,'#ba9865'],[0.58,'#8c6830'],
    [0.80,'#604020'],[1,   '#301808']
  ]);

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* Horizontal bands — 9 bands */
  var bands=[
    {yo:-0.78,h:0.16,col:'rgba(155,105,48,0.56)'},
    {yo:-0.60,h:0.12,col:'rgba(198,158,88,0.42)'},
    {yo:-0.46,h:0.18,col:'rgba(140,85,32,0.64)'},
    {yo:-0.26,h:0.14,col:'rgba(192,155,85,0.48)'},
    {yo:-0.10,h:0.20,col:'rgba(135,82,30,0.66)'},
    {yo: 0.12,h:0.14,col:'rgba(180,128,58,0.52)'},
    {yo: 0.28,h:0.16,col:'rgba(145,95,42,0.58)'},
    {yo: 0.46,h:0.12,col:'rgba(175,125,55,0.48)'},
    {yo: 0.60,h:0.18,col:'rgba(130,78,28,0.62)'},
  ];
  bands.forEach(function(b,idx){
    var drift=Math.sin(now*0.0000038+idx*0.55)*0.012;
    var lg=ctx.createLinearGradient(x-r,y+(b.yo+drift)*r,x+r,y+(b.yo+drift+b.h)*r);
    var tc=b.col.replace(/[\d.]+\)$/,'0)');
    lg.addColorStop(0,tc);
    lg.addColorStop(0.20,b.col);
    lg.addColorStop(0.80,b.col);
    lg.addColorStop(1,tc);
    ctx.globalCompositeOperation='overlay';
    ctx.fillStyle=lg; ctx.fillRect(x-r,y+(b.yo+drift)*r,r*2,b.h*r);
  });

  /* Great Red Spot */
  var gx=x+r*0.22+Math.sin(now*0.0000048)*r*0.04;
  var gy=y+r*0.10;
  ctx.globalCompositeOperation='source-over';
  var grs=ctx.createRadialGradient(gx,gy,0,gx,gy,r*0.14);
  grs.addColorStop(0,'rgba(185,50,18,0.92)');
  grs.addColorStop(0.4,'rgba(165,35,12,0.72)');
  grs.addColorStop(0.75,'rgba(140,25,8,0.40)');
  grs.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=grs; ctx.fillRect(0,0,W,H);
  /* GRS swirl detail */
  ctx.globalCompositeOperation='overlay';
  var grs2=ctx.createRadialGradient(gx-r*0.04,gy-r*0.02,0,gx,gy,r*0.10);
  grs2.addColorStop(0,'rgba(255,120,60,0.35)');
  grs2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=grs2; ctx.fillRect(0,0,W,H);

  ctx.restore();

  pTerminator(x,y,r,0.60);
  pRimLight(x,y,r,'rgba(240,215,165,0.50)');
  pSpecular(x,y,r,0.10,0.40);
  ctx.restore();
}

/* ================================================================
   VEGA — deep purple, energy tendrils, pulsing core
   ================================================================ */
function drawVega(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,   '#e0d0ff'],[0.12,'#9868e0'],
    [0.32,'#6838b8'],[0.58,'#401880'],
    [0.80,'#200848'],[1,   '#0c0220']
  ]);

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='screen';

  /* Energy tendrils */
  for(var vi=0;vi<12;vi++){
    var va=(vi/12)*Math.PI*2+now*0.0000140;
    var vr=r*(0.08+0.65*Math.abs(Math.sin(vi*0.85+now*0.0000105)));
    ctx.beginPath();
    ctx.moveTo(x+Math.cos(va)*r*0.05,y+Math.sin(va)*r*0.05);
    ctx.lineTo(x+Math.cos(va)*vr,y+Math.sin(va)*vr);
    ctx.strokeStyle='rgba(195,165,255,0.20)';
    ctx.lineWidth=0.8; ctx.stroke();
  }

  /* Pulsing core */
  var pulse=0.20+0.16*Math.sin(now*0.0032);
  var cp=ctx.createRadialGradient(x,y,0,x,y,r*0.42);
  cp.addColorStop(0,'rgba(225,210,255,'+pulse+')');
  cp.addColorStop(0.5,'rgba(180,150,255,'+(pulse*0.5).toFixed(3)+')');
  cp.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=cp; ctx.fillRect(0,0,W,H);

  ctx.restore();

  /* Outer energy corona */
  ctx.globalCompositeOperation='screen';
  var ec=ctx.createRadialGradient(x,y,r*0.46,x,y,r*2.20);
  ec.addColorStop(0,'rgba(148,88,255,'+(0.30+0.12*Math.sin(now*0.0020)).toFixed(3)+')');
  ec.addColorStop(0.40,'rgba(115,65,218,0.10)');
  ec.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ec; ctx.fillRect(0,0,W,H);

  pAtmosphere(x,y,r,'rgba(148,88,255,0.24)','rgba(108,58,200,0.08)',1.35);
  pTerminator(x,y,r,0.50);
  pRimLight(x,y,r,'rgba(195,165,255,0.72)');
  pSpecular(x,y,r,0.22,0.48);
  ctx.restore();
}

/* ================================================================
   RENDER LOOP
   ================================================================ */
function render(dt,now){
  drawBg(now);
  drawDust(now);
  drawStars(now);

  for(var i=0;i<PLANETS.length;i++) drawOrbitRing(PLANETS[i],now);

  drawSun(now);

  var posed=PLANETS.map(function(p,idx){
    return {p:p, pos:planetPos(p,now), idx:idx};
  });
  posed.sort(function(a,b){ return a.pos.y-b.pos.y; });

  _cache=[];
  for(var i=0;i<PLANETS.length;i++) _cache.push({x:0,y:0});

  for(var i=0;i<posed.length;i++){
    var item=posed[i], p=item.p, pos=item.pos;
    var r=getR(p);
    _cache[item.idx]={x:pos.x,y:pos.y};
    if(p.route===activeRoute) pActive(pos.x,pos.y,r,now);
    p.draw(pos.x,pos.y,r,now);
    if(p.moon){
      var moonR=r*0.28;
      var moonOff=r*1.58+Math.sin(now*0.00092)*r*0.10;
      drawMoon(pos.x+moonOff,pos.y+r*0.20,moonR,now);
    }
    drawLabel(p,pos);
  }
}

/* ================================================================
   PUBLIC API
   ================================================================ */
window.KD_setState=function(){};
window.KD_setRoute=function(r){
  if(!ROUTE_HUE[r]) return;
  activeRoute=r;
  _tgtHue=ROUTE_HUE[r]||208;
  document.querySelectorAll('.rpill,.ctx-tag,.route-chip').forEach(function(el){
    el.classList.toggle('active',el.dataset.r===r);
  });
};
window.KD_pulse=function(){};
window.LYLA_thinking=function(){};
window.LYLA_answered=function(){};
window.setRoute=window.KD_setRoute;

/* ── INIT ── */
doResize();
if(cv.style){ cv.style.willChange='transform'; cv.style.transform='translateZ(0)'; }
requestAnimationFrame(function(now){
  doResize(); _last=now;
  _raf=requestAnimationFrame(loop);
});

})();
