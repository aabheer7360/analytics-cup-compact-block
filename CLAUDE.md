# CLAUDE.md — briefing for Claude Code sessions

Read this first, then `docs/PROJECT_LOG.md` (full step-by-step history) and `docs/DATA_REFERENCE.md` (what the data contains). This project was started in a claude.ai chat on 19–20 Nov 2026 and continues here.

## The project

**Owner:** Aabheer (GitHub `aabheer7360`). Former youth football coach (6 years), economics/data-analytics background, comfortable with Python. Wants to build a football-analytics portfolio and contacts in UK/European football data companies.

**Entry:** SkillCorner / PySport **Analytics Cup 2.0**, Paris edition. Repo: `aabheer7360/analytics-cup-compact-block` (public, MIT).

**Question — "Compact, but vulnerable?"** When a defensive block (medium or low) is compact, how do attackers still get the ball inside it centrally, and what simple spacing rules can coaches use to prevent it?

**What matters most to Aabheer:** findings that coaches and non-data staff can actually use. Not "the optimal way to defend", but simple rules (e.g. "past X m between the lines, breaches double"), named patterns in coaching language, and a per-team report with clip timestamps.

## How Aabheer wants to work (important)

- **Go slowly and explain.** He wants to understand every step, not just receive results.
- **Discuss before changing things.** Propose changes to method or code and agree them before making them.
- **Log every step** in `docs/PROJECT_LOG.md`: what was done, why, how the measures were built and used. Include what went wrong and anything sketchy (⚠️) and open decisions (🟡). No line-by-line code explanation needed.
- **Keep everything organised in this folder** (`D:\Analytics Cup 2.0`). Code, figures and docs all live here.
- **Notebooks for understanding, `src/` for reusable code.** One notebook per stage in `notebooks/` that walks through the step with text, tables and pictures, calling functions from `src/compact_block/` rather than copying them.
- He is the football expert: ask him to judge definitions, pictures and pattern names. He writes and voices the README and the video.
- Plain language, exact numbers, say clearly when something is uncertain. Never claim something was done or verified when it wasn't.

## Competition facts

Verified 19 Nov 2026: **deadline 18 Dec 2026**; **only SkillCorner open data may be used**.

From October notes, **recheck against the official rules** before relying on them: individual or pair entry; public openly licensed repo without the data; README max 1,000 words and max two figures/tables combined; max 1-minute YouTube pitch voiced by the participant; five judging criteria at 20% each (relevance, methodology, originality, communication, open-source potential); Paris final 17 Feb 2027, in person, travel not reimbursed. Also still to check: any rule on AI-assisted code, and whether a specific submission template or notebook is required.

## Plan (about 6 hours a week)

