import argparse
import os
import sys
from src.templateMatching.pytomTm import pytomTm


def parse_arguments():
    parser = argparse.ArgumentParser(description="filter tilts")
    parser.add_argument("--in_mics", "-in_mic", required=True, help="Input tilt series STAR file")
    parser.add_argument("--o", dest="out_dir", required=True, help="Output directory name")
    parser.add_argument("--j", "-nr_threads",dest="threads" ,required=False, default=None, help="Nr of threads used. Ignore!")
    
    parser.add_argument("--implementation", required=False,default="pytom", help="Default: pytom implementation to use")
    parser.add_argument("--volumeColumn", required=False,default="rlnTomoReconstructedTomogram", help="Folder containing the masks for the volumes") 
    parser.add_argument("--volumeMaskFold", required=False,default=None, help="Folder containing the masks for the volumes")
    parser.add_argument("--template", required=True,default=None ,help="Volume,pdb or pdb code")
    parser.add_argument("--templateSym", required=False,default="C1", help="Symmetry of the template for pytom only Cn implemented")
    parser.add_argument("--templateMask", required=False,default="Sphere", help="Path to Volume,Diameter or Auto")
    parser.add_argument("--angularSearch", required=True,default="12", help="Default: 12 Angular increment or a list of euler angles in zxz comma seperated")
    parser.add_argument("--nonSphericalMask", required=False,default=False, help="Default: Set to true for non spherical masks")
    
    parser.add_argument("--bandPassFilter", required=False,default=None, help="two comma separated values low,high")
    parser.add_argument("--ctfWeight", required=False,default=True, help="Default True Apply ctf correction ")
    parser.add_argument("--doseWeight", required=False,default=True, help="Default True Apply dose weighting")
    parser.add_argument("--spectral-whitening", required=False,default=True, help="Default True Apply spectral whitening")
    parser.add_argument("--random-phase-correction", required=False,default=False, help="Default: False")
        
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    
    args,addArg = parse_arguments()
    
    print("launching")
    if args.implementation=="pytom":
        tm=pytomTm(args,runFlag="Full")
    
    if tm.result.returncode==1:
        raise Exception("Error: ts_ctf failed")
    if tm.result.returncode==0:
        successName=args.out_dir + "/RELION_JOB_EXIT_SUCCESS"
        with open(successName, 'a'):
             os.utime(successName, None)
    
    
if __name__ == '__main__':
    main()