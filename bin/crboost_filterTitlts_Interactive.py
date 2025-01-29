#!/usr/bin/env crboost_python 
from src.filterTilts.filterTiltsInt import filterTiltsInterActive
import argparse
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir))
sys.path.append(root_dir)



def parse_arguments():
    parser = argparse.ArgumentParser(description="filter tilts")
    parser.add_argument("--in_mics", "-in_mics", required=True, help="Input tilt series STAR file")
    parser.add_argument("--o", dest="out_dir", required=True, help="Output directory name")
    parser.add_argument("--interActiveMode", "-iam",required=False, default="onFailure", help="when to start interactive sorting (onFailure,never,always)")
    parser.add_argument("--j", "-nr_threads",dest="threads" ,required=False, default=None, help="Nr of threads used. Ignore!")
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    args,addArg = parse_arguments()
    filterTiltsInterActive(args.in_mics,args.out_dir,args.interActiveMode)
    successName=args.out_dir + "/RELION_JOB_EXIT_SUCCESS"
    with open(successName, 'a'):
        os.utime(successName, None)
    print("done")

if __name__ == '__main__':
    main()