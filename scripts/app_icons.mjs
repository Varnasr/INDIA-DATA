// Writes assets/app/icon-192.png, icon-512.png, maskable-512.png and
// apple-touch-icon.png: the installed app's icons, drawn from the same mark as
// the favicon (build_site.py, favicon()). Run once after changing the mark.
//
//   PLAYWRIGHT_CORE=... CHROME=... node scripts/app_icons.mjs
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const { chromium } = await import(process.env.PLAYWRIGHT_CORE || 'playwright-core');
// rounded corners for the plain icon; a full square for the maskable one,
// whose launcher crops it, with the mark kept inside the central 60%
const mark = (rx, inset) => `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
<rect width="32" height="32" rx="${rx}" fill="#1f4e79"/>
<g transform="translate(${16 * inset} ${16 * inset}) scale(${1 - inset})">
<path d="M8 9h16M8 15h16M8 21h9" stroke="white" stroke-width="2.4" stroke-linecap="round" fill="none"/></g></svg>`;
const OUT = [['icon-192.png', 192, mark(6, 0)], ['icon-512.png', 512, mark(6, 0)], ['maskable-512.png', 512, mark(0, 0.3)], ['apple-touch-icon.png', 180, mark(0, 0.12)]];
fs.mkdirSync(path.join(ROOT, 'assets/app'), { recursive: true });
const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
try {
  for (const [name, px, svg] of OUT) {
    const page = await browser.newPage({ viewport: { width: px, height: px } });
    await page.setContent(`<html><body style="margin:0;background:transparent">${svg.replace('<svg ', `<svg width="${px}" height="${px}" `)}</body></html>`);
    await page.screenshot({ path: path.join(ROOT, 'assets/app', name), omitBackground: true });
    await page.close();
    console.log(name, px);
  }
} finally { await browser.close(); }
