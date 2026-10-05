/* KING DIADEM — สลับภาษาหน้าเว็บ (ไทย · English · 日本語)
 * แปลเฉพาะข้อความคงที่ของหน้า (เมนู ปุ่ม ช่องกรอก) ด้วยพจนานุกรม — คำตอบของ LYLA ตอบตามภาษาที่ผู้ใช้พิมพ์อยู่แล้ว
 * ไม่ส่งอะไรไปเซิร์ฟเวอร์ · จำภาษาที่เลือกไว้ในเครื่อง (ถ้าเบราว์เซอร์ไม่ให้เก็บ ก็ใช้ภาษาตามเครื่องแทน) */
(function () {
  'use strict';
  // ไทย → [English, 日本語]
  var D = {
    'เมนู': ['Menu', 'メニュー'], 'แชทใหม่': ['New chat', '新しいチャット'], '＋ แชทใหม่': ['＋ New chat', '＋ 新しいチャット'], 'ค้นหาแชท': ['Search chats', 'チャットを検索'],
    'ปรึกษา': ['Talk', '相談'], 'จักรวาล': ['Universe', '宇宙'], 'เครื่องมือ': ['Tools', 'ツール'], 'ระบบ': ['System', 'システム'],
    'เข้าสู่ระบบ': ['Sign in', 'ログイン'], 'สิ่งที่ LYLA จำไว้จากแชทก่อนๆ': ['What LYLA remembers from earlier chats', 'LYLAが以前のチャットから覚えていること'],
    'ความจำ': ['Memory', 'メモリー'], 'ออก': ['Sign out', 'ログアウト'], 'เปิดเมนู': ['Open menu', 'メニューを開く'],
    '▲ อัปเกรด': ['▲ Upgrade', '▲ アップグレード'], 'เครดิต': ['Credits', 'クレジット'],
    'สถานะ backend (/health)': ['Backend status (/health)', 'バックエンドの状態 (/health)'],
    'สถานะของฉัน → Waterline': ['My state → Waterline', '自分の状態 → Waterline'],
    'ทั่วไป': ['General', '一般'], 'เส้นทาง': ['Route', 'ルート'], 'ผู้ตอบ': ['Responder', '応答者'],
    'สภา 5 เสียง: LYLA · VEGA · PATICCA · TITAN · COSMOS': ['Council of 5: LYLA · VEGA · PATICCA · TITAN · COSMOS', '5人の評議会: LYLA · VEGA · PATICCA · TITAN · COSMOS'],
    'สภา': ['Council', '評議会'], 'เล่ามาได้เลย': ['Tell me what’s going on', '何でも話してください'],
    'ข้อความ': ['Message', 'メッセージ'], 'ส่ง': ['Send', '送信'],
    'จักรวาลการตัดสินใจ': ['Decision universe', '意思決定の宇宙'], 'โหมดจักรวาล': ['Universe mode', '宇宙モード'],
    'การตัดสินใจ': ['Decisions', '意思決定'], 'ยังไม่มีดาว': ['No stars yet', 'まだ星がありません'], 'เริ่มปรึกษา': ['Start talking', '相談を始める'],
    'จำลองทางเลือก': ['Simulate options', '選択肢をシミュレート'], 'Downside First · 30 / 90 วัน': ['Downside First · 30 / 90 days', 'Downside First · 30 / 90日'],
    'สถานการณ์': ['Situation', '状況'],
    'เช่น ลังเลว่าจะลาออกไปเปิดร้านไหม · เงินเก็บ 300,000 · เงินเดือน 25,000 · รายจ่าย 18,000':
      ['e.g. Thinking of quitting to open a shop · savings 300,000 · salary 25,000 · expenses 18,000',
       '例: 仕事を辞めて店を開くか迷っている · 貯金 300,000 · 月給 25,000 · 支出 18,000'],
    'ทางเลือกที่มี': ['Your options', 'あなたの選択肢'], '+ เพิ่มทางเลือก': ['+ Add option', '+ 選択肢を追加'], 'จำลอง': ['Simulate', 'シミュレート'],
    'วิเคราะห์ภาพ': ['Analyze image', '画像を分析'], 'แตะเพื่อเลือกภาพ': ['Tap to choose an image', 'タップして画像を選択'],
    'วิเคราะห์ภาพนี้': ['Analyze this image', 'この画像を分析'], 'แพ็กเกจ': ['Plans', 'プラン'], 'เติมเครดิต →': ['Top up credits →', 'クレジットを追加 →'],
    'อีเมล': ['Email', 'メール'], 'พื้นฐาน': ['Basic', 'ベーシック'], '+10 เครดิตต่อรอบบิล': ['+10 credits per billing cycle', '請求ごとに +10 クレジット'],
    'อารยธรรม': ['Civilization', 'シビライゼーション'], '+100 เครดิตต่อรอบบิล': ['+100 credits per billing cycle', '請求ごとに +100 クレジット'],
    'ไปหน้าชำระเงิน': ['Go to checkout', 'お支払いへ進む'], 'ระบบจริง': ['Live system', '稼働中のシステム'], 'จักรวาล →': ['Universe →', '宇宙 →'],
    'หนึ่งข้อความ': ['One message', '1つのメッセージ'], 'เซิร์ฟเวอร์': ['Server', 'サーバー'], 'กำลังโหลด…': ['Loading…', '読み込み中…'],
    'ไฟล์': ['Files', 'ファイル'], 'ค้นหา': ['Search', '検索'], 'ค้นหาไฟล์': ['Search files', 'ファイルを検索'],
    'สมการของคำตอบ': ['Equation behind the answer', '回答の数式'], 'แท็บ': ['Tabs', 'タブ'],
    'สิ่งที่ LYLA จำไว้': ['What LYLA remembers', 'LYLAが覚えていること'], 'ปิด': ['Close', '閉じる'],
    'LYLA จำเรื่องสำคัญจากแชทก่อนๆ เพื่อคุยต่อได้ไม่ต้องเล่าใหม่ · เรื่องเปราะบางจะจำแค่ว่าเคยผ่านช่วงหนัก ไม่เก็บข้อความ · ปิดหรือล้างได้ทุกเมื่อ':
      ['LYLA remembers important things from earlier chats so you don’t have to repeat yourself · for sensitive topics it only remembers that you went through a hard time, never the words · turn off or clear any time',
       'LYLAは以前のチャットの大切なことを覚えているので、同じ話を繰り返す必要はありません · つらい話は「大変な時期があった」ことだけを覚え、内容は保存しません · いつでもオフ・消去できます'],
    'ให้ LYLA จำเรื่องจากแชทก่อนๆ': ['Let LYLA remember earlier chats', 'LYLAに以前のチャットを覚えさせる'],
    'ล้างความจำทั้งหมด': ['Clear all memory', 'メモリーをすべて消去'], 'สถานะของฉัน': ['My state', '自分の状態'],
    'พลังงาน ·': ['Energy ·', 'エネルギー ·'], 'นอนเมื่อคืน (ชั่วโมง)': ['Sleep last night (hours)', '昨夜の睡眠（時間）'],
    'อยู่ในภาวะนี้มากี่วัน': ['Days in this situation', 'この状態が続いている日数'], 'จิตใจ': ['Mind', '心の状態'],
    'ปกติ': ['Okay', '普通'], 'เครียด': ['Stressed', 'ストレス'], 'ท่วมท้น รับไม่ไหว': ['Overwhelmed', 'もう限界'],
    'เงินที่ใช้ได้ตอนนี้ (บาท)': ['Money available now (THB)', '今使えるお金（バーツ）'], 'ไม่ระบุ': ['Not specified', '未指定'],
    'มีอาหารกินไหม': ['Do you have food?', '食べ物はありますか？'], 'มี': ['Yes', 'ある'], 'ไม่มี': ['No', 'ない'],
    'มีที่อยู่ที่ปลอดภัยไหม': ['Do you have a safe place to stay?', '安全な居場所はありますか？'],
    'ล้าง': ['Clear', 'クリア'], 'ใช้': ['Apply', '適用'], 'ฟรี / วัน': ['Free / day', '無料 / 日'], 'ต่อข้อความ': ['per message', '1メッセージあたり'],
    'เติมเครดิต': ['Top up credits', 'クレジットを追加'], 'สมการ': ['Equation', '数式'],
    'ระบบนี้ไม่ต้องการผู้สร้างเพื่อดำรงอยู่': ['This system does not need its creator to exist', 'このシステムは存在するために作者を必要としない'],
    'ไม่ต้องมีนิธิกร บุญสร้างจึงจะใช้งานได้': ['It works without Nithikorn Boonsang', 'ニティコーン・ブンサーンがいなくても動く'],
    'เพราะอิสรภาพไม่ขึ้นกับตัวตน': ['because freedom does not depend on identity', '自由は個人に依存しないから'],
    'และความเมตตาไม่ขึ้นกับกาลเวลา': ['and compassion does not depend on time', 'そして慈悲は時に依存しないから'],
    'ความสมบูรณ์ไม่เคยมีจริง': ['Perfection never truly existed', '完全さは本当には存在しなかった'],
    'จักรวาลไม่เคยมอบมัน': ['the universe never granted it', '宇宙はそれを与えなかった'],
    'ระบบนี้ไม่อ้างความสมบูรณ์': ['This system does not claim perfection', 'このシステムは完全さを主張しない'],
    'ไม่สัญญาความถูกต้องสุดท้าย': ['promises no final correctness', '最終的な正しさを約束しない'],
    'และไม่ปิดความเป็นไปได้ของการเรียนรู้': ['and never closes the possibility of learning', 'そして学ぶ可能性を決して閉ざさない']
  };
  var LANGS = ['th', 'en', 'ja'], KEY = 'kd_lang', ATTRS = ['title', 'placeholder', 'aria-label', 'alt'];
  var REV = {};                                 // ข้อความที่แปลแล้ว → ไทย (สลับกลับได้โดยไม่ต้องโหลดหน้าใหม่)
  Object.keys(D).forEach(function (th) { REV[D[th][0]] = th; REV[D[th][1]] = th; });

  function pick() {
    try { var s = localStorage.getItem(KEY); if (LANGS.indexOf(s) >= 0) return s; } catch (e) {}
    var n = String((navigator.languages && navigator.languages[0]) || navigator.language || 'th').toLowerCase();
    return n.indexOf('th') === 0 ? 'th' : n.indexOf('ja') === 0 ? 'ja' : 'en';
  }
  function tr(s, lang) {
    var key = s.trim(), th = D[key] ? key : REV[key];
    if (!th) return null;
    var out = lang === 'th' ? th : D[th][lang === 'en' ? 0 : 1];
    return out === key ? null : s.replace(key, out);
  }
  function apply(root, lang) {
    if (!root || root.nodeType !== 1) return;
    if (root.closest && root.closest('script,style,.m,.bubble,#sim-out,[data-i18n-skip]')) return;   // ไม่แตะข้อความแชท
    var w = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (n) {
        var p = n.parentNode;
        return p && p.closest && p.closest('script,style,.m,.bubble,#sim-out,[data-i18n-skip]') ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
      }
    });
    var n, todo = [];
    while ((n = w.nextNode())) todo.push(n);
    todo.forEach(function (t) { var v = tr(t.nodeValue, lang); if (v !== null) t.nodeValue = v; });
    [root].concat([].slice.call(root.querySelectorAll('[' + ATTRS.join('],[') + ']'))).forEach(function (el) {
      ATTRS.forEach(function (a) { if (el.hasAttribute && el.hasAttribute(a)) { var v = tr(el.getAttribute(a), lang); if (v !== null) el.setAttribute(a, v); } });
    });
  }
  var current = pick();
  function set(lang) {
    if (LANGS.indexOf(lang) < 0) return;
    current = lang;
    try { localStorage.setItem(KEY, lang); } catch (e) {}
    document.documentElement.lang = lang;
    apply(document.body, lang);
    var sel = document.getElementById('lang-pick');
    if (sel) sel.value = lang;
  }
  window.KD_I18N = { set: set, get: function () { return current; }, t: function (s) { return tr(s, current) || s; }, dict: D };

  function boot() {
    var sel = document.getElementById('lang-pick');
    if (sel) sel.addEventListener('change', function () { set(sel.value); });
    set(current);
    // ส่วนที่สคริปต์เพิ่มทีหลัง (เมนู ป๊อปอัป) ก็แปลด้วย
    if (window.MutationObserver) new MutationObserver(function (ms) {
      if (current === 'th') return;
      ms.forEach(function (m) { [].forEach.call(m.addedNodes, function (x) { apply(x.nodeType === 1 ? x : x.parentNode, current); }); });
    }).observe(document.body, { childList: true, subtree: true });
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot); else boot();
})();
