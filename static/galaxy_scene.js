/* ================================================================
   KING DIADEM — Galaxy Scene v54 · LIGHT WITH DEPTH
   โครงเดิมของ v53: แก่นกลาง KING DIADEM + 6 วงโคจรของเส้นทาง
   แต่แสงทุกดวงมีมิติ — มองผ่านชั้นเมฆเหมือนดูดวงจันทร์คืนเมฆบาง:
     · ดวงไฟเล็กแต่จ้า ถูกเมฆที่ลอยผ่านบังจริง (แสงหรี่/สว่างตามความหนาเมฆ)
     · แสงกระเจิงในเมฆ: ขอบเมฆบางเรืองแสง เนื้อเมฆหนาเป็นเงา (backlit)
     · วงแสงสีรุ้ง (corona) เกิดเฉพาะบนเมฆบาง เหมือนการเลี้ยวเบนจริง
     · เมฆ 2 ชั้นลอยคนละความเร็ว (parallax = ความลึก)
     · ดาวเคราะห์ของแต่ละเส้นทางเป็นทรงกลม รับแสงจากแก่นกลาง (มีด้านมืด/ขอบบรรยากาศ)
     · ดาวพื้นหลังเห็นเฉพาะช่องว่างระหว่างเมฆ
   วาดด้วยโค้ดทั้งหมด (WebGL shader) ไม่มีภาพ · ถ้าไม่มี WebGL ใช้ 2D แบบเบา
   API เดิม: KD_setRoute · KD_pulse · KD_setState · events KD:response / KD:decision /
            KD:thinking / KD:resize / KD:visibility · เพิ่ม KD_galaxy.{route,think,focus}
   ================================================================ */
