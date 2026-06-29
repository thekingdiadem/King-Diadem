/* ============================================================
   KING DIADEM — static/app.js v3.1
   ★ PATCH v3.1: ลบ simulate() และ addSimPath() ออก
     เพราะ index.html มี version ที่ถูกต้องอยู่แล้ว
     (อ่านจาก #sim-input-text)
   ★ LYLA◈/VEGA◆ จาก backend · memory sync /api/chat-state
   ============================================================ */
'use strict';

/* ── Conversation history ───────────────────────────────────── */
const _convHistory = {};
let _memorySyncTimer = null;

function _activeSessionId() {
  try {
    const s = JSON.parse(localStorage.getItem('kd_sessions_v1') || '{}');
    return s.active || 'default';
  } catch (_) { return 'default'; }
}
function _getHistory(sid) {
  if (!_convHistory[sid]) _convHistory[sid] = [];
  return _convHistory[sid];
}
function _pushHistory(sid, role, content) {
  const h = _getHistory(sid);
  h.push({ role, content: String(content) });
  if (h.length > 40) h.splice(0, h.length - 40);
  _scheduleMemorySync(sid);
}

/* ── Memory persistence ─────────────────────────────────────── */
function _scheduleMemorySync(sid) {
  clearTimeout(_memorySyncTimer);
  _memorySyncTimer = setTimeout(() => _syncMemory(sid), 1500);
}
async function _syncMemory(sid) {
  try {
    await fetch('/api/chat-state', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ session_id: sid, history: _getHistory(sid) })
    });
  } catch (_) {}
}
async function _loadMemory() {
  try {
    const r = await fetch('/api/chat-state');
    const d = await r.json();
    if (d.state && d.state.history) {
      const sid = _activeSessionId();
      _convHistory[sid] = d.state.history;
    }
  } catch (_) {}
}

/* ── Tone detection ─────────────────────────────────────────── */
const _CRISIS_KW = ['ฆ่าตัวตาย','อยากตาย','สิ้นหวัง','ทนไม่ไหว','หมดหวัง','จบชีวิต','เลิกมีชีวิต','crisis','suicid','hopeless'];
const _VEGA_KW   = ['เจ็บปวด','เสียใจ','ร้องไห้','กลัว','เหงา','โดดเดี่ยว','ทรมาน','hurt','pain','scared','lonely','heartbreak'];

window.detectConversationMode = function(text) {
  const t = text.toLowerCase();
  if (_CRISIS_KW.some(k => t.includes(k))) return 'crisis';
  if (_VEGA_KW.some(k => t.includes(k)))   return 'vega';
  return 'lyla';
};
window.buildVoiceHint = function(text, mode) {
  if (mode === 'crisis') return 'ผู้ใช้อาจอยู่ในภาวะวิกฤต ให้ความห่วงใยและข้อมูลความปลอดภัยก่อน';
  if (mode === 'vega')   return 'ผู้ใช้แสดงอารมณ์ ให้รับฟังและเห็นอกเห็นใจก่อนให้ข้อมูล';
  return 'โหมดสังเกตการณ์ — วิเคราะห์และเปิดทางเลือก';
};

/* ── UI helpers ─────────────────────────────────────────────── */
function autoResize(el) {
  el.style.height = 'auto';
  el.style.height = Math.min(el.scrollHeight, 120) + 'px';
}
function escH(t) {
  return String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}
function hideWelcome() {
  const w = document.getElementById('welcome');
  if (w) w.remove();
}

/* ── addMsg ─────────────────────────────────────────────────── */
function addMsg(type, text, meta, persona) {
  hideWelcome();
  const area = document.getElementById('chat-scroll');
  if (!area) return;
  const div = document.createElement('div');
  div.className = 'msg ' + type;

  const av = type === 'user'
    ? '<div class="msg-avatar">YOU</div>'
    : '<div class="msg-avatar"><img class="msg-logo" src="/static/logo.png" alt=""></div>';

  let sigHtml = '';
  if (type !== 'user' && persona) {
    const isVega = persona === 'VEGA';
    sigHtml = `<span class="msg-persona ${isVega?'vega':'lyla'}">${isVega?'— VEGA ◆':'— LYLA ◈'}</span>`;
  }

  const html = escH(text)
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\n/g, '<br>');

  div.innerHTML = av +
    '<div class="msg-body">' +
      '<div class="msg-text">' + html + '</div>' +
      sigHtml +
      (meta ? '<div class="route-tag">' + escH(meta) + '</div>' : '') +
    '</div>';

  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
  if (typeof persistActiveChatHtml === 'function') persistActiveChatHtml();
}

