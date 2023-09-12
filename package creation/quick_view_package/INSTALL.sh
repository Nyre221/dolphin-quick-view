#!/bin/bash
SELF=$(readlink -f "$0")
HERE=${SELF%/*}



mkdir -p ~/.config/quick_view
[ "$?" != "0" ] && exit 1
mkdir -p ~/.local/share/kservices5/ServiceMenus/
[ "$?" != "0" ] && exit 1
cp "$HERE"/quick_view.pyz ~/.config/quick_view
[ "$?" != "0" ] && exit 1
chmod +x ~/.config/quick_view/quick_view.pyz
[ "$?" != "0" ] && exit 1
cp "$HERE"/dolphin_quick_view_shortcut.sh ~/.config/quick_view
[ "$?" != "0" ] && exit 1
chmod +x ~/.config/quick_view/dolphin_quick_view_shortcut.sh
[ "$?" != "0" ] && exit 1
cp "$HERE"/quick_view.desktop ~/.local/share/kservices5/ServiceMenus/
[ "$?" != "0" ] && exit 1


#send desktop notification
if command -v gdbus >/dev/null 2>&1; then
gdbus call --session   --dest=org.freedesktop.Notifications   --object-path=/org/freedesktop/Notifications   --method=org.freedesktop.Notifications.Notify   ""   0   "quickview"   "Quick View installed"   ""   '[]'   '{"urgency": <1>}'   5000 >/dev/null
fi

echo -e "\n\nINSTALLED"
