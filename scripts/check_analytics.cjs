const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(require('node:path').join(__dirname, '../analytics.js'), 'utf8');
function run(disabled, saved, blockedStorage = false) {
  const appended = [];
  const window = disabled ? { 'ga-disable-G-PHY346X94N': true } : {};
  window.location = { hostname: 'nichehubpro.com' };
  window.localStorage = { getItem() { if (blockedStorage) throw Error('blocked'); return saved; }, setItem() { if (blockedStorage) throw Error('blocked'); } };
  const elements = [];
  function element() {
    const el = { style: {}, children: [], setAttribute() {}, appendChild(node) { this.children.push(node); },
      addEventListener(name, callback) { this[name] = callback; }, focus() {} };
    elements.push(el); return el;
  }
  const context = vm.createContext({ window, document: {
    readyState: 'complete', body: element(), createElement: element, head: { appendChild: node => appended.push(node) }
  }});
  vm.runInContext(source, context);
  vm.runInContext(source, context);
  assert.equal(window.dataLayer[0][0], 'consent');
  assert.equal(window.dataLayer[0][2].analytics_storage, 'denied');
  if (disabled || saved !== 'granted') {
    assert.equal(appended.length, 0);
  } else {
    assert.equal(appended.length, 1);
    assert.equal(appended[0].async, true);
    assert.equal(appended[0].src, 'https://www.googletagmanager.com/gtag/js?id=G-PHY346X94N');
    assert.equal(window.dataLayer.filter(x => x[0] === 'config').length, 1);
  }
  const allow = elements.find(el => el.textContent === 'Allow analytics');
  const decline = elements.find(el => el.textContent === 'Decline analytics');
  allow.click(); allow.click();
  assert.equal(appended.length, disabled ? 0 : 1);
  decline.click();
  assert.equal(window['ga-disable-G-PHY346X94N'], true);
  assert.equal(window.dataLayer.at(-1)[2].analytics_storage, 'denied');
}
run(false, null);
run(false, 'denied');
run(false, 'granted');
run(true, 'granted');
run(false, null, true);
console.log('PASS: no tracking before choice, grant, decline, opt-out, blocked storage and duplicate initialization.');