(function(){
'use strict';

var cv = document.getElementById('galaxy');
if (!cv) return;

var REDUCED = window.matchMedia && matchMedia('(prefers-reduced-motion: reduce)').matches;
var ROUTE_COLOR = {
  general:  {h:42,  s:65, l:62},  /* gold */
  risk:     {h:18,  s:75, l:58},  /* amber-red */
  survival: {h:205, s:70, l:58},  /* blue */
  collapse: {h:0,   s:65, l:55},  /* red */
  civil:    {h:265, s:55, l:62},  /* purple */
  vega:     {h:235, s:60, l:62}   /* deep blue */
};
var ORBIT_ROUTES = [
  {route:'general', lbl:'GENERAL', orb:0.30, per:8,  ao:0.0},
  {route:'risk',    lbl:'RISK',    orb:0.38, per:11, ao:1.3},
  {route:'survival',lbl:'SURVIVAL',orb:0.46, per:14, ao:2.6},
  {route:'collapse',lbl:'COLLAPSE',orb:0.54, per:17, ao:3.9},
  {route:'civil',   lbl:'CIVIL',   orb:0.62, per:20, ao:5.2},
  {route:'vega',    lbl:'VEGA',    orb:0.70, per:24, ao:0.7}
];

var activeRoute = 'general';
var W = 0, H = 0, DPR = 1, Q = 1;            // CSS px, overlay DPR, GL resolution scale
var tint = [1, 0.93, 0.8], tintT = tint.slice();
var flash = 0, think = 0, thinkT = 0, gainPulse = 0;
var drift1 = [0.13, 0.41], drift2 = [0.57, 0.08];
var t0 = performance.now(), lastT = t0, raf = 0, running = false;
var hits = [];

/* ── สี ───────────────────────────────────────────────────────── */
function hsl2rgb(h, s, l){
  h = ((h % 360) + 360) % 360 / 360; s /= 100; l /= 100;
  function f(n){ var k = (n + h * 12) % 12, a = s * Math.min(l, 1 - l); return l - a * Math.max(-1, Math.min(k - 3, 9 - k, 1)); }
  return [f(0), f(8), f(4)];
}
function routeTint(r){
  var c = ROUTE_COLOR[r] || ROUTE_COLOR.general, rgb = hsl2rgb(c.h, c.s, Math.max(c.l, 60));
  /* แสงหลักยังเป็นขาวอุ่นเหมือนแสงจันทร์ แค่ถูกย้อมด้วยสีเส้นทาง */
  return [0.55 + 0.45 * rgb[0], 0.55 + 0.45 * rgb[1], 0.55 + 0.45 * rgb[2]];
}
function routeRGB(r){ var c = ROUTE_COLOR[r] || ROUTE_COLOR.general; return hsl2rgb(c.h, c.s, c.l); }

/* ── noise texture (tileable fBm 256², 3 channels) ───────────────
   ใช้ทั้งใน shader (texture) และใน JS (หาความหนาเมฆตรงดวงไฟ/เส้นวงโคจร) */
var NS = 256, NOISE = [new Float32Array(NS * NS), new Float32Array(NS * NS), new Float32Array(NS * NS)];
(function buildNoise(){
  var seed = 1337;
  function rnd(){ seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 4294967296; }
  function sm(t){ return t * t * (3 - 2 * t); }
  for(var ch = 0; ch < 3; ch++){
    var out = NOISE[ch], amp = 1, norm = 0;
    for(var o = 0; o < 6; o++){
      var P = 4 << o; if(P > NS) break;
      var g = new Float32Array(P * P); for(var i = 0; i < g.length; i++) g[i] = rnd();
      var cell = NS / P;
      for(var y = 0; y < NS; y++){
        var gy = y / cell, iy = Math.floor(gy), fy = sm(gy - iy), y0 = iy % P, y1 = (iy + 1) % P;
        for(var x = 0; x < NS; x++){
          var gx = x / cell, ix = Math.floor(gx), fx = sm(gx - ix), x0 = ix % P, x1 = (ix + 1) % P;
          var a = g[y0 * P + x0], b = g[y0 * P + x1], c = g[y1 * P + x0], d = g[y1 * P + x1];
          out[y * NS + x] += amp * ((a + (b - a) * fx) + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fy);
        }
      }
      norm += amp; amp *= 0.52;
    }
    var lo = 1e9, hi = -1e9;
    for(var k = 0; k < out.length; k++){ out[k] /= norm; if(out[k] < lo) lo = out[k]; if(out[k] > hi) hi = out[k]; }
    for(k = 0; k < out.length; k++) out[k] = (out[k] - lo) / (hi - lo);
  }
})();
function tex(ch, u, v){
  u = (u - Math.floor(u)) * NS - 0.5; v = (v - Math.floor(v)) * NS - 0.5;
  var x0 = Math.floor(u), y0 = Math.floor(v), fx = u - x0, fy = v - y0, A = NOISE[ch];
  var X0 = (x0 + NS) % NS, X1 = (x0 + 1 + NS) % NS, Y0 = (y0 + NS) % NS, Y1 = (y0 + 1 + NS) % NS;
  var a = A[Y0 * NS + X0], b = A[Y0 * NS + X1], c = A[Y1 * NS + X0], d = A[Y1 * NS + X1];
  return a + (b - a) * fx + ((c + (d - c) * fx) - (a + (b - a) * fx)) * fy;
}
function smoothstep(a, b, x){ var t = Math.max(0, Math.min(1, (x - a) / (b - a))); return t * t * (3 - 2 * t); }

/* ความหนาเมฆ (optical depth) ที่จุดหน้าจอ — ต้องตรงกับ dens() ใน shader */
var COVER = 0.50, cloudScale = 800;
function densAt(px, py){
  var qx = px / cloudScale, qy = py / cloudScale;
  var ax = qx + drift1[0], ay = qy + drift1[1];
  ax += (tex(1, ax * 0.37, ay * 0.37) - 0.5) * 0.2; ay += (tex(2, ax * 0.37 + 0.5, ay * 0.37) - 0.5) * 0.2;
  var n = 0.50 * tex(0, ax, ay) + 0.28 * tex(0, ax * 2.13 + 0.31, ay * 2.13 + 0.17) + 0.22 * tex(1, ax * 4.37 + 0.71, ay * 4.37 + 0.29);
  var hf = tex(2, ax * 7.9 + 0.13, ay * 7.9 + 0.61);
  var dA = smoothstep(COVER, COVER + 0.2, n) * (0.6 + 2.2 * Math.min(0.4, Math.max(0, n - COVER))) * (0.55 + 0.9 * hf);
  var bx = qx * 0.55 + drift2[0], by = qy * 0.55 + drift2[1];
  var n2 = 0.6 * tex(1, bx, by) + 0.4 * tex(2, bx * 2.31 + 0.5, by * 2.31 + 0.13);
  var dB = smoothstep(COVER + 0.08, COVER + 0.34, n2);
  return dA * 1.6 + dB * 0.7;
}

/* ── เรขาคณิต (CSS px) ─────────────────────────────────────────── */
var geo = { cx: 0, cy: 0, s: 0, rd: 0, tilt: 0.22 };
function computeGeo(){
  var f = typeof window.KD_GALAXY_FOCUS === 'function' ? window.KD_GALAXY_FOCUS() : null;
  var cx = W * 0.5, cy = H * 0.46, s = Math.min(W, H), portrait = W < H * 0.8;
  if(f){ cx = f.x; cy = f.y; s = f.s || s; }
  geo.cx = cx; geo.cy = cy; geo.s = s;
  geo.tilt = portrait ? 0.34 : 0.22;
  geo.rd = Math.max(7, Math.min(20, s * (portrait ? 0.03 : 0.02)));
}
function planets(now){
  var t = REDUCED ? 0 : (now - t0) / 1000, out = [];
  ORBIT_ROUTES.forEach(function(rt){
    var R = geo.s * rt.orb, ang = (t * 0.2 / rt.per + rt.ao) % (Math.PI * 2);
    var sa = Math.sin(ang), act = rt.route === activeRoute;
    var base = act ? 10 : 6.2, r = base * Math.max(0.75, Math.min(1.25, geo.s / 700)) * (1 + 0.14 * sa);
    out.push({ rt: rt, x: geo.cx + Math.cos(ang) * R, y: geo.cy + sa * R * geo.tilt, z: sa * R, r: Math.max(4, r), act: act, R: R, sa: sa });
  });
  return out;
}

/* ── WebGL ───────────────────────────────────────────────────── */
var gl = null, prog = null, U = {}, noiseTex = null;
var VS = 'attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}';
var FS = [
'#ifdef GL_FRAGMENT_PRECISION_HIGH',
'precision highp float;',
'#else',
'precision mediump float;',
'#endif',
'uniform vec2 uRes;uniform float uTime,uPx,uRd,uTc,uGain,uFlash,uCover,uScale;',
'uniform vec2 uCore,uD1,uD2;uniform vec3 uTint;',
'uniform vec4 uP[6];uniform vec3 uPC[6];uniform vec3 uPL[6];uniform float uPA[6];',
'uniform sampler2D uN;',
'float h21(vec2 p){p=fract(p*vec2(123.34,456.21));p+=dot(p,p+45.32);return fract(p.x*p.y);}',
'float T(vec2 uv,int c){vec3 t=texture2D(uN,uv).rgb;return c==0?t.r:(c==1?t.g:t.b);}',
/* ความหนาเมฆ — ต้องตรงกับ densAt() ใน JS */
'float dens(vec2 p,out float shade){',
'  vec2 q=p/uScale;vec2 a=q+uD1;',
'  a.x+=(T(a*.37,1)-.5)*.2;a.y+=(T(a*.37+vec2(.5,0.),2)-.5)*.2;',
'  float n=.50*T(a,0)+.28*T(a*2.13+vec2(.31,.17),0)+.22*T(a*4.37+vec2(.71,.29),1);',
'  float hf=T(a*7.9+vec2(.13,.61),2);',
'  float dA=smoothstep(uCover,uCover+.2,n)*(.6+2.2*clamp(n-uCover,0.,.4))*(.55+.9*hf);',
'  vec2 b=q*.55+uD2;float n2=.6*T(b,1)+.4*T(b*2.31+vec2(.5,.13),2);',
'  float dB=smoothstep(uCover+.08,uCover+.34,n2);',
'  shade=n*.5+hf*.3+n2*.2;return dA*1.6+dB*.7;}',
'vec3 stars(vec2 p){',
'  float cs=30.*uPx;vec2 c=floor(p/cs);float h=h21(c);if(h>.42)return vec3(0.);',
'  vec2 o=(c+.15+.7*vec2(h21(c+7.1),h21(c+3.7)))*cs;float d=length(p-o);',
'  float b=pow(h21(c+11.3),3.)*.9+.05;float sz=(.55+1.3*pow(h21(c+5.9),8.))*uPx;',
'  float tw=.65+.35*sin(uTime*(.7+2.*h)+h*60.);',
'  vec3 col=mix(vec3(1.,.86,.72),vec3(.72,.82,1.),h21(c+2.2));',
'  return col*b*tw*exp(-d*d/(sz*sz))*1.6;}',
'vec4 planet(vec2 p,vec4 P,vec3 C,vec3 L,float act,vec3 lc,out vec3 glow){',
'  vec2 dv=(p-P.xy)/P.z;float r=length(dv);glow=vec3(0.);',
'  float lit2=max(dot(normalize(vec3(dv,.4)),L),0.);',
'  if(r>1.){float g=exp(-(r-1.)*(act>.5?2.2:4.));glow=C*lc*g*(.05+.22*act)*(.25+.75*lit2);return vec4(0.);}',
'  vec3 n=vec3(dv,sqrt(max(0.,1.-r*r)));',
'  float lam=max((dot(n,L)+.08)/1.08,0.);',
'  float band=T(vec2(dv.y*.45+P.x*.001,dv.x*.12+uTime*.004),0);',
'  vec3 alb=C*(.55+.75*band);',
'  vec3 col=alb*lc*lam*2.1+C*.018;',
'  float fr=pow(1.-n.z,2.5);col+=C*lc*fr*smoothstep(-.3,.7,dot(n.xy,normalize(L.xy+1e-4)))*(.7+.6*act);',
'  float a=1.-smoothstep(1.-1.6/P.z,1.,r);',
'  return vec4(col,a);}',
'vec3 aces(vec3 x){return clamp((x*(2.51*x+.03))/(x*(2.43*x+.59)+.14),0.,1.);}',
'void main(){',
'  vec2 p=gl_FragCoord.xy;float d=length(p-uCore);float rd=uRd;',
'  float vy=p.y/uRes.y;',
'  vec3 col=mix(vec3(.004,.006,.014),vec3(.011,.015,.030),vy);',
'  col+=stars(p);',
'  vec3 lc=mix(vec3(1.,.95,.86),uTint,.45)*uGain;',
'  lc=mix(lc,lc*vec3(1.35,.55,.42),uFlash*.65);',
'  vec3 gsum=vec3(0.);vec3 g;',
/* ดาวเคราะห์ที่อยู่ไกลกว่าแก่นกลาง (หลัง) */
'  for(int i=0;i<6;i++){if(uP[i].w<0.){vec4 pl=planet(p,uP[i],uPC[i],uPL[i],uPA[i],lc,g);col=mix(col,pl.rgb,pl.a);gsum+=g;}}',
/* แก่นกลาง: ดิสก์เล็กสว่างจัด ขอบมืดลงเล็กน้อย มีลายพื้นผิวจางๆ */
'  float disc=1.-smoothstep(rd-1.2*uPx,rd+.6*uPx,d);',
'  if(disc>0.){vec2 dv=(p-uCore)/rd;float mu=sqrt(max(0.,1.-dot(dv,dv)));',
'    float mar=T(dv*.18+vec2(.3,.6),2);vec3 dc=vec3(1.,.97,.9)*(.78+.3*mar)*(.55+.45*mu);',
'    col=mix(col,dc*mix(vec3(1.),uTint,.2)*16.*uGain,disc);}',
'  for(int i=0;i<6;i++){if(uP[i].w>=0.){vec4 pl=planet(p,uP[i],uPC[i],uPL[i],uPA[i],lc,g);col=mix(col,pl.rgb,pl.a);gsum+=g;}}',
'  col+=gsum;',
/* ชั้นบรรยากาศ: เมฆดูดแสงด้านหลัง แล้วกระเจิงแสงจากแก่นกลางเข้าตา */
'  float sh,sh2;float D=dens(p,sh);float Tr=exp(-D*1.15);',
'  vec2 tl=uCore-p;float tlen=length(tl);',
'  float D2=dens(p+tl/max(tlen,1.)*min(tlen,rd*1.4),sh2);',
'  float facing=clamp((D-D2)*1.4,-1.,1.);',
'  col*=Tr;',
'  float S=3.2*exp(-d/(rd*1.9))+.95*exp(-d/(rd*5.))+.16*exp(-d/(rd*13.))+.018*exp(-d/(rd*38.));',
'  float self=exp(-D*1.7);',
'  vec3 cloud=lc*S*(1.-Tr)*mix(1.,self,.72)*(.6+.8*sh)*(1.+.9*facing);',
'  vec3 amb=vec3(.0058,.0080,.0150)*(1.-Tr)*(.35+1.1*sh)*(1.+.45*facing);',
/* corona: วงสีรุ้งจากการเลี้ยวเบน เห็นเฉพาะตรงเมฆบาง */
'  float x=d/(rd*4.6);',
'  vec3 irid=.5+.5*cos(6.2832*(x*1.15+vec3(0.,.33,.67))+.9);',
'  float env=exp(-x*2.1)*smoothstep(.35,.8,x);',
'  float thin=clamp((1.-Tr)*Tr*4.,0.,1.);',
'  irid=mix(vec3(1.,.93,.84),irid,.5);',
'  vec3 corona=(irid*env*.55+vec3(.82,.9,1.)*exp(-x*x*5.)*.35)*thin*lc;',
'  vec3 haze=lc*S*.035;',
/* แสงจ้าในเลนส์ (glare) ขึ้นกับว่าดวงไฟถูกเมฆบังแค่ไหนจริงๆ */
'  float G=uTc*(1.5*exp(-d/(rd*1.1))+.30*exp(-d/(rd*3.6))+.06*exp(-d/(rd*14.)));',
'  col+=cloud+amb+corona+haze+lc*G;',
'  col=aces(col*1.05);',
'  col=pow(col,vec3(1./2.2));',
'  col+=(h21(p+fract(uTime))-.5)/255.;',
'  gl_FragColor=vec4(col,1.);}'
].join('\n');

function initGL(){
  try{
    gl = cv.getContext('webgl', { alpha:false, antialias:false, depth:false, stencil:false, premultipliedAlpha:false, preserveDrawingBuffer:false })
      || cv.getContext('experimental-webgl');
  }catch(_){ gl = null; }
  if(!gl) return false;
  function sh(type, src){ var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    if(!gl.getShaderParameter(s, gl.COMPILE_STATUS)){ console.warn('[KD galaxy] shader:', gl.getShaderInfoLog(s)); return null; } return s; }
  var vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, FS);
  if(!vs || !fs){ gl = null; return false; }
  prog = gl.createProgram(); gl.attachShader(prog, vs); gl.attachShader(prog, fs); gl.linkProgram(prog);
  if(!gl.getProgramParameter(prog, gl.LINK_STATUS)){ console.warn('[KD galaxy] link:', gl.getProgramInfoLog(prog)); gl = null; return false; }
  gl.useProgram(prog);
  var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(prog, 'a'); gl.enableVertexAttribArray(loc); gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);
  ['uRes','uTime','uPx','uRd','uTc','uGain','uFlash','uCover','uScale','uCore','uD1','uD2','uTint','uN'].forEach(function(n){ U[n] = gl.getUniformLocation(prog, n); });
  ['uP','uPC','uPL','uPA'].forEach(function(n){ U[n] = gl.getUniformLocation(prog, n + '[0]'); });
  var px = new Uint8Array(NS * NS * 4);
  for(var i = 0; i < NS * NS; i++){ px[i*4] = NOISE[0][i] * 255; px[i*4+1] = NOISE[1][i] * 255; px[i*4+2] = NOISE[2][i] * 255; px[i*4+3] = 255; }
  noiseTex = gl.createTexture(); gl.activeTexture(gl.TEXTURE0); gl.bindTexture(gl.TEXTURE_2D, noiseTex);
  gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, NS, NS, 0, gl.RGBA, gl.UNSIGNED_BYTE, px);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.REPEAT);
  gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
  gl.uniform1i(U.uN, 0);
  return true;
}
cv.addEventListener('webglcontextlost', function(e){ e.preventDefault(); stop(); gl = null; }, false);
cv.addEventListener('webglcontextrestored', function(){ if(initGL()){ resize(); start(); } }, false);

