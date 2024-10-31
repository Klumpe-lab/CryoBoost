
import sys
import os
import pandas as pd
import glob,random  
from PyQt6 import QtWidgets
from PyQt6.QtGui import QTextCursor
from PyQt6.uic import loadUi
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QVBoxLayout, QApplication, QMainWindow,QMessageBox,QDialog, QComboBox, QTabWidget, QWidget,QScrollArea ,QCheckBox, QAbstractItemView
from PyQt6.QtCore import Qt
from src.pipe.libpipe import pipe
from src.rw.librw import starFileMeta
from src.misc.system import run_command_async
import subprocess, shutil
from PyQt6.QtCore import QTimer 
import mrcfile
import datetime

current_dir = os.path.dirname(os.path.abspath(__name__))
# change the path to be until src
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

#from lib.functions import get_value_from_tab
from src.gui.libGui import externalTextViewer,browse_dirs,browse_files,checkDosePerTilt,browse_filesOrFolders,change_values,change_bckgrnd,checkGainOptions,get_inputNodesFromSchemeTable,messageBox 
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
        self.adaptWidgetsToJobsInScheme()
        self.genSchemeTable()
        self.system=self.selSystemComponents()
        
        self.groupBox_WorkFlow.setEnabled(False)
        self.groupBox_Setup.setEnabled(False)
        #self.groupBox_Project.setEnabled(False)
        self.tabWidget.setCurrentIndex(0)
        
        if (self.cbdat.args.autoGen or self.cbdat.args.skipSchemeEdit):
            self.makeJobTabsFromScheme()
    
    def adaptWidgetsToJobsInScheme(self):
        
        if "fs_motion_and_ctf" in self.cbdat.scheme.jobs_in_scheme.values:
            self.dropDown_gainRot.clear()  # This will remove all items from the dropdown
            self.dropDown_gainRot.addItem("No transpose")
            self.dropDown_gainRot.addItem("Transpose")
        
         
    def selSystemComponents(self):
        system = type('', (), {})() 
        if shutil.which("zenity") is None:
           system.filebrowser="qt"
        else:   
           system.filebrowser="zenity"
        return system
                
    def initializeDataStrcuture(self,args):
        #custom varibales
        cbdat = type('', (), {})() 
        cbdat.CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
        if args.scheme=="relion_tomo_prep" or args.scheme=="default":      
            cbdat.defaultSchemePath=cbdat.CRYOBOOST_HOME + "/config/Schemes/relion_tomo_prep/"
        if args.scheme=="warp_tomo_prep":
            cbdat.defaultSchemePath=cbdat.CRYOBOOST_HOME + "/config/Schemes/warp_tomo_prep/"
        cbdat.confPath=cbdat.CRYOBOOST_HOME + "/config/conf.yaml"
        cbdat.pipeRunner= None
        cbdat.conf=cbconfig(cbdat.confPath)     
        cbdat.args=args
        if os.path.exists(str(args.proj) +  "/Schemes/" + args.scheme + "/scheme.star"):
            cbdat.scheme=schemeMeta(args.proj +  "/Schemes/" + args.scheme )
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
        self.line_path_mdocs.textChanged.connect(self.updateTomogramsForTraining)
        self.line_path_gain.textChanged.connect(self.setPathGainToJobTap)
        self.line_path_new_project.textChanged.connect(self.updateLogViewer)
        self.line_path_crImportPrefix.textChanged.connect(self.updateTomogramsForTraining)
        self.dropDown_gainRot.activated.connect(self.setGainRotToJobTap)
        self.dropDown_gainFlip.activated.connect(self.setGainFlipJobTap)
        self.textEdit_pixelSize.textChanged.connect(self.setPixelSizeToJobTap)
        self.textEdit_dosePerTilt.textChanged.connect(self.setdosePerTiltToJobTap)
        self.textEdit_nomTiltAxis.textChanged.connect(self.setTiltAxisToJobTap)
        self.textEdit_invertHand.textChanged.connect(self.setInvertHandToJobTap)
        self.textEdit_eerFractions.textChanged.connect(self.setEerFractionsToJobTap)
        self.textEdit_areTomoSampleThick.textChanged.connect(self.setAreTomoSampleThickToJobTap)
        
        self.textEdit_areTomoPatch.textChanged.connect(self.setAreTomoPatchToJobTap)
        self.textEdit_algRescaleTilts.textChanged.connect(self.setAlgRescaleTiltsJobTap)
        
        
        self.textEdit_ImodPatchSize.textChanged.connect(self.setImodPatchSizeToJobTap)
        self.textEdit_imodPatchOverlap.textChanged.connect(self.setImodPatchOverlapToJobTap)
        
        self.textEdit_refineTiltAxisNrTomo.textChanged.connect(self.setTiltAxisRefineParamToJobTap)
        self.textEdit_refineTiltAxisIter.textChanged.connect(self.setTiltAxisRefineParamToJobTap)
        self.dropDown_doRefineTiltAxis.activated.connect(self.setTiltAxisRefineParamToJobTap)
        
        self.dropDown_tomoAlignProgram.activated.connect(self.setTomoAlignProgramToJobTap)
        self.btn_openWorkFlowLog.clicked.connect(self.openExtLogViewerWorkFlow)
        self.btn_openWorkFlowLog.clicked.connect(self.openExtLogViewerWorkFlow)
        self.btn_openJobOutpuLog.clicked.connect(self.openExtLogViewerJobOutput)
        self.btn_openJobErrorLog.clicked.connect(self.openExtLogViewerJobError)
        #self.textBrowser_workFlow.clicked.connect(self.openExtLogViewer) 
        self.btn_browse_movies.clicked.connect(self.browsePathMovies)
        self.btn_browse_mdocs.clicked.connect(self.browsePathMdocs)
        self.btn_browse_denoisingModel.clicked.connect(self.browseDenoisingModel)
        self.textEdit_tomoForDenoiseTrain.textChanged.connect(self.setTomoForDenoiseTrainToJobTap)
        self.textEdit_pathDenoiseModel.textChanged.connect(self.setPathDenoiseModelToJobTap)
        self.textEdit_modelForFilterTilts.textChanged.connect(self.setmodelForFilterTiltsToJobTap)
        self.textEdit_probThr.textChanged.connect(self.setProbThrToJobTap)
        self.btn_browse_gain.clicked.connect(self.browsePathGain)
        self.btn_browse_autoPrefix.clicked.connect(self.generatePrefix)
        self.btn_use_movie_path.clicked.connect(self.mdocs_use_movie_path)
        self.dropDown_config.activated.connect(self.loadConfig)
        self.dropDown_probThrBehave.activated.connect(self.setProbBehaveToJobTab)
        self.btn_browse_target.clicked.connect(self.browsePathTarget)
        self.btn_genProject.clicked.connect(self.generateProject)
        self.btn_updateWorkFlow.clicked.connect(self.updateWorkflow)    
        self.btn_importData.clicked.connect(self.importData)
        self.btn_startWorkFlow.clicked.connect(self.startWorkflow)
        self.btn_showClusterStatus.clicked.connect(self.showClusterStatus)
        self.checkBox_openRelionGui.stateChanged.connect(self.openRelionGui)
        self.btn_stopWorkFlow.clicked.connect(self.stopWorkflow)
        self.btn_unlockWorkFlow.clicked.connect(self.unlockWorkflow)
        self.btn_resetWorkFlow.clicked.connect(self.resetWorkflow)
        self.btn_resetWorkFlowHead.clicked.connect(self.resetWorkflowHead)
        self.dropDown_config.addItem("Choose Microscope Set-Up")
        self.dropDown_nrNodes.activated.connect(self.setNrNodesToJobTap)
        self.dropDown_partitionName.activated.connect(self.setNrNodesToJobTap)
        self.checkBox_shareNodes.stateChanged.connect(self.setNrNodesToJobTap)
        self.dropDown_nrNodes.setCurrentIndex(2)
        self.dropDown_jobSize.setCurrentIndex(1)
        self.dropDown_jobSize.activated.connect(self.setNrNodesFromJobSize)
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
        if (self.cbdat.args.pixS != None):
             self.textEdit_pixelSize.setText(self.cbdat.args.pixS)
        if (self.cbdat.args.gain != None):
            if not os.path.isfile(self.cbdat.args.gain):
                raise Exception("file not found: "+self.cbdat.args.gain)
            if not os.path.isabs(self.cbdat.args.gain):
                self.line_path_gain.setText(os.path.abspath(self.cbdat.args.gain)) 
            else:
                self.line_path_gain.setText(self.cbdat.args.gain)
             
        self.groupBox_WorkFlow.setEnabled(True)
        self.groupBox_Setup.setEnabled(True)
        self.groupBox_Project.setEnabled(True)
        
        if "denoisetrain" in self.cbdat.scheme.jobs_in_scheme.values  or "denoisepredict" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"generate_split_tomograms": "Yes" }
            self.setParamsDictToJobTap(params_dict)
              
        
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
        
        if "ctffind" in self.cbdat.scheme.jobs_in_scheme.values:
            thoneRingFade = self.cbdat.scheme.getJobOptions("ctffind").loc[
                             self.cbdat.scheme.getJobOptions("ctffind")["rlnJobOptionVariable"] == "exp_factor_dose",
                             "rlnJobOptionValue"
                             ].values[0]  
            if self.textEdit_dosePerTilt.toPlainText().isnumeric():
                checkDosePerTilt(self.line_path_mdocs.text(),float(self.textEdit_dosePerTilt.toPlainText()),float(thoneRingFade))
        
        self.setParamsDictToJobTap(params_dict)
    #self.textEdit_tomoForDenoiseTrain.textChanged.connect(self.setTomoForDenoiseTrainToJobTap)
    #self.textEdit_pathDenoiseModel.textChanged.connect(self.setPathDenoiseModelToJobTap)
    
    def showClusterStatus(self):
        
        sshStr=self.cbdat.conf.confdata['submission'][0]['SshCommand']
        headNode=self.cbdat.conf.confdata['submission'][0]['HeadNode']
        command=sshStr + " " + headNode + ' "' + "sinfo -o '%P %.6D %.6t' | sort -k3 | grep -v 'PAR'" + '"'
        print(command)
        proc=subprocess.Popen(command,shell=True ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        stdout, stderr = proc.communicate()
        
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setWindowTitle('Information')
        msg_box.setText(stdout)
        msg_box.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg_box.resize(2000, 400) 
        msg_box.exec()
       
    def setTomoForDenoiseTrainToJobTap(self):
  
        params_dict = {"tomograms_for_training": self.textEdit_tomoForDenoiseTrain.toPlainText() }
        self.setParamsDictToJobTap(params_dict)
    
    def setPathDenoiseModelToJobTap(self):
  
        params_dict = {"care_denoising_model": self.textEdit_pathDenoiseModel.toPlainText() }
        self.setParamsDictToJobTap(params_dict)
    
    def setmodelForFilterTiltsToJobTap(self):
        
        params_dict = {"param1_value": self.textEdit_modelForFilterTilts.toPlainText() }
        self.setParamsDictToJobTap(params_dict,applyToJobs="filtertilts")
    
    def setProbThrToJobTap(self):
        
        params_dict = {"param5_value": self.textEdit_probThr.toPlainText() }
        self.setParamsDictToJobTap(params_dict,applyToJobs="filtertilts")
    
    def setProbBehaveToJobTab(self):
        
        params_dict = {"param6_value": self.dropDown_probThrBehave.currentText() }
        self.setParamsDictToJobTap(params_dict,applyToJobs="filtertilts")
    
    
    def updateTomogramsForTraining(self):
        wk_mdocs=self.line_path_mdocs.text()
        mdocList=glob.glob(wk_mdocs)
        pref=self.line_path_crImportPrefix.text()
        mdocList=[mdoc for mdoc in mdocList]# if pref in mdoc]
        tomoNames=[pref+os.path.splitext(os.path.basename(path))[0].replace(".st","") for path in mdocList]
        if len(tomoNames)<3:
            nTomo=len(tomoNames)
        else:
            nTomo=3
        tomoNamesSub=random.sample(tomoNames, k=nTomo)
        tomoStr=":".join(tomoNamesSub)
        print("updating...")
        self.textEdit_tomoForDenoiseTrain.setText(tomoStr)
       
    def setPixelSizeToJobTap(self):
        params_dict = {"angpix": self.textEdit_pixelSize.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["importmovies"])      
     
    def setdosePerTiltToJobTap(self):
        params_dict = {"dose_rate": self.textEdit_dosePerTilt.toPlainText()} 
        if "ctffind" in self.cbdat.scheme.jobs_in_scheme.values:
             thoneRingFade = self.cbdat.scheme.getJobOptions("ctffind").loc[
                             self.cbdat.scheme.getJobOptions("ctffind")["rlnJobOptionVariable"] == "exp_factor_dose",
                             "rlnJobOptionValue"
                             ].values[0]  
            
        if (self.textEdit_dosePerTilt.toPlainText().isnumeric()):
            checkDosePerTilt(self.line_path_mdocs.text(),float(self.textEdit_dosePerTilt.toPlainText()),float(thoneRingFade))
        
        self.setParamsDictToJobTap(params_dict,["importmovies"])       
    
    def setTiltAxisToJobTap(self):
        params_dict = {"tilt_axis_angle": self.textEdit_nomTiltAxis.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["importmovies"]) 
    
    def setPathGainToJobTap(self):
        params_dict = {"fn_gain_ref": self.line_path_gain.text()} 
        self.setParamsDictToJobTap(params_dict,["motioncorr"]) 
        params_dict = {"param2_value": self.line_path_gain.text()} 
        self.setParamsDictToJobTap(params_dict,["fs_motion_and_ctf"]) 
        
    
    def setGainRotToJobTap(self):
        if "motioncorr" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"gain_rot": self.dropDown_gainRot.currentText()} 
            checkGainOptions(self.line_path_gain.text(),self.dropDown_gainRot.currentText(),self.dropDown_gainFlip.currentText())
            self.setParamsDictToJobTap(params_dict,["motioncorr"]) 
        if "fs_motion_and_ctf" in self.cbdat.scheme.jobs_in_scheme.values:   
            selFlip=self.dropDown_gainFlip.currentText()
            selRot=self.dropDown_gainRot.currentText()
            gainOpString=""
            if selFlip=="Flip upside down (1)":
                gainOpString=gainOpString+"flip_y"
            if selFlip=="Flip left to right (2)":
                if gainOpString!="":
                    gainOpString=gainOpString+":"
                gainOpString=gainOpString+"flip_x"
            if selRot=="Transpose":
                if gainOpString!="":
                    gainOpString=gainOpString+":"
                gainOpString=gainOpString+"transpose"
            
            #checkGainOptions(self.line_path_gain.text(),self.dropDown_gainRot.currentText(),self.dropDown_gainFlip.currentText())
            params_dict = {"param3_value": gainOpString}
            self.setParamsDictToJobTap(params_dict,["fs_motion_and_ctf"]) 
        
        
    def setGainFlipJobTap(self):
        if "motioncorr" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"gain_flip": self.dropDown_gainFlip.currentText()} 
            checkGainOptions(self.line_path_gain.text(),self.dropDown_gainRot.currentText(),self.dropDown_gainFlip.currentText())
            self.setParamsDictToJobTap(params_dict,["motioncorr"]) 
        if "fs_motion_and_ctf" in self.cbdat.scheme.jobs_in_scheme.values:   
            
            selFlip=self.dropDown_gainFlip.currentText()
            selRot=self.dropDown_gainRot.currentText()
            gainOpString=""
            if selFlip=="Flip upside down (1)":
                gainOpString=gainOpString+"flip_y"
            if selFlip=="Flip left to right (2)":
                if gainOpString!="":
                    gainOpString=gainOpString+":"
                gainOpString=gainOpString+"flip_x"
            if selRot=="Transpose":
                if gainOpString!="":
                    gainOpString=gainOpString+":"
                gainOpString=gainOpString+"transpose"
            
            #checkGainOptions(self.line_path_gain.text(),self.dropDown_gainRot.currentText(),self.dropDown_gainFlip.currentText())
            params_dict = {"param3_value": gainOpString}
            print(params_dict)
            self.setParamsDictToJobTap(params_dict,["fs_motion_and_ctf"]) 
            
    def setInvertHandToJobTap(self):
        params_dict = {"flip_tiltseries_hand": self.textEdit_invertHand.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["importmovies"]) 
    
    def setEerFractionsToJobTap(self):
        if "motioncorr" in self.cbdat.scheme.jobs_in_scheme.values: 
            params_dict = {"eer_grouping": self.textEdit_eerFractions.toPlainText()}
            self.setParamsDictToJobTap(params_dict,["motioncorr"]) 
        if "fs_motion_and_ctf" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"param1_value": self.textEdit_eerFractions.toPlainText()}
            self.setParamsDictToJobTap(params_dict,["fs_motion_and_ctf"]) 
            
    def setAreTomoSampleThickToJobTap(self):
        
        params_dict = {"aretomo_thickness": self.textEdit_areTomoSampleThick.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["aligntilts"]) 
        
        if "aligntiltsWarp" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"param6_value": self.textEdit_areTomoSampleThick.toPlainText()}
            self.setParamsDictToJobTap(params_dict,["aligntiltsWarp"]) 
    #self.textEdit_areTomoPatch.textChanged.connect(self.setAreTomoPatchToJobTap)
    #self.textEdit_algRescaleTilts.textChanged.connect(self.setAlgRescaleTiltsJobTap)
    def setAreTomoPatchToJobTap(self):
        
        if "aligntiltsWarp" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"other_args": self.textEdit_areTomoPatch.toPlainText()}
            self.setParamsDictToJobTap(params_dict,["aligntiltsWarp"]) 
        
    def setAlgRescaleTiltsJobTap(self):
        
        if "aligntiltsWarp" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"param8_value": self.textEdit_algRescaleTilts.toPlainText()}
            self.setParamsDictToJobTap(params_dict,["aligntiltsWarp"]) 
        
            
    # def setAreTomoSampleThickToJobTap(self):
    #     params_dict = {"aretomo_thickness": self.textEdit_areTomoSampleThick.toPlainText()} 
    #     self.setParamsDictToJobTap(params_dict,["aligntilts"]) 
    
    def setTiltAxisRefineParamToJobTap(self):
        if "aligntiltsWarp" in self.cbdat.scheme.jobs_in_scheme.values:
            if self.dropDown_doRefineTiltAxis.currentText() == "False":
                refineStr = "0:0"
            else:
                refineStr = self.textEdit_refineTiltAxisIter.toPlainText()+":"+self.textEdit_refineTiltAxisNrTomo.toPlainText()
            params_dict = {"param9_value": refineStr}
            self.setParamsDictToJobTap(params_dict,["aligntiltsWarp"]) 
    
    def setImodPatchSizeToJobTap(self):
        params_dict = {"patch_size": self.textEdit_ImodPatchSize.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["aligntilts"]) 
        if "aligntiltsWarp" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"param7_value": self.textEdit_ImodPatchSize.toPlainText()+
                           ":"+self.textEdit_imodPatchOverlap.toPlainText()
                           }
            self.setParamsDictToJobTap(params_dict,["aligntiltsWarp"]) 
    
    def setImodPatchOverlapToJobTap(self):
        params_dict = {"patch_overlap": self.textEdit_imodPatchOverlap.toPlainText()} 
        self.setParamsDictToJobTap(params_dict,["aligntilts"]) 
        if "aligntiltsWarp" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"param7_value": self.textEdit_ImodPatchSize.toPlainText()+
                           ":"+self.textEdit_imodPatchOverlap.toPlainText()
                           }
            self.setParamsDictToJobTap(params_dict,["aligntiltsWarp"]) 
        
        
    def setNrNodesFromJobSize(self):
       
       if self.dropDown_jobSize.currentText().strip()=="small":
            self.dropDown_nrNodes.setCurrentText("1")
       if self.dropDown_jobSize.currentText().strip()=="medium":
            self.dropDown_nrNodes.setCurrentText("3") 
       if self.dropDown_jobSize.currentText().strip()=="large":
            self.dropDown_nrNodes.setCurrentText("5") 
       
       self.setNrNodesToJobTap() 
            
    def setTomoAlignProgramToJobTap(self):
        
        programSelected=self.dropDown_tomoAlignProgram.currentText()
        if (programSelected=="Imod"):
            params_dictAre = {"do_aretomo": "No"}
            params_dictImod = {"do_imod_patchtrack": "Yes"}
        
        if (programSelected=="Aretomo"):
            params_dictAre = {"do_aretomo": "Yes"}
            params_dictImod = {"do_imod_patchtrack": "No"}
        
        self.setParamsDictToJobTap(params_dictAre,["aligntilts"])
        self.setParamsDictToJobTap(params_dictImod,["aligntilts"])
        if "aligntiltsWarp" in self.cbdat.scheme.jobs_in_scheme.values:
            params_dict = {"param5_value": programSelected}
            self.setParamsDictToJobTap(params_dict,["aligntiltsWarp"]) 
        
        
    def setNrNodesToJobTap(self):
       
        nrNodes=int(self.dropDown_nrNodes.currentText())
        partion=self.dropDown_partitionName.currentText()
        shareNodes=self.checkBox_shareNodes.isChecked()
        for job in self.cbdat.scheme.jobs_in_scheme:
            comDict=self.cbdat.conf.getJobComputingParams([job,nrNodes,partion],shareNodes)
            if (comDict is not None):
                self.setParamsDictToJobTap(comDict,applyToJobs=job)
         
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
            #print(current_tab in applyToJobs)
            if current_tab in applyToJobs:
                index_import = self.cbdat.scheme.jobs_in_scheme[self.cbdat.scheme.jobs_in_scheme == current_tab].index
                self.tabWidget.setCurrentIndex(index_import.item())
                table_widget = self.tabWidget.currentWidget().findChild(QTableWidget)
                change_values(table_widget, params_dict, self.cbdat.scheme.jobs_in_scheme,self.cbdat.conf)
        self.tabWidget.setCurrentIndex(0)
    
    
    def browsePathMovies(self):
        
        #browse_files(self.line_path_movies)
        targetFold=os.getcwd()
        dirName=browse_dirs(self.line_path_movies,targetFold,self.system.filebrowser)
        if glob.glob(dirName+"*.tif"):
            self.line_path_movies.setText(dirName + "*.tif")
        if glob.glob(dirName+"*.tiff"):
            self.line_path_movies.setText(dirName + "*.tiff")
        if glob.glob(dirName+"*.eer"):
            self.line_path_movies.setText(dirName + "*.eer")  
        
    def browsePathMdocs(self):
        targetFold=os.getcwd()
        dirName=browse_dirs(None,targetFold,self.system.filebrowser)
        if glob.glob(dirName+"*.mdoc"):
            self.line_path_mdocs.setText(dirName + "*.mdoc")

    def browsePathGain(self):
        browse_files(self.line_path_gain,self.system.filebrowser)
    
    def browseDenoisingModel(self):
        browse_files(self.textEdit_pathDenoiseModel,self.system.filebrowser)

    def generatePrefix(self):
       current_datetime = datetime.datetime.now()
       prefix=current_datetime.strftime("%Y-%m-%d-%H-%M-%S_")
       self.line_path_crImportPrefix.setText(prefix)
        
    def mdocs_use_movie_path(self):
        movieP=self.line_path_movies.text()
        mpRoot,ext= os.path.splitext(movieP)
        self.line_path_mdocs.setText(mpRoot+".mdoc")

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
        
        self.cbdat.pipeRunner.runScheme()
        
    def openRelionGui(self):
        
        if self.checkPipeRunner()==False:
            self.checkBox_openRelionGui.setChecked(False)
            return
        
        if self.checkBox_openRelionGui.isChecked():
            self.cbdat.pipeRunner.openRelionGui()    
         
    
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
        logMid=self.cbdat.scheme.scheme_star.dict["scheme_general"]["rlnSchemeName"].replace("Schemes/","").replace("/","")
        logfile_path=self.line_path_new_project.text()+os.path.sep + logMid +".log"
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
            log_contentOut=[]
            with open(logOut, 'r') as log_file:
                for line in log_file:
                   cleaned_line = self.process_backspaces(line).strip()
                   if (cleaned_line):
                        log_contentOut.append(cleaned_line)
                if len(log_contentOut) > 200:
                    log_contentOut=log_contentOut[-200:]

                log_contentOutStr= "\n".join(log_contentOut)
                self.textBrowserJobsOut.setText(log_contentOutStr)
                           
            with open(logError, 'r') as log_fileError:
                log_contentError = log_fileError.readlines()
                if len(log_contentError) > 200:
                     log_contentError=log_contentError[-200:]
                
                if self.checkBox_jobErrroShowWarning.isChecked()==False:
                    log_contentError = [line for line in log_contentError if "warning" not in line.lower() and "warn" not in line.lower()]
                    
                log_contentErrorStr= "\n".join(log_contentError)
                self.textBrowserJobsError.setText(log_contentErrorStr)    
        except Exception as e:
            self.textBrowserJobsOut.setText(f"Logfile not available your job is probably waiting\nCheck queue") #{e})
        self.textBrowserJobsOut.moveCursor(QTextCursor.MoveOperation.End) 
        self.textBrowserJobsError.moveCursor(QTextCursor.MoveOperation.End)
    
    
    def process_backspaces(self,line):
        
        result = []
        for char in line:
            if char == '\b':  # '\b' is the backspace character in Python
                if result:
                    result.pop()  # Remove the last character in the result
            else:
                result.append(char)
        return ''.join(result)
    
    
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
        defPath=os.getcwd()   
        browse_dirs(self.line_path_new_project,defPath,self.system.filebrowser)
       

    def updateLogViewer(self):
        print("logViewer updated")
        logMid=self.cbdat.scheme.scheme_star.dict["scheme_general"]["rlnSchemeName"].replace("Schemes/","").replace("/","")
        logfile_path=self.line_path_new_project.text()+ os.path.sep + logMid +".log"
        if hasattr(self, 'timer') and self.timer.isActive():
            self.timer.stop()  
        if not hasattr(self, 'timer'):
            self.timer = QTimer(self)
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.view_log_file(logfile_path))
        self.timer.start(4000)  # Updat
    
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
        #pipeRunner.scheme.schemeFilePath=args.proj +  "/Schemes/relion_tomo_prep/scheme.star"
        self.cbdat.pipeRunner=pipeRunner
        
    def updateWorkflow(self):
        
        if self.checkPipeRunner()==False:
            return
        scheme=self.cbdat.scheme
        scheme=self.updateSchemeFromJobTabs(scheme,self.tabWidget)
        scheme.scheme_star=starFileMeta(self.cbdat.pipeRunner.scheme.schemeFilePath)
        self.cbdat.scheme=scheme
        self.cbdat.pipeRunner.scheme=scheme
        self.cbdat.pipeRunner.writeScheme()
        
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