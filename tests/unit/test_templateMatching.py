import shutil,os
from src.rw.librw import tiltSeriesMeta
from src.templateMatching.pytomTm import pytomTm

def test_pytomTM_Full():
    inputTsPath='data/vols/tomograms.star'
    output = 'tmpOut/test_pytomTM_Full/'
    
    
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs(output, exist_ok=True)
    
    
    args= type('', (), {})() 
    args.in_mics=inputTsPath
    args.out_dir=output
    args.volumeColumn="rlnTomoReconstructedTomogram"
    args.volumeMaskFold=None
    args.template="data/vols/Position_1.mrc"
    args.templateSym="C1"
    args.templateMask="data/vols/mask.mrc"
    args.nonSphericalMask="True"
    args.angularSearch=str(30)    
    args.doseWeight="False"
    args.nonSphericalMask="False"
    args.bandPassFilter=None
    args.ctfWeight="False"
    args.bandPassFilter="None"
    args.doseWeight="True"
    args.spectralWhitening="False"
    args.randomPhaseCorrection="True"
    args.gpu_ids="0"
    args.split="None"
        
    tm=pytomTm(args,runFlag="Full")
    
    assert os.path.isfile(output+'tmResults/Position_1_scores.mrc')
    assert os.path.isfile(output+'tmResults/Position_1_angles.mrc')
    assert os.path.isfile(output+'tmResults/Position_2_scores.mrc')
    assert os.path.isfile(output+'tmResults/Position_2_angles.mrc')
    
def test_pytomTM_PrepareInputs():
    inputTsPath='data/vols/tomograms.star'
    output = 'tmpOut/test_pytomTM_PrepareInputs/'
    
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs(output, exist_ok=True)
    
    args= type('', (), {})() 
    args.in_mics=inputTsPath
    args.out_dir=output
   
    tm=pytomTm(args)
    tm.prepareInputs()
       
    assert os.path.isfile(output+'defocusFiles/Position_1.txt') and os.path.isfile(output+'defocusFiles/Position_2.txt')
    assert os.path.isfile(output+'doseFiles/Position_1.txt')  and os.path.isfile(output+'doseFiles/Position_2.txt') 
    assert os.path.isfile(output+'tiltAngleFiles/Position_1.tlt') and os.path.isfile(output+'tiltAngleFiles/Position_2.tlt')
    
    