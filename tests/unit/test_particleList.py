from src.rw.particleList import particleListMeta
import shutil,os
import pandas as pd
from pandas.testing import assert_frame_equal
import numpy as np

def test_ReadWritePytomRelion5PickList():
    
    listName='data/pickLists/candidatesPytomRel5.star'
    pl=particleListMeta(listName)    
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs("tmpOut/test_ReadWritePytomRelion5PickList", exist_ok=True)
    pl.writeList('tmpOut/test_ReadWritePytomRelion5PickList/candidatesPytomRel5.star')
    pl2=particleListMeta('tmpOut/test_ReadWritePytomRelion5PickList/candidatesPytomRel5.star')
    
    assert_frame_equal(pl.all_particle_df,pl2.all_particle_df)
    

def test_ReadRelion5PickListExportToWarp():
    
    listName='data/pickLists/candidatesPytomRel5.star'
    tomoSize=[1024,1024,512]
    pl=particleListMeta(listName)    
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs("tmpOut/test_ReadRelion5PickListExportToWarp", exist_ok=True)
    pl.writeList('tmpOut/test_ReadRelion5PickListExportToWarp/candidatesWarp',"warpCoords",tomoSize=tomoSize)
    pl2=particleListMeta('tmpOut/test_ReadRelion5PickListExportToWarp/candidatesWarp/*.star',tomoSize=tomoSize)
    columns_to_compare=["rlnCenteredCoordinateXAngst",
                        "rlnCenteredCoordinateYAngst",
                        "rlnCenteredCoordinateZAngst",
                        "rlnAngleRot",
                        "rlnAngleTilt",
                        "rlnAnglePsi",
                        "rlnLCCmax",
                        "rlnTomoTiltSeriesPixelSize"
                        ]
    
    assert_frame_equal(
                        pl.all_particle_df[columns_to_compare],
                        pl2.all_particle_df[columns_to_compare]
                        )
    
       

def test_ReadRelion5PickListWriteImodModel():
    listName='data/pickLists/candidatesPytomRel5.star'
    diaInAng=550
    tomoSize=[1024,1024,512]
    os.makedirs("tmpOut", exist_ok=True)
    os.makedirs("tmpOut/test_ReadRelion5PickListWriteImodModel", exist_ok=True)
    pl=particleListMeta(listName)
    pl.writeImodModel('tmpOut/test_ReadRelion5PickListWriteImodModel/',diaInAng,tomoSize)
    txt_coords = np.loadtxt('tmpOut/test_ReadRelion5PickListWriteImodModel/coords_Position_1_11.80Apx.txt')
    coordsList=pl.getImodCoords(None,tomoSize)
    
    np.testing.assert_array_almost_equal(txt_coords,coordsList, decimal=1)
    
    



#  pl=particleListMeta
    
#     inputFormat={}
#     inputFormat['pixelSizeInAng']=1.0
#     inputFormat['coordsParadigm']="centCoordInAng"
#     inputFormat['angParadigm']="ZYZ"
    
#     pl.addItem(pos=[100,200,300],ang=[10,20,30],score=0.4,tomoName="Postion_1",inputFormat=inputFormat)
    
#     print("picklist Module not implemented")    