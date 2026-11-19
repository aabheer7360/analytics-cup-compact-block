"""Pitch drawings of the defensive block, used to check the measurements by eye."""
import matplotlib.pyplot as plt
import numpy as np
from mplsoccer import Pitch

from .block import assign_lines, orient
from .load import BACK_LINE_POSITIONS, player_positions
from .load import iter_tracking, load_meta, player_table

DEF, ATT, LINE, INK = "#c0392b", "#2e6fb5", "#7f8c8d", "#2b2b2b"


def draw_block(ax, match_id, frame, attacking_side, defending_team_id, title=None, meta=None):
    meta = meta or load_meta(match_id)
    players = player_table(meta)
    team_of = dict(zip(players.player_id, players.team_id))
    gks = set(players.player_id[players.is_gk])
    fr = next(iter_tracking(match_id, {frame}))

    Pitch(pitch_type="skillcorner", pitch_length=meta["pitch_length"], pitch_width=meta["pitch_width"],
          line_color="#b0b4b8", pitch_color="white", linewidth=1).draw(ax=ax)
    position = player_positions(match_id)
    pts = [(p["x"], p["y"], team_of.get(p["player_id"]), p["player_id"] in gks, p["is_detected"],
            position.get(p["player_id"]) in BACK_LINE_POSITIONS)
           for p in fr["player_data"]]
    x, y = orient(np.array([p[0] for p in pts]), np.array([p[1] for p in pts]), attacking_side)
    is_def = np.array([p[2] == defending_team_id for p in pts])
    is_gk = np.array([p[3] for p in pts])
    seen = np.array([bool(p[4]) for p in pts])

    for mask, colour in ((is_def, DEF), (~is_def, ATT)):
        ax.scatter(x[mask & seen], y[mask & seen], s=90, c=colour, edgecolors="white", zorder=4)
        ax.scatter(x[mask & ~seen], y[mask & ~seen], s=90, facecolors="white", edgecolors=colour,
                   linewidths=1.6, zorder=4)            # hollow = estimated, not on camera

    out = is_def & ~is_gk
    dx, dy = x[out], y[out]
    names = ("back", "mid", "front")
    backs = np.array([p[5] for p in pts])[out]
    for name, idx in zip(names, assign_lines(dx, backs)):
        lx = dx[idx].mean()
        ax.plot([lx, lx], [dy[idx].min() - 2, dy[idx].max() + 2], color=LINE, lw=1.5, ls="--", zorder=3)
        ax.text(lx, dy[idx].max() + 3.5, name, ha="center", fontsize=8, color=LINE)

    b = fr["ball_data"]
    if b["x"] is not None:
        bx, by = orient(np.array([b["x"]]), np.array([b["y"]]), attacking_side)
        ax.scatter(bx, by, s=30, c="black", zorder=6)
    if title:
        ax.set_title(title, fontsize=9.5, color=INK, loc="left")
