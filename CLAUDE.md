# Birthday Animation — Project Brief

## Concept

A mathematical letter animation created as a birthday gift. Each letter of the name **ENIYA** is drawn stroke by stroke using mathematical functions, animated in matplotlib. The final deliverable is an **MP4 video**.

The idea: each stroke is a mathematical function, and the formula is displayed on screen as the stroke is drawn — making the math itself part of the gift.

---

## What is Being Written

- **"Happy Birthday"** — written as plain text/characters, not plotted
- **"Eniya"** — each letter plotted mathematically, stroke by stroke, animated

---

## Letters and Their Mathematical Strokes

### I
- `x = 0` — single vertical line. One formula, cleanest letter.

### Y
- Upper left arm: `y = -x` for `x ∈ [-1, 0]`
- Upper right arm: `y = x` for `x ∈ [0, 1]`
- Stem: `x = 0` for `y ∈ [-1, 0]`
- 3 strokes total

### A
- Left side: `y = 1 - x` (or equivalent slope)
- Right side: `y = 1 + x` (or equivalent slope)  
- Crossbar: `y = 0.3` for `x ∈ [-0.5, 0.5]`
- 3 strokes total. The roof shape is `y = 1 - |x|`

### N
- Left vertical: `x = -1` for `y ∈ [0, 1]`
- Diagonal: line from top-left to bottom-right
- Right vertical: `x = 1` for `y ∈ [0, 1]`
- 3 strokes, all line segments

### E
- Vertical back: `x = 0` for `y ∈ [0, 1]`
- Top horizontal: `y = 1` for `x ∈ [0, 1]`
- Middle horizontal: `y = 0.5` for `x ∈ [0, 0.8]`
- Bottom horizontal: `y = 0` for `x ∈ [0, 1]`
- 4 strokes total

---

## Animation Behaviour

- Each stroke **grows incrementally** — horizontal strokes sweep along x, vertical strokes sweep along y
- As each stroke draws, its **formula is displayed** on screen (stacking per letter)
- Once a letter is complete, all its strokes **offset to the left**
- Next letter begins drawing in position
- **One clean pass** through all 5 letters, then hold on final frame
- No looping

---

## Deliverables

1. **MP4 video** — main gift deliverable, works on all platforms
2. **Windows .exe** — built via PyInstaller, bonus shareable executable for Windows

---

## Tech Stack

- **Language:** Python
- **Library:** Matplotlib (animation)
- **Video export:** `matplotlib.animation.FFMpegWriter` → MP4
- **Executable:** PyInstaller → single file `.exe` for Windows

---

## Status

- [x] Concept finalised
- [x] Letters and stroke breakdown discussed
- [x] Animation behaviour agreed
- [x] Deliverable format decided
- [ ] Stroke order per letter to be finalised
- [ ] Code to be written
- [ ] MP4 export
- [ ] PyInstaller packaging

---

## Notes for Claude Code

- Do not write "Happy Birthday" as plotted functions — plain text only
- Only ENIYA is plotted mathematically
- Stroke order should feel natural, like handwriting (top to bottom, left to right generally)
- Formula display should stack on screen per letter, cleared when next letter begins
- Fixed character width units needed for consistent spacing between letters
- Y and A involve `|x|` — sweep x and compute y, not a straight line growth
- Keep formulas simple and human-readable — the formula shown on screen is part of the gift aesthetic
