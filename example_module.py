from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
import sys

# Adhere to naming conventions: https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html

# Call the module like this: name_viewer.py (all lowercase)
# I chose this way of naming the modules to avoid using a name already in use.

class ClassExample(QWidget):

    def __init__(self, parent=None):
        super(ClassExample, self).__init__(parent)

        # buttons
        self.button_1 = QPushButton()
        self.button_1.setText("Button 1")
        self.button_2 = QPushButton()
        self.button_2.setText("Button 2")

        # label
        self.example_label = QLabel()
        self.example_label.setText("Label Text")

        # main layout
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.example_label)
        self.main_layout.addWidget(self.button_1)
        self.main_layout.addWidget(self.button_2)
        self.setLayout(self.main_layout)



# load_file() is the class method that will be called by quick_view.py
# Use this method to receive the path of the file to show.
    def load_file(self,file_path):
        pass





if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = ClassExample()
    widget.resize(640, 480)
    widget.show()
    sys.exit(app.exec_())