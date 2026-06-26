/* ================================================================
   KING DIADEM — Galaxy Scene v42 MEGA CINEMATIC
   144-240hz · Delta-time · Every planet photo-real
   Sun · Mercury · Venus · Earth+Moon · Mars · Jupiter
   Saturn+Rings · Uranus · Neptune · Pluto · VEGA
   Nebula · Starfield · Asteroid belt · Kuiper belt
   ================================================================ */
(function(){
'use strict';

var cv=document.getElementById('galaxy');
if(!cv)return;
var ctx=cv.getContext('2d',{alpha:true,desynchronized:true});
var W=0,H=0,_raf=null,_last=0,_dt=0;
var activeRoute='general';
var ROUTE_HUE={general:208,risk:22,collapse:338,survival:142,civil:268,vega:286};
var _tgtHue=208,_curHue=208;
// FIX: isMobile declared at module scope — was only inside buildStars() causing ReferenceError in buildDust()
var isMobile=false;

function loop(now){
  _raf=requestAnimationFrame(loop);
  _dt=Math.min(now-_last,50);
  /* ── ADAPTIVE FRAME SKIP ──
     target 60fps base; at 144hz+ skip every other BG redraw
     but always update physics. Keeps GPU load stable.      */
  _last=now;
  render(_dt,now);
}

var _rT;
function doResize(){
  W=cv.width=window.innerWidth;
  H=cv.height=window.innerHeight;
  isMobile=(W<768);
  buildStars();buildDust();buildBelt();buildKuiper();
}
window.addEventListener('resize',function(){clearTimeout(_rT);_rT=setTimeout(doResize,80);},{passive:true});
window.addEventListener('KD:resize',function(){clearTimeout(_rT);_rT=setTimeout(doResize,80);},{passive:true});
document.addEventListener('visibilitychange',function(){
  if(document.hidden){if(_raf){cancelAnimationFrame(_raf);_raf=null;}}
  else{if(!_raf){_last=performance.now();_raf=requestAnimationFrame(loop);}}
},{passive:true});

/* ================================================================
   STAR FIELD — 600 stars, 5 layers, diffraction, pastel
   ================================================================ */
var STARS=[];
function buildStars(){
  STARS=[];
  var n=Math.min(isMobile?280:600,Math.floor(W*H/(isMobile?4200:2400)));
  for(var i=0;i<n;i++){
    var sz=Math.random();
    STARS.push({
      x:Math.random()*W, y:Math.random()*H,
      r:sz<0.45?0.25+Math.random()*0.40:
        sz<0.72?0.40+Math.random()*0.70:
        sz<0.90?0.70+Math.random()*1.00:
        sz<0.97?1.00+Math.random()*1.60:
               1.60+Math.random()*2.80,
      a:0.05+Math.random()*0.75,
      ph:Math.random()*Math.PI*2,
      sp:0.12+Math.random()*0.85,
      ct:Math.random()<0.28?'blue':Math.random()<0.14?'warm':Math.random()<0.08?'red':'white',
      cross:sz>0.96&&Math.random()<0.65,
      twinkle:Math.random()<0.70,
      pastel:Math.random()<0.16,
      pH:[265,285,305,185,200,340,10][Math.floor(Math.random()*7)]
    });
  }
}

function drawStars(now){
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var tw=s.twinkle?s.a*(0.40+0.60*Math.sin(now*s.sp*0.00046+s.ph)):s.a;
    var col;
    if(s.pastel) col='hsla('+s.pH+',26%,80%,'+tw.toFixed(3)+')';
    else if(s.ct==='blue') col='rgba(162,198,255,'+tw.toFixed(3)+')';
    else if(s.ct==='warm') col='rgba(255,225,180,'+tw.toFixed(3)+')';
    else if(s.ct==='red')  col='rgba(255,185,162,'+tw.toFixed(3)+')';
    else col='rgba(208,222,245,'+tw.toFixed(3)+')';

    if(s.cross&&tw>s.a*0.60){
      ctx.save();
      ctx.strokeStyle=col;ctx.lineWidth=0.42;
      var cl=s.r*4.2;
      ctx.beginPath();ctx.moveTo(s.x-cl,s.y);ctx.lineTo(s.x+cl,s.y);ctx.stroke();
      ctx.beginPath();ctx.moveTo(s.x,s.y-cl);ctx.lineTo(s.x,s.y+cl);ctx.stroke();
      ctx.lineWidth=0.20;ctx.globalAlpha=0.35;
      var cl2=cl*0.58;
      ctx.beginPath();ctx.moveTo(s.x-cl2,s.y-cl2);ctx.lineTo(s.x+cl2,s.y+cl2);ctx.stroke();
      ctx.beginPath();ctx.moveTo(s.x+cl2,s.y-cl2);ctx.lineTo(s.x-cl2,s.y+cl2);ctx.stroke();
      ctx.restore();
    }
    ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fillStyle=col;ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   VOLUMETRIC DUST — 240 pastel nebula particles
   ================================================================ */
var DUST=[];
function buildDust(){
  DUST=[];
  var n=Math.min(isMobile?80:240,Math.floor(W*H/(isMobile?9000:6000)));
  var hues=[265,278,295,185,198,205,335,350,15];
  for(var i=0;i<n;i++){
    DUST.push({
      x:Math.random()*W,y:Math.random()*H,
      r:10+Math.random()*48,
      a:0.004+Math.random()*0.020,
      ph:Math.random()*Math.PI*2,
      sp:0.045+Math.random()*0.165,
      hue:hues[Math.floor(Math.random()*hues.length)],
      sat:14+Math.random()*28,
      lum:52+Math.random()*26
    });
  }
}
function drawDust(now){
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<DUST.length;i++){
    var d=DUST[i];
    var da=d.a*(0.40+0.60*Math.sin(now*d.sp*0.00018+d.ph));
    var g=ctx.createRadialGradient(d.x,d.y,0,d.x,d.y,d.r);
    g.addColorStop(0,'hsla('+d.hue+','+d.sat+'%,'+d.lum+'%,'+da.toFixed(4)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g;ctx.fillRect(d.x-d.r,d.y-d.r,d.r*2,d.r*2);
  }
  ctx.restore();
}

/* ================================================================
   ASTEROID BELT — between Mars & Jupiter
   ================================================================ */
var BELT=[];
function buildBelt(){
  BELT=[];
  var n=Math.min(160,Math.floor(W/5));
  for(var i=0;i<n;i++){
    BELT.push({
      x:Math.random()*W,
      y:H*0.595+Math.random()*(H*0.048),
      r:0.35+Math.random()*1.90,
      a:0.05+Math.random()*0.35,
      ph:Math.random()*Math.PI*2,
      sp:0.07+Math.random()*0.30,
      vx:(Math.random()-0.5)*0.11
    });
  }
}
function drawBelt(dt,now){
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<BELT.length;i++){
    var b=BELT[i];
    b.x+=b.vx*(dt/16);
    if(b.x<-5)b.x=W+5;if(b.x>W+5)b.x=-5;
    var ba=b.a*(0.36+0.64*Math.sin(now*b.sp*0.00036+b.ph));
    ctx.beginPath();ctx.arc(b.x,b.y,b.r,0,Math.PI*2);
    ctx.fillStyle='rgba(182,172,158,'+ba.toFixed(3)+')';ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   KUIPER BELT — beyond Neptune/Pluto
   ================================================================ */
var KUIPER=[];
function buildKuiper(){
  KUIPER=[];
  var n=Math.min(80,Math.floor(W/8));
  for(var i=0;i<n;i++){
    KUIPER.push({
      x:Math.random()*W,
      y:H*0.945+Math.random()*(H*0.030),
      r:0.25+Math.random()*1.20,
      a:0.04+Math.random()*0.22,
      ph:Math.random()*Math.PI*2,
      sp:0.05+Math.random()*0.20,
      vx:(Math.random()-0.5)*0.06
    });
  }
}
function drawKuiper(dt,now){
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<KUIPER.length;i++){
    var k=KUIPER[i];
    k.x+=k.vx*(dt/16);
    if(k.x<-4)k.x=W+4;if(k.x>W+4)k.x=-4;
    var ka=k.a*(0.35+0.65*Math.sin(now*k.sp*0.00028+k.ph));
    ctx.beginPath();ctx.arc(k.x,k.y,k.r,0,Math.PI*2);
    ctx.fillStyle='rgba(168,185,205,'+ka.toFixed(3)+')';ctx.fill();
  }
  ctx.restore();
}

/* ================================================================
   BACKGROUND — layered deep space + pastel nebula columns
   ================================================================ */
function drawBg(now){
  ctx.clearRect(0,0,W,H);
  var bg=ctx.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,'#0c1425');bg.addColorStop(0.16,'#090f1c');
  bg.addColorStop(0.38,'#070d18');bg.addColorStop(0.62,'#060b14');
  bg.addColorStop(0.82,'#050910');bg.addColorStop(1,'#03070c');
  ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);

  _curHue+=(_tgtHue-_curHue)*0.005*(_dt/16);
  ctx.save();ctx.globalCompositeOperation='screen';

  /* violet left */
  var nb1=ctx.createRadialGradient(W*0.10,H*0.30,0,W*0.10,H*0.30,W*0.55);
  nb1.addColorStop(0,'rgba(85,58,135,0.072)');nb1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb1;ctx.fillRect(0,0,W,H);
  /* rose right */
  var nb2=ctx.createRadialGradient(W*0.92,H*0.58,0,W*0.92,H*0.58,W*0.50);
  nb2.addColorStop(0,'rgba(125,58,85,0.060)');nb2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb2;ctx.fillRect(0,0,W,H);
  /* teal center spine */
  var spine=ctx.createRadialGradient(W*0.5,H*0.5,0,W*0.5,H*0.5,W*0.40);
  spine.addColorStop(0,'rgba(38,78,112,0.052)');spine.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=spine;ctx.fillRect(0,0,W,H);
  /* route tint */
  var rt=ctx.createRadialGradient(W*0.5,H*0.5,0,W*0.5,H*0.5,W*0.85);
  rt.addColorStop(0,'hsla('+_curHue+',28%,15%,0.026)');rt.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=rt;ctx.fillRect(0,0,W,H);
  ctx.restore();
}

/* ================================================================
   SUN — proportional, cinematic, bleeding off top
   ================================================================ */
function drawSun(now){
  var cx=W*0.50,cy=H*(-0.010);
  var Rs=Math.min(W,H)*(W<420?0.26:W<680?0.22:0.19);
  ctx.save();

  /* corona layers */
  ctx.globalCompositeOperation='screen';
  [[Rs*5.5,0.036,'255,88,5'],[Rs*3.2,0.078,'255,108,10'],[Rs*1.85,0.152,'255,125,15']].forEach(function(c){
    var g=ctx.createRadialGradient(cx,cy,Rs*0.36,cx,cy,c[0]);
    g.addColorStop(0,'rgba('+c[2]+','+c[1]+')');
    g.addColorStop(0.42,'rgba('+c[2]+','+(c[1]*0.36).toFixed(3)+')');
    g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  });

  /* solar wind — 16 rays */
  ctx.save();
  for(var ri=0;ri<16;ri++){
    var ra=(ri/16)*Math.PI*2+now*0.000018;
    var rl=Rs*(1.35+0.28*Math.sin(now*0.000015+ri*0.80));
    ctx.globalCompositeOperation='screen';
    ctx.globalAlpha=0.022+0.010*Math.abs(Math.sin(now*0.00020+ri));
    var rx1=cx+Math.cos(ra)*Rs*0.50,ry1=cy+Math.sin(ra)*Rs*0.50;
    var rx2=cx+Math.cos(ra)*rl,ry2=cy+Math.sin(ra)*rl;
    var rg=ctx.createLinearGradient(rx1,ry1,rx2,ry2);
    rg.addColorStop(0,'rgba(255,145,26,0.92)');rg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle=rg;ctx.lineWidth=Rs*0.072;ctx.lineCap='round';
    ctx.beginPath();ctx.moveTo(rx1,ry1);ctx.lineTo(rx2,ry2);ctx.stroke();
  }
  ctx.globalAlpha=1;ctx.restore();

  /* chromosphere */
  ctx.globalCompositeOperation='source-over';
  var CHR=ctx.createRadialGradient(cx,cy,Rs*0.88,cx,cy,Rs*1.22);
  CHR.addColorStop(0,'rgba(145,15,0,0)');CHR.addColorStop(0.25,'rgba(210,42,4,0.56)');
  CHR.addColorStop(0.52,'rgba(255,62,8,0.36)');CHR.addColorStop(0.78,'rgba(195,34,0,0.15)');
  CHR.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=CHR;ctx.beginPath();ctx.arc(cx,cy,Rs*1.22,0,Math.PI*2);ctx.fill();

  /* prominences — 4 arcs */
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var pi=0;pi<4;pi++){
    var pa=(pi/4)*Math.PI*2+now*0.0000085+pi*0.75;
    var pl=Rs*(0.22+0.16*Math.abs(Math.sin(now*0.0000105+pi)));
    var ppx=cx+Math.cos(pa)*Rs,ppy=cy+Math.sin(pa)*Rs;
    var ppx2=cx+Math.cos(pa+0.32)*(Rs+pl),ppy2=cy+Math.sin(pa+0.32)*(Rs+pl);
    var pg=ctx.createLinearGradient(ppx,ppy,ppx2,ppy2);
    pg.addColorStop(0,'rgba(255,115,28,0.38)');pg.addColorStop(1,'rgba(255,55,0,0)');
    ctx.strokeStyle=pg;ctx.lineWidth=Rs*0.036;ctx.lineCap='round';
    ctx.beginPath();ctx.moveTo(ppx,ppy);
    ctx.quadraticCurveTo(cx+Math.cos(pa+0.16)*Rs*1.28,cy+Math.sin(pa+0.16)*Rs*1.28,ppx2,ppy2);
    ctx.stroke();
  }
  ctx.restore();

  /* photosphere */
  var PH=ctx.createRadialGradient(cx-Rs*0.20,cy-Rs*0.15,0,cx+Rs*0.06,cy+Rs*0.08,Rs);
  PH.addColorStop(0,'#fff8d2');PH.addColorStop(0.08,'#ffdc42');PH.addColorStop(0.25,'#ffa812');
  PH.addColorStop(0.50,'#ff6202');PH.addColorStop(0.72,'#ce2000');PH.addColorStop(0.88,'#960e00');
  PH.addColorStop(1,'#680600');
  ctx.fillStyle=PH;ctx.beginPath();ctx.arc(cx,cy,Rs,0,Math.PI*2);ctx.fill();

  /* granulation — 30 cells */
  ctx.save();ctx.beginPath();ctx.arc(cx,cy,Rs*0.99,0,Math.PI*2);ctx.clip();
  ctx.globalCompositeOperation='overlay';
  for(var gi=0;gi<30;gi++){
    var ga=(gi/30)*Math.PI*2+now*0.000044;
    var gd=Rs*(0.14+0.48*Math.abs(Math.sin(gi*1.618+now*0.000050)));
    var gx=cx+Math.cos(ga)*gd*(0.56+0.44*Math.cos(gi*0.88));
    var gy=cy+Math.sin(ga)*gd*(0.46+0.44*Math.sin(gi*1.08));
    var gr=Rs*(0.044+0.034*Math.abs(Math.sin(gi*0.68+now*0.000060)));
    var gg=ctx.createRadialGradient(gx,gy,0,gx,gy,gr);
    gg.addColorStop(0,'rgba(255,240,100,0.26)');gg.addColorStop(0.5,'rgba(255,198,55,0.10)');gg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=gg;ctx.fillRect(0,0,W,H);
  }
  /* sunspots — 5 */
  ctx.globalCompositeOperation='multiply';
  for(var si=0;si<5;si++){
    var sa=(si/5)*Math.PI*2+0.5+now*0.0000088;
    var sd=Rs*(0.20+0.20*Math.sin(si*2.08));
    var sx2=cx+Math.cos(sa)*sd,sy2=cy+Math.sin(sa)*sd;
    var sr=Rs*(0.028+0.015*Math.abs(Math.sin(si*1.35)));
    var sg=ctx.createRadialGradient(sx2,sy2,0,sx2,sy2,sr);
    sg.addColorStop(0,'rgba(0,0,0,0.60)');sg.addColorStop(0.5,'rgba(0,0,0,0.28)');sg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sg;ctx.fillRect(0,0,W,H);
  }
  ctx.restore();

  /* specular */
  ctx.globalCompositeOperation='screen';
  var HI=ctx.createRadialGradient(cx-Rs*0.16,cy-Rs*0.10,0,cx,cy,Rs);
  HI.addColorStop(0,'rgba(255,252,200,0.62)');HI.addColorStop(0.32,'rgba(255,212,78,0.10)');HI.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=HI;ctx.beginPath();ctx.arc(cx,cy,Rs,0,Math.PI*2);ctx.fill();

  /* lens flare x3 */
  [[Rs*0.10,Rs*0.06,Rs*0.22,0.34],[-Rs*0.38,Rs*0.28,Rs*0.10,0.16],[Rs*0.55,Rs*0.42,Rs*0.06,0.12]].forEach(function(lf){
    var lg=ctx.createRadialGradient(cx+lf[0],cy+lf[1],0,cx+lf[0],cy+lf[1],lf[2]);
    lg.addColorStop(0,'rgba(255,252,235,'+lf[3]+')');lg.addColorStop(0.4,'rgba(255,220,95,0.06)');lg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=lg;ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
}

/* ================================================================
   ORBIT RING
   ================================================================ */
function drawOrbit(py,rx,ry,isActive,now){
  ctx.save();ctx.globalCompositeOperation='screen';
  if(isActive){
    var glow=ctx.createRadialGradient(W*0.5,py,0,W*0.5,py,ry*4.0);
    glow.addColorStop(0,'rgba(75,135,215,0.060)');glow.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=glow;ctx.fillRect(0,0,W,H);
  }
  var a=isActive?0.56:0.13;
  var g=ctx.createLinearGradient(W*0.5-rx,py,W*0.5+rx,py);
  g.addColorStop(0,'rgba(95,142,212,0)');
  g.addColorStop(0.10,'rgba(132,178,240,'+(a*0.50)+')');
  g.addColorStop(0.30,'rgba(162,204,250,'+(a*0.80)+')');
  g.addColorStop(0.50,'rgba(192,218,255,'+a+')');
  g.addColorStop(0.70,'rgba(162,204,250,'+(a*0.80)+')');
  g.addColorStop(0.90,'rgba(132,178,240,'+(a*0.50)+')');
  g.addColorStop(1,'rgba(95,142,212,0)');
  ctx.strokeStyle=g;ctx.lineWidth=isActive?1.85:0.55;
  ctx.beginPath();ctx.ellipse(W*0.5,py,rx,ry,0,0,Math.PI*2);ctx.stroke();
  if(isActive){
    var ang=now*0.00042;
    var sx=W*0.5+rx*Math.cos(ang),sy=py+ry*Math.sin(ang);
    var sg=ctx.createRadialGradient(sx,sy,0,sx,sy,9.5);
    sg.addColorStop(0,'rgba(225,240,255,1.0)');sg.addColorStop(0.35,'rgba(190,218,255,0.55)');sg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sg;ctx.fillRect(0,0,W,H);
    ctx.globalAlpha=0.28;
    var ra=ctx.createRadialGradient(sx+2.2,sy,0,sx+2.2,sy,5.5);
    ra.addColorStop(0,'rgba(255,52,52,0.90)');ra.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=ra;ctx.fillRect(0,0,W,H);
    var ba=ctx.createRadialGradient(sx-2.2,sy,0,sx-2.2,sy,5.5);
    ba.addColorStop(0,'rgba(52,52,255,0.90)');ba.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=ba;ctx.fillRect(0,0,W,H);
    ctx.globalAlpha=1;
  }
  ctx.restore();
}

/* ================================================================
   PLANET HELPERS
   ================================================================ */
function pBase(x,y,r,c0,c1,c2,c3,c4){
  var g=ctx.createRadialGradient(x-r*0.28,y-r*0.22,0,x+r*0.10,y+r*0.12,r*1.04);
  g.addColorStop(0,c0);g.addColorStop(0.22,c1);g.addColorStop(0.50,c2);
  g.addColorStop(0.76,c3);g.addColorStop(1,c4);
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
}
function pLimb(x,y,r,col){
  ctx.save();ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.30,y-r*0.24,0,x,y,r*1.04);
  g.addColorStop(0,col);g.addColorStop(0.40,'rgba(255,255,255,0.026)');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();
}
function pDark(x,y,r,s){
  s=s||0.65;ctx.save();ctx.globalCompositeOperation='multiply';
  var g=ctx.createRadialGradient(x+r*0.36,y+r*0.30,0,x,y,r*1.04);
  g.addColorStop(0,'rgba(0,0,0,'+s+')');g.addColorStop(0.42,'rgba(0,0,0,'+(s*0.34).toFixed(3)+')');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();
}
function pSpec(x,y,r,a){
  a=a||0.20;ctx.save();ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.24,y-r*0.20,0,x-r*0.04,y-r*0.04,r*0.62);
  g.addColorStop(0,'rgba(255,255,255,'+a+')');g.addColorStop(0.5,'rgba(255,255,255,'+(a*0.18).toFixed(3)+')');g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.restore();
}
function pAtm(x,y,r,col,s){
  s=s||0.18;ctx.save();ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x,y,r*0.80,x,y,r*1.36);
  var c0=col.replace(/[\d.]+\)$/,s.toFixed(3)+')');
  var c1=col.replace(/[\d.]+\)$/,(s*0.34).toFixed(3)+')');
  g.addColorStop(0,c0);g.addColorStop(0.5,c1);g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);ctx.restore();
}
function pActive(x,y,r,now){
  ctx.save();ctx.globalCompositeOperation='screen';
  var pulse=0.66+0.34*Math.sin(now*0.0028);
  var g=ctx.createRadialGradient(x,y,r*0.50,x,y,r*2.6);
  g.addColorStop(0,'rgba(200,168,75,'+(0.32*pulse).toFixed(3)+')');
  g.addColorStop(0.40,'rgba(200,168,75,'+(0.13*pulse).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g;ctx.fillRect(0,0,W,H);
  ctx.globalAlpha=0.22*pulse;
  ctx.strokeStyle='rgba(255,48,48,0.74)';ctx.lineWidth=1.5;
  ctx.beginPath();ctx.arc(x+1.8,y,r*1.10,0,Math.PI*2);ctx.stroke();
  ctx.strokeStyle='rgba(48,48,255,0.74)';
  ctx.beginPath();ctx.arc(x-1.8,y,r*1.10,0,Math.PI*2);ctx.stroke();
  ctx.globalAlpha=1;ctx.restore();
}

/* land blob helper for Earth */
function eLand(x,y,r,ox,oy,rx,R,G,B,a){
  var eg=ctx.createRadialGradient(x+ox*r,y+oy*r,0,x+ox*r,y+oy*r,rx*r);
  eg.addColorStop(0,'rgba('+R+','+G+','+B+','+a+')');
  eg.addColorStop(0.45,'rgba('+R+','+G+','+B+','+(a*0.55).toFixed(2)+')');
  eg.addColorStop(0.75,'rgba('+R+','+G+','+B+','+(a*0.20).toFixed(2)+')');
  eg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=eg;ctx.fillRect(0,0,W,H);
}

/* ================================================================
   MERCURY — cratered, barren, grey-brown
   ================================================================ */
function drawMercury(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#e0c8a2','#c09862','#966c3a','#6a4822','#3c2812');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  /* 14 craters */
  var CR=[[0.32,0.18,0.20],[-0.28,0.32,0.16],[0.08,-0.28,0.19],[-0.12,0.05,0.10],
    [0.42,-0.15,0.13],[-0.38,-0.22,0.14],[0.18,0.40,0.11],[-0.05,-0.45,0.12],
    [0.35,0.42,0.08],[-0.42,0.18,0.09],[0.05,0.55,0.07],[0.50,-0.35,0.10],
    [-0.22,-0.12,0.06],[0.28,-0.48,0.08]];
  CR.forEach(function(c){
    var cx2=x+c[0]*r,cy2=y+c[1]*r,cr=c[2]*r;
    var cg=ctx.createRadialGradient(cx2,cy2,0,cx2,cy2,cr);
    cg.addColorStop(0,'rgba(35,18,6,0.62)');cg.addColorStop(0.55,'rgba(58,34,12,0.30)');
    cg.addColorStop(0.85,'rgba(145,108,55,0.10)');cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply';ctx.fillStyle=cg;ctx.fillRect(0,0,W,H);
    ctx.globalCompositeOperation='screen';
    var rim=ctx.createRadialGradient(cx2-cr*0.30,cy2-cr*0.30,cr*0.62,cx2,cy2,cr);
    rim.addColorStop(0,'rgba(0,0,0,0)');rim.addColorStop(0.82,'rgba(200,175,128,0.16)');rim.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=rim;ctx.fillRect(0,0,W,H);
  });
  /* Caloris basin — large impact */
  ctx.globalCompositeOperation='multiply';
  var cal=ctx.createRadialGradient(x+r*0.20,y-r*0.10,0,x+r*0.20,y-r*0.10,r*0.38);
  cal.addColorStop(0,'rgba(25,12,4,0.45)');cal.addColorStop(0.6,'rgba(45,22,8,0.18)');cal.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=cal;ctx.fillRect(0,0,W,H);
  ctx.globalCompositeOperation='screen';
  var calR=ctx.createRadialGradient(x+r*0.20,y-r*0.10,r*0.25,x+r*0.20,y-r*0.10,r*0.40);
  calR.addColorStop(0,'rgba(0,0,0,0)');calR.addColorStop(0.7,'rgba(195,168,125,0.12)');calR.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=calR;ctx.fillRect(0,0,W,H);
  ctx.restore();
  pLimb(x,y,r,'rgba(225,190,118,0.66)');pDark(x,y,r,0.66);pSpec(x,y,r,0.11);
  ctx.restore();
}

/* ================================================================
   VENUS — sulphur clouds, yellow-orange banded
   ================================================================ */
function drawVenus(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#ffe8a8','#ecc040','#c88520','#9c5c10','#683808');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  /* 8 cloud bands */
  for(var i=0;i<8;i++){
    var by=y-r*0.80+i*r*0.24+Math.sin(now*0.0000105+i*1.22)*r*0.036;
    var ba=0.13+0.12*Math.abs(Math.sin(i*0.82+now*0.0000088));
    var bd=ctx.createLinearGradient(x-r,by,x+r,by+r*0.09);
    bd.addColorStop(0,'rgba(255,238,162,0)');
    bd.addColorStop(0.35,'rgba(255,238,162,'+ba+')');
    bd.addColorStop(0.65,'rgba(238,202,98,'+ba+')');
    bd.addColorStop(1,'rgba(255,238,162,0)');
    ctx.globalCompositeOperation='overlay';
    ctx.fillStyle=bd;ctx.fillRect(x-r,by,r*2,r*0.22);
  }
  /* Maxwell Montes — high mountain reflection */
  ctx.globalCompositeOperation='screen';
  var mm=ctx.createRadialGradient(x+r*0.30,y-r*0.18,0,x+r*0.30,y-r*0.18,r*0.12);
  mm.addColorStop(0,'rgba(255,248,200,0.22)');mm.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=mm;ctx.fillRect(0,0,W,H);
  ctx.restore();
  pAtm(x,y,r,'rgba(255,208,78,0.18)',0.18);
  pLimb(x,y,r,'rgba(255,226,136,0.68)');pDark(x,y,r,0.58);pSpec(x,y,r,0.14);
  ctx.restore();
}

/* ================================================================
   EARTH — every continent, ocean depth, terminator,
   clouds, polar ice, city lights, atmosphere rim
   ================================================================ */
function drawEarth(x,y,r,now){
  ctx.save();
  /* ocean base — deep blue */
  var ocean=ctx.createRadialGradient(x-r*0.22,y-r*0.18,0,x+r*0.08,y+r*0.10,r*1.02);
  ocean.addColorStop(0,'#a8d8f8');ocean.addColorStop(0.15,'#58a0e0');
  ocean.addColorStop(0.35,'#2068c8');ocean.addColorStop(0.58,'#0c48a0');
  ocean.addColorStop(0.78,'#083270');ocean.addColorStop(1,'#051e4a');
  ctx.fillStyle=ocean;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();

  /* ocean depth variation */
  ctx.globalCompositeOperation='screen';
  var pd=ctx.createRadialGradient(x-r*0.52,y+r*0.06,0,x-r*0.52,y+r*0.06,r*0.52);
  pd.addColorStop(0,'rgba(6,38,98,0.18)');pd.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=pd;ctx.fillRect(0,0,W,H);

  ctx.globalCompositeOperation='source-over';
  /* ── N AMERICA ── */
  eLand(x,y,r,-0.34,-0.30,0.22,72,128,55,0.92);
  eLand(x,y,r,-0.20,-0.20,0.12,58,118,48,0.78);
  eLand(x,y,r,-0.44,-0.18,0.10,95,140,62,0.72);
  eLand(x,y,r,-0.30,0.02,0.08,88,148,58,0.80);
  eLand(x,y,r,-0.06,-0.52,0.10,215,230,240,0.85); /* Greenland */
  eLand(x,y,r,-0.52,-0.28,0.08,68,118,52,0.78); /* Alaska */
  eLand(x,y,r,-0.30,-0.38,0.14,82,138,55,0.68); /* Canada */
  /* ── S AMERICA ── */
  eLand(x,y,r,-0.20,0.22,0.14,38,108,38,0.92); /* Amazon */
  eLand(x,y,r,-0.32,0.25,0.05,128,108,60,0.80); /* Andes */
  eLand(x,y,r,-0.12,0.18,0.10,52,120,45,0.85);
  eLand(x,y,r,-0.22,0.52,0.08,108,128,78,0.72); /* Patagonia */
  /* ── EUROPE ── */
  eLand(x,y,r,0.08,-0.22,0.10,78,148,62,0.88);
  eLand(x,y,r,0.04,-0.28,0.07,148,158,68,0.82); /* Iberia */
  eLand(x,y,r,0.10,-0.35,0.08,68,138,58,0.78); /* Scandinavia */
  eLand(x,y,r,0.04,-0.30,0.04,72,138,55,0.80); /* UK */
  /* ── AFRICA ── */
  eLand(x,y,r,0.10,-0.02,0.18,218,195,108,0.88); /* Sahara */
  eLand(x,y,r,0.12,0.15,0.15,148,168,72,0.85); /* Savanna */
  eLand(x,y,r,0.14,0.18,0.09,42,108,40,0.90); /* Congo */
  eLand(x,y,r,0.22,0.08,0.08,168,158,68,0.82); /* E Africa */
  eLand(x,y,r,0.15,0.38,0.10,138,148,72,0.78); /* S Africa */
  eLand(x,y,r,0.28,0.32,0.04,148,148,68,0.72); /* Madagascar */
  /* ── ASIA ── */
  eLand(x,y,r,0.32,-0.38,0.32,78,148,62,0.82); /* Russia */
  eLand(x,y,r,0.44,-0.10,0.16,98,158,65,0.85); /* China */
  eLand(x,y,r,0.35,0.08,0.10,138,168,68,0.88); /* India */
  eLand(x,y,r,0.24,-0.05,0.12,218,195,100,0.82); /* Middle East */
  eLand(x,y,r,0.50,0.05,0.10,58,128,48,0.85); /* SE Asia */
  eLand(x,y,r,0.56,-0.12,0.04,78,148,58,0.78); /* Japan */
  eLand(x,y,r,0.52,0.18,0.12,52,118,45,0.82); /* Indonesia */
  eLand(x,y,r,0.32,-0.18,0.18,168,175,85,0.75); /* C Asia steppe */
  eLand(x,y,r,0.40,-0.18,0.12,178,175,108,0.72); /* Tibet */
  /* ── AUSTRALIA ── */
  eLand(x,y,r,0.48,0.35,0.16,218,175,85,0.85);
  eLand(x,y,r,0.56,0.32,0.06,88,138,58,0.72);
  eLand(x,y,r,0.60,0.45,0.04,78,138,55,0.70); /* NZ */

  /* polar ice */
  ctx.globalCompositeOperation='screen';
  var npg=ctx.createRadialGradient(x,y-r*0.79,0,x,y-r*0.79,r*0.30);
  npg.addColorStop(0,'rgba(245,252,255,0.95)');npg.addColorStop(0.4,'rgba(228,244,255,0.80)');
  npg.addColorStop(0.7,'rgba(210,235,255,0.42)');npg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=npg;ctx.fillRect(0,0,W,H);
  var spg=ctx.createRadialGradient(x,y+r*0.83,0,x,y+r*0.83,r*0.26);
  spg.addColorStop(0,'rgba(242,250,255,0.92)');spg.addColorStop(0.45,'rgba(225,242,255,0.68)');
  spg.addColorStop(0.72,'rgba(205,232,255,0.35)');spg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=spg;ctx.fillRect(0,0,W,H);

  /* cloud systems — ITCZ + weather fronts */
  var CL=[
    [x-r*0.40,y-r*0.05,r*0.30,r*0.06,0.22],
    [x+r*0.20,y-r*0.08,r*0.24,r*0.05,0.18],
    [x-r*0.15,y+r*0.38,r*0.22,r*0.05,0.16],
    [x-r*0.52,y-r*0.22,r*0.18,r*0.08,0.20],
    [x+r*0.38,y+r*0.12,r*0.16,r*0.06,0.18],
    [x-r*0.08,y-r*0.30,r*0.20,r*0.06,0.15],
    [x+r*0.10,y+r*0.55,r*0.28,r*0.05,0.14],
    [x+r*0.55,y-r*0.28,r*0.14,r*0.05,0.12]
  ];
  CL.forEach(function(cl){
    var drift=Math.sin(now*0.0000075+cl[0]*0.001)*r*0.025;
    var cg=ctx.createRadialGradient(cl[0]+drift,cl[1],0,cl[0]+drift,cl[1],cl[2]);
    cg.addColorStop(0,'rgba(245,250,255,'+cl[4]+')');
    cg.addColorStop(0.42,'rgba(238,247,255,'+(cl[4]*0.58).toFixed(3)+')');
    cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cg;ctx.fillRect(0,0,W,H);
  });
  /* cyclone spiral */
  var stA=now*0.000076;
  for(var sci=0;sci<3;sci++){
    var sAng=stA+sci*(Math.PI*2/3);
    var sCX=x-r*0.48+Math.cos(sAng)*r*0.058,sCY=y-r*0.20+Math.sin(sAng)*r*0.040;
    var sCG=ctx.createRadialGradient(sCX,sCY,0,sCX,sCY,r*0.082);
    sCG.addColorStop(0,'rgba(245,250,255,0.20)');sCG.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=sCG;ctx.fillRect(0,0,W,H);
  }

  /* terminator — night side shadow */
  ctx.globalCompositeOperation='multiply';
  var term=ctx.createRadialGradient(x+r*0.28,y+r*0.22,r*0.14,x+r*0.28,y+r*0.22,r*1.10);
  term.addColorStop(0,'rgba(0,0,0,0)');term.addColorStop(0.60,'rgba(0,0,0,0.22)');
  term.addColorStop(0.80,'rgba(0,0,0,0.58)');term.addColorStop(1,'rgba(0,0,0,0.82)');
  ctx.fillStyle=term;ctx.fillRect(0,0,W,H);

  /* city lights on night side */
  ctx.globalCompositeOperation='screen';
  [[x+r*0.40,y+r*0.22,r*0.06,0.16],[x+r*0.32,y+r*0.15,r*0.05,0.13],
   [x+r*0.18,y+r*0.08,r*0.05,0.11],[x+r*0.14,y-r*0.08,r*0.04,0.11],
   [x+r*0.44,y+r*0.30,r*0.04,0.09]].forEach(function(ct){
    var cg=ctx.createRadialGradient(ct[0],ct[1],0,ct[0],ct[1],ct[2]);
    cg.addColorStop(0,'rgba(255,238,158,'+ct[3]+')');cg.addColorStop(0.5,'rgba(255,212,98,'+(ct[3]*0.44).toFixed(3)+')');cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=cg;ctx.fillRect(0,0,W,H);
  });
  ctx.restore();

  /* atmosphere layers */
  ctx.save();ctx.globalCompositeOperation='screen';
  var a1=ctx.createRadialGradient(x,y,r*0.88,x,y,r*1.08);
  a1.addColorStop(0,'rgba(98,165,255,0.24)');a1.addColorStop(0.5,'rgba(78,145,240,0.12)');a1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=a1;ctx.fillRect(0,0,W,H);
  var a2=ctx.createRadialGradient(x,y,r*0.96,x,y,r*1.24);
  a2.addColorStop(0,'rgba(138,198,255,0.42)');a2.addColorStop(0.35,'rgba(78,158,255,0.18)');a2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=a2;ctx.fillRect(0,0,W,H);
  var a3=ctx.createRadialGradient(x-r*0.28,y-r*0.22,r*0.82,x-r*0.10,y-r*0.08,r*1.20);
  a3.addColorStop(0,'rgba(162,212,255,0.32)');a3.addColorStop(0.55,'rgba(118,182,255,0.10)');a3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=a3;ctx.fillRect(0,0,W,H);
  ctx.restore();

  pLimb(x,y,r,'rgba(118,198,255,0.72)');pDark(x,y,r,0.54);pSpec(x,y,r,0.20);
  ctx.restore();
}

/* ================================================================
   MOON — maria, craters, no atm
   ================================================================ */
function drawMoon(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#d8d0c2','#a89882','#7a6a52','#524438','#302820');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  /* maria */
  [[-0.12,-0.08,0.38],[0.20,0.15,0.28],[-0.30,0.25,0.22],[0.05,-0.30,0.20]].forEach(function(m){
    var mg=ctx.createRadialGradient(x+m[0]*r,y+m[1]*r,0,x+m[0]*r,y+m[1]*r,m[2]*r);
    mg.addColorStop(0,'rgba(50,40,32,0.54)');mg.addColorStop(0.55,'rgba(60,48,36,0.28)');mg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply';ctx.fillStyle=mg;ctx.fillRect(0,0,W,H);
  });
  /* craters */
  [[0.25,0.10,0.15],[-0.18,-0.25,0.12],[0.05,0.35,0.10],[-0.35,0.08,0.11],[0.38,-0.20,0.08],[0.12,-0.40,0.07]].forEach(function(c){
    var cg=ctx.createRadialGradient(x+c[0]*r,y+c[1]*r,0,x+c[0]*r,y+c[1]*r,c[2]*r);
    cg.addColorStop(0,'rgba(26,18,12,0.58)');cg.addColorStop(0.6,'rgba(46,34,24,0.26)');cg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply';ctx.fillStyle=cg;ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pLimb(x,y,r,'rgba(212,202,186,0.55)');pDark(x,y,r,0.68);pSpec(x,y,r,0.10);
  ctx.restore();
}

/* ================================================================
   MARS — Tharsis, Olympus, Valles, Hellas, polar ice, dust
   ================================================================ */
function drawMars(x,y,r,now){
  ctx.save();
  var base=ctx.createRadialGradient(x-r*0.25,y-r*0.20,0,x+r*0.10,y+r*0.12,r*1.03);
  base.addColorStop(0,'#f0b890');base.addColorStop(0.18,'#d87048');
  base.addColorStop(0.40,'#b85030');base.addColorStop(0.62,'#8c3820');
  base.addColorStop(0.82,'#602010');base.addColorStop(1,'#3c1008');
  ctx.fillStyle=base;ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();

  /* Tharsis bulge */
  ctx.globalCompositeOperation='screen';
  var th=ctx.createRadialGradient(x-r*0.28,y-r*0.05,0,x-r*0.28,y-r*0.05,r*0.42);
  th.addColorStop(0,'rgba(222,162,102,0.36)');th.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=th;ctx.fillRect(0,0,W,H);

  /* Olympus Mons */
  ctx.globalCompositeOperation='multiply';
  var om=ctx.createRadialGradient(x-r*0.30,y-r*0.15,0,x-r*0.30,y-r*0.15,r*0.18);
  om.addColorStop(0,'rgba(28,6,2,0.52)');om.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=om;ctx.fillRect(0,0,W,H);
  ctx.globalCompositeOperation='screen';
  var cal2=ctx.createRadialGradient(x-r*0.30,y-r*0.16,0,x-r*0.30,y-r*0.16,r*0.04);
  cal2.addColorStop(0,'rgba(232,182,138,0.32)');cal2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=cal2;ctx.fillRect(0,0,W,H);

  /* Valles Marineris */
  ctx.globalCompositeOperation='multiply';
  var vm=ctx.createLinearGradient(x-r*0.55,y+r*0.02,x+r*0.20,y+r*0.16);
  vm.addColorStop(0,'rgba(78,14,4,0)');vm.addColorStop(0.12,'rgba(42,6,2,0.68)');
  vm.addColorStop(0.50,'rgba(38,5,1,0.74)');vm.addColorStop(0.88,'rgba(42,6,2,0.62)');
  vm.addColorStop(1,'rgba(78,14,4,0)');
  ctx.fillStyle=vm;ctx.fillRect(x-r,y+r*0.01,r*2,r*0.12);
  ctx.globalCompositeOperation='screen';
  var vmh=ctx.createLinearGradient(x-r*0.52,y+r*0.01,x+r*0.18,y+r*0.03);
  vmh.addColorStop(0,'rgba(218,148,78,0)');vmh.addColorStop(0.5,'rgba(218,148,78,0.12)');vmh.addColorStop(1,'rgba(218,148,78,0)');
  ctx.fillStyle=vmh;ctx.fillRect(x-r,y+r*0.01,r*2,r*0.02);

  /* Hellas basin */
  ctx.globalCompositeOperation='multiply';
  var hel=ctx.createRadialGradient(x+r*0.35,y+r*0.30,0,x+r*0.35,y+r*0.30,r*0.30);
  hel.addColorStop(0,'rgba(22,4,2,0.58)');hel.addColorStop(0.5,'rgba(38,8,3,0.30)');hel.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=hel;ctx.fillRect(0,0,W,H);
  ctx.globalCompositeOperation='screen';
  var helR=ctx.createRadialGradient(x+r*0.35,y+r*0.30,r*0.18,x+r*0.35,y+r*0.30,r*0.34);
  helR.addColorStop(0,'rgba(0,0,0,0)');helR.addColorStop(0.65,'rgba(222,165,102,0.14)');helR.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=helR;ctx.fillRect(0,0,W,H);

  /* Argyre basin */
  ctx.globalCompositeOperation='multiply';
  var arg=ctx.createRadialGradient(x-r*0.20,y+r*0.42,0,x-r*0.20,y+r*0.42,r*0.18);
  arg.addColorStop(0,'rgba(25,5,2,0.50)');arg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=arg;ctx.fillRect(0,0,W,H);

  /* polar ice caps */
  ctx.globalCompositeOperation='screen';
  var npM=ctx.createRadialGradient(x,y-r*0.76,0,x,y-r*0.76,r*0.28);
  npM.addColorStop(0,'rgba(248,240,228,0.95)');npM.addColorStop(0.38,'rgba(235,228,215,0.72)');
  npM.addColorStop(0.68,'rgba(218,210,198,0.36)');npM.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=npM;ctx.fillRect(0,0,W,H);
  /* N polar spiral */
  var spAngle=now*0.0000095;
  for(var msi=0;msi<3;msi++){
    var msA=spAngle+msi*(Math.PI*2/3);
    var msPX=x+Math.cos(msA)*r*0.08,msPY=y-r*0.76+Math.sin(msA)*r*0.05;
    var msG=ctx.createRadialGradient(msPX,msPY,0,msPX,msPY,r*0.10);
    msG.addColorStop(0,'rgba(248,242,230,0.22)');msG.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=msG;ctx.fillRect(0,0,W,H);
  }
  var spM=ctx.createRadialGradient(x,y+r*0.80,0,x,y+r*0.80,r*0.22);
  spM.addColorStop(0,'rgba(244,236,222,0.90)');spM.addColorStop(0.45,'rgba(228,220,208,0.58)');spM.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=spM;ctx.fillRect(0,0,W,H);

  /* dust storms */
  ctx.globalCompositeOperation='overlay';
  var ds=now*0.000011,dsx=x+Math.cos(ds)*r*0.78,dsy=y+Math.sin(ds)*r*0.55;
  var dg=ctx.createRadialGradient(dsx,dsy,0,dsx,dsy,r*0.35);
  dg.addColorStop(0,'rgba(212,155,78,0.30)');dg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=dg;ctx.fillRect(0,0,W,H);
  var ds2=now*0.0000082+1.95,dsx2=x+Math.cos(ds2)*r*0.55,dsy2=y+Math.sin(ds2)*r*0.72;
  var dg2=ctx.createRadialGradient(dsx2,dsy2,0,dsx2,dsy2,r*0.20);
  dg2.addColorStop(0,'rgba(205,148,70,0.22)');dg2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=dg2;ctx.fillRect(0,0,W,H);

  ctx.restore();
  ctx.save();ctx.globalCompositeOperation='screen';
  var mAtm=ctx.createRadialGradient(x,y,r*0.86,x,y,r*1.22);
  mAtm.addColorStop(0,'rgba(208,118,58,0.17)');mAtm.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=mAtm;ctx.fillRect(0,0,W,H);ctx.restore();
  pLimb(x,y,r,'rgba(235,160,108,0.68)');pDark(x,y,r,0.62);pSpec(x,y,r,0.10);
  ctx.restore();
}

/* ================================================================
   JUPITER — 10 bands, GRS 3-layer, polar hex, animated
   ================================================================ */
function drawJupiter(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#f0e0c0','#d8c090','#b89860','#8a6830','#604020');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  var JB=[[-0.72,0.14,'rgba(162,110,52,0.60)'],[-0.55,0.10,'rgba(205,165,95,0.46)'],
    [-0.42,0.16,'rgba(148,90,38,0.64)'],[-0.23,0.12,'rgba(198,160,90,0.50)'],
    [-0.08,0.18,'rgba(140,88,36,0.66)'],[0.12,0.14,'rgba(185,135,65,0.52)'],
    [0.28,0.18,'rgba(122,72,28,0.64)'],[0.48,0.12,'rgba(192,148,75,0.48)'],
    [0.62,0.16,'rgba(152,100,48,0.56)'],[0.78,0.12,'rgba(168,118,52,0.54)']];
  JB.forEach(function(bd,idx){
    var yo=bd[0]+Math.sin(now*0.0000042+idx*0.6)*0.011;
    var lg=ctx.createLinearGradient(x-r,y+yo*r,x+r,y+(yo+bd[1])*r);
    var ct=bd[2].replace(/[\d.]+\)$/,'0)');
    lg.addColorStop(0,ct);lg.addColorStop(0.28,bd[2]);lg.addColorStop(0.72,bd[2]);lg.addColorStop(1,ct);
    ctx.globalCompositeOperation='overlay';ctx.fillStyle=lg;ctx.fillRect(x-r,y+yo*r,r*2,bd[1]*r);
  });
  /* GRS outer halo */
  var grsx=x+r*0.22+Math.sin(now*0.0000052)*r*0.04,grsy=y+r*0.12;
  ctx.globalCompositeOperation='source-over';
  var grs0=ctx.createRadialGradient(grsx,grsy,r*0.11,grsx,grsy,r*0.28);
  grs0.addColorStop(0,'rgba(138,28,7,0.42)');grs0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=grs0;ctx.fillRect(0,0,W,H);
  var grs1=ctx.createRadialGradient(grsx,grsy,0,grsx,grsy,r*0.18);
  grs1.addColorStop(0,'rgba(180,48,18,0.90)');grs1.addColorStop(0.45,'rgba(160,36,12,0.74)');
  grs1.addColorStop(0.78,'rgba(136,26,8,0.42)');grs1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=grs1;ctx.fillRect(0,0,W,H);
  ctx.globalCompositeOperation='screen';
  var grs2=ctx.createRadialGradient(grsx-r*0.04,grsy-r*0.02,0,grsx,grsy,r*0.09);
  grs2.addColorStop(0,'rgba(218,90,30,0.64)');grs2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=grs2;ctx.fillRect(0,0,W,H);
  /* polar hexagon */
  ctx.globalCompositeOperation='multiply';
  var phxg=ctx.createRadialGradient(x,y-r*0.70,0,x,y-r*0.70,r*0.38);
  phxg.addColorStop(0,'rgba(78,52,28,0.44)');phxg.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=phxg;ctx.fillRect(0,0,W,H);
  ctx.restore();
  pLimb(x,y,r,'rgba(240,212,162,0.55)');pDark(x,y,r,0.55);pSpec(x,y,r,0.12);
  ctx.restore();
}

/* ================================================================
   SATURN — 6 ring bands D/C/B/Cassini/A/F + 7 cloud bands
   ================================================================ */
function drawSaturn(x,y,r,now){
  ctx.save();
  var rW=r*2.65,rH=r*0.27;
  /* back rings */
  ctx.save();ctx.beginPath();ctx.rect(x-rW,y-rH,rW*2,rH+1);ctx.clip();
  _sRings(x,y,rW,rH,0.52);ctx.restore();
  /* planet */
  pBase(x,y,r,'#f8ead8','#e8d0a0','#c8a868','#9a7840','#6e5025');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  var SB=[[-0.56,0.14,'rgba(200,168,100,0.44)'],[-0.38,0.10,'rgba(228,195,135,0.36)'],
    [-0.22,0.16,'rgba(185,148,82,0.50)'],[-0.03,0.12,'rgba(215,180,118,0.40)'],
    [0.11,0.16,'rgba(175,138,72,0.52)'],[0.30,0.12,'rgba(208,172,105,0.42)'],[0.45,0.14,'rgba(182,148,78,0.46)']];
  SB.forEach(function(bd){
    var lg=ctx.createLinearGradient(x-r,y+bd[0]*r,x+r,y+(bd[0]+bd[1])*r);
    var ct=bd[2].replace(/[\d.]+\)$/,'0)');
    lg.addColorStop(0,ct);lg.addColorStop(0.5,bd[2]);lg.addColorStop(1,ct);
    ctx.globalCompositeOperation='overlay';ctx.fillStyle=lg;ctx.fillRect(x-r,y+bd[0]*r,r*2,bd[1]*r);
  });
  ctx.restore();
  pAtm(x,y,r,'rgba(218,182,118,0.12)',0.12);
  pLimb(x,y,r,'rgba(248,226,178,0.62)');pDark(x,y,r,0.52);pSpec(x,y,r,0.15);
  /* front rings */
  ctx.save();ctx.beginPath();ctx.rect(x-rW,y,rW*2,rH+2);ctx.clip();
  _sRings(x,y,rW,rH,0.92);ctx.restore();
  ctx.restore();
}
function _sRings(x,y,rW,rH,alpha){
  var RINGS=[
    {i0:0.40,i1:0.50,col:'rgba(168,142,92,0.18)'},
    {i0:0.50,i1:0.68,col:'rgba(208,182,128,0.38)'},
    {i0:0.68,i1:0.92,col:'rgba(228,202,150,0.58)'},
    {i0:0.92,i1:0.96,col:'rgba(16,10,4,0.04)'},
    {i0:0.96,i1:1.15,col:'rgba(215,188,138,0.52)'},
    {i0:1.15,i1:1.20,col:'rgba(188,162,112,0.25)'}
  ];
  ctx.save();
  RINGS.forEach(function(rg){
    var gr=ctx.createRadialGradient(x,y,rg.i0*rW,x,y,rg.i1*rW);
    var bA=parseFloat(rg.col.match(/[\d.]+\)$/)[0]);
    var a0=(bA*alpha).toFixed(3);
    var atop=rg.col.replace(/[\d.]+\)$/,'0)');
    var amid=rg.col.replace(/[\d.]+\)$/,a0+')');
    gr.addColorStop(0,atop);gr.addColorStop(0.25,amid);gr.addColorStop(0.75,amid);gr.addColorStop(1,atop);
    ctx.fillStyle=gr;
    ctx.beginPath();
    ctx.ellipse(x,y,rg.i1*rW,rg.i1*rH,0,0,Math.PI*2,false);
    ctx.ellipse(x,y,rg.i0*rW,rg.i0*rH,0,Math.PI*2,0,true);
    ctx.fill();
  });
  ctx.restore();
}

