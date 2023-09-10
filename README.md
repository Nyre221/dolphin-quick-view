## dolphin-quick-view

Simple program to have a quick preview of the files in a folder (similar to Apple's Quick Look)

![Screenshot-10-09-2023-CEST](https://github.com/Nyre221/dolphin-quick-view/assets/104171042/38bfe4e8-80da-4634-98d9-00a0f2a8c1ad)

Supported files: mp3,mp4,jpg,webp,svg,svgz,doc,docx,odt,xls,xlsx,csv,ods,md,pdf

# Installation:
1: Download the latest release from here and extract it: https://github.com/Nyre221/dolphin-quick-view/releases/

2: Install the dependencies (README_REQUIREMENTS.txt)

3: Make the "INSTALL.sh" file executable (right click-> properties->check "executable") and run it

4: If you want to open it with a shortcut and not just via dolphin's context menu:
go to plasma settings -> shortcuts -> add a shortcut that executes a command: /home/YOUR_USERNAME/.config/quick_view/dolphin_quick_view_shortcut.sh 

(you can activate the shortcut as you want)


# Common Quick view shortcuts:
a, b and arrow keys = back and forward

spacebar = open with default app

q = quit


# Debug:
If quick view doesn't open via dolphin's dropdown menu:
open a terminal and type "dolphin", error messages will appear in the terminal window (possible missing dependencies)

if dolphin_quick_view_shortcut.sh doesn't work, run: "sleep 5 ; ~/.config/quick_view/dolphin_quick_view_shortcut.sh" in a terminal and reactivate a dolphin window (you have 5 seconds).
The errors should appear there.

if the pdfs are not visible it is because you have not installed python3-qpageview or python3-poppler-qt5 (names may differ a bit)

if some mp4 files don't play it's probably because you're missing some gstreamer library



# Support me: https://www.paypal.com/donate/?hosted_button_id=J7QU55MMUP4G4
