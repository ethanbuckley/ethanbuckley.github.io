const { test } = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { join } = require('node:path');
const { runInNewContext } = require('node:vm');

const source = readFileSync(join(__dirname, '../assets/theme.js'), 'utf8');

function mount({ saved = null, systemDark = false, storageBlocked = false } = {}) {
  const attributes = new Map();
  const clicks = {};
  const listeners = {};
  const events = [];
  const root = {
    getAttribute: key => attributes.get(key) ?? null,
    setAttribute: (key, value) => attributes.set(key, value),
    removeAttribute: key => attributes.delete(key),
  };
  const button = { setAttribute() {}, addEventListener: (type, fn) => { clicks[type] = fn; } };
  const media = { matches: systemDark, addEventListener: (_, fn) => { media.change = fn; } };
  runInNewContext(source, {
    document: { documentElement: root, readyState: 'complete', getElementById: () => button },
    localStorage: {
      getItem() { if (storageBlocked) throw new Error('Storage unavailable'); return saved; },
      setItem(_, value) { if (storageBlocked) throw new Error('Storage unavailable'); saved = value; },
    },
    window: {
      matchMedia: () => media,
      dispatchEvent: event => events.push(event.type),
      addEventListener: (type, fn) => { listeners[type] = fn; },
    },
    Event: class { constructor(type) { this.type = type; } },
  });
  return {
    root, button, media, events, click: () => clicks.click(),
    sync(value) { saved = value; listeners.storage({ key: 'theme' }); },
  };
}

test('follows the system until a saved preference is available', () => {
  assert.equal(mount({ systemDark: true }).button.textContent, 'Light mode');
  const page = mount({ systemDark: true, saved: 'light' });
  assert.equal(page.root.getAttribute('data-theme'), 'light');
  assert.equal(page.button.textContent, 'Dark mode');
});

test('switches in both directions when localStorage throws', () => {
  const page = mount({ storageBlocked: true });
  page.click();
  assert.equal(page.root.getAttribute('data-theme'), 'dark');
  assert.equal(page.button.textContent, 'Light mode');
  page.click();
  assert.equal(page.root.getAttribute('data-theme'), 'light');
  assert.equal(page.button.textContent, 'Dark mode');
  assert.deepEqual(page.events, ['themechange', 'resize', 'themechange', 'resize']);
});

test('system changes notify the canvas and update the button', () => {
  const page = mount();
  page.media.matches = true;
  page.media.change();
  assert.equal(page.button.textContent, 'Light mode');
  assert.deepEqual(page.events, ['themechange', 'resize']);
});

test('an explicit choice survives a system theme change', () => {
  const page = mount({ saved: 'light' });
  page.media.matches = true;
  page.media.change();
  assert.equal(page.root.getAttribute('data-theme'), 'light');
  assert.equal(page.button.textContent, 'Dark mode');
});

test('a change in another tab synchronises the theme, including removal', () => {
  const page = mount();
  page.sync('dark');
  assert.equal(page.root.getAttribute('data-theme'), 'dark');
  assert.equal(page.button.textContent, 'Light mode');
  page.sync(null);
  assert.equal(page.root.getAttribute('data-theme'), null);
  assert.equal(page.button.textContent, 'Dark mode');
});