/* ================================================================
   URANUS — ice giant, tilted ring system
   ================================================================ */
function drawUranus(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#c8f0f5','#78d0dc','#38a8bc','#1878a0','#0c5072');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  for(var ui=0;ui<6;ui++){
    var uy=y-r*0.65+ui*r*0.28;
    var ubg=ctx.createLinearGradient(x-r,uy,x+r,uy+r*0.10);
    ubg.addColorStop(0,'rgba(78,198,218,0)');ubg.addColorStop(0.5,'rgba(78,198,218,0.10)');ubg.addColorStop(1,'rgba(78,198,218,0)');
    ctx.globalCompositeOperation='screen';ctx.fillStyle=ubg;ctx.fillRect(x-r,uy,r*2,r*0.18);
  }
  ctx.restore();
  ctx.save();ctx.globalCompositeOperation='screen';
  [[r*1.42,r*0.17,0.08,'rgba(158,218,230,0.30)'],[r*1.58,r*0.20,0.07,'rgba(138,202,218,0.20)'],[r*1.70,r*0.22,0.05,'rgba(118,188,205,0.12)']].forEach(function(rg){
    ctx.strokeStyle=rg[3];ctx.lineWidth=rg[2]*r*10;
    ctx.beginPath();ctx.ellipse(x,y,rg[0],rg[1],Math.PI*0.08,0,Math.PI*2);ctx.stroke();
  });
  ctx.restore();
  pAtm(x,y,r,'rgba(78,208,228,0.20)',0.20);
  pLimb(x,y,r,'rgba(175,240,248,0.68)');pDark(x,y,r,0.55);pSpec(x,y,r,0.20);
  ctx.restore();
}

