/* ============================================================
   KING DIADEM — Galaxy Scene v37 VERTICAL SOLAR SYSTEM
   Layout: Sun top-center, planets cascade down vertically
   with elliptical orbital rings — inspired by lockscreen ref
   ============================================================ */
(function(){
'use strict';

var cv=document.getElementById('galaxy');
if(!cv)return;
var ctx=cv.getContext('2d',{alpha:true});
var W=0,H=0,lastTime=0;
var activeRoute='general';
var FPS_LOW=false;

/* ── RESIZE ── */
var _rT;
function doResize(){
  W=cv.width=window.innerWidth;
  H=cv.height=window.innerHeight;
  buildStars();buildDust();
}
window.addEventListener('resize',function(){clearTimeout(_rT);_rT=setTimeout(doResize,60);},{passive:true});

/* ── STATE ── */
var STATE={
  entropy:45,stability:62,resources:78,waterline:89,
  choice_count:4,thinking:false,activeRoute:'general',
  blackHole:false
};

function updateWaterline(){
  var d=(STATE.entropy*0.33)+(100-STATE.stability)*0.33+(100-STATE.resources)*0.34;
  STATE.waterline=Math.max(0,Math.min(100,100-d));
  STATE.blackHole=STATE.waterline<20;
}

/* ── ROUTE COLORS ── */
var ROUTE_HUE={general:208,risk:10,survival:36,collapse:28,civil:168,vega:258};
var _curHue=208,_tgtHue=208;

/* ── VERTICAL LAYOUT ── */
// Sun sits near top-center, planets cascade downward
// Each planet has an elliptical ring (like lockscreen)
function SX(){ return W*0.50; }
function sunY(){ return H*0.08; }  // sun near top
function sunR(){ return Math.min(W*0.10, H*0.075, 52); }

// Vertical spacing: planets spread from sunY+sunR to H*0.94
function planetY(idx, total){
  var topGap=sunY()+sunR()*2.8;
  var available=H*0.94-topGap;
  return topGap + (idx/(total-1||1))*available;
}

/* ── PLANET DEFINITIONS ── */
// For vertical layout: orb = horizontal half-width of elliptical ring
// Each planet orbits on its own horizontal ellipse, centered on X=SX()
var PDEFS=[
  {id:'a1',  label:null,     orbW:.12, orbH:.016, spd:.00022, ang:.80, sz:2.2,  c0:'#c8c0b8',c1:'#706860',c2:'#1e1a18',glow:'rgba(200,190,175,',atm:null},
  {id:'a2',  label:null,     orbW:.18, orbH:.022, spd:.00018, ang:2.10,sz:3.5,  c0:'#f0d890',c1:'#b89030',c2:'#2a1e04',glow:'rgba(230,200,100,',atm:'rgba(220,180,80,'},
  {id:'general', label:'GENERAL',  orbW:.30, orbH:.034, spd:.00014, ang:3.60,sz:14,  c0:'#78c8f8',c1:'#1a6eca',c2:'#05152e',glow:'rgba(80,160,255,', atm:'rgba(60,140,240,'},
  {id:'risk',    label:'RISK',     orbW:.30, orbH:.034, spd:.00011, ang:5.20,sz:11,  c0:'#e87848',c1:'#a03818',c2:'#220a02',glow:'rgba(230,100,60,', atm:'rgba(200,70,30,'},
  {id:'survival',label:'SURVIVAL', orbW:.30, orbH:.034, spd:.000078,ang:1.40,sz:22,  c0:'#e8c880',c1:'#b87820',c2:'#1e0e00',glow:'rgba(200,160,60,', atm:'rgba(180,130,40,',bands:true},
  {id:'collapse',label:'COLLAPSE', orbW:.30, orbH:.034, spd:.000055,ang:4.00,sz:18,  c0:'#d8c090',c1:'#987040',c2:'#1a1004',glow:'rgba(200,170,90,', atm:'rgba(170,140,60,',rings:true},
  {id:'civil',   label:'CIVIL',    orbW:.30, orbH:.034, spd:.000035,ang:.50, sz:15,  c0:'#80e8e0',c1:'#289898',c2:'#021e1e',glow:'rgba(80,220,210,', atm:'rgba(60,200,190,'},
  {id:'vega',    label:'VEGA',     orbW:.30, orbH:.034, spd:.000022,ang:2.80,sz:14,  c0:'#6898e8',c1:'#2838b8',c2:'#020416',glow:'rgba(100,140,240,', atm:'rgba(80,110,220,',storm:true},
];
var PLANETS=PDEFS.map(function(d,i){return Object.assign({ang:d.ang||0,vIdx:i},d);});
var VLABELS=PLANETS.filter(function(p){return p.label;});

/* ── STARS ── */
var STARS=[];
function buildStars(){
  STARS=[];
  for(var i=0;i<2000;i++)STARS.push({x:Math.random()*W,y:Math.random()*H,r:.06+Math.random()*.20,a:.04+Math.random()*.20,col:Math.random()>.5?'170,205,255':'205,185,255',tw:false});
  for(var j=0;j<280;j++)STARS.push({x:Math.random()*W,y:Math.random()*H,r:.12+Math.random()*.28,a:.14+Math.random()*.24,col:Math.random()>.5?'145,205,255':'195,155,255',tw:true,tS:.00008+Math.random()*.00015,tO:Math.random()*Math.PI*2});
  for(var k=0;k<50;k++){var rr=Math.random();STARS.push({x:Math.random()*W,y:Math.random()*H,r:.35+Math.random()*.55,a:.35+Math.random()*.38,col:rr<.42?'130,195,255':rr<.80?'200,150,255':'255,205,130',tw:true,tS:.00004+Math.random()*.00009,tO:Math.random()*Math.PI*2,bloom:true});}
}

/* ── DUST ── */
var DUST=[];
function buildDust(){
  DUST=[];var n=W<600?40:100;
  for(var i=0;i<n;i++)DUST.push({x:Math.random()*W,y:Math.random()*H,vx:(Math.random()-.5)*.008,vy:(Math.random()-.5)*.004,r:.3+Math.random()*.8,a:.025+Math.random()*.065,col:Math.random()<.6?'130,190,255':'180,140,255',tS:.0001+Math.random()*.0002,tO:Math.random()*Math.PI*2});
}

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
  SWS.push({x:x,y:y,r:0,maxR:Math.min(W,H)*(big?.55:.28),alpha:big?.80:.50,col:col||'120,200,255'});
  if(SWS.length>6)SWS.shift();
}

/* ── ION TRAILS ── */
var ION={};
VLABELS.forEach(function(p){ION[p.id]=[];});
function updateTrail(id,x,y){if(!ION[id])return;ION[id].push({x:x,y:y});if(ION[id].length>40)ION[id].shift();}

/* ── GET PLANET SCREEN POSITION ── */
function getPlanetPos(p){
  // Vertical position: based on index among labeled planets
  var lIdx=VLABELS.indexOf(p);
  if(lIdx<0){
    // unnamed planets: small orbit around sun
    var R2=p.orbW*Math.min(W,H*0.3);
    return{x:SX()+Math.cos(p.ang)*R2, y:sunY()+Math.sin(p.ang)*R2*0.4};
  }
  var cy=planetY(lIdx, VLABELS.length);
  var rx=p.orbW*W*0.5; // half-width of ellipse
  var ry=p.orbH*H*0.5; // half-height (thin ellipse = depth illusion)
  return{x:SX()+Math.cos(p.ang)*rx, y:cy+Math.sin(p.ang)*ry};
}

/* ── CLICK ── */
cv.addEventListener('click',function(e){
  var rect=cv.getBoundingClientRect();
  var mx=e.clientX-rect.left,my=e.clientY-rect.top;
  for(var i=0;i<VLABELS.length;i++){
    var p=VLABELS[i];
    var pos=getPlanetPos(p);
    var sz=getPlanetSz(p);
    var dist=Math.sqrt((mx-pos.x)*(mx-pos.x)+(my-pos.y)*(my-pos.y));
    if(dist<sz*3.5){
      var col=p.glow.replace('rgba(','').split(',').slice(0,3).join(',');
      shockwave(pos.x,pos.y,col,false);spawnEx(pos.x,pos.y,col,55);
      if(p.id!==activeRoute){if(window.setRoute)window.setRoute(p.id);}
      return;
    }
  }
  spawnEx(mx,my,'120,190,255',12);
},{passive:true});

/* ── GET PLANET SIZE (scales with screen) ── */
function getPlanetSz(p){
  var base=p.sz;
  var scale=Math.max(0.55, Math.min(W/375, 1.5));
  return base*scale;
}

/* ── DRAW BG ── */
function drawBg(t){
  ctx.clearRect(0,0,W,H);
  if(STATE.blackHole){
    var bg=ctx.createRadialGradient(SX(),sunY(),0,W*.5,H*.5,Math.max(W,H)*.82);
    bg.addColorStop(0,'#0a0000');bg.addColorStop(.4,'#040000');bg.addColorStop(1,'#020409');
    ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);return;
  }
  // Deep space gradient — darker at bottom, slightly lighter near sun
  var bg=ctx.createLinearGradient(0,0,0,H);
  bg.addColorStop(0,'#03050e');bg.addColorStop(.15,'#020409');bg.addColorStop(.5,'#010307');bg.addColorStop(1,'#010205');
  ctx.fillStyle=bg;ctx.fillRect(0,0,W,H);

  // Subtle nebula glow
  _curHue+=(_tgtHue-_curHue)*.006;
  ctx.save();ctx.globalCompositeOperation='screen';
  var nb=ctx.createRadialGradient(W*.35,H*.35,0,W*.5,H*.5,W*.65);
  nb.addColorStop(0,'hsla('+_curHue+',55%,25%,0.040)');nb.addColorStop(.5,'hsla('+_curHue+',45%,18%,0.018)');nb.addColorStop(1,'rgba(0,0,0,0)');
  ctx.fillStyle=nb;ctx.fillRect(0,0,W,H);
  ctx.restore();
}

