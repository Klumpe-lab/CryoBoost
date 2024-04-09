#!/usr/bin/env python
import argparse
import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.abspath(os.path.join(current_dir, '../'))
sys.path.append(root_dir)

from src.filterTilts.libFilterTilts import filterTitls

def parse_arguments():
    parser = argparse.ArgumentParser(description="Rule based exclusion")
    parser.add_argument("--in_mics", "-in_mics", required=True, help="Input tilt series STAR file")
    parser.add_argument("--o", dest="out_dir", required=True, help="Output directory name")
    parser.add_argument("--shift", "-shift", required=False, default=None, help="threshold movement")
    parser.add_argument("--defocus", "-defocus", required=False, default=None, help="threshold defocus")
    parser.add_argument("--resolution", "-resolution", required=False, default=None, help="threshold resolution")
    parser.add_argument("--j", "-nr_threads", required=False, default=None, help="Nr of threads used. Ignore!")
    return parser.parse_args()

def main():
    args = parse_arguments()

    python_script = os.path.join(root_dir, "src/lib/exclude_tilts/exclude_tilts_rules.py")
    
    # only in_mics and out_dir should be required, rest only appended if value is given
    python_command = f"python3 {python_script} --in_mics {args.in_mics} --o {args.out_dir} "
    
    if args.shift:
        python_command += f"--shift {args.shift} "

    if args.defocus:
        python_command += f"--defocus {args.defocus} "

    if args.resolution:
        python_command += f"--resolution {args.resolution} "

    if args.j:
        python_command += f"--j {args.j} "

    python_exit_status = os.system(python_command)


    # Redirect stdout and stderr to files
    os.chdir(args.out_dir)
    with open("run.out", "w") as out_file:
        sys.stdout = out_file
    with open("run.err", "w") as err_file:
        sys.stderr = err_file
        if python_exit_status != 0:
            sys.stderr.write(f"Error occurred while running {python_script}\n")


    if python_exit_status == 0:
        open("RELION_JOB_EXIT_SUCCESS", "w").close()
    else:
        open("RELION_JOB_EXIT_FAILURE", "w").close()

    sys.exit(0)

if __name__ == '__main__':
    main()
