import puppeteer from 'puppeteer-core';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ASSETS_DIR = path.resolve(__dirname, '..', 'docs', 'presentation_assets');

const files = [
  'architecture/system_architecture',
  'workflow/user_journey',
  'workflow/technical_workflow',
  'dataflow/data_flow',
  'ai_pipeline/ai_ml_pipeline',
  'deployment/deployment_architecture',
  'technology_stack/technology_stack'
];

async function convert() {
  const browser = await puppeteer.launch({
    executablePath: 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
    headless: 'new',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  const page = await browser.newPage();

  for (const f of files) {
    const svgPath = path.resolve(ASSETS_DIR, `${f}.svg`);
    const pngPath = path.resolve(ASSETS_DIR, `${f}.png`);
    if (fs.existsSync(svgPath)) {
      const svgContent = fs.readFileSync(svgPath, 'utf8');
      await page.setViewport({ width: 1200, height: 800, deviceScaleFactor: 2 });
      await page.setContent(`<body style="margin:0; background:transparent;">${svgContent}</body>`);
      const svgElement = await page.$('svg');
      if (svgElement) {
        await svgElement.screenshot({ path: pngPath, omitBackground: true });
        console.log(`Rendered PNG: ${pngPath}`);
      }
    }
  }

  await browser.close();
  console.log('All SVGs rendered to PNG successfully!');
}

convert().catch(console.error);
