/* ================================================================
   KING DIADEM — Galaxy Scene v48 SUNYATA EDITION
   ความว่างที่ยิ่งใหญ่กว่าสรรพสิ่ง
   Void > Matter · Pink-violet sourceless light · Real stars
   ไม่มีสิ่งเกินจริง · ไม่มีแสงแฟนตาซี · มีเพียงความเวิ้งว้าง
   ================================================================ */
(function(){
'use strict';

var cv = document.getElementById('galaxy');
if (!cv) return;
var ctx = cv.getContext('2d', {alpha:true, desynchronized:true});
var W=0, H=0, _raf=null, _last=0, _dt=0;
var activeRoute = 'general';
var isMobile = false;

var ROUTE_HUE = {general:300,risk:355,collapse:320,survival:270,civil:285,vega:260};
var _tgtHue=300, _curHue=300;
var _burstAlpha = 0;

function loop(now){
  if(!window.KD||window.KD.visible!==false){
    _raf = requestAnimationFrame(loop);
  } else { _raf = null; return; }
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
  buildCityLights();
}
window.addEventListener('KD:resize', function(){ doResize(); }, {passive:true});
window.addEventListener('resize', function(){ clearTimeout(_rT); _rT=setTimeout(doResize,80); },{passive:true});

window.addEventListener('KD:visibility', function(e){
  var vis = e.detail && e.detail.visible;
  if(vis && !_raf){ _last=performance.now(); _raf=requestAnimationFrame(loop); }
}, {passive:true});
document.addEventListener('visibilitychange',function(){
  if(document.hidden){ if(_raf){cancelAnimationFrame(_raf);_raf=null;} }
  else { if(!_raf){_last=performance.now();_raf=requestAnimationFrame(loop);} }
},{passive:true});

window.addEventListener('KD:response', function(e){
  var detail = e.detail || {};
  var route  = detail.consensus && detail.consensus.final_action;
  if(route && ROUTE_HUE[route]){ _tgtHue = ROUTE_HUE[route]; }
  var risk = detail.risk && detail.risk.risk_score;
  if(risk > 75) _burstAlpha = 0.18;
  else if(risk > 45) _burstAlpha = 0.08;
}, {passive:true});

window.addEventListener('KD:decision', function(e){
  var route = e.detail && e.detail.route;
  if(route){ activeRoute = route; _tgtHue = ROUTE_HUE[route]||300; }
}, {passive:true});

/* ================================================================
   STARFIELD — sparse, real, minimal
   ดาวน้อย กระจายสมจริง ไม่แน่น ไม่แฟนตาซี
   ================================================================ */
var STARS=[];
function buildStars(){
  STARS=[];
  /* น้อยกว่า v47 มาก — ให้ความว่างครองพื้นที่ */
  var total = isMobile ? 160 : 280;
  for(var i=0;i<total;i++){
    var layer = Math.random();
    var sz = layer<0.60?0:layer<0.85?1:2;
    /* โทน: mostly white-blue ธรรมชาติ ชมพูอ่อนบ้าง ม่วงน้อยบ้าง */
    var ct = Math.random()<0.12?'pink':Math.random()<0.14?'lavender':'white';
    STARS.push({
      x: Math.random()*W, y: Math.random()*H,
      r: [0.15+Math.random()*0.25, 0.30+Math.random()*0.45, 0.55+Math.random()*0.80][sz],
      /* ความสว่างน้อยกว่า — เพื่อให้ดูลึกและห่างไกล */
      a: [0.10+Math.random()*0.28, 0.20+Math.random()*0.38, 0.35+Math.random()*0.55][sz],
      tw: Math.random()<0.55,
      ph: Math.random()*Math.PI*2,
      sp: 0.08+Math.random()*0.40,  /* กระพริบช้าลง */
      ct: ct,
      cross: sz===2&&Math.random()<0.25  /* cross น้อยลง */
    });
  }
}

function drawStars(now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var a=s.tw?s.a*(0.40+0.60*Math.sin(now*s.sp*0.00038+s.ph)):s.a;
    var col;
    if(s.ct==='pink')     col='rgba(255,190,215,'+a.toFixed(3)+')';
    else if(s.ct==='lavender') col='rgba(200,180,255,'+a.toFixed(3)+')';
    else                   col='rgba(225,235,255,'+a.toFixed(3)+')';
    if(s.cross&&a>s.a*0.60){
      ctx.strokeStyle=col; ctx.lineWidth=0.22;
      var cl=s.r*2.8;
      ctx.beginPath();ctx.moveTo(s.x-cl,s.y);ctx.lineTo(s.x+cl,s.y);ctx.stroke();
      ctx.beginPath();ctx.moveTo(s.x,s.y-cl);ctx.lineTo(s.x,s.y+cl);ctx.stroke();
    }
    ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fillStyle=col; ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   NEBULA DUST — เบา บาง เกือบไม่มี
   แสงไม่มีแหล่งกำเนิด · ชมพูอมม่วงอ่อน · ฟ้าจาง
   ================================================================ */
var DUST=[];
function buildDust(){
  DUST=[];
  /* น้อยมาก และ opacity ต่ำ — ให้รู้สึกว่ามีแสง ไม่ใช่เนบิวลาหนาแน่น */
  var n = isMobile ? 20 : 38;
  var hues=[312,285,268,295,308,275];
  var sats=[22,18,16,20,19,15];
  var lums=[55,52,50,54,52,48];
  for(var i=0;i<n;i++){
    var hi=Math.floor(Math.random()*hues.length);
    DUST.push({
      x:Math.random()*W, y:Math.random()*H,
      r:60+Math.random()*160,   /* ใหญ่ขึ้น แต่โปร่งมาก */
      a:0.008+Math.random()*0.022,  /* opacity ต่ำมาก */
      ph:Math.random()*Math.PI*2,
      sp:0.008+Math.random()*0.035, /* เคลื่อนช้ามาก */
      hue:hues[hi], sat:sats[hi], lum:lums[hi]
    });
  }
}

function drawDust(now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<DUST.length;i++){
    var d=DUST[i];
    var a=d.a*(0.50+0.50*Math.sin(now*d.sp*0.00012+d.ph));
    var g=ctx.createRadialGradient(d.x,d.y,0,d.x,d.y,d.r);
    g.addColorStop(0,'hsla('+d.hue+','+d.sat+'%,'+d.lum+'%,'+a.toFixed(4)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(d.x-d.r,d.y-d.r,d.r*2,d.r*2);
  }
  ctx.restore();
}

/* ================================================================
   CITY LIGHTS
   ================================================================ */
var CITY_DOTS=[];
var CITY_CLUSTERS=[
  [-0.38,-0.18, isMobile?100:180, 0.13, 255,205,120,'usa_east'],
  [-0.48,-0.12, isMobile? 45: 80, 0.09, 255,190,100,'usa_mid'],
  [-0.56,-0.08, isMobile? 35: 60, 0.07, 255,195,110,'usa_west'],
  [-0.08,-0.28, isMobile? 90:160, 0.11, 255,215,135,'europe_w'],
  [-0.10,-0.30, isMobile? 30: 55, 0.04, 255,228,160,'paris'],
  [ 0.06,-0.26, isMobile? 35: 60, 0.07, 255,205,125,'europe_e'],
  [ 0.52,-0.18, isMobile? 50: 90, 0.07, 255,225,145,'japan'],
  [ 0.44,-0.10, isMobile? 55:100, 0.09, 255,215,130,'china'],
  [ 0.28, 0.08, isMobile? 40: 70, 0.08, 255,200,118,'india'],
  [ 0.46, 0.18, isMobile? 28: 50, 0.06, 255,205,120,'sea'],
];
function buildCityLights(){ _cityBuilt=false; CITY_DOTS=[]; }
var _cityBuilt=false, _cityR=0;

function rebuildCityDots(x,y,r){
  CITY_DOTS=[]; _cityR=r;
  for(var ci=0;ci<CITY_CLUSTERS.length;ci++){
    var cl=CITY_CLUSTERS[ci];
    var ox=cl[0],oy=cl[1],density=cl[2],spread=cl[3];
    var R=cl[4],G=cl[5],B=cl[6];
    var cx2=x+ox*r, cy2=y+oy*r;
    var nightFade=Math.max(0,Math.min(1,(-ox+0.08)*3.5));
    if(nightFade<=0.05) continue;
    for(var di=0;di<density;di++){
      var ang=Math.random()*Math.PI*2;
      var dist=Math.random()*spread*r;
      var dx=cx2+Math.cos(ang)*dist;
      var dy=cy2+Math.sin(ang)*dist;
      var ddx=dx-x, ddy=dy-y;
      if(ddx*ddx+ddy*ddy>r*r*0.94) continue;
      CITY_DOTS.push({
        x:dx, y:dy,
        sz:0.5+Math.random()*1.4,
        brightness:(0.45+Math.random()*0.55)*nightFade,
        ph:Math.random()*Math.PI*2,
        sp:0.0008+Math.random()*0.0012,
        R:R, G:G, B:B
      });
    }
  }
  _cityBuilt=true;
}

function drawCityLights(now){
  if(!_cityBuilt||CITY_DOTS.length===0) return;
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<CITY_DOTS.length;i++){
    var d=CITY_DOTS[i];
    var flicker=0.85+0.15*Math.sin(now*d.sp+d.ph);
    var a=d.brightness*flicker;
    ctx.globalAlpha=a*0.90;
    ctx.fillStyle='rgba('+d.R+','+d.G+','+d.B+',1)';
    ctx.beginPath(); ctx.arc(d.x,d.y,d.sz*0.6,0,Math.PI*2); ctx.fill();
    ctx.globalAlpha=a*0.30;
    var dg=ctx.createRadialGradient(d.x,d.y,0,d.x,d.y,d.sz*2.8);
    dg.addColorStop(0,'rgba('+d.R+','+d.G+','+d.B+',1)');
    dg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=dg;
    ctx.beginPath(); ctx.arc(d.x,d.y,d.sz*2.8,0,Math.PI*2); ctx.fill();
  }
  ctx.globalAlpha=1;
  ctx.restore();
}

/* ================================================================
   BACKGROUND — Sunyata Void
   ความมืดลึก · แสงไม่มีแหล่งกำเนิด · ชมพูอมม่วงอ่อนมาก
   ================================================================ */
function drawBg(now){
  ctx.clearRect(0,0,W,H);

  /* base — ลึกกว่า v47 เกือบดำสนิท มีโทนม่วงน้อยมาก */
  var bg=ctx.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,  '#0a040f');
  bg.addColorStop(0.30,'#08030c');
  bg.addColorStop(0.60,'#060209');
  bg.addColorStop(1,  '#040108');
  ctx.fillStyle=bg; ctx.fillRect(0,0,W,H);

  _curHue+=(_tgtHue-_curHue)*0.003*(_dt/16);
  ctx.save(); ctx.globalCompositeOperation='screen';

  /* แสงชมพูอมม่วงอ่อน — กว้าง ไม่มีจุดศูนย์กลาง สื่อถึง sourceless light */
  var nb0=ctx.createRadialGradient(W*0.42,H*0.38,0,W*0.42,H*0.38,W*0.90);
  nb0.addColorStop(0,'rgba(160,80,140,0.07)');
  nb0.addColorStop(0.5,'rgba(120,60,110,0.03)');
  nb0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb0; ctx.fillRect(0,0,W,H);

  /* ฟ้าจาง ๆ ฝั่งซ้าย — แสงที่ไม่รู้มาจากไหน */
  var nb1=ctx.createRadialGradient(W*0.08,H*0.50,0,W*0.08,H*0.50,W*0.55);
  nb1.addColorStop(0,'rgba(80,60,180,0.06)');
  nb1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb1; ctx.fillRect(0,0,W,H);

  /* ม่วงอ่อนฝั่งขวา */
  var nb2=ctx.createRadialGradient(W*0.88,H*0.45,0,W*0.88,H*0.45,W*0.45);
  nb2.addColorStop(0,'rgba(140,70,160,0.055)');
  nb2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb2; ctx.fillRect(0,0,W,H);

  /* risk burst — เบาลงมาก */
  if(_burstAlpha>0.003){
    _burstAlpha*=0.96;
    var burst=ctx.createRadialGradient(W*0.5,H*0.5,0,W*0.5,H*0.5,W*0.7);
    burst.addColorStop(0,'rgba(200,80,140,'+(_burstAlpha).toFixed(3)+')');
    burst.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=burst; ctx.fillRect(0,0,W,H);
  }

  ctx.restore();
}

/* ================================================================
   SUN — เล็กลง · อยู่นอกกรอบ · ให้รู้สึกห่างไกล
   ================================================================ */
function sunCX(){ return W*0.50; }
function sunCY(){ return H*(-0.12); }

function drawSun(now){
  var cx=sunCX(), cy=sunCY();
  var Rs=Math.min(W,H)*(isMobile?0.14:0.11);
  ctx.save(); ctx.globalCompositeOperation='screen';

  /* corona เบาลงมาก */
  var c1=ctx.createRadialGradient(cx,cy,Rs*0.3,cx,cy,Rs*5.0);
  c1.addColorStop(0,'rgba(255,120,80,0.035)');
  c1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c1; ctx.fillRect(0,0,W,H);

  var c2=ctx.createRadialGradient(cx,cy,Rs*0.5,cx,cy,Rs*2.8);
  c2.addColorStop(0,'rgba(255,130,90,0.10)');
  c2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c2; ctx.fillRect(0,0,W,H);

  /* body */
  ctx.globalCompositeOperation='source-over';
  var ph=ctx.createRadialGradient(cx-Rs*0.22,cy-Rs*0.16,0,cx+Rs*0.08,cy+Rs*0.10,Rs);
  ph.addColorStop(0,'#fff8e0');ph.addColorStop(0.08,'#ffe080');ph.addColorStop(0.25,'#ff9c30');
  ph.addColorStop(0.50,'#ff5820');ph.addColorStop(0.75,'#cc2000');ph.addColorStop(1,'#6a0800');
  ctx.fillStyle=ph;
  ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();

  ctx.globalCompositeOperation='screen';
  var hi=ctx.createRadialGradient(cx-Rs*0.16,cy-Rs*0.12,0,cx,cy,Rs);
  hi.addColorStop(0,'rgba(255,255,220,0.55)');
  hi.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=hi;
  ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

/* ================================================================
   PLANET SYSTEM — orbit spacing เหมือนเดิม
   ================================================================ */
var TILT = 0.28;

var PLANETS=[
  {id:'mercury',lbl:'GENERAL', route:'general', orb:0.10,per:0.241,yOff:0.24,rD:0.025,rM:0.032,draw:drawMercury},
  {id:'venus',  lbl:'RISK',    route:'risk',    orb:0.16,per:0.615,yOff:0.34,rD:0.033,rM:0.042,draw:drawVenus  },
  {id:'earth',  lbl:'SURVIVAL',route:'survival',orb:0.22,per:1.000,yOff:0.44,rD:0.072,rM:0.090,draw:drawEarth,moon:true},
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
  /* orbit ring บางและจาง — สื่อถึงวงโคจรที่ไม่ยึดติด */
  ctx.strokeStyle=isAct?'rgba(210,140,200,0.32)':'rgba(160,120,200,0.06)';
  ctx.lineWidth=isAct?0.80:0.30;
  ctx.stroke();
  if(isAct){
    var pos=planetPos(p,now);
    var sg=ctx.createRadialGradient(pos.x,pos.y,0,pos.x,pos.y,8);
    sg.addColorStop(0,'rgba(240,170,210,0.70)');sg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sg; ctx.fillRect(0,0,W,H);
  }
  ctx.restore();
}

function drawLabel(p,pos){
  var isAct=p.route===activeRoute;
  var r=getR(p);
  var fs=Math.max(7,Math.min(10,r*0.50));
  ctx.save();
  ctx.font='500 '+fs+'px "DM Mono",monospace';
  ctx.textAlign='center'; ctx.textBaseline='top';
  if(isAct){
    ctx.shadowColor='rgba(230,150,200,0.70)'; ctx.shadowBlur=7;
    ctx.fillStyle='rgba(255,195,230,0.95)';
  } else {
    ctx.fillStyle='rgba(170,140,210,0.35)';
  }
  ctx.fillText(p.lbl,pos.x,pos.y+r+5);
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
   PLANET HELPERS — ไม่เปลี่ยน
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
  g.addColorStop(0.35,'rgba(255,255,255,0.03)');
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
  g.addColorStop(0,col0); g.addColorStop(0.45,col1); g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  ctx.restore();
}
function pActive(x,y,r,now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var pulse=0.70+0.30*Math.sin(now*0.0020);
  var g=ctx.createRadialGradient(x,y,r*0.5,x,y,r*2.4);
  g.addColorStop(0,'rgba(230,130,195,'+(0.28*pulse).toFixed(3)+')');
  g.addColorStop(0.5,'rgba(190,100,170,'+(0.10*pulse).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  ctx.globalAlpha=0.16*pulse;
  ctx.strokeStyle='rgba(240,140,190,0.70)';ctx.lineWidth=0.9;
  ctx.beginPath();ctx.arc(x,y,r*1.08,0,Math.PI*2);ctx.stroke();
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
   [-0.10,0.06,0.08,0.44],[0.36,-0.16,0.11,0.46],[-0.32,-0.20,0.12,0.50]].forEach(function(c){
    var cg=ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0,x+c[0]*r,y+c[1]*r,c[2]*r);
    cg.addColorStop(0,'rgba(18,8,2,'+c[3]+')');
    cg.addColorStop(0.5,'rgba(30,16,6,'+(c[3]*0.5).toFixed(3)+')');
    cg.addColorStop(0.85,'rgba(120,90,50,'+(c[3]*0.15).toFixed(3)+')');
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply'; ctx.fillStyle=cg; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pTerminator(x,y,r,0.75); pRimLight(x,y,r,'rgba(240,200,140,0.50)');
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
   EARTH v48 — photorealistic satellite view
   เหมือนรูปอ้างอิง: city lights amber · atmosphere pink-blue rim
   ================================================================ */
function drawEarth(x,y,r,now){
  ctx.save();
  if(!_cityBuilt || Math.abs(_cityR-r)>1){ rebuildCityDots(x,y,r); }

  ctx.fillStyle='#000510';
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* Ocean — deep photorealistic */
  ctx.globalCompositeOperation='source-over';
  var ocean=ctx.createRadialGradient(x-r*0.15,y-r*0.12,r*0.05,x+r*0.20,y+r*0.20,r*1.05);
  ocean.addColorStop(0,'#c0eeff'); ocean.addColorStop(0.06,'#52ccea');
  ocean.addColorStop(0.16,'#1a90cc'); ocean.addColorStop(0.32,'#0660a8');
  ocean.addColorStop(0.52,'#033a80'); ocean.addColorStop(0.72,'#011c48');
  ocean.addColorStop(0.88,'#000c28'); ocean.addColorStop(1,'#000510');
  ctx.fillStyle=ocean; ctx.fillRect(0,0,W,H);

  function land(ox,oy,rx,R,G,B,a){
    var g=ctx.createRadialGradient(x+ox*r,y+oy*r,0,x+ox*r,y+oy*r,rx*r);
    g.addColorStop(0,'rgba('+R+','+G+','+B+','+a+')');
    g.addColorStop(0.38,'rgba('+R+','+G+','+B+','+(a*0.70).toFixed(2)+')');
    g.addColorStop(0.68,'rgba('+R+','+G+','+B+','+(a*0.28).toFixed(2)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  }
  /* continents */
  land( 0.46, 0.26,0.24,200,60,10,0.99); land( 0.55, 0.18,0.12,185,48,8,0.96);
  land( 0.60, 0.34,0.09, 65,122,38,0.90); land( 0.10,-0.05,0.23,200,154,68,0.92);
  land( 0.14, 0.16,0.17,152,122,52,0.88); land( 0.15, 0.02,0.10, 44,108,35,0.86);
  land( 0.06,-0.13,0.12,218,175,84,0.88); land( 0.24,-0.09,0.14,215,178,95,0.90);
  land( 0.06,-0.25,0.12, 68,140,48,0.84); land( 0.12,-0.34,0.09, 62,130,44,0.80);
  land( 0.34,-0.32,0.29, 78,142,52,0.80); land( 0.48,-0.14,0.15, 92,152,56,0.82);
  land( 0.36, 0.02,0.12,132,162,62,0.84); land( 0.52, 0.02,0.10, 44,112,38,0.82);
  land( 0.30,-0.22,0.18,162,170,82,0.76); land(-0.32,-0.30,0.22, 68,125,46,0.86);
  land(-0.22, 0.16,0.15, 32, 98,32,0.92); land(-0.30, 0.20,0.06,120,100,54,0.80);
  land(-0.10,-0.54,0.08,212,224,232,0.86);

  /* Coastal teal */
  ctx.globalCompositeOperation='screen';
  var tc=ctx.createRadialGradient(x+r*0.40,y+r*0.22,r*0.12,x+r*0.40,y+r*0.22,r*0.26);
  tc.addColorStop(0,'rgba(0,200,188,0.28)'); tc.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=tc; ctx.fillRect(0,0,W,H);

  /* Ice caps */
  ctx.globalCompositeOperation='source-over';
  var ant=ctx.createRadialGradient(x,y+r*0.80,0,x,y+r*0.80,r*0.30);
  ant.addColorStop(0,'rgba(252,255,255,0.96)'); ant.addColorStop(0.5,'rgba(232,246,255,0.72)'); ant.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ant; ctx.fillRect(0,0,W,H);
  var np=ctx.createRadialGradient(x,y-r*0.77,0,x,y-r*0.77,r*0.22);
  np.addColorStop(0,'rgba(245,252,255,0.92)'); np.addColorStop(0.5,'rgba(225,244,255,0.62)'); np.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np; ctx.fillRect(0,0,W,H);

  /* Clouds */
  ctx.globalCompositeOperation='screen';
  var cSpin=now*0.000038;
  for(var ci=0;ci<14;ci++){
    var ca=cSpin+ci*(Math.PI*2/14);
    var crad=r*(0.08+ci*0.016);
    var cx2=x+Math.cos(ca)*crad*0.55;
    var cy2=y+Math.sin(ca)*crad*0.28;
    var csz=r*(0.13+Math.sin(ci*1.3)*0.055);
    var cg=ctx.createRadialGradient(cx2,cy2,0,cx2,cy2,csz);
    var ca2=(0.18+0.14*Math.sin(ci*0.9+now*0.000010));
    cg.addColorStop(0,'rgba(255,255,255,'+ca2+')');
    cg.addColorStop(0.5,'rgba(240,248,255,'+(ca2*0.45).toFixed(3)+')');
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cg; ctx.fillRect(0,0,W,H);
  }

  drawCityLights(now);

  /* Night terminator */
  ctx.globalAlpha=1; ctx.globalCompositeOperation='multiply';
  var term=ctx.createLinearGradient(x-r*0.05,y,x+r*0.50,y);
  term.addColorStop(0,'rgba(0,0,0,0)'); term.addColorStop(0.30,'rgba(0,4,18,0.18)');
  term.addColorStop(0.58,'rgba(0,4,18,0.64)'); term.addColorStop(0.78,'rgba(0,2,10,0.88)');
  term.addColorStop(1,'rgba(0,0,0,0.96)');
  ctx.fillStyle=term; ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.globalAlpha=1;
  ctx.restore();

  /* Atmosphere rim — เหมือนรูปอ้างอิง: ชมพูอมม่วงอ่อน + ฟ้า */
  ctx.globalCompositeOperation='screen';
  var atm=ctx.createRadialGradient(x,y,r*0.87,x,y,r*1.24);
  atm.addColorStop(0,'rgba(170,130,250,0.24)');
  atm.addColorStop(0.30,'rgba(110,90,220,0.10)');
  atm.addColorStop(0.60,'rgba(70,150,255,0.06)');
  atm.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm; ctx.fillRect(0,0,W,H);

  pSpecular(x,y,r,0.26,0.36);
  pTerminator(x,y,r,0.68);
  pRimLight(x,y,r,'rgba(195,145,255,0.60)');
  ctx.globalAlpha=1; ctx.restore();
}

/* ================================================================
   MARS
   ================================================================ */
function drawMars(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#f0b090'],[0.15,'#c86038'],[0.35,'#9c3018'],
    [0.58,'#6a1808'],[0.80,'#400c02'],[1,'#200400']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='overlay';
  [[0.18,-0.12,0.32,0.28],[-0.14,0.22,0.24,0.22],[0.30,0.10,0.18,0.20]].forEach(function(c){
    var mg=ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0,x+c[0]*r,y+c[1]*r,c[2]*r);
    mg.addColorStop(0,'rgba(180,80,40,'+c[3]+')'); mg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=mg; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  var pc=ctx.createRadialGradient(x,y-r*0.78,0,x,y-r*0.78,r*0.20);
  pc.addColorStop(0,'rgba(240,240,255,0.88)'); pc.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=pc; ctx.globalCompositeOperation='source-over'; ctx.fillRect(0,0,W,H);
  pTerminator(x,y,r,0.76); pRimLight(x,y,r,'rgba(255,180,100,0.50)');
  pSpecular(x,y,r,0.10,0.38);
  ctx.restore();
}

/* ================================================================
   JUPITER
   ================================================================ */
function drawJupiter(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#f0d8b0'],[0.12,'#d4a060'],[0.28,'#b87838'],
    [0.50,'#9a5820'],[0.72,'#6c3408'],[1,'#3c1800']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='overlay';
  var jSpin=now*0.0000058;
  for(var bi=0;bi<10;bi++){
    var by=y-r*0.88+bi*r*0.20+Math.sin(jSpin+bi*0.7)*r*0.018;
    var ba=0.12+0.14*Math.abs(Math.sin(bi*0.55+jSpin));
    var jg=ctx.createLinearGradient(x-r,by,x+r,by+r*0.05);
    var c1b=bi%3===0?'rgba(160,80,40,'+ba+')':bi%3===1?'rgba(200,140,70,'+ba+')':'rgba(140,100,60,'+ba+')';
    var c2b=bi%3===0?'rgba(120,50,20,'+ba+')':bi%3===1?'rgba(180,110,50,'+ba+')':'rgba(100,70,40,'+ba+')';
    jg.addColorStop(0,'rgba(0,0,0,0)');jg.addColorStop(0.25,c1b);jg.addColorStop(0.5,c2b);
    jg.addColorStop(0.75,c1b);jg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=jg; ctx.fillRect(x-r,by,r*2,r*0.16);
  }
  var grs=ctx.createRadialGradient(x+r*0.20,y+r*0.12,0,x+r*0.20,y+r*0.12,r*0.14);
  grs.addColorStop(0,'rgba(180,50,30,0.72)');grs.addColorStop(0.5,'rgba(140,40,20,0.40)');grs.addColorStop(1,'rgba(0,0,0,0)');
  ctx.globalCompositeOperation='overlay'; ctx.fillStyle=grs; ctx.fillRect(0,0,W,H);
  ctx.restore();
  pTerminator(x,y,r,0.62); pRimLight(x,y,r,'rgba(255,220,160,0.48)');
  pSpecular(x,y,r,0.14,0.50);
  ctx.restore();
}

/* ================================================================
   VEGA — ringed albino planet
   ================================================================ */
function drawVega(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#f0e8ff'],[0.15,'#d0b8f8'],[0.35,'#a888e0'],
    [0.58,'#7048b8'],[0.80,'#301878'],[1,'#100838']
  ]);
  ctx.save(); ctx.globalCompositeOperation='screen';
  ctx.beginPath();
  ctx.ellipse(x,y,r*1.85,r*0.32,0,0,Math.PI*2);
  var rg=ctx.createLinearGradient(x-r*1.85,y,x+r*1.85,y);
  rg.addColorStop(0,'rgba(240,180,255,0)');
  rg.addColorStop(0.15,'rgba(220,160,255,0.30)');
  rg.addColorStop(0.38,'rgba(200,140,240,0.50)');
  rg.addColorStop(0.50,'rgba(180,120,220,0.18)');
  rg.addColorStop(0.62,'rgba(200,140,240,0.50)');
  rg.addColorStop(0.85,'rgba(220,160,255,0.30)');
  rg.addColorStop(1,'rgba(240,180,255,0)');
  ctx.strokeStyle=rg; ctx.lineWidth=r*0.22; ctx.stroke();
  ctx.restore();
  pTerminator(x,y,r,0.66); pRimLight(x,y,r,'rgba(220,170,255,0.72)');
  pSpecular(x,y,r,0.20,0.40);
  ctx.restore();
}

/* ================================================================
   MOON
   ================================================================ */
function drawMoon(earthPos,now){
  var mr=getR(PLANETS[2])*0.28;
  var ma=now*0.000120;
  var md=getR(PLANETS[2])*1.85;
  var mx2=earthPos.x+Math.cos(ma)*md;
  var my2=earthPos.y+Math.sin(ma)*md*0.40;
  ctx.save();
  pSphere(mx2,my2,mr,[
    [0,'#f0e8e0'],[0.20,'#d0c8b0'],[0.50,'#a09078'],
    [0.78,'#706050'],[1,'#302818']
  ]);
  pTerminator(mx2,my2,mr,0.78);
  pRimLight(mx2,my2,mr,'rgba(230,195,215,0.38)');
  ctx.restore();
}

/* ================================================================
   SPACECRAFT — จาง เงียบ
   ================================================================ */
function drawSpacecraft(now){
  var st=0.000022, sa=(now*st)%(Math.PI*2);
  var sr=Math.min(W,H)*0.62;
  var sx=sunCX()+Math.cos(sa)*sr;
  var sy=sunCY()+H*0.28+Math.sin(sa)*sr*TILT;
  ctx.save(); ctx.globalCompositeOperation='screen';
  ctx.fillStyle='rgba(210,190,245,0.75)';
  ctx.beginPath(); ctx.arc(sx,sy,1.6,0,Math.PI*2); ctx.fill();
  ctx.font='500 7px "DM Mono",monospace';
  ctx.fillStyle='rgba(200,175,240,0.50)';
  ctx.fillText('KD-1',sx+4,sy-3);
  ctx.restore();

  var lp=0.000035, la=(now*lp+1.8)%(Math.PI*2);
  var lr=Math.min(W,H)*0.48;
  var lx=sunCX()+Math.cos(la)*lr;
  var ly=sunCY()+H*0.20+Math.sin(la)*lr*TILT;
  ctx.save(); ctx.globalCompositeOperation='screen';
  ctx.fillStyle='rgba(245,170,208,0.72)';
  ctx.beginPath(); ctx.arc(lx,ly,1.4,0,Math.PI*2); ctx.fill();
  ctx.font='500 6px "DM Mono",monospace';
  ctx.fillStyle='rgba(240,165,205,0.48)';
  ctx.fillText('LYLA-P',lx+3,ly-3);
  ctx.restore();

  var vp=0.000028, va=(now*vp+3.5)%(Math.PI*2);
  var vr=Math.min(W,H)*0.54;
  var vx=sunCX()+Math.cos(va)*vr;
  var vy=sunCY()+H*0.22+Math.sin(va)*vr*TILT;
  ctx.save(); ctx.globalCompositeOperation='screen';
  ctx.fillStyle='rgba(190,160,250,0.72)';
  ctx.beginPath(); ctx.arc(vx,vy,1.4,0,Math.PI*2); ctx.fill();
  ctx.font='500 6px "DM Mono",monospace';
  ctx.fillStyle='rgba(185,155,245,0.48)';
  ctx.fillText('VEGA-P',vx+3,vy-3);
  ctx.restore();
}

/* ================================================================
   RENDER
   ================================================================ */
function render(dt,now){
  drawBg(now);
  drawDust(now);
  drawStars(now);
  drawSun(now);
  for(var i=0;i<PLANETS.length;i++) drawOrbitRing(PLANETS[i],now);
  _cache=[];
  for(var j=0;j<PLANETS.length;j++){
    var p=PLANETS[j];
    var pos=planetPos(p,now);
    _cache.push(pos);
    var r=getR(p);
    if(p.route===activeRoute) pActive(pos.x,pos.y,r,now);
    p.draw(pos.x,pos.y,r,now);
    if(p.moon) drawMoon(pos,now);
    drawLabel(p,pos);
  }
  drawSpacecraft(now);
}

/* ================================================================
   PUBLIC API
   ================================================================ */
window.KD_setRoute=function(route){
  activeRoute=route;
  _tgtHue=ROUTE_HUE[route]||300;
  if(typeof window.setRoute==='function') window.setRoute(route);
  window.dispatchEvent(new CustomEvent('KD:routeChange',{detail:{route:route}}));
};
window.KD_pulse = window.KD_pulse || function(route){
  if(route) window.KD_setRoute(route);
};
window.KD_setState = window.KD_setState || function(key,val){
  if(!window.KD) window.KD={};
  if(!window.KD.state) window.KD.state={};
  window.KD.state[key]=val;
};

doResize();
_last=performance.now();
_raf=requestAnimationFrame(loop);

})();
