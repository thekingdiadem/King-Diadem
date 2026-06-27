/* ================================================================
   KING DIADEM — Galaxy Scene v45 PHOTOREALISTIC
   Sun tucked higher · Each planet multi-layer shading
   Earth: realistic like wallpaper · Perspective tilt
   Mobile adaptive · delta-time · GPU hints
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
   STARFIELD
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
   BACKGROUND — deep space navy, not pure black
   ================================================================ */
function drawBg(now){
  ctx.clearRect(0,0,W,H);
  var bg=ctx.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,  '#0d1728');
  bg.addColorStop(0.20,'#0a1220');
  bg.addColorStop(0.50,'#080f1c');
  bg.addColorStop(0.78,'#060c18');
  bg.addColorStop(1,  '#050a14');
  ctx.fillStyle=bg; ctx.fillRect(0,0,W,H);

  _curHue+=(_tgtHue-_curHue)*0.004*(_dt/16);
  ctx.save(); ctx.globalCompositeOperation='screen';

  var nb0=ctx.createRadialGradient(W*0.50,H*0.50,0,W*0.50,H*0.50,W*0.65);
  nb0.addColorStop(0,'rgba(28,75,155,0.16)');nb0.addColorStop(0.5,'rgba(18,52,115,0.07)');nb0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb0; ctx.fillRect(0,0,W,H);

  var nb1=ctx.createRadialGradient(W*0.05,H*0.30,0,W*0.05,H*0.30,W*0.52);
  nb1.addColorStop(0,'rgba(75,50,175,0.18)');nb1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb1; ctx.fillRect(0,0,W,H);

  var nb2=ctx.createRadialGradient(W*0.92,H*0.58,0,W*0.92,H*0.58,W*0.45);
  nb2.addColorStop(0,'rgba(155,65,95,0.14)');nb2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb2; ctx.fillRect(0,0,W,H);

  /* warm orange nebula bottom-left like wallpaper */
  var nb4=ctx.createRadialGradient(W*0.08,H*0.88,0,W*0.08,H*0.88,W*0.55);
  nb4.addColorStop(0,'rgba(180,90,30,0.12)');nb4.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb4; ctx.fillRect(0,0,W,H);

  var mw=ctx.createLinearGradient(0,H*0.40,W,H*0.60);
  mw.addColorStop(0,'rgba(0,0,0,0)');
  mw.addColorStop(0.28,'rgba(58,95,195,0.055)');
  mw.addColorStop(0.50,'rgba(78,115,215,0.090)');
  mw.addColorStop(0.72,'rgba(58,95,195,0.055)');
  mw.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=mw; ctx.fillRect(0,H*0.28,W,H*0.44);
  ctx.restore();
}

/* ================================================================
   SUN — corona only visible at top, body hidden off-screen
   ================================================================ */
function sunCX(){ return W*0.50; }
function sunCY(){ return H*(-0.10); }