| Week | Stage | Status |
|---|---|---|
| 1 (to 26 Nov) | Measure the block frame by frame from tracking | **Done** (code); walkthrough notebook not yet written |
| 2 (27 Nov – 3 Dec) | Spacing rule: block shape 1–2 s before breaches vs non-breach moments; find thresholds; test on held-out matches | Next |
| 3 (4 – 10 Dec) | Name the patterns that break compact blocks (midfielder steps out, winger doesn't tuck in, back line drops); count per team | – |
| 4 (11 – 18 Dec) | Coach report generator (one page per team, plain English, clip timestamps); README; video script | – |

## Where things stand (20 Nov 2026)

**Done**
- Topic chosen (Idea A) after testing it against "dangerous runs left unused" (Idea B, dropped: SkillCorner already publishes those counts). Tests in `exploration/`.
- Week 1 code: `src/compact_block/` measures the defending team's shape 5 times a second in every medium/low-block moment of all 20 matches → `outputs/cache/block_frames.parquet` (193,920 rows; 57% well observed).
- Docs: `docs/PROJECT_LOG.md`, `docs/DATA_REFERENCE.md`, README with folder layout.

**Next steps, in order**
0. **Commit the handover files** (`CLAUDE.md`, `docs/PROJECT_LOG.md` Step 4, the `scripts/download_data.py` Windows fix were copied in but not committed), then `git push origin main`.
1. **Set up on this PC** (see below) and check `scripts/build_block_frames.py` reproduces 193,920 frames, 57% well observed.
2. **Write `notebooks/01_measure_block.ipynb`**: a slow walkthrough of Week 1 for Aabheer (one match: load → pick block moments → rotate → filter by camera → find lines → measure → picture).
3. **Go through the open decisions with him** (below) before Week 2.
4. **Test the camera-filter bias** (⚠️ below) before using the filter in Week 2.
5. Start Week 2.

**Open decisions (ask Aabheer)**
- 🟡 Build the coaching rule on **`screen_gap`** (back line to the two deepest players in front of it; steady when a midfielder steps out) or **`back_mid_gap`** (back line to midfield line; familiar coaching language)?
- 🟡 **Breach definition.** Currently: a player possession starting `inside_defensive_shape_start == True`, in channel `center` / `half_space_left` / `half_space_right`, in the `middle_third` or `attacking_third`. Is that right for coaches? Also confirm in SkillCorner's event spec how "defensive shape" is drawn.
- 🟡 Keep the **8 of 10 defenders on camera** filter, or test 7 and 9 first?

**Known risks**
- ⚠️ The camera follows the ball, so stretched blocks lose players off camera more often; the filter may bias the sample toward compact moments. Compare shape distributions with and without the filter.
- ⚠️ Frames are not independent (5 per second from the same spell). Use phase or match as the unit; hold out whole matches for testing.
- ⚠️ Team coverage is uneven: Auckland 7 matches, Newcastle 1.
- ⚠️ Positions are one per player per match (most common in events); mid-match system changes are missed. Always three lines, so 4-1-4-1 shapes get squeezed. Width is set by the two widest players.
- ⚠️ The 26% → 50% breach pattern from topic selection is partly built in (a looser block has more space by definition) and mixed up with pitch location.

## Technical notes and pitfalls

- **Data:** `python scripts/download_data.py` puts SkillCorner open data (commit `4340d27`, 20 A-League 2024/25 matches, ~1.9 GB) in `data/matches/`. Tracking files are Git LFS objects fetched from `media.githubusercontent.com` and checked against their SHA-256. `data/` is git-ignored. Path override: `SKILLCORNER_DATA` environment variable.
- **Join events on `(match_id, event_id)`**; event IDs repeat across matches (a bug we hit).
- **Boolean columns contain NaN.** Compare with `.eq(True)`; `any()` on object columns counts NaN as true (a bug we hit).
- **Orientation:** each phase has `attacking_side`; `block.orient()` rotates tracking so attack is left to right and the defending goal is at +x. Event coordinates already follow this convention.
- **Back line** = players whose usual position in that match (mode of `player_position` in events) is LB/RB/CB/LCB/RCB/LWB/RWB; the others are split by depth into midfield and front lines (`block.assign_lines`). Depth-only splitting mislabelled shifted blocks (a bug we fixed).
- `is_detected` is per player per frame; hollow dots in our pictures = estimated positions.
- Tracking line format starts `{"frame": N,`; `load.iter_tracking` uses this to skip unneeded frames quickly. One match builds in about 6 seconds.
- Code needs **Python 3.10+** (uses `X | None` type hints).
- If git shows every file as modified with mode changes only, that came from copying files across; on Windows `git config core.fileMode false` hides it.

## Setup on Windows (first session)

```powershell
cd "D:\Analytics Cup 2.0"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt jupyter
python scripts\download_data.py
python scripts\build_block_frames.py
```

**GitHub:** the claude.ai cloud session could not push (the Claude GitHub App wasn't installed). The local commits `40a1b17` and `bbc51ba` (plus later ones) exist only in this folder until pushed. From this PC, push with Aabheer's own git login: `git push origin main`.

## Related

- claude.ai project "Football Data Outreach" holds `PROJECT_HANDOFF.md` (wider career/outreach context and October notes) and the data reference doc. The outreach work and a separate "2–0 lead" study are out of scope here.
