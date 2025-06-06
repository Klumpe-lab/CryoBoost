#%%

import os
import glob
import subprocess
import math
from src.rw.librw import cbconfig

def get_EERsections_per_frame(eer_file, dosePerTilt=3, dosePerRenderedFrame=0.3,optRange=0.15):
    """
    Calculate optimal sections per frame for an EER file based on dose parameters
    
    Args:
        eer_file (str): Path to the EER file
        dosePerTilt (float): Dose per Angstrom squared per tilt (default 3)
        dosePerRenderedFrame (float): Wanted dose per rendered frame (default 0.3)
        optRange (float): Range for optimization (default 0.15) in percentage/100
        
    Returns:
        int: Optimal sections per frame value
    """
    
    CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
    confPath=CRYOBOOST_HOME + "/config/conf.yaml"
    conf=cbconfig(confPath)   
    envStr = conf.confdata['local']['Environment']
    call=envStr+';header ' + eer_file 
    result = subprocess.run(call, shell=True, capture_output=True, text=True)
    
    #result = subprocess.run(['header', eer_file], capture_output=True, text=True)
    output_lines = result.stdout.split('\n')
    
    framesPerTilt = None
    for line in output_lines:
        if "Number of columns, rows, sections" in line:
            parts = line.split('.')[-1].strip().split()
            framesPerTilt = int(parts[2])
            break
            
    if framesPerTilt is None:
        raise ValueError(f"Could not find sections information in file: {eer_file}")
    
    # Calculate target value
    dosePerFrame = dosePerTilt/framesPerTilt
    numFramesToGroup=math.floor(dosePerRenderedFrame/dosePerFrame)
    numOfRenderedFrames=math.floor(framesPerTilt/numFramesToGroup)
    
    # print(f"Number of eer frames per tilt: {framesPerTilt}")
    # print(f"Total dose per tilt: {dosePerTilt}")
    # print(f"Dose per eer frame: {dosePerFrame}")
    # print(f"Dose per rendered frame (input): {dosePerRenderedFrame}")
    # print(f"Number of frames to group: {numFramesToGroup}")
    # print(f"Number of Rendered Frames: {numOfRenderedFrames}")
    # print(f"Lost EER Frames: {framesPerTilt - numOfRenderedFrames*numFramesToGroup}")
    # print(" ")
    
    allNumOfFramesToGroup = []
    allLostEERFrames = []
    for i in range(round(numFramesToGroup*(1-optRange)),round(numFramesToGroup*(1+optRange))):
        allNumOfFramesToGroup.append(i) 
        numOfRenderedFrames=math.floor(framesPerTilt/i)
        allLostEERFrames.append(framesPerTilt - numOfRenderedFrames*i)
   

    minLost = min(allLostEERFrames)
    minLostIndex = allLostEERFrames.index(minLost)
    numFramesToGroup=allNumOfFramesToGroup[minLostIndex]
    if numOfRenderedFrames < 3:
        print("Warning: Number of rendered frames is less than 3 with a requested dose of " + str(dosePerRenderedFrame) + "electrons.")
        print("Adpated grouping to get 3 rendered frames per tilt.")
        numFramesToGroup = math.floor(framesPerTilt/3)
    numOfRenderedFrames=math.floor(framesPerTilt/numFramesToGroup)
    dosePerRenderedFrameOpt = round(dosePerFrame * numFramesToGroup,2)
    lostEERframesOpt=framesPerTilt - numOfRenderedFrames*numFramesToGroup
    
    print("Opt. number of grouped EER frames:")
    print("=================================")
    print(f"Number of eer frames per tilt: {framesPerTilt}")
    print(f"Total dose per tilt: {dosePerTilt}")
    print(f"Dose per eer frame: {round(dosePerFrame,4)}")
    print(f"Dose per rendered frame (opt to lost EER Frames): {dosePerRenderedFrameOpt} (input): {dosePerRenderedFrame}")
    print(f"Number of frames to group: {numFramesToGroup}")
    print(f"Number of rendered frames: {numOfRenderedFrames}")
    print(f"Lost EER Frames: {lostEERframesOpt} of {framesPerTilt} ({round(lostEERframesOpt/framesPerTilt*100,1)}%)")
    
    return numFramesToGroup


#%% something like this should be in the code then:

#self.textEdit_eerFractions.setText(get_EERsections_per_frame(glob.glob(self.line_path_movies)[0]))

# p='/fs/pool/pool-fbeck/projects/4TomoPipe/rel5Pipe/src/CryoBoost/data/raw/copia/frames/Position_1_001[10.00]_EER.eer'
# get_EERsections_per_frame(p, dosePerTilt=3, dosePerRenderedFrame=0.3, optRange=0.15)


