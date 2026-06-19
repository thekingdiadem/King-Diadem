<!DOCTYPE html>
<html lang="th">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>KING DIADEM — Galaxy Screen</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&family=DM+Mono:wght@300;400;500&display=swap">
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
html,body{width:100%;height:100%;overflow:hidden;background:#020409;}
canvas{display:block;position:fixed;inset:0;width:100%;height:100%;}

/* ── HUD OVERLAY ── */
#hud{
  position:fixed;inset:0;pointer-events:none;z-index:10;
  font-family:'DM Mono',monospace;
}

/* Top bar */
#topbar{
  position:absolute;top:0;left:0;right:0;height:48px;
  display:flex;align-items:center;justify-content:space-between;
  padding:0 20px;
  background:linear-gradient(to bottom,rgba(2,4,9,0.85),rgba(2,4,9,0));
  border-bottom:1px solid rgba(200,168,75,0.08);
}
.tb-brand{
  display:flex;align-items:center;gap:10px;
}
.tb-crown{
  width:22px;height:22px;border-radius:5px;
  border:1px solid rgba(200,168,75,0.40);
  background:rgba(200,168,75,0.10);
  display:flex;align-items:center;justify-content:center;
  font-size:11px;
  box-shadow:0 0 10px rgba(200,168,75,0.20);
}
.tb-title{
  font-family:'Cinzel',serif;font-size:11px;letter-spacing:.18em;
  background:linear-gradient(135deg,#78bcff,#e8cc7a);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
}
.tb-right{display:flex;gap:10px;align-items:center;}
.tb-badge{
  font-size:7px;letter-spacing:.12em;padding:3px 8px;border-radius:3px;
  border:1px solid;text-transform:uppercase;
}
.tb-badge.ok {border-color:rgba(80,220,160,0.35);color:rgba(80,220,160,0.85);background:rgba(80,220,160,0.06);}
.tb-badge.off{border-color:rgba(255,74,110,0.35);color:rgba(255,74,110,0.70);background:rgba(255,74,110,0.06);}
#tb-time{font-size:9px;color:rgba(200,168,75,0.40);}

/* Waterline float */
#wl-float{
  position:absolute;top:56px;right:16px;
  display:flex;flex-direction:column;gap:3px;align-items:flex-end;
}
.wl-dot{
  font-size:7px;letter-spacing:.14em;
  padding:3px 10px;border-radius:999px;
  border:1px solid rgba(74,158,255,0.20);
  background:rgba(2,4,9,0.65);
  backdrop-filter:blur(8px);
  color:rgba(120,188,255,0.65);
}
.wl-dot.warn{border-color:rgba(240,168,20,0.30);color:rgba(240,168,20,0.75);}
.wl-dot.crit{border-color:rgba(255,74,110,0.35);color:rgba(255,100,130,0.80);animation:critBlink .9s ease-in-out infinite;}
@keyframes critBlink{0%,100%{opacity:.6;}50%{opacity:1;}}

/* LYLA float */
#lyla-float{
  position:absolute;top:56px;left:16px;
  font-size:7px;letter-spacing:.14em;
  padding:3px 10px;border-radius:999px;
  border:1px solid rgba(200,168,75,0.22);
  background:rgba(2,4,9,0.65);
  backdrop-filter:blur(8px);
  color:rgba(220,190,100,0.60);
}

/* Route pills */
#route-pills{
  position:absolute;bottom:72px;left:50%;transform:translateX(-50%);
  display:flex;gap:6px;flex-wrap:wrap;justify-content:center;
  pointer-events:all;
  padding:0 16px;
}
.rpill{
  font-size:8px;letter-spacing:.12em;padding:6px 14px;border-radius:999px;
  border:1px solid rgba(74,158,255,0.16);
  background:rgba(2,4,9,0.60);
  color:rgba(100,150,220,0.55);
  cursor:pointer;transition:all .18s;
  backdrop-filter:blur(8px);
}
.rpill:hover{border-color:rgba(200,168,75,0.40);color:rgba(220,190,100,0.90);background:rgba(200,168,75,0.08);}
.rpill.active{
  border-color:rgba(200,168,75,0.55);
  color:rgba(232,204,122,0.95);
  background:rgba(200,168,75,0.14);
  box-shadow:0 0 14px rgba(200,168,75,0.18);
}

/* HUD bottom bar */
#hud-bottom{
  position:absolute;bottom:0;left:0;right:0;height:52px;
  display:flex;align-items:center;justify-content:center;gap:20px;
  background:linear-gradient(to top,rgba(2,4,9,0.90),rgba(2,4,9,0));
  padding:0 20px;
}
.hud-stat{
  display:flex;flex-direction:column;align-items:center;gap:2px;
}
.hud-stat-k{font-size:6px;letter-spacing:.16em;color:rgba(100,130,200,0.40);text-transform:uppercase;}
.hud-stat-v{font-size:11px;font-weight:400;color:rgba(160,200,255,0.80);}
.hud-stat-v.gold{color:rgba(220,190,100,0.85);}
.hud-stat-v.warn{color:rgba(240,168,20,0.90);}
.hud-stat-v.crit{color:rgba(255,90,120,0.95);}

