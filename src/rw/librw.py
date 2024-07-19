# %%

import yaml
import os
import starfile
import subprocess
import glob
import tempfile

#from lib.functions import calculate_dose_rate_per_pixel, extract_eer_from_header
class cbconfig:
  def __init__(self,configPath):
    self.configPath = configPath
    self.read_config()
    self.get_microscopePreSetNames()

  def read_config(self):
    """
    reads a configuration file in yaml format.
    
    Args:
      filename (str): name of the .yaml file.
    
    Returns: 
      dict: dictioanry with paramName and data.
    """
    with open(self.configPath) as f:
      self.confdata = yaml.load(f, Loader=yaml.FullLoader)
  
  def getJobComputingParams(self,comReq,doNodeSharing):    
       self.confdata["computing"]["JOBTypes"]
       confComp=self.confdata["computing"]
       jobType=None
       for entry in confComp["JOBTypes"]:
         for job in confComp["JOBTypes"][entry]:
            if job == comReq[0]:
              jobType=entry
              break
       
       if (jobType == None):
         compParams=None
         return compParams 
       
       partionSetup= self.confdata["computing"][comReq[2]]
       kMPIperNode=self.get_alias_reverse(comReq[0],"MPIperNode")
       kNrGPU=self.get_alias_reverse(comReq[0],"NrGPU")
       kNrNodes=self.get_alias_reverse(comReq[0],"NrNodes")
       kPartName=self.get_alias_reverse(comReq[0],"PartionName")
       kMemory=self.get_alias_reverse(comReq[0],"MemoryRAM")
       compParams={}
       compParams[kPartName]=comReq[2]
       compParams[kMemory]=partionSetup["RAM"]
       NodeSharing= self.confdata["computing"]["NODE-Sharing"]
       if (doNodeSharing and (comReq[2] in NodeSharing["ApplyTo"])):
         compParams[kMemory]=str(round(int(partionSetup["RAM"][:-1])/2))+"G"
       gpuIDString=":".join(str(i) for i in range(0,partionSetup["NrGPU"]))
       maxNodes= self.confdata["computing"]["JOBMaxNodes"]
       
      
       if (comReq[0] in maxNodes.keys()):  
          if (comReq[1]>maxNodes[comReq[0]][0]):
              comReq[1]=maxNodes[comReq[0]][0]
       
       if (jobType == "CPU-MPI"):
         compParams[kMPIperNode]=partionSetup["NrCPU"]
         compParams["nr_mpi"]=partionSetup["NrCPU"]*comReq[1]  
         compParams[kNrGPU]=0
         compParams[kNrNodes]=comReq[1] 
         compParams["nr_threads"]=1
         if (doNodeSharing and comReq[2] in NodeSharing["ApplyTo"]):
            compParams[kMPIperNode]=partionSetup["NrCPU"]-(partionSetup["NrGPU"]*NodeSharing["CPU-PerGPU"]) 
            compParams["nr_mpi"]=compParams[kMPIperNode]*comReq[1]
            
       if (jobType == "CPU-2MPIThreads"):
         compParams[kMPIperNode]=2
         compParams["nr_mpi"]=compParams[kMPIperNode]*comReq[1]  
         compParams[kNrGPU]=0
         compParams[kNrNodes]=comReq[1] 
         compParams["nr_threads"]=round(partionSetup["NrCPU"]/2)
         if (doNodeSharing and comReq[2] in NodeSharing["ApplyTo"]):
            compParams["nr_threads"]=compParams["nr_threads"]-round(partionSetup["NrGPU"]*NodeSharing["CPU-PerGPU"]/2)
       
       if (jobType == "GPU-OneProcess") or (jobType == "GPU-OneProcessOneGPU"):
         compParams[kMPIperNode]=1
         compParams["nr_mpi"]=1  
         compParams[kNrGPU]=partionSetup["NrGPU"]
         compParams[kNrNodes]=1
         compParams["nr_threads"]=1
         compParams["gpu_ids"]=gpuIDString
       
       if (jobType == "GPU-OneProcessOneGPU"):
         compParams["gpu_ids"]=0
         compParams[kNrGPU]=1
       
       if (jobType == "GPU-ThreadsOneNode"):
         compParams[kMPIperNode]=1
         compParams["nr_mpi"]=1  
         compParams[kNrGPU]=partionSetup["NrGPU"]
         compParams[kNrNodes]=1 
         compParams["nr_threads"]=round(partionSetup["NrCPU"]/1)
         if (doNodeSharing and comReq[2] in NodeSharing["ApplyTo"]):
            compParams["nr_threads"]=compParams["nr_threads"]-round(partionSetup["NrGPU"]*NodeSharing["CPU-PerGPU"])
       
        
       return compParams 
        
  def get_alias(self,job, parameter):
    """
    some inputs used by Relion are not self-explanatory (eg. qsub_extra2) so a yaml list was created to change the 
    respective name that is displayed while still keeping the original name for writing the data.

    Args:
      job (str): job name the parameter is used for.
      parameter (str): parameter name.

    Returns:
      alias (str): alias displayed instead of the parameter name.

    Example:
      job
    """
    
    for entry in self.confdata["aliases"]:
      # if the entry Job of one of the lists equals the given job or all and the entry Parameter contains the given 
      # parameter name, return the entry Alias
      if (entry["Job"] == job or entry["Job"] == "all") and entry["Parameter"] == parameter:
        return entry["Alias"]
    return None
  
  def getJobOutput(self, jobName):
    return self.confdata["star_file"][jobName]
  
  def get_microscopePreSet(self,microscope):
      mic_data= self.confdata['microscopes']
      for entry in mic_data:
          if entry["Microscope"] == microscope:
              microscope_parameters_list_of_dicts= entry["Parameters"]
      
      microscope_parameters = {}
      for dicts in microscope_parameters_list_of_dicts:
          microscope_parameters.update(dicts)
      
      return microscope_parameters    
  
  def get_microscopePreSetNames(self):
      mic_data = self.confdata['microscopes']
      microscope_presets = {}  # Initialize an empty dictionary
      for i, entry in enumerate(mic_data):  # Use enumerate to get both index and entry
        microscope_presets[i] = entry["Microscope"]
      self.microscope_presets=microscope_presets
      
      return microscope_presets
      
      
      # mic_data= self.confdata['microscopes']
      # for entry in mic_data:
      #      microscope_presets[i]= entry["Microscope"]
      
      # return microscope_presets
      
  
  def get_alias_reverse(self,job, alias,):
    """
    reverse of the get alias function, i.e. returns the parameter name as used in the .star file when entering the 
    alias. Kept seperate to keep reading and writing clearly separated to avoid errors. 

    Args:
      job (str): job name the parameter is used for.
      alias (str): alias displayed instead of the parameter name.

    Returns:
      parameter (str): parameter name as displayed in the job.star file.

    Example:
      job
    """
    
    # go through entries in the aliases dict
    for entry in self.confdata["aliases"]:
      # if the entry Job of one of the lists equals the given job or all and the entry Alias contains the given 
      # parameter name, return the entry Parameter
      if (entry["Job"] == job or entry["Job"] == "all") and entry["Alias"] == alias:
        return entry["Parameter"]
    return None

