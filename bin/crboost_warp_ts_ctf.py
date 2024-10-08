#!/usr/bin/env crboost_python 

import argparse
import os
import sys


from src.warp.libWarp import tsCtf

def parse_arguments():
    parser = argparse.ArgumentParser(description="filter tilts")
    parser.add_argument("--in_mics", "-in_mic", required=True, help="Input tilt series STAR file")
    parser.add_argument("--o", dest="out_dir", required=True, help="Output directory name")
    parser.add_argument("--j", "-nr_threads",dest="threads" ,required=False, default=None, help="Nr of threads used. Ignore!")
    
    parser.add_argument("--window", required=False,default="512" ,help="Default: 512. Patch size for CTF estimation in binned pixels")
    parser.add_argument("--range_min_max", required=False,default="30:4", help="Default: 30:4 Minimum/Maxium  (sep by :) resolution in Angstrom to consider in fit")
    parser.add_argument("--defocus_min_max", required=False,default="0.5:8", help="Default: 0.5:8. Minimum/Maximum (sep by :) defocus value in um to explore during fitting")
    parser.add_argument("--auto_hand", required=False,default="5", help="Default: 1Run defocus handedness estimation based on this many tilt series (e.g. 10), then estimate CTF with the correct handedness")
    
    parser.add_argument("--perdevice", required=False,default="1" ,help="Default: 1. Number of processes per GPU")
    
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    
    args,addArg = parse_arguments()
    
    print("launching")
    retVal=tsCtf(args)
    if retVal==1:
        raise Exception("Error: ts_ctf failed")
    if retVal==0:
        successName=args.out_dir + "/RELION_JOB_EXIT_SUCCESS"
        with open(successName, 'a'):
             os.utime(successName, None)
    
    
if __name__ == '__main__':
    main()