/* Intro overlay */
#intro{
  position:fixed;inset:0;z-index:50;
  display:flex;flex-direction:column;align-items:center;justify-content:center;
  background:rgba(2,4,9,1);
  transition:opacity 1.2s ease;
}
#intro.fade{opacity:0;pointer-events:none;}
.intro-title{
  font-family:'Cinzel',serif;font-size:clamp(22px,5vw,40px);
  letter-spacing:.14em;
  background:linear-gradient(135deg,#ffffff,#c8a84b);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
  margin-bottom:6px;
}
.intro-sub{font-size:9px;letter-spacing:.28em;color:rgba(74,158,255,0.50);margin-bottom:28px;}
.intro-bar{width:180px;height:1px;background:rgba(255,255,255,0.06);border-radius:1px;overflow:hidden;}
.intro-fill{height:100%;background:linear-gradient(90deg,#4a9eff,#c8a84b);width:0;transition:width 2.2s ease;}
.intro-tagline{margin-top:16px;font-size:8px;letter-spacing:.20em;color:rgba(140,170,220,0.35);}

/* Ctx tags */
#ctx-tags{
  position:absolute;top:56px;left:50%;transform:translateX(-50%);
  display:flex;gap:6px;
  pointer-events:all;
}
.ctx-tag{
  font-size:8px;letter-spacing:.10em;padding:4px 12px;border-radius:999px;
  border:1px solid rgba(74,158,255,0.14);
  background:rgba(2,4,9,0.55);
  color:rgba(100,140,210,0.50);
  cursor:pointer;transition:all .18s;
  backdrop-filter:blur(6px);
}
.ctx-tag:hover{color:rgba(120,188,255,0.80);border-color:rgba(74,158,255,0.35);}
.ctx-tag.active{
  border-color:rgba(200,168,75,0.45);
  color:rgba(232,204,122,0.90);
  background:rgba(200,168,75,0.10);
}
</style>
</head>
<body>

<!-- CANVAS -->
<canvas id="galaxy"></canvas>

<!-- INTRO -->
<div id="intro">
  <div class="intro-title">KING DIADEM</div>
  <div class="intro-sub">DRIFTZERO · WATERLINE · FATE™</div>
  <div class="intro-bar"><div class="intro-fill" id="intro-fill"></div></div>
  <div class="intro-tagline">FAIL LESS · HARM LESS · RESTORE CHOICE</div>
</div>

<!-- HUD -->
<div id="hud">
  <div id="topbar">
    <div class="tb-brand">
      <div class="tb-crown">♛</div>
      <div class="tb-title">KING DIADEM</div>
    </div>
    <div class="tb-right">
      <span class="tb-badge ok" id="b-fate">FATE</span>
      <span class="tb-badge ok" id="b-lyla">LYLA</span>
      <span class="tb-badge off" id="b-crit">WL</span>
      <div id="tb-time">--:--</div>
    </div>
  </div>

  <div id="lyla-float">LYLA ◈ ONLINE</div>

  <div id="wl-float">
    <div class="wl-dot" id="wl-val">WATERLINE 89</div>
    <div class="wl-dot" id="wl-status">SAFE</div>
  </div>

  <div id="ctx-tags">
    <div class="ctx-tag active" data-r="general"  onclick="setRoute('general')">GENERAL</div>
    <div class="ctx-tag"        data-r="risk"     onclick="setRoute('risk')">RISK</div>
    <div class="ctx-tag"        data-r="survival" onclick="setRoute('survival')">SURVIVAL</div>
    <div class="ctx-tag"        data-r="collapse" onclick="setRoute('collapse')">COLLAPSE</div>
    <div class="ctx-tag"        data-r="civil"    onclick="setRoute('civil')">CIVIL</div>
    <div class="ctx-tag"        data-r="vega"     onclick="setRoute('vega')">VEGA</div>
  </div>

  <div id="hud-bottom">
    <div class="hud-stat">
      <div class="hud-stat-k">Entropy</div>
      <div class="hud-stat-v" id="h-ent">45</div>
    </div>
    <div class="hud-stat">
      <div class="hud-stat-k">Stability</div>
      <div class="hud-stat-v gold" id="h-stb">62</div>
    </div>
    <div class="hud-stat">
      <div class="hud-stat-k">Resources</div>
      <div class="hud-stat-v gold" id="h-rsc">78</div>
    </div>
    <div class="hud-stat">
      <div class="hud-stat-k">Waterline</div>
      <div class="hud-stat-v" id="h-wl">89</div>
    </div>
    <div class="hud-stat">
      <div class="hud-stat-k">Choice(t)</div>
      <div class="hud-stat-v gold" id="h-choice">≥1</div>
    </div>
    <div class="hud-stat">
      <div class="hud-stat-k">Route</div>
      <div class="hud-stat-v gold" id="h-route">GENERAL</div>
    </div>
  </div>

  <div id="route-pills">
    <div class="rpill active" data-r="general"  onclick="setRoute('general')">ทั่วไป</div>
    <div class="rpill"        data-r="risk"     onclick="setRoute('risk')">ความเสี่ยง</div>
    <div class="rpill"        data-r="survival" onclick="setRoute('survival')">รอดชีวิต</div>
    <div class="rpill"        data-r="collapse" onclick="setRoute('collapse')">วิกฤต</div>
    <div class="rpill"        data-r="civil"    onclick="setRoute('civil')">สังคม</div>
    <div class="rpill"        data-r="vega"     onclick="setRoute('vega')">VEGA</div>
  </div>
</div>

<script>
/* ============================================================
   KING DIADEM — Galaxy Screen v36 STANDALONE
   Full cosmic engine — no backend needed
   ============================================================ */
(function(){
'use strict';

var cv=document.getElementById('galaxy');
var ctx=cv.getContext('2d',{alpha:true});
var W=0,H=0,lastTime=0;
var activeRoute='general';
var FPS_LOW=false;

/* ── RESIZE ── */
var _rT;
function doResize(){
  W=cv.width=window.innerWidth;
  H=cv.height=window.innerHeight;
  buildStars();buildFilaments();buildAurora();buildDustMotes();
}
window.addEventListener('resize',function(){clearTimeout(_rT);_rT=setTimeout(doResize,60);},{passive:true});

/* ── STATE ── */
var STATE={
  entropy:45,stability:62,resources:78,waterline:89,
  choice_count:4,thinking:false,activeRoute:'general',
  blackHole:false,flareCharge:0
};

function updateWaterline(){
  var d=(STATE.entropy*0.33)+(100-STATE.stability)*0.33+(100-STATE.resources)*0.34;
  STATE.waterline=Math.max(0,Math.min(100,100-d));
  STATE.blackHole=STATE.waterline<20;
}

/* ── ROUTE COLORS ── */
var ROUTE_HUE={general:208,risk:10,survival:36,collapse:28,civil:168,vega:258};
var _curHue=208,_tgtHue=208;

/* ── PLANETS ── */
var PDEFS=[
  {id:'a1',label:null,orb:.13,spd:.00028,ang:.80,sz:2.0,c0:'#c8c0b8',c1:'#706860',c2:'#1e1a18',glow:'rgba(200,190,175,',atm:null},
  {id:'a2',label:null,orb:.20,spd:.00022,ang:2.10,sz:3.2,c0:'#f0d890',c1:'#b89030',c2:'#2a1e04',glow:'rgba(230,200,100,',atm:'rgba(220,180,80,'},
  {id:'general',label:'GENERAL',orb:.28,spd:.00016,ang:3.60,sz:4.8,c0:'#78c8f8',c1:'#1a6eca',c2:'#05152e',glow:'rgba(80,160,255,',atm:'rgba(60,140,240,'},
  {id:'risk',label:'RISK',orb:.37,spd:.00011,ang:5.20,sz:3.8,c0:'#e87848',c1:'#a03818',c2:'#220a02',glow:'rgba(230,100,60,',atm:'rgba(200,70,30,'},
  {id:'survival',label:'SURVIVAL',orb:.50,spd:.00006,ang:1.40,sz:7.5,c0:'#e8c880',c1:'#b87820',c2:'#1e0e00',glow:'rgba(200,160,60,',atm:'rgba(180,130,40,',bands:true},
  {id:'collapse',label:'COLLAPSE',orb:.62,spd:.00004,ang:4.00,sz:6.2,c0:'#d8c090',c1:'#987040',c2:'#1a1004',glow:'rgba(200,170,90,',atm:'rgba(170,140,60,',rings:true},
  {id:'civil',label:'CIVIL',orb:.76,spd:.000025,ang:.50,sz:5.0,c0:'#80e8e0',c1:'#289898',c2:'#021e1e',glow:'rgba(80,220,210,',atm:'rgba(60,200,190,'},
  {id:'vega',label:'VEGA',orb:.91,spd:.000016,ang:2.80,sz:4.8,c0:'#6898e8',c1:'#2838b8',c2:'#020416',glow:'rgba(100,140,240,',atm:'rgba(80,110,220,',storm:true},
];
var PLANETS=PDEFS.map(function(d){return Object.assign({ang:d.ang||0},d);});

/* ── LAYOUT ── */
function SX(){return W*0.50;}
function SY(){return H*0.48;}
function sunR(){return Math.max(10,Math.min(H*0.048,22));}
function maxOrb(){return Math.min(W*0.42,H*0.42);}

/* ── ION TRAILS ── */
var ION={};
PLANETS.forEach(function(p){if(p.label)ION[p.id]=[];});
function updateTrail(id,x,y){if(!ION[id])return;ION[id].push({x:x,y:y});if(ION[id].length>45)ION[id].shift();}

/* ── PARTICLES ── */
var PAR=[];
function spawnEx(x,y,col,n){
  n=n||40;
  for(var i=0;i<n;i++){
    var a=Math.random()*Math.PI*2,s=.4+Math.random()*2.8;
    PAR.push({x:x,y:y,vx:Math.cos(a)*s,vy:Math.sin(a)*s,r:.4+Math.random()*2.2,
      alpha:.7+Math.random()*.3,decay:.012+Math.random()*.022,col:col||'120,200,255',grav:.008+Math.random()*.012});
  }
}

/* ── SHOCKWAVES ── */
var SWS=[];
function shockwave(x,y,col,big){
  SWS.push({x:x,y:y,r:0,maxR:Math.min(W,H)*(big?.55:.32),alpha:big?.80:.55,col:col||'120,200,255'});
  if(SWS.length>6)SWS.shift();
}

/* ── FLARES ── */
var FLARES=[],nextFlare=8000;
function spawnFlare(sx,sy,R){
  var a=Math.random()*Math.PI*2,l=R*(2.2+Math.random()*3.5);
  FLARES.push({angle:a,len:l,sx:sx,sy:sy,R:R,life:0,maxLife:.8+Math.random()*1.4,
    width:.5+Math.random()*1.2,col:Math.random()<.6?'255,160,40':'255,220,80'});
}

/* ── WORMHOLE ── */
var WH={active:false,progress:0,fromX:0,fromY:0,toX:0,toY:0,alpha:0};
var nextWH=20000;

/* ── STARS ── */
var STARS=[];
function buildStars(){
  STARS=[];
  for(var i=0;i<2400;i++)STARS.push({x:Math.random()*W,y:Math.random()*H,r:.05+Math.random()*.22,a:.05+Math.random()*.22,col:Math.random()>.5?'170,205,255':'205,185,255',tw:false});
  for(var j=0;j<320;j++)STARS.push({x:Math.random()*W,y:Math.random()*H,r:.14+Math.random()*.32,a:.16+Math.random()*.28,col:Math.random()>.5?'145,205,255':'195,155,255',tw:true,tS:.00008+Math.random()*.00015,tO:Math.random()*Math.PI*2});
  for(var k=0;k<60;k++){var rr=Math.random();STARS.push({x:Math.random()*W,y:Math.random()*H,r:.38+Math.random()*.60,a:.38+Math.random()*.40,col:rr<.42?'130,195,255':rr<.80?'200,150,255':'255,205,130',tw:true,tS:.00004+Math.random()*.00009,tO:Math.random()*Math.PI*2,bloom:true});}
}

/* ── FILAMENTS ── */
var FIL=[];
function buildFilaments(){
  FIL=[];var n=W<500?5:11;
  for(var i=0;i<n;i++)FIL.push({x:Math.random()*W,y:Math.random()*H,w:W*(.14+Math.random()*.42),h:H*(.04+Math.random()*.16),angle:-.5+Math.random()*1.0,hue:_curHue+(Math.random()-.5)*40,alpha:.018+Math.random()*.048,speed:.000004+Math.random()*.000012,phase:Math.random()*Math.PI*2});
}

/* ── AURORA ── */
var AUR=[];
function buildAurora(){
  AUR=[];var n=W<600?2:4;
  for(var i=0;i<n;i++){
    var segs=16+Math.floor(Math.random()*12),pts=[];
    for(var j=0;j<=segs;j++)pts.push({x:(j/segs)*W,dy:0,dv:(Math.random()-.5)*.08});
    AUR.push({pts:pts,baseY:H*(.05+Math.random()*.28),height:H*(.05+Math.random()*.10),hue:Math.random()<.5?165+Math.random()*30:210+Math.random()*40,alpha:.010+Math.random()*.018,speed:.000004+Math.random()*.000008,phase:Math.random()*Math.PI*2});
  }
}

/* ── DUST ── */
var DUST=[];
function buildDustMotes(){
  DUST=[];var n=W<600?50:130;
  for(var i=0;i<n;i++)DUST.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.009,vy:(Math.random()-.5)*.005,r:.3+Math.random()*.9,a:.03+Math.random()*.08,col:Math.random()<.6?'130,190,255':'180,140,255',tS:.0001+Math.random()*.0002,tO:Math.random()*Math.PI*2});
}

/* ── ASTEROIDS ── */
var AST=(function(){var b=[];for(var i=0;i<180;i++)b.push({frac:.42+Math.random()*.06,ang:Math.random()*Math.PI*2,spd:.000008+Math.random()*.000005,r:.3+Math.random()*.9,a:.06+Math.random()*.18,scatter:(Math.random()-.5)*.025});return b;})();

/* ── FATE TEXTS ── */
var CANON=['Logic over Persona.','Rule over Authority.','Downside before Upside.','Human retains\nfinal authority.','Fail less.\nHarm less.\nRestore more.','Choice(t) >= 1\ncollapse = False','ไม่ได้สร้างมาเพื่อชนะทุกครั้ง\nสร้างมาเพื่อไม่พังแบบเดิมอีกครั้ง','Stay simple long enough\nto outlive the impossible.','The crown belongs to no one.\nChoice itself is the crown.','ปฏิจสมุปบาท —\nทุกอย่างเกิดจากเหตุปัจจัย','Structure before action.','กฎมีไว้จำกัดอำนาจ\nไม่ใช่ขยายอำนาจ'];
var FTX=[];
function spawnFT(){
  var t=CANON[Math.floor(Math.random()*CANON.length)];
  return{lines:t.split('\n'),x:W*(.15+Math.random()*.70),y:H*(.12+Math.random()*.76),alpha:0,maxAlpha:.038+Math.random()*.035,state:'in',lifeIn:2400+Math.random()*1600,lifeHold:4200+Math.random()*5000,lifeOut:2200+Math.random()*1400,age:0,size:W<500?7+Math.random()*2.5:8.5+Math.random()*3.5};
}
function initFT(){FTX=[];for(var i=0;i<(W<500?3:5);i++){var f=spawnFT();f.age=Math.random()*(f.lifeIn+f.lifeHold);if(f.age>f.lifeIn)f.state='hold';FTX.push(f);}}

/* ── COMET ── */
var COMET={active:false,x:0,y:0,vx:0,vy:0,life:0,maxLife:0};
var nextComet=14000;
var METEORS=[],metActive=false,metEnd=0,nextMet=10000;

/* ── LENS RINGS ── */
function drawLens(x,y,sz,t){
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var ri=1;ri<=3;ri++){
    var lR=sz*(2.2+ri*1.4),al=.055/ri*(.7+.3*Math.sin(t*.0008+ri*1.1));
    ctx.beginPath();ctx.arc(x,y,lR,0,Math.PI*2);
    ctx.strokeStyle='rgba(180,220,255,'+al+')';ctx.lineWidth=.5;ctx.stroke();
    ctx.save();ctx.translate(x,y);ctx.rotate(t*.0002*ri);
    ctx.beginPath();ctx.arc(0,0,lR,-.4,.4);
    ctx.strokeStyle='rgba(200,230,255,'+(al*2.5)+')';ctx.lineWidth=.8;ctx.stroke();
    ctx.restore();
  }
  ctx.restore();
}

/* ── CLICK ── */
cv.addEventListener('click',function(e){
  var rect=cv.getBoundingClientRect();
  var mx=e.clientX-rect.left,my=e.clientY-rect.top;
  var sx=SX(),sy=SY(),mr=maxOrb();
  for(var i=0;i<PLANETS.length;i++){
    var p=PLANETS[i];if(!p.label)continue;
    var r=p.orb*mr,px2=sx+Math.cos(p.ang)*r,py2=sy+Math.sin(p.ang)*r;
    var dist=Math.sqrt((mx-px2)*(mx-px2)+(my-py2)*(my-py2));
    var scale=Math.max(.70,Math.min(H/560,1.30));
    if(dist<p.sz*scale*3.5){
      var col=p.glow.replace('rgba(','').split(',').slice(0,3).join(',');
      shockwave(px2,py2,col,false);spawnEx(px2,py2,col,60);
      if(p.id!==activeRoute){setRoute(p.id);}
      return;
    }
  }
  spawnEx(mx,my,'120,190,255',14);
},{passive:true});

/* ── DRAW BG ── */
function drawBg(t){
  ctx.clearRect(0,0,W,H);
  if(STATE.blackHole){
    var bhP=Math.max(0,(20-STATE.waterline)/20);
    var bg=ctx.createRadialGradient(SX(),SY(),0,W*.5,H*.5,Math.max(W,H)*.82);
    bg.addColorStop(0,'rgba(10,0,0,'+(0.95*bhP)+')');
    bg.addColorStop(.4,'rgba(4,0,0,'+(0.98*bhP)+')');
    bg.addColorStop(1,'#020409');
    ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);return;
  }
  var bg=ctx.createRadialGradient(SX()*.6,SY(),0,W*.5,H*.5,Math.max(W,H)*.82);
  bg.addColorStop(0,'#050814');bg.addColorStop(.30,'#040711');bg.addColorStop(.65,'#03060e');bg.addColorStop(1,'#020409');
  ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);
  ctx.save();ctx.globalCompositeOperation='screen';
  var band=ctx.createLinearGradient(0,H*.20,W,H*.80);
  band.addColorStop(0,'rgba(0,0,0,0)');band.addColorStop(.25,'rgba(60,80,140,0.038)');band.addColorStop(.50,'rgba(80,100,180,0.055)');band.addColorStop(.75,'rgba(60,80,140,0.038)');band.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=band;ctx.fillRect(0,0,W,H);ctx.restore();
}

