# library for the functions required for the basic functions of the application
import sys
import os
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QTableWidgetItem, QTabWidget, QFileDialog

current_dir = os.path.dirname(os.path.abspath(__name__))
# change the path to be until src
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

def get_inputNodesFromSchemeTable(table_widget,jobsOnly=True):
    
    inputNodes={}
    for row in range(table_widget.rowCount()):
        inputNodes[row]=table_widget.item(row,0).text()        
    return inputNodes

def browse_dirs(target_field):
    """
    browse through the files to find the path and paste that path into the specified field.

    Args:
        target_field (QLineEdit): field in which the path should be set.
    
    Example:
        target_field = line_path_to_movies
        
        A window will open, allowing you to browse through your files. Once a directory is selected, 
        the path to that directory will be copied into the field line_path_to_movies.
    """
    current_dir = os.path.dirname(__file__)
    dir_name = QFileDialog.getExistingDirectory(None, "Navigate to Directory", current_dir)
    target_field.setText(dir_name + "/")


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