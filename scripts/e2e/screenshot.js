// Screenshot the Haqeeq dashboard at 1920x1080 for the pitch deck and the backup video.
//
// Usage:
//   node scripts/e2e/screenshot.js                                  # http://localhost:3000/?mock=1
//   node scripts/e2e/screenshot.js https://<prod>.vercel.app/
//
// Uses the Chromium that is already installed for Playwright (`require('playwright')`).
// Never run `npx playwright install` here: it downloads browsers and is not needed.
// Output: scripts/e2e/out/dashboard-1920.png (directory is git-ignored).

const fs = require('fs');
const path = require('path');
const { chromium } = require('playwright');

const url = process.argv[2] || 'http://localhost:3000/?mock=1';
const outDir = path.join(__dirname, 'out');
const outFile = path.join(outDir, 'dashboard-1920.png');

(async () => {
  fs.mkdirSync(outDir, { recursive: true });

  const browser = await chromium.launch();
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();

  const consoleErrors = [];
  page.on('console', (msg) => {
    if (msg.type() === 'error') consoleErrors.push(msg.text());
  });
  page.on('pageerror', (err) => consoleErrors.push('pageerror: ' + err.message));

  try {
    await page.goto(url, { waitUntil: 'networkidle', timeout: 60000 });
  } catch (e) {
    // networkidle can time out on pages with live realtime sockets; keep going.
    console.warn('warning: networkidle not reached, continuing: ' + e.message);
  }

  // Wait for map tiles if the page has a map (Leaflet-style). Not fatal if absent.
  try {
    await page.waitForSelector('.leaflet-tile-loaded, img.leaflet-tile', { timeout: 15000 });
  } catch (_) {
    console.warn('note: no map tiles found (no map on page, or tiles blocked by network)');
  }
  // Small settle time for charts and animations.
  await page.waitForTimeout(1500);

  await page.screenshot({ path: outFile, fullPage: false });
  await browser.close();

  console.log('saved: ' + outFile);
  if (consoleErrors.length) {
    console.log('console errors (' + consoleErrors.length + '):');
    for (const e of consoleErrors) console.log('  - ' + e);
  } else {
    console.log('console errors: none');
  }
})().catch((err) => {
  console.error('screenshot failed: ' + err.message);
  process.exit(1);
});