function drawFilaments(t){
  if(STATE.blackHole)return;
  _curHue+=(_tgtHue-_curHue)*.008;
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<FIL.length;i++){
    var f=FIL[i];f.hue+=(_curHue-f.hue)*.004;
    var breathe=Math.sin(t*f.speed+f.phase);
    var al=f.alpha*(.6+.4*breathe);
    var fx=f.x+Math.sin(t*f.speed*.7+f.phase)*W*.030;
    var fy=f.y+Math.cos(t*f.speed*.5+f.phase)*H*.020;
    ctx.save();ctx.translate(fx,fy);ctx.rotate(f.angle);
    var ng=ctx.createRadialGradient(0,0,0,0,0,f.w*.5);
    ng.addColorStop(0,'hsla('+f.hue+',60%,55%,'+al+')');ng.addColorStop(.5,'hsla('+f.hue+',50%,45%,'+(al*.4)+')');ng.addColorStop(1,'hsla('+f.hue+',40%,35%,0)');
    ctx.beginPath();ctx.ellipse(0,0,f.w*.5,f.h*.5,0,0,Math.PI*2);ctx.fillStyle=ng;ctx.fill();ctx.restore();
  }
  ctx.restore();
}

function drawAurora(t){
  if(STATE.blackHole||FPS_LOW)return;
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<AUR.length;i++){
    var au=AUR[i];
    for(var j=0;j<au.pts.length;j++){au.pts[j].dv+=(Math.random()-.5)*.004;au.pts[j].dv*=.96;au.pts[j].dy+=au.pts[j].dv;au.pts[j].dy*=.97;}
    var aal=au.alpha*(.6+.4*Math.sin(t*au.speed+au.phase));
    var ag=ctx.createLinearGradient(0,au.baseY,0,au.baseY+au.height);
    ag.addColorStop(0,'hsla('+au.hue+',80%,60%,0)');ag.addColorStop(.3,'hsla('+au.hue+',80%,60%,'+aal+')');ag.addColorStop(.7,'hsla('+au.hue+',70%,50%,'+(aal*.5)+')');ag.addColorStop(1,'hsla('+au.hue+',70%,50%,0)');
    ctx.beginPath();ctx.moveTo(au.pts[0].x,au.baseY+au.pts[0].dy);
    for(var k=1;k<au.pts.length;k++){var p0=au.pts[k-1],p1=au.pts[k];ctx.quadraticCurveTo(p0.x,au.baseY+p0.dy,(p0.x+p1.x)*.5,(au.baseY+p0.dy+au.baseY+p1.dy)*.5);}
    ctx.lineTo(W,au.baseY+au.height);ctx.lineTo(0,au.baseY+au.height);ctx.closePath();ctx.fillStyle=ag;ctx.fill();
  }
  ctx.restore();
}

