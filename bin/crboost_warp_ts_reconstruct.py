#!/usr/bin/env crboost_python 

import argparse
import os
import sys


from src.warp.tsReconstruct import tsReconstruct

def parse_arguments():
    parser = argparse.ArgumentParser(description="warp tomogram reconstruction")
    parser.add_argument("--in_mics", "-in_mic", required=True, help="Input tilt series STAR file")
    parser.add_argument("--o", dest="out_dir", required=True, help="Output directory name")
    parser.add_argument("--j", "-nr_threads",dest="threads" ,required=False, default=None, help="Nr of threads used. Ignore!")
    parser.add_argument("--rescale_angpixs", required=False,default="12", help="Rescale tilt images to this pixel size")
    parser.add_argument("--halfmap_frames", required=False,default="1", help="Reconstruct half tomograms for denoising")
    parser.add_argument("--deconv", required=False,default="1", help="Reconstruct deconvoluted tomograms")
    
    parser.add_argument("--perdevice", required=False,default="1" ,help="Default: 1. Number of processes per GPU")
   
    
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    
    args,addArg = parse_arguments()
    
    print("launching")
    tsR=tsReconstruct(args,runFlag="Full")
    if tsR.result.returncode==1:
        raise Exception("Error: ts_reconstruction failed")
    if tsR.result.returncode==0:
        successName=args.out_dir + "/RELION_JOB_EXIT_SUCCESS"
        with open(successName, 'a'):
             os.utime(successName, None)
    
    
if __name__ == '__main__':
    main()
