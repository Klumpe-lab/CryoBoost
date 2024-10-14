from src.rw.librw import starFileMeta,tiltSeriesMeta
from src.rw.librw import warpMetaData
import shlex,os,subprocess,select,sys,threading
import shutil,glob

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

def tsReconstruct(args):
    relProj=os.path.dirname(os.path.dirname(os.path.dirname(args.in_mics)))
    if relProj != "" and relProj is not None:
        relProj=relProj+"/"
    st=tiltSeriesMeta(args.in_mics,relProj)
    outputFolder=args.out_dir    
    warpTiltSeriesFoldSource=os.path.split(args.in_mics)[0]+"/warp_tiltseries"
    warpTiltSeriesFoldTarget=outputFolder+"/warp_tiltseries"
    
    print("generating: ",warpTiltSeriesFoldTarget)
    os.makedirs(warpTiltSeriesFoldTarget,exist_ok=True) 
    print("copying data: ",warpTiltSeriesFoldSource + "/*.xml to" + warpTiltSeriesFoldTarget)
    for f in glob.glob(warpTiltSeriesFoldSource + "/*.xml"):
        shutil.copy(f,warpTiltSeriesFoldTarget)
    print("copying data: ", os.path.split(args.in_mics)[0] + "/warp_tiltseries.settings to " + warpTiltSeriesFoldTarget)
    shutil.copy(os.path.split(args.in_mics)[0] + "/warp_tiltseries.settings",outputFolder)
    print("copying data: ", os.path.split(args.in_mics)[0] + "/tomostar to " + outputFolder)
    shutil.copytree(os.path.split(args.in_mics)[0] + "/tomostar",outputFolder+"/tomostar",dirs_exist_ok=True)

    # command=["WarpTools", "ts_reconstruct",
    #         "--settings", outputFolder + "/warp_tiltseries.settings",
    #         "--angpix" ,str(args.rescale_angpixs),
    #         "--halfmap_frames" ,str(args.halfmap_frames),
    #         "--deconv" ,str(args.deconv),
    #         "--perdevice",str(args.perdevice),
    #         ]
    
    command=["WarpTools", "ts_reconstruct",
            "--settings", outputFolder + "/warp_tiltseries.settings",
            "--angpix" ,str(args.rescale_angpixs),
            "--halfmap_frames" ,str(args.halfmap_frames),
            "--deconv" ,str(args.deconv),
            "--perdevice" ,str(args.perdevice),
            ]
    
    
    command_string = shlex.join(command)
    print(command_string)  

    try:
        #print("launching via subprocess")
        result = subprocess.run(command, check=True) #,capture_output=True, text=True) #, capture_output=True, text=True)          
    except subprocess.CalledProcessError as e:
        print("Error output:", e.stderr, file=sys.stderr)
        
    
    if result.returncode == 0:
        #adapt values here
        print("transfer from tsReconstruct still missing...not needed to proceed in warp")
        for index, row in st.all_tilts_df.iterrows():
            key=st.all_tilts_df.at[index,'cryoBoostKey']
            #st.all_tilts_df.at[index, 'cryoBoostXfPath'] = str(res.iloc[0]['folder']) + "/average/" + key + ".mrc" 
            # st.all_tilts_df.at[index, '_rlnTomoXTilt']= 
            # _rlnTomoYTilt #26
            # _rlnTomoZRot #27
            # _rlnTomoXShiftAngst #28
            # _rlnTomoYShiftAngst #29
        st.writeTiltSeries(outputFolder+"/tomograms.star")
        return 0
    else:
        return 1        





