from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QListWidget, QHBoxLayout, QVBoxLayout, QListWidgetItem, QFrame
from PySide6.QtGui import QPixmap, QFont, QIcon, QFontMetrics
from PySide6.QtCore import Qt
from datetime import datetime
import sys
import zipfile
import os
from glob import glob
import tarfile
import rarfile
from threading import Thread
from random import randint

from translation_manager import Translator


class ContainerViewer(QWidget):

    def __init__(self, parent=None):
        super(ContainerViewer, self).__init__()
        #5GB. is used to determine whether the archive should be opened and its contents shown.
        self.maximum_archive_size = 5368709120
        #to get translations
        self.translator = Translator()
        # used to determine if threads are still needed.
        self.is_active_viewer = False
        # is used to discard a thread no longer needed.
        self.current_thread_id = 0
        #the size to use for the image.
        self.logo_size = QApplication.primaryScreen().size()*0.125
        # preloads the icons to use in the listwidget.
        self.__preload_icons__()
        # file type logo/img
        self.logo_img = QLabel()

        # set the size of the logo if the class is opened by its own script (for testing).
        if parent is None:
            self.logo_img.setPixmap(QPixmap("/usr/share/icons/breeze-dark/mimetypes/64/application-zip.svg").scaled(self.logo_size, Qt.KeepAspectRatioByExpanding))

        # fonts
        # name font
        self.font_label_name = QFont()
        self.font_label_name.setPointSize(14)
        self.font_label_name.setBold(True)
        # size_text/modified_text,etc
        self.font_info_section = QFont()
        self.font_info_section.setPointSize(11)
        self.font_info_section.setBold(True)
        # size_value/modified_value,etc
        self.font_info_value = QFont()
        self.font_info_value.setPointSize(10)
        self.font_info_value.setUnderline(True)

        # name label
        self.label_name = QLabel()
        self.label_name.setText("Name")
        self.label_name.setFont(self.font_label_name)
        self.label_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # needed to elide the text of the name
        self.name_font_metrics = QFontMetrics(self.font_label_name)

        # modified date label (section)
        label_modified_date_text = QLabel()
        label_modified_date_text.setFont(self.font_info_section)
        label_modified_date_text.setText(self.translator.get_translation("last_modified"))
        label_modified_date_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # modified date label (value)
        self.label_modified_date_value = QLabel()
        self.label_modified_date_value.setFont(self.font_info_value)
        self.label_modified_date_value.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # size label (section)
        label_size_text = QLabel()
        label_size_text.setText(self.translator.get_translation("size"))
        label_size_text.setFont(self.font_info_section)
        label_size_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # size label (value)
        self.label_size_value = QLabel()
        self.label_size_value.setFont(self.font_info_value)
        self.label_size_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # files count label (section)
        label_files_count_text = QLabel()
        label_files_count_text.setText(self.translator.get_translation("files"))
        label_files_count_text.setFont(self.font_info_section)
        label_files_count_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # files count label (value)
        self.label_files_count_value = QLabel()
        self.label_files_count_value.setFont(self.font_info_value)
        self.label_files_count_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # separator
        separator_line = QFrame()
        separator_line.setFrameShape(QFrame.Shape.HLine)

        # widgets
        self.list_widget = QListWidget(self)

        # layouts
        self.main_layout = QHBoxLayout()
        layout_info = QVBoxLayout()
        layout_labels_container = QVBoxLayout()

        # setting main layout
        self.setLayout(self.main_layout)

        # adding to layouts:

        layout_labels_container.addWidget(label_files_count_text)
        layout_labels_container.addWidget(self.label_files_count_value)
        layout_labels_container.addWidget(label_size_text)
        layout_labels_container.addWidget(self.label_size_value)
        layout_labels_container.addWidget(label_modified_date_text)
        layout_labels_container.addWidget(self.label_modified_date_value)

        layout_info.addWidget(self.logo_img)
        layout_info.addWidget(self.label_name)
        layout_info.addWidget(separator_line)
        layout_info.addLayout(layout_labels_container)
        layout_info.insertStretch(-1)

        self.main_layout.addLayout(layout_info)
        self.main_layout.addWidget(self.list_widget)
        self.__set_placeholder_text__()

    def load_file(self, path):
        # to stop the thread if it is no longer the active viewer.
        self.is_active_viewer = True
        th = None
        # so the arrow keys can scroll through the items in the list.
        self.list_widget.setFocus()

        # get a random id for thread
        random_id = randint(0, 1000)
        # check that the id is not the same as the previous one.
        while random_id == self.current_thread_id:
            random_id = randint(0, 1000)

        # makes the id global so it can be accessed from anywhere.
        self.current_thread_id = random_id
        # load the placeholder text as it may take time to load the new data.
        self.__set_placeholder_text__()

        
        # use the correct function for the file type.
        extension = os.path.splitext(path.lower())[-1]
        if os.path.isdir(path):
            # change the logo image to match the file type.
            self.__set_logo_icon__("/usr/share/icons/breeze/places/96/folder.svg")
            # prepare to start the function in another thread to avoid slowdowns.
            th = Thread(target=self.__load_folder__, args=([path]))
        elif extension in ".zip":
            # change the logo image to match the file type.
            self.__set_logo_icon__(
                "/usr/share/icons/breeze-dark/mimetypes/64/application-zip.svg")
            # prepare to start the function in another thread to avoid slowdowns.
            th = Thread(target=self.__load_zip__, args=([path]))
        elif extension in ".rar":
            # change the logo image to match the file type.
            self.__set_logo_icon__(
                "/usr/share/icons/breeze-dark/mimetypes/64/application-zip.svg")
            # prepare to start the function in another thread to avoid slowdowns.
            th = Thread(target=self.__load_rar__, args=([path]))
        elif extension in [".gz", ".xz"]:
            # change the logo image to match the file type.
            self.__set_logo_icon__(
                "/usr/share/icons/breeze-dark/mimetypes/64/application-zip.svg")
            # prepare to start the function in another thread to avoid slowdowns.
            th = Thread(target=self.__load_tar__, args=([path]))
        else:
            print("container viewer:File not supported")
            return

        

        # allows closing the application even if the thread has not finished
        th.daemon=True
        #start the thread
        th.start()
        # uses another thread to set basic information about the file.
        # This makes things faster.
        th_2 = Thread(target=self.__set_path_info__, args=([path]))
        # allows closing the application even if the thread has not finished
        th_2.daemon=True
        th_2.start()