/* ── overlay 2D: เส้นวงโคจร + ชื่อ (คมเต็มความละเอียดจอ) ───────── */
var ov = document.createElement('canvas'); ov.id = 'galaxy-ui';
ov.setAttribute('aria-hidden', 'true');
ov.style.cssText = 'position:fixed;inset:0;width:100%;height:100%;pointer-events:none;display:block;z-index:' + (getComputedStyle(cv).zIndex === 'auto' ? 0 : getComputedStyle(cv).zIndex);
cv.parentNode.insertBefore(ov, cv.nextSibling);
var o2 = ov.getContext('2d');
var c2 = null;    // 2D fallback context (ตั้งใน boot ถ้าไม่มี WebGL)

function resize(){
  W = window.innerWidth; H = window.innerHeight;
  DPR = Math.min(2, window.devicePixelRatio || 1);
  var glScale = Math.min(DPR, 1.5) * Q, maxPx = 2.2e6;
  if(W * H * glScale * glScale > maxPx) glScale = Math.sqrt(maxPx / (W * H));
  cv.width = Math.max(1, Math.round(W * glScale)); cv.height = Math.max(1, Math.round(H * glScale));
  ov.width = Math.round(W * DPR); ov.height = Math.round(H * DPR);
  computeGeo();
  cloudScale = Math.max(380, geo.s * 0.85);
  if(!running) frame(performance.now());
}
var _rT;
window.addEventListener('resize', function(){ clearTimeout(_rT); _rT = setTimeout(resize, 90); }, { passive:true });
window.addEventListener('KD:resize', function(){ resize(); }, { passive:true });

