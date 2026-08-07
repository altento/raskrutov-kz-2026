import { spawnSync } from 'node:child_process';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';

const url = process.argv[2];
if (!url) {
  console.error('Укажите URL: npm run lighthouse:mobile -- https://example.com/page/');
  process.exit(1);
}
const config = JSON.parse(fs.readFileSync('site-standard.config.json', 'utf8'));
const results = [];
for (let i = 1; i <= config.lighthouse.runs; i++) {
  const out = path.join(os.tmpdir(), `raskrutov-lh-${Date.now()}-${i}.json`);
  const run = spawnSync(process.platform === 'win32' ? 'npx.cmd' : 'npx', ['lighthouse', url, '--quiet', '--output=json', `--output-path=${out}`, '--only-categories=performance,accessibility,seo', '--form-factor=mobile', '--screenEmulation.mobile=true'], { stdio: 'inherit' });
  if (run.status !== 0) process.exit(run.status || 1);
  const report = JSON.parse(fs.readFileSync(out, 'utf8'));
  fs.unlinkSync(out);
  results.push({
    performance: Math.round(report.categories.performance.score * 100),
    accessibility: Math.round(report.categories.accessibility.score * 100),
    seo: Math.round(report.categories.seo.score * 100),
    lcp: Math.round(report.audits['largest-contentful-paint'].numericValue),
    cls: report.audits['cumulative-layout-shift'].numericValue,
    tbt: Math.round(report.audits['total-blocking-time'].numericValue)
  });
}
const median = (key) => results.map((r) => r[key]).sort((a,b) => a-b)[Math.floor(results.length / 2)];
console.table(results);
console.log('Медиана:', { performance: median('performance'), accessibility: median('accessibility'), seo: median('seo'), lcp: median('lcp'), cls: median('cls'), tbt: median('tbt') });
const b = config.lighthouse;
const ok = median('performance') >= b.performance * 100 && median('accessibility') >= b.accessibility * 100 && median('seo') >= b.seo * 100 && median('lcp') <= b.lcpMs && median('cls') <= b.cls && median('tbt') <= b.tbtMs;
process.exit(ok ? 0 : 1);
