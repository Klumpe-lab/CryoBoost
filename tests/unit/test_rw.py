from src.rw.librw import dataImport
import os,glob,shutil 


def test_importData():

   
   targetPath="tmpOut/testImport/"
   if os.path.exists(targetPath):
        shutil.rmtree(targetPath)
        
   wkFrames=targetPath + "/inputFrames/*.eer"
   wkMdoc=targetPath + "/inputMdoc/*.mdoc"
   
   #gen input data
   os.makedirs(targetPath+"inputFrames", exist_ok=True)
   os.makedirs(targetPath+"inputMdoc", exist_ok=True)
   file_names = ["Position_1_001[10.00]_EER.eer", "Position_1_002[15.00]_EER.eer", "Position_1_003[30.00]_EER.eer"]
   for file_name in file_names:
        with open(targetPath+"/inputFrames/"+file_name, "w") as file:
            pass
   with open(targetPath+"/inputMdoc/Position_1.mdoc", "w") as file:
       for file_name in file_names:
          file.writelines("SubFramePath = \\offload\\umba-umba\\" + file_name + "\n")
   
   #run code
   dataImport(targetPath,wkFrames,wkMdoc)
   
   fileFr=[fileFr for fileFr in glob.glob(targetPath + "frames/*.eer")]
   fileMd=[fileMd for fileMd in glob.glob(targetPath + "mdoc/*.mdoc")]
   #eval for assert
   assert len(fileFr)==len(file_names)
   assert len(fileMd)==1
   
   #test for adapted mdoc missing
   framePath=[]
   for file_name in fileMd:
      with open(file_name, "r") as file:
         lines = file.readlines()
         for i, line in enumerate(lines):
            if 'SubFramePath' in line:
               framePath.append(targetPath + "frames/"  + line.replace("SubFramePath = ","").replace('\n',''))
   
   fileFr.sort()
   framePath.sort()
                
   assert fileFr==framePath
   
   #test for duplicate import
   dataImport(targetPath,wkFrames,wkMdoc)
   assert len(fileFr)==len(file_names)
   assert len(fileMd)==1
   if os.path.exists(targetPath):
        shutil.rmtree(targetPath)