#!/usr/bin/env python3
"""Frame renderer for the NEON SERPENT make.fun clip.

Draws every frame of the 36-second main video (1080x1920, 30 fps) with PIL:
hook, prompt card, code-editor montage, live gameplay, CTA. The gameplay
frames are produced by a port of game.html's own rules (24x24 grid, tick
150 ms shrinking 6 ms per orb to a 60 ms floor, +10 per orb) driven by a
deterministic orb-seeking AI, so what is on screen is the real game running.
"""
import math, os, random, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H, FPS = 1080, 1920, 30
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames")
GAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "game.html")
os.makedirs(OUT, exist_ok=True)

BG      = (5, 6, 15)
PANEL   = (13, 17, 32)
PANEL2  = (10, 13, 26)
EDGE    = (38, 48, 84)
TEXT    = (215, 249, 255)
DIM     = (110, 135, 175)
FAINT   = (70, 84, 120)
CYAN    = (43, 255, 232)
MAGENTA = (255, 45, 120)
VIOLET  = (176, 45, 255)
GREEN   = (126, 231, 135)
ORANGE  = (255, 180, 84)
PINK    = (255, 121, 198)
COMMENT = (96, 108, 140)
CODEFG  = (188, 204, 232)

F = "/usr/share/fonts/truetype/dejavu/"
def font(name, size): return ImageFont.truetype(F + name, size)
BOLD  = "DejaVuSans-Bold.ttf"
MONO  = "DejaVuSansMono.ttf"
MONOB = "DejaVuSansMono-Bold.ttf"

def clamp01(v): return max(0.0, min(1.0, v))
def fade(t, a, b): return clamp01((t - a) / (b - a))

def base_frame():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for x in range(0, W + 1, 60):
        d.line([(x, 0), (x, H)], fill=(10, 12, 26))
    for y in range(0, H + 1, 60):
        d.line([(0, y), (W, y)], fill=(10, 12, 26))
    return img

def glow_text(img, xy, s, fnt, color, glow=None, anchor="mm", blur=16, strength=2):
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, s, font=fnt, fill=(glow or color) + (255,), anchor=anchor)
    layer = layer.filter(ImageFilter.GaussianBlur(blur))
    for _ in range(strength):
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    d2 = ImageDraw.Draw(img)
    d2.text(xy, s, font=fnt, fill=color, anchor=anchor)

def text_alpha(img, xy, s, fnt, color, alpha, anchor="mm"):
    if alpha <= 0: return
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.text(xy, s, font=fnt, fill=color + (int(255 * alpha),), anchor=anchor)
    img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))

def rrect(d, box, r, **kw):
    d.rounded_rectangle(box, radius=r, **kw)

# ---------------------------------------------------------------- hook scene
def scene_hook(t):
    img = base_frame()
    cx = W // 2
    a1 = fade(t, 0.15, 0.65)
    text_alpha(img, (cx, 700), "I gave my AI agent", font(BOLD, 66), TEXT, a1)
    a2 = fade(t, 0.55, 1.05)
    if a2 > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.text((cx, 830), "ONE prompt.", font=font(BOLD, 118), fill=CYAN + (int(255 * a2),), anchor="mm")
        glow = layer.filter(ImageFilter.GaussianBlur(18))
        img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    a3 = fade(t, 1.75, 2.25)
    text_alpha(img, (cx, 1010), "It built a whole game.", font(BOLD, 66), TEXT, a3)
    a4 = fade(t, 2.35, 2.8)
    if a4 > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.text((cx, 1140), "Watch.", font=font(BOLD, 118), fill=MAGENTA + (int(255 * a4),), anchor="mm")
        glow = layer.filter(ImageFilter.GaussianBlur(18))
        img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    return img

# ------------------------------------------------------------- prompt scene
PROMPT = ("Build NEON SERPENT: a one-file browser snake game. Neon glow on a dark grid, "
          "arrow keys and touch, speed climbs as you eat, score and best on screen, "
          "game-over screen. No libraries.")

