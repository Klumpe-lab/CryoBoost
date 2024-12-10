import sys,requests,os
import numpy as np
from src.misc.libpdb import pdb
from src.misc.libmask import ellipsoid_mask
from libGui import statusMessageBox



import subprocess
from PyQt6.QtWidgets import (QApplication, QWidget, QLabel, QLineEdit, 
                            QPushButton, QVBoxLayout, QHBoxLayout, 
                            QFileDialog, QGridLayout,QInputDialog,QMessageBox)

class SimulateForm(QWidget):
    def __init__(self, main_form):
        super().__init__()
        self.main_form = main_form
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Simulate Form')
        self.setMinimumWidth(400)
        layout = QGridLayout()
        self.setLayout(layout)
       
        self.fields = []
        
        layout.addWidget(QLabel('PDB File:'), 0, 0)
        self.pdb_field = QLineEdit()
        layout.addWidget(self.pdb_field, 0, 1)
        self.fields.append(self.pdb_field)
        
        layout.addWidget(QLabel('Pixel Size  (Å):'), 1, 0)
        self.pixel_size_field = QLineEdit()
        layout.addWidget(self.pixel_size_field, 1, 1)
        self.fields.append(self.pixel_size_field)
        
        layout.addWidget(QLabel('Box Size: (Voxel)'), 2, 0)
        self.box_size_field = QLineEdit()
        layout.addWidget(self.box_size_field, 2, 1)
        self.fields.append(self.box_size_field)
        
        layout.addWidget(QLabel('Resolution (Å):'), 3, 0)
        self.resolution_field = QLineEdit()
        layout.addWidget(self.resolution_field, 3, 1)
        self.fields.append(self.resolution_field)
        
        layout.addWidget(QLabel('Linear scaling of per atom bFactor'), 4, 0)
        self.LinearscalingofperatombFactor = QLineEdit()
        self.LinearscalingofperatombFactor.setText("1") 
        layout.addWidget(self.LinearscalingofperatombFactor, 4, 1)
        self.fields.append(self.LinearscalingofperatombFactor)
        
        layout.addWidget(QLabel('Per atom (xtal) bFactor added to all atoms'), 5, 0)
        self.PeratombFactoraddedtoallatoms = QLineEdit()
        self.PeratombFactoraddedtoallatoms.setText("0")
        layout.addWidget(self.PeratombFactoraddedtoallatoms, 5, 1)
        self.fields.append(self.PeratombFactoraddedtoallatoms)
        
        layout.addWidget(QLabel('Oversample Factor'), 6, 0)
        self.OverSampleFactor =QLineEdit()
        self.OverSampleFactor .setText("2")
        layout.addWidget(self.OverSampleFactor , 6, 1)
        self.fields.append(self.OverSampleFactor)
        
        layout.addWidget(QLabel('Number of Frames per movie'), 7, 0)
        self.numOfFrames = QLineEdit()
        self.numOfFrames.setText("7")
        layout.addWidget(self.numOfFrames , 7, 1)
        self.fields.append(self.numOfFrames )
        
        # Add Simulate button
        GenAndExit_btn = QPushButton('GenAndExit')
        GenAndExit_btn.clicked.connect(self.GenAndExit)
        layout.addWidget(GenAndExit_btn, 7, 0, 1, 2)

    def GenAndExit(self):
        
        text, ok = QInputDialog.getText(self, 'Tag Input', 'Enter tag:', 
                              QLineEdit.EchoMode.Normal, 'default_tag')
        
        name=os.path.basename(self.pdb_field.text())
        name=os.path.splitext(name)[0]+".mrc"
        name=text
        outpath=self.outFold+os.path.sep+name
        pixS=float(self.pixel_size_field.text())
        outBox=float(self.box_size_field.text())
        modScaleBF=float(self.LinearscalingofperatombFactor.text())
        modBf=self.PeratombFactoraddedtoallatoms.text()
        oversamp=self.OverSampleFactor.text()
        numOfFrames=self.numOfFrames.text()
        
        
        self.pdb=pdb(self.pdb_field.text())
        self.pdb.simulateMapFromPDB(outpath,pixS,outBox,modScaleBF,modBf,oversamp,numOfFrames)
        self.close()

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.simulate_form = None

    def initUI(self):
        self.setWindowTitle('Generate Template')
        self.setMinimumWidth(400)
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
        self.templatePixelSize = QLineEdit()
        self.templatePixelSize.setPlaceholderText('pixelsize of template')
        layout.addWidget(self.templatePixelSize, 0, 1)
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
        
         # Field 2 with four buttons
        layout.addWidget(QLabel('Map File:'), 3, 0)
        self.line_edit_mapFile = QLineEdit()
        self.line_edit_mapFile.setPlaceholderText('Enter map file path')
        layout.addWidget(self.line_edit_mapFile, 3, 1)
        
        button_layout2 = QHBoxLayout()
        push_button_browse_map = QPushButton('Browse')
        push_button_simulate_map = QPushButton('Sim from Pdb')
        push_button_basicShape_map = QPushButton('Use basic shape')
        push_button_view_map = QPushButton('View')
        
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
    
        #subprocess.Popen(['chimera', self.pdbFile.text()])
        outputPath=self.line_edit_outputFolder.text()+os.path.sep+self.pdbDefaultName
        self.pdb.writePDB(outputPath,verboseQt=1)
        subprocess.Popen(['pymol', outputPath])
        
        
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
        
        msg=statusMessageBox("Fetching " + pdbCode)
        self.pdb=pdb(pdbCode,outFold)
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
        pass
        
    def viewMap(self):
        pass
        
    
    def openSimulateForm(self):
        if self.simulate_form is None:
            self.simulate_form = SimulateForm(self)
        self.simulate_form.pixel_size_field.setText(self.templatePixelSize.text())
        self.simulate_form.pdb_field.setText(self.line_edit_pdbFile.text())
        self.simulate_form.resolution_field.setText(str(float(self.templatePixelSize.text())*2))
        self.simulate_form.box_size_field.setText(str(self.pdb.getOptBoxSize(float(self.templatePixelSize.text())))) 
        self.simulate_form.outFold=self.line_edit_outputFolder.text()
       
        self.simulate_form.show()
    
    def checkAndExit(self):
        self.close()
    
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())