"""Reading SkillCorner open-data files for one match."""
import json
from pathlib import Path

import pandas as pd

from .config import DATA_DIR


def match_ids(data_dir: Path = DATA_DIR) -> list[str]:
    """All match ids that have a folder in the data directory."""
    return sorted(p.name for p in Path(data_dir).iterdir() if p.is_dir())


def load_meta(match_id: str, data_dir: Path = DATA_DIR) -> dict:
    with open(Path(data_dir) / match_id / f"{match_id}_match.json", encoding="utf-8") as f:
        return json.load(f)


def load_events(match_id: str, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    return pd.read_csv(Path(data_dir) / match_id / f"{match_id}_dynamic_events.csv", low_memory=False)


def load_phases(match_id: str, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    return pd.read_csv(Path(data_dir) / match_id / f"{match_id}_phases_of_play.csv")


def iter_tracking(match_id: str, frames: set[int] | None = None, data_dir: Path = DATA_DIR):
    """Yield tracking frames (dicts) one at a time, optionally only those in `frames`.

    The tracking file is ~90 MB per match, so we stream it line by line rather
    than loading it all into memory.
    """
    path = Path(data_dir) / match_id / f"{match_id}_tracking_extrapolated.jsonl"
    with open(path, encoding="utf-8") as f:
        for line in f:
            if frames is not None:
                # Cheap pre-check on the frame number before parsing the whole line.
                n = int(line[10:line.index(",")])
                if n not in frames:
                    continue
            yield json.loads(line)


def player_table(meta: dict) -> pd.DataFrame:
    """One row per player: id, team, name, role, goalkeeper flag."""
    rows = []
    for p in meta["players"]:
        role = p["player_role"]["name"] if isinstance(p["player_role"], dict) else str(p["player_role"])
        rows.append(dict(player_id=p["id"], team_id=p["team_id"], name=p["short_name"],
                         role=role, is_gk=role == "Goalkeeper"))
    return pd.DataFrame(rows)


BACK_LINE_POSITIONS = {"LB", "RB", "CB", "LCB", "RCB", "LWB", "RWB"}


def player_positions(match_id: str, data_dir: Path = DATA_DIR) -> dict:
    """Each player's usual position code in this match (e.g. 'LCB', 'RW').

    Taken from the dynamic events (most common value per player), which also
    covers substitutes who came on.
    """
    e = load_events(match_id, data_dir)
    e = e[e.player_position.notna()]
    return e.groupby("player_id").player_position.agg(lambda s: s.mode().iat[0]).to_dict()
