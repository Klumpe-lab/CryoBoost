import shutil,os
from src.rw.librw import tiltSeriesMeta
from src.warp.fsMotionAndCtf import fsMotionAndCtf

def test_fsMotionAndCtfSettings():
    inputTsPath='data/tilts/tilt_series_ctf.star'
    output = 'tmpOut/test_fsMotionAndCtfSettings/'
    
    if os.path.isfile(output + "warp_frameseries.settings"):
        os.remove(output + "warp_frameseries.settings")

    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs(output, exist_ok=True)
    
    args=type('', (), {})()   
    args.in_mics =inputTsPath
    args.out_dir=output
    args.gain_path="None"
    args.gain_operations=None
    fsM=fsMotionAndCtf(args)
    fsM.createSettings()
    
    assert os.path.isfile(output + "warp_frameseries.settings")   
    