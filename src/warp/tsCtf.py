import sys
from src.rw.librw import warpMetaData
from src.misc.system import run_wrapperCommand
from src.warp.libWarp import warpWrapperBase

class tsCtf(warpWrapperBase):
    def __init__(self,args,runFlag=None):
       
        super().__init__(args,runFlag=runFlag)
       #pass
        
    def createSettings(self):
        
        print("--------------create settings---------------------------")
        sys.stdout.flush()  
        self.copyWarpTiltSeriesMetaData(self.preJobFolder,self.args.out_dir)
    
    def runMainApp(self):    
        
        print("--------------tilt seriees ctf determination---------------------------")
        sys.stdout.flush()  
        
        if (int(self.args.auto_hand)>int(self.st.tsInfo.numTiltSeries)):
            nrAutoHand=self.st.tsInfo.numTiltSeries
        else:
            nrAutoHand=int(self.args.auto_hand)
        nrAutoHand=1
        
        command=["WarpTools", "ts_ctf",
            "--settings", self.args.out_dir + "/" + self.tsSettingsName,
            "--window" ,str(self.args.window),
            "--range_low" ,self.args.range_min_max.split(":")[0],
            "--range_high" ,self.args.range_min_max.split(":")[1],
            "--defocus_min" ,self.args.defocus_min_max.split(":")[0],
            "--defocus_max" ,self.args.defocus_min_max.split(":")[1],
            "--voltage" ,str(round(self.st.tsInfo.volt)),
            "--cs" ,str(self.st.tsInfo.cs),
            "--amplitude" ,str(self.st.tsInfo.cAmp),
            "--perdevice",str(self.args.perdevice),
            #"--auto_hand" ,str(nrAutoHand),
            ]
        self.result=run_wrapperCommand(command,tag="run_tsCtf",relionProj=self.relProj)
    
    def updateMetaData(self):
        wm=warpMetaData(self.args.out_dir+"/warp_tiltseries/*.xml")
        for index, row in self.st.all_tilts_df.iterrows():
            key=self.st.all_tilts_df.at[index,'cryoBoostKey']
            #res = wm.data_df.query(f"cryoBoostKey == '{key}'")
            #self.st.all_tilts_df.at[index, 'xxxxxx'] = str(res.iloc[0]['folder']) + "/average/" + key + ".mrc"
        self.st.writeTiltSeries(self.args.out_dir+"/ts_ctf_tilt_series.star")
    
    def checkResults(self):
        #check if important results exists and values are in range
        #set to 1 of something is missing self.result.returncode
        pass    
    def updateMetaData(self):
        wm=warpMetaData(self.args.out_dir+"/warp_tiltseries/*.xml")
        for index, row in self.st.all_tilts_df.iterrows():
            key=self.st.all_tilts_df.at[index,'cryoBoostKey']
            #res = wm.data_df.query(f"cryoBoostKey == '{key}'")
            #self.st.all_tilts_df.at[index, 'xxxxxx'] = str(res.iloc[0]['folder']) + "/average/" + key + ".mrc"
        self.st.writeTiltSeries(self.args.out_dir+"/ts_ctf_tilt_series.star")
        