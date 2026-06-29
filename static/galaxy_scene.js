/* ================================================================
   KING DIADEM — Galaxy Scene v53 NIGHT EARTH SOVEREIGN
   Canvas-only — no external image URLs (CORS safe, always works)
   Target: dark void Earth + amber city lights dominant
   Atmosphere = thin rim only, not solid blue overlay
   ================================================================ */
(function(){
'use strict';

var cv = document.getElementById('galaxy');
if (!cv) return;
var ctx = cv.getContext('2d', {alpha:true, desynchronized:true});
var W=0, H=0, _raf=null, _last=0;
var activeRoute = 'general';
var isMobile = false;
var _burstAlpha = 0;

function loop(now){
  if(!window.KD||window.KD.visible!==false){
    _raf = requestAnimationFrame(loop);
  } else { _raf=null; return; }
  _last = now;
  render(now);
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
  var risk=d.risk&&d.risk.risk_score;
  if(risk>75) _burstAlpha=0.10;
},{passive:true});
window.addEventListener('KD:decision',function(e){
  var route=e.detail&&e.detail.route;
  if(route) activeRoute=route;
},{passive:true});

/* ================================================================
   STARFIELD — เบาลง เน้น performance
   ================================================================ */
var STARS=[];
function buildStars(){
  STARS=[];
  var total = isMobile ? 400 : 900;
  for(var i=0;i<total;i++){
    var sz=Math.random();
    var tier=sz<0.68?0:sz<0.90?1:2;
    var r=[0.12+Math.random()*0.18,0.24+Math.random()*0.35,0.48+Math.random()*0.75][tier];
    var a=[0.10+Math.random()*0.48,0.18+Math.random()*0.55,0.35+Math.random()*0.68][tier];
    var ct=Math.random()<0.06?'amber':Math.random()<0.08?'blue':'white';
    STARS.push({ x:Math.random()*W, y:Math.random()*H, r:r, a:a,
      tw:Math.random()<0.35, ph:Math.random()*Math.PI*2, sp:0.04+Math.random()*0.20, ct:ct,
      cross:tier===2&&Math.random()<0.14 });
  }
}

function drawStars(now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var a=s.tw?s.a*(0.28+0.72*Math.sin(now*s.sp*0.00028+s.ph)):s.a;
    var col=s.ct==='amber'?'rgba(255,205,110,'+a.toFixed(2)+')':
            s.ct==='blue' ?'rgba(155,198,255,'+a.toFixed(2)+')':
                           'rgba(238,242,255,'+a.toFixed(2)+')';
    if(s.cross&&a>s.a*0.55){
      ctx.strokeStyle=col; ctx.lineWidth=0.14;
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
   BG — deep space + amber nebula
   ================================================================ */
function drawBg(){
  ctx.fillStyle='#010108'; ctx.fillRect(0,0,W,H);
  ctx.save(); ctx.globalCompositeOperation='screen';
  var nb=ctx.createRadialGradient(W*0.08,H*0.92,0,W*0.08,H*0.92,W*0.55);
  nb.addColorStop(0,'rgba(198,115,30,0.22)');
  nb.addColorStop(0.30,'rgba(170,82,14,0.13)');
  nb.addColorStop(0.58,'rgba(125,55,8,0.06)');
  nb.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb; ctx.fillRect(0,0,W,H);
  if(_burstAlpha>0.002){
    _burstAlpha*=0.97;
    var bst=ctx.createRadialGradient(W*0.5,H*0.5,0,W*0.5,H*0.5,W*0.6);
    bst.addColorStop(0,'rgba(255,145,40,'+_burstAlpha.toFixed(3)+')');
    bst.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=bst; ctx.fillRect(0,0,W,H);
  }
  ctx.restore();
}

/* ================================================================
   SUN — top-left
   ================================================================ */
function drawSun(now){
  var cx=W*0.13, cy=H*0.11;
  var Rs=Math.min(W,H)*(isMobile?0.08:0.072);
  ctx.save(); ctx.globalCompositeOperation='screen';
  var c0=ctx.createRadialGradient(cx,cy,Rs*0.3,cx,cy,Rs*7.0);
  c0.addColorStop(0,'rgba(255,238,165,0.10)');
  c0.addColorStop(0.30,'rgba(255,195,75,0.05)');
  c0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c0; ctx.fillRect(0,0,W,H);
  var c1=ctx.createRadialGradient(cx,cy,Rs*0.45,cx,cy,Rs*3.2);
  c1.addColorStop(0,'rgba(255,222,105,0.25)');
  c1.addColorStop(0.55,'rgba(255,162,42,0.09)');
  c1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c1; ctx.fillRect(0,0,W,H);
  /* rays — fast, reduced */
  ctx.save();
  for(var ri=0;ri<12;ri++){
    var ra=(ri/12)*Math.PI*2+now*0.000007;
    var rl=Rs*(1.4+0.25*Math.sin(now*0.000007+ri));
    ctx.globalAlpha=0.012+0.005*Math.abs(Math.sin(now*0.00010+ri));
    var rx1=cx+Math.cos(ra)*Rs*0.55, ry1=cy+Math.sin(ra)*Rs*0.55;
    var rx2=cx+Math.cos(ra)*rl,      ry2=cy+Math.sin(ra)*rl;
    var rg=ctx.createLinearGradient(rx1,ry1,rx2,ry2);
    rg.addColorStop(0,'rgba(255,228,112,1)'); rg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle=rg; ctx.lineWidth=Rs*0.035; ctx.lineCap='round';
    ctx.beginPath();ctx.moveTo(rx1,ry1);ctx.lineTo(rx2,ry2);ctx.stroke();
  }
  ctx.globalAlpha=1; ctx.restore();
  ctx.globalCompositeOperation='source-over';
  var ph=ctx.createRadialGradient(cx-Rs*0.20,cy-Rs*0.14,Rs*0.01,cx+Rs*0.05,cy+Rs*0.07,Rs);
  ph.addColorStop(0,'#fffdee'); ph.addColorStop(0.06,'#fff3a0');
  ph.addColorStop(0.18,'#ffd038'); ph.addColorStop(0.34,'#ffaa16');
  ph.addColorStop(0.55,'#ff7800'); ph.addColorStop(0.74,'#e04000');
  ph.addColorStop(0.90,'#a01600'); ph.addColorStop(1,'#500600');
  ctx.fillStyle=ph; ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();
  ctx.globalCompositeOperation='multiply';
  var ld=ctx.createRadialGradient(cx,cy,Rs*0.55,cx,cy,Rs*1.02);
  ld.addColorStop(0,'rgba(0,0,0,0)'); ld.addColorStop(0.75,'rgba(80,18,0,0.20)'); ld.addColorStop(1,'rgba(20,4,0,0.55)');
  ctx.fillStyle=ld; ctx.beginPath(); ctx.arc(cx,cy,Rs*1.02,0,Math.PI*2); ctx.fill();
  ctx.globalCompositeOperation='screen';
  var hi=ctx.createRadialGradient(cx-Rs*0.17,cy-Rs*0.13,0,cx,cy,Rs*0.48);
  hi.addColorStop(0,'rgba(255,255,232,0.62)'); hi.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=hi; ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

/* ================================================================
   EARTH — using NASA texture image mapped to sphere
   
   วิธี: วาด canvas sphere โดย clip เป็นวงกลม แล้ว
   scroll texture horizontally ตาม earthLon
   texture ต้องถูก map แบบ cylindrical → sphere distortion
   ================================================================ */
function earthCX(){ return W*0.50; }
function earthCY(){ return H*(isMobile?0.56:0.54); }
function earthR(){  return Math.min(W,H)*(isMobile?0.34:0.40); }

/* Earth cache vars */
var _earthCacheR = 0;

/* ================================================================
   EARTH — Canvas night earth (primary, no external URLs)
   ================================================================ */

/* Static city dots — pre-generated, not rebuilt every frame */
var CITY_STATIC = [];
var CITY_BUILT = false;

/* Simplified city data: [lon_deg, lat_deg, count, spread, brightness] */
var CITY_DEF = [
  /* East Asia */
  [121,31,isMobile?80:180,0.038,1.0],[116,40,isMobile?75:170,0.036,0.95],
  [139,36,isMobile?88:200,0.040,1.0],[127,37,isMobile?58:140,0.033,0.92],
  [114,22,isMobile?48:120,0.031,0.90],[103,1,isMobile?42:105,0.030,0.90],
  [100,14,isMobile?32:80,0.028,0.85],[121,25,isMobile?38:95,0.028,0.88],
  [135,34,isMobile?42:105,0.030,0.90],[108,22,isMobile?18:45,0.020,0.78],
  /* South Asia */
  [77,29,isMobile?68:165,0.038,0.92],[73,19,isMobile?62:155,0.036,0.90],
  [88,23,isMobile?48:120,0.031,0.87],[80,13,isMobile?38:95,0.028,0.85],
  [67,25,isMobile?16:40,0.018,0.76],[90,24,isMobile?20:50,0.020,0.78],
  /* Middle East */
  [55,25,isMobile?28:70,0.028,0.88],[44,33,isMobile?18:45,0.022,0.80],
  [36,34,isMobile?20:50,0.022,0.82],[51,36,isMobile?16:40,0.018,0.78],
  /* Europe */
  [2,49,isMobile?95:235,0.058,0.96],[13,52,isMobile?58:145,0.040,0.92],
  [4,52,isMobile?52:132,0.038,0.91],[37,56,isMobile?48:120,0.036,0.90],
  [24,61,isMobile?38:95,0.032,0.88],[28,41,isMobile?28:70,0.026,0.85],
  [23,38,isMobile?16:40,0.018,0.80],[12,42,isMobile?18:45,0.020,0.82],
  [-4,41,isMobile?16:40,0.018,0.80],[18,50,isMobile?22:55,0.022,0.83],
  /* Africa */
  [13,7,isMobile?20:50,0.022,0.80],[28,-26,isMobile?22:55,0.024,0.82],
  [18,-34,isMobile?16:40,0.018,0.79],[31,30,isMobile?22:55,0.022,0.83],
  [3,6,isMobile?12:30,0.015,0.72],[37,-1,isMobile?14:35,0.016,0.74],
  /* North America */
  [-74,41,isMobile?88:220,0.053,0.96],[-77,39,isMobile?58:145,0.043,0.93],
  [-87,42,isMobile?62:155,0.043,0.92],[-83,42,isMobile?42:105,0.036,0.89],
  [-84,34,isMobile?38:95,0.033,0.88],[-80,26,isMobile?36:90,0.031,0.88],
  [-95,30,isMobile?38:95,0.033,0.87],[-118,34,isMobile?72:180,0.048,0.92],
  [-122,37,isMobile?52:130,0.040,0.90],[-98,30,isMobile?28:70,0.025,0.85],
  [-79,44,isMobile?42:105,0.036,0.89],[-99,19,isMobile?48:120,0.036,0.88],
  [-104,40,isMobile?25:62,0.023,0.83],[-97,33,isMobile?32:80,0.028,0.86],
  [-112,33,isMobile?28:70,0.025,0.84],[-123,49,isMobile?25:62,0.022,0.84],
  /* South America */
  [-43,-23,isMobile?52:130,0.040,0.90],[-46,-24,isMobile?58:145,0.043,0.91],
  [-58,-34,isMobile?32:80,0.030,0.86],[-70,-33,isMobile?25:62,0.024,0.83],
  [-77,-12,isMobile?20:50,0.020,0.80],
  /* Australia */
  [151,-34,isMobile?40:100,0.034,0.88],[145,-38,isMobile?32:80,0.028,0.85],
  [153,-27,isMobile?20:50,0.020,0.81],[115,-32,isMobile?16:40,0.018,0.79],
  /* Russia */
  [82,55,isMobile?18:45,0.020,0.80],[37,56,isMobile?44:110,0.035,0.89],
];

function lonLatToXY(lon_deg,lat_deg,earthLon,cx,cy,r){
  var lon_rad=(lon_deg*Math.PI/180)-earthLon;
  var lat_rad=lat_deg*Math.PI/180;
  while(lon_rad>Math.PI)  lon_rad-=Math.PI*2;
  while(lon_rad<-Math.PI) lon_rad+=Math.PI*2;
  var cosLat=Math.cos(lat_rad), sinLat=Math.sin(lat_rad);
  var depth=cosLat*Math.cos(lon_rad);
  return { x:cx+r*cosLat*Math.sin(lon_rad), y:cy-r*sinLat,
           visible:depth>-0.05, depth:depth };
}

function buildCityStatic(cx,cy,r,lon){
  CITY_STATIC=[];
  for(var ci=0;ci<CITY_DEF.length;ci++){
    var cd=CITY_DEF[ci];
    var pos=lonLatToXY(cd[0],cd[1],lon,cx,cy,r);
    if(!pos.visible||pos.depth<0.04) continue;
    var fade=Math.min(1,Math.pow(Math.max(0,pos.depth),0.35));
    var dn=cd[2], sp=cd[3], bright=cd[4];
    for(var di=0;di<dn;di++){
      var ang=Math.random()*Math.PI*2;
      var dist=Math.random()*sp*r;
      var dx=pos.x+Math.cos(ang)*dist, dy=pos.y+Math.sin(ang)*dist;
      var ddx=dx-cx, ddy=dy-cy;
      if(ddx*ddx+ddy*ddy>r*r*0.97) continue;
      CITY_STATIC.push({ x:dx,y:dy, sz:0.38+Math.random()*1.0,
        b:bright*fade*(0.32+Math.random()*0.52),
        ph:Math.random()*Math.PI*2, sp:0.0005+Math.random()*0.0009 });
    }
  }
  CITY_BUILT=true;
}

var _lastBuildLon=-999;
function drawEarthFallback(cx,cy,r,earthLon){
  /* Rebuild cities when lon changes enough */
  if(!CITY_BUILT||Math.abs(_earthCacheR-r)>2){  /* rebuild only on resize */
    buildCityStatic(cx,cy,r,earthLon);
    _lastBuildLon=earthLon;
    _earthCacheR=r;
  }

  ctx.save();

  /* base — near-black ocean */
  var oc=ctx.createRadialGradient(cx-r*0.16,cy-r*0.12,r*0.02,cx+r*0.10,cy+r*0.08,r*1.04);
  oc.addColorStop(0,'#060d18'); oc.addColorStop(0.08,'#040a12');
  oc.addColorStop(0.20,'#020709'); oc.addColorStop(0.42,'#010408');
  oc.addColorStop(0.68,'#010306'); oc.addColorStop(0.88,'#010203'); oc.addColorStop(1,'#000102');
  ctx.fillStyle=oc; ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.fill();

  /* dark continent shapes */
  ctx.save(); ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.clip();
  drawDarkContinents(cx,cy,r,earthLon);
  ctx.restore();

  /* city lights */
  ctx.save(); ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='screen';
  var now=_last;
  for(var i=0;i<CITY_STATIC.length;i++){
    var d=CITY_STATIC[i];
    var fl=0.78+0.22*Math.sin(now*d.sp+d.ph);
    var a=d.b*fl;
    ctx.globalAlpha=a*0.88;
    ctx.fillStyle='rgba(255,210,140,1)';
    ctx.beginPath(); ctx.arc(d.x,d.y,d.sz*0.46,0,Math.PI*2); ctx.fill();
    if(d.sz>0.7){
      ctx.globalAlpha=a*0.20;
      var dg=ctx.createRadialGradient(d.x,d.y,0,d.x,d.y,d.sz*2.2);
      dg.addColorStop(0,'rgba(255,210,140,1)'); dg.addColorStop(1,'rgba(0,0,0,0)');
      ctx.fillStyle=dg; ctx.beginPath(); ctx.arc(d.x,d.y,d.sz*2.2,0,Math.PI*2); ctx.fill();
    }
  }
  ctx.globalAlpha=1;
  ctx.restore();

  /* terminator */
  ctx.save(); ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.clip();
  ctx.globalCompositeOperation='multiply';
  var term=ctx.createLinearGradient(cx-r*0.40,cy,cx+r*0.60,cy);
  term.addColorStop(0,'rgba(0,0,0,0)'); term.addColorStop(0.25,'rgba(0,4,16,0.12)');
  term.addColorStop(0.55,'rgba(0,4,16,0.65)'); term.addColorStop(0.78,'rgba(0,2,10,0.90)'); term.addColorStop(1,'rgba(0,0,0,0.97)');
  ctx.fillStyle=term; ctx.fillRect(0,0,W,H);
  ctx.restore();

  /* atmosphere — THIN RIM ONLY — outside sphere edge, not overlaying city lights */
  ctx.save(); ctx.globalCompositeOperation='screen';
  /* outer diffuse glow — barely visible */
  var atm=ctx.createRadialGradient(cx,cy,r*0.96,cx,cy,r*1.22);
  atm.addColorStop(0,'rgba(100,175,255,0.22)');
  atm.addColorStop(0.30,'rgba(70,140,248,0.10)');
  atm.addColorStop(0.65,'rgba(45,100,220,0.04)');
  atm.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm; ctx.fillRect(0,0,W,H);
  /* sharp bright rim exactly at sphere edge */
  var atm2=ctx.createRadialGradient(cx,cy,r*0.975,cx,cy,r*1.035);
  atm2.addColorStop(0,'rgba(140,200,255,0.30)');
  atm2.addColorStop(0.55,'rgba(100,165,255,0.12)');
  atm2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm2; ctx.fillRect(0,0,W,H);
  ctx.restore();

  /* specular */
  ctx.save(); ctx.globalCompositeOperation='screen';
  var sp=ctx.createRadialGradient(cx-r*0.22,cy-r*0.18,0,cx-r*0.06,cy-r*0.05,r*0.38);
  sp.addColorStop(0,'rgba(255,255,255,0.08)'); sp.addColorStop(1,'rgba(0,0,0,0)');  /* subtle specular */
  ctx.fillStyle=sp; ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.fill();
  ctx.restore();

  /* limb darkening */
  ctx.save(); ctx.globalCompositeOperation='multiply';
  var ld=ctx.createRadialGradient(cx-r*0.12,cy-r*0.09,r*0.65,cx,cy,r*1.02);
  ld.addColorStop(0,'rgba(0,0,0,0)'); ld.addColorStop(0.74,'rgba(0,5,18,0.16)'); ld.addColorStop(1,'rgba(0,3,12,0.52)');
  ctx.fillStyle=ld; ctx.beginPath(); ctx.arc(cx,cy,r*1.02,0,Math.PI*2); ctx.fill();
  ctx.restore();

  ctx.restore();
}

/* minimal continent outlines for dark side */
var DARK_CONTINENTS=[
  {c:[8,12,6], p:[[[-18,14],[37,36],[51,11],[44,-11],[35,-35],[18,-35],[14,-17],[10,5],[-2,5],[-18,14]]]},
  {c:[7,10,5], p:[[[-10,35],[0,43],[20,43],[30,45],[28,62],[5,62],[-10,53],[-10,35]]]},
  {c:[7,10,5], p:[[[25,41],[60,21],[80,27],[95,24],[130,29],[148,43],[140,53],[100,51],[65,54],[35,59],[30,49],[25,41]]]},
  {c:[7,10,5], p:[[[68,35],[88,27],[80,7],[77,7],[72,13],[68,35]]]},
  {c:[7,10,5], p:[[[-140,69],[-65,49],[-80,25],[-90,15],[-105,19],[-120,21],[-124,35],[-130,49],[-140,59],[-140,69]]]},
  {c:[7,10,5], p:[[[-82,11],[-62,7],[-50,-6],[-34,-9],[-40,-23],[-70,-53],[-76,-41],[-80,-23],[-82,11]]]},
  {c:[12,8,4], p:[[[114,-21],[150,-21],[154,-25],[148,-38],[136,-38],[130,-32],[116,-34],[114,-26],[114,-21]]]},
  {c:[32,28,22],p:[[[-180,-70],[180,-70],[180,-90],[-180,-90],[-180,-70]]]},
];

function drawDarkContinents(cx,cy,r,earthLon){
  for(var ci=0;ci<DARK_CONTINENTS.length;ci++){
    var cont=DARK_CONTINENTS[ci], col=cont.c;
    for(var pi=0;pi<cont.p.length;pi++){
      var poly=cont.p[pi];
      var anyV=false;
      for(var vi=0;vi<poly.length;vi++){
        var tp=lonLatToXY(poly[vi][0],poly[vi][1],earthLon,cx,cy,r);
        if(tp.visible){anyV=true;break;}
      }
      if(!anyV) continue;
      ctx.beginPath();
      for(var ki=0;ki<poly.length;ki++){
        var pp=lonLatToXY(poly[ki][0],poly[ki][1],earthLon,cx,cy,r);
        if(ki===0) ctx.moveTo(pp.x,pp.y); else ctx.lineTo(pp.x,pp.y);
      }
      ctx.closePath();
      ctx.fillStyle='rgba('+col[0]+','+col[1]+','+col[2]+',0.55)';
      ctx.fill();
    }
  }
}

function drawEarth(now){
  var cx=earthCX(), cy=earthCY(), r=earthR();
  var earthLon=(now*0.000055)%(Math.PI*2);
  drawEarthFallback(cx,cy,r,earthLon);
}

/* ================================================================
   GOLD ORBIT RING + satellites
   ================================================================ */
function drawEarthRing(now){
  var cx=earthCX(), cy=earthCY(), r=earthR();
  var ringR=r*1.52, tilt=0.20;
  var isActive=activeRoute==='survival';

  ctx.save(); ctx.globalCompositeOperation='screen';

  /* glow */
  if(isActive){
    ctx.save();
    ctx.strokeStyle='rgba(255,210,55,0.32)';
    ctx.lineWidth=ringR*0.042*tilt*7;
    ctx.beginPath(); ctx.ellipse(cx,cy,ringR,ringR*tilt,0,0,Math.PI*2); ctx.stroke();
    ctx.restore();
  }

  /* main ring */
  ctx.strokeStyle=isActive?'rgba(255,215,58,0.75)':'rgba(195,198,215,0.16)';
  ctx.lineWidth=isActive?1.8:0.7;
  ctx.beginPath(); ctx.ellipse(cx,cy,ringR,ringR*tilt,0,0,Math.PI*2); ctx.stroke();

  /* dotted inner */
  ctx.setLineDash([4,9]);
  ctx.strokeStyle=isActive?'rgba(255,222,78,0.42)':'rgba(175,178,198,0.08)';
  ctx.lineWidth=isActive?0.9:0.4;
  ctx.beginPath(); ctx.ellipse(cx,cy,ringR*0.91,ringR*0.91*tilt,0,0,Math.PI*2); ctx.stroke();
  ctx.setLineDash([]);

  /* label */
  var la=Math.PI*0.60;
  var lx=cx+Math.cos(la)*ringR, ly=cy+Math.sin(la)*ringR*tilt;
  ctx.font='600 '+(isMobile?9:12)+'px "DM Mono",monospace';
  ctx.fillStyle=isActive?'rgba(255,225,98,0.92)':'rgba(175,178,205,0.42)';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  if(isActive){ ctx.shadowColor='rgba(255,210,55,0.78)'; ctx.shadowBlur=7; }
  ctx.fillText('SURVIVAL',lx,ly-ringR*tilt*0.12);
  ctx.shadowBlur=0;

  /* satellites */
  [[now*0.000052,0.88],[now*0.000052+Math.PI*1.35,0.70]].forEach(function(s){
    var sa=s[0]%(Math.PI*2), sc=s[1];
    var sx=cx+Math.cos(sa)*ringR, sy=cy+Math.sin(sa)*ringR*tilt;
    ctx.fillStyle='rgba(200,215,242,'+sc+')';
    ctx.beginPath(); ctx.arc(sx,sy,2.2,0,Math.PI*2); ctx.fill();
    ctx.strokeStyle='rgba(200,215,242,'+(sc*0.7)+')'; ctx.lineWidth=0.7;
    var sl=4.5;
    ctx.beginPath(); ctx.moveTo(sx-sl,sy); ctx.lineTo(sx+sl,sy); ctx.stroke();
  });

  ctx.restore();
}

/* ================================================================
   ORBIT RINGS — route labels
   ================================================================ */
var ORBIT_RINGS=[
  {route:'general',lbl:'GENERAL',orb:0.27,tilt:0.20,ao:0.22},
  {route:'risk',   lbl:'RISK',   orb:0.35,tilt:0.20,ao:0.88},
  {route:'collapse',lbl:'COLLAPSE',orb:0.43,tilt:0.20,ao:1.65},
  {route:'civil',  lbl:'CIVIL',  orb:0.51,tilt:0.20,ao:2.42},
  {route:'vega',   lbl:'VEGA',   orb:0.59,tilt:0.20,ao:3.22},
  {route:'',       lbl:'PLUTO',  orb:0.67,tilt:0.20,ao:4.02},
];

function drawOrbitRings(){
  var cx=earthCX(), cy=earthCY();
  ctx.save(); ctx.globalCompositeOperation='screen';
  ORBIT_RINGS.forEach(function(or){
    var R=Math.min(W,H)*or.orb;
    var isAct=or.route&&or.route===activeRoute;
    ctx.strokeStyle=isAct?'rgba(210,190,118,0.26)':'rgba(155,160,188,0.07)';
    ctx.lineWidth=isAct?0.88:0.30;
    ctx.beginPath(); ctx.ellipse(cx,cy,R,R*or.tilt,0,0,Math.PI*2); ctx.stroke();
    if(or.lbl){
      var lx2=cx+Math.cos(or.ao)*R, ly2=cy+Math.sin(or.ao)*R*or.tilt;
      ctx.font='500 '+(isMobile?6:8)+'px "DM Mono",monospace';
      ctx.fillStyle=isAct?'rgba(255,228,98,0.80)':'rgba(145,150,178,0.28)';
      ctx.textAlign='center'; ctx.textBaseline='middle';
      ctx.fillText(or.lbl,lx2,ly2);
    }
  });
  ctx.restore();
}

/* ================================================================
   SMALL PLANETS
   ================================================================ */
function pSphere(x,y,r,stops){
  var g=ctx.createRadialGradient(x-r*0.32,y-r*0.26,r*0.01,x+r*0.12,y+r*0.12,r*1.04);
  for(var i=0;i<stops.length;i++) g.addColorStop(stops[i][0],stops[i][1]);
  ctx.fillStyle=g; ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
}
function pTm(x,y,r,s){ s=s||0.75;
  ctx.save(); ctx.globalCompositeOperation='multiply';
  var g=ctx.createRadialGradient(x+r*0.28,y+r*0.22,r*0.05,x+r*0.32,y+r*0.26,r*1.08);
  g.addColorStop(0,'rgba(0,0,0,0)'); g.addColorStop(0.44,'rgba(0,0,0,'+(s*0.35).toFixed(3)+')');
  g.addColorStop(0.72,'rgba(0,0,0,'+(s*0.72).toFixed(3)+')'); g.addColorStop(1,'rgba(0,0,0,'+s+')');
  ctx.fillStyle=g; ctx.beginPath(); ctx.arc(x,y,r*1.06,0,Math.PI*2); ctx.fill(); ctx.restore();
}
function pRm(x,y,r,col){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.28,y-r*0.22,r*0.82,x,y,r*1.02);
  g.addColorStop(0,col); g.addColorStop(0.40,'rgba(255,255,255,0.02)'); g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.beginPath(); ctx.arc(x,y,r*1.02,0,Math.PI*2); ctx.fill(); ctx.restore();
}

var SMALL_PLANETS=[
  {id:'mercury',lbl:'GENERAL',route:'general',orb:0.27,per:0.241,tilt:0.20,r:0.015,rm:0.020,
   draw:function(x,y,r){ ctx.save(); pSphere(x,y,r,[[0,'#e8ddd0'],[0.35,'#a89878'],[0.75,'#5a3c20'],[1,'#180c04']]); pTm(x,y,r,0.78); pRm(x,y,r,'rgba(225,185,122,0.42)'); ctx.restore(); }},
  {id:'venus',lbl:'RISK',route:'risk',orb:0.35,per:0.615,tilt:0.20,r:0.020,rm:0.026,
   draw:function(x,y,r){ ctx.save(); pSphere(x,y,r,[[0,'#fff8c8'],[0.25,'#e0b838'],[0.60,'#a05c0c'],[1,'#301200']]); pTm(x,y,r,0.65); pRm(x,y,r,'rgba(255,230,145,0.52)'); ctx.restore(); }},
  {id:'mars',lbl:'COLLAPSE',route:'collapse',orb:0.43,per:1.881,tilt:0.20,r:0.018,rm:0.024,
   draw:function(x,y,r){ ctx.save(); pSphere(x,y,r,[[0,'#f4b090'],[0.25,'#c85838'],[0.60,'#7a2408'],[1,'#200400']]); pTm(x,y,r,0.76); pRm(x,y,r,'rgba(255,150,80,0.42)'); ctx.restore(); }},
  {id:'jupiter',lbl:'CIVIL',route:'civil',orb:0.51,per:11.86,tilt:0.20,r:0.034,rm:0.043,
   draw:function(x,y,r,now){
     ctx.save(); pSphere(x,y,r,[[0,'#f4e8c8'],[0.22,'#c89845'],[0.55,'#9a5820'],[1,'#381800']]);
     ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip(); ctx.globalCompositeOperation='overlay';
     for(var bi=0;bi<6;bi++){
       var by=y-r*0.86+bi*r*0.29+Math.sin(now*0.0000044+bi*0.7)*r*0.012;
       var ba=0.08+0.09*Math.abs(Math.sin(bi*0.5+now*0.0000044));
       var jg=ctx.createLinearGradient(x-r,by,x+r,by+r*0.03);
       var bc=bi%2===0?'rgba(140,68,34,'+ba+')':'rgba(185,125,55,'+ba+')';
       jg.addColorStop(0,'rgba(0,0,0,0)');jg.addColorStop(0.25,bc);jg.addColorStop(0.75,bc);jg.addColorStop(1,'rgba(0,0,0,0)');
       ctx.fillStyle=jg; ctx.fillRect(x-r,by,r*2,r*0.22);
     }
     ctx.restore(); pTm(x,y,r,0.60); pRm(x,y,r,'rgba(255,205,145,0.40)'); ctx.restore();
   }},
  {id:'saturn',lbl:'VEGA',route:'vega',orb:0.59,per:29.46,tilt:0.20,r:0.030,rm:0.038,
   draw:function(x,y,r){
     ctx.save(); pSphere(x,y,r,[[0,'#f8f0c0'],[0.25,'#d8b840'],[0.60,'#9a7010'],[1,'#3a2600']]);
     var rt=0.28;
     var rings=[{ri:1.22,ro:1.48,R:198,G:183,B:145,a:0.30},{ri:1.48,ro:1.82,R:215,G:200,B:162,a:0.52},{ri:1.84,ro:2.12,R:205,G:190,B:155,a:0.44}];
     ctx.save(); ctx.globalCompositeOperation='screen';
     rings.forEach(function(rng){
       var rg=ctx.createLinearGradient(x-r*rng.ro,y,x+r*rng.ro,y);
       rg.addColorStop(0,'rgba(0,0,0,0)'); rg.addColorStop(0.10,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.52).toFixed(3)+')');
       rg.addColorStop(0.50,'rgba('+rng.R+','+rng.G+','+rng.B+','+rng.a+')'); rg.addColorStop(0.90,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.52).toFixed(3)+')'); rg.addColorStop(1,'rgba(0,0,0,0)');
       ctx.beginPath(); ctx.ellipse(x,y,r*rng.ro,r*rng.ro*rt,0,Math.PI,Math.PI*2); ctx.ellipse(x,y,r*rng.ri,r*rng.ri*rt,0,Math.PI*2,Math.PI,true); ctx.fillStyle=rg; ctx.fill();
     });
     ctx.restore(); pTm(x,y,r,0.58); pRm(x,y,r,'rgba(255,235,150,0.48)');
     ctx.save(); ctx.globalCompositeOperation='screen';
     rings.forEach(function(rng){
       var rg2=ctx.createLinearGradient(x-r*rng.ro,y,x+r*rng.ro,y);
       rg2.addColorStop(0,'rgba(0,0,0,0)'); rg2.addColorStop(0.10,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.52).toFixed(3)+')');
       rg2.addColorStop(0.50,'rgba('+rng.R+','+rng.G+','+rng.B+','+rng.a+')'); rg2.addColorStop(0.90,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.52).toFixed(3)+')'); rg2.addColorStop(1,'rgba(0,0,0,0)');
       ctx.beginPath(); ctx.ellipse(x,y,r*rng.ro,r*rng.ro*rt,0,0,Math.PI); ctx.ellipse(x,y,r*rng.ri,r*rng.ri*rt,0,Math.PI,0,true); ctx.fillStyle=rg2; ctx.fill();
     });
     ctx.restore(); ctx.restore();
   }},
  {id:'pluto',lbl:'PLUTO',route:'',orb:0.67,per:247.9,tilt:0.20,r:0.009,rm:0.012,
   draw:function(x,y,r){ ctx.save(); pSphere(x,y,r,[[0,'#d8c8b0'],[0.42,'#8a6848'],[1,'#281408']]); pTm(x,y,r,0.82); pRm(x,y,r,'rgba(185,160,136,0.28)'); ctx.restore(); }},
];

