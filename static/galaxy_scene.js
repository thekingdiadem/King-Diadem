/* ============================================================
   KING DIADEM — Galaxy Scene v39 SCI-FI 4D CINEMATIC
   Deep space. Volumetric. Alive. Every planet a world.
   Sun bleeds off top. Planets cascade with orbital rings.
   Chromatic aberration. Lens flare. Particle nebula.
   ============================================================ */
(function(){
'use strict';

var cv=document.getElementById('galaxy');
if(!cv)return;
var ctx=cv.getContext('2d',{alpha:true});
var W=0,H=0,T=0,_raf=null;
var activeRoute='general';
var ROUTE_HUE={general:208,risk:22,collapse:338,survival:142,civil:268,vega:286};
var _tgtHue=208,_curHue=208;

/* ── RESIZE ── */
var _rT;
function doResize(){
  W=cv.width=window.innerWidth;
  H=cv.height=window.innerHeight;
  buildParticles();buildStars();
}
window.addEventListener('resize',function(){clearTimeout(_rT);_rT=setTimeout(doResize,60);},{passive:true});

/* ── STAR FIELD — dense, multi-layer, blue-white ── */
var STARS=[];
function buildStars(){
  STARS=[];
  var n=Math.min(420,Math.floor(W*H/3200));
  for(var i=0;i<n;i++){
    var sz=Math.random();
    STARS.push({
      x:Math.random()*W,y:Math.random()*H,
      r:sz<0.55?0.35+Math.random()*0.55:sz<0.85?0.55+Math.random()*0.95:0.95+Math.random()*1.8,
      a:0.08+Math.random()*0.70,
      ph:Math.random()*Math.PI*2,
      sp:0.18+Math.random()*0.80,
      hue:Math.random()<0.30?200+Math.random()*35:Math.random()<0.12?28+Math.random()*18:0,
      cross:Math.random()<0.04 /* bright cross-star */
    });
  }
}

/* ── NEBULA PARTICLES — volumetric dust cloud ── */
var PARTS=[];
function buildParticles(){
  PARTS=[];
  var n=Math.min(180,Math.floor(W*H/9000));
  for(var i=0;i<n;i++){
    PARTS.push({
      x:Math.random()*W,y:Math.random()*H,
      r:8+Math.random()*28,
      a:0.008+Math.random()*0.022,
      ph:Math.random()*Math.PI*2,
      sp:0.08+Math.random()*0.25,
      hue:180+Math.random()*60
    });
  }
}

/* ── PLANET TABLE ── */
var PT=[
  {id:'mercury',label:'GENERAL', route:'general', yF:0.215,rf:0.038,
   colors:['#f0c888','#c89040','#956020','#6a3e10','#3c2008'],limb:'rgba(240,190,110,0.62)'},
  {id:'venus',  label:'RISK',    route:'risk',    yF:0.345,rf:0.056,
   colors:['#ffe8a8','#ecc040','#c88520','#9c5c10','#683808'],limb:'rgba(255,228,130,0.65)',bands:true},
  {id:'earth',  label:'SURVIVAL',route:'survival',yF:0.475,rf:0.062,
   colors:['#88c8f5','#2878d0','#1658a8','#0c3870','#082448'],limb:'rgba(110,195,255,0.65)',earth:true},
  {id:'mars',   label:'COLLAPSE',route:'collapse',yF:0.610,rf:0.048,
   colors:['#e8a078','#c05838','#985028','#703018','#481808'],limb:'rgba(235,155,105,0.62)',mars:true},
  {id:'jupiter',label:'CIVIL',   route:'civil',   yF:0.760,rf:0.088,
   colors:['#f0e0c0','#d8c090','#b89860','#8a6830','#603e18'],limb:'rgba(242,215,165,0.52)',jupiter:true},
  {id:'vega',   label:'VEGA',    route:'vega',    yF:0.940,rf:0.036,
   colors:['#e0d0ff','#9870e0','#6840b8','#402080','#200848'],limb:'rgba(195,165,255,0.68)',vega:true}
];

function R(p){return Math.min(W,H)*p.rf;}

/* ── DRAW DEEP SPACE BG ── */
function drawBg(){
  ctx.clearRect(0,0,W,H);

  /* layered gradient — blue-black deep space */
  var bg=ctx.createRadialGradient(W*.5,H*.08,0,W*.5,H*.55,Math.max(W,H)*1.05);
  bg.addColorStop(0,'#0e1830');
  bg.addColorStop(0.12,'#0a1222');
  bg.addColorStop(0.30,'#07101c');
  bg.addColorStop(0.55,'#050c16');
  bg.addColorStop(0.78,'#030a12');
  bg.addColorStop(1,'#02060c');
  ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);

  /* atmospheric hue shift from route */
  _curHue+=(_tgtHue-_curHue)*0.006;
  ctx.save();ctx.globalCompositeOperation='screen';

  /* blue nebula clouds — LEFT */
  var nb1=ctx.createRadialGradient(W*.15,H*.38,0,W*.15,H*.38,W*.52);
  nb1.addColorStop(0,'rgba(22,58,145,0.13)');nb1.addColorStop(.5,'rgba(14,38,100,0.06)');nb1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb1;ctx.fillRect(0,0,W,H);

  /* blue nebula clouds — RIGHT */
  var nb2=ctx.createRadialGradient(W*.88,H*.65,0,W*.88,H*.65,W*.48);
  nb2.addColorStop(0,'rgba(18,50,130,0.10)');nb2.addColorStop(.6,'rgba(10,30,80,0.04)');nb2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb2;ctx.fillRect(0,0,W,H);

  /* center spine glow — subtle backlight behind planet column */
  var spine=ctx.createRadialGradient(W*.5,H*.5,0,W*.5,H*.5,W*.38);
  spine.addColorStop(0,'rgba(30,65,160,0.055)');spine.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=spine;ctx.fillRect(0,0,W,H);

  /* route color tint */
  var rt=ctx.createRadialGradient(W*.5,H*.5,0,W*.5,H*.5,W*.75);
  rt.addColorStop(0,'hsla('+_curHue+',60%,22%,0.030)');rt.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=rt;ctx.fillRect(0,0,W,H);
  ctx.restore();
}

/* ── STARS ── */
function drawStars(){
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var tw=s.a*(0.48+0.52*Math.sin(T*s.sp*0.00052+s.ph));
    if(s.cross&&tw>s.a*.7){
      /* bright cross diffraction spike */
      ctx.save();
      var cl=s.hue>0?'hsla('+s.hue+',60%,92%,'+tw.toFixed(3)+')':'rgba(215,228,248,'+tw.toFixed(3)+')';
      ctx.strokeStyle=cl;ctx.lineWidth=0.5;
      ctx.beginPath();ctx.moveTo(s.x-s.r*3.5,s.y);ctx.lineTo(s.x+s.r*3.5,s.y);ctx.stroke();
      ctx.beginPath();ctx.moveTo(s.x,s.y-s.r*3.5);ctx.lineTo(s.x,s.y+s.r*3.5);ctx.stroke();
      ctx.restore();
    }
    ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fillStyle=s.hue>0?'hsla('+s.hue+',55%,92%,'+tw.toFixed(3)+')':'rgba(205,222,248,'+tw.toFixed(3)+')';
    ctx.fill();
  }
  ctx.restore();
}

