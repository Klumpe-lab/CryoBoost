# library for the functions required for the basic functions of the application
import sys, subprocess
import os
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTableWidgetItem, QTabWidget, QFileDialog
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QMainWindow,QApplication, QWidget, QVBoxLayout, QTextEdit, QScrollBar
from PyQt6.QtCore import Qt



current_dir = os.path.dirname(os.path.abspath(__name__))
# change the path to be until src
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

def get_inputNodesFromSchemeTable(table_widget,jobsOnly=True):
    
    inputNodes={}
    for row in range(table_widget.rowCount()):
        inputNodes[row]=table_widget.item(row,0).text()        
    return inputNodes


def messageBox(title, text):
    """
    Shows a message box with the specified title and text.

    Args:
        title (str): title of the message box
        text (str): text of the message box

    Example:
        title = "Error"
        text = "Something went wrong"

        messageBox(title, text)
    """
    message_box = QMessageBox()
    message_box.setWindowTitle(title)
    message_box.setText(text)
    message_box.setStandardButtons(QMessageBox.StandardButton.Ok)
    message_box.exec()    
        


def browse_dirs(target_field,target_fold,dialog="qt"):
    """
    browse through the files to find the path and paste that path into the specified field.

    Args:
        target_field (QLineEdit): field in which the path should be set.
    
    Example:
        target_field = line_path_to_movies
        
        A window will open, allowing you to browse through your files. Once a directory is selected, 
        the path to that directory will be copied into the field line_path_to_movies.
    """
    current_dir = target_fold
    
      
    if dialog=="qt":
        options = QFileDialog.Option.ShowDirsOnly | QFileDialog.Option.DontResolveSymlinks |  QFileDialog.Option.DontUseNativeDialog
        dir_name = QFileDialog.getExistingDirectory(None, "Navigate to Directory", current_dir,options)
    if dialog=="zenity":
        try:
            result = subprocess.run(
                ['zenity', '--file-selection', '--directory','--filename='+current_dir],
                capture_output=True,
                text=True,
                check=True
            )
            dir_name = result.stdout.strip()
        except:
            dir_name = ""   
    if (target_field is not None):    
        target_field.setText(dir_name + "/")
    
    return dir_name+"/"
    
def browse_files(target_field,dialog="qt"):
    
    current_dir = os.path.dirname(os.getcwd())+"/"
    if dialog=="qt":
        filepath,_=QFileDialog.getOpenFileName(None, "Select File", current_dir)
    else:
        try:
            result = subprocess.run(
                ['zenity', '--file-selection','--filename='+current_dir],
                capture_output=True,
                text=True,
                check=True
            )
            filepath = result.stdout.strip()
        except:
            filepath="" 
        
    
    target_field.setText(filepath)    

def browse_filesOrFolders(target_field,rootDir=None):
    print("not workig ...")
    

def change_bckgrnd(table_widget, row_index, col_index, colour = (QColor(200, 200, 200))):
    """
    change the background colour of the respective field in the table to signal that this field was filled automatically.

    Args:
        row_index (int): row of the field for which the colour should be changed.
        col_index (int): column of the field for which the colour should be changed.
        colour (str): 3 values determining the colour the field is set to (default = darker grey).

    Example:
        auto_change_value changes a value of a field when a certain microscopy set-up is selected, this function
        will then turn the background dark grey, signalling that this is already the correct value.
    """
    table_widget.item(row_index, col_index).setBackground(colour)


def change_values(table_widget, param_val_dict, job_names,conf):
    """
    goes to the tab defined and changes the respective parameter to the new value.

    Args:
        table_widget (PyQt6 tabWidget): the widget in which the values should be changed.
        param_val_dict (dict): dictionary containing the parameter as key and the new value as value.
        job_names (pd.Series): series of job names to check for aliases.

    Example:
        table_widget = table
        param_val_dict = {"Path to movies": "../../movies/\*.eer"}
        job_names = jobs_in_scheme

        First, the aliases yaml is searched for an alias for "Path to movies". Then, it iterates
        over the rows in col 0 of the table looking for "Path to movies" (or the respective alias).
        If the parameter is found, "../../movies/\*.eer" is set in col 1 of the table at the respective
        position and the background colour of that field is changed.
    """
    nRows = table_widget.rowCount()
    for param, value in param_val_dict.items():
        # look for an alias for the param and if one is present, set the param to this alias
        original_param_name = None
        for job in job_names:
            original_param_name = conf.get_alias(job, param)
            if original_param_name:
                break

        # if an alias was found, use it as the param name. If not, use param of the param_val_dict
        param_to_set = original_param_name if original_param_name else param
        
        # find the row corresponding to the param in the table
        for row in range(nRows):
            current_param = table_widget.item(row, 0).text()
            if current_param == param_to_set:
                # set the value and change background color
                table_widget.setItem(row, 1, QTableWidgetItem(str(value)))
                change_bckgrnd(table_widget, row, 1)
                break


def read_header():
    pass

class externalTextViewer(QMainWindow):
       def __init__(self, file_path):
           super().__init__()
           self.setWindowTitle("Text File Viewer")
           self.setGeometry(100, 100, 600, 400)

           self.text_edit = QTextEdit(self)
           self.setCentralWidget(self.text_edit)
           print("file_path",file_path) 
           self.load_file(file_path)
           
           

       def load_file(self, file_path):
           try:
               with open(file_path, 'r') as file:
                   content = file.read()
                   self.text_edit.setText(content)
           except Exception as e:
               self.text_edit.setText(f"Failed to load file: {str(e)}")