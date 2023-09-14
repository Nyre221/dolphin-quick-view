#!/bin/bash

# Get out of here if dbus-send is not available
if command -v dbus-send >/dev/null 2>&1; then
    # dbus-send is installed, proceed
    :
else
echo -e "dbus-send not found.\nClosing..."
exit 1
fi

original_clipboard_content="$(dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents | grep -v "method return time=" | sed -r '1s/^\s+//g' | sed ' s/^string "//' | sed '$ s/"$//')"
sleep 0.1
# "clear" the clipboard.
# by using setClipboardContents the clipboard history is not cancelled and the last copied element can be restored later.
dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents string:" "
[ "$?" != "0" ] && exit 1
#search for the process of dolphin
windows=$(qdbus | grep -i dolphin)
dolphin=""

#controls which dolphin window is active
for w in $windows; do

is_active_window=$(dbus-send --session --print-reply --type=method_call --dest=$w /dolphin/Dolphin_1 org.qtproject.Qt.QWidget.isActiveWindow)
[ "$?" != "0" ] && exit 1
[ "$( echo $is_active_window | grep -i true)" ] &&  dolphin="$w"

done


[ "$dolphin" = "" ] &&  exit 1

#sends the signal to dolphin to copy the location of the current file to the clipboard.
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/copy_location org.qtproject.Qt.QAction.trigger
[ "$?" != "0" ] && exit 1
sleep 0.1
#gets clipboard contents from klipper
path="$(dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents | grep string | cut -d'"' -f2)"
[ "$?" != "0" ] && exit 1


#if the path is invalid, sends the signal to select all files and sends the signal to copy the location again.
#(if no file is selected dolphin does not copy the path to the clipboard)
if [ ! -e "$path" ]; then

dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/edit_select_all org.qtproject.Qt.QAction.trigger
[ "$?" != "0" ] && exit 1
sleep 0.1
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/copy_location org.qtproject.Qt.QAction.trigger
[ "$?" != "0" ] && exit 1
sleep 0.1
path=$(dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents | grep string | cut -d'"' -f2)
[ "$?" != "0" ] && exit 1
#deselect what was previously selected (aesthetic reason)
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/invert_selection org.qtproject.Qt.QAction.trigger
[ "$?" != "0" ] && exit 1

#if the file is a folder, go back one folder.
#this is necessary because dolphin can also copy the location of a folder and the python program would show the contents of that folder and not the current one.
#(This part of code runs only if no specific file was selected.)
if [[ -d "$path" ]]; then

path="$(echo "$path" | rev |  cut -d'/' -f2-100 | rev)"

fi



fi

#restore clipboard content
#Note: this unfortunately restores everything as text and therefore it is impossible to paste files, etc, even if the full path is in the clipboard.
dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents string:"$original_clipboard_content"

#run quick view
~/.config/quick_view/quick_view.pyz "$path"
