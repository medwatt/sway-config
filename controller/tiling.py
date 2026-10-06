"""Auto-tiling: keeps every workspace as side-by-side columns.

After each window event (main.py), repair_all() asks plan_repair() for the next
fix on each workspace and applies it, until nothing is left. Workspaces with
auto_tiling=False (config.py) and ones arranged by hand are left alone.
"""

# imports <<<
import logging

from config import FIRST_COLUMN_WIDTH, WORKSPACES
# >>>

NO_AUTO_TILING = {name for name, ws in WORKSPACES.entries.items() if not ws.auto_tiling}

# Each repair step moves one window; this only bounds a runaway loop.
MAX_STEPS = 50


# tree helpers <<<

def is_window(con):
    """True for a real window: XWayland ones have .window, native Wayland ones
    have .app_id (and .window == None)."""
    return bool(con.window or getattr(con, "app_id", None))


def tiled_windows(ws):
    return [w for w in ws.leaves() if is_window(w) and w.floating not in ["user_on", "auto_on"]]


def is_manual(ws):
    """True when the workspace was arranged by hand (tabs, stacks, splits inside
    a column); such workspaces are left alone."""
    if any(c.layout in ["tabbed", "stacked"] for c in ws.descendants()):
        return True
    cols = ws.nodes
    if len(cols) < 2:
        return False  # one column or a wrapper: repaired by plan_repair
    if ws.layout != "splith":
        return True
    for col in cols:
        if is_window(col):
            continue
        if any(not is_window(n) for n in col.nodes):
            return True
        if len(col.nodes) > 1 and col.layout != "splitv":
            return True
    return False
# >>>

# repair plan (pure: tree in, next fix out) <<<

def plan_repair(ws):
    windows = tiled_windows(ws)
    if not windows or is_manual(ws):
        return []

    if len(windows) == 1:
        w = windows[0]
        if w.parent.type != "workspace":
            # Removes every wrapper around the window; `split h` would add one.
            return [(w.id, "split none")]
        if ws.layout != "splith":
            # On the only child of a workspace this changes the workspace layout.
            return [(w.id, "splith")]
        return []

    cols = ws.nodes
    if len(cols) == 1:
        # Everything in one column (or one wrapper): pop the first window out
        # to the left so it becomes the first column.
        return [(windows[0].id, "move left")]

    for col in cols:
        if is_window(col):
            # A bare window as a column: give it its vertical container.
            fixes = [(col.id, "split v")]
            # Only runs when a column is new, so later manual resizes are kept.
            # sway applies the width to the column even if cols[0] is the
            # window being wrapped here.
            if len(cols) == 2:
                fixes.append((cols[0].id, f"resize set width {FIRST_COLUMN_WIDTH} ppt"))
            return fixes
    for col in cols:
        if len(col.nodes) == 1 and col.layout != "splitv":
            # On an only child this changes the column's layout, no new wrapper.
            return [(col.nodes[0].id, "split v")]
    return []
# >>>

# applying it <<<

def _next_repair(sway):
    for ws in sway.get_tree().workspaces():
        if ws.name in NO_AUTO_TILING or ws.name.startswith("__"):
            continue
        fixes = plan_repair(ws)
        if fixes:
            return fixes
    return []


def repair_all(sway):
    """Repair every auto-tiled workspace, one step at a time, re-reading the
    tree after each step. All workspaces are checked, not just the focused one,
    because windows close and move on any of them."""
    for _ in range(MAX_STEPS):
        fixes = _next_repair(sway)
        if not fixes:
            return
        sway.command("; ".join(f"[con_id={cid}] {cmd}" for cid, cmd in fixes))
    logging.warning("repair did not settle in %d steps", MAX_STEPS)
# >>>
