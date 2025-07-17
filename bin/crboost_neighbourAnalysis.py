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
    parser.add_argument("--i2", dest="particleList2",required=False,default=None,help="Input second particle list ")
    parser.add_argument("--i3", dest="particleList3",required=False,default=None,help="Input second particle list ")
    parser.add_argument("--tomoCoordPixs", "-tcp", required=False,default=None, help="If absolute coordinates are used, provide the tomogram coordinate pixelsize")
    parser.add_argument("--tomoSize", "-ts", required=False,default="4096,4096,2048", help="If relative coordinates are used, provide the tomogram size in pixels (default: 4096,4096,2048)")
    parser.add_argument("--boxsize", "-b", required=False,default=96, help="Box size")
    parser.add_argument("--pixs", "-p", required=False,default=1.0, help="pixelsize of output neighbour map")
    parser.add_argument("--recenterCoords", "-r",dest="recenterCoords" ,action="store_true", help="Recenter coordinates (default: True)")
    parser.add_argument("--noRecenterCoords","-rn",dest="recenterCoords" ,action="store_false", help="Do not Recenter coordinates")
    parser.set_defaults(recenterCoords=True)
    
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def main():
    
    args,addArg = parse_arguments()
    nM=neighbourMap(particleListName=args.particleList, outputMapName=args.output,tomoCoordPixs=args.tomoCoordPixs,boxsize=args.boxsize, pixs=args.pixs,calc=True,recenterCoords=args.recenterCoords,particleListName2=args.particleList2,
                    particleListName3=args.particleList3,tomoSize=args.tomoSize)
    
    
if __name__ == '__main__':
    main()