/* ── วาดหนึ่งเฟรม ─────────────────────────────────────────────── */
function draw(now){
  computeGeo();
  var tsec = (now - t0) / 1000, pl = planets(now);
  var gain = 1 + 0.18 * think * Math.sin(tsec * 3.2) + gainPulse;
  var Tc = Math.exp(-densAt(geo.cx, geo.cy) * 1.15);
  var sx = cv.width / W;                                    // CSS → GL px

  if(gl){
    gl.viewport(0, 0, cv.width, cv.height);
    gl.uniform2f(U.uRes, cv.width, cv.height);
    gl.uniform1f(U.uTime, tsec); gl.uniform1f(U.uPx, sx);
    gl.uniform1f(U.uRd, geo.rd * sx); gl.uniform1f(U.uTc, Tc); gl.uniform1f(U.uGain, gain);
    gl.uniform1f(U.uFlash, flash); gl.uniform1f(U.uCover, COVER); gl.uniform1f(U.uScale, cloudScale * sx);
    gl.uniform2f(U.uCore, geo.cx * sx, (H - geo.cy) * sx);
    gl.uniform2f(U.uD1, drift1[0], drift1[1]); gl.uniform2f(U.uD2, drift2[0], drift2[1]);
    gl.uniform3f(U.uTint, tint[0], tint[1], tint[2]);
    var P = new Float32Array(24), PC = new Float32Array(18), PL = new Float32Array(18), PA = new Float32Array(6);
    pl.forEach(function(p, i){
      P[i*4] = p.x * sx; P[i*4+1] = (H - p.y) * sx; P[i*4+2] = p.r * sx; P[i*4+3] = p.sa;
      var c = routeRGB(p.rt.route), k = p.act ? 1 : 0.72;
      PC[i*3] = c[0] * k + 0.08 * (1 - k); PC[i*3+1] = c[1] * k + 0.08 * (1 - k); PC[i*3+2] = c[2] * k + 0.1 * (1 - k);
      /* ทิศแสงจากดาวเคราะห์ไปหาแก่นกลางใน 3 มิติ (GL: y ขึ้น, z เข้าหาผู้ดู) */
      var lx = geo.cx - p.x, ly = -(geo.cy - p.y), lz = -p.z * 0.9, ln = Math.sqrt(lx*lx + ly*ly + lz*lz) || 1;
      PL[i*3] = lx / ln; PL[i*3+1] = ly / ln; PL[i*3+2] = lz / ln;
      PA[i] = p.act ? 1 : 0;
    });
    gl.uniform4fv(U.uP, P); gl.uniform3fv(U.uPC, PC); gl.uniform3fv(U.uPL, PL); gl.uniform1fv(U.uPA, PA);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
  } else if(c2){
    drawFallback(pl, Tc);
  }
  drawOverlay(pl, tsec);
}

