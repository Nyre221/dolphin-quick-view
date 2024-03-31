from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel,QScrollArea
from PySide6.QtGui import QPixmap, QFont, QResizeEvent
from PySide6.QtCore import Qt
from translation_manager import Translator
import sys
import tempfile
import zipfile


class ImageViewer(QWidget):

    def __init__(self, parent=None, app=None):
        super(ImageViewer, self).__init__(parent)
        self.temp_dir = None
        #used to resize the image when resizing the window
        self.curent_image_path = ""
        self.translator = Translator()

        # name font
        self.font_label_message_name = QFont()
        self.font_label_message_name.setPointSize(14)
        self.font_label_message_name.setBold(True)
        # header font
        self.font_label_message_header = QFont()
        self.font_label_message_header.setPointSize(11)
        self.font_label_message_header.setBold(True)

        #image 
        self.image = QLabel(self)
        self.image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        #scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.image)
        self.scroll_area.setWidgetResizable(True)

        # loading img
        self.logo_img = QLabel()
        self.logo_img.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # sets the image size based on the screen size
        self.logo_size = QApplication.primaryScreen().size()*0.135
        self.logo_img.setPixmap(QPixmap("/usr/share/icons/breeze/mimetypes/64/image-x-generic.svg").scaled(
            self.logo_size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.FastTransformation))

        # labels
        self.label_message_name = QLabel()
        self.label_message_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_message_name.setFont(self.font_label_message_name)
        self.label_message_header = QLabel()
        self.label_message_header.setFont(self.font_label_message_header)
        self.label_message_header.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # layouts
        # main
        self.layout_main = QVBoxLayout()
        self.layout_main.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout_main)
        # message layout
        self.layout_message = QVBoxLayout()

        # labels container
        self.container_message = QWidget()
        self.container_message.setLayout(self.layout_message)

        # adding to layout
        self.layout_main.addWidget(self.container_message)
        self.layout_main.addWidget(self.scroll_area)
        # self.layout_main.addWidget(self.image)
        self.layout_message.addWidget(self.logo_img)
        self.layout_message.addWidget(self.label_message_name)
        self.layout_message.addWidget(self.label_message_header)

        self.layout_message.insertStretch(-1)

        # placeholder
        self.__set_placeholder_text__()

    def load_file(self, path, extension):
        # loading message
        self.container_message.show()
        self.__set_placeholder_text__()
        self.label_message_name.setText(path.split("/")[-1])
        # clears the previous image.
        self.image.setPixmap(QPixmap(""))

        
        if extension in [".png", ".jpeg", ".jpg", ".webp",".svg",".svgz"]:
            # sets and scales the image
            self.curent_image_path = path
            #the width and height are multiplied by 0.X to avoid showing the scroll bars.
            self.image.setPixmap(QPixmap(self.curent_image_path).scaled(int(self.scroll_area.width()*0.995),int(self.scroll_area.height()*0.995),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.FastTransformation))
            self.__file_loaded__()

        elif extension in [".kra"]:
            # extracts the image
            self.__open_kra__(path=path)

    def __file_loaded__(self):
        # hides the messages/loading screen and shows the image.
        self.container_message.hide()
        self.image.show()


    def __open_kra__(self,path):
        # create a temporary folder
        if self.temp_dir is None:
            self.temp_dir = tempfile.mkdtemp()

        # opens tje .kra and extract the preview
        with zipfile.ZipFile(path, 'r') as zip_ref:
            zip_ref.extract("mergedimage.png",self.temp_dir)

        output_dir = self.temp_dir+"/mergedimage.png"
        self.load_file(output_dir,".png")

    def __set_placeholder_text__(self):
        self.label_message_header.setText(
            self.translator.get_translation("loading_placeholder"))
        # there is no need to translate it because the name is set immediately.
        self.label_message_name.setText("Name")

    def resizeEvent(self, event: QResizeEvent) -> None:
        #resizes the image when resizing the window
        #the width and height are multiplied by 0.X to avoid showing the scroll bars.
        self.image.setPixmap(QPixmap(self.curent_image_path).scaled(int(self.scroll_area.width()*0.995),int(self.scroll_area.height()*0.995),Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.FastTransformation))
        return super().resizeEvent(event)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ImageViewer()
    widget.resize(640, 480)
    widget.show()
    sys.exit(app.exec())
