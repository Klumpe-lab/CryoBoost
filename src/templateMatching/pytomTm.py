import sys,os
from distutils.util import strtobool
from src.misc.system import run_wrapperCommand
from src.templateMatching.libTemplateMatching import templateMatchingWrapperBase


class pytomTm(templateMatchingWrapperBase):
    def __init__(self,args,runFlag=None):
       
        super().__init__(args,runFlag=runFlag)
       #pass
        
    def prepareInputs(self):
        
        print("--------------generate files for pytom---------------------------")
        sys.stdout.flush()  
        self.generatePytomInputFiles(columnName="rlnTomoNominalStageTiltAngle",tag="tiltAngle",ext=".tlt")
        self.generatePytomInputFiles(columnName="rlnDefocusU",tag="defocus")
        self.generatePytomInputFiles(columnName="rlnMicrographPreExposure",tag="dose")

     
    def runMainApp(self):    
        
        print("--------------run template matching---------------------------")
        sys.stdout.flush()  
        os.makedirs(self.args.out_dir + "tmResults",exist_ok=True)
        
        constParams=["-t",self.args.template,
                     "-d",self.args.out_dir + "tmResults",
                     "-m",self.args.templateMask,
                     "--angular-search",self.args.angularSearch,
                     "--voltage",str(self.st.tsInfo.volt),
                     "--spherical-aberration",str(self.st.tsInfo.cs),
                     "--amplitude-contrast",str(self.st.tsInfo.cAmp),
                     "--per-tilt-weighting",
                     "-g", "0",
                     "--log","debug"]
        
        volumes=self.st.tilt_series_df[[self.args.volume_column,"rlnTomoName"]]
        z=0
        for row in volumes.itertuples():
            z+=1
            volumeName=row[1]
            tomoName=row[2]
            print("  --> processing " + tomoName + ": " + str(z) + " of " + str(len(volumes)) + " tomograms", flush=True)
            command=["pytom_match_template.py", 
                    "-v", volumeName, 
                    "--tilt-angles",self.args.out_dir+"/tiltAngleFiles/"+tomoName+".tlt",
                    ]
            if bool(strtobool(self.args.ctfWeight)):            
                    command.extend(["--defocus",self.args.out_dir+"/defocusFiles/"+tomoName+".txt"])
            if bool(strtobool(self.args.doseWeight)):            
                    command.extend(["--dose-accumulation",self.args.out_dir+"/doseFiles/"+tomoName+".txt",])
            command.extend(constParams)
            self.result=run_wrapperCommand(command,tag="run_template_matching",relionProj=self.relProj)
    
    
    def generatePytomInputFiles(self,columnName,tag,ext=".txt"):
        
        outFold=self.args.out_dir + os.path.sep + tag + "Files" + os.path.sep
        os.makedirs(outFold,exist_ok=True)
        tomoNames=self.st.tilt_series_df["rlnTomoName"]
        print("  --> generating " + str(len(tomoNames)) + " " + tag + " Files",end="", flush=True)
        for tomoName in tomoNames:
            OneColumnOneTomo=self.st.all_tilts_df.query("rlnTomoName == @tomoName")[columnName]
            OneColumnOneTomo.to_csv(outFold + tomoName + ext, index=False, header=False)
            print(".", end="",flush=True)
        print("done!")     
    
    
    def updateMetaData(self):
        pass
        
    def checkResults(self):
        #check if important results exists and values are in range
        #set to 1 of something is missing self.result.returncode
        pass        
    def genTiltFileFromTiltSeries(self):
        
        pass
    