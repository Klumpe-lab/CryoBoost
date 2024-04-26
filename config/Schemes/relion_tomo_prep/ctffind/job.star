
# version 30001

data_job

_rlnJobTypeLabel             relion.ctffind.ctffind4
_rlnJobIsContinue                       0
_rlnJobIsTomo                           1
 

# version 30001

data_joboptions_values

loop_ 
_rlnJobOptionVariable #1 
_rlnJobOptionValue #2 
       box        512 
   ctf_win         -1 
      dast        100 
     dfmax      70000 
     dfmin       5000 
    dfstep        500 
    do_EPA         No 
do_ignore_ctffind_params        Yes 
do_phaseshift         No 
  do_queue        Yes 
fn_ctffind_exe /fs/pool/pool-bmapps/hpcl8/app/soft/CTFFIND/4.1.14/bin/ctffind 
fn_gctf_exe /fs/pool/pool-bmapps/hpcl8/app/soft/GCTF/1.06/bin4app/gctf 
   gpu_ids         "" 
input_star_mics Schemes/relion_tomo_prep/motioncorr/corrected_tilt_series.star 
min_dedicated          1 
    nr_mpi         72 
other_args         "" 
other_gctf_args         "" 
 phase_max        180 
 phase_min          0 
phase_step         10 
      qsub     sbatch 
qsub_extra1          3 
qsub_extra2         24 
qsub_extra3    p.hpcl8 
qsub_extra4      2 
qsubscript    qsub/qsub_hpcl89.sh 
 queuename    openmpi 
    resmax          5 
    resmin         30 
slow_search         No 
use_ctffind4        Yes 
  use_gctf         No 
use_given_ps        Yes 
 
