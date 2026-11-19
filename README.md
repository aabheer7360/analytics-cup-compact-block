# Compact, but vulnerable?

*Analytics Cup 2.0 (Football, Europe / Paris) · SkillCorner A-League 2024/25 data · work in progress*

**Question:** when a defensive block is compact, how do attackers still get into the central spaces inside it, and what simple spacing rules can coaches use to prevent it?

The final README (max 1,000 words, two figures) is written in December. This file tracks progress until then.

## Status

| Week | Stage | Status |
|---|---|---|
| 1 | Measure the block frame by frame from tracking | done |
| 2 | Find the spacing threshold where breaches jump | next |
| 3 | Name the patterns that break compact blocks | – |
| 4 | Coach report generator, README, pitch video | – |

## Where things are

| Folder | What's in it |
|---|---|
| `docs/` | `PROJECT_LOG.md` (step-by-step record, problems, decisions) and `DATA_REFERENCE.md` (what the data contains) |
| `src/compact_block/` | The reusable code: loading files, measuring the block, drawing pitches |
| `scripts/` | Small programs you run: download data, build the measurements, draw check pictures |
| `notebooks/` | Step-by-step walkthrough notebooks (one per stage) |
| `exploration/` | The quick tests used to choose the topic (not part of the final method) |
| `outputs/figures/` | Pictures produced by the scripts |
| `data/` | SkillCorner data after download (not stored in the repository) |

## Run it

```bash
pip install -r requirements.txt
python scripts/download_data.py        # ~1.9 GB SkillCorner open data into data/matches/
python scripts/build_block_frames.py   # block measurements for all 20 matches
python scripts/check_block_frames.py   # pitch pictures to check them by eye
```

## What is measured (per frame, 5 per second)

Only spells where the defending team is in a **medium or low block** (SkillCorner phase labels). Coordinates are rotated so the attack always goes left to right.

| Measure | Meaning |
|---|---|
| `depth`, `width` | Front-to-back and side-to-side size of the 10 outfield defenders (m) |
| `back_mid_gap` | Distance between the back line and the midfield line (m) |
| `screen_gap` | Distance from the back line to the two deepest players in front of it (m) |
| `back_max_gap`, `mid_max_gap` | Biggest side-to-side hole between neighbours in each line (m) |
| `n_detected` | Defenders actually on camera; frames with fewer than 8 of 10 are excluded from analysis |

The back line is set by player position (full-backs, wing-backs, centre-backs); the other players are split into midfield and front lines by depth.

## Data

[SkillCorner Open Data](https://github.com/SkillCorner/opendata). Not included in this repository.

## Licence

MIT