/* ================================================================
   NEPTUNE — deep blue, GDS, cloud streaks
   ================================================================ */
function drawNeptune(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#8ab8f8','#2858e0','#1235b8','#0c2290','#081870');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  ctx.globalCompositeOperation='screen';
  for(var ni=0;ni<5;ni++){
    var ny=y-r*0.40+ni*r*0.22+Math.sin(now*0.0000148+ni*2.1)*r*0.044;
    var nba=0.17+0.11*Math.abs(Math.sin(ni*1.2+now*0.0000108));
    var nb=ctx.createLinearGradient(x-r,ny,x+r,ny+r*0.06);
    nb.addColorStop(0,'rgba(178,212,255,0)');nb.addColorStop(0.4,'rgba(178,212,255,'+nba+')');
    nb.addColorStop(0.6,'rgba(178,212,255,'+nba+')');nb.addColorStop(1,'rgba(178,212,255,0)');
    ctx.fillStyle=nb;ctx.fillRect(x-r,ny,r*2,r*0.12);
  }
  ctx.globalCompositeOperation='multiply';
  var gds=ctx.createRadialGradient(x-r*0.18,y+r*0.08,0,x-r*0.18,y+r*0.08,r*0.24);
  gds.addColorStop(0,'rgba(3,7,55,0.60)');gds.addColorStop(0.55,'rgba(5,10,72,0.28)');gds.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=gds;ctx.fillRect(0,0,W,H);
  ctx.restore();
  pAtm(x,y,r,'rgba(58,128,255,0.20)',0.20);
  pLimb(x,y,r,'rgba(128,198,255,0.68)');pDark(x,y,r,0.58);pSpec(x,y,r,0.18);
  ctx.restore();
}

