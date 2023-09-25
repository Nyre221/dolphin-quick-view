import os
import sys
import pyexcel
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QApplication
import xlrd
from random import randint
from threading import Thread

# from pyexcel import xlsx


class TableViewer(QTableWidget):

    def __init__(self, parent=None):
        super(TableViewer, self).__init__(parent)

        # used to discard a thread if the user changes documents
        self.current_thread_id = 0

        self.is_active_viewer = False

        # makes the table read only.
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        # for some reason when I create the quick view executable with zipapp,
        # pyexcel gives an error when I try to open an xlsx:
        # /quick_view/quick_view.pyz/xlrd/xlsx.py", line 266, in process_stream
        # AttributeError: 'ElementTree' object has no attribute 'getiterator'
        # this seems to have to do with some deprecated function that for some
        # reason gets triggered when I add pyexcel into the executable
        # (the module versions are the same as the system ones)
        # this solves the problem for now:
        # (version 1.2.0 is included in the executable)
        if xlrd.__version__ == "1.2.0":
            xlrd.xlsx.ensure_elementtree_imported(False, None)
            xlrd.xlsx.Element_has_iter = True

    def load_file(self, file_path):
        self.__load_placeholder__()
        self.is_active_viewer = True

        # choose an id for the thread.
        # in this way is possible to close the thread if it is no longer needed.
        random_id = randint(0, 1000)
        while random_id == self.current_thread_id:
            random_id = randint(0, 1000)

        self.current_thread_id = random_id

        # prepare the thread
        self.th = Thread(target=self.__load_sheet__, args=([file_path]))
        # #allows to close the application if there is a thread still running.
        self.th.setDaemon(True)
        self.th.start()

    def __load_placeholder__(self):
        # set placeholder text
        self.clear()
        self.setColumnCount(1)
        self.setRowCount(1)
        self.setItem(0, 0, QTableWidgetItem("Loading"))

    def __load_sheet__(self, path):
        # to check if the id has changed.
        thread_id = self.current_thread_id

        if os.path.splitext(path.lower())[-1] == ".csv":
            # for csv files read_only is an invalid parameter.
            sheet = pyexcel.get_sheet(
                file_name=path, encoding="windows-1252", row_limit=50)
        else:
            sheet = pyexcel.get_sheet(
                file_name=path, encoding="windows-1252", read_only=True, row_limit=50)

        if thread_id is not self.current_thread_id or not self.is_active_viewer:
            sys.exit()

        self.__set_table__(sheet)
        sys.exit()

    def __set_table__(self, sheet):

        # convert everything to strings otherwise QTableWidget can crash.
        sheet.format(str)

        self.setColumnCount(sheet.number_of_columns())
        self.setRowCount(sheet.number_of_rows())

        # sets the items in the table.
        for r in range(sheet.number_of_rows()):
            for c in range(sheet.number_of_columns()):
                self.setItem(r, c, QTableWidgetItem(sheet[r, c]))

    def hide(self) -> None:
        # clears the table.
        self.__load_placeholder__()
        pyexcel.free_resources()
        self.is_active_viewer = False
        return super().hide()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    widget = TableViewer()
    widget.resize(640, 480)
    widget.show()
    sys.exit(app.exec_())
