#!/bin/python3

# import QT
from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QStyle, \
    QSizePolicy, QLabel, QShortcut
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtCore import Qt, QEvent
# import viewers
from page_viewer import PageViewer
from text_viewer import TextViewer
from table_viewer import TableViewer
from video_viewer import VideoViewer
from container_viewer import ContainerViewer
# other
from glob import glob
import textract
import subprocess
import sys
import os
import shutil


class Main(QMainWindow):

    def __init__(self, app):
        super().__init__()
        self.app = app
        # gets the active dolphin window before quick view becomes the active window.
        self.dolphin_window = self.get_dolphin_window()
        # a way to access and check if the widget has been created
        self.added_viewers = []
        self.page_viewer = None
        self.video_viewer = None
        self.text_viewer = None
        self.table_viewer = None
        self.container_viewer = None

        # sets the files and folders to display.
        self.set_directory()

        # setting up ui
        self.setWindowIcon(self.style().standardIcon(
            QStyle.SP_FileDialogContentsView))
        screen_size = app.primaryScreen().size()
        self.resize(int(screen_size.width() * 0.5),
                    int(screen_size.height() * 0.55))
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
        self.added_viewers.append(self.error_label)
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
        self.back_button.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowLeft))

        # forward button
        self.forward_button = QPushButton()
        self.forward_button.setFixedHeight(24)
        self.forward_button.setMinimumWidth(80)
        self.forward_button.setIcon(
            self.style().standardIcon(QStyle.SP_ArrowRight))

        # open button
        self.open_button = QPushButton()
        self.open_button.setFixedHeight(24)
        self.open_button.setMinimumWidth(80)
        self.open_button.setSizePolicy(QSizePolicy(
            QSizePolicy.Maximum, QSizePolicy.Fixed))
        self.open_button.setIcon(
            self.style().standardIcon(QStyle.SP_DialogOpenButton))

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
        # hides the viewer shown previously.
        self.hide_widgets()

        # resets some variables
        is_folder = False
        extension = None

        # retrieves the path of the current file
        self.current_file = self.files[index]
        # set the window title
        self.setWindowTitle(self.current_file.split("/")[-1])

        # avoid extracting the extension if it is a folder.
        if os.path.isdir(self.current_file):
            # used to determine whether the container viewer should be used.
            is_folder = True
        elif os.path.splitext(self.current_file.lower())[-1]:
            extension = os.path.splitext(self.current_file.lower())[-1]

        # load viewer based on extension or file type
        if is_folder or extension in [".zip", ".gz", ".xz",".rar"]:
            self.load_container_viewer(self.current_file)
        elif extension in [".pdf"]:
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

        elif extension in [".md"]:
            with open(self.current_file, "r") as f:
                self.load_text_viewer(f.read(), markdown=True)

        elif extension in [".ods", ".xlsx", ".xls", ".csv"]:
            self.load_table_viewer(self.current_file)

        # for simple text (.sh,.txt,.xml,.html,etc) which may or may not have an extension.
        elif "text/" in subprocess.run(["file", "--mime-type", self.current_file],
                                       stdout=subprocess.PIPE).stdout.decode("utf-8"):
            with open(self.current_file, "r") as f:
                self.load_text_viewer(f.read())

        else:
            self.error_label.setText(os.path.basename(self.current_file))
            self.error_label.show()

    def load_container_viewer(self, path):
        if self.container_viewer is None:
            self.container_viewer = ContainerViewer(self)
            # adds the widget to its container.
            self.add_widget(self.container_viewer)

        self.container_viewer.load_file(path)
        self.container_viewer.show()

    def load_table_viewer(self, path):
        if self.table_viewer is None:
            self.table_viewer = TableViewer(self)
            # adds the widget to its container.
            self.add_widget(self.table_viewer)

        self.table_viewer.load_file(path)
        self.table_viewer.show()
        self.table_viewer.setFocus()

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

    def load_page_viewer(self, path, _type):
        if self.page_viewer is None:
            self.page_viewer = PageViewer(self)
            # adds the widget to its container.
            self.add_widget(self.page_viewer)

        # based on the extension use the right function and set the display mode.
        if _type == "pdf":
            self.page_viewer.loadPdf(path)
            self.page_viewer.pdf_mode()
        elif _type == "img":
            self.page_viewer.loadImages([path])
            self.page_viewer.img_mode()
        elif _type == "svg":
            self.page_viewer.loadSvgs([path])
            self.page_viewer.img_mode()

        self.page_viewer.show()
        self.page_viewer.setFocus()

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

        elif args_count > 2 and sys.argv[-1] == "-a":
            # activated by the dophin action in the dropdown menu
            # this is necessary because the actions in the dolphin menu have no way of knowing
            # whether the selected one is the parent folder or a subfolder.
            if os.path.isfile(argv_path):
                # if a file was selected
                # current file is selected file
                self.current_file = argv_path
                # current path is the parent folder
                self.current_path = os.path.dirname(self.current_file)
                # search for files
                self.files = glob(f"{self.current_path}/*")
                self.files = self.sort_files(self.files)
                # set the index at the current file
                self.current_index = self.files.index(self.current_file)
            elif os.path.isdir(argv_path):
                # if a folder was selected
                # current path is the selected folder
                self.current_path = argv_path
                # search for files in the selected folder
                self.files = glob(f"{self.current_path}/*")
                self.files = self.sort_files(self.files)
                # choose a random file or folder.
                self.current_file = self.files[0]
                self.current_index = 0
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
            self.files.insert(0,self.current_file)
            # set the index at the current fie
            self.current_index = self.files.index(self.current_file)

    def add_widget(self, widget):
        # It is used to add new viewers to the default container.
        self.viewer_container_layout.addWidget(widget)
        # Adds the viewer to the list of added ones.
        # This is done to use hide() on all of them.
        self.added_viewers.append(widget)

    def open_with_app(self):
        # opens the folder in the active dolphin window
        if os.path.isdir(self.current_file):
            if self.dolphin_window is None:
                print("dolphin window not found")
                return
            else:
                args_1 = f'dbus-send --session --print-reply --type=method_call --dest={self.dolphin_window} /dolphin/Dolphin_1'
                args_2 = f'org.kde.dolphin.MainWindow.openDirectories array:string:"file://{self.current_file}" boolean:false'
                subprocess.run(["bash", "-c", args_1+" "+args_2],
                               stdout=subprocess.PIPE)
                exit()

        else:  # for any other file
            subprocess.run(["xdg-open", self.current_file])
            exit()

    def get_dolphin_window(self):
        # It is used to get the dolphin dbus address.
        dolphin_window = None
        #the qdbus command can change name depending on the distro
        qdbus_command = 'qdbus-qt5' if shutil.which('qdbus-qt5') else 'qdbus'
        # get dolphin windows
        windows = subprocess.run(
            ["bash", "-c", f"{qdbus_command} | grep -i dolphin"], stdout=subprocess.PIPE)
        # convert string to list
        windows = windows.stdout.decode("utf-8").split()

        # controls which dolphin window is active
        for w in windows:
            is_active_window = subprocess.run(
                ["bash", "-c", f"dbus-send --session --print-reply --type=method_call --dest={w} /dolphin/Dolphin_1 org.qtproject.Qt.QWidget.isActiveWindow"], stdout=subprocess.PIPE)
            if "true" in is_active_window.stdout.decode("utf-8").split():
                dolphin_window = w

        # return the active window
        return dolphin_window

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

    def sort_files(self,content_list):
        ordered_files = []
        # sorting: alphabetical order and folders first.
        folders_in_list = [x for x in content_list if os.path.isdir(x)]
        files_in_list =  [x for x in content_list if os.path.isfile(x)]

        folders_in_list = sorted(folders_in_list,key=str.lower)
        files_in_list = sorted(files_in_list,key=str.lower)

        ordered_files.extend(folders_in_list)
        ordered_files.extend(files_in_list)
        return ordered_files


    def set_shortcut(self):
        for shortcut_close in ["q", Qt.Key_Escape, Qt.Key_Space]:
            QShortcut(shortcut_close, self).activated.connect(self.app.quit)

        for shortcut_back in ["a", Qt.Key_Left]:
            QShortcut(shortcut_back, self).activated.connect(self.back)

        for shortcut_forward in ["d", Qt.Key_Right]:
            QShortcut(shortcut_forward, self).activated.connect(self.forward)

        for shortcut_open in ["w", Qt.Key_Return]:
            QShortcut(shortcut_open, self).activated.connect(
                self.open_with_app)




def launch():
    app = QApplication(sys.argv)
    window = Main(app)
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    launch()
