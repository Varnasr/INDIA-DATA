// Prints the HTML reports written beside the Word files to PDF.
//   node scripts/reports/pdf.mjs report.html [more.html ...]
// Needs playwright-core and a Chromium (PLAYWRIGHT_CORE, CHROME as in i18n_collect.mjs).
const { chromium } = await import(process.env.PLAYWRIGHT_CORE || 'playwright-core');
const browser = await chromium.launch(process.env.CHROME ? { executablePath: process.env.CHROME } : {});
for (const f of process.argv.slice(2)) {
  const page = await browser.newPage();
  await page.goto('file://' + (f.startsWith('/') ? f : process.cwd() + '/' + f), { waitUntil: 'load' });
  const out = f.replace(/\.html$/, '.pdf');
  await page.pdf({ path: out, format: 'A4', printBackground: true, displayHeaderFooter: true,
    margin: { top: '18mm', bottom: '20mm', left: '18mm', right: '18mm' },
    headerTemplate: '<span></span>',
    footerTemplate: '<div style="width:100%;font-size:7.5pt;color:#4D5B69;text-align:center;font-family:sans-serif">PinPoint Ventures · Aggregates only; no names or EPIC numbers · <span class="pageNumber"></span> of <span class="totalPages"></span></div>' });
  console.log('wrote', out);
  await page.close();
}
await browser.close();
