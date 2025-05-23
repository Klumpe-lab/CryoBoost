#!/usr/bin/env crboost_python 
import argparse
import os
import sys
from src.misc.neighbourMap import neighbourMap
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)


def parse_arguments():
    parser = argparse.ArgumentParser(description="neighbour analysis")
    parser.add_argument("--type", "-t", required=False,default="neighborMap", help="Type of analysis neighbourMap (default: neighbourMap)")
    parser.add_argument("--o", dest="output",required=False,default="default", help="Output name")
    parser.add_argument("--i", dest="particleList",required=True, help="Input particle list ")
    parser.add_argument("--boxsize", "-b", required=False,default=96, help="Box size")
    parser.add_argument("--scale", "-s", required=False,default=1.0, help="Scaling factor")
    parser.add_argument("--recenterCoords", "-r", required=False,default=True, help="Recenter coordinates")
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    
    args,addArg = parse_arguments()
    nM=neighbourMap(particleListName=args.particleList, outputMapName=args.output, boxsize=args.boxsize, scaling=args.scale,calc=True,recenterCoords=True)
    
    
if __name__ == '__main__':
    main()


