// Render the code-native SVG diagrams at 1.5x for readable GitHub PNG previews.
const fs = require('node:fs');
const path = require('node:path');
const sharp = require('sharp');
const out = path.resolve(__dirname, '../docs/diagrams');
(async () => {
  for (const file of fs.readdirSync(path.join(out, 'svg')).filter(f => f.endsWith('.svg'))) {
    await sharp(path.join(out, 'svg', file), { density: 108 })
      .png().toFile(path.join(out, file.replace(/\.svg$/, '.png')));
    console.log(file);
  }
})().catch(err => { console.error(err); process.exit(1); });