var _spCache=[];
function spPos(p,now){
  var BASE=0.000032;
  var angle=(now*BASE/p.per)%(Math.PI*2);
  var cx=earthCX(), cy=earthCY();
  var R=Math.min(W,H)*p.orb;
  return {x:cx+Math.cos(angle)*R, y:cy+Math.sin(angle)*R*p.tilt};
}

function pAct(x,y,r,now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var pulse=0.62+0.38*Math.sin(now*0.0021);
  var g=ctx.createRadialGradient(x,y,r*0.5,x,y,r*2.8);
  g.addColorStop(0,'rgba(255,205,68,'+(0.26*pulse).toFixed(3)+')'); g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  ctx.globalAlpha=0.16*pulse; ctx.strokeStyle='rgba(255,198,58,0.70)'; ctx.lineWidth=0.8;
  ctx.beginPath();ctx.arc(x,y,r*1.12,0,Math.PI*2);ctx.stroke();
  ctx.globalAlpha=1; ctx.restore();
}

function spLabel(p,pos){
  if(!p.lbl) return;
  var r=Math.min(W,H)*(isMobile?p.rm:p.r);
  var isAct=p.route&&p.route===activeRoute;
  ctx.save(); ctx.font='500 '+(isMobile?6:8)+'px "DM Mono",monospace';
  ctx.textAlign='center'; ctx.textBaseline='top';
  if(isAct){ ctx.shadowColor='rgba(255,215,92,0.76)'; ctx.shadowBlur=5; ctx.fillStyle='rgba(255,232,165,0.95)'; }
  else { ctx.fillStyle='rgba(158,162,192,0.30)'; }
  ctx.fillText(p.lbl,pos.x,pos.y+r+3); ctx.restore();
}

