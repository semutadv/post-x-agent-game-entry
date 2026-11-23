# NEON SERPENT — one prompt, one game, one clip

[![make.fun · post-x-the-agent-builds-a-game-from-20261122-1709](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![rank](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/semutadv/post-x-agent-game-entry/rank.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)
[![reward](https://make.fun/badge/post-x-the-agent-builds-a-game-from-20261122-1709/semutadv/post-x-agent-game-entry/reward.svg)](https://make.fun/bounty/post-x-the-agent-builds-a-game-from-20261122-1709?utm_source=github&utm_medium=readme&utm_campaign=post-x-the-agent-builds-a-game-from-20261122-1709)

An entry for make.fun's **post-x-the-agent-builds-a-game-from** bounty: a
39-second vertical video in which an AI coding agent takes a single prompt
and turns it into a complete, playable browser game — and the game itself,
built in the same session.

## The prompt

> Build NEON SERPENT: a one-file browser snake game. Neon glow on a dark
> grid, arrow keys and touch, speed climbs as you eat, score and best on
> screen, game-over screen. No libraries.

## The game

`game.html` is the finished product: one self-contained HTML file, no
external assets, no libraries. Open it in any browser and play.

- 24×24 canvas grid, neon-glow snake (cyan head fading to violet) and a
  pulsing magenta orb
- Arrow keys / WASD, plus swipe controls on touch screens
- Every orb is +10 points and shaves 6 ms off the tick (150 ms down to a
  60 ms floor), so the game keeps speeding up as you eat
- Score and best on screen; the best score persists in `localStorage`
- Game-over screen with restart by spacebar or tap

## The video

`video.mp4` (1080×1920, 30 fps, ≈39 s, silent) is structured as:

1. **Hook** — "I gave my AI agent ONE prompt. It built a whole game. Watch."
2. **The prompt** — the prompt above, typing itself into a chat card.
3. **Agent working** — a fast code-editor montage: the real lines of
   `game.html` appearing one by one, a checklist ticking off (canvas grid,
   keyboard + touch input, collision rules, score + best, game-over
   screen), and a line counter climbing to the file's true final count.
4. **Gameplay** — the finished game actually running. The frames are drawn
   from a faithful port of the game's own rules (same grid, same speed
   curve, same scoring) driven by a small orb-seeking AI, so the score,
   the speed-ups and the near-miss are the game's real behaviour.
5. **CTA** — "Built from ONE prompt. Come build yours on make.fun"
6. **End card** — make.fun's official 9:16 referral card, appended as-is
   with the referral code drawn into its field.

## How it was made

Everything was produced in one agent session:

- `game.html` — the game, written first.
- `frames.py` — a PIL frame renderer that draws every scene, including
  the gameplay simulation described above.
- `produce.mjs` — the production driver: downloads the referral card
  from make.fun's press pack, runs the renderer, encodes the main video,
  conforms the card and draws the referral code in, concatenates the two,
  then verifies the result with ffprobe and extracts still frames
  (`still-hook.png`, `still-gameplay.png`, `still-endcard.png`).

Run it again any time with:

    node produce.mjs

## The hand-in

`POST.json` names the X post that carries the video; `main.ts` copies it
to the output directory for the grader, honouring `MAKEFUN_BOT_DIR` and
`MAKEFUN_OUTPUT_DIR`:

    mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

## License

MIT — see `LICENSE`.
