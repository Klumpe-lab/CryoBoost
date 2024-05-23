import pandas as pd
import subprocess
import os
import pytest
from src.misc.system import run_command

def idfn(test_input,context):
    
    if (isinstance(test_input, dict)):
        key=list(test_input.keys())[0]
        value = str(test_input[key])
    else:
        key=""
        value = str(test_input)
   
    return f"{context['function_name']} {key}-{value}"


def test_relion_tomo_prep_copia():
    
    outputProjPath="tmpOut/P_test_relion_tomo_prep_copia"
    options=" -aG -nG -aLsync"
    frames=" -mov data/raw/copia/frames/"
    mdoc=" -m data/raw/copia/mdoc/"
    outputProj=" --proj " + outputProjPath 
    baseCall="./bin/crboost_pipe.py" 
    result1=outputProjPath + "/Tomograms/job006/tomograms/rec_Position_1.mrc"
    result2=outputProjPath + "/Tomograms/job006/tomograms/rec_Position_36.mrc"
    result3=outputProjPath + "/Tomograms/job006/RELION_JOB_EXIT_SUCCESS"
    call=baseCall+options+frames+mdoc+outputProj
    out=run_command(call)
    
    assert os.path.exists(result1), f"File {result1} does not exist"
    assert os.path.exists(result2), f"File {result2} does not exist"
    assert os.path.exists(result3), f"File {result3} does not exist"
