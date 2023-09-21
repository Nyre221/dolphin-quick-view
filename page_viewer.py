import qpageview

class PageViewer(qpageview.View):
    def __init__(self, parent=None):
        super(PageViewer,self).__init__(parent)
        self.verticalScrollBar().setSingleStep(50)


        
    def pdf_mode(self):
        self.setViewMode(qpageview.FitWidth)


    def img_mode(self):
        self.setViewMode(qpageview.FitBoth)

    def hide(self) -> None:
        self.clear()
        return super().hide()