/* ================================================================
   PLUTO — icy, heart-shaped Tombaugh Regio, nitrogen plains
   ================================================================ */
function drawPluto(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#e8d8c8','#c8b0a0','#a08878','#786050','#504030');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  /* Tombaugh Regio — heart shape (nitrogen ice plain) */
  ctx.globalCompositeOperation='screen';
  var tom=ctx.createRadialGradient(x+r*0.05,y+r*0.08,0,x+r*0.05,y+r*0.08,r*0.42);
  tom.addColorStop(0,'rgba(255,248,238,0.58)');tom.addColorStop(0.45,'rgba(245,238,225,0.32)');tom.addColorStop(0.75,'rgba(232,225,210,0.12)');tom.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=tom;ctx.fillRect(0,0,W,H);
  /* dark polar region */
  ctx.globalCompositeOperation='multiply';
  var pp=ctx.createRadialGradient(x,y-r*0.72,0,x,y-r*0.72,r*0.30);
  pp.addColorStop(0,'rgba(45,22,12,0.52)');pp.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=pp;ctx.fillRect(0,0,W,H);
  /* Cthulhu Macula — dark equatorial region */
  ctx.globalCompositeOperation='multiply';
  var cthu=ctx.createLinearGradient(x-r*0.60,y+r*0.02,x+r*0.10,y+r*0.14);
  cthu.addColorStop(0,'rgba(35,18,8,0)');cthu.addColorStop(0.3,'rgba(28,12,5,0.48)');
  cthu.addColorStop(0.7,'rgba(28,12,5,0.44)');cthu.addColorStop(1,'rgba(35,18,8,0)');
  ctx.fillStyle=cthu;ctx.fillRect(x-r,y+r*0.05,r*2,r*0.12);
  /* N polar bright methane ice */
  ctx.globalCompositeOperation='screen';
  var np3=ctx.createRadialGradient(x,y-r*0.78,0,x,y-r*0.78,r*0.20);
  np3.addColorStop(0,'rgba(238,228,212,0.80)');np3.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=np3;ctx.fillRect(0,0,W,H);
  ctx.restore();
  pLimb(x,y,r,'rgba(235,218,198,0.60)');pDark(x,y,r,0.65);pSpec(x,y,r,0.10);
  ctx.restore();
}

