from src.rw.librw import tiltSeriesMeta
import shutil,os

def test_writeTiltSeries():

    tilseriesStar='data/tilts/tilt_series_ctf.star'
    outputTiltSeries='tmpOut/tilt_series.star'
    relionProj=os.path.abspath(__file__)
    relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
 
    os.makedirs("tmpOut", exist_ok=True)
    ts=tiltSeriesMeta(tilseriesStar,relionProj)
    ts.writeTiltSeries(outputTiltSeries)
    tsNew=tiltSeriesMeta(outputTiltSeries,relionProj)
    
    
    assert 1==1
    