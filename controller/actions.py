"""Everything a key can do. keys.py decides which key runs which of these.

A public method that takes no arguments can be bound to a key by name in
config.py (ACTION_KEYS).
"""

# imports <<<
import os
import shlex
import time

from config import FOLDER_PICKER, MONITORS, SCRATCHPADS, WORKSPACES
from tiling import is_window
# >>>

# how long a scratchpad toggle waits for the launched app's window
LAUNCH_TIMEOUT = 10  # seconds


def _matches(con, names):
    """True if the window's name (Wayland app_id or XWayland class) is in names."""
    return con.window_class in names or getattr(con, "app_id", None) in names


class Actions:
    def __init__(self, sway):
        self.sway = sway
        self._waiting = {}  # scratchpad window name -> pending window::new handler

    def run(self, command):
        """Send a plain sway command."""
        self.sway.command(command)

    def _focused_workspace(self):
        focused = self.sway.get_tree().find_focused()
        return focused.workspace() if focused else None

    def _workspace_has(self, names):
        ws = self._focused_workspace()
        return bool(ws and any(_matches(win, names) for win in ws.leaves()))

    # workspaces <<<
    def go_to_workspace(self, name):
        """Go to the workspace, start its app unless it's already there."""
        self.run(f"workspace {name}")
        workspace = WORKSPACES.entries[name]
        if workspace.launch and not self._workspace_has(workspace.windows + workspace.also_open_if):
            self.run(f"exec {workspace.launch}")

    def _free_workspace(self):
        """The first unused numbered workspace on the current monitor, else on
        another monitor, else None."""
        workspaces = self.sway.get_workspaces()
        used = {ws.name.split(":")[0].strip() for ws in workspaces}
        current = next((ws.output for ws in workspaces if ws.focused), None)
        here = [m for m in MONITORS if current in m.outputs]
        elsewhere = [m for m in MONITORS if current not in m.outputs]
        for monitor in here + elsewhere:
            for number in monitor.workspaces:
                if str(number) not in used:
                    return number
        return None

    def go_to_empty_workspace(self):
        number = self._free_workspace()
        if number:
            self.run(f"workspace {number}")

    def move_to_empty_workspace(self):
        """Move the focused window to a free workspace and follow it."""
        focused = self.sway.get_tree().find_focused()
        number = self._free_workspace()
        if focused and focused.type != "workspace" and number:
            self.run(f"move container to workspace {number}; workspace {number}")

    def close_all_windows(self):
        ws = self._focused_workspace()
        for window in ws.leaves() if ws else []:
            if is_window(window):
                window.command("kill")
    # >>>

    # scratchpads <<<
    def toggle_scratchpad(self, pad):
        """Show/hide the app's window; start it and scratchpad it the first time."""
        mark = f"sc_{pad.window}"
        if self.sway.get_tree().find_marked(mark):
            self.run(f"[con_mark={mark}] scratchpad show")
            return

        # at most one listener per app; a repeated press replaces it
        self._stop_waiting(pad.window)
        self.run(f"exec {pad.launch}")
        deadline = time.monotonic() + LAUNCH_TIMEOUT

        def on_window(sway, event):
            if time.monotonic() > deadline:  # window never came (e.g. wrong name)
                self._stop_waiting(pad.window)
            elif _matches(event.container, [pad.window]):
                self.run(f"[con_id={event.container.id}] mark {mark}, {SCRATCHPADS.rule}, "
                         "move scratchpad, scratchpad show")
                self._stop_waiting(pad.window)

        self._waiting[pad.window] = on_window
        self.sway.on("window::new", on_window)

    def _stop_waiting(self, window):
        handler = self._waiting.pop(window, None)
        if handler:
            self.sway.off(handler)
    # >>>

    # folders <<<
    def go_to_folder_workspace(self):
        """The picker's own letter: leave the picker, go to its workspace."""
        self.run("mode default")
        self.go_to_workspace(FOLDER_PICKER.workspace)

    def open_folder(self, letter):
        """Leave the picker, open one of its folders on its workspace."""
        self.run("mode default")
        self.run(f"workspace {FOLDER_PICKER.workspace}")
        marker = os.path.join(os.path.expanduser(FOLDER_PICKER.folders[letter]), ".directory")
        self.run(f"exec {FOLDER_PICKER.open_folder.format(marker=shlex.quote(marker))}")
    # >>>