/* ================================================================
   VEGA NODE — crystalline energy orb, purple
   ================================================================ */
function drawVegaNode(x,y,r,now){
  ctx.save();
  pBase(x,y,r,'#e0d0ff','#9870e0','#6840b8','#402080','#200848');
  ctx.save();ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.clip();
  ctx.globalCompositeOperation='screen';
  for(var vi=0;vi<12;vi++){
    var va=(vi/12)*Math.PI*2+now*0.0000148;
    var vr=r*(0.09+0.66*Math.abs(Math.sin(vi*0.88+now*0.0000108)));
    ctx.beginPath();ctx.moveTo(x+Math.cos(va)*r*0.06,y+Math.sin(va)*r*0.06);
    ctx.lineTo(x+Math.cos(va)*vr,y+Math.sin(va)*vr);
    ctx.strokeStyle='rgba(198,165,255,0.20)';ctx.lineWidth=0.7;ctx.stroke();
  }
  var pulse=0.20+0.17*Math.sin(now*0.0034);
  var cp=ctx.createRadialGradient(x,y,0,x,y,r*0.46);
  cp.addColorStop(0,'rgba(225,210,255,'+pulse+')');cp.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=cp;ctx.fillRect(0,0,W,H);
  ctx.restore();
  ctx.globalCompositeOperation='screen';
  var ec=ctx.createRadialGradient(x,y,r*0.46,x,y,r*2.18);
  ec.addColorStop(0,'rgba(152,92,255,'+(0.32+0.12*Math.sin(now*0.0022)).toFixed(3)+')');
  ec.addColorStop(0.40,'rgba(118,68,218,0.10)');ec.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=ec;ctx.fillRect(0,0,W,H);
  pAtm(x,y,r,'rgba(152,92,255,0.28)',0.28);
  pLimb(x,y,r,'rgba(195,165,255,0.72)');pDark(x,y,r,0.55);pSpec(x,y,r,0.22);
  ctx.restore();
}

