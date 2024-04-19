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


def update_df(job_star_dict, table_widget, table_nRows, table_nCols, current_job_tab, conf):
    """
    update the df that is turned into a job.star file afterwards.

    Args:
        job_star_dict (dict): a dict containing a dict for each job, each containing a df with the respective
        parameters as value to the key "joboptions_values"
        table_widget (PyQt6 tabWidge): the widget containing the updated values.
        table_nRows (int): number or rows in table of current tab.
        table_nCols (int): number or columns in table of current tab.
        current_job_tab (str): name of the current job (for aliases).

    Returns:
        updated job_star_dict.

    Example:
        job_star_dict = job_star_dict 
        table_widget = table 
        table_nRows = 30 
        table_nCols = 2 
        current_job_tab = "importmovies" 

        It will go through the table row by row, extracting the input into each field. For inputs in the first
        columns, it will look for aliases in the yaml file, so all params have the name that Relion expects.
        Once the correct param name is determined, it writes the respective input into the respective position
        in the "joboptions_values" df of the "importmovies" dict inside the job_star_dict dict.
    """
    for row in range(table_nRows):
        for col in range(table_nCols):
            # set the value to the text in the respective field (determined by row and col index)
            value = table_widget.item(row, col).text()
            # check whether there is an alias for a parameter name and if yes, change back to original name 
            if col == 0:
                original_param_name = conf.get_alias_reverse(current_job_tab, value)
                if original_param_name != None:
                    # param_name = original_param_name
                    value = original_param_name     
            # insert value at the position defined by the index of the table
            job_star_dict[current_job_tab].dict["joboptions_values"].iloc[row, col] = value
    return(job_star_dict)


def abs_to_loc_path(path_frames, path_mdocs, path_out_dir):
    """
    Relion only accepts local paths, browsing for paths returns absolute paths. To combine this, create symlinks
    in the out_dir based on the data of the absolute paths.

    Args:
        path_frames (str): absolute path to the imported frames.
        path_mdocs (str): absolute path to the mdoc files.
        path_out_dir (str): absolute path to the project directory, in which the scheme will be executed.

    Returns:
        Creates symlinks for the input data and changes the respective fields in Relion to relative paths
        pointing to these symlinks.

    Example:
        path_frames = /fs/pool/pool-plitzko3/Michael/01-Data/relion/frames
        path_mdocs = /fs/pool/pool-plitzko3/Michael/01-Data/relion/frames
        path_out_dir = /fs/pool/pool-plitzko3/Michael/01-Data/project

        create a symlink to /fs/pool/pool-plitzko3/Michael/01-Data/relion/frames called frames and changes
        the path to the input in Relion to ./frames. As the path to the frames and to the mdocs is identical,
        only one symlink will be created for both.
    """
    original_directory = os.getcwd()

    os.chdir(path_out_dir)
    command_frames = f"ln -s {path_frames} ./"
    os.system(command_frames)
    if path_frames != path_mdocs:
        command_mdoc = f"ln -s {path_mdocs} ./"
        os.system(command_mdoc)
    # Reset directory
    os.chdir(original_directory)
    

def read_header():
    pass