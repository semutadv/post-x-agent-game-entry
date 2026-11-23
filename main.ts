// NEON SERPENT entry program for the make.fun "agent builds a game" bounty.
//
// The entry itself is the X post named in POST.json; this program's whole
// job is to hand that file to the grader: it copies POST.json from the
// repository directory into the output directory, byte for byte, and exits.
// Outside the grader, MAKEFUN_BOT_DIR / MAKEFUN_OUTPUT_DIR point at the two
// directories; inside it they default to /bot and /output.

import { mkdirSync, readFileSync, renameSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(outputDir, { recursive: true });

const source = join(botDir, 'POST.json');
const target = join(outputDir, 'POST.json');

// Read and validate POST.json before copying anything: the grader only
// cares about the post it names, so a malformed file should fail loudly
// here rather than silently handing over a useless entry.
let raw: string;
try {
  raw = readFileSync(source, 'utf8');
} catch (err) {
  console.error(`could not read ${source}: ${(err as Error).message}`);
  process.exit(1);
}

let post: { url?: unknown };
try {
  post = JSON.parse(raw);
} catch (err) {
  console.error(`${source} is not valid JSON: ${(err as Error).message}`);
  process.exit(1);
}

const url = post.url;
if (typeof url !== 'string' || !url.startsWith('https://x.com/') || !url.includes('/status/')) {
  console.error(`${source} must carry a string "url" of an X post (https://x.com/.../status/...); got: ${JSON.stringify(url)}`);
  process.exit(1);
}

// Copy atomically: write to a temp file inside the output directory, then
// rename over the target, so a partial POST.json can never be observed.
const temp = join(outputDir, `.POST.json.tmp-${process.pid}`);
try {
  writeFileSync(temp, raw);
  renameSync(temp, target);
} catch (err) {
  console.error(`could not copy ${source} -> ${target}: ${(err as Error).message}`);
  process.exit(1);
}

console.log(`POST.json handed over; entry post: ${url}`);
