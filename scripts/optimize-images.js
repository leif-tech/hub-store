#!/usr/bin/env node
/*
  One-shot image optimizer: resizes and re-encodes JPG/PNG files in public/
  in place. Files larger than a threshold get rewritten at a sensible max
  width + mozjpeg quality so the storefront stops shipping 7-8 MB category
  images on the homepage.

  Safe to re-run: already-small files are skipped.
  Run: node scripts/optimize-images.js
*/

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const PUBLIC = path.join(__dirname, '..', 'public');

// { glob-ish dir + filename regex, max width, quality, min bytes to bother }
const RULES = [
  { dir: 'cat-images',  match: /\.(jpe?g|png)$/i, maxW: 1000, quality: 78, minBytes: 200 * 1024 },
  { dir: '',            match: /^hero-.*\.(jpe?g|png)$/i, maxW: 2000, quality: 82, minBytes: 300 * 1024 },
  { dir: '',            match: /^customer(-new)?-.*\.(jpe?g|png)$/i, maxW: 600, quality: 80, minBytes: 200 * 1024 },
  { dir: '',            match: /^bundle-.*\.(jpe?g|png)$/i, maxW: 900, quality: 80, minBytes: 200 * 1024 },
  { dir: 'uploads',     match: /\.(jpe?g|png)$/i, maxW: 1400, quality: 80, minBytes: 400 * 1024 },
];

async function processFile(fullPath, rule) {
  const stat = fs.statSync(fullPath);
  if (stat.size < rule.minBytes) return { skipped: true, reason: 'small', size: stat.size };

  const buf = fs.readFileSync(fullPath);
  const img = sharp(buf, { failOn: 'none' });
  const meta = await img.metadata();
  const needsResize = meta.width && meta.width > rule.maxW;

  let pipeline = sharp(buf, { failOn: 'none' }).rotate();
  if (needsResize) pipeline = pipeline.resize({ width: rule.maxW, withoutEnlargement: true });
  const out = await pipeline
    .jpeg({ quality: rule.quality, mozjpeg: true, progressive: true })
    .toBuffer();

  if (out.length >= stat.size * 0.95) {
    return { skipped: true, reason: 'no-gain', size: stat.size, newSize: out.length };
  }
  // Write atomically
  const tmp = fullPath + '.tmp';
  fs.writeFileSync(tmp, out);
  fs.renameSync(tmp, fullPath);
  return { skipped: false, oldSize: stat.size, newSize: out.length, width: needsResize ? rule.maxW : meta.width };
}

function formatBytes(n) {
  if (n > 1024 * 1024) return (n / 1024 / 1024).toFixed(2) + ' MB';
  return (n / 1024).toFixed(0) + ' KB';
}

(async () => {
  let totalOld = 0, totalNew = 0, touched = 0, skipped = 0;
  for (const rule of RULES) {
    const dirPath = path.join(PUBLIC, rule.dir);
    if (!fs.existsSync(dirPath)) continue;
    const files = fs.readdirSync(dirPath).filter(f => rule.match.test(f));
    for (const f of files) {
      const full = path.join(dirPath, f);
      if (!fs.statSync(full).isFile()) continue;
      try {
        const r = await processFile(full, rule);
        if (r.skipped) {
          skipped++;
          continue;
        }
        totalOld += r.oldSize;
        totalNew += r.newSize;
        touched++;
        console.log(`  ${path.join(rule.dir, f).padEnd(42)}  ${formatBytes(r.oldSize).padStart(10)}  ->  ${formatBytes(r.newSize).padStart(10)}  (${Math.round((1 - r.newSize / r.oldSize) * 100)}% smaller)`);
      } catch (e) {
        console.error(`  FAIL ${f}: ${e.message}`);
      }
    }
  }
  console.log('');
  console.log(`Done. Rewrote ${touched} file(s), skipped ${skipped}.`);
  if (touched) console.log(`Total: ${formatBytes(totalOld)} -> ${formatBytes(totalNew)} (${Math.round((1 - totalNew / totalOld) * 100)}% smaller)`);
})();
