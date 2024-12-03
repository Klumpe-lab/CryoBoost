import sys,os
from src.rw.librw import warpMetaData,starFileMeta
from src.misc.system import run_wrapperCommand
from src.warp.libWarp import warpWrapperBase

class tsReconstruct(warpWrapperBase):
    def __init__(self,args,runFlag=None):
       
        super().__init__(args,runFlag=runFlag)
       #pass
        
    def createSettings(self):
        
        print("--------------create settings---------------------------")
        sys.stdout.flush()  
        self.copyWarpTiltSeriesMetaData(self.preJobFolder,self.args.out_dir)
    
    def runMainApp(self):    
        
        print("--------------reconstruct tomograms---------------------------")
        sys.stdout.flush()  
        command=["WarpTools", "ts_reconstruct",
                "--settings", self.args.out_dir + "/" + self.tsSettingsName,
                "--angpix" ,str(self.args.rescale_angpixs),
                "--halfmap_frames" ,str(self.args.halfmap_frames),
                "--deconv" ,str(self.args.deconv),
                "--perdevice" ,str(self.args.perdevice),
                "--dont_invert"
                ]
        self.result=run_wrapperCommand(command,tag="run_tsReconstruct",relionProj=self.relProj)
    
    def updateMetaData(self):
        recRes=format(float(self.args.rescale_angpixs),'.2f')
        #update information for tomograms
        wm=warpMetaData(self.args.out_dir+"/warp_tiltseries/*.xml")
        for index, row in self.st.all_tilts_df.iterrows():
            key=self.st.all_tilts_df.at[index,'cryoBoostKey']
            key=os.path.splitext(key)[0]
            res = wm.data_df.query(f"cryoBoostKey == '{key}'") 
            #TODO Add information for each tilt here
            
        self.st.writeTiltSeries(self.args.out_dir+"/tomograms.star")
        #Just udate the master tilseries star
        st=starFileMeta(self.args.out_dir+"/tomograms.star")
        for index, row in st.df.iterrows():
            #tN=st.df.at(index,['rlnTomoName'])
            tN = st.df.at[index, 'rlnTomoName']
            recName=self.args.out_dir + os.path.sep + self.tsFolderName + "/reconstruction/" + tN + "_" + recRes +"Apx.mrc"
            st.df.at[index, 'rlnTomoReconstructedTomogram'] = recName
            st.df.at[index, 'rlnTomoTiltSeriesPixelSize'] = self.args.rescale_angpixs
            st.df.at[index, 'rlnTomoTomogramBinning']=float(self.args.rescale_angpixs)/float(self.st.tsInfo.framePixS)
        print("writing updated star")                            
        st.writeStar(self.args.out_dir+"/tomograms.star")
            
    def checkResults(self):
        #check if important results exists and values are in range
        #set to 1 of something is missing self.result.returncode
        pass        