/* ================================================================
   PLANET TABLE
   ================================================================ */
var PT=[
  {id:'mercury',label:'GENERAL', route:'general', yF:0.168,rf:0.034,draw:drawMercury,orx:0.452,ory:0.026},
  {id:'venus',  label:'RISK',    route:'risk',    yF:0.268,rf:0.050,draw:drawVenus,  orx:0.458,ory:0.025},
  {id:'earth',  label:'SURVIVAL',route:'survival',yF:0.368,rf:0.056,draw:drawEarth, orx:0.462,ory:0.024,moon:true},
  {id:'mars',   label:'COLLAPSE',route:'collapse',yF:0.468,rf:0.042,draw:drawMars,  orx:0.458,ory:0.024},
  {id:'jupiter',label:'CIVIL',   route:'civil',   yF:0.590,rf:0.080,draw:drawJupiter,orx:0.461,ory:0.025},
  {id:'saturn', label:'SATURN',  route:'general', yF:0.710,rf:0.056,draw:drawSaturn, orx:0.463,ory:0.025},
  {id:'uranus', label:'URANUS',  route:'general', yF:0.808,rf:0.040,draw:drawUranus, orx:0.460,ory:0.024},
  {id:'neptune',label:'NEPTUNE', route:'general', yF:0.885,rf:0.036,draw:drawNeptune,orx:0.458,ory:0.023},
  {id:'pluto',  label:'PLUTO',   route:'general', yF:0.942,rf:0.022,draw:drawPluto,  orx:0.452,ory:0.022},
  {id:'vega',   label:'VEGA',    route:'vega',    yF:0.978,rf:0.034,draw:drawVegaNode,orx:0.450,ory:0.021}
];
function getR(p){return Math.min(W,H)*p.rf;}

