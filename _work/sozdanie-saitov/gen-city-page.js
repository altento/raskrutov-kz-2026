/**
 * Generate regional sozdanie-saitov city page from parent template.
 * Usage: node gen-city-page.js <slug|--all>
 * Reads: cities-batch1.json + cities-remaining.json, parent index.html
 * Writes: web-studiya/sozdanie-saitov/<slug>/index.html
 */
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "../..");
const PARENT = path.join(ROOT, "web-studiya/sozdanie-saitov/index.html");
const CITY_FILES = ["cities-batch1.json", "cities-remaining.json"];
const CITIES = Object.assign(
  {},
  ...CITY_FILES.map((f) => {
    const p = path.join(__dirname, f);
    if (!fs.existsSync(p)) return {};
    return JSON.parse(fs.readFileSync(p, "utf8"));
  })
);

const arg = process.argv[2];
const slugs =
  arg === "--all"
    ? Object.keys(CITIES)
    : arg && CITIES[arg]
      ? [arg]
      : null;
if (!slugs) {
  console.error(
    "Usage: node gen-city-page.js <" +
      Object.keys(CITIES).join("|") +
      "|--all>"
  );
  process.exit(1);
}

function generate(slug) {

const city = CITIES[slug];
let html = fs.readFileSync(PARENT, "utf8");

// Path depth: city is one level deeper
html = html.replace(/\.\.\/\.\.\//g, "../../../");

const baseUrl = `https://raskrutov.kz/web-studiya/sozdanie-saitov/${slug}/`;
const parentUrl = "https://raskrutov.kz/web-studiya/sozdanie-saitov/";

function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function faqHtml(faq) {
  return faq
    .map(
      (item) =>
        `<details><summary><h3 class="sz-faq__q">${esc(item.q)}</h3></summary><div class="sz-faq__a">${esc(item.a)}</div></details>`
    )
    .join("\n          ");
}

function faqJsonLd(faq) {
  return faq.map((item) => ({
    "@type": "Question",
    name: item.q,
    acceptedAnswer: { "@type": "Answer", text: item.a },
  }));
}

function pillarsHtml(pillars) {
  return pillars
    .map(
      (p) =>
        `<article class="sz-why__pillar"><h3 class="sz-why__pillar-title">${esc(p.title)}</h3><p class="sz-why__pillar-text">${esc(p.text)}</p></article>`
    )
    .join("\n          ");
}

// --- Head meta ---
html = html.replace(
  /<title>[\s\S]*?<\/title>/,
  `<title>${esc(city.title)}</title>`
);
html = html.replace(
  /<meta name="description" content="[^"]*">/,
  `<meta name="description" content="${esc(city.description)}">`
);
html = html.replace(
  /<link rel="canonical" href="[^"]*">/,
  `<link rel="canonical" href="${baseUrl}">`
);
html = html.replace(
  /<meta property="og:title" content="[^"]*">/,
  `<meta property="og:title" content="${esc(city.title)}">`
);
html = html.replace(
  /<meta property="og:description" content="[^"]*">/,
  `<meta property="og:description" content="${esc(city.description)}">`
);
html = html.replace(
  /<meta property="og:url" content="[^"]*">/,
  `<meta property="og:url" content="${baseUrl}">`
);

// --- JSON-LD (replace whole script block) ---
const graph = {
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "https://raskrutov.kz/#organization",
      name: "Raskrutov",
      url: "https://raskrutov.kz/",
      telephone: "+77000216900",
      email: "info@raskrutov.kz",
    },
    {
      "@type": "WebSite",
      "@id": "https://raskrutov.kz/#website",
      url: "https://raskrutov.kz/",
      name: "Raskrutov",
    },
    {
      "@type": "WebPage",
      url: baseUrl,
      name: city.title,
      isPartOf: { "@id": "https://raskrutov.kz/#website" },
    },
    {
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "Главная", item: "https://raskrutov.kz/" },
        { "@type": "ListItem", position: 2, name: "Студия", item: "https://raskrutov.kz/web-studiya/" },
        { "@type": "ListItem", position: 3, name: "Создание сайтов", item: parentUrl },
        { "@type": "ListItem", position: 4, name: city.name, item: baseUrl },
      ],
    },
    {
      "@type": "Service",
      name: city.h1,
      provider: { "@id": "https://raskrutov.kz/#organization" },
      areaServed: { "@type": "City", name: city.name },
    },
    {
      "@type": "FAQPage",
      mainEntity: faqJsonLd(city.faq),
    },
  ],
};

