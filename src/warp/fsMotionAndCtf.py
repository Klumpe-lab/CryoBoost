
import os,subprocess,shlex,sys
from src.rw.librw import tiltSeriesMeta,warpMetaData
from src.misc.system import run_wrapperCommand

class fsMotionAndCtf():
    def __init__(self,args,runFlag=None):
       
        self.args=args
        relProj=os.path.dirname(os.path.dirname(os.path.dirname(args.in_mics)))
        if relProj != "" and relProj is not None:
            relProj=relProj+"/"
        self.st=tiltSeriesMeta(args.in_mics,relProj)
        self.args=args
        if (relProj==""):
            relProj="./"
        self.relProj=relProj
        if runFlag=="Full":
            self.run()
                
        
    def run(self):
        self.createSettings()
        self.runMotionAndCtf()
        self.update_tiltseries_data()
        self.check_resutls()
        
        
    def createSettings(self):
        
        command=["WarpTools", "create_settings",
                "--folder_data", "../../"+self.st.tsInfo.frameFold,
                "--extension" ,"*"+self.st.tsInfo.frameExt,
                "--folder_processing", "warp_frameseries",
                "--output" , self.args.out_dir + "/warp_frameseries.settings",
                "--angpix" , str(self.st.tsInfo.framePixS)
                ]
        if self.st.tsInfo.frameExt=="*.eer":
            command.extend(["--eer_ngroups", str(self.args.eer_ngroups)])
        
        if self.args.gain_path!="None":
            command.extend(["--gain_path",self.args.gain_path])
        
        if self.args.gain_operations is not None:
            if self.args.gain_operations.find("flip_x") != -1:
                command.append("--gain_flip_x")
            if self.args.gain_operations.find("flip_y") != -1:
                command.append("--gain_flip_y")
            if self.args.gain_operations.find("gain_transpose") != -1:
                command.append("--gain_gain_transpose")
        print("relPB4",self.relProj)
        self.result=run_wrapperCommand(command,tag="fsMotionAndCtf-Settings",relionProj=self.relProj)
            
    def runMotionAndCtf(self):    
        
        print("generating: ",self.args.out_dir + "/warp_frameseries")
        sys.stdout.flush()
        os.makedirs(self.args.out_dir + "/warp_frameseries",exist_ok=True)
        command=["WarpTools", "fs_motion_and_ctf",
                "--settings", self.args.out_dir + "/warp_frameseries.settings",
                "--m_grid" ,self.args.m_grid,
                "--m_range_min" ,self.args.m_range_min_max.split(":")[0],
                "--m_range_max" ,self.args.m_range_min_max.split(":")[1],
                "--m_bfac" ,str(self.args.m_bfac),
                "--c_grid",self.args.c_grid,
                "--c_window" ,str(self.args.c_window),
                "--c_range_min" ,self.args.c_range_min_max.split(":")[0],
                "--c_range_max" ,self.args.c_range_min_max.split(":")[1],
                "--c_defocus_min" ,self.args.c_defocus_min_max.split(":")[0],
                "--c_defocus_max" ,self.args.c_defocus_min_max.split(":")[1],
                "--c_voltage" ,str(round(self.st.tsInfo.volt)),
                "--c_cs" ,str(self.st.tsInfo.cs),
                "--c_amplitude" ,str(self.st.tsInfo.cAmp),
                "--out_averages",
                "--out_skip_first", str(self.args.out_skip_first),
                "--out_skip_last", str(self.args.out_skip_last),
                "--perdevice", str(self.args.perdevice),
                ]
        
        if self.args.out_average_halves!=False:
            command.append("--out_average_halves")
        
        if self.args.c_use_sum!=False:
            command.append("--c_use_sum")
       
        self.result=run_wrapperCommand(command,tag="run_fsMotionAndCtf",relionProj=self.relProj)
        
        
    def update_tiltseries_data(self):
        wm=warpMetaData(self.args.out_dir+"/warp_frameseries/*.xml")
        for index, row in self.st.all_tilts_df.iterrows():
            key=self.st.all_tilts_df.at[index,'cryoBoostKey']
            res = wm.data_df.query(f"cryoBoostKey == '{key}'")
            self.st.all_tilts_df.at[index, 'rlnMicrographName'] = str(res.iloc[0]['folder']) + "/average/" + key + ".mrc"
            self.st.all_tilts_df.at[index, 'rlnMicrographNameEven'] = str(res.iloc[0]['folder']) + "/average/even/" + key + ".mrc"
            self.st.all_tilts_df.at[index, 'rlnMicrographNameOdd'] = str(res.iloc[0]['folder']) + "/average/odd/" + key + ".mrc"
            self.st.all_tilts_df.at[index, 'rlnMicrographMetadata']="None"
            self.st.all_tilts_df.at[index, 'rlnAccumMotionTotal']=-1
            self.st.all_tilts_df.at[index, 'rlnAccumMotionEarly']=-1
            self.st.all_tilts_df.at[index, 'rlnAccumMotionLate']=-1
            self.st.all_tilts_df.at[index, 'rlnCtfImage'] = str(res.iloc[0]['folder']) + "/powerspectrum/" + key + ".mrc"
            self.st.all_tilts_df.at[index, 'rlnDefocusU'] = str(res.iloc[0]['defocus_value']) 
            self.st.all_tilts_df.at[index, 'rlnDefocusV'] = str(res.iloc[0]['defocus_value'])
            self.st.all_tilts_df.at[index, 'rlnCtfAstigmatism'] = str(res.iloc[0]['defocus_delta'])
            self.st.all_tilts_df.at[index, 'rlnDefocusAngle'] = str(res.iloc[0]['defocus_angle'])
            self.st.all_tilts_df.at[index, 'rlnCtfFigureOfMerit']="None"
            self.st.all_tilts_df.at[index, 'rlnCtfMaxResolution']="None"
            self.st.all_tilts_df.at[index, 'rlnMicrographMetadata']="None"
        self.st.writeTiltSeries(self.args.out_dir+"/fs_motion_and_ctf.star")
         
    def check_resutls(self):
        #check if important results exists and values are in range
        #set to 1 of something is missing self.result.returncode
        pass
        