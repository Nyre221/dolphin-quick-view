#!/bin/python3

# import QT
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStyle, \
    QSizePolicy, QLabel , QShortcut
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
# import viewers
from page_viewer import PageViewer
from text_viewer import TextViewer
from table_viewer import TableViewer
from video_viewer import VideoViewer
# other
from glob import glob
import textract
import subprocess
import sys
import os


class Main(QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app

        # a way to access and check if the widget has been created
        self.added_widgets = []
        self.page_viewer = None
        self.media_player = None
        self.text_viewer = None
        self.table_viewer = None

        if len(sys.argv) < 2:
            print("No path or file given")
            exit()

        if os.path.isfile(sys.argv[1]):
            self.current_file = sys.argv[1]
            self.current_path = os.path.dirname(self.current_file)
            self.files = glob(f"{self.current_path}/*.*")
            self.current_index = self.files.index(self.current_file)
        elif os.path.isdir(sys.argv[1]):
            self.current_path = sys.argv[1]
            self.files = glob(f"{self.current_path}/*.*")
            self.current_file = self.files[0]
            self.current_index = 0
        else:
            print("File or directory not found")
            exit()

        # setting up ui
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_FileDialogContentsView))
        screen_size = app.primaryScreen().size()
        self.resize(int(screen_size.width() * 0.5), int(screen_size.height() * 0.55))
        self.create_ui()
        self.set_shortcut()
        self.setFocus()
        self.load_file_at_index(self.current_index)

    def create_ui(self):
        # central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # main layout
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # controls layout
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(0, 0, 0, 0)

        # file not supported label (just repeat the name for now)
        self.error_label = QLabel()
        # adds the label to the list of added widgets so that it disappears automatically when you select another file.
        self.added_widgets.append(self.error_label)
        font = QFont("Monospace")
        font.setPointSize(15)

        self.error_label.setFont(font)
        # self.error_label.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        self.error_label.setWordWrap(True)
        self.error_label.setAlignment(Qt.AlignCenter)

        # viewer_container and layout
        self.viewer_container = QWidget()
        self.viewer_container_layout = QVBoxLayout(self.viewer_container)
        self.viewer_container_layout.setContentsMargins(0, 0, 0, 0)

        # back button
        self.back_button = QPushButton()
        self.back_button.setFixedHeight(24)
        self.back_button.setMinimumWidth(80)
        self.back_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowLeft))

        # forward button
        self.forward_button = QPushButton()
        self.forward_button.setFixedHeight(24)
        self.forward_button.setMinimumWidth(80)
        self.forward_button.setIcon(self.style().standardIcon(QStyle.SP_ArrowRight))

        # open button
        self.open_button = QPushButton()
        self.open_button.setFixedHeight(24)
        self.open_button.setMinimumWidth(80)
        self.open_button.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed))
        self.open_button.setIcon(self.style().standardIcon(QStyle.SP_DialogOpenButton))

        # button signal
        self.back_button.pressed.connect(self.back)
        self.forward_button.pressed.connect(self.forward)
        self.open_button.pressed.connect(self.open_with_app)

        # adding to layouts
        self.viewer_container_layout.addWidget(self.error_label)
        controls_layout.addWidget(self.back_button)
        controls_layout.addWidget(self.open_button)
        controls_layout.addWidget(self.forward_button)
        self.main_layout.addWidget(self.viewer_container)
        self.main_layout.addLayout(controls_layout)

    def load_file_at_index(self, index):
        self.hide_widgets()
        self.current_file = self.files[index]
        self.setWindowTitle(self.current_file.split("/")[-1])
        extension = os.path.splitext(self.current_file.lower())[-1]

        if extension in ".pdf":
            self.load_page_viewer(self.current_file, "pdf")

        elif extension in [".png", ".jpeg", ".jpg", ".webp"]:
            self.load_page_viewer(self.current_file, "img")

        elif extension in [".svg", ".svgz"]:
            self.load_page_viewer(self.current_file, "svg")

        elif extension in [".mp4", ".mp3"]:
            self.load_video_viewer(self.current_file)

        elif extension in [".doc", ".docx", ".odt", ".txt"]:
            text = textract.process(self.current_file).decode("utf-8")
            self.load_text_viewer(text)

        elif extension in ".md":
            with open(self.current_file, "r") as f:
                self.load_text_viewer(f.read(), markdown=True)

        elif extension in [".ods", ".xlsx", ".xls", ".csv"]:
            self.load_table_viewer(self.current_file)

        # for simple text (.sh,.txt,.xml,.html,etc) which may or may not have an extension.
        # I didn't want to download yet another python module, and so I use subprocess.
        elif "text/" in subprocess.run(["file", "--mime-type", self.current_file],
                                       stdout=subprocess.PIPE).stdout.decode("utf-8"):
            with open(self.current_file, "r") as f:
                self.load_text_viewer(f.read())

        else:
            self.error_label.setText(os.path.basename(self.current_file))
            self.error_label.show()

    # to extend compatibility I used an if ladder, in the future I will remove it.
    # (needs to be updated)
    # match extension:
    #     case  ".pdf":
    #         self.load_page_viewer(self.current_file,"pdf")
    #     case f if f in [".png",".jpeg",".jpg"]:
    #         self.load_page_viewer(self.current_file,"img")
    #     case ".svg":
    #         self.load_page_viewer(self.current_file,"svg")
    #     case f if f in [".mp4",".mp3"]:
    #         self.load_video_viewer(self.current_file)
    #     case f if f in [".doc",".docx",".odt",".txt"]:
    #         text = textract.process(self.current_file).decode("utf-8")
    #         self.load_text_viewer(text)
    #     case f if f in [".xml",".html"]:
    #         with open(self.current_file,"r") as f:
    #              self.load_text_viewer(f.read())
    #     case f if f in [".ods",".xlsx",".xls",".csv"]:
    #         self.load_table_viewer(self.current_file)
    #     case _:
    #         self.error_label.setText(os.path.basename(self.current_file))
    #         self.error_label.show()

    def load_table_viewer(self, path):
        if self.table_viewer is None:
            self.table_viewer = TableViewer(self)
            self.add_widget(self.table_viewer)

        self.table_viewer.load_file(path)
        self.table_viewer.show()

    def load_text_viewer(self, text, markdown=False):
        if self.text_viewer is None:
            self.text_viewer = TextViewer(self)
            self.add_widget(self.text_viewer)

            font = QFont("Monospace")
            self.text_viewer.setFont(font)
            self.text_viewer.zoomIn(3)

        # here I remove the previously set text to avoid showing the contents of another file if something wrong happens.
        self.text_viewer.clear()

        if markdown:
            self.text_viewer.setMarkdown(text)
        else:
            self.text_viewer.setText(text)

        self.text_viewer.show()

    def load_video_viewer(self, path):
        if self.media_player is None:
            self.media_player = VideoViewer(self)
            self.add_widget(self.media_player)

        self.media_player.open(path)
        self.media_player.show()

    def load_page_viewer(self, path, _type):
        if self.page_viewer is None:
            self.page_viewer = PageViewer(self)
            self.add_widget(self.page_viewer)

        if _type == "pdf":
            self.page_viewer.loadPdf(path)
            self.page_viewer.pdf_mode()
        elif _type == "img":
            self.page_viewer.loadImages([path])
            self.page_viewer.img_mode()
        elif _type == "svg":
            self.page_viewer.loadSvgs([path])
            self.page_viewer.img_mode()

        # to extend compatibility I used an if ladder, in the future I will remove it.
        # match type:
        #     case  "pdf": 
        #         self.page_viewer.loadPdf(path)
        #         self.page_viewer.pdf_mode()
        #     case "img":
        #         self.page_viewer.loadImages([path])
        #         self.page_viewer.img_mode()
        #     case "svg":
        #         self.page_viewer.loadSvgs([path])
        #         self.page_viewer.img_mode()

        self.page_viewer.show()

    def add_widget(self, widget):
        self.viewer_container_layout.addWidget(widget)
        self.added_widgets.append(widget)

    def open_with_app(self):
        subprocess.run(["xdg-open", self.current_file])
        exit()

    def back(self):
        if self.current_index == 0:
            self.current_index = self.current_index = len(self.files) - 1
        else:
            self.current_index = self.current_index - 1
        self.load_file_at_index(self.current_index)

    def forward(self):

        if len(self.files) - 1 == self.current_index:
            self.current_index = 0
        else:
            self.current_index = self.current_index + 1
        self.load_file_at_index(self.current_index)

    def hide_widgets(self):
        for w in self.added_widgets:
            w.hide()

    def set_shortcut(self):
        for shortcut_close in ["q", Qt.Key_Escape, Qt.Key_Space]:
            QShortcut(shortcut_close, self).activated.connect(exit)

        for shortcut_back in ["a", Qt.Key_Left]:
            QShortcut(shortcut_back, self).activated.connect(self.back)

        for shortcut_forward in ["d", Qt.Key_Right]:
            QShortcut(shortcut_forward, self).activated.connect(self.forward)

        for shortcut_open in ["w", Qt.Key_Up]:
            QShortcut(shortcut_open, self).activated.connect(self.open_with_app)


def launch():
    app = QApplication(sys.argv)
    window = Main(app)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch()
