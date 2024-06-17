import sys
import os
import pandas as pd
from PyQt6 import QtWidgets
from PyQt6.QtGui import QTextCursor
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QApplication, QMainWindow,QMessageBox,QDialog, QComboBox, QTabWidget, QWidget, QCheckBox, QAbstractItemView
from PyQt6.QtCore import Qt
from src.pipe.libpipe import pipe
import asyncio
import aiofiles  
import yaml
from PyQt6.QtCore import QTimer
from qasync import QEventLoop, asyncSlot
import datetime

current_dir = os.path.dirname(os.path.abspath(__name__))
# change the path to be until src
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

#from lib.functions import get_value_from_tab
from src.gui.libGui import externalTextViewer,browse_dirs,browse_files,change_values,change_bckgrnd,get_inputNodesFromSchemeTable,messageBox 
from src.rw.librw import schemeMeta,cbconfig,read_mdoc,importFolderBySymlink
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
       
        self.cbdat=self.initializeDataStrcuture(args)
        self.setCallbacks()
        self.genSchemeTable()
       
        self.groupBox_WorkFlow.setEnabled(False)
        self.groupBox_Setup.setEnabled(False)
        self.groupBox_Project.setEnabled(False)
        if (self.cbdat.args.autoGen or self.cbdat.args.skipSchemeEdit):
            self.makeJobTabsFromScheme()
        
        
    
    def initializeDataStrcuture(self,args):
        #custom varibales
        cbdat = type('', (), {})() 
        cbdat.CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
        cbdat.defaultSchemePath=cbdat.CRYOBOOST_HOME + "/config/Schemes/relion_tomo_prep/"
        cbdat.confPath=cbdat.CRYOBOOST_HOME + "/config/conf.yaml"
        cbdat.pipeRunner= None
        cbdat.conf=cbconfig(cbdat.confPath)     
        cbdat.args=args
        if os.path.exists(args.proj +  "/Schemes/relion_tomo_prep/scheme.star"):
            cbdat.scheme=schemeMeta(args.proj +  "/Schemes/relion_tomo_prep/")
            args.scheme=cbdat.scheme
            cbdat.pipeRunner=pipe(args);
            cbdat.args.skipSchemeEdit=True
        else:    
            cbdat.scheme=schemeMeta(cbdat.defaultSchemePath)
        
        return cbdat
    
    def setCallbacks(self):
        self.btn_makeJobTabs.clicked.connect(self.makeJobTabsFromScheme)
        #self.groupBox_in_paths.setEnabled(False)
        self.line_path_movies.textChanged.connect(self.setPathMoviesToJobTap)
        self.line_path_mdocs.textChanged.connect(self.setPathMdocsToJobTap)
        self.line_path_gain.textChanged.connect(self.setPathGainToJobTap)
        self.dropDown_gainRot.activated.connect(self.setGainRotToJobTap)
        self.dropDown_gainFlip.activated.connect(self.setGainFlipJobTap)
        self.textEdit_pixelSize.textChanged.connect(self.setPixelSizeToJobTap)
        self.textEdit_dosePerTilt.textChanged.connect(self.setdosePerTiltToJobTap)
        self.textEdit_nomTiltAxis.textChanged.connect(self.setTiltAxisToJobTap)
        self.textEdit_invertHand.textChanged.connect(self.setInvertHandToJobTap)
        self.textEdit_eerFractions.textChanged.connect(self.setEerFractionsToJobTap)
        self.textEdit_areTomoSampleThick.textChanged.connect(self.setAreTomoSampleThickToJobTap)
        self.textEdit_ImodPatchSize.textChanged.connect(self.setImodPatchSizeToJobTap)
        self.textEdit_imodPatchOverlap.textChanged.connect(self.setImodPatchOverlapToJobTap)
        self.dropDown_tomoAlignProgram.activated.connect(self.setTomoAlignProgramToJobTap)
        self.btn_openWorkFlowLog.clicked.connect(self.openExtLogViewerWorkFlow)
        self.btn_openWorkFlowLog.clicked.connect(self.openExtLogViewerWorkFlow)
        self.btn_openJobOutpuLog.clicked.connect(self.openExtLogViewerJobOutput)
        self.btn_openJobErrorLog.clicked.connect(self.openExtLogViewerJobError)
        #self.textBrowser_workFlow.clicked.connect(self.openExtLogViewer) 
        self.btn_browse_movies.clicked.connect(self.browsePathMovies)
        self.btn_browse_mdocs.clicked.connect(self.browsePathMdocs)
        self.btn_browse_gain.clicked.connect(self.browsePathGain)
        self.btn_browse_autoPrefix.clicked.connect(self.generatePrefix)
        self.btn_use_movie_path.clicked.connect(self.mdocs_use_movie_path)
        self.dropDown_config.activated.connect(self.loadConfig)
        self.btn_browse_target.clicked.connect(self.browsePathTarget)
        self.btn_genProject.clicked.connect(self.generateProject)
        self.btn_importData.clicked.connect(self.importData)
        self.btn_startWorkFlow.clicked.connect(self.startWorkflow)
        self.btn_stopWorkFlow.clicked.connect(self.stopWorkflow)
        self.btn_unlockWorkFlow.clicked.connect(self.unlockWorkflow)
        self.btn_resetWorkFlow.clicked.connect(self.resetWorkflow)
        self.btn_resetWorkFlowHead.clicked.connect(self.resetWorkflowHead)
        self.dropDown_config.addItem("Choose Microscope Set-Up")
        for i in self.cbdat.conf.microscope_presets:
            self.dropDown_config.addItem(self.cbdat.conf.microscope_presets[i])
    
    def genSchemeTable(self):
        self.table_scheme.setColumnCount(1) #origianlly 4
        self.labels_scheme = ["Job Name"] #, "Fork", "Output if True", "Boolean Variable"]
        self.table_scheme.setHorizontalHeaderLabels(self.labels_scheme) 
        self.table_scheme.setRowCount(len(self.cbdat.scheme.jobs_in_scheme))    
        for i, job in enumerate(self.cbdat.scheme.jobs_in_scheme):
            self.table_scheme.setItem(i, 0, QTableWidgetItem(str(job))) 
            #self.table_scheme.setItem(i, 1, QTableWidgetItem())
            #self.table_scheme.item(i, 1).setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
            #self.table_scheme.item(i, 1).setCheckState(Qt.CheckState.Unchecked)
            #self.table_scheme.setItem(i, 2, QTableWidgetItem(str("undefined")))
            #self.table_scheme.setItem(i, 3, QTableWidgetItem(str("undefined")))
            
    def makeJobTabsFromScheme(self):
        """
        insert a new tab for every job and place a table with the parameters found in the respective job.star
        file in the ["joboptions_values"] df.
        """
        if ((self.check_edit_scheme.isChecked()) and (self.cbdat.args.autoGen == False) and (self.cbdat.args.skipSchemeEdit == False)):
            EditScheme(self.table_scheme, self).exec()
        
        inputNodes=get_inputNodesFromSchemeTable(self.table_scheme,jobsOnly=True)
        self.cbdat.scheme=self.cbdat.scheme.filterSchemeByNodes(inputNodes)
        
        insertPosition=1
        for job in self.cbdat.scheme.jobs_in_scheme:
           self.schemeJobToTab(job,self.cbdat.conf,insertPosition)
           insertPosition += 1 
        
        if (self.cbdat.args.mdocs != None):
            self.line_path_mdocs.setText(self.cbdat.args.mdocs)
        if (self.cbdat.args.movies != None):
             self.line_path_movies.setText(self.cbdat.args.movies)
        if (self.cbdat.args.proj != None):
             self.line_path_new_project.setText(self.cbdat.args.proj)
             
        self.groupBox_WorkFlow.setEnabled(True)
        self.groupBox_Setup.setEnabled(True)
        self.groupBox_Project.setEnabled(True)
        
        logfile_path=self.line_path_new_project.text()+os.path.sep +"relion_tomo_prep.log"
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.view_log_file(logfile_path))
        self.timer.start(2000)  # Update the log fil    

    def schemeJobToTab(self,job,conf,insertPosition):
        # arguments: insertTab(index where it's inserted, widget that's inserted, name of tab)
        self.tabWidget.insertTab(insertPosition, QWidget(), job)
        # build a table with the dataframe containinng the parameters for the respective job in the tab
        df_job = self.cbdat.scheme.job_star[job].dict["joboptions_values"]
        nRows, nColumns = df_job.shape
        # create empty table with the dimensions of the df
        self.table = QTableWidget(self)
        self.table.setColumnCount(nColumns)
        self.table.setRowCount(nRows)
        self.table.setHorizontalHeaderLabels(("Parameter", "Value"))
       
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
                    self.table.item(row, col).setFlags(self.table.item(row, col).flags() & ~Qt.ItemFlag.ItemIsEditable)
                else:
                    self.table.setItem(row, col, QTableWidgetItem(current_value))
        # set where this table should be placed
        tab_layout = QVBoxLayout(self.tabWidget.widget(insertPosition))
        tab_layout.addWidget(self.table)
        #self.table.setMinimumSize(1500, 400)            
        

    def setPathMoviesToJobTap(self):
        """
        Sets the path to movies in the importmovies job to the link provided in the line_path_movies field.
        Then, sets the parameters dictionary to the jobs in the tab widget.

        Args:
            None

        Returns:
            None
        """
        
        params_dict = {"movie_files": "frames/*" + os.path.splitext(self.line_path_movies.text())[1] }
        self.setParamsDictToJobTap(params_dict)
        
    def setPathMdocsToJobTap(self):
        """
        Sets the parameters dictionary to the jobs in the tab widget for the mdoc files.

        This function retrieves the file extension from the `line_path_mdocs` text field and constructs the `mdoc_files` parameter dictionary. The constructed dictionary is then passed to the `setParamsDictToJobTap` method.

        Parameters:
            None

        Returns:
            None
        """
        
        params_dict = {"mdoc_files": "mdoc/*" + os.path.splitext(self.line_path_mdocs.text())[1] }
        self.setParamsDictToJobTap(params_dict)
    
    def setPixelSizeToJobTap(self):
        params_dict = {"angpix": self.textEdit_pixelSize.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["importmovies"])      
     
    def setdosePerTiltToJobTap(self):
        params_dict = {"dose_rate": self.textEdit_dosePerTilt.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["importmovies"])       
    
    def setTiltAxisToJobTap(self):
        params_dict = {"tilt_axis_angle": self.textEdit_nomTiltAxis.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["importmovies"]) 
    
    def setPathGainToJobTap(self):
        params_dict = {"fn_gain_ref": self.line_path_gain.text()} 
        self.setParamsDictToJobTap(params_dict,["motioncorr"]) 
    
    def setGainRotToJobTap(self):
        params_dict = {"gain_rot": self.dropDown_gainRot.currentText()} 
        self.setParamsDictToJobTap(params_dict,["motioncorr"]) 
    
    def setGainFlipJobTap(self):
        params_dict = {"gain_flip": self.dropDown_gainFlip.currentText()} 
        self.setParamsDictToJobTap(params_dict,["motioncorr"]) 
    def setInvertHandToJobTap(self):
        params_dict = {"flip_tiltseries_hand": self.textEdit_invertHand.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["importmovies"]) 
    
    def setEerFractionsToJobTap(self):
        params_dict = {"eer_grouping": self.textEdit_eerFractions.toPlainText()}
        self.setParamsDictToJobTap(params_dict,["motioncorr"]) 
    
    def setAreTomoSampleThickToJobTap(self):
        params_dict = {"aretomo_thickness": self.textEdit_areTomoSampleThick.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["aligntilts"]) 
    
    def setAreTomoSampleThickToJobTap(self):
        params_dict = {"aretomo_thickness": self.textEdit_areTomoSampleThick.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["aligntilts"]) 
    
    def setImodPatchSizeToJobTap(self):
        params_dict = {"patch_size": self.textEdit_ImodPatchSize.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["aligntilts"]) 
    
    def setImodPatchOverlapToJobTap(self):
        params_dict = {"patch_overlap": self.textEdit_imodPatchOverlap.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["aligntilts"]) 
    
    def setTomoAlignProgramToJobTap(self):
        
        programSelected=self.dropDown_tomoAlignProgram.currentText()
        if (programSelected=="Imod"):
            params_dictAre = {"do_aretomo": "No"}
            params_dictImod = {"do_aretomo": "Yes"}
        
        if (programSelected=="Aretomo"):
            params_dictAre = {"do_aretomo": "Yes"}
            params_dictImod = {"do_aretomo": "No"}
        
        self.setParamsDictToJobTap(params_dictAre,["aligntilts"])
        self.setParamsDictToJobTap(params_dictImod,["aligntilts"])
        
        
    def setParamsDictToJobTap(self,params_dict,applyToJobs="all"):
        """
        A function that sets the parameters dictionary to the jobs in the tab widget based on the given parameters.

        Args:
            params_dict (dict): A dictionary containing the parameters to be set.
            applyToJobs (str, optional): A List specifying which jobs to apply the p
            arameters to. Defaults to "all".
               
        Returns:
            None
        """
        if (applyToJobs == "all"):
           applyToJobs = list(self.cbdat.scheme.jobs_in_scheme)
           
        for current_tab in self.cbdat.scheme.jobs_in_scheme:
            print(current_tab in applyToJobs)
            if current_tab in applyToJobs:
                index_import = self.cbdat.scheme.jobs_in_scheme[self.cbdat.scheme.jobs_in_scheme == current_tab].index
                self.tabWidget.setCurrentIndex(index_import.item())
                table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
                change_values(table_widget, params_dict, self.cbdat.scheme.jobs_in_scheme,self.cbdat.conf)
        self.tabWidget.setCurrentIndex(0)
    
    
    def browsePathMovies(self):
        browse_files(self.line_path_movies)
        
    def browsePathMdocs(self):
        browse_files(self.line_path_mdocs)

    def browsePathGain(self):
        browse_files(self.line_path_gain)
    
    def generatePrefix(self):
       current_datetime = datetime.datetime.now()
       prefix=current_datetime.strftime("%Y-%m-%d-%H-%M-%S_")
       self.line_path_crImportPrefix.setText(prefix)
        
    def mdocs_use_movie_path(self):
        self.line_path_mdocs.setText(self.line_path_movies.text())

    def startWorkflow(self):
        
        if self.checkPipeRunner()==False:
            return
        
        if self.cbdat.pipeRunner.checkForLock():
            messageBox("lock exists","stop workflow first")
            return
        print(self.cbdat.pipeRunner.getCurrentNodeScheme())
        
        if self.cbdat.pipeRunner.getCurrentNodeScheme()=="EXIT":
            reply = QMessageBox.question(self, 'Workflow has finished!',
                                 "WorkFlow has finished. To run it again on new data you need to reset the workflow head. Do you want to reset the workflow head?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
       
            if reply == QMessageBox.StandardButton.Yes:
                self.cbdat.pipeRunner.setCurrentNodeScheme("WAIT")
            else:
                return    
                
        
        if self.checkBox_openRelionGui.isChecked():
            self.cbdat.pipeRunner.openRelionGui()
        self.cbdat.pipeRunner.runScheme()
        
        
         
    
    def stopWorkflow(self):
        
        if self.checkPipeRunner()==False:
            return
        
        reply = QMessageBox.question(self, 'Message',
                                 "Do you really want to stop the workflow?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.cbdat.pipeRunner.abortScheme()
  
       
    def resetWorkflow(self):
       
       if self.checkPipeRunner()==False:
            return
       
       if (self.cbdat.pipeRunner.checkForLock()):
            messageBox("lock exists","stop workflow first")
            return
       
       reply = QMessageBox.question(self, 'Message',
                                 "Do you really want to reset the workflow?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
       
       if reply == QMessageBox.StandardButton.Yes:
            self.cbdat.pipeRunner.resetScheme()          
         
    def resetWorkflowHead(self):
       
       if self.checkPipeRunner()==False:
            return
       
       if (self.cbdat.pipeRunner.checkForLock()):
            messageBox("lock exists","stop workflow first")
            return
       
       reply = QMessageBox.question(self, 'Reset',
                                 "Do you really want to reset the workflow head?",
                                 QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
       
       if reply == QMessageBox.StandardButton.Yes:
            self.cbdat.pipeRunner.setCurrentNodeScheme("WAIT")      
    
    
    def unlockWorkflow(self):
       
       if self.checkPipeRunner()==False:
            return
       
       self.cbdat.pipeRunner.unlockScheme()          
    
    def checkPipeRunner(self,warnProjectExists=False):
        
        if self.cbdat.pipeRunner is not None: 
            if (warnProjectExists):
                messageBox("Project!","You have already a Project")
            return True    
        else:
            if (warnProjectExists==False):
                messageBox("No Project!","Generate a Project first")
            return False 
    
    def openExtLogViewerWorkFlow(self):
        
        logfile_path=self.line_path_new_project.text()+os.path.sep +"relion_tomo_prep.log"
        self.viewer = externalTextViewer(logfile_path)
        self.viewer.show()
        
    def openExtLogViewerJobOutput(self):
        
        if (self.cbdat.pipeRunner is  None):
            return
        
        logOut,logError=self.cbdat.pipeRunner.getLastJobLogs()
        logfile_path=logOut
        self.viewer = externalTextViewer(logfile_path)
        self.viewer.show()
    
    def openExtLogViewerJobError(self):
        
        if (self.cbdat.pipeRunner is  None):
            return
        
        logOut,logError=self.cbdat.pipeRunner.getLastJobLogs()
        logfile_path=logError
        self.viewer = externalTextViewer(logfile_path)
        self.viewer.show()
    
    
    def view_log_file(self, log_file_path):
        """
        This function reads the content of a log file and displays it in a text browser.

        Parameters:
        log_file_path (str): The path to the log file.

        Returns:
        None. The function updates the text in the text browser.
        """
        if (self.cbdat.pipeRunner is None):
            return
        
        try:
            with open(log_file_path, 'r') as log_file:
                log_content = log_file.read()
                self.textBrowser_workFlow.setText(log_content)
        except Exception as e:
            self.textBrowser_workFlow.setText(f"Failed to read log file: {e}")
        self.textBrowser_workFlow.moveCursor(QTextCursor.MoveOperation.End)    
        
        logOut,logError=self.cbdat.pipeRunner.getLastJobLogs()
        
        try:
            with open(logOut, 'r') as log_file:
                log_contentOut = log_file.read()
                self.textBrowserJobsOut.setText(log_contentOut)
            with open(logError, 'r') as log_fileError:
                log_contentError = log_fileError.read()
                if self.checkBox_jobErrroShowWarning.isChecked()==False:
                    log_contentError = "\n".join(line for line in log_contentError.splitlines() if "warning" not in line.lower() and "warn" not in line.lower() )
                self.textBrowserJobsError.setText(log_contentError)    
        except Exception as e:
            self.textBrowserJobsOut.setText(f"Failed to read log file: {e}")
        self.textBrowserJobsOut.moveCursor(QTextCursor.MoveOperation.End) 
        self.textBrowserJobsError.moveCursor(QTextCursor.MoveOperation.End)
    
    
    
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


    def generateProject(self):
        """
        first, create a symlink to the frames and mdoc files and change the absolute paths provided by the browse 
        function to relative paths to these links and change the input fields accordingly.
        Then, go through all tabs that were created using the makeJobTabs function, select the table that is in that tab
        and iterate through the columns and rows of that table, checking whether there is an alias (and reverting
        it if there is) and then writing the value into the df for the job.star file at the same position as it 
        is in the table (table is created based on this df so it should always be the same position and name). 
        """
        
        if self.checkPipeRunner(warnProjectExists=True):
            return
        
        scheme=self.cbdat.scheme
        scheme=self.updateSchemeFromJobTabs(scheme,self.tabWidget)
        self.cbdat.scheme=scheme
        
        args=self.cbdat.args
        args.mdocs=self.line_path_mdocs.text()
        args.movies=self.line_path_movies.text()
        args.proj=self.line_path_new_project.text()
        args.scheme=scheme
        
        pipeRunner=pipe(args)
        pipeRunner.initProject()
        pipeRunner.writeScheme()
        pipeRunner.scheme.schemeFilePath=args.proj +  "/Schemes/relion_tomo_prep/scheme.star"
        self.cbdat.pipeRunner=pipeRunner
        
    
        
    def importData(self):    
        
        if self.checkPipeRunner()==False:
            return
        self.cbdat.pipeRunner.pathFrames=self.line_path_movies.text()
        self.cbdat.pipeRunner.pathMdoc=self.line_path_mdocs.text()
        self.cbdat.pipeRunner.importPrefix=self.line_path_crImportPrefix.text()
        self.cbdat.pipeRunner.importData()    
        #scheme=self.updateSchemeFromJobTabs(scheme,self.tabWidget)
        #self.cbdat.pipeRunner.writeScheme()
    
    def updateSchemeFromJobTabs(self,scheme,tabWidget):
        """
        Updates the given scheme by iterating over each job tab in the given tab widget and updating the corresponding job's star file based on the table widget's contents.

        Parameters:
            scheme (Scheme): The scheme object to be updated.
            tabWidget (QTabWidget): The tab widget containing the job tabs.

        Returns:
            Scheme: The updated scheme object.
        """
        
        for job_tab_index in range(1, len(scheme.jobs_in_scheme) + 1):
            tabWidget.setCurrentIndex(job_tab_index)
            table_widget = tabWidget.currentWidget().findChild(QTableWidget)
            jobName = scheme.jobs_in_scheme[job_tab_index]
            scheme.job_star[jobName]=self.updateSchemeJobFromTable(scheme.job_star[jobName], table_widget,jobName,self.cbdat.conf)

            
        tabWidget.setCurrentIndex(len(self.cbdat.scheme.jobs_in_scheme) + 1)
        return scheme    
    
    def updateSchemeJobFromTable(self,job, table_widget, jobName, conf):
        """
        update the job_star_dict with the values of the table_widget
        """
        nRows = table_widget.rowCount()
        nCols = table_widget.columnCount()
        
        for row in range(nRows):
            for col in range(nCols):
                value = table_widget.item(row, col).text()
                if col == 0:
                    original_param_name = conf.get_alias_reverse(jobName, value)
                    if original_param_name != None:
                        # param_name = original_param_name
                        value = original_param_name     
                # insert value at the position defined by the index of the table
                job.dict["joboptions_values"].iloc[row, col] = value
        
        return job
   
        
    

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ui = MainUI()
    ui.show()
    app.exec()
