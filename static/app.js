/* static/app.js — สคริปต์หลักของหน้าแรก (static/index.html) · แยกออกมาให้แก้ง่าย ไม่พันกับ HTML/CSS */
'use strict';
/* ════════════════════════════════════════════════════════════════
   UTIL
   ════════════════════════════════════════════════════════════════ */
var $ = function(s, r){ return (r||document).querySelector(s); };
var $$ = function(s, r){ return Array.prototype.slice.call((r||document).querySelectorAll(s)); };
function esc(t){ return String(t == null ? '' : t).replace(/[&<>"']/g, function(c){ return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]; }); }
function fmt(t){ return esc(t).replace(/\*\*([^*\n]+)\*\*/g,'<strong>$1</strong>').replace(/\n/g,'<br>'); }
/* เบอร์สายด่วนในคำตอบ → แตะโทรได้ทันทีบนมือถือ (ไม่แตะจำนวนเงิน เช่น "1300 บาท")
   รวมเบอร์ในคำตอบ 54 ภาษา (110 จีน · 119 ญี่ปุ่น · 109 เกาหลี · 3114 ฝรั่งเศส ฯลฯ) — เดิมแตะโทรได้แค่เบอร์ไทยกับ 911/988/112/999 */
var HOTLINES = /(^|[^\d\w.\/:-])(191|1669|1323|1300|1367|1784|1650|1599|1155|1111|1441|1213|1195|1387|1506|1330|1192|1567|1586|1543|1413|1165|1600|1663|1546|1694|1129|1130|1422|1584|1166|1167|1186|1205|1207|1362|1366|1570|199|911|988|112|999|016|101|102|103|108|109|110|113|115|116|119|124|142|155|158|166|188|190|192|194|1018|1122|1201|1480|1553|1813|1926|1990|3114|7333|9110)(?![\d.,]|\s*(?:บาท|฿|baht|ปี|คน|ครั้ง|%))/g;
function telify(html){ return html.replace(HOTLINES, '$1<a class="tel" href="tel:$2">$2</a>'); }
function lsGet(k){ try{ return localStorage.getItem(k); }catch(_){ return null; } }
/* แปลข้อความที่สคริปต์ประกอบเอง (มีตัวเลข/ชื่อแทรก หรืออยู่ในกล่องแชทที่ตัวแปลอัตโนมัติไม่แตะ)
   _t('รหัสกู้คืนเหลือ {n} ชุด', {n: 8}) — คำแปลอยู่ใน static/i18n.js · ไม่มีคำแปลก็คืนภาษาไทย */
function _t(s, v){ var o = window.KD_I18N ? KD_I18N.t(s) : s; return v ? o.replace(/\{(\w+)\}/g, function(m, k){ return v[k] != null ? v[k] : m; }) : o; }
function lsSet(k,v){ try{ localStorage.setItem(k,v); }catch(_){} }
function lsDel(k){ try{ localStorage.removeItem(k); }catch(_){} }
function num(v, d){ var n = Number(v); return isFinite(n) ? n : d; }
function sleep(ms){ return new Promise(function(r){ setTimeout(r, ms); }); }
/* ลดการเคลื่อนไหว: ตั้งในมือถือ หรือกดปุ่มในเมนูสี (ค่าเดียวกับหน้า Universe และฉากบิ๊กแบง · kd-calm) */
var REDUCED = matchMedia('(prefers-reduced-motion: reduce)').matches;
try{ if(localStorage.getItem('kd-calm') === '1'){ REDUCED = true; document.documentElement.classList.add('kd-calm'); } }catch(_){}
/* โหมดสี: night (อวกาศเดิม) · day · latte (คอสมิกลาเต้ #FFF8E7 — สีเฉลี่ยของจักรวาล) · custom (สีที่ผู้ใช้เลือก)
   THEME.v = สีพื้น (null = กลางคืน) · THEME.dark = ตัวหนังสือเข้มบนพื้นสว่าง — ฉากอวกาศและตัวหนังสือบนผืนผ้าใช้ค่านี้ */
var THEME = { t: 'night', c: '#e8dcff', v: null, dark: false };
function applyTheme(t, c){
  if(c && /^#[0-9a-f]{6}$/i.test(c)) THEME.c = c.toLowerCase();
  var v = window.KD_themeVars ? KD_themeVars(t, THEME.c) : null, h = document.documentElement;
  THEME.t = v ? t : 'night'; THEME.v = v; THEME.dark = !!(v && v.ink === 'dark');
  h.setAttribute('data-theme', THEME.t);
  if(v){ h.setAttribute('data-ink', v.ink); h.style.setProperty('--paper', v.p); } else { h.removeAttribute('data-ink'); h.style.removeProperty('--paper'); }
  var tc = document.querySelector('meta[name="theme-color"]'); if(tc) tc.setAttribute('content', v ? v.p : '#04050d');
  try{ localStorage.setItem('kd-theme', THEME.t); localStorage.setItem('kd-theme-color', THEME.c); }catch(_){}
  var sw = document.getElementById('theme-custom-sw'); if(sw) sw.style.background = THEME.c;
  var ci = document.getElementById('theme-color'); if(ci && ci.value !== THEME.c) ci.value = THEME.c;
  var bs = document.querySelector('#theme-btn .sw'); if(bs) bs.style.background = v ? v.p : '#0b0e22';
  document.querySelectorAll('[data-theme-pick]').forEach(function(b){ b.classList.toggle('on', b.getAttribute('data-theme-pick') === THEME.t); });
  if(window.KD_kick) KD_kick();
}
(function(){ var h = document.documentElement, t = h.getAttribute('data-theme') || 'night', c = '#e8dcff';
  try{ c = localStorage.getItem('kd-theme-color') || c; }catch(_){} THEME.c = /^#[0-9a-f]{6}$/i.test(c) ? c : '#e8dcff';
  var v = window.KD_themeVars ? KD_themeVars(t, THEME.c) : null; THEME.t = v ? t : 'night'; THEME.v = v; THEME.dark = !!(v && v.ink === 'dark'); })();

var _toastT = null;
function toast(msg, bad, ms){
  var el = $('#toast'); el.textContent = msg; el.className = 'on' + (bad ? ' bad' : '');
  clearTimeout(_toastT); _toastT = setTimeout(function(){ el.className = ''; }, ms || 4200);
}
async function readJson(res){
  var txt = await res.text(), data = null;
  try{ data = JSON.parse(txt); }catch(_){}
  if(!res.ok){
    if(!data && (res.status===502 || res.status===503 || res.status===504))
      throw new Error('เซิร์ฟเวอร์กำลังตื่น (Render cold start) — รอสัก 30 วินาทีแล้วลองใหม่');
    var m = data && (data.error || data.detail);
    if(m && typeof m !== 'string') m = JSON.stringify(m);
    var err = new Error(m || ('HTTP ' + res.status)); err.status = res.status; err.data = data; throw err;
  }
  if(data === null) throw new Error('เซิร์ฟเวอร์ตอบกลับไม่ใช่ JSON — อาจยังไม่ตื่น ลองใหม่อีกครั้ง');
  return data;
}
/* retry เฉพาะตอนเน็ตหลุด / เซิร์ฟเวอร์ยังไม่ตื่น — ไม่ retry 429 */
async function fetchRetry(url, opts, tries){
  tries = tries || 3;
  for(var i=0; i<tries; i++){
    try{
      var r = await fetch(url, opts);
      if((r.status===502 || r.status===503 || r.status===504) && i < tries-1){
        toast(_t('เซิร์ฟเวอร์ยังไม่พร้อม กำลังลองใหม่ ({i}/{n})', {i: i+1, n: tries}));
        await sleep(1500 * Math.pow(2, i)); continue;
      }
      return r;
    }catch(e){
      if(i === tries-1) throw new Error('เชื่อมต่อเซิร์ฟเวอร์ไม่ได้ — ตรวจอินเทอร์เน็ตแล้วลองใหม่');
      await sleep(1500 * Math.pow(2, i));
    }
  }
}

/* ════════════════════════════════════════════════════════════════
   SYSTEM MAP DATA — ข้อมูลจริงจาก repo (ฝังไว้ใน #system-map)
   ════════════════════════════════════════════════════════════════ */
var MAP = (function(){ try{ return JSON.parse($('#system-map').textContent); }catch(_){ return {commit:'', files:[]}; } })();
var CATS = [
  ['boot',    'ทำงานตอนบูต',        'โหลดทันทีที่เซิร์ฟเวอร์เริ่ม และอยู่ในเส้นทางของ /run'],
  ['request', 'ทำงานตอนตอบ',        'ถูก import ตอนมีข้อความเข้ามา ผ่าน system_orchestrator'],
  ['web',     'หน้าเว็บที่ใช้อยู่',   'หน้าและไฟล์ที่ FastAPI เสิร์ฟจริง'],
  ['broken',  'เสีย',               'import ไม่ได้ หรือเรียกสิ่งที่ไม่มีอยู่จริง'],
  ['dormant', 'รอต่อสาย',           'มีประโยชน์จริงแต่ต้องมีสิ่งเพิ่มก่อน (ตำแหน่งผู้ใช้, API key, ปุ่ม feedback)'],
  ['legacy',  'รุ่นเก่า',           'รุ่นแรกของสิ่งที่ทำงานอยู่แล้ว — เก็บไว้อ้างอิง ไม่ควรต่อซ้ำ'],
  ['vision',  'วิสัยทัศน์',          'แนวคิดระยะยาว (โลก/เครือข่าย/อารยธรรม) — รอข้อมูลจริงก่อนต่อ'],
  ['tests',   'เทสต์',              'pytest กันบั๊กที่ซ่อมแล้วไม่ให้กลับมา'],
  ['pkg',     'ไฟล์บอกโฟลเดอร์',     '__init__.py ที่ทำให้โฟลเดอร์เป็น package'],
  ['docs',    'เอกสาร',             'Markdown อธิบายแนวคิด ไม่ถูกโหลดโดยโค้ด'],
  ['site',    'เว็บ GitHub Pages',  'หน้าเว็บ/ไฟล์ของ docs site แยกจากแอป'],
  ['config',  'ตั้งค่า',             'requirements, render.yaml, launch.json'],
  ['artifact','ไฟล์ build',          '.pyc ที่ถูก commit ติดมา']
];
var CAT_NAME = {}; CATS.forEach(function(c){ CAT_NAME[c[0]] = c[1]; });

/* ════════════════════════════════════════════════════════════════
   AUTH  (GET /me · POST /logout)
   ════════════════════════════════════════════════════════════════ */
var Auth = { loggedIn:false, email:'', premium:false, credits:null, freeLeft:null, freeLimit:20 };
async function refreshMe(){
  var was = Auth.email;
  try{
    var d = await readJson(await fetch('/me', {credentials:'same-origin'}));
    Auth.loggedIn = !!d.logged_in; Auth.email = d.logged_in ? (d.email || d.name || '') : '';
    Auth.premium = !!d.premium; Auth.admin = !!d.admin; Auth.credits = d.logged_in ? num(d.credits, 0) : null;
    Limit.set(d);
  }catch(_){ Auth.loggedIn = false; Auth.email = ''; Auth.credits = null; }
  $('#acc-guest').classList.toggle('hide', Auth.loggedIn);
  $('#acc-user').classList.toggle('hide', !Auth.loggedIn);
  $('#acc-email').textContent = Auth.email;
  $('#credits-pill').textContent = Auth.premium ? '∞' : Auth.loggedIn ? 'CR ' + Auth.credits : 'FREE ' + (Auth.freeLeft == null ? '—' : Auth.freeLeft);
  var pe = $('#pay-email'); if(pe && !pe.value && Auth.email.indexOf('@') > 0) pe.value = Auth.email;
  Limit.ui();
  $('#card-2fa').classList.toggle('hide', !Auth.loggedIn);
  $('#card-biz').classList.toggle('hide', !Auth.admin); if(Auth.admin) Biz.load();
  $('#card-del').classList.toggle('hide', !Auth.loggedIn);
  if(Auth.loggedIn) TFA.load();
  return was !== Auth.email;
}
/* ── ลบบัญชี (/api/account/delete) — พิมพ์อีเมลยืนยัน · เปิด 2FA อยู่ต้องกรอกรหัส · สำเร็จแล้วล้างแชทในเครื่องและกลับหน้าแรก ── */
$('#del-go').addEventListener('click', function(){
  var msg = $('#del-msg'), body = {confirm: $('#del-confirm').value.trim(), code: $('#del-code').value.trim()};
  if(body.confirm.toLowerCase() !== String(Auth.email || '').toLowerCase()){ msg.className = 'bad'; msg.textContent = _t('พิมพ์อีเมลของบัญชีนี้ให้ตรงก่อนนะคะ'); return; }
  if(!confirm(_t('ลบบัญชีถาวร ย้อนกลับไม่ได้ — แน่ใจไหมคะ?'))) return;
  fetch('/api/account/delete', {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body)})
    .then(function(r){ return r.json().then(function(d){ return {ok: r.ok, d: d}; }); })
    .then(function(x){
      if(x.ok && x.d.deleted){
        try{ Object.keys(localStorage).forEach(function(k){ if(/^kd/i.test(k)) localStorage.removeItem(k); }); }catch(_){}
        msg.className = 'ok'; msg.textContent = _t('ลบบัญชีเรียบร้อยแล้ว ขอบคุณที่เคยใช้ KING DIADEM นะคะ');
        setTimeout(function(){ location.href = '/'; }, 1600); return;
      }
      if(x.d && x.d.need_code) $('#del-code-row').classList.remove('hide');
      msg.className = 'bad'; msg.textContent = (x.d && x.d.error) || _t('ลบบัญชีไม่สำเร็จ ลองใหม่อีกครั้งนะคะ');
    }).catch(function(){ msg.className = 'bad'; msg.textContent = _t('ลบบัญชีไม่สำเร็จ ลองใหม่อีกครั้งนะคะ'); });
});
/* ── การยืนยันสองชั้น (/api/2fa) — ปิดอยู่ → ตั้งค่า (เปิดแอป/คัดลอกกุญแจ → กรอกรหัสแรก) → รหัสกู้คืน → เปิดอยู่ ── */
/* ── ตัวเลขธุรกิจ (เฉพาะเจ้าของ · ADMIN_EMAILS) — เส้นทางจากคนเข้าเว็บจนถึงคนจ่ายเงิน ──
   ดูว่าคนหลุดที่ขั้นไหน: เข้าแล้วไม่คุย = หน้าแรกยังไม่ชวน · คุยแต่ไม่ถึงเพดาน = ฟรีพอใช้ · ถึงเพดานแต่ไม่จ่าย = ราคา/คุณค่ายังไม่ชัด */
var Biz = (function(){
  var body = $('#biz-body');
  function pct(a, b){ return b ? Math.round(a / b * 1000) / 10 + '%' : '—'; }
  function n(v){ return Number(v || 0).toLocaleString(); }
  /* ภาพรวมคำถามทั้งระบบ (ENGINE/self_learning) — ความเสี่ยงเฉลี่ยกำลังดีขึ้นหรือแย่ลง */
  function learnHTML(L){
    if(!L) return '';
    if(L.status !== 'active') return '<p class="muted biz-note">' + _t('ภาพรวมคำถาม: ยังเก็บข้อมูลอยู่ ({n}/3)', {n: Number(L.records) || 0}) + '</p>';
    var tr = {improving: _t('ดีขึ้น'), degrading: _t('แย่ลง'), stable: _t('ทรงตัว')}[L.trend] || L.trend;
    return '<p class="biz-sum">' + _t('ภาพรวม {n} คำถามล่าสุด · แนวโน้ม{t} · เรื่องเสี่ยงสูง {h}%', {n: n(L.records), t: esc(tr), h: Math.round((Number(L.high_risk_ratio) || 0) * 100)}) +
      (L.avg_waterline != null ? ' · ' + _t('waterline เฉลี่ย {w} (จาก {k} คนที่กรอกสถานะ)', {w: Math.round(L.avg_waterline), k: n(L.with_state)}) : '') + '</p>' +
      (L.drift_detected ? '<p class="warn biz-note">' + _t('entropy เพิ่มต่อเนื่อง 5 รอบ — ผู้ใช้ช่วงนี้กำลังเครียดขึ้น') + '</p>' : '');
  }
  function render(d){
    var t = d.total, paid = t['u:purchase'] + t['u:renewal'];
    var steps = [
      [_t('คนเข้าเว็บ'), t['u:visitor'], ''],
      [_t('คนที่ลองคุย'), t['u:chatter'], pct(t['u:chatter'], t['u:visitor'])],
      [_t('ใช้ฟรีหมดวัน'), t['u:paywalled'], pct(t['u:paywalled'], t['u:chatter'])],
      [_t('กดไปหน้าจ่าย'), t.checkout, pct(t.checkout, t['u:paywalled'])],
      [_t('จ่ายจริง'), paid, pct(paid, t.checkout)]
    ], top = Math.max(1, steps[0][1]);
    var h = '<div class="biz-funnel">' + steps.map(function(s){
      return '<div class="bf-row"><span class="bf-k">' + esc(s[0]) + '</span><span class="bf-bar"><i style="width:' + Math.max(1.5, s[1] / top * 100) + '%"></i></span>' +
        '<b>' + n(s[1]) + '</b><span class="bf-p">' + s[2] + '</span></div>';
    }).join('') + '</div>' +
      '<p class="biz-sum">' + _t('รายได้ 30 วัน ฿{b} · สมัครใหม่ {s} คน · ข้อความทั้งหมด {m}', {b: n(t.baht), s: n(t['u:signup']), m: n(t.chat)}) + '</p>' +
      learnHTML(d.learning) +
      '<details class="biz-days"><summary>' + _t('ดูรายวัน') + '</summary><table><tr><th>' + _t('วัน') + '</th><th>' + _t('เข้า') + '</th><th>' + _t('คุย') + '</th><th>' + _t('ฟรีหมด') + '</th><th>' + _t('จ่าย') + '</th><th>฿</th></tr>' +
      d.series.slice(0, 14).map(function(r){
        return '<tr><td>' + esc(r.day.slice(5)) + '</td><td>' + n(r['u:visitor']) + '</td><td>' + n(r['u:chatter']) + '</td><td>' + n(r['u:paywalled']) + '</td><td>' + n(r['u:purchase'] + r['u:renewal']) + '</td><td>' + n(r['baht:purchase'] + r['baht:renewal']) + '</td></tr>';
      }).join('') + '</table></details>' +
      '<p class="muted biz-note">' + _t('นับเฉพาะจำนวน ไม่เก็บข้อความ อีเมล หรือ IP · เริ่มนับตั้งแต่ติดตั้งระบบนี้') + '</p>';
    body.innerHTML = h;
  }
  function load(){
    fetch('/api/admin/metrics?days=30', {credentials:'same-origin', cache:'no-store'}).then(readJson).then(render)
      .catch(function(){ body.innerHTML = '<p class="muted">' + _t('ดูตัวเลขไม่ได้ชั่วคราว') + '</p>'; });
  }
  return { load: load };
})();
var TFA = (function(){
  var body = $('#tfa-body');
  function post(url, data){ return fetch(url, {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify(data || {})}).then(readJson); }
  function codeRow(btnText, id){ return '<div class="tfa-row"><input class="inp" id="tfa-code" inputmode="numeric" autocomplete="one-time-code" maxlength="11" placeholder="123456" aria-label="รหัส 6 หลัก"><button type="button" class="btn primary" id="' + id + '">' + btnText + '</button></div><p class="muted" id="tfa-msg"></p>'; }
  function fail(e){ var m = $('#tfa-msg'); if(m){ m.className = 'bad'; m.textContent = e.message || 'ยังไม่สำเร็จ ลองใหม่อีกครั้งนะคะ'; } }
  function off(){
    body.innerHTML = '<p>เพิ่มชั้นป้องกันอีกชั้น: นอกจากรหัสผ่าน ต้องกรอกรหัส 6 หลักจากแอปในมือถือด้วย ใครรู้รหัสผ่านก็เข้าบัญชีไม่ได้</p>' +
      '<p class="muted">ใช้แอปไหนก็ได้ เช่น Google Authenticator · Microsoft Authenticator · 1Password</p>' +
      '<button type="button" class="btn primary" id="tfa-start">เปิดใช้การยืนยันสองชั้น</button>';
    $('#tfa-start').addEventListener('click', function(){ post('/api/2fa/setup').then(setup).catch(function(e){ toast(e.message || 'เริ่มตั้งค่าไม่ได้', true); }); });
  }
  function setup(d){
    var key = String(d.secret || '').replace(/(.{4})/g, '$1 ').trim();
    /* QR มาจากเซิร์ฟเวอร์ของเราเอง (SVG ล้วน) — ยังกันไว้อีกชั้น: รับเฉพาะ <svg> ที่ไม่มีสคริปต์/ตัวจัดการเหตุการณ์ */
    var qr = typeof d.qr === 'string' && /^<svg[\s>]/.test(d.qr) && !/<script|\son\w+=|href=/i.test(d.qr) ? d.qr : '';
    body.innerHTML = (qr ? '<p><b>1.</b> สแกน QR นี้ด้วยแอป Authenticator ในมือถือ</p><div class="tfa-qr" id="tfa-qr"></div>' +
        '<p class="muted">ถ้ากำลังใช้มือถือเครื่องเดียวกัน แตะปุ่มนี้แทน</p>'
      : '<p><b>1.</b> บนมือถือ แตะปุ่มนี้เพื่อเพิ่มบัญชีในแอป Authenticator</p>') +
      '<p><a class="btn" id="tfa-open">เปิดในแอป Authenticator</a></p>' +
      '<p class="muted">หรือในแอปเลือก "ใส่กุญแจเอง" แล้วพิมพ์กุญแจนี้ (แบบตามเวลา):</p><div class="tfa-key" id="tfa-key"></div>' +
      '<p><b>2.</b> กรอกรหัส 6 หลักที่แอปแสดงตอนนี้</p>' + codeRow('ยืนยันและเปิดใช้', 'tfa-enable');
    $('#tfa-open').setAttribute('href', d.uri); $('#tfa-key').textContent = key;
    if(qr) $('#tfa-qr').innerHTML = qr;
    $('#tfa-enable').addEventListener('click', function(){
      post('/api/2fa/enable', { code: $('#tfa-code').value }).then(recovery).catch(fail);
    });
  }
  function recovery(d, fresh){
    var codes = d.recovery_codes || [];
    body.innerHTML = (fresh ? '<p class="ok"><b>✓ ได้รหัสกู้คืนชุดใหม่แล้ว</b> ชุดเก่าใช้ไม่ได้อีกต่อไป</p>'
        : '<p class="ok"><b>✓ เปิดการยืนยันสองชั้นแล้ว</b> เครื่องอื่นที่เคยล็อกอินไว้ถูกออกจากระบบแล้ว</p>') +
      '<p>' + _t('เก็บ <b>รหัสกู้คืน</b> ไว้ที่ปลอดภัย (จดใส่กระดาษหรือตัวจัดการรหัสผ่าน) ใช้ตอนทำมือถือหาย ชุดละครั้ง — หน้านี้แสดงครั้งเดียวเท่านั้น อย่าส่งให้ใครนะคะ') + '</p>' +
      '<div class="tfa-codes" id="tfa-codes"></div>' +
      '<div class="tfa-row"><button type="button" class="btn" id="tfa-copy">คัดลอกรหัสกู้คืน</button><button type="button" class="btn primary" id="tfa-done">เก็บไว้แล้ว</button></div>';
    var box = $('#tfa-codes'); codes.forEach(function(c){ var s = document.createElement('span'); s.textContent = c; box.appendChild(s); });
    $('#tfa-copy').addEventListener('click', function(){ try{ navigator.clipboard.writeText(codes.join('\n')); toast('คัดลอกแล้ว'); }catch(_){ toast('คัดลอกไม่ได้ ลองจดไว้แทนนะคะ', true); } });
    $('#tfa-done').addEventListener('click', load);
  }
  function on(d){
    body.innerHTML = '<p class="ok"><b>✓ เปิดอยู่</b> — เข้าสู่ระบบต้องกรอกรหัสจากแอปทุกครั้ง</p>' +
      '<p class="muted">' + _t((Number(d.recovery_left) || 0) < 3 ? 'รหัสกู้คืนเหลือ {n} ชุด — ใกล้หมดแล้ว กดสร้างชุดใหม่ได้เลย' : 'รหัสกู้คืนเหลือ {n} ชุด', {n: Number(d.recovery_left) || 0}) + '</p>' +
      '<p>กรอกรหัส 6 หลักจากแอป แล้วเลือกสิ่งที่จะทำ</p>' + codeRow('สร้างรหัสกู้คืนชุดใหม่', 'tfa-regen') +
      '<p class="muted">รหัสกู้คืนหลุดหรือหาไม่เจอ สร้างชุดใหม่ได้ ชุดเก่าจะใช้ไม่ได้ทันที · ปิดการยืนยันสองชั้นใช้รหัสกู้คืนแทนรหัสจากแอปได้</p>' +
      '<p><button type="button" class="btn" id="tfa-off">ปิดการยืนยันสองชั้น</button></p>';
    $('#tfa-regen').addEventListener('click', function(){
      if(!confirm(_t('สร้างรหัสกู้คืนชุดใหม่? ชุดเก่าทั้งหมดจะใช้ไม่ได้ทันที'))) return;
      post('/api/2fa/recovery', { code: $('#tfa-code').value }).then(function(r){ recovery(r, true); }).catch(fail);
    });
    $('#tfa-off').addEventListener('click', function(){
      if(!confirm(_t('ปิดการยืนยันสองชั้น? บัญชีจะเหลือแค่รหัสผ่านอย่างเดียว'))) return;
      post('/api/2fa/disable', { code: $('#tfa-code').value }).then(function(){ toast('ปิดการยืนยันสองชั้นแล้ว'); load(); }).catch(fail);
    });
  }
  function load(){
    fetch('/api/2fa', {credentials:'same-origin', cache:'no-store'}).then(readJson).then(function(d){ (d.enabled ? on : off)(d); })
      .catch(function(){ body.innerHTML = '<p class="muted">ดูสถานะไม่ได้ชั่วคราว</p>'; });
  }
  return { load: load };
})();
/* ── ความจำข้ามแชท (/api/memory) ── */
var MEM_TH = { goal_general:'เป้าหมาย', goal_vega:'เป้าหมาย', goal_risk:'เป้าหมาย', goal_survival:'เป้าหมาย', goal_collapse:'เป้าหมาย', goal_civil:'เป้าหมาย',
  crisis_context:'สถานการณ์ที่ยาก', recent_topics:'หัวข้อที่เคยคุย', sensitive_checkin:'ช่วงที่หนัก' };
async function loadMemory(){
  var box = $('#mem-list');
  try{
    var d = await readJson(await fetch('/api/memory', {credentials:'same-origin', cache:'no-store'}));
    $('#mem-on').checked = !!d.enabled;
    var items = Array.isArray(d.items) ? d.items : [];
    box.innerHTML = items.length ? items.map(function(m){ return '<li><b>' + esc(MEM_TH[m.key] || m.key) + '</b> ' + esc(m.content) + '</li>'; }).join('')
      : '<li class="muted">ยังไม่มีอะไรที่จำไว้</li>';
  }catch(e){ box.innerHTML = '<li class="muted">' + esc(e.message || 'ดูความจำไม่ได้ชั่วคราว') + '</li>'; }
}
async function memAction(action){
  try{ await readJson(await fetch('/api/memory', {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify({action:action})})); }
  catch(e){ toast(e.message || 'ตั้งค่าความจำไม่ได้', true); }
  loadMemory();
}
/* ── ประวัติการปรึกษาในบัญชี: ดาวน์โหลด · ส่งเข้าอีเมลของบัญชี (/api/history) ── */
async function loadHistory(){
  var info = $('#hist-info'), mail = $('#hist-mail');
  try{
    var d = await readJson(await fetch('/api/history', {credentials:'same-origin', cache:'no-store'}));
    var n = Number(d.count) || 0;
    info.textContent = n ? _t('เก็บไว้ในบัญชีนี้ {n} ครั้ง · ส่งออกได้เฉพาะของคุณ', {n: n.toLocaleString()}) : _t('ยังไม่มีประวัติในบัญชีนี้');
    $('#hist-dl').classList.toggle('hide', !n);
    mail.disabled = !n || !d.email_ready;
    mail.title = d.email_ready ? _t('ส่งไปที่ {e}', {e: d.email || ''}) : _t('ระบบยังส่งอีเมลไม่ได้ — ดาวน์โหลดแทนได้');
  }catch(e){ info.textContent = e.message || 'ดูประวัติไม่ได้ชั่วคราว'; mail.disabled = true; }
}
$('#hist-mail').addEventListener('click', async function(){
  var b = this; b.disabled = true;
  try{
    var d = await readJson(await fetch('/api/history/email', {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body:'{}'}));
    toast(_t('ส่งประวัติ {n} ครั้งไปที่ {to} แล้วค่ะ', {n: d.count || 0, to: d.sent_to || _t('อีเมลของคุณ')}));
  }catch(e){ toast(e.message || 'ส่งอีเมลไม่สำเร็จ', true); }
  setTimeout(function(){ loadHistory(); }, 400);
});
$('#mem-open').addEventListener('click', function(){ loadMemory(); loadHistory(); $('#dlg-mem').showModal(); });
$('#mem-on').addEventListener('change', function(){ memAction(this.checked ? 'on' : 'off'); });
$('#mem-clear').addEventListener('click', function(){ if(confirm(_t('ล้างทุกอย่างที่ LYLA จำไว้? ย้อนกลับไม่ได้'))) memAction('clear'); });
$('#logout').addEventListener('click', async function(){
  try{ Chat.persist(); await Cloud.push(); }catch(_){}
  try{ await fetch('/logout', {method:'POST', headers:{'Content-Type':'application/json'}, body:'{}'}); }catch(_){}
  location.reload();
});

/* ════════════════════════════════════════════════════════════════
   CHAT STORE — เก็บเป็นข้อมูล (ไม่เก็บ HTML) · ย้ายข้อมูลจากรุ่น v4 อัตโนมัติ
   ════════════════════════════════════════════════════════════════ */
function b64(s){ try{ return btoa(unescape(encodeURIComponent(s))).replace(/=/g,''); }catch(_){ return 'guest'; } }
function keyV5(){ return 'kd_chat_v5_' + b64(Auth.email || 'guest'); }
function keyV4(){ var e = Auth.email || 'guest'; try{ return 'kd_sessions_v4_' + btoa(encodeURIComponent(e)).replace(/=/g,''); }catch(_){ return 'kd_sessions_v4_guest'; } }
function newId(){ return 's' + Date.now().toString(36) + Math.random().toString(36).slice(2,6); }
function freshState(){ var id = newId(); return { v:5, active:id, items:[{id:id, title:'แชทใหม่', msgs:[]}], savedAt:0 }; }
/* แปลง HTML ของรุ่นเก่าเป็นข้อความ — DOMParser สร้างเอกสารเฉื่อย ไม่รันสคริปต์ ไม่โหลดรูป */
function htmlToMsgs(html){
  if(!html || typeof html !== 'string') return [];
  try{
    var doc = new DOMParser().parseFromString('<div id="r">' + html + '</div>', 'text/html');
    return $$('.msg', doc).filter(function(m){ return m.id !== 'thinking-msg'; }).map(function(m){
      var t = m.querySelector('.msg-text'); if(!t) return null;
      $$('br', t).forEach(function(b){ b.replaceWith('\n'); });
      var txt = (t.textContent || '').trim(); if(!txt) return null;
      return { r: m.classList.contains('user') ? 'u' : 'a', t: txt };
    }).filter(Boolean);
  }catch(_){ return []; }
}
function cleanTrace(tr){ try{ return tr && typeof tr === 'object' ? JSON.parse(JSON.stringify(tr)) : null; }catch(_){ return null; } }
function normalize(s){
  if(!s || typeof s !== 'object' || !Array.isArray(s.items) || !s.items.length) return null;
  var items = s.items.slice(0, 200).map(function(it){
    it = it || {};
    var msgs = Array.isArray(it.msgs) ? it.msgs.filter(function(m){ return m && typeof m.t === 'string'; }).map(function(m){
      return { r: (m.r==='u' || m.r==='e') ? m.r : 'a', t: m.t, p: typeof m.p === 'string' ? m.p : '', tr: cleanTrace(m.tr), l: Array.isArray(m.l) ? cleanTrace(m.l.slice(0, 3)) : undefined, v: (m.v === 'up' || m.v === 'down') ? m.v : undefined, ts: num(m.ts, 0) };
    }) : htmlToMsgs(it.html);
    return { id: String(it.id || newId()), title: String(it.title || 'แชท').slice(0, 60), msgs: msgs.slice(-400) };
  });
  var active = items.some(function(x){ return x.id === s.active; }) ? String(s.active) : items[0].id;
  return { v:5, active:active, items:items, savedAt: num(s.savedAt, 0) };
}
var Chat = {
  s: null,
  load: function(){
    var st = null;
    try{ st = normalize(JSON.parse(lsGet(keyV5()))); }catch(_){}
    if(!st){ try{ st = normalize(JSON.parse(lsGet(keyV4()))); }catch(_){} }
    this.s = st || freshState();
  },
  save: function(){ lsSet(keyV5(), JSON.stringify(this.s)); },
  persist: function(){ this.s.savedAt = Date.now(); this.save(); Cloud.schedule(); },
  cur: function(){ var s = this.s; return s.items.find(function(x){ return x.id === s.active; }) || s.items[0]; },
  push: function(m){ m.ts = Date.now(); this.cur().msgs.push(m); this.persist(); },
  select: function(id){ this.s.active = id; this.save(); renderAll(); setView('chat'); closeDrawer(); },
  create: function(){
    var c = this.cur();
    if(c && !c.msgs.length){ this.select(c.id); $('#input').focus(); return; }
    var id = newId(); this.s.items.unshift({id:id, title:'แชทใหม่', msgs:[]}); this.s.active = id;
    this.persist(); renderAll(); setView('chat'); closeDrawer(); $('#input').focus();
  },
  remove: function(id){
    var s = this.s, i = s.items.findIndex(function(x){ return x.id === id; }); if(i < 0) return;
    s.items.splice(i, 1);
    if(!s.items.length){ var f = freshState(); s.items = f.items; s.active = f.active; }
    else if(s.active === id) s.active = s.items[Math.max(0, i-1)].id;
    this.persist(); renderAll();
  },
  rename: function(text){
    var c = this.cur(); if(!c || !/^(แชทใหม่|แชท\s*\d*)$/.test(c.title)) return;
    c.title = text.replace(/\s+/g,' ').trim().slice(0, 40); this.save(); renderSessions();
  }
};
/* ── sync กับบัญชี (GET/PUT /api/chat-state) ───────────────────── */
var Cloud = {
  t: null,
  schedule: function(){ if(!Auth.loggedIn) return; clearTimeout(this.t); this.t = setTimeout(function(){ Cloud.push(); }, 1800); },
  push: async function(){
    if(!Auth.loggedIn) return;
    try{ await fetch('/api/chat-state', {method:'PUT', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify({state: Chat.s})}); }catch(_){}
  },
  pull: async function(){
    if(!Auth.loggedIn) return;
    try{
      var d = await readJson(await fetch('/api/chat-state', {credentials:'same-origin'}));
      var remote = normalize(d && d.state);
      if(remote && remote.savedAt >= (Chat.s.savedAt || 0)){ Chat.s = remote; Chat.save(); renderAll(); }
      else if(Chat.s.items.some(function(x){ return x.msgs.length; })) await Cloud.push();
    }catch(_){}
  }
};
addEventListener('pagehide', function(){
  if(!Auth.loggedIn || !Chat.s) return;
  try{ Chat.s.savedAt = Date.now(); Chat.save();
    fetch('/api/chat-state', {method:'POST', keepalive:true, credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify({state: Chat.s})});
  }catch(_){}
});

/* ════════════════════════════════════════════════════════════════
   โควตา — server นับเอง (ฟรี 20 ข้อความ/วัน → แล้วหัก 1 เครดิต/ข้อความ · Premium ไม่จำกัด)
   หน้าเว็บแค่แสดงผลจาก /me และ field quota ที่ /run ส่งกลับ
   ════════════════════════════════════════════════════════════════ */
var Limit = {
  set: function(q){
    if(!q) return;
    if(q.free_limit != null) Auth.freeLimit = num(q.free_limit, 20);
    if(q.free_left != null) Auth.freeLeft = num(q.free_left, 0);
    if(q.credits != null && Auth.loggedIn) Auth.credits = num(q.credits, 0);
    if(q.premium != null) Auth.premium = !!q.premium;
  },
  ui: function(){
    var low = Auth.freeLeft != null && Auth.freeLeft <= 5 && !(Auth.credits > 5);
    $('#upgrade-pill').classList.toggle('hide', Auth.premium || !low);
    var uf = $('#up-free'); if(uf && Auth.freeLimit != null) uf.textContent = Auth.freeLimit;
    $('#upgrade-pill').textContent = Auth.freeLeft > 0 ? _t('▲ ฟรีเหลือ {n}', {n: Auth.freeLeft}) : _t('▲ เติม/อัปเกรด');
  }
};
function openUpgrade(){ var d = $('#dlg-up'); if(!d.open) d.showModal(); }
$('#upgrade-pill').addEventListener('click', openUpgrade);
$('#upgrade-pill').addEventListener('keydown', function(e){ if(e.key==='Enter' || e.key===' '){ e.preventDefault(); openUpgrade(); } });
$('#up-close').addEventListener('click', function(){ $('#dlg-up').close(); });
$('#eq-close').addEventListener('click', function(){ $('#dlg-eq').close(); });
document.addEventListener('click', function(e){ var a = e.target.closest('[data-axis]'); if(!a) return; e.preventDefault(); var d = $('#dlg-axis'); if(!d.open){ d.showModal(); d.scrollTop = 0; } });
$('#axis-close').addEventListener('click', function(){ $('#dlg-axis').close(); });
$('#dlg-axis').addEventListener('click', function(e){ if(e.target === this) this.close(); });
/* ราคาจริงจาก Stripe บนปุ่ม Premium (เดิมเขียน ฿279 ตายตัว) */
fetch('/pricing').then(function(r){ return r.json(); }).then(function(d){
  var p = d && d.premium; if(!p || !p.amount) return;
  var b = $('#up-go'); if(b) b.textContent = 'Premium ' + (p.currency === 'THB' ? '฿' : p.currency + ' ') + Math.round(p.amount).toLocaleString('en-US') + (p.interval === 'month' ? _t(' / เดือน') : '');
}).catch(function(){});
$('#up-go').addEventListener('click', async function(){
  var b = this; b.disabled = true;
  try{
    var d = await readJson(await fetch('/create-subscription', {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body:'{}'}));
    if(d.url) location.href = d.url; else toast(d.error || 'เชื่อมต่อ Stripe ไม่ได้', true);
  }catch(e){ toast(e.message, true); }
  finally{ b.disabled = false; }
});

/* ════════════════════════════════════════════════════════════════
   MY STATE — context ที่ส่งให้ ENGINE/human_engine.analyze_human()
   ════════════════════════════════════════════════════════════════ */
var MyState = {
  KEY: 'kd_state_v1',
  get: function(){ try{ var o = JSON.parse(lsGet(this.KEY)); return o && o.set ? o : null; }catch(_){ return null; } },
  payload: function(){
    var s = this.get(); if(!s) return {};
    var p = { energy:s.energy, sleep_hours:s.sleep_hours, mental_state:s.mental_state, days_in_crisis:s.days_in_crisis, food_access:s.food_access, safe_place:s.safe_place };
    if(s.money !== null && s.money !== undefined && s.money !== '') p.money = s.money;
    return p;
  },
  /* สูตรเดียวกับ RealHumanSurvivorEngine._calc_waterline() */
  waterline: function(s){
    var w = 100;
    w -= Math.max(0, 50 - s.energy);
    w -= Math.max(0, (6 - s.sleep_hours) * 5);
    if(!s.food_access) w -= 30;
    if(!s.safe_place) w -= 40;
    if(s.mental_state === 'overwhelmed') w -= 25;
    if(s.mental_state === 'stressed') w -= 10;
    w -= Math.min(20, s.days_in_crisis * 2);
    w -= this.moneyCut(s);
    return Math.max(0, Math.min(100, w));
  },
  moneyCut: function(s){                       /* เงินที่ใช้ได้ (เมื่อบอก): 0 บาท −20 · ไม่ถึง 1,000 −10 */
    if(s.money === null || s.money === undefined || s.money === '') return 0;
    return s.money <= 0 ? 20 : s.money < 1000 ? 10 : 0;
  },
  status: function(s){
    if(s.mental_state === 'overwhelmed' || s.energy < 10) return 'RESET_REQUIRED';
    if(!s.food_access) return 'CRITICAL_NO_FOOD';
    if(!s.safe_place) return 'CRITICAL_NO_SHELTER';
    if(s.energy < 20 || s.sleep_hours < 4) return 'LOW_ENERGY';
    if(s.money !== null && s.money !== undefined && s.money !== '' && s.money <= 0) return 'STRESSED_FUNCTIONAL';
    if(s.mental_state === 'stressed' || s.days_in_crisis > 3) return 'STRESSED_FUNCTIONAL';
    return 'STABLE';
  },
  readForm: function(){
    var m = $('#st-money').value.trim();
    return { set:true, energy: num($('#st-energy').value, 50), sleep_hours: Math.max(0, num($('#st-sleep').value, 6)),
      days_in_crisis: Math.max(0, Math.round(num($('#st-days').value, 0))), mental_state: $('#st-mind').value,
      food_access: $('#st-food').value === '1', safe_place: $('#st-safe').value === '1', money: m === '' ? null : Math.max(0, num(m, 0)) };
  },
  fillForm: function(){
    var s = this.get() || {energy:50, sleep_hours:6, days_in_crisis:0, mental_state:'stable', food_access:true, safe_place:true, money:null};
    $('#st-energy').value = s.energy; $('#st-sleep').value = s.sleep_hours; $('#st-days').value = s.days_in_crisis;
    $('#st-mind').value = s.mental_state; $('#st-food').value = s.food_access ? '1' : '0'; $('#st-safe').value = s.safe_place ? '1' : '0';
    $('#st-money').value = s.money == null ? '' : s.money; this.preview();
  },
  preview: function(){
    var s = this.readForm(), w = this.waterline(s);
    $('#st-energy-v').textContent = s.energy; $('#st-wl').textContent = Math.round(w); $('#st-wl-s').textContent = '· ' + this.status(s);
    var bar = $('#st-wl-bar'); bar.className = 'bar' + (w < 35 ? ' bad' : w < 65 ? ' warn' : ''); bar.firstElementChild.style.width = w + '%';
    var a = Math.max(0, 50 - s.energy), b = Math.max(0, (6 - s.sleep_hours) * 5), f = s.food_access ? 0 : 30, h = s.safe_place ? 0 : 40;
    var m = s.mental_state === 'overwhelmed' ? 25 : s.mental_state === 'stressed' ? 10 : 0, d = Math.min(20, s.days_in_crisis * 2);
    $('#st-wl-f').textContent = '100 − ' + [a, b, f, h, m, d, this.moneyCut(s)].map(r1).join(' − ');
  },
  chip: function(){
    var s = this.get(), c = $('#state-chip');
    c.classList.toggle('set', !!s);
    c.textContent = s ? 'W ' + Math.round(this.waterline(s)) : 'W —';
  }
};
$('#state-chip').addEventListener('click', function(){ MyState.fillForm(); $('#dlg-state').showModal(); });
$('#state-form').addEventListener('input', function(){ MyState.preview(); });
$('#dlg-state').addEventListener('close', function(){
  if(this.returnValue === 'save'){ lsSet(MyState.KEY, JSON.stringify(MyState.readForm())); MyState.chip(); Cosmos.syncCore(); }
});
$('#st-clear').addEventListener('click', function(){ lsDel(MyState.KEY); MyState.chip(); Cosmos.syncCore(); $('#dlg-state').close('clear'); });

/* ════════════════════════════════════════════════════════════════
   ROUTE + PERSONA
   ════════════════════════════════════════════════════════════════ */
var ROUTES = [['general','ทั่วไป'],['risk','ความเสี่ยง'],['civil','งาน/สังคม'],['survival','อยู่รอด'],['collapse','วิกฤต'],['vega','VEGA กลยุทธ์']];
var ROUTE_NAME = {}; ROUTES.forEach(function(r){ ROUTE_NAME[r[0]] = r[1]; });
var Route = lsGet('kd_route') || 'general', Persona = lsGet('kd_persona') || 'auto';
if(!ROUTE_NAME[Route]) Route = 'general';
/* เลือกเส้นทางจากที่อื่น (เช่นแตะกลุ่มดาวในจักรวาล) = เลือกเส้นทางเดียวกับชิป */
window.setRoute = function(r){
  if(!ROUTE_NAME[r]) return;
  Route = r; lsSet('kd_route', Route); syncChips();
  if(window.Cosmos) Cosmos.focusRoute(Route);
};
function syncChips(){
  if(window.KD_galaxy) KD_galaxy.route(Route);
  var rp = $('#route-pill'); if(rp) rp.textContent = ROUTE_NAME[Route] || Route;
  $$('#routes .chip').forEach(function(b){ b.classList.toggle('on', b.dataset.r === Route); });
  $$('#persona-seg button').forEach(function(b){ b.classList.toggle('on', b.dataset.p === Persona); });
}
/* สัญญาณทำร้ายตัวเองเท่านั้น — เดิมนับ "ตาย" "urgent" "วิกฤต" คำเดียว ("แบตมือถือตาย" "ขำจะตาย" ก็เป็นวิกฤต)
   เซิร์ฟเวอร์ตรวจซ้ำอีกชั้นก่อนใช้โหมดวิกฤต */
var CRISIS_RE = /ฆ่าตัว|อยากตาย|ไม่อยากมีชีวิต|ไม่อยากอยู่(?!(?:แล้ว|ต่อ)?\s*(?:ที่|กับ|บ้าน|บริษัท|ห้อง|หอ|ตรงนี้|ทีม|งาน|ใน))|จบชีวิต|ทำร้ายตัวเอง|กรีดข้อมือ|suicid|kill myself|want to die|end my life|死にたい|想死(?!你|您|他|她|我了)|自杀|자살|죽고\s*싶|quiero morir/i;
function detectMode(text){
  if(CRISIS_RE.test(text)) return 'crisis';
  var callV = /เวก้า|เวกา|วีก้า|\bvega\b/i.test(text), callL = /ไลล่า|ไลลา|\blyla\b/i.test(text);   // เรียกชื่อในข้อความ
  if(callV !== callL) return callV ? 'vega' : 'lyla';
  if(/ขอความเห็นสภา|เปิดสภา|ถามสภา|สภา\s*[56]\s*เสียง|\bcouncil\b/i.test(text)) return 'council';
  if(Persona === 'vega' || Persona === 'lyla' || Persona === 'council') return Persona;
  if(/วิเคราะห์|ประเมิน|คำนวณ|โอกาส|เปรียบเทียบ|สถิติ|ข้อมูล|logic|analy[sz]e|compare|probability/i.test(text)) return 'vega';
  return 'lyla';
}
function voiceHint(mode){
  if(mode === 'crisis') return 'พูดด้วยความเร่งด่วน ให้ความช่วยเหลือทันที';
  if(mode === 'vega') return 'ให้ข้อมูลเชิงวิเคราะห์ ตัวเลข ความน่าจะเป็น';
  if(mode === 'council') return 'ให้ 6 มุมมอง แล้วสรุปมติร่วม';
  return 'พูดด้วยความเข้าใจ ให้ทางเลือกที่ชัดเจน';
}

/* ════════════════════════════════════════════════════════════════
   TRACE — แปลง response ของ /run เป็นสิ่งที่คนอ่านได้ (ไม่มีค่าที่แต่งขึ้น)
   ════════════════════════════════════════════════════════════════ */
function traceOf(d, mode, sentState){
  var inp = sentState && typeof sentState === 'object' && Object.keys(sentState).length ? JSON.parse(JSON.stringify(sentState)) : null;
  /* DecisionEngine คืนผล survivor ไว้ที่ human_engine · เส้นทาง PAUSE คืนไว้ที่ pattern */
  var p = Object.assign({}, d.human_engine || {}, d.pattern || {}), b = d.belief_audit || {};
  if(d.human_engine && d.human_engine.waterline != null) p.waterline = d.human_engine.waterline;
  return {
    status: d.status || '', route: d.route || '', persona: d.persona || '', mode: mode,
    risk: d.risk_score != null ? num(d.risk_score, null) : null,
    wl: p.waterline != null ? num(p.waterline, null) : null, hs: p.status || '', pri: p.priority || '',
    flags: Array.isArray(p.flags) ? p.flags.slice(0, 8) : [], canDecide: p.can_decide,
    belief: b.crisis_level ? { lvl: b.crisis_level, msg: b.message || '', arts: b.violated_articles || [], layer: b.stack_layer || '' } : null,
    canon: d.status === 'CANON_BLOCKED' ? 'blocked' : (d.canon_notice ? 'notice' : ''),
    canonV: d.canon_violations || [],
    consensus: typeof d.consensus === 'string' ? d.consensus : (d.consensus && (d.consensus.final_action || d.consensus.consensus)) || '',
    tw: d.time_windows && typeof d.time_windows === 'object' ? d.time_windows : null,
    magga: Array.isArray(d.magga) ? d.magga.slice(0, 8) : [], ariya: d.ariya && typeof d.ariya === 'object' ? d.ariya : null, report: d.report_id || '', share: d.share_token || '', gates: Array.isArray(d.vega_gates) ? d.vega_gates.slice(0, 3) : [], warn: d.governance_warning || '', sentState: !!inp, inp: inp
  };
}
function lvlClass(v, invert){ if(v == null) return ''; if(invert) return v >= 75 ? 'bad' : v >= 45 ? 'warn' : 'ok'; return v < 35 ? 'bad' : v < 65 ? 'warn' : 'ok'; }
function traceHTML(t){
  if(!t) return '';
  var rows = [], flags = Array.isArray(t.flags) ? t.flags : [], canonV = Array.isArray(t.canonV) ? t.canonV : [];
  function row(k, v){ rows.push('<div class="tr-row"><div class="k">' + esc(k) + '</div><div class="v">' + v + '</div></div>'); }
  var stCls = t.status === 'SUCCESS' ? 'ok' : (t.status === 'SYSTEM_PAUSE' ? 'warn' : (t.status ? 'bad' : ''));
  row('ผลลัพธ์', '<span class="badge ' + stCls + '">' + esc(t.status || '—') + '</span>');
  row('เส้นทาง', '<span class="mono">' + esc(String(t.route || '—').toUpperCase()) + '</span> · ' + esc(t.persona || '—'));
  if(t.wl != null){
    var c = lvlClass(t.wl);
    row('Waterline', '<span class="mono">' + Math.round(t.wl) + '/100</span> · ' + esc(t.hs || '') + '<div class="bar ' + (c==='ok'?'':c) + '"><i style="width:' + Math.max(0, Math.min(100, t.wl)) + '%"></i></div>' + (t.pri ? '<div class="muted" style="font-size:12px;margin-top:4px">' + esc(t.pri) + '</div>' : ''));
  }
  /* ช่วงตัดสินใจเป็นวันจริง — จากประวัติ waterline ของผู้ใช้เอง (core/choice_dynamics.py) */
  if(t.tw && t.tw.status){
    var tw = t.tw, twc = tw.status === 'STABLE' ? 'ok' : tw.status === 'WATCH' ? 'warn' : 'bad';
    var days = function(n){ return n == null ? '—' : (n === 0 ? _t('วันนี้') : _t('อีก {n} วัน', {n: n})); };
    row('ช่วงตัดสินใจ', '<span class="badge ' + twc + '">' + esc(tw.status) + '</span> '
      + (tw.time_to_intervention_days == null ? '<span class="muted">waterline ไม่ได้ลดลง — ยังไม่มีวันที่ต้องรีบ</span>'
        : '<span class="mono">' + _t('เหลือทางเดียว {a} · ถึงศูนย์ {b}', {a: esc(days(tw.time_to_intervention_days)), b: esc(days(tw.time_to_failure_days))}) + '</span>')
      + (tw.waterline_per_day != null ? '<div class="muted" style="font-size:12px">' + _t('waterline {n} ต่อวัน', {n: esc(String(tw.waterline_per_day))}) + '</div>' : ''));
  }
  if(t.risk != null) row('ความเสี่ยง', '<span class="badge ' + lvlClass(t.risk, true) + '">' + Math.round(t.risk) + ' / 100</span>');
  if(flags.length) row('Flags', flags.map(function(f){ return '<span class="badge warn">' + esc(f) + '</span>'; }).join(''));
  if(t.canDecide === false) row('ตัดสินใจใหญ่', '<span class="badge warn">ยังไม่ควร</span> <span class="muted">survivor engine ให้ stabilize ก่อน</span>');
  if(t.belief && t.belief.lvl) row('Belief core', '<span class="badge ' + (t.belief.lvl === 'ok' ? 'ok' : t.belief.lvl === 'warn' ? 'warn' : 'bad') + '">' + esc(String(t.belief.lvl).toUpperCase()) + '</span>' + (Array.isArray(t.belief.arts) && t.belief.arts.length ? t.belief.arts.map(function(a){ return '<span class="badge">' + esc(a) + '</span>'; }).join('') : '') + '<div class="muted" style="font-size:12px">' + esc(t.belief.msg) + '</div>');
  row('Canon gate', t.canon === 'blocked' ? '<span class="badge bad">บล็อกคำตอบ</span> ' + esc(canonV.join(', ')) : t.canon === 'notice' ? '<span class="badge warn">เตือน</span>' : '<span class="badge ok">ผ่าน</span>');
  if(t.consensus) row('Consensus', '<span class="mono">' + esc(t.consensus) + '</span>');
  /* VEGA 14 Gates — ประตูที่ติดจากข้อความ พร้อมคำถามของแต่ละประตู */
  if(Array.isArray(t.gates) && t.gates.length) row('VEGA gates', t.gates.map(function(g){ return '<div><span class="badge warn">' + esc(g.id) + '</span> <b>' + esc(g.name) + '</b> — ' + esc(g.ask) + '</div>'; }).join(''));
  /* ลิงก์รายงานสร้างเมื่อกดแชร์เท่านั้น — ไม่มีลิงก์สาธารณะเกิดเองทุกครั้งที่ถาม */
  if(t.report) row('รายงาน', '<a href="/report/' + encodeURIComponent(t.report) + '" target="_blank" rel="noopener" class="mono">/report/' + esc(t.report) + '</a>');
  else if(t.share) row('รายงาน', '<button type="button" class="btn ghost" data-act="share" data-token="' + esc(t.share) + '">สร้างลิงก์แชร์</button> <span class="muted">เปิดได้ 90 วัน · ใครมีลิงก์ก็อ่านได้</span>');
  if(t.warn) row('คำเตือน', '<span class="badge warn">' + esc(t.warn) + '</span>');
  var note = t.sentState ? '' : '<div class="tr-note">ยังไม่ได้ระบุ “สถานะของฉัน” — waterline และความเสี่ยงข้างบนมาจากค่าเริ่มต้นของ backend ไม่ใช่สภาพจริงของคุณ</div>';
  return '<div class="trace">' + rows.join('') + note + '</div>';
}
/* สีของดาว = ความเสี่ยง (ฟ้า → ทอง → แดง) */
/* สีสูงเป็นแดงราสเบอร์รี่ ไม่ใช่แดงอมส้ม — จำลองการมองของคนตาบอดสี 3 แบบแล้ว แยกจากฟ้าและส้มได้ชัดที่สุด
   (ΔE ต่ำสุด 41.7 · เดิม #ff5d6c ใกล้ส้มสำหรับคนตาบอดสีเขียว ΔE 32) · ความเสี่ยงสูงมีวงล้อมดาวด้วย ไม่พึ่งสีอย่างเดียว */
var RISK_HI = '#f2417d';
function riskColor(r){ if(r == null) return '#c9d4ff'; return r >= 75 ? RISK_HI : r >= 45 ? '#f6b24a' : '#6fb2ff'; }

/* ════════════════════════════════════════════════════════════════
   Σ — สมการจริงจากโค้ด (ไม่มีสูตรที่แต่งขึ้น) + การแทนค่าของแต่ละคำตอบ
   ════════════════════════════════════════════════════════════════ */
var EQ = [
  ['W',    'W = 100 − max(0, 50−e) − 5·max(0, 6−s) − 30·¬food − 40·¬safe − m − min(20, 2d)', 'ENGINE/realhuman_survivorengine.py',
   'Waterline = 100 − energy gap − sleep gap − no food − no safe place − mental load − days in crisis',
   'ระดับน้ำ = 100 − พลังที่ขาด − การนอนที่ขาด − ไม่มีอาหาร − ไม่มีที่ปลอดภัย − ภาระใจ − วันที่อยู่ในวิกฤต'],
  ['E, R', 'E = 100 − W   ·   R = W', 'ENGINE/human_engine.py',
   'Entropy = 100 − Waterline · Resource = Waterline',
   'ความยุ่งเหยิง = 100 − ระดับน้ำ · ทรัพยากร = ระดับน้ำ'],
  ['Risk', 'Risk = 0.5·E + 0.5·(100 − R)', 'ENGINE/risk_engine.py',
   'Risk = half of Entropy + half of missing Resource',
   'ความเสี่ยง = ครึ่งหนึ่งของความยุ่งเหยิง + ครึ่งหนึ่งของทรัพยากรที่ขาด'],
  ['C',    'Choice(t) = max(1, ⌊(100 − Risk) / 20⌋)', 'ENGINE/risk_engine.py · core/emptiness_guard.py',
   'Choice = choices still open — never below 1',
   'ทางเลือก = จำนวนทางที่ยังเปิดอยู่ ไม่ต่ำกว่า 1 เสมอ'],
  ['P',    'Risk > 80 → high · > 60 → moderate · else low', 'ENGINE/collapse_predictor.py',
   'Prediction = collapse level read from Risk',
   'คาดการณ์ = ระดับการพังที่อ่านจากความเสี่ยง'],
  ['B-1',  'Choice(t) ≥ 1 → collapse = False', 'AI_KERNEL/belief_core.py',
   'Belief rule: while one choice remains, nothing has collapsed',
   'กฎความเชื่อ: ยังเหลือทางเลือกอย่างน้อย 1 ทาง = ยังไม่พัง'],
  ['R',    'R = (D × E × T) / C', 'AI/freedom_signal.py',
   'Risk = Drift × Exposure × Time ÷ Remaining Choice',
   'ความเสี่ยง = การเบี่ยงเบน × การเปิดรับ × เวลา ÷ ทางเลือกที่เหลือ'],
  ['T',    'Choice ≈ W ÷ 20 · Drift(t) = Drift(0)·1.001ᵗ · ช่วงตัดสินใจ = วันแรกที่ Choice ≤ 1', 'core/choice_dynamics.py',
   'Time: Drift compounds 0.1% a day · Decision window = first day Choice ≤ 1',
   'เวลา: การเบี่ยงทบต้นวันละ 0.1% · ช่วงตัดสินใจ = วันแรกที่ทางเลือกเหลือไม่เกิน 1']
];
function eqRow(sym, expr, val, sub, cls){
  return '<div class="r' + (cls ? ' ' + cls : '') + '"><span class="s">' + esc(sym) + '</span><span class="x">' + expr + '</span><span class="v">' + (val == null ? '' : val) + '</span>' +
    (sub ? '<span class="sub">' + sub + '</span>' : '') + '</div>';
}
function eqCatalog(){
  return '<div class="eq">' + EQ.map(function(e){
    var nm = e[3] ? '<span class="nm" lang="en"><i>' + esc(e[3]) + '</i></span><span class="nm" lang="th">' + esc(e[4]) + '</span>' : '';
    return eqRow(e[0], esc(e[1]) + nm, '', esc(e[2]));
  }).join('') + '</div>';
}
function r1(v){ return Math.round(v * 10) / 10; }
function eqHTML(t){
  if(!t) return eqCatalog();
  var rows = [], s = t.inp, W;
  if(s){
    var a = Math.max(0, 50 - num(s.energy, 50)), b = Math.max(0, (6 - num(s.sleep_hours, 6)) * 5), f = s.food_access === false ? 30 : 0, h = s.safe_place === false ? 40 : 0;
    var m = s.mental_state === 'overwhelmed' ? 25 : s.mental_state === 'stressed' ? 10 : 0, dd = Math.min(20, num(s.days_in_crisis, 0) * 2);
    var wc = Math.max(0, Math.min(100, 100 - a - b - f - h - m - dd));
    W = t.wl != null ? t.wl : wc;
    rows.push(eqRow('W', '100 − ' + [a, b, f, h, m, dd].map(r1).join(' − '), '<b>' + r1(W) + '</b>', esc('e ' + s.energy + ' · s ' + s.sleep_hours + 'h · d ' + s.days_in_crisis + ' · ' + (s.mental_state || '') + (f ? ' · ¬food' : '') + (h ? ' · ¬safe' : ''))));
  } else {
    W = t.wl != null ? t.wl : 100;
    /* ยังไม่มีสถานะ: ไม่โชว์ 100 ตัวหนา (ดูเหมือน "ปลอดภัยทุกอย่าง") — แสดง — แล้วบอกว่าคำนวณต่อด้วย 100 ชั่วคราว */
    rows.push(eqRow('W', t.wl != null ? '100' : '—', t.wl != null ? '<b>' + r1(W) + '</b>' : '<b>—</b>', _t(t.wl != null ? 'ค่าเริ่มต้น' : 'ยังไม่ระบุ · ใช้ 100 ชั่วคราวในสูตรถัดไป') + ' · <a href="#" data-act="state">' + _t('ระบุสถานะ') + '</a>'));
  }
  var E = 100 - W, R = W, rf = 0.5 * E + 0.5 * (100 - R), risk = rf;
  /* ยังไม่ระบุสถานะ: E, R มาจาก W ค่าเริ่มต้น → สูตรได้ Risk 0 เสมอ เดิมโชว์ "Risk 0" คู่ "Risk* 55" ดูขัดกัน
     (หน้าจอจริง: หนี้บัตรเครดิต 50,000 ผ่อนไม่ไหว) → แสดงแถวเดียว คือความเสี่ยงจากข้อความ */
  if(!s && t.risk != null){
    risk = t.risk;
    rows.push(eqRow('Risk', 'engine', '<b>' + r1(risk) + '</b>', 'สัญญาณจากข้อความ / DecisionEngine'));
  } else {
    rows.push(eqRow('E, R', r1(E) + ' · ' + r1(R), ''));
    rows.push(eqRow('Risk', '0.5·' + r1(E) + ' + 0.5·' + r1(100 - R), '<b>' + r1(rf) + '</b>'));
    if(t.risk != null && Math.abs(t.risk - rf) > 0.5){ risk = t.risk; rows.push(eqRow('Risk*', 'engine', '<b>' + r1(risk) + '</b>', 'สัญญาณจากข้อความ / DecisionEngine', 'warn')); }
  }
  var C = Math.max(1, Math.floor((100 - risk) / 20)), P = risk > 80 ? 'high' : risk > 60 ? 'moderate' : 'low';
  rows.push(eqRow('C', 'max(1, ⌊' + r1(100 - risk) + ' / 20⌋)', '<b>' + C + '</b>'));
  rows.push(eqRow('P', 'Risk ' + r1(risk), P, '', P === 'high' ? 'bad' : P === 'moderate' ? 'warn' : ''));
  var paused = t.status === 'SYSTEM_PAUSE';
  rows.push(eqRow('B-1', 'C ≥ 1 → collapse = False', paused ? '⏸' : '✓', paused ? 'SYSTEM_PAUSE' : '', paused ? 'warn' : 'ok'));
  var gates = [];
  gates.push('canon ' + (t.canon === 'blocked' ? '✕' : '✓'));
  if(t.belief && t.belief.lvl) gates.push('belief ' + esc(String(t.belief.lvl).toUpperCase()));
  if(t.consensus) gates.push(esc(t.consensus));
  rows.push(eqRow('⊢', gates.join(' · '), t.report ? '<a href="/report/' + encodeURIComponent(t.report) + '" target="_blank" rel="noopener">↗</a>' : ''));
  t._n = {risk: risk, C: C, P: P, paused: paused, noState: !s};
  return '<div class="eq">' + rows.join('') + '</div>';
}
/* คนทั่วไปอ่านสูตร W · E, R · ⌊⌋ ไม่ออก (เจ้าของโปรเจกต์: "กลัวคนธรรมดาเข้าถึงยาก")
   → สรุปเป็นภาษาคน 3 บรรทัด ตัวเลขชุดเดียวกับสูตรทุกตัว · สูตรเต็มพับไว้ใน "ดูวิธีคำนวณ" */
function plainHTML(t){
  if(!t) return eqCatalog();
  var eq = eqHTML(t), n = t._n, lv = n.P === 'high' ? 2 : n.P === 'moderate' ? 1 : 0;
  var word = riskWord(n.risk);
  var h = '<div class="plain">' +
    '<div class="pr"><span class="pk">ความเสี่ยงตอนนี้</span><span class="pv lv' + lv + '">' + word + '</span></div>' +
    '<div class="pbar" role="img" aria-label="' + Math.round(n.risk) + ' / 100"><i style="width:' + Math.max(3, Math.min(100, n.risk)) + '%"></i></div>' +
    /* ไม่โชว์จำนวน C — คำตอบอาจมี 3 ทางขณะที่ C = 2 ดูขัดกัน · B-1 ถามแค่ว่ายังมีทางไปต่อไหม (C ≥ 1 เสมอ) */
    '<div class="pr"><span class="pk">ยังมีทางไปต่อไหม</span><span class="pv">มี</span></div>' +
    '<div class="pr"><span class="pk">ใครตัดสินใจ</span><span class="pv">' + (n.paused ? 'ระบบชวนพักก่อน' : 'คุณเลือกเองเสมอ') + '</span></div>' +
    (n.noState ? '<p class="pn">ประเมินจากข้อความอย่างเดียว — บอกสถานะของคุณ (พลังงาน การนอน) จะแม่นขึ้น</p>' : '') +
    '</div>';
  return h + ariyaHTML(t) + maggaHTML(t) + '<details class="eq-more"><summary>ดูวิธีคำนวณ</summary>' + eq + '</details>';
}
/* อริยสัจ 4 ของข้อความนี้ (ENGINE/ariya_sacca) — เห็นทุกข์และเหตุก่อน มรรค 8 ข้างล่างจึงตรง
   เนื้อความมาจากเซิร์ฟเวอร์เป็นภาษาไทย · หัวข้อแปลได้ */
function ariyaHTML(t){
  var A = t && t.ariya;
  if(!A || !A.dukkha || A.dukkha === 'ยังไม่ชัด') return '';   /* ไม่มีทุกข์ให้ดู (ถามธรรมะ ขอบทสวด ทักทาย) — ไม่ต้องโชว์ช่องว่าง */
  var row = function(k, v){ return '<div class="ar-r"><span class="ar-k">' + _t(k) + '</span><span class="ar-v' + (v === 'ยังไม่ชัด' ? ' ar-un' : '') + '">' + esc(_t(String(v || ''))) + '</span></div>'; };
  return '<div class="ariya"><div class="mg-h">' + _t('อริยสัจ 4') + '</div>' +
    row('ทุกข์', A.dukkha) + (A.own ? '<div class="ar-r"><span class="ar-k">' + _t('สมุทัย') + '</span><span class="ar-v">' + _t('ตามที่เล่า') + ': ' + esc(A.samudaya) + '</span></div>' : row('สมุทัย', A.samudaya)) +
    row('นิโรธ', A.nirodha) + row('มรรค', A.magga) +
    (A.clear ? '' : '<p class="mg-n">' + _t('ยังเห็นไม่ครบ — เล่าเพิ่มอีกนิด ทางจะตรงขึ้น') + '</p>') +
    /* หฤทัยสูตร: อริยสัจ 4 ก็ว่างจากตัวตน — เครื่องมือข้ามฟาก ไม่ใช่คำตัดสิน */
    '<p class="mg-n ar-note">' + _t('อ่านจากที่เล่า เปลี่ยนได้เมื่อเล่าเพิ่ม — เป็นเครื่องมือนำทาง ไม่ใช่คำตัดสิน') + '</p></div>';
}
/* มรรคมีองค์ 8 ของข้อความนี้ (ENGINE/bodhipakkhiya_engine) — ป้าย ✓/✗ ครบ 8 องค์ · ข้อไหนไม่ผ่านบอกเหตุใต้ป้าย */
function maggaHTML(t){
  var M = t && Array.isArray(t.magga) ? t.magga : [];
  if(!M.length) return '';
  var bad = M.filter(function(m){ return !m.ok; });
  return '<div class="magga"><div class="mg-h">' + _t('มรรค 8') + '</div><div class="mg-b">' +
    M.map(function(m){ return '<span class="badge ' + (m.ok ? 'ok' : 'warn') + '">' + (m.ok ? '✓ ' : '✗ ') + esc(_t(m.name)) + '</span>'; }).join('') + '</div>' +
    (bad.length ? bad.map(function(m){ return '<p class="mg-n"><b>' + esc(_t(m.name)) + '</b> — ' + esc(_t(m.note)) + '</p>'; }).join('')
                : '<p class="mg-n">' + _t('ผ่านครบ 8 องค์') + '</p>') + '</div>';
}
function eqStrip(t){
  if(!t) return '';
  /* ไม่ได้ระบุสถานะ → W 100 เป็นแค่ค่าเริ่มต้นของ backend แสดง "W —" (เดิมโชว์ W 100 คู่กับ Risk 80 ดูขัดกัน) */
  var W = t.sentState === false ? null : t.wl, risk = t.risk;
  if(W == null && risk == null) return '';
  if(risk == null) risk = 100 - W;
  /* เดิม "W — · Risk 55 · C 2 Σ" — คนทั่วไปอ่านไม่ออก → บอกเป็นคำ ตัวเลขเต็มอยู่ในแผงเมื่อแตะ */
  return '<span>' + _t('ความเสี่ยง') + '</span> <span>' + riskWord(risk) + '</span> · <span>' + _t('ดูที่มา') + '</span> <b>Σ</b>';
}
function riskWord(risk){ return _t(risk > 80 ? 'ต้องดูแลด่วน' : risk > 60 ? 'ควรระวัง' : 'ยังรับมือได้'); }

/* ════════════════════════════════════════════════════════════════
   COSMOS — จักรวาลการตัดสินใจ วาดด้วยโค้ดล้วน ไม่มีภาพนิ่ง
   ชิ้นจิ๊กซอว์ = ไฟล์จริงทุกไฟล์ใน repo (ขนาดตามจำนวนบรรทัด)
   ใจกลาง    = ชิ้นที่ต่อติดแล้ว (โมดูลที่รันจริง) เชื่อมด้วยเส้น import จริง
   ชิ้นแดง    = ไฟล์ที่เสีย ยื่นเส้นประไปหาจุดที่พยายามต่อแต่ต่อไม่ติด
   วงนอก     = ชิ้นที่ยังไม่ต่อสาย ลอยเรียงตามโฟลเดอร์ รอถูกต่อเข้ามา
   โหมดการตัดสินใจ = คำตอบจริงจาก /run เป็นดาวบนท้องฟ้ารอบตัวผู้สังเกต เรียงเป็นกลุ่มดาวตามเส้นทาง — ไม่มีใจกลาง
   ════════════════════════════════════════════════════════════════ */
var Cosmos = (function(){
  var cv = $('#cosmos'), ctx = cv.getContext('2d'), W = 0, H = 0, DPR = 1, bgCv = null, twk = [], raf = 0;
  var mode = 'decisions', view = 'chat', hover = null, sel = null, think = false, focusR = null, focusT = 0;
  var births = [], packets = [], coreWL = null, t0 = performance.now(), lastPaint = 0, lastSpawn = 0, stars = [];
  var ORB = ['general','risk','civil','survival','collapse','vega'];
  /* สีประจำเส้นทาง (วงโคจรหน้าแรก) */
  var PCOL = ['#ffd99a', '#ffa860', '#c9c2ff', '#8cc2ff', '#ff7a66', '#a9c4ff'];
  var COL = { boot:'#f6b24a', request:'#ffe2a8', web:'#6fb2ff', broken:'#ff5d6c', docs:'#a78bfa', site:'#7d8fc4', config:'#9aa2bc', artifact:'#4a5284', dormant:'#7a86b8', legacy:'#3a4060', vision:'#8a6fd1', tests:'#2bcfb4', pkg:'#2e3352' };
  var TAU = Math.PI * 2;
  /* ── มิติ: กล้อง 3 มิติ + สนามดาวที่มีความลึก ─────────────────────
     ทุกการเคลื่อนไหวคิดจากเวลาจริง (dt) จึงลื่นเท่ากันทั้งจอ 60 / 120 / 240 Hz — วาดทุกเฟรมที่จอขอ */
  var cam = { yaw: 0, pitch: 0, vy: 0, vp: 0, lx: 0, ly: 0, drag: null, idle: 0 }, FIELD = [], warpAt = 0, dtLast = 0, fpsAcc = 0, fpsT = 0;

  function hash(s){ var h = 2166136261; s = String(s); for(var i = 0; i < s.length; i++){ h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); } return (h >>> 0) / 4294967295; }
  function clamp(v, a, b){ return Math.max(a, Math.min(b, v)); }

  /* ── ชิ้นส่วนและเส้นเชื่อม (ข้อมูลจริงจาก MAP) ───────────────── */
  var P = (MAP.files || []).map(function(f, i){
    return { i:i, f:f, cat:f[2], x:0, y:0, sx:0, sy:0, a:0, r:0, rot: hash(f[0] + 'r') * TAU, spin: (hash(f[0] + 's') - .5) * .5,
      size: clamp(Math.sqrt(f[1] || 1) / 5.5, 1.5, 7), zone:'', out:[], inn:[] };
  });
  var byName = {}; P.forEach(function(p){ byName[p.f[0]] = p; });
  var EDGES = (MAP.edges || []).map(function(e){ return { a:P[e[0]], b:P[e[1]], serve: e[2] === 1 }; }).filter(function(e){ return e.a && e.b; });
  EDGES.forEach(function(e){ e.a.out.push(e); e.b.inn.push(e); });
  function isCore(p){ return p.cat === 'boot' || p.cat === 'request'; }
  var CORE = P.filter(isCore), CORE_E = EDGES.filter(function(e){ return isCore(e.a) && isCore(e.b); });
  var PY = P.filter(function(p){ return /\.py$/.test(p.f[0]); }), PY_LIVE = PY.filter(isCore);
  var BELT_DIRS = [];

  /* ── วางชิ้นส่วน (คำนวณครั้งเดียว ผลเหมือนเดิมทุกครั้ง) ──────── */
  (function layout(){
    var app = byName['app.py'];
    CORE.forEach(function(p){ var a = hash(p.f[0]) * TAU, r = .25 + hash(p.f[0] + 'x') * .7; p.x = Math.cos(a) * r; p.y = Math.sin(a) * r; p.zone = 'core'; });
    if(app){ app.x = 0; app.y = 0; }
    for(var it = 0; it < 420; it++){
      var step = .06 * (1 - it / 420) + .004;
      CORE.forEach(function(p){ p.fx = -p.x * .03; p.fy = -p.y * .03; });
      for(var i = 0; i < CORE.length; i++) for(var j = i + 1; j < CORE.length; j++){
        var a = CORE[i], b = CORE[j], dx = a.x - b.x, dy = a.y - b.y, d2 = Math.max(.0009, dx * dx + dy * dy), f = .005 / d2;
        a.fx += dx * f; a.fy += dy * f; b.fx -= dx * f; b.fy -= dy * f;
      }
      CORE_E.forEach(function(e){
        var dx = e.b.x - e.a.x, dy = e.b.y - e.a.y, d = Math.sqrt(dx * dx + dy * dy) || .001, f = (d - .42) * .09;
        e.a.fx += dx / d * f; e.a.fy += dy / d * f; e.b.fx -= dx / d * f; e.b.fy -= dy / d * f;
      });
      CORE.forEach(function(p){ if(p === app) return; p.x += clamp(p.fx, -step, step); p.y += clamp(p.fy, -step, step); });
    }
    var m = .001; CORE.forEach(function(p){ m = Math.max(m, Math.hypot(p.x, p.y)); });
    CORE.forEach(function(p){ p.x /= m; p.y /= m; });

    /* หน้าเว็บที่ app.py เสิร์ฟ: กรอบของภาพที่ต่อแล้ว */
    var web = P.filter(function(p){ return p.cat === 'web'; });
    web.forEach(function(p, k){ var a = -Math.PI / 2 + (k - (web.length - 1) / 2) * .2; p.x = Math.cos(a) * 1.28; p.y = Math.sin(a) * 1.28; p.zone = 'web'; });

    /* ชิ้นที่เสีย: ชี้ไปทางชิ้นที่มันพยายาม import */
    P.filter(function(p){ return p.cat === 'broken'; }).forEach(function(p, k){
      var tx = 0, ty = 0, n = 0;
      p.out.forEach(function(e){ if(e.b.zone === 'core'){ tx += e.b.x; ty += e.b.y; n++; } });
      var a = n ? Math.atan2(ty, tx) : hash(p.f[0]) * TAU;
      a += (k % 2 ? 1 : -1) * .08 * k;
      p.x = Math.cos(a) * 1.5; p.y = Math.sin(a) * 1.5; p.zone = 'broken';
    });

    /* ชิ้นที่ยังไม่ต่อสาย: เรียงเป็นกลุ่มตามโฟลเดอร์บนวงแหวน */
    var dormant = P.filter(function(p){ return ['dormant','legacy','vision','pkg'].indexOf(p.cat) >= 0; }), groups = {}, order = [];
    dormant.forEach(function(p){ var i = p.f[0].indexOf('/'), d = i < 0 ? 'root' : p.f[0].slice(0, i); if(!groups[d]){ groups[d] = []; order.push(d); } groups[d].push(p); });
    order.sort();
    var gap = .05, total = dormant.length, start = -Math.PI / 2, span = TAU - gap * order.length;
    order.forEach(function(d){
      var g = groups[d], w = span * g.length / total;
      g.forEach(function(p, k){ p.a = start + w * (k + .5) / g.length; p.r = 1.95 + hash(p.f[0] + 'b') * .8; p.zone = 'belt'; });
      BELT_DIRS.push({ name: d === 'root' ? '/' : d + '/', a: start + w / 2, n: g.length });
      start += w + gap;
    });
    /* เอกสาร / เว็บ docs / ตั้งค่า / build: ฝุ่นวงนอกสุด */
    P.filter(function(p){ return ['docs','site','config','artifact','tests'].indexOf(p.cat) >= 0; }).forEach(function(p){
      p.a = hash(p.f[0] + 'o') * TAU; p.r = 3.05 + hash(p.f[0] + 'q') * .35; p.zone = 'outer';
    });
  })();

  /* ── พื้นหลังอวกาศ (สุ่มครั้งเดียวต่อขนาดจอ) ─────────────────── */
  function buildBg(){
    bgCv = document.createElement('canvas'); bgCv.width = Math.round(W * DPR); bgCv.height = Math.round(H * DPR);
    var b = bgCv.getContext('2d'); b.scale(DPR, DPR);
    var g = b.createLinearGradient(0, 0, 0, H); g.addColorStop(0, '#03040c'); g.addColorStop(.55, '#070a1f'); g.addColorStop(1, '#0a0b1e'); b.fillStyle = g; b.fillRect(0, 0, W, H);
    var M = Math.max(W, H);
    function neb(x, y, r, col){ var n = b.createRadialGradient(x, y, 0, x, y, r); n.addColorStop(0, col); n.addColorStop(1, 'rgba(0,0,0,0)'); b.fillStyle = n; b.fillRect(0, 0, W, H); }
    b.globalCompositeOperation = 'screen';
    neb(W * .12, H * .30, M * .55, 'rgba(46,96,255,.28)');
    neb(W * .30, H * .10, M * .30, 'rgba(90,140,255,.12)');
    neb(W * .90, H * .26, M * .50, 'rgba(255,140,40,.22)');
    neb(W * .04, H * .94, M * .40, 'rgba(110,70,200,.20)');
    neb(W * .96, H * .94, M * .40, 'rgba(170,90,160,.14)');
    neb(W * .5, H * 1.08, M * .45, 'rgba(255,190,110,.12)');
    /* ไม่มี WebGL: แถบทางช้างเผือกแบบ 2D พาดเฉียงทิศเดียวกับฟ้าจริง — เย็นซ้าย อุ่นขวา */
    var mr = $('#main').getBoundingClientRect(), tl = mr.width < (mr.height - 54) * .9 ? 1.0 : .52;
    b.save(); b.translate(mr.left + mr.width * .53, mr.top + 54 + (mr.height - 54) * .6); b.rotate(-tl); b.scale(1, .2);
    for(var k = -5; k <= 5; k++){
      var u = (k + 5) / 10, bx = k * M * .14, br = M * .3, gb = b.createRadialGradient(bx, 0, 0, bx, 0, br);
      gb.addColorStop(0, u < .5 ? 'rgba(130,160,255,' + (.05 + u * .08).toFixed(3) + ')' : 'rgba(255,' + Math.round(200 - u * 40) + ',140,' + (.06 + u * .1).toFixed(3) + ')');
      gb.addColorStop(1, 'rgba(0,0,0,0)'); b.fillStyle = gb; b.fillRect(bx - br, -br, br * 2, br * 2);
    }
    b.restore();
    b.globalCompositeOperation = 'source-over';
    var n = Math.min(600, Math.round(W * H / 3600));
    for(var i = 0; i < n; i++){
      var x = Math.random() * W, y = Math.random() * H, r = Math.random() < .93 ? Math.random() * .8 + .2 : Math.random() * 1.4 + .8;
      var warm = x / W + (Math.random() - .5) * .5 > .55;
      b.fillStyle = (warm ? 'rgba(255,214,150,' : 'rgba(170,205,255,') + (Math.random() * .6 + .2).toFixed(2) + ')';
      b.beginPath(); b.arc(x, y, r, 0, TAU); b.fill();
    }
    twk = [];
    for(var j = 0; j < 18; j++) twk.push({ x: Math.random() * W, y: Math.random() * H, r: Math.random() * 1.1 + .5, p: Math.random() * 6.28, s: Math.random() * 1.5 + .5, warm: Math.random() < .5 });
    FIELD = [];
    var nf = Math.min(520, Math.round(W * H / 1900));
    for(var f = 0; f < nf; f++) FIELD.push(fieldStar(Math.random()));
  }
  /* ดาวในสนาม 3 มิติ: x,y กระจายรอบกล้อง z = ระยะลึก (1 ไกลสุด → 0 ชนกล้อง) */
  function fieldStar(z){
    var r = Math.random();
    return { x: (Math.random() - .5) * 2.4, y: (Math.random() - .5) * 2.4, z: z, m: r < .9 ? .35 + Math.random() * .5 : .9 + Math.random() * .6,
      c: r < .5 ? '#cfe0ff' : r < .82 ? '#ffffff' : r < .95 ? '#ffd9a8' : '#ffb3a0' };
  }
  /* วาดสนามดาว: เคลื่อนเข้าหากล้องช้าๆ (ดาวใกล้ขยับเร็วกว่า = เห็นความลึก) · ตอนวาร์ปเป็นเส้นแสงพุ่งออกจากกลาง */
  function drawField(now, dt, g){
    var k = warpAt ? clamp((now - warpAt) / 1500, 0, 1) : 1, boost = REDUCED ? 0 : 1.6 * Math.pow(1 - k, 2.6);
    var speed = REDUCED ? 0 : .018 + boost, dz = speed * dt, F = Math.max(W, H) * .55, cx = g.cx, cy = g.cy;
    var ox = -cam.lx * F * .05, oy = -cam.ly * F * .05;
    ctx.globalCompositeOperation = 'lighter';
    for(var i = 0; i < FIELD.length; i++){
      var s = FIELD[i]; s.z -= dz;
      if(s.z < .02){ FIELD[i] = s = fieldStar(1); }
      var iz = 1 / s.z, x = cx + s.x * F * iz + ox * iz, y = cy + s.y * F * iz + oy * iz;
      if(x < -40 || x > W + 40 || y < -40 || y > H + 40){ if(boost > .05 || s.z < .3){ FIELD[i] = fieldStar(.6 + Math.random() * .4); } continue; }
      var near = 1 - s.z, a = clamp(near * 1.25 * s.m + .08, 0, 1), r = Math.max(.45, near * near * 2.6 * s.m);
      ctx.globalAlpha = a; ctx.fillStyle = s.c; ctx.strokeStyle = s.c;
      if(boost > .05){
        var z2 = s.z + dz * 7, iz2 = 1 / z2, x2 = cx + s.x * F * iz2 + ox * iz2, y2 = cy + s.y * F * iz2 + oy * iz2;
        ctx.lineWidth = Math.max(.5, r * .6); ctx.beginPath(); ctx.moveTo(x2, y2); ctx.lineTo(x, y); ctx.stroke();
      } else if(r < 1.1) ctx.fillRect(x - r / 2, y - r / 2, r, r);
      else { ctx.drawImage(glow(s.c), x - r * 3.2, y - r * 3.2, r * 6.4, r * 6.4); }
    }
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  }
  /* ── ชั้นภาพ WebGL: ท้องฟ้าจากข้างในทางช้างเผือก (แท็บจักรวาล) + ฉากโลก (หน้าแรก) ──────────
     ร้อน (ทอง/กุหลาบ) สลับเย็น (ฟ้า/เทอร์ควอยซ์) · ความมืดยังเป็นพื้นหลัก · ไม่มีจุดแสงไหนเป็นใจกลาง */
  var GLX = (function(){
    var c = document.createElement('canvas'); c.id = 'cosmos-gl'; c.setAttribute('aria-hidden', 'true');
    cv.parentNode.insertBefore(c, cv);
    var gl = null, U = {}, Q = 1, qs = 1, slow = 0, mode2 = 'sky';
    try{ gl = c.getContext('webgl', { alpha:false, antialias:false, depth:false, stencil:false, premultipliedAlpha:false }); }catch(_){ gl = null; }
    if(!gl){ c.remove(); return null; }
    var VS = 'attribute vec2 a;void main(){gl_Position=vec4(a,0.,1.);}';
    /* ── ท้องฟ้าจากข้างใน (แทนกาแล็กซีกังหันที่ทุกอย่างหมุนรอบแก่น) ─────────────────────
       "จักรวาลไม่ได้หมุนรอบใคร แต่ทุกคนร่วมกันเป็นส่วนหนึ่งของทั้งจักรวาล" — แนวคิดของผู้ก่อตั้ง
       เราอยู่ข้างในทางช้างเผือก จึงเห็นมันเป็นแถบพาดรอบตัว (Personal Horizon) · ใจกลางกาแล็กซีอยู่นอกจอ ไม่ใช่เรา
       ไกลออกไปคือกาแล็กซีนับไม่ถ้วนกระจายทั่วฟ้าเท่าๆ กัน (Uniform Distribution) · ฝุ่นในแถบบังมันไว้
       ทุกพิกเซลคิดจากทิศที่ตามองจริง (ศูนย์กลางจอ/ระยะโฟกัส/yaw/pitch เดียวกับดาว 2D) หมุนกล้องแล้วฟ้าหมุนตามถูกต้อง */
    var SKY_FS = [
      'precision highp float;',
      'uniform vec2 uRes,uC;uniform float uQ,uT,uF,uYaw,uPitch,uBand,uThink,uLow,uDim;uniform vec3 uN,uG;',
      'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
      'float h3(vec3 p){p=fract(p*.3183099+.1);p*=17.;return fract(p.x*p.y*p.z*(p.x+p.y+p.z));}',
      'float n3(vec3 x){vec3 i=floor(x),f=fract(x);f=f*f*(3.-2.*f);',
      ' return mix(mix(mix(h3(i),h3(i+vec3(1.,0.,0.)),f.x),mix(h3(i+vec3(0.,1.,0.)),h3(i+vec3(1.,1.,0.)),f.x),f.y),',
      '  mix(mix(h3(i+vec3(0.,0.,1.)),h3(i+vec3(1.,0.,1.)),f.x),mix(h3(i+vec3(0.,1.,1.)),h3(i+vec3(1.,1.,1.)),f.x),f.y),f.z);}',
      'float fb4(vec3 p){float a=.5,s=0.;for(int i=0;i<4;i++){s+=a*n3(p);p=p*2.03+vec3(1.7,9.2,4.1);a*=.5;}return s;}',
      'float fb3(vec3 p){float a=.5,s=0.;for(int i=0;i<3;i++){s+=a*n3(p);p=p*2.03+vec3(1.7,9.2,4.1);a*=.5;}return s;}',
      /* กริดบนหน้าลูกบาศก์ (ไม่มีรอยต่อที่ขั้ว): xy = ตำแหน่งบนหน้า · z = หมายเลขหน้า */
      'vec3 face(vec3 d){vec3 a=abs(d);if(a.x>=a.y&&a.x>=a.z)return vec3(d.yz/a.x,d.x>0.?1.:2.);if(a.y>=a.z)return vec3(d.xz/a.y,d.y>0.?3.:4.);return vec3(d.xy/a.z,d.z>0.?5.:6.);}',
      /* กาแล็กซีไกล: วงรีเล็กเอียงสุ่ม อุ่น (ทรงรี) สลับเย็น (กังหัน) */
      'vec3 gal(vec3 d,float K,float th,float s0,float s1){',
      ' vec3 F=face(d);vec2 g=F.xy*K,c=floor(g)+F.z*97.,f=fract(g)-.5;',
      ' if(h(c)<th)return vec3(0.);',
      ' vec2 q=f-(vec2(h(c+.37),h(c+.71))-.5)*.4;float an=h(c+1.3)*6.2832,ca=cos(an),sa=sin(an);q=vec2(q.x*ca+q.y*sa,-q.x*sa+q.y*ca);',
      ' float e=.25+.75*h(c+2.1),s=mix(s0,s1,h(c+2.9)),r2=(q.x*q.x+q.y*q.y/(e*e))/(s*s);',
      ' return mix(vec3(.66,.78,1.),vec3(1.,.8,.56),step(.55,h(c+4.3)))*(exp(-r2)*.7+exp(-r2*7.)*.6)*(.45+.55*h(c+3.7));',
      '}',
      /* ดาวจางๆ นับไม่ถ้วน: ทั่วฟ้าเท่าๆ กัน และหนาแน่นขึ้นมากในแถบทางช้างเผือก */
      'vec3 pts(vec3 d,float K,float dens){',
      ' vec3 F=face(d);vec2 g=F.xy*K,c=floor(g)+F.z*131.,f=fract(g)-.5;',
      ' if(h(c+.5)>dens)return vec3(0.);',
      ' vec2 q=f-(vec2(h(c+.13),h(c+.29))-.5)*.6;',
      ' return mix(vec3(.74,.84,1.),vec3(1.,.86,.66),h(c+.77))*exp(-dot(q,q)*55.)*(.25+.75*h(c+.91));',
      '}',
      'void main(){',
      ' vec2 p=vec2(gl_FragCoord.x,uRes.y-gl_FragCoord.y)/uQ;',
      ' vec3 v=normalize(vec3((p.x-uC.x)/uF,-(p.y-uC.y)/uF,-1.));',
      ' float cp=cos(uPitch),sp=sin(uPitch);v=vec3(v.x,v.y*cp-v.z*sp,v.y*sp+v.z*cp);',
      ' float cy=cos(uYaw),sy=sin(uYaw);vec3 d=vec3(v.x*cy-v.z*sy,v.y,v.x*sy+v.z*cy);',
      ' vec3 E=cross(uN,uG);float b=asin(clamp(dot(d,uN),-1.,1.)),l=atan(dot(d,E),dot(d,uG)),t=uT;',
      ' vec3 col=vec3(.004,.006,.017);',
      /* แถบทางช้างเผือก: หนาขึ้นใกล้ใจกลาง · เมฆดาว · ร่องฝุ่นมืดกลางแถบ · ใกล้ใจกลางอุ่น (ทอง) ไกลออกไปเย็น (ฟ้า) */
      ' float core=exp(-l*l/.9),sg=.07+.12*exp(-l*l/.25),G=exp(-b*b/(2.*sg*sg));',
      ' float dn=0.;',
      ' if(G>.003){',
      '  dn=fb3(d*15.+7.7);float cl=fb4(d*6.5+3.1),nb=fb3(d*4.2+11.),fine=n3(d*42.);',
      '  float b0=.016*sin(l*3.+1.)+.03*(n3(d*3.5)-.5);',
      '  float rift=exp(-pow((b-b0)/(.012+.02*core),2.))*smoothstep(.3,.62,dn);',
      '  float I=G*(.24+.6*core)*(.45+1.1*cl)*(.8+.4*fine);',
      '  I*=(1.-.82*rift)*(1.-.5*smoothstep(.48,.78,dn)*G)*(1.+uThink*.22*(.5+.5*sin(l*5.-t*1.7)));',
      '  vec3 warm=uLow>.5?vec3(1.,.5,.4):vec3(1.,.8,.55),bc=mix(vec3(.55,.68,1.),warm,smoothstep(.15,.85,core));',
      /* ร้อนสลับเย็นตามแนวแถบ: เนบิวลาเปล่งแสงสีกุหลาบ สลับเนบิวลาสะท้อนแสงสีฟ้า */
      '  float hot=smoothstep(.56,.8,nb)*G,cold=smoothstep(.56,.8,1.-nb)*G;',
      '  col+=(bc*I*.52+vec3(1.,.38,.56)*hot*.18+vec3(.36,.58,1.)*cold*.15+vec3(1.,.84,.62)*exp(-l*l/.06-b*b/.006)*.3)*uBand;',
      ' }',
      ' float za=1.-smoothstep(0.,.45,G);',
      ' col+=pts(d,230.,.035+.4*G*(1.-.6*smoothstep(.3,.62,dn)*G))*.55;',
      ' col+=(gal(d,34.,.8,.03,.085)*.22+gal(d,13.,.93,.05,.11)*.4)*(.25+.75*za);',
      ' col=(1.-exp(-col*1.25))*uDim;',
      ' col+=(h(p+fract(t))-.5)*.006;',
      ' gl_FragColor=vec4(col,1.);',
      '}'].join('\n');
    /* ── ฉากหน้าแรก (แบบภาพอ้างอิงของผู้ก่อตั้ง) ─────────────────────────────────
       โลกดวงใหญ่จากภาพดาวเทียมจริง (static/earth/) หันเอเชียตะวันออกเฉียงใต้เข้าหา · ไฟเมืองสีทองทั่วโลก
       แผ่นดินเห็นจางๆ ทะเลน้ำเงินลึก ขอบโลกเรืองทองฝั่งดวงอาทิตย์ · ดวงอาทิตย์มุมซ้ายบน (ผิวเดือดเป็นเม็ด + โคโรนา)
       ดาวเสาร์ (มีวงแหวน หน้า-หลังถูกต้อง) ดาวพฤหัส (แถบเมฆ) ดาวยูเรนัส ทางขวา · เนบิวลาฝุ่นอุ่นมุมซ้ายล่าง
       ทุกดวงรับแสงจากดวงอาทิตย์บนจอ · uShow: 1 = หน้าว่าง · 0 = เริ่มพิมพ์/มีแชท เหลือพื้นมืดกับดาวจางๆ */
    var DAWN_FS = [
      '#ifdef GL_OES_standard_derivatives',
      '#extension GL_OES_standard_derivatives : enable',
      '#endif',
      'precision highp float;',
      'uniform vec2 uRes,uC,uNeb;uniform float uQ,uT,uR,uShow,uThink,uRisk,uDim,uTex,uSpin;',
      'uniform vec3 uSun,uSat,uJup,uUra;',
      'uniform sampler2D uDay,uLights,uClouds;',
      'uniform vec2 uPar;',
      'uniform vec3 uPaper;uniform float uLight;',
      'float h(vec2 p){return fract(sin(dot(p,vec2(127.1,311.7)))*43758.5453);}',
      'float n(vec2 p){vec2 i=floor(p),f=fract(p);f=f*f*(3.-2.*f);return mix(mix(h(i),h(i+vec2(1.,0.)),f.x),mix(h(i+vec2(0.,1.)),h(i+vec2(1.,1.)),f.x),f.y);}',
      'float fbm(vec2 p){float a=.5,s=0.;for(int i=0;i<5;i++){s+=a*n(p);p=p*2.07+vec2(3.1,1.7);a*=.5;}return s;}',
      'float lonU(float lon){float u1=fract(lon/6.2831853+.5);',
      '#ifdef GL_OES_standard_derivatives',
      ' float u2=fract(lon/6.2831853+1.)-.5; return fwidth(u1)<=fwidth(u2)+1e-6?u1:u2;',
      '#else',
      ' return u1;',
      '#endif',
      '}',
      /* ทิศแสงจากดวงอาทิตย์บนจอ มายังวัตถุที่ c */
      'vec3 sunDir(vec2 c){vec2 v=uSun.xy-c;return normalize(vec3(v.x,-v.y,length(v)*.32));}',
      /* ดาวเคราะห์: k=0 พฤหัส · 1 เสาร์ · 2 ยูเรนัส */
      'vec4 planet(vec2 p,vec3 P,float k,float t){',
      ' vec2 d=(p-P.xy)/P.z; float r=length(d); if(r>1.) return vec4(0.);',
      ' vec3 nv=vec3(d.x,-d.y,sqrt(1.-r*r)); vec3 L=sunDir(P.xy); float dif=max(dot(nv,L),0.);',
      ' float lat=nv.y, lo=atan(nv.x,nv.z); vec3 c;',
      ' if(k<.5){ float tb=fbm(vec2(lo*2.+t*.01,lat*7.)); float b=sin(lat*21.+tb*2.6);',
      '  c=mix(vec3(.55,.38,.25),vec3(.95,.88,.76),.5+.5*b); c=mix(c,vec3(.72,.55,.42),smoothstep(.65,1.,abs(lat))*.5);',
      '  float spot=exp(-pow((lat+.32)/.07,2.)-pow((lo-.4)/.22,2.)); c=mix(c,vec3(.78,.36,.24),spot*.7); }',
      ' else if(k<1.5){ float b=sin(lat*15.+n(vec2(lat*18.,2.))*1.4); c=mix(vec3(.78,.67,.47),vec3(.96,.9,.74),.5+.5*b); }',
      ' else { c=mix(vec3(.50,.78,.84),vec3(.78,.94,.96),.5+.5*lat); }',
      ' c*=dif*1.05+.035; c+=c*pow(1.-nv.z,3.)*.25;',
      ' return vec4(c,smoothstep(1.,.96,r));',
      '}',
      'void main(){',
      ' vec2 p=vec2(gl_FragCoord.x,uRes.y-gl_FragCoord.y)/uQ; vec2 S=uRes/uQ; float M=max(S.x,S.y); float t=uT;',
      ' vec3 bg=mix(vec3(.006,.008,.016),uPaper,uLight);',                      /* โหมดสว่าง: พื้นเป็นสีกระดาษ ไม่มีดาว/ฝุ่น */
      /* ดาว: เล็กละเอียด + ดวงสว่างเป็นระยะ */
      /* ความลึกแบบกล้องหนัง: ดาวไกลเลื่อนน้อย เนบิวลาใกล้กว่าเลื่อนมากกว่า · โลกกับดาวเคราะห์เป็นจุดยึดของภาพ */
      ' vec2 sp=p+uPar*.4; vec2 sc=floor(sp/2.); float hs=h(sc);',
      ' vec3 stars=mix(vec3(.72,.8,1.),vec3(1.,.9,.74),h(sc+9.))*step(.9968,hs)*(.3+.7*h(sc+3.1))*(.8+.2*sin(t*(.5+hs*2.)+hs*60.));',
      ' vec2 s3=floor(sp/28.); float h3=h(s3+1.3);',
      ' if(h3>.94){vec2 o=(s3+.2+.6*vec2(h(s3+4.),h(s3+8.)))*28.; float dd=length(sp-o); stars+=vec3(1.,.95,.86)*(exp(-dd*dd/1.1)*.9+exp(-dd/3.5)*.04);}',
      ' stars*=(1.-uLight)*.6;',                                            /* ดาวสุ่มเหลือเป็นฝุ่นจางๆ — ดาวจริงจากแคตตาล็อกวาดทับ */
      ' vec3 plain=bg+stars*.35;',
      ' vec3 col=bg+stars;',
      /* เนบิวลาฝุ่นอุ่นมุมซ้ายล่าง + ดาวกระจุก */
      ' vec2 np=p+uPar*.85; vec2 nq=(np-uNeb)/(M*.36); float nm=smoothstep(1.,0.,length(nq*vec2(.9,1.25)));',
      ' nm*=1.-uLight;',
      ' if(nm>0.){',
      '  vec2 w=np/M; float dn=fbm(w*4.6+vec2(t*.002,0.)+fbm(w*2.3)*1.2); float d2=fbm(w*10.+5.);',
      '  float dust=pow(smoothstep(.32,.85,dn),1.6)*nm;',
      '  vec3 ncol=mix(vec3(.32,.11,.03),vec3(1.,.64,.30),smoothstep(.35,.8,d2));',
      '  col+=ncol*dust*.3; col*=1.-smoothstep(.6,.78,d2)*nm*.25;',
      '  vec2 c2=floor(np/3.); float hc=h(c2+7.);',
      '  col+=vec3(1.,.86,.64)*step(1.-.016*nm,hc)*(.55+.45*sin(t*.8+hc*40.))*0.;',            /* จุดสี่เหลี่ยมดูเป็นพิกเซล ไม่เหมือนดาวจริง — ปิด (ดาวจริงจากแคตตาล็อกแทน) */
      ' }',
      /* ดวงอาทิตย์ */
      ' vec2 sd=(p-uSun.xy)/uSun.z; float sr=length(sd);',
      ' col+=vec3(1.,.58,.22)*.16/(1.+sr*sr*.35);',
      ' if(sr<7.){',
      '  float an=atan(sd.y,sd.x); float ry=pow(n(vec2(an*5.,t*.07))*.6+n(vec2(an*13.,-t*.05))*.4,3.); float so=max(sr-1.,0.);',
      '  col+=vec3(1.,.74,.38)*(exp(-so*4.)*.6+ry*exp(-so*1.3)*(.45+uThink*.4))*smoothstep(.9,1.,sr);',
      ' }',
      ' if(sr<1.){',
      '  float g=fbm(sd*5.5+vec2(t*.02,0.)); float g2=n(sd*22.+t*.06);',
      '  vec3 s0=mix(vec3(1.,.55,.12),vec3(1.,.95,.70),smoothstep(1.,.1,sr));',
      '  s0*=(.74+.36*g+.12*g2)*(.72+.28*sqrt(1.-sr*sr));',
      '  col=mix(col,s0*1.45,smoothstep(1.,.95,sr));',
      ' }',
      /* ดาวเสาร์: วงแหวนครึ่งหลัง → ตัวดาว → วงแหวนครึ่งหน้า */
      ' vec2 q=(p-uSat.xy)/uSat.z; float ca=cos(.26),sa=sin(.26); q=vec2(q.x*ca+q.y*sa,-q.x*sa+q.y*ca);',
      ' float rr=length(vec2(q.x,q.y/.3));',
      ' float ring=smoothstep(1.3,1.36,rr)*smoothstep(2.4,2.3,rr)*(1.-.85*smoothstep(1.84,1.88,rr)*smoothstep(1.99,1.95,rr))*(.55+.45*n(vec2(rr*36.,0.)));',
      ' vec3 ringC=vec3(.86,.77,.58)*ring*.85*(.35+.65*max(sunDir(uSat.xy).x*-1.,0.)+.3);',
      ' if(q.y<0.) col=mix(col,ringC,ring*.9);',
      ' vec4 P=planet(p,uSat,1.,t); col=mix(col,P.rgb,P.a);',
      ' if(q.y>=0.){ float sh=1.-.6*step(length((p-uSat.xy)/uSat.z),1.)*0.; col=mix(col,ringC*sh,ring*.9); }',
      ' P=planet(p,uJup,0.,t); col=mix(col,P.rgb,P.a);',
      ' P=planet(p,uUra,2.,t); col=mix(col,P.rgb,P.a);',
      /* โลก */
      ' vec2 d=(p-uC)/uR; float r=length(d); vec3 L=sunDir(uC);',
      ' vec2 sdir=normalize(L.xy+1e-5);',
      ' if(r<1.){',
      '  vec3 nv=vec3(d.x,-d.y,sqrt(1.-r*r)); float sunF=max(dot(nv,L),0.);',
      '  float ct=.985,st=.174; vec3 ng=vec3(nv.x,nv.y*ct+nv.z*st,-nv.y*st+nv.z*ct);',
      '  float lon=atan(ng.x,ng.z)+uSpin, lat=asin(clamp(ng.y,-1.,1.));',
      '  float lit=mix(.075,.4,uLight)+.5*pow(sunF,1.6); vec3 ec;',      /* พื้นสว่าง: ฝั่งกลางคืนไม่ดำทึบ */
      '  float pulse=1.+uThink*.22*sin(t*3.);',
      '  if(uTex>.5){',
      '   vec2 uv=vec2(lonU(lon),.5-lat/3.1415927);',
      '   vec3 tx=texture2D(uDay,uv).rgb; vec3 alb=pow(tx,vec3(2.2));',
      '   float cl=smoothstep(.15,.9,texture2D(uClouds,vec2(lonU(lon+t*.008),uv.y)).r);',
      '   float li=texture2D(uLights,uv).r;',
      '   float lg=texture2D(uLights,uv,2.).r;',                  /* ไฟเมืองเรืองแสง: อ่าน mip ที่เบลอกว่าเป็นรัศมีรอบเมือง (bloom ราคาถูก ไม่ต้องเรนเดอร์ซ้ำ) */
      '   float water=smoothstep(.03,.12,tx.b-max(tx.r,tx.g)*.9);',
      '   ec=alb*lit+water*vec3(.002,.010,.032)*(.7+sunF);',
      '   vec3 hv=normalize(L+vec3(0.,0.,1.)); ec+=vec3(.5,.72,1.)*pow(max(dot(nv,hv),0.),24.)*water*(1.-cl)*.16;',
      '   ec=mix(ec,vec3(.78,.82,.92)*(.025+sunF*.6),cl*.3);',
      '   float ck=1.-.6*smoothstep(.35,.9,sunF);',
      '   float lc=smoothstep(.02,.62,li);',
      '   ec+=(mix(vec3(1.,.58,.22),vec3(1.,.84,.54),lc)*lc*lc*3.1+vec3(1.,.6,.24)*lg*lg*1.6)*ck*(1.-cl*.4)*pulse*(1.-uLight*.75);',
      '  } else {',
      '   vec2 uv=vec2(lon,lat);',
      '   float land=smoothstep(.555,.6,fbm(uv*vec2(1.5,2.1)+7.)); float ice=smoothstep(1.1,1.3,abs(lat));',
      '   vec3 alb=mix(vec3(.002,.012,.05),vec3(.04,.045,.02),land); alb=mix(alb,vec3(.6,.65,.7),ice);',
      '   vec2 g=uv*95.; vec2 fc=fract(g)-.5;',
      '   float cty=step(.58,h(floor(g)))*land*(1.-ice)*smoothstep(.45,.7,fbm(uv*8.+2.))*exp(-dot(fc,fc)*22.);',
      '   ec=alb*lit+vec3(1.,.66,.32)*cty*1.6*pulse;',
      '  }',
      '  float fr=pow(1.-nv.z,2.5); float side=max(dot(normalize(vec2(d.x,-d.y)+1e-5),sdir),0.);',
      '  vec3 warm=mix(vec3(1.,.66,.32),vec3(1.,.38,.28),uRisk);',
      '  ec+=vec3(.10,.26,.75)*fr*.45+warm*fr*side*side*.4;',
      '  vec3 earth=pow(ec/(1.+ec*.18)*1.12,vec3(.4545));',
      '  col=mix(col,earth,smoothstep(1.,.99,r));',
      ' }',
      /* ขอบบรรยากาศ: ทองฝั่งดวงอาทิตย์ จางรอบทั้งดวง */
      ' if(r>=.97){',
      '  float hg=r-1.; float side=.5+.5*dot(normalize(vec2(d.x,-d.y)+1e-5),sdir);',
      '  vec3 warm=mix(vec3(1.,.70,.36),vec3(1.,.40,.30),uRisk);',
      '  float atm=hg<0.?smoothstep(.97,1.,r)*(.14+.25*side):exp(-hg/.012)*(.30+.5*side)+exp(-hg/.07)*(.07+.10*side);',
      '  col+=mix(vec3(.35,.55,1.),warm,.45+.55*side)*atm;',
      ' }',
      /* แฟลร์เลนส์อนามอร์ฟิกแบบกล้องหนังจอกว้าง: เส้นแสงแนวนอนบางๆ ผ่านดวงอาทิตย์ อุ่นตรงกลาง เย็นที่ปลาย */
      ' float fx=(p.x-uSun.x)/uSun.z, fy=(p.y-uSun.y)/uSun.z;',
      ' col+=mix(vec3(.38,.56,1.),vec3(1.,.8,.55),exp(-fx*fx*.5))*(exp(-fy*fy*160.)*.85+exp(-fy*fy*9.)*.15)*exp(-abs(fx)*.24)*.24;',
      ' col=mix(plain,col,uShow)*uDim;',
      ' col+=(h(p+fract(t))-.5)*.008;',
      ' gl_FragColor=vec4(col,1.);',
      '}'].join('\n');
    function sh(type, src){ var o = gl.createShader(type); gl.shaderSource(o, src); gl.compileShader(o);
      if(!gl.getShaderParameter(o, gl.COMPILE_STATUS)){ console.warn('[KD cosmos-gl]', gl.getShaderInfoLog(o)); return null; } return o; }
    function prog(fsrc, names){
      var vs = sh(gl.VERTEX_SHADER, VS), fs = sh(gl.FRAGMENT_SHADER, fsrc); if(!vs || !fs) return null;
      var pr = gl.createProgram(); gl.attachShader(pr, vs); gl.attachShader(pr, fs); gl.linkProgram(pr);
      if(!gl.getProgramParameter(pr, gl.LINK_STATUS)) return null;
      var u = {}; names.forEach(function(k){ u[k] = gl.getUniformLocation(pr, k); }); return { pr: pr, U: u, a: gl.getAttribLocation(pr, 'a') };
    }
    function use(P){ if(cur === P) return; cur = P; gl.useProgram(P.pr); gl.enableVertexAttribArray(P.a); gl.vertexAttribPointer(P.a, 2, gl.FLOAT, false, 0, 0); }
    var SKYP = prog(SKY_FS, ['uRes','uQ','uT','uC','uF','uYaw','uPitch','uN','uG','uBand','uThink','uLow','uDim']);
    try{ gl.getExtension('OES_standard_derivatives'); }catch(_){}
    var DAWN = prog(DAWN_FS, ['uRes','uQ','uT','uC','uR','uShow','uThink','uRisk','uDim','uTex','uSpin','uDay','uLights','uClouds','uSun','uSat','uJup','uUra','uNeb','uPar'].concat(['uPaper','uLight'])), cur = null;
    /* ภาพโลกจริง: โหลดหลังหน้าเว็บขึ้นแล้ว (~790KB) · ระหว่างรอใช้โลก noise */
    var EARTH_TEX = null;
    function loadEarth(){
      if(!DAWN || EARTH_TEX) return; EARTH_TEX = 'loading';
      var srcs = ['/static/earth/day.jpg', '/static/earth/lights.jpg', '/static/earth/clouds.jpg'], fmt = [gl.RGB, gl.LUMINANCE, gl.LUMINANCE], imgs = [], left = srcs.length;
      srcs.forEach(function(src, i){
        var im = new Image(); im.decoding = 'async';
        im.onload = function(){ imgs[i] = im; if(--left === 0) upload(); };
        im.onerror = function(){ EARTH_TEX = 'failed'; };
        im.src = src;
      });
      function upload(){
        if(!gl || EARTH_TEX === 'failed') return;
        EARTH_TEX = imgs.map(function(im, i){
          var tx = gl.createTexture(); gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, tx);
          gl.texImage2D(gl.TEXTURE_2D, 0, fmt[i], fmt[i], gl.UNSIGNED_BYTE, im);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.REPEAT); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
          gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR); gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR_MIPMAP_LINEAR);
          gl.generateMipmap(gl.TEXTURE_2D); return tx;
        });
        gl.activeTexture(gl.TEXTURE0); kick();
        setTimeout(loadHi, 1500);
      }
      /* 4K ทีหลัง (เมื่อภาพแรกขึ้นแล้ว): พื้นโลกคมขึ้น เมฆไม่เป็นบล็อกตอนโลกใหญ่เต็มจอ (โหมดหนัง/บทสวด)
         เฉพาะเครื่องที่ไหว — GPU รับ 4096 · ไม่ได้เปิดประหยัดเน็ต · RAM ≥ 4GB (ถ้าเบราว์เซอร์บอก) · โลกบนจอใหญ่พอจะเห็นต่าง */
      function loadHi(){
        try{
          var conn = navigator.connection || {}, mem = navigator.deviceMemory || 8;
          var px = Math.min(innerWidth, innerHeight) * Math.min(devicePixelRatio || 1, 2);
          if(!gl || gl.getParameter(gl.MAX_TEXTURE_SIZE) < 4096 || conn.saveData || /2g/.test(conn.effectiveType || '') || mem < 4 || px < 640) return;
        }catch(_){ return; }
        /* ไฟเมืองคงไฟล์ 2K: ไฟล์ 4K เป็นจุดเล็กกว่ามาก พอย่อลงเป็นลูกโลกทั้งใบไฟจะจางหาย (ลองแล้ว) */
        ['/static/earth/day_4k.jpg', null, '/static/earth/clouds_4k.jpg'].forEach(function(src, i){
          if(!src) return;
          var im = new Image(); im.decoding = 'async';
          im.onload = function(){
            if(!gl || !Array.isArray(EARTH_TEX)) return;
            gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, EARTH_TEX[i]);
            gl.texImage2D(gl.TEXTURE_2D, 0, fmt[i], fmt[i], gl.UNSIGNED_BYTE, im); gl.generateMipmap(gl.TEXTURE_2D);
            gl.activeTexture(gl.TEXTURE0); kick();
          };
          im.src = src;
        });
      }
    }
    if(!SKYP){ c.remove(); return null; }
    U = SKYP.U;
    var b = gl.createBuffer(); gl.bindBuffer(gl.ARRAY_BUFFER, b); gl.bufferData(gl.ARRAY_BUFFER, new Float32Array([-1,-1,3,-1,-1,3]), gl.STATIC_DRAW);
    c.addEventListener('webglcontextlost', function(e){ e.preventDefault(); gl = null; });
    return {
      size: function(){ var dp = window.devicePixelRatio || 1; Q = (mode2 === 'earth' ? Math.min(2, dp) : Math.min(1.25, dp) * .7) * qs;
        c.width = Math.round(W * Q); c.height = Math.round(H * Q); if(gl) gl.viewport(0, 0, c.width, c.height); },
      want: function(m){ if(m !== mode2){ mode2 = m; qs = 1; slow = 0; this.size(); } },
      ok: function(){ return !!gl; },
      /* ชั้นนี้ภาพนุ่มอยู่แล้ว ลดความละเอียดได้โดยไม่เสียความคม (ดาว/เส้น/ป้ายอยู่ชั้น 2D) */
      pace: function(dt){
        if(dt <= 0) return; slow = dt > 1 / 45 ? slow + dt : Math.max(0, slow - dt * .5);
        if(slow > 1 && qs > .6){ qs *= .8; slow = 0; this.size(); }
      },
      /* ท้องฟ้าจากข้างใน: s = กล้องเดียวกับดาว 2D (ศูนย์กลางจอ · ระยะโฟกัส · yaw/pitch) · band = ความสว่างของแถบทางช้างเผือก */
      sky: function(s, tsec, band){
        if(!gl) return;
        this.want('sky'); use(SKYP);
        gl.uniform2f(U.uRes, c.width, c.height); gl.uniform1f(U.uQ, Q); gl.uniform1f(U.uT, REDUCED ? 0 : tsec);
        gl.uniform2f(U.uC, s.cx, s.cy); gl.uniform1f(U.uF, s.f); gl.uniform1f(U.uYaw, s.yaw); gl.uniform1f(U.uPitch, s.pitch);
        gl.uniform3f(U.uN, GAL.N[0], GAL.N[1], GAL.N[2]); gl.uniform3f(U.uG, GAL.G[0], GAL.G[1], GAL.G[2]);
        gl.uniform1f(U.uBand, band == null ? 1 : band); gl.uniform1f(U.uThink, think ? 1 : 0);
        gl.uniform1f(U.uLow, coreWL != null && coreWL < 35 ? 1 : 0); gl.uniform1f(U.uDim, 1);
        gl.drawArrays(gl.TRIANGLES, 0, 3);
      },
      /* ฉากหน้าแรก: โลกทั้งใบ กึ่งแสงกึ่งมืด */
      dawn: function(d, tsec){
        if(!gl || !DAWN) return false;
        this.want('earth'); use(DAWN); var u = DAWN.U;
        gl.uniform2f(u.uRes, c.width, c.height); gl.uniform1f(u.uQ, Q); gl.uniform1f(u.uT, REDUCED ? 0 : tsec);
        gl.uniform2f(u.uC, d.cx, d.cy); gl.uniform1f(u.uR, d.r);
        gl.uniform3f(u.uSun, d.sun[0], d.sun[1], d.sun[2]); gl.uniform3f(u.uSat, d.sat[0], d.sat[1], d.sat[2]);
        gl.uniform3f(u.uJup, d.jup[0], d.jup[1], d.jup[2]); gl.uniform3f(u.uUra, d.ura[0], d.ura[1], d.ura[2]); gl.uniform2f(u.uNeb, d.neb[0], d.neb[1]);
        gl.uniform2f(u.uPar, d.par ? d.par[0] : 0, d.par ? d.par[1] : 0);
        gl.uniform1f(u.uShow, d.show); gl.uniform1f(u.uThink, d.think); gl.uniform1f(u.uRisk, d.risk); gl.uniform1f(u.uDim, d.dim);
        var tv = THEME.v; gl.uniform3f(u.uPaper, tv ? tv.rgb[0] : 0, tv ? tv.rgb[1] : 0, tv ? tv.rgb[2] : 0); gl.uniform1f(u.uLight, tv ? 1 : 0);
        loadEarth();
        var ok = EARTH_TEX && typeof EARTH_TEX === 'object';
        gl.uniform1f(u.uTex, ok ? 1 : 0); gl.uniform1f(u.uSpin, 1.885 + (d.spin || 0) - (REDUCED ? 0 : tsec * .025));
        if(ok){ for(var i = 0; i < 3; i++){ gl.activeTexture(gl.TEXTURE0 + i); gl.bindTexture(gl.TEXTURE_2D, EARTH_TEX[i]); } gl.activeTexture(gl.TEXTURE0);
          gl.uniform1i(u.uDay, 0); gl.uniform1i(u.uLights, 1); gl.uniform1i(u.uClouds, 2); }
        gl.drawArrays(gl.TRIANGLES, 0, 3);
        return true;
      }
    };
  })();
  function resize(){
    DPR = Math.min(2, window.devicePixelRatio || 1); W = innerWidth; H = innerHeight;
    var mr = $('#main').getBoundingClientRect(); galFrame(mr.width < (mr.height - 54) * .9);
    cv.width = Math.round(W * DPR); cv.height = Math.round(H * DPR); buildBg(); buildSkyField(); layoutStars(); if(GLX) GLX.size(); kick();
  }

  /* ── เรขาคณิตตามมุมมอง ─────────────────────────────────────── */
  function geo(){
    var r = $('#main').getBoundingClientRect(), top = r.top + 54, cx = r.left + r.width / 2, cy, avW = r.width, avH = r.bottom - top;
    var portrait = avW < avH * .8, R;
    if(view === 'chat' && !$('#empty').classList.contains('hide')){
      var cs = $('#core-space').getBoundingClientRect(); cy = cs.top + cs.height * .5;
      R = Math.min(cs.height / 2 / (portrait ? 1.95 : 1.55), avW / 2 / 3.2);
    } else if(view === 'universe'){
      cy = top + avH * (portrait ? .5 : .53);
      R = mode === 'system' ? Math.min(avW / 2 / 3.45, (avH - 170) / 2 / (3.45 * (portrait ? .62 : .46))) : Math.min(avW / 2 / (portrait ? 3.75 : 3.45), (avH - 150) / 2 / (portrait ? 2.3 : 1.55));
    } else { cy = top + avH * .44; R = Math.min(avW / 2 / 3.45, avH / 2 / (3.45 * (portrait ? .62 : .46))); }
    var g = { cx:cx, cy:cy, R: Math.max(14, R), tilt: portrait ? -.1 : -.13, squash: portrait ? .62 : .42, portrait: portrait };
    return g;
  }

  /* ── ดาวการตัดสินใจ ──────────────────────────────────────── */
  function countDecisions(){ var n = 0; if(Chat.s) Chat.s.items.forEach(function(it){ it.msgs.forEach(function(m){ if(m.r === 'a' && m.tr) n++; }); }); return n; }
  function rebuild(){
    stars = [];
    if(Chat.s) Chat.s.items.forEach(function(it){
      it.msgs.forEach(function(m, idx){
        if(m.r !== 'a' || !m.tr) return;
        var rt = String(m.tr.route || 'general').toLowerCase(); if(rt === 'crisis') rt = 'collapse';
        var oi = ORB.indexOf(rt); if(oi < 0) oi = 0;
        var q = ''; for(var k = idx - 1; k >= 0; k--){ if(it.msgs[k].r === 'u'){ q = it.msgs[k].t; break; } }
        stars.push({ kind:'d', orb:oi, key: m.ts + '|' + it.id + '|' + idx, r: 3.4 + Math.min(4.2, (m.tr.risk || 0) / 20), col: riskColor(m.tr.risk), ts: m.ts || 0, sid: it.id, m: m, q: q });
      });
    });
    stars.sort(function(a, b){ return a.ts - b.ts; });
    layoutStars(); MY.key = '';
    $('#nav-stars').textContent = stars.length;
    if(view === 'universe') legend();
    kick();
  }
  /* ── ท้องฟ้ารอบตัวผู้สังเกต (โหมดการตัดสินใจ) ─────────────────────────────
     Personal Horizon: เราอยู่ข้างใน มองออกไปเห็นฟ้ารอบตัว เพราะตาเราอยู่ที่นี่ ไม่ใช่เพราะเราเป็นใจกลาง
     Orbiting Observer: ผู้สังเกตโคจรช้าๆ (ไม่ใช่จักรวาลหมุนรอบเรา) — ดาวใกล้จึงเลื่อนมากกว่าดาวไกล (parallax)
     กรอบทางช้างเผือก GAL ใช้ร่วมกันทั้ง shader ท้องฟ้าและดาว 2D */
  var GAL = { N: [0, 1, 0], G: [1, 0, 0], E: [0, 0, 1] }, SG = null;
  function v3n(v){ var l = Math.hypot(v[0], v[1], v[2]) || 1; return [v[0] / l, v[1] / l, v[2] / l]; }
  function v3c(a, b){ return [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]]; }
  /* แถบพาดเฉียงขึ้นขวา ผ่านใต้กลางจอเล็กน้อย (จอตั้งชันกว่า) · ใจกลางกาแล็กซีอุ่นอยู่นอกจอขวาบน · ฝั่งซ้ายคือขอบนอกที่เย็น */
  function galFrame(portrait){
    var F = v3n([.06, -.15, -1]), tl = portrait ? 1.0 : .52, T0 = [Math.cos(tl), Math.sin(tl), 0];
    var k = T0[0] * F[0] + T0[1] * F[1], T = v3n([T0[0] - k * F[0], T0[1] - k * F[1], -k * F[2]]);
    var a = portrait ? 1.35 : 1.25, ca = Math.cos(a), sa = Math.sin(a), N = v3n(v3c(F, T));
    var G = v3n([F[0] * ca + T[0] * sa, F[1] * ca + T[1] * sa, F[2] * ca + T[2] * sa]);
    GAL = { N: N, G: G, E: v3c(N, G) };
  }
  /* still = มุมมองนิ่งตรงไปข้างหน้า (หน้าระบบ / ใช้วางกลุ่มดาว)
     ตอนเข้าจักรวาล: กล้องเคลื่อนเข้าพร้อมระยะโฟกัสหดลง = dolly zoom — ดาวของเราขนาดคงเดิม แต่ฟ้าข้างหลังถอยออก
     (Geometry Illusion: ความรู้สึกว่าทุกอย่างพุ่งออกจากเรา เกิดจากมุมมองล้วนๆ) */
  function skyGeo(now, still){
    var r = $('#main').getBoundingClientRect(), top = r.top + 54, avW = r.width, avH = r.bottom - top, f = Math.max(avW, avH) * .66, tsec = (now - t0) / 1000;
    var e = warpAt && !still && !REDUCED ? clamp((now - warpAt) / 1800, 0, 1) : 1, k = 1 - Math.pow(1 - e, 3), ox = 0, oy = 0, oz = 0, yaw = 0, pitch = 0;
    if(!still){
      yaw = cam.yaw; pitch = cam.pitch;
      if(!REDUCED){
        var w = tsec * TAU / 120;
        ox = .07 * Math.cos(w); oy = .025 * Math.sin(w * 1.3); oz = .07 * Math.sin(w) + .9 * (1 - k) * (1 - k);
        yaw += .02 * Math.sin(tsec * .07); pitch += .012 * Math.sin(tsec * .05);
      }
    }
    var s = { cx: r.left + avW / 2, cy: top + avH * .5, f0: f, f: f * (1 + .7 * (1 - k) * (1 - k)), avW: avW, avH: avH, k: k, ox: ox, oy: oy, oz: oz, yaw: yaw, pitch: pitch,
      cyw: Math.cos(yaw), syw: Math.sin(yaw), cpt: Math.cos(pitch), spt: Math.sin(pitch) };
    if(!still) SG = s;
    return s;
  }
  /* จุดในอวกาศ → จอ (อยู่หลังกล้อง = null) · กล้องเดียวกับ shader ท้องฟ้าทุกประการ */
  function sp3(s, X, Y, Z){
    var x = X - s.ox, y = Y - s.oy, z = Z - s.oz, x1 = x * s.cyw + z * s.syw, z1 = -x * s.syw + z * s.cyw, y2 = y * s.cpt + z1 * s.spt, z2 = -y * s.spt + z1 * s.cpt;
    if(z2 > -.03) return null;
    return { x: s.cx - s.f * x1 / z2, y: s.cy + s.f * y2 / z2, d: -z2 };
  }
  /* กลุ่มดาวของแต่ละเส้นทางกระจายทั่วฟ้า — ไม่มีกลุ่มไหนอยู่กลางจอ (ไม่มีใครเป็นใจกลาง)
     ในกลุ่ม ดาวเรียงตามเวลา เดินต่อกันเป็นเส้นทางของเรา · แต่ละดวงลึกไม่เท่ากัน จึงขยับไม่พร้อมกันเมื่อผู้สังเกตเคลื่อน */
  var ANCH = [[-.42, .2], [.4, .42], [-.6, -.36], [.06, -.5], [.62, -.08], [-.1, .58]], CONS = [[], [], [], [], [], []];
  function layoutStars(){
    /* จอตั้งแคบ: ดึงกลุ่มดาวเข้ามาจากขอบเล็กน้อย ไม่ให้ดาวตกขอบเวลาผู้สังเกตเคลื่อน */
    var s = skyGeo(performance.now(), true), pt = s.avW < s.avH, tx = s.avW / 2 / s.f0 * (pt ? .8 : 1), ty = s.avH / 2 / s.f0 * (pt ? .92 : 1);
    CONS = [[], [], [], [], [], []]; stars.forEach(function(n){ CONS[n.orb].push(n); });
    CONS.forEach(function(list, oi){
      var ax = Math.atan(ANCH[oi][0] * tx), ay = Math.atan(ANCH[oi][1] * ty), px = 0, py = 0, ang = hash(ORB[oi] + '|w') * TAU, lim = .1 + .022 * Math.sqrt(list.length);
      list.forEach(function(n, k){
        if(k){
          ang += (hash(n.key + '|t') - .5) * 1.6;
          var st = .036 + .03 * hash(n.key + '|s'), nx = px + Math.cos(ang) * st, ny = py + Math.sin(ang) * st;
          if(Math.hypot(nx, ny) > lim){ ang = Math.atan2(-py, -px) + (hash(n.key + '|b') - .5) * 1.2; nx = px + Math.cos(ang) * st; ny = py + Math.sin(ang) * st; }
          px = nx; py = ny;
        }
        var X = Math.tan(ax + px), Y = Math.tan(ay + py), L = Math.hypot(X, Y, 1), D = 1.05 + .75 * hash(n.key + '|d');
        n.wx = X / L * D; n.wy = Y / L * D; n.wz = -D / L;
      });
    });
  }
  function projectStars(s){
    for(var i = 0; i < stars.length; i++){
      var n = stars[i], q = n.wx == null ? null : sp3(s, n.wx, n.wy, n.wz);
      n.vis = !!q && q.x > -60 && q.x < W + 60 && q.y > -60 && q.y < H + 60;
      if(!n.vis){ n.sx = n.sy = -1e4; continue; }
      n.sx = q.x; n.sy = q.y; n.sc = clamp(1.4 / q.d, .55, 1.8);
    }
  }
  /* ── วาด ─────────────────────────────────────────────────── */
  /* ดาวหนึ่งดวง: แกนขาวร้อน + ออร่าสีตามหมวด + แฉกแสง 4 ทิศสำหรับดวงใหญ่ (วาดแบบ additive) */
  var GLOW = {};
  function glow(col){
    if(GLOW[col]) return GLOW[col];
    var c = document.createElement('canvas'); c.width = c.height = 96; var g = c.getContext('2d');
    var r = g.createRadialGradient(48, 48, 0, 48, 48, 48);
    r.addColorStop(0, 'rgba(255,255,255,1)'); r.addColorStop(.08, col); r.addColorStop(.28, col + '55'); r.addColorStop(1, col + '00');
    g.fillStyle = r; g.fillRect(0, 0, 96, 96); return (GLOW[col] = c);
  }
  function star(x, y, r, col, a, spike, gl){
    ctx.globalAlpha = a;
    var s = r * (gl || 5); ctx.drawImage(glow(col), x - s, y - s, s * 2, s * 2);
    if(spike > 0){
      var L = r * spike;
      ctx.globalAlpha = a * .55; ctx.strokeStyle = col; ctx.lineWidth = Math.max(.6, r * .22);
      ctx.beginPath(); ctx.moveTo(x - L, y); ctx.lineTo(x + L, y); ctx.moveTo(x, y - L); ctx.lineTo(x, y + L); ctx.stroke();
    }
    ctx.globalAlpha = Math.min(1, a * 1.2); ctx.fillStyle = '#ffffff';
    ctx.beginPath(); ctx.arc(x, y, Math.max(.5, r * .42), 0, TAU); ctx.fill();
  }
  /* จานกาแล็กซีเอียง: ใจกลางเป็นส่วนนูน (แบนน้อย) วงนอกเป็นจาน (แบนมาก) */
  function disc(g, x, y, sq){
    var yy = y * sq, c = Math.cos(g.tilt), s = Math.sin(g.tilt);
    return [g.cx + (x * c - yy * s) * g.R, g.cy + (x * s + yy * c) * g.R];
  }
  function place(g, tsec){
    var k = clamp(g.R / 60, .55, 1.4), belt = REDUCED ? 0 : tsec * .012, outer = REDUCED ? 0 : -tsec * .006, dsq = g.portrait ? .62 : .46, q;
    P.forEach(function(p){
      if(p.zone === 'belt'){ var a = p.a + belt; q = disc(g, Math.cos(a) * p.r, Math.sin(a) * p.r, dsq); p.back = Math.sin(a) < 0; }
      else if(p.zone === 'outer'){ var o = p.a + outer; q = disc(g, Math.cos(o) * p.r, Math.sin(o) * p.r, dsq); p.back = Math.sin(o) < 0; }
      else { q = disc(g, p.x, p.y, .86); p.back = false; }
      p.sx = q[0]; p.sy = q[1];
      p.px = p.zone === 'core' ? (1.1 + p.size * .36) * k : p.zone === 'belt' ? (.55 + p.size * .22) * k : p.zone === 'outer' ? .7 * k : (1.2 + p.size * .3) * k;
    });
  }
  function drawSystem(g, now, full){
    var tsec = (now - t0) / 1000, dimAll = full ? 1 : .3, focus = hover || sel, fx = focus && focus.f ? focus : null;
    ctx.globalCompositeOperation = 'lighter';
    /* ฝุ่นดาว: ชิ้นที่รอต่อ (ระยิบระยับเบาๆ) */
    if(full) P.forEach(function(p){
      if(p.zone !== 'outer' && p.zone !== 'belt') return;
      var lit = fx && (fx === p || fx.out.concat(fx.inn).some(function(e){ return e.a === p || e.b === p; }));
      var tw = REDUCED ? 1 : .65 + .35 * Math.sin(tsec * (1 + p.spin * 3) + p.rot * 3);
      var a = (p.zone === 'outer' ? .45 : .85) * tw * (p.back ? .7 : 1) * (fx && !lit ? .35 : 1);
      star(p.sx, p.sy, lit ? p.px * 1.8 : p.px, lit ? '#ffffff' : COL[p.cat], lit ? 1 : a, 0);
    });
    /* เส้น import ของชิ้นที่ยังไม่ต่อสาย — เห็นเมื่อแตะเท่านั้น */
    EDGES.forEach(function(e){
      if(isCore(e.a) && isCore(e.b)) return;
      var hot = fx && (e.a === fx || e.b === fx), broken = e.a.cat === 'broken' && e.b.zone === 'core';
      if(!hot && !broken && !(e.serve && full)) return;
      var gr = ctx.createLinearGradient(e.a.sx, e.a.sy, e.b.sx, e.b.sy);
      var c0 = hot ? 'rgba(255,255,255,.8)' : broken ? 'rgba(255,93,108,.42)' : 'rgba(111,178,255,.22)';
      gr.addColorStop(0, c0); gr.addColorStop(1, broken ? 'rgba(255,93,108,0)' : 'rgba(111,178,255,.05)');
      ctx.globalAlpha = dimAll; ctx.strokeStyle = gr; ctx.lineWidth = hot ? 1.2 : .7;
      ctx.beginPath(); ctx.moveTo(e.a.sx, e.a.sy); ctx.lineTo(e.b.sx, e.b.sy); ctx.stroke();
    });
    /* ออร่าใจกลางตาม waterline ของผู้ใช้ */
    var wl = coreWL == null ? 72 : coreWL, lum = .35 + wl / 100 * .65, br = REDUCED ? 0 : Math.sin(tsec * (think ? 3.4 : 1.1)) * (think ? .1 : .035);
    var hr = g.R * 1.9 * (1 + br), halo = ctx.createRadialGradient(g.cx, g.cy, 0, g.cx, g.cy, hr);
    halo.addColorStop(0, wl < 35 ? 'rgba(255,93,108,' + (.20 * lum) + ')' : 'rgba(255,214,150,' + (.18 * lum) + ')');
    halo.addColorStop(.45, 'rgba(90,140,255,' + (.07 * lum) + ')'); halo.addColorStop(1, 'rgba(0,0,0,0)');
    ctx.globalAlpha = 1; ctx.fillStyle = halo; ctx.beginPath(); ctx.arc(g.cx, g.cy, hr, 0, TAU); ctx.fill();
    /* เส้นแสงระหว่างชิ้นที่ต่อติดแล้ว (import จริง) */
    CORE_E.forEach(function(e){
      var hot = fx && (e.a === fx || e.b === fx);
      var gr = ctx.createLinearGradient(e.a.sx, e.a.sy, e.b.sx, e.b.sy);
      gr.addColorStop(0, 'rgba(255,200,120,' + (hot ? .9 : .22) + ')'); gr.addColorStop(1, 'rgba(111,178,255,' + (hot ? .9 : .18) + ')');
      ctx.globalAlpha = 1; ctx.strokeStyle = gr; ctx.lineWidth = hot ? 1.4 : .75;
      ctx.beginPath(); ctx.moveTo(e.a.sx, e.a.sy); ctx.lineTo(e.b.sx, e.b.sy); ctx.stroke();
    });
    /* ดาวหางวิ่งตามเส้น import (ผู้เรียก → ผู้ถูกเรียก) */
    if(!REDUCED && CORE_E.length && now - lastSpawn > (think ? 45 : 320)){
      lastSpawn = now; packets.push({ e: CORE_E[Math.floor(Math.random() * CORE_E.length)], at: now, dur: think ? 600 : 1300 });
    }
    packets = packets.filter(function(k){ return now - k.at < k.dur; });
    packets.forEach(function(k){
      var t = (now - k.at) / k.dur, t2 = Math.max(0, t - .18), a = Math.sin(t * Math.PI);
      var x = k.e.a.sx + (k.e.b.sx - k.e.a.sx) * t, y = k.e.a.sy + (k.e.b.sy - k.e.a.sy) * t;
      var x2 = k.e.a.sx + (k.e.b.sx - k.e.a.sx) * t2, y2 = k.e.a.sy + (k.e.b.sy - k.e.a.sy) * t2;
      var col = think ? '#ffd98f' : '#bcd6ff', tail = ctx.createLinearGradient(x2, y2, x, y);
      tail.addColorStop(0, 'rgba(255,255,255,0)'); tail.addColorStop(1, think ? 'rgba(255,217,143,.9)' : 'rgba(188,214,255,.8)');
      ctx.globalAlpha = a; ctx.strokeStyle = tail; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.moveTo(x2, y2); ctx.lineTo(x, y); ctx.stroke();
      star(x, y, clamp(g.R / 40, 1, 2.2), col, a, 0);
    });
    /* ชิ้นที่ต่อติดแล้ว + หน้าเว็บ + ชิ้นที่เสีย */
    P.forEach(function(p){
      if(p.zone !== 'core' && p.zone !== 'web' && p.zone !== 'broken') return;
      var lit = fx === p, a = p.zone === 'broken' ? .75 + (REDUCED ? 0 : .25 * Math.sin(tsec * 2.2 + p.i)) : 1;
      var spike = p.zone === 'core' && p.size > 4.2 ? 3.2 : p.zone === 'web' ? 2.2 : 0;
      star(p.sx, p.sy, lit ? p.px * 1.6 : p.px, lit ? '#ffffff' : COL[p.cat], a * (p.zone === 'core' ? .62 : 1) * (fx && !lit ? .7 : 1), lit ? 4 : spike, p.zone === 'core' ? 3.2 : 4.5);
    });
    ctx.globalCompositeOperation = 'source-over';
    if(fx){
      ctx.globalAlpha = .9; ctx.strokeStyle = '#fff'; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(fx.sx, fx.sy, fx.px * 2.4 + 6, 0, TAU); ctx.stroke();
      /* สัญลักษณ์ของเครื่องมือ — ภาพเดียว อ่านจากสัญลักษณ์ ไม่ใช่ชื่อไฟล์ */
      var sym = fx.f[4] || '', nm = fx.f[0].split('/').pop();
      if(sym.length > 64) sym = sym.slice(0, 63) + '…';
      var tx = fx.sx + fx.px * 2.4 + 12, right = tx + 8 * Math.max(sym.length, nm.length) > W;
      ctx.textAlign = right ? 'end' : 'start'; ctx.textBaseline = 'middle';
      if(right) tx = fx.sx - fx.px * 2.4 - 12;
      if(sym){ ctx.globalAlpha = .95; ctx.fillStyle = '#ffe2a8'; ctx.font = '500 13px "IBM Plex Mono", monospace'; ctx.fillText(sym, tx, fx.sy - 7); }
      ctx.globalAlpha = .6; ctx.fillStyle = '#c9d4f5'; ctx.font = '400 10px "IBM Plex Mono", monospace'; ctx.fillText(nm, tx, sym ? fx.sy + 9 : fx.sy);
      ctx.textAlign = 'start';
    }
    /* ชื่อโฟลเดอร์ของกลุ่มที่รอต่อ */
    if(full && view === 'universe' && W >= 640){
      ctx.globalAlpha = .55; ctx.fillStyle = '#c9d4f5'; ctx.font = '500 10px "IBM Plex Mono", monospace'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
      BELT_DIRS.forEach(function(d){
        if(d.n < 6) return; var a = d.a + (REDUCED ? 0 : tsec * .012), q = disc(g, Math.cos(a) * 3.0, Math.sin(a) * 3.0, g.portrait ? .62 : .46);
        ctx.fillText(d.name, q[0], q[1]);
      });
      ctx.textAlign = 'start';
    }
    ctx.globalAlpha = 1;
  }
  /* ── สนามดาว 3 มิติรอบตัวผู้สังเกต: ทุกทิศเท่ากัน (Uniform Distribution) + หนาขึ้นตามแนวทางช้างเผือก
     ร้อนสลับเย็น: ฟ้า · ขาว · ทอง · กุหลาบ · เทอร์ควอยซ์ · ดาวใกล้เลื่อนมากเมื่อผู้สังเกตเคลื่อน = เห็นความลึกจริง */
  var SKYF = [];
  function buildSkyField(){
    SKYF = [];
    var n = clamp(Math.round(W * H / 1100), 340, 1200), N = GAL.N, G = GAL.G, E = GAL.E;
    for(var i = 0; i < n; i++){
      var d;
      if(Math.random() < .55){
        var l = Math.random() * TAU, b = (Math.random() + Math.random() + Math.random() + Math.random() - 2) * .085, cb = Math.cos(b), cl = Math.cos(l) * cb, sl = Math.sin(l) * cb, sb = Math.sin(b);
        d = [G[0] * cl + E[0] * sl + N[0] * sb, G[1] * cl + E[1] * sl + N[1] * sb, G[2] * cl + E[2] * sl + N[2] * sb];
      } else { var z = Math.random() * 2 - 1, th = Math.random() * TAU, rr = Math.sqrt(1 - z * z); d = [rr * Math.cos(th), z, rr * Math.sin(th)]; }
      var u = Math.random(), D = u < .08 ? .25 + Math.random() * .4 : u < .38 ? .65 + Math.random() * .9 : 1.6 + Math.random() * 2.6, c = Math.random();
      SKYF.push({ x: d[0] * D, y: d[1] * D, z: d[2] * D, m: Math.pow(Math.random(), 2.6), tw: Math.random() * TAU, sp: .5 + Math.random() * 1.8, lx: null, ly: 0,
        c: c < .38 ? '#cfe0ff' : c < .66 ? '#ffffff' : c < .84 ? '#ffd9a8' : c < .93 ? '#ffc0d0' : '#b8f0ff' });
    }
  }
  function drawSky(s, now){
    var tsec = (now - t0) / 1000, warp = s.k < 1;
    ctx.globalCompositeOperation = 'lighter';
    for(var i = 0; i < SKYF.length; i++){
      var st = SKYF[i], q = sp3(s, st.x, st.y, st.z);
      if(!q || q.x < -30 || q.x > W + 30 || q.y < -30 || q.y > H + 30){ st.lx = null; continue; }
      var near = Math.min(1.2, .9 / q.d), a = clamp(.12 + .95 * st.m * near + .1 * near, 0, 1), r = .35 + 1.8 * st.m * near;
      if(!REDUCED) a *= .8 + .2 * Math.sin(tsec * st.sp + st.tw);
      if(RIP.length){ var bo = rippleAt(q.x, q.y, now); if(bo > .01){ a = Math.min(1, a * (1 + 2.6 * bo) + .25 * bo); r *= 1 + .9 * bo; } }
      ctx.globalAlpha = a; ctx.fillStyle = st.c; ctx.strokeStyle = st.c;
      if(warp && st.lx != null && Math.abs(q.x - st.lx) + Math.abs(q.y - st.ly) > 2.5){ ctx.lineWidth = Math.max(.5, r * .7); ctx.beginPath(); ctx.moveTo(st.lx, st.ly); ctx.lineTo(q.x, q.y); ctx.stroke(); }
      else if(r < 1.15) ctx.fillRect(q.x - r / 2, q.y - r / 2, r, r);
      else ctx.drawImage(glow(st.c), q.x - r * 3, q.y - r * 3, r * 6, r * 6);
      st.lx = q.x; st.ly = q.y;
    }
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  }
  /* ── แสงเดียวกัน: แตะดาวของเรา (หรือมีดาวดวงใหม่เกิด) แสงจะแผ่ออกไปทั่วฟ้า ดาวดวงอื่นสว่างขึ้นเมื่อแสงผ่าน
     "ช่วยให้เราเห็นความงดงามของผู้อื่นที่อาบแสงเดียวกับเรา" ───────────────────────────────── */
  var RIP = [];
  function ripple(n, now){ if(!REDUCED && n) RIP.push({ n: n, at: now }); }
  function rippleAt(x, y, now){
    var b = 0, sp = Math.hypot(W, H) * .5;
    for(var k = 0; k < RIP.length; k++){
      var R = RIP[k], age = (now - R.at) / 1000, dd = Math.hypot(x - R.n.sx, y - R.n.sy) - age * sp;
      b += Math.exp(-dd * dd / 3600) * Math.pow(Math.max(0, 1 - age / 2.4), 1.5);
    }
    return Math.min(1, b);
  }
  function drawRipples(now){
    RIP = RIP.filter(function(R){ return now - R.at < 2400; });
    var sp = Math.hypot(W, H) * .5;
    RIP.forEach(function(R){
      var age = (now - R.at) / 1000; if(R.n.sx < -9e3) return;
      var fa = Math.pow(1 - age / 2.4, 2); ctx.strokeStyle = R.n.col; ctx.globalCompositeOperation = 'lighter';
      ctx.globalAlpha = .05 * fa; ctx.lineWidth = 26; ctx.beginPath(); ctx.arc(R.n.sx, R.n.sy, age * sp, 0, TAU); ctx.stroke();
      ctx.globalAlpha = .07 * fa; ctx.lineWidth = 1; ctx.stroke(); ctx.globalCompositeOperation = 'source-over';
    });
    ctx.globalAlpha = 1;
  }
  /* ป้ายชื่อ: ลองตำแหน่งตามลำดับจนไม่ชนป้ายอื่น ข้อความ "ยังไม่มีดาว" และไม่ตกขอบจอ · ไม่มีที่ = ไม่เขียน (คลีนไว้ก่อน) */
  var LBL = [];
  function placeText(cands, w){
    var h = 14, xl = SG ? SG.cx - SG.avW / 2 + 6 : 6;          /* ไม่ให้ป้ายมุดใต้แถบข้าง */
    for(var k = 0; k < cands.length; k++){
      var tx = cands[k][0], ty = cands[k][1], box = [tx - 2, ty - h / 2, tx + w + 2, ty + h / 2];
      if(box[0] < xl || box[2] > W - 6 || box[1] < 4 || box[3] > H - 4) continue;
      if(LBL.some(function(b){ return box[0] < b[2] && box[2] > b[0] && box[1] < b[3] && box[3] > b[1]; })) continue;
      LBL.push(box); return cands[k];
    }
    return null;
  }
  /* ── กลุ่มดาว: เส้นบางเชื่อมการตัดสินใจในเส้นทางเดียวกันตามลำดับเวลา (24 ช่วงล่าสุด) · เส้นทางที่เลือก/แตะสว่างขึ้น ── */
  function drawConstellations(now){
    var hotR = focusR != null && now - focusT < 2600 ? focusR : null, act = hover || sel;
    ctx.lineCap = 'round';
    for(var oi = 0; oi < 6; oi++){
      var L = CONS[oi]; if(!L.length) continue;
      var on = hotR === ORB[oi] || !!(act && act.kind === 'd' && act.orb === oi), from = Math.max(1, L.length - 24);
      for(var k = from; k < L.length; k++){
        var a = L[k - 1], b = L[k]; if(!a.vis || !b.vis) continue;
        var gr = ctx.createLinearGradient(a.sx, a.sy, b.sx, b.sy); gr.addColorStop(0, a.col); gr.addColorStop(1, b.col);
        ctx.globalAlpha = (on ? .55 : .2) * (.5 + .5 * (k - from + 1) / (L.length - from)); ctx.strokeStyle = gr; ctx.lineWidth = on ? 1.1 : .8;
        ctx.beginPath(); ctx.moveTo(a.sx, a.sy); ctx.lineTo(b.sx, b.sy); ctx.stroke();
      }
      var m = 0, cx = 0, by = -1e9; L.forEach(function(n){ if(n.vis){ cx += n.sx; by = Math.max(by, n.sy); m++; } }); if(!m) continue;
      cx /= m; ctx.font = '400 10.5px "Noto Sans Thai Looped", sans-serif'; ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
      var lbl = (ROUTE_NAME[ORB[oi]] || ORB[oi]) + ' · ' + L.length, w = ctx.measureText(lbl).width;
      var at = placeText([[cx - w / 2, by + 22], [cx - w / 2, by + 36], [cx + 18, by], [cx - w - 18, by]], w);
      if(at){ ctx.globalAlpha = on ? .92 : .5; ctx.fillStyle = on ? '#fff1d2' : '#d8e0f5'; ctx.fillText(lbl, at[0], at[1]); }
    }
    ctx.globalAlpha = 1;
  }
  /* ── พลังงานที่มีเจตจำนง ──────────────────────────────────────
     Energy in motion without intention = ฝุ่นที่ลอยไปเรื่อย · ที่นี่แสงทุกสายมีปลายทาง:
     ไหลไปตามเส้นกลุ่มดาว จากการตัดสินใจเก่า → ดวงล่าสุด (ปัจจุบัน) · กำลังคิด = ไหลเร็วขึ้นและอุ่นขึ้น */
  var FLOW = [];
  function drawFlows(now, dt){
    if(REDUCED) return;
    ctx.globalCompositeOperation = 'lighter';
    for(var oi = 0; oi < 6; oi++){
      var L = CONS[oi], f = FLOW[oi];
      if(L.length < 2){ FLOW[oi] = null; continue; }
      if(!f) f = FLOW[oi] = { p: Math.max(0, L.length - 7) - hash(ORB[oi] + '|f') * 3 };
      f.p += dt * (think ? 1.9 : .5);
      if(f.p >= L.length - 1){ f.p = Math.max(0, L.length - 7) - 1.5 - Math.random() * 2; continue; }
      if(f.p < 0) continue;
      var k = Math.floor(f.p), u = f.p - k, a = L[k], b = L[k + 1];
      if(!a.vis || !b.vis) continue;
      var x = a.sx + (b.sx - a.sx) * u, y = a.sy + (b.sy - a.sy) * u, u2 = Math.max(0, u - .25), x2 = a.sx + (b.sx - a.sx) * u2, y2 = a.sy + (b.sy - a.sy) * u2;
      var tail = ctx.createLinearGradient(x2, y2, x, y), col = think ? '#ffd98f' : '#cfe0ff';
      tail.addColorStop(0, 'rgba(255,255,255,0)'); tail.addColorStop(1, think ? 'rgba(255,217,143,.85)' : 'rgba(207,224,255,.7)');
      ctx.globalAlpha = .9; ctx.strokeStyle = tail; ctx.lineWidth = 1.3; ctx.beginPath(); ctx.moveTo(x2, y2); ctx.lineTo(x, y); ctx.stroke();
      ctx.drawImage(glow(col), x - 5, y - 5, 10, 10);
    }
    ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
  }
  /* ── ดาวการตัดสินใจ: แฉก 6 แฉกแบบภาพจากกล้องเจมส์ เว็บบ์ · สีตามความเสี่ยง · ใกล้ใหญ่ ไกลเล็ก ── */
  var SPK = {};
  function spikes(col){
    if(SPK[col]) return SPK[col];
    var c = document.createElement('canvas'); c.width = c.height = 128; var g = c.getContext('2d'); g.translate(64, 64); g.lineCap = 'round';
    function ray(an, L, w, al){
      var dx = Math.cos(an) * L, dy = Math.sin(an) * L, gr = g.createLinearGradient(-dx, -dy, dx, dy);
      gr.addColorStop(0, col + '00'); gr.addColorStop(.5, col + al); gr.addColorStop(1, col + '00');
      g.strokeStyle = gr; g.lineWidth = w; g.beginPath(); g.moveTo(-dx, -dy); g.lineTo(dx, dy); g.stroke();
    }
    for(var k = 0; k < 3; k++) ray(Math.PI / 2 + k * Math.PI / 3, 62, 1.8, 'dd');
    ray(0, 30, 1.2, '80');
    return (SPK[col] = c);
  }
  function jwst(x, y, r, col, a){
    var gs = r * 5, L = r * 4.4;
    ctx.globalAlpha = a; ctx.drawImage(glow(col), x - gs, y - gs, gs * 2, gs * 2);
    ctx.globalAlpha = a * .75; ctx.drawImage(spikes(col), x - L, y - L, L * 2, L * 2);
    ctx.globalAlpha = Math.min(1, a * 1.2); ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(x, y, Math.max(.6, r * .42), 0, TAU); ctx.fill();
  }
  function drawStars(now){
    var tsec = (now - t0) / 1000, sz = SG ? clamp(SG.f0 / 650, .7, 1.15) : 1, last = stars.length - 1;
    for(var i = 0; i < stars.length; i++){
      var n = stars[i]; if(!n.vis) continue;
      var r = n.r * sz * n.sc, flash = 0;
      for(var j = 0; j < births.length; j++){
        var b = births[j]; if(b.ts !== n.ts) continue;
        var k = Math.min(1, (now - b.at) / 1600); if(!b.rip){ b.rip = 1; ripple(n, now); }
        r *= .25 + .75 * (1 - Math.pow(1 - k, 3)) + 1.4 * (1 - k) * (1 - k); flash = 1 - k;
      }
      var hl = n === hover || n === sel;
      ctx.globalCompositeOperation = 'lighter'; jwst(n.sx, n.sy, r * .9, hl ? '#ffffff' : n.col, Math.min(1, .92 + flash)); ctx.globalCompositeOperation = 'source-over';
      if(hl){ ctx.globalAlpha = .9; ctx.strokeStyle = '#fff'; ctx.lineWidth = 1.1; ctx.beginPath(); ctx.arc(n.sx, n.sy, r + 6, 0, TAU); ctx.stroke(); }
      if(i === last && !REDUCED){ var pr = (tsec % 2.6) / 2.6; ctx.globalAlpha = .55 * (1 - pr); ctx.strokeStyle = n.col; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(n.sx, n.sy, r + 4 + pr * 18, 0, TAU); ctx.stroke(); }
    }
    ctx.globalAlpha = 1;
  }
  /* ── กลุ่มดาวของฉัน ─────────────────────────────────────────────
     ตำแหน่งดาวคงที่ตามรหัสของข้อความ (เปิดกี่ครั้งก็ที่เดิม) และห่างกันพอให้นิ้วแตะถูกดวง
     เส้นบางๆ ต่อดาวตามลำดับเวลาที่คุย = เส้นทางของเรา · ดาวล่าสุดเรืองแสงเบาๆ · ลดการเคลื่อนไหว = นิ่งสนิท */
  var MY = { key: '' };
  function myArea(){
    var top = 0, bot = H - 110, l = 0, r = W, ut = $('#view-universe .u-top'), lg = $('#u-legend'), vw = $('#view-universe');
    if(ut){ var q = ut.getBoundingClientRect(); top = q.bottom + 26; }
    if(lg){ var q2 = lg.getBoundingClientRect(); if(q2.height) bot = q2.top - 26; }
    /* จอคอมมีแถบเมนูซ้าย: วางดาวเฉพาะในกรอบหน้าจักรวาล ไม่ให้ดาว/เส้นไปซ่อนใต้เมนู */
    if(vw){ var q3 = vw.getBoundingClientRect(); if(q3.width > 200){ l = Math.max(0, q3.left); r = Math.min(W, q3.right); } }
    return { l: l + 34, r: r - 34, t: Math.max(top, 90), b: Math.max(bot, top + 160) };
  }
  function layoutMine(){
    var A = myArea(), k = W + 'x' + H + '|' + stars.length + '|' + Math.round(A.l) + '|' + Math.round(A.r) + '|' + Math.round(A.t) + '|' + Math.round(A.b);
    if(MY.key === k) return; MY.key = k;
    var min = Math.max(34, Math.min(70, Math.sqrt((A.r - A.l) * (A.b - A.t) / Math.max(1, stars.length)) * .55)), put = [];
    /* ดวงถัดไปเกิดใกล้ดวงก่อน (เดินต่อเป็นทางเดียว) — เส้นไม่ตัดกันไปมาเหมือนวางสุ่มทั่วจอ */
    stars.forEach(function(n, i){
      var best = null, bd = -1, pv = put[i - 1];
      for(var tr = 0; tr < 16; tr++){
        var x, y;
        if(!pv){ x = A.l + (.2 + .6 * hash(n.key + '|mx' + tr)) * (A.r - A.l); y = A.t + (.2 + .6 * hash(n.key + '|my' + tr)) * (A.b - A.t); }
        else { var an = hash(n.key + '|ma' + tr) * TAU, ds = min * (1.15 + .8 * hash(n.key + '|md' + tr)); x = pv[0] + Math.cos(an) * ds; y = pv[1] + Math.sin(an) * ds; }
        if(x < A.l || x > A.r || y < A.t || y > A.b) continue;
        var d = 1e9;
        for(var j = 0; j < put.length; j++) d = Math.min(d, Math.hypot(put[j][0] - x, put[j][1] - y));
        if(d >= min){ best = [x, y]; break; }
        if(d > bd){ bd = d; best = [x, y]; }
      }
      if(!best) best = [A.l + hash(n.key + '|mx') * (A.r - A.l), A.t + hash(n.key + '|my') * (A.b - A.t)];
      put.push(best); n.sx = best[0]; n.sy = best[1]; n.vis = true;
    });
  }
  function drawMySky(now){
    layoutMine();
    var tsec = (now - t0) / 1000, last = stars.length - 1, from = Math.max(1, stars.length - 60);
    /* เส้นทางของเรา: ต่อดาวตามลำดับเวลา (60 ดวงล่าสุด) · เส้นใหม่สว่างกว่าเส้นเก่า */
    ctx.save(); ctx.lineCap = 'round';
    for(var i = from; i < stars.length; i++){
      var a = stars[i - 1], b = stars[i], age = (stars.length - i) / 60;
      ctx.globalAlpha = .12 + .3 * (1 - age); ctx.strokeStyle = THEME.dark ? '#c9d4ff' : '#5b6aa8'; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(a.sx, a.sy); ctx.lineTo(b.sx, b.sy); ctx.stroke();
    }
    ctx.restore();
    for(var k = 0; k < stars.length; k++){
      var n = stars[k], risk = n.m && n.m.tr ? n.m.tr.risk || 0 : 0, r = 3.2 + Math.min(4, risk / 25), flash = 0;
      for(var j = 0; j < births.length; j++){
        var bb = births[j]; if(bb.ts !== n.ts) continue;
        var e = Math.min(1, (now - bb.at) / 1600); r *= .25 + .75 * (1 - Math.pow(1 - e, 3)) + (REDUCED ? 0 : 1.2 * (1 - e) * (1 - e)); flash = 1 - e;
      }
      var hl = n === hover || n === sel, tw = REDUCED ? 1 : .86 + .14 * Math.sin(tsec * .8 + hash(n.key) * 6.28);
      n.px = Math.max(16, r * 3);
      ctx.globalCompositeOperation = 'lighter'; jwst(n.sx, n.sy, r, hl ? '#ffffff' : n.col, Math.min(1, tw + flash)); ctx.globalCompositeOperation = 'source-over';
      /* ความเสี่ยงสูงมีวงรอบดาวเพิ่ม — คนตาบอดสีแยกได้โดยไม่ต้องพึ่งสี */
      if(risk >= 75){ ctx.globalAlpha = .8; ctx.strokeStyle = n.col; ctx.lineWidth = 1.2; ctx.beginPath(); ctx.arc(n.sx, n.sy, r + 5, 0, TAU); ctx.stroke(); }
      if(hl){ ctx.globalAlpha = .9; ctx.strokeStyle = THEME.dark ? '#fff' : '#334'; ctx.lineWidth = 1.1; ctx.beginPath(); ctx.arc(n.sx, n.sy, r + 9, 0, TAU); ctx.stroke(); }
      if(k === last && !REDUCED){ var pr = (tsec % 3.2) / 3.2; ctx.globalAlpha = .45 * (1 - pr); ctx.strokeStyle = n.col; ctx.lineWidth = 1; ctx.beginPath(); ctx.arc(n.sx, n.sy, r + 6 + pr * 16, 0, TAU); ctx.stroke(); }
      ctx.globalAlpha = 1;
    }
  }
  function frame(now){
    raf = 0;
    if(document.hidden || !W) return;
    /* จำกัดไว้ 90 เฟรม/วินาที: จอ 120/144/240 Hz วาดเฉลี่ย 90 (สะสมเวลา) · จอ 60 Hz วาดทุกเฟรม */
    var gap = (now - (dtLast || now)) / 1000;
    fpsAcc = Math.min(fpsAcc + gap, 2 / 90);
    if(dtLast && fpsAcc + 1e-4 < 1 / 90){ dtLast = now; raf = requestAnimationFrame(frame); return; }
    fpsAcc = Math.max(0, fpsAcc - 1 / 90);
    var dt = clamp((now - (fpsT || now)) / 1000, 0, .05); fpsT = now; dtLast = now; lastPaint = now;
    if(view !== 'universe'){ backdrop(now, dt); return; }
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.globalAlpha = 1;
    var tsec = (now - t0) / 1000, useGL = GLX && GLX.ok();
    if(mode === 'decisions'){
      /* กลุ่มดาวของฉัน: ฟ้านิ่ง ไม่ลอย ไม่ซูม ไม่ลากหมุน — ทุกการคุยได้ดาว 1 ดวง ต่อเส้นตามลำดับเวลา
         (เจ้าของโปรเจกต์: หน้าเดิมที่ฟ้าไหวตลอดและดาวเล็กจนมองไม่เห็น "ดูเวียนหัว") */
      var s = skyGeo(now, true);
      if(useGL){ ctx.clearRect(0, 0, W, H); GLX.pace(dt); GLX.sky(s, 0, .85); }
      else ctx.drawImage(bgCv, 0, 0, W, H);
      LBL = [];
      drawMySky(now); drawRipples(now);
    } else {
      var g = geo();
      if(useGL){ ctx.clearRect(0, 0, W, H); GLX.pace(dt); GLX.sky(skyGeo(now, true), tsec, .55); }
      else ctx.drawImage(bgCv, 0, 0, W, H);
      drawField(now, dt, g);
      for(var i = 0; i < twk.length; i++){
        var tw = twk[i]; ctx.globalAlpha = REDUCED ? .5 : .25 + .75 * Math.abs(Math.sin(tsec * tw.s + tw.p));
        ctx.fillStyle = tw.warm ? '#ffe2b0' : '#cfe0ff'; ctx.beginPath(); ctx.arc(tw.x, tw.y, tw.r, 0, TAU); ctx.fill();
      }
      ctx.globalAlpha = 1;
      place(g, tsec); drawSystem(g, now, true);
    }
    births = births.filter(function(b){ return now - b.at < 1700; });
    if(!REDUCED || births.length || RIP.length) kick();
  }
  function kick(){ if(!raf) raf = requestAnimationFrame(frame); }
  window.KD_kick = kick;                                  /* เปลี่ยนโหมดสีแล้ววาดฉากใหม่ทันที */
  /* ฉากหลังหน้าปรึกษา/เครื่องมือ/ระบบ: กาแล็กซีเดียวกับแท็บจักรวาล ไม่มีวงโคจร/ป้าย
     หรี่ลงให้อ่านแชทสบาย (#veil หรี่เพิ่มเองเมื่อมีข้อความ) · หมุนช้ามาก */
  /* ── วงโคจรของ 6 เส้นทางรอบโลก (แบบภาพอ้างอิง) ──────────────────────────
     เส้นบางเกือบโปร่ง ชื่อเส้นทางเขียนตามแนววง · เส้นทางที่เลือกอยู่ (ชิปเส้นทาง) เรืองสีของมัน
     สถานีอวกาศเล็กๆ วิ่งบนทุกวง ครึ่งหลังของวงและสถานีที่อ้อมไปหลังโลกถูกโลกบังจริง */
  var ROUTE_EN = ['GENERAL', 'RISK', 'CIVIL', 'SURVIVAL', 'COLLAPSE', 'VEGA'];
  function drawRoutes(cx, cy, R, tsec, A, top, bottom){
    if(A < .01) return;
    var cur = typeof Route !== 'undefined' ? Route : 'general', hasLS = 'letterSpacing' in ctx;
    function orbit(i){
      var rr = R * (1.12 + i * .2), k = .3 + i * .02, tau = -.17 + (i % 2 ? .05 : -.02) + i * .008, ct = Math.cos(tau), st = Math.sin(tau);
      return function(a){ var x = Math.cos(a) * rr, y = Math.sin(a) * rr * k; return { x: cx + x * ct - y * st, y: cy + x * st + y * ct, front: Math.sin(a) > 0, a: a, rr: rr, k: k, ct: ct, st: st }; };
    }
    function hidden(q){ return !q.front && Math.hypot(q.x - cx, q.y - cy) < R * 1.02; }
    ctx.save(); ctx.lineCap = 'round'; var boxes = [];
    for(var i = 0; i < 6; i++){
      var P = orbit(i), on = ORB[i] === cur, col = PCOL[i];
      /* เส้นวง: ครึ่งหลังจางกว่า · ช่วงที่อยู่หลังโลกไม่วาด */
      for(var pass = 0; pass < (on ? 2 : 1); pass++){
        ctx.beginPath(); var pen = false;
        for(var k2 = 0; k2 <= 180; k2++){
          var q = P(k2 / 180 * TAU);
          if(hidden(q)){ pen = false; continue; }
          if(pen) ctx.lineTo(q.x, q.y); else { ctx.moveTo(q.x, q.y); pen = true; }
        }
        if(on){ ctx.strokeStyle = col; ctx.globalAlpha = A * (pass ? .9 : .16); ctx.lineWidth = pass ? 1 : 4; }
        else { ctx.strokeStyle = THEME.dark ? 'rgba(70,60,110,1)' : 'rgba(226,232,246,1)'; ctx.globalAlpha = A * (THEME.dark ? .22 : .26); ctx.lineWidth = .8; }
        ctx.stroke();
      }
      /* ชื่อเส้นทางตามแนววง: ด้านหน้าล่าง สลับซ้าย/ขวา · ถ้าตกจอหรือชนช่องพิมพ์ ย้ายไปอีกฝั่ง */
      ctx.font = '500 9px "IBM Plex Mono", monospace'; if(hasLS) ctx.letterSpacing = '2.5px';
      var txt = ROUTE_EN[i], tw = ctx.measureText(txt).width, cand = i % 2 ? [.62, 2.52] : [2.52, .62], spot = null;
      cand = cand.map(function(c){ return c + (i - 2.5) * .06; });
      for(var c = 0; c < cand.length && !spot; c++){
        var q2 = P(cand[c]), nx = q2.x - cx, ny = q2.y - cy, nl = Math.hypot(nx, ny) || 1, lx = q2.x + nx / nl * 9, ly = q2.y + ny / nl * 9;
        var bx = [lx - tw / 2 - 4, ly - 8, lx + tw / 2 + 4, ly + 8];
        var clash = boxes.some(function(o){ return bx[0] < o[2] && bx[2] > o[0] && bx[1] < o[3] && bx[3] > o[1]; });
        if(!clash && lx - tw / 2 > 8 && lx + tw / 2 < W - 8 && ly > top + 10 && ly < bottom - 14){ spot = { q: q2, x: lx, y: ly }; boxes.push(bx); }
      }
      if(spot && !CINEMA.on){
        var tx = -Math.sin(spot.q.a) * spot.q.rr, ty = Math.cos(spot.q.a) * spot.q.rr * spot.q.k;
        var ang = Math.atan2(tx * spot.q.st + ty * spot.q.ct, tx * spot.q.ct - ty * spot.q.st);
        if(ang > Math.PI / 2) ang -= Math.PI; if(ang < -Math.PI / 2) ang += Math.PI;
        ctx.save(); ctx.translate(spot.x, spot.y); ctx.rotate(ang);
        ctx.globalAlpha = A * (on ? .95 : .5); ctx.fillStyle = on ? col : (THEME.dark ? '#5d5480' : '#d6def2'); ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        ctx.fillText(txt, 0, 0); ctx.restore();
      }
      if(hasLS) ctx.letterSpacing = '0px';
      /* สถานีอวกาศ: แผงโซลาร์สองปีก + ตัวสถานี หันตามทิศที่วิ่ง · สะท้อนแสงเป็นจังหวะ */
      var sa = i * 1.9 + 2.2 + (REDUCED ? 0 : tsec * .05 / (1 + i * .35)), sq = P(sa);
      if(!hidden(sq)){
        var dx = -Math.sin(sa) * sq.rr, dy = Math.cos(sa) * sq.rr * sq.k, sang = Math.atan2(dx * sq.st + dy * sq.ct, dx * sq.ct - dy * sq.st);
        var sz = (sq.front ? 1 : .78) * clamp(R / 110, .7, 1.25), al = A * (sq.front ? 1 : .55);
        ctx.save(); ctx.translate(sq.x, sq.y); ctx.rotate(sang + Math.PI / 2); ctx.scale(sz, sz); ctx.globalAlpha = al;
        ctx.strokeStyle = 'rgba(220,226,240,.9)'; ctx.lineWidth = .7; ctx.beginPath(); ctx.moveTo(-8, 0); ctx.lineTo(8, 0); ctx.stroke();
        ctx.fillStyle = on ? col : 'rgba(140,175,235,.95)'; ctx.fillRect(-8.5, -2.2, 4.6, 4.4); ctx.fillRect(3.9, -2.2, 4.6, 4.4);
        ctx.fillStyle = '#eef1f8'; ctx.fillRect(-2, -1.6, 4, 3.2);
        var gl2 = REDUCED ? .3 : Math.max(0, Math.sin(tsec * 1.3 + i * 2.1)); 
        if(gl2 > .85){ ctx.globalCompositeOperation = 'lighter'; ctx.drawImage(glow('#fff2d6'), -6, -6, 12, 12); ctx.globalCompositeOperation = 'source-over'; }
        ctx.restore();
      }
    }
    ctx.restore(); ctx.globalAlpha = 1;
  }
  /* ป้ายชื่อดวงอาทิตย์และดาวเคราะห์ (แบบภาพอ้างอิง) — ตัวเล็ก สีขาวนวล อยู่เหนือแต่ละดวง ไม่ตกขอบจอ */
  function drawBodyLabels(B, R, A, top){
    if(A < .01) return;
    ctx.save(); ctx.font = '500 11px "Noto Sans Thai Looped", system-ui, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'bottom'; var placed = [];
    [['Sun', B.sun, 1.25], ['Saturn', B.sat, 1.25], ['Jupiter', B.jup, 1.35], ['Uranus', B.ura, 1.6]].forEach(function(b){
      if(b[1][0] < -20 || b[1][0] > W + 20 || b[1][1] < -20 || b[1][1] > H + 20) return;      /* ออกนอกจอ = ไม่มีป้ายค้างที่ขอบ */
      if(b[0] !== 'Sun' && Math.hypot(b[1][0] - B.cx, b[1][1] - B.cy) < R) return;              /* อยู่หลังโลก โลกบังทั้งดวงและป้าย */
      var x = b[1][0], y = b[1][1] - b[1][2] * b[2] - 4, w = ctx.measureText(b[0]).width;
      x = clamp(x, w / 2 + 6, W - w / 2 - 6); if(y < top + 12) y = b[1][1] + b[1][2] * b[2] + 16;
      /* ดาวโคจรเข้าใกล้กัน → ย้ายป้ายไปใต้ดวง · ถ้ายังชนก็ไม่แสดง */
      function hit(yy){ return placed.some(function(o){ return Math.abs(o[0] - x) < (o[2] + w) / 2 + 4 && Math.abs(o[1] - yy) < 14; }); }
      if(hit(y)) y = b[1][1] + b[1][2] * b[2] + 16;
      if(hit(y)) return;
      placed.push([x, y, w]);
      ctx.globalAlpha = A * .82; ctx.fillStyle = THEME.dark ? '#3d3558' : '#eef1f8'; ctx.shadowColor = THEME.dark ? 'rgba(255,255,255,.7)' : 'rgba(0,0,0,.6)'; ctx.shadowBlur = 4;
      ctx.fillText(b[0], x, y);
    });
    ctx.restore(); ctx.globalAlpha = 1;
  }
  /* ── ท้องฟ้าจริงแบบ Stellarium ─────────────────────────────────────────
     ดาวจริง 5,804 ดวงรอบดาวลูกไก่ (กลุ่มดาววัว · นายพราน · เพอร์ซิอุส) จากแคตตาล็อก Hipparcos
     — static/earth/sky_taurus.json (scripts/build_sky_stars.py) · ตำแหน่งจริง ความสว่างจริง สีจริงจากค่า B−V
     ฉายแบบ gnomonic ให้ดาวลูกไก่อยู่ฟ้าด้านบนซ้าย ทิศเหนือขึ้นบน ตะวันออกอยู่ซ้าย (แบบมองฟ้าจริง)
     วาดลงผืนผ้าแยกครั้งเดียว (เปลี่ยนเมื่อขนาดจอ/โหมดสีเปลี่ยน) แล้วแปะทุกเฟรม — มือถือไม่หน่วง */
  var SKY = { data: null, busy: false, key: '', cv: null, hit: null };
  function openPleiades(h){
    function go(){ if(window.KD_pleiades) KD_pleiades.open({ x: h.x, y: h.y, k: h.k, stars: SKY.data.stars, onClose: kick }); }
    if(window.KD_pleiades) return go();
    var sc = document.createElement('script'); sc.src = '/static/pleiades_view.js'; sc.onload = go; document.head.appendChild(sc);
  }
  function loadSky(){
    if(SKY.data || SKY.busy) return; SKY.busy = true;
    fetch('/static/earth/sky_taurus.json').then(function(r){ return r.ok ? r.json() : null; })
      .then(function(d){ if(d && d.stars && d.stars.length){ SKY.data = d; kick(); } }).catch(function(){})
      .then(function(){ SKY.busy = false; });
  }
  var BV = [[-.4, [155, 176, 255]], [-.1, [178, 198, 255]], [0, [205, 217, 255]], [.3, [238, 240, 255]], [.6, [255, 243, 230]],
            [.9, [255, 224, 186]], [1.2, [255, 204, 150]], [1.6, [255, 176, 110]], [2.1, [255, 148, 86]]];
  function bvRGB(b){                                    /* สีดาวตามอุณหภูมิ: ร้อนฟ้า → เย็นส้ม */
    if(!(b > BV[0][0])) return BV[0][1];
    for(var i = 1; i < BV.length; i++) if(b <= BV[i][0]){
      var t = (b - BV[i - 1][0]) / (BV[i][0] - BV[i - 1][0]), a = BV[i - 1][1], c = BV[i][1];
      return [a[0] + (c[0] - a[0]) * t, a[1] + (c[1] - a[1]) * t, a[2] + (c[2] - a[2]) * t];
    }
    return BV[BV.length - 1][1];
  }
  function gno(ra, dec, ra0, dec0){                      /* องศา → ระนาบภาพ (องศา) · null = อยู่หลังกล้อง */
    var R = Math.PI / 180, d = dec * R, d0 = dec0 * R, h = (ra - ra0) * R;
    var cc = Math.sin(d0) * Math.sin(d) + Math.cos(d0) * Math.cos(d) * Math.cos(h);
    if(cc < .25) return null;
    return [Math.cos(d) * Math.sin(h) / cc / R, (Math.cos(d0) * Math.sin(d) - Math.sin(d0) * Math.cos(d) * Math.cos(h)) / cc / R];
  }
  function skyXY(ra, dec, px, py, k){ var g = SKY.data && gno(ra, dec, SKY.data.center[0], SKY.data.center[1]); return g ? [px - g[0] * k, py - g[1] * k] : null; }
  function skyLayer(px, py, k, paper){
    var key = [W, H, DPR, Math.round(px), Math.round(py), k.toFixed(2), paper ? 1 : 0].join();
    if(SKY.key === key && SKY.cv) return SKY.cv;
    var cv2 = SKY.cv || document.createElement('canvas'); cv2.width = Math.round(W * DPR); cv2.height = Math.round(H * DPR);
    var g = cv2.getContext('2d'); g.setTransform(DPR, 0, 0, DPR, 0, 0); g.clearRect(0, 0, W, H);
    var c0 = SKY.data.center;
    /* หมอกสะท้อนแสงสีฟ้ารอบดาวลูกไก่ (ภาพถ่ายจริงเห็นชัด) */
    var neb = g.createRadialGradient(px + .2 * k, py + .25 * k, 0, px + .2 * k, py + .25 * k, 1.5 * k);
    neb.addColorStop(0, paper ? 'rgba(90,120,210,.14)' : 'rgba(120,160,255,.26)'); neb.addColorStop(1, 'rgba(120,160,255,0)');
    g.fillStyle = neb; g.beginPath(); g.arc(px + .2 * k, py + .25 * k, 1.5 * k, 0, TAU); g.fill();
    SKY.data.stars.forEach(function(st){
      var q = skyXY(st[0], st[1], px, py, k); if(!q || q[0] < -10 || q[0] > W + 10 || q[1] < -10 || q[1] > H + 10) return;
      var inM45 = Math.abs(st[0] - c0[0]) < 1.6 && Math.abs(st[1] - c0[1]) < 1.3;
      if(paper && !inM45) return;                         /* พื้นสว่าง: เหลือแค่ดาวลูกไก่ */
      var mag = st[2] - (inM45 ? .6 : 0), f = Math.pow(10, -.4 * (mag - 1));          /* ดาวลูกไก่เด่นขึ้นนิดให้มองเห็นเป็นกลุ่ม */
      var r = Math.max(.6, 1.8 * Math.pow(f, .23)), a = Math.min(1, .38 + 1.0 * Math.pow(f, .3)), c = bvRGB(st[3]);
      if(paper){ g.fillStyle = 'rgba(40,60,140,' + Math.min(1, a + .2) + ')'; g.beginPath(); g.arc(q[0], q[1], r * .9, 0, TAU); g.fill(); return; }
      var cs = 'rgba(' + (c[0] | 0) + ',' + (c[1] | 0) + ',' + (c[2] | 0) + ',';
      if(mag < 3.8){                                       /* แสงฟุ้งรอบดาวสว่าง */
        var hr = r * (5 + 3 * Math.min(1, f)), hg = g.createRadialGradient(q[0], q[1], 0, q[0], q[1], hr);
        hg.addColorStop(0, cs + (.42 * Math.min(1, Math.pow(f, .35))) + ')'); hg.addColorStop(1, cs + '0)');
        g.fillStyle = hg; g.beginPath(); g.arc(q[0], q[1], hr, 0, TAU); g.fill();
      }
      g.fillStyle = cs + a + ')'; g.beginPath(); g.arc(q[0], q[1], r, 0, TAU); g.fill();
      if(mag < 2.6){ g.fillStyle = 'rgba(255,255,255,.9)'; g.beginPath(); g.arc(q[0], q[1], r * .5, 0, TAU); g.fill(); }
    });
    SKY.key = key; SKY.cv = cv2; return cv2;
  }
  /* ชื่อไทย: ดาวลูกไก่ (M45) · ดาวโรหิณี (Aldebaran) · ดาวไถ (เข็มขัดนายพราน — Alnilam อยู่กลาง) */
  var SKY_LABELS = [['ดาวลูกไก่', 56.75, 24.12, 1.35], ['ดาวโรหิณี', 68.98, 16.51, .9], ['ดาวไถ', 84.05, -1.2, .9]];
  function drawSky(px, py, k, A, B, top, bottom){
    if(A < .01) return;
    loadSky(); if(!SKY.data) return;
    var L = skyLayer(px, py, k, THEME.dark), ox = PAR.x * 10, oy = PAR.y * 6;
    SKY.hit = A > .5 ? { x: px + ox, y: py + oy, k: k } : null;          /* แตะตรงนี้ = บินเข้าไปดูดาวลูกไก่ใกล้ๆ */
    ctx.save(); ctx.globalAlpha = .4 + .6 * A; ctx.drawImage(L, ox, oy, W, H);
    /* ดาวอยู่ไกลกว่า: โลก ดวงอาทิตย์ ดาวเคราะห์บังดาว (ลบดาวในวงของวัตถุพวกนั้นออก) */
    ctx.globalCompositeOperation = 'destination-out'; ctx.globalAlpha = 1; ctx.fillStyle = '#000';
    [[B.cx, B.cy, B.r * 1.02], [B.sun[0], B.sun[1], B.sun[2] * 1.4], [B.sat[0], B.sat[1], B.sat[2] * 2.4], [B.jup[0], B.jup[1], B.jup[2] * 1.15], [B.ura[0], B.ura[1], B.ura[2] * 1.2]]
      .forEach(function(o){ ctx.beginPath(); ctx.arc(o[0], o[1], o[2], 0, TAU); ctx.fill(); });
    ctx.globalCompositeOperation = 'source-over';
    ctx.font = '500 11px "Noto Sans Thai Looped", system-ui, sans-serif'; ctx.textAlign = 'center'; ctx.textBaseline = 'top';
    ctx.fillStyle = THEME.dark ? '#3d3558' : 'rgba(200,214,255,.9)'; ctx.shadowColor = THEME.dark ? 'rgba(255,255,255,.7)' : 'rgba(0,0,0,.6)'; ctx.shadowBlur = 4;
    SKY_LABELS.forEach(function(l){
      var q = skyXY(l[1], l[2], px, py, k); if(!q) return;
      var x = q[0] + ox, y = q[1] + oy + l[3] * k;
      if(x < 24 || x > W - 24 || y < top + 6 || y > bottom - 24 || Math.hypot(x - B.cx, y - B.cy) < B.r * 1.1) return;
      if(THEME.dark && l[0] !== 'ดาวลูกไก่') return;
      if(!CINEMA.on){ ctx.globalAlpha = A * .8; ctx.fillText(_t(l[0]), x, y); }
    });
    ctx.restore(); ctx.globalAlpha = 1;
  }
  var DAWN = { show: 1, think: 0, last: 0, spinOff: 0, drag: null };
  /* โหมดภาพยนตร์ (อัดคลิป): ซ่อน UI ทั้งหมด เหลือโลกเต็มจอ · กล้องดันเข้าช้าๆ · ดวงอาทิตย์ค่อยๆ ขึ้นจากขอบโลก */
  var CINEMA = { on: false, t0: 0 };
  /* ธรรมจักร: วงล้อ 8 ซี่จางๆ รอบโลก หมุนรอบละ 6 นาที · หายใจตามจังหวะสวด (6.4 วินาที) · ตอนคิดหมุนเร็วขึ้นเล็กน้อย
     ไม่ทับตัวโลก (ซี่เริ่มนอกขอบ) · ลดการเคลื่อนไหว = นิ่ง */
  var WHEEL = { a: 0, cv: null, key: '' };
  /* วาดวงล้อลงภาพเก็บไว้ครั้งเดียว (ขนาด/ธีมเปลี่ยนค่อยวาดใหม่) — ทุกเฟรมแค่หมุนภาพ ไม่สร้าง gradient ใหม่ = ไม่แลค */
  function wheelSprite(r){
    var R2 = r * 1.4, sz = Math.ceil((R2 + 6) * 2 * DPR), k = Math.round(r) + '|' + DPR + '|' + (THEME.dark ? 1 : 0);
    if(WHEEL.key === k) return WHEEL.cv;
    var cv = WHEEL.cv || document.createElement('canvas'); cv.width = cv.height = sz;
    var g = cv.getContext('2d'), col = THEME.dark ? '110,84,36' : '236,214,166', R0 = r * 1.15, R1 = r * 1.33;
    g.setTransform(DPR, 0, 0, DPR, sz / 2, sz / 2); g.clearRect(-sz, -sz, sz * 2, sz * 2);
    function ring(rr, al, lw){ g.strokeStyle = 'rgba(' + col + ',' + al + ')'; g.lineWidth = lw; g.beginPath(); g.arc(0, 0, rr, 0, TAU); g.stroke(); }
    ring(R1, .26, 1.1); ring(R2, .15, .7); ring(R0, .1, .6);
    for(var i = 0; i < 8; i++){
      var t = i * TAU / 8, c = Math.cos(t), sn = Math.sin(t), gr = g.createLinearGradient(c * r * 1.05, sn * r * 1.05, c * R2, sn * R2);
      gr.addColorStop(0, 'rgba(' + col + ',0)'); gr.addColorStop(1, 'rgba(' + col + ',.36)');
      g.strokeStyle = gr; g.lineWidth = 1.1; g.beginPath(); g.moveTo(c * r * 1.05, sn * r * 1.05); g.lineTo(c * R2, sn * R2); g.stroke();
      g.fillStyle = 'rgba(' + col + ',.42)'; g.beginPath(); g.arc(c * R2, sn * R2, 2.4, 0, TAU); g.fill();
    }
    WHEEL.cv = cv; WHEEL.key = k; return cv;
  }
  function drawWheel(cx, cy, r, tsec, dt, A){
    if(A < .01) return;
    if(!REDUCED) WHEEL.a += dt * (TAU / 360) * (1 + DAWN.think * 4);
    var br = REDUCED ? .85 : .7 + .3 * (.5 - .5 * Math.cos(tsec * TAU / 6.4)), cv = wheelSprite(r), h = cv.width / DPR / 2;
    ctx.save(); ctx.translate(cx, cy); ctx.rotate(WHEEL.a); ctx.globalAlpha = Math.min(1, A * br);
    if(!THEME.dark) ctx.globalCompositeOperation = 'lighter';
    ctx.drawImage(cv, -h, -h, h * 2, h * 2);
    ctx.restore(); ctx.globalAlpha = 1;
  }
  /* แสงอาทิตย์ขึ้นจากขอบโลก (โหมดภาพยนตร์): ประกาย "แหวนเพชร" ตอนดวงอาทิตย์พ้นขอบ + รัศมีแสงยาวผ่านฉาก
     ภาพแสงวาดเก็บไว้ครั้งเดียวแล้วย่อ/ขยายตามจริง — ทั้งฉากเพิ่มแค่ drawImage 2 ครั้งต่อเฟรม */
  var FLARE = null;
  function flareSprite(){
    if(FLARE) return FLARE;
    var cv = document.createElement('canvas'), n = 256, g = cv.getContext('2d'); cv.width = cv.height = n;
    var rg = g.createRadialGradient(n / 2, n / 2, 0, n / 2, n / 2, n / 2);
    rg.addColorStop(0, 'rgba(255,250,235,1)'); rg.addColorStop(.08, 'rgba(255,236,190,.85)'); rg.addColorStop(.3, 'rgba(236,200,130,.22)'); rg.addColorStop(1, 'rgba(216,184,120,0)');
    g.fillStyle = rg; g.fillRect(0, 0, n, n);
    g.translate(n / 2, n / 2);
    [[0, 1], [Math.PI / 2, .55], [Math.PI / 4, .3], [-Math.PI / 4, .3]].forEach(function(a){
      g.save(); g.rotate(a[0]); var lg = g.createLinearGradient(-n / 2, 0, n / 2, 0);
      lg.addColorStop(0, 'rgba(255,240,210,0)'); lg.addColorStop(.5, 'rgba(255,244,222,' + .9 * a[1] + ')'); lg.addColorStop(1, 'rgba(255,240,210,0)');
      g.fillStyle = lg; g.fillRect(-n / 2, -1.2, n, 2.4); g.restore();
    });
    return (FLARE = cv);
  }
  function drawSunrise(sun, r, sk, ct){
    if(sk <= 0) return;
    var f = flareSprite(), burst = Math.exp(-Math.pow((sk - .16) / .09, 2)), hold = .28 * ease((ct - 6) / 6);
    var a = Math.min(1, burst + hold), s = r * (1.1 + 2.4 * burst);
    if(a < .01) return;
    ctx.save(); ctx.globalCompositeOperation = 'lighter'; ctx.globalAlpha = a;
    ctx.drawImage(f, sun[0] - s / 2, sun[1] - s / 2, s, s);
    ctx.globalAlpha = a * .35; var L = r * 5;
    ctx.translate(sun[0], sun[1]); ctx.rotate(-.06); ctx.drawImage(f, -L / 2, -r * .12, L, r * .24);   /* แสงยาวพาดฟ้าแบบเลนส์ภาพยนตร์ */
    ctx.restore(); ctx.globalAlpha = 1;
  }
  function ease(x){ x = clamp(x, 0, 1); return x * x * (3 - 2 * x); }
  /* กล้องลอยช้าๆ แบบสเตดิแคม (เวลานับเฉพาะตอนวาด — กลับมาวาดใหม่ดาวไม่กระโดด) · เมาส์บนจอคอมขยับมุมกล้องนิดหน่อย */
  var PAR = { t: 0, x: 0, y: 0, tx: 0, ty: 0 };
  addEventListener('pointermove', function(e){ if(e.pointerType === 'mouse'){ PAR.tx = e.clientX / innerWidth - .5; PAR.ty = e.clientY / innerHeight - .5; } }, { passive:true });
  /* ปัดหน้าจอเพื่อหมุนโลกเอง (หน้าแรกเท่านั้น) */
  (function(){
    var el = document.getElementById('chat-scroll'); if(!el) return;
    el.addEventListener('pointerdown', function(e){ if(DAWN.show > .5) DAWN.drag = e.clientX; DAWN.down = [e.clientX, e.clientY]; });
    /* แตะดาวลูกไก่ (ไม่ใช่ปัดหมุนโลก) → โหลด static/pleiades_view.js ครั้งแรกแล้วบินเข้าไป */
    el.addEventListener('click', function(e){
      var h = SKY.hit, d = DAWN.down; if(!h || !SKY.data) return;
      if(d && Math.hypot(e.clientX - d[0], e.clientY - d[1]) > 8) return;
      if(Math.hypot(e.clientX - h.x, e.clientY - h.y) > Math.max(30, h.k * 1.8)) return;
      openPleiades(h);
    });
    addEventListener('pointerup', function(){ DAWN.drag = null; });
    el.addEventListener('pointermove', function(e){ if(DAWN.drag == null) return; DAWN.spinOff -= (e.clientX - DAWN.drag) * .008; DAWN.drag = e.clientX; kick(); });
  })();
  function backdrop(now, dt){
    var tsec = (now - t0) / 1000, m = $('#main').getBoundingClientRect(), ct = CINEMA.on ? (now - CINEMA.t0) / 1000 : 0;
    if(CINEMA.on) m = { left: 0, top: -40, width: W, height: H + 40, bottom: H };
    /* หน้าว่างและยังไม่พิมพ์ = เห็นโลกเต็ม · เริ่มพิมพ์หรือมีแชท = โลกค่อยๆ จาง เหลือพื้นหลังมืดเรียบ */
    var inp = $('#input'), emptyOn = view === 'chat' && !$('#empty').classList.contains('hide');
    var want = CINEMA.on || (emptyOn && !(inp && inp.value.trim())) ? 1 : 0;
    /* จางตามเวลาจริง (ไม่ใช่จำนวนเฟรม) — เครื่องช้าก็หายหมดในเวลาเท่ากัน */
    var rdt = DAWN.last ? Math.min(.5, (now - DAWN.last) / 1000) : 0; DAWN.last = now;
    DAWN.show += (want - DAWN.show) * Math.min(1, rdt * 3.2);
    if(Math.abs(want - DAWN.show) < .002) DAWN.show = want;
    DAWN.think += ((think ? 1 : 0) - DAWN.think) * Math.min(1, dt * 1.8);
    var cp = $('#composer'), bottom = !CINEMA.on && cp && cp.getBoundingClientRect().height ? cp.getBoundingClientRect().top : m.bottom;
    /* จัดวางแบบภาพอ้างอิง: โลกดวงใหญ่กลางพื้นที่ · ดวงอาทิตย์ซ้ายบน · เสาร์ พฤหัส ยูเรนัส ขวา · เนบิวลาซ้ายล่าง */
    var top = m.top + 54, avW = m.width, avH = bottom - top, portrait = avW < avH * .9;
    /* จอตั้ง (มือถือ): โลกกว้างราว 60% ของจอ — เดิม 86% ดูใหญ่คับจอและดาวเบียดขอบ · จอคอมคงเดิม */
    var r = Math.max(70, portrait ? Math.min(avW * .3, avH * .22) : Math.min(avW * .36, avH * .42));
    var cx = m.left + avW * (portrait ? .5 : .52), cy = top + avH * (portrait ? .5 : .52);
    /* โหมดภาพยนตร์: กล้องค่อยๆ ดันเข้าหาโลก 40 วินาที (ไม่เด้ง) */
    if(CINEMA.on){ r = Math.max(70, Math.min(W * (portrait ? .36 : .3), H * .34)); cx = W / 2; cy = H * (portrait ? .42 : .44); if(!REDUCED) r *= 1 + .1 * ease(ct / 40); }
    /* ใช้การจัดวางเดียวกันทุกจอ (แบบจอคอมที่ผู้ก่อตั้งชอบ) · กันไม่ให้ตกขอบจอ */
    var sunR = Math.max(12, r * .16), sunX = Math.max(m.left + sunR * 1.7, cx - r), sunY = Math.max(top + sunR * 1.6, cy - r * 1.02);
    /* โหมดภาพยนตร์: ดวงอาทิตย์เริ่มที่ขอบโลก (โลกบังไว้ครึ่งดวง) แล้วค่อยๆ ขึ้นไปที่เดิมใน 16 วินาที */
    var sk = 0;
    if(CINEMA.on){ sk = REDUCED ? 1 : ease((ct - 1.5) / 16); var sa = Math.atan2(sunY - cy, sunX - cx);
      sunX = cx + Math.cos(sa) * r * .9 + (sunX - cx - Math.cos(sa) * r * .9) * sk; sunY = cy + Math.sin(sa) * r * .9 + (sunY - cy - Math.sin(sa) * r * .9) * sk; }
    /* Orbiting Observer: ดาวเคราะห์ไม่ได้โคจรรอบโลก — ทุกดวง (รวมโลกที่เราโดยสาร) โคจรรอบดวงอาทิตย์
       จากบนโลกเราจึงเห็นมันเลื่อนช้าๆ ไปตามเส้นสุริยวิถีที่ลากผ่านดวงอาทิตย์ ห่างออกแล้วเข้าใกล้สลับกัน
       ดวงไกลเลื่อนช้ากว่า (พฤหัส → เสาร์ → ยูเรนัส) · ผ่านหลังขอบโลกเมื่อไร โลกบังจริง */
    /* เส้นสุริยวิถีเชิดขึ้นทางขวาพ้นขอบบนของโลก แต่ไม่หลุดขอบจอด้านบน (จอกว้างมากก็ไม่ยืดยาวเกิน) */
    var eL = Math.min(r * 2.5, Math.max(r * 1.6, m.left + avW - 24 - sunX)), eT = clamp(-(sunY - top - 60) / eL, -.15, .08);
    function orb(k, a0, per, rad){ var a = a0 - (REDUCED ? 0 : tsec * TAU / per), e = Math.min(1, k + .14 * Math.sin(a)) * eL;
      return [sunX + e * Math.cos(eT), sunY + e * Math.sin(eT) + rad * 1.6 * Math.cos(a), rad]; }
    var BOD = {
      sun: [sunX, sunY, sunR],
      /* เริ่มห่างกัน: พฤหัสใกล้ดวงอาทิตย์ · เสาร์กลางทาง · ยูเรนัสปลายเส้น แล้วค่อยๆ เลื่อนเข้าออก */
      sat: orb(.74, 0, 150, Math.max(6, r * .085)),
      jup: orb(.52, -1.57, 95, Math.max(7, r * .1)),
      ura: orb(.88, 1.57, 210, Math.max(4.5, r * .05)),
      neb: [m.left + avW * (portrait ? .12 : .1), bottom - avH * (portrait ? .08 : .1)],
      cx: cx, cy: cy
    };
    var drew = false;
    ctx.setTransform(DPR, 0, 0, DPR, 0, 0); ctx.globalAlpha = 1;
    if(GLX && GLX.ok()){
      ctx.clearRect(0, 0, W, H); GLX.pace(dt);
      if(!REDUCED){ var pk = Math.min(1, dt * 1.6); PAR.t += dt; PAR.x += (PAR.tx - PAR.x) * pk; PAR.y += (PAR.ty - PAR.y) * pk; }
      var par = [PAR.x * 34 + Math.sin(PAR.t * .045) * 12, PAR.y * 22 + Math.cos(PAR.t * .033) * 8];
      drew = GLX.dawn({ par: par, spin: DAWN.spinOff, cx:cx, cy:cy, r:r, sun: BOD.sun, sat: BOD.sat, jup: BOD.jup, ura: BOD.ura, neb: BOD.neb, show: DAWN.show, think: DAWN.think, risk: coreWL != null && coreWL < 35 ? 1 : 0, dim: 1 }, tsec);
    }
    if(!drew) ctx.drawImage(bgCv, 0, 0, W, H);
    /* ท้องฟ้าจริง: ดาวลูกไก่อยู่ฟ้าด้านบนซ้าย เหนือดวงอาทิตย์ · ราว 15 พิกเซลต่อองศาบนมือถือ (กระจุกกว้าง ~20 px แบบ Stellarium) */
    if(drew) drawSky(m.left + avW * (portrait ? .47 : .32), top + Math.max(46, (sunY - sunR * 2.4 - top) * .5),
                     clamp(avW / 30, 11, 22), DAWN.show, { cx: cx, cy: cy, r: r, sun: BOD.sun, sat: BOD.sat, jup: BOD.jup, ura: BOD.ura }, top, bottom);
    /* โหมดภาพยนตร์: ไม่มีเส้นวงโคจร/ป้าย (คลีน) · ธรรมจักรสว่างขึ้นตามแสงอาทิตย์ที่ขึ้น · ประกายแสงตอนพ้นขอบโลก */
    if(CINEMA.on && !REDUCED) drawSunrise(BOD.sun, r, sk, ct);
    drawWheel(cx, cy, r, tsec, dt, DAWN.show * (CINEMA.on ? .45 + .75 * sk : 1));
    drawRoutes(cx, cy, r, tsec, CINEMA.on ? 0 : DAWN.show, top, bottom);
    if(drew && !CINEMA.on) drawBodyLabels(BOD, r, DAWN.show, top);
    /* ดาวลูกไก่ลอยอยู่ฟ้าด้านบนระหว่างดวงอาทิตย์กับขอบจอ — เลื่อนตามกล้องนิดหน่อยให้รู้ว่าอยู่ไกลกว่าดาวเคราะห์ */

    /* ── ดาวหางผ่านมาเป็นระยะๆ ────────────────────────────────────────────
       ดาวหางไม่โคจรรอบโลก แต่เป็นวัตถุไกลๆ ที่พุ่งผ่านฉากหลังระบบสุริยะ
       ปรากฏทุก ~8-15 วินาที · หางแสงเรืองชี้ออกจากดวงอาทิตย์ · ความเร็วและทิศสุ่ม
       วาดบนชั้น 2D ทับกับฉาก WebGL · ใช้ 'lighter' composite ให้แสงรวมกับพื้นหลัง */
    drawComet(tsec, DAWN.show);
    /* ตอนเป็นพื้นหลังเรียบ (show = 0) ภาพนิ่ง ไม่ต้องวาดซ้ำ — ประหยัดแบต · พิมพ์/เปลี่ยนหน้าจะปลุกเอง */
    if(!REDUCED && (DAWN.show > 0 || want > 0)) kick();
  }
  /* ── ดาวหาง: วัตถุเดินทางไกลที่ผ่านมาเป็นระยะ ─────────────────────────────
     เกิดสุ่มทุก 8-15 วินาที · หางชี้หนีดวงอาทิตย์จริง (แสงอาทิตย์มาจากทิศ sun)
     หัวสว่าง + หางจางค่อยๆ ยาว · ใช้ parallax เล็กน้อยให้ดูมีความลึก */
  var COMET = { active: false, t0: 0, x0: 0, y0: 0, x1: 0, y1: 0, next: 0 };
  function drawComet(tsec, show){
    if(REDUCED || show <= 0){ COMET.active = false; return; }
    var now = tsec;
    /* สุ่มดาวหางใหม่ถ้าถึงเวลา */
    if(!COMET.active && now >= COMET.next){
      COMET.active = true; COMET.t0 = now;
      /* จุดเริ่ม: ขอบจอฝั่งสุ่ม */
      var side = Math.floor(Math.random() * 4);
      var m = { l: 0, t: 0, r: W, b: H };
      if(side === 0){ COMET.x0 = Math.random() * W; COMET.y0 = -20; }
      else if(side === 1){ COMET.x0 = W + 20; COMET.y0 = Math.random() * H; }
      else if(side === 2){ COMET.x0 = Math.random() * W; COMET.y0 = H + 20; }
      else { COMET.x0 = -20; COMET.y0 = Math.random() * H; }
      /* จุดหมาย: ไปทางตรงข้ามผ่ากลางจอ (เพิ่มความเร็วสุ่มเล็กน้อย) */
      var cx0 = W * .5, cy0 = H * .5;
      var dx = cx0 - COMET.x0, dy = cy0 - COMET.y0;
      var len = Math.sqrt(dx * dx + dy * dy) || 1;
      var speed = .12 + Math.random() * .08; /* เศษส่วนของระยะต่อวินาที */
      var dur = 2.5 + Math.random() * 3; /* อยู่บนจอ 2.5-5.5 วินาที */
      COMET.x1 = COMET.x0 + dx / len * len * speed * dur;
      COMET.y1 = COMET.y0 + dy / len * len * speed * dur;
      COMET.dur = dur;
    }
    if(!COMET.active) return;
    var k = (now - COMET.t0) / COMET.dur;
    if(k >= 1){
      COMET.active = false;
      COMET.next = now + 8 + Math.random() * 7; /* รอ 8-15 วินาที */
      return;
    }
    /* easing: ช้าต้น เร็วกลาง ช้าปลาย */
    var e = k < .5 ? 2 * k * k : 1 - Math.pow(-2 * k + 2, 2) / 2;
    var x = COMET.x0 + (COMET.x1 - COMET.x0) * e;
    var y = COMET.y0 + (COMET.y1 - COMET.y0) * e;
    /* ทิศหาง: ชี้ออกจากดวงอาทิตย์ (แสงจาก BOD.sun) */
    var sunX2 = 0, sunY2 = 0;
    try { sunX2 = BOD.sun[0]; sunY2 = BOD.sun[1]; } catch(_){}
    var tdx = x - sunX2, tdy = y - sunY2;
    var tl = Math.sqrt(tdx * tdx + tdy * tdy) || 1;
    tdx /= tl; tdy /= tl;
    var tailLen = 60 + 80 * Math.sin(Math.PI * k); /* หางยาวสุดตอนกลางทาง */
    var tx2 = x + tdx * tailLen, ty2 = y + tdy * tailLen;
    var fade = Math.sin(Math.PI * k); /* จางตอนเข้า-ออกจอ */
    /* วาดหาง: gradient จากหัว (สว่าง) ไปท้าย (จาง) */
    var grd = ctx.createLinearGradient(x, y, tx2, ty2);
    grd.addColorStop(0, 'rgba(180,220,255,' + (.55 * fade) + ')');
    grd.addColorStop(.25, 'rgba(140,180,255,' + (.28 * fade) + ')');
    grd.addColorStop(.6, 'rgba(100,150,255,' + (.10 * fade) + ')');
    grd.addColorStop(1, 'rgba(80,120,255,0)');
    ctx.save();
    ctx.globalCompositeOperation = 'lighter';
    /* หางหลัก */
    ctx.strokeStyle = grd;
    ctx.lineWidth = 2.5;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(tx2, ty2);
    ctx.stroke();
    /* หางรอง (กว้างขึ้น จางลง) */
    ctx.lineWidth = 6;
    ctx.globalAlpha = .35;
    ctx.beginPath();
    ctx.moveTo(x, y);
    ctx.lineTo(tx2, ty2);
    ctx.stroke();
    ctx.globalAlpha = 1;
    /* หัวดาวหาง: จุดสว่างเรือง */
    ctx.fillStyle = 'rgba(220,240,255,' + (.9 * fade) + ')';
    ctx.beginPath();
    ctx.arc(x, y, 1.8, 0, Math.PI * 2);
    ctx.fill();
    /* glow รอบหัว */
    var hg = ctx.createRadialGradient(x, y, 0, x, y, 10);
    hg.addColorStop(0, 'rgba(180,210,255,' + (.5 * fade) + ')');
    hg.addColorStop(1, 'rgba(180,210,255,0)');
    ctx.fillStyle = hg;
    ctx.beginPath();
    ctx.arc(x, y, 10, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();
  }
  var INP = document.getElementById('input'); if(INP) INP.addEventListener('input', function(){ kick(); });
  /* หมุนกล้อง = หันมองรอบตัว (ฟ้าไม่ได้หมุนรอบเรา) · ปล่อยแล้วไหลต่อตามแรงเฉื่อย
     ปล่อยไว้สักพักค่อยหันกลับมาที่กลุ่มดาวของเรา */
  function stepCam(dt){
    if(REDUCED || cam.drag) return;
    cam.yaw += cam.vy * dt; cam.pitch = clamp(cam.pitch + cam.vp * dt, -1.3, 1.3);
    var f = Math.pow(.05, dt); cam.vy *= f; cam.vp *= f;
    if(performance.now() - cam.idle > 3500){
      var yw = Math.atan2(Math.sin(cam.yaw), Math.cos(cam.yaw)), k = 1 - Math.pow(.4, dt);
      cam.yaw = yw * (1 - k); cam.pitch *= 1 - k;
    }
  }
  /* ── โต้ตอบ ──────────────────────────────────────────────── */
  function pick(x, y){
    var best = null, bd = 1e9, list = mode === 'decisions' ? stars : P;
    list.forEach(function(n){
      var dx = n.sx - x, dy = n.sy - y, d = dx * dx + dy * dy, lim = Math.max(12, (n.px || n.r || 4) + 8);
      if(d < lim * lim && d < bd){ bd = d; best = n; }
    });
    return best;
  }
  function names(list, key){
    var xs = list.map(function(e){ return e[key].f[0]; });
    return xs.length ? xs.slice(0, 6).map(esc).join('<br>') + (xs.length > 6 ? '<br>' + _t('… อีก {n}', {n: xs.length - 6}) : '') : '<span class="muted">—</span>';
  }
  function card(n){
    var c = $('#u-card');
    if(!n){ c.classList.add('hide'); c.innerHTML = ''; return; }
    var h = '<button type="button" class="icon-btn x" aria-label="ปิด">✕</button>';
    if(n.kind === 'd'){
      var t = n.m.tr || {}, when = n.ts ? new Date(n.ts).toLocaleString('th-TH', {dateStyle:'medium', timeStyle:'short'}) : '';
      h += '<h3>' + esc(ROUTE_NAME[ORB[n.orb]] || ORB[n.orb]) + ' · <span style="color:' + n.col + '">' + _t('ความเสี่ยง {n}', {n: t.risk != null ? Math.round(t.risk) : '—'}) + '</span></h3>' +
        '<div class="meta">' + esc(when) + (t.wl != null ? ' · WL ' + Math.round(t.wl) : '') + ' · ' + esc(n.m.p || '') + '</div>' +
        (n.q ? '<p class="q">' + esc(n.q.slice(0, 280)) + '</p>' : '') +
        '<p class="a">' + fmt(n.m.t.slice(0, 420) + (n.m.t.length > 420 ? '…' : '')) + '</p>' + (t.mode === 'crisis' || /1323|1669/.test(n.m.t) ? crisisCard() : '') +
        '<details><summary>Σ</summary>' + eqHTML(t) + '</details>' +
        '<div style="margin-top:12px"><button type="button" class="btn sm primary" id="u-open">เปิดแชทนี้</button></div>';
    } else {
      var f = n.f;
      h += '<h3 class="mono" style="font-size:14px">' + esc(f[0]) + '</h3><div class="meta"><span style="color:' + COL[n.cat] + '">■ ' + esc(CAT_NAME[n.cat] || n.cat) + '</span> · ' + _t('{n} บรรทัด', {n: (f[1] || 0).toLocaleString('en-US')}) + '</div>' +
        (f[4] ? '<div class="sym">' + esc(f[4]) + '</div>' : '') +
        (f[3] ? '<p class="a" data-i18n-skip>' + esc(f[3]) + '</p>' : '<p class="a">ไม่มีคำอธิบายในไฟล์</p>') +
        (f[6] ? '<div class="tr-row" style="padding:6px 0"><div class="k">รอยรั่ว</div><div class="v" style="font-size:12.5px" data-i18n-skip>' + esc(f[6]) + '</div></div>' : '') +
        (f[7] ? '<div class="tr-row" style="padding:6px 0"><div class="k">' + (f[5] === 'note' ? 'ข้อเสนอ' : 'ซ่อม') + '</div><div class="v" style="font-size:12.5px;color:var(--ok)" data-i18n-skip>' + esc(f[7]) + '</div></div>' : '') +
        '<div class="tr-row" style="padding:6px 0"><div class="k">ต่อไปหา</div><div class="v mono" style="font-size:12px">' + names(n.out, 'b') + '</div></div>' +
        '<div class="tr-row" style="padding:6px 0"><div class="k">ถูกต่อจาก</div><div class="v mono" style="font-size:12px">' + names(n.inn, 'a') + '</div></div>';
    }
    c.innerHTML = h; c.classList.remove('hide');
    c.querySelector('.x').addEventListener('click', function(){ sel = null; card(null); kick(); });
    var o = $('#u-open'); if(o) o.addEventListener('click', function(){ Chat.select(n.sid); });
  }
  function legend(){
    var L = $('#u-legend');
    if(mode === 'decisions'){
      $('#u-count').textContent = _t('{n} ดวง · คุย 1 ครั้งได้ดาว 1 ดวง · แตะดาวเพื่อดูเรื่องที่คุย', {n: stars.length});
      L.innerHTML = '<div class="row"><span><i class="sw" style="background:#6fb2ff"></i>ความเสี่ยงต่ำ &lt;45</span><span><i class="sw" style="background:#f6b24a"></i>กลาง 45–74</span><span><i class="sw ring" style="background:' + RISK_HI + ';color:' + RISK_HI + '"></i>สูง ≥75</span></div>' +
        '';
      $('#u-empty').classList.toggle('hide', stars.length > 0);
    } else {
      var counts = {}; P.forEach(function(p){ counts[p.cat] = (counts[p.cat] || 0) + 1; });
      var pct = PY.length ? Math.round(PY_LIVE.length / PY.length * 100) : 0;
      $('#u-count').textContent = _t('ต่อติดแล้ว {a} / {b} ชิ้น Python ({p}%) · {f} ไฟล์ · commit {c}', {a: PY_LIVE.length, b: PY.length, p: pct, f: P.length, c: MAP.commit || '—'});
      L.innerHTML = '<div class="row">' + CATS.filter(function(c){ return counts[c[0]]; }).map(function(c){ return '<span><i class="sw" style="background:' + COL[c[0]] + ';border-radius:1px"></i>' + esc(c[1]) + ' ' + counts[c[0]] + '</span>'; }).join('') + '</div>' +
        '';
      $('#u-empty').classList.add('hide');
    }
  }
  var U = $('#view-universe'), UI_SEL = '.u-top,#u-card,.u-legend,.u-empty';
  /* กลุ่มดาวของฉันเป็นฟ้านิ่ง — ไม่มีการลากหมุนฟ้าแล้ว (เดิมลากแล้วฟ้าหมุนตามนิ้ว ทำให้เวียนหัว) แตะดาวเพื่อดูเรื่องที่คุยได้เหมือนเดิม */
  function endDrag(){
    if(!cam.drag) return; var d = cam.drag; cam.drag = null; cam.idle = performance.now(); U.classList.remove('dragging');
    if(d.moved){ U._noClick = performance.now(); var sl = getSelection && getSelection(); if(sl) sl.removeAllRanges(); }
  }
  addEventListener('pointerup', endDrag); addEventListener('pointercancel', endDrag);
  U.addEventListener('pointermove', function(e){
    var d = cam.drag;
    if(d){
      var mx = e.clientX - d.lx, my = e.clientY - d.ly, t = performance.now(), dts = Math.max(.008, (t - d.t) / 1000);
      if(!d.moved && Math.hypot(e.clientX - d.x, e.clientY - d.y) > 6){ d.moved = true; U.classList.add('dragging'); }
      if(d.moved){
        /* ลากฟ้าตามนิ้ว 1:1 (1 พิกเซล = 1/f เรเดียน) */
        var fz = SG ? SG.f : 600;
        cam.yaw -= mx / fz; cam.pitch = clamp(cam.pitch + my / fz, -1.3, 1.3);
        cam.vy = clamp(-mx / fz / dts, -3, 3); cam.vp = clamp(my / fz / dts, -3, 3); cam.idle = t;
        kick(); d.lx = e.clientX; d.ly = e.clientY; d.t = t; return;
      }
    }
    var n = e.target.closest(UI_SEL) ? null : pick(e.clientX, e.clientY);
    if(n !== hover){ hover = n; U.classList.toggle('hovering', !!n); kick(); }
  });
  U.addEventListener('click', function(e){ if(e.target.closest(UI_SEL) || performance.now() - (U._noClick || 0) < 250) return; sel = pick(e.clientX, e.clientY); card(sel); if(sel && sel.kind === 'd') ripple(sel, performance.now()); kick(); });
  /* คำของผู้ก่อตั้ง ปรากฏครั้งเดียวต่อแท็บตอนเข้าจักรวาล แล้วจางหาย เหลือแต่ท้องฟ้า */
  function epigraph(){
    var el = $('#u-epi'); if(!el || REDUCED) return;
    try{ if(sessionStorage.getItem('kd_epi')) return; sessionStorage.setItem('kd_epi', '1'); }catch(_){ return; }
    el.classList.remove('on'); void el.offsetWidth; el.classList.add('on');
  }
  function setMode(m){ mode = m; sel = null; hover = null; card(null); $$('#u-mode button').forEach(function(x){ x.classList.toggle('on', x.dataset.m === m); }); legend(); kick(); }
  $$('#u-mode button').forEach(function(b){ b.addEventListener('click', function(){ setMode(b.dataset.m); }); });
  addEventListener('resize', function(){ clearTimeout(resize._t); resize._t = setTimeout(resize, 120); });
  document.addEventListener('visibilitychange', kick);
  $('#chat-scroll').addEventListener('scroll', function(){ if(REDUCED) kick(); }, {passive:true});
  return {
    init: function(){ resize(); this.syncCore(); },
    rebuild: rebuild,
    setView: function(v){
      if(v === 'universe' && view !== 'universe'){
        if(!REDUCED) warpAt = performance.now();
        /* ตำแหน่งดาวจากการเข้าครั้งก่อนใช้ไม่ได้แล้ว — ไม่ล้าง เส้นแสงตอนเคลื่อนกล้องเข้าจะลากยาวข้ามจอในเฟรมแรก */
        SKYF.forEach(function(st){ st.lx = null; }); layoutStars(); epigraph();
      }
      view = v; if(v !== 'universe'){ sel = null; hover = null; card(null); } else legend(); kick();
    },
    setMode: setMode,
    syncCore: function(){ var s = MyState.get(); coreWL = s ? MyState.waterline(s) : null; if(view === 'universe') legend(); kick(); },
    thinking: function(on){ think = on; kick(); },
    birth: function(ts){ births.push({ ts:ts, at: performance.now() }); if(view !== 'universe') flyStar(); kick(); },
    focusRoute: function(r){ focusR = r; focusT = performance.now(); kick(); },
    cinema: function(on){ CINEMA.on = !!on; CINEMA.t0 = performance.now(); kick(); },
    stats: function(){ return { live: PY_LIVE.length, py: PY.length }; }
  };
})();

