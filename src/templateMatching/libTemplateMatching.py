from src.rw.librw import tiltSeriesMeta
import shlex,os,shutil,glob,subprocess,sys,pathlib
from abc import ABC, abstractmethod
import json


class templateMatchingWrapperBase(ABC):
    
    def __init__(self,args,runFlag=None):
        
        self.args=args
        
        self.getRelionProjPath(args.in_mics)
        self.st=tiltSeriesMeta(args.in_mics,self.relProj)
        self.inputFold=os.path.dirname(args.in_mics)
        
        sys.stdout.flush()
        if runFlag=="Full":
            self.run()
        
    @abstractmethod
    def prepareInputs(self):
        pass
    @abstractmethod
    def runMainApp(self):
        pass
    @abstractmethod
    def updateMetaData(self):
        pass     
    @abstractmethod
    def checkResults(self):
        pass
    
    def run(self):
        self.prepareInputs()
        self.runMainApp()
        self.updateMetaData()
        self.checkResults()
    
    def getParameterForTemplateMatching(self):
        return self.paramTm
    
    def createSettings(self):
        self.prepareInputs()
        self.paramTm=self.getParameterForTemplateMatching()
    
    def getRelionProjPath(self,in_mics):    
        relProj=os.path.dirname(os.path.dirname(os.path.dirname(in_mics)))
        if relProj != "" and relProj is not None:
            relProj=relProj+"/"
        if (relProj==""):
            relProj="./"
        
        self.relProj=relProj
    
    def getFilesByWildCard(self,source_pattern, target_dir, copy_files=False):
        
        print("  found " + str(len(glob.glob(source_pattern))) + " files")
        for source_file in glob.glob(source_pattern):
        
            file_name = os.path.basename(source_file)
            target_path = os.path.join(target_dir, file_name)
            try:
                if copy_files:
                    #shutil.copy2(source_file, target_path)
                    with open(source_file, 'r') as file:
                        data = json.load(file)
                        data["output_dir"]=os.path.dirname(target_path)
                        with open(target_path, 'w') as fileOut:
                            json.dump(data, fileOut)
                else:
                    os.symlink(os.path.abspath(source_file), target_path)
            except FileExistsError:
                print(f"File already exists: {target_path}")
            except Exception as e:
                print(f"Error processing {source_file}: {e}")      