function drawStars(t){
  ctx.save();ctx.globalCompositeOperation='screen';
  for(var i=0;i<STARS.length;i++){
    var s=STARS[i];
    var al=s.a;
    if(s.tw)al*=(.5+.5*Math.sin(t*s.tS+s.tO));
    al=Math.max(.01,Math.min(1,al));
    ctx.beginPath();ctx.arc(s.x,s.y,s.r,0,Math.PI*2);
    ctx.fillStyle='rgba('+s.col+','+al.toFixed(3)+')';ctx.fill();
    if(!FPS_LOW&&s.bloom&&al>.40){
      var sp=s.r*3.2;
      ctx.strokeStyle='rgba('+s.col+','+(al*.055).toFixed(3)+')';ctx.lineWidth=.16;
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

/* ── DRAW ORBITAL RING (elliptical, like lockscreen) ── */
function drawOrbitalRing(p, cy, isA, t){
  var rx=p.orbW*W*0.5;
  var ry=p.orbH*H*0.5;
  ctx.save();
  ctx.translate(SX(), cy);

  // Ring glow for active
  if(isA){
    ctx.save();ctx.globalCompositeOperation='screen';
    ctx.beginPath();ctx.ellipse(0,0,rx,ry,0,0,Math.PI*2);
    ctx.strokeStyle='rgba(140,200,255,0.15)';ctx.lineWidth=2.5;ctx.stroke();
    ctx.restore();
  }

  // Main ring — dashed, subtle
  ctx.setLineDash([3,12]);
  ctx.beginPath();ctx.ellipse(0,0,rx,ry,0,0,Math.PI*2);
  if(STATE.blackHole){
    ctx.strokeStyle=isA?'rgba(180,20,20,0.25)':'rgba(80,10,10,0.06)';
  } else {
    ctx.strokeStyle=isA?'rgba(160,220,255,0.30)':'rgba(80,130,220,0.075)';
  }
  ctx.lineWidth=isA?.75:.30;ctx.stroke();
  ctx.setLineDash([]);

  // Bright arc on top-front of ring (creates 3D depth illusion)
  if(!STATE.blackHole){
    var arcAlpha=isA?0.55:0.12;
    ctx.beginPath();ctx.ellipse(0,0,rx,ry,0,Math.PI*1.05,Math.PI*1.95);
    ctx.strokeStyle='rgba(200,230,255,'+arcAlpha+')';
    ctx.lineWidth=isA?1.0:.42;ctx.stroke();
  }
  ctx.restore();
}

/* ── DRAW PLANET ── */
function drawPlanet(x,y,p,isA,t){
  var sz=getPlanetSz(p);
  ctx.save();ctx.globalCompositeOperation='screen';

  // Atmosphere
  if(p.atm){
    var atmA=isA?.24:.09,atmR=sz*2.6+(isA?sz*.6:0);
    var atm=ctx.createRadialGradient(x,y,sz*.5,x,y,atmR);
    atm.addColorStop(0,p.atm+atmA+')');atm.addColorStop(.6,p.atm+(atmA*.28)+')');atm.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.arc(x,y,atmR,0,Math.PI*2);ctx.fillStyle=atm;ctx.fill();
  }

  // Glow
  if(p.glow){
    var pulse=isA?(1+Math.sin(t*.0011)*.16):1;
    var gR2=sz*(isA?5.5:3.2)*pulse;
    var gr2=ctx.createRadialGradient(x,y,sz,x,y,gR2);
    gr2.addColorStop(0,p.glow+(isA?'0.20':'0.06')+')');gr2.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.arc(x,y,gR2,0,Math.PI*2);ctx.fillStyle=gr2;ctx.fill();
    var gR=sz*(isA?3.4:2.2)*pulse;
    var gr=ctx.createRadialGradient(x,y,sz*.7,x,y,gR);
    gr.addColorStop(0,p.glow+(isA?'0.52':'0.20')+')');gr.addColorStop(.4,p.glow+(isA?'0.14':'0.06')+')');gr.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.arc(x,y,gR,0,Math.PI*2);ctx.fillStyle=gr;ctx.fill();
  }
  ctx.restore();

  // Saturn rings (behind planet)
  if(p.rings){
    var rx=sz*3.2,ry=sz*.32;
    ctx.save();ctx.translate(x,y);ctx.rotate(-.20);ctx.globalCompositeOperation='screen';
    for(var ri=0;ri<3;ri++){
      var rf=.80+ri*.11;
      var rg=ctx.createLinearGradient(-rx*rf,0,rx*rf,0);
      rg.addColorStop(0,'rgba(0,0,0,0)');rg.addColorStop(.25,p.glow+(isA?'0.26':'0.13')+')');rg.addColorStop(.5,p.glow+(isA?'0.40':'0.18')+')');rg.addColorStop(.75,p.glow+(isA?'0.26':'0.13')+')');rg.addColorStop(1,'rgba(0,0,0,0)');
      ctx.beginPath();ctx.ellipse(0,0,rx*rf,ry*rf,0,Math.PI,Math.PI*2);ctx.strokeStyle=rg;ctx.lineWidth=isA?1.8:.9;ctx.stroke();
    }
    ctx.restore();
  }

  // Planet body
  ctx.save();
  var body=ctx.createRadialGradient(x-sz*.30,y-sz*.28,0,x+sz*.08,y+sz*.08,sz*1.08);
  body.addColorStop(0,p.c0);body.addColorStop(.45,p.c1);body.addColorStop(1,p.c2);
  ctx.beginPath();ctx.arc(x,y,sz,0,Math.PI*2);ctx.fillStyle=body;ctx.fill();

  // Bands (Jupiter-like)
  if(p.bands){
    ctx.globalCompositeOperation='overlay';
    for(var bi=0;bi<4;bi++){
      var by=y-sz*.65+bi*(sz*.36),bh=sz*.14;
      var bg2=ctx.createLinearGradient(x-sz,by,x+sz,by);
      bg2.addColorStop(0,'rgba(0,0,0,0)');bg2.addColorStop(.3,'rgba(100,60,20,0.26)');bg2.addColorStop(.7,'rgba(100,60,20,0.26)');bg2.addColorStop(1,'rgba(0,0,0,0)');
      ctx.save();ctx.beginPath();ctx.ellipse(x,by+bh*.5,sz*.92,bh,0,0,Math.PI*2);ctx.fillStyle=bg2;ctx.fill();ctx.restore();
    }
  }

  // Storm spot (VEGA)
  if(p.storm){
    ctx.globalCompositeOperation='screen';
    var stx=x+sz*.28,sty=y-sz*.20;
    var stg=ctx.createRadialGradient(stx,sty,0,stx,sty,sz*.30);
    stg.addColorStop(0,'rgba(180,200,255,0.32)');stg.addColorStop(1,'rgba(0,0,0,0)');
    ctx.beginPath();ctx.arc(stx,sty,sz*.30,0,Math.PI*2);ctx.fillStyle=stg;ctx.fill();
  }

  // Specular highlight
  ctx.globalCompositeOperation='screen';
  var vein=ctx.createRadialGradient(x-sz*.22,y-sz*.22,0,x-sz*.06,y-sz*.06,sz*.60);
  vein.addColorStop(0,p.glow?p.glow+'0.30)':'rgba(255,255,255,0.16)');vein.addColorStop(1,'rgba(0,0,0,0)');
  ctx.beginPath();ctx.arc(x,y,sz,0,Math.PI*2);ctx.fillStyle=vein;ctx.fill();

  // Limb darkening
  ctx.globalCompositeOperation='source-over';
  var limb=ctx.createRadialGradient(x,y,sz*.14,x,y,sz*1.05);
  limb.addColorStop(0,'rgba(0,0,0,0)');limb.addColorStop(.5,'rgba(0,0,0,0.14)');limb.addColorStop(1,'rgba(0,0,0,0.80)');
  ctx.beginPath();ctx.arc(x,y,sz,0,Math.PI*2);ctx.fillStyle=limb;ctx.fill();
  ctx.restore();

  // Saturn rings (front)
  if(p.rings){
    var rx2=sz*3.2,ry2=sz*.32;
    ctx.save();ctx.translate(x,y);ctx.rotate(-.20);ctx.globalCompositeOperation='screen';
    for(var ri2=0;ri2<3;ri2++){
      var rf2=.80+ri2*.11;
      var rg2=ctx.createLinearGradient(-rx2*rf2,0,rx2*rf2,0);
      rg2.addColorStop(0,'rgba(0,0,0,0)');rg2.addColorStop(.25,p.glow+(isA?'0.26':'0.13')+')');rg2.addColorStop(.5,p.glow+(isA?'0.40':'0.18')+')');rg2.addColorStop(.75,p.glow+(isA?'0.26':'0.13')+')');rg2.addColorStop(1,'rgba(0,0,0,0)');
      ctx.beginPath();ctx.ellipse(0,0,rx2*rf2,ry2*rf2,0,0,Math.PI);ctx.strokeStyle=rg2;ctx.lineWidth=isA?1.8:.9;ctx.stroke();
    }
    ctx.restore();
  }

  // Label
  if(p.label){
    ctx.save();
    var fs=Math.max(8,Math.round(sz*.75));
    if(isA){
      ctx.globalCompositeOperation='screen';
      ctx.shadowColor=p.glow?p.glow+'0.90)':'rgba(120,200,255,0.90)';
      ctx.shadowBlur=12;ctx.fillStyle=p.c0;
    } else {
      ctx.fillStyle='rgba(120,185,160,0.30)';
    }
    ctx.font='500 '+fs+'px "DM Mono",monospace';ctx.textAlign='center';ctx.textBaseline='top';
    ctx.fillText(p.label,x,y+sz+5);ctx.restore();
  }
  updateTrail(p.id,x,y);
}

/* ── DRAW ION TRAILS ── */
function drawIonTrails(){
  ctx.save();ctx.globalCompositeOperation='screen';
  VLABELS.forEach(function(p){
    var trail=ION[p.id];if(!trail||trail.length<3)return;
    for(var i=1;i<trail.length;i++){
      var prog=i/trail.length,al=prog*.12;
      ctx.beginPath();ctx.moveTo(trail[i-1].x,trail[i-1].y);ctx.lineTo(trail[i].x,trail[i].y);
      ctx.strokeStyle=p.glow?p.glow+al+')':'rgba(150,200,255,'+al+')';
      ctx.lineWidth=prog*1.6;ctx.stroke();
    }
  });
  ctx.restore();
}

/* ── DRAW SUN ── */
function drawSun(t){
  if(STATE.blackHole){drawBlackHole(t);return;}
  var sx=SX(),sy=sunY(),R=sunR();
  var gm=STATE.waterline<40?.58:STATE.waterline<70?.95:1.28;
  if(STATE.thinking)gm*=(1+Math.sin(t*.005)*.30);

  ctx.save();ctx.globalCompositeOperation='lighter';
  // Outer corona rings
  for(var ring=7;ring>=1;ring--){
    var rAl=(.014/ring)*gm,rR=R*(2.8+ring*3.2);
    ctx.beginPath();ctx.arc(sx,sy,rR,0,Math.PI*2);
    ctx.strokeStyle='rgba(255,200,80,'+rAl+')';ctx.lineWidth=.28;ctx.stroke();
  }
  // Thinking pulse rings
  if(STATE.thinking){
    for(var b=0;b<3;b++){
      var bPhase=(t*.003+b*1.0)%(Math.PI*2);
      var bR=R*(2+b*4+Math.sin(bPhase)*2),bAl=Math.max(0,Math.sin(bPhase)*.28);
      ctx.beginPath();ctx.arc(sx,sy,bR,0,Math.PI*2);
      ctx.strokeStyle='rgba(255,220,80,'+bAl+')';ctx.lineWidth=.65;ctx.stroke();
    }
  }
  // Far glow
  var fc=ctx.createRadialGradient(sx,sy,R*.12,sx,sy,R*14);
  fc.addColorStop(0,'rgba(255,200,60,'+(0.32*gm)+')');fc.addColorStop(.12,'rgba(255,140,20,'+(0.10*gm)+')');fc.addColorStop(.38,'rgba(90,170,255,'+(0.045*gm)+')');fc.addColorStop(.65,'rgba(40,70,150,'+(0.016*gm)+')');fc.addColorStop(1,'rgba(0,0,0,0)');
  ctx.beginPath();ctx.arc(sx,sy,R*14,0,Math.PI*2);ctx.fillStyle=fc;ctx.fill();

  // Rays
  ctx.save();ctx.translate(sx,sy);ctx.rotate(t*.000014);
  for(var i=0;i<18;i++){
    var a=(i/18)*Math.PI*2,rl=R*(1.75+.26*Math.sin(i*1.7+t*.00011))*gm;
    var gr=ctx.createLinearGradient(Math.cos(a)*R*.18,Math.sin(a)*R*.18,Math.cos(a)*rl,Math.sin(a)*rl);
    gr.addColorStop(0,'rgba(255,200,50,'+(0.30*gm)+')');gr.addColorStop(.5,'rgba(200,120,10,0.04)');gr.addColorStop(1,'rgba(0,0,0,0)');
    ctx.strokeStyle=gr;ctx.lineWidth=.55;
    ctx.beginPath();ctx.moveTo(Math.cos(a)*R*.18,Math.sin(a)*R*.18);ctx.lineTo(Math.cos(a)*rl,Math.sin(a)*rl);ctx.stroke();
  }
  ctx.restore();
  ctx.globalCompositeOperation='source-over';

  // Inner halo
  var ih=ctx.createRadialGradient(sx,sy,R*.20,sx,sy,R*2.8);
  ih.addColorStop(0,'rgba(255,240,150,0.96)');ih.addColorStop(.25,'rgba(255,190,50,0.60)');ih.addColorStop(.60,'rgba(200,90,10,0.18)');ih.addColorStop(1,'rgba(0,0,0,0)');
  ctx.beginPath();ctx.arc(sx,sy,R*2.8,0,Math.PI*2);ctx.fillStyle=ih;ctx.fill();

  // Sun body
  var sbody=ctx.createRadialGradient(sx-R*.22,sy-R*.22,0,sx,sy,R);
  sbody.addColorStop(0,'#fffad0');sbody.addColorStop(.25,'#ffdd40');sbody.addColorStop(.65,'#e06800');sbody.addColorStop(1,'#5c1e00');
  ctx.beginPath();ctx.arc(sx,sy,R,0,Math.PI*2);ctx.fillStyle=sbody;ctx.fill();

  // Specular
  var spec=ctx.createRadialGradient(sx-R*.34,sy-R*.34,0,sx-R*.16,sy-R*.16,R*.50);
  spec.addColorStop(0,'rgba(255,252,230,0.50)');spec.addColorStop(1,'rgba(255,252,230,0)');
  ctx.beginPath();ctx.arc(sx,sy,R,0,Math.PI*2);ctx.fillStyle=spec;ctx.fill();

  // Limb
  var slim=ctx.createRadialGradient(sx,sy,R*.14,sx,sy,R*1.05);
  slim.addColorStop(0,'rgba(0,0,0,0)');slim.addColorStop(.5,'rgba(0,0,0,0.12)');slim.addColorStop(1,'rgba(0,0,0,0.70)');
  ctx.beginPath();ctx.arc(sx,sy,R,0,Math.PI*2);ctx.fillStyle=slim;ctx.fill();

  // LYLA label
  ctx.save();ctx.globalCompositeOperation='screen';
  ctx.shadowColor='rgba(255,200,60,0.90)';ctx.shadowBlur=12;ctx.fillStyle='rgba(255,240,140,0.96)';
  var lfs=Math.max(8,Math.round(R*.62));
  ctx.font='600 '+lfs+'px "DM Mono",monospace';ctx.textAlign='center';ctx.textBaseline='bottom';
  ctx.fillText('LYLA',sx,sy-R-5);ctx.restore();
  ctx.restore();
}

function drawBlackHole(t){
  var sx=SX(),sy=sunY(),R=sunR();
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
  ctx.restore();
}

/* ── PARTICLES & SHOCKWAVES ── */
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
    var sw=SWS[i];sw.r+=dt*260;sw.alpha*=.96;
    if(sw.r>=sw.maxR||sw.alpha<.005){SWS.splice(i,1);continue;}
    var prog=sw.r/sw.maxR;
    ctx.beginPath();ctx.arc(sw.x,sw.y,sw.r,0,Math.PI*2);
    ctx.strokeStyle='rgba('+sw.col+','+sw.alpha.toFixed(3)+')';ctx.lineWidth=(1-prog)*3+.5;ctx.stroke();
  }
  ctx.restore();
}

/* ── HUD ── */
function drawHUD(){
  ctx.save();ctx.font='300 7px "DM Mono",monospace';ctx.textBaseline='bottom';
  ctx.fillStyle='rgba(150,205,255,0.10)';ctx.textAlign='left';
  ctx.fillText('Choice(t)='+STATE.choice_count+'  WL='+Math.round(STATE.waterline)+(STATE.blackHole?' ⚠':''),12,H-14);
  ctx.fillStyle='rgba(150,205,255,0.07)';ctx.textAlign='right';
  ctx.fillText('FATE™ v37 | '+activeRoute.toUpperCase(),W-12,H-14);
  ctx.restore();
}

/* ── FPS ── */
var _fF=0,_fL=0;
function monFPS(ts){_fF++;if(ts-_fL>2000){var fps=_fF/((ts-_fL)/1000);FPS_LOW=fps<26;_fF=0;_fL=ts;}}

/* ── MAIN LOOP ── */
function loop(ts){
  if(!lastTime)lastTime=ts;
  var dt=Math.min((ts-lastTime)/1000,.05);
  lastTime=ts;monFPS(ts);updateWaterline();

  try{
    drawBg(ts);
    drawStars(ts);
    drawDust(ts);

    // Draw orbital rings for labeled planets (behind planets)
    VLABELS.forEach(function(p,i){
      var cy=planetY(i, VLABELS.length);
      drawOrbitalRing(p, cy, p.id===activeRoute, ts);
    });

    // Draw ion trails
    drawIonTrails();

    // Advance & draw planets (sorted by y for depth)
    var items=[];
    PLANETS.forEach(function(p){
      p.ang+=p.spd*dt*60;
      var pos=getPlanetPos(p);
      items.push({p:p,x:pos.x,y:pos.y});
    });
    items.sort(function(a,b){return a.y-b.y;});
    items.forEach(function(item){
      drawPlanet(item.x,item.y,item.p,item.p.id===activeRoute,ts);
    });

    // Sun on top
    drawSun(ts);
    drawParticles(dt);
    drawShockwaves(dt);
    drawHUD();
  }catch(e){console.error('[v37]',e);}
  requestAnimationFrame(loop);
}
/* ── INIT ── */
// doResize MUST run before first rAF frame — W,H=0 ทำให้ canvas ดำ
doResize();
// double-resize: mobile บางตัว innerWidth ยังไม่ settle ตอน script load
requestAnimationFrame(function(){ doResize(); requestAnimationFrame(loop); });

/* ── ROUTE ── */
window.setRoute=function(r){
  if(!ROUTE_HUE[r])return;
  activeRoute=r;STATE.activeRoute=r;_tgtHue=ROUTE_HUE[r]||208;
  document.querySelectorAll('.rpill,.ctx-tag,.route-chip').forEach(function(el){el.classList.toggle('active',el.dataset.r===r);});
  var ap=VLABELS.find(function(p){return p.id===r;});
  if(ap){
    var pos=getPlanetPos(ap);
    var col=ap.glow.replace('rgba(','').split(',').slice(0,3).join(',');
    shockwave(pos.x,pos.y,col,false);spawnEx(pos.x,pos.y,col,55);
  }
};

/* ── PUBLIC API ── */
window.KD_pulse=function(route){
  if(route&&ROUTE_HUE[route]){
    activeRoute=route;STATE.activeRoute=route;_tgtHue=ROUTE_HUE[route]||208;
  }
  var sx=SX(),sy=sunY();
  spawnEx(sx,sy,'120,180,255',22);
  shockwave(sx,sy,'80,160,255',false);
};

window.LYLA_thinking=function(){
  STATE.thinking=true;
  clearTimeout(window._lylaThinkT);
  window._lylaThinkT=setTimeout(function(){STATE.thinking=false;},5000);
  var sx=SX(),sy=sunY();
  spawnEx(sx,sy,'200,168,75',12);
};

window.LYLA_answered=function(){
  STATE.thinking=false;
  var sx=SX(),sy=sunY();
  spawnEx(sx,sy,'80,220,160',28);
  shockwave(sx,sy,'80,220,160',false);
};

window.KD_setState=function(s,v){
  if(s==null)return;
  if(typeof s==='string'){var tmp={};tmp[s]=v;s=tmp;}
  if(s.entropy!=null)STATE.entropy=+s.entropy;
  if(s.stability!=null)STATE.stability=+s.stability;
  if(s.resources!=null)STATE.resources=+s.resources;
  if(s.waterline!=null)STATE.waterline=+s.waterline;
  if(s.choice_count!=null)STATE.choice_count=+s.choice_count;
};

window.KD_setRoute=function(r){
  if(typeof window.setRoute==='function')window.setRoute(r);
};

})();
