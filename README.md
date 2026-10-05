# My sway setup

This is my sway configuration. It's a normal sway config with a small Python
program on the side (the "controller") that handles the things sway can't do on
its own: one workspace per app, launching an app only when it isn't already
open, scratchpads that start their app the first time, a folder picker, and
keeping windows tiled in tidy columns.

If you just want to change a keybinding or a window rule, you only need the
sway `config` file. If you want to add an app with its own workspace, you only
need `controller/config.py`.

## What's where

```
config                  the sway config
controller/             the Python controller
  config.py             workspaces, monitors, scratchpads, folder picker, keys that run Python
  schema.py             what each field in config.py means
  keys.py               turns config.py into sway keybindings and rules
  actions.py            what those keys actually do
  tiling.py             keeps windows in side-by-side columns
  main.py               starts it all; its docstring has a map like this one
scripts/                small helpers (monitors, waybar, screenshots, ...)
waybar/                 the bar: layout, module settings, style
install.sh              installs the packages (Arch or Debian/Ubuntu)
```

A few things the config uses live next to these files but aren't in git:
`tools/wl-vcgt` (loads the laptop panel's colour calibration), the calibration
profile in `assets/`, and `alttab/` (a patched build of sway-alttab-gui for
Super+Tab). On a fresh machine you'll need to install them yourself, or comment
out the lines that use them.

## The two halves

**The sway config** holds everything sway can do by itself.

**The controller** holds everything that needs a bit of logic. It starts with
sway and restarts on every reload (Super+Shift+r), because a reload throws away
the keybindings and rules it sends.

**Background programs** that mustn't die quietly (the controller, waybar,
swayidle, and `wl-vcgt`) run as systemd user units named `sway-<program>`,
through `scripts/run-unit`. systemd restarts them if they crash and keeps their
logs. They're temporary units, created when sway starts them, so there are no
unit files to install. dunst runs from the unit its package ships. Everything
else is started once with a plain `exec`.

To see them: `systemctl --user list-units 'sway-*'`. To read one's log:
`journalctl --user -u sway-waybar` (and so on). To stop one for good while you
experiment: `systemctl --user stop sway-waybar`; Super+Shift+r brings waybar and
the controller back, the others come back at your next login.

The rule for deciding where something goes: if sway can do it alone, it goes in
the sway config. If the controller has to look at something first (is the app
already open? is this the first time?), it goes in `controller/config.py`.

## Keys worth knowing

Super is the Windows key.


| Key | What it does |
|---|---|
| Super+Return | terminal (kitty) |
| Alt+Space | app launcher (rofi) |
| Super+b | browser |
| Super+q | close window |
| Super+Shift+q | close every window on the workspace |
| Super+arrows / Super+Shift+arrows | move focus / move the window |
| Super+1…9 | numbered workspaces (1–4 on the laptop, 5–9 on the external monitor; set in `MONITORS`) |
| Super+Space | jump to an empty numbered workspace: on this monitor if there's one, else the other |
| Super+Shift+Space | move the window to an empty numbered workspace (same order) and follow it |
| Super+comma / Super+period | previous / next workspace on this monitor |
| Super+*letter* | that app's workspace, starting the app if it isn't open (see below) |
| Super+Shift+*letter* | send the window to that app's workspace |
| Super+e, then a letter | open a folder in Dolphin (c = ~/.config, d = Downloads, ...) |
| Super+minus / Super+h | Thunar / KWrite as a scratchpad |
| Super+grave | drop-down terminal (show / hide) |
| Super+Alt+d | do not disturb: pause notifications (the bar shows a bell while paused) |
| Super+Tab | switch between windows on this monitor |
| Super+c | clipboard history |
| Super+f | fullscreen |
| Super+Alt+t / f / s | tabbed / floating / sticky |
| Super+r | resize mode (arrows, then Escape) |
| Super+F7 | monitors: place, mirror or switch off |
| Print / Shift+Print / Ctrl+Print | screenshot a region / the screen / a region into a floating window |
| Super+Alt+i | click a window to get its name (for window rules) |
| Super+Shift+r | reload everything |
| Super+F5 | restart just the controller |
| Super+Escape | lock, log out, suspend, reboot, shut down |


## App workspaces

Most apps I use get a workspace named after a letter: P for PDFs (okular), M for
mail, Z for Zoom, and so on. Super+P takes you to P and opens okular if it isn't
already there. Windows of those apps are also moved to their workspace when they
open, wherever you started them from. The full list is `WORKSPACES` in
`controller/config.py`.

Some workspaces open their windows as tabs (`tabbed=True`), and some are left
out of the automatic column tiling (`auto_tiling=False`) so a layout you've
arranged by hand stays put.

## Adding things

**An app with its own workspace.** Find its window name with Super+Alt+i (click
the window; the name is copied to the clipboard), then add an entry to
`WORKSPACES` in `controller/config.py`:

```python
"P": Workspace(
    windows=["org.kde.okular"],
    launch="okular",
),
```

Reload with Super+Shift+r, and the letter's Super and Super+Shift keys work.
Every letter is taken at the moment, so a new app means replacing one, or using
B, F or H with `bind_key=False`: their Super keys do other things (browser,
fullscreen, KWrite), but Super+Shift+B/F/H are free to move windows there. The
other fields you can set are described in `controller/schema.py`.

**A plain keybinding or window rule.** Put it in the sway `config`, like in any
sway setup.

**A key that runs Python.** Write a method in `controller/actions.py` and add
its key to `ACTION_KEYS` in `controller/config.py`.

**A scratchpad.** Add an entry to `SCRATCHPADS` in `controller/config.py`.

**A folder for the picker.** Add a letter and path to `folders` in
`FOLDER_PICKER`.

Keys in `controller/config.py` are written the way sway spells them: `Mod4` is
Super, `Mod1` is Alt, e.g. `"Mod4+Shift+q"`. Don't bind the same key there and
in the sway config.

## Monitors and sleep

The screen locks after 10 minutes idle and switches off a minute later, except
while something is fullscreen or Zoom is open.

Super+F7 places a monitor (right of, left of, or above the laptop), mirrors the
laptop, or leaves one screen on. Each monitor's position is remembered. After
sleep, the monitors that were on come back on.

## When something doesn't work

- **The app keys or scratchpads do nothing:** the controller probably isn't
  running. Check `systemctl --user status sway-controller`, read its log with
  `journalctl --user -u sway-controller`, and restart it with Super+F5. Plain
  sway keys keep working without it.
- **The bar disappeared:** systemd restarts it; its log is
  `journalctl --user -u sway-waybar`. Super+Shift+r starts it if it's gone.

## Installing

`./install.sh install` installs the packages and adds a "Sway (nvidia)" session
for the login screen. The controller also needs `python-i3ipc`, and the config
expects kitty, dunst, rofi, polkit-gnome and feh to be around.
