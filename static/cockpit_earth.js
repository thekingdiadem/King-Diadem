/* ฉากเปิดของหน้า Universe — ภาพสดจากกล้องดาวเทียม เห็นโลกตอนกลางคืน แสงไฟเมืองสีส้ม เริ่มที่อเมริกาเหนือแล้วเคลื่อนไปตลอดเวลา
 * วาดด้วย WebGL จากภาพ NASA Black Marble ที่มีอยู่แล้ว (static/earth/lights.jpg · day.jpg · clouds.jpg)
 * ไม่มีไลบรารีเพิ่ม · ถ้าเครื่องไม่มี WebGL จะเหลือพื้นหลังไล่สีแทน · เคารพ prefers-reduced-motion
 */
(function () {
  var canvas = document.getElementById('cockpit-earth');
  if (!canvas) return;
  var gl = canvas.getContext('webgl', { antialias: false, alpha: false, premultipliedAlpha: false });
  if (!gl) { canvas.parentNode.classList.add('no-webgl'); return; }

  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ดาวเทียมเคลื่อนไปทางตะวันออกตลอดเวลา — รอบโลกใน ~12 นาที (เร็วกว่า ISS จริงราว 8 เท่า ให้เห็นการเคลื่อนไหว)
  var LON0 = -95, RATE = 2 * Math.PI / 720;
  window.KD_satLon = function (t) { var l = LON0 + (t * RATE) * 180 / Math.PI; return ((l + 540) % 360) - 180; };
  var VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;',
    'uniform vec2 res;uniform float t;uniform sampler2D lights,day,clouds;uniform float ready;',
    'const float PI=3.14159265;',
    'const float LON0=' + LON0.toFixed(2) + ';const float RATE=' + RATE.toFixed(6) + ';',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+1.),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<5;i++){v+=a*vn(p);p*=2.03;a*=.5;}return v;}',
    'mat3 rx(float a){float c=cos(a),s=sin(a);return mat3(1.,0.,0.,0.,c,s,0.,-s,c);}',
    'mat3 ry(float a){float c=cos(a),s=sin(a);return mat3(c,0.,-s,0.,1.,0.,s,0.,c);}',
    'void main(){',
    '  vec2 uv=(gl_FragCoord.xy-.5*res)/res.y;',          // y ขึ้นบน · หน่วยเท่ากับความสูงจอ
    '  float aspect=res.x/res.y;',
    '  float R=max(.82,aspect*.95);',                       // จอกว้าง → โลกใหญ่ขึ้น · จอแนวตั้งเห็นทั้งทวีป
    '  vec2 c=vec2(0.,-R-.02+.30);',                         // ขอบฟ้าอยู่ราวหนึ่งในสามจากด้านบน
    '  vec2 q=(uv-c)/R;float d=length(q);',
    '  vec3 col=vec3(.004,.005,.012);',                                   // อวกาศจริงเกือบดำสนิท
    // ดาวพื้นหลัง — หนาแน่นขึ้นในแถบทางช้างเผือก
    '  vec2 g=floor(gl_FragCoord.xy/2.);float s=h(g);float th=.9975;',
    '  if(s>th){float tw=.6+.4*sin(t*2.+s*90.);col+=vec3(.75,.8,1.)*tw*(s-th)*90.;}',
    // ดวงจันทร์
    '  vec2 mc=vec2(aspect<.8?-.10:.30*min(aspect,1.6),.40);float mr=.022;vec2 mq=(uv-mc)/mr;float md=length(mq);',
    '  if(md<1.){float mz=sqrt(1.-md*md);float lit=clamp(dot(normalize(vec3(mq,mz)),normalize(vec3(-.5,.3,.8))),0.,1.);',
    '    float cr=fbm(mq*3.5+5.);vec3 mcol=vec3(.86,.86,.9)*(.55+.45*cr)*(.25+.85*lit);col=mix(col,mcol,smoothstep(1.,.97,md));}',
    '  col+=vec3(.6,.65,.9)*exp(-max(md-1.,0.)*7.)*step(1.,md)*.18;',      // แสงนวลรอบดวงจันทร์
    '  if(d<1.){',
    '    float z=sqrt(1.-d*d);vec3 n=vec3(q.x,q.y,z);',
    '    float pitch=asin(clamp(-c.y/R,-1.,1.))-.70;',          // ล็อกกลางจอที่ละติจูด 40°N ทุกขนาดจอ
    '    n=ry(radians(LON0)+t*RATE)*rx(pitch)*n;',           // เริ่มที่ลองจิจูด −95° (กลางสหรัฐฯ) แล้วเคลื่อนไปทางตะวันออกตลอดเวลา
    '    float lat=asin(clamp(n.y,-1.,1.)),lon=atan(n.x,n.z);',
    '    vec2 tc=vec2(lon/(2.*PI)+.5,.5-lat/PI);',
    '    vec2 px=vec2(1./2048.,1./1024.);',
    '    float L=texture2D(lights,tc).r;',                                   // แสงเมืองคมๆ ตามภาพจริง
    '    float B=(texture2D(lights,tc+px*vec2(3.,0.)).r+texture2D(lights,tc-px*vec2(3.,0.)).r+texture2D(lights,tc+px*vec2(0.,2.)).r+texture2D(lights,tc-px*vec2(0.,2.)).r)*.25;', // แสงเรืองจางๆ รอบเมือง
    '    float cl=texture2D(clouds,tc+vec2(t*.0006,0.)).r;',
    '    vec3 land=texture2D(day,tc).rgb;',
    '    vec3 base=land*vec3(.018,.026,.05)+vec3(.002,.005,.014);',       // ด้านกลางคืนใต้แสงจันทร์ เห็นทะเลสีฟ้า
    '    vec3 city=vec3(1.,.48,.10)*pow(L,1.35)*2.4+vec3(1.,.78,.42)*pow(L,4.)*1.4+vec3(1.,.42,.1)*pow(B,1.5)*.45;',
    '    city*=1.-.55*cl;',                                     // เมฆบังแสงเมือง
    '    vec3 surf=base+city*ready+vec3(.55,.62,.85)*pow(cl,1.4)*.16;',   // เมฆขาวอมฟ้าต้องแสงจันทร์
    '    float limb=pow(1.-z,2.6);',
    '    surf+=vec3(.18,.35,1.)*limb*.35+vec3(.35,.55,1.)*pow(1.-z,9.)*.6;', // บรรยากาศฟ้าอมม่วงที่ขอบโลก
    '    col=mix(col,surf,smoothstep(1.,.995,d));',
    '  }',
    '  float halo=exp(-max(d-1.,0.)*28.)*step(1.,d);',         // แสงบรรยากาศเหนือขอบฟ้า
    '  col+=vec3(.15,.35,1.)*halo*.45+vec3(.35,.6,1.)*exp(-max(d-1.,0.)*160.)*step(1.,d)*.55;',
    '  col+=vec3(.20,.85,.42)*exp(-abs(d-1.007)*500.)*.5;',               // airglow สีเขียวบางๆ เหนือขอบฟ้า แบบภาพถ่ายจาก ISS
    '  col*=1.-.35*pow(length(uv*vec2(.9,1.1)),2.2);',                     // vignette ของเลนส์
    '  col+=(h(gl_FragCoord.xy+fract(t)*91.)-.5)*.018;',                   // เกรนเซนเซอร์กล้องจางๆ
    '  col=1.-exp(-col*1.35);',                                 // tone map
    '  gl_FragColor=vec4(pow(col,vec3(.92)),1.);',
    '}'
  ].join('\n');

  function sh(type, src) {
    var o = gl.createShader(type); gl.shaderSource(o, src); gl.compileShader(o);
    if (!gl.getShaderParameter(o, gl.COMPILE_STATUS)) throw new Error(gl.getShaderInfoLog(o));
    return o;
  }
  var prog;
  try {
    prog = gl.createProgram();
    gl.attachShader(prog, sh(gl.VERTEX_SHADER, VS));
    gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, FS));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  } catch (e) { canvas.parentNode.classList.add('no-webgl'); return; }
  gl.useProgram(prog);

  var buf = gl.createBuffer();
  gl.bindBuffer(gl.ARRAY_BUFFER, buf);
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  var U = {};
  ['res', 't', 'lights', 'day', 'clouds', 'ready'].forEach(function (k) { U[k] = gl.getUniformLocation(prog, k); });

  var base = (document.currentScript && document.currentScript.src || '/static/cockpit_earth.js').replace(/cockpit_earth\.js.*$/, '');
  var pending = 3, ready = 0;
  function tex(unit, name, uniform) {
    var tx = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, tx);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([0, 0, 0, 255]));
    gl.uniform1i(U[uniform], unit);
    var img = new Image();
    img.onload = function () {
      gl.activeTexture(gl.TEXTURE0 + unit);
      gl.bindTexture(gl.TEXTURE_2D, tx);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
      // ภาพ 2048×1024 ไม่ใช่ power-of-two ทั้งสองด้านในบางเครื่อง — ใช้ CLAMP + LINEAR เพื่อให้ WebGL1 ยอม
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      if (--pending === 0) { canvas.parentNode.classList.add('lit'); }
    };
    img.src = base + 'earth/' + name;
  }
  tex(0, 'lights.jpg', 'lights');
  tex(1, 'day.jpg', 'day');
  tex(2, 'clouds.jpg', 'clouds');

  function size() {
    var dpr = Math.min(window.devicePixelRatio || 1, 1.5);   // คมพอ แต่ไม่หนักมือถือ
    var w = canvas.clientWidth, hgt = canvas.clientHeight;
    canvas.width = Math.max(1, Math.round(w * dpr));
    canvas.height = Math.max(1, Math.round(hgt * dpr));
    gl.viewport(0, 0, canvas.width, canvas.height);
  }
  size();
  window.addEventListener('resize', size);

  var visible = true;
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; }).observe(canvas);
  }
  var hudPos = document.getElementById('sat-pos'), hudUtc = document.getElementById('sat-utc'), lastHud = 0;
  var t0 = performance.now();
  function frame(now) {
    if (visible || still) {
      var t = still ? 20 : (now - t0) / 1000;
      if (pending === 0) ready = Math.min(1, ready + 0.02);      // แสงเมืองค่อยๆ สว่างขึ้นเมื่อภาพโหลดเสร็จ
      gl.uniform2f(U.res, canvas.width, canvas.height);
      gl.uniform1f(U.t, t);
      gl.uniform1f(U.ready, ready);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
      if (hudPos && (!lastHud || now - lastHud > 250)) {          // พิกัดบนจอตรงกับภาพจริง (กลางจอ)
        lastHud = now;
        var lo = window.KD_satLon(t);
        hudPos.textContent = 'LAT 40.0°N · LON ' + Math.abs(lo).toFixed(1) + '°' + (lo < 0 ? 'W' : 'E');
        var d = new Date();
        hudUtc.textContent = 'UTC ' + d.toISOString().slice(11, 19);
      }
    }
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
