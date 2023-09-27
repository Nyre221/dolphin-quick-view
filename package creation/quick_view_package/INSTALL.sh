#!/bin/bash

# Installer script for Quick View, a previewer for the Dolphin file manager
# https://github.com/Nyre221/dolphin-quick-view

SELF=$(readlink -f "$0")
HERE=${SELF%/*}

exit_w_error() {
    local msg="$1"
    echo -e "\nERROR: ${msg} Exiting...\n"
    exit 1
}

# Check if the script is being run as root
if [[ ${EUID} -eq 0 ]]; then
    exit_w_error "This script must not be run as root."
fi


echo -e "\nInstalling Quick View previewer for Dolphin..."

mkdir -p ~/.config/quick_view || \
    exit_w_error "Failed to create install folder."

mkdir -p ~/.local/share/kservices5/ServiceMenus/ || \
    exit_w_error "Failed to create ServiceMenus folder."

cp "$HERE"/quick_view.pyz ~/.config/quick_view || \
    exit_w_error "Failed to copy 'quick_view.pyz' file."

chmod +x ~/.config/quick_view/quick_view.pyz || \
    exit_w_error "Failed to set 'quick_view.pyz' as executable."

cp "$HERE"/dolphin_quick_view_shortcut.sh ~/.config/quick_view || \
    exit_w_error "Failed to copy shortcut script."

chmod +x ~/.config/quick_view/dolphin_quick_view_shortcut.sh || \
    exit_w_error "Failed to set shortcut script as executable."

cp "$HERE"/quick_view.desktop ~/.local/share/kservices5/ServiceMenus/ || \
    exit_w_error "Failed to copy desktop file to ServiceMenus folder."


ntfy_title="Quick View Installer"
ntfy_icon="quickview"
ntfy_msg="Quick View successfully installed"
ntfy_time_ms=5000
# ntfy_time_s=$((${ntfy_time_ms}/1000))     # in case something needs the timeout in seconds

#send desktop notification
if command -v gdbus >/dev/null 2>&1; then
    gdbus call --session \
        --dest=org.freedesktop.Notifications \
        --object-path=/org/freedesktop/Notifications \
        --method=org.freedesktop.Notifications.Notify \
        "${ntfy_title}" 0 "${ntfy_icon}" \
        "${ntfy_msg}" "" '[]' '{"urgency": <1>}' "${ntfy_time_ms}" >/dev/null 2>&1
elif command -v notify-send >/dev/null 2>&1; then
    notify-send --expire-time="${ntfy_time_ms}" --icon="${ntfy_icon}" \
        "${ntfy_title}" "${ntfy_msg}" >/dev/null 2>&1
elif command -v kdialog >/dev/null 2>&1; then
    kdialog --icon "${ntfy_icon}" --title "${ntfy_title}" \
        --passivepopup "${ntfy_msg}" "${ntfy_time_ms}ms" >/dev/null 2>&1
else
    echo -e "\nINFO: Installer script cannot show 'success' desktop notification."
    echo "Reason: No suitable notification command available on system."
    echo "(This only affects the installer script.)"
fi

echo -e "\nQuick View successfully installed.\n"