#

    def __load_folder__(self, path):
        # get the current thread id
        thread_id = self.current_thread_id
        items = []
        files = []
        folders_in_list = []
        files_in_list = []
        ordered_files = []

        # gets a list of the files.
        files = glob(f"{path}/*")
        
        # sorting: alphabetical order and folders first.
        folders_in_list = [x for x in files if os.path.isdir(x)]
        files_in_list =  [x for x in files if os.path.isfile(x)]

        folders_in_list = sorted(folders_in_list,key=str.lower)
        files_in_list = sorted(files_in_list,key=str.lower)

        ordered_files.extend(folders_in_list)
        ordered_files.extend(files_in_list)

        # create the object for qlistwidget.
        for file in ordered_files:
            if not self.__continue_thread_execution__(thread_id):
               # not needed, exit
                exit()
            # gets the icon appropriate for the file type.
            icon = self.__list_icon_chooser__(file, is_folder=os.path.isdir(file))
            # creates the object for qlistwidget and appends it to the list.
            items.append(QListWidgetItem(icon, os.path.basename(file)))

        # sets the file count in the label.
        self.__set_labels_text__(file_count=len(files))
        # adds items to qlistwidget.
        self.__set_list_widget_items__(items)

    def __load_zip__(self, path):
        # get the current thread id
        thread_id = self.current_thread_id
        items = []
        files_list = []

        # avoid opening the archive if it is too large.
        if os.stat(path).st_size > self.maximum_archive_size:
            # adds an item to let the user know that the content will not be shown.
            self.__show_warning_file_too_big__()
            exit()
        # check if the thread is still needed.
        if not self.__continue_thread_execution__(thread_id):
                    #not needed,exit
                    exit()
        with zipfile.ZipFile(path, "r") as zip_ref:
            zip_infolist = zip_ref.infolist()
        # gets a list of the files and create the object for qlistwidget.
        for file in  zip_infolist:
            if not self.__continue_thread_execution__(thread_id):
                # not needed, exit
                exit()
            if not file.is_dir():
                # gets the icon appropriate for the file type.
                icon = self.__list_icon_chooser__(file.filename, is_folder=False)
                # creates the object for qlistwidget and appends it to the list.
                items.append(QListWidgetItem(icon, file.filename))
                # used later to count the number of files.
                files_list.append(file.filename)
        # sets the file count in the label.
        self.__set_labels_text__(file_count=len(files_list))
        # adds items to qlistwidget.
        self.__set_list_widget_items__(items)

    def __load_rar__(self, path):
        # get the current thread id
        thread_id = self.current_thread_id
        items = []
        files_list = []

        # avoid opening the archive if it is too large.
        if os.stat(path).st_size > self.maximum_archive_size:
            # adds an item to let the user know that the content will not be shown.
            self.__show_warning_file_too_big__()
            exit()
        # check if the thread is still needed.
        if not self.__continue_thread_execution__(thread_id):
                    #not needed,exit
                    exit()

        with rarfile.RarFile(path, "r") as rar_ref:
            rar_infolist = rar_ref.infolist()
        # gets a list of the files and create the object for qlistwidget.
        for file in rar_infolist:
            if not self.__continue_thread_execution__(thread_id):
                # not needed, exit
                exit()
            if not file.is_dir():
                # gets the icon appropriate for the file type.
                icon = self.__list_icon_chooser__(file.filename, is_folder=False)
                # creates the object for qlistwidget and appends it to the list.
                items.append(QListWidgetItem(icon, file.filename))
                # used later to count the number of files.
                files_list.append(file.filename)
        # sets the file count in the label.
        self.__set_labels_text__(file_count=len(files_list))
        # adds items to qlistwidget.
        self.__set_list_widget_items__(items)

    def __load_tar__(self, path):
        # get the current thread id
        thread_id = self.current_thread_id
        items = []
        files_list = []

        # avoid opening the archive if it is too large.
        if os.stat(path).st_size > self.maximum_archive_size:
            # adds an item to let the user know that the content will not be shown.
            self.__show_warning_file_too_big__()
            exit()
        # check if the thread is still needed.
        if not self.__continue_thread_execution__(thread_id):
                    #not needed,exit
                    exit()

        with tarfile.open(path,"r") as tar_ref:
            tar_infolist = tar_ref.getmembers()
        # gets a list of the files and create the object for qlistwidget.
        for file in tar_infolist:
            if not self.__continue_thread_execution__(thread_id):
                # not needed, exit
                exit()
            if not file.isdir():
                # gets the icon appropriate for the file type.
                icon = self.__list_icon_chooser__(file.name, is_folder=False)
                # creates the object for qlistwidget and appends it to the list.
                items.append(QListWidgetItem(icon, file.name))
                # used later to count the number of files.
                files_list.append(file.name)
        # sets the file count in the label.
        self.__set_labels_text__(file_count=len(files_list))
        # adds items to qlistwidget.
        self.__set_list_widget_items__(items)

    def __set_list_widget_items__(self, items):
        self.list_widget.clear()
        for i in items:
            self.list_widget.addItem(i)

    def __preload_icons__(self):
        # these icons are the ones that will be used in qlistwidget.
        # default icon:
        self.unknown_icon = QIcon(
            "/usr/share/icons/breeze-dark/mimetypes/64/unknown.svg")
        # icons
        self.txt_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/text-x-log.svg")
        self.folder_icon = QIcon(
            "/usr/share/icons/breeze/places/16/folder-blue.svg")
        self.archive_icon = QIcon(
            "/usr/share/icons/breeze-dark/mimetypes/16/application-zip.svg")
        self.pdf_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/application-pdf.svg")
        self.img_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/image-png.svg")
        self.video_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/video-mp4.svg")
        self.audio_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/audio-mp3.svg")
        self.shell_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/application-x-shellscript.svg")
        self.python_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/text-x-python.svg")
        self.c_language_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/text-x-c++src.svg")
        self.html_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/text-html.svg")
        self.document_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/application-vnd.oasis.opendocument.text.svg")
        self.iso_image_icon = QIcon(
            "/usr/share/icons/breeze/mimetypes/16/application-x-iso.svg")
        self.krita_image_icon = QIcon(
            "/usr/share/icons/breeze-dark/mimetypes/64/application-x-krita.svg")

    def __list_icon_chooser__(self, path, is_folder=False):
        # returns the icon based on the file type.
        icon = None
        extension = os.path.splitext(path.lower())[-1]

        if is_folder:
            icon = self.folder_icon
        elif extension in [".zip", ".gz", ".rar", ".pyz"]:
            icon = self.archive_icon
        elif extension in [".pdf"]:
            icon = self.pdf_icon
        elif extension in [".png", ".jpg", ".jpeg", ".webp", ".svg", ".svgz"]:
            icon = self.img_icon
        elif extension in [".mp4"]:
            icon = self.video_icon
        elif extension in [".mp3"]:
            icon = self.audio_icon
        elif extension in [".sh"]:
            icon = self.shell_icon
        elif extension in [".py"]:
            icon = self.python_icon
        elif extension in [".ccp",".h"]:
            icon = self.c_language_icon
        elif extension in [".txt"]:
            icon = self.txt_icon
        elif extension in [".html", ".htm"]:
            icon = self.html_icon
        elif extension in [".doc", ".docx", ".odt", ".ods", ".xlsx", ".xls", ".csv"]:
            icon = self.document_icon
        elif extension in [".iso", ".img"]:
            icon = self.iso_image_icon
        elif extension in [".kra"]:
            icon = self.krita_image_icon
        else:
            icon = self.unknown_icon
        return icon

    def __set_logo_icon__(self, path):
        icon = QPixmap(path).scaled(self.logo_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding)
        self.logo_img.setPixmap(icon)

    def __set_labels_text__(self, name=None, last_modified=None, size=None, size_unit="?", file_count=None):
        if name:
            # sets the text and elides it if necessary.
            self.label_name.setText(self.name_font_metrics.elidedText(
                name, Qt.TextElideMode.ElideMiddle,int(self.logo_size.width())))
        if last_modified:
            self.label_modified_date_value.setText(last_modified)
        if size is not None:
            self.label_size_value.setText(f"{size} {size_unit}")
        if file_count is not None:
            self.label_files_count_value.setText(f"{file_count}")

    def __set_path_info__(self, path):
        # set name
        self.__set_labels_text__(name=os.path.basename(path))
        # get and set modification date
        last_modified_date = datetime.fromtimestamp(os.path.getmtime(path))
        last_modified_date = last_modified_date.replace(microsecond=0)
        last_modified_date = str(last_modified_date)
        self.__set_labels_text__(last_modified=last_modified_date)
        # get and set size
        size, unit = self.get_size(path)
        self.__set_labels_text__(size=size, size_unit=unit)

    def get_size(self, path):
        # get the current thread id
        thread_id = self.current_thread_id
        size = 0
        if os.path.isdir(path):
            subfile_path = ""
            try:
                # adds the size of each file to the size variable
                for subfolder_path, dirs, files in os.walk(path):
                    for f in files:
                        if thread_id is not self.current_thread_id or not self.is_active_viewer:
                            # exits if the id has changed (this happens when the user changes files).
                            exit()
                        subfile_path = os.path.join(subfolder_path, f)
                        # .st_size doesn't work on links.
                        if not os.path.islink(subfile_path):
                            size += os.stat(subfile_path).st_size
            except FileNotFoundError:
                print(
                    "get_size(): file not found during size calculation:" + str(subfile_path))

        elif os.path.isfile(path) and not os.path.islink(path):
            # if it is a generic file.
            size = os.stat(path).st_size
        # returns the converted value.
        return self.convert_size(size)

    def convert_size(self, size):
        # convert bytes to KiB
        size = size/1024
        # starting unit
        unit = "KiB"

        if size > 1024:
            # convert KiB to MiB if more than 1024 KiB
            size = size/1024
            unit = "MiB"

        if size > 1024:
            # convert MiB to GiB if more than 1024 MiB
            size = size/1024
            unit = "GiB"

        # round the number
        size = round(size, 1)
        return [size, unit]

    def __set_placeholder_text__(self):
        self.list_widget.clear()
        # ph = placeholder
        ph = self.translator.get_translation("loading_placeholder")
        self.__set_labels_text__(name=ph, last_modified=ph,
                             size=ph, size_unit="", file_count=ph)
        # adds an element to qlistwidget to indicate that the files are loading.
        self.list_widget.addItem(ph)
        


    def hide(self) -> None:
        # to stop the thread if it is no longer the active viewer.
        self.is_active_viewer = False
        return super().hide()

    def __continue_thread_execution__(self,thread_id):
        # check if the thread is still needed.
        if thread_id is self.current_thread_id and self.is_active_viewer:
            #needed, returns true.
            return True
        else:
            return False

    def __show_warning_file_too_big__(self):
        # adds an item to qlistwidget.
        self.__set_list_widget_items__([QListWidgetItem(self.translator.get_translation("container_file_too_big"))])
        # set file count text to "unknown"
        self.__set_labels_text__(file_count=self.translator.get_translation("unknown"))

         
if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ContainerViewer()
    widget.resize(640, 480)
    widget.show()
    sys.exit(app.exec_())
