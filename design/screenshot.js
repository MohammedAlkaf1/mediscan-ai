const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

const screens = [
  { file: 'landing.html',       out: 'mediscan_landing.png',       width: 1440, height: 1 },
  { file: 'login.html',         out: 'mediscan_login.png',         width: 1440, height: 900 },
  { file: 'dashboard.html',     out: 'mediscan_dashboard.png',     width: 1440, height: 1 },
  { file: 'upload.html',        out: 'mediscan_upload.png',        width: 1440, height: 1 },
  { file: 'report_detail.html', out: 'mediscan_report_detail.png', width: 1440, height: 1 },
  { file: 'history.html',       out: 'mediscan_history.png',       width: 1440, height: 1 },
  { file: 'shared_report.html', out: 'mediscan_shared_report.png', width: 1440, height: 1 },
  { file: 'mobile.html',        out: 'mediscan_mobile_preview.png',width: 390,  height: 1 },
];

const outDir = path.join(__dirname, 'exports');
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir);

(async () => {
  const browser = await chromium.launch();

  for (const s of screens) {
    console.log(`Rendering: ${s.out}`);
    const page = await browser.newPage();

    // Disable cache, set device scale for retina-quality
    await page.setViewportSize({ width: s.width, height: s.height === 1 ? 900 : s.height });

    const filePath = path.join(__dirname, 'screens', s.file);
    await page.goto(`file:///${filePath}`, { waitUntil: 'networkidle' });

    // Wait for Google Fonts (or fallback gracefully)
    await page.waitForTimeout(800);

    // Full page screenshot
    const outPath = path.join(outDir, s.out);
    await page.screenshot({
      path: outPath,
      fullPage: true,
      type: 'png',
    });

    console.log(`  ✓ Saved: ${outPath}`);
    await page.close();
  }

  await browser.close();
  console.log('\nAll screenshots exported to design/exports/');
})();
