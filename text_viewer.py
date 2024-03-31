from PySide6.QtWidgets import QTextBrowser

class TextViewer(QTextBrowser):
    def __init__(self, parent=None):
        super(TextViewer,self).__init__()
        self.verticalScrollBar().setSingleStep(30)

        
