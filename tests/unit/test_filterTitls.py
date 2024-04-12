from src.filterTilts.filterTiltsDL import filterTiltsDL
from src.filterTilts.filterTiltsRule import filterTiltsRule
from starfile import read as starread
from src.rw.librw import tiltSeriesMeta
import pandas as pd
import subprocess
import os
import pytest


def test_fitlerTiltsDL_binaryWithModel():
    
    tilseriesStar="data/tilts/tilt_series_ctf.star"
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
    model="data/models/model.pkl"
    
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    ts=filterTiltsDL(ts,model,'binary','data/tmp/')
    assert (ts.all_tilts_df.cryoBoostTestLabel=="good").all()
    
    
def test_fitlerTiltsRule_filterbyCtrMaxResolution():
    
    tilseriesStar="data/tilts/tilt_series_ctf.star"
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
    filterParams = {"rlnCtfMaxResolution": (1,20,-70,70)}
    
    os.makedirs("tmpOut", exist_ok=True)
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    ts=filterTiltsRule(ts,filterParams,'tmpOut')
    assert (ts.all_tilts_df.cryoBoostTestLabel=="good").all()
  
    
def test_crboost_filterTilts_filterbyMaxResolution():
    
    tilseriesStar="data/tilts/tilt_series_ctf.star"
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
    outputFold=relionProj+"tmpOut/"
    
    call=relionProj + "/bin/crboost_filterTitlts.py"
    call+=" --in_mics " + relionProj + tilseriesStar
    call+=" --o " + outputFold
    call+=" --ctfMaxResolution '1,20,-70,70'"
    
    result = subprocess.run(call, capture_output=True, text=True,shell=True)
    ts=tiltSeriesMeta(outputFold + os.path.sep + "tiltseries_filtered.star")
    
    assert (ts.all_tilts_df.cryoBoostTestLabel=="good").all()
    
def test_crboost_filterTilts_filterbyDLModel():
    
    tilseriesStar="data/tilts/tilt_series_ctf.star"
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
    outputFold=relionProj+"tmpOut/"
    
    call=relionProj + "/bin/crboost_filterTitlts.py"
    call+=" --in_mics " + relionProj + tilseriesStar
    call+=" --o " + outputFold
    call+=" --model data/models/model.pkl"
    
    result = subprocess.run(call, capture_output=True, text=True,shell=True)
    ts=tiltSeriesMeta(outputFold + os.path.sep + "tiltseries_filtered.star")
    
    assert (ts.all_tilts_df.cryoBoostTestLabel=="good").all()
    
@pytest.mark.parametrize("test_input", 
                         [("--ctfMaxResolution '1,20,-70,70'"), 
                          ("--ctfMaxResolution '1,20,-70,70'"), 
                          ("--model data/models/model.pkl")])
def test_crboost_filterTilts(test_input):
    
    tilseriesStar="data/tilts/tilt_series_ctf.star"
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
    outputFold=relionProj+"tmpOut/"
    
    call=relionProj + "/bin/crboost_filterTitlts.py"
    call+=" --in_mics " + relionProj + tilseriesStar
    call+=" --o " + outputFold
    call+=" " + test_input
    
    result = subprocess.run(call, capture_output=True, text=True,shell=True)
    ts=tiltSeriesMeta(outputFold + os.path.sep + "tiltseries_filtered.star")
    
    assert (ts.all_tilts_df.cryoBoostTestLabel=="good").all()    


