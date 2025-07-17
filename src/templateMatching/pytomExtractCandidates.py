import sys,os,glob,subprocess
from distutils.util import strtobool
from src.misc.system import run_wrapperCommand
from src.templateMatching.libTemplateMatching import templateMatchingWrapperBase
from src.rw.particleList import particleListMeta
from src.rw.librw import starFileMeta
import pandas as pd
import shlex

class pytomExtractCandidates(templateMatchingWrapperBase):
    def __init__(self,args,runFlag=None):
        super().__init__(args,runFlag=runFlag)
       #pass
        
    def prepareInputs(self):
        
        print("--------------prepare inputs for extraction-------------------")
        print(self.st.tsInfo.tomoSize)
        sys.stdout.flush()  
        tmOutFold=self.args.out_dir + "tmResults"
        os.makedirs(tmOutFold,exist_ok=True)    
        self.getFilesByWildCard(self.inputFold+"/tmResults/*.mrc",tmOutFold)
        self.getFilesByWildCard(self.inputFold+"/tmResults/*.json",tmOutFold,copy_files=True)
        
    def runMainApp(self):
        print("--------------run candidate extraction-------------------------")
        sys.stdout.flush() 
        if self.args.apixScoreMap=="auto":
            pixs=float(self.st.tilt_series_df["rlnTomoTiltSeriesPixelSize"][0])*float(self.st.tilt_series_df["rlnTomoTomogramBinning"][0]) 
        else:
            pixs=float(self.args.apixScoreMap)
        
        self.pixs=pixs
        self.radiusInPix=int(float(self.args.particleDiameterInAng)/2.0/pixs)
        constParams=["-n",str(self.args.maxNumParticles),
                     "--particle-diameter",str(self.radiusInPix*pixs),#"-r", str(self.radiusInPix),#"--particle-diameter",str(self.radiusInPix), #pytom radius in pixels
                     "--relion5-compat",
                     "--log","debug"]
      
        if self.args.cutOffMethod=="NumberOfFalsePositives":            
            constParams.extend(["--number-of-false-positives",str(self.args.cutOffValue)])
        if self.args.cutOffMethod=="ManualCutOff":            
            constParams.extend(["-c",str(self.args.cutOffValue)])
        if self.args.scoreFilterMethod=="tophat":
            constParams.extend(["--tophat-filter"])
            if self.args.scoreFilterValue!="None":
                constParams.extend(["--tophat-connectivity",self.args.scoreFilterValue.split[0]])
                constParams.extend(["--tophat-bins",self.args.scoreFilterValue.split[1]])
                
        
        tmOutFold=self.args.out_dir + "tmResults"
        jobFiles=glob.glob(tmOutFold+"/*_job.json") 
        print("starting to extract " + str(len(jobFiles)))
        z=1
        for job in jobFiles:    
            print("  --> processing " + job + ": " + str(z) + " of " + str(len(jobFiles)) + " scores", flush=True)
            command=["pytom_extract_candidates.py", "-j", job] 
            command.extend(constParams)
        command_pre = " ".join(shlex.quote(p) for p in command)
        #command_post="'" + command_pre + "'"
        full_command = ["apptainer", "run", "--nv", "/groups/klumpe/software/PyTom_tm/PyTom_tm.sif",command_pre]
        self.result=run_wrapperCommand(full_command,tag="run_candidate_extraction",relionProj=self.relProj)
        z+=1
            
    def updateMetaData(self):
        self.st.writeTiltSeries(self.args.out_dir+"/tomograms.star")
        print("--------------combining outputs---------------------------", flush=True)
        tmOutFold=self.args.out_dir + "tmResults"
        command=["pytom_merge_stars.py", 
                    "-i", tmOutFold,
                    "-o",self.args.out_dir + "/candidates.star"] 
        command_pre = " ".join(shlex.quote(p) for p in command)
        #command_post="'" + command_pre + "'"
        full_command = ["apptainer", "run", "--nv", "/groups/klumpe/software/PyTom_tm/PyTom_tm.sif",command_pre]
        self.result=run_wrapperCommand(full_command,tag="run_combineFiles",relionProj=self.relProj)
        stCand=starFileMeta(self.args.out_dir + "/candidates.star")
        rmStr=float(stCand.df.rlnTomoTiltSeriesPixelSize[0])
        rmStr= f"_{round(rmStr, 2):.2f}Apx" 
        stCand.df.rlnTomoName=stCand.df.rlnTomoName.str.replace(rmStr,"")
        stCand.writeStar(self.args.out_dir + "/candidates.star")
        df = pd.DataFrame({
            'rlnTomoParticlesFile': [self.args.out_dir + "/candidates.star"],
            'rlnTomoTomogramsFile': [self.args.out_dir + "/tomograms.star"]
         })
        stOpt=starFileMeta(df)
        stOpt.writeStar(self.args.out_dir + "/optimisation_set.star")
        
        print("-----generating visualisation---------------------------", flush=True)
        pl=particleListMeta(self.args.out_dir + "/candidates.star")    
        pl.writeImodModel(self.args.out_dir + "/vis/imodPartRad/",int(self.args.particleDiameterInAng),self.st.tsInfo.tomoSize)
        pl.writeImodModel(self.args.out_dir + "/vis/imodCenter/",int(8*self.pixs),self.st.tsInfo.tomoSize,color=[255,0,0],thick=4)
        print("-----generating warp output---------------------------",flush=True)
        print("  --> writing to " + "candidatesWarp", flush=True)
        pl.writeList(self.args.out_dir + "/candidatesWarp/",'warpCoords',self.st.tsInfo.tomoSize)
        
    def checkResults(self):
        pass