function drawFallback(pl, Tc){
  var g = c2, w = cv.width, h = cv.height, s = w / W;
  g.setTransform(1, 0, 0, 1, 0, 0);
  var bg = g.createLinearGradient(0, 0, 0, h); bg.addColorStop(0, '#0a0e1c'); bg.addColorStop(1, '#03040a');
  g.fillStyle = bg; g.fillRect(0, 0, w, h);
  var cx = geo.cx * s, cy = geo.cy * s, r = geo.rd * s, c = 'rgba(' + Math.round(255 * tint[0]) + ',' + Math.round(240 * tint[1]) + ',' + Math.round(220 * tint[2]) + ',';
  g.globalCompositeOperation = 'lighter';
  [[r * 60, .05], [r * 18, .12], [r * 6, .3], [r * 2.2, .6]].forEach(function(L){
    var gr = g.createRadialGradient(cx, cy, 0, cx, cy, L[0]); gr.addColorStop(0, c + (L[1] * (0.4 + 0.6 * Tc)) + ')'); gr.addColorStop(1, c + '0)');
    g.fillStyle = gr; g.fillRect(cx - L[0], cy - L[0], L[0] * 2, L[0] * 2);
  });
  g.globalCompositeOperation = 'source-over'; g.fillStyle = '#fffaf0'; g.beginPath(); g.arc(cx, cy, r, 0, 6.2832); g.fill();
  pl.forEach(function(p){
    var col = routeRGB(p.rt.route), lx = (geo.cx - p.x), ly = (geo.cy - p.y), ln = Math.sqrt(lx*lx + ly*ly) || 1;
    var gr = g.createRadialGradient((p.x + lx / ln * p.r * .5) * s, (p.y + ly / ln * p.r * .5) * s, 0, p.x * s, p.y * s, p.r * s);
    gr.addColorStop(0, 'rgb(' + col.map(function(v){ return Math.round(Math.min(255, v * 300)); }).join(',') + ')'); gr.addColorStop(1, '#05060c');
    g.fillStyle = gr; g.beginPath(); g.arc(p.x * s, p.y * s, p.r * s, 0, 6.2832); g.fill();
  });
}

