// ep1.html を 30fps で書き出す。python3 -m http.server 8765 を src/ で起動しておく
// 使い方: node render.mjs <開始フレーム> <終了フレーム> <out.mp4>
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';
import { spawn } from 'child_process';
const [f0, f1, out] = process.argv.slice(2).map((v, i) => i < 2 ? +v : v);
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1920, height: 1080 } });
page.on('pageerror', e => console.log('ERR', e.message));
await page.goto('http://127.0.0.1:8765/ep1/ep1.html');
await page.evaluate(() => window.ready);
const canvas = await page.$('#c');
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', '30', '-c:v', 'mjpeg', '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', out], { stdio: ['pipe', 'inherit', 'inherit'] });
for (let i = f0; i < f1; i++) {
  await page.evaluate(t => render(t), i / 30);
  const buf = await canvas.screenshot({ type: 'jpeg', quality: 94 });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if ((i - f0) % 600 === 0) console.log(out, i - f0, '/', f1 - f0);
}
ff.stdin.end(); await new Promise(r => ff.on('close', r));
await browser.close();
