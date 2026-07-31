import fs from "fs";
const t = fs.readFileSync("site_mirror/index.html", "utf8");
const markers = [
  "section_image_9466bf80",
  "section_image_container",
  "6eea3ed3de3e5cbe118d06eb148fe963",
  "hero-home-mobile",
  'id="9466bf80aa894ca9b20b37b4d9409cc1"',
  'data-id="s-9466bf80aa894ca9b20b37b4d9409cc1"',
];
for (const m of markers) {
  console.log(m, "count", t.split(m).length - 1, "first", t.indexOf(m));
}
const key = 'data-id="s-9466bf80aa894ca9b20b37b4d9409cc1"';
const p = t.indexOf(key);
console.log("\n=== SECTION ===\n");
console.log(t.slice(Math.max(0, p - 400), p + 6000));

// background urls near hero
const heroSlice = t.slice(p, p + 8000);
const urls = [...heroSlice.matchAll(/url\(['"]?([^'")]+)['"]?\)/g)].map((m) => m[1]);
const srcs = [...heroSlice.matchAll(/\bsrc=["']([^"']+)["']/g)].map((m) => m[1]);
console.log("\nBG URLS", urls);
console.log("SRCS", srcs.slice(0, 20));

// deferred/critical height rules
for (const file of [
  "site_mirror/assets/css/home-critical.v3.css",
  "site_mirror/assets/css/home-deferred.v3.css",
]) {
  const c = fs.readFileSync(file, "utf8");
  const hits = [];
  let idx = 0;
  while ((idx = c.indexOf("9466bf80", idx)) !== -1 && hits.length < 8) {
    hits.push(c.slice(idx, idx + 400).replace(/\s+/g, " "));
    idx += 8;
  }
  console.log("\nFILE", file, "hits", c.split("9466bf80").length - 1);
  hits.forEach((h, i) => console.log(i, h));
}
