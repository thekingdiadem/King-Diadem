/* KING DIADEM — ตัววาดฉากบิ๊กแบงด้วยการ์ดจอ (WebGL) สำหรับ static/big_bang.js
 *
 * ตำแหน่งของอนุภาคทุกจุดคำนวณใน vertex shader จากเวลาโดยตรง (ไม่มีสถานะเก็บในเครื่อง)
 * จึงวาดได้หลักแสนจุดแม้บนมือถือ · อวกาศเป็น 3 มิติ กล้องค่อยๆ บินเข้าไปทะลุกาแล็กซีหลักตอนท้าย
 *  · พื้นหลัง: แสงวาบ · ซุปพลาสมาร้อน · ลายแสงแรก (แสงพื้นหลังของจักรวาล) · เนบิวลาจางๆ รอบกาแล็กซี
 *  · บทโลก: ดาวเคราะห์น้อยกว้างราว 10 กม. ชนคาบสมุทรยูคาทานเมื่อ 66 ล้านปีก่อน — ลูกไฟ คลื่นกระแทก ฝุ่นปกคลุมโลก
 *  · ลูกเล่น: กดค้าง = หลุมแรงโน้มถ่วงดูดและหมุนวนอนุภาครอบนิ้ว · แตะ = คลื่นกระแทกแผ่เป็นวง
 * ใช้ WebGL 1 · ไม่มีไฟล์ภาพหรือไลบรารีภายนอก · เครื่องที่ไม่รองรับ big_bang.js ใช้ตัววาด Canvas 2D เดิม */