function drawOverlay(pl, tsec){
  var g = o2; g.setTransform(DPR, 0, 0, DPR, 0, 0); g.clearRect(0, 0, W, H);
  var small = Math.min(W, H) < 520;
  hits = [];
  /* วงโคจร: ครึ่งหลังจาง ครึ่งหน้าชัด จางลงใกล้แสงจ้า และถูกเมฆบังตามความหนาจริง */
  ORBIT_ROUTES.forEach(function(rt){
    var R = geo.s * rt.orb, act = rt.route === activeRoute, col = routeRGB(rt.route), N = 120;
    var rgb = act ? col.map(function(v){ return Math.round(Math.min(255, v * 290)); }).join(',') : '170,182,220';
    g.lineWidth = act ? 1.3 : 0.7;
    for(var i = 0; i < N; i++){
      if(!act && (i % 4 > 1)) continue;                       /* เส้นประสำหรับวงที่ไม่ได้เลือก */
      var a0 = i / N * 6.2832, a1 = (i + 1) / N * 6.2832, am = (a0 + a1) / 2;
      var x0 = geo.cx + Math.cos(a0) * R, y0 = geo.cy + Math.sin(a0) * R * geo.tilt;
      var x1 = geo.cx + Math.cos(a1) * R, y1 = geo.cy + Math.sin(a1) * R * geo.tilt;
      var xm = (x0 + x1) / 2, ym = (y0 + y1) / 2, dc = Math.hypot(xm - geo.cx, ym - geo.cy);
      var back = Math.sin(am) < 0 ? 0.42 : 1;
      var near = smoothstep(geo.rd * 2.5, geo.rd * 9, dc);
      var veil = 0.35 + 0.65 * Math.exp(-densAt(xm, ym) * 1.15);
      var a = (act ? 0.55 : 0.13) * back * near * veil;
      if(a < 0.01) continue;
      g.strokeStyle = 'rgba(' + rgb + ',' + a.toFixed(3) + ')';
      g.beginPath(); g.moveTo(x0, y0); g.lineTo(x1, y1); g.stroke();
    }
  });
  /* ชื่อเส้นทางใต้ดาวเคราะห์ */
  g.textAlign = 'center'; g.textBaseline = 'top';
  pl.forEach(function(p){
    hits.push({ x: p.x, y: p.y, r: Math.max(16, p.r + 10), route: p.rt.route });
    var veil = 0.4 + 0.6 * Math.exp(-densAt(p.x, p.y) * 1.15), depth = p.sa < 0 ? 0.6 : 1;
    var dc = Math.hypot(p.x - geo.cx, p.y - geo.cy);
    if(p.sa < 0) depth *= smoothstep(geo.rd * 3, geo.rd * 9, dc);      /* อยู่หลังแสงจ้า → มองไม่เห็นชื่อ */
    if(depth < 0.05){ hits.pop(); return; }
    var ly = p.y + p.r + 5, coreLy = geo.cy + geo.rd * 2.4 + 6;
    if(Math.abs(ly - coreLy) < 14 && Math.abs(p.x - geo.cx) < 70) depth *= 0.15;     /* ชนกับชื่อแก่นกลาง */
    var col = routeRGB(p.rt.route).map(function(v){ return Math.round(Math.min(255, 120 + v * 160)); }).join(',');
    g.font = (p.act ? '600 ' : '500 ') + (small ? 9 : 10) + 'px "IBM Plex Mono","DM Mono",ui-monospace,monospace';
    g.fillStyle = p.act ? 'rgba(' + col + ',' + (0.95 * veil).toFixed(3) + ')' : 'rgba(176,186,220,' + (0.42 * veil * depth).toFixed(3) + ')';
    g.fillText(p.rt.lbl, p.x, p.y + p.r + 5);
  });
  /* ชื่อแก่นกลาง */
  var lv = 0.5 + 0.5 * Math.exp(-densAt(geo.cx, geo.cy + geo.rd * 3) * 1.15);
  g.font = '600 ' + (small ? 10 : 11) + 'px "IBM Plex Mono","DM Mono",ui-monospace,monospace';
  g.fillStyle = 'rgba(255,246,228,' + (0.78 * lv).toFixed(3) + ')';
  g.fillText('KING DIADEM', geo.cx, geo.cy + geo.rd * 2.4 + 6);
}