def importFolderBySymlink(sourceFold, targetFold):
    """
    creates a symlink from sourceFold to targetFold

    Args:
        path_frames (str): absolute path to the imported frames.
        targetFold (str): path where the symlink will be created

    Returns:
        -

    Example:
        path_frames = /fs/pool/pool-plitzko3/Michael/01-Data/relion/frames
        path_out_dir = /fs/pool/pool-plitzko3/Michael/01-Data/project

        importFolderBySymlink(path_frames, path_out_dir)
        
    """
    import warnings
    
    if not os.path.exists(targetFold):
        os.makedirs(targetFold)      
    
    command_frames = f"ln -s {os.path.abspath(sourceFold)} {targetFold}" + os.path.sep
    
    foldFrames=targetFold + os.path.sep + os.path.basename(sourceFold.rstrip("/")) 
    if os.path.exists(foldFrames):
        warnings.warn("Path to folder already exists." + f" {foldFrames} ")
        #os.unlink(foldFrames)
    else:
        os.system(command_frames)
    
   
    



def read_header(path_to_frames):
  """
  reads header of a file to fetch the nr of eer's to calculate the optimal split using the calculate_dose_rate_per_pixel function.

  Args:
    path_to_frames (str): path to the respective frames.

  Returns:
    eer_split (dict): best possible eer split per frame as value so it can be added to the dict when transferring
                      information from the file path to the input data.
  Example:

  """
  # so it only fetches the first instance of *.eer, not all of them
  eer_file = glob.glob(f"{path_to_frames}/*.eer")[0]
  command = f"header {eer_file}"
  result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
  header = str(result)
  #eers = extract_eer_from_header(header)
  #print(eers)
  #eer_split = calculate_dose_rate_per_pixel(eers)
  #header = frame.read()
  #print(result.stdout)
  

