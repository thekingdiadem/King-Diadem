/* ฉากเปิดของหน้า Universe — โลกตอนกลางคืนจากอวกาศ แสงไฟทุกเมือง ทะเลสะท้อนแสงจันทร์ ซูมจากทั้งใบลงไปจนเห็นเมือง
 *
 * · กล้องจริงแบบมีมุมมอง (perspective): ยิ่งซูมลง กล้องยิ่งต่ำและเอียงเห็นขอบฟ้าโค้ง — ไม่ใช่ภาพแบนขยาย
 * · ระดับซูมต่อเนื่องค่าเดียว L: 0 = ทั้งโลก · 1 = วงโคจร · 2–4.4 = ลงใกล้ขึ้นทีละ 2 เท่า
 *   ซูมเลย 4.4 → แผนที่เมืองกลางคืน 3 มิติ (static/city_map.js) รับช่วงต่อที่ตำแหน่งเดิม · ซูมออกกลับมาเป็นโลก
 * · นิ้ว: ลากเลื่อน (ปล่อยแล้วไหลต่อ) · ถ่าง/บีบซูมเข้าหาจุดที่นิ้วอยู่ · แตะสองครั้งบินไปจุดนั้น
 *   เมาส์: ลาก · ล้อเลื่อนซูมเมื่อซูมเข้าไปแล้ว (หรือกด Ctrl / ถ่างบนทัชแพด) · ดับเบิลคลิก · คีย์บอร์ด: ลูกศร + −
 * · ชื่อเมืองเป็นชั้นตามความสำคัญ: เมืองหลวง → ศูนย์กลางจังหวัด/รัฐ → เมืองใหญ่ไปเล็ก · จังหวัดไทยแสดงชื่อไทย
 * · ภาพ NASA 2K โหลดก่อน แล้วสลับเป็น 4K เมื่อเครื่องรองรับ (ไม่โหลด 4K ถ้าเปิดโหมดประหยัดเน็ต) — scripts/build_earth_textures.py
 * · ลื่นบนมือถือ: ปรับความละเอียดการวาดตามความเร็วเครื่อง · คลื่นทะเลคำนวณเฉพาะจุดที่เป็นน้ำ · ชื่อเมืองวาดใหม่เมื่อกล้องขยับเท่านั้น
 * · ลดการเคลื่อนไหว (ตั้งในเครื่อง หรือปุ่มในหน้า → html.kd-calm): โลกหยุด ดาวไม่กะพริบ ไม่ไหลต่อ เปลี่ยนมุมทันที
 * · โหมดกลางวัน (ปุ่ม "กลางวัน" → html.kd-day): ภาพดาวเทียม NASA สีจริง เมฆขาว แดดสะท้อนทะเล — ค่อยๆ เปลี่ยนจากกลางคืน
 * วาดด้วย WebGL ไม่มีไลบรารีเพิ่ม · ไม่มี WebGL = พื้นหลังไล่สีแทน
 */