function drawStars(t){
  ctx.save();ctx.globalCompositeOperation='screen';
  var bhP=STATE.blackHole?Math.max(0,(20-STATE.waterline)/20):0;
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var al=s.a*(1-bhP*.85);
    if(s.tw)al*=(.5+.5*Math.sin(t*s.tS+s.tO));
    al=Math.max(.01,Math.min(1,al));
    ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fillStyle='rgba('+s.col+','+al.toFixed(3)+')';ctx.fill();
    if(!FPS_LOW&&s.bloom&&al>.44){
      var sp=s.r*3.5;
      ctx.strokeStyle='rgba('+s.col+','+(al*.06).toFixed(3)+')';ctx.lineWidth=.18;
      ctx.beginPath();ctx.moveTo(s.x-sp,s.y);ctx.lineTo(s.x+sp,s.y);ctx.moveTo(s.x,s.y-sp);ctx.lineTo(s.x,s.y+sp);ctx.stroke();
    }
  }
  ctx.restore();
}

function drawDust(t){
  if(FPS_LOW)return;
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<DUST.length;i++){
    var d=DUST[i];d.x=(d.x+d.vx+W)%W;d.y=(d.y+d.vy+H)%H;
    var al=d.a*(.5+.5*Math.sin(t*d.tS+d.tO));
    ctx.beginPath();ctx.arc(d.x,d.y,d.r,0,Math.PI*2);ctx.fillStyle='rgba('+d.col+','+al.toFixed(3)+')';ctx.fill();
  }
  ctx.restore();
}

function drawFateTexts(dt){
  if(STATE.blackHole)return;
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<FTX.length;i++){
    var ft=FTX[i];ft.age+=dt*1000;
    if(ft.state==='in'){ft.alpha=ft.maxAlpha*Math.min(1,ft.age/ft.lifeIn);if(ft.age>=ft.lifeIn){ft.state='hold';ft.age=0;}}
    else if(ft.state==='hold'){ft.alpha=ft.maxAlpha;if(ft.age>=ft.lifeHold){ft.state='out';ft.age=0;}}
    else if(ft.state==='out'){ft.alpha=ft.maxAlpha*Math.max(0,1-ft.age/ft.lifeOut);if(ft.age>=ft.lifeOut){FTX[i]=spawnFT();continue;}}
    if(ft.alpha<.002)continue;
    ctx.font='300 '+ft.size+'px "DM Mono",monospace';
    ctx.fillStyle='rgba(175,210,255,'+ft.alpha.toFixed(4)+')';
    ctx.textAlign='center';ctx.textBaseline='middle';
    for(var li=0;li<ft.lines.length;li++)ctx.fillText(ft.lines[li],ft.x,ft.y+(li-(ft.lines.length-1)*.5)*(ft.size*1.5));
  }
  ctx.restore();
}

function drawOrbits(){
  var sx=SX(),sy=SY(),mr=maxOrb();
  ctx.save();ctx.setLineDash([2,14]);
  PLANETS.forEach(function(p){
    var r=p.orb*mr,isA=p.id===activeRoute;
    ctx.beginPath();ctx.arc(sx,sy,r,0,Math.PI*2);
    if(STATE.blackHole)ctx.strokeStyle=isA?'rgba(180,20,20,0.28)':'rgba(80,10,10,0.06)';
    else ctx.strokeStyle=isA?'rgba(140,200,255,0.22)':'rgba(80,130,220,0.06)';
    ctx.lineWidth=isA?.70:.28;ctx.stroke();
  });
  ctx.setLineDash([]);ctx.restore();
}