def read_mdoc(path_to_mdoc_dir, path_to_yaml = "../src/read_write/config_reading_meta.yaml"):
  """
  reads mdoc file and fetches the relevant parameters to automatically set the respective values.

  Args:
    path_to_mdoc (str): path to the directory containing the mdoc files.
  
  Returns:
    return_mdoc_data (dict): values set in the config_reading_meta.yaml file for the respective meta-data type.

  Example:
    path_to_mdoc_dir = [path to mdoc file]

    returns a dict with the respective "x/z dimension", "Pixel size in A", and "Voltage of Microscope"
    (names must be set in the config_reading_meta.yaml file and be the same as in the config_aliases.yaml 
    file). This can subsequently be used to update the respective fields in the table.  
  """
  return_mdoc_data = {}
  # using the dir, access the first mdoc file in the folder
  path_to_mdoc = glob.glob(f"{path_to_mdoc_dir}")[0]
  # get respective mdoc file
  with open(path_to_mdoc, "r") as mdoc_file:
    # store the lines in that mdoc file in a list to iterate over
    mdoc_list = [line.strip() for line in mdoc_file if line.strip()]
    # get entries to look for in the mdoc file (based on the config_reading_meta.yaml file)
    # when only accessing the config_reading_meta.yaml file here, it's only accessed once a valid file-path is 
    # entered, not everytime there is a change to the QLine field
    with open(path_to_yaml, "r") as yaml_file:
      yaml_data = yaml.safe_load(yaml_file)
      print("mdoc file found")
      # access the respective list in the config_reading_meta.yaml file (parameter to look for in mdoc and respective alias)
      yaml_mdoc = yaml_data["meta_data"].get("mdoc", [])
      # access the list of dicts
      for yaml_entry in yaml_mdoc:
        # iterate through the meta data yaml to get the parameters which should be found (and the associated alias as key)
        for yaml_param_name, yaml_alias in yaml_entry.items():
          # iterate through the lines in the mdoc file until the respective entry is found
          for mdoc_current_line in mdoc_list:
            # remove spaces ect that might be in front/after the parameter name
            mdoc_current_line = mdoc_current_line.strip()
            # Skip empty lines
            if not mdoc_current_line:
              continue
            else:
              # data in the mdoc file is in this format: "PixelSpacing = 2.93" --> separate into key and value
              mdoc_key_value = mdoc_current_line.split("=")
              mdoc_current_line_key = mdoc_key_value[0].strip()
              mdoc_current_line_value = mdoc_key_value[1].strip()
              # if the current line holds the information we want as specified in the yaml), add it to the data dict
              # (keys = alias; value = value in meta data)
              if yaml_param_name == mdoc_current_line_key:
                # ImageSize contains both xdim and ydim in the mdoc file, have to split it up
                if mdoc_current_line_key == "ImageSize" and len(mdoc_current_line_value.split()) == 2:
                  xdim, ydim = mdoc_current_line_value.split()
                  # Add entries for both x and y dimensions
                  yaml_alias = "x dimensions"
                  return_mdoc_data[yaml_alias] = xdim
                  yaml_alias = "y dimensions"
                  return_mdoc_data[yaml_alias] = ydim
                else:      
                  return_mdoc_data[yaml_alias] = mdoc_current_line_value
  return(return_mdoc_data) 


# %%
# create Sphinx documentation: sphinx-build -M html docs/ docs/
# remove everything in the _build: make clean
# update Sphinx documentation: make html
import pandas as pd
from pathlib import Path
from starfile import read as starread
from starfile import write as starwrite
import copy
import os
from datetime import datetime
import time

class starFileMeta:
  """_summary_

  Raises:
      Exception: _description_

  Returns:
      _type_: _description_
  """
  def __init__(self, starfile,always_dict = True):
    
    self.always_dict = always_dict
    if isinstance(starfile, str):
      self.starfilePath = starfile
      self.readStar()
    if isinstance(starfile, pd.DataFrame):
      self.df = starfile
      self.dict = None  
    if isinstance(starfile, dict):
      self.dict = starfile
      self.df = None  
    
    
  def readStar(self):
    #Hack to avoid caching
    
    file_path = Path(self.starfilePath)
    if not file_path.exists():
        raise FileNotFoundError(f"The file {file_path} does not exist.")
    tmpTargetPath=tempfile.gettempdir() + os.path.sep + "tmpPointer.tmp" + str(time.time())
    os.symlink(os.path.abspath(self.starfilePath),tmpTargetPath)
    #self.dict = starread(self.starfilePath, always_dict = self.always_dict)
    self.dict = starread(tmpTargetPath,always_dict = self.always_dict)
    os.remove(tmpTargetPath)
    if (len(self.dict.keys())==1):
      self.df=self.dict[next(iter(self.dict.keys()))]
    else:
      self.df=None
    
  def writeStar(self,starfilePath):
    
    if isinstance(self.dict, dict):
       starwrite(self.dict,starfilePath)
       return
    if isinstance(self.df, pd.DataFrame):
        starwrite(self.df,starfilePath)
        return
    
