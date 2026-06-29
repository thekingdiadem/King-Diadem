/* ================================================================
   KING DIADEM — Galaxy Scene v49 SOLAR SYSTEM REAL EDITION
   พื้นหลัง: deep space dark + dense stars + warm amber nebula
   ดาวทุกดวง: สีจริง ขนาดสัมพัทธ์จริง วงโคจรจริง
   ลำดับ: Sun → Mercury → Venus → Earth+Moon → Mars →
           Jupiter → Saturn(rings) → Pluto
   ไม่มีชมพู ไม่มีม่วง ไม่มีสีแฟนตาซี
   Route mapping ยังคงเดิม (GENERAL/RISK/SURVIVAL/COLLAPSE/CIVIL/VEGA)
   ================================================================ */
(function(){
'use strict';

var cv = document.getElementById('galaxy');
if (!cv) return;
var ctx = cv.getContext('2d', {alpha:true, desynchronized:true});
var W=0, H=0, _raf=null, _last=0, _dt=0;
var activeRoute = 'general';
var isMobile = false;

var ROUTE_HUE = {general:45,risk:15,collapse:0,survival:200,civil:30,vega:220};
var _tgtHue=45, _curHue=45;
var _burstAlpha = 0;

/* ── PLANET → ROUTE MAP ─────────────────────────────────────── */
/* Mercury=GENERAL Venus=RISK Earth=SURVIVAL Mars=COLLAPSE
   Jupiter=CIVIL Saturn=VEGA Pluto=bonus(no route) */
var ROUTE_PLANET = {
  general:'mercury', risk:'venus', survival:'earth',
  collapse:'mars', civil:'jupiter', vega:'saturn'
};

function loop(now){
  if(!window.KD||window.KD.visible!==false){
    _raf = requestAnimationFrame(loop);
  } else { _raf=null; return; }
  _dt = Math.min(now-_last,50);
  _last = now;
  render(_dt,now);
}

var _rT;
function doResize(){
  W = cv.width  = window.innerWidth;
  H = cv.height = window.innerHeight;
  isMobile = W < 768;
  buildStars();
}
window.addEventListener('KD:resize',function(){ doResize(); },{passive:true});
window.addEventListener('resize',function(){ clearTimeout(_rT); _rT=setTimeout(doResize,80); },{passive:true});
window.addEventListener('KD:visibility',function(e){
  var vis=e.detail&&e.detail.visible;
  if(vis&&!_raf){ _last=performance.now(); _raf=requestAnimationFrame(loop); }
},{passive:true});
document.addEventListener('visibilitychange',function(){
  if(document.hidden){ if(_raf){cancelAnimationFrame(_raf);_raf=null;} }
  else{ if(!_raf){_last=performance.now();_raf=requestAnimationFrame(loop);} }
},{passive:true});
window.addEventListener('KD:response',function(e){
  var detail=e.detail||{};
  var risk=detail.risk&&detail.risk.risk_score;
  if(risk>75) _burstAlpha=0.12;
  else if(risk>45) _burstAlpha=0.06;
},{passive:true});
window.addEventListener('KD:decision',function(e){
  var route=e.detail&&e.detail.route;
  if(route){ activeRoute=route; }
},{passive:true});

/* ================================================================
   STARFIELD — dense, real, blue-white-amber mix (เหมือนรูป 3)
   ================================================================ */
var STARS=[];
function buildStars(){
  STARS=[];
  var total=isMobile?500:900;
  for(var i=0;i<total;i++){
    var sz=Math.random();
    var r=sz<0.65?0.18+Math.random()*0.22:
           sz<0.88?0.35+Math.random()*0.55:
                   0.65+Math.random()*1.10;
    /* สีดาวจริง: ส่วนใหญ่ขาว-ฟ้า บางดวง amber/warm white */
    var ct=Math.random()<0.08?'amber':
           Math.random()<0.12?'blue':'white';
    STARS.push({
      x:Math.random()*W, y:Math.random()*H, r:r,
      a:0.15+Math.random()*0.75,
      tw:Math.random()<0.45,
      ph:Math.random()*Math.PI*2,
      sp:0.05+Math.random()*0.30,
      ct:ct,
      cross:r>0.9&&Math.random()<0.20
    });
  }
}

function drawStars(now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var a=s.tw?s.a*(0.30+0.70*Math.sin(now*s.sp*0.00035+s.ph)):s.a;
    var col;
    if(s.ct==='amber')  col='rgba(255,210,120,'+a.toFixed(3)+')';
    else if(s.ct==='blue') col='rgba(180,210,255,'+a.toFixed(3)+')';
    else                   col='rgba(245,248,255,'+a.toFixed(3)+')';
    if(s.cross&&a>s.a*0.55){
      ctx.strokeStyle=col; ctx.lineWidth=0.18;
      var cl=s.r*3.2;
      ctx.beginPath();ctx.moveTo(s.x-cl,s.y);ctx.lineTo(s.x+cl,s.y);ctx.stroke();
      ctx.beginPath();ctx.moveTo(s.x,s.y-cl);ctx.lineTo(s.x,s.y+cl);ctx.stroke();
    }
    ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fillStyle=col; ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   BACKGROUND — deep space + warm amber nebula bottom-left
   reference: รูป 3 (dark void, dense stars, amber galaxy arm)
   ================================================================ */
function drawBg(now){
  ctx.clearRect(0,0,W,H);

  /* base — สีจริงของอวกาศลึก เกือบดำ มีน้ำเงินน้อยมาก */
  var bg=ctx.createLinearGradient(0,0,W,H);
  bg.addColorStop(0,  '#020308');
  bg.addColorStop(0.35,'#010206');
  bg.addColorStop(0.70,'#020307');
  bg.addColorStop(1,  '#030408');
  ctx.fillStyle=bg; ctx.fillRect(0,0,W,H);

  ctx.save(); ctx.globalCompositeOperation='screen';

  /* warm amber nebula bottom-left — เหมือนรูป 3 */
  var nb0=ctx.createRadialGradient(W*0.08,H*0.92,0,W*0.08,H*0.92,W*0.55);
  nb0.addColorStop(0,'rgba(200,120,40,0.18)');
  nb0.addColorStop(0.35,'rgba(180,90,20,0.10)');
  nb0.addColorStop(0.70,'rgba(140,60,10,0.04)');
  nb0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb0; ctx.fillRect(0,0,W,H);

  /* milky way arm — amber ล่างซ้าย สาดขึ้นมา */
  var mw=ctx.createLinearGradient(0,H,W*0.55,H*0.20);
  mw.addColorStop(0,'rgba(180,100,30,0.12)');
  mw.addColorStop(0.40,'rgba(160,80,20,0.06)');
  mw.addColorStop(0.70,'rgba(100,50,10,0.025)');
  mw.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=mw; ctx.fillRect(0,0,W,H);

  /* faint blue tint top-right — ความลึกของอวกาศ */
  var nb1=ctx.createRadialGradient(W*0.85,H*0.15,0,W*0.85,H*0.15,W*0.50);
  nb1.addColorStop(0,'rgba(30,50,120,0.06)');
  nb1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb1; ctx.fillRect(0,0,W,H);

  /* risk burst */
  if(_burstAlpha>0.002){
    _burstAlpha*=0.97;
    var burst=ctx.createRadialGradient(W*0.5,H*0.5,0,W*0.5,H*0.5,W*0.65);
    burst.addColorStop(0,'rgba(255,140,40,'+(_burstAlpha).toFixed(3)+')');
    burst.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=burst; ctx.fillRect(0,0,W,H);
  }

  ctx.restore();
}

/* ================================================================
   SUN — ดวงอาทิตย์จริง อยู่บนสุด มองเห็นชัด
   สี: white-yellow core, orange corona, red-orange limb
   ================================================================ */
function sunCX(){ return W*0.50; }
function sunCY(){ return H*(-0.06); }  /* โผล่จากขอบบน */

function drawSun(now){
  var cx=sunCX(), cy=sunCY();
  var Rs=Math.min(W,H)*(isMobile?0.18:0.15);

  ctx.save(); ctx.globalCompositeOperation='screen';

  /* outer corona glow — warm white-gold */
  var c0=ctx.createRadialGradient(cx,cy,Rs*0.4,cx,cy,Rs*7.0);
  c0.addColorStop(0,'rgba(255,240,180,0.06)');
  c0.addColorStop(0.30,'rgba(255,200,80,0.03)');
  c0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c0; ctx.fillRect(0,0,W,H);

  /* mid corona */
  var c1=ctx.createRadialGradient(cx,cy,Rs*0.5,cx,cy,Rs*3.5);
  c1.addColorStop(0,'rgba(255,220,100,0.18)');
  c1.addColorStop(0.50,'rgba(255,160,40,0.07)');
  c1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c1; ctx.fillRect(0,0,W,H);

  /* inner corona */
  var c2=ctx.createRadialGradient(cx,cy,Rs*0.6,cx,cy,Rs*1.85);
  c2.addColorStop(0,'rgba(255,240,160,0.35)');
  c2.addColorStop(0.55,'rgba(255,180,60,0.14)');
  c2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c2; ctx.fillRect(0,0,W,H);

  /* solar rays */
  ctx.save();
  for(var ri=0;ri<16;ri++){
    var ra=(ri/16)*Math.PI*2+now*0.000008;
    var rl=Rs*(1.4+0.3*Math.sin(now*0.000009+ri*0.7));
    ctx.globalAlpha=0.012+0.006*Math.abs(Math.sin(now*0.00012+ri));
    var rx1=cx+Math.cos(ra)*Rs*0.6, ry1=cy+Math.sin(ra)*Rs*0.6;
    var rx2=cx+Math.cos(ra)*rl,     ry2=cy+Math.sin(ra)*rl;
    var rg=ctx.createLinearGradient(rx1,ry1,rx2,ry2);
    rg.addColorStop(0,'rgba(255,230,120,1)');
    rg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle=rg; ctx.lineWidth=Rs*0.040; ctx.lineCap='round';
    ctx.beginPath();ctx.moveTo(rx1,ry1);ctx.lineTo(rx2,ry2);ctx.stroke();
  }
  ctx.globalAlpha=1; ctx.restore();

  /* sun body — photosphere */
  ctx.globalCompositeOperation='source-over';
  var ph=ctx.createRadialGradient(cx-Rs*0.20,cy-Rs*0.15,Rs*0.01,cx+Rs*0.05,cy+Rs*0.08,Rs);
  ph.addColorStop(0,'#fffde8');   /* center: near-white hot */
  ph.addColorStop(0.04,'#fff5a0');
  ph.addColorStop(0.12,'#ffd040');
  ph.addColorStop(0.28,'#ffaa18');
  ph.addColorStop(0.50,'#ff7800');
  ph.addColorStop(0.72,'#e04000');
  ph.addColorStop(0.88,'#a01800');
  ph.addColorStop(1,  '#500800');
  ctx.fillStyle=ph;
  ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();

  /* limb darkening overlay */
  ctx.globalCompositeOperation='multiply';
  var ld=ctx.createRadialGradient(cx-Rs*0.10,cy-Rs*0.08,Rs*0.55,cx,cy,Rs*1.02);
  ld.addColorStop(0,'rgba(255,255,255,0)');
  ld.addColorStop(0.72,'rgba(80,20,0,0.18)');
  ld.addColorStop(1,'rgba(20,4,0,0.52)');
  ctx.fillStyle=ld;
  ctx.beginPath(); ctx.arc(cx,cy,Rs*1.02,0,Math.PI*2); ctx.fill();

  /* specular highlight */
  ctx.globalCompositeOperation='screen';
  var hi=ctx.createRadialGradient(cx-Rs*0.18,cy-Rs*0.14,0,cx-Rs*0.04,cy-Rs*0.02,Rs*0.55);
  hi.addColorStop(0,'rgba(255,255,240,0.65)');
  hi.addColorStop(0.28,'rgba(255,248,200,0.18)');
  hi.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=hi;
  ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();

  ctx.restore();
}

/* ================================================================
   PLANET ORBIT SYSTEM
   ลำดับจริง: Mercury→Venus→Earth→Mars→Jupiter→Saturn→Pluto
   yOff = ตำแหน่ง vertical ใน viewport (0=บน 1=ล่าง)
   orb  = orbital radius สัมพัทธ์ต่อ min(W,H)
   per  = orbital period สัมพัทธ์ (Earth=1.0)
   ================================================================ */
var TILT = 0.26;  /* perspective tilt */

/* rD=desktop radius factor, rM=mobile radius factor */
var PLANETS = [
  /* id          lbl        route       orb    per      yOff   rD      rM    draw */
  {id:'mercury', lbl:'GENERAL',  route:'general',  orb:0.09, per:0.241, yOff:0.22, rD:0.018, rM:0.024, draw:drawMercury},
  {id:'venus',   lbl:'RISK',     route:'risk',     orb:0.15, per:0.615, yOff:0.31, rD:0.028, rM:0.036, draw:drawVenus  },
  {id:'earth',   lbl:'SURVIVAL', route:'survival', orb:0.21, per:1.000, yOff:0.40, rD:0.062, rM:0.078, draw:drawEarth, moon:true},
  {id:'mars',    lbl:'COLLAPSE', route:'collapse', orb:0.28, per:1.881, yOff:0.50, rD:0.033, rM:0.042, draw:drawMars  },
  {id:'jupiter', lbl:'CIVIL',    route:'civil',    orb:0.37, per:11.86, yOff:0.61, rD:0.055, rM:0.068, draw:drawJupiter},
  {id:'saturn',  lbl:'VEGA',     route:'vega',     orb:0.43, per:29.46, yOff:0.73, rD:0.045, rM:0.056, draw:drawSaturn },
  {id:'pluto',   lbl:'PLUTO',    route:'',         orb:0.48, per:247.9, yOff:0.84, rD:0.014, rM:0.018, draw:drawPluto  },
];

function planetPos(p,now){
  var BASE=0.000038;
  var angle=(now*BASE/p.per)%(Math.PI*2);
  var R=Math.min(W,H)*p.orb;
  var cx=sunCX()+Math.cos(angle)*R;
  var oy=sunCY()+H*p.yOff;
  var cy=oy+Math.sin(angle)*R*TILT;
  return {x:cx,y:cy,angle:angle,orbitR:R,orbitY:oy};
}

function getR(p){ return Math.min(W,H)*(isMobile?p.rM:p.rD); }

function drawOrbitRing(p){
  var R=Math.min(W,H)*p.orb;
  var oy=sunCY()+H*p.yOff;
  var isAct=p.route===activeRoute;
  ctx.save(); ctx.globalCompositeOperation='screen';
  ctx.beginPath();
  ctx.ellipse(sunCX(),oy,R,R*TILT,0,0,Math.PI*2);
  ctx.strokeStyle=isAct?'rgba(255,220,120,0.28)':'rgba(180,180,200,0.05)';
  ctx.lineWidth=isAct?0.90:0.28;
  ctx.stroke();
  ctx.restore();
}

function drawLabel(p,pos){
  if(!p.lbl) return;
  var isAct=p.route===activeRoute;
  var r=getR(p);
  var fs=Math.max(7,Math.min(10,r*0.50));
  ctx.save();
  ctx.font='500 '+fs+'px "DM Mono",monospace';
  ctx.textAlign='center'; ctx.textBaseline='top';
  if(isAct){
    ctx.shadowColor='rgba(255,220,100,0.80)'; ctx.shadowBlur=8;
    ctx.fillStyle='rgba(255,240,180,0.97)';
  } else {
    ctx.fillStyle='rgba(180,185,200,0.38)';
  }
  ctx.fillText(p.lbl,pos.x,pos.y+r+5);
  ctx.restore();
}

/* click / touch → setRoute */
var _cache=[];
cv.addEventListener('click',function(e){
  var rc=cv.getBoundingClientRect();
  var mx=e.clientX-rc.left,my=e.clientY-rc.top;
  for(var i=0;i<_cache.length;i++){
    var pp=_cache[i];
    var dx=mx-pp.x,dy=my-pp.y,r=getR(PLANETS[i])*1.9;
    if(dx*dx+dy*dy<r*r&&PLANETS[i].route)
      window.KD_setRoute&&window.KD_setRoute(PLANETS[i].route);
  }
},{passive:true});
cv.addEventListener('touchend',function(e){
  if(e.changedTouches.length===1){
    var t=e.changedTouches[0];
    cv.dispatchEvent(new MouseEvent('click',{clientX:t.clientX,clientY:t.clientY}));
  }
},{passive:true});

/* ================================================================
   PLANET DRAW HELPERS
   ================================================================ */
function pSphere(x,y,r,stops){
  var g=ctx.createRadialGradient(x-r*0.32,y-r*0.26,r*0.01,x+r*0.12,y+r*0.12,r*1.04);
  for(var i=0;i<stops.length;i++) g.addColorStop(stops[i][0],stops[i][1]);
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
}
function pTerminator(x,y,r,s){
  s=s||0.72;
  ctx.save(); ctx.globalCompositeOperation='multiply';
  var g=ctx.createRadialGradient(x+r*0.28,y+r*0.22,r*0.05,x+r*0.32,y+r*0.26,r*1.08);
  g.addColorStop(0,'rgba(0,0,0,0)');
  g.addColorStop(0.42,'rgba(0,0,0,'+(s*0.35).toFixed(3)+')');
  g.addColorStop(0.68,'rgba(0,0,0,'+(s*0.72).toFixed(3)+')');
  g.addColorStop(0.85,'rgba(0,0,0,'+(s*0.90).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,'+s+')');
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r*1.04,0,Math.PI*2); ctx.fill();
  ctx.restore();
}
function pRimLight(x,y,r,col){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.28,y-r*0.22,r*0.82,x,y,r*1.02);
  g.addColorStop(0,col);
  g.addColorStop(0.40,'rgba(255,255,255,0.025)');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r*1.02,0,Math.PI*2); ctx.fill();
  ctx.restore();
}
function pSpecular(x,y,r,a,sz){
  a=a||0.22; sz=sz||0.42;
  ctx.save(); ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.20,y-r*0.16,0,x-r*0.06,y-r*0.04,r*sz);
  g.addColorStop(0,'rgba(255,255,255,'+a+')');
  g.addColorStop(0.32,'rgba(255,255,255,'+(a*0.26).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.restore();
}
function pActive(x,y,r,now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var pulse=0.68+0.32*Math.sin(now*0.0022);
  var g=ctx.createRadialGradient(x,y,r*0.5,x,y,r*2.5);
  g.addColorStop(0,'rgba(255,210,80,'+(0.30*pulse).toFixed(3)+')');
  g.addColorStop(0.5,'rgba(255,160,30,'+(0.10*pulse).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  ctx.globalAlpha=0.18*pulse;
  ctx.strokeStyle='rgba(255,200,60,0.75)'; ctx.lineWidth=0.9;
  ctx.beginPath();ctx.arc(x,y,r*1.10,0,Math.PI*2);ctx.stroke();
  ctx.globalAlpha=1; ctx.restore();
}

/* ================================================================
   MERCURY — สีเทาอมน้ำตาล มี craters
   ================================================================ */
function drawMercury(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#e8ddd0'],[0.12,'#c8b89a'],[0.30,'#a89878'],
    [0.55,'#7a6a50'],[0.78,'#4a3c28'],[1,'#201808']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  [[0.22,0.10,0.16,0.50],[-.20,0.25,0.13,0.46],[0.05,-.24,0.15,0.48],
   [-.08,0.05,0.08,0.44],[0.32,-.14,0.10,0.45]].forEach(function(c){
    var g=ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0,x+c[0]*r,y+c[1]*r,c[2]*r);
    g.addColorStop(0,'rgba(16,8,2,'+c[3]+')');
    g.addColorStop(0.5,'rgba(28,14,4,'+(c[3]*0.48).toFixed(3)+')');
    g.addColorStop(0.85,'rgba(110,85,45,'+(c[3]*0.14).toFixed(3)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply'; ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pTerminator(x,y,r,0.76);
  pRimLight(x,y,r,'rgba(230,190,130,0.48)');
  pSpecular(x,y,r,0.11,0.38);
  ctx.restore();
}

/* ================================================================
   VENUS — สีเหลืองอมน้ำตาล มีชั้นเมฆหนา
   ================================================================ */
function drawVenus(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#fff8c8'],[0.10,'#f0d860'],[0.25,'#d4a830'],
    [0.50,'#a86c10'],[0.75,'#6a3c00'],[1,'#301400']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='overlay';
  for(var bi=0;bi<9;bi++){
    var by=y-r*0.88+bi*r*0.22+Math.sin(now*0.0000085+bi*1.1)*r*0.022;
    var ba=0.07+0.11*Math.abs(Math.sin(bi*0.68+now*0.0000072));
    var lg=ctx.createLinearGradient(x-r,by,x+r,by+r*0.05);
    lg.addColorStop(0,'rgba(255,240,160,0)');
    lg.addColorStop(0.28,'rgba(255,235,145,'+ba+')');
    lg.addColorStop(0.72,'rgba(255,235,145,'+ba+')');
    lg.addColorStop(1,'rgba(255,240,160,0)');
    ctx.fillStyle=lg; ctx.fillRect(x-r,by,r*2,r*0.17);
  }
  ctx.restore();
  /* atmosphere haze */
  ctx.globalCompositeOperation='screen';
  var ah=ctx.createRadialGradient(x,y,r*0.90,x,y,r*1.24);
  ah.addColorStop(0,'rgba(240,200,80,0.14)');
  ah.addColorStop(0.45,'rgba(200,150,40,0.05)');
  ah.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ah; ctx.fillRect(0,0,W,H);
  pTerminator(x,y,r,0.64);
  pRimLight(x,y,r,'rgba(255,240,160,0.62)');
  pSpecular(x,y,r,0.15,0.40);
  ctx.restore();
}

/* ================================================================
   EARTH — photorealistic satellite view + city lights
   ================================================================ */
var _cityBuilt=false, _cityR=0, CITY_DOTS=[];
var CITY_CLUSTERS=[
  [-0.38,-0.18,isMobile?90:160,0.13,255,205,120],
  [-0.48,-0.12,isMobile?40:72,0.09,255,190,100],
  [-0.56,-0.08,isMobile?30:55,0.07,255,195,110],
  [-0.08,-0.28,isMobile?85:150,0.11,255,215,135],
  [ 0.06,-0.26,isMobile?32:56,0.07,255,205,125],
  [ 0.52,-0.18,isMobile?48:85,0.07,255,225,145],
  [ 0.44,-0.10,isMobile?52:95,0.09,255,215,130],
  [ 0.28, 0.08,isMobile?38:65,0.08,255,200,118],
  [ 0.46, 0.18,isMobile?26:46,0.06,255,205,120],
];
function rebuildCityDots(x,y,r){
  CITY_DOTS=[]; _cityR=r;
  for(var ci=0;ci<CITY_CLUSTERS.length;ci++){
    var cl=CITY_CLUSTERS[ci];
    var ox=cl[0],oy=cl[1],dn=cl[2],sp=cl[3];
    var R=cl[4],G=cl[5],B=cl[6];
    var cx2=x+ox*r, cy2=y+oy*r;
    var nf=Math.max(0,Math.min(1,(-ox+0.08)*3.5));
    if(nf<=0.05) continue;
    for(var di=0;di<dn;di++){
      var ang=Math.random()*Math.PI*2;
      var dist=Math.random()*sp*r;
      var dx=cx2+Math.cos(ang)*dist, dy=cy2+Math.sin(ang)*dist;
      var ddx=dx-x,ddy=dy-y;
      if(ddx*ddx+ddy*ddy>r*r*0.94) continue;
      CITY_DOTS.push({x:dx,y:dy,sz:0.5+Math.random()*1.3,
        brightness:(0.40+Math.random()*0.55)*nf,
        ph:Math.random()*Math.PI*2,sp:0.0008+Math.random()*0.0012,R:R,G:G,B:B});
    }
  }
  _cityBuilt=true;
}
function drawCityLights(now){
  if(!_cityBuilt||!CITY_DOTS.length) return;
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<CITY_DOTS.length;i++){
    var d=CITY_DOTS[i];
    var fl=0.85+0.15*Math.sin(now*d.sp+d.ph), a=d.brightness*fl;
    ctx.globalAlpha=a*0.88;
    ctx.fillStyle='rgba('+d.R+','+d.G+','+d.B+',1)';
    ctx.beginPath(); ctx.arc(d.x,d.y,d.sz*0.55,0,Math.PI*2); ctx.fill();
    ctx.globalAlpha=a*0.28;
    var dg=ctx.createRadialGradient(d.x,d.y,0,d.x,d.y,d.sz*2.8);
    dg.addColorStop(0,'rgba('+d.R+','+d.G+','+d.B+',1)');
    dg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=dg; ctx.beginPath(); ctx.arc(d.x,d.y,d.sz*2.8,0,Math.PI*2); ctx.fill();
  }
  ctx.globalAlpha=1; ctx.restore();
}

function drawEarth(x,y,r,now){
  ctx.save();
  if(!_cityBuilt||Math.abs(_cityR-r)>1) rebuildCityDots(x,y,r);

  ctx.fillStyle='#000810';
  ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();

  /* ocean */
  ctx.globalCompositeOperation='source-over';
  var oc=ctx.createRadialGradient(x-r*0.15,y-r*0.12,r*0.04,x+r*0.20,y+r*0.20,r*1.05);
  oc.addColorStop(0,'#d0f0ff'); oc.addColorStop(0.05,'#60d0f0');
  oc.addColorStop(0.14,'#1e9ad8'); oc.addColorStop(0.30,'#0870b8');
  oc.addColorStop(0.50,'#044888'); oc.addColorStop(0.70,'#012258');
  oc.addColorStop(0.88,'#000e30'); oc.addColorStop(1,'#000610');
  ctx.fillStyle=oc; ctx.fillRect(0,0,W,H);

  function land(ox,oy,rx,R,G,B,a){
    var g=ctx.createRadialGradient(x+ox*r,y+oy*r,0,x+ox*r,y+oy*r,rx*r);
    g.addColorStop(0,'rgba('+R+','+G+','+B+','+a+')');
    g.addColorStop(0.38,'rgba('+R+','+G+','+B+','+(a*0.68).toFixed(2)+')');
    g.addColorStop(0.70,'rgba('+R+','+G+','+B+','+(a*0.26).toFixed(2)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  }
  land( 0.46, 0.26,0.24,198,58,8,0.99);  /* australia/asia dark red-brown */
  land( 0.55, 0.18,0.12,182,46,6,0.97);
  land( 0.60, 0.34,0.09, 62,118,36,0.90);
  land( 0.10,-0.05,0.23,196,150,64,0.93); /* africa */
  land( 0.14, 0.16,0.17,148,118,50,0.88);
  land( 0.15, 0.02,0.10, 40,105,32,0.86);
  land( 0.06,-0.14,0.12,215,172,80,0.88); /* europe */
  land( 0.24,-0.09,0.14,212,175,92,0.90);
  land( 0.06,-0.26,0.12, 64,136,46,0.84); /* north europe */
  land( 0.12,-0.35,0.09, 58,126,42,0.80);
  land( 0.34,-0.33,0.29, 74,138,50,0.80); /* north america */
  land( 0.48,-0.15,0.15, 88,148,54,0.82);
  land( 0.36, 0.02,0.12,128,158,60,0.84);
  land( 0.52, 0.02,0.10, 42,108,36,0.82);
  land( 0.30,-0.22,0.18,158,166,80,0.76);
  land(-.32,-0.31,0.22, 64,120,44,0.86);  /* south america */
  land(-.22, 0.16,0.15, 30, 95,30,0.92);
  land(-.30, 0.20,0.06,118, 98,52,0.80);
  land(-.10,-0.55,0.08,208,220,230,0.86); /* antarctic */

  /* coastal shimmer */
  ctx.globalCompositeOperation='screen';
  var cs=ctx.createRadialGradient(x+r*0.38,y+r*0.20,r*0.10,x+r*0.38,y+r*0.20,r*0.25);
  cs.addColorStop(0,'rgba(0,200,180,0.26)'); cs.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=cs; ctx.fillRect(0,0,W,H);

  /* ice caps */
  ctx.globalCompositeOperation='source-over';
  var ant=ctx.createRadialGradient(x,y+r*0.80,0,x,y+r*0.80,r*0.28);
  ant.addColorStop(0,'rgba(252,255,255,0.96)'); ant.addColorStop(0.55,'rgba(228,244,255,0.68)'); ant.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ant; ctx.fillRect(0,0,W,H);
  var np=ctx.createRadialGradient(x,y-r*0.78,0,x,y-r*0.78,r*0.21);
  np.addColorStop(0,'rgba(244,252,255,0.92)'); np.addColorStop(0.55,'rgba(222,242,255,0.60)'); np.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np; ctx.fillRect(0,0,W,H);

  /* clouds */
  ctx.globalCompositeOperation='screen';
  var cs2=now*0.000036;
  for(var ci=0;ci<14;ci++){
    var ca=cs2+ci*(Math.PI*2/14);
    var crad=r*(0.07+ci*0.015);
    var cx2=x+Math.cos(ca)*crad*0.54, cy2=y+Math.sin(ca)*crad*0.27;
    var csz=r*(0.12+Math.sin(ci*1.3)*0.050);
    var cg=ctx.createRadialGradient(cx2,cy2,0,cx2,cy2,csz);
    var ca2=0.16+0.14*Math.sin(ci*0.9+now*0.000009);
    cg.addColorStop(0,'rgba(255,255,255,'+ca2+')');
    cg.addColorStop(0.55,'rgba(240,248,255,'+(ca2*0.42).toFixed(3)+')');
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cg; ctx.fillRect(0,0,W,H);
  }

  drawCityLights(now);

  /* night terminator */
  ctx.globalAlpha=1; ctx.globalCompositeOperation='multiply';
  var nt=ctx.createLinearGradient(x-r*0.05,y,x+r*0.50,y);
  nt.addColorStop(0,'rgba(0,0,0,0)'); nt.addColorStop(0.28,'rgba(0,4,18,0.16)');
  nt.addColorStop(0.56,'rgba(0,4,18,0.66)'); nt.addColorStop(0.76,'rgba(0,2,10,0.90)');
  nt.addColorStop(1,'rgba(0,0,0,0.97)');
  ctx.fillStyle=nt; ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.globalAlpha=1;
  ctx.restore();

  /* atmosphere — thin blue rim (จริง) */
  ctx.globalCompositeOperation='screen';
  var atm=ctx.createRadialGradient(x,y,r*0.88,x,y,r*1.22);
  atm.addColorStop(0,'rgba(80,140,255,0.20)');
  atm.addColorStop(0.35,'rgba(60,110,220,0.08)');
  atm.addColorStop(0.65,'rgba(40,80,180,0.03)');
  atm.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm; ctx.fillRect(0,0,W,H);

  pSpecular(x,y,r,0.25,0.34);
  pTerminator(x,y,r,0.70);
  pRimLight(x,y,r,'rgba(100,160,255,0.52)');
  ctx.globalAlpha=1; ctx.restore();
}

/* ================================================================
   MOON — สีเทาจริง ไม่มีสีแฟนตาซี
   ================================================================ */
function drawMoon(ep,now){
  var mr=getR(PLANETS[2])*0.27;
  var ma=now*0.000116;
  var md=getR(PLANETS[2])*1.88;
  var mx=ep.x+Math.cos(ma)*md, my=ep.y+Math.sin(ma)*md*0.38;
  ctx.save();
  pSphere(mx,my,mr,[
    [0,'#ece8e0'],[0.18,'#d0c8b8'],[0.45,'#a09888'],
    [0.72,'#6e6458'],[1,'#2c2418']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(mx,my,mr,0,Math.PI*2); ctx.clip();
  [[0.20,0.15,0.15,0.48],[-0.18,0.22,0.12,0.44],[0.05,-0.20,0.14,0.46],
   [-0.06,0.04,0.07,0.40],[0.28,-0.12,0.09,0.44]].forEach(function(c){
    var g=ctx.createRadialGradient(mx+c[0]*mr,my+c[1]*mr,0,mx+c[0]*mr,my+c[1]*mr,c[2]*mr);
    g.addColorStop(0,'rgba(12,8,4,'+c[3]+')');
    g.addColorStop(0.5,'rgba(20,14,8,'+(c[3]*0.45).toFixed(3)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply'; ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pTerminator(mx,my,mr,0.80);
  pRimLight(mx,my,mr,'rgba(200,190,175,0.38)');
  pSpecular(mx,my,mr,0.09,0.36);
  ctx.restore();
}

/* ================================================================
   MARS — สีแดงอมส้มจริง
   ================================================================ */
function drawMars(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#f4b090'],[0.12,'#d86840'],[0.30,'#b04020'],
    [0.55,'#7a2408'],[0.78,'#480e02'],[1,'#220400']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='overlay';
  [[0.16,-0.14,0.30,0.26],[-.12,0.20,0.22,0.20],[0.28,0.08,0.16,0.18]].forEach(function(c){
    var g=ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0,x+c[0]*r,y+c[1]*r,c[2]*r);
    g.addColorStop(0,'rgba(175,70,35,'+c[3]+')'); g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  /* polar ice */
  var pc=ctx.createRadialGradient(x,y-r*0.78,0,x,y-r*0.78,r*0.19);
  pc.addColorStop(0,'rgba(238,238,248,0.90)'); pc.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=pc; ctx.globalCompositeOperation='source-over'; ctx.fillRect(0,0,W,H);
  /* thin atmosphere */
  ctx.globalCompositeOperation='screen';
  var ma2=ctx.createRadialGradient(x,y,r*0.90,x,y,r*1.18);
  ma2.addColorStop(0,'rgba(220,120,60,0.09)');
  ma2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ma2; ctx.fillRect(0,0,W,H);
  pTerminator(x,y,r,0.76);
  pRimLight(x,y,r,'rgba(255,160,90,0.48)');
  pSpecular(x,y,r,0.10,0.37);
  ctx.restore();
}

/* ================================================================
   JUPITER — สีน้ำตาลทองแถบสีจริง + Great Red Spot
   ================================================================ */
function drawJupiter(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#f4e8c8'],[0.10,'#d8b870'],[0.25,'#bc8840'],
    [0.48,'#9a6028'],[0.70,'#6e3c10'],[1,'#381800']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='overlay';
  var jSpin=now*0.0000052;
  for(var bi=0;bi<11;bi++){
    var by=y-r*0.90+bi*r*0.185+Math.sin(jSpin+bi*0.65)*r*0.016;
    var ba=0.10+0.13*Math.abs(Math.sin(bi*0.52+jSpin));
    var jg=ctx.createLinearGradient(x-r,by,x+r,by+r*0.04);
    var c1=bi%3===0?'rgba(155,75,38,'+ba+')':bi%3===1?'rgba(195,135,65,'+ba+')':'rgba(135,95,55,'+ba+')';
    var c2=bi%3===0?'rgba(115,45,18,'+ba+')':bi%3===1?'rgba(175,105,45,'+ba+')':'rgba(95,65,35,'+ba+')';
    jg.addColorStop(0,'rgba(0,0,0,0)');jg.addColorStop(0.22,c1);
    jg.addColorStop(0.50,c2);jg.addColorStop(0.78,c1);jg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=jg; ctx.fillRect(x-r,by,r*2,r*0.152);
  }
  /* Great Red Spot */
  var gs=ctx.createRadialGradient(x+r*0.22,y+r*0.14,0,x+r*0.22,y+r*0.14,r*0.13);
  gs.addColorStop(0,'rgba(180,45,25,0.75)');
  gs.addColorStop(0.45,'rgba(145,35,18,0.42)');
  gs.addColorStop(1,'rgba(0,0,0,0)');
  ctx.globalCompositeOperation='overlay'; ctx.fillStyle=gs; ctx.fillRect(0,0,W,H);
  ctx.restore();
  pTerminator(x,y,r,0.60);
  pRimLight(x,y,r,'rgba(255,215,155,0.45)');
  pSpecular(x,y,r,0.13,0.48);
  ctx.restore();
}

/* ================================================================
   SATURN — สีเหลืองทองอมเทา + วงแหวนจริง
   ================================================================ */
function drawSaturn(x,y,r,now){
  ctx.save();

  /* ring shadow on planet */
  ctx.globalCompositeOperation='multiply';
  var rs=ctx.createLinearGradient(x-r*1.8,y-r*0.10,x+r*1.8,y+r*0.10);
  rs.addColorStop(0,'rgba(0,0,0,0)'); rs.addColorStop(0.30,'rgba(0,0,0,0.12)');
  rs.addColorStop(0.70,'rgba(0,0,0,0.12)'); rs.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=rs; ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
  ctx.globalCompositeOperation='source-over';

  /* planet body */
  pSphere(x,y,r,[
    [0,'#f8f0c0'],[0.10,'#e8d880'],[0.25,'#d0b848'],
    [0.48,'#aa8828'],[0.70,'#7a5c0e'],[1,'#3c2800']
  ]);

  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='overlay';
  var sSpin=now*0.0000038;
  for(var si=0;si<8;si++){
    var sy2=y-r*0.85+si*r*0.24+Math.sin(sSpin+si*0.8)*r*0.012;
    var sa=0.08+0.10*Math.abs(Math.sin(si*0.60+sSpin));
    var sg2=ctx.createLinearGradient(x-r,sy2,x+r,sy2+r*0.04);
    sg2.addColorStop(0,'rgba(0,0,0,0)');
    sg2.addColorStop(0.30,'rgba(180,140,50,'+sa+')');
    sg2.addColorStop(0.70,'rgba(150,110,30,'+sa+')');
    sg2.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sg2; ctx.fillRect(x-r,sy2,r*2,r*0.18);
  }
  ctx.restore();

  /* rings — back half (วาดก่อนดาว) */
  ctx.save(); ctx.globalCompositeOperation='screen';
  var ringTilt=0.28;

  /* ring system: D,C,B,Cassini,A,F */
  var rings=[
    {ri:1.24, ro:1.44, R:200,G:185,B:150, a:0.32},  /* C ring */
    {ri:1.44, ro:1.82, R:220,G:205,B:170, a:0.56},  /* B ring (brightest) */
    {ri:1.82, ro:1.86, R:60, G:55, B:45,  a:0.18},  /* Cassini division */
    {ri:1.86, ro:2.18, R:210,G:195,B:162, a:0.48},  /* A ring */
    {ri:2.18, ro:2.22, R:180,G:165,B:140, a:0.28},  /* F ring */
  ];

  for(var ri2=0;ri2<rings.length;ri2++){
    var rng=rings[ri2];
    var innerR=r*rng.ri, outerR=r*rng.ro;
    var rg=ctx.createLinearGradient(x-outerR,y,x+outerR,y);
    rg.addColorStop(0,'rgba(0,0,0,0)');
    rg.addColorStop(0.06,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.5).toFixed(3)+')');
    rg.addColorStop(0.32,'rgba('+rng.R+','+rng.G+','+rng.B+','+rng.a+')');
    rg.addColorStop(0.50,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.7).toFixed(3)+')');
    rg.addColorStop(0.68,'rgba('+rng.R+','+rng.G+','+rng.B+','+rng.a+')');
    rg.addColorStop(0.94,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.5).toFixed(3)+')');
    rg.addColorStop(1,'rgba(0,0,0,0)');

    /* back half */
    ctx.beginPath();
    ctx.ellipse(x,y,outerR,outerR*ringTilt,0,Math.PI,Math.PI*2);
    ctx.ellipse(x,y,innerR,innerR*ringTilt,0,Math.PI*2,Math.PI,true);
    ctx.fillStyle=rg; ctx.fill();
  }
  ctx.restore();

  pTerminator(x,y,r,0.60);
  pRimLight(x,y,r,'rgba(255,240,160,0.52)');
  pSpecular(x,y,r,0.16,0.46);

  /* rings — front half */
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var ri3=0;ri3<rings.length;ri3++){
    var rng2=rings[ri3];
    var innerR2=r*rng2.ri, outerR2=r*rng2.ro;
    var rg2=ctx.createLinearGradient(x-outerR2,y,x+outerR2,y);
    rg2.addColorStop(0,'rgba(0,0,0,0)');
    rg2.addColorStop(0.06,'rgba('+rng2.R+','+rng2.G+','+rng2.B+','+(rng2.a*0.5).toFixed(3)+')');
    rg2.addColorStop(0.32,'rgba('+rng2.R+','+rng2.G+','+rng2.B+','+rng2.a+')');
    rg2.addColorStop(0.50,'rgba('+rng2.R+','+rng2.G+','+rng2.B+','+(rng2.a*0.7).toFixed(3)+')');
    rg2.addColorStop(0.68,'rgba('+rng2.R+','+rng2.G+','+rng2.B+','+rng2.a+')');
    rg2.addColorStop(0.94,'rgba('+rng2.R+','+rng2.G+','+rng2.B+','+(rng2.a*0.5).toFixed(3)+')');
    rg2.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();
    ctx.ellipse(x,y,outerR2,outerR2*ringTilt,0,0,Math.PI);
    ctx.ellipse(x,y,innerR2,innerR2*ringTilt,0,Math.PI,0,true);
    ctx.fillStyle=rg2; ctx.fill();
  }
  ctx.restore();
  ctx.restore();
}

/* ================================================================
   PLUTO — สีเทาอมน้ำตาลแดงจริง (ข้อมูล New Horizons 2015)
   ================================================================ */
function drawPluto(x,y,r,now){
  ctx.save();
  pSphere(x,y,r,[
    [0,'#d8c8b0'],[0.20,'#b8a080'],[0.45,'#8a6848'],
    [0.70,'#5c3c22'],[1,'#281408']
  ]);
  ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
  /* Tombaugh Regio (heart region — lighter) */
  var tr=ctx.createRadialGradient(x-r*0.10,y+r*0.08,0,x-r*0.10,y+r*0.08,r*0.45);
  tr.addColorStop(0,'rgba(220,200,175,0.60)');
  tr.addColorStop(0.5,'rgba(200,175,145,0.30)');
  tr.addColorStop(1,'rgba(0,0,0,0)');
  ctx.globalCompositeOperation='screen'; ctx.fillStyle=tr; ctx.fillRect(0,0,W,H);
  ctx.restore();
  pTerminator(x,y,r,0.80);
  pRimLight(x,y,r,'rgba(190,165,140,0.35)');
  pSpecular(x,y,r,0.08,0.34);
  ctx.restore();
}

/* ================================================================
   RENDER
   ================================================================ */
function render(dt,now){
  drawBg(now);
  drawStars(now);
  drawSun(now);
  for(var i=0;i<PLANETS.length;i++) drawOrbitRing(PLANETS[i]);
  _cache=[];
  for(var j=0;j<PLANETS.length;j++){
    var p=PLANETS[j];
    var pos=planetPos(p,now);
    _cache.push(pos);
    var r=getR(p);
    if(p.route&&p.route===activeRoute) pActive(pos.x,pos.y,r,now);
    p.draw(pos.x,pos.y,r,now);
    if(p.moon) drawMoon(pos,now);
    drawLabel(p,pos);
  }
}

/* ================================================================
   PUBLIC API — unchanged interface
   ================================================================ */
window.KD_setRoute=function(route){
  activeRoute=route;
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