function drawAsteroids(dt){
  var sx=SX(),sy=SY(),mr=maxOrb();
  var em=.5+(STATE.entropy/100)*1.5;
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<AST.length;i++){
    var a=AST[i];a.ang+=a.spd*dt*60*em;
    var r=(a.frac+a.scatter)*mr;
    ctx.beginPath();ctx.arc(sx+Math.cos(a.ang)*r,sy+Math.sin(a.ang)*r,a.r,0,Math.PI*2);
    ctx.fillStyle='rgba(160,150,140,'+a.a+')';ctx.fill();
  }
  ctx.restore();
}

function drawIonTrails(){
  ctx.save();ctx.globalCompositeOperation='screen';
  PLANETS.forEach(function(p){
    if(!p.label||!ION[p.id])return;
    var trail=ION[p.id];if(trail.length<3)return;
    for(var i=1;i<trail.length;i++){
      var prog=i/trail.length,al=prog*.15;
      ctx.beginPath();ctx.moveTo(trail[i-1].x,trail[i-1].y);ctx.lineTo(trail[i].x,trail[i].y);
      ctx.strokeStyle=p.glow?p.glow+al+')':'rgba(150,200,255,'+al+')';
      ctx.lineWidth=prog*1.8;ctx.stroke();
    }
  });
  ctx.restore();
}

function drawWormhole(t,dt){
  var sx=SX(),sy=SY(),mr=maxOrb();
  var ap=PLANETS.find(function(p){return p.id===activeRoute;});
  if(!ap)return;
  var r=ap.orb*mr,apx=sx+Math.cos(ap.ang)*r,apy=sy+Math.sin(ap.ang)*r;
  if(t>nextWH&&!WH.active){
    WH.active=true;WH.progress=0;WH.fromX=sx;WH.fromY=sy;WH.toX=apx;WH.toY=apy;WH.alpha=0;
    nextWH=t+35000+Math.random()*40000;
  }
  if(!WH.active)return;
  WH.progress+=dt*.35;WH.toX=apx;WH.toY=apy;
  if(WH.progress<.3)WH.alpha=WH.progress/.3;
  else if(WH.progress>.7)WH.alpha=Math.max(0,(1-WH.progress)/.3);
  else WH.alpha=1;
  if(WH.progress>=1){WH.active=false;return;}
  ctx.save();ctx.globalCompositeOperation='screen';
  var al=WH.alpha*.35;
  var dx=WH.toX-WH.fromX,dy=WH.toY-WH.fromY;
  var wg=ctx.createLinearGradient(WH.fromX,WH.fromY,WH.toX,WH.toY);
  wg.addColorStop(0,'rgba(255,200,60,'+al+')');wg.addColorStop(.5,'rgba(120,180,255,'+(al*.6)+')');wg.addColorStop(1,'rgba(200,150,255,'+al+')');
  ctx.setLineDash([4,8]);ctx.beginPath();ctx.moveTo(WH.fromX,WH.fromY);ctx.lineTo(WH.toX,WH.toY);
  ctx.strokeStyle=wg;ctx.lineWidth=.8+WH.alpha;ctx.stroke();ctx.setLineDash([]);
  var pt=WH.progress%1;var px=WH.fromX+dx*pt,py=WH.fromY+dy*pt;
  var pg=ctx.createRadialGradient(px,py,0,px,py,8);
  pg.addColorStop(0,'rgba(255,240,200,'+(al*2)+')');pg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.beginPath();ctx.arc(px,py,8,0,Math.PI*2);ctx.fillStyle=pg;ctx.fill();ctx.restore();
}

function drawFlares(t,dt){
  var sx=SX(),sy=SY(),R=sunR();
  if(t>nextFlare&&!FPS_LOW){spawnFlare(sx,sy,R);nextFlare=t+3000+Math.random()*8000;STATE.flareCharge=Math.min(1,STATE.flareCharge+.15);}
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=FLARES.length-1;i>=0;i--){
    var f=FLARES[i];f.life+=dt;
    if(f.life>=f.maxLife){FLARES.splice(i,1);continue;}
    var prog=f.life/f.maxLife;
    var al=(prog<.2?prog/.2:Math.max(0,1-(prog-.2)/.8))*.65;
    var curve=Math.sin(prog*Math.PI)*f.len;
    var perpA=f.angle+Math.PI*.5;
    var midX=f.sx+Math.cos(f.angle)*curve*.5+Math.cos(perpA)*f.len*.22;
    var midY=f.sy+Math.sin(f.angle)*curve*.5+Math.sin(perpA)*f.len*.22;
    var endX=f.sx+Math.cos(f.angle)*curve,endY=f.sy+Math.sin(f.angle)*curve;
    var fg=ctx.createLinearGradient(f.sx,f.sy,endX,endY);
    fg.addColorStop(0,'rgba('+f.col+','+al+')');fg.addColorStop(.5,'rgba('+f.col+','+(al*.6)+')');fg.addColorStop(1,'rgba('+f.col+',0)');
    ctx.beginPath();ctx.moveTo(f.sx+Math.cos(f.angle)*f.R,f.sy+Math.sin(f.angle)*f.R);
    ctx.quadraticCurveTo(midX,midY,endX,endY);ctx.strokeStyle=fg;ctx.lineWidth=f.width*(1-prog*.6);ctx.stroke();
  }
  ctx.restore();
}

