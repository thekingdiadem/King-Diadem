/* ================================================================
   KING DIADEM — Galaxy Scene v53 MINIMAL SOVEREIGN
   เรียบง่าย ลื่นไหล ไม่อ้างว่าเป็นภาพถ่ายดาวเทียม
   สื่อ Waterline / Drift / Route ด้วยภาพนามธรรมที่สวยและจริงใจ
   Performance-first: เบามาก รันลื่นทุกอุปกรณ์
   ================================================================ */
(function(){
'use strict';

var cv = document.getElementById('galaxy');
if (!cv) return;
var ctx = cv.getContext('2d', {alpha:true, desynchronized:true});
var W=0, H=0, _raf=null, _last=0;
var activeRoute = 'general';
var isMobile = false;

var ROUTE_COLOR = {
  general:  {h:42,  s:65, l:62},  /* gold */
  risk:     {h:18,  s:75, l:58},  /* amber-red */
  survival: {h:205, s:70, l:58},  /* blue */
  collapse: {h:0,   s:65, l:55},  /* red */
  civil:    {h:265, s:55, l:62},  /* purple */
  vega:     {h:235, s:60, l:62},  /* deep blue */
};
var _curHue=42, _tgtHue=42;
var _burstAlpha=0;

function loop(now){
  if(!window.KD||window.KD.visible!==false){
    _raf = requestAnimationFrame(loop);
  } else { _raf=null; return; }
  render(now);
  _last=now;
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
  var d=e.detail||{};
  var route=d.consensus&&d.consensus.final_action;
  if(route&&ROUTE_COLOR[route]) _tgtHue=ROUTE_COLOR[route].h;
  var risk=d.risk&&d.risk.risk_score;
  if(risk>75) _burstAlpha=0.14;
  else if(risk>45) _burstAlpha=0.07;
},{passive:true});
window.addEventListener('KD:decision',function(e){
  var route=e.detail&&e.detail.route;
  if(route){ activeRoute=route; if(ROUTE_COLOR[route]) _tgtHue=ROUTE_COLOR[route].h; }
},{passive:true});

/* ================================================================
   STARFIELD — เบา สวย จริงใจ
   ================================================================ */
var STARS=[];
function buildStars(){
  STARS=[];
  var total=isMobile?180:380;
  for(var i=0;i<total;i++){
    var sz=Math.random();
    var tier=sz<0.65?0:sz<0.88?1:2;
    var r=[0.20+Math.random()*0.25,0.40+Math.random()*0.45,0.65+Math.random()*0.85][tier];
    var a=[0.15+Math.random()*0.40,0.28+Math.random()*0.48,0.45+Math.random()*0.55][tier];
    STARS.push({x:Math.random()*W,y:Math.random()*H,r:r,a:a,
      tw:Math.random()<0.50,ph:Math.random()*Math.PI*2,sp:0.10+Math.random()*0.45});
  }
}

function drawStars(now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var a=s.tw?s.a*(0.35+0.65*Math.sin(now*s.sp*0.00045+s.ph)):s.a;
    ctx.beginPath(); ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fillStyle='rgba(225,232,250,'+a.toFixed(3)+')'; ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   BACKGROUND — deep void, subtle warmth
   ================================================================ */
function drawBg(){
  var bg=ctx.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,'#07060f'); bg.addColorStop(0.5,'#050410'); bg.addColorStop(1,'#03030a');
  ctx.fillStyle=bg; ctx.fillRect(0,0,W,H);

  ctx.save(); ctx.globalCompositeOperation='screen';
  /* subtle warm glow bottom-left, cool glow top-right — cosmic latte / blue-purple */
  var g1=ctx.createRadialGradient(W*0.08,H*0.92,0,W*0.08,H*0.92,W*0.55);
  g1.addColorStop(0,'rgba(180,140,90,0.10)'); g1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g1; ctx.fillRect(0,0,W,H);

  var g2=ctx.createRadialGradient(W*0.85,H*0.10,0,W*0.85,H*0.10,W*0.45);
  g2.addColorStop(0,'rgba(90,100,200,0.08)'); g2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g2; ctx.fillRect(0,0,W,H);

  if(_burstAlpha>0.002){
    _burstAlpha*=0.96;
    var bst=ctx.createRadialGradient(W*0.5,H*0.5,0,W*0.5,H*0.5,W*0.6);
    bst.addColorStop(0,'hsla('+_curHue+',70%,55%,'+_burstAlpha.toFixed(3)+')');
    bst.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=bst; ctx.fillRect(0,0,W,H);
  }
  ctx.restore();
}

/* ================================================================
   CORE — central living sphere representing the system itself
   ไม่อ้างเป็นโลก/ดาวเคราะห์จริง — เป็น "แก่นกลาง" ของระบบ
   เปลี่ยนสีตาม active route, เคลื่อนไหวด้วย Waterline values
   ================================================================ */
function coreCX(){ return W*0.50; }
function coreCY(){ return H*0.46; }
function coreR(){  return Math.min(W,H)*(isMobile?0.20:0.17); }

function drawCore(now){
  var cx=coreCX(), cy=coreCY(), r=coreR();
  _curHue += (_tgtHue-_curHue)*0.02;

  var waterline = (window.KD&&window.KD.state&&window.KD.state.stability)||60;
  var entropy   = (window.KD&&window.KD.state&&window.KD.state.entropy)||40;

  var pulse = 1 + Math.sin(now*0.0009)*0.018;
  var rr = r*pulse;

  ctx.save();

  /* outer atmosphere glow */
  ctx.globalCompositeOperation='screen';
  var glow=ctx.createRadialGradient(cx,cy,rr*0.7,cx,cy,rr*1.9);
  glow.addColorStop(0,'hsla('+_curHue+',60%,60%,0.30)');
  glow.addColorStop(0.5,'hsla('+_curHue+',55%,50%,0.10)');
  glow.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=glow; ctx.fillRect(0,0,W,H);

  /* core sphere — layered gradient, no fake "photo" claim */
  ctx.globalCompositeOperation='source-over';
  var body=ctx.createRadialGradient(cx-rr*0.30,cy-rr*0.26,rr*0.05,cx+rr*0.10,cy+rr*0.12,rr*1.05);
  body.addColorStop(0,'hsla('+_curHue+',45%,88%,1)');
  body.addColorStop(0.18,'hsla('+_curHue+',55%,68%,1)');
  body.addColorStop(0.42,'hsla('+_curHue+',58%,46%,1)');
  body.addColorStop(0.70,'hsla('+(_curHue+8)+',55%,26%,1)');
  body.addColorStop(0.90,'hsla('+(_curHue+12)+',50%,14%,1)');
  body.addColorStop(1,'hsla('+(_curHue+14)+',45%,6%,1)');
  ctx.fillStyle=body;
  ctx.beginPath(); ctx.arc(cx,cy,rr,0,Math.PI*2); ctx.fill();

  /* internal flowing lines — representing decision flow, not geography */
  ctx.save(); ctx.beginPath(); ctx.arc(cx,cy,rr,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='screen';
  for(var li=0;li<5;li++){
    var lt = now*0.00006 + li*1.3;
    var ly = cy - rr*0.7 + (li/5)*rr*1.4;
    var amp = rr*0.18*Math.sin(lt*0.6+li);
    ctx.beginPath();
    for(var lx=cx-rr;lx<=cx+rr;lx+=4){
      var yy = ly + Math.sin((lx-cx)*0.012+lt)*amp*0.3;
      if(lx===cx-rr) ctx.moveTo(lx,yy); else ctx.lineTo(lx,yy);
    }
    ctx.strokeStyle='hsla('+(_curHue+li*6)+',60%,70%,'+(0.06+0.03*Math.sin(lt))+')';
    ctx.lineWidth=rr*0.025;
    ctx.stroke();
  }
  ctx.restore();

  /* specular highlight */
  ctx.globalCompositeOperation='screen';
  var sp=ctx.createRadialGradient(cx-rr*0.26,cy-rr*0.22,0,cx-rr*0.08,cy-rr*0.06,rr*0.45);
  sp.addColorStop(0,'rgba(255,255,255,0.38)');
  sp.addColorStop(0.4,'rgba(255,255,255,0.08)');
  sp.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=sp; ctx.beginPath(); ctx.arc(cx,cy,rr,0,Math.PI*2); ctx.fill();

  /* rim light */
  var rim=ctx.createRadialGradient(cx,cy,rr*0.92,cx,cy,rr*1.06);
  rim.addColorStop(0,'hsla('+_curHue+',70%,70%,0.45)');
  rim.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=rim; ctx.fillRect(0,0,W,H);

  /* limb darkening */
  ctx.globalCompositeOperation='multiply';
  var ld=ctx.createRadialGradient(cx-rr*0.10,cy-rr*0.08,rr*0.60,cx,cy,rr*1.02);
  ld.addColorStop(0,'rgba(0,0,0,0)');
  ld.addColorStop(0.75,'rgba(0,0,10,0.18)');
  ld.addColorStop(1,'rgba(0,0,8,0.42)');
  ctx.fillStyle=ld; ctx.beginPath(); ctx.arc(cx,cy,rr*1.02,0,Math.PI*2); ctx.fill();

  ctx.restore();

  /* center label */
  ctx.save();
  ctx.font='600 '+(isMobile?9:11)+'px "DM Mono",monospace';
  ctx.fillStyle='rgba(255,255,255,0.55)';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  ctx.fillText('KING DIADEM',cx,cy);
  ctx.font='400 '+(isMobile?7:8)+'px "DM Mono",monospace';
  ctx.fillStyle='hsla('+_curHue+',60%,72%,0.65)';
  ctx.fillText((activeRoute||'GENERAL').toUpperCase(),cx,cy+(isMobile?14:17));
  ctx.restore();
}

/* ================================================================
   ORBIT RINGS — route indicators, ไม่ใช่ดาวเคราะห์จริง
   เส้นวงโคจรเรียบง่าย + จุดนำทางตาม route
   ================================================================ */
var ORBIT_ROUTES=[
  {route:'general', lbl:'GENERAL', orb:0.30, per:8,  ao:0.0},
  {route:'risk',    lbl:'RISK',    orb:0.38, per:11, ao:1.3},
  {route:'survival',lbl:'SURVIVAL',orb:0.46, per:14, ao:2.6},
  {route:'collapse',lbl:'COLLAPSE',orb:0.54, per:17, ao:3.9},
  {route:'civil',   lbl:'CIVIL',   orb:0.62, per:20, ao:5.2},
  {route:'vega',    lbl:'VEGA',    orb:0.70, per:24, ao:0.7},
];

var _ringCache=[];
function ringPos(rt,now){
  var cx=coreCX(), cy=coreCY();
  var R=Math.min(W,H)*rt.orb;
  var tilt=0.20;
  var angle=(now*0.00002/rt.per*10 + rt.ao)%(Math.PI*2);
  return {x:cx+Math.cos(angle)*R, y:cy+Math.sin(angle)*R*tilt, R:R, tilt:tilt};
}

function drawOrbits(now){
  var cx=coreCX(), cy=coreCY();
  ctx.save(); ctx.globalCompositeOperation='screen';
  _ringCache=[];

  ORBIT_ROUTES.forEach(function(rt){
    var R=Math.min(W,H)*rt.orb, tilt=0.20;
    var isAct=rt.route===activeRoute;
    var col=ROUTE_COLOR[rt.route]||ROUTE_COLOR.general;

    /* orbit line */
    ctx.strokeStyle=isAct
      ? 'hsla('+col.h+','+col.s+'%,'+col.l+'%,0.45)'
      : 'rgba(160,170,210,0.07)';
    ctx.lineWidth=isAct?1.4:0.5;
    if(!isAct){ ctx.setLineDash([2,6]); }
    ctx.beginPath(); ctx.ellipse(cx,cy,R,R*tilt,0,0,Math.PI*2); ctx.stroke();
    ctx.setLineDash([]);

    /* node */
    var pos=ringPos(rt,now);
    _ringCache.push({x:pos.x,y:pos.y,route:rt.route});
    var nodeR=isAct?(isMobile?7:9):(isMobile?4:5);

    if(isAct){
      var ng=ctx.createRadialGradient(pos.x,pos.y,0,pos.x,pos.y,nodeR*3);
      ng.addColorStop(0,'hsla('+col.h+','+col.s+'%,'+col.l+'%,0.55)');
      ng.addColorStop(1,'rgba(0,0,0,0)');
      ctx.fillStyle=ng; ctx.beginPath(); ctx.arc(pos.x,pos.y,nodeR*3,0,Math.PI*2); ctx.fill();
    }

    var nodeGrad=ctx.createRadialGradient(pos.x-nodeR*0.3,pos.y-nodeR*0.3,0,pos.x,pos.y,nodeR);
    nodeGrad.addColorStop(0,'hsla('+col.h+',60%,85%,1)');
    nodeGrad.addColorStop(0.6,'hsla('+col.h+','+col.s+'%,'+col.l+'%,1)');
    nodeGrad.addColorStop(1,'hsla('+col.h+',50%,28%,1)');
    ctx.fillStyle=nodeGrad;
    ctx.beginPath(); ctx.arc(pos.x,pos.y,nodeR,0,Math.PI*2); ctx.fill();

    /* label */
    ctx.font=(isAct?'600 ':'500 ')+(isMobile?7:9)+'px "DM Mono",monospace';
    ctx.textAlign='center'; ctx.textBaseline='top';
    if(isAct){
      ctx.shadowColor='hsla('+col.h+','+col.s+'%,'+col.l+'%,0.7)'; ctx.shadowBlur=6;
      ctx.fillStyle='hsla('+col.h+',55%,88%,0.95)';
    } else {
      ctx.fillStyle='rgba(170,176,205,0.32)';
    }
    ctx.fillText(rt.lbl,pos.x,pos.y+nodeR+4);
    ctx.shadowBlur=0;
  });

  ctx.restore();
}

/* click → route select */
cv.addEventListener('click',function(e){
  var rc=cv.getBoundingClientRect(), mx=e.clientX-rc.left, my=e.clientY-rc.top;
  for(var i=0;i<_ringCache.length;i++){
    var p=_ringCache[i];
    var dx=mx-p.x, dy=my-p.y;
    var hitR=(isMobile?16:20);
    if(dx*dx+dy*dy<hitR*hitR) window.KD_setRoute&&window.KD_setRoute(p.route);
  }
},{passive:true});
cv.addEventListener('touchend',function(e){
  if(e.changedTouches.length===1){
    var t=e.changedTouches[0];
    cv.dispatchEvent(new MouseEvent('click',{clientX:t.clientX,clientY:t.clientY}));
  }
},{passive:true});

/* ================================================================
   AMBIENT PARTICLES — drift slowly, representing decision traces
   ================================================================ */
var PARTICLES=[];
function buildParticles(){
  PARTICLES=[];
  var n=isMobile?12:24;
  for(var i=0;i<n;i++){
    PARTICLES.push({
      x:Math.random()*W, y:Math.random()*H,
      vx:(Math.random()-0.5)*0.012, vy:(Math.random()-0.5)*0.012,
      r:0.6+Math.random()*1.2, a:0.08+Math.random()*0.18,
      ph:Math.random()*Math.PI*2
    });
  }
}

function drawParticles(now,dt){
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<PARTICLES.length;i++){
    var p=PARTICLES[i];
    p.x+=p.vx*dt; p.y+=p.vy*dt;
    if(p.x<0)p.x=W; if(p.x>W)p.x=0; if(p.y<0)p.y=H; if(p.y>H)p.y=0;
    var a=p.a*(0.5+0.5*Math.sin(now*0.0006+p.ph));
    ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
    ctx.fillStyle='hsla('+_curHue+',50%,75%,'+a.toFixed(3)+')'; ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   RENDER
   ================================================================ */
var _lastFrame=0;
function render(now){
  var dt=Math.min(now-_lastFrame,50); _lastFrame=now;
  drawBg();
  drawStars(now);
  drawParticles(now,dt);
  drawOrbits(now);
  drawCore(now);
}

/* ================================================================
   PUBLIC API
   ================================================================ */
window.KD_setRoute=function(route){
  activeRoute=route;
  if(ROUTE_COLOR[route]) _tgtHue=ROUTE_COLOR[route].h;
  if(typeof window.setRoute==='function') window.setRoute(route);
  window.dispatchEvent(new CustomEvent('KD:routeChange',{detail:{route:route}}));
};
window.KD_pulse = window.KD_pulse || function(route){ if(route) window.KD_setRoute(route); };
window.KD_setState = window.KD_setState || function(key,val){
  if(!window.KD) window.KD={};
  if(!window.KD.state) window.KD.state={};
  window.KD.state[key]=val;
};

doResize();
buildParticles();
_last=performance.now();
_lastFrame=_last;
_raf=requestAnimationFrame(loop);

})();
