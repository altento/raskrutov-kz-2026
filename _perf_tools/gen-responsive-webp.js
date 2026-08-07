const sharp = require("sharp");
const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const SITE = path.join(ROOT, "site_plesk");
const STUDIO = path.join(SITE, "assets", "img", "studio");
const CITIES = path.join(SITE, "assets", "img", "cities");
const PERF = path.join(SITE, "assets", "img", "perf");

const created = [];

async function writeVariant(src, dest, width, quality) {
  const meta = await sharp(src).metadata();
  let pipeline = sharp(src);
  if (meta.width && meta.width > width) {
    pipeline = pipeline.resize({ width, withoutEnlargement: true });
  } else if (meta.width && meta.width < width) {
    // do not upscale; just recompress at native width
    pipeline = pipeline.resize({ width: meta.width, withoutEnlargement: true });
  } else {
    pipeline = pipeline.resize({ width, withoutEnlargement: true });
  }
  await pipeline.webp({ quality }).toFile(dest);
  const st = fs.statSync(dest);
  created.push({ file: dest, bytes: st.size, width, quality, srcW: meta.width });
  return st.size;
}

async function main() {
  // A) hero-devices
  const heroDevices = path.join(STUDIO, "hero-devices.webp");
  if (!fs.existsSync(heroDevices)) throw new Error("Missing " + heroDevices);
  await writeVariant(heroDevices, path.join(STUDIO, "hero-devices-420.webp"), 420, 78);
  await writeVariant(heroDevices, path.join(STUDIO, "hero-devices-760.webp"), 760, 80);
  await writeVariant(heroDevices, path.join(STUDIO, "hero-devices-1100.webp"), 1100, 82);

  // B) hero-bg
  const heroBg = path.join(STUDIO, "hero-bg.webp");
  if (!fs.existsSync(heroBg)) throw new Error("Missing " + heroBg);
  const bgMeta = await sharp(heroBg).metadata();
  await writeVariant(heroBg, path.join(STUDIO, "hero-bg-768.webp"), 768, 75);
  await writeVariant(heroBg, path.join(STUDIO, "hero-bg-1280.webp"), 1280, 78);
  // 1920: resize or recompress if already ~1920
  const dest1920 = path.join(STUDIO, "hero-bg-1920.webp");
  if (bgMeta.width && Math.abs(bgMeta.width - 1920) <= 40) {
    await sharp(heroBg).webp({ quality: 80 }).toFile(dest1920);
    const st = fs.statSync(dest1920);
    created.push({ file: dest1920, bytes: st.size, width: bgMeta.width, quality: 80, srcW: bgMeta.width, note: "recompress" });
  } else {
    await writeVariant(heroBg, dest1920, 1920, 80);
  }

  // C) cities
  const cityFiles = fs.readdirSync(CITIES).filter((f) => {
    if (!f.toLowerCase().endsWith(".webp")) return false;
    if (/-\d+\.webp$/i.test(f)) return false; // skip *-320 / *-640 etc
    return true;
  });
  for (const f of cityFiles) {
    const base = f.replace(/\.webp$/i, "");
    const src = path.join(CITIES, f);
    await writeVariant(src, path.join(CITIES, `${base}-320.webp`), 320, 72);
    await writeVariant(src, path.join(CITIES, `${base}-640.webp`), 640, 78);
  }

  // D) logo — prefer perf/logo-*.webp (largest)
  let logoSrc = null;
  if (fs.existsSync(PERF)) {
    const logos = fs
      .readdirSync(PERF)
      .filter((f) => /^logo-\d+\.webp$/i.test(f))
      .map((f) => {
        const m = f.match(/logo-(\d+)\.webp$/i);
        return { f, w: m ? parseInt(m[1], 10) : 0, p: path.join(PERF, f) };
      })
      .sort((a, b) => b.w - a.w);
    if (logos.length) logoSrc = logos[0].p;
  }
  if (!logoSrc) {
    // search site_plesk for logo files
    function walk(dir, acc) {
      for (const ent of fs.readdirSync(dir, { withFileTypes: true })) {
        const p = path.join(dir, ent.name);
        if (ent.isDirectory()) {
          if (ent.name === "node_modules" || ent.name === ".git") continue;
          walk(p, acc);
        } else if (/logo/i.test(ent.name) && /\.(webp|png|jpe?g)$/i.test(ent.name)) {
          acc.push(p);
        }
      }
      return acc;
    }
    const found = walk(SITE, []);
    if (!found.length) throw new Error("No logo source found");
    logoSrc = found.sort((a, b) => fs.statSync(b).size - fs.statSync(a).size)[0];
  }

  // write logos under assets/img/studio/ (and also ok under perf — prefer studio per request "studio/ or perf/")
  const logoOutDir = STUDIO;
  await writeVariant(logoSrc, path.join(logoOutDir, "raskrutov-logo-160.webp"), 160, 82);
  await writeVariant(logoSrc, path.join(logoOutDir, "raskrutov-logo-240.webp"), 240, 82);
  await writeVariant(logoSrc, path.join(logoOutDir, "raskrutov-logo-422.webp"), 422, 85);

  // Print table
  console.log("\nCreated files:");
  console.log("-".repeat(90));
  console.log(
    "bytes".padStart(10) +
      "  " +
      "w".padStart(5) +
      "  q".padStart(3) +
      "  relative path"
  );
  console.log("-".repeat(90));
  let total = 0;
  for (const row of created) {
    const rel = path.relative(ROOT, row.file).replace(/\\/g, "/");
    total += row.bytes;
    const note = row.note ? ` (${row.note}, srcW=${row.srcW})` : ` (srcW=${row.srcW})`;
    console.log(
      String(row.bytes).padStart(10) +
        "  " +
        String(row.width).padStart(5) +
        "  " +
        String(row.quality).padStart(3) +
        "  " +
        rel +
        note
    );
  }
  console.log("-".repeat(90));
  console.log(`Total: ${created.length} files, ${total} bytes`);
  console.log(`Logo source: ${path.relative(ROOT, logoSrc).replace(/\\/g, "/")}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
