from src.filterTilts.filterTiltsDL import filterTiltsDL
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
 
    


