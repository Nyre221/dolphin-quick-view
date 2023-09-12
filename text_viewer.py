from PyQt5.QtWidgets import QTextBrowser

class Text_viewer(QTextBrowser):
    def __init__(self, parent=None):
        super(Text_viewer,self).__init__(parent)
        self.setFocus()

        
