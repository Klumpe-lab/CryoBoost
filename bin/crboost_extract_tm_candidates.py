#!/usr/bin/env crboost_python 

import argparse
import os
import sys
from src.templateMatching.pytomExtractCandidates import pytomExtractCandidates


def parse_arguments():
    parser = argparse.ArgumentParser(description="extract candidates")
    parser.add_argument("--in_mics", "-in_mic", required=True, help="Input tilt series STAR file")
    parser.add_argument("--o", dest="out_dir", required=True, help="Output directory name")
    parser.add_argument("--j", "-nr_threads",dest="threads" ,required=False, default=None, help="Nr of threads used. Ignore!")
    parser.add_argument("--implementation", required=False,default="pytom", help="Default: pytom implementation to use")
    parser.add_argument("--apixScoreMap", required=True,default="auto", help="Pixel size of scoring map")
    parser.add_argument("--particleDiameterInAng", required=True,default=None, help="Particle diameter for peak removal")
    parser.add_argument("--maxNumParticles", required=True,default=1500, help="Max number of particles per tomo")
    parser.add_argument("--cutOffMethod", required=True,default="NumberOfFalsePositives", help="Default: NumberOfFalsePositives or ManualCutOff")
    parser.add_argument("--cutOffValue", required=True,default=1, help="Cut off value")
    parser.add_argument("--scoreFilterMethod", required=False,default="None", help="Filter for score function type opt. tophat")
    parser.add_argument("--scoreFilterValue", required=False,default="None", help="Filter for score function Value tophat connectivity:bins")
    parser.add_argument("--maskFoldPath", required=False,default="None", help="Folder containing masks for scores")
    #parser.add_argument("--outputFormat", required=False,default="relion5", help="defualt relion5 use warp for warp part extraction Format for coordiante .star file")
    
     
     
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    
    args,addArg = parse_arguments()
    print(args)
    
    print("launching")
    if args.implementation=="Pytom":
        tm=pytomExtractCandidates(args,runFlag="Full")
    
    if tm.result.returncode==1:
        raise Exception("Error: cadidate extraction failed")
    if tm.result.returncode==0:
        successName=args.out_dir + "/RELION_JOB_EXIT_SUCCESS"
        with open(successName, 'a'):
             os.utime(successName, None)
    
    
if __name__ == '__main__':
    main()