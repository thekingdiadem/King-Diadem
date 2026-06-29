/* ================================================================
   KING DIADEM — Galaxy Scene v51 NIGHT EARTH SOVEREIGN
   Reference: รูป 1 (solar system layout) + รูป 2 (night Earth)
   
   - Earth ครึ่งจอ กลางจอ NIGHT SIDE — city lights สว่าง amber
   - Gold orbit ring รอบ Earth label "SURVIVAL"
   - Blue atmosphere rim ชัด
   - ดวงอาทิตย์บนซ้าย สว่างมาก
   - ดาวเคราะห์อื่นโคจรรอบ orbit rings มี route labels
   - Dense starfield + amber nebula bottom-left
   - ดาวเทียมเล็กๆ บน orbit ring
   ================================================================ */
(function(){
'use strict';

var cv = document.getElementById('galaxy');
if (!cv) return;
var ctx = cv.getContext('2d', {alpha:true, desynchronized:true});
var W=0, H=0, _raf=null, _last=0, _dt=0;
var activeRoute = 'general';
var isMobile = false;
var _burstAlpha = 0;

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
  _cityBuilt = false;
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
  else if(risk>45) _burstAlpha=0.05;
},{passive:true});
window.addEventListener('KD:decision',function(e){
  var route=e.detail&&e.detail.route;
  if(route) activeRoute=route;
},{passive:true});

/* ================================================================
   STARFIELD — dense real, 2000+
   ================================================================ */
var STARS=[];
function buildStars(){
  STARS=[];
  var total=isMobile?700:1800;
  for(var i=0;i<total;i++){
    var sz=Math.random();
    var tier=sz<0.65?0:sz<0.88?1:2;
    var r=[0.12+Math.random()*0.18,0.25+Math.random()*0.38,0.50+Math.random()*0.85][tier];
    var a=[0.10+Math.random()*0.50,0.20+Math.random()*0.60,0.38+Math.random()*0.72][tier];
    var ct=Math.random()<0.06?'amber':Math.random()<0.09?'blue':Math.random()<0.04?'red':'white';
    STARS.push({
      x:Math.random()*W, y:Math.random()*H, r:r, a:a,
      tw:Math.random()<0.38, ph:Math.random()*Math.PI*2,
      sp:0.04+Math.random()*0.22, ct:ct,
      cross:tier===2&&Math.random()<0.16
    });
  }
}

