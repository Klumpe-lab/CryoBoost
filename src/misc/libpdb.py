import pymol2
import os
import numpy as np
import subprocess
import tempfile
from Bio.PDB import MMCIFParser, MMCIFIO

class pdb:
    """
    Class for handling pdb metadata.

    Args:
      
    """

    def __init__(self,pdbIn):
        """
        Initializes the tiltSeriesMeta class.
        """
        self.pdbName = None
        self.pdbCode = None
        self.pymol=pymol2.PyMOL()
        self.pymol.start()

        if os.path.isfile(pdbIn):
            self.pdbName = pdbIn
            self.pdbCode = pdbIn.split('.')[0]
            self.readPDB(pdbIn)
        else:
            self.pdbName = None
            self.pdbCode = pdbIn
            self.fetchPDB(pdbIn)
        self.pymol.cmd.center(self.modelName)    
    
    def fetchPDB(self,pdbCode,output="tmpDir"):
        """
        Fetches the pdb file from the PDB server.
        """
        if output=="tmpDir":
            self.pymol.cmd.set('fetch_path',tempfile.gettempdir())
            self.pymol.cmd.fetch(pdbCode)
        else:
            self.pymol.cmd.fetch(pdbCode,filename=output)
            
        self.model = self.pymol.cmd.get_model(pdbCode)
        self.modelName=pdbCode
        
        
    def writePDB(self,outputName,outputFormat="cif"):
        self.outputName=outputName
        self.pymol.cmd.save(outputName, self.modelName,format=outputFormat)
        parser = MMCIFParser()
        structure = parser.get_structure('structure_id', outputName)
        io = MMCIFIO()
        io.set_structure(structure)
        io.save(outputName)
        
        
    def readPDB(self,inputName):
        self.pymol.cmd.load(inputName)
        object_name = os.path.splitext(os.path.basename(inputName))[0]
        self.model = self.pymol.cmd.get_model(object_name)
        self.modelName=object_name
 
    def rotatePDB(self,axis,angle):
        self.pymol.cmd.rotate(axis,angle)
    
    def alignToPrincipalAxis(self):
        """
        Align coordinates from a PyMOL model to principal axes and replace original model

        Parameters:
        model_name: str, name of the PyMOL model/object

        Returns:
        aligned_coords: numpy array of aligned coordinates
        eigenvectors: principal axes
        center: center of mass
        """

        cmd=self.pymol.cmd
        model_name=self.modelName
        coords = cmd.get_coords(model_name)
        center = np.mean(coords, axis=0)
        centered_coords = coords - center
        covariance_matrix = np.cov(centered_coords.T)
        eigenvalues, eigenvectors = np.linalg.eigh(covariance_matrix)
        idx = eigenvalues.argsort()[::-1]
        eigenvalues = eigenvalues[idx]
        eigenvectors = eigenvectors[:, idx]
       
        aligned_coords = np.dot(centered_coords, eigenvectors)

        cmd.delete('aligned_temp')
        cmd.load_coords(aligned_coords, model_name)

    
    def simulateMapFromPDB(self,outPath,outPix,outBox,modScaleBf=1,modBf=0,oversamp=2,numOfFrames=7,pdbOutFormat="cif"):
        
        pdbLocal=os.path.splitext(outPath)[0] + "." + pdbOutFormat 
        self.writePDB(pdbLocal,pdbOutFormat)
        full_dict={}
        full_dict['outFile']=outPath
        full_dict['scPotential']='Yes'
        full_dict['boxSize']=outBox
        full_dict['threads']=25
        full_dict['inputPDBPath']=pdbLocal
        full_dict['addPart']='No'
        full_dict['outputPix']=outPix
        full_dict['perAtomScaleBfact']=modScaleBf
        full_dict['perAtomBfact']=modBf
        full_dict['oversample']=oversamp
        full_dict['numOfFrames']=numOfFrames
        full_dict['expert']='No'
        full_dict['EOF']='EOF'
        full_dict['exit']='exit 0'
        
        paramFileName=os.path.splitext(outPath)[0] + ".inp" 
        with open(paramFileName, 'w') as f:
            for value in full_dict.values():
                 f.write(f"{value}\n")

        call="simulate < " + paramFileName
        print(call)
        result=subprocess.run(call,shell=True,capture_output=True, text=True, check=True)
        print(result.stdout)
        print(result.stderr) 
    
    def getMaxDiameter(self):
        min_xyz, max_xyz = self.pymol.cmd.get_extent()
        distances = [max_xyz[i] - min_xyz[i] for i in range(3)]
    
        return max(distances)    
    
    def getOptBoxSize(self,pixelSize,minBox=128):
        
        diaM=self.getMaxDiameter()/pixelSize
        box_size=self.__get_next_box_size_power2(diaM)
        
        if box_size < minBox:
            box_size=minBox
        
        return box_size

        
    def __get_next_box_size_power2(self,value: int, offset: int = 32) -> int:
        """
        Find next box size that's aligned to offset and checks if it's power of 2
        """
       
        size = self.__get_next_box_size(value, offset)
        
        return size
        
        # if (size & (size - 1)) == 0:
        #     return size
        
        # # If not power of 2, get next power of 2
        # power = 1
        # while power < size:
        #     power *= 2
        # return power

    def __get_next_box_size(self,value: int, offset: int = 32) -> int:
        """
        Find next box size that's aligned to offset
        Args:
            value: input value
            offset: alignment value (default 32)
        Returns:
            Next aligned box size
        Example:
            get_next_box_size(65, 32) -> 96
            get_next_box_size(33, 32) -> 64
            get_next_box_size(95, 32) -> 96
        """

        num_blocks = (value + offset - 1) // offset
        # Multiply by offset to get aligned size
        return num_blocks * offset