/* โลโก้ในแถบข้าง: ชิ้นจิ๊กซอว์ 5 ชิ้นที่ต่อกัน วาดด้วยโค้ด */
(function(){
  var c = $('#brand-mark'); if(!c) return; var g = c.getContext('2d');
  var n = [[36,36,12,'#f6b24a'],[14,16,7,'#6fb2ff'],[58,56,7,'#6fb2ff'],[57,15,6,'#ffe2a8'],[15,57,6,'#ffe2a8']];
  g.strokeStyle = 'rgba(201,212,255,.5)'; g.lineWidth = 2;
  n.slice(1).forEach(function(p){ g.beginPath(); g.moveTo(36,36); g.lineTo(p[0],p[1]); g.stroke(); });
  n.forEach(function(p){ g.shadowColor = p[3]; g.shadowBlur = 10; g.fillStyle = p[3]; g.fillRect(p[0]-p[2]/2, p[1]-p[2]/2, p[2], p[2]); });
})();

/* route chips (หลัง Cosmos เพราะกดแล้ววงโคจรของเส้นทางนั้นจะสว่าง) */
(function(){
  var box = $('#routes');
  ROUTES.forEach(function(r){
    var b = document.createElement('button'); b.type = 'button'; b.className = 'chip'; b.dataset.r = r[0]; b.textContent = r[1];
    b.addEventListener('click', function(){ Route = r[0]; lsSet('kd_route', Route); syncChips(); Cosmos.focusRoute(Route); routeMenu(false); });
    box.appendChild(b);
  });
  /* มือถือ: แถวปุ่ม (.comp-row1) เลื่อนแนวนอนได้ (overflow-x:auto) จึงตัดเมนูที่ลอยเหนือแถวทิ้ง
     เดิมกด "ทั่วไป ▾" บนมือถือแล้วไม่เห็นอะไร (แลปท็อปแถวไม่เลื่อน จึงเห็นปกติ) → วางเมนูตามจอแทน */
  function routeMenu(on){
    var m = $('#route-menu'), pill = $('#route-pill');
    if(on){
      var r = pill.getBoundingClientRect();
      m.style.position = 'fixed'; m.style.left = Math.max(8, Math.min(r.left, innerWidth - 186)) + 'px';
      m.style.bottom = (innerHeight - r.top + 8) + 'px'; m.style.top = 'auto';
    }
    m.classList.toggle('hide', !on); pill.setAttribute('aria-expanded', on ? 'true' : 'false');
  }
  addEventListener('resize', function(){ routeMenu(false); });
  $('.comp-row1').addEventListener('scroll', function(){ routeMenu(false); }, {passive:true});
  $('#route-pill').addEventListener('click', function(e){ e.stopPropagation(); routeMenu($('#route-menu').classList.contains('hide')); });
  /* ปุ่มโหมดสีบนแถบบน: กลางคืน · กลางวัน · คอสมิกลาเต้ · สีที่เลือกเอง (เปลี่ยนสีแล้วเห็นทันที) */
  function themeMenu(on){ $('#theme-menu').classList.toggle('hide', !on); $('#theme-btn').setAttribute('aria-expanded', on ? 'true' : 'false'); }
  $('#theme-btn').addEventListener('click', function(e){ e.stopPropagation(); themeMenu($('#theme-menu').classList.contains('hide')); });
  $('#theme-menu').addEventListener('click', function(e){ e.stopPropagation(); });
  $$('#theme-menu button[data-theme-pick]').forEach(function(b){ b.addEventListener('click', function(){ applyTheme(b.getAttribute('data-theme-pick')); themeMenu(false); }); });
  $('#theme-color').addEventListener('input', function(){ applyTheme('custom', this.value); });
  /* ลดการเคลื่อนไหว: ฟ้าและดาวหยุดนิ่ง ปิดแอนิเมชันทั้งแอป และฉากบิ๊กแบงไม่เล่นเอง */
  function calmUI(){ var b = $('#calm-btn'); if(b){ b.setAttribute('aria-pressed', REDUCED ? 'true' : 'false'); b.classList.toggle('on', REDUCED); } }
  $('#calm-btn').addEventListener('click', function(){
    var sys = matchMedia('(prefers-reduced-motion: reduce)').matches, on = !REDUCED || sys;
    if(sys && REDUCED){ toast('มือถือตั้งลดการเคลื่อนไหวไว้แล้ว — ปิดได้ที่การตั้งค่าของเครื่อง'); return; }
    REDUCED = on; document.documentElement.classList.toggle('kd-calm', on); lsSet('kd-calm', on ? '1' : '0'); calmUI();
    if(window.KD_kick) KD_kick();
  });
  calmUI();
  /* ธีมฮาโลวีน: เปิด/ปิดเองจากเมนูสี และจำค่าไว้ · ช่วง 24 ต.ค.–1 พ.ย. ชวนลองวันละครั้ง (ไม่เปิดให้เอง) */
  var hw = false; try{ hw = localStorage.getItem('kd-halloween') === '1'; }catch(_){}
  function hwUI(){ document.documentElement.classList.toggle('kd-halloween', hw); var b = $('#halloween-btn'); b.setAttribute('aria-pressed', hw ? 'true' : 'false'); b.classList.toggle('on', hw); }
  $('#halloween-btn').addEventListener('click', function(){ hw = !hw; lsSet('kd-halloween', hw ? '1' : '0'); hwUI(); });
  hwUI();
  (function(){
    var d = new Date(), md = (d.getMonth() + 1) * 100 + d.getDate(), key = 'kd-hw-nudge-' + d.getFullYear() + md;
    if(hw || md < 1024 || md > 1101) return;
    try{ if(localStorage.getItem(key)) return; localStorage.setItem(key, '1'); }catch(_){ return; }
    setTimeout(function(){ toast('ช่วงฮาโลวีน 🎃 เปิดธีมค้างคาวน่ารักๆ ได้ที่ปุ่มวงกลมมุมขวาบน', false, 6000); }, 2500);
  })();
  document.addEventListener('click', function(){ themeMenu(false); });
  applyTheme(THEME.t, THEME.c);
  document.addEventListener('click', function(e){ if(!e.target.closest('.menu-wrap')) routeMenu(false); });
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') routeMenu(false); });
  $$('#persona-seg button').forEach(function(b){
    b.addEventListener('click', function(){ Persona = b.dataset.p; lsSet('kd_persona', Persona); syncChips(); });
  });
})();

