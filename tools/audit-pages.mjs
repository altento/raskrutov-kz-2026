import fs from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const config = JSON.parse(fs.readFileSync(path.join(root, 'site-standard.config.json'), 'utf8'));
const excluded = new Set(config.excludeDirs);
const files = [];
const walk = (dir) => {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (excluded.has(entry.name)) continue;
    const absolute = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(absolute);
    else if (entry.isFile() && entry.name.toLowerCase().endsWith('.html')) files.push(path.relative(root, absolute));
  }
};
walk(root);
const errors = [];
const warnings = [];

const attr = (tag, name) => new RegExp(`\\b${name}\\s*=\\s*["'][^"']+["']`, 'i').test(tag);
const count = (text, re) => (text.match(re) || []).length;

for (const file of files) {
  const html = fs.readFileSync(path.join(root, file), 'utf8');
  const fail = (m) => errors.push(`${file}: ${m}`);
  const warn = (m) => warnings.push(`${file}: ${m}`);
  if (!/<html\b[^>]*\blang=/i.test(html)) fail('нет lang у html');
  if (count(html, /<h1\b/gi) !== 1) fail('должен быть ровно один H1');
  if (!/<title>[^<]{8,}<\/title>/is.test(html)) fail('нет содержательного title');
  if (!/<meta\b[^>]*name=["']description["'][^>]*content=["'][^"']{30,}["']/i.test(html) && !/<meta\b[^>]*content=["'][^"']{30,}["'][^>]*name=["']description["']/i.test(html)) fail('нет содержательного meta description');
  if (!/<link\b[^>]*rel=["']canonical["'][^>]*href=["']https?:\/\//i.test(html) && !/<link\b[^>]*href=["']https?:\/\/[^"']+["'][^>]*rel=["']canonical["']/i.test(html)) fail('нет абсолютного canonical');
  const imgs = html.match(/<img\b[^>]*>/gi) || [];
  imgs.forEach((tag, i) => {
    if (!/\balt\s*=\s*["'][^"']*["']/i.test(tag)) fail(`img #${i + 1} без alt`);
    if (!(attr(tag, 'width') && attr(tag, 'height')) && !attr(tag, 'style')) warn(`img #${i + 1}: проверь размеры/аспект`);
  });
  const highs = imgs.filter((tag) => /fetchpriority\s*=\s*["']high["']/i.test(tag));
  if (highs.length > config.limits.maxHighPriorityImages) fail(`fetchpriority=high указан ${highs.length} раз`);
  const forms = html.match(/<form\b[\s\S]*?<\/form>/gi) || [];
  forms.forEach((form, fi) => {
    const controls = form.match(/<(input|select|textarea)\b[^>]*>/gi) || [];
    controls.filter((t) => !/type\s*=\s*["'](?:submit|button|hidden)["']/i.test(t)).forEach((tag, ci) => {
      if (!attr(tag, 'name')) fail(`форма #${fi + 1}, поле #${ci + 1} без name`);
      if (/^<input/i.test(tag) && !attr(tag, 'type')) fail(`форма #${fi + 1}, input #${ci + 1} без type`);
    });
  });
}

if (!files.length) errors.push('HTML-файлы не найдены; проверьте запуск из корня проекта');
warnings.forEach((m) => console.warn(`WARN ${m}`));
errors.forEach((m) => console.error(`ERROR ${m}`));
console.log(`Проверено HTML-файлов: ${files.length}; ошибок: ${errors.length}; предупреждений: ${warnings.length}`);
process.exit(errors.length ? 1 : 0);
