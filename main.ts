// "The Day in Full" — news-image entrypoint (Node 22, standard library only).
//
// Preferred path: render the front page fresh by running dayfront.py with
// python3, then validate the PNG it produced (magic bytes, exactly
// 1024x1024, at most 1 MiB) and copy it to the output directory.
// Fallback path: if python3 or Pillow is unavailable, copy the committed
// entry.png that sits beside this file — the bytes are identical because
// dayfront.py is deterministic.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, readFileSync, statSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const rendered = join(here, 'entry.png');
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const MAX_BYTES = 1024 * 1024;

function pngIsValid(path: string): boolean {
  try {
    const buf = readFileSync(path);
    if (buf.length < 24 || buf.length > MAX_BYTES) return false;
    // PNG magic: 89 50 4E 47 0D 0A 1A 0A; IHDR width/height are big-endian
    // uint32 at offsets 16 and 20.
    const magic = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];
    for (let i = 0; i < magic.length; i++) if (buf[i] !== magic[i]) return false;
    return buf.readUInt32BE(16) === 1024 && buf.readUInt32BE(20) === 1024;
  } catch {
    return false;
  }
}

let renderedFresh = false;
try {
  execFileSync('python3', [join(here, 'dayfront.py')], { stdio: 'inherit', timeout: 120_000 });
  renderedFresh = pngIsValid(rendered);
} catch {
  renderedFresh = false;
}

if (!renderedFresh && !pngIsValid(rendered)) {
  throw new Error('entry.png is missing or invalid and rendering failed');
}

copyFileSync(rendered, join(outDir, 'entry.png'));
console.log(`entry.png -> ${join(outDir, 'entry.png')} (${statSync(rendered).size} bytes, ${renderedFresh ? 'fresh render' : 'committed copy'})`);
