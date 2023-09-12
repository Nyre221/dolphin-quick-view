import pyexcel
from PyQt5.QtWidgets import QTableWidget,QTableWidgetItem

class TableViewer(QTableWidget):
    def __init__(self, parent = None):
        super(TableViewer,self).__init__(parent)
        self.setFocus()

        
    def load_file(self,file_path):
        sheet = pyexcel.get_sheet(file_name=file_path,encoding="windows-1252")
        #here I convert everything to strings otherwise QTableWidget can crash.
        sheet.format(str)

        self.setColumnCount(sheet.number_of_columns())  
        self.setRowCount(sheet.number_of_rows())  
        
        for r in range(sheet.number_of_rows()):
            for c in range(sheet.number_of_columns()):
                self.setItem(r,c, QTableWidgetItem(sheet[r,c]))