function drawSun(now){
  var cx=sunCX(), cy=sunCY();
  var Rs=Math.min(W,H)*(isMobile?0.16:0.13);

  ctx.save();
  ctx.globalCompositeOperation='screen';

  var c1=ctx.createRadialGradient(cx,cy,Rs*0.3,cx,cy,Rs*6.5);
  c1.addColorStop(0,'rgba(255,100,12,0.048)');
  c1.addColorStop(0.35,'rgba(255,80,6,0.020)');
  c1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c1; ctx.fillRect(0,0,W,H);

  var c2=ctx.createRadialGradient(cx,cy,Rs*0.5,cx,cy,Rs*3.2);
  c2.addColorStop(0,'rgba(255,115,16,0.13)');
  c2.addColorStop(0.5,'rgba(255,90,8,0.052)');
  c2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c2; ctx.fillRect(0,0,W,H);

  var c3=ctx.createRadialGradient(cx,cy,Rs*0.6,cx,cy,Rs*1.9);
  c3.addColorStop(0,'rgba(255,135,24,0.24)');
  c3.addColorStop(0.6,'rgba(255,88,10,0.10)');
  c3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c3; ctx.fillRect(0,0,W,H);

  ctx.save();
  for(var ri=0;ri<12;ri++){
    var ra=(ri/12)*Math.PI*2+now*0.000013;
    var rl=Rs*(1.32+0.26*Math.sin(now*0.000011+ri*0.8));
    ctx.globalAlpha=0.020+0.009*Math.abs(Math.sin(now*0.00015+ri));
    var rx1=cx+Math.cos(ra)*Rs*0.5, ry1=cy+Math.sin(ra)*Rs*0.5;
    var rx2=cx+Math.cos(ra)*rl,     ry2=cy+Math.sin(ra)*rl;
    var rg=ctx.createLinearGradient(rx1,ry1,rx2,ry2);
    rg.addColorStop(0,'rgba(255,152,32,1)');
    rg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle=rg; ctx.lineWidth=Rs*0.052; ctx.lineCap='round';
    ctx.beginPath();ctx.moveTo(rx1,ry1);ctx.lineTo(rx2,ry2);ctx.stroke();
  }
  ctx.globalAlpha=1; ctx.restore();

  ctx.globalCompositeOperation='source-over';
  var ph=ctx.createRadialGradient(cx-Rs*0.22,cy-Rs*0.16,0,cx+Rs*0.08,cy+Rs*0.10,Rs);
  ph.addColorStop(0,'#fff9e0');ph.addColorStop(0.08,'#ffe050');ph.addColorStop(0.25,'#ff9c10');
  ph.addColorStop(0.50,'#ff5800');ph.addColorStop(0.75,'#cc1600');ph.addColorStop(1,'#6a0400');
  ctx.fillStyle=ph;
  ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();

  ctx.globalCompositeOperation='screen';
  var hi=ctx.createRadialGradient(cx-Rs*0.16,cy-Rs*0.12,0,cx,cy,Rs);
  hi.addColorStop(0,'rgba(255,255,220,0.62)');
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
    ctx.fillStyle='rgba(130,170,230,0.45)';
  }
  ctx.fillText(p.lbl,pos.x,pos.y+r+6);
  ctx.restore();
}

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
   PLANET HELPERS — Photorealistic light model
   Light source: top-left (matches Sun above)
   ================================================================ */
function pSphere(x,y,r,stops){
  var g=ctx.createRadialGradient(x-r*0.32,y-r*0.26,r*0.01,x+r*0.12,y+r*0.12,r*1.04);
  for(var i=0;i<stops.length;i++) g.addColorStop(stops[i][0],stops[i][1]);
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
}

