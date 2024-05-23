import subprocess

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