/* ── NEBULA PARTICLES ── */
function drawParticles(){
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<PARTS.length;i++){
    var p=PARTS[i];
    var pa=p.a*(0.5+0.5*Math.sin(T*p.sp*0.00025+p.ph));
    var g=ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r);
    g.addColorStop(0,'hsla('+p.hue+',55%,55%,'+pa.toFixed(3)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g;ctx.fillRect(p.x-p.r,p.y-p.r,p.r*2,p.r*2);
  }
  ctx.restore();
}

/* ── SUN — cinematic, bleeding off top ── */
function drawSun(){
  var cx=W*.50,cy=H*-0.025;
  var Rv=Math.min(W,H);
  var Rs=Rv*(W<480?0.52:0.46);

  ctx.save();

  /* volumetric corona — 3 layers */
  ctx.globalCompositeOperation='screen';
  [
    [Rs*4.5,'rgba(255,100,10,0.055)'],
    [Rs*2.8,'rgba(255,120,15,0.10)'],
    [Rs*1.65,'rgba(255,140,20,0.18)']
  ].forEach(function(c){
    var g=ctx.createRadialGradient(cx,cy,Rs*.35,cx,cy,c[0]);
    g.addColorStop(0,c[1]);g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  });

  /* chromosphere red rim */
  var chr=ctx.createRadialGradient(cx,cy,Rs*.86,cx,cy,Rs*1.22);
  chr.addColorStop(0,'rgba(160,20,0,0)');
  chr.addColorStop(.32,'rgba(220,48,6,0.48)');
  chr.addColorStop(.62,'rgba(255,72,12,0.28)');
  chr.addColorStop(.85,'rgba(200,40,0,0.10)');
  chr.addColorStop(1,'rgba(0,0,0,0)');
  ctx.globalCompositeOperation='source-over';
  ctx.fillStyle=chr;ctx.beginPath();ctx.arc(cx,cy,Rs*1.22,0,Math.PI*2);ctx.fill();

  /* photosphere body */
  var ph=ctx.createRadialGradient(cx-Rs*.22,cy-Rs*.16,0,cx+Rs*.06,cy+Rs*.08,Rs);
  ph.addColorStop(0,'#fff8d8');
  ph.addColorStop(.10,'#ffe055');
  ph.addColorStop(.30,'#ffaa18');
  ph.addColorStop(.55,'#ff6808');
  ph.addColorStop(.78,'#cc2800');
  ph.addColorStop(1,'#881200');
  ctx.fillStyle=ph;ctx.beginPath();ctx.arc(cx,cy,Rs,0,Math.PI*2);ctx.fill();

  /* surface texture — animated granulation */
  ctx.save();ctx.beginPath();ctx.arc(cx,cy,Rs,0,Math.PI*2);ctx.clip();
  ctx.globalCompositeOperation='overlay';
  for(var i=0;i<18;i++){
    var a=(i/18)*Math.PI*2+T*.000055;
    var gx=cx+Math.cos(a)*Rs*.38*(0.4+0.6*Math.abs(Math.sin(i*1.9)));
    var gy=cy+Math.sin(a)*Rs*.30*(0.4+0.6*Math.abs(Math.cos(i*2.3)));
    var gr2=Rs*(0.055+0.040*Math.abs(Math.sin(i*.8+T*.00008)));
    var gg=ctx.createRadialGradient(gx,gy,0,gx,gy,gr2);
    gg.addColorStop(0,'rgba(255,240,100,0.20)');gg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=gg;ctx.fillRect(0,0,W,H);
  }
  ctx.restore();

  /* specular highlight */
  ctx.globalCompositeOperation='screen';
  var hi=ctx.createRadialGradient(cx-Rs*.16,cy-Rs*.09,0,cx,cy,Rs);
  hi.addColorStop(0,'rgba(255,252,200,0.55)');
  hi.addColorStop(.38,'rgba(255,210,80,0.08)');
  hi.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=hi;ctx.beginPath();ctx.arc(cx,cy,Rs,0,Math.PI*2);ctx.fill();

  /* lens flare — 4D signature */
  ctx.globalCompositeOperation='screen';
  var lx=cx+Rs*.12,ly=cy+Rs*.08;
  var lf=ctx.createRadialGradient(lx,ly,0,lx,ly,Rs*.28);
  lf.addColorStop(0,'rgba(255,255,240,0.28)');
  lf.addColorStop(.45,'rgba(255,220,100,0.06)');
  lf.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=lf;ctx.fillRect(0,0,W,H);

  ctx.restore();
}

