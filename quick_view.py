#!/bin/python3

# import QT
from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStyle, \
    QSizePolicy
from PySide6.QtGui import QCloseEvent, QFont, QShortcut
from PySide6.QtCore import Qt,QSize,QSettings
# import viewers
from document_viewer import DocumentViewer
from image_viewer import ImageViewer
from text_viewer import TextViewer
from video_viewer import VideoViewer
from container_viewer import ContainerViewer
from fallback_viewer import FallbackViewer
# other
from glob import glob
import subprocess
import sys
import os


class Main(QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.settings = QSettings("Nyre", "DolphinQuickView")
        # a way to access and check if the widget has been created
        self.added_viewers = []
        self.image_viewer = None
        self.document_viewer = None
        self.fallback_viewer = None
        self.video_viewer = None
        self.text_viewer = None
        self.container_viewer = None
        # used to manage the index indicator in the title bar.
        self.is_parent_in_list = False
        # sets the files and folders to display.
        self.set_directory()
        # setting up ui
        self.setWindowIcon(self.style().standardIcon(
            QStyle.StandardPixmap.SP_FileDialogContentsView))
        #gets the screen size.
        screen_size = app.primaryScreen().size()
        #Reads window size settings and sets the default window size based on the screen resolution.
        self.resize(self.settings.value("size", defaultValue=QSize(int(screen_size.width() * 0.5), int(screen_size.height() * 0.55))))
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

        # viewer_container and layout
        self.viewer_container = QWidget()
        self.viewer_container_layout = QVBoxLayout(self.viewer_container)
        self.viewer_container_layout.setContentsMargins(0, 0, 0, 0)

        # back button
        self.back_button = QPushButton()
        self.back_button.setFixedHeight(24)
        self.back_button.setMinimumWidth(80)
        self.back_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowLeft))

        # forward button
        self.forward_button = QPushButton()
        self.forward_button.setFixedHeight(24)
        self.forward_button.setMinimumWidth(80)
        self.forward_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_ArrowRight))

        # open button
        self.open_button = QPushButton()
        self.open_button.setFixedHeight(24)
        self.open_button.setMinimumWidth(80)
        self.open_button.setSizePolicy(QSizePolicy(
            QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed))
        self.open_button.setIcon(
            self.style().standardIcon(QStyle.StandardPixmap.SP_DialogOpenButton))

        # button signal
        self.back_button.pressed.connect(self.back)
        self.forward_button.pressed.connect(self.forward)
        self.open_button.pressed.connect(self.open_with_app)

        # adding to layouts
        controls_layout.addWidget(self.back_button)
        controls_layout.addWidget(self.open_button)
        controls_layout.addWidget(self.forward_button)
        self.main_layout.addWidget(self.viewer_container)
        self.main_layout.addLayout(controls_layout)

    def load_file_at_index(self, index):
        # hides the viewer shown previously.
        self.hide_widgets()

        # resets some variables
        is_folder = False
        extension = None

        # retrieves the path of the current file
        self.current_file = self.files[index]
        # set the window title
        file_name = self.current_file.split("/")[-1]
        if not self.is_parent_in_list:
            self.setWindowTitle(f"[{index+1}/{len(self.files)}]  {file_name}")
        else:
            self.setWindowTitle(f"[{index}/{len(self.files)-1}]  {file_name}")

        # avoid extracting the extension if it is a folder.
        if os.path.isdir(self.current_file):
            # used to determine whether the container viewer should be used.
            is_folder = True
        elif os.path.splitext(self.current_file.lower())[-1]:
            extension = os.path.splitext(self.current_file.lower())[-1]

        # load viewer based on extension or file type
        if is_folder or extension in [".zip", ".gz", ".xz", ".rar"]:
            self.load_container_viewer(self.current_file)

        elif extension in [".png", ".jpeg", ".jpg", ".webp",".svg", ".svgz",".kra"]:
            self.load_image_viewer(self.current_file, extension)

        elif extension in [".pdf", ".doc", ".docx", ".odt", ".ods", ".xlsx", ".xls", ".csv", ".odp", ".ppt", ".pptx"]:
            self.load_document_viewer(self.current_file, extension)
        
        elif extension in [".mp4", ".mp3"]:
            self.load_video_viewer(self.current_file)

        elif extension in [".md"]:
            with open(self.current_file, "r") as f:
                self.load_text_viewer(f.read(), markdown=True)

        # for simple text (.sh,.txt,.xml,.html,etc) which may or may not have an extension.
        elif "text/" in subprocess.run(["file", "--mime-type", self.current_file],
                                       stdout=subprocess.PIPE).stdout.decode("utf-8"):
            with open(self.current_file, "r") as f:
                self.load_text_viewer(f.read())

        else:
            self.load_fallback_viewer(path=self.current_file)

    def load_container_viewer(self, path):
        if self.container_viewer is None:
            self.container_viewer = ContainerViewer(self)
            # adds the widget to its container.
            self.add_widget(self.container_viewer)

        self.container_viewer.show()
        self.container_viewer.load_file(path)

    def load_text_viewer(self, text, markdown=False):
        if self.text_viewer is None:
            self.text_viewer = TextViewer(self)
            # adds the widget to its container.
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
        self.text_viewer.setFocus()

    def load_video_viewer(self, path):
        if self.video_viewer is None:
            self.video_viewer = VideoViewer(self)
            # adds the widget to its container.
            self.add_widget(self.video_viewer)

        self.video_viewer.open(path)
        self.video_viewer.show()
      
    def load_document_viewer(self, path, extension):
        if self.document_viewer is None:
            # self.app is used to connect the signal "aboutToQuit"
            self.document_viewer = DocumentViewer(self, self.app)
            # adds the widget to its container.
            self.add_widget(self.document_viewer)

        self.document_viewer.load_file(path, extension)
        self.document_viewer.show()

    def load_image_viewer(self, path, extension):
        if self.image_viewer is None:
            # adds the widget to its container.
            self.image_viewer = ImageViewer(self, self.app)
            self.add_widget(self.image_viewer)

        self.image_viewer.load_file(path, extension)
        self.image_viewer.show()

    def load_fallback_viewer(self, path):
        if self.fallback_viewer is None:
            self.fallback_viewer = FallbackViewer(self)
            # adds the widget to its container.
            self.add_widget(self.fallback_viewer)

        self.fallback_viewer.load_file(path)
        self.fallback_viewer.show()

    def set_directory(self):
        # gets the directory from the system arguments.

        args_count = len(sys.argv)
        if args_count < 2:
            print("No path or file given")
            exit()
        if not os.path.exists(sys.argv[1]):
            print("Invalid path:", sys.argv[1])
            exit()

        argv_path = os.path.abspath(sys.argv[1])

        # if something (folder or file) was selected: "-s"
        if args_count > 2 and sys.argv[-1] == "-s":
            # is a file or folder was selected
            # current file is selected file
            self.current_file = argv_path
            # current path is the parent folder
            self.current_path = os.path.dirname(self.current_file)
            # search for files in the folder
            self.files = glob(f"{self.current_path}/*")
            self.files = self.sort_files(self.files)
            # set the index at the current file
            self.current_index = self.files.index(self.current_file)
        else:
            # if the shortcut was used and no file was selected.
            # current file is the parent folder
            self.current_file = argv_path
            # current path is the parent folder
            self.current_path = argv_path
            # search for files in the folder
            self.files = glob(f"{self.current_path}/*")
            self.files = self.sort_files(self.files)
            # add the parent directory to the files list
            # this is done so as not to break the back and forward function
            self.files.insert(0, self.current_file)
            # used to manage the index indicator in the title bar.
            self.is_parent_in_list = True
            # set the index at the current fie
            self.current_index = self.files.index(self.current_file)

    def add_widget(self, widget):
        # It is used to add new viewers to the default container.
        self.viewer_container_layout.addWidget(widget)
        # Adds the viewer to the list of added ones.
        # This is done to use hide() on all of them.
        self.added_viewers.append(widget)

    def open_with_app(self):
            subprocess.run(["xdg-open", f"{self.current_file}"])
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
        for w in self.added_viewers:
            w.hide()

    def sort_files(self, content_list):
        ordered_files = []
        # sorting: alphabetical order and folders first.
        folders_in_list = [x for x in content_list if os.path.isdir(x)]
        files_in_list = [x for x in content_list if os.path.isfile(x)]

        folders_in_list = sorted(folders_in_list, key=str.lower)
        files_in_list = sorted(files_in_list, key=str.lower)

        ordered_files.extend(folders_in_list)
        ordered_files.extend(files_in_list)
        return ordered_files

    def set_shortcut(self):
        for shortcut_close in ["q", Qt.Key.Key_Escape, Qt.Key.Key_Space]:
            QShortcut(shortcut_close, self).activated.connect(self.app.quit)

        for shortcut_back in ["a", Qt.Key.Key_Left]:
            QShortcut(shortcut_back, self).activated.connect(self.back)

        for shortcut_forward in ["d", Qt.Key.Key_Right]:
            QShortcut(shortcut_forward, self).activated.connect(self.forward)

        for shortcut_open in ["w", Qt.Key.Key_Return]:
            QShortcut(shortcut_open, self).activated.connect(
                self.open_with_app)
            
    def closeEvent(self, event: QCloseEvent) -> None:
        #save the window size in the settings.
        self.settings.setValue("size", self.size())
        return super().closeEvent(event)
    

def launch():
    app = QApplication(sys.argv)
    window = Main(app)
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    launch()
