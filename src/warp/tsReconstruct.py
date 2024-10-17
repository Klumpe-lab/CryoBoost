import sys
from src.rw.librw import warpMetaData
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
                ]
        self.result=run_wrapperCommand(command,tag="run_tsReconstruct",relionProj=self.relProj)
    
    def updateMetaData(self):
        wm=warpMetaData(self.args.out_dir+"/warp_tiltseries/*.xml")
        for index, row in self.st.all_tilts_df.iterrows():
            key=self.st.all_tilts_df.at[index,'cryoBoostKey']
            #res = wm.data_df.query(f"cryoBoostKey == '{key}'")
            #self.st.all_tilts_df.at[index, 'xxxxxx'] = str(res.iloc[0]['folder']) + "/average/" + key + ".mrc"
        self.st.writeTiltSeries(self.args.out_dir+"/tomograms.star")    
    def checkResults(self):
        #check if important results exists and values are in range
        #set to 1 of something is missing self.result.returncode
        pass        