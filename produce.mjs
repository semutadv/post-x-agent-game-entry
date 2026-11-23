// produce.mjs — builds video.mp4 for the NEON SERPENT make.fun entry.
//
// Pipeline:
//   1. fetch the official make.fun referral end card (9:16, solid magenta)
//   2. render all main-video frames with frames.py (PIL drawing code)
//   3. encode the 36 s main video from the frames
//   4. conform the card to 30 fps and draw the referral code into its field
//      (visible from 1.5 s into the card to its end; the card is otherwise
//      used exactly as downloaded)
//   5. concatenate main + card, add a silent AAC track, faststart
//   6. verify with ffprobe and extract three still frames for eyeballing

import { execFileSync } from 'node:child_process';
import { existsSync, statSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const DIR = dirname(fileURLToPath(import.meta.url));
const CARD_URL = 'https://make.fun/press/referral-card/9x16/makefun-card-9x16.mp4';
const CARD = join(DIR, 'card-src.mp4');
const REFERRAL_CODE = 'z9fk2tgw';
const MONO_BOLD = '/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf';

function run(cmd, args) {
  console.log('+', cmd, args.join(' '));
  execFileSync(cmd, args, { stdio: 'inherit' });
}

// 1. the end card, straight from make.fun's press pack
if (!existsSync(CARD)) {
  run('curl', ['-sL', '-o', CARD, CARD_URL]);
}
console.log('card bytes:', statSync(CARD).size);

// 2. frames
run('python3', [join(DIR, 'frames.py')]);

// 3. main video: 36 s, 1080x1920, 30 fps
run('ffmpeg', ['-y', '-framerate', '30', '-i', join(DIR, 'frames', 'f_%04d.png'),
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30',
  '-preset', 'medium', '-crf', '18', join(DIR, 'main.mp4')]);

// 4. card segment: fps conformed; referral code typed into its field
//    field box: x=210 y=1232 w=510 h=78 (centre_y 1271) on the 1080x1920 card
const drawtext = [
  `fontfile=${MONO_BOLD}`,
  `text=${REFERRAL_CODE}`,
  'fontsize=62',
  'fontcolor=0x191419',
  'x=210+(510-text_w)/2',
  'y=1232+(78-text_h)/2',
  "enable='between(t,1.5,3)'",
].join(':');
run('ffmpeg', ['-y', '-i', CARD,
  '-vf', `fps=30,drawtext=${drawtext}`,
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-r', '30', '-crf', '18', '-an',
  join(DIR, 'card-seg.mp4')]);

// 5. final assembly: main + card, silent AAC, faststart
run('ffmpeg', ['-y', '-i', join(DIR, 'main.mp4'), '-i', join(DIR, 'card-seg.mp4'),
  '-f', 'lavfi', '-i', 'anullsrc=cl=stereo:r=48000',
  '-filter_complex', '[0:v][1:v]concat=n=2:v=1:a=0[v]',
  '-map', '[v]', '-map', '2:a',
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-shortest',
  '-movflags', '+faststart', join(DIR, 'video.mp4')]);

// 6. verify + stills
const probe = execFileSync('ffprobe', ['-v', 'error',
  '-show_entries', 'stream=codec_name,width,height,r_frame_rate',
  '-show_entries', 'format=duration,size',
  '-of', 'default=noprint_wrappers=1', join(DIR, 'video.mp4')], { encoding: 'utf8' });
console.log('--- ffprobe video.mp4 ---\n' + probe);
for (const [t, name] of [[1.5, 'still-hook'], [25, 'still-gameplay'], [37.8, 'still-endcard']]) {
  run('ffmpeg', ['-y', '-ss', String(t), '-i', join(DIR, 'video.mp4'),
    '-frames:v', '1', join(DIR, `${name}.png`)]);
}
console.log('done: video.mp4', statSync(join(DIR, 'video.mp4')).size, 'bytes');
