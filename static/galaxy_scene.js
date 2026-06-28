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
   EARTH v47 — NASA Satellite View
   - Day side: ocean depth, continents, clouds, atmosphere
   - Night side: city lights constellation (USA, Europe, Asia)
   - Terminator: soft twilight band
   - Specular: ocean glint top-left
   ================================================================ */
function drawEarth(x,y,r,now){
  ctx.save();

  /* ── BASE: deep space black (night side base) ── */
  ctx.fillStyle='#000510';
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* ── OCEAN — day side only (right half) ── */
  ctx.globalCompositeOperation='source-over';
  var ocean=ctx.createRadialGradient(x-r*0.15,y-r*0.12,r*0.05, x+r*0.20,y+r*0.20,r*1.05);
  ocean.addColorStop(0,  '#c0eeff');
  ocean.addColorStop(0.06,'#52ccea');
  ocean.addColorStop(0.16,'#1a90cc');
  ocean.addColorStop(0.32,'#0660a8');
  ocean.addColorStop(0.52,'#033a80');
  ocean.addColorStop(0.72,'#011c48');
  ocean.addColorStop(0.88,'#000c28');
  ocean.addColorStop(1,  '#000510');
  ctx.fillStyle=ocean;
  ctx.fillRect(0,0,W,H);

  /* ── CONTINENTS — day side ── */
  function land(ox,oy,rx,R,G,B,a){
    var g=ctx.createRadialGradient(x+ox*r,y+oy*r,0, x+ox*r,y+oy*r,rx*r);
    g.addColorStop(0,'rgba('+R+','+G+','+B+','+a+')');
    g.addColorStop(0.38,'rgba('+R+','+G+','+B+','+(a*0.70).toFixed(2)+')');
    g.addColorStop(0.68,'rgba('+R+','+G+','+B+','+(a*0.28).toFixed(2)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  }
  /* Australia — iconic red/orange */
  land( 0.46, 0.26,0.22,188,64,14,0.98);
  land( 0.55, 0.18,0.10,170,52,12,0.94);
  land( 0.60, 0.34,0.08, 65,122,38,0.88);
  /* Africa */
  land( 0.10,-0.05,0.23,200,154,68,0.92);
  land( 0.14, 0.16,0.17,152,122,52,0.88);
  land( 0.15, 0.02,0.10, 44,108,35,0.86);
  land( 0.06,-0.13,0.12,218,175,84,0.88);
  /* Middle East */
  land( 0.24,-0.09,0.14,215,178,95,0.90);
  /* Europe */
  land( 0.06,-0.25,0.12, 68,140,48,0.84);
  land( 0.12,-0.34,0.09, 62,130,44,0.80);
  /* Asia */
  land( 0.34,-0.32,0.29, 78,142,52,0.80);
  land( 0.48,-0.14,0.15, 92,152,56,0.82);
  land( 0.36, 0.02,0.12,132,162,62,0.84);
  land( 0.52, 0.02,0.10, 44,112,38,0.82);
  land( 0.30,-0.22,0.18,162,170,82,0.76);
  /* Americas */
  land(-0.32,-0.30,0.22, 68,125,46,0.86);
  land(-0.22, 0.16,0.15, 32, 98,32,0.92);
  land(-0.30, 0.20,0.06,120,100,54,0.80);
  land(-0.10,-0.54,0.08,212,224,232,0.86);

  /* ── COASTAL TEAL SHALLOWS — subtle ── */
  ctx.globalCompositeOperation='screen';
  var tc=ctx.createRadialGradient(x+r*0.40,y+r*0.22,r*0.12, x+r*0.40,y+r*0.22,r*0.25);
  tc.addColorStop(0,'rgba(0,195,185,0.26)'); tc.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=tc; ctx.fillRect(0,0,W,H);

  /* ── ICE CAPS ── */
  var ant=ctx.createRadialGradient(x,y+r*0.80,0, x,y+r*0.80,r*0.28);
  ant.addColorStop(0,'rgba(252,255,255,0.96)'); ant.addColorStop(0.5,'rgba(232,246,255,0.70)'); ant.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ant; ctx.fillRect(0,0,W,H);
  var np=ctx.createRadialGradient(x,y-r*0.77,0, x,y-r*0.77,r*0.22);
  np.addColorStop(0,'rgba(245,252,255,0.90)'); np.addColorStop(0.5,'rgba(225,244,255,0.60)'); np.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np; ctx.fillRect(0,0,W,H);

  /* ── CLOUDS — day side, volumetric ── */
  var cSpin=now*0.000040;
  for(var ci=0;ci<7;ci++){
    var ca=cSpin+ci*(Math.PI*2/7);
    var crad=r*(0.08+ci*0.058);
    var cx2=x-r*0.16+Math.cos(ca)*crad*0.58;
    var cy2=y-r*0.08+Math.sin(ca)*crad*0.30;
    var calpha=Math.max(0.06,0.52-ci*0.058);
    var cg=ctx.createRadialGradient(cx2,cy2,0,cx2,cy2,r*(0.18+ci*0.036));
    cg.addColorStop(0,'rgba(255,255,255,'+calpha+')');
    cg.addColorStop(0.35,'rgba(252,254,255,'+(calpha*0.62).toFixed(3)+')');
    cg.addColorStop(0.65,'rgba(245,250,255,'+(calpha*0.24).toFixed(3)+')');
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cg; ctx.fillRect(0,0,W,H);
  }
  [[x+r*0.22,y+r*0.10,r*0.28,0.46],[x-r*0.06,y+r*0.26,r*0.22,0.38],
   [x-r*0.42,y-r*0.07,r*0.20,0.40],[x+r*0.40,y-r*0.15,r*0.17,0.34],
   [x-r*0.14,y-r*0.37,r*0.18,0.30],[x+r*0.06,y+r*0.48,r*0.20,0.28],
   [x+r*0.28,y+r*0.40,r*0.14,0.26]
  ].forEach(function(c){
    var drift=Math.sin(now*0.0000058+c[0]*0.001)*r*0.010;
    var cpg=ctx.createRadialGradient(c[0]+drift,c[1],0,c[0]+drift,c[1],c[2]);
    cpg.addColorStop(0,'rgba(255,255,255,'+c[3]+')');
    cpg.addColorStop(0.28,'rgba(255,255,255,'+(c[3]*0.72).toFixed(3)+')');
    cpg.addColorStop(0.55,'rgba(248,252,255,'+(c[3]*0.36).toFixed(3)+')');
    cpg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cpg; ctx.fillRect(0,0,W,H);
  });

  /* ── TERMINATOR — soft twilight band ── */
  ctx.globalCompositeOperation='multiply';
  var term=ctx.createRadialGradient(x+r*0.28,y+r*0.22,r*0.04, x+r*0.30,y+r*0.24,r*1.18);
  term.addColorStop(0,   'rgba(0,0,0,0)');
  term.addColorStop(0.38,'rgba(0,0,0,0.05)');
  term.addColorStop(0.55,'rgba(0,0,8,0.38)');
  term.addColorStop(0.70,'rgba(0,0,12,0.72)');
  term.addColorStop(0.85,'rgba(0,2,20,0.90)');
  term.addColorStop(1,   'rgba(0,3,22,0.97)');
  ctx.fillStyle=term; ctx.fillRect(0,0,W,H);

  /* ── CITY LIGHTS — night side ── */
  ctx.globalCompositeOperation='screen';
  function city(ox,oy,size,brightness,color){
    /* only draw if on night side (right+bottom = night) */
    var g=ctx.createRadialGradient(x+ox*r,y+oy*r,0, x+ox*r,y+oy*r,size*r);
    g.addColorStop(0,'rgba('+color+','+brightness+')');
    g.addColorStop(0.35,'rgba('+color+','+(brightness*0.45).toFixed(3)+')');
    g.addColorStop(0.70,'rgba('+color+','+(brightness*0.12).toFixed(3)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  }

  /* USA East Coast + Midwest — amber-white */
  city(-0.28,-0.20,0.060,0.82,'255,228,145');
  city(-0.22,-0.22,0.042,0.68,'255,215,130');
  city(-0.34,-0.18,0.034,0.58,'255,222,140');
  city(-0.18,-0.28,0.032,0.52,'255,210,128');
  city(-0.26,-0.26,0.025,0.48,'255,225,148');
  /* USA West Coast */
  city(-0.44,-0.20,0.028,0.45,'255,220,135');
  city(-0.46,-0.22,0.020,0.38,'255,218,138');
  /* USA Midwest corridor */
  city(-0.30,-0.24,0.022,0.42,'255,222,142');
  city(-0.24,-0.20,0.018,0.38,'255,218,138');
  /* Europe cluster — bright */
  city( 0.05,-0.28,0.050,0.78,'255,235,160');
  city( 0.10,-0.32,0.034,0.62,'255,228,148');
  city( 0.16,-0.26,0.030,0.56,'255,225,145');
  city( 0.02,-0.22,0.028,0.50,'255,230,150');
  city( 0.12,-0.24,0.022,0.45,'255,228,148');
  city( 0.18,-0.30,0.020,0.40,'255,225,145');
  /* Japan + Korea — bright dense */
  city( 0.56,-0.22,0.035,0.68,'255,240,170');
  city( 0.52,-0.18,0.025,0.55,'255,235,160');
  city( 0.58,-0.24,0.018,0.45,'255,238,165');
  /* China East coast */
  city( 0.48,-0.12,0.040,0.58,'255,228,148');
  city( 0.44,-0.08,0.028,0.45,'255,222,140');
  city( 0.50,-0.16,0.022,0.38,'255,225,145');
  /* India */
  city( 0.36, 0.05,0.036,0.50,'255,218,138');
  city( 0.40, 0.08,0.022,0.38,'255,215,135');
  /* Middle East */
  city( 0.22,-0.08,0.032,0.52,'255,230,155');
  city( 0.26,-0.10,0.020,0.40,'255,228,150');
  /* SE Asia */
  city( 0.54, 0.06,0.025,0.42,'255,220,145');
  /* Australia east */
  city( 0.58, 0.32,0.022,0.38,'255,215,135');

  /* Tiny city sparkle nodes — more realistic scatter */
  var sparkles=[
    [-0.26,-0.24,0.008,0.80],[-0.30,-0.20,0.007,0.70],[-0.20,-0.26,0.007,0.68],
    [-0.24,-0.18,0.007,0.65],[-0.32,-0.22,0.006,0.60],[-0.18,-0.22,0.006,0.58],
    [ 0.06,-0.30,0.008,0.75],[ 0.12,-0.28,0.007,0.65],[ 0.08,-0.24,0.007,0.62],
    [ 0.14,-0.32,0.006,0.58],[ 0.02,-0.26,0.006,0.55],[ 0.18,-0.28,0.006,0.52],
    [ 0.56,-0.20,0.007,0.65],[ 0.50,-0.16,0.006,0.55],[ 0.46,-0.10,0.007,0.50],
    [ 0.38, 0.04,0.006,0.48],[ 0.24,-0.10,0.006,0.50],[ 0.60, 0.30,0.005,0.42],
  ];
  sparkles.forEach(function(s){
    var sg=ctx.createRadialGradient(x+s[0]*r,y+s[1]*r,0, x+s[0]*r,y+s[1]*r,s[2]*r);
    sg.addColorStop(0,'rgba(255,240,180,'+s[3]+')');
    sg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sg; ctx.fillRect(0,0,W,H);
  });

  /* City light connection filaments — like the Gemini satellite image */
  ctx.globalCompositeOperation='screen';
  /* USA network */
  ctx.strokeStyle='rgba(255,220,120,0.10)'; ctx.lineWidth=0.6;
  var links=[
    [-0.28,-0.20,-0.22,-0.22],[-0.22,-0.22,-0.18,-0.28],
    [-0.28,-0.20,-0.34,-0.18],[-0.30,-0.24,-0.26,-0.26],
    [-0.24,-0.20,-0.22,-0.22],[-0.28,-0.20,-0.24,-0.20],
    /* Europe */
    [ 0.06,-0.28, 0.12,-0.28],[ 0.06,-0.28, 0.02,-0.22],
    [ 0.10,-0.32, 0.16,-0.26],[ 0.12,-0.24, 0.18,-0.30],
    [ 0.05,-0.28, 0.10,-0.32],
    /* East Asia */
    [ 0.56,-0.20, 0.50,-0.16],[ 0.56,-0.20, 0.58,-0.24],
    [ 0.48,-0.12, 0.44,-0.08],[ 0.50,-0.16, 0.48,-0.12],
    /* cross-regional faint */
    [ 0.16,-0.26, 0.22,-0.08],[ 0.36, 0.05, 0.40, 0.08],
  ];
  links.forEach(function(l){
    ctx.beginPath();
    ctx.moveTo(x+l[0]*r,y+l[1]*r);
    ctx.lineTo(x+l[2]*r,y+l[3]*r);
    ctx.stroke();
  });
  /* brighter core links */
  ctx.strokeStyle='rgba(255,228,145,0.16)'; ctx.lineWidth=0.4;
  [[-0.28,-0.20,-0.30,-0.24],[0.06,-0.28,0.12,-0.28],[0.56,-0.22,0.52,-0.18]].forEach(function(l){
    ctx.beginPath(); ctx.moveTo(x+l[0]*r,y+l[1]*r); ctx.lineTo(x+l[2]*r,y+l[3]*r); ctx.stroke();
  });

  ctx.restore(); /* end clip */

  /* ── ATMOSPHERE RIM — blue glow ── */
  ctx.save(); ctx.globalCompositeOperation='screen';
  var atm1=ctx.createRadialGradient(x,y,r*0.82,x,y,r*1.10);
  atm1.addColorStop(0,'rgba(50,175,252,0.70)');
  atm1.addColorStop(0.30,'rgba(35,142,238,0.38)');
  atm1.addColorStop(0.62,'rgba(20,108,220,0.14)');
  atm1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm1; ctx.fillRect(0,0,W,H);

  var atm2=ctx.createRadialGradient(x,y,r*0.90,x,y,r*1.38);
  atm2.addColorStop(0,'rgba(88,205,255,0.56)');
  atm2.addColorStop(0.28,'rgba(58,170,248,0.24)');
  atm2.addColorStop(0.56,'rgba(32,125,225,0.09)');
  atm2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm2; ctx.fillRect(0,0,W,H);

  /* Limb brightening — sun side top-left */
  var limb=ctx.createRadialGradient(x-r*0.22,y-r*0.18,r*0.85, x-r*0.08,y-r*0.06,r*1.22);
  limb.addColorStop(0,'rgba(155,232,255,0.52)');
  limb.addColorStop(0.40,'rgba(95,195,255,0.20)');
  limb.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=limb; ctx.fillRect(0,0,W,H);

  /* Twilight orange band at terminator edge */
  var twi=ctx.createRadialGradient(x+r*0.24,y+r*0.18,r*0.60, x+r*0.26,y+r*0.20,r*0.80);
  twi.addColorStop(0,'rgba(0,0,0,0)');
  twi.addColorStop(0.5,'rgba(255,128,30,0.06)');
  twi.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=twi; ctx.fillRect(0,0,W,H);
  ctx.restore();

  /* ── OCEAN SPECULAR — top-left glint ── */
  ctx.save(); ctx.globalCompositeOperation='screen';
  var spec=ctx.createRadialGradient(x-r*0.18,y-r*0.14,0, x-r*0.06,y-r*0.05,r*0.42);
  spec.addColorStop(0,'rgba(255,255,255,0.90)');
  spec.addColorStop(0.14,'rgba(240,252,255,0.62)');
  spec.addColorStop(0.30,'rgba(220,244,255,0.28)');
  spec.addColorStop(0.52,'rgba(200,235,255,0.08)');
  spec.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=spec;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.restore();

  pTerminator(x,y,r,0.46);
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
   SPACECRAFT v46 — Sci-fi future, clockwise orbits
   3 vessel types:
   1. KING STATION  — large ISS-style, orbits Earth
   2. PROBE x3      — small fast survey vessels, cross between planets
   3. ALIEN VESSEL  — slow, geometric, peaceful — outer system
   All carry crew indicators (soft glow = life aboard)
   ================================================================ */

var VESSELS = [
  /* KING STATION — ISS style, Earth orbit */
  {
    id: 'king_station',
    type: 'station',
    orbitPlanet: 'earth',    /* orbits around Earth position */
    orbitR: 0.068,           /* relative to planet radius */
    speed: 0.00058,          /* rad/ms — fast LEO */
    angle: 0.8,
    label: 'KD-1',
    crew: true,
    size: 1.0,
    color: '#c8e8ff',
    engineColor: 'rgba(120,200,255,0.85)',
    alienGlow: false,
  },
  /* PROBE LYLA — survey, crosses inner system */
  {
    id: 'probe_lyla',
    type: 'probe',
    orbitCenter: 'sun',      /* orbits sun directly */
    orbitRFrac: 0.18,        /* fraction of min(W,H) */
    yOffFrac: 0.30,
    speed: 0.000095,
    angle: 1.2,
    label: 'LYLA-P',
    crew: false,
    size: 0.55,
    color: '#76aeff',
    engineColor: 'rgba(74,158,255,0.90)',
    alienGlow: false,
  },
  /* PROBE VEGA — faster, outer track */
  {
    id: 'probe_vega',
    type: 'probe',
    orbitCenter: 'sun',
    orbitRFrac: 0.32,
    yOffFrac: 0.50,
    speed: 0.000062,
    angle: 3.5,
    label: 'VEGA-P',
    crew: false,
    size: 0.55,
    color: '#b48aff',
    engineColor: 'rgba(180,138,255,0.88)',
    alienGlow: false,
  },
  /* ALIEN VESSEL — slow, geometric, outer system, PEACEFUL */
  {
    id: 'alien_one',
    type: 'alien',
    orbitCenter: 'sun',
    orbitRFrac: 0.42,
    yOffFrac: 0.68,
    speed: 0.000028,
    angle: 0.3,
    label: '∞',
    crew: true,
    size: 0.80,
    color: '#38d9b8',
    engineColor: 'rgba(56,217,184,0.82)',
    alienGlow: true,
  },
];

/* Update vessel angles — clockwise = subtract */
function updateVessels(dt){
  VESSELS.forEach(function(v){
    v.angle = (v.angle - v.speed * dt + Math.PI*2) % (Math.PI*2);
  });
}

/* Get vessel screen position */
function vesselPos(v, now, planetPositions){
  if(v.type === 'station'){
    /* orbits around the Earth planet position */
    var earthPos = planetPositions['earth'];
    if(!earthPos) return null;
    var earthR = Math.min(W,H) * (isMobile ? 0.050 : 0.040);
    var orbitR  = earthR * (5.5 + 1.5*Math.sin(now*0.00012));  /* slight ellipse */
    return {
      x: earthPos.x + Math.cos(v.angle) * orbitR,
      y: earthPos.y + Math.sin(v.angle) * orbitR * 0.45,  /* perspective flatten */
    };
  } else {
    /* orbits sun */
    var R  = Math.min(W,H) * v.orbitRFrac;
    var oy = sunCY() + H * v.yOffFrac;
    return {
      x: sunCX() + Math.cos(v.angle) * R,
      y: oy       + Math.sin(v.angle) * R * TILT,
    };
  }
}

/* Draw ISS-style King Station */
function drawStation(vx, vy, sz, v, now){
  ctx.save();
  var s = sz * (isMobile ? 7 : 10);
  /* Engine glow */
  ctx.globalCompositeOperation='screen';
  var eg=ctx.createRadialGradient(vx,vy,0,vx,vy,s*3.5);
  eg.addColorStop(0,'rgba(120,200,255,0.28)');
  eg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=eg; ctx.fillRect(0,0,W,H);

  /* Rotate toward direction of travel */
  var heading = v.angle - Math.PI/2;
  ctx.translate(vx, vy);
  ctx.rotate(heading);

  /* Central module */
  ctx.globalCompositeOperation='source-over';
  ctx.fillStyle='#c8e8ff';
  ctx.fillRect(-s*0.28, -s*0.18, s*0.56, s*0.36);

  /* Solar panels — left */
  ctx.fillStyle='rgba(58,134,245,0.90)';
  ctx.fillRect(-s*1.10, -s*0.08, s*0.72, s*0.16);
  /* Solar panels — right */
  ctx.fillRect( s*0.38, -s*0.08, s*0.72, s*0.16);
  /* Panel struts */
  ctx.fillStyle='rgba(160,210,255,0.70)';
  ctx.fillRect(-s*0.38, -s*0.04, s*0.76, s*0.08);

  /* Docking port */
  ctx.fillStyle='rgba(200,230,255,0.85)';
  ctx.beginPath(); ctx.arc(0, 0, s*0.10, 0, Math.PI*2); ctx.fill();

  /* Crew glow — warm amber dot */
  if(v.crew){
    ctx.globalCompositeOperation='screen';
    var cg=ctx.createRadialGradient(0,-s*0.05,0,0,-s*0.05,s*0.22);
    cg.addColorStop(0,'rgba(255,220,100,0.55)');
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cg; ctx.fillRect(-s,-s,s*2,s*2);
  }
  ctx.restore();

  /* Label */
  ctx.save();
  ctx.globalCompositeOperation='screen';
  ctx.font='500 '+(isMobile?6:7)+'px "DM Mono",monospace';
  ctx.textAlign='center'; ctx.fillStyle='rgba(120,200,255,0.60)';
  ctx.fillText(v.label, vx, vy + s*1.6);
  ctx.restore();
}

/* Draw probe — small dart shape */
function drawProbe(vx, vy, sz, v, now){
  ctx.save();
  var s = sz * (isMobile ? 4 : 5.5);
  var heading = v.angle - Math.PI/2;

  /* Engine trail */
  ctx.globalCompositeOperation='screen';
  var trailAngle = v.angle + Math.PI;  /* behind */
  for(var ti=0;ti<5;ti++){
    var tx = vx + Math.cos(trailAngle)*s*(1.2+ti*0.8);
    var ty = vy + Math.sin(trailAngle)*s*(0.6+ti*0.4)*TILT;
    var ta = (0.45-ti*0.08);
    var tg=ctx.createRadialGradient(tx,ty,0,tx,ty,s*(0.6+ti*0.3));
    tg.addColorStop(0,v.engineColor.replace(/[\d.]+\)$/,ta.toFixed(2)+')'));
    tg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=tg; ctx.fillRect(0,0,W,H);
  }

  ctx.translate(vx, vy);
  ctx.rotate(heading);
  ctx.globalCompositeOperation='source-over';

  /* Body */
  ctx.fillStyle=v.color;
  ctx.beginPath();
  ctx.moveTo(0, -s);            /* nose */
  ctx.lineTo(s*0.30, s*0.55);  /* right */
  ctx.lineTo(0, s*0.30);       /* back center */
  ctx.lineTo(-s*0.30, s*0.55); /* left */
  ctx.closePath(); ctx.fill();

  /* Wing nubs */
  ctx.fillStyle='rgba(255,255,255,0.45)';
  ctx.fillRect(-s*0.55, s*0.10, s*0.22, s*0.22);
  ctx.fillRect( s*0.33, s*0.10, s*0.22, s*0.22);

  /* Engine glow at back */
  ctx.globalCompositeOperation='screen';
  var eg2=ctx.createRadialGradient(0,s*0.45,0,0,s*0.45,s*0.38);
  eg2.addColorStop(0,v.engineColor);
  eg2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=eg2; ctx.fillRect(-s,0,s*2,s*1.2);

  ctx.restore();

  /* Label */
  ctx.save();
  ctx.font='500 '+(isMobile?5:6)+'px "DM Mono",monospace';
  ctx.textAlign='center'; ctx.fillStyle='rgba(180,220,255,0.45)';
  ctx.fillText(v.label, vx, vy + s*1.4);
  ctx.restore();
}

/* Draw alien vessel — geometric, tetrahedron-ish, peaceful teal */
function drawAlien(vx, vy, sz, v, now){
  ctx.save();
  var s = sz * (isMobile ? 6 : 8);
  var spin = now * 0.000095;  /* slow self-rotation */

  /* Outer peaceful aura */
  ctx.globalCompositeOperation='screen';
  var pulse = 0.18 + 0.10*Math.sin(now*0.0018);
  var ag=ctx.createRadialGradient(vx,vy,s*0.5,vx,vy,s*3.8);
  ag.addColorStop(0,'rgba(56,217,184,'+pulse+')');
  ag.addColorStop(0.5,'rgba(56,200,170,'+(pulse*0.35).toFixed(3)+')');
  ag.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ag; ctx.fillRect(0,0,W,H);

  ctx.translate(vx, vy);
  ctx.rotate(spin);
  ctx.globalCompositeOperation='source-over';

  /* Outer ring */
  ctx.strokeStyle='rgba(56,217,184,0.70)';
  ctx.lineWidth=1.2;
  ctx.beginPath(); ctx.arc(0,0,s,0,Math.PI*2); ctx.stroke();

  /* Inner rotating triangle */
  ctx.rotate(spin * 2.5);
  ctx.strokeStyle='rgba(100,240,210,0.85)';
  ctx.lineWidth=0.9;
  ctx.beginPath();
  for(var ai=0;ai<3;ai++){
    var aa=(ai/3)*Math.PI*2 - Math.PI/2;
    if(ai===0) ctx.moveTo(Math.cos(aa)*s*0.62, Math.sin(aa)*s*0.62);
    else        ctx.lineTo(Math.cos(aa)*s*0.62, Math.sin(aa)*s*0.62);
  }
  ctx.closePath(); ctx.stroke();

  /* Core — pulsing orb */
  ctx.globalCompositeOperation='screen';
  var cp2=ctx.createRadialGradient(0,0,0,0,0,s*0.30);
  cp2.addColorStop(0,'rgba(180,255,240,'+(0.65+0.22*Math.sin(now*0.0022))+')');
  cp2.addColorStop(0.5,'rgba(56,217,184,0.35)');
  cp2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=cp2; ctx.fillRect(-s,-s,s*2,s*2);

  /* 6 spoke nodes */
  ctx.globalCompositeOperation='source-over';
  for(var ni=0;ni<6;ni++){
    var na=(ni/6)*Math.PI*2+spin;
    var nx=Math.cos(na)*s*0.72, ny=Math.sin(na)*s*0.72;
    ctx.fillStyle='rgba(100,240,210,0.80)';
    ctx.beginPath(); ctx.arc(nx,ny,s*0.075,0,Math.PI*2); ctx.fill();
  }

  ctx.restore();

  /* Crew/life indicator — peaceful amber */
  ctx.save();
  ctx.globalCompositeOperation='screen';
  var lg2=ctx.createRadialGradient(vx,vy-s*0.5,0,vx,vy-s*0.5,s*0.40);
  lg2.addColorStop(0,'rgba(255,220,80,0.45)');
  lg2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=lg2; ctx.fillRect(0,0,W,H);
  ctx.restore();

  /* Label */
  ctx.save();
  ctx.font='bold '+(isMobile?7:9)+'px "DM Mono",monospace';
  ctx.textAlign='center'; ctx.fillStyle='rgba(56,217,184,0.70)';
  ctx.fillText(v.label, vx, vy + s*1.5);
  ctx.restore();
}

/* Draw orbit ring for vessels orbiting sun */
function drawVesselOrbit(v){
  if(v.type === 'station') return;  /* station orbit too small, skip */
  var R  = Math.min(W,H) * v.orbitRFrac;
  var oy = sunCY() + H * v.yOffFrac;
  ctx.save(); ctx.globalCompositeOperation='screen';
  ctx.beginPath();
  ctx.ellipse(sunCX(), oy, R, R*TILT, 0, 0, Math.PI*2);
  ctx.strokeStyle = v.alienGlow
    ? 'rgba(56,217,184,0.06)'
    : 'rgba(74,158,255,0.05)';
  ctx.lineWidth = 0.35;
  ctx.setLineDash([3,8]);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.restore();
}

/* Master draw call */
function drawVessels(now, planetPositions){
  VESSELS.forEach(function(v){
    var pos = vesselPos(v, now, planetPositions);
    if(!pos) return;
    if(pos.x < -60 || pos.x > W+60 || pos.y < -60 || pos.y > H+60) return;

    if(v.type === 'station') drawStation(pos.x, pos.y, v.size, v, now);
    else if(v.type === 'probe') drawProbe(pos.x, pos.y, v.size, v, now);
    else if(v.type === 'alien') drawAlien(pos.x, pos.y, v.size, v, now);
  });
}

/* ================================================================
   RENDER
   ================================================================ */
function render(dt,now){
  drawBg(now); drawDust(now); drawStars(now);

  /* vessel orbit guides — dashed, very faint */
  VESSELS.forEach(function(v){ drawVesselOrbit(v); });

  for(var i=0;i<PLANETS.length;i++) drawOrbitRing(PLANETS[i],now);
  drawSun(now);

  /* compute planet positions for this frame */
  var planetPositions = {};
  var posed=PLANETS.map(function(p,idx){ return {p:p,pos:planetPos(p,now),idx:idx}; });
  posed.sort(function(a,b){ return a.pos.y-b.pos.y; });
  posed.forEach(function(item){ planetPositions[item.p.id] = item.pos; });

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

  /* update + draw vessels on top of planets */
  updateVessels(dt);
  drawVessels(now, planetPositions);
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
