"""Draw four example frames from one match so the block measurements can be checked by eye.

Usage: python scripts/check_block_frames.py [match_id]
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from compact_block.config import MIN_DETECTED_DEFENDERS, OUTPUT_DIR
from compact_block.frames import block_frames
from compact_block.load import load_meta, load_phases
from compact_block.viz import draw_block

match_id = sys.argv[1] if len(sys.argv) > 1 else "1925299"
df = block_frames(match_id)
ok = df[df.n_detected >= MIN_DETECTED_DEFENDERS]
med, low = ok[ok.block_type == "medium_block"], ok[ok.block_type == "low_block"]
phases = load_phases(match_id).set_index("index")
meta = load_meta(match_id)

picks = [
    ("Most compact medium block", med.nsmallest(1, "area").iloc[0]),
    ("Biggest gap between back and midfield lines", med.nlargest(1, "back_mid_gap").iloc[0]),
    ("Random low block", low.sample(1, random_state=1).iloc[0]),
    ("Random medium block", med.sample(1, random_state=3).iloc[0]),
]
fig, axs = plt.subplots(2, 2, figsize=(14, 9.5))
for ax, (label, r) in zip(axs.flat, picks):
    draw_block(ax, match_id, int(r.frame), phases.loc[r.phase_index, "attacking_side"], r.defending_team_id, meta=meta,
               title=(f"{label} · depth {r.depth:.0f} m, width {r.width:.0f} m, back–mid gap {r.back_mid_gap:.1f} m\n"
                      f"back-line hole {r.back_max_gap:.1f} m, midfield hole {r.mid_max_gap:.1f} m · "
                      f"lines {r.back_n}-{r.mid_n}-{r.front_n}"))
fig.text(0.5, 0.02, "Red = defending team, blue = attacking team (attacking left to right). "
         "Hollow dots = position estimated (off camera). Dashed = lines found by the code.", ha="center", fontsize=9)
out = OUTPUT_DIR / "figures" / f"block_check_{match_id}.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=130, bbox_inches="tight")
print(out)
