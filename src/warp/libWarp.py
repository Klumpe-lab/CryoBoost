from src.rw.librw import starFileMeta,tiltSeriesMeta
import shlex,os,subprocess,select,sys,threading

def read_stream(stream, callback):
    print("above loop")
    while True:
        #print("reading stream")
        output = stream.read()
        if output:
            #callback(output.replace('\r', '\n'))
            callback(output)
        else:
            print("breaking")
            break


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
    
    
    command_string = shlex.join(command)
    print("************************************************")
    print("********settings*********************************")
    print(command_string)  
    result = subprocess.run(command, check=True, capture_output=True, text=True)          
    print("Command executed successfully:", result.stdout)
    print("********  settings done*********************************")    
    
    
    print("generating: ",outputFolder + "/warp_frameseries")
    os.makedirs(outputFolder + "/warp_frameseries",exist_ok=True)
    
    
    command=["WarpTools", "fs_motion_and_ctf",
             "--settings", outputFolder + "/warp_frameseries.settings",
             "--m_grid" ,"1x1x3",
             "--c_grid", "1x1x1",
             "--c_range_max" , "7",
             "--c_defocus_max" ,"8",
             "--c_use_sum", 
             "--out_averages",
             "--out_average_halves",
             "--perdevice","4"
            ]
    command_string = shlex.join(command)
        
    #subprocess.run(command)
    print("************************************************")
    print("********fs-motion*********************************")
    print(command_string)
    #result = subprocess.run(command, check=True, capture_output=True, text=True)
    os.system(command_string)
    #print("Command executed successfully:", result.stdout)
    print("********fs-motion done*********************************")
    
    #add info to star-+
    st.writeTiltSeries(outputFolder+"/fs_motion_and_ctf.star")
    
    