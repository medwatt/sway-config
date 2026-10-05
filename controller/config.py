"""Everything the controller acts on: workspaces, monitors, scratchpads, folders,
and keys that run Python. Anything sway can do by itself (plain keys, window rules)
stays in the sway config. Apply edits with Super+Shift+r.

Keys are written the sway way: Mod4 = Super, Mod1 = Alt, e.g. "Mod4+Shift+q".
Commands run through a shell, so ~ works in them.
The fields of each entry (Workspace, Scratchpad, ...) and what a "window name"
is are explained in schema.py.
"""

# imports <<<
from schema import FolderPicker, Monitor, Scratchpad, Scratchpads, Workspace, Workspaces
# >>>

# action keys <<<

# key: an Actions method (actions.py) that takes no arguments.
# A new feature: write the method, add its key here.
ACTION_KEYS = {
    "Mod4+Shift+q": "close_all_windows",
    "Mod4+space": "go_to_empty_workspace",
    "Mod4+Shift+space": "move_to_empty_workspace",
}
# >>>

# monitors <<<

# Which numbered workspaces open on which monitor (Super+1-9 are in the sway
# config). The free-workspace keys look on the current monitor first.
MONITORS = [
    Monitor(outputs=["eDP-1"], workspaces=[1, 2, 3, 4]),
    Monitor(
        outputs=["DP-1", "DP-2", "DP-3", "DP-4", "DP-5", "HDMI-A-1", "HDMI-A-2", "HDMI-A-3", "HDMI-A-4"],
        workspaces=[5, 6, 7, 8, 9],
    ),
]
# >>>

# workspaces <<<

WORKSPACES = Workspaces(
    key="Mod4+{letter}",
    move_key="Mod4+Shift+{letter}",
    entries={
        "A": Workspace(
            windows=["x2goclient", "X2GoAgent", "vncviewer", "Vncviewer"],
            launch="vncviewer",  # or x2goclient
            tabbed=True,
            auto_tiling=False,
        ),
        "D": Workspace(
            windows=["Goldendict"],
            launch="goldendict",
            also_open_if=["AppRun"],
        ),
        "E": Workspace(
            windows=["dolphin", "org.kde.dolphin"],
            launch="dolphin",
            bind_key=False,  # Super+E is the folder picker
        ),
        "G": Workspace(
            windows=["com.ayugram.desktop"],
            launch="AyuGram",
        ),
        "I": Workspace(
            windows=["Inkscape", "org.inkscape.Inkscape"],
            launch="inkscape",
            also_open_if=["Ld-linux-x86-64.so.2"],
            tabbed=True,
            auto_tiling=False,
        ),
        "J": Workspace(
            windows=["chrome-localhost__lab-Default"],
            launch="google-chrome-stable --use-gl=desktop --app=http://localhost:8888/lab --enable-extensions",
            also_open_if=["Google-chrome", "chrome"],
        ),
        "K": Workspace(
            windows=["virtuoso", "viva", "libManager", "Vsim"],
            auto_tiling=False,
        ),
        "L": Workspace(
            windows=["ltspice.exe"],
            launch="gtk-launch wine-Programs-LTspice-LTspice",
        ),
        "M": Workspace(
            windows=["org.mozilla.Thunderbird"],
            launch="thunderbird",
        ),
        "N": Workspace(
            windows=["kitty_nvim"],
            launch="kitty --single-instance --class kitty_nvim ~/coding/scripts/nn",
        ),
        "O": Workspace(
            windows=["obs", "com.obsproject.Studio"],
            launch="obs",
        ),
        "P": Workspace(
            windows=["okular", "org.kde.okular", "pdfxedit.exe"],
            launch="okular",
            tabbed=True,
            auto_tiling=False,
        ),
        "S": Workspace(
            windows=["Start.tcl", "start.tcl", "scidCommunity"],
            launch="~/Applications/extracted/scid/scid",
        ),
        "T": Workspace(
            windows=["chrome-deepl.com__-Default"],
            launch="google-chrome-stable --use-gl=desktop --app=http://deepl.com --enable-extensions",
            also_open_if=["Google-chrome", "chrome"],
        ),
        "U": Workspace(
            windows=["vmware", "Vmware"],
            launch="vmware",
        ),
        "V": Workspace(
            windows=["vlc", "smplayer"],
            tabbed=True,
            auto_tiling=False,
        ),
        "W": Workspace(
            windows=["chrome-web.whatsapp.com__-Default"],
            launch="google-chrome-stable --use-gl=desktop --app=http://web.whatsapp.com --enable-extensions",
            also_open_if=["Google-chrome", "chrome"],
        ),
        "X": Workspace(
            windows=["mogan", "Mogan", "moganstem", "MoganResearch", "texmacs", "texmacs.bin", "Texmacs.bin"],
            launch="mogan",
            tabbed=True,
            auto_tiling=False,
        ),
        "Y": Workspace(
            windows=["zotero"],
        ),
        "Z": Workspace(
            windows=["zoom"],
            launch="zoom",
            tabbed=True,
        ),
    },
)
# >>>

# scratchpads <<<
SCRATCHPADS = Scratchpads(
    rule="floating enable, resize set 1000 px 800 px, move position center, border pixel 5",
    entries={
        "Mod4+minus": Scratchpad(window="thunar", launch="thunar"),
        "Mod4+h": Scratchpad(window="org.kde.kwrite", launch="kwrite"),
    },
)
# >>>

# folder picker <<<

FOLDER_PICKER = FolderPicker(
    key="Mod4+e",
    mode="folders",
    folders={
        "c": "~/.config/",
        "d": "~/Downloads/",
        "g": "~/git/",
        "h": "~/",
        "l": "~/.local/",
        "r": "~/Recordings/",
        "v": "~/Videos/",
        "w": "~/Writing/texmacs",
    },
    workspace="E",
    open_folder="dolphin --select {marker}",
)
# >>>
