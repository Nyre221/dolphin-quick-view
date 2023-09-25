import qpageview
import shutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt, pyqtSignal
from translation_manager import Translator
import sys
import subprocess
from threading import Thread
import tempfile
import shlex
import os
import signal
import time
from queue import Queue


class FallbackViewer(QWidget):


    def __init__(self, parent=None):
        super(FallbackViewer, self).__init__(parent)
        # to get translations
        self.translator = Translator()
        # name font
        self.font_label_message_name = QFont()
        self.font_label_message_name.setPointSize(14)
        self.font_label_message_name.setBold(True)
        # header font
        self.font_label_message = QFont()
        self.font_label_message.setPointSize(11)
        self.font_label_message.setBold(True)

        # img
        self.logo_img = QLabel()
        self.logo_img.setAlignment(Qt.AlignCenter)
        # sets the image size based on the screen size
        self.logo_size = QApplication.primaryScreen().size()*0.135
        self.logo_img.setPixmap(QPixmap("/usr/share/icons/breeze-dark/mimetypes/64/unknown.svg").scaled(
            self.logo_size, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation))

        # labels
        self.label_message_name = QLabel()
        self.label_message_name.setAlignment(Qt.AlignCenter)
        self.label_message_name.setFont(self.font_label_message_name)
        self.label_message = QLabel()
        self.label_message.setFont(self.font_label_message)
        self.label_message.setAlignment(Qt.AlignCenter)

        # layouts
        # main
        self.layout_main = QVBoxLayout()
        self.setLayout(self.layout_main)

        # adding to layout
        self.layout_main.addWidget(self.logo_img)
        self.layout_main.addWidget(self.label_message_name)
        self.layout_main.addWidget(self.label_message)
        self.layout_main.insertStretch(-1)

        # placeholder
        self.__set_placeholder_text__()

    def load_file(self, path):
        self.label_message_name.setText(path.split("/")[-1])

    def __set_placeholder_text__(self):
        self.label_message_name.setText("Name")
        self.label_message.setText(self.translator.get_translation("unsupported_file_type"))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = FallbackViewer()
    widget.resize(640, 480)
    widget.show()
    sys.exit(app.exec_())
