# SkillCorner A-League Data: Reference Guide

Nov 19, 2026 · @Aabheer Patil

## Overview

The Analytics Cup 2.0 dataset covers the **2024/25 Australian A-League** (13 clubs): detailed data for **20 matches** (23 Nov 2024 – 17 May 2025) plus season-level player aggregates. Only this data may be used in the competition.

- Source: [SkillCorner Open Data](https://github.com/SkillCorner/opendata), commit `4340d27`, downloaded 19 Nov 2026 (same version as the October inventory).
- Coordinates are in metres with (0, 0) at the centre spot; x runs along the pitch, y across it. Pitches are 104–105 m × 68 m.
- Clubs appear unevenly: from 1 match (Newcastle) to 7 (Auckland FC), about 3 for most.

## Per-match files

Every match folder (`data/matches/<match_id>/`) holds four files. Tracking is the raw positions; the other three are SkillCorner's interpretation of it.

| File | What it holds | Size per match | Plain-English meaning |
| --- | --- | --- | --- |
| `<id>_match.json` | Teams, line-ups, player roles, kick-off times, pitch size, which side each team attacks | 1 small file | The team sheet |
| `<id>_tracking_extrapolated.jsonl` | x/y of all 22 players and the ball, 10 snapshots per second; an `is_detected` flag per player | \~57,000 frames, \~90 MB | A bird's-eye replay as numbers |
| `<id>_dynamic_events.csv` | \~4,700 rows × 322 columns of events built from tracking | \~5 MB | What happened, with context |
| `<id>_phases_of_play.csv` | \~440 labelled spells of play with team shape at start and end | \~130 KB | What each team was doing, spell by spell |

Key to join events across matches: `(match_id, event_id)`. Event IDs repeat between matches, so never join on `event_id` alone.

## The four event types

Dynamic events come in four types; counts are totals across all 20 matches.

| Event type | Count | What one row is | Fields worth knowing |
| --- | --- | --- | --- |
| Player possession | 18,710 | One player's spell on the ball | `end_type` (pass, shot, loss), `overall_pressure_start`, `inside_defensive_shape_start`, `channel_start`, `third_start`, line breaks |
| Passing option | 48,308 | A teammate available to receive, whether or not the pass went to him | `targeted`, `received`, `xpass_completion`, `xthreat`, `dangerous` |
| Off-ball run | 9,898 | A run without the ball (behind, coming short, overlap…) | `event_subtype`, `targeted`, `received`, `dangerous` |
| On-ball engagement | 17,445 | A defender pressing or closing down the carrier | `event_subtype` (pressure, pressing, counter-press…) |

Terms that are easy to misread:

- **Passing option** is a potential receiver, not a pass. `targeted` = the pass went to him; `received` = he got it.
- **`xthreat`** is SkillCorner's estimate of the chance of a goal within 10 seconds if the pass is completed. `dangerous` = xthreat above 0.02.
- **`xpass_completion`** is the estimated chance a pass to that option succeeds. Both are model outputs, not observed results.
- **`inside_defensive_shape_start`** = the player got the ball inside the opponent's defensive outline. This is the core measure of central access for our project.
- **`time_to_impact`** fields are difficulty bands, not seconds.

## Phases of play

Each match is cut into spells (8,834 across 20 matches), and each spell is labelled from both sides at once. The defending label is what our project filters on.

| Attacking team doing | Defending team doing | Phases (20 matches) |
| --- | --- | --- |
| Build-up | High block | 1,196 |
| Create | Medium block | 2,880 |
| Finish | Low block | 1,623 |
| Chaotic | Chaotic | 1,802 |
| Direct | Defending direct play | 677 |
| Set play | Defending set play | 360 |
| Transition | Defending transition | 185 |
| Quick break | Defending quick break | 111 |

Each phase also records both teams' **width and length in metres** at its start and end (`team_out_of_possession_width_start` and so on). The median defending shape at phase start is 36 m wide × 53 m long. These are one snapshot per phase; frame-by-frame compactness has to come from tracking.

The defensive block is "organised" in medium and low blocks (3,737 usable phases); these are the sample for the compact-block study.

## Season aggregates and body pose

The season files (`data/aggregates/`) cover the whole 2024/25 season, one row per player-team-position. They are useful for context, not for analysing moments.

| File | Shape | Content |
| --- | --- | --- |
| Physical | 406 rows × 65 cols | Distance, sprints, top speed (PSV99), mostly per-match averages |
| Off-ball runs | 407 × 130 | Runs by type: count, targeted, received, dangerous, per 30 min of team possession |
| Passing | 407 × 48 | Pass attempts and completion, including to dangerous options |

Suffixes: `p30tip` = per 30 minutes of own-team possession; `p90` = per 90 minutes; `p60_bip` = per 60 ball-in-play minutes. Percentages are written as 75.76, not 0.7576. Physical values such as minutes and distance are per-match averages, not season totals.

Body pose (29 joints per player, 25 per second) exists in full for only two matches; we are not using it.

## Limitations and pitfalls

The biggest risk for a compactness study is off-camera players: tracking comes from TV broadcast video, so some positions are estimated.

1. **Estimated positions.** In medium and low blocks, about **70% of defenders** are visible (`is_detected = true`) on average; only **43–61% of moments** have at least 8 in 10 defenders visible (checked on 6 matches). Compactness must be measured on well-observed frames.
2. **Small sample per team.** 1 to 7 matches per club (most have 2–4): fine for league-wide patterns, too thin for scouting one opponent.
3. **Model outputs are not outcomes.** `xthreat`, `xpass_completion`, EPV and passing-option scores are SkillCorner estimates.
4. **Missing often means "not applicable".** Many columns only apply to some event types; never apply a blanket `dropna()`. Check NaN handling in boolean columns: NaN counts as true in some pandas operations.
5. **Ordering.** Clock labels overlap at half-time; sort by `period` then frame.
6. **Empty frames.** Some tracking frames have no players, null timestamps or no ball position (e.g. before kick-off).
7. **Pass length fields** (`pass_range`, `pass_distance`) are filled only for completed passes, so grouping completion by them shows a false 100%.

## Sources

- [SkillCorner Open Data repository](https://github.com/SkillCorner/opendata) — files, schemas and tutorials
- [Dynamic Events CSV Specifications](https://26560301.fs1.hubspotusercontent-eu1.net/hubfs/26560301/Guides/Dynamic%20Events/20250216%20-%20Dynamic%20Events%20CSV%20Specifications.pdf) (SkillCorner, Feb 2025) — field definitions
- Counts and detection rates computed in this project's workspace on 19 Nov 2026