function drawStars(now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var a=s.tw?s.a*(0.28+0.72*Math.sin(now*s.sp*0.00030+s.ph)):s.a;
    var col=s.ct==='amber'?'rgba(255,205,110,'+a.toFixed(3)+')':
            s.ct==='blue' ?'rgba(155,198,255,'+a.toFixed(3)+')':
            s.ct==='red'  ?'rgba(255,155,115,'+a.toFixed(3)+')':
                           'rgba(240,244,255,'+a.toFixed(3)+')';
    if(s.cross&&a>s.a*0.52){
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
   BACKGROUND — deep void + amber nebula bottom-left (ref รูป 1,2)
   ================================================================ */
function drawBg(now){
  ctx.clearRect(0,0,W,H);
  ctx.fillStyle='#010108'; ctx.fillRect(0,0,W,H);

  ctx.save(); ctx.globalCompositeOperation='screen';

  /* amber nebula bottom-left — เหมือน ref */
  var nb0=ctx.createRadialGradient(W*0.06,H*0.94,0,W*0.06,H*0.94,W*0.58);
  nb0.addColorStop(0,'rgba(200,118,32,0.24)');
  nb0.addColorStop(0.25,'rgba(175,85,16,0.15)');
  nb0.addColorStop(0.52,'rgba(130,58,8,0.07)');
  nb0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb0; ctx.fillRect(0,0,W,H);

  var mw=ctx.createLinearGradient(0,H,W*0.48,H*0.20);
  mw.addColorStop(0,'rgba(178,92,22,0.16)');
  mw.addColorStop(0.35,'rgba(148,72,14,0.09)');
  mw.addColorStop(0.68,'rgba(95,45,6,0.03)');
  mw.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=mw; ctx.fillRect(0,0,W,H);

  /* deep blue top-right */
  var nb1=ctx.createRadialGradient(W*0.90,H*0.10,0,W*0.90,H*0.10,W*0.42);
  nb1.addColorStop(0,'rgba(18,38,108,0.055)');
  nb1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb1; ctx.fillRect(0,0,W,H);

  if(_burstAlpha>0.002){
    _burstAlpha*=0.97;
    var bst=ctx.createRadialGradient(W*0.5,H*0.5,0,W*0.5,H*0.5,W*0.65);
    bst.addColorStop(0,'rgba(255,145,40,'+_burstAlpha.toFixed(3)+')');
    bst.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=bst; ctx.fillRect(0,0,W,H);
  }
  ctx.restore();
}

/* ================================================================
   SUN — top-left, large, bright (ref รูป 1)
   ================================================================ */
function drawSun(now){
  var cx=W*0.14, cy=H*0.12;
  var Rs=Math.min(W,H)*(isMobile?0.09:0.08);
  ctx.save(); ctx.globalCompositeOperation='screen';

  /* wide corona */
  var c0=ctx.createRadialGradient(cx,cy,Rs*0.3,cx,cy,Rs*8.0);
  c0.addColorStop(0,'rgba(255,240,170,0.10)');
  c0.addColorStop(0.25,'rgba(255,200,80,0.06)');
  c0.addColorStop(0.55,'rgba(255,160,40,0.02)');
  c0.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c0; ctx.fillRect(0,0,W,H);

  /* mid corona */
  var c1=ctx.createRadialGradient(cx,cy,Rs*0.4,cx,cy,Rs*3.5);
  c1.addColorStop(0,'rgba(255,225,110,0.28)');
  c1.addColorStop(0.5,'rgba(255,165,45,0.10)');
  c1.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=c1; ctx.fillRect(0,0,W,H);

  /* rays */
  ctx.save();
  for(var ri=0;ri<16;ri++){
    var ra=(ri/16)*Math.PI*2+now*0.000007;
    var rl=Rs*(1.5+0.3*Math.sin(now*0.000008+ri*0.8));
    ctx.globalAlpha=0.015+0.007*Math.abs(Math.sin(now*0.00011+ri));
    var rx1=cx+Math.cos(ra)*Rs*0.55, ry1=cy+Math.sin(ra)*Rs*0.55;
    var rx2=cx+Math.cos(ra)*rl,      ry2=cy+Math.sin(ra)*rl;
    var rg=ctx.createLinearGradient(rx1,ry1,rx2,ry2);
    rg.addColorStop(0,'rgba(255,228,115,1)');
    rg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle=rg; ctx.lineWidth=Rs*0.038; ctx.lineCap='round';
    ctx.beginPath();ctx.moveTo(rx1,ry1);ctx.lineTo(rx2,ry2);ctx.stroke();
  }
  ctx.globalAlpha=1; ctx.restore();

  /* body */
  ctx.globalCompositeOperation='source-over';
  var ph=ctx.createRadialGradient(cx-Rs*0.22,cy-Rs*0.16,Rs*0.01,cx+Rs*0.06,cy+Rs*0.08,Rs);
  ph.addColorStop(0,'#fffdee'); ph.addColorStop(0.05,'#fff3a0');
  ph.addColorStop(0.16,'#ffd038'); ph.addColorStop(0.32,'#ffaa16');
  ph.addColorStop(0.52,'#ff7800'); ph.addColorStop(0.72,'#e04000');
  ph.addColorStop(0.88,'#a01600'); ph.addColorStop(1,'#500600');
  ctx.fillStyle=ph;
  ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();

  ctx.globalCompositeOperation='multiply';
  var ld=ctx.createRadialGradient(cx,cy,Rs*0.55,cx,cy,Rs*1.02);
  ld.addColorStop(0,'rgba(0,0,0,0)');
  ld.addColorStop(0.72,'rgba(80,18,0,0.20)');
  ld.addColorStop(1,'rgba(20,4,0,0.55)');
  ctx.fillStyle=ld;
  ctx.beginPath(); ctx.arc(cx,cy,Rs*1.02,0,Math.PI*2); ctx.fill();

  ctx.globalCompositeOperation='screen';
  var hi=ctx.createRadialGradient(cx-Rs*0.18,cy-Rs*0.14,0,cx,cy,Rs*0.50);
  hi.addColorStop(0,'rgba(255,255,235,0.65)');
  hi.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=hi;
  ctx.beginPath(); ctx.arc(cx,cy,Rs,0,Math.PI*2); ctx.fill();
  ctx.restore();
}

/* ================================================================
   EARTH — NIGHT SOVEREIGN — ครึ่งจอ กลางจอ
   Night side dominant — city lights amber สว่างมาก
   หมุนแสดงทุกทวีปด้วย lon/lat orthographic projection
   ================================================================ */
function earthCX(){ return W*0.50; }
function earthCY(){ return H*(isMobile?0.55:0.54); }
function earthR(){  return Math.min(W,H)*(isMobile?0.34:0.40); }

/* lon/lat → screen xy (orthographic projection) */
function lonLatToXY(lon_deg,lat_deg,earthLon,cx,cy,r){
  var lon_rad=(lon_deg*Math.PI/180)-earthLon;
  var lat_rad=lat_deg*Math.PI/180;
  while(lon_rad>Math.PI)  lon_rad-=Math.PI*2;
  while(lon_rad<-Math.PI) lon_rad+=Math.PI*2;
  var cosLat=Math.cos(lat_rad), sinLat=Math.sin(lat_rad);
  var cosLon=Math.cos(lon_rad), sinLon=Math.sin(lon_rad);
  var depth=cosLat*cosLon;
  return {
    x:cx+r*cosLat*sinLon,
    y:cy-r*sinLat,
    visible:depth>-0.05,
    depth:depth
  };
}

/* ── City lights data — comprehensive worldwide ─────────────── */
/* [lon, lat, count, spread, R, G, B, brightness] */
var CITY_DATA=[
  /* East Asia — highly dense */
  [121,31,isMobile?80:200,0.040,255,215,145,0.95,'shanghai'],
  [116,40,isMobile?75:190,0.038,255,212,142,0.93,'beijing'],
  [139,36,isMobile?85:210,0.042,255,220,148,0.96,'tokyo_yokohama'],
  [135,34,isMobile?45:110,0.032,255,215,142,0.90,'osaka'],
  [127,37,isMobile?60:150,0.035,255,215,140,0.92,'seoul'],
  [114,22,isMobile?50:125,0.033,255,210,138,0.90,'hong_kong'],
  [121,25,isMobile?40:100,0.030,255,212,140,0.88,'taipei'],
  [103,1, isMobile?45:110,0.032,255,210,138,0.90,'singapore'],
  [100,14,isMobile?35:88, 0.030,255,205,132,0.85,'bangkok'],
  [106,11,isMobile?30:75, 0.028,255,200,128,0.82,'hcmc'],
  [106,11,isMobile?25:62, 0.025,255,198,125,0.80,'hanoi_offset'],
  [108,22,isMobile?20:50, 0.022,255,195,122,0.78,'guangzhou'],
  /* South Asia */
  [77,29, isMobile?70:175,0.040,255,210,138,0.92,'delhi'],
  [73,19, isMobile?65:160,0.038,255,210,138,0.90,'mumbai'],
  [88,23, isMobile?50:125,0.033,255,205,132,0.87,'kolkata'],
  [80,13, isMobile?40:100,0.030,255,205,130,0.85,'chennai'],
  [85,20, isMobile?30:75, 0.028,255,202,128,0.82,'bhubaneswar'],
  [72,24, isMobile?20:50, 0.022,255,200,125,0.78,'ahmedabad'],
  [67,25, isMobile?18:45, 0.020,255,198,122,0.76,'karachi'],
  [74,32, isMobile?18:45, 0.020,255,200,126,0.77,'lahore'],
  [90,24, isMobile?22:55, 0.022,255,200,126,0.78,'dhaka'],
  [80,7,  isMobile?15:38, 0.018,255,198,122,0.75,'colombo'],
  /* Middle East */
  [55,25, isMobile?30:75, 0.030,255,215,142,0.88,'dubai_abudhabi'],
  [44,33, isMobile?20:50, 0.025,255,205,130,0.82,'baghdad'],
  [36,34, isMobile?22:55, 0.025,255,208,132,0.83,'tel_aviv'],
  [51,36, isMobile?18:45, 0.020,255,205,130,0.80,'tehran'],
  [46,25, isMobile?15:38, 0.018,255,210,135,0.78,'riyadh'],
  [39,21, isMobile?12:30, 0.016,255,205,128,0.75,'jeddah'],
  /* Europe — dense network */
  [2,49,  isMobile?100:250,0.060,255,228,158,0.95,'europe_core'],
  [13,52, isMobile?60:150,0.042,255,225,155,0.92,'berlin'],
  [4,52,  isMobile?55:138,0.040,255,225,155,0.91,'amsterdam'],
  [24,61, isMobile?40:100,0.035,255,220,150,0.88,'scandinavia'],
  [37,56, isMobile?50:125,0.038,255,220,148,0.90,'moscow'],
  [31,30, isMobile?25:62, 0.025,255,215,140,0.85,'cairo'],
  [28,41, isMobile?30:75, 0.028,255,218,142,0.86,'istanbul'],
  [23,38, isMobile?18:45, 0.020,255,215,140,0.82,'athens'],
  [12,42, isMobile?20:50, 0.022,255,220,145,0.83,'rome'],
  [-4,41, isMobile?18:45, 0.020,255,218,142,0.82,'madrid'],
  [-9,39, isMobile?15:38, 0.018,255,215,140,0.80,'lisbon'],
  [18,50, isMobile?25:62, 0.024,255,222,148,0.84,'warsaw'],
  [14,48, isMobile?20:50, 0.022,255,220,146,0.83,'vienna'],
  [26,45, isMobile?15:38, 0.018,255,215,140,0.80,'bucharest'],
  /* Africa — city clusters */
  [13,7,  isMobile?22:55, 0.025,255,200,125,0.80,'nigeria_lagos'],
  [18,-4, isMobile?15:38, 0.018,255,195,120,0.76,'kinshasa'],
  [39,-7, isMobile?12:30, 0.016,255,195,120,0.74,'dar_es_salaam'],
  [28,-26,isMobile?25:62, 0.026,255,205,130,0.83,'johannesburg'],
  [18,-34,isMobile?18:45, 0.020,255,200,125,0.80,'cape_town'],
  [3,6,   isMobile?15:38, 0.018,255,198,122,0.77,'accra'],
  [-17,15,isMobile?12:30, 0.015,255,195,118,0.74,'dakar'],
  [32,15, isMobile?14:35, 0.017,255,198,122,0.76,'khartoum'],
  [38,9,  isMobile?14:35, 0.017,255,198,122,0.76,'addis_ababa'],
  [-1,-4, isMobile?12:30, 0.015,255,195,118,0.73,'nairobi_offset'],
  [37,-1, isMobile?16:40, 0.018,255,198,122,0.77,'nairobi'],
  [47,2,  isMobile?10:25, 0.014,255,195,118,0.72,'mogadishu'],
  /* North America */
  [-74,41,isMobile?90:225,0.055,255,225,152,0.96,'nyc_metro'],
  [-77,39,isMobile?60:150,0.045,255,220,148,0.93,'dc_philly'],
  [-71,42,isMobile?50:125,0.040,255,218,146,0.91,'boston'],
  [-84,34,isMobile?40:100,0.035,255,215,142,0.88,'atlanta'],
  [-87,42,isMobile?65:162,0.045,255,218,146,0.92,'chicago'],
  [-83,42,isMobile?45:112,0.038,255,215,142,0.89,'detroit'],
  [-81,41,isMobile?35:88, 0.032,255,212,140,0.87,'cleveland'],
  [-80,26,isMobile?38:95, 0.033,255,215,142,0.88,'miami'],
  [-95,30,isMobile?40:100,0.035,255,212,140,0.87,'houston'],
  [-98,30,isMobile?30:75, 0.028,255,210,138,0.85,'san_antonio'],
  [-97,33,isMobile?35:88, 0.030,255,210,138,0.86,'dallas'],
  [-104,40,isMobile?28:70,0.025,255,208,135,0.84,'denver'],
  [-112,33,isMobile?30:75,0.027,255,210,138,0.85,'phoenix'],
  [-118,34,isMobile?75:188,0.050,255,218,145,0.92,'la'],
  [-122,37,isMobile?55:138,0.042,255,215,142,0.90,'sf_bay'],
  [-123,49,isMobile?28:70, 0.026,255,210,136,0.85,'vancouver'],
  [-79,44,isMobile?45:112, 0.038,255,215,140,0.89,'toronto'],
  [-73,45,isMobile?35:88,  0.030,255,212,138,0.87,'montreal'],
  [-99,19,isMobile?50:125, 0.038,255,210,136,0.88,'mexico_city'],
  /* South America */
  [-43,-23,isMobile?55:138,0.042,255,210,136,0.90,'rio'],
  [-46,-24,isMobile?60:150,0.045,255,212,138,0.91,'sao_paulo'],
  [-58,-34,isMobile?35:88, 0.032,255,208,134,0.87,'buenos_aires'],
  [-70,-33,isMobile?28:70, 0.026,255,205,130,0.84,'santiago'],
  [-77,-12,isMobile?22:55, 0.022,255,202,128,0.81,'lima'],
  [-74,5,  isMobile?18:45, 0.020,255,200,126,0.79,'bogota'],
  [-67,11, isMobile?15:38, 0.018,255,198,122,0.77,'caracas'],
  /* Australia & Pacific */
  [151,-34,isMobile?42:105,0.036,255,208,134,0.88,'sydney'],
  [145,-38,isMobile?35:88, 0.030,255,205,132,0.86,'melbourne'],
  [153,-27,isMobile?22:55, 0.022,255,202,128,0.82,'brisbane'],
  [115,-32,isMobile?18:45, 0.020,255,200,126,0.80,'perth'],
  [138,-35,isMobile?15:38, 0.018,255,198,124,0.78,'adelaide'],
  [174,-37,isMobile?18:45, 0.020,255,200,126,0.80,'auckland'],
  /* Central Asia / Russia */
  [82,55,  isMobile?20:50, 0.022,255,208,132,0.82,'novosibirsk'],
  [73,55,  isMobile?15:38, 0.018,255,205,130,0.80,'omsk'],
  [60,57,  isMobile?18:45, 0.020,255,205,130,0.80,'yekaterinburg'],
  [49,53,  isMobile?15:38, 0.018,255,202,128,0.78,'kazan'],
  [44,43,  isMobile?12:30, 0.016,255,200,126,0.76,'georgia_tb'],
  /* Indigenous / sparse regions — small lights representing communities */
  [-65,-25,isMobile?8:20,  0.012,255,190,115,0.60,'chaco'],
  [25,9,   isMobile?6:15,  0.010,255,185,110,0.55,'chad_basin'],
  [135,-22,isMobile?5:12,  0.008,255,185,108,0.52,'central_aus'],
  [-110,65,isMobile?5:12,  0.008,255,185,108,0.52,'northwest_canada'],
  [115,60, isMobile?5:12,  0.008,255,185,108,0.52,'siberia_yakutia'],
  [-75,-5, isMobile?5:12,  0.008,255,182,105,0.50,'amazon_communities'],
  [27,-5,  isMobile?5:12,  0.008,255,180,105,0.50,'congo_basin'],
  [94,28,  isMobile?6:15,  0.010,255,185,110,0.54,'myanmar_north'],
  [102,22, isMobile?5:12,  0.008,255,183,108,0.52,'yunnan'],
];

var _cityBuilt=false, _cityR=0, CITY_DOTS=[], _cityLon=0;

function buildCityDots(cx,cy,r,earthLon){
  CITY_DOTS=[]; _cityR=r; _cityLon=earthLon;
  for(var ci=0;ci<CITY_DATA.length;ci++){
    var cd=CITY_DATA[ci];
    var lon=cd[0],lat=cd[1],dn=cd[2],sp=cd[3];
    var R=cd[4],G=cd[5],B=cd[6],bright=cd[7];
    var pos=lonLatToXY(lon,lat,earthLon,cx,cy,r);
    if(!pos.visible||pos.depth<0.04) continue;
    var fade=Math.min(1,Math.pow(Math.max(0,pos.depth),0.4));
    for(var di=0;di<dn;di++){
      var ang=Math.random()*Math.PI*2;
      var dist=Math.random()*sp*r;
      var dx=pos.x+Math.cos(ang)*dist;
      var dy=pos.y+Math.sin(ang)*dist;
      var ddx=dx-cx,ddy=dy-cy;
      if(ddx*ddx+ddy*ddy>r*r*0.97) continue;
      CITY_DOTS.push({
        x:dx,y:dy,
        sz:0.35+Math.random()*1.1,
        brightness:bright*fade*(0.30+Math.random()*0.55),
        ph:Math.random()*Math.PI*2,
        sp:0.0005+Math.random()*0.0010,
        R:R,G:G,B:B
      });
    }
  }
  _cityBuilt=true;
}

function drawCityLights(now){
  if(!_cityBuilt||!CITY_DOTS.length) return;
  ctx.save(); ctx.globalCompositeOperation='screen';
  for(var i=0;i<CITY_DOTS.length;i++){
    var d=CITY_DOTS[i];
    var fl=0.80+0.20*Math.sin(now*d.sp+d.ph);
    var a=d.brightness*fl;
    ctx.globalAlpha=a*0.88;
    ctx.fillStyle='rgba('+d.R+','+d.G+','+d.B+',1)';
    ctx.beginPath(); ctx.arc(d.x,d.y,d.sz*0.48,0,Math.PI*2); ctx.fill();
    ctx.globalAlpha=a*0.22;
    var dg=ctx.createRadialGradient(d.x,d.y,0,d.x,d.y,d.sz*2.4);
    dg.addColorStop(0,'rgba('+d.R+','+d.G+','+d.B+',1)');
    dg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.fillStyle=dg; ctx.beginPath(); ctx.arc(d.x,d.y,d.sz*2.4,0,Math.PI*2); ctx.fill();
  }
  ctx.globalAlpha=1; ctx.restore();
}

/* Continent shapes for landmass visibility on night side */
var CONTINENTS=[
  {c:[22,26,15],a:0.82,p:[[[-18,14],[37,36],[51,11],[44,-11],[35,-35],[18,-35],[14,-17],[10,5],[-2,5],[-18,14]]]},
  {c:[22,22,12],a:0.80,p:[[[5,15],[25,30],[36,22],[15,13],[3,11],[5,15]]]}, /* sahara slightly */
  {c:[25,35,18],a:0.78,p:[[[-10,35],[0,43],[20,43],[30,45],[28,62],[5,62],[-10,53],[-10,35]]]},
  {c:[20,28,16],a:0.76,p:[[[4,56],[28,70],[30,62],[15,56],[4,56]]]},
  {c:[22,24,14],a:0.78,p:[[[34,29],[60,21],[58,11],[44,11],[34,19],[34,29]]]},
  {c:[18,30,14],a:0.72,p:[[[25,41],[60,21],[80,27],[95,24],[130,29],[148,43],[140,53],[100,51],[65,54],[35,59],[30,49],[25,41]]]},
  {c:[18,30,15],a:0.76,p:[[[68,35],[88,27],[80,7],[77,7],[72,13],[68,35]]]},
  {c:[18,28,14],a:0.74,p:[[[96,21],[105,21],[108,11],[103,1],[100,3],[96,15],[96,21]]]},
  {c:[18,26,13],a:0.72,p:[[[95,39],[125,39],[122,21],[108,19],[95,27],[95,39]]]},
  {c:[28,24,15],a:0.82,p:[[[-140,69],[-65,49],[-80,25],[-90,15],[-105,19],[-120,21],[-124,35],[-130,49],[-140,59],[-140,69]]]},
  {c:[40,40,35],a:0.78,p:[[[-50,81],[-25,71],[-18,67],[-45,61],[-60,67],[-50,81]]]},
  {c:[18,30,15],a:0.80,p:[[[-82,11],[-62,7],[-50,-6],[-34,-9],[-40,-23],[-70,-53],[-76,-41],[-80,-23],[-82,11]]]},
  {c:[38,22,12],a:0.85,p:[[[114,-21],[150,-21],[154,-25],[148,-38],[136,-38],[130,-32],[116,-34],[114,-26],[114,-21]]]},
  {c:[55,32,18],a:0.88,p:[[[125,-21],[140,-21],[138,-32],[126,-32],[125,-21]]]},
  {c:[18,28,14],a:0.70,p:[[[28,61],[70,71],[110,71],[140,69],[138,55],[105,49],[65,54],[35,59],[28,61]]]},
  {c:[60,70,80],a:0.88,p:[[[-180,-70],[180,-70],[180,-90],[-180,-90],[-180,-70]]]},
  {c:[12,55,90],a:0.78,p:[[[50,36],[52,42],[54,45],[52,48],[50,46],[49,41],[50,36]]]},
  {c:[15,65,105],a:0.75,p:[[[-6,35],[36,35],[36,41],[30,41],[15,37],[2,39],[-6,37],[-6,35]]]},
  {c:[18,28,14],a:0.74,p:[[[130,31],[135,33],[140,39],[141,41],[132,43],[130,33],[130,31]]]},
  {c:[12,55,90],a:0.72,p:[[[-88,41],[-76,43],[-75,45],[-83,45],[-86,43],[-88,41]]]},
  {c:[18,28,14],a:0.74,p:[[[118,7],[122,9],[124,17],[120,17],[118,13],[118,7]]]},
  {c:[172,40,14],a:0.78,p:[[[172,-33],[176,-35],[172,-43],[170,-39],[172,-33]]]},
];

function drawContinents(cx,cy,r,earthLon){
  ctx.save(); ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.clip();
  for(var ci=0;ci<CONTINENTS.length;ci++){
    var cont=CONTINENTS[ci];
    var col=cont.c;
    for(var pi=0;pi<cont.p.length;pi++){
      var poly=cont.p[pi];
      var anyVis=false;
      for(var vi=0;vi<poly.length;vi++){
        var tp=lonLatToXY(poly[vi][0],poly[vi][1],earthLon,cx,cy,r);
        if(tp.visible){anyVis=true;break;}
      }
      if(!anyVis) continue;
      ctx.beginPath();
      for(var ki=0;ki<poly.length;ki++){
        var pp=lonLatToXY(poly[ki][0],poly[ki][1],earthLon,cx,cy,r);
        if(ki===0) ctx.moveTo(pp.x,pp.y); else ctx.lineTo(pp.x,pp.y);
      }
      ctx.closePath();
      /* dark landmass — night side */
      var depth_avg=0;
      for(var di2=0;di2<poly.length;di2++){
        var dp=lonLatToXY(poly[di2][0],poly[di2][1],earthLon,cx,cy,r);
        depth_avg+=dp.depth;
      }
      depth_avg/=poly.length;
      var fa=cont.a*Math.max(0.15,Math.min(1,(depth_avg+0.3)*0.8));
      ctx.fillStyle='rgba('+col[0]+','+col[1]+','+col[2]+','+fa+')';
      ctx.fill();
    }
  }
  ctx.restore();
}

var _prevEarthLon=-999;
function drawEarth(now){
  var cx=earthCX(), cy=earthCY(), r=earthR();
  /* rotation: ~100s per full rotation */
  var earthLon=(now*0.000063)%(Math.PI*2);

  /* rebuild cities every rotation tick */
  if(!_cityBuilt||Math.abs(_cityR-r)>2||Math.abs(earthLon-_prevEarthLon)>0.15){
    buildCityDots(cx,cy,r,earthLon);
    _prevEarthLon=earthLon;
  }

  ctx.save();

  /* base — deep dark ocean (night) */
  var oc=ctx.createRadialGradient(cx-r*0.18,cy-r*0.14,r*0.02,cx+r*0.12,cy+r*0.10,r*1.05);
  oc.addColorStop(0,'#0a2035'); oc.addColorStop(0.08,'#061828');
  oc.addColorStop(0.20,'#040e1c'); oc.addColorStop(0.40,'#020810');
  oc.addColorStop(0.65,'#010509'); oc.addColorStop(0.85,'#010306');
  oc.addColorStop(1,'#000204');
  ctx.fillStyle=oc;
  ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.fill();

  /* continents — dark (night) */
  drawContinents(cx,cy,r,earthLon);

  /* city lights — primary feature */
  ctx.save(); ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.clip();
  drawCityLights(now);
  ctx.restore();

  /* day-side terminator glow (sun from top-left) */
  ctx.save(); ctx.globalCompositeOperation='screen';
  var dayGlow=ctx.createRadialGradient(cx-r*0.62,cy-r*0.52,0,cx-r*0.30,cy-r*0.25,r*1.10);
  dayGlow.addColorStop(0,'rgba(80,120,200,0.12)');
  dayGlow.addColorStop(0.30,'rgba(40,80,160,0.06)');
  dayGlow.addColorStop(0.65,'rgba(10,30,80,0.02)');
  dayGlow.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=dayGlow;
  ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.fill();
  ctx.restore();

  /* night terminator — darken right side */
  ctx.save(); ctx.globalCompositeOperation='multiply';
  var term=ctx.createLinearGradient(cx-r*0.45,cy,cx+r*0.55,cy);
  term.addColorStop(0,'rgba(0,0,0,0)');
  term.addColorStop(0.35,'rgba(0,4,14,0.10)');
  term.addColorStop(0.60,'rgba(0,3,10,0.55)');
  term.addColorStop(0.80,'rgba(0,2,8,0.88)');
  term.addColorStop(1,'rgba(0,0,0,0.96)');
  ctx.fillStyle=term;
  ctx.beginPath(); ctx.arc(cx,cy,r,0,Math.PI*2); ctx.fill();
  ctx.restore();

  /* atmosphere — blue rim (like ref รูป 2) */
  ctx.save(); ctx.globalCompositeOperation='screen';
  var atm=ctx.createRadialGradient(cx,cy,r*0.88,cx,cy,r*1.28);
  atm.addColorStop(0,'rgba(100,170,255,0.32)');
  atm.addColorStop(0.22,'rgba(70,130,245,0.18)');
  atm.addColorStop(0.50,'rgba(45,95,220,0.08)');
  atm.addColorStop(0.78,'rgba(25,65,190,0.03)');
  atm.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm; ctx.fillRect(0,0,W,H);

  /* inner glow edge */
  var atm2=ctx.createRadialGradient(cx,cy,r*0.93,cx,cy,r*1.06);
  atm2.addColorStop(0,'rgba(130,190,255,0.20)');
  atm2.addColorStop(0.50,'rgba(90,150,255,0.08)');
  atm2.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=atm2; ctx.fillRect(0,0,W,H);
  ctx.restore();

  /* limb darkening */
  ctx.save(); ctx.globalCompositeOperation='multiply';
  var ld=ctx.createRadialGradient(cx-r*0.14,cy-r*0.11,r*0.62,cx,cy,r*1.02);
  ld.addColorStop(0,'rgba(0,0,0,0)');
  ld.addColorStop(0.70,'rgba(0,5,18,0.18)');
  ld.addColorStop(1,'rgba(0,3,12,0.55)');
  ctx.fillStyle=ld;
  ctx.beginPath(); ctx.arc(cx,cy,r*1.02,0,Math.PI*2); ctx.fill();
  ctx.restore();

  ctx.restore();
}

/* ================================================================
   GOLD ORBIT RING around Earth (SURVIVAL ring) — ref รูป 2
   ================================================================ */
function drawEarthOrbitRing(now){
  var cx=earthCX(), cy=earthCY(), r=earthR();
  var ringR=r*1.55;
  var ringTilt=0.22;
  var isActive=activeRoute==='survival';

  ctx.save(); ctx.globalCompositeOperation='screen';

  /* outer glow */
  if(isActive){
    var glow=ctx.createRadialGradient(cx,cy,ringR*0.88,cx,cy,ringR*1.12);
    glow.addColorStop(0,'rgba(255,210,60,0.18)');
    glow.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle=glow; /* not used directly */
    /* draw as filled ellipse ring */
    ctx.save();
    ctx.strokeStyle='rgba(255,215,65,0.35)';
    ctx.lineWidth=ringR*0.045*ringTilt*6;
    ctx.beginPath();
    ctx.ellipse(cx,cy,ringR,ringR*ringTilt,0,0,Math.PI*2);
    ctx.stroke();
    ctx.restore();
  }

  /* main ring */
  ctx.strokeStyle=isActive?'rgba(255,215,60,0.72)':'rgba(200,200,220,0.18)';
  ctx.lineWidth=isActive?1.8:0.8;
  ctx.beginPath();
  ctx.ellipse(cx,cy,ringR,ringR*ringTilt,0,0,Math.PI*2);
  ctx.stroke();

  /* dotted inner ring */
  ctx.setLineDash([4,8]);
  ctx.strokeStyle=isActive?'rgba(255,220,80,0.45)':'rgba(180,180,200,0.10)';
  ctx.lineWidth=isActive?1.0:0.5;
  ctx.beginPath();
  ctx.ellipse(cx,cy,ringR*0.92,ringR*0.92*ringTilt,0,0,Math.PI*2);
  ctx.stroke();
  ctx.setLineDash([]);

  /* SURVIVAL label */
  var labelAngle=Math.PI*0.62;
  var lx=cx+Math.cos(labelAngle)*ringR;
  var ly=cy+Math.sin(labelAngle)*ringR*ringTilt;
  ctx.font='600 '+(isMobile?10:13)+'px "DM Mono",monospace';
  ctx.fillStyle=isActive?'rgba(255,225,100,0.92)':'rgba(180,185,210,0.45)';
  ctx.textAlign='center'; ctx.textBaseline='middle';
  if(isActive){ ctx.shadowColor='rgba(255,210,60,0.80)'; ctx.shadowBlur=8; }
  ctx.fillText('SURVIVAL',lx,ly-ringR*ringTilt*0.15);
  ctx.shadowBlur=0;

  /* satellites on ring — ref รูป 2 */
  var satAngle1=(now*0.000055)%(Math.PI*2);
  var satAngle2=satAngle1+Math.PI*1.3;
  [[satAngle1,'rgba(200,215,240,0.85)'],[satAngle2,'rgba(200,215,240,0.70)']].forEach(function(s){
    var sa=s[0], sc=s[1];
    var sx=cx+Math.cos(sa)*ringR, sy=cy+Math.sin(sa)*ringR*ringTilt;
    ctx.save();
    ctx.fillStyle=sc;
    ctx.beginPath(); ctx.arc(sx,sy,2.5,0,Math.PI*2); ctx.fill();
    /* satellite body */
    ctx.strokeStyle=sc; ctx.lineWidth=0.8;
    var slen=5;
    ctx.beginPath(); ctx.moveTo(sx-slen,sy); ctx.lineTo(sx+slen,sy); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(sx,sy-slen*0.4); ctx.lineTo(sx,sy+slen*0.4); ctx.stroke();
    ctx.restore();
  });

  ctx.restore();
}

/* ================================================================
   PLANET ORBIT RINGS — ref รูป 1 (orbit lines with route labels)
   ================================================================ */
var ORBIT_RINGS=[
  {route:'general', lbl:'GENERAL', orb:0.28, tilt:0.22, angle_off:0.20},
  {route:'risk',    lbl:'RISK',    orb:0.36, tilt:0.22, angle_off:0.85},
  {route:'collapse',lbl:'COLLAPSE',orb:0.44, tilt:0.22, angle_off:1.60},
  {route:'civil',   lbl:'CIVIL',   orb:0.52, tilt:0.22, angle_off:2.40},
  {route:'vega',    lbl:'VEGA',    orb:0.60, tilt:0.22, angle_off:3.20},
  {route:'',        lbl:'PLUTO',   orb:0.68, tilt:0.22, angle_off:4.00},
];

function drawOrbitRings(){
  var cx=earthCX(), cy=earthCY();
  ctx.save(); ctx.globalCompositeOperation='screen';
  ORBIT_RINGS.forEach(function(or){
    var R=Math.min(W,H)*or.orb;
    var isAct=or.route&&or.route===activeRoute;
    ctx.strokeStyle=isAct?'rgba(210,190,120,0.28)':'rgba(160,165,190,0.08)';
    ctx.lineWidth=isAct?0.90:0.35;
    ctx.beginPath();
    ctx.ellipse(cx,cy,R,R*or.tilt,0,0,Math.PI*2);
    ctx.stroke();
    /* route label */
    if(or.lbl){
      var la=or.angle_off;
      var lx=cx+Math.cos(la)*R, ly=cy+Math.sin(la)*R*or.tilt;
      ctx.font='500 '+(isMobile?7:9)+'px "DM Mono",monospace';
      ctx.fillStyle=isAct?'rgba(255,225,100,0.82)':'rgba(155,160,185,0.32)';
      ctx.textAlign='center'; ctx.textBaseline='middle';
      ctx.fillText(or.lbl,lx,ly);
    }
  });
  ctx.restore();
}

/* ================================================================
   SMALL PLANETS — orbit around Earth center
   ================================================================ */
function pSphere(x,y,r,stops){
  var g=ctx.createRadialGradient(x-r*0.32,y-r*0.26,r*0.01,x+r*0.12,y+r*0.12,r*1.04);
  for(var i=0;i<stops.length;i++) g.addColorStop(stops[i][0],stops[i][1]);
  ctx.fillStyle=g; ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill();
}
function pTerm(x,y,r,s){
  s=s||0.75; ctx.save(); ctx.globalCompositeOperation='multiply';
  var g=ctx.createRadialGradient(x+r*0.28,y+r*0.22,r*0.05,x+r*0.32,y+r*0.26,r*1.08);
  g.addColorStop(0,'rgba(0,0,0,0)'); g.addColorStop(0.44,'rgba(0,0,0,'+(s*0.35).toFixed(3)+')');
  g.addColorStop(0.70,'rgba(0,0,0,'+(s*0.72).toFixed(3)+')'); g.addColorStop(1,'rgba(0,0,0,'+s+')');
  ctx.fillStyle=g; ctx.beginPath(); ctx.arc(x,y,r*1.06,0,Math.PI*2); ctx.fill(); ctx.restore();
}
function pRim(x,y,r,col){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var g=ctx.createRadialGradient(x-r*0.28,y-r*0.22,r*0.82,x,y,r*1.02);
  g.addColorStop(0,col); g.addColorStop(0.40,'rgba(255,255,255,0.02)'); g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.beginPath(); ctx.arc(x,y,r*1.02,0,Math.PI*2); ctx.fill(); ctx.restore();
}

var SMALL_PLANETS=[
  {id:'mercury',lbl:'GENERAL',route:'general',orb:0.28,per:0.241,tilt:0.22,r:0.016,rm:0.022,
   draw:function(x,y,r){ ctx.save(); pSphere(x,y,r,[[0,'#e8ddd0'],[0.35,'#a89878'],[0.75,'#5a3c20'],[1,'#180c04']]); pTerm(x,y,r,0.78); pRim(x,y,r,'rgba(228,188,125,0.42)'); ctx.restore(); }},
  {id:'venus',  lbl:'RISK',   route:'risk',   orb:0.36,per:0.615,tilt:0.22,r:0.022,rm:0.028,
   draw:function(x,y,r){ ctx.save(); pSphere(x,y,r,[[0,'#fff8c8'],[0.25,'#e0b838'],[0.60,'#a05c0c'],[1,'#301200']]); pTerm(x,y,r,0.65); pRim(x,y,r,'rgba(255,232,148,0.52)'); ctx.restore(); }},
  {id:'mars',   lbl:'COLLAPSE',route:'collapse',orb:0.44,per:1.881,tilt:0.22,r:0.019,rm:0.025,
   draw:function(x,y,r){ ctx.save(); pSphere(x,y,r,[[0,'#f4b090'],[0.25,'#c85838'],[0.60,'#7a2408'],[1,'#200400']]); pTerm(x,y,r,0.76); pRim(x,y,r,'rgba(255,152,82,0.42)'); ctx.restore(); }},
  {id:'jupiter',lbl:'CIVIL',  route:'civil',  orb:0.52,per:11.86,tilt:0.22,r:0.038,rm:0.048,
   draw:function(x,y,r,now){
     ctx.save(); pSphere(x,y,r,[[0,'#f4e8c8'],[0.22,'#c89845'],[0.55,'#9a5820'],[1,'#381800']]);
     ctx.save(); ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.clip();
     ctx.globalCompositeOperation='overlay';
     for(var bi=0;bi<7;bi++){
       var by=y-r*0.86+bi*r*0.28+Math.sin(now*0.0000046+bi*0.7)*r*0.012;
       var ba=0.08+0.10*Math.abs(Math.sin(bi*0.5+(now||0)*0.0000046));
       var jg=ctx.createLinearGradient(x-r,by,x+r,by+r*0.04);
       var bc=bi%2===0?'rgba(140,68,34,'+ba+')':'rgba(185,125,55,'+ba+')';
       jg.addColorStop(0,'rgba(0,0,0,0)');jg.addColorStop(0.25,bc);jg.addColorStop(0.75,bc);jg.addColorStop(1,'rgba(0,0,0,0)');
       ctx.fillStyle=jg; ctx.fillRect(x-r,by,r*2,r*0.20);
     }
     ctx.restore();
     pTerm(x,y,r,0.60); pRim(x,y,r,'rgba(255,208,148,0.40)'); ctx.restore();
   }},
  {id:'saturn', lbl:'VEGA',   route:'vega',   orb:0.60,per:29.46,tilt:0.22,r:0.032,rm:0.040,
   draw:function(x,y,r){
     ctx.save();
     pSphere(x,y,r,[[0,'#f8f0c0'],[0.25,'#d8b840'],[0.60,'#9a7010'],[1,'#3a2600']]);
     ctx.save(); ctx.globalCompositeOperation='screen';
     var rt=0.28;
     var rings=[{ri:1.22,ro:1.48,R:198,G:183,B:145,a:0.30},{ri:1.48,ro:1.82,R:215,G:200,B:162,a:0.52},{ri:1.82,ro:1.86,R:50,G:46,B:36,a:0.14},{ri:1.86,ro:2.12,R:205,G:190,B:155,a:0.44}];
     rings.forEach(function(rng){
       var rg=ctx.createLinearGradient(x-r*rng.ro,y,x+r*rng.ro,y);
       rg.addColorStop(0,'rgba(0,0,0,0)'); rg.addColorStop(0.10,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.55).toFixed(3)+')');
       rg.addColorStop(0.50,'rgba('+rng.R+','+rng.G+','+rng.B+','+rng.a+')'); rg.addColorStop(0.90,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.55).toFixed(3)+')'); rg.addColorStop(1,'rgba(0,0,0,0)');
       ctx.beginPath(); ctx.ellipse(x,y,r*rng.ro,r*rng.ro*rt,0,Math.PI,Math.PI*2); ctx.ellipse(x,y,r*rng.ri,r*rng.ri*rt,0,Math.PI*2,Math.PI,true); ctx.fillStyle=rg; ctx.fill();
     });
     ctx.restore();
     pTerm(x,y,r,0.58); pRim(x,y,r,'rgba(255,235,152,0.48)');
     ctx.save(); ctx.globalCompositeOperation='screen';
     rings.forEach(function(rng){
       var rg2=ctx.createLinearGradient(x-r*rng.ro,y,x+r*rng.ro,y);
       rg2.addColorStop(0,'rgba(0,0,0,0)'); rg2.addColorStop(0.10,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.55).toFixed(3)+')');
       rg2.addColorStop(0.50,'rgba('+rng.R+','+rng.G+','+rng.B+','+rng.a+')'); rg2.addColorStop(0.90,'rgba('+rng.R+','+rng.G+','+rng.B+','+(rng.a*0.55).toFixed(3)+')'); rg2.addColorStop(1,'rgba(0,0,0,0)');
       ctx.beginPath(); ctx.ellipse(x,y,r*rng.ro,r*rng.ro*rt,0,0,Math.PI); ctx.ellipse(x,y,r*rng.ri,r*rng.ri*rt,0,Math.PI,0,true); ctx.fillStyle=rg2; ctx.fill();
     });
     ctx.restore(); ctx.restore();
   }},
  {id:'pluto',  lbl:'PLUTO',  route:'',       orb:0.68,per:247.9,tilt:0.22,r:0.010,rm:0.014,
   draw:function(x,y,r){ ctx.save(); pSphere(x,y,r,[[0,'#d8c8b0'],[0.40,'#8a6848'],[1,'#281408']]); pTerm(x,y,r,0.82); pRim(x,y,r,'rgba(188,162,138,0.30)'); ctx.restore(); }},
];