/* ════════════════════════════════════════════════════════════════
   RENDER CHAT
   ════════════════════════════════════════════════════════════════ */
var PNAME = { LYLA:['LYLA','lyla'], VEGA:['VEGA','vega'], COUNCIL:['สภา 6 เสียง','council'], CRISIS:['HALT · ช่วยเหลือฉุกเฉิน','crisis'] };
function crisisCard(){
  return '<div class="crisis-card"><b>' + _t('ถ้ากำลังอยู่ในอันตราย หรือคิดทำร้ายตัวเอง') + '</b> ' + _t('โทรหาคนที่ช่วยได้ทันที') + '<br>' +
    '<a href="tel:1323">1323</a>' + _t('สายด่วนสุขภาพจิต 24 ชม.') + '<br><a href="tel:1669">1669</a>' + _t('เจ็บป่วยฉุกเฉิน') + ' <a href="tel:191">191</a>' + _t('ตำรวจ') + '</div>';
}
/* สภา 6 เสียง: ชื่อแต่ละเสียงเป็นตัวหนา อ่านง่ายบนมือถือ */
function councilFmt(t){
  return fmt(t).replace(/(^|<br>)(LYLA ◈|VEGA ◆|PATICCA ☸|TITAN ▲|COSMOS ✦|CIVIL ⬡|มติสภา[^:<]{0,24}:)/g, '$1<strong class="cm">$2</strong>');
}
function helpCard(links){
  // ลิงก์มาจากเซิร์ฟเวอร์ — รับเฉพาะ Google Maps แบบ https เท่านั้น
  var ok = (Array.isArray(links) ? links : []).filter(function(l){ return l && typeof l.url === 'string' && l.url.indexOf('https://www.google.com/maps/') === 0; }).slice(0, 3);
  if(!ok.length) return '';
  return '<div class="help-card"><b>' + _t('หาความช่วยเหลือใกล้คุณ') + '</b> ' + _t('แผนที่จะใช้ตำแหน่งในเครื่องของคุณเอง') + '<br>' +
    ok.map(function(l){ return '<a href="' + esc(l.url) + '" target="_blank" rel="noopener noreferrer">' + esc(l.label) + ' ↗</a>'; }).join('') + '</div>';
}
/* ช่วงตัดสินใจ — บอกเป็นวันชัดๆ ใต้คำตอบ (เดิมอยู่ลึกในหน้าต่างรายละเอียด Σ คนแทบไม่เห็น)
   มาจากประวัติระดับน้ำของผู้ใช้เอง (ล็อกอิน + บันทึกสถานะอย่างน้อย 2 วัน) — ไม่มีข้อมูลก็ไม่แสดง ไม่เดา */
