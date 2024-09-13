from src.rw.librw import starFileMeta,tiltSeriesMeta
import shutil,os,subprocess
def fsMotionAndCtf(inputList,outputFolder,gain=None,threads=4):
    """
    fsMotionAndCtf
    """
    #st=starFileMeta(inputList)
    relProj=os.path.dirname(os.path.dirname(os.path.dirname(inputList)))
    if relProj != "" and relProj is not None:
        relProj=relProj+"/"
    st=tiltSeriesMeta(inputList,relProj)
    frameFold="../../"+os.path.dirname(st.all_tilts_df["rlnMicrographMovieName"][0])
    _,frameExt=os.path.splitext(st.all_tilts_df["rlnMicrographMovieName"][0])
    frameExt="*"+frameExt
    framePixS=st.all_tilts_df["rlnMicrographOriginalPixelSize"][0]
    
    command=["WarpTools", "create_settings",
             "--folder_data", frameFold,
             "--extension" ,frameExt,
             "--folder_processing", "warp_frameseries",
             "--output" , outputFolder + "/warp_frameseries.settings",
             "--angpix" , str(framePixS)
            ]
   
    if gain is not None:
        command.append("--gain_path " + gain.path)
    
    print(command)    
    result = subprocess.run(command, check=True, capture_output=True, text=True)          
    print("Command executed successfully:", result.stdout)
    print(result.stderr)        
    
    command=["WarpTools", "fs_motion_and_ctf",
             "--settings", outputFolder + "/warp_frameseries.settings",
             "--m_grid" ,"1x1x3",
             "--c_grid", "1x1x1",
             "--c_range_max" , "7",
             "--c_defocus_max" ,"8",
             "--c_use_sum", 
             "--out_averages",
             "--out_average_halves",
             "--perdevice","6"
            ]
    print(command)    
    result = subprocess.run(command, check=True, capture_output=True, text=True)          
    print("Command executed successfully:", result.stdout)    
    
    #add info to star-+
    st.writeTiltSeries(outputFolder+"/fs_motion_and_ctf.star")
    
    