class dataImport():
  
  def __init__(self,targetPath,wkFrames,wkMdoc=None,prefix="auto",logDir=None):  
    self.targetPath=targetPath
    self.wkFrames=wkFrames
    self.wkMdoc=wkMdoc
    if (prefix == "auto"):
      current_datetime = datetime.now()
      self.prefix=current_datetime.strftime("%Y-%m-%d-%H-%M-%S_")
    else:
      self.prefix=prefix
    self.mdocLocalFold="mdoc/"
    self.framesLocalFold="frames/"
    frameTargetPattern=self.targetPath + "/" + self.framesLocalFold + os.path.basename(self.wkFrames)
    self.existingFrames=[os.path.realpath(file) for file in glob.glob(frameTargetPattern)]
    self.existingMdoc=self.__getexistingMdoc()
    self.logDir=logDir
    self.logToConsole=False
    if (logDir is not None):  
      os.makedirs(logDir, exist_ok=True)
      self.logErrorFile=open(os.path.join(logDir,"run.err"),'a')
      self.logInfoFile=open(os.path.join(logDir,"run.out"),'a')
      
    self.runImport()
  
  def __del__(self):
    if self.logDir is not None:
      self.logErrorFile.close()
      self.logInfoFile.close()
  
  def __getexistingMdoc(self):
    
    existingMdoc=[]
    mdocTargetPattern=self.targetPath + "/" + self.mdocLocalFold + os.path.basename(self.wkMdoc)
    print("mdocTargetPattern: " + mdocTargetPattern)
    for fileName in glob.glob(mdocTargetPattern):
      with open(fileName, 'r') as file:
        lines = file.readlines()
        for i, line in enumerate(lines):
          if 'CryoBoost_RootMdocPath' in line:
            existingMdoc.append(line.replace("CryoBoost_RootMdocPath = ",""))
    
    return existingMdoc  
  
  def runImport(self):   
    os.makedirs(self.targetPath, exist_ok=True)
    framesFold=os.path.join(self.targetPath,self.framesLocalFold)
    os.makedirs(framesFold, exist_ok=True)
    
    self.__genLinks(self.wkFrames,framesFold,self.existingFrames)
    
    if self.wkMdoc is not None:
      mdocFold=os.path.join(self.targetPath,self.mdocLocalFold)
      os.makedirs(mdocFold, exist_ok=True)  
      self.__writeAdaptedMdoc(self.wkMdoc,mdocFold,self.existingMdoc)
      #self.__genLinks(self.wkMdoc,mdocFold,self.existingMdoc)
  
  def __writeAdaptedMdoc(self,inputPattern,targetFold,existingFiles):
    
    nrFilesAlreadyImported=len(glob.glob(targetFold + "/*" + os.path.splitext(inputPattern)[1])); 
    for file_path in glob.glob(inputPattern):
        file_name = os.path.basename(file_path)
        tragetFileName = os.path.join(targetFold,self.prefix+file_name)
        print("targetFileName:"+tragetFileName)
        print("inputPatter:"+inputPattern)
        if self.__chkFileExists(file_path,existingFiles)==False:
            self.__adaptMdoc(self.prefix,file_path,tragetFileName)
    
    nrFilesTotalImported=len(glob.glob(targetFold + "/*" + os.path.splitext(inputPattern)[1]));
    nrFilesNewImported=nrFilesTotalImported-nrFilesAlreadyImported
    self.__writeLog("info","Total number of mdocs imported: " + str(nrFilesTotalImported) )
    self.__writeLog("info","Number of new mdoc imported: " + str(nrFilesNewImported) )        
          
  def __adaptMdoc(self,prefix,inputMdoc,outputMdoc):
    
    with open(inputMdoc, 'r') as file:
      lines = file.readlines()
      for i, line in enumerate(lines):
        if 'SubFramePath' in line:
            lineTmp=line.replace("SubFramePath = \\","")
            lineTmp=os.path.basename(lineTmp.replace('\\',"/"))
            lines[i] = "SubFramePath = " + prefix + lineTmp
      
      lines.append("CryoBoost_RootMdocPath = " + os.path.abspath(inputMdoc) + "\n")       
      with open(outputMdoc, 'w') as file:
        file.writelines(lines)
  
  def __genLinks(self,inputPattern,targetFold,existingFiles):  
    
    #print("targetWk:" + targetFold + "/*." + os.path.splitext(inputPattern)[1])
    nrFilesAlreadyImported=len(glob.glob(targetFold + "/*" + os.path.splitext(inputPattern)[1]));
    for file_path in glob.glob(inputPattern):
        file_name = os.path.basename(file_path)
        tragetFileName = os.path.join(targetFold,self.prefix+file_name)
        if self.__chkFileExists(os.path.abspath(file_path),existingFiles)==False:
          try:
             os.symlink(os.path.abspath(file_path),tragetFileName)
             self.__writeLog("info","Created symlink: " + tragetFileName + " -> " + file_path)
          except FileExistsError:
             self.__writeLog("info","Symlink already exists: " + tragetFileName + " -> " + file_path)
          except OSError as e:
             self.__writeLog("error","Error creating symlink for " + tragetFileName + ": " + str(e))
    nrFilesTotalImported=len(glob.glob(targetFold + "/*" + os.path.splitext(inputPattern)[1]));
    nrFilesNewImported=nrFilesTotalImported-nrFilesAlreadyImported
    
    self.__writeLog("info","Total number of tilts imported: " + str(nrFilesTotalImported) )
    self.__writeLog("info","Number of new tilts imported: " + str(nrFilesNewImported) )
    
              
  def __writeLog(self,type,message):
    
    if self.logDir is not None:
      if type=="error":
        self.logErrorFile.write("Error: " + message + "\n")
      elif type=="info":
        self.logInfoFile.write(message + "\n")
      
      if (self.logToConsole): 
        print(message)            
    
    
  def __chkFileExists(self,inputPattern,existingFiles):
    
    if inputPattern in existingFiles:
        return True
    
    return False
      
       

