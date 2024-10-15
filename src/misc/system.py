# %%

import subprocess,os,getpass,sys,shlex,time
from src.rw.librw import cbconfig,starFileMeta


def run_wrapperCommand(command,tag=None,relionProj=None):
    """
    Run a command and return 0/1 for working non working

    Parameters:
    command (str): The command to run.

    Returns:
    tuple: A tuple containing the output, standard error, and exit code.
    """
    command_string = shlex.join(command)
    print(command_string)
    sys.stdout.flush()
        
    try:
        result = subprocess.run(command, check=True) #, capture_output=True, text=True)          
    except subprocess.CalledProcessError as e:
        print(tag," error",file=sys.stderr)
        error_output = e.stderr if e.stderr else str(e)
        sys.stderr.flush()
        print("Error syscall:", error_output, file=sys.stderr)
        print("***************************************************", file=sys.stderr)
        print("Error: " +tag+ " stopping" , file=sys.stderr)
        sys.stderr.flush()
        if relionProj is not None:
            try:
                defPipePath=relionProj+os.path.sep+"default_pipeline.star"
                st=starFileMeta(defPipePath)
                df=st.dict["pipeline_processes"]
                hit=df.rlnPipeLineProcessName[df.index[df['rlnPipeLineProcessStatusLabel'] == 'Running']]
                fold=str(hit.values[0])
                if os.path.isfile(fold + os.path.sep + "RELION_JOB_EXIT_SUCCESS")==False:
                    df.loc[df['rlnPipeLineProcessStatusLabel'] == 'Running', 'rlnPipeLineProcessStatusLabel'] = 'Failed'
                    print("setting to job to failed")
                    st.writeStar(defPipePath)
                    CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
                    conf=cbconfig(CRYOBOOST_HOME + "/config/conf.yaml")
                    envRel=conf.confdata['submission'][0]['Environment']+"; "
                    resultUpdate = subprocess.run(envRel+";relion_pipeliner --RunJobs ", shell=True, capture_output=True, text=True, check=True)
                     
            except subprocess.CalledProcessError as e:
                print("error resetting pipe!"+str(e))
                
        sys.exit(1)
    if result is not None:
        return result
    else:
        raise Exception("Command execution failed without raising an exception")
    
    
    
def run_command(command):
    """
    Run a command and capture its output, standard error, and exit code.

    Parameters:
    command (str): The command to run.

    Returns:
    tuple: A tuple containing the output, standard error, and exit code.
    """
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.CalledProcessError as e:
        return None, e.stderr.strip(), e.returncode
 
def run_command_async(command):
    """
    Run a command and capture its output, standard error, and exit code.

    Parameters:
    command (str): The command to run.

    Returns:
    ret val of suprocess.Popen
    """
    p = subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    return p
def test_crboostSetup():
    """
    Test the crboostSetup function.
    """
    sysOkFile = os.path.expanduser('~/.crboost/')+"setUpOK"
    if os.path.exists(sysOkFile):
        return True
    CRYOBOOST_HOME=os.getenv("CRYOBOOST_HOME")
    if CRYOBOOST_HOME is None or CRYOBOOST_HOME.strip() == "":
        print("error CRYOBOOST_HOME is empty")
        print("set CRYOBOOST_HOME !")
        return False
      
    conf=cbconfig(CRYOBOOST_HOME + "/config/conf.yaml")   
    headNode=conf.confdata['submission'][0]['HeadNode']
    sshStr=conf.confdata['submission'][0]['SshCommand']
    helpSsh=conf.confdata['submission'][0]['Helpssh']
    helpConflict=conf.confdata['submission'][0]['HelpConflict']
    # Run the command and capture the output, standard error, and exit code.
    if not os.path.exists(sysOkFile):
        sshOk=check_passwordless_ssh(headNode,sshStr,helpSsh)
        if (sshOk):
            return True
        else:
            return False
        # if sshOk:
        #     conflictRelionOk=check_appConflict(headNode,"relion",helpConflict)
        #     conflictPythonOk=check_appConflict(headNode,"python",helpConflict)
        # else:
        #     conflictRelionOk=False
        #     conflictPythonOk=False
            
        # if (sshOk and conflictRelionOk and conflictPythonOk):
        #     print("setup ok ready to start cryoboost")
        #     return True
        # else:
        #      print("Error you cannot use cryoboost check messages above")
        #      return False
        
        
def check_appConflict(hostname,app,helpStr):
    
    command = f"ssh {hostname} 'which {app}'"
    print("testing:"+ command)
    result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=10)
    if result.stdout:
        print("App conflict with "+app )
        print(helpStr)
        print(" ")
        return False
    else:
        print(f"No conflicting {app} ..ok")
        print(" ")
        return True

def check_passwordless_ssh(hostname,sshStr,helpStr):
    try:
        command = f"{sshStr} -o BatchMode=yes {hostname} echo 'SSH test message'"
        #command = "sleep 20"
        print("testing: "+ command)
        result = subprocess.run(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=20)
        if result.returncode == 0:
            print("Passwordless SSH ok")
            print(" ")
            return True
        else:
            print("Error: Passwordless SSH is not set up.")
            print("Error:", result.stderr.decode())
            print("Check: " + helpStr)
            print(" ")
            return False
    except subprocess.TimeoutExpired:
        print("Error: SSH connection attempt timed out.")
        print("Check: " + helpStr)
        print(" ")
        return False
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Check: " + helpStr)
        print(" ")
        return False

# %%

        