"""Measure the defensive block frame by frame for all matches and save one table.

Usage: python scripts/build_block_frames.py
Output: outputs/cache/block_frames.parquet (one row per sampled block frame)
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pandas as pd

from compact_block.config import MIN_DETECTED_DEFENDERS, OUTPUT_DIR
from compact_block.frames import block_frames
from compact_block.load import match_ids

parts = []
for m in match_ids():
    t = time.time()
    parts.append(block_frames(m))
    print(f"{m}: {len(parts[-1]):,} frames ({time.time() - t:.0f}s)")
df = pd.concat(parts, ignore_index=True)
out = OUTPUT_DIR / "cache" / "block_frames.parquet"
out.parent.mkdir(parents=True, exist_ok=True)
df.to_parquet(out)
well = df.n_detected >= MIN_DETECTED_DEFENDERS
print(f"\n{len(df):,} block frames, {well.mean():.0%} well observed (>= {MIN_DETECTED_DEFENDERS}/10 defenders on camera)")
print(f"saved {out}")