function twCard(t){
  var tw = t && t.tw;
  if(!tw || !tw.status) return '';
  var n = tw.time_to_intervention_days, perDay = tw.waterline_per_day, cls, head, sub;
  if(n == null){
    cls = 'ok'; head = _t('🌿 ยังมีเวลา ไม่ต้องรีบตัดสินใจ');
    sub = _t('ระดับน้ำของคุณไม่ได้ลดลงในช่วงที่ผ่านมา ค่อยๆ คิดได้');
  } else if(n === 0){
    cls = 'bad'; head = _t('⏳ ควรเริ่มวันนี้');
    sub = _t('ทางเลือกเหลือน้อยมากแล้ว เริ่มจากเรื่องเล็กที่สุดที่ทำได้วันนี้ก่อน');
  } else {
    cls = n <= 7 ? 'bad' : n <= 30 ? 'warn' : 'ok';
    head = _t('⏳ เหลือเวลาตัดสินใจราว {n} วัน', {n: n});
    sub = _t('ก่อนทางเลือกจะเหลือทางเดียว') + (tw.time_to_failure_days != null ? ' · ' + _t('ถ้าไม่มีอะไรเปลี่ยน อีก {n} วันจะไม่เหลือทางเลือก', {n: tw.time_to_failure_days}) : '');
  }
  if(perDay != null && perDay < 0) sub += ' ' + _t('(ระดับน้ำลดวันละ {n})', {n: Math.abs(perDay)});
  return '<div class="tw-card ' + cls + '" role="note"><b>' + esc(head) + '</b><span>' + esc(sub) + '</span></div>';
}
/* ดาวลอยจากคำตอบไปที่ปุ่ม "จักรวาล" — คุย 1 ครั้งได้ดาว 1 ดวงในกลุ่มดาวของฉัน
   ลดการเคลื่อนไหว: ไม่ลอย แค่ตัวเลขบนปุ่มเด้งเบาๆ */