function addThinking() {
  hideWelcome();
  const area = document.getElementById('chat-scroll');
  if (!area) return;
  const div = document.createElement('div');
  div.className = 'msg system'; div.id = 'thinking-msg';
  div.innerHTML =
    '<div class="msg-avatar"><img class="msg-logo" src="/static/logo.png" alt=""></div>' +
    '<div class="msg-body"><div class="msg-text"><div class="thinking"><span></span><span></span><span></span></div></div></div>';
  area.appendChild(div);
  area.scrollTop = area.scrollHeight;
}
function removeThinking() {
  const el = document.getElementById('thinking-msg');
  if (el) el.remove();
}

/* ── LYLA meters ─────────────────────────────────────────────── */
function updateLyla(data) {
  const pat = data.pattern || {};
  const e = +pat.entropy||40, s = +pat.stability||60, r = +pat.resource||50;
  uM('wl-entropy',e,true); uM('wl-stability',s,false); uM('wl-resource',r,false);
  const ev=document.getElementById('wl-entropy-val'),sv=document.getElementById('wl-stability-val'),rv=document.getElementById('wl-resource-val');
  if(ev)ev.textContent=e.toFixed(0); if(sv)sv.textContent=s.toFixed(0); if(rv)rv.textContent=r.toFixed(0);
  const lc=document.getElementById('lyla-choices'); if(lc)lc.textContent=(data.risk_score>75)?'LOW':'≥1';
  const ld=document.getElementById('lyla-drift'); if(ld)ld.textContent=((e/100)*0.1).toFixed(2)+'%';
}
function uM(id,val,inv) {
  const f=document.getElementById(id); if(!f)return;
  const p=Math.max(0,Math.min(100,val)); f.style.width=p+'%';
  const bad=inv?p>72:p<28,mid=inv?p>48:p<48;f.className='wl-fill '+(bad?'crit':mid?'warn':'safe');
}

/* ── Route ───────────────────────────────────────────────────── */
window._KD_ROUTE = 'general';
function setRoute(r) {
  window._KD_ROUTE = r;
  document.querySelectorAll('.route-chip').forEach(b=>b.classList.toggle('active',b.dataset.r===r));
  document.querySelectorAll('.ctx-tag').forEach(t=>t.classList.toggle('active',t.dataset.r===r));
}

/* ── Hint chips ──────────────────────────────────────────────── */
function useHint(el) {
  const inp=document.getElementById('main-input');
  inp.value=el.textContent; autoResize(inp); inp.focus();
  if(typeof setTab==='function')setTab('chat');
  if(typeof closeRailMobile==='function')closeRailMobile();
}

