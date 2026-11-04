import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { spawn } from 'child_process';
const [mode, a, b, out] = process.argv.slice(2);
const browser = await chromium.launch({ args: ['--disable-web-security'] });
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('console', m => console.log('PAGE', m.text())); page.on('pageerror', e => console.log('ERR', e.message));
await page.goto('http://127.0.0.1:8765/scene.html');
await page.evaluate(() => window.ready);
const canvas = await page.$('#c');
if (mode === 'still') {
  for (const t of a.split(',')) { await page.evaluate(t => render(t), +t); await canvas.screenshot({ path: `${out}/still_${t}.jpg`, type: 'jpeg', quality: 85 }); }
} else {
  const fps = 30, n = Math.round((+b - +a) * fps);
  const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
  for (let i = 0; i < n; i++) {
    await page.evaluate(t => render(t), +a + i / fps);
    const buf = await canvas.screenshot({ type: 'jpeg', quality: 95 });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (i % 150 === 0) console.log('frame', i, '/', n);
  }
  ff.stdin.end(); await new Promise(r => ff.on('close', r));
}
await browser.close();
