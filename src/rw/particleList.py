import subprocess
import numpy as np
import os
import pandas as pd
from src.rw.librw import starFileMeta

class particleListMeta:
    """
    Class for handling pickList metadata.

    Args:
      
    """

    def __init__(self, partLilstStarFile=None):
        """
        Initializes the tiltSeriesMeta class.
        """
        self.partLilstStarFile = None
        self.partList = None
       
        if (partLilstStarFile is not None):
            self.partLilstStarFile=partLilstStarFile
            self.partList_df=self.read(partLilstStarFile)

    def addItem(self,coord,angle,score,tomoName,format):
        pass
    
    def read(self,partLilstStarFile):
        st=starFileMeta(partLilstStarFile)

        #determine type of input list
        df=st.df
        self.pixelSize=df['rlnTomoTiltSeriesPixelSize'].values[0]

        return df
    
    def writeList(self,outputPath,plType,tomoSize):
        
        if plType=="warpCoords":
            tomos = self.partList_df['rlnTomoName'].unique()
            os.makedirs(outputPath, exist_ok=True)
            for tomo in tomos:
                tmp=tomo.split('_')
                tomoStarName = '_'.join(tmp[:-1])+'.tomostar'
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
                    
                
    def writeImodModel(self,outPutFolder,diameterInAng,tomoSize,color="default"):
        
        os.makedirs(outPutFolder, exist_ok=True)
        tomos = self.partList_df['rlnTomoName'].unique()
        if color=="default":
            color=[0,255,0]
        
        for tomo in tomos:
            coords=self.getImodCoords(tomo,tomoSize)
            particle_txtname = os.path.join(outPutFolder, f'coords_{tomo}.txt')
            particle_modname = os.path.join(outPutFolder, f'coords_{tomo}.mod')
            np.savetxt(particle_txtname, coords, delimiter='\t',fmt='%.0f')
            radiusInPix=np.int32(diameterInAng/(self.pixelSize*2))
            cmd = f'point2model {particle_txtname} {particle_modname} -sphere {radiusInPix} -scat -color {color[0]},{color[1]},{color[2]} -t 2'
            subprocess.run(cmd, shell=True)
        
    
    def getImodCoords(self,tomoName,tomoSize):    
       
        temp_df = self.partList_df[self.partList_df['rlnTomoName'] == tomoName]
        coords = temp_df[['rlnCenteredCoordinateXAngst', 'rlnCenteredCoordinateYAngst', 'rlnCenteredCoordinateZAngst']].values
        coords/=self.pixelSize
        coords+=np.array(tomoSize)/2
        coords=np.int32(coords)
        
        return coords
    def getAngles(self,tomoName):
        temp_df = self.partList_df[self.partList_df['rlnTomoName'] == tomoName]
        angles = temp_df[['rlnAngleRot', 'rlnAngleTilt', 'rlnAnglePsi']].values
        
        return angles
    
    def getScores(self,tomoName):
        temp_df = self.partList_df[self.partList_df['rlnTomoName'] == tomoName]
        scores = temp_df[['rlnCutOff']].values
        
        return scores 