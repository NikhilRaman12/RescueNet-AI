import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import test from 'node:test';

const page = readFileSync(new URL('../ready-at-home.html', import.meta.url), 'utf8');
const entry = readFileSync(new URL('../src/readyathome-main.tsx', import.meta.url), 'utf8');

test('ReadyAtHome page loads its React mount entry point', () => {
  assert.match(page, /src="\/src\/readyathome-main\.tsx"/);
});

test('ReadyAtHome entry mounts the component into the page root', () => {
  assert.match(entry, /createRoot\(rootElement\)\.render\(/);
  assert.match(entry, /<ReadyAtHome\s*\/>/);
});
