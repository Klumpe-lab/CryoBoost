import shutil,os
from src.rw.librw import tiltSeriesMeta
from src.warp.fsMotionAndCtf import fsMotionAndCtf

def test_fsMotionAndCtfSettings():
    inputTsPath='data/tilts/tilt_series_ctf.star'
    output = 'tmpOut/test_fsMotionAndCtfSettings/'
    
    # if ((output[0]!='/') and ('tmpOut' in output) and os.path.exists(output)): 
    #     shutil.rmtree(output)
    
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs(output, exist_ok=True)
        
    args.in_mics =inputTsPath
    args.cs=1
    fsM=fsMotionAndCtf(args.in_mics)
    
    
    assert 1 == 1   
    