function pTerminator(x,y,r,strength){
  strength=strength||0.72;
  ctx.save(); ctx.globalCompositeOperation='multiply';
  var g=ctx.createRadialGradient(x+r*0.28,y+r*0.22,r*0.05,x+r*0.32,y+r*0.26,r*1.08);
  g.addColorStop(0,'rgba(0,0,0,0)');
  g.addColorStop(0.42,'rgba(0,0,0,'+(strength*0.35).toFixed(3)+')');
  g.addColorStop(0.68,'rgba(0,0,0,'+(strength*0.70).toFixed(3)+')');
  g.addColorStop(0.84,'rgba(0,0,0,'+(strength*0.88).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,'+strength+')');
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r*1.04,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

function pRimLight(x,y,r,col){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.28,y-r*0.22,r*0.82,x,y,r*1.02);
  g.addColorStop(0,col);
  g.addColorStop(0.35,'rgba(255,255,255,0.04)');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r*1.02,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

function pSpecular(x,y,r,a,size){
  a=a||0.22; size=size||0.45;
  ctx.save(); ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.20,y-r*0.16,0,x-r*0.06,y-r*0.04,r*size);
  g.addColorStop(0,'rgba(255,255,255,'+a+')');
  g.addColorStop(0.30,'rgba(255,255,255,'+(a*0.28).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

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
   MERCURY
   ================================================================ */
function drawMercury(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#e8d8c0'],[0.15,'#c8a878'],[0.35,'#a07848'],
    [0.58,'#6a4c28'],[0.80,'#3e2810'],[1,'#1e1006']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  [[0.28,0.12,0.18,0.52],[-0.22,0.28,0.14,0.48],[0.04,-0.26,0.16,0.50],
   [-0.10,0.06,0.08,0.44],[0.36,-0.16,0.11,0.46],[-0.32,-0.20,0.12,0.50],
   [0.18,0.38,0.09,0.40],[-0.40,0.10,0.10,0.46]].forEach(function(c){
    var cg=ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0,x+c[0]*r,y+c[1]*r,c[2]*r);
    cg.addColorStop(0,'rgba(18,8,2,'+c[3]+')');
    cg.addColorStop(0.5,'rgba(30,16,6,'+(c[3]*0.5).toFixed(3)+')');
    cg.addColorStop(0.85,'rgba(120,90,50,'+(c[3]*0.15).toFixed(3)+')');
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply'; ctx.fillStyle=cg; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pTerminator(x,y,r,0.75); pRimLight(x,y,r,'rgba(240,200,140,0.55)');
  pSpecular(x,y,r,0.12,0.40);
  ctx.restore();
}

/* ================================================================
   VENUS
   ================================================================ */
function drawVenus(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#fff0b0'],[0.12,'#f0c840'],[0.30,'#d09018'],
    [0.55,'#a05c08'],[0.80,'#6c3200'],[1,'#3c1200']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='overlay';
  for(var i=0;i<8;i++){
    var by=y-r*0.90+i*r*0.24+Math.sin(now*0.0000095+i*1.1)*r*0.025;
    var ba=0.08+0.12*Math.abs(Math.sin(i*0.72+now*0.0000080));
    var lg=ctx.createLinearGradient(x-r,by,x+r,by+r*0.06);
    lg.addColorStop(0,'rgba(255,248,180,0)');lg.addColorStop(0.3,'rgba(255,240,160,'+ba+')');
    lg.addColorStop(0.7,'rgba(255,240,160,'+ba+')');lg.addColorStop(1,'rgba(255,248,180,0)');
    ctx.fillStyle=lg; ctx.fillRect(x-r,by,r*2,r*0.18);
  }
  ctx.restore();
  pAtmosphere(x,y,r,'rgba(255,210,80,0.18)','rgba(255,180,40,0.06)',1.28);
  pTerminator(x,y,r,0.66); pRimLight(x,y,r,'rgba(255,240,160,0.65)');
  pSpecular(x,y,r,0.16,0.42);
  ctx.restore();
}

/* ================================================================
   EARTH — wallpaper accurate
   - Deep navy ocean with VIVID TEAL coastal shallows
   - Australia deep red/orange
   - Thick volumetric 3D clouds
   - Strong white specular top-left
   - Thick blue atmosphere rim
   ================================================================ */
function drawEarth(x,y,r,now){
  ctx.save();

  /* ── OCEAN: deep navy + vivid teal shallow coastal like wallpaper ── */
  var ocean=ctx.createRadialGradient(x-r*0.18,y-r*0.14,r*0.05, x+r*0.16,y+r*0.18,r*1.05);
  ocean.addColorStop(0,   '#e8f8ff');  /* specular center very bright */
  ocean.addColorStop(0.05,'#90e8ff');  /* vivid teal highlight */
  ocean.addColorStop(0.14,'#20c0e0');  /* teal mid */
  ocean.addColorStop(0.28,'#0888c8');  /* blue transition */
  ocean.addColorStop(0.48,'#044898');
  ocean.addColorStop(0.68,'#022060');
  ocean.addColorStop(0.85,'#010c30');
  ocean.addColorStop(1,   '#000818');
  ctx.fillStyle=ocean;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* ── TEAL COASTAL SHALLOWS — key feature of wallpaper ── */
  ctx.globalCompositeOperation='screen';
  /* Around Australia coast */
  var tc1=ctx.createRadialGradient(x+r*0.42,y+r*0.32,0, x+r*0.42,y+r*0.32,r*0.28);
  tc1.addColorStop(0,'rgba(0,220,210,0.45)');
  tc1.addColorStop(0.4,'rgba(0,185,175,0.22)');
  tc1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=tc1; ctx.fillRect(0,0,W,H);
  /* Indian ocean teal */
  var tc2=ctx.createRadialGradient(x+r*0.25,y+r*0.15,0, x+r*0.25,y+r*0.15,r*0.22);
  tc2.addColorStop(0,'rgba(0,200,195,0.35)');
  tc2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=tc2; ctx.fillRect(0,0,W,H);
  /* SE Asia coast */
  var tc3=ctx.createRadialGradient(x+r*0.50,y+r*0.05,0, x+r*0.50,y+r*0.05,r*0.18);
  tc3.addColorStop(0,'rgba(0,215,200,0.40)');
  tc3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=tc3; ctx.fillRect(0,0,W,H);

  /* ── LAND CONTINENTS ── */
  ctx.globalCompositeOperation='source-over';
  function land(ox,oy,rx,R,G,B,a){
    var g=ctx.createRadialGradient(x+ox*r,y+oy*r,0, x+ox*r,y+oy*r,rx*r);
    g.addColorStop(0,'rgba('+R+','+G+','+B+','+a+')');
    g.addColorStop(0.38,'rgba('+R+','+G+','+B+','+(a*0.65).toFixed(2)+')');
    g.addColorStop(0.68,'rgba('+R+','+G+','+B+','+(a*0.25).toFixed(2)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  }

  /* Australia — DEEP RED like wallpaper, very prominent */
  land( 0.46, 0.26, 0.24, 188, 65, 15, 0.98);  /* main red mass */
  land( 0.55, 0.18, 0.11, 170, 52, 12, 0.94);  /* north */
  land( 0.60, 0.34, 0.09,  72,128, 42, 0.86);  /* green east coast */
  land( 0.44, 0.38, 0.10, 165, 58, 14, 0.88);  /* south */

  /* Africa — warm ochre/brown */
  land( 0.10,-0.06, 0.24, 200,155, 70, 0.92);
  land( 0.14, 0.16, 0.17, 152,122, 52, 0.88);
  land( 0.16, 0.02, 0.11,  48,112, 38, 0.86);  /* Congo green */
  land( 0.06,-0.12, 0.12, 218,175, 85, 0.88);  /* Sahara */
  land( 0.20, 0.30, 0.10, 135,115, 55, 0.82);  /* S Africa */

  /* Middle East — tan */
  land( 0.24,-0.10, 0.14, 215,178, 95, 0.90);

  /* Europe */
  land( 0.06,-0.26, 0.12,  72,145, 52, 0.84);
  land( 0.12,-0.34, 0.09,  65,135, 48, 0.80);

  /* Asia */
  land( 0.34,-0.32, 0.30,  82,148, 58, 0.80);
  land( 0.48,-0.14, 0.15,  98,158, 60, 0.82);
  land( 0.36, 0.02, 0.12, 138,168, 68, 0.84);  /* India */
  land( 0.52, 0.02, 0.11,  48,118, 42, 0.82);  /* SE Asia */
  land( 0.32,-0.22, 0.20, 165,172, 82, 0.76);  /* Central Asia steppe */

  /* Americas */
  land(-0.32,-0.30, 0.22,  72,132, 50, 0.86);
  land(-0.22, 0.16, 0.15,  36,102, 36, 0.92);  /* Amazon */
  land(-0.30, 0.20, 0.07, 125,105, 58, 0.80);  /* Andes */
  land(-0.10,-0.54, 0.09, 212,224,232, 0.86);  /* Greenland */

  /* Ice caps */
  ctx.globalCompositeOperation='screen';
  var ant=ctx.createRadialGradient(x,y+r*0.80,0, x,y+r*0.80,r*0.30);
  ant.addColorStop(0,'rgba(252,255,255,0.98)');
  ant.addColorStop(0.45,'rgba(238,248,255,0.78)');
  ant.addColorStop(0.75,'rgba(220,240,255,0.38)');
  ant.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ant; ctx.fillRect(0,0,W,H);

  var np=ctx.createRadialGradient(x,y-r*0.76,0, x,y-r*0.76,r*0.24);
  np.addColorStop(0,'rgba(248,254,255,0.94)');
  np.addColorStop(0.5,'rgba(230,246,255,0.65)');
  np.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np; ctx.fillRect(0,0,W,H);

  /* ── THICK VOLUMETRIC CLOUDS — key 3D look from wallpaper ── */
  /* Large swirling mass upper-left — the dominant cloud system */
  var cSpin=now*0.000042;
  for(var ci=0;ci<8;ci++){
    var ca=cSpin+ci*(Math.PI*2/8);
    var crad=r*(0.08+ci*0.062);
    var cx2=x-r*0.18+Math.cos(ca)*crad*0.60;
    var cy2=y-r*0.08+Math.sin(ca)*crad*0.32;
    var csize=r*(0.20+ci*0.038);
    var calpha=Math.max(0.05, 0.55-ci*0.060);
    var cg=ctx.createRadialGradient(cx2,cy2,0, cx2,cy2,csize);
    cg.addColorStop(0,'rgba(255,255,255,'+calpha+')');
    cg.addColorStop(0.30,'rgba(252,254,255,'+(calpha*0.65).toFixed(3)+')');
    cg.addColorStop(0.60,'rgba(245,250,255,'+(calpha*0.28).toFixed(3)+')');
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cg; ctx.fillRect(0,0,W,H);
  }
  /* Additional cloud patches */
  [
    [x+r*0.24,y+r*0.10,r*0.30,0.48],[x-r*0.05,y+r*0.28,r*0.25,0.40],
    [x-r*0.40,y-r*0.06,r*0.22,0.42],[x+r*0.42,y-r*0.14,r*0.18,0.38],
    [x-r*0.14,y-r*0.38,r*0.20,0.36],[x+r*0.08,y+r*0.50,r*0.22,0.34],
    [x+r*0.32,y+r*0.42,r*0.16,0.30],[x-r*0.32,y+r*0.42,r*0.18,0.32],
    [x+r*0.55,y+r*0.20,r*0.15,0.28],[x-r*0.50,y+r*0.20,r*0.15,0.30],
  ].forEach(function(c){
    var drift=Math.sin(now*0.0000060+c[0]*0.001)*r*0.012;
    var g=ctx.createRadialGradient(c[0]+drift,c[1],0, c[0]+drift,c[1],c[2]);
    g.addColorStop(0,'rgba(255,255,255,'+c[3]+')');
    g.addColorStop(0.25,'rgba(255,255,255,'+(c[3]*0.75).toFixed(3)+')');
    g.addColorStop(0.50,'rgba(250,252,255,'+(c[3]*0.42).toFixed(3)+')');
    g.addColorStop(0.75,'rgba(245,250,255,'+(c[3]*0.15).toFixed(3)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  });

  /* ── NIGHT SIDE TERMINATOR ── */
  ctx.globalCompositeOperation='multiply';
  var term=ctx.createRadialGradient(x+r*0.30,y+r*0.24,r*0.06, x+r*0.32,y+r*0.26,r*1.16);
  term.addColorStop(0,'rgba(0,0,0,0)');
  term.addColorStop(0.45,'rgba(0,0,0,0.10)');
  term.addColorStop(0.65,'rgba(0,0,0,0.45)');
  term.addColorStop(0.82,'rgba(0,0,0,0.72)');
  term.addColorStop(1,'rgba(0,2,18,0.90)');
  ctx.fillStyle=term; ctx.fillRect(0,0,W,H);

  ctx.restore(); /* end clip */

  /* ── ATMOSPHERE RIM — thick vivid blue like wallpaper ── */
  ctx.save(); ctx.globalCompositeOperation='screen';

  /* Inner rim — bright cyan/blue */
  var atm1=ctx.createRadialGradient(x,y,r*0.82,x,y,r*1.10);
  atm1.addColorStop(0,'rgba(60,190,255,0.72)');
  atm1.addColorStop(0.30,'rgba(40,158,245,0.42)');
  atm1.addColorStop(0.60,'rgba(25,120,225,0.18)');
  atm1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm1; ctx.fillRect(0,0,W,H);

  /* Outer glow */
  var atm2=ctx.createRadialGradient(x,y,r*0.90,x,y,r*1.38);
  atm2.addColorStop(0,'rgba(100,220,255,0.58)');
  atm2.addColorStop(0.28,'rgba(65,185,252,0.28)');
  atm2.addColorStop(0.55,'rgba(40,140,230,0.10)');
  atm2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm2; ctx.fillRect(0,0,W,H);

  /* Limb brightening — top-left sun side */
  var limb=ctx.createRadialGradient(x-r*0.24,y-r*0.20,r*0.84, x-r*0.08,y-r*0.06,r*1.22);
  limb.addColorStop(0,'rgba(175,240,255,0.55)');
  limb.addColorStop(0.40,'rgba(115,205,255,0.22)');
  limb.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=limb; ctx.fillRect(0,0,W,H);

  ctx.restore();

  /* ── SPECULAR HIGHLIGHT — very bright white top-left like wallpaper ── */
  ctx.save(); ctx.globalCompositeOperation='screen';

  /* Main specular — large bright core */
  var spec1=ctx.createRadialGradient(x-r*0.22,y-r*0.18,0, x-r*0.10,y-r*0.08,r*0.42);
  spec1.addColorStop(0,'rgba(255,255,255,0.95)');
  spec1.addColorStop(0.12,'rgba(245,252,255,0.72)');
  spec1.addColorStop(0.28,'rgba(230,248,255,0.38)');
  spec1.addColorStop(0.50,'rgba(210,240,255,0.14)');
  spec1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=spec1;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();

  /* Secondary specular — smaller glint */
  var spec2=ctx.createRadialGradient(x-r*0.14,y-r*0.28,0, x-r*0.10,y-r*0.22,r*0.12);
  spec2.addColorStop(0,'rgba(255,255,255,0.80)');
  spec2.addColorStop(0.5,'rgba(240,252,255,0.25)');
  spec2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=spec2;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();

  ctx.restore();

  /* Edge darkening */
  pTerminator(x,y,r,0.48);
  ctx.restore();
}

/* ================================================================
   MOON
   ================================================================ */
function drawMoon(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#ddd4c8'],[0.18,'#b09080'],[0.40,'#806050'],
    [0.65,'#503828'],[0.85,'#302018'],[1,'#180c06']
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
  pTerminator(x,y,r,0.72); pRimLight(x,y,r,'rgba(210,200,185,0.50)');
  pSpecular(x,y,r,0.08,0.38);
  ctx.restore();
}

/* ================================================================
   MARS
   ================================================================ */
function drawMars(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#f0b890'],[0.18,'#d07048'],[0.40,'#b85030'],
    [0.62,'#8c3820'],[0.82,'#601808'],[1,'#380c02']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='multiply';
  var vm=ctx.createLinearGradient(x-r*0.55,y+r*0.06,x+r*0.20,y+r*0.14);
  vm.addColorStop(0,'rgba(80,14,4,0)');vm.addColorStop(0.15,'rgba(42,6,2,0.70)');
  vm.addColorStop(0.85,'rgba(38,5,1,0.72)');vm.addColorStop(1,'rgba(80,14,4,0)');
  ctx.fillStyle=vm; ctx.fillRect(x-r,y+r*0.04,r*2,r*0.10);
  ctx.globalCompositeOperation='screen';
  var np3=ctx.createRadialGradient(x,y-r*0.72,0,x,y-r*0.72,r*0.28);
  np3.addColorStop(0,'rgba(250,242,230,0.94)');np3.addColorStop(0.6,'rgba(235,228,215,0.55)');np3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np3; ctx.fillRect(0,0,W,H);
  ctx.restore();
  pAtmosphere(x,y,r,'rgba(205,118,58,0.12)','rgba(185,90,38,0.04)',1.22);
  pTerminator(x,y,r,0.68); pRimLight(x,y,r,'rgba(235,160,110,0.58)');
  pSpecular(x,y,r,0.08,0.38);
  ctx.restore();
}

/* ================================================================
   JUPITER
   ================================================================ */
function drawJupiter(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#f5e5c5'],[0.15,'#ddc598'],[0.35,'#ba9865'],
    [0.58,'#8c6830'],[0.80,'#604020'],[1,'#301808']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  [{yo:-0.72,h:0.14,col:'rgba(150,100,45,0.55)'},{yo:-0.56,h:0.12,col:'rgba(195,155,85,0.42)'},
   {yo:-0.42,h:0.16,col:'rgba(138,82,30,0.62)'},{yo:-0.24,h:0.13,col:'rgba(190,152,82,0.46)'},
   {yo:-0.09,h:0.18,col:'rgba(132,78,28,0.64)'},{yo:0.11,h:0.13,col:'rgba(178,125,55,0.50)'},
   {yo:0.26,h:0.16,col:'rgba(142,92,40,0.56)'},{yo:0.44,h:0.12,col:'rgba(172,122,52,0.46)'},
   {yo:0.58,h:0.16,col:'rgba(128,75,26,0.60)'}].forEach(function(b,idx){
    var drift=Math.sin(now*0.0000038+idx*0.55)*0.012;
    var lg=ctx.createLinearGradient(x-r,y+(b.yo+drift)*r,x+r,y+(b.yo+drift+b.h)*r);
    var tc=b.col.replace(/[\d.]+\)$/,'0)');
    lg.addColorStop(0,tc);lg.addColorStop(0.20,b.col);lg.addColorStop(0.80,b.col);lg.addColorStop(1,tc);
    ctx.globalCompositeOperation='overlay'; ctx.fillStyle=lg; ctx.fillRect(x-r,y+(b.yo+drift)*r,r*2,b.h*r);
  });
  var gx=x+r*0.22+Math.sin(now*0.0000048)*r*0.04, gy=y+r*0.10;
  ctx.globalCompositeOperation='source-over';
  var grs=ctx.createRadialGradient(gx,gy,0,gx,gy,r*0.14);
  grs.addColorStop(0,'rgba(185,50,18,0.92)');grs.addColorStop(0.4,'rgba(165,35,12,0.72)');
  grs.addColorStop(0.75,'rgba(140,25,8,0.40)');grs.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=grs; ctx.fillRect(0,0,W,H);
  ctx.restore();
  pTerminator(x,y,r,0.60); pRimLight(x,y,r,'rgba(240,215,165,0.50)');
  pSpecular(x,y,r,0.10,0.40);
  ctx.restore();
}

/* ================================================================
   VEGA
   ================================================================ */
function drawVega(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#e0d0ff'],[0.12,'#9868e0'],[0.32,'#6838b8'],
    [0.58,'#401880'],[0.80,'#200848'],[1,'#0c0220']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='screen';
  for(var vi=0;vi<12;vi++){
    var va=(vi/12)*Math.PI*2+now*0.0000140;
    var vr=r*(0.08+0.65*Math.abs(Math.sin(vi*0.85+now*0.0000105)));
    ctx.beginPath();
    ctx.moveTo(x+Math.cos(va)*r*0.05,y+Math.sin(va)*r*0.05);
    ctx.lineTo(x+Math.cos(va)*vr,y+Math.sin(va)*vr);
    ctx.strokeStyle='rgba(195,165,255,0.20)'; ctx.lineWidth=0.8; ctx.stroke();
  }
  var pulse=0.20+0.16*Math.sin(now*0.0032);
  var cp=ctx.createRadialGradient(x,y,0,x,y,r*0.42);
  cp.addColorStop(0,'rgba(225,210,255,'+pulse+')');
  cp.addColorStop(0.5,'rgba(180,150,255,'+(pulse*0.5).toFixed(3)+')');
  cp.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=cp; ctx.fillRect(0,0,W,H);
  ctx.restore();
  ctx.globalCompositeOperation='screen';
  var ec=ctx.createRadialGradient(x,y,r*0.46,x,y,r*2.20);
  ec.addColorStop(0,'rgba(148,88,255,'+(0.30+0.12*Math.sin(now*0.0020)).toFixed(3)+')');
  ec.addColorStop(0.40,'rgba(115,65,218,0.10)');ec.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ec; ctx.fillRect(0,0,W,H);
  pAtmosphere(x,y,r,'rgba(148,88,255,0.24)','rgba(108,58,200,0.08)',1.35);
  pTerminator(x,y,r,0.50); pRimLight(x,y,r,'rgba(195,165,255,0.72)');
  pSpecular(x,y,r,0.22,0.48);
  ctx.restore();
}

/* ================================================================
   RENDER
   ================================================================ */
function render(dt,now){
  drawBg(now); drawDust(now); drawStars(now);
  for(var i=0;i<PLANETS.length;i++) drawOrbitRing(PLANETS[i],now);
  drawSun(now);

  var posed=PLANETS.map(function(p,idx){ return {p:p,pos:planetPos(p,now),idx:idx}; });
  posed.sort(function(a,b){ return a.pos.y-b.pos.y; });
  _cache=[];
  for(var i=0;i<PLANETS.length;i++) _cache.push({x:0,y:0});

  for(var i=0;i<posed.length;i++){
    var item=posed[i], p=item.p, pos=item.pos, r=getR(p);
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
  activeRoute=r; _tgtHue=ROUTE_HUE[r]||208;
  document.querySelectorAll('.rpill,.ctx-tag,.route-chip').forEach(function(el){
    el.classList.toggle('active',el.dataset.r===r);
  });
};
window.KD_pulse=function(){};
window.LYLA_thinking=function(){};
window.LYLA_answered=function(){};
window.setRoute=window.KD_setRoute;

doResize();
if(cv.style){ cv.style.willChange='transform'; cv.style.transform='translateZ(0)'; }
requestAnimationFrame(function(now){ doResize(); _last=now; _raf=requestAnimationFrame(loop); });

})();
