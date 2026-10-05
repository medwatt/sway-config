#!/usr/bin/env bash
set -euo pipefail

# Install or remove everything the sway session needs (Arch or Ubuntu/Debian).
#   ./install.sh install
#   ./install.sh uninstall

PKGS=(
    sway swaybg foot        # compositor, wallpaper, fallback terminal
    waybar                  # bar
    swaylock swayidle       # lock screen, idle/suspend handling
    grim slurp wl-clipboard # screenshots, clipboard tools
    wtype                   # typing keys into wayland windows (scripts/neovim_terminal)
    cliphist                # clipboard history
    brightnessctl           # backlight keys
    xdg-desktop-portal-wlr  # screen sharing (zoom, obs, browsers)
    wl-mirror               # display clone (scripts/display-mode)
    rofi                    # launcher, clipboard picker, display menu
)
AUR_PKGS=(sway-alttab-gui-bin) # window switcher (replaces alttab); Arch only

# LightDM's stock sway session refuses to start with the nvidia driver loaded.
SESSION=/usr/share/wayland-sessions/sway-nvidia.desktop

case "${1:-}" in
install)
    if command -v pacman >/dev/null; then
        sudo pacman -S --needed "${PKGS[@]}"
        yay -S --needed "${AUR_PKGS[@]}"
    else
        sudo apt-get install "${PKGS[@]}"
    fi
    sudo tee "$SESSION" >/dev/null <<'EOF'
[Desktop Entry]
Name=Sway (nvidia)
Comment=Sway with --unsupported-gpu
Exec=sway --unsupported-gpu
DesktopNames=sway
Type=Application
EOF
    ;;
uninstall)
    if command -v pacman >/dev/null; then
        mapfile -t installed < <(pacman -Qq "${PKGS[@]}" "${AUR_PKGS[@]}" 2>/dev/null || true)
        ((${#installed[@]})) && sudo pacman -Rns "${installed[@]}"
    else
        sudo apt-get remove --autoremove "${PKGS[@]}"
    fi
    sudo rm -f "$SESSION"
    ;;
*)
    echo "usage: $0 install|uninstall" >&2
    exit 1
    ;;
esac