/* ── ORBIT RING — glowing ellipse ── */
function drawOrbit(py,rx,ry,isActive){
  ctx.save();

  /* outer soft glow */
  if(isActive){
    ctx.globalCompositeOperation='screen';
    var glow=ctx.createRadialGradient(W*.5,py,0,W*.5,py,ry*2.5);
    glow.addColorStop(0,'rgba(100,160,255,0.06)');glow.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=glow;ctx.fillRect(0,0,W,H);
  }

  /* main ring gradient */
  ctx.globalCompositeOperation='screen';
  var g=ctx.createLinearGradient(W*.5-rx,py,W*.5+rx,py);
  var a=isActive?.50:.14;
  g.addColorStop(0,'rgba(100,150,220,0)');
  g.addColorStop(.14,'rgba(140,185,245,'+(a*.55)+')');
  g.addColorStop(.35,'rgba(175,210,255,'+(a*.82)+')');
  g.addColorStop(.50,'rgba(200,225,255,'+a+')');
  g.addColorStop(.65,'rgba(175,210,255,'+(a*.82)+')');
  g.addColorStop(.86,'rgba(140,185,245,'+(a*.55)+')');
  g.addColorStop(1,'rgba(100,150,220,0)');

  ctx.strokeStyle=g;
  ctx.lineWidth=isActive?1.8:.65;
  ctx.beginPath();ctx.ellipse(W*.5,py,rx,ry,0,0,Math.PI*2);ctx.stroke();

  /* moving shimmer dot on active ring */
  if(isActive){
    var ang=T*.00048;
    var sx=W*.5+rx*Math.cos(ang),sy=py+ry*Math.sin(ang);
    ctx.globalCompositeOperation='screen';
    var sg=ctx.createRadialGradient(sx,sy,0,sx,sy,9);
    sg.addColorStop(0,'rgba(220,238,255,0.98)');
    sg.addColorStop(.4,'rgba(180,215,255,0.40)');
    sg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sg;ctx.fillRect(0,0,W,H);
    /* chromatic aberration on dot */
    ctx.globalAlpha=0.35;
    var sa=ctx.createRadialGradient(sx+2,sy,0,sx+2,sy,5);
    sa.addColorStop(0,'rgba(255,60,60,0.80)');sa.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sa;ctx.fillRect(0,0,W,H);
    ctx.globalAlpha=1;
  }

  ctx.restore();
}

