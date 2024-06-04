from src.rw.librw import cbconfig,importFolderBySymlink,schemeMeta
from src.misc.system import run_command,run_command_async
import shutil
import os,re 
import subprocess

class pipe:
  """_summary_

  Raises:if (type(args.scheme) == str and os.path.exists(file_path)):
      self.defaultSchemePath=args.scheme
      Exception: _description_

  Returns:
      _type_: _description_
  """
  def __init__(self,args):
    CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
    if (type(args.scheme) == str and os.path.exists(args.scheme)==False):
      self.defaultSchemePath=CRYOBOOST_HOME + "/config/Schemes/" + args.scheme
    if (type(args.scheme) == str and os.path.exists(args.scheme)):
      self.defaultSchemePath=args.scheme
    if type(args.scheme)==schemeMeta:  
      self.scheme=args.scheme
    else:
      self.scheme=schemeMeta(self.defaultSchemePath)
    
    self.confPath=CRYOBOOST_HOME + "/config/conf.yaml"
    self.conf=cbconfig(self.confPath)     
    self.args=args
    self.pathMdoc=args.mdocs
    self.pathFrames=args.movies
    self.pathProject=args.proj
    headNode=self.conf.confdata['submission'][0]['HeadNode']
    sshStr=sub=self.conf.confdata['submission'][0]['SshCommand']
    schemeName=self.scheme.scheme_star.dict['scheme_general']['rlnSchemeName']
    schemeName=os.path.basename(schemeName.strip(os.path.sep)) #remove path from schemeName
    schemeLockFile=".relion_lock_scheme_" + schemeName + os.path.sep  + "lock_scheme"
    relSchemeStart="relion_schemer --scheme " + schemeName  + " --run"
    self.schemeLockFile=schemeLockFile
    self.schemeName=schemeName
    
    chFold="cd " + os.path.abspath(self.pathProject) + ";"
    #relSchemeAbrot="relion_schemer --scheme " + schemeName  + " --abort; + pkill -f """ + 
    relSchemeAbrot="pkill -f \'relion_schemer --scheme " + schemeName + "\'" 
    relStopLastJob="scancel XXXJOBIDXXX"
    relSchemeReset="relion_schemer --scheme " + schemeName  + " --reset"
    relSchemeUnlock="rm " + schemeLockFile + ";rmdir "+ os.path.dirname(schemeLockFile)
    relGuiStart="relion --tomo --do_projdir "
   
    envStr="module load RELION/5.0-beta-3;"
    logStr=" > " + schemeName + ".log 2>&1 " 
    logStrAdd=" >> " + schemeName + ".log 2>&1 "
    self.commandSchemeStart=sshStr + " " + headNode + ' "'  + envStr + chFold + relSchemeStart + logStrAdd + '"'
    self.commandSchemeAbrot=sshStr + " " + headNode + ' "'  + envStr  + relSchemeAbrot + ";" + logStrAdd + '"'
    self.commandSchemeJobAbrot=sshStr + " " + headNode + ' "' + relStopLastJob + ";" + logStrAdd + '"'
    self.commandSchemeReset=sshStr + " " + headNode + ' "'  + envStr + chFold + relSchemeReset + logStrAdd + '"'
    self.commandGui=sshStr + " " + headNode + ' "'  + envStr + chFold + relGuiStart  + '"'
    self.commandSchemeUnlock=sshStr + " " + headNode + ' "'  + envStr + chFold + relSchemeUnlock + logStrAdd + '"'
    
      
  def initProject(self):
    importFolderBySymlink(self.pathFrames, self.pathProject)
    if (self.pathFrames!=self.pathMdoc):
        importFolderBySymlink(self.pathMdoc, self.pathProject)
    self.scheme.update_job_star_dict('importmovies','movie_files',os.path.basename(self.pathFrames.strip(os.path.sep)) + os.path.sep + "*.eer")
    self.scheme.update_job_star_dict('importmovies','mdoc_files',os.path.basename(self.pathMdoc.strip(os.path.sep)) + os.path.sep + "*.mdoc")
    shutil.copytree(os.getenv("CRYOBOOST_HOME") + "/config/qsub", self.pathProject + os.path.sep + "qsub",dirs_exist_ok=True)
    
      
  def writeScheme(self):
     path_scheme = os.path.join(self.pathProject, self.scheme.scheme_star.dict['scheme_general']['rlnSchemeName'])
     nodes = {i: job for i, job in enumerate(self.scheme.jobs_in_scheme)}
     self.scheme.filterSchemeByNodes(nodes) #to correct for input output mismatch within the scheme
     self.scheme.write_scheme(path_scheme)
  
  def runScheme(self):
    print("-----------------------------------------")
    print(self.commandSchemeStart)
    p=run_command_async(self.commandSchemeStart)
    print("-----------------------------------------")
 
  def runSchemeSync(self):
    print("-----------------------------------------")
    print(self.commandSchemeStart)
    p=run_command(self.commandSchemeStart)
    print("-----------------------------------------")
 
  def abortScheme(self):
    lastBatchJobId,lastJobFolder=self.parseSchemeLogFile()
    self.writeToLog("+++++++++++++++++++++++++++++++++++++++++++++++++\n");
    self.writeToLog(" + Abort scheme: " + self.schemeName + "\n")
    self.writeToLog(" + " + self.commandSchemeAbrot + "\n")
    p=run_command(self.commandSchemeAbrot)
    self.writeToLog(" + " + self.commandSchemeJobAbrot.replace("XXXJOBIDXXX",lastBatchJobId) + "\n")
    p=run_command(self.commandSchemeJobAbrot.replace("XXXJOBIDXXX",lastBatchJobId))
    self.writeToLog("+++++++++++++++++++++++++++++++++++++++++++++++++\n");
    self.unlockScheme()
    
 
  def resetScheme(self):
    print("-----------------------------------------")
    print(self.commandSchemeReset)
    p=run_command(self.commandSchemeReset)
    print("-----------------------------------------")
 
  def unlockScheme(self):
    pathLock=self.pathProject + os.path.sep + os.path.dirname(self.schemeLockFile)
    if os.path.isdir(pathLock):
      print("-----------------------------------------") 
      print(pathLock)
      print(self.commandSchemeUnlock)
      p=run_command(self.commandSchemeUnlock)
      print("-----------------------------------------")
 
  def openRelionGui(self):
    print("-----------------------------------------")
    print(self.commandGui)
    p=run_command_async(self.commandGui)
    print("-----------------------------------------") 
  
  def parseSchemeLogFile(self):
   
    file_path = self.pathProject + os.path.sep + self.schemeName + ".log"
    with open(file_path, 'r') as file:
        lastBatchJobID=None
        lastJobFolder=None
        for line in file:
          reResLastBatchJob=re.search("Submitted batch job", line)
          if (reResLastBatchJob):
             lastBatchJobID=reResLastBatchJob.string.split("job")[1]  # Assuming the format is "Submitted jobid"
          reReslastJobFolder=re.search("Creating new Job", line)
          if (reReslastJobFolder):
             lastJobFolder=reReslastJobFolder.string.split("Job:")[1].split(" ")[1] 
             
    return lastBatchJobID.strip(),lastJobFolder.strip()    
               
  def getLastJobLogs(self):
      lastBatchJobId,lastJobFolder=self.parseSchemeLogFile()
      jobOut=self.pathProject+os.path.sep+lastJobFolder+os.path.sep+"run.out"
      jobErr=self.pathProject+os.path.sep+lastJobFolder+os.path.sep+"run.err"
      #TODO: check for ext Log
      return jobOut,jobErr               
  def writeToLog(self,text):
      logFile=self.pathProject+os.path.sep+self.schemeName+".log"
      with open(logFile, "a") as myfile:
          myfile.write(text)
          