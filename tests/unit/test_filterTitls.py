from src.filterTilts.filterTiltsDL import filterTiltsDL
from src.filterTilts.filterTiltsRule import filterTiltsRule
from starfile import read as starread
import pandas as pd
import os

pathToStarFile = "data/tilts/tilt_series_ctfLables.star"
pathToRelionProj = "./"

def test_fitlerTiltsDL_TiltseriesStar():
    
    
    tilseriesStar="data/tilts/tilt_series_ctf.star"
    relionProj="./"
    model="data/models/model.pkl"
    lablesPred,probs,tiltspath=filterTiltsDL(tilseriesStar,relionProj,model,'binary')
    
    st = starread(tilseriesStar)
    lablesTrue = pd.Series([])
    for ts in st["rlnTomoTiltSeriesStarFile"]:
        stts = starread(os.path.join(pathToRelionProj, ts))
        tmp=stts['cryoBoostLabel']
        lablesTrue = pd.concat([lablesTrue, tmp])
    
    lablesTrue_list = lablesTrue.tolist()
    
    assert (lablesTrue_list==lablesPred)

def test_fitlerTiltsRule_TiltseriesStar():
    
    
    tilseriesStar="data/tilts/tilt_series_ctf.star"
    res = "5-12"
    out_dir="tests/tmpOutput"
    
    filterTiltsRule(tilseriesStar,out_dir,shift_init=None,defocus_init=None,res_init=res)
    st = starread(tilseriesStar)
    
    
    
    assert (lablesTrue_list==lablesPred)
  
    


