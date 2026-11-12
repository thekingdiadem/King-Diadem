// สร้าง static/hero.jpg (2560×1440) และ static/hero_m.jpg (1280×720) จาก scripts/hero/scene.html
// ใช้:  node scripts/hero/build.js   (ต้องมี Playwright + Chromium)
const { chromium } = require('playwright'); const path = require('path');
(async () => {
  const b = await chromium.launch();
  for (const [file, scale, q] of [['hero.jpg', 1, 82], ['hero_m.jpg', .5, 80]]) {
    const p = await b.newPage({ viewport: { width: 2560 * scale, height: 1440 * scale }, deviceScaleFactor: 1 });
    await p.goto('file://' + path.join(__dirname, 'scene.html'));
    await p.evaluate(s => { document.getElementById('s').style.cssText += ';transform-origin:0 0;transform:scale(' + s + ')'; }, scale);
    await p.waitForTimeout(1500);
    await p.screenshot({ path: path.join(__dirname, '..', '..', 'static', file), type: 'jpeg', quality: q });
    await p.close();
  }
  await b.close();
})();