function drawPlanet(x,y,p,isA,t){
  var scale=Math.max(.70,Math.min(H/560,1.30));
  var sz=p.sz*scale;
  ctx.save();ctx.globalCompositeOperation='screen';
  if(p.atm){
    var atmA=isA?.22:.08,atmR=sz*2.8+(isA?7:0);
    var atm=ctx.createRadialGradient(x,y,sz*.5,x,y,atmR);
    atm.addColorStop(0,p.atm+atmA+')');atm.addColorStop(.6,p.atm+(atmA*.3)+')');atm.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.arc(x,y,atmR,0,Math.PI*2);ctx.fillStyle=atm;ctx.fill();
  }
  if(p.glow){
    var pulse=isA?(1+Math.sin(t*.0011)*.14):1;
    var gR2=sz*(isA?5.2:3.0)*pulse;
    var gr2=ctx.createRadialGradient(x,y,sz*1.0,x,y,gR2);
    gr2.addColorStop(0,p.glow+(isA?'0.22':'0.07')+')');gr2.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.arc(x,y,gR2,0,Math.PI*2);ctx.fillStyle=gr2;ctx.fill();
    var gR=sz*(isA?3.2:2.0)*pulse;
    var gr=ctx.createRadialGradient(x,y,sz*.7,x,y,gR);
    gr.addColorStop(0,p.glow+(isA?'0.55':'0.22')+')');gr.addColorStop(.4,p.glow+(isA?'0.16':'0.07')+')');gr.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.arc(x,y,gR,0,Math.PI*2);ctx.fillStyle=gr;ctx.fill();
  }
  ctx.restore();
  if(p.rings){
    var rx=sz*3.4,ry=sz*.36;
    ctx.save();ctx.translate(x,y);ctx.rotate(-.22);ctx.globalCompositeOperation='screen';
    for(var ri=0;ri<3;ri++){
      var rf=.78+ri*.12;
      var rg=ctx.createLinearGradient(-rx*rf,0,rx*rf,0);
      rg.addColorStop(0,'rgba(0,0,0,0)');rg.addColorStop(.25,p.glow+(isA?'0.28':'0.14')+')');rg.addColorStop(.5,p.glow+(isA?'0.42':'0.20')+')');rg.addColorStop(.75,p.glow+(isA?'0.28':'0.14')+')');rg.addColorStop(1,'rgba(0,0,0,0)');
      ctx.beginPath();ctx.ellipse(0,0,rx*rf,ry*rf,0,Math.PI,Math.PI*2);ctx.strokeStyle=rg;ctx.lineWidth=isA?1.6:.8;ctx.stroke();
    }
    ctx.restore();
  }
  ctx.save();
  var body=ctx.createRadialGradient(x-sz*.28,y-sz*.26,0,x+sz*.08,y+sz*.08,sz*1.06);
  body.addColorStop(0,p.c0);body.addColorStop(.45,p.c1);body.addColorStop(1,p.c2);
  ctx.beginPath();ctx.arc(x,y,sz,0,Math.PI*2);ctx.fillStyle=body;ctx.fill();
  if(p.bands){
    ctx.globalCompositeOperation='overlay';
    for(var bi=0;bi<4;bi++){
      var by=y-sz*.65+bi*(sz*.36),bh=sz*.14;
      var bg2=ctx.createLinearGradient(x-sz,by,x+sz,by);
      bg2.addColorStop(0,'rgba(0,0,0,0)');bg2.addColorStop(.3,'rgba(100,60,20,0.28)');bg2.addColorStop(.7,'rgba(100,60,20,0.28)');bg2.addColorStop(1,'rgba(0,0,0,0)');
      ctx.save();ctx.beginPath();ctx.ellipse(x,by+bh*.5,sz*.92,bh,0,0,Math.PI*2);ctx.fillStyle=bg2;ctx.fill();ctx.restore();
    }
  }
  if(p.storm){
    ctx.globalCompositeOperation='screen';
    var stx=x+sz*.28,sty=y-sz*.20;
    var stg=ctx.createRadialGradient(stx,sty,0,stx,sty,sz*.32);
    stg.addColorStop(0,'rgba(180,200,255,0.35)');stg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.arc(stx,sty,sz*.32,0,Math.PI*2);ctx.fillStyle=stg;ctx.fill();
  }
  ctx.globalCompositeOperation='screen';
  var vein=ctx.createRadialGradient(x-sz*.20,y-sz*.20,0,x-sz*.06,y-sz*.06,sz*.62);
  vein.addColorStop(0,p.glow?p.glow+'0.32)':'rgba(255,255,255,0.18)');vein.addColorStop(1,'rgba(0,0,0,0)');
  ctx.beginPath();ctx.arc(x,y,sz,0,Math.PI*2);ctx.fillStyle=vein;ctx.fill();
  ctx.globalCompositeOperation='source-over';
  var limb=ctx.createRadialGradient(x,y,sz*.12,x,y,sz*1.05);
  limb.addColorStop(0,'rgba(0,0,0,0)');limb.addColorStop(.5,'rgba(0,0,0,0.16)');limb.addColorStop(1,'rgba(0,0,0,0.78)');
  ctx.beginPath();ctx.arc(x,y,sz,0,Math.PI*2);ctx.fillStyle=limb;ctx.fill();
  ctx.restore();
  if(p.rings){
    var rx2=sz*3.4,ry2=sz*.36;
    ctx.save();ctx.translate(x,y);ctx.rotate(-.22);ctx.globalCompositeOperation='screen';
    for(var ri2=0;ri2<3;ri2++){
      var rf2=.78+ri2*.12;
      var rg2=ctx.createLinearGradient(-rx2*rf2,0,rx2*rf2,0);
      rg2.addColorStop(0,'rgba(0,0,0,0)');rg2.addColorStop(.25,p.glow+(isA?'0.28':'0.14')+')');rg2.addColorStop(.5,p.glow+(isA?'0.42':'0.20')+')');rg2.addColorStop(.75,p.glow+(isA?'0.28':'0.14')+')');rg2.addColorStop(1,'rgba(0,0,0,0)');
      ctx.beginPath();ctx.ellipse(0,0,rx2*rf2,ry2*rf2,0,0,Math.PI);ctx.strokeStyle=rg2;ctx.lineWidth=isA?1.6:.8;ctx.stroke();
    }
    ctx.restore();
  }
  if(isA&&!FPS_LOW)drawLens(x,y,sz,t);
  if(p.label){
    ctx.save();
    var fs=Math.max(7,Math.round(sz*.82));
    if(isA){ctx.globalCompositeOperation='screen';ctx.shadowColor=p.glow?p.glow+'0.85)':'rgba(120,200,255,0.85)';ctx.shadowBlur=10;ctx.fillStyle=p.c0;}
    else{ctx.fillStyle='rgba(120,185,160,0.28)';}
    ctx.font='500 '+fs+'px "DM Mono",monospace';ctx.textAlign='center';ctx.textBaseline='top';
    ctx.fillText(p.label,x,y+sz+4);ctx.restore();
  }
  if(p.label)updateTrail(p.id,x,y);
}

function drawPlanets(dt,t){
  var sx=SX(),sy=SY(),mr=maxOrb();
  var em=.4+(STATE.entropy/100)*1.6;
  var items=PLANETS.map(function(p){
    p.ang+=p.spd*dt*60*em;
    var r=p.orb*mr;
    return{p:p,x:sx+Math.cos(p.ang)*r,y:sy+Math.sin(p.ang)*r};
  });
  items.sort(function(a,b){return a.y-b.y;});
  items.forEach(function(item){
    if(item.x<-40||item.x>W+40||item.y<-40||item.y>H+40)return;
    drawPlanet(item.x,item.y,item.p,item.p.id===activeRoute,t);
  });
}

