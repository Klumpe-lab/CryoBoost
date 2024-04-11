from src.filterTilts.filterTiltsDL import filterTiltsDL
from src.filterTilts.filterTiltsRule import filterTiltsRule
from starfile import read as starread
from src.rw.librw import tiltSeriesMeta
import pandas as pd
import os

pathToStarFile = "data/tilts/tilt_series_ctfLables.star"
pathToRelionProj = "./"

def test_fitlerTiltsDL_TiltseriesStar():
    
    
    tilseriesStar="data/tilts/tilt_series_ctf.star"
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
    model="data/models/model.pkl"
    
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    ts=filterTiltsDL(ts,model,'binary','data/tmp/')
    assert (ts.all_tilts_df.cryoBoostDlLabel=="good").all()
    
    
def test_fitlerTiltsRule_TiltseriesStar():
    
    tilseriesStar="data/tilts/tilt_series_ctf.star"
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
    model="data/models/model.pkl"
    
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    
    
    filterTiltsRule(tilseriesStar,out_dir,shift_init=None,defocus_init=None,res_init=res)
    st = starread(tilseriesStar)
    
    
    
    assert (lablesTrue_list==lablesPred)
  
    


