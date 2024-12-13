import sys,requests,os
import numpy as np
from src.misc.libpdb import pdb
from src.misc.libimVol import processVolume,gaussian_lowpass_mrc
from src.misc.libmask import ellipsoid_mask
from src.gui.libGui import statusMessageBox,messageBox
from src.rw.librw import cbconfig
import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                            QPushButton, QDialog, QHBoxLayout, 
                            QFileDialog, QGridLayout,QInputDialog,QMessageBox)

class SimulateForm(QDialog):
    def __init__(self, main_form):
        super().__init__()
        self.main_form = main_form
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Simulate Form')
        self.setMinimumWidth(600)
        layout = QGridLayout()
        self.setLayout(layout)
        
        self.fields = []
        
        layout.addWidget(QLabel('PDB File:'), 0, 0)
        self.pdb_field = QLineEdit()
        layout.addWidget(self.pdb_field, 0, 1)
        self.fields.append(self.pdb_field)
        
        layout.addWidget(QLabel('Simulation Pixel Size (max 4) (Å):'), 1, 0)
        self.smpixel_size_field = QLineEdit()
        layout.addWidget(self.smpixel_size_field, 1, 1)
        self.fields.append(self.smpixel_size_field)
        
        layout.addWidget(QLabel('Template Pixel Size  (Å):'), 2, 0)
        self.tmpixel_size_field = QLineEdit()
        layout.addWidget(self.tmpixel_size_field, 2, 1)
        self.fields.append(self.tmpixel_size_field)
        
        layout.addWidget(QLabel('Simulation Box Size : (Voxel)'), 3, 0)
        self.smbox_size_field = QLineEdit()
        layout.addWidget(self.smbox_size_field, 3, 1)
        self.fields.append(self.smbox_size_field)
        
        layout.addWidget(QLabel('Template Box Size : (Voxel)'), 4, 0)
        self.tmbox_size_field = QLineEdit()
        layout.addWidget(self.tmbox_size_field, 4, 1)
        self.fields.append(self.tmbox_size_field)
        
        layout.addWidget(QLabel('Resolution (Å):'), 5, 0)
        self.resolution_field = QLineEdit()
        layout.addWidget(self.resolution_field, 5, 1)
        self.fields.append(self.resolution_field)
        
        layout.addWidget(QLabel('Linear scaling of per atom bFactor'), 6, 0)
        self.LinearscalingofperatombFactor = QLineEdit()
        self.LinearscalingofperatombFactor.setText("1") 
        layout.addWidget(self.LinearscalingofperatombFactor, 6, 1)
        self.fields.append(self.LinearscalingofperatombFactor)
        
        layout.addWidget(QLabel('Per atom (xtal) bFactor added to all atoms'), 7, 0)
        self.PeratombFactoraddedtoallatoms = QLineEdit()
        self.PeratombFactoraddedtoallatoms.setText("0")
        layout.addWidget(self.PeratombFactoraddedtoallatoms, 7, 1)
        self.fields.append(self.PeratombFactoraddedtoallatoms)
        
        layout.addWidget(QLabel('Oversample Factor'), 8, 0)
        self.OverSampleFactor =QLineEdit()
        self.OverSampleFactor .setText("4")
        layout.addWidget(self.OverSampleFactor , 8, 1)
        self.fields.append(self.OverSampleFactor)
        
        layout.addWidget(QLabel('Number of Frames per movie'), 9, 0)
        self.numOfFrames = QLineEdit()
        self.numOfFrames.setText("7")
        layout.addWidget(self.numOfFrames , 9, 1)
        self.fields.append(self.numOfFrames )
        
        # Add Simulate button
        GenAndExit_btn = QPushButton('GenAndExit')
        GenAndExit_btn.clicked.connect(self.GenAndExit)
        layout.addWidget(GenAndExit_btn, 10, 0, 1, 2)

    def GenAndExit(self):
        
        if self.pdbCode is None:
            self.pdbCode = "template"
        tag=self.pdbCode+"_apix"+self.tmpixel_size_field.text()+"_ares"+self.resolution_field.text()+"_box"+self.tmbox_size_field.text()
        
        text, ok = QInputDialog.getText(self, 'Tag for template', 'Enter tag:', 
                              QLineEdit.EchoMode.Normal,tag )
        if ok==False:
            return
        
        nameTemplate=text
        nameSim=self.pdbCode+"_apix"+self.smpixel_size_field.text()+"_box"+self.smbox_size_field.text()
        name=os.path.basename(self.pdb_field.text())
        name=os.path.splitext(name)[0]+".mrc"
       
        self.outpath=self.outFold+os.path.sep+nameTemplate+".mrc"
        self.simOutpath=self.outFold+os.path.sep+nameSim+".mrc"
        pixS=float(self.smpixel_size_field.text())
        outBox=float(self.smbox_size_field.text())
        modScaleBF=float(self.LinearscalingofperatombFactor.text())
        modBf=self.PeratombFactoraddedtoallatoms.text()
        oversamp=self.OverSampleFactor.text()
        numOfFrames=self.numOfFrames.text()
        
        self.pdb=pdb(self.pdb_field.text())
        msg=statusMessageBox("Simulating Map: " + self.simOutpath)
        self.pdb.simulateMapFromPDB(self.simOutpath,pixS,outBox,modScaleBF,modBf,oversamp,numOfFrames)
        
        boxTm=float(self.tmbox_size_field.text())
        pixsTm=float(self.tmpixel_size_field.text())
        resTm=float(self.resolution_field.text())
        msg=statusMessageBox("Generating Template from Simulation: (white)" + self.outpath)
        print('boxTm '+ str(boxTm))
        processVolume(self.simOutpath,self.outpath,resTm,invert_contrast=0,voxel_size_angstrom_output=pixsTm,box_size_output=boxTm,voxel_size_angstrom=pixS,
                      voxel_size_angstrom_out_header=pixsTm)
        
        self.outpathBlack=os.path.splitext(self.outpath)[0] + "_black"  + os.path.splitext(self.outpath)[1]
        msg=statusMessageBox("Generating Template from Simulation: (black)" + self.outpath)
        processVolume(self.simOutpath,self.outpathBlack,resTm,invert_contrast=1,voxel_size_angstrom_output=pixsTm,box_size_output=boxTm,voxel_size_angstrom=pixS,
                      voxel_size_angstrom_out_header=pixsTm)
        msg.close()
        self.accept()

