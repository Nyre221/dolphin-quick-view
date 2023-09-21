Installation:
1: Install the requirements: https://github.com/Nyre221/dolphin-quick-view/tree/main/Requirements

2: Make the "INSTALL.sh" file executable (right click-> properties->check "executable") and run it

3: If you want to open it with a shortcut and not just via dolphin's context menu: go to plasma settings -> shortcuts -> add a shortcut that executes a command: /home/YOUR_USERNAME/.config/quick_view/dolphin_quick_view_shortcut.sh (you can activate the shortcut as you want)

Common Quick view shortcuts:
a,d and arrow keys (right/left) = back and forward
arrow keys (down/up) = scroll
spacebar, q and ESC = quit
"w" and return key = open with default app




Debug:
If quick view doesn't open via dolphin's dropdown menu:
open a terminal and type "dolphin", error messages will appear in the terminal window (possible missing dependencies)

if dolphin_quick_view_shortcut.sh doesn't work, run: "sleep 5 ; ~/.config/quick_view/dolphin_quick_view_shortcut.sh" in a terminal and reactivate a dolphin window.
(you have 5 seconds). The errors should appear there.
alternatively you can use this command: ~/.config/quick_view/quick_view.pyz /path/to/some/file -s

if the pdfs are not visible it is because you have not installed python3-qpageview or python3-poppler-qt5 (names may differ a bit)

if some mp4 files don't play it's probably because you're missing some gstreamer library