def tsCtf(args):
    relProj=os.path.dirname(os.path.dirname(os.path.dirname(args.in_mics)))
    if relProj != "" and relProj is not None:
        relProj=relProj+"/"
    st=tiltSeriesMeta(args.in_mics,relProj)
    framePixS=st.all_tilts_df["rlnMicrographOriginalPixelSize"][0]
    tiltAxis=st.all_tilts_df["rlnTomoNominalTiltAxisAngle"][0]
    volt=st.tilt_series_df.rlnVoltage[0]
    cs=st.tilt_series_df.rlnSphericalAberration[0]
    cAmp=st.tilt_series_df.rlnAmplitudeContrast[0]  
    outputFolder=args.out_dir    
    dataFold=outputFolder+"/tomostar"
    expPerTilt=st.all_tilts_df["rlnMicrographPreExposure"].sort_values().iloc[1]
    warpTiltSeriesFoldSource=os.path.split(args.in_mics)[0]+"/warp_tiltseries"
    warpTiltSeriesFoldTarget=outputFolder+"/warp_tiltseries"
    nrTilt=st.tilt_series_df.shape[0]
    if (int(args.auto_hand)>int(nrTilt)):
        nrAutoHand=nrTilt
    else:
        nrAutoHand=int(args.auto_hand)
    nrAutoHand=1
        
    print("generating: ",warpTiltSeriesFoldTarget)
    os.makedirs(warpTiltSeriesFoldTarget,exist_ok=True) 
    print("copying data: ",warpTiltSeriesFoldSource + "/*.xml to" + warpTiltSeriesFoldTarget)
    for f in glob.glob(warpTiltSeriesFoldSource + "/*.xml"):
        shutil.copy(f,warpTiltSeriesFoldTarget)
    print("copying data: ", os.path.split(args.in_mics)[0] + "/warp_tiltseries.settings to " + warpTiltSeriesFoldTarget)
    shutil.copy(os.path.split(args.in_mics)[0] + "/warp_tiltseries.settings",outputFolder)
    print("copying data: ", os.path.split(args.in_mics)[0] + "/tomostar to " + outputFolder)
    shutil.copytree(os.path.split(args.in_mics)[0] + "/tomostar",outputFolder+"/tomostar",dirs_exist_ok=True)
    # command=["WarpTools", "ts_ctf",
    #          "--settings", outputFolder + "/warp_tiltseries.settings",
    #          "--range_high","6",
    #          "--defocus_max", "8"]
    
    command=["WarpTools", "ts_ctf",
            "--settings", outputFolder + "/warp_tiltseries.settings",
            "--window" ,str(args.window),
            "--range_low" ,args.range_min_max.split(":")[0],
            "--range_high" ,args.range_min_max.split(":")[1],
            "--defocus_min" ,args.defocus_min_max.split(":")[0],
            "--defocus_max" ,args.defocus_min_max.split(":")[1],
            "--voltage" ,str(round(volt)),
            "--cs" ,str(cs),
            "--amplitude" ,str(cAmp),
            "--perdevice",str(args.perdevice),
            #"--auto_hand" ,str(nrAutoHand),
            ]
    
    command_string = shlex.join(command)
    print(command_string)  
    #os.system(command_string)
    
    try:
        #print("launching via subprocess")
        result = subprocess.run(command, check=True) #,capture_output=True, text=True) #, capture_output=True, text=True)          
    except subprocess.CalledProcessError as e:
        print("Error output:", e.stderr, file=sys.stderr)
        
    
    if result.returncode == 0:
        #adapt values here
        print("transfer from tsCTF still missing...not needed to proceed in warp")
        for index, row in st.all_tilts_df.iterrows():
            key=st.all_tilts_df.at[index,'cryoBoostKey']
            #st.all_tilts_df.at[index, 'cryoBoostXfPath'] = str(res.iloc[0]['folder']) + "/average/" + key + ".mrc" 
            # st.all_tilts_df.at[index, '_rlnTomoXTilt']= 
            # _rlnTomoYTilt #26
            # _rlnTomoZRot #27
            # _rlnTomoXShiftAngst #28
            # _rlnTomoYShiftAngst #29
        st.writeTiltSeries(outputFolder+"/ts_ctf_tilt_series.star")
        return 0
    else:
        return 1        
    