html = html.replace(
  /<script type="application\/ld\+json">[\s\S]*?<\/script>/,
  `<script type="application/ld+json">\n${JSON.stringify(graph, null, 2)}\n  </script>`
);

// --- Breadcrumbs ---
html = html.replace(
  /<nav class="rk-breadcrumbs"[\s\S]*?<\/nav>/,
  `<nav class="rk-breadcrumbs" aria-label="Хлебные крошки">
      <ol>
        <li><a href="/">Главная</a></li>
        <li><a href="/web-studiya/">Студия</a></li>
        <li><a href="/web-studiya/sozdanie-saitov/">Создание сайтов</a></li>
        <li><span aria-current="page">${esc(city.name)}</span></li>
      </ol>
    </nav>`
);

// --- Hero ---
html = html.replace(
  /<p class="sz-hero__badge">[\s\S]*?<\/p>/,
  `<p class="sz-hero__badge"><span class="sz-hero__badge-icon" aria-hidden="true"></span>${esc(city.badge)}</p>`
);
html = html.replace(
  /<h1 class="sz-hero__title"[^>]*>[\s\S]*?<\/h1>/,
  `<h1 class="sz-hero__title" id="sz-hero-title">${esc(city.h1)}</h1>`
);
html = html.replace(
  /<p class="sz-hero__lead">[\s\S]*?<\/p>/,
  `<p class="sz-hero__lead">${esc(city.lead)}</p>`
);

// --- Why block ---
html = html.replace(
  /<section class="sz-why"[\s\S]*?<\/section>\s*\n\s*<section class="sz-reviews"/,
  `<section class="sz-why" aria-labelledby="sz-why-title">
      <div class="rk-container">
        <div class="sz-why__intro">
          <div class="sz-why__intro-text">
            <h2 class="sz-section-title" id="sz-why-title">${esc(city.whyTitle)}</h2>
            <p>${esc(city.whyIntro)}</p>
          </div>
        </div>
        <div class="sz-why__grid">
          ${pillarsHtml(city.pillars)}
        </div>
      </div>
    </section>

    <section class="sz-reviews"`
);

// --- Geo: current city as span ---
const geoSelf = new RegExp(
  `<a class="sz-geo__card" href="/web-studiya/sozdanie-saitov/${slug}/">([\\s\\S]*?)</a>`,
  "i"
);
html = html.replace(
  geoSelf,
  `<span class="sz-geo__card" aria-current="page">$1</span>`
);

// --- FAQ ---
html = html.replace(
  /<div class="rk-faq">[\s\S]*?<\/div>\s*<\/div>\s*<\/section>\s*\n\s*<section class="sz-seo-text"/,
  `<div class="rk-faq">
          ${faqHtml(city.faq)}
        </div>
      </div>
    </section>

    <section class="sz-seo-text"`
);

// --- SEO text ---
html = html.replace(
  /<section class="sz-seo-text"[\s\S]*?<\/section>\s*\n\s*<section class="sz-subnav"/,
  `<section class="sz-seo-text" aria-labelledby="sz-seo-text-title">
      <div class="rk-container sz-seo-text__inner">
        <h2 id="sz-seo-text-title">${esc(city.seoTitle)}</h2>
        <p>${esc(city.seoIntro)}</p>
        <h3>${esc(city.seoH3a)}</h3>
        <p>${esc(city.seoP1)}</p>
        <p>${esc(city.seoP2)}</p>
        <h3>${esc(city.seoH3b)}</h3>
        <p>${esc(city.seoP3)}</p>
        <div class="sz-seo-text__table-wrap">
          <table>
            <thead><tr><th>Направление поддержки</th><th>Что включает услуга</th><th>Ценность для бизнеса</th></tr></thead>
            <tbody>
              <tr><td>Технический мониторинг</td><td>Обновление систем и контроль безопасности</td><td>Защита от сбоев, взломов и потери данных.</td></tr>
              <tr><td>Сохранность данных</td><td>Регулярное резервное копирование (бэкапы)</td><td>Восстановление работы сайта при сбоях на стороне хостинга.</td></tr>
              <tr><td>Digital-консалтинг</td><td>Аудит, аналитика и корректировка стратегии</td><td>Решения на основе данных Яндекс Метрики и GA4.</td></tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>

    <section class="sz-subnav"`
);

