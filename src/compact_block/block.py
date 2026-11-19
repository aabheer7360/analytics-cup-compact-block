"""Measuring the shape of a defensive block in a single tracking frame.

Convention used throughout: coordinates are rotated so the ATTACKING team
always plays left to right. The defending team therefore protects the goal at
x = +L/2, its back line is its highest-x line, and "behind the block" means
larger x.
"""
import numpy as np
from scipy.spatial import ConvexHull


def orient(x: np.ndarray, y: np.ndarray, attacking_side: str):
    """Rotate raw tracking coordinates so the attack goes left to right."""
    if attacking_side == "right_to_left":
        return -x, -y
    return x, y


def split_into_lines(x: np.ndarray, k: int = 3) -> list[np.ndarray]:
    """Group players into k lines by their x position (depth on the pitch).

    Uses an exact 1-D clustering: of all ways to cut the sorted x values into
    k consecutive groups, pick the one with the smallest total within-group
    spread. Returns index arrays, ordered from deepest line (back) forwards.
    """
    order = np.argsort(-x)            # deepest first (largest x = nearest own goal)
    xs = x[order]
    n = len(xs)
    if n < k:
        return [order]

    def cost(i, j):                   # spread of xs[i:j]
        seg = xs[i:j]
        return ((seg - seg.mean()) ** 2).sum()

    best = {}
    def solve(start, groups):
        if (start, groups) in best:
            return best[(start, groups)]
        if groups == 1:
            res = (cost(start, n), [n])
        else:
            res = (np.inf, None)
            for cut in range(start + 1, n - groups + 2):
                c, cuts = solve(cut, groups - 1)
                c += cost(start, cut)
                if c < res[0]:
                    res = (c, [cut] + cuts)
        best[(start, groups)] = res
        return res

    _, cuts = solve(0, k)
    bounds = [0] + cuts
    return [order[bounds[i]:bounds[i + 1]] for i in range(k)]


def max_lateral_gap(y: np.ndarray) -> float:
    """Largest side-to-side gap between neighbouring players in one line."""
    if len(y) < 2:
        return np.nan
    return float(np.diff(np.sort(y)).max())


def assign_lines(x: np.ndarray, is_back: np.ndarray | None = None) -> list[np.ndarray]:
    """Back, midfield and front lines as index arrays.

    If we know which players are defenders by position (full-backs, wing-backs,
    centre-backs), they form the back line and the rest are split into two
    lines by depth. Sorting everyone by depth alone mislabels lines when the
    block shifts across towards the ball, so position is preferred.
    """
    if is_back is not None and 3 <= is_back.sum() <= 6:
        back = np.flatnonzero(is_back)
        rest = np.flatnonzero(~is_back)
        mid_r, front_r = split_into_lines(x[rest], 2)
        return [back, rest[mid_r], rest[front_r]]
    return split_into_lines(x, 3)


def block_metrics(x: np.ndarray, y: np.ndarray, is_back: np.ndarray | None = None) -> dict:
    """Shape measurements for the outfield defenders of one frame (oriented)."""
    out = dict(depth=float(x.max() - x.min()), width=float(y.max() - y.min()))
    try:
        out["area"] = float(ConvexHull(np.c_[x, y]).volume)  # 2-D 'volume' = area
    except Exception:
        out["area"] = np.nan

    back, mid, front = assign_lines(x, is_back)
    out.update(
        back_n=len(back), mid_n=len(mid), front_n=len(front),
        back_x=float(x[back].mean()), mid_x=float(x[mid].mean()), front_x=float(x[front].mean()),
        back_mid_gap=float(x[back].mean() - x[mid].mean()),     # distance between the lines
        # Space in front of the back line: distance to the two deepest players
        # screening it, whatever line they were assigned to.
        screen_gap=float(x[back].mean() - np.sort(np.delete(x, back))[::-1][:2].mean()),
        back_max_gap=max_lateral_gap(y[back]),                   # biggest hole in the back line
        mid_max_gap=max_lateral_gap(y[mid]),                     # biggest hole in midfield
    )
    return out