/* ── Main send ──────────────────────────────────────────────── */
async function run() {
  const inp  = document.getElementById('main-input');
  const text = (inp.value||'').trim();
  if (!text) return;

  const sid       = _activeSessionId();
  const mode      = window.detectConversationMode(text);
  const voiceHint = window.buildVoiceHint(text, mode);

  const tp = document.getElementById('tone-pill');
  if (tp) { tp.textContent = mode.toUpperCase(); tp.className = 'tone-pill ' + mode; }

  addMsg('user', text);
  if (typeof maybeRenameSessionFromMessage==='function') maybeRenameSessionFromMessage(text);
  inp.value=''; inp.style.height='auto';
  const btn = document.getElementById('run-btn');
  if (btn) btn.disabled = true;
  addThinking();

  const historySnapshot = [..._getHistory(sid)];
  _pushHistory(sid, 'user', text);

  try {
    const res = await fetch('/run', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        input:      text,
        route:      window._KD_ROUTE,
        voice_mode: mode,
        voice_hint: voiceHint,
        history:    historySnapshot,
        context: { client_voice: mode, tone_notes: voiceHint, route_ui: window._KD_ROUTE }
      })
    });

    let data;
    try { data = await res.json(); }
    catch (_) { throw new Error('เซิร์ฟเวอร์ตอบไม่ใช่ JSON (อาจ timeout หรือ 502)'); }

    removeThinking();
    if (data.error) { addMsg('system','⚠ '+data.error,'ERROR'); return; }

    const reply   = data.ai_response || data.message || JSON.stringify(data,null,2);
    const persona = data.persona || (mode==='vega'?'VEGA':'LYLA');
    const risk    = data.risk_score!=null?' · RISK '+Math.round(data.risk_score):'';
    const meta    = 'ROUTE '+(data.route||window._KD_ROUTE).toUpperCase()+risk;

    _pushHistory(sid, 'assistant', reply);
    addMsg('system', reply, meta, persona);

    updateLyla(data);
    if (typeof refreshMe==='function') refreshMe();

    try {
      const intent=(data.governance&&data.governance.intent)||{};
      const pat=data.pattern||{};
      if (typeof window.KD_pulse==='function') window.KD_pulse(data.route||'general');
      window.dispatchEvent(new CustomEvent('KD:response',{detail:{
        output:   {action:data.route||'observe',confidence:intent.confidence,risk:data.risk_score},
        consensus:{final_action:data.route||'observe',confidence:intent.confidence},
        risk:     {risk_score:data.risk_score},
        council:  {votes:[
          {member:'LYLA',role:'waterline',action:String(data.route||'observe'),score:Math.round(data.risk_score||0)},
          {member:'VEGA',role:mode==='crisis'?'safety':'empathy',action:mode,score:Math.round(pat.entropy||40)}
        ],score:data.risk_score}
      }}));
    } catch(_) {}

  } catch(e) {
    removeThinking();
    addMsg('system','🔴 เครือข่าย: '+e.message,'ERROR');
  } finally {
    if (btn) btn.disabled=false;
    if (typeof persistActiveChatHtml==='function') persistActiveChatHtml();
  }
}

/* ── Stripe ──────────────────────────────────────────────────── */
async function stripeCheckout() {
  const email=(document.getElementById('payment-email').value||'').trim();
  const plan=document.querySelector('input[name="plan"]:checked')?.value||'basic';
  const d=await _post('/payment/create-checkout',{plan,email,api_key:email});
  if(d.url)location.href=d.url; else alert(d.error||'Stripe ไม่สำเร็จ');
}

/* ── Image ───────────────────────────────────────────────────── */
async function uploadImage() {
  const fi=document.getElementById('photo-file'),out=document.getElementById('photo-output');
  if(!fi.files.length){out.textContent='เลือกภาพก่อน';return;}
  const fd=new FormData(); fd.append('file',fi.files[0]); out.textContent='กำลังวิเคราะห์…';
  try {
    const res=await fetch('/analyze-image',{method:'POST',body:fd});
    const data=await res.json();
    if(data.error){out.textContent='❌ '+data.error;return;}
    out.textContent=(data.analysis||'')+'\n\n['+(data.persona||'')+'] ['+(data.filename||'')+']';
  } catch(e){out.textContent='ERROR '+e;}
}

/* ── Fetch helper ────────────────────────────────────────────── */
async function _post(url,body) {
  try {
    const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    return await r.json();
  } catch(e){return{error:String(e)};}
}

/* ── Init ────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function() {
  _loadMemory();
});

/* ── Expose globals ──────────────────────────────────────────── */
window.run=run; window.setRoute=setRoute; window.useHint=useHint;
window.stripeCheckout=stripeCheckout; window.uploadImage=uploadImage;
window.autoResize=autoResize; window.addMsg=addMsg; window.updateLyla=updateLyla;

/* NOTE: simulate() และ addSimPath() ถูกลบออกจากไฟล์นี้แล้ว
   ใช้ version ใน index.html แทน ซึ่งอ่านจาก #sim-input-text ถูกต้อง */