// --- Contacts intro ---
html = html.replace(
  /<p class="rk-contacts__intro">[\s\S]*?<\/p>/,
  `<p class="rk-contacts__intro">${esc(city.ctaIntro)}</p>`
);

// --- Forms ---
const prefix = `rk-sozdanie-${slug}`;
html = html.replace(
  /id="rk-form-sozdanie-contacts"/,
  `id="rk-form-sozdanie-${slug}-contacts"`
);
html = html.replace(
  /name="sozdanie_contacts"/,
  `name="sozdanie_${slug}_contacts"`
);
html = html.replace(
  /data-form-name="Создание сайтов — контакты — отправьте заявку"/,
  `data-form-name="${esc(city.formContactsName)}"`
);
html = html.replace(/id="rk-sozdanie-contact-name"/g, `id="${prefix}-contact-name"`);
html = html.replace(/for="rk-sozdanie-contact-name"/g, `for="${prefix}-contact-name"`);
html = html.replace(/id="rk-sozdanie-contact-phone"/g, `id="${prefix}-contact-phone"`);
html = html.replace(/for="rk-sozdanie-contact-phone"/g, `for="${prefix}-contact-phone"`);
html = html.replace(/id="rk-sozdanie-contact-regulation"/g, `id="${prefix}-contact-regulation"`);
html = html.replace(/for="rk-sozdanie-contact-regulation"/g, `for="${prefix}-contact-regulation"`);

html = html.replace(
  /id="rk-form-sozdanie-popup-lead"/,
  `id="rk-form-sozdanie-${slug}-popup-lead"`
);
html = html.replace(
  /name="sozdanie_popup_lead"/,
  `name="sozdanie_${slug}_popup_lead"`
);
html = html.replace(
  /data-form-name="Создание сайтов — попап — обсудить проект"/,
  `data-form-name="${esc(city.formPopupName)}"`
);
html = html.replace(/id="rk-sozdanie-popup-name"/g, `id="${prefix}-popup-name"`);
html = html.replace(/for="rk-sozdanie-popup-name"/g, `for="${prefix}-popup-name"`);
html = html.replace(/id="rk-sozdanie-popup-phone"/g, `id="${prefix}-popup-phone"`);
html = html.replace(/for="rk-sozdanie-popup-phone"/g, `for="${prefix}-popup-phone"`);
html = html.replace(/id="rk-sozdanie-popup-email"/g, `id="${prefix}-popup-email"`);
html = html.replace(/for="rk-sozdanie-popup-email"/g, `for="${prefix}-popup-email"`);
html = html.replace(/id="rk-sozdanie-popup-message"/g, `id="${prefix}-popup-message"`);
html = html.replace(/for="rk-sozdanie-popup-message"/g, `for="${prefix}-popup-message"`);

html = html.replace(
  /<p>Оставьте заявку - и мы предложим оптимальное digital-решение под ваши задачи<\/p>/,
  `<p>${esc(city.modalLead)}</p>`
);

// Studio banner
html = html.replace(
  /<p>Наша команда поможет вывести ваш бизнес на новый уровень в digital\.<\/p>/,
  `<p>${esc(city.studioBannerP)}</p>`
);

// Body class marker
html = html.replace(
  /class="rk-clean sozdanie-page"/,
  `class="rk-clean sozdanie-page sozdanie-city sozdanie-city--${slug}"`
);

const outDir = path.join(ROOT, "web-studiya/sozdanie-saitov", slug);
fs.mkdirSync(outDir, { recursive: true });
const outFile = path.join(outDir, "index.html");
fs.writeFileSync(outFile, html, "utf8");
console.log("Wrote", outFile, html.length, "bytes");

}

for (const slug of slugs) generate(slug);