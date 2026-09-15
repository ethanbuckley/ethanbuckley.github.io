const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { runInNewContext } = require('node:vm');

function mount() {
  const html = readFileSync(join(__dirname, '../vocabulary-growth-demo.html'), 'utf8');
  const script = html.match(/<script>\s*(const DATA = [\s\S]*?)<\/script>/)[1];
  const elements = {};
  const ctx = new Proxy({}, { get: (target, key) => target[key] ?? (() => {}) });
  for (const id of ['cv','age','disp','ageLab','dispLab','readout','legend','btnVocab','btnRatio']) {
    elements[id] = {
      style: {}, attributes: {}, innerHTML: '',
      setAttribute(key, value) { this.attributes[key] = value; },
    };
  }
  elements.cv.getContext = () => ctx;
  elements.cv.parentElement = { clientWidth: 800 };
  runInNewContext(script, {
    document: { getElementById: id => elements[id], documentElement: {}, body: {} },
    getComputedStyle: () => ({ getPropertyValue: () => '#555555' }),
    window: { devicePixelRatio: 1, addEventListener() {} },
    matchMedia: () => ({ addEventListener() {} }),
  });
  return elements;
}

test('the initial slider and chart agree at four years, and a step goes forwards', () => {
  const page = mount();
  assert.equal(page.ageLab.textContent, '4.0 yr');
  page.age.oninput({ target: { value: Number(page.age.value) + 1 } });
  assert.equal(page.ageLab.textContent, '4.1 yr');
  assert.equal(page.age.attributes['aria-valuetext'], '4.1 yr');
  assert.match(page.readout.innerHTML, /4\.1 yr/);
});

test('both views distinguish illustrative chart bands from fitted intervals', () => {
  const page = mount();
  page.disp.oninput({ target: { value: '150' } });
  assert.match(page.readout.innerHTML, /Intervals above are from the fitted model/);
  assert.match(page.readout.innerHTML, /rescaled ×1\.50/);
  page.btnRatio.onclick();
  assert.match(page.readout.innerHTML, /Intervals above are from the fitted model/);
  assert.equal(page.cv.attributes['aria-label'], 'Posterior production ratio with credible bands');
  page.disp.oninput({ target: { value: '100' } });
  assert.doesNotMatch(page.readout.innerHTML, /rescaled/);
});
