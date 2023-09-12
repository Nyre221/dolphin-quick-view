#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}



mkdir -p ~/.config/quick_view

mkdir -p ~/.local/share/kservices5/ServiceMenus/

cp "$HERE"/quick_view.pyz ~/.config/quick_view
chmod +x ~/.config/quick_view/quick_view.pyz

cp "$HERE"/dolphin_quick_view_shortcut.sh ~/.config/quick_view
chmod +x ~/.config/quick_view/dolphin_quick_view_shortcut.sh

cp "$HERE"/quick_view.desktop ~/.local/share/kservices5/ServiceMenus/

#send desktop notification
gdbus call --session   --dest=org.freedesktop.Notifications   --object-path=/org/freedesktop/Notifications   --method=org.freedesktop.Notifications.Notify   ""   0   "quickview"   "Quick View installed"   ""   '[]'   '{"urgency": <1>}'   5000


echo -e "\n\n\nINSTALLED"