/* ── loop: ~30fps (เมฆเคลื่อนช้า) · หยุดเมื่อซ่อน ───────────────── */
var acc = 0, slow = 0, frames = 0;
function step(dt){
  var sp = REDUCED ? 0.15 : 1;
  think += (thinkT - think) * Math.min(1, dt * 2.5);
  var boost = 1 + think * 3.5;
  drift1[0] += dt * 0.0042 * sp * boost; drift1[1] += dt * 0.0016 * sp * boost;
  drift2[0] += dt * 0.0075 * sp * boost; drift2[1] += dt * 0.0024 * sp * boost;
  for(var i = 0; i < 3; i++) tint[i] += (tintT[i] - tint[i]) * Math.min(1, dt * 1.6);
  flash *= Math.pow(0.35, dt); gainPulse *= Math.pow(0.2, dt);
}
function frame(now){
  raf = 0;
  var dt = Math.min(0.1, (now - lastT) / 1000);
  if(running && now - lastT < (REDUCED ? 400 : 30)){ raf = requestAnimationFrame(frame); return; }
  lastT = now; step(dt);
  var t1 = performance.now(); draw(now); var cost = performance.now() - t1;
  /* ถ้าเครื่องช้า ลดความละเอียด GL ลงทีละขั้น (เมฆนุ่มอยู่แล้ว ไม่เสียความคม) */
  if(gl && running){ frames++; if(cost > 22) slow++; if(frames >= 40){ if(slow > 20 && Q > 0.55){ Q = Math.max(0.55, Q - 0.15); resize(); } frames = 0; slow = 0; } }
  if(running) raf = requestAnimationFrame(frame);
}
function visible(){ return !document.hidden && !(window.KD && window.KD.visible === false) && getComputedStyle(cv).display !== 'none'; }
function start(){ if(running || !visible()) return; running = true; lastT = performance.now(); raf = requestAnimationFrame(frame); }
function stop(){ running = false; if(raf){ cancelAnimationFrame(raf); raf = 0; } }
document.addEventListener('visibilitychange', function(){ document.hidden ? stop() : start(); });
window.addEventListener('KD:visibility', function(e){ var v = e.detail && e.detail.visible; v ? start() : stop(); }, { passive:true });