var _spCache=[];
function smallPlanetPos(p,now){
  var BASE=0.000034;
  var angle=(now*BASE/p.per)%(Math.PI*2);
  var cx=earthCX(), cy=earthCY();
  var R=Math.min(W,H)*p.orb;
  var x=cx+Math.cos(angle)*R;
  var y=cy+Math.sin(angle)*R*p.tilt;
  return {x:x,y:y};
}

function pActiveSmall(x,y,r,now){
  ctx.save(); ctx.globalCompositeOperation='screen';
  var pulse=0.62+0.38*Math.sin(now*0.0022);
  var g=ctx.createRadialGradient(x,y,r*0.5,x,y,r*2.8);
  g.addColorStop(0,'rgba(255,205,70,'+(0.28*pulse).toFixed(3)+')');
  g.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  ctx.globalAlpha=0.18*pulse;
  ctx.strokeStyle='rgba(255,200,60,0.70)'; ctx.lineWidth=0.8;
  ctx.beginPath();ctx.arc(x,y,r*1.12,0,Math.PI*2);ctx.stroke();
  ctx.globalAlpha=1; ctx.restore();
}

function drawSmallLabel(p,pos){
  if(!p.lbl) return;
  var r=Math.min(W,H)*(isMobile?p.rm:p.r);
  var isAct=p.route&&p.route===activeRoute;
  ctx.save();
  ctx.font='500 '+(isMobile?6:8)+'px "DM Mono",monospace';
  ctx.textAlign='center'; ctx.textBaseline='top';
  if(isAct){ ctx.shadowColor='rgba(255,215,95,0.78)'; ctx.shadowBlur=6; ctx.fillStyle='rgba(255,235,170,0.95)'; }
  else { ctx.fillStyle='rgba(165,170,195,0.32)'; }
  ctx.fillText(p.lbl,pos.x,pos.y+r+3);
  ctx.restore();
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
  if(e.changedTouches.length===1){
    var t=e.changedTouches[0];
    cv.dispatchEvent(new MouseEvent('click',{clientX:t.clientX,clientY:t.clientY}));
  }
},{passive:true});