function flyStar(){
  var src = [].slice.call(document.querySelectorAll('#chat-scroll .m.a .who .star')).pop();
  var dst = [].slice.call(document.querySelectorAll('#tabbar [data-view="universe"], #sidebar [data-view="universe"]'))
    .filter(function(b){ var r = b.getBoundingClientRect(); return r.width > 0 && r.bottom > 0 && r.top < innerHeight && r.right > 0 && r.left < innerWidth; })[0];   /* เมนูข้างบนมือถือซ่อนอยู่นอกจอซ้าย — ไม่นับ */
  if(!dst) return;
  function pop(){ dst.classList.remove('star-pop'); void dst.offsetWidth; dst.classList.add('star-pop'); }
  if(REDUCED || !src){ pop(); return; }
  var a = src.getBoundingClientRect(), b = dst.getBoundingClientRect(), el = document.createElement('span');
  el.className = 'fly-star'; el.setAttribute('aria-hidden', 'true'); el.style.color = getComputedStyle(src).color;
  el.style.left = (a.left + a.width / 2 - 6) + 'px'; el.style.top = (a.top + a.height / 2 - 6) + 'px';
  document.body.appendChild(el);
  var dx = b.left + b.width / 2 - (a.left + a.width / 2), dy = b.top + b.height / 3 - (a.top + a.height / 2);
  /* โค้งขึ้นก่อนแล้วค่อยลงไปที่ปุ่ม เหมือนดาวถูกโยนขึ้นฟ้า */
  var an = el.animate([
    { transform: 'translate(0,0) scale(1)', opacity: 1 },
    { transform: 'translate(' + dx * .45 + 'px,' + (Math.min(dy, 0) - 90) + 'px) scale(1.6)', opacity: 1, offset: .45 },
    { transform: 'translate(' + dx + 'px,' + dy + 'px) scale(.6)', opacity: .2 }
  ], { duration: 1300, easing: 'cubic-bezier(.3,.7,.2,1)' });
  an.onfinish = function(){ el.remove(); pop(); };
}
function msgEl(m){
  var el = document.createElement('div'); el.className = 'm ' + m.r;
  if(m.r === 'u'){ el.innerHTML = '<div class="bubble"></div>'; el.firstChild.textContent = m.t; return el; }
  if(m.r === 'e'){ el.innerHTML = '<div class="who"><span class="crisis">ERROR</span></div><div class="bubble">' + fmt(m.t) + '</div>'; return el; }
  var t = m.tr || {}, key = (t.mode === 'crisis') ? 'CRISIS' : (PNAME[(m.p || 'LYLA').toUpperCase()] && (m.p || '').toUpperCase() !== 'CRISIS' ? (m.p || 'LYLA').toUpperCase() : 'LYLA');
  var pn = PNAME[key], tags = [];
  if(t.route) tags.push(String(t.route).toUpperCase());
  var crisis = t.mode === 'crisis' || /1323|1669/.test(m.t);
  var star = m.tr ? '<span class="star" style="color:' + riskColor(t.risk) + '" title="' + _t('ดาวของการตัดสินใจนี้') + '"></span>' : '';
  el.innerHTML = '<div class="who">' + star + '<span class="' + pn[1] + '">' + _t(pn[0]) + '</span><span class="tag">' + esc(tags.join(' · ')) + '</span></div>' +
    '<div class="bubble">' + telify(key === 'COUNCIL' ? councilFmt(m.t) : fmt(m.t)) + '</div>' + (crisis ? crisisCard() : '') + twCard(t) + helpCard(m.l) +
    (m.tr && eqStrip(t) ? '<button type="button" class="eqs">' + eqStrip(t) + '</button>' : '') +
    (m.tr ? voteRow(m) : '');
  var eb = el.querySelector('.eqs'); if(eb) eb.addEventListener('click', function(){ showEq(m); });
  $$('.fb button', el).forEach(function(b){ b.addEventListener('click', function(){ vote(m, b.getAttribute('data-v'), el); }); });
  return el;
}
/* ── 👍/👎 → /api/feedback (ส่งแค่เส้นทาง · ความเสี่ยง · ผลโหวต ไม่ส่งข้อความ) ── */
function voteRow(m){
  var done = m.v === 'up' || m.v === 'down';
  return '<div class="fb" role="group" aria-label="' + _t('คำตอบนี้ช่วยได้ไหม') + '">' +
    '<button type="button" data-v="up" aria-pressed="' + (m.v === 'up') + '"' + (done ? ' disabled' : '') + ' aria-label="' + _t('ช่วยได้') + '">👍</button>' +
    '<button type="button" data-v="down" aria-pressed="' + (m.v === 'down') + '"' + (done ? ' disabled' : '') + ' aria-label="' + _t('ยังไม่ช่วย') + '">👎</button>' +
    '<span class="muted">' + _t(done ? 'ขอบคุณที่บอกนะคะ' : 'คำตอบนี้ช่วยได้ไหม') + '</span></div>';
}
function vote(m, v, el){
  if(m.v || (v !== 'up' && v !== 'down')) return;
  m.v = v; Chat.persist();
  var row = el.querySelector('.fb'); if(row) row.outerHTML = voteRow(m);
  var t = m.tr || {};
  fetch('/api/feedback', { method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ vote:v, route:t.route || 'general', risk:num(t.risk, 0) }) }).catch(function(){});
}
var eqSel = null;
function eqSub(m){ var t = m && m.tr || {}; return [String(t.route || '').toUpperCase(), m && m.p || ''].filter(Boolean).join(' · '); }
function showEq(m){
  if(innerWidth >= 1240 && $('#app').classList.contains('has-trace')){ eqSel = m; paintEq(); return; }
  $('#dlg-eq-sub').textContent = eqSub(m); $('#dlg-eq-b').innerHTML = plainHTML(m.tr); $('#dlg-eq').showModal();
}
function paintEq(){
  var c = Chat.cur(), m = eqSel && c.msgs.indexOf(eqSel) >= 0 ? eqSel : null;
  if(!m) for(var i = c.msgs.length - 1; i >= 0; i--){ if(c.msgs[i].tr){ m = c.msgs[i]; break; } }
  $('#tp-sub').textContent = m ? eqSub(m) : '';
  $('#trace-last').innerHTML = m ? plainHTML(m.tr) : eqHTML(null);
  syncTrace();
}
/* แผงสูตรด้านขวา (จอกว้าง) โผล่เฉพาะเมื่อมีคำตอบให้อธิบายแล้ว — แชทว่างจะเหลือแค่โลกกับช่องพิมพ์
   (เจ้าของโปรเจกต์: "สูตรข้างๆ ควรซ่อนไว้ไหม คนจะได้มีสมาธิพิมพ์") */
