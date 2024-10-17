#!/usr/bin/env crboost_python 

import argparse
import os
import sys

from src.warp.fsMotionAndCtf import fsMotionAndCtf


def parse_arguments():
    parser = argparse.ArgumentParser(description="filter tilts")
    parser.add_argument("--in_mics", "-in_mic", required=True, help="Input tilt series STAR file")
    parser.add_argument("--o", dest="out_dir", required=True, help="Output directory name")
    parser.add_argument("--j", "-nr_threads",dest="threads" ,required=False, default=None, help="Nr of threads used. Ignore!")
    
    parser.add_argument("--eer_fractions", required=False,default="32", help=" Default: 32. The number of hardware frames to group into one fraction")
    parser.add_argument("--gain_path", required=False,default="None", help="Path to gain file")
    parser.add_argument("--gain_operations", required=False,default="None", help="Operations applied to gain e.g flip_x:transpose or flip_y") 
    
    parser.add_argument("--m_range_min_max", required=False,default="500:10" ,help="Default: 500:10 Minimum/Maximun (sep by :) resolution in Angstrom to consider in fit")
    parser.add_argument("--m_bfac", required=False,default="-500", help="Default: -500. Downweight higher spatial frequencies using a B-factor, in Angstrom^2")
    parser.add_argument("--m_grid", required=False,default="1x1x3", help="Resolution of the motion model grid in X, Y, and temporal dimensions, separated by 'x': e.g. 5x5x40; empty = auto")
    
    parser.add_argument("--c_window", required=False,default="512" ,help="Default: 512. Patch size for CTF estimation in binned pixels")
    parser.add_argument("--c_range_min_max", required=False,default="30:4", help="Default: 30:4 Minimum/Maxium  (sep by :) resolution in Angstrom to consider in fit")
    parser.add_argument("--c_defocus_min_max", required=False,default="0.5:8", help="Default: 0.5:8. Minimum/Maximum (sep by :) defocus value in um to explore during fitting")
    parser.add_argument("--c_use_sum", required=False, action='store_true', help="Use the movie average spectrum instead of the average of individual frames' spectra. Can help in the absence of an energy filter, or when signal is low.")
    parser.add_argument("--c_grid", required=False,default="1x1x1" ,help="Resolution of the defocus model grid in X, Y, and temporal dimensions, separated by 'x': e.g. 5x5x40; empty = auto; Z > 1 is purely experimental")
    
    parser.add_argument("--out_average_halves", required=False, action='store_true', help="Export aligned averages of odd and even frames separately, e.g. for denoiser training")
    parser.add_argument("--out_skip_first", required=False,default="0" ,help="Default: 0. Skip first N frames when exporting averages")
    parser.add_argument("--out_skip_last", required=False,default="0" ,help="Default: 0. Skip last N frames when exporting averages")
    
    parser.add_argument("--perdevice", required=False,default="1" ,help="Default: 1. Number of processes per GPU")
    
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    
    args,addArg = parse_arguments()
    fsM=fsMotionAndCtf(args,runFlag="Full")
    if fsM.result.returncode==1:
        raise Exception("Error: fsMotionAndCtf failed")
    if fsM.result.returncode==0:
        successName=args.out_dir + "/RELION_JOB_EXIT_SUCCESS"
        with open(successName, 'a'):
             os.utime(successName, None)
    
if __name__ == '__main__':
    main()
