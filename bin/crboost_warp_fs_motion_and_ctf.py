#!/usr/bin/env crboost_python 

import argparse
import os
import sys


from src.warp.libWarp import fsMotionAndCtf

def parse_arguments():
    parser = argparse.ArgumentParser(description="filter tilts")
    parser.add_argument("--in_mics", "-in_mic", required=True, help="Input tilt series STAR file")
    parser.add_argument("--o", dest="out_dir", required=True, help="Output directory name")
    parser.add_argument("--j", "-nr_threads",dest="threads" ,required=False, default=None, help="Nr of threads used. Ignore!")
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    
    args,addArg = parse_arguments()
    
    fsMotionAndCtf(args.in_mics,args.out_dir,threads=args.threads)
    print("warp fs_motion_and_ctf done")
    successName=args.out_dir + "/RELION_JOB_EXIT_SUCCESS"
    with open(successName, 'a'):
        os.utime(successName, None)
    
    
if __name__ == '__main__':
    main()
