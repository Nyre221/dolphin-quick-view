https://gist.github.com/lukassup/cf289fdd39124d5394513a169206631c

commands to run:

#includes some dependency inside the project folder. Useful for lowering the number of dependencies that users need to install.
1: pip install -t /path/to/project/quick-view -r /path/to/requirements.txt
#create the pyz package.
#the .pyz should be placed inside the folder with INSTALL.sh and the shortcut (quick_view_package).
2: python3 -m zipapp /path/to/project/quick_view/ -p /bin/python3 -o ./quick_view_package/quick_view.pyz -c

3: compress the folder quick_view_package into tar.gz