class schemeMeta:
  """
  """
  def __init__(self, schemeFolderPath):
    self.CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
    self.conf=cbconfig(self.CRYOBOOST_HOME + "/config/conf.yaml")
    self.schemeFilePath=schemeFolderPath+os.path.sep+"scheme.star"
    self.schemeFolderPath=schemeFolderPath
    self.read_scheme()
    
  def read_scheme(self):
    self.scheme_star=starFileMeta(self.schemeFilePath)
    self.jobs_in_scheme = self.scheme_star.dict["scheme_edges"].rlnSchemeEdgeOutputNodeName.iloc[1:-1]
    self.job_star = {
    f"{job}": starFileMeta(os.path.join(self.schemeFolderPath, f"{job}/job.star"))
    for job in self.jobs_in_scheme}
    #self.scheme_star_dict = starFileMeta(self.schemeFilePath)
    self.nrJobs = len(self.jobs_in_scheme)
  
  def getJobOptions(self, jobName):
    return self.job_star[jobName].dict["joboptions_values"]   
  
  def filterSchemeByNodes(self, nodes):
    
    scFilt=copy.deepcopy(self)
    filtEdges_df=self.filterEdgesByNodes(self.scheme_star.dict["scheme_edges"], nodes)
    jobStar_dict=self.job_star
    schemeJobs_df=self.scheme_star.dict["scheme_jobs"]
    jobStar_dictFilt=self.filterjobStarByNodes(jobStar_dict,nodes)
    #schemeJobs_dfFilt=self.filterSchemeJobsByNodes(schemeJobs_df,nodes)
    scFilt.scheme_star.dict["scheme_edges"]=filtEdges_df
    scFilt.job_star=jobStar_dictFilt
    scFilt.nrJobs =len(scFilt.job_star)
    scFilt.jobs_in_scheme = scFilt.scheme_star.dict["scheme_edges"].rlnSchemeEdgeOutputNodeName.iloc[1:-1]
    
    return scFilt   
  
  
  def filterjobStarByNodes(self,jobStarDict,nodes): 
    
    schemeJobs_dfFilt={}
    for nodeid, node in nodes.items():
      schemeJobs_dfFilt[node]=jobStarDict[node]
      if (nodeid>0):
          indMinusOne=nodes[nodeid-1]
          input=self.scheme_star.dict["scheme_general"]["rlnSchemeName"]+self.conf.getJobOutput(indMinusOne)
          
          df=schemeJobs_dfFilt[node].dict["joboptions_values"]
          ind=df.rlnJobOptionVariable=="input_star_mics"
          if not any(ind):
             ind=df.rlnJobOptionVariable=="in_tiltseries" 
          if not any(ind):
             ind=df.rlnJobOptionVariable=="in_mic"
          if not any(ind):
             ind=df.rlnJobOptionVariable=="in_tomoset"
          
          if not any(ind):
             raise Exception("nether input_star_mics nor in_tiltseries found")
          
          # Get the index of the row to update
          row_index = schemeJobs_dfFilt[node].dict["joboptions_values"].index[ind]
          schemeJobs_dfFilt[node].dict["joboptions_values"].loc[row_index, "rlnJobOptionValue"] = input
          #schemeJobs_dfFilt[node].dict["joboptions_values"].loc[ind].rlnJobOptionValue=input  
          
          
    return schemeJobs_dfFilt 
  
  
  def filterSchemeJobsByNodes(self,jobs_df,jobStarDict,nodes): 
    pass
    return 1 
  
  def filterEdgesByNodes(self,edge_df, nodes):     
    
    tmpEdge=edge_df.loc[0:0].copy(deep=True)
    schemeEdge_df=tmpEdge
    for nodeid, node in nodes.items(): 
        dfOneEdge=tmpEdge.copy(deep=True)
        dfOneEdge["rlnSchemeEdgeInputNodeName"]=schemeEdge_df.loc[nodeid].rlnSchemeEdgeOutputNodeName
        dfOneEdge["rlnSchemeEdgeOutputNodeName"]=node
        schemeEdge_df=pd.concat([schemeEdge_df,dfOneEdge],ignore_index=True) 
    dfOneEdge=tmpEdge
    dfOneEdge["rlnSchemeEdgeInputNodeName"]=schemeEdge_df.iloc[-1].rlnSchemeEdgeOutputNodeName
    dfOneEdge["rlnSchemeEdgeOutputNodeName"]="EXIT" #was "WAIT"
    schemeEdge_df=pd.concat([schemeEdge_df,dfOneEdge],ignore_index=True) 
    
    return schemeEdge_df
      
  def locate_val(self,job_name:str,var:str):
    """
    locates the value defined of the dict defined in the job_star_dict dictionary so it can be displayed and edited.

    Args:
      job_name (str): job name as str as it's stated in the job_star_dict ("importmovies", "motioncorr", "ctffind", "aligntilts", "reconstruction").
      var (str): name of variable/parameter that should be changed (parameters as defined in the job.star files).
      job_dict (str): dataframe that should be accessed inside the job defined in job_name (standard input is the df containing the parameters).
      column_variable (str): column in the dataframe containing the parameters (standard input is the correct name).
      column_value (str): column in the dataframe containing the values assigned to each parameter (standard input is the correct name).

    Returns:
      str: value that is currently assigned to the defined parameter of the defined job.
    """
    job_dict = "joboptions_values", 
    column_variable = "rlnJobOptionVariable" 
    column_value = "rlnJobOptionValue"
    val = self.job_star[job_name].dict[job_dict].loc[self.job_star[job_name].dict[job_dict][column_variable] == var, column_value].values[0]
    return val
  
  def update_job_star_dict(self,job_name, param, value):
      """
      updates the job_star_dict dictionary (containing all .star files of the repective jobs) with the values provided.

      Args:
        job_name (str): job name as str as it's stated in the job_star_dict ("importmovies", "motioncorr", "ctffind", "aligntilts", "reconstruction").
        param (str): parameter that should be updated as str as it's called in the respective job.star file.
        value (str): new value that should be placed in the job.star file for the set parameter.

      Returns:
        job_star_dict with updated value for respective parameter.
      """
      index = self.job_star[job_name].dict["joboptions_values"].index[self.job_star[job_name].dict["joboptions_values"]["rlnJobOptionVariable"] == param]
      self.job_star[job_name].dict["joboptions_values"].iloc[index, 1] = value
      
      return self.job_star[job_name].dict


  
  def write_scheme(self,schemeFolderPath):
     self.schemeFilePath =  schemeFolderPath+os.path.sep+"scheme.star"
     self.schemeFolderPath =  schemeFolderPath
     os.makedirs(schemeFolderPath, exist_ok=True)
     self.scheme_star.writeStar(schemeFolderPath+os.path.sep+"scheme.star")

    
    # repeat for all jobs, creating a job.star file in these directories
     for job in self.jobs_in_scheme:
        jobFold = schemeFolderPath+os.path.sep+job 
        os.makedirs(jobFold, exist_ok=True)
        job_star = self.job_star[job]
        job_star.writeStar(jobFold+os.path.sep+"job.star")
        

