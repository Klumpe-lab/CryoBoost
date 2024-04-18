# A Dialog box to edit the scheme
import os
import sys
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QPushButton
from PyQt6.QtCore import Qt
import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__name__))
# change the path to be until src
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

#from src.read_write.read_write import jobs_in_scheme
from src.rw.librw import schemeMeta,cbconfig,read_mdoc

class EditScheme(QDialog):
    """
    Dialog window for editing the scheme.
    """
    def __init__(self, table_scheme, parent):
        """
        Setting up the UI.
        """ 
        super().__init__(parent)
        self.cbdat=parent.cbdat        
        loadUi(os.path.abspath(__file__).replace('.py','.ui'), self)
        self.table_scheme = table_scheme

        self.table_scheme_options.setColumnCount(5)
        self.table_scheme_current.setColumnCount(5)
        self.labels_options = ["Add Job", "Job Name", "Fork", "Output if True", "Boolean Variable"]
        self.table_scheme_options.setHorizontalHeaderLabels(self.labels_options) 
        self.labels_current = ["Remove Job", "Job Name", "Fork", "Output if True", "Boolean Variable"]
        self.table_scheme_current.setHorizontalHeaderLabels(self.labels_current) 
        self.editSchemeList()
        self.btn_copy_scheme.clicked.connect(self.copyJobs)
        self.btn_remove_from_current.clicked.connect(self.removeJobs)
        self.buttonBox.accepted.connect(self.transferTable)
                


    def editSchemeList(self):
        
        self.table_scheme_options.setRowCount(len(self.cbdat.scheme.jobs_in_scheme))

        for i, job in enumerate(self.cbdat.scheme.jobs_in_scheme):

            self.table_scheme_options.setItem(i, 0, QTableWidgetItem())
            self.table_scheme_options.item(i, 0).setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            self.table_scheme_options.item(i, 0).setCheckState(Qt.CheckState.Unchecked)

            self.table_scheme_options.setItem(i, 1, QTableWidgetItem(str(job))) # make the field uneditable


            self.table_scheme_options.setItem(i, 2, QTableWidgetItem())
            self.table_scheme_options.item(i, 2).setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            self.table_scheme_options.item(i, 2).setCheckState(Qt.CheckState.Unchecked)

            self.table_scheme_options.setItem(i, 3, QTableWidgetItem(str("undefined")))
            self.table_scheme_options.setItem(i, 4, QTableWidgetItem(str("undefined")))


    def copyJobs(self):
        for row in range(self.table_scheme_options.rowCount()):
            if self.table_scheme_options.item(row, 0).checkState() == Qt.CheckState.Checked:
                self.table_scheme_current.insertRow(self.table_scheme_current.rowCount())
                job = [self.table_scheme_options.item(row, col).text() for col in range(self.table_scheme_options.columnCount())]
                for col, var in enumerate(job):
                    if col == 0 or col == 2:
                        new_checkbox = QTableWidgetItem()
                        new_checkbox.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                        new_checkbox.setCheckState(Qt.CheckState.Unchecked)
                        self.table_scheme_current.setItem(self.table_scheme_current.rowCount() - 1, col, new_checkbox)
                    else:
                        self.table_scheme_current.setItem(self.table_scheme_current.rowCount() - 1, col, QTableWidgetItem(var))
                
    def removeJobs(self):
        rows_to_remove = []

        for row in range(self.table_scheme_current.rowCount()):
            if self.table_scheme_current.item(row, 0).checkState() == Qt.CheckState.Checked:
                rows_to_remove.append(row)

        # Remove rows in reverse order to avoid index shifting
        for row in reversed(rows_to_remove):
            self.table_scheme_current.removeRow(row)

    def transferTable(self):
        self.table_scheme.clearContents()
        self.table_scheme.setRowCount(0)
        for row in range(self.table_scheme_current.rowCount()):
            row_data = []
            for col in range(1, self.table_scheme_current.columnCount()):
                val = self.table_scheme_current.item(row, col)
                row_data.append(val.text())

            self.table_scheme.insertRow(self.table_scheme.rowCount())
            for col, data in enumerate(row_data):
                self.table_scheme.setItem(self.table_scheme.rowCount() - 1, col, QTableWidgetItem(data))




if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = EditScheme()
    dialog.show()
    sys.exit(app.exec())


