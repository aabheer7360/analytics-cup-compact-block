# Project log — Compact, but vulnerable?

A plain-language record of each step: what we did, why, how the measures were built, and what might be wrong. Newest step at the bottom. Code details live in the code; this file is for understanding and decisions.

**Status markers:** ✅ done · 🟡 open question · ⚠️ possible problem

---

## Step 0 — Setup (19 Nov 2026)

**What:** downloaded the SkillCorner open data and installed the Python tools.

- Data: [SkillCorner/opendata](https://github.com/SkillCorner/opendata), version `4340d27` (the same version inspected in October).
- 20 matches; each has four files (match sheet, tracking, events, phases). See `docs/DATA_REFERENCE.md`.
- Tracking files are large (1.8 GB in total) and stored separately on GitHub. All 20 were downloaded and checked against their published checksums.
- Competition deadline: 18 December 2026. Only SkillCorner data may be used.

---

## Step 1 — Choosing the topic (19 Nov)

**Question:** which of two ideas is stronger?
- **A.** "Compact, but vulnerable?": how attackers still get inside a compact block.
- **B.** "Dangerous runs left unused": which threatening runs teammates ignore.

**How:** quick tests on the event data for all 20 matches (scripts in `exploration/`).

**Idea A test.** We took every medium- and low-block phase (3,737 usable). Compactness was SkillCorner's own width × length of the defending team at the start of each phase. We asked whether the attackers got a player on the ball *inside the defensive shape*, in the centre or half-spaces, in the middle or final third (our working definition of a **breach**).

| Medium block, by compactness | Most compact | 2 | 3 | Least compact |
|---|---|---|---|---|
| Phases with a breach | 26% | 41% | 45% | 50% |

Compact blocks were breached about half as often, but still about a quarter of the time. They did not concede fewer shots or breaks of the last line.

**Idea B test.** 18% of passes had a "dangerous" receiver available; 57% of those went to one. Dangerous runs were picked slightly less often than other runs (38% vs 41%).

**Decision:** Idea A. SkillCorner already publishes targeted/received/dangerous run counts per player, so B would be hard to make original. A needs frame-by-frame measurement from tracking, which nobody publishes, and it fits the "Defensive Positioning" theme other entrants mention.

**What went wrong along the way:**
- ⚠️ *Bug 1, fixed.* Missing values were counted as "dangerous". In pandas, an empty cell can count as true when you ask "is any value true?". This made it look as if 96% of passes had a dangerous option. Lesson: always compare explicitly (`== True`).
- ⚠️ *Bug 2, fixed.* Events were joined on `event_id` alone, but event IDs repeat in every match. Joins must use `match_id` + `event_id`. The handoff notes said so; I missed it at first.
- ⚠️ *Sketchy:* the 26% → 50% pattern is partly built in. A looser block has more space inside it by definition. It is also mixed up with *where* the block is (deep blocks are compact *and* near goal). It shows the question is worth asking, not the answer.

---

## Step 2 — Understanding the data (19 Nov)

**What:** wrote `docs/DATA_REFERENCE.md`, a guide to every file and the fields that matter.

**Key finding — players off camera.** Tracking comes from TV broadcast video. Players outside the shot have **estimated** positions (`is_detected = false`). In medium and low blocks, about 70% of defenders are on camera on average. Only about half of moments have at least 8 of 10 defenders on camera. Any shape measurement built on estimated positions would partly measure SkillCorner's guesses.

**Other limits:** clubs appear in 1 to 7 of the 20 matches (most 2–4); xThreat and pass-completion values are model estimates, not outcomes.

---

## Step 3 — Week 1: measuring the block frame by frame (19 Nov)

**Goal:** a table that describes the defending team's shape 5 times per second, for every moment it defends in a medium or low block.

**Code:** `src/compact_block/` (`load.py` reads files, `frames.py` picks moments, `block.py` measures shape, `viz.py` draws pictures). Run `scripts/build_block_frames.py` to build the table; `scripts/check_block_frames.py` draws check pictures.

### How it works

1. **Pick the moments.** Take every phase SkillCorner labels as the defending team in a *medium block* or *low block*. Within those, keep every second tracking frame (5 per second instead of 10; neighbouring frames are almost identical).
2. **Turn the pitch the same way every time.** Rotate coordinates so the attacking team always plays left to right. The defending goal is then always on the right, and "deeper" always means larger x.
3. **Take the 10 outfield defenders** (goalkeeper left out). Frames with fewer than 9 outfield defenders are skipped.
4. **Count how many are on camera** (`n_detected`). Analysis will use only frames with **at least 8 of 10** on camera.
5. **Find the lines.** The back line is the players whose position in that match is full-back, wing-back or centre-back. The remaining players are split into a midfield line and a front line by depth.
6. **Measure the shape** (table below).

### The measures

| Measure | What it is | Why we want it |
|---|---|---|
| `depth` | Distance from the deepest to the most advanced outfield defender (m) | Vertical compactness |
| `width` | Distance from the widest player on one side to the other (m) | Horizontal compactness |
| `area` | Area of the outline around all 10 defenders (m²) | Overall compactness in one number |
| `back_mid_gap` | Average position of back line minus average position of midfield line (m) | The classic "space between the lines" |
| `screen_gap` | Back line to the two deepest players in front of it (m) | The space right in front of the centre-backs, where many breaches happen; steadier when a midfielder steps out |
| `back_max_gap` | Biggest side-to-side gap between neighbours in the back line (m) | A hole a pass or run can go through |
| `mid_max_gap` | Same for the midfield line (m) | Holes in the first screen |

### What changed along the way

- ⚠️ *First version mislabelled lines (fixed).* Lines were first found by depth alone. When the block slid across toward the ball, a far-side player dropped and got put in the wrong line (a 4-4-2 shown as 4-2-4). Using player positions for the back line fixed it.
- Added `screen_gap` after seeing a midfielder step up to press: one midfielder stepping out makes `back_mid_gap` jump even if the space in front of the defence hasn't changed.

### Results

- **193,920 block moments** across 20 matches; **57% well observed** (≥ 8 of 10 defenders on camera).
- Typical shapes (median, well-observed frames):

| | Depth | Width | Back–mid gap | Screen gap | Biggest back-line hole |
|---|---|---|---|---|---|
| Medium block | 25.2 m | 37.1 m | 9.5 m | 8.3 m | 13.2 m |
| Low block | 23.1 m | 32.2 m | 6.6 m | 4.7 m | 11.6 m |

- Lines found: 4-4-2 (29%), 4-3-3 (21%), 4-5-1 (11%), 4-2-4 (11%), 5-3-2 (10%), 5-4-1 (7%).
- **Teams differ.** In a medium block, median screen gap ranges from 6.9 m (Wellington) to 9.4 m (Central Coast).
- Sanity checks passed: low blocks sit deeper than medium blocks (back line ~35 m vs ~16 m from halfway); pictures of four moments match what the numbers say.

### Things that may be wrong or sketchy

- ⚠️ **The camera filter may bias the sample.** The broadcast camera follows the ball, so *stretched* blocks (players far apart) are more likely to have players off camera and get filtered out. Our "well observed" moments may lean toward compact moments. Need to check by comparing shapes with and without the filter.
- ⚠️ **The 8-of-10 threshold is a judgement call**, not derived from anything. Should test 7 and 9 to see if results change.
- ⚠️ **Positions are one per player per match** (the most common one in that match's events). If a team changes system mid-match, or a full-back plays as a wing-back for half the game, some frames will have the wrong back line.
- ⚠️ **Always three lines.** Teams that defend in four lines (e.g. 4-1-4-1) get squeezed into three. The front "line" is often one or two players, so front-line measures mean little.
- ⚠️ **Width is set by the two widest players.** One winger tracking a full-back can make the whole block look wide.
- ⚠️ **Frames are not independent.** 5 frames per second from the same spell of play are nearly copies. Any statistics must treat a phase or match as the unit, not a frame. Testing must hold out whole matches.
- ⚠️ **Uneven teams.** Auckland appears in 7 matches, Newcastle in 1. League-wide averages lean toward the teams we see most.
- 🟡 **The breach definition rests on SkillCorner's "inside the defensive shape" field.** We have not yet confirmed exactly how SkillCorner draws that shape. Must check the event specification before relying on it.
- 🟡 **Red cards:** frames with 9 outfield defenders are kept but measured the same way as 10.

### Decisions to make

- 🟡 Build the coaching rule around **screen gap** (steadier) or **back–mid gap** (familiar coaching language)?
- 🟡 Is the **breach definition** right from a coaching point of view? Currently: on the ball inside the defensive shape, in the centre or half-spaces, in the middle or final third.
- 🟡 Keep the **8-of-10 camera filter**, or test alternatives first?

---

## Step 4 — Moving to Claude Code on Aabheer's PC (20 Nov)

**What:** decided to continue in Claude Code on Aabheer's own PC, so he can see and run the code himself. A new Claude Code session doesn't see the claude.ai chat, so `CLAUDE.md` (read automatically at the start of every session) now records how Aabheer wants to work, where things stand, the open decisions, risks and technical pitfalls.

**Fix made:** ⚠️ `scripts/download_data.py` ran git with only the `PATH` setting, which would likely fail on Windows (git needs other system settings there). It now passes the full environment.

**Agreed way of working:** notebooks (one per stage) for understanding, `src/` for reusable code; discuss changes before making them; log every step here.