function syncTrace(v){
  v = v || document.body.dataset.view || 'chat';
  var c = Chat.s && Chat.cur(), has = !!(c && c.msgs.some(function(x){ return x.tr; }));
  $('#app').classList.toggle('has-trace', v === 'chat' && has);
}
/* แชร์รายงาน: สร้างลิงก์ตอนกด → คัดลอกให้ · จำไว้ในข้อความ ครั้งหน้าเห็นลิงก์เลย */
document.addEventListener('click', async function(e){
  var b = e.target.closest('[data-act="share"]'); if(!b) return;
  e.preventDefault(); var tok = b.getAttribute('data-token'); b.disabled = true;
  try{
    var d = await readJson(await fetch('/api/report/share', {method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify({token: tok})}));
    Chat.cur().msgs.forEach(function(m){ if(m.tr && m.tr.share === tok) m.tr.report = d.report_id; });
    Chat.persist();
    var url = d.share_url || (location.origin + d.report_url), copied = false;
    try{ await navigator.clipboard.writeText(url); copied = true; }catch(_){}
    var row = b.parentNode; row.innerHTML = '<a href="' + esc(d.report_url) + '" target="_blank" rel="noopener" class="mono">' + esc(d.report_url) + '</a>';
    toast(copied ? 'คัดลอกลิงก์รายงานแล้วค่ะ' : 'สร้างลิงก์รายงานแล้วค่ะ');
  }catch(err){ b.disabled = false; toast(err.message || 'สร้างลิงก์ไม่สำเร็จ', true); }
});
document.addEventListener('click', function(e){
  var a = e.target.closest('[data-act="state"]'); if(!a) return;
  e.preventDefault(); if($('#dlg-eq').open) $('#dlg-eq').close(); MyState.fillForm(); $('#dlg-state').showModal();
});
/* ข้อความที่เพิ่งปรากฏ "ดึงโฟกัส" เข้ามาทีละข้อความ (.enter) — ข้อความที่เคยเห็นแล้วไม่ขยับซ้ำตอนวาดใหม่
   เปิดแชทเก่า: ไล่เฉพาะ 6 ข้อความท้าย · ระหว่างฉากเปิดเรื่องรอให้ม่านเปิดก่อน */
