#!/bin/bash

# Get out of here if dbus-send is not available
if command -v dbus-send >/dev/null 2>&1; then
    # dbus-send is installed, proceed
    :
else
echo -e "dbus-send not found.\nClosing..."
exit 1
fi

# check what name the qdbus command has
if command -v qdbus >/dev/null 2>&1; then
    qdbus_command="qdbus"
elif command -v qdbus-qt5 >/dev/null 2>&1; then
qdbus_command="qdbus-qt5"
elif command -v qdbus-qt6 >/dev/null 2>&1; then
qdbus_command="qdbus-qt6"
elif command -v qdbus6 >/dev/null 2>&1; then
qdbus_command="qdbus6"
else
echo qdbus/qdbus-qt5/qdbus-qt6/qdbus6 not found
exit 1
fi


restore_clipboard_content() {
local clipboard_content="${1}"
# if the user had copied a file before opening the program, restoring just the text is not enough.
# the "file:///" prefix indicates that the last item copied to the clipboard by the user was a file or folder.
if   ! [  $(echo "${clipboard_content}" | grep "file:///") ] ; then
# plain text, klipper is enough
dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents string:"${clipboard_content}"
return
fi

binary_exec=""
copy_command=""

# check if it is using wayland or X11
if [ $(echo $XDG_SESSION_TYPE | grep -i "wayland") ];then
# wayland
binary_exec="wl-copy"
copy_command='wl-copy -t  text/uri-list "'$clipboard_content'"'
elif [ $(echo $XDG_SESSION_TYPE | grep -E -i 'x11|xorg') ];then
# X11
binary_exec="xclip";
copy_command="echo '${clipboard_content}' | xclip -sel clip -t text/uri-list"
else
# error, use klipper
echo Error: Unable to identify session type. Switching to klipper...
dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents string:"${clipboard_content}"
return
fi
#  Check if the exec is installed.
if command -v $binary_exec >/dev/null 2>&1; then
# run the command
bash -c "${copy_command}"
if [ "$?" != "0" ]; then
# failed, use klipper
echo Error: Failed to restore clipboard content using: $binary_exec
dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents string:"${clipboard_content}"
fi
return
else
# failed, use klipper
echo Error: Failed to restore clipboard content: $binary_exec is not installed
dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents string:"${clipboard_content}"
return

fi
}


#additional attributes to pass if necessary
parameter=""

original_clipboard_content="$(dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents | grep -v "method return time=" | sed -r '1s/^\s+//g' | sed ' s/^string "//' | sed '$ s/"$//')"
[ "$?" != "0" ] && exit 1
sleep 0.1

#search for the process of dolphin
windows=$($qdbus_command | grep -i dolphin)
dolphin=""

#controls which dolphin window is active
for w in $windows; do

is_active_window=$(dbus-send --session --print-reply --dest=$w /dolphin/Dolphin_1 org.freedesktop.DBus.Properties.Get string:org.qtproject.Qt.QWidget string:isActiveWindow)
[ "$?" != "0" ] && exit 1
[ "$( echo $is_active_window | grep -i true)" ] &&  dolphin="$w"

done

[ "$dolphin" = "" ] &&  exit 1

# sets the clipboard contents to " " to remove possible paths previously copied by the user.
dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.setClipboardContents string:" "
[ "$?" != "0" ] && exit 1

#sends the signal to dolphin to copy the location of the current file to the clipboard.
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/copy_location org.qtproject.Qt.QAction.trigger
[ "$?" != "0" ] && restore_clipboard_content "$original_clipboard_content" && exit 1

sleep 0.1
#gets clipboard contents from klipper
path="$(dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents | grep string | cut -d'"' -f2)"
[ "$?" != "0" ] && restore_clipboard_content "$original_clipboard_content" && exit 1



#if there is no selection.
#if the path is invalid (no selection), sends the signal to select all files and the signal to copy the location again.
# if no file is selected dolphin does not copy the path and this can be used to understand if there was a file selected or not.
if [ ! -e "$path" ]; then
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/edit_select_all org.qtproject.Qt.QAction.trigger
[ "$?" != "0" ] && restore_clipboard_content "$original_clipboard_content" && exit 1
sleep 0.1
#enables copying the file path even if multiple files are selected (plasma 6)
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/copy_location org.qtproject.Qt.QAction.resetEnabled
#gets file location
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/copy_location org.qtproject.Qt.QAction.trigger
[ "$?" != "0" ] && restore_clipboard_content "$original_clipboard_content" && exit 1
sleep 0.1
path=$(dbus-send --session --print-reply --type=method_call --dest=org.kde.klipper /klipper org.kde.klipper.klipper.getClipboardContents | grep string | cut -d'"' -f2)
[ "$?" != "0" ] && restore_clipboard_content "$original_clipboard_content" && exit 1
#deselect what was previously selected (aesthetic reason)
dbus-send --session --print-reply --type=method_call --dest=$dolphin /dolphin/Dolphin_1/actions/invert_selection org.qtproject.Qt.QAction.trigger
[ "$?" != "0" ] && restore_clipboard_content "$original_clipboard_content" && exit 1


# the parent folder becomes the path.
# this is done because if nothing is selected, I want to show information about the parent folder.
path="$(echo "$path" | rev |  cut -d'/' -f2-100 | rev)"




elif [ -e "$path" ]; then
# if the path is valid (the user had selected a file), set the variable to "-s"(selected):
parameter="-s"
fi

#restore clipboard content
restore_clipboard_content "$original_clipboard_content"
#run quick view
~/.config/quick_view/quick_view.pyz "$path" $parameter






