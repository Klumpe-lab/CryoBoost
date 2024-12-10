import os
from src.misc.libpdb import pdb
import numpy as np
import pytest

def idfn(test_input,context):
    
    if (isinstance(test_input, dict)):
        key=list(test_input.keys())[0]
        value = str(test_input[key])
    else:
        key=""
        value = str(test_input)
   
    return f"{context['function_name']} {key}-{value}"


def test_FetchPdb():
    
    pdbCode='1pma'
    mass=616439
    pdbO=pdb(pdbCode)
    
    assert int(pdbO.model.get_mass())==pytest.approx(mass, rel=1e-6)
   
def test_pdbMaxDiameter():
    
    pdbCode='1pma'
    diameter=167
    pdbO=pdb(pdbCode)
    diaFromPDB=pdbO.getMaxDiameter()
    
    assert int(diaFromPDB)==int(diameter) 

def test_optBoxSize():
    
    pdbCode='1pma'
    boxSz=160
    pixS=1.2
    pdbO=pdb(pdbCode)
    optBox=pdbO.getOptBoxSize(pixS)
    
    assert int(boxSz)==int(optBox) 


def test_writePdb():
    
    pdbCode='1pma'
    pdbO=pdb(pdbCode)
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs("tmpOut/test_writePdb", exist_ok=True)
    pdbO.writePDB("tmpOut/test_writePdb/1pma.cif")
    pdbRead=pdb("tmpOut/test_writePdb/1pma.cif")
    
    assert pdbO.model.get_mass() == pytest.approx(pdbRead.model.get_mass(), rel=1e-6)
    
def test_rotatePdb():
    
    pdbCode='1pma'
    pdbO=pdb(pdbCode)
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs("tmpOut/test_rotatePdb", exist_ok=True)
    pdbO.rotatePDB('y',45)
    pdbO.rotatePDB('x',45)
    pdbO.writePDB("tmpOut/test_rotatePdb/1pmaRot.cif")
   
    assert os.path.isfile('tmpOut/test_rotatePdb/1pmaRot.cif')  
    

def test_alignToPrincipalAxis():
    
    pdbCode='1pma'
    pdbO=pdb(pdbCode)
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs("tmpOut/test_alignToPrincipalAxis", exist_ok=True)
    pdbO.rotatePDB('y',45)
    pdbO.rotatePDB('x',45)
    pdbO.alignToPrincipalAxis()
    pdbO.writePDB("tmpOut/test_alignToPrincipalAxis/1pmaAligned.cif")
    
    assert os.path.isfile('tmpOut/test_alignToPrincipalAxis/1pmaAligned.cif')  


@pytest.mark.parametrize("pdbCode,outF", 
                         [  ("1pma", "cif"), 
                            ("7tut", "cif")],
                         ids=lambda val: idfn(val, {'function_name': 'simulateMapFromPDB'}))
@pytest.mark.simulateMapFromPDB
def test_simulateMapFromPDB(pdbCode, outF):  # Direct parameters instead of test_input
    pdbO = pdb(pdbCode)
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs("tmpOut/test_simulateMapFromPdb", exist_ok=True)
    outputPath = f'tmpOut/test_simulateMapFromPdb/{pdbCode}.mrc'
    
    pdbO.simulateMapFromPDB(
        outPath=outputPath,
        outPix=4.0,
        outBox=64,
        pdbOutFormat=outF
    ) 
    
    assert os.path.exists(outputPath)


