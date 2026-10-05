"""The shape of the entries in config.py: what each field means and its default.

config.py builds its entries from these; actions.py, keys.py and tiling.py
read them.
"""

# imports <<<
from dataclasses import dataclass, field
# >>>


@dataclass
class Workspace:
    # window names of the windows that belong here; they're moved here when they open
    windows: list
    # started by the workspace key, unless one of its windows is already there
    launch: str = ""
    # generic window names (shared with other apps) that also count as
    # "already open", but aren't moved here
    also_open_if: list = field(default_factory=list)
    # True: its windows open as tabs
    tabbed: bool = False
    # False: auto-tiling (tiling.py) leaves this workspace alone, so hand-made
    # layouts are kept
    auto_tiling: bool = True
    # False: the workspace key isn't bound because it does something else
    # (the move key still is)
    bind_key: bool = True


@dataclass
class Workspaces:
    # key patterns for every entry; {letter} is the entry's name in lower case
    key: str  # go to the workspace (and start its app)
    move_key: str  # move the focused window there
    entries: dict  # name (a letter): Workspace


@dataclass
class Monitor:
    # output names it may be connected as; the first one connected is used
    outputs: list
    # numbered workspaces that open on it. If it isn't connected, sway opens
    # them on the monitor you're on.
    workspaces: list


@dataclass
class Scratchpad:
    window: str  # window name of its window
    launch: str  # started the first time the key is pressed


@dataclass
class Scratchpads:
    # sway commands applied to every scratchpad window the first time it opens
    rule: str
    entries: dict  # key: Scratchpad


@dataclass
class FolderPicker:
    key: str  # starts picking
    mode: str  # sway mode while picking; waybar shows this name
    folders: dict  # letter: folder; that letter then opens it
    # the WORKSPACES entry the folders open on; its letter just goes there
    workspace: str
    # how to open a folder; {marker} is <folder>/.directory, which makes dolphin
    # --select reuse an already-open tab for that folder
    open_folder: str
