#!/usr/bin/env python3
"""Sway controller: started by ../scripts/start-controller, restarted on every sway reload.

Where things are:
  config.py             what the controller acts on: workspaces, monitors, scratchpads, folders, ACTION_KEYS
  schema.py             the fields of each entry in config.py
  keys.py               every key the controller binds, and the workspace rules
  actions.py            everything a key can do
  tiling.py             auto-tiling, run after every window event
  main.py               startup: sends the rules, binds the keys, runs action keys when pressed

Adding things:
  an app on its own workspace   an entry in WORKSPACES.entries (config.py)
  a key that runs Python        a method in actions.py, its key in ACTION_KEYS
  a feature with its own data   a dataclass in schema.py, its entry in config.py,
                                its keys in keys.py, its methods in actions.py
  a plain key or window rule    the sway config, not here
"""

# imports <<<
import logging

from i3ipc import Connection, Event

from actions import Actions
from keys import action_keys, plain_keys, rules
from tiling import repair_all
# >>>


def _safe(fn):
    """Wrap an event callback so a raised exception is logged
    instead of tearing down the event loop."""

    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            logging.exception("handler %r failed", getattr(fn, "__name__", fn))

    return wrapper


class Controller:
    def __init__(self):
        self.bound = {}  # "nop" argument ("mode:key") -> action, filled by bind_keys

    def run(self):
        self.sway = Connection()

        # Sway's reload drops everything sent here; the sway config restarts
        # the controller on every reload (exec_always), which sends it again.
        for rule in rules():
            self.send(rule)
        self.bind_keys(Actions(self.sway))

        def retile(sway, event):
            repair_all(sway)

        for event in (
            Event.WINDOW_NEW,
            Event.WINDOW_CLOSE,
            Event.WINDOW_MOVE,
            Event.WINDOW_FLOATING,
        ):
            self.sway.on(event, _safe(retile))
        self.sway.on(Event.BINDING, _safe(self.on_binding))
        self.sway.main()

    def send(self, command):
        for reply in self.sway.command(command):
            if not reply.success:
                logging.error("sway rejected %r: %s", command, reply.error)

    def bind_keys(self, actions):
        # Always name the mode: a bare bindsym goes into whichever mode is
        # active, e.g. "folders" if the controller restarts while picking.
        taken = set()

        def bind(mode, key, command):
            if (mode, key) in taken:
                logging.warning("%s:%s is bound twice in config.py; the last one wins", mode, key)
            taken.add((mode, key))
            self.send(f"mode {mode} bindsym {key} {command}")

        for mode, key, command in plain_keys():
            bind(mode, key, command)
        for mode, key, action in action_keys(actions):
            name = f"{mode}:{key}"
            self.bound[name] = action
            bind(mode, key, f"nop {name}")

    def on_binding(self, sway, event):
        # action keys run "nop <mode>:<key>"; anything else is a plain binding
        nop, _, name = event.binding.command.partition(" ")
        if nop == "nop" and name in self.bound:
            self.bound[name]()


if __name__ == "__main__":
    # stderr goes to the journal: journalctl --user -u sway-controller
    logging.basicConfig(format="[controller] %(message)s")
    Controller().run()
