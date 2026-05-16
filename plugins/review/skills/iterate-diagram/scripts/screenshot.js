#!/usr/bin/env node
/**
 * Screenshot an HTML file using Playwright.
 *
 * Usage:
 *   node screenshot.js <html-file> [output.png] [--width=N] [--height=N] [--zoom=N] [--pan=X,Y] [--eval="js code"]
 *
 * Examples:
 *   node screenshot.js diagram.html
 *   node screenshot.js diagram.html shot.png --width=2560 --height=1440 --zoom=0.5
 *   node screenshot.js diagram.html shot.png --eval="document.querySelector('.toggle').click()"
 *   node screenshot.js diagram.html shot.png --eval="state.zoom=0.6; applyTransform(); render();"
 */

const path = require('path');
const { execSync } = require('child_process');

let chromium;
try {
  chromium = require('playwright').chromium;
} catch {
  // Node doesn't search global node_modules by default, so resolve it explicitly
  try {
    const globalRoot = execSync('npm root -g', { encoding: 'utf8' }).trim();
    chromium = require(path.join(globalRoot, 'playwright')).chromium;
  } catch {
    console.error('Error: playwright not found. Install it globally with: npm install -g playwright');
    process.exit(1);
  }
}

function parseArgs(argv) {
  const args = { evals: [] };
  const positional = [];

  for (const arg of argv.slice(2)) {
    if (arg.startsWith('--width=')) args.width = parseInt(arg.split('=')[1]);
    else if (arg.startsWith('--height=')) args.height = parseInt(arg.split('=')[1]);
    else if (arg.startsWith('--zoom=')) args.zoom = parseFloat(arg.split('=')[1]);
    else if (arg.startsWith('--pan=')) {
      const [x, y] = arg.split('=')[1].split(',').map(Number);
      args.panX = x; args.panY = y;
    }
    else if (arg.startsWith('--eval=')) args.evals.push(arg.substring(7));
    else if (arg.startsWith('--click=')) args.click = arg.substring(8);
    else if (arg === '--full') args.fullPage = true;
    else positional.push(arg);
  }

  args.htmlFile = positional[0];
  args.output = positional[1] || 'screenshot.png';
  args.width = args.width || 2560;
  args.height = args.height || 1440;

  return args;
}

(async () => {
  const args = parseArgs(process.argv);

  if (!args.htmlFile) {
    console.error('Usage: node screenshot.js <html-file> [output.png] [options]');
    console.error('Options: --width=N --height=N --zoom=N --pan=X,Y --eval="js" --click="selector" --full');
    process.exit(1);
  }

  const htmlPath = path.resolve(args.htmlFile);
  const outputDir = path.dirname(htmlPath);
  const outputPath = path.resolve(outputDir, args.output);

  let browser;
  try {
    browser = await chromium.launch();
    const page = await browser.newPage({
      viewport: { width: args.width, height: args.height }
    });

    await page.goto(`file://${htmlPath}`);
    await page.waitForTimeout(600);

    // Click a text element if requested
    if (args.click) {
      try {
        await page.click(`text=${args.click}`);
        await page.waitForTimeout(300);
      } catch (e) {
        console.error(`Warning: click "${args.click}" failed: ${e.message}`);
      }
    }

    // Run eval scripts in sequence
    for (const code of args.evals) {
      try {
        await page.evaluate(code);
        await page.waitForTimeout(200);
      } catch (e) {
        console.error(`Warning: eval failed: ${e.message}`);
      }
    }

    // Apply zoom/pan if specified (assumes state/applyTransform globals)
    if (args.zoom || args.panX !== undefined) {
      try {
        await page.evaluate(({ zoom, panX, panY }) => {
          if (typeof state !== 'undefined') {
            if (zoom) state.zoom = zoom;
            if (panX !== undefined) state.panX = panX;
            if (panY !== undefined) state.panY = panY;
            if (typeof applyTransform === 'function') applyTransform();
            if (typeof render === 'function') render();
          }
        }, { zoom: args.zoom, panX: args.panX, panY: args.panY });
        await page.waitForTimeout(300);
      } catch (e) {
        console.error(`Warning: zoom/pan failed: ${e.message}`);
      }
    }

    await page.screenshot({
      path: outputPath,
      fullPage: args.fullPage || false
    });

    console.log(outputPath);
  } catch (e) {
    console.error(`Error: ${e.message}`);
    process.exit(1);
  } finally {
    if (browser) await browser.close();
  }
})();
