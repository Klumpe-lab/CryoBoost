
# version 50001

data_job

_rlnJobTypeLabel             relion.ctffind.ctffind4
_rlnJobIsContinue                       1
_rlnJobIsTomo                           1
 

# version 50001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
input_star_mics Schemes/relion_tomo_prep/motioncorr/corrected_tilt_series.star 
do_phaseshift         No 
phase_min          0 
phase_max        180 
phase_step         10 
dast        100 
fn_ctffind_exe /fs/pool/pool-bmapps/hpcl8/app/soft/CTFFIND/4.1.14/bin/ctffind 
use_given_ps        Yes 
slow_search         No 
ctf_win         -1 
box        512 
dfmin       5000 
dfmax      70000 
resmin         30 
resmax          5 
dfstep        500 
localsearch_nominal_defocus      10000 
exp_factor_dose        100 
nr_mpi         72 
do_queue        Yes 
queuename    openmpi 
qsub     sbatch 
qsubscript qsub/qsub_hpcl89.sh 
min_dedicated          1 
other_args         "" 
qsub_extra1          3 
qsub_extra2         24 
qsub_extra3    p.hpcl8 
qsub_extra4          2 
qsub_extra5      370G
 