function drawLabel(p,now){
  var px=W*0.50,py=H*p.yF,pr=getR(p);
  var isAct=p.route===activeRoute;
  var fs=Math.max(7,Math.min(12,pr*0.50));
  ctx.save();
  ctx.font='500 '+fs+'px "DM Mono",monospace';
  ctx.textAlign='center';ctx.textBaseline='top';
  if(isAct){ctx.shadowColor='rgba(200,168,75,0.90)';ctx.shadowBlur=10;ctx.fillStyle='rgba(248,208,100,0.97)';}
  else ctx.fillStyle='rgba(125,162,215,0.40)';
  ctx.fillText(p.label,px,py+pr+7);
  ctx.restore();
}

cv.addEventListener('click',function(e){
  var rc=cv.getBoundingClientRect(),cx=e.clientX-rc.left,cy=e.clientY-rc.top;
  PT.forEach(function(p){
    var px=W*0.5,py=H*p.yF,pr=getR(p)*1.68,dx=cx-px,dy=cy-py;
    if(dx*dx+dy*dy<pr*pr)window.KD_setRoute&&window.KD_setRoute(p.route);
  });
},{passive:true});
cv.addEventListener('touchend',function(e){
  if(e.changedTouches.length===1){var tc=e.changedTouches[0];cv.dispatchEvent(new MouseEvent('click',{clientX:tc.clientX,clientY:tc.clientY}));}
},{passive:true});

