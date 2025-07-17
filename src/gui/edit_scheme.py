# A Dialog box to edit the scheme
import os
import sys
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QApplication, QDialog, QTableWidget, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt
import pandas as pd
from collections import namedtuple

current_dir = os.path.dirname(os.path.abspath(__name__))
# change the path to be until src
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

#from src.read_write.read_write import jobs_in_scheme
from src.rw.librw import schemeMeta,cbconfig,read_mdoc
import warnings


class EditScheme(QDialog):
    """
    Dialog window for editing the scheme.
    """
    def __init__(self,inputScheme):
        """
        Setting up the UI.
        """ 
        warnings.filterwarnings("ignore", category=DeprecationWarning, module="sip")
        warnings.filterwarnings("ignore", message=".*sipPyTypeDict.*")
        super().__init__()  
        loadUi(os.path.abspath(__file__).replace('.py','.ui'), self)
        self.table_scheme_options.setColumnCount(3)
        self.table_scheme_current.setColumnCount(5)
        self.labels_options = ["Add Job", "Job Type","Input Job Type"] #, "Fork", "Output if True", "Boolean Variable"]
        self.table_scheme_options.setHorizontalHeaderLabels(self.labels_options) 
        self.labels_current = ["Remove Job", "Job Type","Job Tag","Input Job Type","Input Job Tag"]#, "Fork", "Output if True", "Boolean Variable"]
        self.table_scheme_current.setHorizontalHeaderLabels(self.labels_current) 
        self.btn_copy_scheme.clicked.connect(self.copyJobs)
        self.btn_remove_from_current.clicked.connect(self.removeJobs)
        self.buttonBox.accepted.connect(self.transferTable)
       
        
        if isinstance(inputScheme, str):
            print("reading: ",inputScheme)
            self.scheme=schemeMeta(inputScheme)
        else:    
            self.scheme=inputScheme
        self.genInputSchemeList(self.scheme)        


    def genInputSchemeList(self,scheme):
        
        self.table_scheme_options.setRowCount(len(scheme.jobs_in_scheme))

        for i, job in enumerate(scheme.jobs_in_scheme):

            self.table_scheme_options.setItem(i, 0, QTableWidgetItem())
            self.table_scheme_options.item(i, 0).setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            self.table_scheme_options.item(i, 0).setCheckState(Qt.CheckState.Unchecked)
            self.table_scheme_options.setItem(i, 1, QTableWidgetItem(str(job))) # make the field uneditable
            if i>0:
                df = scheme.job_star[job].dict['joboptions_values']
                ind=df.rlnJobOptionVariable=="input_star_mics"
                if not any(ind):
                    ind=df.rlnJobOptionVariable=="in_tiltseries" 
                if not any(ind):
                    ind=df.rlnJobOptionVariable=="in_mic"
                if not any(ind):
                    ind=df.rlnJobOptionVariable=="in_tomoset"
                if not any(ind):
                    ind=df.rlnJobOptionVariable=="in_optimisation"
                if not any(ind):
                    raise Exception("nether input_star_mics nor in_tiltseries found")
                row_index = df.index[ind]
                value=os.path.basename(os.path.dirname(df.loc[row_index, "rlnJobOptionValue"].item()))
                self.table_scheme_options.setItem(i, 2, QTableWidgetItem(str(value)))
                
            #self.table_scheme_options.setItem(i, 2, QTableWidgetItem())
            #self.table_scheme_options.item(i, 2).setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            #self.table_scheme_options.item(i, 2).setCheckState(Qt.CheckState.Unchecked)

            #self.table_scheme_options.setItem(i, 3, QTableWidgetItem(str("undefined")))
            #self.table_scheme_options.setItem(i, 4, QTableWidgetItem(str("undefined")))


    def copyJobs(self):
        tag=self.textEdit_tag.toPlainText()
        self.generate_table_scheme_current(tag)
        self.adapt_job_inputs()
                
    def generate_table_scheme_current(self,tag):               
        
        current_row = self.table_scheme_current.rowCount()
        self.table_scheme_current.setRowCount(current_row+self.table_scheme_options.rowCount())
        nrSelected=0
        for row in range(self.table_scheme_options.rowCount()):
            jobName=self.table_scheme_options.item(row, 1).text()
            if self.table_scheme_options.item(row, 0).checkState() == Qt.CheckState.Checked:
                new_checkbox = QTableWidgetItem()
                new_checkbox.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
                new_checkbox.setCheckState(Qt.CheckState.Unchecked)
                self.table_scheme_current.setItem(current_row,0, new_checkbox)
                self.table_scheme_current.setItem(current_row,1, QTableWidgetItem(jobName))
                self.table_scheme_current.setItem(current_row, 2, QTableWidgetItem(str(tag)))
                if self.table_scheme_options.item(row, 2) is not None:
                    inputType=self.table_scheme_options.item(row, 2).text()
                    self.table_scheme_current.setItem(current_row, 3,QTableWidgetItem(str(inputType))) 
                    if nrSelected>0:
                        self.table_scheme_current.setItem(current_row, 4,QTableWidgetItem(str(tag)))
                current_row += 1
                nrSelected += 1
        self.table_scheme_current.setRowCount(current_row)
        self.table_scheme_current.viewport().update()
        
       
    def adapt_job_inputs(self):   
        jobTypesInCurrent = [self.table_scheme_current.item(row, 1).text() 
           for row in range(self.table_scheme_current.rowCount())]
        
        for row in range(self.table_scheme_current.rowCount()):
            input=self.table_scheme_current.item(row, 3)
            if (input is not None) and (input.text() not in jobTypesInCurrent):
                print(input.text())
                jobTypeMinusOne=self.table_scheme_current.item(row-1,1).text()
                self.table_scheme_current.setItem(row, 3,QTableWidgetItem(jobTypeMinusOne))
                
                
         
                
    def removeJobs(self):
        rows_to_remove = []

        for row in range(self.table_scheme_current.rowCount()):
            if self.table_scheme_current.item(row, 0).checkState() == Qt.CheckState.Checked:
                rows_to_remove.append(row)

        # Remove rows in reverse order to avoid index shifting
        for row in reversed(rows_to_remove):
            self.table_scheme_current.removeRow(row)
        self.adapt_job_inputs()
        
    def transferTable(self):
        
        Node = namedtuple('Node', ['type', 'tag', 'inputType', 'inputTag'])
        nodes = []
        for row in range(self.table_scheme_current.rowCount()):
            jobType = self.table_scheme_current.item(row, 1).text()
            jobTag = (self.table_scheme_current.item(row, 2) or QTableWidgetItem()).text() or None
            inputJobType = (self.table_scheme_current.item(row, 3) or QTableWidgetItem()).text() or None
            inputJobTag = (self.table_scheme_current.item(row, 4) or QTableWidgetItem()).text() or None
            oneNode = Node(type=jobType, tag=jobTag, inputType=inputJobType, inputTag=inputJobTag)
            nodes.append(oneNode)
        nodes_dict = {i: node for i, node in enumerate(nodes)}   
        nodes_df = pd.DataFrame.from_dict(nodes_dict, orient='index')
        schemeAdapted=self.scheme.filterSchemeByNodes(nodes_df)
        self.schemeAdapted=schemeAdapted
        
        return schemeAdapted
    
    def getResult(self):
        return self.schemeAdapted

if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        schemePath = sys.argv[1]
    else:
        print("Please provide a scheme argument")
        sys.exit(1)
    
    app = QApplication(sys.argv)
    dialog = EditScheme(schemePath)
    #dialog.show()
    schemeAdapted = dialog.exec()
    sys.exit(app.exec())


