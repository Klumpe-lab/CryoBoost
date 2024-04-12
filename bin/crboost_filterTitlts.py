#!/usr/bin/env python
import argparse
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

from src.filterTilts.libFilterTilts import filterTitls

def parse_arguments():
    parser = argparse.ArgumentParser(description="filter tilts")
    parser.add_argument("--in_mics", "-in_mics", required=True, help="Input tilt series STAR file")
    parser.add_argument("--o", dest="out_dir", required=True, help="Output directory name")
    parser.add_argument("--driftInAng","-shift",dest="rlnAccumMotionTotal",required=False, default=None, help="threshold movement")
    parser.add_argument("--defocusInAng", "-defocus",dest="rlnDefocusU" ,required=False, default=None, help="threshold defocus")
    parser.add_argument("--ctfMaxResolution", "-resolution",dest="rlnCtfMaxResolution" ,required=False, default=None, help="threshold resolution")
    parser.add_argument("--model", "-mod",dest="model" ,required=False, default=None, help="model for prediction")
    parser.add_argument("--j", "-nr_threads", required=False, default=None, help="Nr of threads used. Ignore!")
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    
    args,addArg = parse_arguments()
    filterParams = {}
    for arg, value in vars(args).items():
        if (value==None):
            continue
        if ((arg == 'rlnAccumMotionTotal') | (arg == 'rlnDefocusU') | (arg == 'rlnCtfMaxResolution')):
            filterParams[arg] = [float(num) for num in value.split(',')]   
    
    filterTitls(args.in_mics,relionProj='',pramRuleFilter=filterParams,model=None,plot=None,outputFolder=args.out_dir)
    
    
    return 
    # Redirect stdout and stderr to files
    os.chdir(args.out_dir)
    with open("run.out", "w") as out_file:
        sys.stdout = out_file
    with open("run.err", "w") as err_file:
        sys.stderr = err_file
        if  succes == 0:
            sys.stderr.write(f"Error occurred while running\n")


    if succes == 0:
        open("RELION_JOB_EXIT_SUCCESS", "w").close()
    else:
        open("RELION_JOB_EXIT_FAILURE", "w").close()

    sys.exit(0)

if __name__ == '__main__':
    main()


 #if ((arg == 'in_mics') | (arg == 'out_dir') | (arg == 'model')):
 #           filterParams[arg] = value