cv.addEventListener('click',function(e){
  var rc=cv.getBoundingClientRect(), mx=e.clientX-rc.left, my=e.clientY-rc.top;
  for(var i=0;i<_spCache.length;i++){
    var pp=_spCache[i], p=SMALL_PLANETS[i];
    var r=Math.min(W,H)*(isMobile?p.rm:p.r)*2.2;
    var dx=mx-pp.x, dy=my-pp.y;
    if(dx*dx+dy*dy<r*r&&p.route) window.KD_setRoute&&window.KD_setRoute(p.route);
  }
},{passive:true});
cv.addEventListener('touchend',function(e){
  if(e.changedTouches.length===1){var t=e.changedTouches[0];cv.dispatchEvent(new MouseEvent('click',{clientX:t.clientX,clientY:t.clientY}));}
},{passive:true});

/* ================================================================
   MOON
   ================================================================ */
function drawMoon(now){
  var cx=earthCX(), cy=earthCY(), er=earthR();
  var ma=(now*0.000082)%(Math.PI*2);
  var md=er*1.62, mt=0.18;
  var mx=cx+Math.cos(ma)*md, my=cy+Math.sin(ma)*md*mt;
  var mr=er*0.272;
  ctx.save();
  pSphere(mx,my,mr,[[0,'#f0eee6'],[0.18,'#dcd4c4'],[0.45,'#b0a090'],[0.72,'#6c5c4e'],[1,'#28180e']]);
  ctx.save(); ctx.beginPath(); ctx.arc(mx,my,mr,0,Math.PI*2); ctx.clip();
  [[-.14,-.10,.28],[.12,-.08,.22],[.18,.10,.20]].forEach(function(m){
    var g=ctx.createRadialGradient(mx+m[0]*mr,my+m[1]*mr,0,mx+m[0]*mr,my+m[1]*mr,m[2]*mr);
    g.addColorStop(0,'rgba(26,16,10,0.50)'); g.addColorStop(0.6,'rgba(26,16,10,0.20)'); g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply'; ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pTm(mx,my,mr,0.80); pRm(mx,my,mr,'rgba(202,186,168,0.36)');
  ctx.restore();
}

/* ================================================================
   RENDER
   ================================================================ */
function render(now){
  drawBg();
  drawStars(now);
  drawSun(now);
  drawOrbitRings();
  _spCache=[];
  SMALL_PLANETS.forEach(function(p){
    var pos=spPos(p,now); _spCache.push(pos);
    var r=Math.min(W,H)*(isMobile?p.rm:p.r);
    if(p.route&&p.route===activeRoute) pAct(pos.x,pos.y,r,now);
    p.draw(pos.x,pos.y,r,now); spLabel(p,pos);
  });
  drawEarthRing(now);
  drawEarth(now);
  drawMoon(now);
}

/* ================================================================
   PUBLIC API
   ================================================================ */
window.KD_setRoute=function(route){
  activeRoute=route;
  if(typeof window.setRoute==='function') window.setRoute(route);
  window.dispatchEvent(new CustomEvent('KD:routeChange',{detail:{route:route}}));
};
window.KD_pulse=window.KD_pulse||function(route){ if(route) window.KD_setRoute(route); };
window.KD_setState=window.KD_setState||function(key,val){
  if(!window.KD) window.KD={}; if(!window.KD.state) window.KD.state={}; window.KD.state[key]=val;
};

doResize();
_last=performance.now();
_raf=requestAnimationFrame(loop);

})();