function drawSun(t){
  if(STATE.blackHole){drawBlackHole(t);return;}
  var sx=SX(),sy=SY(),R=sunR();
  var gm=STATE.waterline<40?.60:STATE.waterline<70?1.00:1.30;
  if(STATE.thinking)gm*=(1+Math.sin(t*.005)*.32);
  ctx.save();ctx.globalCompositeOperation='lighter';
  for(var ring=6;ring>=1;ring--){
    var rAl=(.016/ring)*gm,rR=R*(3.2+ring*3.6);
    ctx.beginPath();ctx.arc(sx,sy,rR,0,Math.PI*2);ctx.strokeStyle='rgba(255,200,80,'+rAl+')';ctx.lineWidth=.32;ctx.stroke();
  }
  if(STATE.thinking){
    for(var b=0;b<3;b++){
      var bPhase=(t*.003+b*1.0)%(Math.PI*2);
      var bR=R*(2+b*4+Math.sin(bPhase)*2),bAl=Math.max(0,Math.sin(bPhase)*.28);
      ctx.beginPath();ctx.arc(sx,sy,bR,0,Math.PI*2);ctx.strokeStyle='rgba(255,220,80,'+bAl+')';ctx.lineWidth=.65;ctx.stroke();
    }
  }
  var fc=ctx.createRadialGradient(sx,sy,R*.12,sx,sy,R*13);
  fc.addColorStop(0,'rgba(255,200,60,'+(0.34*gm)+')');fc.addColorStop(.15,'rgba(255,140,20,'+(0.12*gm)+')');fc.addColorStop(.40,'rgba(90,170,255,'+(0.05*gm)+')');fc.addColorStop(.70,'rgba(40,70,150,'+(0.018*gm)+')');fc.addColorStop(1,'rgba(0,0,0,0)');
  ctx.beginPath();ctx.arc(sx,sy,R*13,0,Math.PI*2);ctx.fillStyle=fc;ctx.fill();
  ctx.save();ctx.translate(sx,sy);ctx.rotate(t*.000015);
  for(var i=0;i<18;i++){
    var a=(i/18)*Math.PI*2,rl=R*(1.8+.28*Math.sin(i*1.7+t*.00012))*gm;
    var gr=ctx.createLinearGradient(Math.cos(a)*R*.18,Math.sin(a)*R*.18,Math.cos(a)*rl,Math.sin(a)*rl);
    gr.addColorStop(0,'rgba(255,200,50,'+(0.32*gm)+')');gr.addColorStop(.5,'rgba(200,120,10,0.05)');gr.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle=gr;ctx.lineWidth=.6;ctx.beginPath();ctx.moveTo(Math.cos(a)*R*.18,Math.sin(a)*R*.18);ctx.lineTo(Math.cos(a)*rl,Math.sin(a)*rl);ctx.stroke();
  }
  ctx.restore();ctx.globalCompositeOperation='source-over';
  var ih=ctx.createRadialGradient(sx,sy,R*.22,sx,sy,R*2.6);
  ih.addColorStop(0,'rgba(255,240,150,0.96)');ih.addColorStop(.25,'rgba(255,190,50,0.65)');ih.addColorStop(.60,'rgba(200,90,10,0.20)');ih.addColorStop(1,'rgba(0,0,0,0)');
  ctx.beginPath();ctx.arc(sx,sy,R*2.6,0,Math.PI*2);ctx.fillStyle=ih;ctx.fill();
  var sbody=ctx.createRadialGradient(sx-R*.22,sy-R*.22,0,sx,sy,R);
  sbody.addColorStop(0,'#fffad0');sbody.addColorStop(.25,'#ffdd40');sbody.addColorStop(.65,'#e06800');sbody.addColorStop(1,'#5c1e00');
  ctx.beginPath();ctx.arc(sx,sy,R,0,Math.PI*2);ctx.fillStyle=sbody;ctx.fill();
  var spec=ctx.createRadialGradient(sx-R*.34,sy-R*.34,0,sx-R*.16,sy-R*.16,R*.52);
  spec.addColorStop(0,'rgba(255,252,230,0.52)');spec.addColorStop(1,'rgba(255,252,230,0)');
  ctx.beginPath();ctx.arc(sx,sy,R,0,Math.PI*2);ctx.fillStyle=spec;ctx.fill();
  var slim=ctx.createRadialGradient(sx,sy,R*.14,sx,sy,R*1.05);
  slim.addColorStop(0,'rgba(0,0,0,0)');slim.addColorStop(.5,'rgba(0,0,0,0.14)');slim.addColorStop(1,'rgba(0,0,0,0.72)');
  ctx.beginPath();ctx.arc(sx,sy,R,0,Math.PI*2);ctx.fillStyle=slim;ctx.fill();
  ctx.save();ctx.globalCompositeOperation='screen';
  ctx.shadowColor='rgba(255,200,60,0.90)';ctx.shadowBlur=10;ctx.fillStyle='rgba(255,240,140,0.95)';
  var lfs=Math.max(8,Math.round(R*.60));
  ctx.font='600 '+lfs+'px "DM Mono",monospace';ctx.textAlign='center';ctx.textBaseline='bottom';
  ctx.fillText('LYLA',sx,sy-R-4);ctx.restore();ctx.restore();
}

function drawBlackHole(t){
  var sx=SX(),sy=SY(),R=sunR();
  var bhP=Math.max(0,(20-STATE.waterline)/20);
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var ri=8;ri>=1;ri--){
    ctx.beginPath();ctx.arc(sx,sy,R*(1.5+ri*2.8),0,Math.PI*2);
    ctx.strokeStyle='rgba(200,40,10,'+(.04/ri*bhP)+')';ctx.lineWidth=.6;ctx.stroke();
  }
  ctx.globalCompositeOperation='source-over';
  var ehg=ctx.createRadialGradient(sx,sy,0,sx,sy,R*2.5);
  ehg.addColorStop(0,'rgba(0,0,0,1)');ehg.addColorStop(.5,'rgba(5,0,0,0.92)');ehg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.beginPath();ctx.arc(sx,sy,R*2.5,0,Math.PI*2);ctx.fillStyle=ehg;ctx.fill();
  ctx.globalCompositeOperation='screen';
  var hg=ctx.createRadialGradient(sx,sy,R*.5,sx,sy,R*3.5);
  hg.addColorStop(0,'rgba(220,60,20,'+(0.55*bhP)+')');hg.addColorStop(.4,'rgba(120,10,5,'+(0.18*bhP)+')');hg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.beginPath();ctx.arc(sx,sy,R*3.5,0,Math.PI*2);ctx.fillStyle=hg;ctx.fill();
  ctx.restore();
}

function drawParticles(dt){
  if(!PAR.length)return;
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=PAR.length-1;i>=0;i--){
    var p=PAR[i];p.x+=p.vx*dt*60*.016;p.y+=p.vy*dt*60*.016;p.vy+=p.grav;p.alpha-=p.decay;
    if(p.alpha<=0){PAR.splice(i,1);continue;}
    ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fillStyle='rgba('+p.col+','+Math.max(0,p.alpha).toFixed(3)+')';ctx.fill();
  }
  ctx.restore();
}

function drawShockwaves(dt){
  if(!SWS.length)return;
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=SWS.length-1;i>=0;i--){
    var sw=SWS[i];sw.r+=dt*280;sw.alpha*=.96;
    if(sw.r>=sw.maxR||sw.alpha<.005){SWS.splice(i,1);continue;}
    var prog=sw.r/sw.maxR;
    ctx.beginPath();ctx.arc(sw.x,sw.y,sw.r,0,Math.PI*2);ctx.strokeStyle='rgba('+sw.col+','+sw.alpha.toFixed(3)+')';ctx.lineWidth=(1-prog)*3+.5;ctx.stroke();
  }
  ctx.restore();
}

function drawComet(t,dt){
  if(t>nextComet&&!COMET.active){COMET.x=W*.20+Math.random()*W*.55;COMET.y=-4;COMET.vx=.5+Math.random()*.7;COMET.vy=.4+Math.random()*.5;COMET.life=0;COMET.maxLife=1.5+Math.random()*1.4;COMET.active=true;nextComet=t+22000+Math.random()*38000;}
  if(!COMET.active)return;
  COMET.life+=dt;if(COMET.life>COMET.maxLife||COMET.y>H+20){COMET.active=false;return;}
  COMET.x+=COMET.vx*dt*60*.013;COMET.y+=COMET.vy*dt*60*.013;
  var prog=COMET.life/COMET.maxLife;
  var al=prog<.15?prog/.15:Math.max(0,1-(prog-.15)/.85);
  var tl=80,tx=COMET.x-COMET.vx*tl*.013,ty=COMET.y-COMET.vy*tl*.013;
  var cg=ctx.createLinearGradient(tx,ty,COMET.x,COMET.y);
  cg.addColorStop(0,'rgba(150,205,255,0)');cg.addColorStop(.5,'rgba(170,215,255,'+(al*.20)+')');cg.addColorStop(1,'rgba(210,235,255,'+(al*.72)+')');
  ctx.save();ctx.globalCompositeOperation='screen';ctx.beginPath();ctx.moveTo(tx,ty);ctx.lineTo(COMET.x,COMET.y);ctx.strokeStyle=cg;ctx.lineWidth=.8;ctx.stroke();
  ctx.beginPath();ctx.arc(COMET.x,COMET.y,1.3,0,Math.PI*2);ctx.fillStyle='rgba(195,225,255,'+(al*.90)+')';ctx.fill();ctx.restore();
}

