from src.rw.librw import starFileMeta,tiltSeriesMeta
from src.rw.librw import warpMetaData
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


def fsMotionAndCtf(args):
    """
    fsMotionAndCtf

    """
    
    relProj=os.path.dirname(os.path.dirname(os.path.dirname(args.in_mics)))
    if relProj != "" and relProj is not None:
        relProj=relProj+"/"
    st=tiltSeriesMeta(args.in_mics,relProj)
    frameFold="../../"+os.path.dirname(st.all_tilts_df["rlnMicrographMovieName"][0])
    _,frameExt=os.path.splitext(st.all_tilts_df["rlnMicrographMovieName"][0])
    frameExt="*"+frameExt
    framePixS=st.all_tilts_df["rlnMicrographOriginalPixelSize"][0]
    volt=st.tilt_series_df.rlnVoltage[0]
    cs=st.tilt_series_df.rlnSphericalAberration[0]
    cAmp=st.tilt_series_df.rlnAmplitudeContrast[0]    

    
    outputFolder=args.out_dir    
    
    command=["WarpTools", "create_settings",
             "--folder_data", frameFold,
             "--extension" ,frameExt,
             "--folder_processing", "warp_frameseries",
             "--output" , outputFolder + "/warp_frameseries.settings",
             "--angpix" , str(framePixS)
             ]
    if frameExt=="*.eer":
        command.extend(["--eer_ngroups", str(args.eer_ngroups)])
    
    if args.gain_path!="None":
        command.extend(["--gain_path",args.gain_path])
    
    if args.gain_operations is not None:
        if args.gain_operations.find("flip_x") != -1:
            command.append("--gain_flip_x")
        if args.gain_operations.find("flip_y") != -1:
            command.append("--gain_flip_y")
        if args.gain_operations.find("gain_transpose") != -1:
            command.append("--gain_gain_transpose")
        
    command_string = shlex.join(command)
    print(command_string)  
    try:
        result = subprocess.run(command, check=True) #, capture_output=True, text=True)          
    except subprocess.CalledProcessError as e:
        print("Error output:", e.stderr, file=sys.stderr)
    
    
    print("generating: ",outputFolder + "/warp_frameseries")
    os.makedirs(outputFolder + "/warp_frameseries",exist_ok=True)
    
    command=["WarpTools", "fs_motion_and_ctf",
             "--settings", outputFolder + "/warp_frameseries.settings",
             "--m_grid" ,args.m_grid,
             "--m_range_min" ,args.m_range_min_max.split(":")[0],
             "--m_range_max" ,args.m_range_min_max.split(":")[1],
             "--m_bfac" ,str(args.m_bfac),
             "--c_grid",args.c_grid,
             "--c_window" ,str(args.c_window),
             "--c_range_min" ,args.c_range_min_max.split(":")[0],
             "--c_range_max" ,args.c_range_min_max.split(":")[1],
             "--c_defocus_min" ,args.c_defocus_min_max.split(":")[0],
             "--c_defocus_max" ,args.c_defocus_min_max.split(":")[1],
             "--c_voltage" ,str(round(volt)),
             "--c_cs" ,str(cs),
             "--c_amplitude" ,str(cAmp),
             "--out_averages",
             "--out_skip_first", str(args.out_skip_first),
             "--out_skip_last", str(args.out_skip_last),
             "--perdevice", str(args.perdevice),
             ]
    
    if args.out_average_halves!=False:
        command.append("--out_average_halves")
    
    if args.c_use_sum!=False:
        command.append("--c_use_sum")
    
    command_string = shlex.join(command)
    print(command_string)
    
    try:
        result = subprocess.run(command, check=True)#, capture_output=True, text=True)
    except:
        print("Error output:", e.stderr, file=sys.stderr)
    
    if result.returncode == 0:
        wm=warpMetaData(outputFolder+"/warp_frameseries/*.xml")
        for index, row in st.all_tilts_df.iterrows():
            key=st.all_tilts_df.at[index,'cryoBoostKey']
            res = wm.data_df.query(f"cryoBoostKey == '{key}'")
            st.all_tilts_df.at[index, 'rlnMicrographName'] = str(res.iloc[0]['folder']) + "/average/" + key + ".mrc"
            st.all_tilts_df.at[index, 'rlnMicrographNameEven'] = str(res.iloc[0]['folder']) + "/average/even/" + key + ".mrc"
            st.all_tilts_df.at[index, 'rlnMicrographNameOdd'] = str(res.iloc[0]['folder']) + "/average/odd/" + key + ".mrc"
            st.all_tilts_df.at[index, 'rlnMicrographMetadata']="None"
            st.all_tilts_df.at[index, 'rlnAccumMotionTotal']=-1
            st.all_tilts_df.at[index, 'rlnAccumMotionEarly']=-1
            st.all_tilts_df.at[index, 'rlnAccumMotionLate']=-1
            st.all_tilts_df.at[index, 'rlnCtfImage'] = str(res.iloc[0]['folder']) + "/powerspectrum/" + key + ".mrc"
            st.all_tilts_df.at[index, 'rlnDefocusU'] = str(res.iloc[0]['defocus_value']) 
            st.all_tilts_df.at[index, 'rlnDefocusV'] = str(res.iloc[0]['defocus_value'])
            st.all_tilts_df.at[index, 'rlnCtfAstigmatism'] = str(res.iloc[0]['defocus_delta'])
            st.all_tilts_df.at[index, 'rlnDefocusAngle'] = str(res.iloc[0]['defocus_angle'])
            st.all_tilts_df.at[index, 'rlnCtfFigureOfMerit']="None"
            st.all_tilts_df.at[index, 'rlnCtfMaxResolution']="None"
            st.all_tilts_df.at[index, 'rlnMicrographMetadata']="None"
        st.writeTiltSeries(outputFolder+"/fs_motion_and_ctf.star")
        return 0
    else:
        return 1
    