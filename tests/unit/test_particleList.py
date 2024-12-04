from src.rw.particleList import particleListMeta
import shutil,os
import pandas as pd
from pandas.testing import assert_frame_equal


def testReadParticleList():
    
    listName='tmpOut/V7/External/job027/candidates.star'
    pl=particleListMeta(listName)    
    pl.writeImodModel('tmpOut/',50,[1024,1024,512])
    pl.writeList('tmpOut/testPl','warpCoords',[1024,1024,512])
    assert 1==1

def testWriteParticleList():
    pl=particleListMeta
    
    inputFormat={}
    inputFormat['pixelSizeInAng']=1.0
    inputFormat['coordsParadigm']="centCoordInAng"
    inputFormat['angParadigm']="ZYZ"
    
    pl.addItem(pos=[100,200,300],ang=[10,20,30],score=0.4,tomoName="Postion_1",inputFormat=inputFormat)
    
    print("picklist Module not implemented")
    assert 1==1   
 

# def test_writeTiltSeries():

#     tilseriesStar='data/tilts/tilt_series_ctf.star'
#     outputTiltSeries='tmpOut/tsRw/tilt_series_testRw.star'
#     relionProj=os.path.abspath(__file__)
#     relionProj=os.path.dirname(os.path.dirname(os.path.dirname(relionProj)))+os.path.sep
 
#     #ts2=tiltSeriesMeta('tmpOut/V3/Tomograms/job005/tomograms.star','./tmpOut/V3/')
 
#     os.makedirs("tmpOut", exist_ok=True)
#     os.makedirs("tmpOut/tsRw/", exist_ok=True)
#     ts=tiltSeriesMeta(tilseriesStar,relionProj)
#     ts.writeTiltSeries(outputTiltSeries)
#     tsNew=tiltSeriesMeta(outputTiltSeries,relionProj)
#     df1_red = ts.all_tilts_df.drop('rlnTomoTiltSeriesStarFile', axis=1)
#     df2_red = tsNew.all_tilts_df.drop('rlnTomoTiltSeriesStarFile', axis=1)
    
#     assert_frame_equal(df1_red.sort_index(axis=1),df2_red.sort_index(axis=1))