def wrap_text(s, fnt, maxw):
    words, lines, cur = s.split(), [], ""
    dummy = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if dummy.textlength(trial, font=fnt) <= maxw: cur = trial
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

PROMPT_FONT = font(MONO, 41)
PROMPT_LINES = wrap_text(PROMPT, PROMPT_FONT, 860)

def scene_prompt(t):
    img = base_frame()
    d = ImageDraw.Draw(img)
    d.text((W // 2, 470), "T H E   P R O M P T", font=font(MONOB, 40), fill=DIM, anchor="mm")
    rrect(d, (70, 600, 1010, 1300), 28, fill=PANEL, outline=EDGE, width=2)
    d.ellipse((110, 648, 166, 704), fill=CYAN)
    d.text((138, 676), "A", font=font(BOLD, 34), fill=(4, 20, 24), anchor="mm")
    d.text((190, 676), "you  →  AI agent", font=font(MONO, 36), fill=DIM, anchor="lm")
    d.line([(110, 740), (970, 740)], fill=EDGE, width=2)
    # typewriter: full prompt over 3.1 s starting at local 0.2 s
    local = t - 3.5
    n = int(clamp01((local - 0.2) / 3.1) * len(PROMPT))
    typed = PROMPT[:n]
    lines = wrap_text(typed, PROMPT_FONT, 860) if typed else []
    y = 800
    for ln in lines:
        d.text((110, y), ln, font=PROMPT_FONT, fill=TEXT, anchor="lm")
        y += 62
    if int(local * 2.2) % 2 == 0 and n < len(PROMPT) + 40:
        last = lines[-1] if lines else ""
        cx = 110 + d.textlength(last, font=PROMPT_FONT)
        cy = y - 62
        d.rectangle((cx + 6, cy - 26, cx + 30, cy + 26), fill=CYAN)
    return img

# --------------------------------------------------------------- code scene
GAME_LINES = open(GAME, encoding="utf-8").read().split("\n")
TOTAL_LINES = len(GAME_LINES)
KEYWORDS = {"const", "let", "var", "function", "return", "if", "else", "for",
            "while", "new", "of", "in", "break", "continue", "typeof"}

def color_line(d, x, y, line, fnt):
    """Tiny syntax highlighter: comments, strings, keywords, numbers."""
    s = line.rstrip()
    if len(s) > 46: s = s[:45] + "…"
    stripped = s.lstrip()
    if stripped.startswith("//") or stripped.startswith("<!--"):
        d.text((x, y), s, font=fnt, fill=COMMENT, anchor="lm"); return
    i = 0
    cx = x
    dummy = d
    while i < len(s):
        ch = s[i]
        if ch in "\"'`":
            j = s.find(ch, i + 1)
            j = len(s) if j < 0 else j + 1
            seg, col = s[i:j], GREEN
        elif ch.isdigit():
            j = i
            while j < len(s) and (s[j].isdigit() or s[j] in ".xabcdefABCDEF"): j += 1
            seg, col = s[i:j], ORANGE
        elif ch.isalpha() or ch in "_$":
            j = i
            while j < len(s) and (s[j].isalnum() or s[j] in "_$"): j += 1
            seg = s[i:j]
            col = PINK if seg in KEYWORDS else CODEFG
        else:
            j = i + 1; seg, col = ch, CODEFG
        dummy.text((cx, y), seg, font=fnt, fill=col, anchor="lm")
        cx += dummy.textlength(seg, font=fnt)
        i = j

CHECKLIST = [("canvas grid", 9.0), ("keyboard + touch input", 10.6),
             ("collision rules", 12.2), ("score + best", 13.8),
             ("game-over screen", 15.2)]

def scene_code(t):
    img = base_frame()
    d = ImageDraw.Draw(img)
    local = t - 7.0
    # editor panel
    rrect(d, (40, 300, 1040, 1500), 22, fill=PANEL2, outline=EDGE, width=2)
    d.rounded_rectangle((40, 300, 1040, 386), radius=22, fill=PANEL)
    d.rectangle((40, 350, 1040, 386), fill=PANEL)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse((72 + i * 44, 328, 100 + i * 44, 356), fill=c)
    d.text((230, 343), "game.html", font=font(MONO, 34), fill=DIM, anchor="lm")
    # reveal count: eased acceleration over the montage
    p = clamp01(local / 8.6) ** 1.55
    revealed = max(1, int(p * TOTAL_LINES)) if local > 0 else 1
    if local >= 8.55: revealed = TOTAL_LINES
    counter = f"LINES {revealed:3d} / {TOTAL_LINES}"
    d.text((1010, 343), counter, font=font(MONOB, 34), fill=CYAN, anchor="rm")
    # code window: last 24 revealed lines
    vis = 24
    start = max(0, revealed - vis)
    fnt = font(MONO, 30)
    y = 430
    for idx in range(start, revealed):
        line = GAME_LINES[idx] if idx < len(GAME_LINES) else ""
        if idx == revealed - 1:
            d.rectangle((58, y - 21, 1022, y + 21), fill=(24, 44, 66))
        d.text((86, y), f"{idx + 1:3d}", font=fnt, fill=FAINT, anchor="lm")
        color_line(d, 170, y, line, fnt)
        y += 42
    # checklist panel
    rrect(d, (40, 1540, 1040, 1850), 22, fill=PANEL2, outline=EDGE, width=2)
    d.text((76, 1586), "AGENT CHECKLIST", font=font(MONOB, 32), fill=DIM, anchor="lm")
    iy = 1652
    for label, when in CHECKLIST:
        done = t >= when
        box = (76, iy - 19, 114, iy + 19)
        d.rounded_rectangle(box, radius=6, outline=(GREEN if done else FAINT), width=3)
        if done:
            d.line([(84, iy), (95, iy + 11)], fill=GREEN, width=5)
            d.line([(95, iy + 11), (108, iy - 12)], fill=GREEN, width=5)
        d.text((140, iy), label, font=font(MONO, 37),
               fill=(TEXT if done else FAINT), anchor="lm")
        iy += 47
    return img

# ----------------------------------------------------------- gameplay scene
COLS, ROWS = 24, 24
START_MS, MIN_MS, STEP_MS = 150, 60, 6
CELL, BX, BY = 40, 60, 450

def ai_dir(snake, orb, cur):
    hx, hy = snake[0]
    body = set(map(tuple, snake))
    cands = []
    for order, (dx, dy) in enumerate([(cur), (0, -1), (1, 0), (0, 1), (-1, 0)]):
        if (dx, dy) == (-cur[0], -cur[1]): continue
        nx, ny = hx + dx, hy + dy
        if not (0 <= nx < COLS and 0 <= ny < ROWS): continue
        eating = (nx, ny) == orb
        blocked = body if eating else body - {tuple(snake[-1])}
        if (nx, ny) in blocked: continue
        # flood fill the space reachable after the move (safety)
        after = (blocked | {(nx, ny)})
        seen, stack = {(nx, ny)}, [(nx, ny)]
        while stack:
            cx, cy = stack.pop()
            for ax, ay in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                q = (cx + ax, cy + ay)
                if q not in seen and q not in after and 0 <= q[0] < COLS and 0 <= q[1] < ROWS:
                    seen.add(q); stack.append(q)
        area = len(seen)
        dist = abs(nx - orb[0]) + abs(ny - orb[1])
        cands.append((dist * 100 - min(area, 60), order, (dx, dy)))
    if not cands: return cur
    cands.sort()
    return cands[0][2]

def simulate(seed, seconds=17.0):
    rng = random.Random(seed)
    snake = [(11, 12), (10, 12), (9, 12), (8, 12)]
    cur = (1, 0)
    def place():
        taken = set(snake)
        free = [(x, y) for y in range(ROWS) for x in range(COLS) if (x, y) not in taken]
        return free[rng.randrange(len(free))]
    orb = place()
    tick_ms, score, orbs = START_MS, 0, 0
    states = [(0.0, list(snake), orb, score, tick_ms, orbs)]
    t, acc, nearmiss = 0.0, 0.0, None
    step = 1.0 / FPS
    while t < seconds:
        acc += step * 1000.0
        while acc >= tick_ms:
            acc -= tick_ms
            t_tick = t
            cur = ai_dir(snake, orb, cur)
            hx, hy = snake[0][0] + cur[0], snake[0][1] + cur[1]
            eating = (hx, hy) == orb
            body = snake if eating else snake[:-1]
            if not (0 <= hx < COLS and 0 <= hy < ROWS) or (hx, hy) in body:
                return None  # died: seed rejected
            snake = [(hx, hy)] + (snake if eating else snake[:-1])
            if eating:
                score += 10; orbs += 1
                tick_ms = max(MIN_MS, tick_ms - STEP_MS)
                orb = place()
            if nearmiss is None:
                for seg in snake[4:]:
                    if abs(seg[0] - hx) + abs(seg[1] - hy) == 1:
                        nearmiss = t_tick; break
            states.append((t, list(snake), orb, score, tick_ms, orbs))
        t += step
    return states, score, orbs, nearmiss

def pick_simulation():
    for seed in range(1, 400):
        r = simulate(seed)
        if r and r[1] >= 140 and r[2] >= 14 and r[3] is not None:
            return seed, r
    raise SystemExit("no seed produced a full run")

SIM_SEED, (STATES, FINAL_SCORE, FINAL_ORBS, NEARMISS_T) = pick_simulation()

def state_at(time_s):
    cur = STATES[0]
    for s in STATES:
        if s[0] <= time_s: cur = s
        else: break
    return cur

def draw_board(img, state, t_now, flash_until=-1):
    _, snake, orb, score, tick_ms, orbs = state
    d = ImageDraw.Draw(img, "RGBA")
    glow_text(img, (W // 2, 268), "NEON SERPENT", font(BOLD, 66), CYAN, blur=14, strength=1)
    d = ImageDraw.Draw(img, "RGBA")
    d.text((70, 386), f"SCORE {score:04d}", font=font(MONOB, 46), fill=TEXT, anchor="lm")
    d.text((1010, 386), f"BEST {score:04d}", font=font(MONOB, 46), fill=DIM, anchor="rm")
    # board
    d.rectangle((BX - 4, BY - 4, BX + COLS * CELL + 4, BY + ROWS * CELL + 4),
                outline=(23, 58, 77), width=3)
    d.rectangle((BX, BY, BX + COLS * CELL, BY + ROWS * CELL), fill=(7, 8, 24))
    for x in range(1, COLS):
        d.line([(BX + x * CELL, BY), (BX + x * CELL, BY + ROWS * CELL)], fill=(30, 34, 70))
    for y in range(1, ROWS):
        d.line([(BX, BY + y * CELL), (BX + COLS * CELL, BY + y * CELL)], fill=(30, 34, 70))
    # orb
    pulse = 1 + 0.18 * math.sin(t_now * 6.0)
    ocx, ocy = BX + orb[0] * CELL + CELL // 2, BY + orb[1] * CELL + CELL // 2
    r = int((CELL / 2 - 4) * pulse)
    d.ellipse((ocx - r - 9, ocy - r - 9, ocx + r + 9, ocy + r + 9), fill=MAGENTA + (70,))
    d.ellipse((ocx - r, ocy - r, ocx + r, ocy + r), fill=MAGENTA + (255,))
    d.ellipse((ocx - 4, ocy - 4, ocx + 4, ocy + 4), fill=(255, 215, 234, 255))
    # snake with glow pass
    def mix(a, b, tt):
        return tuple(int(a[i] + (b[i] - a[i]) * tt) for i in range(3))
    n = len(snake)
    for i in range(n - 1, -1, -1):
        sx, sy = snake[i]
        tt = 0 if n <= 1 else i / (n - 1)
        col = CYAN if i == 0 else mix(CYAN, VIOLET, tt)
        x0, y0 = BX + sx * CELL, BY + sy * CELL
        pad = 3 if i == 0 else 5
        d.rounded_rectangle((x0 + pad - 5, y0 + pad - 5, x0 + CELL - pad + 5, y0 + CELL - pad + 5),
                            radius=10, fill=col + (60,))
        d.rounded_rectangle((x0 + pad, y0 + pad, x0 + CELL - pad, y0 + CELL - pad),
                            radius=8, fill=col + (255,))
    hx, hy = snake[0]
    ex, ey = BX + hx * CELL + CELL // 2, BY + hy * CELL + CELL // 2
    d.ellipse((ex - 4, ey - 10, ex + 4, ey - 2), fill=(4, 34, 43, 255))
    d.ellipse((ex - 4, ey + 2, ex + 4, ey + 10), fill=(4, 34, 43, 255))
    # speed row
    frac = (START_MS - tick_ms) / (START_MS - MIN_MS)
    d.text((70, 1480), "SPEED", font=font(MONOB, 40), fill=DIM, anchor="lm")
    d.rounded_rectangle((240, 1462, 830, 1498), radius=18, outline=EDGE, width=2)
    if frac > 0:
        d.rounded_rectangle((244, 1466, 244 + int(582 * frac), 1494), radius=14,
                            fill=MAGENTA)
    d.text((1010, 1480), f"×{START_MS / tick_ms:.1f}", font=font(MONOB, 44), fill=MAGENTA, anchor="rm")
    if t_now < flash_until:
        glow_text(img, (W // 2, BY + 480), "SPEED UP!", font(BOLD, 84), MAGENTA, blur=14, strength=1)
    d.text((W // 2, 1620), "the finished game — running live", font=font(MONO, 34),
           fill=FAINT, anchor="mm")

def scene_gameplay(t):
    img = base_frame()
    local = t - 16.0
    state = state_at(local)
    # flash for 0.6 s after every 4th orb (based on the state where it happened)
    flash_until = -1
    prev_orbs = 0
    for s in STATES:
        if s[5] != prev_orbs and s[5] % 4 == 0 and s[0] <= local < s[0] + 0.6:
            flash_until = local + 1  # any value > local triggers; recompute below
            flash_until = s[0] + 0.6
        prev_orbs = s[5]
    draw_board(img, state, local, flash_until=flash_until if flash_until > local else -1)
    return img

def scene_cta(t):
    img = scene_gameplay(33.0)
    dark = Image.new("RGB", (W, H), (2, 2, 8))
    img = Image.blend(img, dark, 0.55)
    a = fade(t, 33.1, 33.6)
    if a > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.text((W // 2, 800), "Built from ONE prompt.", font=font(BOLD, 82),
               fill=TEXT + (int(255 * a),), anchor="mm")
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    a2 = fade(t, 33.8, 34.3)
    if a2 > 0:
        layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        d.text((W // 2, 950), "Come build yours on", font=font(BOLD, 56),
               fill=TEXT + (int(255 * a2),), anchor="mm")
        d.text((W // 2, 1064), "make.fun", font=font(BOLD, 96),
               fill=CYAN + (int(255 * a2),), anchor="mm")
        glow = layer.filter(ImageFilter.GaussianBlur(14))
        img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
        img.paste(Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB"), (0, 0))
    return img

# ------------------------------------------------------------------- driver
def main():
    total = 36 * FPS
    for i in range(total):
        t = i / FPS
        if t < 3.5: img = scene_hook(t)
        elif t < 7.0: img = scene_prompt(t)
        elif t < 16.0: img = scene_code(t)
        elif t < 33.0: img = scene_gameplay(t)
        else: img = scene_cta(t)
        img.save(os.path.join(OUT, f"f_{i:04d}.png"))
        if i % 180 == 0: print(f"frame {i}/{total}", flush=True)
    print(f"SIM seed={SIM_SEED} final_score={FINAL_SCORE} orbs={FINAL_ORBS} "
          f"near_miss_at={NEARMISS_T:.1f}s total_lines={TOTAL_LINES}")
    print("frames done:", total)

if __name__ == "__main__":
    main()