class tiltSeriesMeta:
    """
    Class for handling tilt series metadata.

    Args:
        tiltseriesStarFile (str): Path to the tilt series star file.
        relProjPath (str): Path to the relative project directory.

    Attributes:
        tilt_series_df (pd.DataFrame): DataFrame containing the tilt series information.
        tiltseriesStarFile (str): Path to the tilt series star file.
        relProjPath (str): Path to the relative project directory.

    Methods:
        __init__(self, tiltseriesStarFile, relProjPath): Initializes the tiltSeriesMeta class.
        readTiltSeries(self): Reads the tilt series star file and its associated tilt series files.
        filterTilts(self, fitlterParams): Filters the tilt series based on the provided parameters.
        filterTiltSeries(self, fitlterParams): Filters the tilt series based on the provided parameters.
        writeTiltSeries(self, tiltseriesStarFile, tiltSeriesStarFolder='tilt_series'): Writes the tilt series star file and its associated tilt series files.
    """

    def __init__(self, tiltseriesStarFile, relProjPath=''):
        """
        Initializes the tiltSeriesMeta class.

        Args:
            tiltseriesStarFile (str): Path to the tilt series star file.
            relProjPath (str): Path to the relative project directory.

        Attributes:
            tilt_series_df (pd.DataFrame): DataFrame containing the tilt series information.
            tiltseriesStarFile (str): Path to the tilt series star file.
            relProjPath (str): Path to the relative project directory.
        """
        self.tilt_series_df = None
        self.tiltseriesStarFile = tiltseriesStarFile
        self.relProjPath = relProjPath
        self.readTiltSeries()

    def readTiltSeries(self):
        
        print("Reading: " + self.tiltseriesStarFile)
        tilt_series=starFileMeta(self.tiltseriesStarFile)
        #tilt_series_df =tilt_series.dict[next(iter(tilt_series.dict.keys()))] 
        self.nrTomo=tilt_series.df.shape[0]
        all_tilts_df = pd.DataFrame()
        tilt_series_tmp = pd.DataFrame()
        
        i = 0
        for tilt_seriesName in tilt_series.df["rlnTomoTiltSeriesStarFile"]:
           # tilt_star_df = read_star(self.relProjPath + tilt_series)
            tilt_star=starFileMeta(self.relProjPath + tilt_seriesName)
            all_tilts_df = pd.concat([all_tilts_df, tilt_star.df], ignore_index=True)
            tmp_df = pd.concat([tilt_series.df.iloc[[i]]] * tilt_star.df.shape[0], ignore_index=True)
            tilt_series_tmp = pd.concat([tilt_series_tmp, tmp_df], ignore_index=True)
            i += 1

        all_tilts_df = pd.concat([all_tilts_df, tilt_series_tmp], axis=1)
        all_tilts_df.dropna(inplace=True)  # check !!
        #generte key to merge later on
        k=all_tilts_df['rlnMicrographName'].apply(os.path.basename)
        if (k.is_unique):
          all_tilts_df['cryoBoostKey']=k
        else:
          raise Exception("rlnMicrographName is not unique !!")        

        self.all_tilts_df = all_tilts_df
        self.tilt_series_df = tilt_series.df

    def writeTiltSeries(self, tiltseriesStarFile, tiltSeriesStarFolder='tilt_series'):
        """
        Writes the tilt series star file and its associated tilt series files.

        Args:
            self (tiltSeriesMeta): An instance of the tiltSeriesMeta class.
            tiltseriesStarFile (str): Path to the tilt series star file.
            tiltSeriesStarFolder (str): Folder name for the tilt series star files.

        Example:
            >>> ts = tiltSeriesMeta("/path/to/tilt_series_star_file", "/path/to/rel_proj_path")
            >>> ts.writeTiltSeries("/tmp/fbeck/test8/tiltseries.star")
        """
        print("Writing: " + tiltseriesStarFile)
        #generate tiltseries star from all dataframe ...more generic if filter removes all tilts of one series
        ts_df = self.all_tilts_df[self.tilt_series_df.columns].copy()
        ts_df.drop_duplicates(inplace=True)
        tsFold = os.path.dirname(tiltseriesStarFile) + os.path.sep + tiltSeriesStarFolder + os.path.sep
        ts_df['rlnTomoTiltSeriesStarFile'] = ts_df['rlnTomoTiltSeriesStarFile'].apply(lambda x: os.path.join(tsFold, os.path.basename(x)))
        os.makedirs(tsFold,exist_ok=True)
        ts_dict={}
        ts_dict['global']=ts_df
        stTs=starFileMeta(ts_dict)
        stTs.writeStar(tiltseriesStarFile)
       
        fold = os.path.dirname(tiltseriesStarFile)
        Path(fold + os.sep + tiltSeriesStarFolder).mkdir(exist_ok=True)
        for tilt_series in self.tilt_series_df["rlnTomoTiltSeriesStarFile"]:
            oneTs_df = self.all_tilts_df[self.all_tilts_df['rlnTomoTiltSeriesStarFile'] == tilt_series].copy()
            oneTs_df.drop(self.tilt_series_df.columns, axis=1, inplace=True)
            tomoName = self.all_tilts_df.loc[self.all_tilts_df['rlnTomoTiltSeriesStarFile'] == tilt_series, 'rlnTomoName'].unique()[0]
            oneTS_dict={}
            oneTS_dict[tomoName]=oneTs_df
            stOneTs=starFileMeta(oneTS_dict)
            stOneTs.writeStar(fold + os.sep + tiltSeriesStarFolder + os.sep + os.path.basename(tilt_series))
           
            
    def filterTilts(self, fitlterParams):
      """
      Filters the tilt series based on the provided parameters.

      Args:
          self (tiltSeriesMeta): An instance of the tiltSeriesMeta class.
          fitlterParams (dict): A dictionary containing the parameters and their respective thresholds for filtering the tilt series.

      Raises:
          ValueError: If any of the required star files are not found.

      Returns:
          None: This method modifies the tiltSeriesMeta object in-place.

      Example:
          >>> ts = tiltSeriesMeta("/path/to/tilt_series_star_file", "/path/to/rel_proj_path")
          >>> ts.filterTilts({"rlnCtfMaxResolution": (7.5, 30,-35,35), "rlnDefocusU": (1, 80000,-60,60)})
      """
      pTilt = "rlnTomoNominalStageTiltAngle"  # fieldName for tiltRange
      dfTmp = self.all_tilts_df

      for param, thresholds in fitlterParams.items():
          
          if isinstance(thresholds, set):
              v = dfTmp[param].isin(thresholds)
          else:    
              if isinstance(thresholds[0], str):
                  v = dfTmp[param] == thresholds
              else:
                  vParamRange = (dfTmp[param] > thresholds[0]) & (dfTmp[param] < thresholds[1])
                  vTiltRange = (dfTmp[pTilt] > thresholds[2]) & (dfTmp[pTilt] < thresholds[3])
                  # Tiltrange defines for which tilts the filter gets applied
                  v = vParamRange | (vTiltRange == False)

          dfTmp = dfTmp[v]

      dfTmp.reset_index(drop=True, inplace=True)
      self.all_tilts_df = dfTmp
      
      ts_df = self.all_tilts_df[self.tilt_series_df.columns].copy()
      ts_df.drop_duplicates(inplace=True)
      self.tilt_series_df=ts_df
      self.nrTomo=len(self.tilt_series_df)
      
    def reduceToNonOverlab(self,tsSubset):
      tomoNamesSub=set(tsSubset.tilt_series_df["rlnTomoName"])
      tomoNamesFull=set(self.tilt_series_df["rlnTomoName"])
      tomoNamesDiff=tomoNamesFull-tomoNamesSub
      self.filterTilts({"rlnTomoName": tomoNamesDiff})
    
    def mergeTiltSeries(self,tsToAdd):
      
      self.all_tilts_df=pd.concat([self.all_tilts_df,tsToAdd.all_tilts_df],axis=0)
      self.all_tilts_df.reset_index(drop=True, inplace=True)
      ts_df = self.all_tilts_df[self.tilt_series_df.columns].copy()
      ts_df.drop_duplicates(inplace=True)
      self.tilt_series_df=ts_df
      self.nrTomo=len(self.tilt_series_df) 
      
    def filterTiltSeries(self,minNumTilts,fitlterParams):
      pass 
    
    def getMicrographMovieNameFull(self):
      return self.relProjPath+self.all_tilts_df['rlnMicrographName'] 
    
    def addColumns(self,columns_df):  
      """
      Adds new columns to the DataFrame stored in the instance variable `all_tilts_df`.

      This method takes a DataFrame `columns_df` containing new columns to be added to `all_tilts_df`. 
      The merge is performed on the 'rlnMicrographMovieName' column, using a left join. This means that all 
      entries in `all_tilts_df` will be retained, and matching entries from `columns_df` will be added based 
      on the 'cryoBoostKey' column. If there are no matching entries in `columns_df`, the new 
      columns will contain NaN values for those rows.

      Args:
      - columns_df (DataFrame): A pandas DataFrame containing the columns to be added to `all_tilts_df`. 
         It must include a 'cryoBoostKey' column for the merge operation.

      Returns:
      - None. The method updates `all_tilts_df` in place by adding the new columns from `columns_df`.

      """ 
      k=columns_df['cryoBoostKey'].apply(os.path.basename)
      if (k.is_unique):
        columns_df['cryoBoostKey']=k
      
      self.all_tilts_df=self.all_tilts_df.merge(columns_df,on='cryoBoostKey',how='left') 
        

