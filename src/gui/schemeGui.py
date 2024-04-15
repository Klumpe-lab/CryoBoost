import sys
import os
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QApplication, QMainWindow, QDialog, QComboBox, QTabWidget, QWidget
from PyQt6.QtCore import Qt


current_dir = os.path.dirname(os.path.abspath(__name__))
# change the path to be until src
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

#from lib.functions import get_value_from_tab
from src.gui.libGui import browse_dirs, change_values, update_df, abs_to_loc_path
from src.rw.librw import scheme_star_dict, job_star_dict, jobs_in_scheme, get_alias, get_alias_reverse, load_config, read_mdoc, read_header, write_star

class MainUI(QMainWindow):
    """
    Main window of the UI.
    """
    def __init__(self):
        """
        Setting up the buttons in the code and connecting them to their respective functions.
        """ 
        super(MainUI, self).__init__()
        
        loadUi(os.path.abspath(__file__).replace('.py','.ui'), self)
        self.btn_makeJobTabs.clicked.connect(self.makeJobTabs)
        self.groupBox_in_paths.setEnabled(False)
        # have now put to textChanged --> every key entered updates it. If it takes too long to iterate every
        # time, change to editingFinished
        self.line_path_movies.textChanged.connect(self.loadPathMovies)
        self.btn_browse_movies.clicked.connect(self.browsePathMovies)
        self.line_path_mdocs.textChanged.connect(self.loadPathMdocs)
        self.btn_browse_mdocs.clicked.connect(self.browsePathMdocs)
        self.btn_use_movie_path.clicked.connect(self.mdocs_use_movie_path)
        self.dropDown_config.addItem("Choose Microscope Set-Up")
        self.dropDown_config.addItem("Titan Krios 4")
        self.dropDown_config.addItem("Titan Krios 5")
        self.dropDown_config.activated.connect(self.loadConfig)
        self.btn_browse_target.clicked.connect(self.browsePathTarget)
        self.btn_writeStar.clicked.connect(self.changeDf)
        self.btn_writeStar.clicked.connect(self.writeStar)
        

    def makeJobTabs(self):
        """
        insert a new tab for every job and place a table with the parameters found in the respective job.star
        file in the ["joboptions_values"] df.
        """
        # define where the new tabs should be inserted so all tabs can be used in order             
        first_insert_position = 1
        # loop through the jobs and create a tab for each job
        for job in jobs_in_scheme:
            # arguments: insertTab(index where it's inserted, widget that's inserted, name of tab)
            self.tabWidget.insertTab(first_insert_position, QWidget(), job)
            # build a table with the dataframe containinng the parameters for the respective job in the tab
            self.df = (job_star_dict[job]["joboptions_values"])
            nRows, nColumns = self.df.shape
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
                    current_value = self.df.iloc[row, col]
                    # see whether there is an alias for the parameter (only for the Parameters column)
                    if col == 0:
                        alias = get_alias(job, current_value)
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
        for current_tab in jobs_in_scheme:
            index_import = jobs_in_scheme[jobs_in_scheme == current_tab].index
            self.tabWidget.setCurrentIndex(index_import.item())
            # find the  copy the text of the input field to the path to file, check for aliases of the field, and
            # iterate over the parameters of the header to input them too
            table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
            change_values(table_widget, params_dict_movies, jobs_in_scheme)
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
        for current_tab in jobs_in_scheme:
            index_import = jobs_in_scheme[jobs_in_scheme == current_tab].index
            self.tabWidget.setCurrentIndex(index_import.item())
            # find the  copy the text of the input field to the path to file, check for aliases of the field, and
            # iterate over the parameters of the header to input them too
            table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
            change_values(table_widget, params_dict_mdoc, jobs_in_scheme)
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
            microscope_parameters_list_of_dicts = load_config(microscope)
            microscope_parameters = {}
            for dicts in microscope_parameters_list_of_dicts:
                microscope_parameters.update(dicts)

            # exclude the first tab (= set up)
            for job_tab_index in range(1, len(jobs_in_scheme) + 1):
                # go to the tabs based on their index
                self.tabWidget.setCurrentIndex(job_tab_index)
                # access the TableWidget in the currently open TabWidget
                table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
                #change_values(table_widget, microscope_parameters, jobs_in_scheme)
                change_values(table_widget, microscope_parameters, jobs_in_scheme)
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
        for job_tab_index in range(1, len(jobs_in_scheme) + 1):
            # save the name of the job based on the index (tabs also created in order of the index --> is the same)
            job = jobs_in_scheme[job_tab_index]
            #job_name = self.tabWidget.tabText(job_tab)
            # go to the tabs based on their index
            self.tabWidget.setCurrentIndex(job_tab_index)
            # access the TableWidget in the currently open TabWidget
            table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
            
            nRows = table_widget.rowCount()
            nColumns = table_widget.columnCount()
            # iterate through the table and access each row
            update_df(job_star_dict, table_widget, nRows, nColumns, job)
        # in the end, go back to the start relion tab from where the command was started (range excludes last entry)
        self.tabWidget.setCurrentIndex(len(jobs_in_scheme) + 1)


    def writeStar(self):
        """
        write the star file with the coordinates given and with the values of job_star_dict.
        so far works only if the directory doesn't exist yet.
        can be made into a pop-up window later.
        """
        # set the location for the new project to the link set in the respective field
        self.path_to_new_project = self.line_path_new_project.text()

        # create the master_scheme dict (where all other jobs are in) at the position set
        path_scheme_star = os.path.join(self.path_to_new_project, "Schemes/master_scheme/scheme.star")
        # make a directory with this path and raise an error if such a directory already exists
        os.makedirs(path_scheme_star, exist_ok=False)
        write_star(scheme_star_dict, path_scheme_star)

        # repeat for all jobs, creating a job.star file in these directories
        for job in jobs_in_scheme:
            path = os.path.join(self.path_to_new_project, f"Schemes/master_scheme/{job}/job.star")
            os.makedirs(path, exist_ok=False)
            job_star = job_star_dict[job]
            write_star(job_star, path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()