/* ================================================================
   MOON — โคจรรอบโลก
   ================================================================ */
function drawMoon(now){
  var cx=earthCX(), cy=earthCY(), er=earthR();
  var moonAngle=(now*0.000085)%(Math.PI*2);
  var moonDist=er*1.65, moonTilt=0.18;
  var mx=cx+Math.cos(moonAngle)*moonDist;
  var my=cy+Math.sin(moonAngle)*moonDist*moonTilt;
  var mr=er*0.272;
  ctx.save();
  pSphere(mx,my,mr,[[0,'#f2eee6'],[0.18,'#dcd4c4'],[0.45,'#b0a090'],[0.72,'#6c5c4e'],[1,'#28180e']]);
  ctx.save(); ctx.beginPath(); ctx.arc(mx,my,mr,0,Math.PI*2); ctx.clip();
  [[-.14,-.10,.28],[.12,-.08,.22],[.18,.10,.20],[-.08,.16,.18],[.00,-.22,.15]].forEach(function(m){
    var g=ctx.createRadialGradient(mx+m[0]*mr,my+m[1]*mr,0,mx+m[0]*mr,my+m[1]*mr,m[2]*mr);
    g.addColorStop(0,'rgba(28,18,12,0.52)'); g.addColorStop(0.6,'rgba(28,18,12,0.22)'); g.addColorStop(1,'rgba(0,0,0,0)');
    ctx.globalCompositeOperation='multiply'; ctx.fillStyle=g; ctx.fillRect(0,0,W,H);
  });
  ctx.restore();
  pTerm(mx,my,mr,0.80); pRim(mx,my,mr,'rgba(205,188,172,0.38)');
  ctx.restore();
}

/* ================================================================
   RENDER
   ================================================================ */
function render(dt,now){
  drawBg(now);
  drawStars(now);
  drawSun(now);
  drawOrbitRings();

  _spCache=[];
  SMALL_PLANETS.forEach(function(p){
    var pos=smallPlanetPos(p,now);
    _spCache.push(pos);
    var r=Math.min(W,H)*(isMobile?p.rm:p.r);
    if(p.route&&p.route===activeRoute) pActiveSmall(pos.x,pos.y,r,now);
    p.draw(pos.x,pos.y,r,now);
    drawSmallLabel(p,pos);
  });

  drawEarthOrbitRing(now);
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
  if(!window.KD) window.KD={};
  if(!window.KD.state) window.KD.state={};
  window.KD.state[key]=val;
};

doResize();
_last=performance.now();
_raf=requestAnimationFrame(loop);

})();