var SEEN = Object.create(null), CHANT_TS = 0;      /* คำตอบที่เพิ่งได้ — ค่อยๆ ปรากฏทีละบรรทัดแบบการสวด */
function renderMsgs(){
  var c = Chat.cur(), box = $('#msgs'), n = 0, last = c.msgs.length;
  /* กำลังคุยเรื่องด่วน/วิกฤต: ซ่อนของตกแต่งตามเทศกาล (ค้างคาว ฟักทอง) — ไม่ใช่เวลาเล่นสนุก */
  var la = c.msgs.slice().reverse().find(function(m){ return m.r === 'a' && m.tr; });
  document.documentElement.classList.toggle('kd-hush', !!(la && (la.tr.mode === 'crisis' || (la.tr.risk || 0) >= 75 || /1323|1669/.test(la.t))));
  var base = document.documentElement.classList.contains('opening') ? 1800 : 0; box.innerHTML = '';
  c.msgs.forEach(function(m, i){
    var el = msgEl(m), k = c.id + '|' + m.r + (m.ts || 0) + '|' + i;
    if(!SEEN[k]){ SEEN[k] = 1; if(!REDUCED && i >= last - 6){ el.classList.add('enter'); el.style.setProperty('--d', (base + n++ * 90) + 'ms'); } }
    if(CHANT_TS && m.r === 'a' && m.ts === CHANT_TS && !REDUCED){ CHANT_TS = 0; el.classList.add('chant'); el.style.setProperty('--chant', Math.min(7, Math.max(1.8, String(m.t || '').length / 45)).toFixed(1) + 's'); }
    box.appendChild(el);
  });
  $('#empty').classList.toggle('hide', c.msgs.length > 0);
  syncStarters();
  paintEq();
  updateVeil(); scrollBottom();
}
function scrollBottom(){ var s = $('#chat-scroll'), empty = !Chat.s || !Chat.cur().msgs.length; requestAnimationFrame(function(){ s.scrollTop = empty ? 0 : s.scrollHeight; }); }
function renderSessions(){
  var box = $('#sessions'), q = ($('#chat-search').value || '').trim().toLowerCase(); box.innerHTML = '';
  Chat.s.items.forEach(function(it){
    if(q && it.title.toLowerCase().indexOf(q) < 0 && !it.msgs.some(function(m){ return m.t.toLowerCase().indexOf(q) >= 0; })) return;
    var row = document.createElement('div'); row.className = 'sess' + (it.id === Chat.s.active ? ' on' : ''); row.setAttribute('role','listitem');
    var t = document.createElement('button'); t.type = 'button'; t.className = 't'; t.textContent = it.title || 'แชท';
    t.addEventListener('click', function(){ Chat.select(it.id); });
    var x = document.createElement('button'); x.type = 'button'; x.className = 'x'; x.textContent = '×'; x.setAttribute('aria-label', _t('ลบแชท {t}', {t: _t(it.title || '')}));
    x.addEventListener('click', function(e){ e.stopPropagation(); if(it.msgs.length && !confirm(_t('ลบแชท “{t}” ?', {t: it.title}))) return; Chat.remove(it.id); });
    row.appendChild(t); row.appendChild(x); box.appendChild(row);
  });
}
function renderAll(){ renderSessions(); renderMsgs(); Cosmos.rebuild(); }
/* ── โหมดภาพยนตร์: สำหรับอัดคลิป — ซ่อน UI เหลือโลก ธรรมจักร และบาลีจากธัมมจักกัปปวัตตนสูตรที่ค่อยๆ ปรากฏทีละวรรค
   สองท่อนที่เจ้าของโปรเจกต์เลือก: ธรรมจักรที่ไม่มีใครหมุนกลับได้ · ญาณทัสสนะในอริยสัจ ๔ ที่บริสุทธิ์ (= ปัญญา)
   บาลีเป็นพระสูตรต้นฉบับ · ความหมายเรียบเรียงใหม่สั้นๆ · ภาษาอื่นแสดงบาลีอักษรโรมัน
   ออก: แตะจอ · Esc · ออกจากเต็มจอ */
var CHANT = [
  { th: ['เอตัมภะคะวะตา พาราณะสิยัง อิสิปะตะเน มิคะทาเย', 'อะนุตตะรัง ธัมมะจักกัง ปะวัตติตัง', 'อัปปะฏิวัตติยัง สะมะเณนะ วา พราหมะเณนะ วา', 'เทเวนะ วา มาเรนะ วา พรัหมุนา วา เกนะจิ วา โลกัสมินติ'],
    ro: ['Etaṃ bhagavatā bārāṇasiyaṃ isipatane migadāye', 'anuttaraṃ dhammacakkaṃ pavattitaṃ', 'appaṭivattiyaṃ samaṇena vā brāhmaṇena vā', 'devena vā mārena vā brahmunā vā kenaci vā lokasmiṃ'],
    mean: 'วงล้อแห่งธรรมอันยอดเยี่ยมหมุนไปแล้ว — ไม่มีผู้ใดในโลกหมุนกลับได้' },
  { th: ['ยะโต จะ โข เม ภิกขะเว', 'อิเมสุ จะตูสุ อะริยะสัจเจสุ', 'เอวันติปะริวัฏฏัง ทวาทะสาการัง', 'ยะถาภูตัง ญาณะทัสสะนัง สุวิสุทธัง อะโหสิ'],
    ro: ['Yato ca kho me, bhikkhave,', 'imesu catūsu ariyasaccesu', 'evaṃ tiparivaṭṭaṃ dvādasākāraṃ', 'yathābhūtaṃ ñāṇadassanaṃ suvisuddhaṃ ahosi'],
    mean: 'เมื่อปัญญาที่รู้เห็นตามจริงในอริยสัจทั้งสี่ บริสุทธิ์ดีแล้ว' }
];
var Cine = (function(){
  var on = false, timer = 0, fs = false, P = $('#cn-pali'), M = $('#cn-mean'), H = $('#cn-hint');
  function seq(){
    var key = (window.KD_I18N && KD_I18N.get() !== 'th') ? 'ro' : 'th', out = [];
    CHANT.forEach(function(c){ c[key].forEach(function(l, i){ out.push({ l: l, m: i === 0 ? _t(c.mean) : null, end: i === c[key].length - 1 }); }); out.push(null); });
    return out;
  }
  function play(){
    var S = seq(), i = 0;
    function step(){
      if(!on) return;
      var it = S[i++ % S.length];
      P.classList.remove('on');
      if(!it){ M.classList.remove('on'); timer = setTimeout(step, 5000); return; }
      timer = setTimeout(function(){
        if(!on) return;
        P.textContent = it.l; P.classList.add('on');
        if(it.m != null){ M.textContent = it.m; M.classList.add('on'); }
        timer = setTimeout(function(){ if(it.end) M.classList.remove('on'); step(); }, REDUCED ? 5200 : 4600);
      }, REDUCED ? 200 : 1800);
    }
    timer = setTimeout(step, REDUCED ? 600 : 5200);          /* รอดวงอาทิตย์เริ่มขึ้นก่อน */
  }
  function enter(){
    if(on) return; on = true;
    if(document.body.dataset.view !== 'chat') setView('chat');
    document.documentElement.classList.add('kd-cinema'); Cosmos.cinema(true);
    H.textContent = _t('แตะหรือกด Esc เพื่อออก'); H.classList.remove('off'); setTimeout(function(){ H.classList.add('off'); }, 3200);
    try{ var r = document.documentElement.requestFullscreen && document.documentElement.requestFullscreen(); if(r && r.then) r.then(function(){ fs = true; }, function(){}); }catch(_){}
    play();
  }
  function exit(){
    if(!on) return; on = false; clearTimeout(timer); fs = false;
    P.classList.remove('on'); M.classList.remove('on');
    document.documentElement.classList.remove('kd-cinema'); Cosmos.cinema(false);
    try{ if(document.fullscreenElement) document.exitFullscreen(); }catch(_){}
  }
  $('#cinema-btn').addEventListener('click', function(){ $('#theme-menu').classList.add('hide'); enter(); });
  $('#cinema').addEventListener('click', exit);
  addEventListener('keydown', function(e){ if(on && e.key === 'Escape') exit(); });
  document.addEventListener('fullscreenchange', function(){ if(on && fs && !document.fullscreenElement) exit(); });
  return { enter: enter, exit: exit, on: function(){ return on; } };
})();
/* เปลี่ยนภาษา (static/i18n.js ส่ง kd:lang): วาดส่วนที่สคริปต์ประกอบเองใหม่ ให้ตัวเลข/ข้อความแทรกเป็นภาษาใหม่ด้วย */
document.addEventListener('kd:lang', function(){
  try{ renderAll(); Limit.ui(); }catch(_){}
  try{ if(Auth.loggedIn){ TFA.load(); loadHistory(); loadMemory(); } }catch(_){}
  try{ if(sysBuilt){ sysStats(); renderHealth(); renderFiles(); } }catch(_){}
});
$('#chat-search').addEventListener('input', renderSessions);
$('#new-chat').addEventListener('click', function(){ Chat.create(); });

/* ════════════════════════════════════════════════════════════════
   SEND  (POST /run)
   ════════════════════════════════════════════════════════════════ */
var busy = false;
async function send(textArg){
  var inp = $('#input'), text = String(textArg != null ? textArg : inp.value).trim();
  if(!text || busy) return;
  if(navigator.vibrate) try{ navigator.vibrate(6); }catch(_){}
  var mode = detectMode(text), sessId = Chat.s.active;
  var history = Chat.cur().msgs.filter(function(m){ return m.r !== 'e'; }).slice(-8).map(function(m){ return { role: m.r === 'u' ? 'user' : 'assistant', content: m.t }; });
  var state = MyState.payload(), sentState = Object.keys(state).length > 0;
  Chat.push({ r:'u', t:text }); Chat.rename(text);
  inp.value = ''; autosize(); renderAll();
  busy = true; $('#send').disabled = true; Cosmos.thinking(true);
  window.dispatchEvent(new CustomEvent('KD:thinking', { detail:{ on:true } }));
  var th = document.createElement('div'); th.className = 'm a' + (REDUCED ? '' : ' enter'); th.innerHTML = '<div class="who"><span class="' + (mode==='vega'?'vega':mode==='crisis'?'crisis':mode==='council'?'council':'lyla') + '">' + (mode==='vega'?'VEGA':mode==='crisis'?'HALT':mode==='council'?_t('สภา 6 เสียง'):'LYLA') + '</span><span class="tag">กำลังคิด…</span></div><div class="thinking"><i></i><i></i><i></i></div>';
  $('#msgs').appendChild(th); scrollBottom();
  var body = { input:text, route:Route, voice_mode:mode, persona_ui:Persona, voice_hint:voiceHint(mode), history:history,
    context: Object.assign({ client_voice:mode, tone_notes:voiceHint(mode), route_ui:Route }, state) };
  var born = null;
  try{
    var d = await readJson(await fetchRetry('/run', { method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify(body) }, 3));
    var target = Chat.s.items.find(function(x){ return x.id === sessId; }) || Chat.cur();
    if(d.quota){ Limit.set(d.quota); }
    if(!d.error) window.dispatchEvent(new CustomEvent('KD:response', { detail:{ route: d.route, risk_score: num(d.risk_score, 0), consensus: d.consensus } }));
    if(d.error){ target.msgs.push({ r:'e', t:String(d.error), ts:Date.now() }); toast(String(d.error), true); }
    else{
      var reply = String(d.ai_response || d.pause_reason || d.message || '').replace(/\s*[—–-]+\s*(LYLA\s*[◈✦✧]?|VEGA\s*[◆◇]?|HALT\s*[⬡]?|สภา\s*KING\s*DIADEM\s*✦?)\s*$/gi, '').trim();
      born = { r:'a', t: reply || '(ไม่มีข้อความตอบกลับ)', p: d.persona || (mode==='vega' ? 'VEGA' : mode==='council' ? 'COUNCIL' : 'LYLA'), tr: traceOf(d, mode, sentState ? state : null), l: d.help_links, ts:Date.now() };
      target.msgs.push(born);
    }
    Chat.persist(); refreshMe();
  }catch(e){
    var tg = Chat.s.items.find(function(x){ return x.id === sessId; }) || Chat.cur();
    if(e.status === 402){ Limit.set(e.data && e.data.quota); Limit.ui(); openUpgrade(); }
    tg.msgs.push({ r:'e', t:e.message, ts:Date.now() }); Chat.persist(); if(e.status !== 402) toast(e.message, true, 6000);
  }finally{
    busy = false; $('#send').disabled = false; th.remove(); Cosmos.thinking(false); if(born) CHANT_TS = born.ts; renderAll();
    window.dispatchEvent(new CustomEvent('KD:thinking', { detail:{ on:false } }));
    if(window.KD_galaxy) KD_galaxy.refocus();
    if(born) Cosmos.birth(born.ts);
  }
}
function autosize(){ var t = $('#input'); t.style.height = 'auto'; t.style.height = Math.min(t.scrollHeight, 160) + 'px'; }
$('#input').addEventListener('input', autosize);
$('#input').addEventListener('keydown', function(e){
  if(e.key === 'Enter' && !e.shiftKey && !e.isComposing && e.keyCode !== 229){ e.preventDefault(); send(); }
});
$('#send').addEventListener('click', function(){ send(); });
/* ตัวอย่างคำถามหน้าแรก: แสดงเฉพาะแชทว่างและยังไม่ได้พิมพ์ · แตะ = เติมลงช่องพิมพ์ (ยังไม่ส่ง ให้แก้ให้ตรงเรื่องตัวเองก่อน) */
function syncStarters(){
  var st = $('#starters'); if(!st) return;
  var inp = $('#input'), show = !$('#empty').classList.contains('hide') && !(inp && inp.value.trim());
  st.classList.toggle('hide', !show);
}
$$('#starters .st-chip').forEach(function(b){
  b.addEventListener('click', function(){
    /* หน้าไทยเติมประโยคเต็ม · เปลี่ยนภาษาแล้วใช้ข้อความบนปุ่ม (แปลแล้ว) ตัดอีโมจิหน้าออก */
    var inp = $('#input'), th = /^th/i.test(document.documentElement.lang || 'th');
    inp.value = th ? b.getAttribute('data-q') : b.textContent.replace(/^[^\p{L}\p{N}]+/u, '').trim();
    inp.dispatchEvent(new Event('input', { bubbles: true })); inp.focus();
    try{ inp.setSelectionRange(inp.value.length, inp.value.length); }catch(_){}
  });
});
$('#input').addEventListener('input', syncStarters);
$$('.sugg button').forEach(function(b){ b.addEventListener('click', function(){ send(b.textContent); }); });

/* ════════════════════════════════════════════════════════════════
   TOOLS — /simulate · /analyze-image · /create-checkout-session
   ════════════════════════════════════════════════════════════════ */
