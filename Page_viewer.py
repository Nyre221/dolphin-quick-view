import qpageview

class Viewer(qpageview.View):
    def __init__(self, parent=None):
        super(Viewer,self).__init__(parent)
        self.setFocus()


        
    def pdf_mode(self):
        self.setViewMode(qpageview.FitWidth)


    def img_mode(self):
        self.setViewMode(qpageview.FitBoth)
