import puppeteer from 'puppeteer-core';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SCREENSHOT_DIR = path.resolve(__dirname, '..', 'docs', 'presentation_assets', 'screenshots');

const sleep = (ms) => new Promise((res) => setTimeout(res, ms));

async function run() {
  console.log('Launching Chrome...');
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--disable-gpu',
      '--window-size=1440,920'
    ]
  });

  const page = await browser.newPage();
  await page.setViewport({ width: 1440, height: 920, deviceScaleFactor: 2 });

  // 1. Auth Page
  console.log('Capturing Auth Screen...');
  await page.goto('http://localhost:8501', { waitUntil: 'networkidle2' });
  await sleep(3500);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '01_auth_screen.png') });
  console.log('Saved 01_auth_screen.png');

  // 2. Demo Login & Dashboard
  console.log('Logging in via Demo Mode...');
  await page.goto('http://localhost:8501/?auth_action=demo', { waitUntil: 'networkidle2' });
  await sleep(5000);
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '02_dashboard_overview.png') });
  console.log('Saved 02_dashboard_overview.png');

  // Function to click sidebar nav items
  async function navigateTo(menuText) {
    console.log(`Navigating to ${menuText}...`);
    await page.evaluate((text) => {
      const labels = Array.from(document.querySelectorAll('div[data-testid="stRadio"] label, div[data-testid="stSidebar"] label'));
      for (const label of labels) {
        if (label.innerText.includes(text)) {
          label.click();
          break;
        }
      }
    }, menuText);
    await sleep(4000);
  }

  // 3. Transactions Page
  await navigateTo('Transactions');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '03_transactions_hub.png') });
  console.log('Saved 03_transactions_hub.png');

  // 4. Budgets Page
  await navigateTo('Budgets');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '04_budgets_monitoring.png') });
  console.log('Saved 04_budgets_monitoring.png');

  // 5. Analytics Page
  await navigateTo('Analytics');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '05_analytics_visualizations.png') });
  console.log('Saved 05_analytics_visualizations.png');

  // 6. Forecast Page (ML Engine)
  await navigateTo('Forecast');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '06_forecast_ml_engine.png') });
  console.log('Saved 06_forecast_ml_engine.png');

  // 7. Insights Page
  await navigateTo('Insights');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '07_insights_intelligence.png') });
  console.log('Saved 07_insights_intelligence.png');

  // 8. Savings Goals Page
  await navigateTo('Savings Goals');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '08_savings_goals.png') });
  console.log('Saved 08_savings_goals.png');

  // 9. Import & Export Page
  await navigateTo('Import & Export');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '09_import_export_hub.png') });
  console.log('Saved 09_import_export_hub.png');

  // 10. Settings Page
  await navigateTo('Settings');
  await page.screenshot({ path: path.join(SCREENSHOT_DIR, '10_settings_preferences.png') });
  console.log('Saved 10_settings_preferences.png');

  await browser.close();
  console.log('All 10 screenshots captured successfully!');
}

run().catch((err) => {
  console.error('Error during capture:', err);
  process.exit(1);
});
