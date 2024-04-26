#!/fs/pool/pool-fbeck/projects/4TomoPipe/trainClassifyer/softFastAI/conda3/bin/python 
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
    parser.add_argument("--j", "-nr_threads",dest="threads" ,required=False, default=None, help="Nr of threads used. Ignore!")
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
    
    filterTitls(args.in_mics,relionProj='',pramRuleFilter=filterParams,model=args.model,plot=None,outputFolder=args.out_dir,threads=args.threads)
    print("filtering done")
    successName=args.out_dir + "/RELION_JOB_EXIT_SUCCESS"
    with open(successName, 'a'):
        os.utime(successName, None)
    
    
if __name__ == '__main__':
    main()


