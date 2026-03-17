#!/usr/bin/env python3
"""
Birthday animation for Eniya.
Each letter of ENIYA is drawn stroke by stroke using mathematical functions.
Formulas are displayed on screen as each stroke is drawn.
"""

import argparse
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path
from datetime import date

# ── Argument parsing ───────────────────────────────────────────────────────────
parser = argparse.ArgumentParser()
parser.add_argument('--save',        action='store_true', help='Export MP4 + PDF')
parser.add_argument('--sample_date', type=str, default=None,
                    help='Simulate a date (YYYY-MM-DD)')
args, _ = parser.parse_known_args()

if args.sample_date:
    today = date.fromisoformat(args.sample_date)
else:
    today = date.today()

# ── Birthday logic ─────────────────────────────────────────────────────────────
BIRTH_DATE = date(1996, 5, 1)

def ordinal(n):
    if 11 <= (n % 100) <= 13:
        return f'{n}th'
    return f'{n}{["th","st","nd","rd","th"][min(n % 10, 4)]}'

birthday_this_year = BIRTH_DATE.replace(year=today.year)
if today >= birthday_this_year:
    AGE = today.year - BIRTH_DATE.year
else:
    AGE = today.year - BIRTH_DATE.year - 1

TITLE_TEXT = f'Happy {ordinal(AGE)} Birthday'
DAYS_ALIVE = (today - BIRTH_DATE).days

next_bday = BIRTH_DATE.replace(year=today.year)
if next_bday <= today:
    next_bday = BIRTH_DATE.replace(year=today.year + 1)
DAYS_TO_NEXT = (next_bday - today).days

COUNTER_TEXT = f'Days Alive: {DAYS_ALIVE}     |     Next Birthday in: {DAYS_TO_NEXT} days'

# ── Config ────────────────────────────────────────────────────────────────────
FPS           = 30
STROKE_FRAMES = 26      # frames to animate one stroke
HOLD_FRAMES   = 90      # hold on final frame
LINE_WIDTH    = 7.0

# Colours
BG         = '#ffffff'
C_LETTER   = '#00c896'   # northern lights green — the drawn strokes
C_FORMULA  = '#8b00ff'   # purple — formula text
C_TITLE    = '#000000'   # black  — "Happy Birthday"

# Letter geometry (all stroke coords normalised to [0,1] × [0,1])
LETTER_W = 1.0
GAP      = 0.55

# ── Stroke constructors ───────────────────────────────────────────────────────
def h(y, x0, x1, formula):
    """Horizontal: y = const, x sweeps x0 → x1."""
    return dict(kind='h', y=y, x0=x0, x1=x1, formula=formula)

def v(x, y0, y1, formula):
    """Vertical: x = const, y sweeps y0 → y1."""
    return dict(kind='v', x=x, y0=y0, y1=y1, formula=formula)

def d(x0, y0, x1, y1, formula):
    """Diagonal: parametric line from (x0,y0) to (x1,y1)."""
    return dict(kind='d', x0=x0, y0=y0, x1=x1, y1=y1, formula=formula)

# ── Letter definitions ────────────────────────────────────────────────────────
# Strokes are in each letter's NATURAL coordinate system so the formulas
# shown on screen are mathematically exact.  nat_range = (x0, x1, y0, y1).
LETTERS = [
    {'char': 'E', 'nat_range': (0, 1, 0, 1), 'strokes': [
        v(0.0, 1.0, 0.0, 'x = 0'),            # backbone  top → bottom
        h(1.0, 0.0, 1.0, 'y = 1'),            # top bar
        h(0.5, 0.0, 0.8, 'y = 0.5'),          # middle bar
        h(0.0, 0.0, 1.0, 'y = 0'),            # bottom bar
    ]},
    {'char': 'N', 'nat_range': (0, 1, 0, 1), 'strokes': [
        v(0.0, 0.0, 1.0, 'x = 0'),            # left post
        d(0.0, 1.0, 1.0, 0.0, 'y = 1 - x'),  # diagonal
        v(1.0, 0.0, 1.0, 'x = 1'),            # right post
    ]},
    # I: natural x ∈ [-0.5, 0.5] so the stroke x=0 is centred
    {'char': 'I', 'nat_range': (-0.5, 0.5, 0, 1), 'strokes': [
        v(0.0, 0.0, 1.0, 'x = 0'),            # single vertical at x=0
    ]},
    # Y: natural x ∈ [-1,1], y ∈ [-1,1] — arms meet at origin (0,0)
    {'char': 'Y', 'nat_range': (-1, 1, -1, 1), 'strokes': [
        d(-1.0, 1.0, 0.0, 0.0, 'y = -x'),    # left arm  (-1,1)→(0,0)  y=-x ✓
        d( 1.0, 1.0, 0.0, 0.0, 'y = x'),     # right arm (1,1)→(0,0)   y=x  ✓
        v( 0.0, 0.0,-1.0, 'x = 0'),           # stem      (0,0)→(0,-1)  x=0  ✓
    ]},
    # A: natural x ∈ [-1,1], y ∈ [0,1] — apex at (0,1), feet at (±1,0)
    {'char': 'A', 'nat_range': (-1, 1, 0, 1), 'strokes': [
        d(-1.0, 0.0, 0.0, 1.0, 'y = 1 + x'),  # left leg  y=1+x ✓
        d( 1.0, 0.0, 0.0, 1.0, 'y = 1 - x'),  # right leg y=1-x ✓
        h(0.35, -0.7, 0.7, 'y = 1 - |x|'),    # crossbar
    ]},
]