/* ── PLANET CORE DRAW ── */
function drawPlanetBody(x,y,r,p){
  var c=p.colors;
  var b=ctx.createRadialGradient(x-r*.28,y-r*.22,0,x+r*.10,y+r*.12,r*1.04);
  b.addColorStop(0,c[0]);b.addColorStop(.22,c[1]);b.addColorStop(.50,c[2]);b.addColorStop(.76,c[3]);b.addColorStop(1,c[4]);
  ctx.fillStyle=b;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
}
function addLimb(x,y,r,color){
  ctx.save();ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*.30,y-r*.24,0,x,y,r*1.04);
  g.addColorStop(0,color);g.addColorStop(.42,'rgba(255,255,255,0.03)');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();
}
function addDark(x,y,r){
  ctx.save();ctx.globalCompositeOperation='multiply';
  var g=ctx.createRadialGradient(x+r*.36,y+r*.30,0,x,y,r*1.04);
  g.addColorStop(0,'rgba(0,0,0,0.65)');g.addColorStop(.42,'rgba(0,0,0,0.22)');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();
}
function addSpecular(x,y,r){
  ctx.save();ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*.25,y-r*.20,0,x-r*.05,y-r*.05,r*.65);
  g.addColorStop(0,'rgba(255,255,255,0.18)');g.addColorStop(.5,'rgba(255,255,255,0.04)');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();
}
/* atmosphere rim glow */
function addAtmosphere(x,y,r,color){
  ctx.save();ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x,y,r*.82,x,y,r*1.28);
  g.addColorStop(0,color);g.addColorStop(.5,color.replace(/[\d.]+\)$/,'0.03)'));g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);ctx.restore();
}