/* ================================================================
   RENDER
   ================================================================ */
function render(dt,now){
  drawBg(now);drawDust(now);drawStars(now);
  drawBelt(dt,now);drawKuiper(dt,now);
  PT.forEach(function(p){drawOrbit(H*p.yF,W*p.orx,H*p.ory,p.route===activeRoute,now);});
  drawSun(now);
  PT.forEach(function(p){if(p.route===activeRoute)pActive(W*0.5,H*p.yF,getR(p),now);});
  PT.forEach(function(p){
    var px=W*0.5,py=H*p.yF,pr=getR(p);
    p.draw(px,py,pr,now);
    if(p.moon)drawMoon(px+pr*1.58,py+pr*0.32,pr*0.31,now);
    drawLabel(p,now);
  });
}

/* ================================================================
   PUBLIC API
   ================================================================ */
window.KD_setState=function(s){};
window.KD_setRoute=function(r){
  if(!ROUTE_HUE[r])return;
  activeRoute=r;_tgtHue=ROUTE_HUE[r]||208;
  document.querySelectorAll('.rpill,.ctx-tag,.route-chip').forEach(function(el){el.classList.toggle('active',el.dataset.r===r);});
};
window.KD_pulse=function(){};window.LYLA_thinking=function(){};window.LYLA_answered=function(){};
window.setRoute=window.KD_setRoute;

/* ================================================================
   INIT
   ================================================================ */
doResize();
/* GPU compositing hints */
if(cv.style){
  cv.style.willChange='transform';
  cv.style.imageRendering='pixelated';
  cv.style.transform='translateZ(0)';
}
requestAnimationFrame(function(now){doResize();_last=now;_raf=requestAnimationFrame(loop);});

})();
