import subprocess
import numpy as np
import os
import pandas as pd
import glob
from src.rw.librw import starFileMeta

class particleListMeta:
    """
    Class for handling pickList metadata.

    Args:
      
    """

    def __init__(self, partLilstStarFile=None,tomoSize=None):
        """
        Initializes the tiltSeriesMeta class.
        """
        self.partLilstStarFile = None
        self.partList = None
       
        if partLilstStarFile is not None:
            self.partLilstStarFile=partLilstStarFile
            self.read(partLilstStarFile,tomoSize)

    def addItem(self,coord,angle,score,tomoName,format):
        pass
    
    def read(self,partLilstStarFile,tomoSize=None):
        
        self.st={}
        self.all_particle_df = pd.DataFrame()
        self.inputType={}
        self.pixelSize={}
        self.particle_df={}
        self.opticsGroups_dict={}
        for file in glob.glob(partLilstStarFile):
            fname=os.path.basename(file)
            self.st[fname]=starFileMeta(file)
            if "rlnCutOff" in self.st[fname].df.columns.values and len(glob.glob(partLilstStarFile))==1:
                self.inputType[fname]="pytomRelion5"
                self.pixelSize[fname]=self.st[fname].df['rlnTomoTiltSeriesPixelSize'].values[0]
                self.particle_df[fname]=self.st[fname].df
                self.opticsGroups_dict[fname]=None
                self.all_particle_df = pd.concat([self.all_particle_df, self.st[fname].df], ignore_index=True)
            if "rlnAutopickFigureOfMerit" in self.st[fname].df.columns.values and fname.find("Apx")>-1: 
                if tomoSize is None:
                    raise Exception("tomoSize is required for warpCoords")
                self.inputType[fname]="warpCoords"
                self.pixelSize[fname]=float(fname.split("_")[-1].replace("Apx.star",""))
                df=pd.DataFrame()
                df["rlnCenteredCoordinateXAngst"]=(self.st[fname].df['rlnCoordinateX']-tomoSize[0]/2)*float(self.pixelSize[fname])
                df["rlnCenteredCoordinateYAngst"]=(self.st[fname].df['rlnCoordinateY']-tomoSize[1]/2)*float(self.pixelSize[fname])
                df["rlnCenteredCoordinateZAngst"]=(self.st[fname].df['rlnCoordinateZ']-tomoSize[2]/2)*float(self.pixelSize[fname])
                angleColumns = ['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']
                df[angleColumns]=self.st[fname].df[angleColumns]
                df['rlnTomoName']= os.path.splitext(fname)[0]
                df['rlnLCCmax']=self.st[fname].df['rlnAutopickFigureOfMerit']
                df['rlnTomoTiltSeriesPixelSize']=self.pixelSize[fname]
                self.particle_df[fname]=df
                self.all_particle_df = pd.concat([self.all_particle_df, self.particle_df[fname]], ignore_index=True)
                self.opticsGroups_dict[fname]=None

                
    def writeList(self,outputPath,plType=None,tomoSize=None):
        
        if plType is None:
            plType=self.inputType
        
        if plType==self.inputType: 
            for fname in self.st:  
                self.st[fname].writeStar(outputPath)
        
        if plType=="warpCoords" and plType!=self.inputType:
            if tomoSize is None:
                raise Exception("tomoSize is required for warpCoords")
            tomos = self.all_particle_df['rlnTomoName'].unique()
            os.makedirs(outputPath, exist_ok=True)
            for tomo in tomos:
                tmp=tomo.split('_')
                tomoStarName = tomo + '_'.join(tmp[:-1])+'.tomostar'
                df = pd.DataFrame()
                coords=self.getImodCoords(tomo,tomoSize)
                angles=self.getAngles(tomo)
                scores=self.getScores(tomo)
                df['rlnCoordinateX']=coords[:,0]
                df['rlnCoordinateY']=coords[:,1]
                df['rlnCoordinateZ']=coords[:,2]
                df['rlnAngleRot']=angles[:,0]
                df['rlnAngleTilt']=angles[:,1]
                df['rlnAnglePsi']=angles[:,2]
                df['rlnMicrographName']=tomoStarName
                df['rlnAutopickFigureOfMerit']=scores
                st=starFileMeta(df)
                st.writeStar(os.path.join(outputPath,f'{tomo}.star'))
                    
                
    def writeImodModel(self,outPutFolder,diameterInAng,tomoSize,color="default",thick="default"):
        
        os.makedirs(outPutFolder, exist_ok=True)
        tomos = self.all_particle_df['rlnTomoName'].unique()
        if thick== "default":
            thick=2
        
        if color=="default":
            color=[0,255,0]
            
        for tomo in tomos:
            coords=self.getImodCoords(tomo,tomoSize)
            particle_txtname = os.path.join(outPutFolder, f'coords_{tomo}.txt')
            particle_modname = os.path.join(outPutFolder, f'coords_{tomo}.mod')
            np.savetxt(particle_txtname, coords, delimiter='\t',fmt='%.0f')
            radiusInPix=np.int32(diameterInAng/(next(iter(self.pixelSize.values()))*2))
            cmd = f'point2model {particle_txtname} {particle_modname} -sphere {radiusInPix} -scat -color {color[0]},{color[1]},{color[2]} -t {thick}'
            subprocess.run(cmd, shell=True)
        
    
    def getImodCoords(self,tomoName,tomoSize):    
        
        if tomoName is None:
            temp_df = self.all_particle_df 
        else:
            temp_df = self.all_particle_df[self.all_particle_df['rlnTomoName'] == tomoName]
        
        coords = temp_df[['rlnCenteredCoordinateXAngst', 'rlnCenteredCoordinateYAngst', 'rlnCenteredCoordinateZAngst']].values
        coords/=next(iter(self.pixelSize.values())) 
        coords+=np.array(tomoSize)/2
        coords=np.int32(coords)
        
        return coords
    def getAngles(self,tomoName):
        temp_df = self.all_particle_df[self.all_particle_df['rlnTomoName'] == tomoName]
        angles = temp_df[['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].values
        
        return angles
    
    def getScores(self,tomoName):
        temp_df = self.all_particle_df[self.all_particle_df['rlnTomoName'] == tomoName]
        scores = temp_df[['rlnLCCmax']].values
        
        return scores 