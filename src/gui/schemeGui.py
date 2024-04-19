import sys
import os
import pandas as pd
from PyQt6 import QtWidgets
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QApplication, QMainWindow, QDialog, QComboBox, QTabWidget, QWidget, QCheckBox, QAbstractItemView
from PyQt6.QtCore import Qt
import yaml


current_dir = os.path.dirname(os.path.abspath(__name__))
# change the path to be until src
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

#from lib.functions import get_value_from_tab
from src.gui.libGui import browse_dirs, change_values, update_df, abs_to_loc_path, change_bckgrnd,get_inputNodesFromSchemeTable 
from src.rw.librw import schemeMeta,cbconfig,read_mdoc
from src.gui.edit_scheme import EditScheme

class MainUI(QMainWindow):
    """
    Main window of the UI.
    """
    def __init__(self,args):
        """
        Setting up the buttons in the code and connecting them to their respective functions.
        """ 
        super(MainUI, self).__init__()
        loadUi(os.path.abspath(__file__).replace('.py','.ui'), self)
       
        #custom varibales
        self.cbdat = type('', (), {})() 
        self.cbdat.CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
        self.cbdat.defaultSchemePath=self.cbdat.CRYOBOOST_HOME + "/config/master_scheme"
        self.cbdat.confPath=self.cbdat.CRYOBOOST_HOME + "/config/conf.yaml"
        self.cbdat.scheme=schemeMeta(self.cbdat.defaultSchemePath)
        self.cbdat.conf=cbconfig(self.cbdat.confPath)     
       
        self.btn_makeJobTabs.clicked.connect(self.makeJobTabs)
        self.groupBox_in_paths.setEnabled(False)
        # have now put to textChanged --> every key entered updates it. If it takes too long to iterate every
        # time, change to editingFinished
        self.line_path_movies.textChanged.connect(self.loadPathMovies)
        self.btn_browse_movies.clicked.connect(self.browsePathMovies)
        self.line_path_mdocs.textChanged.connect(self.loadPathMdocs)
        self.btn_browse_mdocs.clicked.connect(self.browsePathMdocs)
        self.btn_use_movie_path.clicked.connect(self.mdocs_use_movie_path)
        self.dropDown_config.activated.connect(self.loadConfig)
        self.btn_browse_target.clicked.connect(self.browsePathTarget)
        self.btn_writeStar.clicked.connect(self.changeDf)
        self.btn_writeStar.clicked.connect(self.writeStar)
        self.table_scheme.setColumnCount(4)
        #self.table_scheme.setEditTriggers(QAbstractItemView.editTriggers)
        
        self.labels_scheme = ["Job Name", "Fork", "Output if True", "Boolean Variable"]
        self.table_scheme.setHorizontalHeaderLabels(self.labels_scheme) 
        self.table_scheme.setRowCount(len(self.cbdat.scheme.jobs_in_scheme))    
        for i, job in enumerate(self.cbdat.scheme.jobs_in_scheme):
            self.table_scheme.setItem(i, 0, QTableWidgetItem(str(job))) 
            self.table_scheme.setItem(i, 1, QTableWidgetItem())
            self.table_scheme.item(i, 1).setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            self.table_scheme.item(i, 1).setCheckState(Qt.CheckState.Unchecked)
            self.table_scheme.setItem(i, 2, QTableWidgetItem(str("undefined")))
            self.table_scheme.setItem(i, 3, QTableWidgetItem(str("undefined")))
       
        self.dropDown_config.addItem("Choose Microscope Set-Up")
        for i in self.cbdat.conf.microscope_presets:
            self.dropDown_config.addItem(self.cbdat.conf.microscope_presets[i])
    def makeJobTabs(self):
        """
        insert a new tab for every job and place a table with the parameters found in the respective job.star
        file in the ["joboptions_values"] df.
        """
        if self.check_edit_scheme.isChecked():
            EditScheme(self.table_scheme, self).exec()
        inputNodes=get_inputNodesFromSchemeTable(self.table_scheme,jobsOnly=True)
        self.cbdat.scheme=self.cbdat.scheme.filterSchemeByNodes(inputNodes)
        
        # define where the new tabs should be inserted so all tabs can be used in order             
        first_insert_position = 1
        # loop through the jobs and create a tab for each job
        
        conf=self.cbdat.conf
        for job in self.cbdat.scheme.jobs_in_scheme:
            # arguments: insertTab(index where it's inserted, widget that's inserted, name of tab)
            self.tabWidget.insertTab(first_insert_position, QWidget(), job)
            # build a table with the dataframe containinng the parameters for the respective job in the tab
            df_job = self.cbdat.scheme.job_star[job].dict["joboptions_values"]
            nRows, nColumns = df_job.shape
            # create empty table with the dimensions of the df
            self.table = QTableWidget(self)
            self.table.setColumnCount(nColumns)
            self.table.setRowCount(nRows)
            self.table.setHorizontalHeaderLabels(("Parameter", "Value"))
            # this doesn't work yet...:
            #self.table.setMinimumSize(1500, 400)            
            # populate the table with the values of the df
            for row in range(nRows):
                for col in range(nColumns):
                    # set the value that should be added to the respective col/row combination in the df containing the parameters
                    current_value =df_job.iloc[row, col]
                    # see whether there is an alias for the parameter (only for the Parameters column)
                    if col == 0:
                        alias = conf.get_alias(job, current_value)
                        # if there is an alias, set the widgetItem to this alias, else, do as normal
                        if alias != None:
                            self.table.setItem(row, col, QTableWidgetItem(alias))
                        else:
                            self.table.setItem(row, col, QTableWidgetItem(current_value))
                        # set the flag for this field as not editable --> people cannot accidentally change the 
                        # name of a parameter, inhibiting Relion later
                        self.table.item(row, col).setFlags(self.table.item(row, col).flags() & ~Qt.ItemFlag.ItemIsEditable)
                    else:
                        self.table.setItem(row, col, QTableWidgetItem(current_value))
            # set where this table should be placed
            tab_layout = QVBoxLayout(self.tabWidget.widget(first_insert_position))
            tab_layout.addWidget(self.table)
            #self.table.setMinimumSize(1500, 400)            
            first_insert_position += 1
        # make groupBox_in_paths available so it can only be used after the tabs are created (--> can load in data)
        self.groupBox_in_paths.setEnabled(True)

    
    
    
    
    
    def makeJobTabsNew(self):
        """
        insert a new tab for every job and place a table with the parameters found in the respective job.star
        file in the ["joboptions_values"] df.
        """
        if self.check_edit_scheme.isChecked():
            EditScheme(self.table_scheme, self).exec()

        """ make this into a function that just takes table as input"""
        self.df_col_name = ["rlnSchemeEdgeInputNodeName", "rlnSchemeEdgeOutputNodeName", "rlnSchemeEdgeIsFork", "rlnSchemeEdgeOutputNodeNameIfTrue", "rlnSchemeEdgeBooleanVariable"]
        self.new_scheme = {"scheme_edges": pd.DataFrame(columns=self.df_col_name)} 
        self.table_data = {0: {"Job Name": "EXIT_maxtime", "Fork": "0", "Output if True": "undefined", "Boolean Variable": "undefined"}}

        # Iterate over each row in the table
        for row in range(self.table_scheme.rowCount()):
            # Create an empty dictionary to store data for the current row
            self.row_data = {}

            # Iterate over each column in the table
            for col in self.labels_scheme:
                # Get the item in the current cell
                if col == "Fork":
                    if self.table_scheme.item(row, 0).checkState() == Qt.CheckState.Checked:
                        self.item = "1"
                    else:
                        self.item = "0"
                else:
                    self.col_index = self.labels_scheme.index(col)
                    self.item = self.table_scheme.item(row, self.col_index).text()
            
                self.row_data[col] = self.item
            
            self.table_data[row+1] = self.row_data    

        self.table_data[self.table_scheme.rowCount()+1] = {"Job Name": "WAIT", "Fork": "0", "Output if True": "undefined", "Boolean Variable": "undefined"}
        #print(self.table_data)
        # Initialize lists to hold data for each column
        rlnSchemeEdgeInputNodeName = []
        rlnSchemeEdgeOutputNodeName = []
        rlnSchemeEdgeIsFork = []
        rlnSchemeEdgeOutputNodeNameIfTrue = []
        rlnSchemeEdgeBooleanVariable = []

        for i, data in self.table_data.items():
            if i == 0:
                rlnSchemeEdgeInputNodeName.append("WAIT")
            else:
                prev_data = list(self.table_data.values())[i - 1]
                rlnSchemeEdgeInputNodeName.append(prev_data["Job Name"])

            rlnSchemeEdgeOutputNodeName.append(data["Job Name"])
            rlnSchemeEdgeIsFork.append(data["Fork"])
            rlnSchemeEdgeOutputNodeNameIfTrue.append(data["Output if True"])
            rlnSchemeEdgeBooleanVariable.append(data["Boolean Variable"])

        # Assign lists to corresponding keys in self.new_scheme["scheme_edges"]
        self.new_scheme["scheme_edges"]["rlnSchemeEdgeInputNodeName"] = rlnSchemeEdgeInputNodeName
        self.new_scheme["scheme_edges"]["rlnSchemeEdgeOutputNodeName"] = rlnSchemeEdgeOutputNodeName
        self.new_scheme["scheme_edges"]["rlnSchemeEdgeIsFork"] = rlnSchemeEdgeIsFork
        self.new_scheme["scheme_edges"]["rlnSchemeEdgeOutputNodeNameIfTrue"] = rlnSchemeEdgeOutputNodeNameIfTrue
        self.new_scheme["scheme_edges"]["rlnSchemeEdgeBooleanVariable"] = rlnSchemeEdgeBooleanVariable


        self.cbdat.scheme.scheme_star["scheme_edges"] = self.new_scheme["scheme_edges"]

        self.jobs_in_scheme = self.scheme_star_dict["scheme_edges"].rlnSchemeEdgeOutputNodeName.iloc[1:-1]

        
        # After the scheme is edited, crerate the dict with "Jobname": "df with job.star" 
        """Prob can put back in lib as a function"""
        self.job_star_dict = {
        f"{job}": read_star(os.path.join(path_to_scheme, f"{job}/job.star"))
        for job in self.jobs_in_scheme
        }

        """ create the 2nd pd.Series by moving the last entry to the first position, then change the 2 columns in the df (should I change the other parts too?="""


        # define where the new tabs should be inserted so all tabs can be used in order             
        first_insert_position = 1
        # loop through the jobs and create a tab for each job
        last_job = None
        path_to_star_file_names_yaml = root_dir + "/src/gui/star_file_names.yaml"
        with open(path_to_star_file_names_yaml, "r") as file:
            star_file_names_yaml_data = yaml.safe_load(file)
        for job in self.jobs_in_scheme:
            # arguments: insertTab(index where it's inserted, widget that's inserted, name of tab)
            self.tabWidget.insertTab(first_insert_position, QWidget(), job)
            # build a table with the dataframe containinng the parameters for the respective job in the tab
            self.df = (self.job_star_dict[job]["joboptions_values"])
            nRows, nColumns = self.df.shape
            # create empty table with the dimensions of the df
            self.table = QTableWidget(self)
            self.table.setColumnCount(nColumns)
            self.table.setRowCount(nRows)
            self.table.setHorizontalHeaderLabels(("Parameter", "Value"))
            # this doesn't work yet...:
            #self.table.setMinimumSize(1500, 400)            
            # populate the table with the values of the df
            skip_next_iteration = False # To edit the the input file correctly, have to manually set it --> skip the next iteration that would set it
            for row in range(nRows):
                if skip_next_iteration:
                    skip_next_iteration = False  # Reset the flag for the next iteration
                    #continue
                for col in range(nColumns):
                    # set the value that should be added to the respective col/row combination in the df containing the parameters
                    current_value = self.df.iloc[row, col]
                    # see whether there is an alias for the parameter (only for the Parameters column)
                    if col == 0:
                        alias = get_alias(job, current_value)
                        # if there is an alias, set the widgetItem to this alias, else, do as normal
                        if alias != None:
                            self.table.setItem(row, col, QTableWidgetItem(alias))
                            if alias == "Input .star file" and last_job:
                                self.input_star_file = star_file_names_yaml_data["star_file"][f"{last_job}"]
                                self.table.setItem(row, 1, QTableWidgetItem(f"Schemes/master_scheme/{self.input_star_file}"))
                                change_bckgrnd(self.table, row, 1)
                                break # Sets skip_next_iteration to True
                        else:
                            self.table.setItem(row, col, QTableWidgetItem(current_value))
                        # set the flag for this field as not editable --> people cannot accidentally change the 
                        # name of a parameter, inhibiting Relion later
                        self.table.item(row, col).setFlags(self.table.item(row, col).flags() & ~Qt.ItemFlag.ItemIsEditable)
                    else:
                        self.table.setItem(row, col, QTableWidgetItem(current_value))
            # set where this table should be placed
            tab_layout = QVBoxLayout(self.tabWidget.widget(first_insert_position))
            tab_layout.addWidget(self.table)
            #self.table.setMinimumSize(1500, 400)            
            first_insert_position += 1
            last_job = job
        # make groupBox_in_paths available so it can only be used after the tabs are created (--> can load in data)
        self.groupBox_in_paths.setEnabled(True)
        self.btn_makeJobTabs.setEnabled(False)


    def loadPathMovies(self):
        """
        set the parameter path to files in the importmovies job to the link provided here. Then, look into the 
        header of the movies provided and copy the respective information to the respective parameters too.
        """
        # save the input of the field as variable
        params_dict_movies = {"movie_files": self.line_path_movies.text() + "*.eer"}

        # reading the header doesn't work yet!
 
        # go to the importmovies tab by getting the index where importmovies is
        # if header also has parameters for other jobs, have to loop through here
        for current_tab in self.cbdat.scheme.jobs_in_scheme:
            index_import = self.cbdat.scheme.jobs_in_scheme[self.cbdat.scheme.jobs_in_scheme == current_tab].index
            self.tabWidget.setCurrentIndex(index_import.item())
            # find the  copy the text of the input field to the path to file, check for aliases of the field, and
            # iterate over the parameters of the header to input them too
            table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
            change_values(table_widget, params_dict_movies, self.cbdat.scheme.jobs_in_scheme,self.cbdat.conf)
        # go back to setup tab
        self.tabWidget.setCurrentIndex(0)

    def browsePathMovies(self):
        browse_dirs(self.line_path_movies)
        

    def browsePathMdocs(self):
        browse_dirs(self.line_path_mdocs)


    def mdocs_use_movie_path(self):
        self.line_path_mdocs.setText(self.line_path_movies.text())


    def loadPathMdocs(self):
        """
        set the parameter path to mdoc in the importmovies job to the link provided here. Then, look into the 
        mdoc file and copy the respective information to the respective parameters too.
        """
        # save the input of the field as variable
        params_dict_mdoc = {"mdoc_files": self.line_path_mdocs.text() + "*.mdoc"}
        # look into the mdoc file and save all parameters as variables
        try:
            params_dict_mdoc.update(read_mdoc(params_dict_mdoc["mdoc_files"]))
        except:
            pass
        # go to the importmovies tab by getting the index where importmovies is
        # if mdoc also has parameters for other jobs, have to loop through here
        for current_tab in self.cbdat.scheme.jobs_in_scheme:
            index_import = self.cbdat.scheme.jobs_in_scheme[self.cbdat.scheme.jobs_in_scheme == current_tab].index
            self.tabWidget.setCurrentIndex(index_import.item())
            # find the  copy the text of the input field to the path to file, check for aliases of the field, and
            # iterate over the parameters of the header to input them too
            table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
            change_values(table_widget, params_dict_mdoc, self.cbdat.scheme.jobs_in_scheme,self.cbdat.conf)
        # go back to setup tab
        self.tabWidget.setCurrentIndex(0)
        

    def loadConfig(self):
        """
        go through all parameters of all tabs and see whether any parameter is in the config_microscopes file
        (= contains all parameters that are solely dependent on the setup) under the chosen setup. If a parameter
        is found, its value is set to the value defined in the config_microscopes for this parameter.
        """
        microscope = self.dropDown_config.currentText()
        # only do something if a microscope is chosen
        if microscope != "Choose Microscope Set-Up":
        
            microscope_parameters=self.cbdat.conf.get_microscopePreSet(microscope)
            # exclude the first tab (= set up)
            for job_tab_index in range(1, len(self.cbdat.scheme.jobs_in_scheme) + 1):
                # go to the tabs based on their index
                self.tabWidget.setCurrentIndex(job_tab_index)
                # access the TableWidget in the currently open TabWidget
                table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
                #change_values(table_widget, microscope_parameters, jobs_in_scheme)
                change_values(table_widget, microscope_parameters, self.cbdat.scheme.jobs_in_scheme,self.cbdat.conf)
            # go back to setup tab
            self.tabWidget.setCurrentIndex(0)


    def browsePathTarget(self):
        browse_dirs(self.line_path_new_project)


    def changeDf(self):
        """
        first, create a symlink to the frames and mdoc files and change the absolute paths provided by the browse 
        function to relative paths to these links and change the input fields accordingly.
        Then, go through all tabs that were created using the makeJobTabs function, select the table that is in that tab
        and iterate through the columns and rows of that table, checking whether there is an alias (and reverting
        it if there is) and then writing the value into the df for the job.star file at the same position as it 
        is in the table (table is created based on this df so it should always be the same position and name). 
        """
        self.path_to_new_project = self.line_path_new_project.text()        
        self.name_new_frames_dir = self.line_path_movies.text().split("/")[-2]
        self.name_new_mdocs_dir = self.line_path_mdocs.text().split("/")[-2]

        abs_to_loc_path(self.line_path_movies.text(), self.line_path_mdocs.text(), self.path_to_new_project)

        if self.line_path_mdocs.text() != self.line_path_movies.text():
            self.line_path_mdocs.setText("./" + self.name_new_mdocs_dir)
        else:
            self.line_path_mdocs.setText("./" + self.name_new_frames_dir + "/")
        self.line_path_movies.setText("./" + self.name_new_frames_dir + "/")

        # exclude the first tab (= set up)
        for job_tab_index in range(1, len(self.cbdat.scheme.jobs_in_scheme) + 1):
            # save the name of the job based on the index (tabs also created in order of the index --> is the same)
            job = self.cbdat.scheme.jobs_in_scheme[job_tab_index]
            #job_name = self.tabWidget.tabText(job_tab)
            # go to the tabs based on their index
            self.tabWidget.setCurrentIndex(job_tab_index)
            # access the TableWidget in the currently open TabWidget
            table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
            
            nRows = table_widget.rowCount()
            nColumns = table_widget.columnCount()
            # iterate through the table and access each row
            update_df(self.cbdat.scheme.job_star, table_widget, nRows, nColumns, job,self.cbdat.conf)
        # in the end, go back to the start relion tab from where the command was started (range excludes last entry)
        self.tabWidget.setCurrentIndex(len(self.cbdat.scheme.jobs_in_scheme) + 1)


    def writeStar(self):
        """
        write the star file with the coordinates given and with the values of job_star_dict.
        so far works only if the directory doesn't exist yet.
        can be made into a pop-up window later.
        """
        # set the location for the new project to the link set in the respective field
        self.path_to_new_project = self.line_path_new_project.text()

        # create the master_scheme dict (where all other jobs are in) at the position set
        path_scheme = os.path.join(self.path_to_new_project, "Schemes/master_scheme/")
        # make a directory with this path and raise an error if such a directory already exists
        self.cbdat.scheme.write_scheme(path_scheme)
       


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
