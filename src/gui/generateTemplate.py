import sys,requests,os
import numpy as np
from Bio import PDB
from Bio.PDB.PDBParser import PDBParser
from Bio.PDB.Structure import Structure
from Bio.PDB.Atom import Atom

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
        
        layout.addWidget(QLabel('Pixel Size:'), 1, 0)
        self.pixel_size_field = QLineEdit()
        layout.addWidget(self.pixel_size_field, 1, 1)
        self.fields.append(self.pixel_size_field)
        
        layout.addWidget(QLabel('Resolution (Å):'), 2, 0)
        self.resolution_field = QLineEdit()
        layout.addWidget(self.resolution_field, 2, 1)
        self.fields.append(self.resolution_field)
        
        layout.addWidget(QLabel('Box Size:'), 3, 0)
        self.box_size_field = QLineEdit()
        layout.addWidget(self.box_size_field, 3, 1)
        self.fields.append(self.box_size_field)
        
        layout.addWidget(QLabel('Center'), 4, 0)
        self.center_field = QLineEdit()
        self.center_field.setText("True") 
        layout.addWidget(self.center_field, 4, 1)
        self.fields.append(self.center_field)
        
        layout.addWidget(QLabel('Chains'), 5, 0)
        self.chains_field = QLineEdit()
        self.chains_field.setText("None")
        layout.addWidget(self.chains_field, 5, 1)
        self.fields.append(self.chains_field)
        
        layout.addWidget(QLabel('SymFull'), 6, 0)
        self.sym_full_field =QLineEdit()
        self.sym_full_field .setText("None")
        layout.addWidget(self.sym_full_field , 6, 1)
        self.fields.append(self.sym_full_field)
        
        layout.addWidget(QLabel('Addpdbfactor'), 7, 0)
        self.add_pdb_factor_field  = QLineEdit()
        layout.addWidget(self.add_pdb_factor_field , 7, 1)
        self.fields.append(self.add_pdb_factor_field )
        
        # Add Simulate button
        GenAndExit_btn = QPushButton('GenAndExit')
        GenAndExit_btn.clicked.connect(self.GenAndExit)
        layout.addWidget(GenAndExit_btn, 7, 0, 1, 2)

    def GenAndExit(self):
        print("Simulating with parameters:")
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

       
        layout.addWidget(QLabel('OutputFolder'), 0, 0)
        self.outputFolder = QLineEdit()
        self.outputFolder.setPlaceholderText('Enter outputFolder')
        self.outputFolder.setText('tmpOut/testTmp')
        layout.addWidget(self.outputFolder, 0, 1)
        button_layout_ouputFolder = QHBoxLayout()
        browse_btn_outputFolder = QPushButton('Browse')  
        button_layout_ouputFolder.addWidget(browse_btn_outputFolder)
        button_widget1 = QWidget()
        button_widget1.setLayout(button_layout_ouputFolder)
        layout.addWidget(button_widget1, 0, 2)
        
        
        layout.addWidget(QLabel('Template Pixelsize'), 1, 0)
        self.templatePixelSize = QLineEdit()
        self.templatePixelSize.setPlaceholderText('pixelsize of template')
        layout.addWidget(self.templatePixelSize, 1, 1)
    
        
        # Field 1 with four buttons
        layout.addWidget(QLabel('PDB File:'), 2, 0) 
        self.pdbFile = QLineEdit()
        self.pdbFile.setPlaceholderText('Enter PDB file path or ID')
        self.pdbFile.textChanged.connect(self.pdbFileChanged)
        layout.addWidget(self.pdbFile, 2, 1)
        
        button_pdb_layout = QHBoxLayout()
        browse_pdb = QPushButton('Browse')
        fetch_pdb = QPushButton('Fetch')
        align_pdb = QPushButton('Align')
        view_pdb = QPushButton('View')
        
        browse_pdb.clicked.connect(self.browsePdb)
        fetch_pdb.clicked.connect(self.fetchPdb)
        align_pdb.clicked.connect(self.alignPdb)
        view_pdb.clicked.connect(self.viewPdb)
        
        for btn in [browse_pdb, fetch_pdb, align_pdb, view_pdb]:
            button_pdb_layout.addWidget(btn)
        
        
        button_widget_pdb = QWidget()
        button_widget_pdb.setLayout(button_pdb_layout)
        layout.addWidget(button_widget_pdb, 2 ,2)

        # Field 2 with four buttons
        layout.addWidget(QLabel('Map File:'), 3, 0)
        self.field2 = QLineEdit()
        self.field2.setPlaceholderText('Enter map file path')
        layout.addWidget(self.field2, 3, 1)
        
        button_layout2 = QHBoxLayout()
        browse_btn2 = QPushButton('Browse')
        simulate_btn2 = QPushButton('Sim from Pdb')
        fetch_btn2 = QPushButton('Use basic shape')
        view_btn2 = QPushButton('View')
        
        browse_btn2.clicked.connect(self.browseFiles2)
        fetch_btn2.clicked.connect(lambda: self.fetch(2))
        simulate_btn2.clicked.connect(self.openSimulateForm)
        view_btn2.clicked.connect(lambda: self.view(2))
        
        for btn in [browse_btn2, fetch_btn2, simulate_btn2, view_btn2]:
            button_layout2.addWidget(btn)
        
        button_widget2 = QWidget()
        button_widget2.setLayout(button_layout2)
        layout.addWidget(button_widget2, 3, 2)
        
        exit_form_btn = QPushButton('Exit')
        exit_form_btn.clicked.connect(self.openSimulateForm)
        layout.addWidget(exit_form_btn, 7, 0, 1, 3)    
    
    def viewPdb(self):
        #subprocess.Popen(['chimera', self.pdbFile.text()])
        subprocess.Popen(['pymol', self.pdbFile.text()])
        
        
    def alignPdb(self):
        parser = PDB.PDBParser()
        structure = parser.get_structure('pixel_size_fieldname',  self.pdbFile.text())

        coords = []
        for atom in structure.get_atoms():
            coords.append(atom.get_coord())
        coords = np.array(coords)

        mean = np.mean(coords, axis=0)
        coords_centered = coords - mean
        cov = np.cov(coords_centered.T)
        evals, evecs = np.linalg.eigh(cov)

        sort_idx = np.argsort(evals)[::-1]
        evecs = evecs[:, sort_idx]
        coords_aligned = np.dot(coords_centered, evecs)

        for atom, new_coord in zip(structure.get_atoms(), coords_aligned + mean):
            atom.set_coord(new_coord)

        io = PDB.PDBIO()
        io.set_structure(structure)
        io.save(self.pdbFile.text().replace('.pdb','_aligned.pdb'))
        self.pdbFile.setText(self.pdbFile.text().replace('.pdb','')+ '_aligned.pdb')
    
    def browsePdb(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Select PDB File", 
            "", 
            "PDB Files (*.pdb);;All Files (*)"
        )
        if filename:
            self.pdbFile.setText(filename)
    def fetchPdb(self):
        outFold = self.outputFolder.text()
        pdbCode, ok = QInputDialog.getText(None, 'Enter PDB Code', None)
        
        # Try PDB format first, then CIF if PDB fails
        formats = ['.pdb', '.cif']
        success = False
        
        for fmt in formats:
            url = f"https://files.rcsb.org/download/{pdbCode}{fmt}"
            try:
                response = requests.get(url)
                response.raise_for_status()
                output_file = f"{outFold+os.path.sep+pdbCode}{fmt}"
                
                with open(output_file, 'wb') as f:
                    f.write(response.content)
                
                QMessageBox.information(None, "Success", f"Successfully downloaded {pdbCode}{fmt}")
              
                if fmt==".cif":
                    import pymol
                    pymol.cmd.load(output_file)
                    pymol.cmd.save(output_file.replace(".cif",".pdb"))
                    self.pdbFile.setText(output_file.replace(".cif",".pdb"))
                break  # Exit loop if successful
                
            except requests.exceptions.HTTPError as http_err:
                if response.status_code == 404:
                    if fmt == '.cif':  # Only show error if both formats failed
                        QMessageBox.critical(None, "Error", 
                            f"PDB code '{pdbCode}' not found in either PDB or mmCIF format. Please check the PDB code.")
                    continue  # Try next format if available
                else:
                    QMessageBox.critical(None, "HTTP Error", f"HTTP Error occurred: {http_err}")
                    break
            except requests.exceptions.RequestException as err:
                QMessageBox.critical(None, "Error", f"Error occurred: {err}")
                break
            except IOError as io_err:
                QMessageBox.critical(None, "File Error", f"Error saving file: {io_err}")
                break
    
        
    def simulatePdb(self):
        self.openSimulateForm() 
    
    def browseFiles(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Select PDB File", 
            "", 
            "PDB Files (*.pdb);;All Files (*)"
        )
        if filename:
            self.field1.setText(filename)

    def browseFiles2(self):
        filename, _ = QFileDialog.getOpenFileName(
            self, 
            "Select Map File", 
            "", 
            "MRC Files (*.mrc);;All Files (*)"
        )
        if filename:
            self.field2.setText(filename)

    def simulate(self, field_num):
        print(f"Simulating field {field_num}")

    def fetch(self, field_num):
        print(f"Fetching for field {field_num}")

    def view(self, field_num):
        print(f"Viewing field {field_num}")

    # def fetchPdb(self):
    #     pdb_id = self.field1.text()
    #     print(f"Fetching PDB ID: {pdb_id}")

    def openSimulateForm(self):
        if self.simulate_form is None:
            self.simulate_form = SimulateForm(self)
        self.simulate_form.pixel_size_field.setText(self.templatePixelSize.text())
        self.simulate_form.pdb_field.setText(self.pdbFile.text())
        self.simulate_form.show()

    def calcMaxPdbDiameter(self,pdbName):
        parser = PDBParser()
        structure = parser.get_structure('name', pdbName)
        # Get all atom coordinates
        atoms = structure.get_atoms()
        coords = [atom.get_coord() for atom in atoms]
        # Convert to numpy array
        import numpy as np
        coords = np.array(coords)
        # Calculate max distance between any two points (diameter)
        from scipy.spatial.distance import pdist
        max_diameter = np.max(pdist(coords))

        return max_diameter
        
    def pdbFileChanged(self):
        print("callBack File changed")
        diameter=self.calcMaxPdbDiameter(self.pdbFile.text())
        print(diameter)
    
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())