def tsAlignment(args):
    relProj=os.path.dirname(os.path.dirname(os.path.dirname(args.in_mics)))
    if relProj != "" and relProj is not None:
        relProj=relProj+"/"
    st=tiltSeriesMeta(args.in_mics,relProj)
    framePixS=st.all_tilts_df["rlnMicrographOriginalPixelSize"][0]
    tiltAxis=st.all_tilts_df["rlnTomoNominalTiltAxisAngle"][0]
    outputFolder=args.out_dir    
    dataFold=outputFolder+"/tomostar"
    expPerTilt=st.all_tilts_df["rlnMicrographPreExposure"].drop_duplicates().sort_values().iloc[1]
    warpFrameSeriesFold=st.all_tilts_df["rlnMicrographName"].sort_values().iloc[0]
    warpFrameSeriesFold=os.path.split(warpFrameSeriesFold)[0].replace("average","")
    
    print("generating: ",dataFold)
    os.makedirs(dataFold,exist_ok=True) 
    
    command=["WarpTools", "create_settings",
             "--folder_data", "tomostar",
             "--extension" ,"*.tomostar",
             "--folder_processing", "warp_tiltseries",
             "--output" , outputFolder + "/warp_tiltseries.settings",
             "--angpix" , str(framePixS),
             "--exposure",str(expPerTilt),
             "--tomo_dimensions",args.tomo_dimensions,
             ]
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
    
    print("++++++++++settings done++++++++++++++++")
    print("modoc pattern:",args.mdocWk)
    mdocFolder,mdocPattern = os.path.split(args.mdocWk)
    mdocPattern="*.mdoc"
    
    command=["WarpTools", "ts_import",
             "--mdocs",mdocFolder,
             "--pattern",mdocPattern,
             "--frameseries",warpFrameSeriesFold,
             "--output" ,dataFold,
             "--tilt_exposure",str(expPerTilt), 
             "--override_axis",str(tiltAxis),
            ]
    
    command_string = shlex.join(command)
    print(command_string)  
    try:
        result = subprocess.run(command, check=True) #, capture_output=True, text=True)          
    except subprocess.CalledProcessError as e:
        print("Error output:", e.stderr, file=sys.stderr) 
    
    print("generating: ",outputFolder + "/warp_tiltseries")
    os.makedirs(outputFolder + "/warp_tiltseries",exist_ok=True) 
    print("++++++++++Tiltseries import done++++++++++++++++")
    
    if (args.alignment_program=="Aretomo"):
    
        command=["WarpTools", "ts_aretomo",
                "--settings", outputFolder + "/warp_tiltseries.settings",
                "--angpix",str(args.rescale_angpixs),
                "--alignz",str(int(float(args.aretomo_sample_thickness)*10)),
                "--perdevice",str(args.perdevice),
                ]
        #if args.refine_tilt_axis:
            #-"--patches",str(args.aretomo_patches),
        #    command.append('--axis_iter 3')
        #    command.append('--axis_batch 5')
        
    else:
        command=["WarpTools", "ts_etomo_patches",
                "--settings", outputFolder + "/warp_tiltseries.settings",
                "--angpix",str(args.rescale_angpixs),
                ]
    command_string = shlex.join(command)
    print(command_string)  
    try:
        result = subprocess.run(command, check=True) #, capture_output=True, text=True)          
    except subprocess.CalledProcessError as e:
        print("Error output:", e.stderr, file=sys.stderr)     
    
    if result.returncode == 0:
        #adapt values here
        print("transfer from xf still missing ...not needed to proceed in warp")
        for index, row in st.all_tilts_df.iterrows():
            key=st.all_tilts_df.at[index,'cryoBoostKey']
            #st.all_tilts_df.at[index, 'cryoBoostXfPath'] = str(res.iloc[0]['folder']) + "/average/" + key + ".mrc" 
            # st.all_tilts_df.at[index, '_rlnTomoXTilt']= 
            # _rlnTomoYTilt #26
            # _rlnTomoZRot #27
            # _rlnTomoXShiftAngst #28
            # _rlnTomoYShiftAngst #29
        st.writeTiltSeries(outputFolder+"/aligned_tilt_series.star")
        
        return 0
    else:
        return 1        
               


    