function addPath(v){
  var box = $('#sim-paths'), n = box.children.length; if(n >= 7) return;   /* เซิร์ฟเวอร์รับ 7 ทาง (A–G) — ทางที่ 8 เคยถูกทิ้งเงียบๆ */
  var row = document.createElement('div'); row.className = 'path';
  row.innerHTML = '<b></b><input class="inp" type="text" aria-label="ทางเลือก" placeholder="ทางเลือก เช่น ลงทุน 200,000 · ได้เพิ่มเดือนละ 5,000"><button type="button" aria-label="ลบทางเลือก">×</button>';
  row.querySelector('input').value = v || '';
  row.querySelector('button').addEventListener('click', function(){ row.remove(); relabel(); });
  box.appendChild(row); relabel();
}
function relabel(){ $$('#sim-paths .path b').forEach(function(b, i){ b.textContent = String.fromCharCode(65 + i); }); }
['เดินหน้าต่อแบบเดิม','หยุดและประเมินใหม่','หาพันธมิตรหรือทรัพยากรเพิ่ม'].forEach(function(v){ addPath(_t(v)); });
$('#sim-add').addEventListener('click', function(){ addPath(''); var ins = $$('#sim-paths input'); ins[ins.length-1].focus(); });
$('#sim-run').addEventListener('click', async function(){
  var btn = this, out = $('#sim-out'), input = $('#sim-input').value.trim();
  if(!input){ out.className = 'out empty'; out.textContent = _t('พิมพ์สถานการณ์ก่อน'); $('#sim-input').focus(); return; }
  var paths = $$('#sim-paths input').map(function(i){ return i.value.trim(); }).filter(Boolean);
  btn.disabled = true; out.className = 'out empty'; out.textContent = _t('กำลังวิเคราะห์ทางเลือก…');
  try{
    var d = await readJson(await fetchRetry('/simulate', { method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ input:input, paths:paths, user_email: Auth.email || null }) }, 2));
    if(d.error) throw new Error(d.error);
    var txt = d.simulation || d.message || '';
    if(typeof txt !== 'string') txt = JSON.stringify(txt, null, 2);
    if(!txt) txt = JSON.stringify(d, null, 2);
    out.className = 'out'; out.textContent = txt;
    drawFuture(d.future);
  }catch(e){ out.className = 'out'; out.textContent = '⚠ ' + e.message; drawFuture(null); }
  finally{ btn.disabled = false; }
});
/* ── ภาพจำลองอนาคต 12 เดือน (core/future_paths) — เส้น = ค่ากลาง · แถบ = p10–p90 ── */
function drawFuture(f){
  var box = $('#sim-future');
  var P = f && Array.isArray(f.paths) ? f.paths.filter(function(p){ return p && Array.isArray(p.mid) && p.mid.length > 1; }).slice(0, 3) : [];
  if(!P.length){ box.classList.add('hide'); box.innerHTML = ''; return; }
  var W = 360, H = 210, L = 30, R = 64, T = 12, B = 26, n = P[0].mid.length - 1, floor = num(f.floor, 30);
  function x(t){ return L + (W - L - R) * t / n; }
  function y(v){ return T + (H - T - B) * (1 - Math.max(0, Math.min(100, num(v, 0))) / 100); }
  function line(a){ return a.map(function(v, t){ return (t ? 'L' : 'M') + x(t).toFixed(1) + ' ' + y(v).toFixed(1); }).join(''); }
  var svg = '<svg viewBox="0 0 ' + W + ' ' + H + '" role="img" aria-label="ภาพจำลองความมั่นคง W ของแต่ละทางเลือก 12 เดือน">';
  [0, 50, 100].forEach(function(v){ svg += '<line class="g" x1="' + L + '" x2="' + (W - R) + '" y1="' + y(v) + '" y2="' + y(v) + '"/><text class="ax" x="' + (L - 6) + '" y="' + (y(v) + 4) + '" text-anchor="end">' + v + '</text>'; });
  [[0, _t('วันนี้')], [n / 2, _t('{n} เดือน', {n: n / 2})], [n, _t('{n} เดือน', {n: n})]].forEach(function(a){ svg += '<text class="ax" x="' + x(a[0]) + '" y="' + (H - 8) + '" text-anchor="middle">' + a[1] + '</text>'; });
  svg += '<line class="fl" x1="' + L + '" x2="' + (W - R) + '" y1="' + y(floor) + '" y2="' + y(floor) + '"/>';
  P.forEach(function(p, i){
    var band = line(p.hi) + p.lo.slice().reverse().map(function(v, k){ return 'L' + x(n - k).toFixed(1) + ' ' + y(v).toFixed(1); }).join('') + 'Z';
    svg += '<path class="band s' + (i + 1) + '" d="' + band + '"/>';
  });
  P.forEach(function(p, i){ svg += '<path class="mid s' + (i + 1) + (p.reversible ? '' : ' irr') + '" d="' + line(p.mid) + '"/>'; });
  var ends = P.map(function(p, i){ return { i:i, y:y(p.mid[n]), p:p }; }).sort(function(a, b){ return a.y - b.y; });
  ends.forEach(function(e, k){ if(k && e.y - ends[k - 1].y < 13) e.y = ends[k - 1].y + 13; });     // ป้ายไม่ทับกัน
  ends.forEach(function(e){ svg += '<circle class="dot s' + (e.i + 1) + '" cx="' + x(n) + '" cy="' + y(e.p.mid[n]) + '" r="4"/><text class="lab" x="' + (x(n) + 8) + '" y="' + (e.y + 4) + '">' + esc(e.p.label) + ' · ' + Math.round(e.p.mid[n]) + '</text>'; });
  svg += '<text class="ax fll" x="' + (L + 4) + '" y="' + (y(floor) - 4) + '">' + _t('เส้นอันตราย W {n}', {n: floor}) + '</text>';      // วาดทีหลังแถบ ไม่ให้ถูกบัง
  svg += '<line class="xh hide" y1="' + T + '" y2="' + (H - B) + '"/><rect class="hit" x="' + L + '" y="' + T + '" width="' + (W - L - R) + '" height="' + (H - T - B) + '"/></svg>';
  var legend = P.map(function(p, i){ return '<li><span class="sw s' + (i + 1) + '"></span><b>' + esc(p.label) + '</b> ' + esc(p.action) + ' <span class="muted">· ' + _t(p.reversible ? 'ย้อนกลับได้' : 'ย้อนกลับไม่ได้ (เส้นประ)') + (p.same ? ' · ' + _t('สมการให้ผลเท่ากัน') : '') + '</span>' +
    (p.money && Array.isArray(p.money.notes) && p.money.notes.length ? '<div class="mn">' + esc(p.money.notes.join(' · ')) + '</div>' : '') + '</li>'; }).join('');
  var notes = P.filter(function(p){ return p.money && p.money.runs_out_month != null; }).map(function(p){ return '<p>⚠ ' + esc(p.label) + ': ' + _t('ตามตัวเลขที่บอก เงินเก็บจะหมดราวเดือนที่ {n} — ลองลดเงินก้อนแรก หรือหารายได้ช่วงเปลี่ยนผ่านก่อน', {n: num(p.money.runs_out_month, 0)}) + '</p>'; }).join('') +
    P.filter(function(p){ return p.below_floor_month != null; }).map(function(p){ return '<p>⚠ ' + esc(p.label) + ': ' + _t('กรณีแย่ลงไปต่ำกว่าเส้นอันตรายได้ตั้งแต่เดือนที่ {n} — เตรียมเงินสำรองหรือทางถอยไว้ก่อนเริ่ม', {n: p.below_floor_month}) + '</p>'; }).join('') +
    (f.black_swan ? '<p>🦢 ' + _t('เรื่องที่เล่ามีโอกาสเกิดเหตุช็อกใหญ่ (ฟื้นตัวราว {n} วัน)', {n: num(f.black_swan.recovery_days, 0)}) + ' — ' + P.map(function(p){ return esc(p.label) + ' ' + _t('ถ้าโดนช็อก W อาจลงถึง {n}', {n: num(p.tail_worst, 0)}); }).join(' · ') + '. ' + esc(f.black_swan.recommendation || '') + '</p>' : '');
  var mb = f.money_basis || {}, basisTxt = [['savings', 'เงินเก็บ'], ['income', 'รายได้/เดือน'], ['expense', 'รายจ่าย/เดือน']].filter(function(k){ return mb[k[0]] != null; }).map(function(k){ return _t(k[1]) + ' ' + Math.round(num(mb[k[0]], 0)).toLocaleString('th-TH'); }).join(' · ');
  var cols = [0, 3, 6, 9, 12].filter(function(t){ return t <= n; });
  var table = '<details><summary>ดูเป็นตาราง</summary><table><tr><th>ทาง</th>' + cols.map(function(t){ return '<th>' + (t ? _t('เดือน {n}', {n: t}) : _t('วันนี้')) + '</th>'; }).join('') + '</tr>' +
    P.map(function(p){ return '<tr><td>' + esc(p.label) + '</td>' + cols.map(function(t){ return '<td>' + Math.round(p.mid[t]) + ' <span class="muted">(' + Math.round(p.lo[t]) + '–' + Math.round(p.hi[t]) + ')</span></td>'; }).join('') + '</tr>'; }).join('') + '</table></details>';
  box.innerHTML = '<div class="fh"><b>ภาพจำลองอนาคต 12 เดือน</b><span class="muted">' + _t('W ตอนนี้ {n}', {n: num(f.w0, 0)}) + '</span></div>' +
    '<div class="chart">' + svg + '<div class="tip hide"></div></div><ul class="lg">' + legend + '</ul>' + notes +
    (Array.isArray(f.hidden) && f.hidden.length ? '<p class="muted">' + _t('ไม่ได้วาด: {x}', {x: esc(f.hidden.join(' · '))}) + '</p>' : '') +
    (basisTxt ? '<p class="muted">' + _t('ตัวเลขที่ใช้คิด: {x}', {x: esc(basisTxt)}) + '</p>' : '') +
    (f.money_hint ? '<p class="hint">💡 ' + esc(f.money_hint) + '</p>' : '') +
    '<p class="muted">เส้น = ค่ากลาง · แถบ = ช่วงที่เป็นไปได้ 80% · คำนวณจากสมการของระบบ (ย้อนกลับได้ไหม · สถานะตอนนี้ · ตัวเลขเงินที่คุณบอก) ไม่ใช่คำทำนาย</p>' + table;
  box.classList.remove('hide');
  var el = box.querySelector('svg'), xh = el.querySelector('.xh'), tip = box.querySelector('.tip');
  el.querySelector('.hit').addEventListener('pointermove', function(ev){
    var r = el.getBoundingClientRect(), sx = (ev.clientX - r.left) * W / r.width;
    var t = Math.max(0, Math.min(n, Math.round((sx - L) / (W - L - R) * n)));
    xh.setAttribute('x1', x(t)); xh.setAttribute('x2', x(t)); xh.classList.remove('hide');
    tip.innerHTML = '<b>' + (t ? _t('เดือนที่ {n}', {n: t}) : _t('วันนี้')) + '</b>' + P.map(function(p, i){ return '<div><span class="sw s' + (i + 1) + '"></span>' + esc(p.label) + ' W ' + Math.round(p.mid[t]) + ' <span class="muted">(' + Math.round(p.lo[t]) + '–' + Math.round(p.hi[t]) + ')</span></div>'; }).join('');
    tip.classList.remove('hide');
    var px = x(t) / W * r.width; tip.style.left = Math.min(Math.max(0, px - tip.offsetWidth / 2), r.width - tip.offsetWidth) + 'px';
  });
  el.querySelector('.hit').addEventListener('pointerleave', function(){ xh.classList.add('hide'); tip.classList.add('hide'); });
}
$('#img-file').addEventListener('change', function(){
  var f = this.files[0], prev = $('#img-prev');
  if(!f){ prev.classList.add('hide'); $('#img-name').textContent = 'แตะเพื่อเลือกภาพ'; return; }
  $('#img-name').textContent = f.name + ' · ' + (f.size / 1048576).toFixed(1) + ' MB';
  try{ if(prev.src) URL.revokeObjectURL(prev.src); prev.src = URL.createObjectURL(f); prev.classList.remove('hide'); }catch(_){}
});
$('#img-run').addEventListener('click', async function(){
  var btn = this, f = $('#img-file').files[0], out = $('#img-out');
  if(!f){ out.className = 'out empty'; out.textContent = 'เลือกภาพก่อน'; return; }
  if(['image/jpeg','image/png','image/webp'].indexOf(f.type) < 0){ out.className = 'out'; out.textContent = '⚠ รองรับเฉพาะ jpeg / png / webp'; return; }
  if(f.size > 10 * 1048576){ out.className = 'out'; out.textContent = '⚠ ไฟล์ใหญ่เกิน 10MB'; return; }
  var fd = new FormData(); fd.append('file', f);
  btn.disabled = true; out.className = 'out empty'; out.textContent = 'กำลังวิเคราะห์ภาพ…';
  try{
    var d = await readJson(await fetchRetry('/analyze-image', { method:'POST', credentials:'same-origin', body: fd }, 2));
    if(d.error) throw new Error(d.error);
    out.className = 'out'; out.textContent = (d.analysis || 'วิเคราะห์ภาพไม่ได้ — ลองภาพอื่น').trim();
  }catch(e){ out.className = 'out'; out.textContent = '⚠ ' + e.message; }
  finally{ btn.disabled = false; }
});
$('#pay-run').addEventListener('click', async function(){
  var btn = this, email = $('#pay-email').value.trim(), plan = ($('input[name=plan]:checked') || {}).value || 'basic';
  if(!Auth.loggedIn){ toast('เข้าสู่ระบบก่อนนะคะ เครดิตจะได้เข้าบัญชีของคุณ', true); setTimeout(function(){ location.href = '/static/login.html'; }, 900); return; }
  btn.disabled = true;
  try{
    var d = await readJson(await fetch('/create-checkout-session', { method:'POST', credentials:'same-origin', headers:{'Content-Type':'application/json'}, body: JSON.stringify({ plan:plan, email:email, api_key:email }) }));
    if(d.url) location.href = d.url; else toast(d.error || d.message || 'สร้าง Stripe checkout ไม่สำเร็จ', true);
  }catch(e){ toast(e.message, true); }
  finally{ btn.disabled = false; }
});

/* ════════════════════════════════════════════════════════════════
   HEALTH  (GET /health)
   ════════════════════════════════════════════════════════════════ */
var Health = { d:null, at:0 };
var HEALTH_ROWS = [
  ['llm_loaded','Gemini LLM','bool'], ['engine_loaded','DecisionEngine','bool'], ['universal_engine','Universal engine','bool'],
  ['belief_core','Belief core','bool'], ['survivor_engine','Survivor engine','bool'], ['risk_engine','Risk engine','bool'],
  ['consensus_engine','Consensus engine','bool'], ['collapse_predictor','Collapse predictor','bool'], ['simulation_engine','Simulation engine','bool'],
  ['cosmic_latte_canon','Canon gate','bool'], ['king_diadem_core','KING DIADEM core','core'], ['stripe_loaded','Stripe','bool'],
  ['db_initialized','Database','bool'], ['freedom_score','Freedom score','num'], ['feedback','เสียงจากผู้ใช้ 👍/👎','fb']
];
var sysBuilt = false;
async function checkHealth(){
  if(document.hidden) return;
  try{
    Health.d = await readJson(await fetch('/health', {cache:'no-store'})); Health.at = Date.now();
    $('#ai-dot').className = 'dot ' + (Health.d.llm_loaded ? 'ok' : 'bad'); $('#ai-txt').textContent = Health.d.llm_loaded ? 'AI' : 'AI ✕';
  }catch(_){
    Health.d = null; $('#ai-dot').className = 'dot warn'; $('#ai-txt').textContent = 'ออฟไลน์';
  }
  if(sysBuilt) renderHealth();
}
function renderHealth(){
  var box = $('#sys-health'), d = Health.d;
  if(!d){ box.innerHTML = '<span class="muted">ติดต่อ /health ไม่ได้ — เซิร์ฟเวอร์อาจกำลังตื่น</span>'; return; }
  $('#sys-health-at').textContent = _t('อัปเดต {t}', {t: ''}) + new Date(Health.at).toLocaleTimeString('th-TH', {hour:'2-digit', minute:'2-digit', second:'2-digit'});
  box.innerHTML = HEALTH_ROWS.map(function(r){
    var v = d[r[0]], cls, txt;
    if(r[2] === 'core'){ var cv = v && v.core_version; cls = cv && cv !== 'fallback' ? 'ok' : 'warn'; txt = cv || '—'; }
    else if(r[2] === 'num'){ cls = ''; txt = v == null ? '—' : String(v); }
    else if(r[2] === 'fb'){ cls = !v ? 'bad' : v.signal === 'DRIFT_ALERT' ? 'bad' : v.votes ? 'ok' : ''; txt = !v ? _t('ไม่โหลด') : v.votes ? _t('{v} โหวต · ช่วยได้ {r}% · {t}', {v: v.votes, r: Math.round(num(v.helpful_rate, 0) * 100), t: v.trend}) : _t('ยังไม่มีโหวต'); }
    else { cls = v ? 'ok' : 'bad'; txt = v ? 'โหลดแล้ว' : 'ไม่โหลด'; }
    return '<div><span class="dot ' + cls + '"></span>' + esc(r[1]) + '<span class="mono">' + esc(txt) + '</span></div>';
  }).join('') + (d.version ? '<div><span class="dot"></span>เวอร์ชัน<span class="mono">' + esc(d.version) + '</span></div>' : '');
}

/* ════════════════════════════════════════════════════════════════
   SYSTEM VIEW
   ════════════════════════════════════════════════════════════════ */
var PIPE = [
  ['จำกัดความถี่ + ตัวตน', 'สูงสุด 20 ข้อความต่อ 60 วินาทีต่อคน · ข้อความยาวไม่เกิน 4,000 ตัว · ตัวตนมาจาก cookie ที่เซ็นด้วย SECRET_KEY เท่านั้น · IP มาจาก proxy ที่เชื่อถือ (ปลอม header ไม่ได้)', 'app.py', 'ok', 'ทำงาน'],
  ['โควตา + เครดิต', 'ฟรี 20 ข้อความ/วัน นับที่ server (ต่ออีเมล หรือต่อ IP) → เกินแล้วหัก 1 เครดิต/ข้อความ · Premium ไม่จำกัด · ถ้าระบบตอบไม่ได้ (error / Gemini ล้ม / ถูกระงับ) คืนให้อัตโนมัติ · เติมผ่าน Stripe ที่หน้า wallet', 'app.py · DATABASE/db.py', 'ok', 'ทำงาน'],
  ['อ่านสถานะคน', 'แปลง context (พลังงาน การนอน อาหาร ที่พัก จิตใจ) เป็น waterline 0–100 — หน้านี้ส่งจาก “สถานะของฉัน”', 'ENGINE/human_engine.py → realhuman_survivorengine.py', 'ok', 'ทำงาน'],
  ['จับเจตนา', 'จัดประเภทคำถาม', 'AI/intent_engine.py', 'ok', 'ทำงาน'],
  ['ประเมินความเสี่ยง', 'risk = entropy×0.5 + (100−resource)×0.5 · คำในข้อความ: ทำร้ายตัวเอง → collapse, ขาดปัจจัยพื้นฐาน → survival · เส้นทางยกระดับได้อย่างเดียว ไม่ลดลง', 'ENGINE/risk_engine.py', 'ok', 'ทำงาน'],
  ['คาดการณ์ collapse', 'ความเสี่ยงระดับ moderate/high จะเติมบริบท [Collapse: …] ให้ LLM', 'ENGINE/collapse_predictor.py', 'ok', 'ทำงาน'],
  ['โพธิปักขิยธรรม (core v2.1)', 'structure = ((100−E)+R+S)/300 · < 0.35 → survival · ปฏิจจสมุปบาท + โยนิโสมนสิการ เติมบริบทเมื่อมีสัญญาณจริง', 'core/king_diadem_core.py', 'ok', 'ทำงาน'],
  ['Orchestrator + survivor', 'ร้อยปฏิจจสมุปบาท living water survival advisor แล้วส่ง survivor context ให้ขั้นถัดไป (ไม่เรียก LLM ซ้ำ)', 'core/system_orchestrator.py', 'ok', 'ทำงาน'],
  ['Belief core audit', 'ตรวจ Choice และ Survival floor ถ้าวิกฤตจะหยุดระบบ (SYSTEM_PAUSE) ก่อนถึง LLM', 'AI_KERNEL/belief_core.py', 'ok', 'ทำงาน'],
  ['DecisionEngine', 'ต่อติดแล้วด้วยตัวเชื่อม emptiness_guard(): วิเคราะห์ pattern → emptiness guard (Choice ≥ 1) → core loop → ปฏิจจสมุปบาท → engine router ตามเส้นทาง', 'ENGINE/decision_engine.py → core/emptiness_guard.py', 'ok', 'ทำงาน'],
  ['Gemini ตอบ', 'DecisionEngine ส่งบริบททั้งหมดให้ LLM สร้างคำตอบตามเสียง LYLA หรือ VEGA พร้อมตรวจสัญญาณวิกฤตและแนบสายด่วน 1323', 'core/llm_gemini.py', 'ok', 'LLM 1 ครั้ง'],
  ['ไม่มี AI ก็ตอบได้', 'Gemini ล้ม / โควตาหมด / ไม่มี key → ตอบจากสมการทันที: W · Risk · Choice(t) + ทางที่ทำได้จริง + สายด่วน · input เดิมได้คำตอบเดิม · ไม่หักโควตา', 'core/kernel_voice.py', 'ok', 'ทำงาน'],
  ['Universal engine', 'เติม council / state ถ้ายังไม่มี', 'ENGINE/universal_engine.py', 'ok', 'ทำงาน'],
  ['Consensus', 'สรุป final action จากข้อความ คำตอบ และสถานะ', 'ENGINE/consensus_engine.py', 'ok', 'ทำงาน'],
  ['Belief enforce', 'แนบผล audit ลงคำตอบ และแทนคำตอบด้วยข้อความ PAUSE ถ้าจำเป็น', 'AI_KERNEL/belief_core.py', 'ok', 'ทำงาน'],
  ['Canon gate', 'บล็อกคำตอบที่ทำให้ทางเลือกเป็นศูนย์หรือบังคับ identity · รู้จักคำปฏิเสธ (“ไม่ต้องทำ” ผ่าน) และไม่บล็อกคำตอบที่เสนอทางเลือกตั้งแต่ 2 ทาง', 'core/cosmic_latte_canon.py', 'ok', 'ทำงาน'],
  ['Freedom signal', 'นับวิกฤตและทางเลือกที่ยังเหลือต่อคน (ไม่มี inf ใน JSON) · เก็บข้าง DB_PATH บนดิสก์ถาวร', 'AI/freedom_signal.py', 'ok', 'ทำงาน'],
  ['บันทึก + รายงาน', 'บันทึกการตัดสินใจลง SQLite · กดแชร์แล้วได้รายงาน /report/<id> (เปิดได้ 90 วัน) — และหน้านี้เปลี่ยนคำตอบเป็นดาวในจักรวาล', 'DATABASE/db.py · report_engine.py', 'ok', 'ทำงาน'],
  ['เรียนรู้จากเสียงผู้ใช้', '👍/👎 ใต้คำตอบ → เก็บแค่เส้นทาง · ความเสี่ยง · ผลโหวต (ไม่เก็บข้อความ) ลง SQLite → อัตราที่ช่วยได้ต่อเส้นทาง + แนวโน้ม + drift', 'core/feedback_loop.py', 'ok', 'ทำงาน'],
];
var catOn = {};
CATS.forEach(function(c){ catOn[c[0]] = true; });
function catColor(c){ return 'var(--c-' + c + ')'; }
function buildSystem(){
  if(sysBuilt) return; sysBuilt = true;
  loadLiveMap();                                   // ขอตัวเลขสดก่อน ป้ายจะได้ขึ้นว่า "กำลังโหลด" ไม่ใช่ "ชุดที่ฝังไว้"
  sysStats();
  $('#sys-eq').outerHTML = eqCatalog();
  $('#sys-pipe').innerHTML = PIPE.map(function(p){
    return '<li title="' + esc(p[1]) + '"><div><div class="t">' + esc(p[0]) + '</div><code>' + esc(p[2]) + '</code></div><span class="st"><i style="background:var(--' + (p[3] === 'ok' ? 'ok' : 'warn') + ')"></i>' + (p[3] === 'ok' ? '' : esc(p[4])) + '</span></li>';
  }).join('');
  renderHealth(); renderFiles();
  $('#fx-q').addEventListener('input', renderFiles);
}
/* แผนผังสด: เซิร์ฟเวอร์นับจากไฟล์ที่รันอยู่จริงหลัง deploy ล่าสุด (/api/system_map)
   เดิมตัวเลขมาจากชุดที่ฝังไว้ในหน้านี้ตอน commit — ลืมรันสคริปต์ทีไรตัวเลขก็ค้าง · โหลดไม่ได้ก็ใช้ชุดเดิมต่อ */
var mapLive = false, mapLoading = false;
function loadLiveMap(){
  if(mapLive || mapLoading) return;
  mapLoading = true;
  fetch('/api/system_map', { cache: 'no-cache' }).then(function(r){ return r.ok ? r.json() : null; }).then(function(d){
    if(!d || !d.files || !d.files.length) return;
    MAP = d; mapLive = true;
    sysStats(); renderFiles();
    if($('#nav-files')) $('#nav-files').textContent = MAP.files.length;
  }).catch(function(){}).then(function(){ mapLoading = false; if(!mapLive) sysStats(); });
}
function sysStats(){
  var F = MAP.files || [], counts = {}, lines = 0, py = 0;
  var fixed = 0;
  F.forEach(function(f){ counts[f[2]] = (counts[f[2]] || 0) + 1; lines += f[1]; if(/\.py$/.test(f[0])) py++; if(f[5] === 'fixed' || f[5] === 'new') fixed++; });
  $('#sys-commit').textContent = MAP.commit || '—';
  var pill = $('#sys-live');
  if(pill){
    pill.className = 'live-pill ' + (mapLive ? 'on' : mapLoading ? 'wait' : 'old');
    pill.innerHTML = '<i></i><span>' + (mapLive ? 'สด · นับจากโค้ดที่รันอยู่จริง' : mapLoading ? 'กำลังโหลดตัวเลขสด…' : 'ชุดที่ฝังไว้ · ยังโหลดตัวเลขสดไม่ได้') + '</span>' +
      (MAP.commit ? ' <small>' + esc(MAP.commit) + '</small>' : '');
  }
  $('#sys-commit').title = mapLive ? _t('นับจากไฟล์ที่เซิร์ฟเวอร์รันอยู่จริง') + (MAP.built_at ? ' · ' + MAP.built_at : '') : _t('ยังโหลดแผนผังสดไม่ได้ — แสดงชุดที่ฝังไว้ตอน commit');
  var live = (counts.boot || 0) + (counts.request || 0);
  $('#sys-stats').innerHTML =
    '<div><b>' + F.length + '</b><span>ไฟล์ใน repo</span></div>' +
    '<div><b>' + lines.toLocaleString('en-US') + '</b><span>บรรทัด (text)</span></div>' +
    '<div><b>' + live + '</b><span>โมดูล Python ที่รันจริง</span></div>' +
    '<div><b>' + py + '</b><span>ไฟล์ Python ทั้งหมด</span></div>' +
    '<div><b>' + fixed + '</b><span>ไฟล์ที่ซ่อมรอยรั่วแล้ว</span></div>';
  $('#sys-stack').innerHTML = CATS.filter(function(c){ return counts[c[0]]; }).map(function(c){
    return '<i style="width:' + (counts[c[0]] / F.length * 100) + '%;background:' + catColor(c[0]) + '" title="' + esc(_t(c[1]) + ' ' + counts[c[0]]) + '"></i>';
  }).join('');
  var lg = $('#sys-legend'); lg.innerHTML = '';
  CATS.forEach(function(c){
    if(!counts[c[0]]) return;
    var b = document.createElement('button'); b.type = 'button'; b.dataset.c = c[0]; if(!catOn[c[0]]) b.classList.add('off');   // วาดใหม่ตอนแผนผังสดมาถึง — คงตัวกรองที่เลือกไว้
    b.innerHTML = '<span class="sw" style="background:' + catColor(c[0]) + '"></span>' + esc(c[1]) + ' <b>' + counts[c[0]] + '</b>';
    b.addEventListener('click', function(){
      var only = Object.keys(catOn).every(function(k){ return catOn[k] === (k === c[0]); });
      Object.keys(catOn).forEach(function(k){ catOn[k] = only ? true : (k === c[0]); });
      $$('#sys-legend button').forEach(function(x){ x.classList.toggle('off', !catOn[x.dataset.c]); });
      renderFiles();
    });
    lg.appendChild(b);
  });
  $('#sys-defs').innerHTML = CATS.filter(function(c){ return counts[c[0]]; }).map(function(c){
    return '<div><span class="sw" style="background:' + catColor(c[0]) + '"></span><span><b>' + esc(c[1]) + '</b> — <span>' + esc(c[2]) + '</span></span></div>';
  }).join('');
}
function renderFiles(){
  var q = ($('#fx-q').value || '').trim().toLowerCase(), groups = {}, order = [];
  (MAP.files || []).forEach(function(f){
    if(!catOn[f[2]]) return;
    if(q && [f[0], f[3], f[4], f[6], f[7]].join(' ').toLowerCase().indexOf(q) < 0) return;
    var i = f[0].indexOf('/'), dir = i < 0 ? '/ (root)' : f[0].slice(0, i) + '/';
    if(!groups[dir]){ groups[dir] = []; order.push(dir); }
    groups[dir].push(f);
  });
  order.sort(function(a, b){ return a === '/ (root)' ? -1 : b === '/ (root)' ? 1 : a.localeCompare(b); });
  var html = order.map(function(dir){
    var fs = groups[dir], cc = {};
    fs.forEach(function(f){ cc[f[2]] = (cc[f[2]] || 0) + 1; });
    var bar = CATS.filter(function(c){ return cc[c[0]]; }).map(function(c){ return '<i style="width:' + (cc[c[0]] / fs.length * 100) + '%;background:' + catColor(c[0]) + '"></i>'; }).join('');
    var rows = fs.map(function(f){
      var name = dir === '/ (root)' ? f[0] : f[0].slice(dir.length);
      return '<tr><td class="f">' + esc(name) + '</td><td class="l">' + (f[1] ? f[1].toLocaleString('en-US') : '—') + '</td><td class="s"><span class="st"><i style="background:' + catColor(f[2]) + '"></i>' + esc(CAT_NAME[f[2]] || f[2]) + '</span></td><td class="d" data-i18n-skip>' + (f[4] ? '<code class="sy">' + esc(f[4]) + '</code>' : '') + esc(f[3] || '') + (f[6] ? '<span class="lk">' + (f[5] === 'note' ? '○ ' : '✓ ') + esc(f[7] || '') + '</span>' : '') + '</td></tr>';
    }).join('');
    return '<details class="dir"' + (q ? ' open' : '') + '><summary><span class="n">' + esc(dir) + '</span><span class="c">' + _t('{n} ไฟล์', {n: fs.length}) + '</span><span class="stack sm">' + bar + '</span></summary><table class="files"><tbody>' + rows + '</tbody></table></details>';
  }).join('');
  $('#fx').innerHTML = html || '<p class="muted">ไม่พบไฟล์ที่ตรงกับเงื่อนไข</p>';
}
$('#to-sys-universe').addEventListener('click', function(e){ e.preventDefault(); setView('universe'); Cosmos.setMode('system'); });

/* ════════════════════════════════════════════════════════════════
   NAV
   ════════════════════════════════════════════════════════════════ */
var VIEW_TITLE = { chat:'ปรึกษา', universe:'จักรวาล', tools:'เครื่องมือ', system:'ระบบ' };
var curView = 'chat';
/* ม่านบนจักรวาล: 0 = เห็นเต็ม · 1 = จางลงให้อ่านแชทได้ · 2 = มืดสำหรับหน้าข้อมูล */
function updateVeil(){
  document.body.dataset.veil = curView === 'universe' ? '0' : curView === 'chat' ? ($('#empty').classList.contains('hide') ? '1' : '0') : '2';
}
function setView(v){
  if(!VIEW_TITLE[v]) v = 'chat';
  var prev = curView; curView = v;
  $$('.view').forEach(function(el){ el.classList.toggle('on', el.id === 'view-' + v); });
  $$('.nav [data-view], #tabbar [data-view]').forEach(function(b){ b.classList.toggle('on', b.dataset.view === v); });
  /* ชื่อหน้าเข้ามาแบบการ์ดชื่อฉาก (ตัวห่างแล้วหดเข้า) เมื่อเปลี่ยนหน้าจริง — เลือกแชทเดิมซ้ำไม่กระพริบ */
  var vt = $('#view-title'); vt.textContent = VIEW_TITLE[v];
  if(prev !== v || !vt.classList.contains('cut')){ vt.classList.remove('cut'); void vt.offsetWidth; vt.classList.add('cut'); }
  syncTrace(v);
  if(v === 'system') buildSystem();
  if(v === 'chat') scrollBottom();
  document.body.dataset.view = v;
  updateVeil(); Cosmos.setView(v);
  if(window.KD_galaxy){ if(v === 'universe') KD_galaxy.pause(); else { KD_galaxy.resume(); KD_galaxy.refocus(); } }
}
document.addEventListener('click', function(e){
  // เฉพาะปุ่มเปลี่ยนหน้า — <body> ก็มี data-view (ไว้ให้ CSS) เดิมคลิกตรงไหนก็ตรงกับ body
  // จึงสั่งปิดเมนูทุกครั้ง: ปุ่ม ☰ บนมือถือเปิดเมนูไม่ได้เลย และแชทเลื่อนลงล่างทุกครั้งที่คลิก
  var b = e.target.closest('button[data-view], a[data-view]'); if(!b) return;
  setView(b.dataset.view); closeDrawer();
});
/* ระหว่างรอคำตอบ แสงโคจรรอบช่องพิมพ์ (body.kd-busy) */
addEventListener('KD:thinking', function(e){ document.body.classList.toggle('kd-busy', !!(e.detail && e.detail.on)); });
function openDrawer(){ $('#sidebar').classList.add('open'); $('#scrim').classList.add('on'); }
function closeDrawer(){ $('#sidebar').classList.remove('open'); $('#scrim').classList.remove('on'); }
$('#menu-btn').addEventListener('click', openDrawer);
$('#scrim').addEventListener('click', closeDrawer);
addEventListener('keydown', function(e){ if(e.key === 'Escape') closeDrawer(); });

/* ════════════════════════════════════════════════════════════════
   BOOT
   ════════════════════════════════════════════════════════════════ */
(async function boot(){
  if((MAP.files || []).length) $('#nav-files').textContent = MAP.files.length;
  syncChips(); MyState.chip();
  Chat.load();
  Cosmos.init();
  renderAll();
  var qs = new URLSearchParams(location.search), tab = qs.get('tab');
  setView(VIEW_TITLE[tab] ? tab : 'chat');
  if(qs.get('payment') === 'success') toast('ชำระเงินสำเร็จ — เครดิตจะเข้าหลัง Stripe ยืนยันรายการ', false, 7000);
  if(qs.get('payment') === 'cancel') toast('ยกเลิกการชำระเงินแล้ว', false, 5000);
  if(qs.has('payment') || qs.has('tab') || qs.has('new')) history.replaceState(null, '', location.pathname);
  checkHealth(); setInterval(checkHealth, 60000);
  document.addEventListener('visibilitychange', function(){ if(!document.hidden && Date.now() - Health.at > 60000) checkHealth(); });
  var changed = await refreshMe();
  if(changed){ Chat.load(); renderAll(); }
  await Cloud.pull();
  if(qs.get('new') === '1') Chat.create();
})();
