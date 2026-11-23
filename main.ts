// NEON SERPENT entry program for the make.fun "agent builds a game" bounty.
//
// The entry itself is the X post named in POST.json; this program's whole
// job is to hand that file to the grader: it copies POST.json from the
// repository directory into the output directory, byte for byte, and exits.
// Outside the grader, MAKEFUN_BOT_DIR / MAKEFUN_OUTPUT_DIR point at the two
// directories; inside it they default to /bot and /output.

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const botDir = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(outputDir, { recursive: true });

const source = join(botDir, 'POST.json');
const target = join(outputDir, 'POST.json');
try {
  copyFileSync(source, target);
} catch (err) {
  console.error(`could not copy ${source} -> ${target}: ${(err as Error).message}`);
  process.exit(1);
}
