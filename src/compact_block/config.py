"""Paths and settings shared across the project."""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Where the SkillCorner match folders live. Override with the SKILLCORNER_DATA
# environment variable if you keep the data elsewhere.
DATA_DIR = Path(os.environ.get("SKILLCORNER_DATA", REPO_ROOT / "data" / "matches"))
OUTPUT_DIR = REPO_ROOT / "outputs"

# Defensive phases we study: an organised block, not transitions or chaos.
BLOCK_PHASES = ("medium_block", "low_block")

# A frame is "well observed" when at least this many of the 10 outfield
# defenders are seen by the broadcast camera (not estimated by SkillCorner).
MIN_DETECTED_DEFENDERS = 8

# Tracking runs at 10 frames per second; keep every Nth frame (2 -> 5 per second).
FRAME_STEP = 2
