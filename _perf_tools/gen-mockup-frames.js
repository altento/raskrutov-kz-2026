const { Resvg } = require('@resvg/resvg-js');
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..', 'site_plesk', 'assets', 'img', 'sozdanie-saitov');

async function svgToWebp(svgName, outName, width, quality) {
  const svgPath = path.join(root, svgName);
  const svg = fs.readFileSync(svgPath);
  const resvg = new Resvg(svg, {
    fitTo: { mode: 'width', value: width },
    background: 'rgba(0,0,0,0)',
  });
  const pngData = resvg.render();
  const pngBuf = pngData.asPng();
  const h = pngData.height;
  const w = pngData.width;
  const outPath = path.join(root, outName);
  await sharp(pngBuf)
    .webp({ quality, alphaQuality: 80, effort: 6 })
    .toFile(outPath);
  const size = fs.statSync(outPath).size;
  console.log(`${outName}: ${w}x${h} ${size} bytes (${(size/1024).toFixed(1)}KB)`);
  return size;
}

(async () => {
  console.log('Before SVG sizes:');
  for (const f of ['mockup-laptop.svg', 'mockup-phone.svg']) {
    console.log(`  ${f}: ${fs.statSync(path.join(root, f)).size} bytes`);
  }
  await svgToWebp('mockup-laptop.svg', 'mockup-laptop-480.webp', 480, 70);
  await svgToWebp('mockup-laptop.svg', 'mockup-laptop-710.webp', 710, 70);
  await svgToWebp('mockup-phone.svg', 'mockup-phone-160.webp', 160, 70);
  await svgToWebp('mockup-phone.svg', 'mockup-phone-153.webp', 153, 70);
})().catch((e) => { console.error(e); process.exit(1); });
