#!/usr/bin/env node
/*
  One-shot image optimizer: resizes and re-encodes JPG/PNG files in public/
  in place. Files larger than a threshold get rewritten at a sensible max
  width + mozjpeg quality so the storefront stops shipping 7-8 MB category
  images on the homepage.

  Supports WebP output (format: 'webp') — writes a new .webp file alongside
  the original so HTML references can switch to the lighter format.

  Safe to re-run: already-small files are skipped.
  Run: node scripts/optimize-images.js
*/

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

const PUBLIC = path.join(__dirname, '..', 'public');

// format: 'webp' writes a .webp sibling; 'jpeg' overwrites in place; 'png' keeps PNG
const RULES = [
  // Category icon PNGs → 400px WebP (transparent backgrounds)
  { dir: '',            match: /^cat-.*\.png$/i,     maxW: 400,  quality: 80, minBytes: 50 * 1024,  format: 'webp' },
  // Hero images → 1920px WebP
  { dir: '',            match: /^hero-.*\.png$/i,     maxW: 1920, quality: 82, minBytes: 100 * 1024, format: 'webp' },
  // Logo + favicon → 200px compressed PNG (keep PNG for favicon compatibility)
  { dir: '',            match: /^(logo|favicon)\.png$/i, maxW: 200, quality: 85, minBytes: 50 * 1024, format: 'png' },
  // Existing rules (unchanged)
  { dir: 'cat-images',  match: /\.(jpe?g|png)$/i,    maxW: 1000, quality: 78, minBytes: 200 * 1024, format: 'jpeg' },
  { dir: '',            match: /^hero-.*\.(jpe?g)$/i, maxW: 2000, quality: 82, minBytes: 300 * 1024, format: 'jpeg' },
  { dir: '',            match: /^customer(-new)?-.*\.(jpe?g|png)$/i, maxW: 600, quality: 80, minBytes: 200 * 1024, format: 'jpeg' },
  { dir: '',            match: /^bundle-.*\.(jpe?g|png)$/i, maxW: 900, quality: 80, minBytes: 200 * 1024, format: 'jpeg' },
  { dir: 'uploads',     match: /\.(jpe?g|png)$/i,    maxW: 1400, quality: 80, minBytes: 400 * 1024, format: 'jpeg' },
];

async function processFile(fullPath, rule) {
  const stat = fs.statSync(fullPath);
  if (stat.size < rule.minBytes) return { skipped: true, reason: 'small', size: stat.size };

  const fmt = rule.format || 'jpeg';
  const buf = fs.readFileSync(fullPath);
  const img = sharp(buf, { failOn: 'none' });
  const meta = await img.metadata();
  const needsResize = meta.width && meta.width > rule.maxW;

  let pipeline = sharp(buf, { failOn: 'none' }).rotate();
  if (needsResize) pipeline = pipeline.resize({ width: rule.maxW, withoutEnlargement: true });

  let out;
  if (fmt === 'webp') {
    out = await pipeline.webp({ quality: rule.quality, effort: 6 }).toBuffer();
  } else if (fmt === 'png') {
    out = await pipeline.png({ quality: rule.quality, compressionLevel: 9 }).toBuffer();
  } else {
    out = await pipeline.jpeg({ quality: rule.quality, mozjpeg: true, progressive: true }).toBuffer();
  }

  // For WebP, write as sibling .webp file (don't overwrite original)
  if (fmt === 'webp') {
    const webpPath = fullPath.replace(/\.(png|jpe?g)$/i, '.webp');
    // Skip if webp already exists and is small enough
    if (fs.existsSync(webpPath)) {
      const webpStat = fs.statSync(webpPath);
      if (webpStat.size <= out.length * 1.05) {
        return { skipped: true, reason: 'webp-exists', size: stat.size };
      }
    }
    const tmp = webpPath + '.tmp';
    fs.writeFileSync(tmp, out);
    fs.renameSync(tmp, webpPath);
    return { skipped: false, oldSize: stat.size, newSize: out.length, width: needsResize ? rule.maxW : meta.width, webp: true };
  }

  if (out.length >= stat.size * 0.95) {
    return { skipped: true, reason: 'no-gain', size: stat.size, newSize: out.length };
  }
  // Write atomically (overwrite original)
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
  const processed = new Set(); // track files already handled by earlier rules
  for (const rule of RULES) {
    const dirPath = path.join(PUBLIC, rule.dir);
    if (!fs.existsSync(dirPath)) continue;
    const files = fs.readdirSync(dirPath).filter(f => rule.match.test(f));
    for (const f of files) {
      const full = path.join(dirPath, f);
      const ruleKey = full + ':' + (rule.format || 'jpeg');
      if (processed.has(ruleKey)) continue;
      processed.add(ruleKey);
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
        const label = r.webp ? '→ .webp' : '';
        console.log(`  ${path.join(rule.dir, f).padEnd(42)}  ${formatBytes(r.oldSize).padStart(10)}  ->  ${formatBytes(r.newSize).padStart(10)}  (${Math.round((1 - r.newSize / r.oldSize) * 100)}% smaller) ${label}`);
      } catch (e) {
        console.error(`  FAIL ${f}: ${e.message}`);
      }
    }
  }
  console.log('');
  console.log(`Done. Rewrote ${touched} file(s), skipped ${skipped}.`);
  if (touched) console.log(`Total: ${formatBytes(totalOld)} -> ${formatBytes(totalNew)} (${Math.round((1 - totalNew / totalOld) * 100)}% smaller)`);
})();
