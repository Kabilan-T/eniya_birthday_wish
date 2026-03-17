#!/usr/bin/env python3
"""
Birthday animation for Eniya.
Each letter of ENIYA is drawn stroke by stroke using mathematical functions.
Formulas are displayed on screen as each stroke is drawn.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pathlib import Path

# ── Config ────────────────────────────────────────────────────────────────────
FPS           = 30
STROKE_FRAMES = 26      # frames to animate one stroke
HOLD_FRAMES   = 90      # hold on final frame
LINE_WIDTH    = 7.0

# Colours
BG         = '#0d1117'
C_LETTER   = '#ff79c6'   # pink  — the drawn strokes
C_FORMULA  = '#8be9fd'   # cyan  — formula text
C_TITLE    = '#f8f8f2'   # white — "Happy Birthday"

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
LETTERS = [
    {'char': 'E', 'strokes': [
        v(0.0, 1.0, 0.0, 'x = 0'),            # backbone  top → bottom
        h(1.0, 0.0, 1.0, 'y = 1'),            # top bar
        h(0.5, 0.0, 0.8, 'y = 0.5'),          # middle bar
        h(0.0, 0.0, 1.0, 'y = 0'),            # bottom bar
    ]},
    {'char': 'N', 'strokes': [
        v(0.0, 0.0, 1.0, 'x = 0'),            # left post
        d(0.0, 1.0, 1.0, 0.0, 'y = 1 - x'),  # diagonal
        v(1.0, 0.0, 1.0, 'x = 1'),            # right post
    ]},
    {'char': 'I', 'strokes': [
        v(0.5, 0.0, 1.0, 'x = 0'),            # single vertical
    ]},
    {'char': 'Y', 'strokes': [
        d(0.0, 1.0, 0.5, 0.5, 'y = -x'),     # left arm  top → centre
        d(1.0, 1.0, 0.5, 0.5, 'y = x'),      # right arm top → centre
        v(0.5, 0.5, 0.0, 'x = 0'),            # stem      centre → bottom
    ]},
    {'char': 'A', 'strokes': [
        d(0.0, 0.0, 0.5, 1.0, 'y = 1 + x'),  # left leg  bottom → apex
        d(1.0, 0.0, 0.5, 1.0, 'y = 1 - x'),  # right leg bottom → apex
        h(0.35, 0.15, 0.85, 'y = 1 - |x|'),  # crossbar
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

fig, ax = plt.subplots(figsize=(14, 8))
fig.patch.set_facecolor(BG)
ax.set_facecolor(BG)
ax.set_xlim(-PAD_L, total_w + PAD_R)
ax.set_ylim(-PAD_B, 1.0 + PAD_T)
ax.set_aspect('equal')
ax.axis('off')

# ── Static title — auto-sized to span the full axes width ─────────────────────
title = ax.text(
    total_w / 2, 1.0 + 1.3,
    'Happy 30th Birthday',
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

# ── Signature ─────────────────────────────────────────────────────────────────
ax.text(
    total_w + PAD_R - 0.05, -PAD_B + 0.1,
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

def stroke_xy(s, x_off, t):
    """Return (xs, ys) for stroke s at progress t ∈ [0, 1]."""
    t = float(np.clip(t, 0.0, 1.0))
    if s['kind'] == 'h':
        xe = s['x0'] + t * (s['x1'] - s['x0'])
        return [x_off + s['x0'], x_off + xe], [s['y'], s['y']]
    elif s['kind'] == 'v':
        ye = s['y0'] + t * (s['y1'] - s['y0'])
        return [x_off + s['x'], x_off + s['x']], [s['y0'], ye]
    else:  # diagonal
        xe = s['x0'] + t * (s['x1'] - s['x0'])
        ye = s['y0'] + t * (s['y1'] - s['y0'])
        return [x_off + s['x0'], x_off + xe], [s['y0'], ye]

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
        x_off = LETTERS[li]['x_off']
        if i < stroke_idx or holding:
            xs, ys = stroke_xy(s, x_off, 1.0)
        elif i == stroke_idx:
            xs, ys = stroke_xy(s, x_off, t)
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

import sys

if '--save' in sys.argv:
    # Export mode: python animate.py --save
    Path('output').mkdir(exist_ok=True)
    out = 'output/birthday_eniya.mp4'
    writer = animation.FFMpegWriter(fps=FPS, bitrate=2000,
                                    metadata={'title': 'Happy Birthday Eniya'})
    ani.save(out, writer=writer, dpi=120)
    print(f'Saved → {out}')
    # Export last frame as PNG
    update(TOTAL_FRAMES - 1)
    png_out = 'output/birthday_eniya.png'
    fig.savefig(png_out, dpi=120, facecolor=BG)
    print(f'Saved → {png_out}')
    plt.close(fig)
else:
    # Default: just show the animation (used by the .exe)
    plt.show()
