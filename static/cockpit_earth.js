/* ฉากเปิดของหน้า Universe — มองออกจากหน้าต่างยาน เห็นโลกตอนกลางคืน แสงไฟเมืองสีส้มทั่วอเมริกาเหนือ
 * วาดด้วย WebGL จากภาพ NASA Black Marble ที่มีอยู่แล้ว (static/earth/lights.jpg · day.jpg · clouds.jpg)
 * ไม่มีไลบรารีเพิ่ม · ถ้าเครื่องไม่มี WebGL จะเหลือพื้นหลังไล่สีแทน · เคารพ prefers-reduced-motion
 */
(function () {
  var canvas = document.getElementById('cockpit-earth');
  if (!canvas) return;
  var gl = canvas.getContext('webgl', { antialias: false, alpha: false, premultipliedAlpha: false });
  if (!gl) { canvas.parentNode.classList.add('no-webgl'); return; }

  var still = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  var VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;',
    'uniform vec2 res;uniform float t;uniform sampler2D lights,day,clouds;uniform float ready;',
    'const float PI=3.14159265;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'mat3 rx(float a){float c=cos(a),s=sin(a);return mat3(1.,0.,0.,0.,c,s,0.,-s,c);}',
    'mat3 ry(float a){float c=cos(a),s=sin(a);return mat3(c,0.,-s,0.,1.,0.,s,0.,c);}',
    'void main(){',
    '  vec2 uv=(gl_FragCoord.xy-.5*res)/res.y;',          // y ขึ้นบน · หน่วยเท่ากับความสูงจอ
    '  float aspect=res.x/res.y;',
    '  float R=max(.82,aspect*.95);',                       // จอกว้าง → โลกใหญ่ขึ้น · จอแนวตั้งเห็นทั้งทวีป
    '  vec2 c=vec2(0.,-R-.02+.30);',                         // ขอบฟ้าอยู่ราวหนึ่งในสามจากด้านบน
    '  vec2 q=(uv-c)/R;float d=length(q);',
    '  vec3 col=vec3(0.);',
    // ดาวพื้นหลัง
    '  vec2 g=floor(gl_FragCoord.xy/2.);float s=h(g);',
    '  if(s>.996){float tw=.6+.4*sin(t*2.+s*90.);col+=vec3(.75,.8,1.)*tw*(s-.996)*220.;}',
    '  col+=vec3(.04,.03,.09)*(1.-uv.y);',                   // ท้องฟ้าม่วงเข้มจางๆ
    '  if(d<1.){',
    '    float z=sqrt(1.-d*d);vec3 n=vec3(q.x,q.y,z);',
    '    float pitch=asin(clamp(-c.y/R,-1.,1.))-.70;',          // ล็อกกลางจอที่ละติจูด 40°N ทุกขนาดจอ
    '    n=ry(-1.66+.10*sin(t*.03))*rx(pitch)*n;',           // ลองจิจูด −95° (กลางสหรัฐฯ) แล้วส่ายช้าๆ
    '    float lat=asin(clamp(n.y,-1.,1.)),lon=atan(n.x,n.z);',
    '    vec2 tc=vec2(lon/(2.*PI)+.5,.5-lat/PI);',
    '    vec2 px=vec2(1./2048.,1./1024.);',
    '    float L=texture2D(lights,tc).r;',                                   // แสงเมืองคมๆ ตามภาพจริง
    '    float B=(texture2D(lights,tc+px*vec2(3.,0.)).r+texture2D(lights,tc-px*vec2(3.,0.)).r+texture2D(lights,tc+px*vec2(0.,2.)).r+texture2D(lights,tc-px*vec2(0.,2.)).r)*.25;', // แสงเรืองจางๆ รอบเมือง
    '    float cl=texture2D(clouds,tc+vec2(t*.0006,0.)).r;',
    '    vec3 land=texture2D(day,tc).rgb;',
    '    vec3 base=land*vec3(.022,.03,.065)+vec3(.003,.006,.02);', // ด้านกลางคืน แสงจันทร์สีน้ำเงินจางๆ
    '    vec3 city=vec3(1.,.48,.10)*pow(L,1.35)*2.4+vec3(1.,.78,.42)*pow(L,4.)*1.4+vec3(1.,.42,.1)*pow(B,1.5)*.45;',
    '    city*=1.-.55*cl;',                                     // เมฆบังแสงเมือง
    '    vec3 surf=base+city*ready+vec3(.07,.08,.15)*cl*.35;',
    '    float limb=pow(1.-z,2.6);',
    '    surf+=vec3(.25,.38,1.)*limb*.7+vec3(.55,.35,1.)*pow(1.-z,7.)*.8;', // บรรยากาศฟ้าอมม่วงที่ขอบโลก
    '    col=mix(col,surf,smoothstep(1.,.995,d));',
    '  }',
    '  float halo=exp(-max(d-1.,0.)*28.)*step(1.,d);',         // แสงบรรยากาศเหนือขอบฟ้า
    '  col+=vec3(.25,.45,1.)*halo*.85+vec3(.6,.4,1.)*exp(-max(d-1.,0.)*90.)*step(1.,d)*.5;',
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
  var t0 = performance.now();
  function frame(now) {
    if (visible || still) {
      var t = still ? 20 : (now - t0) / 1000;
      if (pending === 0) ready = Math.min(1, ready + 0.02);      // แสงเมืองค่อยๆ สว่างขึ้นเมื่อภาพโหลดเสร็จ
      gl.uniform2f(U.res, canvas.width, canvas.height);
      gl.uniform1f(U.t, t);
      gl.uniform1f(U.ready, ready);
      gl.drawArrays(gl.TRIANGLES, 0, 3);
    }
    if (!still || pending > 0 || ready < 1) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);
})();
