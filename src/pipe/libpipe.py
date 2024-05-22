from src.rw.librw import cbconfig,importFolderBySymlink,schemeMeta
import shutil
import os 

class pipe:
  """_summary_

  Raises:
      Exception: _description_

  Returns:
      _type_: _description_
  """
  def __init__(self,args):
    CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
    self.defaultSchemePath=CRYOBOOST_HOME + "/config/Schemes/relion_tomo_prep/"
    self.confPath=CRYOBOOST_HOME + "/config/conf.yaml"
    self.scheme=schemeMeta(self.defaultSchemePath)
    self.conf=cbconfig(self.confPath)     
    self.args=args
    self.pathMdoc=args.mdocs
    self.pathFrames=args.movies
    self.pathProject=args.proj
    
      
  def initProject(self):
    importFolderBySymlink(self.pathFrames, self.pathProject)
    if (self.pathFrames!=self.pathMdoc):
        importFolderBySymlink(self.pathMdoc, self.pathProject)
    self.scheme.update_job_star_dict('importmovies','movie_files',os.path.basename(self.pathFrames.strip(os.path.sep)) + os.path.sep + "*.eer")
    self.scheme.update_job_star_dict('importmovies','mdoc_files',os.path.basename(self.pathMdoc.strip(os.path.sep)) + os.path.sep + "*.mdoc")
    shutil.copytree(os.getenv("CRYOBOOST_HOME") + "/config/qsub", self.pathProject + os.path.sep + "qsub",dirs_exist_ok=True)
    
      
  def writeScheme(self):
     path_scheme = os.path.join(self.pathProject, self.scheme.scheme_star.dict['scheme_general']['rlnSchemeName'])
     nodes={}
     i=0
     for job in self.scheme.jobs_in_scheme:
       nodes[i]=job
       i+=1
     self.scheme.filterSchemeByNodes(nodes)
     self.scheme.write_scheme(path_scheme)
  
  def runScheme(self):
     pass    
          