# Assign x offsets
for i, L in enumerate(LETTERS):
    L['x_off'] = i * (LETTER_W + GAP)

# ── Flat stroke list ──────────────────────────────────────────────────────────
all_strokes = []          # (letter_index, stroke_dict)
for li, L in enumerate(LETTERS):
    for s in L['strokes']:
        all_strokes.append((li, s))

N_STROKES    = len(all_strokes)
TOTAL_FRAMES = N_STROKES * STROKE_FRAMES + HOLD_FRAMES

# ── Canvas ────────────────────────────────────────────────────────────────────
total_w = len(LETTERS) * (LETTER_W + GAP) - GAP   # ≈ 7.2 units
PAD_L, PAD_R = 0.5, 0.5
PAD_B        = 1.8    # space below letters for formula stack
PAD_T        = 2.0    # space above for title

fig, ax = plt.subplots(figsize=(19.2, 10.8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(-PAD_L, total_w + PAD_R)
ax.set_ylim(-PAD_B, 1.0 + PAD_T)
ax.set_aspect('equal')
ax.axis('off')

# ── Per-letter grids — drawn in each letter's natural coordinate system ────────
grid_color = '#000000'
axis_color = '#000000'

for L in LETTERS:
    xo = L['x_off']
    nx0, nx1, ny0, ny1 = L['nat_range']

    # Transform helpers (capture loop vars via defaults)
    def tx(gx, _xo=xo, _nx0=nx0, _nx1=nx1):
        return _xo + (gx - _nx0) / (_nx1 - _nx0) * LETTER_W
    def ty(gy, _ny0=ny0, _ny1=ny1):
        return (gy - _ny0) / (_ny1 - _ny0) * 1.0

    # Extend grid 10% beyond natural bounds on all sides
    pad_x = 0.2 * (nx1 - nx0)
    pad_y = 0.2 * (ny1 - ny0)
    gx0, gx1 = nx0 - pad_x, nx1 + pad_x
    gy0, gy1 = ny0 - pad_y, ny1 + pad_y

    sx0, sx1 = tx(gx0), tx(gx1)
    sy0, sy1 = ty(gy0), ty(gy1)

    # 5 evenly-spaced grid ticks at natural coord positions
    x_ticks = np.linspace(nx0, nx1, 5)
    y_ticks = np.linspace(ny0, ny1, 5)

    for gx in x_ticks:
        if abs(gx) > 1e-9:   # skip x=0 — drawn as axis below
            ax.plot([tx(gx), tx(gx)], [sy0, sy1],
                    color=grid_color, lw=0.5, alpha=0.07, zorder=0)
    for gy in y_ticks:
        if abs(gy) > 1e-9:   # skip y=0 — drawn as axis below
            ax.plot([sx0, sx1], [ty(gy), ty(gy)],
                    color=grid_color, lw=0.5, alpha=0.07, zorder=0)

    # y-axis: natural x = 0 (highlighted, full padded height)
    ax.plot([tx(0), tx(0)], [sy0, sy1],
            color=axis_color, lw=1.5, alpha=0.5, zorder=1)
    # x-axis: natural y = 0 (highlighted, full padded width)
    ax.plot([sx0, sx1], [ty(0), ty(0)],
            color=axis_color, lw=1.5, alpha=0.5, zorder=1)

# ── Static title — auto-sized to span the full axes width ─────────────────────
title = ax.text(
    total_w / 2, 1.0 + 1.3,
    TITLE_TEXT,
    ha='center', va='center',
    fontsize=32, fontweight='bold',
    color=C_TITLE, fontfamily='serif',
)
# Measure rendered width and scale fontsize to fill the axes
fig.canvas.draw()
renderer  = fig.canvas.get_renderer()
t_bb      = title.get_window_extent(renderer=renderer)
ax_bb     = ax.get_window_extent(renderer=renderer)
title.set_fontsize(32 * (ax_bb.width * 0.97 / t_bb.width))

# ── Day counter ───────────────────────────────────────────────────────────────
ax.text(
    total_w / 2, -PAD_B + 0.45,
    COUNTER_TEXT,
    ha='center', va='bottom',
    fontsize=14, color=C_FORMULA, alpha=0.7,
    fontfamily='monospace',
)

# ── Signature ─────────────────────────────────────────────────────────────────
ax.text(
    total_w + PAD_R - 0.05, -PAD_B + 0.15,
    '— Aaron Stone',
    ha='right', va='bottom',
    fontsize=13, style='italic',
    color=C_TITLE, alpha=0.35,
    fontfamily='serif',
)

# ── Formula text artists — one per stroke, fixed below its letter ─────────────
# Each starts invisible; becomes visible (alpha=1) when its stroke is drawn
# and stays visible for the rest of the animation.
formula_artists = {}   # key: global stroke index → Text artist
for gi, (li, s) in enumerate(all_strokes):
    # stroke index within this letter
    si = sum(1 for j, (lj, _) in enumerate(all_strokes) if lj == li and j < gi)
    fx = LETTERS[li]['x_off'] + LETTER_W / 2
    fy = -0.22 - si * 0.20
    ft = ax.text(fx, fy, s['formula'],
                 ha='center', va='top',
                 fontsize=13, color=C_FORMULA,
                 fontfamily='monospace', alpha=0.0)
    formula_artists[gi] = ft

# ── Stroke line artists ───────────────────────────────────────────────────────
line_artists = []
for _ in all_strokes:
    ln, = ax.plot([], [], color=C_LETTER, lw=LINE_WIDTH,
                  solid_capstyle='round', solid_joinstyle='round')
    line_artists.append(ln)

# ── Helpers ───────────────────────────────────────────────────────────────────
def ease_inout(t):
    """Smooth acceleration + deceleration."""
    return t * t * (3.0 - 2.0 * t)

def stroke_xy(s, x_off, nat_range, t):
    """Return (xs, ys) for stroke s at progress t ∈ [0, 1].
    Transforms from natural coords → screen coords using nat_range."""
    t = float(np.clip(t, 0.0, 1.0))
    nx0, nx1, ny0, ny1 = nat_range
    def tx(nx): return x_off + (nx - nx0) / (nx1 - nx0) * LETTER_W
    def ty(ny): return (ny - ny0) / (ny1 - ny0) * 1.0
    if s['kind'] == 'h':
        xe = s['x0'] + t * (s['x1'] - s['x0'])
        return [tx(s['x0']), tx(xe)], [ty(s['y']), ty(s['y'])]
    elif s['kind'] == 'v':
        ye = s['y0'] + t * (s['y1'] - s['y0'])
        return [tx(s['x']), tx(s['x'])], [ty(s['y0']), ty(ye)]
    else:  # diagonal
        xe = s['x0'] + t * (s['x1'] - s['x0'])
        ye = s['y0'] + t * (s['y1'] - s['y0'])
        return [tx(s['x0']), tx(xe)], [ty(s['y0']), ty(ye)]

# ── Animation update ──────────────────────────────────────────────────────────
def update(frame):
    holding = frame >= N_STROKES * STROKE_FRAMES

    if holding:
        stroke_idx = N_STROKES - 1
        t = 1.0
    else:
        stroke_idx = frame // STROKE_FRAMES
        raw_t = (frame % STROKE_FRAMES) / STROKE_FRAMES
        t = ease_inout(raw_t)

    # Draw strokes
    for i, (li, s) in enumerate(all_strokes):
        x_off     = LETTERS[li]['x_off']
        nat_range = LETTERS[li]['nat_range']
        if i < stroke_idx or holding:
            xs, ys = stroke_xy(s, x_off, nat_range, 1.0)
        elif i == stroke_idx:
            xs, ys = stroke_xy(s, x_off, nat_range, t)
        else:
            xs, ys = [], []
        line_artists[i].set_data(xs, ys)

    # Reveal formula for every stroke that has been drawn so far
    for gi, ft in formula_artists.items():
        ft.set_alpha(1.0 if (gi < stroke_idx or (gi == stroke_idx and t > 0.05) or holding) else 0.0)

    return line_artists + list(formula_artists.values())

# ── Run ───────────────────────────────────────────────────────────────────────
ani = animation.FuncAnimation(
    fig, update,
    frames=TOTAL_FRAMES,
    interval=1000 // FPS,
    blit=True,
)

if args.save:
    # Export mode: python animate.py --save
    Path('output').mkdir(exist_ok=True)
    out = 'output/birthday_eniya.mp4'
    writer = animation.FFMpegWriter(fps=FPS, bitrate=2000,
                                    metadata={'title': 'Happy Birthday Eniya'})
    ani.save(out, writer=writer, dpi=120)
    print(f'Saved → {out}')
    # Export last frame as PDF
    update(TOTAL_FRAMES - 1)
    pdf_out = 'output/birthday_eniya.pdf'
    fig.savefig(pdf_out, facecolor=BG)
    print(f'Saved → {pdf_out}')
    plt.close(fig)
else:
    # Default: just show the animation (used by the .exe)
    plt.show()
