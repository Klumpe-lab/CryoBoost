#!/bin/bash -l
# Standard output and error:
#SBATCH -e XXXerrfileXXX
#SBATCH -o XXXoutfileXXX
# Initial working directory:
#SBATCH -D ./
# Job Name:
#SBATCH -J Relion
# Queue (Partition):
#SBATCH --partition=XXXextra3XXX
# Number of nodes and MPI tasks per node:
#SBATCH --nodes=XXXextra1XXX
#SBATCH --ntasks=XXXmpinodesXXX
#SBATCH --ntasks-per-node=XXXextra2XXX
#SBATCH --cpus-per-task=XXXthreadsXXX
#SBATCH --gres=gpu:XXXextra4XXX
#
#SBATCH --mail-type=none
#SBATCH --mem 378880
#
# Wall clock limit:
#SBATCH --time=168:00:00

module purge
module load intel/18.0.5
module load impi/2018.4
module purge
module load intel/18.0.5
module load impi/2018.4
module load IMOD/4.11.1
module load ARETOMO/1.3.3
#module load ANACONDA/3/2023.09
module load RELION/5.0-beta-2
export CRYOBOOST_HOME=/fs/pool/pool-fbeck/projects/4TomoPipe/rel5Pipe/src/CryoBoost/

module list
echo "submitting relion"

srun XXXcommandXXX

echo "done"