(function () {
  var canvas = document.getElementById('cockpit-earth');
  if (!canvas) return;
  var wrap = canvas.parentNode;
  var gl = canvas.getContext('webgl', { antialias: false, alpha: false, premultipliedAlpha: false });
  if (!gl) { wrap.classList.add('no-webgl'); return; }

  var MQ = window.matchMedia ? window.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };
  function calm() { return MQ.matches || document.documentElement.classList.contains('kd-calm'); }

  var PI = Math.PI, RAD = PI / 180, LMAX = 4.4;   // ลึกกว่านี้ภาพ NASA (~10 กม./พิกเซล) เบลอเป็นก้อน
  // lon/lat = จุดกลางจอบนผิวโลก · L = ระดับซูม · ค่า t* คือเป้าหมายที่ค่อยๆ เลื่อนไปหา · v* = ความเร็วที่ไหลต่อหลังปล่อยนิ้ว
  // zoom/mag เก็บไว้ให้โค้ดเดิมอ่านได้: zoom 0–1 (ทั้งโลก → วงโคจร) · mag = 2^(L−1)
  var S = { lon: -95, lat: 40, L: 1, tlon: -95, tlat: 40, tL: 1, vlon: 0, vlat: 0, zoom: 1, mag: 1, tzoom: 1, tmag: 1 };
  var DRIFT = 0.5;                                  // องศาต่อวินาที — รอบโลกราว 12 นาที
  window.KD_satLon = function () { return ((S.lon % 360) + 540) % 360 - 180; };
  function clamp(x, a, b) { return x < a ? a : x > b ? b : x; }
  function smooth(x) { x = clamp(x, 0, 1); return x * x * (3 - 2 * x); }
  function sync() {
    S.zoom = Math.min(1, S.L); S.mag = Math.pow(2, Math.max(0, S.L - 1));
    S.tzoom = Math.min(1, S.tL); S.tmag = Math.pow(2, Math.max(0, S.tL - 1));
  }

  // ── กล้อง: ระยะเหนือผิวโลก D (หน่วยรัศมีโลก) และมุมเอียงจากแนวดิ่ง ─────────────────────────────
  var FOV = 40 * RAD, F = .5 / Math.tan(FOV / 2);
  function camera(L, aspect) {
    // ทั้งโลก: ถอยจนลูกโลกพอดีจอ (จอแนวตั้งต้องถอยไกลกว่า)
    var half = Math.min(FOV / 2, Math.atan(Math.tan(FOV / 2) * aspect)) * .86;
    var Dg = 1 / Math.sin(half) - 1, Do = .62;
    var D, tilt;
    if (L <= 1) { var z = smooth(L); D = Math.exp(Math.log(Dg) + (Math.log(Do) - Math.log(Dg)) * z); tilt = 1.02 * z; }
    else { D = Do / Math.pow(2, L - 1); tilt = 1.02 - .30 * smooth((L - 1) / 4); }   // ลงใกล้ = เอียงน้อยลง เห็นพื้นชัดขึ้น
    return { D: D, tilt: tilt, st: Math.sin(tilt), ct: Math.cos(tilt) };
  }

  var VS = 'attribute vec2 p;void main(){gl_Position=vec4(p,0.,1.);}';
  var FS = [
    'precision highp float;',
    'uniform vec2 res;uniform float t,ready,lon,lat,D,tilt,F,hasW,dayM,sunM,near;uniform vec3 sun;uniform sampler2D lights,day,clouds,water;',
    'const float PI=3.14159265;',
    'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
    'float vn(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+1.),f.x),f.y);}',
    'float fbm(vec2 p){float v=0.,a=.5;for(int i=0;i<4;i++){v+=a*vn(p);p*=2.03;a*=.5;}return v;}',
    'mat3 rx(float a){float c=cos(a),s=sin(a);return mat3(1.,0.,0.,0.,c,s,0.,-s,c);}',
    'mat3 ry(float a){float c=cos(a),s=sin(a);return mat3(c,0.,-s,0.,1.,0.,s,0.,c);}',
    'void main(){',
    '  vec2 uv=(gl_FragCoord.xy-.5*res)/res.y;',
    '  float st=sin(tilt),ct=cos(tilt);',
    '  vec3 fw=vec3(0.,st,-ct),up=vec3(0.,ct,st),rt=vec3(1.,0.,0.);',
    '  vec3 P=vec3(0.,0.,1.)+D*vec3(0.,-st,ct);',                 // กล้องอยู่เหนือจุดกลางจอ ถอยไปทางใต้ตามมุมเอียง
    '  vec3 rd=normalize(fw*F+uv.x*rt+uv.y*up);',
    '  mat3 M=ry(radians(lon))*rx(-radians(lat));vec3 sl=sun*M;',  // ทิศดวงอาทิตย์จริงในกรอบของกล้อง (sunM = 1 เว้นแต่เลือกกลางวันทั้งโลก)
    '  float b=dot(P,rd),c2=dot(P,P)-1.,disc=b*b-c2,pix=1./(F*res.y);',
    // ดาว — เลื่อนตามกล้องนิดหน่อยให้มีมิติ
    '  vec3 col=vec3(.004,.005,.012);',
    '  vec2 g=floor((gl_FragCoord.xy+vec2(lon,-lat)*res.y*.003)/2.);float s=h(g);',
    '  if(s>.9975){float tw=.6+.4*sin(t*2.+s*90.);col+=vec3(.75,.8,1.)*tw*(s-.9975)*90.*(1.+1.3*near);}',   // ในยาน ห้องมืด ตาเห็นดาวชัดขึ้น
    '  float dmin=sqrt(max(dot(P,P)-b*b,0.));',
    '  if(b<0.){float o=max(dmin-1.,0.);',                          // บรรยากาศเหนือขอบฟ้า + airglow สีเขียวแบบภาพจาก ISS
    // ดวงอาทิตย์จริง (sunM): ขอบฟ้าสว่างเฉพาะด้านที่โดนแดด · แถบส้มตรงเส้นแบ่งกลางวันกลางคืน = พระอาทิตย์ขึ้น/ตกจากวงโคจร
    // มองใกล้ในยาน (near): ชั้นอากาศบางตามจริง · airglow ที่ราว 94 กม. จางแบบที่ตาเห็น
    '    float sd=dot(normalize(P-b*rd),sl),ls=sunM*smoothstep(-.12,.08,sd),tw=sunM*max(0.,1.-abs(sd)*5.);',
    '    float k1=mix(26.,130.,near),k2=mix(150.,700.,near);',
    '    col+=vec3(.15,.35,1.)*exp(-o*k1)*mix(.45+.5*dayM,.05+.95*ls,sunM)+vec3(.35,.6,1.)*exp(-o*k2)*.55*mix(1.,.12+.88*ls,sunM)',
    '      +vec3(.20,.85,.42)*exp(-abs(o-mix(.007,.0147,near))*480.)*mix(.5,.26,near)*(1.-ls)+vec3(1.,.42,.12)*exp(-o*320.)*tw*.8;}',
    '  if(disc>0.&&-b-sqrt(disc)>0.){',
    '    vec3 nl=P+rd*(-b-sqrt(disc));',
    '    vec3 n=M*nl;float sz=dot(nl,sl),dl=max(dayM,sunM*smoothstep(-.08,.06,sz));',   // dl = ส่วนที่เป็นกลางวัน ณ จุดนี้
    '    float la=asin(clamp(n.y,-1.,1.)),lo=atan(n.x,n.z);',
    '    vec2 tc=vec2(lo/(2.*PI)+.5,.5-la/PI);',
    // รอยต่อเส้นแบ่งวัน (180°): พิกัดภาพกระโดดจาก 1 → 0 การ์ดจอเลยเลือกภาพความละเอียดต่ำสุดเป็นเส้นจุดพาดลูกโลก
    // (กลางวันเห็นชัด) — ใช้พิกัดอีกชุดที่รอยต่ออยู่ที่ 0° แล้วเลือกชุดที่เปลี่ยนช้ากว่าในแต่ละจุด (ภาพวนรอบ จึงได้ภาพเดียวกัน)
    '#ifdef DERIV',
    '    float tx2=fract(tc.x+.5)-.5;',
    '    if(fwidth(tx2)<fwidth(tc.x))tc.x=tx2;',
    '#endif',
    '    float zz=max(dot(nl,-rd),0.);',
    '    vec2 px=vec2(1./4096.,1./2048.);',
    // มองใกล้ (หน้าแรกของหน้านี้บนมือถือ): ภาพ 2K ถูกขยาย 3–4 เท่า ไฟเมืองกับเมฆเลยเห็นเป็นบล็อกสี่เหลี่ยม
    // mag = 1 เมื่อจุดบนจอเล็กกว่าจุดของภาพ → เกลี่ยขอบบล็อก 4 จุด แล้วเติมเม็ดละเอียดให้ไฟเป็นกลุ่มจุดเล็กๆ แบบภาพถ่ายจากวงโคจร
    '    float mag=1.-smoothstep(.3,1.,(-b-sqrt(disc))*pix*326.);',
    '    vec2 hp=px*1.3*mag;',
    '    float L=(texture2D(lights,tc+hp).r+texture2D(lights,tc-hp).r+texture2D(lights,tc+hp*vec2(1.,-1.)).r+texture2D(lights,tc+hp*vec2(-1.,1.)).r)*.25;',
    '    float gr=vn(tc*vec2(9000.,4500.))*vn(tc*vec2(3100.,1550.)+7.);',
    '    L*=mix(1.,.5+1.9*gr,mag*.75);',
    '    float B=(texture2D(lights,tc+px*vec2(5.,0.)).r+texture2D(lights,tc-px*vec2(5.,0.)).r+texture2D(lights,tc+px*vec2(0.,4.)).r+texture2D(lights,tc-px*vec2(0.,4.)).r)*.25;',
    '    vec2 cc=tc+vec2(t*.0004,0.);',
    '    float cl=(texture2D(clouds,cc+hp).r+texture2D(clouds,cc-hp).r+texture2D(clouds,cc+hp*vec2(1.,-1.)).r+texture2D(clouds,cc+hp*vec2(-1.,1.)).r)*.25;',
    '    cl=clamp(cl+(fbm(cc*vec2(1500.,750.))-.5)*.7*mag*smoothstep(.04,.45,cl)*(1.-cl),0.,1.);',   // ขอบเมฆเป็นริ้วละเอียด ไม่เป็นขั้นบันได
    '    cl=mix(cl,smoothstep(.08,.85,cl),near*.55);',                 // ในยาน: ขอบเมฆคมขึ้น (ภาพถูกขยายมากตอนมองใกล้)
    '    vec3 land=texture2D(day,tc).rgb;',
    '    float wm=hasW>.5?texture2D(water,tc).r:0.;',
    '    vec3 baseC=land*vec3(.018,.026,.05)+vec3(.002,.005,.014);',
    '    float glint=0.;',
    '    baseC+=vec3(.10,.12,.17)*smoothstep(.55,.8,dot(land,vec3(.33)))*(1.-wm);',   // น้ำแข็งขั้วโลก/ภูเขาหิมะต้องแสงจันทร์
    '    if(wm>.01){',                                                                  // ทะเล — คำนวณเฉพาะจุดที่เป็นน้ำ
    '      vec2 wv=vec2(fbm(tc*vec2(900.,450.)+t*.05),fbm(tc*vec2(900.,450.)+17.-t*.04))-.5;',
    '      vec3 wn=normalize(nl+(rt*wv.x+up*wv.y)*.10);',
    '      vec3 Ld=sunM>.5?sl:normalize(.38*rt+.55*up-.74*fw);',
    '      vec3 rf=reflect(rd,wn);',
    '      glint=pow(max(dot(rf,Ld),0.),90.)*1.4+pow(max(dot(rf,Ld),0.),12.)*.10;',
    '      float fres=.02+.98*pow(1.-max(dot(wn,-rd),0.),5.);',
    '      vec3 sea=vec3(.004,.014,.034)+vec3(.30,.38,.55)*fres*.22+vec3(.75,.82,1.)*glint*(1.-cl);',
    '      baseC=mix(baseC,sea,wm);',
    '    }',
    '    vec3 city=vec3(1.,.48,.10)*pow(L,1.35)*2.4+vec3(1.,.78,.42)*pow(L,4.)*1.4+vec3(1.,.42,.1)*pow(B,1.5)*.45;',
    '    city*=(1.-.55*cl)*(1.-.85*wm);',                                              // ไฟเรือ/แท่นเจาะยังเห็นจางๆ
    '    vec3 surf=(baseC+vec3(.55,.62,.85)*pow(cl,1.4)*.16)*mix(1.,.42,sunM)+city*ready;',   // ในยาน: กลางคืนมืดตามจริง ไฟเมืองเท่าเดิม
    '    surf+=(vec3(.18,.35,1.)*pow(1.-zz,2.6)*.35+vec3(.35,.55,1.)*pow(1.-zz,9.)*.6)*(1.-.85*sunM);', // ฟ้าหลัวตามความหนาของบรรยากาศที่มองผ่าน (ในยาน: กลางคืนไม่มีฟ้าหลัวสีฟ้า)
    '    if(dl>0.){',                                                                  // กลางวัน: สีจริงจากดาวเทียม เมฆขาว แดดสะท้อนทะเล
    // แดดสะท้อนทะเลกลางวัน: ใช้ผิวน้ำเรียบ (ไม่ใช้คลื่นแบบกลางคืน ซึ่งกลางวันดูเป็นเม็ดหยาบ) · ในยานใช้ทิศดวงอาทิตย์จริง
    '      vec3 Lg=sunM>.5?sl:normalize(.38*rt+.55*up-.74*fw);',
    '      float sg=pow(max(dot(reflect(rd,nl),Lg),0.),36.);',
    '      vec3 dc=pow(land,vec3(1.15))*1.25+vec3(1.,.96,.88)*sg*wm*.35*(1.-cl);',
    '      dc=mix(dc,vec3(.95,.97,1.),smoothstep(.15,.85,cl)*.85);',
    '      dc+=vec3(.25,.45,1.)*pow(1.-zz,2.2)*.55+vec3(.5,.7,1.)*pow(1.-zz,8.)*.5;',
    '      dc*=mix(1.,.45+.55*smoothstep(0.,.5,sz),sunM);',                       // แดดเฉียงใกล้เส้นแบ่งวัน = สลัวลง
    '      dc*=mix(vec3(1.),vec3(1.,.66,.42),sunM*(1.-smoothstep(0.,.16,sz))*.7);',  // แสงเช้า/เย็นอมส้ม
    '      surf=mix(surf,dc,dl);',
    '    }',
    '    col=mix(col,surf,smoothstep(0.,3.*sqrt(c2)*pix,disc));',
    '  }',
    '  col*=1.-.35*pow(length(uv*vec2(.9,1.1)),2.2);',
    '  col+=(h(gl_FragCoord.xy+fract(t)*91.)-.5)*.018;',
    '  col=1.-exp(-col*1.35);',
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
    // เครื่องที่รองรับ fwidth (มือถือแทบทุกรุ่น) แก้รอยต่อเส้นแบ่งวันได้ · ไม่รองรับก็ยังวาดได้เหมือนเดิม
    var deriv = gl.getExtension('OES_standard_derivatives');
    gl.attachShader(prog, sh(gl.FRAGMENT_SHADER, (deriv ? '#extension GL_OES_standard_derivatives : enable\n#define DERIV 1\n' : '') + FS));
    gl.linkProgram(prog);
    if (!gl.getProgramParameter(prog, gl.LINK_STATUS)) throw new Error(gl.getProgramInfoLog(prog));
  } catch (e) { wrap.classList.add('no-webgl'); return; }
  gl.useProgram(prog);

  gl.bindBuffer(gl.ARRAY_BUFFER, gl.createBuffer());
  gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1, -1, 3, -1, -1, 3]), gl.STATIC_DRAW);
  var loc = gl.getAttribLocation(prog, 'p');
  gl.enableVertexAttribArray(loc);
  gl.vertexAttribPointer(loc, 2, gl.FLOAT, false, 0, 0);

  var U = {};
  ['res', 't', 'ready', 'lon', 'lat', 'D', 'tilt', 'F', 'hasW', 'dayM', 'sunM', 'near', 'sun', 'lights', 'day', 'clouds', 'water']
    .forEach(function (k) { U[k] = gl.getUniformLocation(prog, k); });

  var base = (document.currentScript && document.currentScript.src || '/static/cockpit_earth.js').replace(/cockpit_earth\.js.*$/, '');
  var texs = [], pending = 3, ready = 0, hasW = 0;
  ['lights', 'day', 'clouds', 'water'].forEach(function (name, unit) {
    var tx = gl.createTexture();
    gl.activeTexture(gl.TEXTURE0 + unit);
    gl.bindTexture(gl.TEXTURE_2D, tx);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, 1, 1, 0, gl.RGBA, gl.UNSIGNED_BYTE, new Uint8Array([0, 0, 0, 255]));
    gl.uniform1i(U[name], unit);
    texs[unit] = tx;
  });
  function load(unit, file, done) {
    var img = new Image();
    img.onload = function () {
      gl.activeTexture(gl.TEXTURE0 + unit);
      gl.bindTexture(gl.TEXTURE_2D, texs[unit]);
      gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, gl.RGBA, gl.UNSIGNED_BYTE, img);
      // ภาพทุกภาพกว้างยาวเป็นกำลังของ 2 — ใช้ mipmap ได้ ภาพทั้งโลกจึงไม่ระยิบเวลาหมุน · วนรอบเส้นแบ่งวันได้ไม่มีรอยต่อ
      gl.generateMipmap(gl.TEXTURE_2D);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
      gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
      if (done) done();
      kick();
    };
    img.src = base + 'earth/' + file;
  }
  var conn = navigator.connection || {};
  var can4k = gl.getParameter(gl.MAX_TEXTURE_SIZE) >= 4096 && !conn.saveData;
  // มือถือ/เครื่องแรมน้อย/เน็ตช้า: ภาพ 4K (ราว 2.6 MB) ยังไม่โหลดจนกว่าจะซูมเข้าไปดูจริง — ทั้งโลกภาพ 2K ก็คมพอบนจอเล็ก
  var light = Math.min(screen.width, screen.height) < 700 || (navigator.deviceMemory || 8) <= 4 || /2g|3g/.test(conn.effectiveType || '');
  var got4k = false, firstIn = false;
  function maybe4k() {
    if (got4k || !firstIn || !can4k || (light && S.tL < 2 && !SHIP.on)) return;
    got4k = true;
    load(0, 'lights_4k.jpg'); load(1, 'day_4k.jpg'); load(2, 'clouds_4k.jpg');      // 4K หลังภาพแรกขึ้นแล้ว — เน็ตช้าไม่ต้องรอ
  }
  function firstDone() {
    if (--pending > 0) return;
    wrap.classList.add('lit');
    load(3, 'water.png', function () { hasW = 1; });
    firstIn = true;
    maybe4k();
    safeArrive();
  }
  // มาจากหน้าฉุกเฉิน (/safe) พร้อมตำแหน่ง: /universe#safe=lat,lon → บินลงแผนที่เมืองตรงนั้น เห็นจุดตำรวจ/โรงพยาบาล/ร้านที่มีคน
  // ตำแหน่งอยู่ใน hash (#) จึงไม่ถูกส่งไปเซิร์ฟเวอร์เลย
  function safeArrive() {
    var m = /^#safe=(-?\d{1,2}(?:\.\d+)?),(-?\d{1,3}(?:\.\d+)?)$/.exec(location.hash || '');
    if (!m) return;
    var la = clamp(+m[1], -85, 85), lo = +m[2];
    if (!(Math.abs(lo) <= 180)) return;
    S.lat = S.tlat = la; S.lon = S.tlon = lo; S.L = S.tL = LMAX; sync();
    go({ lat: la, lon: lo, L: LMAX + .5 });                          // ลึกกว่าภาพ NASA → แผนที่เมืองรับช่วง
    var tries = 0;
    (function deeper() {                                              // ซูมต่อจนเห็นจุดที่ขอความช่วยเหลือได้ (ซูม ~15)
      if (S.city && window.KD_cityMap) { window.KD_cityMap.zoom(2.5); setTimeout(function () { window.KD_cityMap.zoom(1); }, 700); return; }
      if (++tries < 20) setTimeout(deeper, 400);
    })();
  }
  load(0, 'lights.jpg', firstDone); load(1, 'day.jpg', firstDone); load(2, 'clouds.jpg', firstDone);

  // ── ความละเอียดการวาดปรับตามเครื่อง: เฟรมช้า → ลดลงทีละขั้น · เร็วพอ → เพิ่มกลับ ─────────────────────
  var DPR_BASE = Math.min(window.devicePixelRatio || 1, light ? 1.25 : 1.5), DPR_MAX = DPR_BASE, scale = DPR_MAX, ftAvg = 16, ftCheck = 0;
  function size() {
    canvas.width = Math.max(1, Math.round(canvas.clientWidth * scale));
    canvas.height = Math.max(1, Math.round(canvas.clientHeight * scale));
    gl.viewport(0, 0, canvas.width, canvas.height);
    labelsDirty = true;
    kick();
  }
  window.addEventListener('resize', size);

  // ── ฉายจุดบนโลกมาที่จอ และกลับกัน — สมการเดียวกับ shader ───────────────────────────────────────
  // world n = ry(lon)·rx(−lat)·l  →  l = rx(lat)·ry(−lon)·n
  function rxv(a, v) { var c = Math.cos(a), s = Math.sin(a); return [v[0], c * v[1] - s * v[2], s * v[1] + c * v[2]]; }
  function ryv(a, v) { var c = Math.cos(a), s = Math.sin(a); return [c * v[0] + s * v[2], v[1], -s * v[0] + c * v[2]]; }
  function view() {
    var W = canvas.clientWidth, H = canvas.clientHeight, cam = camera(S.L, W / Math.max(1, H));
    var P = [0, -cam.D * cam.st, 1 + cam.D * cam.ct];
    return { W: W, H: H, cam: cam, P: P, C: ryv(S.lon * RAD, rxv(-S.lat * RAD, P)) };   // C = ตำแหน่งกล้องในพิกัดโลก
  }
  function toScreen(V, w) {
    if (w[0] * V.C[0] + w[1] * V.C[1] + w[2] * V.C[2] <= 1.002) return null;          // อยู่หลังขอบฟ้า
    var l = rxv(S.lat * RAD, ryv(-S.lon * RAD, w)), c = V.cam;
    var vx = l[0] - V.P[0], vy = l[1] - V.P[1], vz = l[2] - V.P[2];
    var x = vx, y = vy * c.ct + vz * c.st, z = vy * c.st - vz * c.ct;
    if (z <= 1e-4) return null;
    return [V.W / 2 + x / z * F * V.H, V.H / 2 - y / z * F * V.H, z];
  }
  function pick(V, sx, sy) {                                           // จุดบนจอ → lat/lon (null = ไม่โดนโลก)
    var c = V.cam, ux = (sx - V.W / 2) / V.H, uy = (V.H / 2 - sy) / V.H;
    var d = [ux, F * c.st + uy * c.ct, -F * c.ct + uy * c.st], dl = Math.hypot(d[0], d[1], d[2]);
    d = [d[0] / dl, d[1] / dl, d[2] / dl];
    var b = V.P[0] * d[0] + V.P[1] * d[1] + V.P[2] * d[2];
    var disc = b * b - (V.P[0] * V.P[0] + V.P[1] * V.P[1] + V.P[2] * V.P[2] - 1);
    if (disc <= 0) return null;
    var tt = -b - Math.sqrt(disc);
    if (tt <= 0) return null;
    var n = ryv(S.lon * RAD, rxv(-S.lat * RAD, [V.P[0] + d[0] * tt, V.P[1] + d[1] * tt, V.P[2] + d[2] * tt]));
    var lo = Math.atan2(n[0], n[2]) / RAD;
    return { lat: Math.asin(clamp(n[1], -1, 1)) / RAD, lon: lo + 360 * Math.round((S.tlon - lo) / 360) };
  }

  // ── การควบคุม ─────────────────────────────────────────────────────────────────────────────
  var idleUntil = 0, pointers = {}, gest = null, lastTap = 0, hist = [];
  function setL(L) {
    if (SHIP.on && L > LMAX) L = LMAX;                               // อยู่ในยาน: ล้อเมาส์/ถ่างนิ้วลึกไม่สลับไปแผนที่เมือง
    if (L > LMAX + .02 && toCity()) return;                          // ลึกกว่าภาพ NASA → แผนที่เมืองรับช่วงต่อ
    S.tL = clamp(L, 0, LMAX); sync(); maybe4k();
  }
  // ── ส่งต่อให้แผนที่เมืองกลางคืน (static/city_map.js) ด้วยตำแหน่งและระยะเดียวกับกล้องตอนนี้ ──────────────
  function toCity() {
    var CM = window.KD_cityMap;
    if (!CM || !CM.can() || S.city) return false;
    var V = view(), cam = camera(LMAX, V.W / Math.max(1, V.H));
    var mpp = cam.D * 6371000 / (F * V.H);                             // เมตรต่อพิกเซลกลางจอ
    var lon = ((S.tlon % 360) + 540) % 360 - 180;
    if (!CM.enter({ lon: lon, lat: S.tlat, zoom: Math.log(78271.517 * Math.cos(S.tlat * RAD) / mpp) / Math.LN2,
                    pitch: cam.tilt / RAD })) return false;
    S.city = true; pointers = {}; gest = null; S.vlon = S.vlat = 0; hideHazard();
    S.tL = LMAX; sync();
    if (lab) lab.style.opacity = '0';
    if (hero) { hero.style.setProperty('--hero-a', '0'); hero.classList.add('zoomed'); }   // โลกหยุดวาดแล้ว — ต้องซ่อนหัวเรื่องเอง
    return true;
  }
  function settle() { if (calm()) { S.lon = S.tlon; S.lat = S.tlat; S.L = S.tL; sync(); } }
  function hold(ms) { idleUntil = performance.now() + ms; kick(); }
  function degPerPx(V) {                                             // ระยะบนพื้นต่อ 1 พิกเซล (องศา) ตรงกลางจอ
    return V.cam.D / (F * V.H) / RAD;
  }
  function zoomAt(newL, sx, sy) {
    // ซูมเข้าหาจุดที่ชี้: เป้าหมายเลื่อนเข้าหาจุดนั้นตามสัดส่วนระยะที่หดลง (ทำเฉพาะตอนลงใกล้กว่าวงโคจร)
    var V = view(), at = sx != null && S.tL >= 1 && newL >= 1 ? pick(V, sx, sy) : null;
    var k = Math.pow(2, S.tL - clamp(newL, 0, LMAX));
    if (at) { S.tlon = at.lon + (S.tlon - at.lon) * k; S.tlat = clamp(at.lat + (S.tlat - at.lat) * k, -85, 85); }
    setL(newL);
  }
  function panBy(dx, dy, V) {
    var g = degPerPx(V);
    S.tlon -= dx * g / Math.max(.25, Math.cos(S.tlat * RAD));
    S.tlat = clamp(S.tlat + dy * g / Math.max(.5, V.cam.ct * 1.6 + .2), -85, 85);
  }
  function setTouchMode() { canvas.style.touchAction = S.tL > 1.02 ? 'none' : 'pan-y'; }   // ซูมเข้าไปแล้ว = แอปแผนที่เต็มตัว
  canvas.addEventListener('pointerdown', function (e) {
    pointers[e.pointerId] = { x: e.clientX, y: e.clientY };
    S.vlon = S.vlat = 0; hist = [];
    var ids = Object.keys(pointers);
    if (ids.length === 2) {
      var a = pointers[ids[0]], b = pointers[ids[1]];
      gest = { pinch: true, d0: Math.hypot(a.x - b.x, a.y - b.y) || 1, L0: S.tL, mx: (a.x + b.x) / 2, my: (a.y + b.y) / 2 };
    } else {
      gest = { pinch: false, x: e.clientX, y: e.clientY, touch: e.pointerType === 'touch', moved: 0 };
    }
    if (ids.length === 2) hideHazard();
    hold(6000);
  });
  window.addEventListener('pointermove', function (e) {
    var p = pointers[e.pointerId];
    if (!p || !gest) return;
    var V = view(), r = canvas.getBoundingClientRect(), dx = e.clientX - p.x, dy = e.clientY - p.y;
    p.x = e.clientX; p.y = e.clientY;
    if (gest.pinch) {
      var ids = Object.keys(pointers);
      if (ids.length < 2) return;
      var a = pointers[ids[0]], b = pointers[ids[1]], mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      panBy(mx - gest.mx, my - gest.my, V); gest.mx = mx; gest.my = my;
      zoomAt(gest.L0 + Math.log(Math.hypot(a.x - b.x, a.y - b.y) / gest.d0) / Math.LN2, mx - r.left, my - r.top);
    } else {
      if (gest.moved > 8) hideHazard();
      // นิ้วเดียวตอนมองทั้งโลก/วงโคจร: หมุนแนวนอนเท่านั้น (ลากแนวตั้งยังเลื่อนหน้าได้) · ซูมเข้าไปแล้วเลื่อนได้ทุกทิศ
      gest.moved += Math.abs(dx) + Math.abs(dy);
      var free = !gest.touch || S.tL > 1.02;
      panBy(dx * (S.tL <= 1 ? 1.4 : 1), free ? dy : 0, V);
      hist.push([performance.now(), S.tlon, S.tlat]);
      if (hist.length > 6) hist.shift();
    }
    settle();
    hold(6000);
  });
  function up(e) {
    var p = pointers[e.pointerId];
    delete pointers[e.pointerId];
    if (!gest) return;
    if (!gest.pinch && p) {
      var now = performance.now();
      if (gest.moved < 8) {                                             // แตะ (ไม่ใช่ลาก) — แตะสองครั้ง = บินไปจุดนั้น
        var rr = canvas.getBoundingClientRect(), hz = hazardAt(e.clientX - rr.left, e.clientY - rr.top);
        var pl = hz ? null : placeAt(e.clientX - rr.left, e.clientY - rr.top);
        if (hz) showHazard(hz); else hideHazard();
        if (pl) showPlace(pl); else hidePlace();
        if (now - lastTap < 320) { var r = canvas.getBoundingClientRect(); flyTo(e.clientX - r.left, e.clientY - r.top); lastTap = 0; }
        else lastTap = now;
      } else if (!calm() && hist.length > 1) {                          // ปล่อยนิ้ว = โลกไหลต่ออีกนิดแล้วหยุดเอง
        var h0 = hist[0], h1 = hist[hist.length - 1], dt = (h1[0] - h0[0]) / 1000;
        if (dt > 0 && now - h1[0] < 80) { S.vlon = (h1[1] - h0[1]) / dt; S.vlat = (h1[2] - h0[2]) / dt; }
      }
    }
    gest = null;                                                        // ยกนิ้วใดนิ้วหนึ่ง = จบท่านั้น
    setTouchMode();
    hold(6000);
  }
  window.addEventListener('pointerup', up);
  window.addEventListener('pointercancel', up);
  canvas.addEventListener('wheel', function (e) {
    // ล้อเมาส์ซูมเมื่อซูมเข้าไปแล้ว หรือกด Ctrl/ถ่างทัชแพด — ที่ระดับวงโคจรปล่อยให้เลื่อนหน้าได้ตามปกติ
    if (!e.ctrlKey && S.tL <= 1.02 && e.deltaY > 0) return;
    if (!e.ctrlKey && S.tL <= 1.02 && e.deltaY < 0 && window.scrollY > 40) return;
    e.preventDefault();
    var r = canvas.getBoundingClientRect(), dy = e.deltaMode === 1 ? e.deltaY * 16 : e.deltaY;
    zoomAt(S.tL - clamp(dy, -120, 120) * (e.ctrlKey ? .012 : .0045), e.clientX - r.left, e.clientY - r.top);
    S.vlon = S.vlat = 0;
    settle(); setTouchMode(); hold(8000);
  }, { passive: false });
  canvas.tabIndex = 0;
  canvas.addEventListener('keydown', function (e) {
    var V = view(), step = 60, k = e.key;
    if (k === 'ArrowLeft') panBy(-step, 0, V); else if (k === 'ArrowRight') panBy(step, 0, V);
    else if (k === 'ArrowUp') panBy(0, -step, V); else if (k === 'ArrowDown') panBy(0, step, V);
    else if (k === '+' || k === '=') setL(S.tL < 1 ? 1 : S.tL + 1);
    else if (k === '-' || k === '_') setL(S.tL - 1);
    else return;
    e.preventDefault(); settle(); setTouchMode(); hold(8000);
  });
  function flyTo(sx, sy) {
    var at = pick(view(), sx, sy);
    if (!at) return;
    go({ lat: at.lat, lon: at.lon, L: Math.max(2, Math.min(LMAX, S.tL + 1)) });
  }
  canvas.addEventListener('dblclick', function (e) {
    if (e.pointerType === 'touch') return;                            // นิ้วจัดการเองใน pointerup แล้ว
    var r = canvas.getBoundingClientRect();
    flyTo(e.clientX - r.left, e.clientY - r.top);
  });

  function sunVec(ms) { var OB = window.KD_orbit; if (!OB) return [0, 0, 1]; var su = OB.sun(ms); return OB.vec(su.lat, su.lon); }
  function leaveCity() { if (S.city && window.KD_cityMap) window.KD_cityMap.exit(); }
  function go(o) {
    if (SHIP.on && o.L > LMAX) return;                          // อยู่ในยาน: ถ่างนิ้วลึกไม่สลับไปแผนที่เมือง (ยานจะค้างอยู่ข้างหลัง)
    if (o.L > LMAX + .02 && toCity()) return;
    for (var k in o) S['t' + k] = o[k];
    S.tL = clamp(S.tL, 0, LMAX); S.vlon = S.vlat = 0;
    sync(); settle(); setTouchMode(); maybe4k();
    hold(8000);
  }
  // โหมดยานอวกาศ — เริ่มวงโคจรเหนือจุดที่กำลังดูอยู่ · ออกจากโหมดกลับมาที่วงโคจรเดิม
  var SHIP = { on: false, fast: false, k: 0, st: { u: 0, node: 0 }, clock: 0 }, shipHud = document.getElementById('ship-hud'), lastShipHud = 0;
  // วงโคจรที่ผ่านจุด lat/lon ตอนนี้ (ช่วงขาขึ้น มุ่งตะวันออกเฉียงเหนือ) — ละติจูดเกินความเอียงของวงโคจรใช้ขอบวงโคจรแทน
  function orbitOver(OB, lat, lon) {
    var i = OB.INC_DEG * RAD, la = clamp(lat, -OB.INC_DEG + .5, OB.INC_DEG - .5);
    var u = Math.asin(Math.sin(la * RAD) / Math.sin(i));             // มุมในวงโคจรที่ผ่านละติจูดนี้
    return { u: u, node: lon - Math.atan2(Math.cos(i) * Math.sin(u), Math.cos(u)) / RAD };
  }
  function shipStart() {
    var OB = window.KD_orbit; if (!OB) return false;
    if (SHIP.k > 0) { SHIP.on = true; maybe4k(); shipRes(true); return true; }      // กดกลับเข้ายานระหว่างกำลังออก = โคจรต่อจากเดิม (ไม่กระโดด)
    SHIP.st = orbitOver(OB, S.lat, S.lon); SHIP.clock = Date.now(); SHIP.on = true; leaveCity(); go({ L: 1 }); maybe4k(); shipRes(true); return true;
  }
  // ในยาน: วาดที่ความละเอียดจอจริง (สูงสุด 2×) ให้คมที่สุด — ตัวลดความละเอียดอัตโนมัติยังลดให้เองถ้าเครื่องช้า
  function shipRes(on) { DPR_MAX = on ? Math.max(DPR_BASE, Math.min(window.devicePixelRatio || 1, 2)) : DPR_BASE; scale = Math.min(DPR_MAX, on ? DPR_MAX : scale); size(); }
  function leaveShip() { if (SHIP.on) { SHIP.on = false; shipRes(false); document.documentElement.classList.remove('kd-ship'); kick(); } }
  window.KD_earth = {
    ship: function (on) { if (on) { if (!shipStart()) return false; } else leaveShip(); kick(); return SHIP.on; },
    shipFast: function () { SHIP.fast = !SHIP.fast; kick(); return SHIP.fast; },
    shipOn: function () { return SHIP.on; },
    layer: function (k, on) {
      if (!(k in LAYER)) return false;
      LAYER[k] = on == null ? !LAYER[k] : !!on;
      try { localStorage.setItem(k === 'places' ? 'kd-places' : 'kd-names', LAYER[k] ? '1' : '0'); } catch (e) {}
      if (k === 'places' && !LAYER.places) hidePlace();
      labelsDirty = true; kick(); return LAYER[k];
    },
    layerOn: function (k) { return !!LAYER[k]; },
    // บินไปให้เห็นบ้านเรา: วางยานทางใต้ของกรุงเทพฯ เท่าระยะที่หน้าต่างมองไปข้างหน้า — กรุงเทพฯ อยู่กลางหน้าต่างพอดี แล้วโคจรต่อตามจริง
    shipHome: function () {
      var OB = window.KD_orbit; if (!OB || !SHIP.on) return false;
      var asp = canvas.width / Math.max(1, canvas.height), VW = asp < 1 ? OB.VIEW_TALL : OB.VIEW;
      SHIP.st = orbitOver(OB, 13.75 - VW.ahead, 100.5); kick(); return true;
    },
    globe: function (on) { leaveShip(); leaveCity(); go({ L: on ? 0 : 1, lat: on ? 20 : 40 }); },
    // บินไปจุดภัย แล้วเปิดกล้องรายละเอียดเมื่อถึง (ใช้กับรายการภัยในแผงเครื่องมือ)
    flyHazard: function (i) {
      var h = HZ.list[i]; if (!h) return;
      leaveShip(); leaveCity(); go({ lat: clamp(h.lat, -85, 85), lon: h.lon + 360 * Math.round((S.tlon - h.lon) / 360), L: 2.2 });
      var tries = 0;                                              // รอจนโลกบินถึงแล้วจุดขึ้นจอ (เครื่องช้าก็รอได้ ไม่เกิน ~5 วินาที)
      (function wait() {
        var m = HZ.shown.filter(function (x) { return x.h === h; })[0], V = view();
        if (m && Math.hypot(m.x - V.W / 2, m.y - V.H / 2) < Math.min(V.W, V.H) * .3) { showHazard(m); return; }
        if (++tries < 14) setTimeout(wait, 350);
      })();
    },
    hazards: function () { return HZ.list; },
    pole: function (north) { leaveShip(); leaveCity(); go({ L: 0, lat: north ? 80 : -80 }); },
    zoomIn: function () { leaveShip(); if (S.city) window.KD_cityMap.zoom(1); else go({ L: S.tL < 1 ? 1 : S.tL + 1 }); },
    zoomOut: function () {
      leaveShip();
      if (S.city) { window.KD_cityMap.zoom(-1); return; }
      go({ L: S.tL > 1 ? S.tL - 1 : 0, lat: S.tL > 1 ? S.tlat : clamp(S.tlat, -60, 60) });
    },
    // แผนที่เมืองเรียกตอนซูมออกพ้นระดับที่เข้ามา — กลับมาเป็นโลกที่จุดเดิม
    fromCity: function (c) {
      S.city = false;
      S.lon = S.tlon = c.lon; S.lat = S.tlat = clamp(c.lat, -85, 85);
      S.L = LMAX; S.tL = LMAX - .5; sync(); setTouchMode();
      if (lab) lab.style.opacity = '';
      labelsDirty = true; last = 0; hold(6000);
    },
    state: S
  };

  var hudPos = document.getElementById('sat-pos'), hudUtc = document.getElementById('sat-utc'), hudAlt = document.getElementById('sat-alt'), lastHud = 0;
  var hero = document.getElementById('hero');
  var visible = true, raf = 0, last = 0, tsec = 0, labelsDirty = true, lastKey = '';
  if ('IntersectionObserver' in window) {
    new IntersectionObserver(function (es) { visible = es[0].isIntersecting; if (visible) kick(); }).observe(canvas);
  }
  function kick() { if (!raf) raf = requestAnimationFrame(frame); }
  // เฟรมเรตสูงสุดตามที่ผู้ใช้เลือกในหน้าแชต (localStorage kd-fps: 30 · 60 · 90 · 120 · 144) — ใช้ค่าเดียวกันทั้งเว็บ
  // เดิมโลกวาดเต็มความเร็วจอเสมอ (จอ 120/144 Hz วาดทุกเฟรม เครื่องร้อน) · สะสมเวลา วาดเฉลี่ยเท่าค่าที่เลือก
  var FPS_OK = [30, 60, 90, 120, 144], cap = 90, capUser = false, capAcc = 0, capLast = 0;
  function fpsCap() { var v = 0; try { v = +localStorage.getItem('kd-fps'); } catch (e) {} capUser = FPS_OK.indexOf(v) >= 0; cap = capUser ? v : 90; }
  fpsCap();
  window.addEventListener('storage', function (e) { if (e.key === 'kd-fps') fpsCap(); });
  window.addEventListener('kd-fps', function () { fpsCap(); kick(); });          // เมนูเฟรมเรตในหน้านี้เอง
  window.addEventListener('kd-calm', kick);
  // กลางวัน/กลางคืน: dayM ไหลจาก 0 ↔ 1 ราว 1 วินาที (โหมดลดการเคลื่อนไหว = เปลี่ยนทันที)
  function dayOn() { return document.documentElement.classList.contains('kd-day') ? 1 : 0; }
  var dayM = dayOn();
  window.addEventListener('kd-theme', function () { labelsDirty = true; kick(); });
  document.addEventListener('visibilitychange', kick);

  function frame(now) {
    raf = 0;
    if (document.hidden || !visible || S.city) { last = 0; return; }   // แผนที่เมืองเต็มจอ — โลกไม่ต้องวาด
    var gap = (now - (capLast || now)) / 1000;
    // ในยาน ใครไม่ได้ตั้งเฟรมเรตเองใช้ 60 — วิวเคลื่อนตลอดและวาดเต็มจอที่ความละเอียดสูง 60 ลื่นและเครื่องไม่ร้อน
    var capNow = SHIP.on && !capUser ? Math.min(cap, 60) : cap;
    capAcc = Math.min(capAcc + gap, 2 / capNow);
    if (capLast && capAcc + 1e-4 < 1 / capNow) { capLast = now; kick(); return; }
    capAcc = Math.max(0, capAcc - 1 / capNow); capLast = now;
    var busy = !!gest || Math.abs(S.vlon) + Math.abs(S.vlat) > .01;
    // เครื่องเบา: ตอนลอยเองไม่มีใครแตะ วาด ~30 ภาพ/วินาทีพอ — ประหยัดแบตและไม่ร้อน
    // (ยกเว้นผู้ใช้เลือกเฟรมเรตเอง หรืออยู่ในยาน ซึ่งวิวเคลื่อนตลอด — ใช้ค่าที่เลือกแทน)
    if (light && !busy && !SHIP.on && !capUser && last && now - last < 30) { kick(); return; }
    var dt = last ? Math.min(.05, (now - last) / 1000) : .016;
    if (last && (busy || SHIP.on)) {                                    // วัดความลื่นเฉพาะตอนมีคนเล่นอยู่ หรืออยู่ในยาน
      ftAvg = ftAvg * .9 + (now - last) * .1;
      if (now - ftCheck > 900) {
        ftCheck = now;
        var slack = Math.max(0, 1000 / capNow - 16.7);                    // เลือก 30 เฟรมเอง: ภาพห่าง 33 ms ไม่ได้แปลว่าเครื่องช้า
        if (ftAvg > 26 + slack * 1.5 && scale > .55) { scale = Math.max(.55, scale * .82); size(); }
        else if (ftAvg < 17 + slack && scale < DPR_MAX) { scale = Math.min(DPR_MAX, scale * 1.12); size(); }
      }
    }
    last = now;
    var still = calm();
    if (!still) tsec += dt;
    if (!still && !gest && now > idleUntil && S.tL > .5 && S.tL <= 1.02) S.tlon += DRIFT * dt;   // ดาวเทียมเคลื่อนไปทางตะวันออก
    if (!gest && (S.vlon || S.vlat)) {                                 // ไหลต่อหลังปล่อยนิ้ว แล้วค่อยๆ หยุด
      S.tlon += S.vlon * dt; S.tlat = clamp(S.tlat + S.vlat * dt, -85, 85);
      var f = Math.exp(-dt * 3.2); S.vlon *= f; S.vlat *= f;
      if (Math.abs(S.vlon) + Math.abs(S.vlat) < .01) S.vlon = S.vlat = 0;
    }
    var k = still ? 1 : 1 - Math.exp(-dt * (gest ? 18 : 5));
    S.lon += (S.tlon - S.lon) * k; S.lat += (S.tlat - S.lat) * k;
    S.L += (S.tL - S.L) * (still ? 1 : 1 - Math.exp(-dt * (gest ? 16 : 4)));
    sync();
    if (S.tL > LMAX - 1 && window.KD_cityMap) window.KD_cityMap.prefetch();   // ใกล้ถึงระดับเมือง — โหลดแผนที่รอไว้
    var dayT = dayOn();
    if (dayM !== dayT) dayM = still ? dayT : dayT > dayM ? Math.min(1, dayM + dt * 1.1) : Math.max(0, dayM - dt * 1.1);
    if (ready < 1 && pending === 0) ready = still ? 1 : Math.min(1, ready + dt * 1.2);
    var cam = camera(S.L, canvas.width / Math.max(1, canvas.height)), near = 0, Fv = F, clock = Date.now();
    var OB = window.KD_orbit;
    if (OB && (SHIP.on || SHIP.k > 0)) {
      if (SHIP.on && !still) { var kx = SHIP.fast ? 60 : 1; SHIP.st = OB.step(SHIP.st, dt, kx); SHIP.clock += dt * 1000 * kx; }
      var asp = canvas.width / Math.max(1, canvas.height), gp = OB.ground(SHIP.st.u, SHIP.st.node), VW = asp < 1 ? OB.VIEW_TALL : OB.VIEW;
      SHIP.k = still ? (SHIP.on ? 1 : 0) : clamp(SHIP.k + (SHIP.on ? dt : -dt) / 1.6, 0, 1);
      var e = smooth(SHIP.k);                                         // บินลงจากวงโคจรสูงสู่ความสูงยานแบบนุ่มๆ
      // กล้องหันไปทางเหนือ: จุดกลางจออยู่เหนือจุดใต้ยาน VW.ahead องศา — ตัวกล้องจึงอยู่ตรงเหนือจุดใต้ยานที่ 408 กม. พอดี
      S.lon = S.tlon = gp.lon + 360 * Math.round((S.lon - gp.lon) / 360); S.lat = S.tlat = gp.lat + VW.ahead * e; S.vlon = S.vlat = 0;
      cam = { D: Math.exp(Math.log(cam.D) + (Math.log(VW.D) - Math.log(cam.D)) * e), tilt: cam.tilt + (VW.tilt - cam.tilt) * e };
      near = e; clock = SHIP.clock;                                     // เวลาในยาน (เร่ง ×60 ได้)
      var sv = sunVec(clock);
      if (asp < 1) Fv = F + (Math.min(F, .5 * asp / Math.tan(22 * RAD)) - F) * e;   // จอแนวตั้ง: มุมกว้าง ~44° ให้เห็นขอบโลกโค้ง
      if (shipHud && now - lastShipHud > 500) {
        lastShipHud = now;
        var nv = OB.vec(gp.lat, gp.lon), lit = nv[0] * sv[0] + nv[1] * sv[1] + nv[2] * sv[2] > 0;
        shipHud.textContent = 'ALT ' + OB.ALT_KM + ' km · ' + OB.SPEED_KMS + ' km/s · ' + Math.abs(gp.lat).toFixed(1) + '°' + (gp.lat < 0 ? 'S' : 'N')
          + ' ' + Math.abs(gp.lon).toFixed(1) + '°' + (gp.lon < 0 ? 'W' : 'E') + (lit ? ' · ☀ DAY' : ' · ☾ NIGHT') + (SHIP.fast ? ' · ×60' : '');
      }
    }
    // โลกใบเดียวกันทุกมุม: ทั้งลูกโลกและหน้าต่างยานใช้ดวงอาทิตย์จริงชุดเดียวกัน (เดิมลูกโลกเป็นกลางคืนทั้งใบ แต่ในยานมีกลางวัน)
    // เลือก "กลางวัน" ไว้ = สว่างทั้งโลกเหมือนเดิม
    var svv = sunVec(clock); gl.uniform3f(U.sun, svv[0], svv[1], svv[2]);
    gl.uniform1f(U.sunM, OB ? 1 - dayM : 0); gl.uniform1f(U.near, near);
    gl.uniform2f(U.res, canvas.width, canvas.height);
    gl.uniform1f(U.t, tsec); gl.uniform1f(U.ready, ready);
    gl.uniform1f(U.lon, S.lon); gl.uniform1f(U.lat, S.lat);
    gl.uniform1f(U.D, cam.D); gl.uniform1f(U.tilt, cam.tilt); gl.uniform1f(U.F, Fv);
    gl.uniform1f(U.hasW, hasW); gl.uniform1f(U.dayM, dayM);
    gl.drawArrays(gl.TRIANGLES, 0, 3);
    if (hudPos && now - lastHud > 250) {
      lastHud = now;
      var lo = window.KD_satLon(), la = S.lat, V = view(), alt = (Math.hypot(V.C[0], V.C[1], V.C[2]) - 1) * 6371;
      hudPos.textContent = 'LAT ' + Math.abs(la).toFixed(1) + '°' + (la < 0 ? 'S' : 'N') + ' · LON ' + Math.abs(lo).toFixed(1) + '°' + (lo < 0 ? 'W' : 'E');
      if (hudUtc) hudUtc.textContent = 'UTC ' + new Date().toISOString().slice(11, 19);
      if (hudAlt) hudAlt.textContent = S.L < .3 ? 'FULL DISK' : 'ALT ' + Math.round(alt).toLocaleString('en-US') + ' km';
    }
    if (SHIP.k > 0) { if (lab) lab.style.opacity = '0'; } else { if (lab && lab.style.opacity === '0') lab.style.opacity = ''; labels(); }   // หน้าต่างยาน: ไม่มีชื่อเมืองบังวิว
    if (!still || ready < 1 || dayM !== dayT || (SHIP.on && SHIP.k < 1)) kick();                                    // คลื่น/ดาว/เมฆขยับตลอด — โหมดลดการเคลื่อนไหวหยุดวาดเมื่อนิ่ง
  }

  // ── ชื่อเมือง — ชั้นตามความสำคัญ โหลดเมื่อซูมถึง (มองทั้งโลกไม่โหลดอะไรเลย) ───────────────────────
  // GeoNames ผ่าน static/earth/ — scripts/build_earth_cities.py · แถว [ชื่อ, lat, lon, ชื่อไทย?]
  var lab = document.getElementById('earth-labels'), lctx = lab && lab.getContext('2d');
  var THAI = /^th/i.test(document.documentElement.lang || '');
  var FONT = '"Noto Sans Thai Looped",system-ui,sans-serif';
  var TIERS = [
    { f: 'capitals.json', at: 1.55, cap: 1, font: '600 12.5px ', color: '#edcc62', a: .96, dot: 2.4 },
    { f: 'admin1.json', at: 2.25, font: '500 11.5px ', color: '#f2e2b4', a: .9, dot: 1.9 },
    { f: 'cities_t2.json', at: 1.75, font: '500 11px ', color: '#e6f0ff', a: .86, dot: 1.6 },
    { f: 'cities_t3.json', at: 2.85, font: '500 10.5px ', color: '#e6f0ff', a: .76, dot: 1.4 },
    { f: 'cities_t4.json', at: 3.45, font: '400 10px ', color: '#dfe8fa', a: .68, dot: 1.2 },
    { f: 'cities_t5.json', at: 4.0, font: '400 10px ', color: '#d6e0f2', a: .6, dot: 1.1 }
  ];
  TIERS.forEach(function (T) { T.data = null; T.busy = false; });
  function fetchTier(T) {
    T.busy = true;
    fetch(base + 'earth/' + T.f).then(function (r) { return r.json(); }).then(function (d) {
      T.data = (d.capitals || d).map(function (c) {            // [ชื่อ, lat, lon, ไทย?] หรือ [ชื่อ, ประเทศ, lat, lon, ประชากร, ไทย?]
        var la = (T.cap ? c[2] : c[1]) * RAD, lo = (T.cap ? c[3] : c[2]) * RAD, th = T.cap ? c[5] : c[3];
        return [THAI && th ? th : c[0], Math.cos(la) * Math.sin(lo), Math.sin(la), Math.cos(la) * Math.cos(lo)];
      });
      labelsDirty = true; kick();
    }).catch(function () { T.busy = false; });
  }
  // ── ภัยจริงบนลูกโลก: แผ่นดินไหว (USGS) + พายุ น้ำท่วม ภูเขาไฟ ไฟป่า ภัยแล้ง (GDACS) ─────────────────────
  // ฉายด้วย toScreen() เดียวกับชื่อเมือง จุดจึงอยู่ตรงพิกัดจริงทุกระดับซูม · ดึงใหม่ทุก 10 นาที · ดึงไม่ได้ = ไม่วาด (ไม่เดา)
  // แชร์ให้แผนที่เมือง (city_map.js) ผ่าน window.KD_hazards — ซูมลงถึงระดับถนนก็ยังเห็นจุดเดิม
  var HZ = { list: [], shown: [], at: 0 };
  var HZ_STYLE = { EQ: ['#ffb066', 'quake'], TC: ['#7fe3ff', 'storm'], FL: ['#6fa8ff', 'flood'], VO: ['#ff6b5a', 'volcano'], WF: ['#ffcf5a', 'wildfire'], DR: ['#d9b98a', 'drought'] };
  var HZ_TH = { EQ: 'แผ่นดินไหว', TC: 'พายุหมุนเขตร้อน', FL: 'น้ำท่วม', VO: 'ภูเขาไฟ', WF: 'ไฟป่า', DR: 'ภัยแล้ง' };
  var HZ_EN = { EQ: 'Earthquake', TC: 'Tropical cyclone', FL: 'Flood', VO: 'Volcano', WF: 'Wildfire', DR: 'Drought' };
  var HZ_LV = { green: ['ระดับเขียว', 'Green alert'], orange: ['ระดับส้ม', 'Orange alert'], red: ['ระดับแดง', 'Red alert'] };
  function loadHazards() {
    HZ.at = Date.now();
    var get = function (u) { return fetch(u).then(function (r) { return r.ok ? r.json() : null; }).catch(function () { return null; }); };
    var keep = function (r) { return r && r.ok ? (r.near || []).concat(r.world || []) : []; };
    Promise.all([get('/api/quakes?scope=map'), get('/api/hazards')]).then(function (res) {
      var qs = res[0] && res[0].ok ? (res[0].points || keep(res[0])) : [];     // 7 วัน · ใกล้ไทย M3.5+ · ทั่วโลก M5.5+
      var q = qs.map(function (x) {
        return { lat: x.lat, lon: x.lon, kind: 'EQ', level: x.mag >= 6.5 ? 'red' : x.mag >= 5 ? 'orange' : 'green',
                 name: 'M' + x.mag + ' · ' + (x.place || ''), km: x.km, url: x.url, hours: x.hours };
      });
      // บอกสถานะข้อมูลในแผงเครื่องมือ — คนดูจะรู้ว่า "ไม่มีจุด" เพราะไม่มีเหตุ หรือเพราะดึงข้อมูลไม่ได้
      var st = document.getElementById('ec-hz-status');
      if (st) {
        var nq = q.length, nh = keep(res[1]).length, okq = !!(res[0] && res[0].ok), okh = !!(res[1] && res[1].ok);
        st.textContent = !okq && !okh ? (THAI ? 'ตอนนี้ดึงข้อมูลภัยจาก USGS/GDACS ไม่ได้ — ลองใหม่ภายหลัง' : 'Hazard data from USGS/GDACS is unavailable right now')
          : (THAI ? 'ตอนนี้บนโลก: แผ่นดินไหว 7 วัน ' + (okq ? nq + ' จุด' : '(ดึงไม่ได้)') + ' · ภัยอื่น ' + (okh ? nh + ' จุด' : '(ดึงไม่ได้)')
                  : 'Now: quakes (7 days) ' + (okq ? nq : 'n/a') + ' · other hazards ' + (okh ? nh : 'n/a'));
      }
      var h = keep(res[1]).map(function (x) { return { lat: x.lat, lon: x.lon, kind: x.kind, level: x.level, name: x.name || x.country, km: x.km, url: x.url }; });
      HZ.list = q.concat(h).filter(function (x) { return isFinite(x.lat) && isFinite(x.lon) && HZ_STYLE[x.kind]; }).slice(0, 40);
      HZ.list.forEach(function (x) {
        var la = x.lat * RAD, lo = x.lon * RAD;
        x.w = [Math.cos(la) * Math.sin(lo), Math.sin(la), Math.cos(la) * Math.cos(lo)];
        x.color = HZ_STYLE[x.kind][0];
      });
      window.KD_hazards = HZ.list;
      try { window.dispatchEvent(new Event('kd-hazards')); } catch (e) {}
      labelsDirty = true; kick();
    });
  }
  // กล่องรายละเอียด (DOM ล้วน ไม่ต่อสตริง HTML) — แผนที่เมืองเรียกใช้ตัวเดียวกัน
  window.KD_hazardCard = function (h) {
    var d = document.createElement('div'), en = !THAI, b = document.createElement('b');
    b.textContent = (en ? HZ_EN : HZ_TH)[h.kind] || '';
    d.appendChild(b);
    var lv = HZ_LV[h.level];
    if (lv) d.appendChild(document.createTextNode(' · ' + lv[en ? 1 : 0]));
    function line(t, tag) { d.appendChild(document.createElement('br')); var e = document.createElement(tag || 'span'); e.textContent = t; d.appendChild(e); return e; }
    if (h.name) line(h.name);
    if (h.km != null) line((en ? '{km} km from Bangkok' : 'ห่างกรุงเทพฯ {km} กม.').replace('{km}', Number(h.km).toLocaleString()), 'i');
    if (h.hours != null) line(h.hours < 1 ? (en ? 'within the last hour' : 'ไม่ถึงชั่วโมงที่แล้ว') : h.hours < 48 ? (en ? Math.round(h.hours) + ' h ago' : Math.round(h.hours) + ' ชม.ที่แล้ว')
                                 : (en ? Math.round(h.hours / 24) + ' days ago' : Math.round(h.hours / 24) + ' วันที่แล้ว'), 'i');
    d.appendChild(document.createElement('br'));
    var st = HZ_STYLE[h.kind], g = document.createElement('a');
    g.href = '/survival' + (en ? '?lang=en' : '') + '#' + (st ? st[1] : '');
    g.target = '_blank'; g.rel = 'noopener'; g.textContent = '📘 ' + (en ? 'Survival guide' : 'คู่มือเอาชีวิตรอด');
    d.appendChild(g);
    var ask = document.createElement('a'), kn = (en ? { EQ: 'earthquake', TC: 'typhoon', FL: 'flood', VO: 'volcano eruption', WF: 'wildfire', DR: 'drought' } : HZ_TH)[h.kind] || '';   // คำที่ตัวตรวจภัยรู้จัก
    ask.href = '/?ask=' + encodeURIComponent(en ? 'I am near the ' + kn + ' ' + (h.name || '') + ' — what should I do first?' : 'ฉันอยู่ใกล้' + kn + ' ' + (h.name || '') + ' ตอนนี้ต้องทำอะไรก่อน');
    ask.textContent = '🆘 ' + (en ? 'I am near here · ask LYLA' : 'ฉันอยู่แถวนี้ · ถาม LYLA');
    d.appendChild(document.createElement('br')); d.appendChild(ask);
    if (h.url && /^https:\/\/(?:earthquake\.usgs\.gov|www\.gdacs\.org)\//.test(h.url)) {   // ลิงก์ไปแหล่งทางการเท่านั้น
      var o = document.createElement('a');
      o.href = h.url; o.target = '_blank'; o.rel = 'noopener'; o.textContent = h.kind === 'EQ' ? 'USGS' : 'GDACS';
      d.appendChild(document.createTextNode(' · ')); d.appendChild(o);
    }
    return d;
  };
  var hzPop = document.createElement('div');
  hzPop.className = 'hz-pop hide'; hzPop.setAttribute('role', 'status'); hzPop.setAttribute('aria-live', 'polite');
  wrap.appendChild(hzPop);
  function popOpen() { if (hero) hero.classList.toggle('pop-open', !hzPop.classList.contains('hide') || !!(plPop && !plPop.classList.contains('hide'))); }
  function hideHazard() { hzPop.classList.add('hide'); popOpen(); }
  function hazardAt(px, py) {
    var best = null, bd = 1e9;
    HZ.shown.forEach(function (m) { var d = Math.hypot(px - m.x, py - m.y); if (d < Math.max(22, m.k * 3) && d < bd) { bd = d; best = m; } });
    return best;
  }
  function showHazard(m) {
    hzPop.textContent = ''; hzPop.appendChild(window.KD_hazardCard(m.h));
    var Wc = canvas.clientWidth, Hc = canvas.clientHeight;
    hzPop.style.left = Math.round(clamp(m.x + 14, 8, Math.max(8, Wc - 240))) + 'px';
    hzPop.style.top = Math.round(clamp(m.y - 10, 8, Math.max(8, Hc - 150))) + 'px';
    hzPop.classList.remove('hide'); popOpen();
  }
  function drawHazards(V, Wc, Hc, boxes) {
    HZ.shown = [];
    if (Date.now() - HZ.at > 6e5) loadHazards();
    if (!HZ.list.length) return;
    var k0 = 2.6 + clamp(S.L, 0, 3) * .6;                               // ซูมลงใกล้ จุดใหญ่ขึ้นนิดหน่อย
    lctx.save();
    HZ.list.forEach(function (h) {
      var p = toScreen(V, h.w);
      if (!p || p[0] < -10 || p[0] > Wc + 10 || p[1] < -10 || p[1] > Hc + 10) return;
      var far = clamp(2.4 - p[2] / (V.cam.D * 1.7), .35, 1);
      var big = h.level === 'red' ? 1.6 : h.level === 'orange' ? 1.25 : 1, k = k0 * big;
      lctx.globalAlpha = .55 * far; lctx.strokeStyle = h.color; lctx.lineWidth = 1.5;
      lctx.beginPath(); lctx.arc(p[0], p[1], k * 2.2, 0, 6.283); lctx.stroke();
      lctx.globalAlpha = far; lctx.fillStyle = h.color;
      lctx.beginPath(); lctx.arc(p[0], p[1], k * .8, 0, 6.283); lctx.fill();
      HZ.shown.push({ x: p[0], y: p[1], k: k, h: h });
      boxes.push([p[0] - k * 2.4, p[1] - k * 2.4, p[0] + k * 2.4, p[1] + k * 2.4]);   // ชื่อเมืองหลบจุดภัย
    });
    lctx.restore();
  }
  // ── สถานที่ท่องเที่ยวจริง (Wikidata CC0 — scripts/build_earth_places.py): มรดกโลกทุกแห่ง + ที่เที่ยวสำคัญในไทย ──────────
  // วาดเป็นจุดแสงเล็กๆ ที่เรืองนุ่ม ไม่ใช่หมุด — แสงที่ชี้ทาง ไม่แย่งความสนใจจากโลก · โหลดเมื่อเริ่มซูมลง (ทั้งโลกไม่โหลด)
  // ระดับ 1 (คนรู้จักทั่วโลก) ขึ้นก่อน · ระดับ 2–3 ขึ้นเมื่อมองใกล้ · แถว [อังกฤษ, ไทย, lat, lon, ระดับ, คำอธิบาย, Q-id, มรดกโลก]
  var PL = { data: null, busy: false, shown: [] }, PL_AT = [0, 1.3, 2.3, 3.1];
  // ซ่อนได้: บางคนตาลายเมื่อจุดและชื่อเยอะ — ปุ่มในแผงเครื่องมือ จำไว้ในเครื่อง (kd-places / kd-names = '0' คือซ่อน)
  function lsOn(k) { try { return localStorage.getItem(k) !== '0'; } catch (e) { return true; } }
  var LAYER = { places: lsOn('kd-places'), names: lsOn('kd-names') };
  function loadPlaces() {
    PL.busy = true;
    fetch(base + 'earth/places.json').then(function (r) { return r.json(); }).then(function (d) {
      PL.data = d.places.map(function (r) { var la = r[2] * RAD, lo = r[3] * RAD;
        return { en: r[0], th: r[1], lat: r[2], lon: r[3], tier: r[4], desc: r[5], q: r[6], whs: r[7], w: [Math.cos(la) * Math.sin(lo), Math.sin(la), Math.cos(la) * Math.cos(lo)] }; });
      labelsDirty = true; kick();
    }).catch(function () { PL.busy = false; });
  }
  var plGlow = null;
  function glowSprite() {                                             // แสงนุ่มวาดครั้งเดียว แล้ววางซ้ำ — ไม่สร้าง gradient ทุกเฟรม
    if (plGlow) return plGlow;
    var c = document.createElement('canvas'); c.width = c.height = 32; var g = c.getContext('2d'), gr = g.createRadialGradient(16, 16, 0, 16, 16, 16);
    gr.addColorStop(0, 'rgba(255,248,226,1)'); gr.addColorStop(.18, 'rgba(255,236,190,.75)'); gr.addColorStop(.45, 'rgba(214,200,255,.22)'); gr.addColorStop(1, 'rgba(160,170,255,0)');
    g.fillStyle = gr; g.fillRect(0, 0, 32, 32); return (plGlow = c);
  }
  function drawPlaces(V, Wc, Hc, boxes) {
    PL.shown = [];
    if (!LAYER.places) return;                                        // ผู้ใช้ซ่อนไว้
    if (S.tL < PL_AT[1] - .15) return;
    if (!PL.data) { if (!PL.busy) loadPlaces(); return; }
    var spr = glowSprite(), n = 0, max = Math.min(60, Math.round(Wc * Hc / 9000));
    lctx.save(); lctx.textBaseline = 'middle'; lctx.font = 'italic 500 11px ' + FONT;
    for (var i = 0; i < PL.data.length && n < max; i++) {
      var P = PL.data[i], ta = smooth((S.L - PL_AT[P.tier]) / .4);
      if (ta <= .02) continue;
      var p = toScreen(V, P.w);
      if (!p || p[0] < -10 || p[0] > Wc + 10 || p[1] < 6 || p[1] > Hc - 6) continue;
      var far = clamp(2.4 - p[2] / (V.cam.D * 1.7), 0, 1); if (far <= .05) continue;
      var a = ta * far, r = P.tier === 1 ? 9 : 7;
      lctx.globalAlpha = a * .9; lctx.drawImage(spr, p[0] - r, p[1] - r, r * 2, r * 2);
      PL.shown.push({ x: p[0], y: p[1], P: P }); n++;
      var name = THAI && P.th ? P.th : P.en, show = S.L > PL_AT[P.tier] + .55;
      if (!show) { boxes.push([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6]); continue; }
      var tw = lctx.measureText(name).width + 10, bx = [p[0] - 8, p[1] - 10, p[0] + tw + 8, p[1] + 10], hit = false;
      for (var j = 0; j < boxes.length; j++) { var o = boxes[j]; if (bx[0] < o[2] && bx[2] > o[0] && bx[1] < o[3] && bx[3] > o[1]) { hit = true; break; } }
      if (hit) { boxes.push([p[0] - 6, p[1] - 6, p[0] + 6, p[1] + 6]); continue; }
      boxes.push(bx);
      lctx.globalAlpha = a * .92; lctx.shadowColor = 'rgba(0,0,0,.85)'; lctx.shadowBlur = 4; lctx.fillStyle = '#fff1d2';
      lctx.fillText(name, p[0] + 8, p[1]); lctx.shadowBlur = 0;
    }
    lctx.restore();
  }
  function placeAt(px, py) {
    var best = null, bd = 18;
    PL.shown.forEach(function (m) { var d = Math.hypot(px - m.x, py - m.y); if (d < bd) { bd = d; best = m; } });
    return best;
  }
  // ลิงก์ Google Maps แบบทางการ (Maps URLs) — ไม่ต้องมีคีย์ ไม่มีค่าใช้จ่าย ไม่ได้ดึงข้อมูลของ Google มาวางบนแผนที่เรา
  function gmaps(lat, lon, name) {
    return 'https://www.google.com/maps/search/?api=1&query=' + encodeURIComponent(name ? name : lat.toFixed(5) + ',' + lon.toFixed(5));
  }
  window.KD_gmaps = gmaps;
  var plPop = document.createElement('div');
  plPop.className = 'pl-pop hide'; plPop.setAttribute('role', 'dialog'); plPop.setAttribute('aria-live', 'polite');
  wrap.appendChild(plPop);
  function hidePlace() { plPop.classList.add('hide'); popOpen(); }
  function showPlace(m) {
    var P = m.P, en = !THAI, d = document.createDocumentFragment();
    function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; d.appendChild(e); return e; }
    plPop.textContent = '';
    el('i', 'pl-line');
    if (P.whs) el('span', 'pl-tag', en ? 'UNESCO World Heritage' : 'มรดกโลก UNESCO');
    el('b', 'pl-name', !en && P.th ? P.th : P.en);
    if (!en && P.th && P.th !== P.en) el('span', 'pl-sub', P.en);
    if (P.desc) el('p', 'pl-desc', P.desc);
    var row = el('div', 'pl-row');
    var g = document.createElement('a'); g.href = gmaps(P.lat, P.lon, P.en); g.target = '_blank'; g.rel = 'noopener'; g.textContent = en ? 'Open in Google Maps' : 'เปิดใน Google Maps'; row.appendChild(g);
    var f = document.createElement('button'); f.type = 'button'; f.textContent = en ? 'Fly closer' : 'บินเข้าไปดู';
    f.addEventListener('click', function () { hidePlace(); go({ lat: P.lat, lon: P.lon + 360 * Math.round((S.tlon - P.lon) / 360), L: Math.max(S.tL, 3.6) }); }); row.appendChild(f);
    var w = document.createElement('a'); w.href = 'https://www.wikidata.org/wiki/' + P.q; w.target = '_blank'; w.rel = 'noopener'; w.className = 'pl-src'; w.textContent = 'Wikidata'; row.appendChild(w);
    plPop.appendChild(d);
    var Wc = canvas.clientWidth, Hc = canvas.clientHeight;
    plPop.style.left = Math.round(clamp(m.x + 16, 8, Math.max(8, Wc - 290))) + 'px';
    plPop.style.top = Math.round(clamp(m.y - 20, 8, Math.max(8, Hc - 210))) + 'px';
    plPop.classList.remove('hide'); plPop.classList.remove('lit'); void plPop.offsetWidth; plPop.classList.add('lit'); popOpen();
  }
  function labels() {
    // หัวเว็บค่อยๆ จางเมื่อซูมลง จนหายไปเมื่อเลยวงโคจร — แผนที่จะได้โล่ง
    var heroA = 1 - smooth((S.L - 1.08) / .55);
    if (hero) { hero.style.setProperty('--hero-a', heroA.toFixed(3)); hero.classList.toggle('zoomed', heroA < .99); }
    if (!lctx) return;
    var key = [S.lon.toFixed(3), S.lat.toFixed(3), S.L.toFixed(3), canvas.clientWidth, canvas.clientHeight].join();
    if (key === lastKey && !labelsDirty) return;                       // กล้องไม่ขยับ = ไม่ต้องวาดชื่อใหม่
    lastKey = key; labelsDirty = false;
    var dpr = Math.min(window.devicePixelRatio || 1, 2), Wc = canvas.clientWidth, Hc = canvas.clientHeight;
    if (lab.width !== Math.round(Wc * dpr)) { lab.width = Math.round(Wc * dpr); lab.height = Math.round(Hc * dpr); }
    lctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    lctx.clearRect(0, 0, Wc, Hc);
    var V = view(), boxes = [];
    drawHazards(V, Wc, Hc, boxes);
    drawPlaces(V, Wc, Hc, boxes);                                     // สถานที่วางก่อนชื่อเมือง — ชื่อเมืองหลบแสง
    var show = smooth((S.L - 1.5) / .4);
    if (show <= 0) return;
    if (!LAYER.names) return;                                         // ผู้ใช้ซ่อนชื่อเมืองไว้
    var limit = Math.min(Math.round(26 + 14 * S.mag), Math.round(Wc * Hc / 6500)), drawn = 0;
    lctx.textBaseline = 'middle';
    lctx.shadowColor = 'rgba(0,0,0,.9)';
    for (var ti = 0; ti < TIERS.length && drawn < limit; ti++) {
      var T = TIERS[ti], ta = smooth((S.L - T.at) / .35);
      if (S.tL < T.at - .3 && ta <= 0) continue;
      if (!T.data) { if (!T.busy) fetchTier(T); continue; }
      if (ta < .35) continue;                                          // ยังจางเกินอ่าน — ไม่ต้องขึ้นให้รกจอ
      lctx.font = T.font + FONT;
      for (var i = 0; i < T.data.length && drawn < limit; i++) {
        var c = T.data[i], w = [c[1], c[2], c[3]], p = toScreen(V, w);
        if (!p || p[0] < -20 || p[0] > Wc + 20 || p[1] < 8 || p[1] > Hc - 8) continue;
        var far = clamp(2.4 - p[2] / (V.cam.D * 1.7), 0, 1);           // ชื่อที่อยู่ไกลไปทางขอบฟ้าจางลง
        if (far <= .05) continue;
        var tw = lctx.measureText(c[0]).width + 10, bx = [p[0] - 12, p[1] - 11, p[0] + tw + 10, p[1] + 11], hit = false;
        for (var j = 0; j < boxes.length; j++) {
          var o = boxes[j];
          if (bx[0] < o[2] && bx[2] > o[0] && bx[1] < o[3] && bx[3] > o[1]) { hit = true; break; }
        }
        if (hit) continue;                                              // ชนกับชื่อที่สำคัญกว่า — ข้าม (ชั้นสำคัญวาดก่อน)
        boxes.push(bx); drawn++;
        lctx.globalAlpha = show * ta * far * T.a;
        lctx.fillStyle = T.color;
        lctx.shadowBlur = 0;
        lctx.beginPath(); lctx.arc(p[0], p[1], T.dot, 0, 6.283); lctx.fill();
        lctx.shadowBlur = 4;
        lctx.fillText(c[0], p[0] + 6, p[1]);
      }
    }
    lctx.shadowBlur = 0;
    lctx.globalAlpha = 1;
  }
  // ปุ่ม "ดูดาว": เปิดฟ้าเหนือจุดกลางจอ (ดูอเมริกาอยู่ = ฟ้าอเมริกา) พร้อมชื่อเมืองใกล้สุดที่โหลดไว้แล้ว
  // ปุ่ม Google Maps ในแผงเครื่องมือ: เปิดตรงจุดกลางจอที่กำลังดูอยู่ (ลิงก์ทางการ ไม่มีค่าใช้จ่าย)
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('#ec-gmaps'); if (!a) return;
    var la = clamp(S.tlat, -85, 85), lo = ((S.tlon % 360) + 540) % 360 - 180; a.href = gmaps(la, lo);
  }, true);
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="/sky"]');
    if (!a) return;
    var la = clamp(S.tlat, -89, 89), lo = ((S.tlon % 360) + 540) % 360 - 180, r = RAD;
    var w = [Math.cos(la * r) * Math.sin(lo * r), Math.sin(la * r), Math.cos(la * r) * Math.cos(lo * r)], best = '', bd = Math.cos(2.5 * r);
    TIERS.forEach(function (T) { (T.data || []).forEach(function (c) { var d = c[1] * w[0] + c[2] * w[1] + c[3] * w[2]; if (d > bd) { bd = d; best = c[0]; } }); });
    a.href = '/sky?lat=' + la.toFixed(2) + '&lon=' + lo.toFixed(2) + (best ? '&name=' + encodeURIComponent(best) : '');
  }, true);
  sync(); setTouchMode(); size();
})();
