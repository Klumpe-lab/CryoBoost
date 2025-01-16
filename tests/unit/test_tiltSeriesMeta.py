from src.rw.librw import tiltSeriesMeta
import shutil,os
import pandas as pd
from pandas.testing import assert_frame_equal

def test_writeTiltSeries():

    tilseriesStar='data/tilts/tilt_series_ctf.star'
   
    outputTiltSeries='tmpOut/tsRw/tilt_series_testRw.star'
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
    #tilseriesStar='tmpOut/E10/Tomograms/job009/tomograms.star'
    #relionProj='tmpOut/E10/'
    
    #ts2=tiltSeriesMeta('tmpOut/V3/Tomograms/job005/tomograms.star','./tmpOut/V3/')
 
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs("tmpOut/tsRw/", exist_ok=True)
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    ts.writeTiltSeries(outputTiltSeries)
    tsNew=tiltSeriesMeta(outputTiltSeries,relionProj)
    df1_red = ts.all_tilts_df.drop('rlnTomoTiltSeriesStarFile', axis=1)
    df2_red = tsNew.all_tilts_df.drop('rlnTomoTiltSeriesStarFile', axis=1)
    df2_red = df2_red.drop('cryoBoostKey', axis=1)
    df1_red = df1_red.drop('cryoBoostKey', axis=1)
    assert_frame_equal(df1_red.sort_index(axis=1),df2_red.sort_index(axis=1))
    
    
    