function drawMeteors(t,dt){
  if(t>nextMet&&!metActive){
    METEORS=[];var n=16+Math.floor(Math.random()*20);
    for(var i=0;i<n;i++)METEORS.push({x:Math.random()*W*.8+W*.05,y:-10-Math.random()*60,vx:.5+Math.random()*.8,vy:.4+Math.random()*.7,length:40+Math.random()*80,alpha:.55+Math.random()*.35,life:0,maxLife:1.2+Math.random()*1.0,delay:Math.random()*3000,col:Math.random()<.7?'195,220,255':'255,220,180',active:false});
    metActive=true;metEnd=t+7000;nextMet=t+50000+Math.random()*60000;
  }
  if(!metActive)return;
  if(t>metEnd&&METEORS.every(function(m){return m.life>=m.maxLife;})){metActive=false;METEORS=[];return;}
  var elapsed=t-(metEnd-7000);
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<METEORS.length;i++){
    var m=METEORS[i];if(elapsed<m.delay)continue;if(!m.active)m.active=true;
    m.life+=dt;if(m.life>=m.maxLife||m.y>H+20)continue;
    m.x+=m.vx*dt*60*.014;m.y+=m.vy*dt*60*.014;
    var prog2=m.life/m.maxLife;
    var al2=prog2<.10?(prog2/.10)*m.alpha:Math.max(0,m.alpha*(1-(prog2-.10)/.90));
    var tx2=m.x-m.vx*m.length*.013,ty2=m.y-m.vy*m.length*.013;
    var mg=ctx.createLinearGradient(tx2,ty2,m.x,m.y);
    mg.addColorStop(0,'rgba('+m.col+',0)');mg.addColorStop(.5,'rgba('+m.col+','+(al2*.25)+')');mg.addColorStop(1,'rgba('+m.col+','+al2+')');
    ctx.beginPath();ctx.moveTo(tx2,ty2);ctx.lineTo(m.x,m.y);ctx.strokeStyle=mg;ctx.lineWidth=.9;ctx.stroke();
    ctx.beginPath();ctx.arc(m.x,m.y,1.1,0,Math.PI*2);ctx.fillStyle='rgba('+m.col+','+al2+')';ctx.fill();
  }
  ctx.restore();
}

function drawHUD(){
  ctx.save();ctx.font='300 7px "DM Mono",monospace';ctx.textBaseline='bottom';
  ctx.fillStyle='rgba(150,205,255,0.12)';ctx.textAlign='left';
  ctx.fillText('Choice(t)='+STATE.choice_count+'  ENT='+Math.round(STATE.entropy)+'  STB='+Math.round(STATE.stability)+'  RSC='+Math.round(STATE.resources)+'  WL='+Math.round(STATE.waterline)+(STATE.blackHole?' ⚠ COLLAPSE':''),14,H-56);
  ctx.fillStyle='rgba(150,205,255,0.08)';ctx.textAlign='right';
  ctx.fillText('FATE™ DETERMINISTIC v36 | '+activeRoute.toUpperCase(),W-14,H-56);
  ctx.restore();
}

/* ── FPS ── */
var _fF=0,_fL=0;
function monFPS(ts){_fF++;if(ts-_fL>2000){var fps=_fF/((ts-_fL)/1000);FPS_LOW=fps<28;_fF=0;_fL=ts;}}

/* ── MAIN LOOP ── */
function loop(ts){
  if(!lastTime)lastTime=ts;
  var dt=Math.min((ts-lastTime)/1000,.05);
  lastTime=ts;monFPS(ts);updateWaterline();
  try{
    drawBg(ts);drawFilaments(ts);drawAurora(ts);drawStars(ts);drawDust(ts);
    drawFateTexts(dt);drawMeteors(ts,dt);drawComet(ts,dt);
    drawIonTrails();drawOrbits();drawAsteroids(dt);drawPlanets(dt,ts);
    drawWormhole(ts,dt);drawFlares(ts,dt);drawSun(ts);
    drawParticles(dt);drawShockwaves(dt);drawHUD();
  }catch(e){console.error('[v36]',e);}
  requestAnimationFrame(loop);
}
requestAnimationFrame(loop);

/* ── INIT ── */
doResize();initFT();

/* ── HUD UPDATE ── */
function updateHUD(){
  var wl=Math.round(STATE.waterline);
  var st=wl>60?'SAFE':wl>30?'WARN':'CRIT';
  var wlEl=document.getElementById('wl-val');
  var stEl=document.getElementById('wl-status');
  if(wlEl)wlEl.textContent='WATERLINE '+wl;
  if(stEl){stEl.textContent=st;stEl.className='wl-dot '+(wl>60?'':'wl>30?\'warn\':\'crit\'');}
  if(stEl)stEl.className='wl-dot'+(wl<=20?' crit':wl<=40?' warn':'');
  var bCrit=document.getElementById('b-crit');
  if(bCrit)bCrit.className='tb-badge '+(wl>60?'ok':wl>30?'':'off');
  var h={ent:Math.round(STATE.entropy),stb:Math.round(STATE.stability),rsc:Math.round(STATE.resources),wl:wl,choice:STATE.choice_count>=4?'≥1':'LOW',route:activeRoute.toUpperCase()};
  var _t=function(id,v){var e=document.getElementById(id);if(e)e.textContent=v;};
  _t('h-ent',h.ent);_t('h-stb',h.stb);_t('h-rsc',h.rsc);_t('h-wl',h.wl);_t('h-choice',h.choice);_t('h-route',h.route);
  var wlV=document.getElementById('h-wl');
  if(wlV)wlV.className='hud-stat-v'+(wl<=20?' crit':wl<=40?' warn':'');
}
setInterval(updateHUD,500);

/* ── ROUTE ── */
window.setRoute=function(r){
  if(!ROUTE_HUE[r])return;
  activeRoute=r;STATE.activeRoute=r;_tgtHue=ROUTE_HUE[r]||208;
  document.querySelectorAll('.rpill,.ctx-tag').forEach(function(el){el.classList.toggle('active',el.dataset.r===r);});
  document.getElementById('h-route').textContent=r.toUpperCase();
  var ap=PLANETS.find(function(p){return p.id===r;});
  if(ap){
    var sx=SX(),sy=SY(),mr=maxOrb(),orb=ap.orb*mr;
    var px=sx+Math.cos(ap.ang)*orb,py=sy+Math.sin(ap.ang)*orb;
    var col=ap.glow.replace('rgba(','').split(',').slice(0,3).join(',');
    shockwave(px,py,col,false);spawnEx(px,py,col,55);
  }
};

/* ── TIME ── */
function tick(){var e=document.getElementById('tb-time');if(e)e.textContent=new Date().toLocaleTimeString('th-TH',{hour:'2-digit',minute:'2-digit'});}
tick();setInterval(tick,30000);

/* ── THINKING TOGGLE (demo) ── */
var _thinkT;
document.addEventListener('keydown',function(e){
  if(e.key==='t'||e.key==='T'){STATE.thinking=!STATE.thinking;clearTimeout(_thinkT);if(STATE.thinking)_thinkT=setTimeout(function(){STATE.thinking=false;},4000);}
  if(e.key==='r'||e.key==='R'){STATE.entropy=Math.random()*80+10;STATE.stability=Math.random()*80+10;STATE.resources=Math.random()*80+10;}
});

})();

/* ── INTRO ── */
(function(){
  var fill=document.getElementById('intro-fill');
  var intro=document.getElementById('intro');
  if(fill)setTimeout(function(){fill.style.width='100%';},100);
  setTimeout(function(){if(intro)intro.classList.add('fade');},2800);
  setTimeout(function(){if(intro&&intro.parentNode)intro.parentNode.removeChild(intro);},4200);
})();
</script>
</body>
</html>
