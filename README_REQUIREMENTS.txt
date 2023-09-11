Required dependencies:

kubuntu 20
sudo apt install python3-pip python3-qpageview python3-pyqt5.qtsvg  python3-pyqt5.qtmultimedia antiword  python3-poppler-qt5 gstreamer1.0-libav
pip install pyexcel pyexcel-xls pyexcel-xlsx textract


kubuntu 22
sudo apt install antiword python3-pyqt5.qtmultimedia gstreamer1.0-libav python3-poppler-qt5 python3-pip python3-qpageview
pip install pyexcel pyexcel-xls pyexcel-xlsx textract


kubuntu 23
sudo apt install python3-pyqt5.qtmultimedia python3-poppler-qt5 python3-pip python3-qpageview antiword gstreamer1.0-libav
pip install pyexcel pyexcel-xls pyexcel-xlsx textract --break-system-packages



fedora 37
sudo dnf install python3-qt5 python3-poppler-qt5 antiword gstreamer1-plugin-libav gstreamer1-plugin-openh264 python3-qpageview
pip install pyexcel pyexcel-xls pyexcel-xlsx textract



fedora 38
sudo dnf install python3-qt5 python3-pip antiword python3-poppler-qt5 python3-qpageview gstreamer1-plugin-libav gstreamer1-plugin-openh264
pip install pyexcel pyexcel-xls pyexcel-xlsx
pip install textract



manjaro:
sudo pacman -S python-pyqt5 python-poppler-qt5  python-pip  python-qpageview antiword
yay -S python-pyexcel python-pyexcel-xls python-pyexcel-xlsx
pip install textract --break-system-packages

