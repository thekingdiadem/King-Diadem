/* KING DIADEM — ท้องฟ้าของหน้า The Universe
 * "จักรวาลไม่ได้หมุนรอบใคร แต่ทุกคนร่วมกันเป็นส่วนหนึ่งของทั้งจักรวาล"
 *
 * ไม่มีลำแสงกลาง ไม่มีจุดให้ทุกอย่างหมุนรอบ — เรามองออกไปจากข้างในทางช้างเผือก
 *  · เลื่อนหน้าเว็บ = หันมองรอบตัวครบหนึ่งรอบ (Personal Horizon)
 *  · ผู้สังเกตลอยโคจรช้าๆ ฟ้าจึงไหวตามเรา ไม่ใช่ฟ้าหมุนรอบเรา (Orbiting Observer)
 *  · กาแล็กซีไกลกระจายเท่าๆ กันทุกทิศ (Uniform Distribution)
 *  · บทที่ว่าด้วยภาพลวงตา: กล้องเลื่อนเข้าพร้อมซูมออก (Geometry Illusion)
 *  · แตะตรงไหนก็ได้ แสงแผ่จากจุดนั้นไปทั่วฟ้า ดาวทุกดวงสว่างตาม (Ego-less Universe)
 * วาดด้วย WebGL ชั้นเดียว · จำกัด 90 เฟรม · หยุดวาดเมื่อซ่อนแท็บ · ลดการเคลื่อนไหว = ฟ้านิ่ง */