class TemplateGen(QDialog):
    def __init__(self):
        import warnings
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        super().__init__()
        self.initUI()
        self.simulate_form = None
        self.framePixs=2.95
        self.minTemplateSize=96
        CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
        self.confPath=CRYOBOOST_HOME + "/config/conf.yaml"
        self.conf=cbconfig(self.confPath)     
        
          
    def initUI(self):
        self.setWindowTitle('Generate Template')
        self.setMinimumWidth(500)
        layout = QGridLayout()
        self.setLayout(layout)
        self.pdbDefaultName="pdb4Template.cif"
        self.pdbCode=None
        
        self.generateOutputColumn(layout)
        self.generatePDBColumn(layout)
        self.generateVolumeColumn(layout)    
 
        exit_form_btn = QPushButton('Exit')
        exit_form_btn.clicked.connect(self.checkAndExit)
        layout.addWidget(exit_form_btn, 7, 0, 1, 3)    
    
    def generateOutputColumn(self,layout):
        
        layout.addWidget(QLabel('Template Pixelsize'), 0, 0)
        self.line_edit_templatePixelSize = QLineEdit()
        self.line_edit_templatePixelSize.setPlaceholderText('pixelsize of template')
        layout.addWidget(self.line_edit_templatePixelSize, 0, 1)
        output_folder_layout = QHBoxLayout()
        output_folder_layout.addWidget(QLabel('OutputFolder'))
        self.line_edit_outputFolder = QLineEdit()
        self.line_edit_outputFolder.setPlaceholderText('Enter outputFolder')
        self.line_edit_outputFolder.setText('tmpOut/aaa')
        output_folder_layout.addWidget(self.line_edit_outputFolder)
        browse_btn_outputFolder = QPushButton('Browse')
        output_folder_layout.addWidget(browse_btn_outputFolder)
        output_folder_widget = QWidget()
        output_folder_widget.setLayout(output_folder_layout)
        layout.addWidget(output_folder_widget, 0, 2) #1, 3)
         
    
    def generatePDBColumn(self,layout):
        
        layout.addWidget(QLabel('PDB File:'), 2, 0) 
        self.line_edit_pdbFile = QLineEdit()
        self.line_edit_pdbFile.setPlaceholderText('Enter PDB file path or ID')
        layout.addWidget(self.line_edit_pdbFile, 2, 1)
        
        button_pdb_layout = QHBoxLayout()
        push_button_browse_pdb = QPushButton('Browse')
        push_button_fetch_pdb = QPushButton('Fetch')        

        push_button_align_pdb = QPushButton('Align')
        push_button_view_pdb = QPushButton('View')
        
        push_button_browse_pdb.clicked.connect(self.browsePdb)
        push_button_fetch_pdb.clicked.connect(self.fetchPdb)
        push_button_align_pdb.clicked.connect(self.alignPdb)
        push_button_view_pdb.clicked.connect(self.viewPdb)
        
        for btn in [push_button_browse_pdb, push_button_fetch_pdb, push_button_align_pdb, push_button_view_pdb]:
            button_pdb_layout.addWidget(btn)
        
        button_widget_pdb = QWidget()
        button_widget_pdb.setLayout(button_pdb_layout)
        layout.addWidget(button_widget_pdb, 2 ,2)
        
    def generateVolumeColumn(self,layout):
        
         # Field 2 with four buttons 4, 0)
        self.LinearscalingofperatombFactor = QLineEdit()
        layout.addWidget(QLabel('Map File:'), 3, 0)
        self.line_edit_mapFile = QLineEdit()
        self.line_edit_mapFile.setPlaceholderText('Enter map file path')
        layout.addWidget(self.line_edit_mapFile, 3, 1)
        
        button_layout2 = QHBoxLayout()
        push_button_browse_map = QPushButton('Browse')
        push_button_simulate_map = QPushButton('Sim from Pdb')
        push_button_basicShape_map = QPushButton('Use basic shape')
        push_button_view_map = QPushButton('View')
         #self.simulate_form.show()
        push_button_browse_map.clicked.connect(self.browseMap)
        push_button_basicShape_map.clicked.connect(self.basicShape)
        push_button_simulate_map.clicked.connect(self.openSimulateForm)
        push_button_view_map.clicked.connect(self.viewMap)
        
        for btn in [push_button_browse_map, push_button_basicShape_map, push_button_simulate_map, push_button_view_map]:
            button_layout2.addWidget(btn)
        
        button_widget2 = QWidget()
        button_widget2.setLayout(button_layout2)
        layout.addWidget(button_widget2, 3, 2)
    
    def viewPdb(self):  
        
        try:
            outputPath = self.line_edit_outputFolder.text() + os.path.sep + self.pdbDefaultName
            self.pdb.writePDB(outputPath, verboseQt=1)
            envStr = self.conf.confdata['local']['Environment']
            call=envStr+';pymol ' + outputPath
            subprocess.Popen(call,shell=True)
        except Exception as e:
            QMessageBox.critical(self, 
                                "Error", 
                                f"An error occurred:\n\nType: {type(e).__name__}\nDetails: {str(e)}")
            print(f"Full error details:\n{type(e).__name__}: {str(e)}")
        
        
    def alignPdb(self):
       
        outFold = self.line_edit_outputFolder.text()
        msg=statusMessageBox("Aligning to principle axis")
        self.pdb.alignToPrincipalAxis()
        msg.update("writing pdb: " + outFold+os.path.sep+self.pdbDefaultName)
        self.pdb.writePDB(outFold+os.path.sep+self.pdbDefaultName)
        self.line_edit_pdbFile.setText(outFold+os.path.sep+self.pdbDefaultName)
        msg.close()
                
       
    
    def browsePdb(self):
        outFold = self.line_edit_outputFolder.text()
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Select PDB/CIF File", 
            "", 
            "PDB Files (*.pdb);(*.cif);All Files (*)"
        )
        if filename:
            msg=statusMessageBox("Reading " + filename)
            self.pdb=pdb(filename)
            msg.update("writing " + outFold+os.path.sep+self.pdbDefaultName)
            self.pdb.writePDB(outFold+os.path.sep+self.pdbDefaultName)
            self.line_edit_pdbFile.setText(outFold+os.path.sep+self.pdbDefaultName)
            msg.close()

    
    def fetchPdb(self):
        outFold = self.line_edit_outputFolder.text()
        pdbCode, ok = QInputDialog.getText(None, 'Enter PDB Code', None)
        
        if not ok or pdbCode=="":
            return
        
        msg=statusMessageBox("Fetching " + pdbCode)
        self.pdb=pdb(pdbCode,outFold)
        if self.pdb.pdbFetchSuccess==-1:
            messageBox("problem", pdbCode + " not found")
            msg.close()
            return
        msg.update("writing pdb: " + outFold+os.path.sep+self.pdbDefaultName)
        self.pdb.writePDB(outFold+os.path.sep+self.pdbDefaultName)
        self.line_edit_pdbFile.setText(outFold+os.path.sep+self.pdbDefaultName)
        self.pdbCode=pdbCode
        msg.close()
        
    def simulatePdb(self):
        self.openSimulateForm() 
    
   
    def browseMap(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Map File", 
            "", 
            "MRC Files (*.mrc);;All Files (*)"
        )
        if filename:
            self.line_edit_mapFile.setText(filename)

    def basicShape(self):
        if self.line_edit_templatePixelSize.text().replace(".","").isdigit()==False:
            messageBox("Problem","Pixelsize not numeric")
            return
        pixS = float(self.line_edit_templatePixelSize.text())
        outFold = self.line_edit_outputFolder.text()
        szStr, ok = QInputDialog.getText(None, 'Enter sz:sy:sz Diameter in Ang', 'Input', text='100:500:100')
        outputName = outFold + os.path.sep + 'ellipsoid_' + szStr.replace(":", "_") + "_apix" + str(pixS) +".mrc"
        szPix = np.array(szStr.split(":"), dtype=float)/pixS   
        offset = 32
        max_size = int(np.ceil(np.max(szPix*1.2) + offset - 1) // offset) * offset
        box_size = int(max_size)
        if box_size<self.minTemplateSize:
            box_size=self.minTemplateSize
        msg=statusMessageBox("Generating Mask: " + outputName)
        ellipsoid_mask(box_size,np.round(szPix/2),np.round(szPix/2),decay_width=0.0, voxel_size=pixS, output_path=outputName)
        outputNameBlack=os.path.splitext(outputName)[0] + "_black"  + os.path.splitext(outputName)[1]
        msg=statusMessageBox("Filtering And Inverting Mask: " + outputNameBlack)
        gaussian_lowpass_mrc(outputName,outputNameBlack,45,invert_contrast=1)
        gaussian_lowpass_mrc(outputName,outputName,45,invert_contrast=0)
        self.line_edit_mapFile.setText(outputNameBlack)
        msg.close()
        
    def viewMap(self):
        try:
            mapName = self.line_edit_mapFile.text()
            # pdbName = os.path.splitext(mapName)[0] + ".cif"
            # pdbName = pdbName.replace("_black.cif",".cif")
            envStr = self.conf.confdata['local']['Environment']
            call=envStr + ';imod '
            if os.path.exists(mapName):
                call+=mapName
                subprocess.Popen(call, shell=True)
            else:
                print("Map file not found")
           
        except Exception as e:
            print(f"Error launching PyMOL: {str(e)}")
            
    def openSimulateForm(self):
        
        if self.line_edit_templatePixelSize.text().replace('.','').isnumeric()==False:
            QMessageBox.critical(self, "Error", "Template Pixel Size must be a number")
            print("in")
            return
        if not hasattr(self, 'pdb') or self.pdb is None:
            QMessageBox.critical(self, "Error", "No PDB file loaded. Please load a PDB file first.")
            return
        
        if self.simulate_form is None:
            self.simulate_form = SimulateForm(self)
        
        self.simulate_form.tmpixel_size_field.setText(self.line_edit_templatePixelSize.text())
        self.simulate_form.tmbox_size_field.setText(str(self.pdb.getOptBoxSize(float(self.line_edit_templatePixelSize.text()),self.minTemplateSize))) 
        if float(self.line_edit_templatePixelSize.text())>4:
            pixFrame=str(self.framePixs)
            self.simulate_form.smpixel_size_field.setText(pixFrame)
            self.simulate_form.smbox_size_field.setText(str(self.pdb.getOptBoxSize(float(pixFrame),self.minTemplateSize))) 
        else:
            self.simulate_form.smpixel_size_field.setText(self.line_edit_templatePixelSize.text())
            self.simulate_form.smbox_size_field.setText(str(self.pdb.getOptBoxSize(float(self.line_edit_templatePixelSize.text()),self.minTemplateSize))) 
            
        self.simulate_form.pdb_field.setText(self.line_edit_pdbFile.text())
        self.simulate_form.resolution_field.setText(str(round(float(self.line_edit_templatePixelSize.text())*2.2)))
        self.simulate_form.outFold=self.line_edit_outputFolder.text()
        self.simulate_form.pdbCode=self.pdbCode
       
        result=self.simulate_form.exec()  # Use 
        if result == QDialog.DialogCode.Accepted:  # Check if OK was clicked
            self.line_edit_mapFile.setText(self.simulate_form.outpathBlack)
            
        
    def checkAndExit(self):
        self.close()
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = TemplateGen()
    ex.show()
    sys.exit(app.exec())