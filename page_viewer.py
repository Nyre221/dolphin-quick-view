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


class PageViewer(QWidget):
    # used to trigger a function in the main thread from the secondary thread.
    # Qt does not allow calling some widget functions from a secondary thread.
    signLoadingArrested = pyqtSignal(bool, bool, bool, str)
    signConversionFinished = pyqtSignal(str)

    def __init__(self, parent=None):
        super(PageViewer, self).__init__(parent)
        self.temp_dir = None
        self.conversion_process = None
        self.is_active_viewer = False
        self.libreoffice_command = self.__get_libreoffice_command__()
        # the page to see if they have problems with libreoffice.
        self.libreoffice_help_page = "https://github.com/Nyre221/dolphin-quick-view/tree/main/extras/Libreoffice%20troubleshooting"
        # to get translations
        self.translator = Translator()
        # name font
        self.font_label_message_name = QFont()
        self.font_label_message_name.setPointSize(14)
        self.font_label_message_name.setBold(True)
        # header font
        self.font_label_message_header = QFont()
        self.font_label_message_header.setPointSize(11)
        self.font_label_message_header.setBold(True)
        # message font
        self.font_label_message = QFont()
        self.font_label_message.setPointSize(10)

        # qpageview
        self.qpage = qpageview.View()
        # set scroll speed
        self.qpage.verticalScrollBar().setSingleStep(50)

        # img
        self.logo_img = QLabel()
        self.logo_img.setAlignment(Qt.AlignCenter)
        # sets the image size based on the screen size
        self.logo_size = QApplication.primaryScreen().size()*0.135
        self.logo_img.setPixmap(QPixmap("/usr/share/icons/breeze-dark/mimetypes/64/x-office-document.svg").scaled(
            self.logo_size, Qt.KeepAspectRatioByExpanding, Qt.FastTransformation))

        # labels
        self.label_message_name = QLabel()
        self.label_message_name.setAlignment(Qt.AlignCenter)
        self.label_message_name.setFont(self.font_label_message_name)
        self.label_message_header = QLabel()
        self.label_message_header.setFont(self.font_label_message_header)
        self.label_message_header.setAlignment(Qt.AlignCenter)
        self.label_message = QLabel()
        self.label_message.setFont(self.font_label_message)
        self.label_message.setAlignment(Qt.AlignCenter)
        # allows to open external links.
        self.label_message.setWordWrap(True)
        self.label_message.setTextFormat(Qt.RichText)
        self.label_message.setTextInteractionFlags(Qt.TextBrowserInteraction)
        self.label_message.setOpenExternalLinks(True)
        # layouts
        # main
        self.layout_main = QVBoxLayout()
        self.setLayout(self.layout_main)
        # message layout
        self.layout_message = QVBoxLayout()

        # labels container
        self.container_message = QWidget()
        self.container_message.setLayout(self.layout_message)

        # adding to layout
        self.layout_main.addWidget(self.container_message)
        self.layout_main.addWidget(self.qpage)
        self.layout_message.addWidget(self.logo_img)
        self.layout_message.addWidget(self.label_message_name)
        self.layout_message.addWidget(self.label_message_header)
        self.layout_message.addWidget(self.label_message)
        self.layout_message.insertStretch(-1)

        # connecting signals
        # used to trigger a function in the main thread from the secondary thread.
        self.signLoadingArrested.connect(self.__loading_arrested__)
        self.signConversionFinished.connect(self.__conversion_finished__)
        # placeholder
        self.__set_placeholder_text__()

    def load_file(self, path, extension):
        # loading message
        self.container_message.show()
        self.__set_placeholder_text__()
        self.label_message_name.setText(path.split("/")[-1])
        # set the focus so you can scroll through the pages with the arrow keys.
        self.qpage.setFocus()
        # gives space to the loading screen.
        self.qpage.hide()
        # removes the previously viewed document.
        self.qpage.clear()
        # It is used to kill the process if the viewer has been hidden.
        self.is_active_viewer = True


        # load and set the display mode based on the file.
        if extension == ".pdf":
            self.qpage.loadPdf(path)
            self.qpage.setViewMode(qpageview.FitWidth)
            self.__file_loaded__()
        elif extension in [".png", ".jpeg", ".jpg", ".webp"]:
            self.qpage.loadImages([path])
            self.qpage.setViewMode(qpageview.FitBoth)
            self.__file_loaded__()
        elif extension in [".svg"]:
            self.qpage.loadSvgs([path])
            self.qpage.setViewMode(qpageview.FitBoth)
            self.__file_loaded__()
        elif extension in [".doc", ".docx", ".odt", ".ods", ".xlsx", ".xls", ".csv", ".odp"]:
            # converts to pdf.
            self.__convert_document__(path=path)

    def __file_loaded__(self):
        # hides the messages/loading screen and shows qpage.
        self.container_message.hide()
        self.qpage.show()

    def hide(self) -> None:
        # clears qpageview screen to save memory(doesn't seem to work).
        self.qpage.clear()
        self.is_active_viewer = False
        return super().hide()

    def __convert_document__(self, path):
        # shows a message and stops the function if libreoffice was not found.
        if self.libreoffice_command is None:
            self.__loading_arrested__(loffice_not_found=True)
            print("libreoffice not found")
            return

        # create a temporary folder to put the pdfs in.
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp()

        # use another thread to avoid blocking the interface.
        th = Thread(target=self.__convert_document_thread__,
                    args=(path, self.temp_dir))
        th.setDaemon(True)
        th.start()

    def __convert_document_thread__(self, path, temp_dir):
        if self.conversion_process is not None and self.conversion_process.poll() is None:
            # kills the process group if the old process is still running.
            os.killpg(self.conversion_process.pid, signal.SIGTERM)

        # libreoffice shell command
        commands = f"{self.libreoffice_command} --headless --nolockcheck --norestore --convert-to pdf '{path}' --outdir {temp_dir} "
        args = shlex.split(commands)
        # preexec_fn=os.setsid is used to create a process group.
        # this is necessary to terminate libreoffice and reopen it later.
        self.conversion_process = subprocess.Popen(
            args=args, preexec_fn=os.setsid, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # the global variable is used to kill the old process when a new thread starts,
        #  the local one is used to get the return code and information without risking taking those of the new process.
        local_process = self.conversion_process
        # to kill the process after X sec
        # I don't want to make the user wait forever if the file takes too long to load.
        start = time.time()
        end = start + 10
        # checks if the maximum time limit is reached.
        while True:
            if local_process.poll() is not None:
                # exits the loop if the process has finished.
                break

            if time.time() >= end:
                # kill the process
                os.killpg(local_process.pid, signal.SIGTERM)
                # display the message
                self.signLoadingArrested.emit(True, False, False, "")
                # exit
                break

            time.sleep(0.1)

        # store the return code
        return_code = local_process.returncode
        # send the path of the pdf if the return code is 0 and the viewer is active
        if return_code == 0 and self.is_active_viewer:
            output = local_process.communicate()[0]
            try:
                # get the path
                pdf_path = output.decode(
                    "utf-8").split(">")[1].split("using filter")[0].strip()

                print(os.path.exists(pdf_path))
                if not os.path.exists(pdf_path):
                    # shows an error if for some reason libreoffice fails to give a path.
                    # True:path error
                    self.signLoadingArrested.emit(False, False, True, "")
                    return

                # send
                self.signConversionFinished.emit(pdf_path)
            except IndexError:
                print("IndexError")
                process_error = local_process.communicate()[1]
                # shows an error if for some reason libreoffice fails to give a path.
                self.signLoadingArrested.emit(
                    False, False, False, process_error.decode("utf-8"))
                return

    def __conversion_finished__(self, path: str):
        # calls the function with the path of the new pdf
        self.load_file(path=path, extension=".pdf")
        self.qpage.setFocus()

    def __get_libreoffice_command__(self):
        # check if libreoffice is installed.
        if shutil.which('libreoffice'):
            command = "libreoffice"
        elif shutil.which('flatpak'):
            # check if libreoffice is installed with flatpak
            if subprocess.run(["bash", "-c", "flatpak list | grep -i libreoffice"]).returncode == 0:
                command = "flatpak run org.libreoffice.LibreOffice"
        else:
            command = None

        # return the command to use
        return command

    def __loading_arrested__(self, timeout=False, loffice_not_found=False, path_error=False, custom_message=""):
        # sets the information in the labels.
        self.label_message_header.setText(
            self.translator.get_translation("libreoffice_preview_unavailable"))
        html = f"<a href=\"{self.libreoffice_help_page}\">{self.translator.get_translation('click_here')}</a>"
        if timeout:
            self.label_message.setText(
                self.translator.get_translation("libreoffice_timeout"))
        elif loffice_not_found:
            self.label_message.setText(self.translator.get_translation(
                "libreoffice_not_found")+" "+html)
        elif path_error:
            self.label_message.setText(self.translator.get_translation(
                "libreoffice_file_not_found")+" "+html)
        if custom_message != "":

            self.label_message.setText(custom_message + " : " + html)

    def __set_placeholder_text__(self):
        self.label_message_header.setText(
            self.translator.get_translation("loading_placeholder"))
        # there is no need to translate it because the name is set immediately.
        self.label_message_name.setText("Name")
        self.label_message.setText("")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = PageViewer()
    widget.resize(640, 480)
    widget.show()
    sys.exit(app.exec_())
