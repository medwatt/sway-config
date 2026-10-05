"""Every key the controller binds, and the workspace rules, built from config.py."""

# imports <<<
import logging
import re
from functools import partial

from config import ACTION_KEYS, FOLDER_PICKER, MONITORS, SCRATCHPADS, WORKSPACES
# >>>


def plain_keys():
    """(mode, key, sway command) for every key sway handles by itself."""
    for name in WORKSPACES.entries:
        yield (
            "default",
            WORKSPACES.move_key.format(letter=name.lower()),
            f"move container to workspace {name}",
        )

    picker = FOLDER_PICKER
    yield "default", picker.key, f"mode {picker.mode}"
    yield picker.mode, "Return", "mode default"
    yield picker.mode, "Escape", "mode default"


def action_keys(actions):
    """(mode, key, action) for every key that runs Python; action takes no arguments."""
    for key, name in ACTION_KEYS.items():
        action = getattr(actions, name, None)
        if action is None:
            logging.error("ACTION_KEYS: %s -> %r is not in actions.py", key, name)
            continue
        yield "default", key, action

    for name, workspace in WORKSPACES.entries.items():
        if workspace.bind_key:
            yield (
                "default",
                WORKSPACES.key.format(letter=name.lower()),
                partial(actions.go_to_workspace, name),
            )

    for key, pad in SCRATCHPADS.entries.items():
        yield "default", key, partial(actions.toggle_scratchpad, pad)

    picker = FOLDER_PICKER
    for letter in picker.folders:
        yield picker.mode, letter, partial(actions.open_folder, letter)
    yield picker.mode, picker.workspace.lower(), actions.go_to_folder_workspace


def rules():
    """Workspace rules, sent once at startup: which monitor the numbered ones
    open on, and which windows (and layout) the app ones get."""
    for monitor in MONITORS:
        for number in monitor.workspaces:
            yield f"workspace {number} output {' '.join(monitor.outputs)}"

    for name, workspace in WORKSPACES.entries.items():
        pattern = "^(" + "|".join(re.escape(w) for w in workspace.windows) + ")$"
        for attr in ("app_id", "class"):
            yield f'assign [{attr}="{pattern}"] workspace {name}'
            if workspace.tabbed:
                yield f'for_window [{attr}="{pattern}"] layout tabbed'
