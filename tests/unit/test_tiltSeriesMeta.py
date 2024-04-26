from src.rw.librw import tiltSeriesMeta
import shutil,os
import pandas as pd
from pandas.testing import assert_frame_equal

def test_writeTiltSeries():

    tilseriesStar='data/tilts/tilt_series_ctf.star'
    outputTiltSeries='tmpOut/tilt_series.star'
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
 
    os.makedirs("tmpOut", exist_ok=True)
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    ts.writeTiltSeries(outputTiltSeries)
    tsNew=tiltSeriesMeta(outputTiltSeries,relionProj)
    df1_red = ts.all_tilts_df.drop('rlnTomoTiltSeriesStarFile', axis=1)
    df2_red = tsNew.all_tilts_df.drop('rlnTomoTiltSeriesStarFile', axis=1)
    
    assert_frame_equal(df1_red.sort_index(axis=1),df2_red.sort_index(axis=1))
    
    
    