/* ── events จากหน้าแอป ───────────────────────────────────────── */
function setRouteInternal(r){
  if(!ROUTE_COLOR[r]) return;
  activeRoute = r; tintT = routeTint(r); if(!running) frame(performance.now());
}
window.addEventListener('KD:response', function(e){
  var d = e.detail || {};
  var route = (d.consensus && d.consensus.final_action) || d.route;
  if(route === 'crisis') route = 'collapse';
  if(route && ROUTE_COLOR[route]) setRouteInternal(route);
  var risk = d.risk_score != null ? d.risk_score : (d.risk && d.risk.risk_score);
  gainPulse = 0.35;
  if(risk > 75) flash = 1; else if(risk > 45) flash = 0.45;
  thinkT = 0;
}, { passive:true });
window.addEventListener('KD:decision', function(e){ var r = e.detail && e.detail.route; if(r) setRouteInternal(r); }, { passive:true });
window.addEventListener('KD:thinking', function(e){ window.KD_galaxy.think(!(e.detail && e.detail.on === false)); }, { passive:true });

/* คลิกดาวเคราะห์ = เลือกเส้นทาง (ฟังที่ document เพราะหน้าแอปอยู่ชั้นบน canvas) */
var INTERACTIVE = 'a,button,input,textarea,select,label,dialog,summary,[role=button],[contenteditable],.m,.bubble,#composer,#sidebar,#tabbar,.card,.u-card';
function hitAt(x, y){ for(var i = 0; i < hits.length; i++){ var h = hits[i]; if((x - h.x) * (x - h.x) + (y - h.y) * (y - h.y) < h.r * h.r) return h; } return null; }
document.addEventListener('click', function(e){
  if(!running || (e.target.closest && e.target.closest(INTERACTIVE))) return;
  var h = hitAt(e.clientX, e.clientY); if(h) window.KD_setRoute(h.route);
});
document.addEventListener('pointermove', function(e){
  if(!running || e.pointerType === 'touch') return;
  var over = !(e.target.closest && e.target.closest(INTERACTIVE)) && !!hitAt(e.clientX, e.clientY);
  document.documentElement.style.cursor = over ? 'pointer' : '';
}, { passive:true });

/* ── PUBLIC API (เดิม + ใหม่) ─────────────────────────────────── */
window.KD_setRoute = function(route){
  setRouteInternal(route);
  if(typeof window.setRoute === 'function') window.setRoute(route);
  window.dispatchEvent(new CustomEvent('KD:routeChange', { detail:{ route:route } }));
};
window.KD_pulse = window.KD_pulse || function(route){ if(route) window.KD_setRoute(route); };
window.KD_setState = window.KD_setState || function(key, val){
  if(!window.KD) window.KD = {};
  if(!window.KD.state) window.KD.state = {};
  window.KD.state[key] = val;
};
window.KD_galaxy = {
  route: setRouteInternal,                                   /* ไม่เรียกกลับ setRoute (กันวนลูป) */
  think: function(on){ thinkT = on ? 1 : 0; if(!on) think = Math.min(think, 0.6); },
  pause: stop, resume: start, resize: resize,
  refocus: function(){ computeGeo(); if(!running) frame(performance.now()); }
};

/* ── boot ─────────────────────────────────────────────────────── */
if(!initGL()){
  try{ c2 = cv.getContext('2d'); }catch(_){ c2 = null; }
}
tint = routeTint(activeRoute); tintT = tint.slice();
resize();
start();
})();
