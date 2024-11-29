import shutil,os
from src.rw.librw import tiltSeriesMeta,starFileMeta
from src.templateMatching.pytomExtractCandidates import pytomExtractCandidates
import numpy as np
import mrcfile
import json

def test_pytomExtractCandidatesFull():
    tomoList='data/vols/tomograms.star'
    output = 'tmpOut/test_pytomExtractCandidatesFull/'
    mokdir,fileNames = create_mock_data(output, tomoList)
    
    args= type('', (), {})() 
    args.in_mics=mokdir+"/tomograms.star"
    args.out_dir=output
    args.implementation="pytom"
    args.apixScoreMap=11.8
    args.particleDiameterInAng=540
    args.maxNumParticles=1500
    args.cutOffMethod="NumberOfFalsePositives" 
    args.cutOffValue=1
    args.scoreFilter=None
    
    tm=pytomExtractCandidates(args,runFlag="Full")
    
    assert os.path.isfile(output+'tmResults/rec_Position_1_particles.star') #os.path.isfile(output+'tmResults/Position_1_scores.mrc')
    
def test_pytomExtractCandidatesPrepareInputs():
    output = 'tmpOut/test_pytomExtractCandidatesPrepareInputs/'
    tomoList='data/vols/tomograms.star'
    
    mokdir,fileNames = create_mock_data(output, tomoList)
    
    args= type('', (), {})() 
    args.in_mics=mokdir+"/tomograms.star"
    args.out_dir=output
   
    tm=pytomExtractCandidates(args)
    tm.prepareInputs()
    for f in fileNames:
        assert os.path.isfile(output+'tmResults/'+f)
        
    
    
def create_mock_data(output, tomoList, size=128, point_pos=(65,65,65)):
    """
    Create mock data structure for testing
    
    Parameters:
    output (str): Output directory path
    tomoList (list): List of tomograms
    size (int): Size of volume (default: 128)
    point_pos (tuple): Position for point in volume (default: (65,65,65))
    """
    mokIn = os.path.join(output, "input")
    directories = [
        "tmpOut",
        output,
        mokIn,
        os.path.join(mokIn, "tmResults")
    ]
    
    # Create directories
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    # Create and write tilt series
    st = tiltSeriesMeta(tomoList)
    st.writeTiltSeries(os.path.join(mokIn, "tomograms.star"))
    del st
    stt = starFileMeta(os.path.join(mokIn, "tomograms.star"))
    stt.df['rlnTomoTiltSeriesStarFile'] = stt.df['rlnTomoTiltSeriesStarFile'].str.replace('tmpOut/', '')
    stt.writeStar(os.path.join(mokIn, "tomograms.star"))
    
    # Create mock MRC files
    fileNames = [
        'rec_Position_1_job.json',
        'rec_Position_1_scores.mrc',
        'rec_Position_1_angles.mrc',
        'rec_Position_1.mrc',
    ]
    
    for f in fileNames:
        volume = np.zeros((size, size, size), dtype=np.float32)
        volume[point_pos] = 1
        output_path = os.path.join(mokIn, 'tmResults', f)
        if f.endswith('.mrc'):
            with mrcfile.new(output_path, overwrite=True) as mrc:
                mrc.set_data(volume.astype(np.float32))
        else:
            shutil.copyfile(os.path.dirname(tomoList)+"/"+f,output_path)
            # with open(os.path.dirname(tomoList)+"/"+f, 'r') as file:
            #     data = json.load(file)   
            # data['name'] = 'New Name'      
            
    return mokIn,fileNames    



# size=128
#     point_pos=(65,65,65)
    
#     os.makedirs("tmpOut", exist_ok=True)
#     os.makedirs(output, exist_ok=True)
#     os.makedirs(mokIn, exist_ok=True)
#     os.makedirs(mokIn+"/tmResults", exist_ok=True)
    
#     st=tiltSeriesMeta(tomoList)
#     st.writeTiltSeries(mokIn+"/tomograms.star")
#     del st
#     stt=starFileMeta(mokIn+"/tomograms.star")
#     stt.df['rlnTomoTiltSeriesStarFile'] = stt.df['rlnTomoTiltSeriesStarFile'].str.replace('tmpOut/', '')
#     stt.writeStar(mokIn+"/tomograms.star")
#     #mok input
#     fileNames=['rec_Position_1_job.json',
#                'rec_Position_1_scores.mrc',
#                'rec_Position_1_angles.mrc']
#     for f in fileNames:
#         volume = np.zeros((size, size, size), dtype=np.float32)
#         volume[point_pos]=1
#         output_path=mokIn+'/tmResults/'+f
#         with mrcfile.new(output_path, overwrite=True) as mrc:
#             mrc.set_data(volume.astype(np.float32))
#         #open(mokIn+'/tmResults/'+f, 'a').close()