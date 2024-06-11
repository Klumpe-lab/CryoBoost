from src.rw.librw import dataImport
import os


def test_importData():

   targetPath="tmpOut/testImport/"
   wkFrames=targetPath + "/inputFrames/*.eer"
   wkMdoc=targetPath + "/inputMdoc/*.mdoc"
   
   os.makedirs(targetPath+"inputFrames", exist_ok=True)
   os.makedirs(targetPath+"inputMdoc", exist_ok=True)
   file_names = ["Position_1_001[10.00]_EER.eer", "Position_1_002[15.00]_EER.eer", "Position_1_003[30.00]_EER.eer"]
   for file_name in file_names:
        with open(targetPath+"/inputFrames/"+file_name, "w") as file:
            pass
   with open(targetPath+"/inputMdoc/Position_1.mdoc", "w") as file:
       pass
   
   dataImport(targetPath,wkFrames,wkMdoc)
   
   
    
   assert 1==1