/* planet-specific overlays */
function earthDetail(x,y,r){
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  /* continents */
  [[.06,-.18,.26,.20,'4a8c30'],[.28,.06,.20,.24,'3a7828'],[-.26,.10,.18,.20,'558832'],[-.04,.34,.28,.17,'8aaa60']].forEach(function(c){
    var rgb=c[4].match(/../g).map(function(h){return parseInt(h,16);});
    var eg=ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0,x+c[0]*r,y+c[1]*r,c[2]*r);
    eg.addColorStop(0,'rgba('+rgb+',0.92)');eg.addColorStop(.52,'rgba('+rgb+',0.55)');eg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=eg;ctx.fillRect(0,0,W,H);
  });
  /* polar ice */
  var ic=ctx.createRadialGradient(x,y-r*.80,0,x,y-r*.80,r*.26);
  ic.addColorStop(0,'rgba(235,248,255,0.85)');ic.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ic;ctx.fillRect(0,0,W,H);
  ctx.restore();
  addAtmosphere(x,y,r,'rgba(65,140,255,0.18)');
}
function venusDetail(x,y,r){
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  ctx.globalCompositeOperation='overlay';
  for(var i=0;i<4;i++){
    var by=y-r*.55+i*r*.38+Math.sin(T*.00013+i*1.2)*r*.035;
    var bd=ctx.createLinearGradient(x-r,by,x+r,by+r*.09);
    bd.addColorStop(0,'rgba(255,235,155,0)');bd.addColorStop(.5,'rgba(255,235,155,0.26)');bd.addColorStop(1,'rgba(255,235,155,0)');
    ctx.fillStyle=bd;ctx.fillRect(x-r,by,r*2,r*.18);
  }
  ctx.restore();
  addAtmosphere(x,y,r,'rgba(255,210,80,0.14)');
}
function marsDetail(x,y,r){
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  var pc=ctx.createRadialGradient(x,y-r*.78,0,x,y-r*.78,r*.25);
  pc.addColorStop(0,'rgba(238,228,215,0.80)');pc.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=pc;ctx.fillRect(0,0,W,H);
  ctx.restore();
  addAtmosphere(x,y,r,'rgba(200,100,50,0.10)');
}
function jupiterDetail(x,y,r){
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  [[-0.60,0.17,'rgba(155,105,52,0.58)'],[-0.38,0.13,'rgba(196,155,90,0.42)'],[-0.18,0.19,'rgba(136,85,38,0.64)'],
   [0.06,0.15,'rgba(175,125,62,0.47)'],[0.25,0.19,'rgba(116,70,28,0.60)'],[0.49,0.13,'rgba(185,140,72,0.44)'],[0.66,0.17,'rgba(145,95,45,0.54)']].forEach(function(bd){
    var lg=ctx.createLinearGradient(x-r,y+bd[0]*r,x+r,y+(bd[0]+bd[1])*r);
    var ct=bd[2].replace(/[\d.]+\)$/,'0)');
    lg.addColorStop(0,ct);lg.addColorStop(.5,bd[2]);lg.addColorStop(1,ct);
    ctx.fillStyle=lg;ctx.fillRect(x-r,y+bd[0]*r,r*2,bd[1]*r);
  });
  /* GRS */
  var gs=ctx.createRadialGradient(x+r*.22,y+r*.12,0,x+r*.22,y+r*.12,r*.19);
  gs.addColorStop(0,'rgba(175,45,16,0.85)');gs.addColorStop(.5,'rgba(155,35,10,0.55)');gs.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=gs;ctx.fillRect(0,0,W,H);
  ctx.restore();
}
function vegaDetail(x,y,r){
  ctx.save();ctx.globalCompositeOperation='screen';
  /* outer energy glow */
  var gl=ctx.createRadialGradient(x,y,r*.5,x,y,r*2.0);
  gl.addColorStop(0,'rgba(150,90,255,0.28)');
  gl.addColorStop(.4,'rgba(100,55,200,0.10)');
  gl.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=gl;ctx.fillRect(0,0,W,H);
  /* energy grid */
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  for(var i=0;i<6;i++){
    var a2=i*Math.PI/3+T*.0002;
    ctx.beginPath();
    ctx.moveTo(x+Math.cos(a2)*r*.08,y+Math.sin(a2)*r*.08);
    ctx.lineTo(x+Math.cos(a2)*r*.88,y+Math.sin(a2)*r*.88);
    ctx.strokeStyle='rgba(180,148,255,0.20)';ctx.lineWidth=0.7;ctx.stroke();
  }
  ctx.restore();
  ctx.restore();
  addAtmosphere(x,y,r,'rgba(150,90,255,0.22)');
}
function moonDraw(x,y,r){
  ctx.save();
  var b=ctx.createRadialGradient(x-r*.24,y-r*.20,0,x+r*.10,y+r*.08,r*1.04);
  b.addColorStop(0,'#d8d0c2');b.addColorStop(.38,'#a89882');b.addColorStop(.68,'#7a6a52');b.addColorStop(1,'#4a3c2c');
  ctx.fillStyle=b;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
  addLimb(x,y,r,'rgba(215,205,188,0.52)');addDark(x,y,r);addSpecular(x,y,r);
  ctx.restore();
}

/* ── DRAW ONE PLANET ── */
function drawPlanet(p){
  var px=W*.50,py=H*p.yF,pr=R(p);
  ctx.save();
  drawPlanetBody(px,py,pr,p);
  if(p.earth)  earthDetail(px,py,pr);
  if(p.bands)  venusDetail(px,py,pr);
  if(p.mars)   marsDetail(px,py,pr);
  if(p.jupiter)jupiterDetail(px,py,pr);
  if(p.vega)   vegaDetail(px,py,pr);
  addLimb(px,py,pr,p.limb);
  addDark(px,py,pr);
  addSpecular(px,py,pr);
  if(p.id==='earth') moonDraw(px+pr*1.58,py+pr*.32,pr*.32);
  ctx.restore();
}

