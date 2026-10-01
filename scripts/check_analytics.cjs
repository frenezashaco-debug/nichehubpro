const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const source = fs.readFileSync(require('node:path').join(__dirname, '../analytics.js'), 'utf8');
function run(disabled) {
  const appended = [];
  const window = disabled ? { 'ga-disable-G-PHY346X94N': true } : {};
  window.location = { hostname: 'nichehubpro.com' };
  const context = vm.createContext({ window, document: {
    createElement: () => ({}), head: { appendChild: node => appended.push(node) }
  }});
  vm.runInContext(source, context);
  vm.runInContext(source, context);
  if (disabled) {
    assert.equal(appended.length, 0);
    assert.equal(window.dataLayer, undefined);
  } else {
    assert.equal(appended.length, 1);
    assert.equal(appended[0].async, true);
    assert.equal(appended[0].src, 'https://www.googletagmanager.com/gtag/js?id=G-PHY346X94N');
    assert.equal(window.dataLayer.filter(x => x[0] === 'config').length, 1);
    assert.equal(window.dataLayer[1][1], 'G-PHY346X94N');
  }
}
run(false);
run(true);
console.log('PASS: single Analytics initialization and existing opt-out respected.');
