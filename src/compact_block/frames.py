"""Build the frame-by-frame table of block measurements for a match."""
import numpy as np
import pandas as pd

from .block import block_metrics, orient
from .config import BLOCK_PHASES, FRAME_STEP
from .load import BACK_LINE_POSITIONS, iter_tracking, load_meta, load_phases, player_positions, player_table


def block_frames(match_id: str, step: int = FRAME_STEP) -> pd.DataFrame:
    """One row per sampled frame in which a team defends in a medium/low block."""
    meta = load_meta(match_id)
    players = player_table(meta)
    team_of = dict(zip(players.player_id, players.team_id))
    gks = set(players.player_id[players.is_gk])
    position = player_positions(match_id)
    team_ids = {meta["home_team"]["id"], meta["away_team"]["id"]}

    phases = load_phases(match_id)
    phases = phases[phases.team_out_of_possession_phase_type.isin(BLOCK_PHASES)]

    # Which phase each sampled frame belongs to.
    lookup = {}
    for ph in phases.itertuples():
        defending = (team_ids - {ph.team_in_possession_id}).pop()
        for f in range(int(ph.frame_start), int(ph.frame_end) + 1, step):
            lookup[f] = (ph.index, ph.team_out_of_possession_phase_type, ph.attacking_side,
                         ph.team_in_possession_id, defending)

    rows = []
    for fr in iter_tracking(match_id, set(lookup)):
        phase_index, block, side, attacking, defending = lookup[fr["frame"]]
        d = [p for p in fr["player_data"]
             if team_of.get(p["player_id"]) == defending and p["player_id"] not in gks]
        if len(d) < 9:                      # missing players: skip the frame
            continue
        x, y = orient(np.array([p["x"] for p in d]), np.array([p["y"] for p in d]), side)
        ball = fr["ball_data"]
        bx, by = (orient(np.array([ball["x"]]), np.array([ball["y"]]), side)
                  if ball["x"] is not None else (np.array([np.nan]), np.array([np.nan])))
        rows.append(dict(
            match_id=match_id, frame=fr["frame"], period=fr["period"], timestamp=fr["timestamp"],
            phase_index=phase_index, block_type=block, defending_team_id=defending,
            attacking_team_id=attacking, n_defenders=len(d),
            n_detected=sum(bool(p["is_detected"]) for p in d),
            ball_x=float(bx[0]), ball_y=float(by[0]),
            **block_metrics(x, y, np.array([position.get(p["player_id"]) in BACK_LINE_POSITIONS for p in d])),
        ))
    return pd.DataFrame(rows)
