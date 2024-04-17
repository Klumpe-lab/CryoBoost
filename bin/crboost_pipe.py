#!/usr/bin/env python
import argparse
import os
import sys

from PyQt6.QtWidgets import QApplication
from src.gui.schemeGui import MainUI 

def parse_arguments():
    parser = argparse.ArgumentParser(description="scheme gui")
    parser.add_argument("--scheme", "-s", required=False, help="Input input scheme file")
    parser.add_argument("--movies", "-f", required=False, help="Input input movie dir")
    parser.add_argument("--mdocs", "-m", required=False,default="umba,umba",help="Input input mdocs dir")
    parser.add_argument("--proj", "-p", required=False, help="Output output project dir")
    parser.add_argument("--gui", "-g", required=False,default=True,help="Outpu output project dir")
    parser.add_argument("--autoGen", "-aG", required=False, default=False, help="gen Project and scheme")
    parser.add_argument("--autoLaunch", "-aL", required=False, default=False, help="launch relion scheme")
    args,unkArgs=parser.parse_known_args()
    return args,unkArgs

def open_scheme_gui(args):
    app = QApplication([])
    main_ui = MainUI(args)
    main_ui.show()
    app.exec()


def main():
    
    args,addArg = parse_arguments()
    open_scheme_gui(args)
    
if __name__ == '__main__':
    main()


