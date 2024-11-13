from src.rw.librw import tiltSeriesMeta
import shlex,os,subprocess,sys,pathlib
from abc import ABC, abstractmethod


class templateMatchingWrapperBase(ABC):
    
    def __init__(self,args,runFlag=None):
        
        self.args=args
        
        self.getRelionProjPath(args.in_mics)
        self.st=tiltSeriesMeta(args.in_mics,self.relProj)

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