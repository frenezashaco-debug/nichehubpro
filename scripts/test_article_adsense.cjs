const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const root = path.join(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'analytics.js'), 'utf8');
function test(pathname, existing, readyState, choice, hostname = 'nichehubpro.com') {
  const scripts = [], handlers = {};
  const window = {location: {hostname, pathname}, localStorage: {getItem: () => choice},
    addEventListener: (name, fn) => { handlers[name] = fn; }};
  const document = {readyState, addEventListener() {},
    querySelector: () => existing || scripts.some(s => s.src.includes('adsbygoogle.js')),
    createElement: () => ({}), head: {appendChild: s => scripts.push(s)}};
  // Keep UI mounting out of this unit test; test bootstrap before DOMContentLoaded.
  const boot = source.slice(0, source.indexOf('  function mount()')) + '\n}());';
  vm.runInNewContext(boot, {window, document});
  if (handlers.load) { handlers.load(); handlers.load(); }
  vm.runInNewContext(boot, {window, document});
  const ads = scripts.filter(s => s.src.includes('adsbygoogle.js'));
  assert.equal(ads.length, hostname === 'nichehubpro.com' && pathname.startsWith('/articles/') && !existing ? 1 : 0);
  if (ads.length) { assert.equal(ads[0].crossOrigin, 'anonymous'); assert.equal(ads[0].async, true); }
  for (const call of window.dataLayer || []) {
    if (call[0] === 'consent') assert.notEqual(call[2].ad_storage, 'granted');
  }
  if (choice !== 'granted') assert.equal(scripts.some(s => s.src.includes('googletagmanager')), false);
}
for (const choice of [null, 'denied', 'granted']) {
  for (const ready of ['loading', 'complete']) {
    test('/articles/example.html', false, ready, choice);
    test('/articles/example.html', true, ready, choice);
    test('/', false, ready, choice);
    test('/articles/example.html', false, ready, choice, 'localhost');
  }
}
const articles = fs.readdirSync(path.join(root, 'articles')).filter(f => f.endsWith('.html'));
for (const file of articles) assert.match(fs.readFileSync(path.join(root, 'articles', file), 'utf8'), /src="\/analytics\.js/);
assert.match(fs.readFileSync(path.join(root, 'publisher_v2.py'), 'utf8'), /src="\/analytics\.js/);
console.log(`PASS: ${articles.length} articles + generator share bootstrap; no duplicates, no automatic ad consent, Analytics opt-in preserved.`);
