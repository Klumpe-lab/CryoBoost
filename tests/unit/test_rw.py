from src.rw.librw import dataImport
from src.rw.librw import mdocMeta,tiltSeriesMeta

import os,glob,shutil 


def test_mdocReadWrite():
   
   sourceWk="data/raw/copia/mdoc/*.mdoc"
   targetPath="tmpOut/test_mdocReadWrite/"
   
   if os.path.exists(targetPath):
       shutil.rmtree(targetPath)
   os.makedirs(targetPath, exist_ok=True)
    
   mdoc=mdocMeta(sourceWk)   
   mdoc.writeAllMdoc(targetPath)
   mdocNew=mdocMeta(targetPath+"*.mdoc")
   
   assert mdocNew.all_df.equals(mdoc.all_df)

def test_mdocFilterByTiltSeriesStar():

   sourceWk="data/tilts/mdoc/*.mdoc"
   sourceTsStar="data/tilts/tilt_series_ctf.star"
   targetPath="tmpOut/test_mdocFilterByTiltSeriesStar/"
   
   if os.path.exists(targetPath):
       shutil.rmtree(targetPath)
   os.makedirs(targetPath, exist_ok=True)
   mdoc=mdocMeta(sourceWk)   
   ts=tiltSeriesMeta(sourceTsStar)
   filterParams = {"cryoBoostTestLabel": ("good")}
   ts.filterTilts(filterParams)
   ts.writeTiltSeries(targetPath+"/ts_test.star")
   
   mdoc.filterByTiltSeriesStarFile(targetPath+"/ts_test.star")
   mdoc.writeAllMdoc(targetPath)
   mdocNew=mdocMeta(targetPath+"*.mdoc")
   mdocNew=mdocNew.all_df['cryoBoostKey']
   dfTs=ts.all_tilts_df['rlnMicrographMovieName'].apply(os.path.basename)
   
   assert dfTs.equals(mdocNew)

   
def test_mdocAddPrefix():

   sourceWk="data/tilts/mdoc/*.mdoc"
   targetPath="tmpOut/test_mdocAddPrefix/"
   testPref="umba-prefix_"
   
   if os.path.exists(targetPath):
      shutil.rmtree(targetPath)
   os.makedirs(targetPath, exist_ok=True)
   mdoc=mdocMeta(sourceWk)   
   mdoc.addPrefixToFileName(testPref) 
   mdoc.writeAllMdoc(targetPath)
   mdoc=mdocMeta(targetPath+"*.mdoc")

   mdocOrg=mdocMeta(sourceWk)
   dfPref=mdoc.all_df['SubFramePath']   
   dfTest=mdocOrg.all_df['SubFramePath'].apply(lambda x:testPref+os.path.basename(x))
   
   assert dfTest.equals(dfPref)


def test_mdocAddOrgPath():

   sourceWk="data/tilts/mdoc/*.mdoc"
   targetPath="tmpOut/test_mdocAddOrgPath/"
   
   resultPath=glob.glob(os.path.abspath(sourceWk))[0]
   if os.path.exists(targetPath):
      shutil.rmtree(targetPath)
   os.makedirs(targetPath, exist_ok=True)
   mdoc=mdocMeta(sourceWk)   
  
   mdoc.writeAllMdoc(targetPath,appendMdocRootPath=True)
   mdoc=mdocMeta(targetPath+"*.mdoc")
   orgPathMdoc=mdoc.all_df["mdocOrgPath"].unique()[0]
   
   assert orgPathMdoc==resultPath



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