(function () {
  'use strict';
  var cv = document.getElementById('galaxy'); if (!cv) return;
  var REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
  var gl = null;
  try { gl = cv.getContext('webgl', { alpha: false, antialias: false, depth: false, stencil: false }); } catch (e) { gl = null; }
  if (!gl) { document.documentElement.classList.add('no-sky'); return; }   // ภาพสำรองใน CSS

  var VS = 'attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}';
  var FS = [
    'precision highp float;',
    'uniform vec2 uRes,uC;uniform float uQ,uT,uF,uYaw,uPitch,uGal,uDim;uniform vec3 uN,uG;uniform vec4 uRip,uRip2;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float h3(vec3 p){p=fract(p*.3183099+.1);p*=17.;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}',
    'float n3(vec3 x){vec3 i=floor(x),f=fract(x);f=f*f*(3.-2.*f);',
    ' return mix(mix(mix(h3(i),h3(i+vec3(1.,0.,0.)),f.x),mix(h3(i+vec3(0.,1.,0.)),h3(i+vec3(1.,1.,0.)),f.x),f.y),',
    '  mix(mix(h3(i+vec3(0.,0.,1.)),h3(i+vec3(1.,0.,1.)),f.x),mix(h3(i+vec3(0.,1.,1.)),h3(i+vec3(1.,1.,1.)),f.x),f.y),f.z);}',
    'float fb4(vec3 p){float a=.5,s=0.;for(int i=0;i<4;i++){s+=a*n3(p);p=p*2.03+vec3(1.7,9.2,4.1);a*=.5;}return s;}',
    'float fb3(vec3 p){float a=.5,s=0.;for(int i=0;i<3;i++){s+=a*n3(p);p=p*2.03+vec3(1.7,9.2,4.1);a*=.5;}return s;}',
    'vec3 face(vec3 d){vec3 a=abs(d);if(a.x>=a.y&&a.x>=a.z)return vec3(d.yz/a.x,d.x>0.?1.:2.);if(a.y>=a.z)return vec3(d.xz/a.y,d.y>0.?3.:4.);return vec3(d.xy/a.z,d.z>0.?5.:6.);}',
    /* กาแล็กซีไกล: วงรีเล็กเอียงสุ่ม อุ่นสลับเย็น */
    'vec3 gal(vec3 d,float K,float th,float s0,float s1){',
    ' vec3 F=face(d);vec2 g=F.xy*K,c=floor(g)+F.z*97.,f=fract(g)-.5;',
    ' if(h(c)<th)return vec3(0.);',
    ' vec2 q=f-(vec2(h(c+.37),h(c+.71))-.5)*.4;float an=h(c+1.3)*6.2832,ca=cos(an),sa=sin(an);q=vec2(q.x*ca+q.y*sa,-q.x*sa+q.y*ca);',
    ' float e=.25+.75*h(c+2.1),s=mix(s0,s1,h(c+2.9)),r2=(q.x*q.x+q.y*q.y/(e*e))/(s*s);',
    ' return mix(vec3(.66,.78,1.),vec3(1.,.8,.56),step(.55,h(c+4.3)))*(exp(-r2)*.7+exp(-r2*7.)*.6)*(.45+.55*h(c+3.7));',
    '}',
    /* ดาว: จุดเล็กนับไม่ถ้วน · ดาวสว่างมีแฉกบางๆ */
    'vec3 pts(vec3 d,float K,float dens,float sharp){',
    ' vec3 F=face(d);vec2 g=F.xy*K,c=floor(g)+F.z*131.,f=fract(g)-.5;',
    ' if(h(c+.5)>dens)return vec3(0.);',
    ' vec2 q=f-(vec2(h(c+.13),h(c+.29))-.5)*.5;float r2=dot(q,q);',
    ' float sp=exp(-abs(q.x)*40.)*exp(-q.y*q.y*9000.)+exp(-abs(q.y)*40.)*exp(-q.x*q.x*9000.);',
    ' return mix(vec3(.72,.84,1.),vec3(1.,.84,.62),h(c+.77))*(exp(-r2*sharp)+sp*step(K,110.)*.35)*(.3+.7*h(c+.91));',
    '}',
    /* แสงที่แผ่ออกจากจุดที่แตะ: วงแหวนบนท้องฟ้า (ระยะเชิงมุม) */
    'float ring(vec3 d,vec4 R){if(R.w<0.)return 0.;float an=acos(clamp(dot(d,R.xyz),-1.,1.));return exp(-pow((an-R.w*1.15)/.13,2.))*max(0.,1.-R.w/3.2);}',
    'void main(){',
    ' vec2 p=vec2(gl_FragCoord.x,uRes.y-gl_FragCoord.y)/uQ;',
    ' vec3 v=normalize(vec3((p.x-uC.x)/uF,-(p.y-uC.y)/uF,-1.));',
    ' float cp=cos(uPitch),sp=sin(uPitch);v=vec3(v.x,v.y*cp-v.z*sp,v.y*sp+v.z*cp);',
    ' float cy=cos(uYaw),sy=sin(uYaw);vec3 d=vec3(v.x*cy-v.z*sy,v.y,v.x*sy+v.z*cy);',
    ' vec3 E=cross(uN,uG);float b=asin(clamp(dot(d,uN),-1.,1.)),l=atan(dot(d,E),dot(d,uG)),t=uT;',
    ' vec3 col=vec3(.004,.006,.017);',
    ' float core=exp(-l*l/.9),sg=.07+.12*exp(-l*l/.25),G=exp(-b*b/(2.*sg*sg)),dn=0.;',
    ' if(G>.003){',
    '  dn=fb3(d*15.+7.7);float cl=fb4(d*6.5+3.1),nb=fb3(d*4.2+11.),fine=n3(d*42.);',
    '  float b0=.016*sin(l*3.+1.)+.03*(n3(d*3.5)-.5);',
    '  float rift=exp(-pow((b-b0)/(.012+.02*core),2.))*smoothstep(.3,.62,dn);',
    '  float I=G*(.24+.6*core)*(.45+1.1*cl)*(.8+.4*fine)*(1.-.82*rift)*(1.-.5*smoothstep(.48,.78,dn)*G);',
    '  vec3 bc=mix(vec3(.55,.68,1.),vec3(1.,.8,.55),smoothstep(.15,.85,core));',
    '  float hot=smoothstep(.56,.8,nb)*G,cold=smoothstep(.56,.8,1.-nb)*G;',
    '  col+=bc*I*.52+vec3(1.,.38,.56)*hot*.18+vec3(.36,.58,1.)*cold*.15+vec3(1.,.84,.62)*exp(-l*l/.06-b*b/.006)*.3;',
    ' }',
    ' float za=1.-smoothstep(0.,.45,G), lit=1.+3.5*(ring(d,uRip)+ring(d,uRip2));',
    ' col+=(gal(d,34.,.8,.03,.085)*.22+gal(d,13.,.93,.05,.11)*.4)*(.25+.75*za)*uGal*lit;',
    ' vec3 st=pts(d,230.,.035+.4*G*(1.-.6*smoothstep(.3,.62,dn)*G),55.)*.55+pts(d,62.,.06,140.)*.9;',
    ' col+=st*lit*(.85+.15*sin(t*1.3+h(floor(d.xy*60.))*30.));',
    ' col+=vec3(1.,.86,.66)*(ring(d,uRip)+ring(d,uRip2))*.035;',
    ' col=(1.-exp(-col*1.25))*uDim;',
    ' col+=(h(p+fract(t))-.5)*.006;',
    ' gl_FragColor=vec4(col,1.);',
    '}'].join('\n');

  function sh(type, src) { var o = gl.createShader(type); gl.shaderSource(o, src); gl.compileShader(o);
    if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) { console.warn('[KD universe sky]', gl.getShaderInfoLog(o)); return null; } return o; }
  var vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, FS);
  if (!vs || !fs) { document.documentElement.classList.add('no-sky'); return; }
  var pr = gl.createProgram(); gl.attachShader(pr, vs); gl.attachShader(pr, fs); gl.linkProgram(pr); gl.useProgram(pr);
  var U = {}; ['uRes', 'uQ', 'uT', 'uC', 'uF', 'uYaw', 'uPitch', 'uGal', 'uDim', 'uN', 'uG', 'uRip', 'uRip2'].forEach(function (k) { U[k] = gl.getUniformLocation(pr, k); });
  var buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var A = gl.getAttribLocation(pr, 'a'); gl.enableVertexAttribArray(A); gl.vertexAttribPointer(A, 2, gl.FLOAT, false, 0, 0);

  /* กรอบทางช้างเผือก (เหมือนแท็บจักรวาล): แถบพาดเฉียง ใจกลางกาแล็กซีอยู่นอกจอ */
  function nrm(v) { var l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; }
  function crs(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  var GN, GG;
  function frame3(portrait) {
    var F = nrm([.06, -.15, -1]), tl = portrait ? 1.0 : .52, T0 = [Math.cos(tl), Math.sin(tl), 0];
    var k = T0[0] * F[0] + T0[1] * F[1], T = nrm([T0[0] - k * F[0], T0[1] - k * F[1], -k * F[2]]);
    var a = portrait ? 1.35 : 1.25; GN = nrm(crs(F, T)); GG = nrm([F[0] * Math.cos(a) + T[0] * Math.sin(a), F[1] * Math.cos(a) + T[1] * Math.sin(a), F[2] * Math.cos(a) + T[2] * Math.sin(a)]);
  }

  var W = 0, H = 0, Q = 1, qs = 1, slow = 0;
  function size() {
    W = innerWidth; H = innerHeight; Q = Math.min(1.25, window.devicePixelRatio || 1) * .75 * qs;
    cv.width = Math.round(W * Q); cv.height = Math.round(H * Q); gl.viewport(0, 0, cv.width, cv.height); frame3(W < H * .9); kick();
  }

  /* ── กล้อง: เลื่อนหน้า = หันรอบตัว · เมาส์/นิ้ว = เหลือบมอง · บทต่างๆ ตั้งเป้าให้ (ค่อยๆ ไหลเข้าหา) ── */
  var cam = { yaw: 0, pitch: 0, zoom: 1, gal: 1, sway: 1 }, tgt = { pitch: 0, gal: 1, sway: 1 }, look = { x: 0, y: 0, tx: 0, ty: 0 };
  var dolly = -1, rips = [{ w: -1 }, { w: -1 }], ripN = 0, t0 = performance.now(), last = 0, acc = 0, raf = 0, tsec = 0;
  addEventListener('pointermove', function (e) { look.tx = e.clientX / W - .5; look.ty = e.clientY / H - .5; kick(); }, { passive: true });

  /* ทิศบนฟ้าที่อยู่ใต้จุด (x, y) บนจอ ตามกล้องตอนนี้ */
  function dirAt(x, y) {
    var f = Math.max(W, H) * .66 * cam.zoom, v = nrm([(x - W / 2) / f, -(y - H / 2) / f, -1]);
    var cp = Math.cos(cam.pitch), sp = Math.sin(cam.pitch); v = [v[0], v[1] * cp - v[2] * sp, v[1] * sp + v[2] * cp];
    var cy = Math.cos(cam.yaw), sy = Math.sin(cam.yaw); return [v[0] * cy - v[2] * sy, v[1], v[0] * sy + v[2] * cy];
  }
  function ripple(x, y) { if (REDUCED) return; var d = dirAt(x, y); rips[ripN % 2] = { x: d[0], y: d[1], z: d[2], w: 0 }; ripN++; kick(); }
  /* แตะท้องฟ้า (ที่ไม่ใช่ปุ่ม/ช่องกรอก) = แสงเดียวกันแผ่ไปถึงทุกดวง */
  addEventListener('click', function (e) { if (e.target.closest('a,button,input,textarea,label,.sim-box')) return; ripple(e.clientX, e.clientY); });

  /* บทของแนวคิด 5 ข้อ (data-sky บนแต่ละการ์ด) */
  var CH = {
    horizon: function () { tgt.pitch = .28; },
    orbit: function () { tgt.sway = 4; },
    uniform: function () { tgt.gal = 2.4; },
    illusion: function () { if (!REDUCED) dolly = 0; },
    egoless: function () { ripple(W / 2, H * .42); }
  };
  function chapter(name) { tgt.pitch = 0; tgt.gal = 1; tgt.sway = 1; if (CH[name]) CH[name](); kick(); }
  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) {
        if (e.target.dataset.sky && e.isIntersecting) chapter(e.target.dataset.sky);
        if (e.isIntersecting) e.target.classList.add('in');               // ค่อยๆ ชัดขึ้นเมื่อเลื่อนมาถึง
      });
    }, { threshold: .55 });
    document.querySelectorAll('[data-sky],.section,.reveal').forEach(function (el) { io.observe(el); });
  } else document.querySelectorAll('.section,.reveal').forEach(function (el) { el.classList.add('in'); });

  /* เส้นขอบฟ้าส่วนตัว (HUD): เข็มทิศบางๆ ด้านบนเลื่อนตามมุมที่หัน */
  var hud = document.getElementById('hud-track'), hudDeg = document.getElementById('hud-deg');
  if (hud) {
    var marks = '';
    for (var k = -2; k < 26; k++) { var dg = ((k * 30) % 360 + 360) % 360; marks += '<i style="left:' + (k * 60) + 'px">' + (dg % 90 ? '·' : ['N', 'E', 'S', 'W'][dg / 90]) + '</i>'; }
    hud.innerHTML = marks;
  }

  /* เส้นทางที่ simulator ตรวจเจอ → หันไปทางนั้นพร้อมแสงแผ่ (เส้นทางคือกลุ่มดาว ไม่ใช่ดาวเคราะห์รอบแก่น) */
  var ROUTE_YAW = { general: -.6, risk: .5, civil: -1.2, survival: 1.1, collapse: 1.7, vega: -1.8 }, routeYaw = 0;
  window.KD_setRoute = function (r) { if (ROUTE_YAW[r] == null) return; routeYaw = ROUTE_YAW[r]; setTimeout(function () { ripple(W / 2, H * .45); }, 600); kick(); };

  function draw(now) {
    raf = 0; if (document.hidden) return;
    var gap = last ? (now - last) / 1000 : 0; last = now; acc = Math.min(acc + gap, 2 / 90);
    if (gap && acc + 1e-4 < 1 / 90) { raf = requestAnimationFrame(draw); return; }      // ไม่เกิน 90 เฟรม/วินาที
    acc = Math.max(0, acc - 1 / 90);
    var dt = Math.min(.05, gap || .016); if (!REDUCED) tsec += dt;
    if (dt > 1 / 40) { slow += dt; if (slow > 1.2 && qs > .55) { qs *= .8; slow = 0; size(); } } else slow = Math.max(0, slow - dt * .5);
    var sc = scrollY / Math.max(1, document.documentElement.scrollHeight - H), k = Math.min(1, dt * 2.2);
    look.x += (look.tx - look.x) * k; look.y += (look.ty - look.y) * k;
    cam.pitch += (tgt.pitch - cam.pitch) * Math.min(1, dt * 1.2); cam.gal += (tgt.gal - cam.gal) * Math.min(1, dt * 1.5); cam.sway += (tgt.sway - cam.sway) * Math.min(1, dt);
    var yaw = sc * Math.PI * 2 * .92 + routeYaw + look.x * .12 + (REDUCED ? 0 : cam.sway * .018 * Math.sin(tsec * .07));
    var pitch = cam.pitch - look.y * .08 + .12 * Math.sin(sc * Math.PI * 2) + (REDUCED ? 0 : cam.sway * .01 * Math.sin(tsec * .05));
    cam.yaw += (yaw - cam.yaw) * Math.min(1, dt * 4);
    if (dolly >= 0) { dolly += dt / 2.4; var e = Math.min(1, dolly); cam.zoom = 1 + .75 * Math.pow(1 - e, 2) * (e < .08 ? e / .08 : 1); if (dolly >= 1) { dolly = -1; cam.zoom = 1; } }
    rips.forEach(function (r) { if (r.w >= 0) { r.w += dt; if (r.w > 3.2) r.w = -1; } });
    var f = Math.max(W, H) * .66 * cam.zoom;
    gl.uniform2f(U.uRes, cv.width, cv.height); gl.uniform1f(U.uQ, Q); gl.uniform1f(U.uT, tsec);
    gl.uniform2f(U.uC, W / 2, H / 2); gl.uniform1f(U.uF, f); gl.uniform1f(U.uYaw, cam.yaw); gl.uniform1f(U.uPitch, pitch);
    gl.uniform1f(U.uGal, cam.gal); gl.uniform1f(U.uDim, 1); gl.uniform3f(U.uN, GN[0], GN[1], GN[2]); gl.uniform3f(U.uG, GG[0], GG[1], GG[2]);
    gl.uniform4f(U.uRip, rips[0].x || 0, rips[0].y || 0, rips[0].z || -1, rips[0].w); gl.uniform4f(U.uRip2, rips[1].x || 0, rips[1].y || 0, rips[1].z || -1, rips[1].w);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    if (hud) { var deg = ((cam.yaw * 180 / Math.PI) % 360 + 360) % 360; hud.style.transform = 'translateX(' + (-deg * 2 - 120) + 'px)'; if (hudDeg) hudDeg.textContent = Math.round(deg) + '°'; }
    var moving = !REDUCED || Math.abs(yaw - cam.yaw) > 1e-4 || dolly >= 0 || rips[0].w >= 0 || rips[1].w >= 0 || Math.abs(look.tx - look.x) > 1e-3;
    if (moving) kick();
  }
  function kick() { if (!raf) raf = requestAnimationFrame(draw); }
  addEventListener('scroll', kick, { passive: true });
  addEventListener('resize', function () { clearTimeout(size._t); size._t = setTimeout(size, 120); });
  document.addEventListener('visibilitychange', kick);
  cv.addEventListener('webglcontextlost', function (e) { e.preventDefault(); document.documentElement.classList.add('no-sky'); });
  size();
})();