(function () {
  'use strict';
  var NG = 5;                                   // จำนวนกาแล็กซี (ตัวแรกคือกาแล็กซีหลักที่กล้องบินเข้าไป)

  var VS_PTS = [
    'precision highp float;',
    'attribute vec4 aS;attribute vec4 aG;',     // aS = สุ่ม 4 ค่า · aG = (กาแล็กซี, ระยะจากแกน, แขน, เยื้อง)
    'uniform float uT,uAsp,uCam,uYaw,uPitch,uDPR,uPx,uGain;uniform vec2 uShake;',
    'uniform vec4 uGC[' + NG + '];uniform vec4 uGU[' + NG + '];uniform vec4 uGV[' + NG + '];',
    'uniform vec3 uWell;uniform vec4 uWave[4];',
    'varying vec3 vC;varying float vA;',
    'vec3 rotY(vec3 p,float a){float c=cos(a),s=sin(a);return vec3(c*p.x+s*p.z,p.y,-s*p.x+c*p.z);}',
    'vec3 rotX(vec3 p,float a){float c=cos(a),s=sin(a);return vec3(p.x,c*p.y-s*p.z,s*p.y+c*p.z);}',
    'void main(){',
    ' float t=uT;',
    // ระเบิดเป็นทรงกลม: ขยายพรวดช่วงแรก (inflation) แล้วค่อยๆ ขยายต่อ
    ' float z=aS.x*2.-1.,ph=aS.y*6.2831853,rr=sqrt(1.-z*z);vec3 dir=vec3(rr*cos(ph),rr*sin(ph),z);',
    ' float sp=pow(aS.z,.45);',
    ' vec3 p=dir*sp*(1.55*(1.-exp(-2.6*max(t,0.)))+.035*max(t,0.));',
    // ซุปพลาสมา: สั่นไหวร้อนจัด
    ' float pl=smoothstep(2.2,2.9,t)*(1.-smoothstep(4.6,5.4,t));',
    ' p+=vec3(sin(t*7.1+aS.x*61.),sin(t*6.3+aS.y*47.),sin(t*5.7+aS.z*53.))*.028*pl;',
    // ยุคมืด: แรงโน้มถ่วงเริ่มรวบเป็นใยบางๆ
    ' float cl=smoothstep(4.8,8.,t);',
    ' p*=1.-.18*cl*(1.-aS.w);',
    // กาแล็กซีหมุนวน
    ' if(aG.x>=0.){',
    '  int gi=int(aG.x+.5);vec4 C=uGC[0],U=uGU[0],V=uGV[0];',
    '  for(int i=0;i<' + NG + ';i++){if(i==gi){C=uGC[i];U=uGU[i];V=uGV[i];}}',
    '  float r=aG.y*C.w*(1.+(aS.y-.5)*.3),a=V.w+aG.z*6.2831853+aG.y*4.6+aG.w+U.w*(t-8.);',
    '  vec3 n=normalize(cross(U.xyz,V.xyz));',
    '  vec3 tg=C.xyz+U.xyz*cos(a)*r+V.xyz*sin(a)*r+n*(aS.w-.5)*.09*C.w*(1.3-aG.y);',
    '  float f=smoothstep(7.4+aS.w*1.4,9.9+aS.w*1.4,t);',
    '  p=mix(p,tg,f);',
    ' }',
    // กล้อง: หมุนรอบช้าๆ แล้วบินเข้าหากาแล็กซีหลัก
    ' vec3 q=rotX(rotY(p,uYaw),uPitch);',
    ' float w=q.z+uCam;',
    ' if(w<.04){gl_Position=vec4(2.,2.,2.,1.);gl_PointSize=0.;return;}',
    ' vec2 nd=vec2(q.x/uAsp,q.y)*1.6*min(uAsp,1.)/w;',      // จอแนวตั้งคิดจากด้านกว้าง — กาแล็กซีไม่หลุดขอบ
    // หลุมแรงโน้มถ่วงใต้นิ้ว: ดูดเข้าและหมุนวนเหมือนจานรอบหลุมดำ
    ' vec2 dv=uWell.xy-nd;vec2 ds=dv*vec2(uAsp,1.);float dl=length(ds)+.001;',
    ' float pull=uWell.z*exp(-dl*1.5);',
    ' nd+=(dv*.55+vec2(-dv.y,dv.x)*.7)*pull;',
    // คลื่นกระแทก
    ' float glow=0.;',
    ' for(int i=0;i<4;i++){vec4 W=uWave[i];if(W.w>0.){vec2 e=(nd-W.xy)*vec2(uAsp,1.);float ed=length(e)+.001;',
    '  float ring=exp(-pow((ed-W.z)/.07,2.));nd+=e/ed*ring*W.w*.07/vec2(uAsp,1.);glow+=ring*W.w;}}',
    ' nd+=uShake;',
    ' gl_Position=vec4(nd,0.,1.);',
    // สีตามยุค
    ' float hue=fract(aS.w*7.31);',
    ' vec3 c0=mix(vec3(.75,.85,1.),vec3(1.,.95,.85),smoothstep(0.,2.4,t));',
    ' vec3 c1=mix(vec3(1.,.42,.12),vec3(1.,.68,.3),hue);',
    ' vec3 c2=vec3(1.,.86,.66);',
    ' vec3 core=vec3(1.,.83,.55),arm=mix(vec3(.62,.75,1.),vec3(.95,.97,1.),hue);',
    ' vec3 c3=aG.x<0.?vec3(.85,.88,1.):(aG.y<.22?core:arm);',
    ' if(aS.w>.16&&aS.w<.2&&aG.x>=0.&&aG.y>.3)c3=vec3(1.,.45,.7);',      // กลุ่มก๊าซสีชมพูที่ดาวเกิดใหม่
    ' vec3 c=mix(c0,c1,smoothstep(2.4,3.,t));c=mix(c,c2,smoothstep(4.6,5.6,t));c=mix(c,c3,smoothstep(7.6,9.2,t));',
    ' float al=mix(.9,.5,smoothstep(2.4,3.,t));al=mix(al,.28,smoothstep(4.8,6.,t));al=mix(al,aG.x<0.?.7:.42,smoothstep(7.6,9.,t));',
    // ดาวดวงแรกวาบขึ้น
    ' float ig=6.3+fract(aS.w*37.)*1.7,fl=aS.w<.05?exp(-pow((t-ig)/.22,2.))*3.:0.;',
    ' float sz=(.8+aS.y*1.1)*(1.+fl)*(t<1.?2.2:1.)*(aG.x>=0.&&aG.y<.2?1.3:1.)*(1.+glow*1.5);',
    ' gl_PointSize=clamp(sz*uPx*uDPR*1.7/max(w,.25),1.,40.);',
    ' vC=c*(1.+fl*1.6+glow);vA=al*uGain*clamp(1.6/w,0.,1.3)*(aS.x<.012?3.:1.)*(1.+3.*(1.-smoothstep(1.8,3.,t)))*(1.-smoothstep(11.9,12.7,t));',
    '}'
  ].join('\n');

  var FS_PTS = [
    'precision mediump float;varying vec3 vC;varying float vA;',
    'void main(){vec2 d=gl_PointCoord-.5;float r=dot(d,d)*4.;if(r>1.)discard;',
    ' float g=exp(-r*4.)+.25*exp(-r*1.2);gl_FragColor=vec4(vC*g*vA,1.);}'
  ].join('\n');

  var VS_BG = 'attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}';
  var FS_BG = [
    'precision mediump float;',
    'uniform vec2 uRes;uniform float uT,uNow;uniform vec3 uWell;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);',
    ' return mix(mix(h(i),h(i+vec2(1,0)),f.x),mix(h(i+vec2(0,1)),h(i+vec2(1,1)),f.x),f.y);}',
    'float fbm(vec2 p){float s=0.,a=.5;for(int i=0;i<4;i++){s+=a*n(p);p=p*2.03+vec2(1.7,9.2);a*=.5;}return s;}',
    // ── บทโลก 66 ล้านปีก่อน: ดาวเคราะห์น้อยชนยูคาทาน (ชน ณ เวลาในฉาก 15.0) ──
    'vec3 earth(vec2 uv,float t){',
    ' vec3 c=vec3(0.);vec2 g=floor(uv*170.);c+=vec3(.8,.85,1.)*step(.996,h(g))*h(g+3.)*.9;',
    ' float R=.3+.05*smoothstep(12.4,19.,t),ti=15.;vec2 ec=vec2(-.04,-.06),q=(uv-ec)/R;float r2=dot(q,q);',
    ' vec3 L=normalize(vec3(-.55,.35,.75)),I=normalize(vec3(.32,.22,.92));vec2 ip=ec+I.xy*R;',
    ' if(r2<1.){float z=sqrt(1.-r2);vec3 nr=vec3(q,z);float ro=t*.04;',
    '  vec3 tn=vec3(cos(ro)*nr.x+sin(ro)*nr.z,nr.y,-sin(ro)*nr.x+cos(ro)*nr.z);vec2 sp=vec2(atan(tn.x,tn.z),asin(tn.y));',
    '  float land=fbm(sp*vec2(1.6,2.2)+vec2(2.,5.))+.35*fbm(sp*5.);',
    '  vec3 col=mix(mix(vec3(.02,.08,.22),vec3(.05,.2,.42),z),mix(vec3(.16,.32,.12),vec3(.45,.38,.22),fbm(sp*6.)),smoothstep(.62,.66,land));',
    '  col=mix(col,vec3(.95),smoothstep(.55,.8,fbm(sp*vec2(3.,4.)+vec2(t*.03,0.)))*.7);',
    '  float dif=max(dot(nr,L),0.);col*=.08+1.1*dif;',
    '  float ta=t-ti;if(ta>0.){float an=acos(clamp(dot(nr,I),-1.,1.));',
    '   float fire=exp(-an*an/(.02+ta*.05))*exp(-ta*.5);',                         // ลูกไฟ
    '   float ring=exp(-pow((an-ta*.55)/.05,2.))*exp(-ta*.35);',                    // คลื่นกระแทกแผ่รอบโลก
    '   float dust=(1.-smoothstep(ta*.6-.2,ta*.6+.1,an))*smoothstep(0.,1.5,ta)*(1.-smoothstep(18.6,20.,t));',
    '   col=mix(col,vec3(.18,.12,.08)*(.25+.6*dif),dust*.85);col+=vec3(1.,.55,.2)*fire*3.+vec3(1.,.65,.35)*ring*1.4;}',
    '  c=col;}',
    ' float rr=sqrt(r2);c+=vec3(.25,.5,1.)*exp(-pow((rr-1.)/.05,2.))*.6;',          // ชั้นบรรยากาศเรืองฟ้า
    ' if(t>12.6&&t<ti+.05){float k=pow(clamp((t-12.6)/(ti-12.6),0.,1.),1.6);vec2 a0=vec2(.95,.75),ap=mix(a0,ip,k),dr=normalize(ip-a0);',
    '  vec2 dv=uv-ap;float al=dot(dv,-dr),pp=length(dv+dr*al);',
    '  float tail=al>0.?exp(-pp*pp/(.00004+al*.0006))*exp(-al*4.)*(.6+1.4*k):0.;',
    '  c+=vec3(1.,.85,.6)*(.00022/(dot(dv,dv)+.00008)+tail*.8)+vec3(1.,.6,.3)*smoothstep(.85,1.,k)*.002/(dot(dv,dv)+.0003);}',
    ' if(t>ti)c+=vec3(1.,.9,.75)*exp(-(t-ti)*2.5)*1.4*exp(-length(uv-ip)*1.5);',      // แสงวาบตอนชน
    ' return c;}',
    'void main(){',
    ' vec2 uv=(gl_FragCoord.xy-.5*uRes)/min(uRes.x,uRes.y);float d=length(uv),t=uT;vec3 c=vec3(0.);',
    ' if(t<0.){float p=1.+.35*sin(uNow*3.8);c=vec3(1.,.93,.8)*(.012*p/(d*d+.0004)+.05*p*exp(-d*14.));',
    '  gl_FragColor=vec4(c,1.);return;}',
    // แสงวาบตอนระเบิด
    ' float fl=max(0.,1.-t/1.3);float fr=.15+t*1.6;c+=vec3(1.,.96,.9)*fl*exp(-d*d/(fr*fr))*1.6;',
    ' c+=vec3(1.,.8,.6)*fl*fl*.6;',
    // ซุปพลาสมาร้อน (เดือดเป็นคลื่น)
    ' float pw=smoothstep(1.4,2.8,t)*(1.-smoothstep(4.7,6.3,t));',
    ' if(pw>0.){float q=fbm(uv*3.+vec2(t*.4,-t*.3));float q2=fbm(uv*7.-q*2.+t*.6);',
    '  c+=mix(vec3(.55,.12,.04),vec3(1.,.5,.18),q2)*pw*(.35+.35*q);}',
    // แสงแรกของจักรวาล: ลายจุดฟ้า-ส้มเหมือนแผนที่แสงพื้นหลังจักรวาล แล้วจางหายเป็นความมืด
    ' float cw=smoothstep(4.6,5.2,t)*(1.-smoothstep(5.6,6.8,t));',
    ' if(cw>0.){float m=fbm(uv*6.+3.1)+.5*fbm(uv*15.)-.75;c+=mix(vec3(.12,.25,.65),vec3(.9,.5,.18),smoothstep(-.25,.25,m))*cw*.3;}',
    // เนบิวลาจางรอบกาแล็กซี
    ' float nw=smoothstep(8.,10.5,t);',
    ' if(nw>0.){vec2 u2=uv*1.6+vec2(t*.02,0.);float a=fbm(u2*2.),b=fbm(u2*3.3+a*1.5+4.);',
    '  c+=(vec3(.16,.22,.5)*a*a+vec3(.42,.1,.32)*b*b*b)*nw*.55;}',
    ' float eb=smoothstep(12.,12.9,t);if(eb>0.)c=mix(c,earth(uv,t),eb);',
    ' c*=1.-.35*smoothstep(.5,1.2,d);',
    // หลุมดำใต้นิ้ว: แกนมืด + วงแสงของจานรอบหลุมดำ
    ' if(uWell.z>0.){vec2 wp=uWell.xy*.5*uRes/min(uRes.x,uRes.y);float wd=length(uv-wp);',
    '  c*=1.-uWell.z*smoothstep(.07,.02,wd);',
    '  c+=vec3(1.,.72,.42)*uWell.z*(exp(-pow((wd-.075)/.012,2.))*1.2+.25*exp(-wd*9.));}',
    ' gl_FragColor=vec4(c,1.);}'
  ].join('\n');

  function compile(gl, type, src) {
    var s = gl.createShader(type); gl.shaderSource(s, src); gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) { var e = gl.getShaderInfoLog(s); gl.deleteShader(s); throw new Error(e); }
    return s;
  }
  function program(gl, vs, fs) {
    var p = gl.createProgram();
    gl.attachShader(p, compile(gl, gl.VERTEX_SHADER, vs)); gl.attachShader(p, compile(gl, gl.FRAGMENT_SHADER, fs));
    gl.linkProgram(p);
    if (!gl.getProgramParameter(p, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(p));
    return p;
  }
  function norm(v) { var l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; }
  function cross(a, b) { return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }

  window.KD_BigBangGL = function (cv) {
    var gl = null;
    try { gl = cv.getContext('webgl', { alpha: false, antialias: false, depth: false, stencil: false, premultipliedAlpha: false }); } catch (e) { gl = null; }
    if (!gl) return null;
    var P, B, U = {}, UB = {}, buf, sBuf, gBuf, N = 0, W = 1, H = 1, DPR = 1, lost = false;
    try {
      P = program(gl, VS_PTS, FS_PTS); B = program(gl, VS_BG, FS_BG);
    } catch (e) { return null; }
    ['uT', 'uAsp', 'uCam', 'uYaw', 'uPitch', 'uDPR', 'uPx', 'uGain', 'uShake', 'uWell'].forEach(function (k) { U[k] = gl.getUniformLocation(P, k); });
    U.uGC = gl.getUniformLocation(P, 'uGC'); U.uGU = gl.getUniformLocation(P, 'uGU'); U.uGV = gl.getUniformLocation(P, 'uGV');
    U.uWave = gl.getUniformLocation(P, 'uWave');
    ['uRes', 'uT', 'uNow', 'uWell'].forEach(function (k) { UB[k] = gl.getUniformLocation(B, k); });
    var aS = gl.getAttribLocation(P, 'aS'), aG = gl.getAttribLocation(P, 'aG'), aB = gl.getAttribLocation(B, 'a');
    buf = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, buf);
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
    sBuf = gl.createBuffer(); gBuf = gl.createBuffer();
    var GC = new Float32Array(NG * 4), GU = new Float32Array(NG * 4), GV = new Float32Array(NG * 4);
    cv.addEventListener('webglcontextlost', function (e) { e.preventDefault(); lost = true; });

    function seed(n) {
      N = n;
      for (var g = 0; g < NG; g++) {                 // กาแล็กซี: ตำแหน่ง ขนาด และระนาบของจานในอวกาศ 3 มิติ
        // กาแล็กซีหลักอยู่กลางเส้นทางของกล้องเสมอ · บริวารอยู่รอบๆ และอยู่ข้างหลัง ไม่ขวางกล้อง ไม่หันสันเข้ากล้อง
        var a = g / NG * Math.PI * 2 + Math.random() * .7, d = g === 0 ? 0 : .95 + Math.random() * .6;
        var c = g === 0 ? [0, 0, 0] : [Math.cos(a) * d * 1.25, Math.sin(a) * d * .7, .35 + Math.random() * .9];
        var nz = (.5 + Math.random() * .5) * (Math.random() < .5 ? -1 : 1);
        var nrm = g === 0 ? norm([.25, -.55, 1]) : norm([Math.random() - .5, Math.random() - .5, nz]);
        var u = norm(cross(nrm, Math.abs(nrm[1]) < .9 ? [0, 1, 0] : [1, 0, 0])), v = cross(nrm, u);
        var spin = (Math.random() < .5 ? -1 : 1) * (.22 + Math.random() * .3);
        GC.set([c[0], c[1], c[2], g === 0 ? .95 : .22 + Math.random() * .2], g * 4);
        GU.set([u[0], u[1], u[2], spin], g * 4); GV.set([v[0], v[1], v[2], Math.random() * 6.283], g * 4);
      }
      var S = new Float32Array(N * 4), G = new Float32Array(N * 4);
      for (var i = 0; i < N; i++) {
        S[i * 4] = Math.random(); S[i * 4 + 1] = Math.random(); S[i * 4 + 2] = Math.random(); S[i * 4 + 3] = Math.random();
        var r = Math.random(), gi = r < .12 ? -1 : r < .6 ? 0 : 1 + Math.floor(Math.random() * (NG - 1));
        var arms = gi === 0 ? 2 : (Math.random() < .5 ? 2 : 3), gr = Math.pow(Math.random(), gi === 0 ? 1.15 : 1.5);
        G[i * 4] = gi; G[i * 4 + 1] = gr; G[i * 4 + 2] = Math.floor(Math.random() * arms) / arms;
        G[i * 4 + 3] = (Math.random() + Math.random() - 1) * .75 * (1.3 - gr);   // แขนฟุ้งแบบระฆัง ไม่ใช่เส้นเดียว
      }
      gl.bindBuffer(gl.ARRAY_BUFFER, sBuf); gl.bufferData(gl.ARRAY_BUFFER, S, gl.STATIC_DRAW);
      gl.bindBuffer(gl.ARRAY_BUFFER, gBuf); gl.bufferData(gl.ARRAY_BUFFER, G, gl.STATIC_DRAW);
    }

    return {
      kind: 'webgl',
      lost: function () { return lost || gl.isContextLost(); },
      resize: function (w, h, dpr) {
        W = w; H = h; DPR = dpr; cv.width = Math.round(w * dpr); cv.height = Math.round(h * dpr);
        cv.style.width = w + 'px'; cv.style.height = h + 'px'; gl.viewport(0, 0, cv.width, cv.height);
      },
      // จำนวนอนุภาคตามขนาดจอ: มือถือราว 9 หมื่น จอใหญ่ราว 2.6 แสน
      count: function (w, h) { return Math.round(Math.min(260000, Math.max(70000, w * h * .3))); },
      seed: seed,
      draw: function (o) {
        if (lost) return;
        var t = o.t;
        gl.disable(gl.BLEND);
        gl.useProgram(B);
        gl.bindBuffer(gl.ARRAY_BUFFER, buf); gl.enableVertexAttribArray(aB); gl.vertexAttribPointer(aB, 2, gl.FLOAT, false, 0, 0);
        gl.uniform2f(UB.uRes, cv.width, cv.height); gl.uniform1f(UB.uT, t); gl.uniform1f(UB.uNow, o.now / 1000);
        gl.uniform3f(UB.uWell, o.well[0], o.well[1], o.well[2]);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        gl.disableVertexAttribArray(aB);
        if (t < 0 || !N) return;
        gl.enable(gl.BLEND); gl.blendFunc(gl.ONE, gl.ONE);           // แสงบวกกัน — จุดซ้อนกันยิ่งสว่าง
        gl.useProgram(P);
        gl.bindBuffer(gl.ARRAY_BUFFER, sBuf); gl.enableVertexAttribArray(aS); gl.vertexAttribPointer(aS, 4, gl.FLOAT, false, 0, 0);
        gl.bindBuffer(gl.ARRAY_BUFFER, gBuf); gl.enableVertexAttribArray(aG); gl.vertexAttribPointer(aG, 4, gl.FLOAT, false, 0, 0);
        // กล้อง: ถอยออกช่วงแรกให้เห็นทั้งระเบิด → ค่อยเข้าใกล้ → ตอนท้ายบินทะลุกาแล็กซีหลัก
        var fly = Math.max(0, t - 11.2), cam = 2.7 - .06 * Math.min(t, 8) - .08 * Math.max(0, Math.min(t, 11.2) - 8) - fly * fly * .55;
        gl.uniform1f(U.uT, t); gl.uniform1f(U.uAsp, W / H); gl.uniform1f(U.uCam, cam);
        gl.uniform1f(U.uYaw, .035 * t + o.yaw); gl.uniform1f(U.uPitch, -.12 + .012 * t + o.pitch);
        gl.uniform1f(U.uDPR, DPR); gl.uniform1f(U.uPx, Math.min(W, H) / 700 + .55);
        // ความสว่างต่อจุดแปรผกผันกับความหนาแน่น — จุดหลักแสนซ้อนกันแล้วไม่ขาวโพลน
        gl.uniform1f(U.uGain, Math.min(1, 29000 / N));
        gl.uniform2f(U.uShake, o.shake[0] / W * 2, -o.shake[1] / H * 2);
        gl.uniform3f(U.uWell, o.well[0], o.well[1], o.well[2]);
        gl.uniform4fv(U.uGC, GC); gl.uniform4fv(U.uGU, GU); gl.uniform4fv(U.uGV, GV);
        gl.uniform4fv(U.uWave, o.waves);
        gl.drawArrays(gl.POINTS, 0, N);
        gl.disableVertexAttribArray(aS); gl.disableVertexAttribArray(aG);
      }
    };
  };
})();