/* ── ACTIVE PLANET EFFECTS ── */
function drawActiveEffects(p){
  var px=W*.50,py=H*p.yF,pr=R(p);
  ctx.save();ctx.globalCompositeOperation='screen';
  /* gold pulse glow */
  var pulse=0.70+0.30*Math.sin(T*.0032);
  var g=ctx.createRadialGradient(px,py,pr*.55,px,py,pr*2.4);
  g.addColorStop(0,'rgba(200,168,75,'+(0.28*pulse).toFixed(3)+')');
  g.addColorStop(.45,'rgba(200,168,75,'+(0.10*pulse).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  /* chromatic aberration ring */
  ctx.globalAlpha=0.18*pulse;
  ctx.strokeStyle='rgba(255,50,50,0.60)';ctx.lineWidth=1.2;
  ctx.beginPath();ctx.arc(px+1.5,py,pr*1.08,0,Math.PI*2);ctx.stroke();
  ctx.strokeStyle='rgba(50,50,255,0.60)';
  ctx.beginPath();ctx.arc(px-1.5,py,pr*1.08,0,Math.PI*2);ctx.stroke();
  ctx.globalAlpha=1;
  ctx.restore();
}

/* ── LABEL ── */
function drawLabel(p){
  var px=W*.50,py=H*p.yF,pr=R(p);
  var isAct=p.route===activeRoute;
  var fs=Math.max(8,Math.min(13,pr*.50));
  ctx.save();
  ctx.font='500 '+fs+'px "DM Mono",monospace';
  ctx.textAlign='center';ctx.textBaseline='top';
  if(isAct){
    /* gold glow label */
    ctx.shadowColor='rgba(200,168,75,0.80)';
    ctx.shadowBlur=8;
    ctx.fillStyle='rgba(245,205,100,0.95)';
  } else {
    ctx.fillStyle='rgba(130,170,220,0.46)';
  }
  ctx.fillText(p.label,px,py+pr+9);
  ctx.restore();
}

/* ── CLICK ── */
cv.addEventListener('click',function(e){
  var rc=cv.getBoundingClientRect(),cx=e.clientX-rc.left,cy=e.clientY-rc.top;
  PT.forEach(function(p){
    var px=W*.5,py=H*p.yF,pr=R(p),dx=cx-px,dy=cy-py;
    if(dx*dx+dy*dy<(pr*1.65)*(pr*1.65)) window.KD_setRoute&&window.KD_setRoute(p.route);
  });
},{passive:true});
cv.addEventListener('touchend',function(e){
  if(e.changedTouches.length===1){var tc=e.changedTouches[0];cv.dispatchEvent(new MouseEvent('click',{clientX:tc.clientX,clientY:tc.clientY}));}
},{passive:true});

/* ── MAIN LOOP ── */
function loop(ts){
  if(!_raf)return;
  T=ts;
  try{
    drawBg();
    drawParticles();
    drawStars();
    /* orbits behind planets */
    PT.forEach(function(p){
      drawOrbit(H*p.yF,W*p.orx||W*.465,H*(p.ory||.028),p.route===activeRoute);
    });
    drawSun();
    /* active effects under planet */
    PT.forEach(function(p){ if(p.route===activeRoute) drawActiveEffects(p); });
    /* planets */
    PT.forEach(function(p){ drawPlanet(p); drawLabel(p); });
  }catch(e){console.error('[v39]',e);}
  _raf=requestAnimationFrame(loop);
}

/* orbit params per planet */
PT[0].orx=.455;PT[0].ory=.030;
PT[1].orx=.462;PT[1].ory=.028;
PT[2].orx=.465;PT[2].ory=.027;
PT[3].orx=.462;PT[3].ory=.027;
PT[4].orx=.462;PT[4].ory=.028;
PT[5].orx=.455;PT[5].ory=.026;

/* ── PUBLIC API ── */
window.KD_setState=function(s){};
window.KD_setRoute=function(r){
  if(!ROUTE_HUE[r])return;
  activeRoute=r;_tgtHue=ROUTE_HUE[r]||208;
  document.querySelectorAll('.rpill,.ctx-tag,.route-chip').forEach(function(el){el.classList.toggle('active',el.dataset.r===r);});
};
window.KD_pulse=function(){};
window.LYLA_thinking=function(){};
window.LYLA_answered=function(){};
window.setRoute=window.KD_setRoute;

/* ── INIT ── */
doResize();
_raf=true;
requestAnimationFrame(function(ts){T=ts;doResize();_raf=requestAnimationFrame(loop);});

})();
