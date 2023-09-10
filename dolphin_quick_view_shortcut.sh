#!/bin/bash
# clears clipboard
dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.clearClipboardHistory | grep string | cut -d'"' -f2


#search for the process of dolphin
windows=$(qdbus | grep -i dolphin)
dolphin=""

#controls which dolphin window is active
for w in $windows; do

is_active_window=$(dbus-send --session --print-reply --type=method_call --dest=$w /dolphin/Dolphin_1 org.kde.dolphin.MainWindow.isActiveWindow)

[ "$( echo $is_active_window | grep -i true)" ] &&  dolphin="$w"

done


[ "$dolphin" = "" ] &&  exit 1

#sends the signal to dolphin to copy the location of the current file to the clipboard.
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/copy_location org.qtproject.Qt.QAction.trigger
sleep 0.1
#gets clipboard contents from klipper
path="$(dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents | grep string | cut -d'"' -f2)"


#if the path is empty, sends the signal to select all files and sends the signal to copy the location again.
#(if no file is selected dolphin does not copy the path to the clipboard)
if [ "$path" = "" ]; then

dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/edit_select_all org.qtproject.Qt.QAction.trigger
sleep 0.1
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/copy_location org.qtproject.Qt.QAction.trigger
sleep 0.1
path=$(dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents | grep string | cut -d'"' -f2)
#deselect what was previously selected (aesthetic reason)
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/invert_selection org.qtproject.Qt.QAction.trigger

#if the file is a folder, go back one folder. 
#this is necessary because dolphin can also copy the location of a folder and the python program would show the contents of that folder and not the current one.
#(This part of code runs only if no specific file was selected.)
if [[ -d "$path" ]]; then

path="$(echo "$path" | rev |  cut -d'/' -f2-100 | rev)"

fi



fi
#run quick view
~/.config/quick_view/quick_view.pyz "$path"
